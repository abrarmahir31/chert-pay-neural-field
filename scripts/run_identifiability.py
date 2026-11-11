#!/usr/bin/env python
"""Identifiability study on the synthetic benchmark (pre-registered rule: DECISIONS.md D20).

Usage: python scripts/run_identifiability.py --config configs/cpu_small.yaml [--only base,fixed_n]
Writes results/identifiability/runs.csv (one row per experiment x seed),
       results/identifiability/summary.json (per-experiment aggregates + rule verdict).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.model.inversion import InversionConfig, JointInversion  # noqa: E402
from chertfield.seed import set_seed  # noqa: E402
from chertfield.synthetic.benchmark import SynthConfig, make_benchmark  # noqa: E402

# experiment -> (synthetic overrides, inversion overrides, description)
EXPERIMENTS = {
    "base": ({}, {}, "realistic base case: learn m, n, f_micro fields (decision rule)"),
    "null_n": ({"n_field": (1.9, 0.0, 20.0)}, {}, "null control: true n constant"),
    "fixed_n": ({}, {"fixed": {"n": 1.9}}, "n fixed at its true mean; learn m, f_micro"),
    "const_n": ({}, {"constant": ("n",)}, "n learned as one scalar; m, f_micro fields"),
    "fixed_n_f": ({}, {"fixed": {"n": 1.9, "f_micro": 0.35}}, "only m learned (n, f_micro at true means)"),
    "archie_model": ({}, {"fixed": {"n": 2.0, "f_micro": 0.0}, "resistivity": "archie"},
                     "mis-specified: plain Archie, n = 2, effective m only"),
    "oracle_k_rmf": ({}, {"know_flushing_exponent": "TRUE_MEAN", "know_rmf_exactly": True},
                     "diagnostic: flushing exponent fixed at 0.21, header Rmf trusted"),
    "exact_flushing": ({"sxo_exp_range": (0.2, 0.2), "rmf_header_error": 0.0},
                       {"know_flushing_exponent": 0.2, "know_rmf_exactly": True},
                       "diagnostic: flushing exponent and Rmf exactly known"),
    "no_shallow": ({"p_missing": {"DT": 0.80, "PE": 0.59, "LRXO": 1.0}}, {},
                   "no shallow resistivity at all"),
    "noise_x2": ({"noise": {"RHOB": 0.03, "NPHI": 0.02, "GR": 8.0, "LRT": 0.06, "LRXO": 0.10,
                            "DT": 3.0, "PE": 0.30}},
                 {"sigma": {"RHOB": 0.03, "NPHI": 0.02, "GR": 8.0, "LRT": 0.06, "LRXO": 0.10,
                            "DT": 3.0, "PE": 0.30}}, "noise doubled"),
    "archie_world": ({"forward_resistivity": "archie"}, {"fixed": {"f_micro": 0.0},
                                                         "resistivity": "archie"},
                     "truth is plain Archie; learn m, n"),
}


def metrics(est, true):
    est, true = np.asarray(est, float).ravel(), np.asarray(true, float).ravel()
    sd = float(true.std())
    r = float(np.corrcoef(est, true)[0, 1]) if est.std() > 1e-9 and sd > 1e-9 else float("nan")
    rmse = float(np.sqrt(np.mean((est - true) ** 2)))
    return dict(r=r, rmse=rmse, rmse_over_sd=rmse / sd if sd > 1e-9 else float("nan"),
                bias=float(np.mean(est - true)), sd_est=float(est.std()), sd_true=sd)


def run_one(name, seed, cfg):
    s_over, i_over, _ = EXPERIMENTS[name]
    sc = SynthConfig(**{**cfg["synthetic"], "seed": seed, **s_over})
    d = make_benchmark(sc)
    i_over = dict(i_over)
    if i_over.get("know_flushing_exponent") == "TRUE_MEAN":
        i_over["know_flushing_exponent"] = float(np.mean(sc.sxo_exp_range))
    f = cfg["field"]
    ic = InversionConfig(n_frequencies=f["n_frequencies"], hidden=f["hidden"], layers=f["layers"],
                         steps=cfg["identifiability"]["steps"], rw=sc.rw, seed=1000 + seed,
                         extent_km=tuple(sc.extent_km), **i_over)
    set_seed(ic.seed)
    model = JointInversion(d["xy_km"], d["obs"], d["mask"], d["rmf_obs"], ic)
    t0 = time.time()
    model.fit()
    with torch.no_grad():
        _, prop, _ = model.predict()
        par = {k: v.numpy() for k, v in model.params_at_wells().items()}
        f_mic = torch.as_tensor(par["f_micro"])[:, None]
        sw_tot = (f_mic + (1 - f_mic) * prop["sw_macro"]).numpy()
        phi = prop["phi"].numpy()
    t = d["truth"]
    row = dict(experiment=name, seed=seed, init_seed=ic.seed, seconds=round(time.time() - t0, 1))
    for k in ("m", "n", "f_micro"):
        row.update({f"{k}_{a}": b for a, b in metrics(par[k], t[k]).items()})
    for k, est, true in (("phi", phi, t["phi"]), ("sw_total", sw_tot, t["sw_total"]),
                         ("bvh", phi * (1 - sw_tot), t["bvh"])):
        mm = metrics(est, true)
        row.update({f"{k}_r": mm["r"], f"{k}_rmse": mm["rmse"]})
    # well-level pay indicator: mean bulk-volume hydrocarbon of the upper 40 samples
    pay_est = (phi * (1 - sw_tot))[:, :40].mean(1)
    wet = t["wet_well"]
    if wet.any() and (~wet).any():
        from sklearn.metrics import roc_auc_score
        row["auc_pay_vs_wet"] = float(roc_auc_score(~wet, pay_est))
    row.update({f"chi2_{k}": v for k, v in model.chi2_per_curve().items()})
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/cpu_small.yaml"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    torch.set_num_threads(cfg.get("threads", 4))
    names = [n for n in a.only.split(",") if n] or list(EXPERIMENTS)
    out = ROOT / "results/identifiability"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in names:
        for seed in cfg["identifiability"]["seeds"]:
            rows.append(run_one(name, seed, cfg))
            r = rows[-1]
            print(f"{name:15s} seed {seed} | m r={r['m_r']:.2f} e={r['m_rmse_over_sd']:.2f} | "
                  f"n r={r['n_r']:.2f} e={r['n_rmse_over_sd']:.2f} | f r={r['f_micro_r']:.2f} "
                  f"e={r['f_micro_rmse_over_sd']:.2f} | bvh r={r['bvh_r']:.2f} | {r['seconds']}s",
                  flush=True)
    df = pd.DataFrame(rows)
    path = out / "runs.csv"
    if a.only and path.exists():
        old = pd.read_csv(path)
        df = pd.concat([old[~old.experiment.isin(names)], df], ignore_index=True)
    df.to_csv(path, index=False)

    # ---- pre-registered rule (D20)
    def separable(p):
        b = df[df.experiment == "base"]
        ok = (b[f"{p}_r"] >= 0.70) & (b[f"{p}_rmse_over_sd"] <= 0.5)
        return bool(ok.sum() >= 2), int(ok.sum())

    summary = {"script": "scripts/run_identifiability.py", "config": Path(a.config).name,
               "benchmark_seeds": cfg["identifiability"]["seeds"], "init_seed": "1000 + seed",
               "experiments": {k: v[2] for k, v in EXPERIMENTS.items()}}
    num = df.select_dtypes("number").columns.drop(["seed", "init_seed"])
    summary["mean_by_experiment"] = json.loads(df.groupby("experiment")[num].mean().round(4).to_json(orient="index"))
    if "base" in set(df.experiment):
        rule = {p: dict(zip(("separable", "seeds_passing"), separable(p), strict=True))
                for p in ("m", "n", "f_micro")}
        if {"null_n"} <= set(df.experiment):
            sd_null = df[df.experiment == "null_n"].n_sd_est.mean()
            sd_base_true = df[df.experiment == "base"].n_sd_true.mean()
            rule["null_control_n"] = dict(sd_n_hat=float(sd_null), limit=float(0.5 * sd_base_true),
                                          passed=bool(sd_null <= 0.5 * sd_base_true))
        m_ok, n_ok = rule["m"]["separable"], rule["n"]["separable"]
        n_ok = n_ok and rule.get("null_control_n", {}).get("passed", False)
        rule["outcome"] = (1 if (m_ok and n_ok) else 2 if m_ok else 3)
        summary["decision_rule_D20"] = rule
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary.get("decision_rule_D20", {}), indent=None))


if __name__ == "__main__":
    main()
