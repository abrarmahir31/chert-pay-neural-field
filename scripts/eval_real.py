#!/usr/bin/env python
"""Evaluate rule D24b: pay-vs-dry AUC on held-out spatial blocks, baselines, bootstrap CIs.

Reads results/real/pay_*.csv written by scripts/train_real.py (or results/standin with
--standin), computes the baselines on the same wells and folds, and writes
results/real/evaluation.json and results/real/well_scores.csv.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ENTRIES = ["archie_field", "dual_field"]            # D27: primary, second
SEED = 20261112


def classical(data, rw, model):
    """Fixed-parameter log analysis (m = n = 2, nominal Rw): mean bulk-volume hydrocarbon."""
    o = data["obs"]
    phi = np.clip(((2.71 - o["RHOB"]) / 1.66 + o["NPHI"]) / 2, 0.01, 0.6)
    rt = 10 ** o["LRT"]
    if model == "archie":
        sw = np.sqrt(rw / (phi**2 * rt))
    else:  # Simandoux, Rsh = 4 ohm.m, linear gamma-ray shale index per well
        lo, hi = np.nanpercentile(o["GR"], [5, 95], axis=1, keepdims=True)
        vsh = np.clip((o["GR"] - lo) / np.maximum(hi - lo, 1.0), 0, 1)
        a_, b_, c_ = phi**2 / rw, vsh / 4.0, 1.0 / rt
        sw = (-b_ + np.sqrt(b_**2 + 4 * a_ * c_)) / (2 * a_)
    return np.nanmean(phi * (1 - np.clip(sw, 0, 1)), axis=1), phi


def features(data, phi):
    cols = []
    for v in (data["obs"]["RHOB"], data["obs"]["NPHI"], data["obs"]["GR"], data["obs"]["LRT"], phi):
        cols += list(np.nanpercentile(v, [10, 50, 90], axis=1))
    return np.c_[tuple(cols)]


def supervised(X, y, fold, kind):
    """Trained on labelled wells of the training blocks only; scored on held-out blocks."""
    score = np.full(len(y), np.nan)
    for k in sorted(set(fold)):
        tr, te = (fold != k) & (y >= 0), fold == k
        if len(set(y[tr])) < 2:
            continue
        if kind == "gbm":
            clf = HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                                                 class_weight="balanced", random_state=SEED)
        else:
            clf = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                MLPClassifier((32, 16), max_iter=2000, random_state=SEED))
        score[te] = clf.fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return score


def boot_auc(y, S, n_boot, rng):
    """Stratified bootstrap over wells; returns AUC matrix (n_boot x n_methods)."""
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    out = np.empty((n_boot, S.shape[1]))
    for b in range(n_boot):
        i = np.r_[rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]
        out[b] = [roc_auc_score(y[i], S[i, j]) for j in range(S.shape[1])]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/cpu_small.yaml"))
    ap.add_argument("--standin", action="store_true")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))["real"]
    out = ROOT / ("results/standin" if a.standin else "results/real")
    if a.standin:
        from chertfield.data.standin import load_standin
        data = load_standin(**cfg.get("standin", {}))
        fold = data["fold"]
    else:
        from chertfield.data.real import load_real
        data = load_real()
        sp = pd.read_csv(ROOT / "results/splits/spatial_blocks_v1.csv", dtype={"KID": str}).set_index("KID")
        fold = sp.loc[data["kid"], "fold"].to_numpy()
    y = data["label"]
    table = pd.DataFrame({"kid": data["kid"], "fold": fold, "label": y}).set_index("kid")
    table["fixed_archie"], phi = classical(data, cfg["rw_nominal"], "archie")
    table["fixed_simandoux"], _ = classical(data, cfg["rw_nominal"], "simandoux")
    X = features(data, phi)
    table["supervised_gbm"] = supervised(X, y, fold, "gbm")
    table["supervised_mlp"] = supervised(X, y, fold, "mlp")
    present = {}
    for f in sorted(out.glob("pay_*.csv")):
        name = f.stem[4:]
        p = pd.read_csv(f, dtype={"kid": str}).groupby("kid").pay.agg(["mean", "std"])
        col = name if name in ENTRIES else f"inversion_{name}"
        table[col] = p["mean"].reindex(table.index)
        table[f"{col}_ens_sd"] = p["std"].reindex(table.index)
        present[col] = f.name
    table.to_csv(out / "well_scores.csv")
    methods = [c for c in table.columns if c not in ("fold", "label") and not c.endswith("_ens_sd")]
    lab = (table.label >= 0) & table[methods].notna().all(axis=1)
    yy, S = table.label[lab].to_numpy(), table.loc[lab, methods].to_numpy()
    rng = np.random.default_rng(SEED)
    B = boot_auc(yy, S, cfg["bootstrap"], rng)
    res = {"script": "scripts/eval_real.py", "seed": SEED, "bootstrap": cfg["bootstrap"],
           "n_producers": int((yy == 1).sum()), "n_dry": int((yy == 0).sum()), "inputs": present,
           "auc": {m: {"auc": float(roc_auc_score(yy, S[:, j])),
                       "ci95": [float(x) for x in np.percentile(B[:, j], [2.5, 97.5])]}
                   for j, m in enumerate(methods)}}
    entries = [m for m in ENTRIES if m in methods]
    base = [m for m in methods if m not in ENTRIES]
    if entries and base:
        best = max(base, key=lambda m: res["auc"][m]["auc"])
        jb = methods.index(best)
        alpha = 0.05 / len(entries)                      # Bonferroni over the entries (D27)
        res["best_baseline"], res["alpha_per_entry"] = best, alpha
        res["paired_difference_vs_best_baseline"] = {}
        for m in entries:
            d = B[:, methods.index(m)] - B[:, jb]
            ci = [float(x) for x in np.percentile(d, [100 * alpha / 2, 100 * (1 - alpha / 2)])]
            res["paired_difference_vs_best_baseline"][m] = {
                "difference": float(res["auc"][m]["auc"] - res["auc"][best]["auc"]),
                "ci_bonferroni": ci, "beats_best_baseline": bool(ci[0] > 0)}
        res["D24b_any_entry_beats_best_baseline"] = any(
            v["beats_best_baseline"] for v in res["paired_difference_vs_best_baseline"].values())
    rec = [pd.read_csv(f).assign(run=f.stem[6:]) for f in sorted(out.glob("recon_*.csv"))
           if f.stat().st_size > 5]
    if rec:
        r = pd.concat(rec)
        r["rmse_over_sd"] = r.rmse / r.sd_obs
        res["blind_curve_reconstruction_mean"] = json.loads(
            r.groupby(["run", "curve"])[["rmse", "rmse_over_sd", "bias"]].mean().round(4)
            .reset_index().to_json(orient="records"))
    (out / "evaluation.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({m: round(v["auc"], 3) for m, v in res["auc"].items()}))
    print(json.dumps(res.get("paired_difference_vs_best_baseline", {})))


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    main()
