#!/usr/bin/env python
"""Blind-well pay indicator under the frozen spatial-block split (rule D24b, entries D27).

For every fold: fit the label-free inversion on the training-block wells, freeze the shared
parts (parameter field or global parameters, Rw), then fit only per-sample and per-well terms
on the held-out wells and record their pay indicator (mean bulk-volume hydrocarbon, D28).
Production labels are never used here.

Usage: python scripts/train_real.py --config configs/cpu_small.yaml --entry archie --spatial field
       add --standin to run the identical pipeline on synthetic stand-in data (tests).
Output: results/real/pay_<entry>_<spatial>.csv (+ .json), or results/standin/... with --standin.
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

ENTRY = {"archie": {"fixed_f": 0.0, "resistivity": "archie"},
         "dual": {"fixed_f": None, "resistivity": "dual_porosity"}}


def subset(d, sel):
    return dict(xy_km=d["xy_km"][sel], obs={k: v[sel] for k, v in d["obs"].items()},
                mask={k: v[sel] for k, v in d["mask"].items()}, rmf_obs=d["rmf_obs"][sel],
                log_rmf_prior_sd=d["log_rmf_prior_sd"][sel])


def build(d, cfg, entry, spatial, steps, seed, drop=()):
    r, f = cfg["real"], cfg["field"]
    fixed = {"n": r["n_fixed"]}
    if ENTRY[entry]["fixed_f"] is not None:
        fixed["f_micro"] = ENTRY[entry]["fixed_f"]
    use = tuple(c for c in ("RHOB", "NPHI", "GR", "LRT", "LRXO", "DT", "PE") if c not in drop)
    ic = InversionConfig(n_frequencies=f["n_frequencies"], hidden=f["hidden"], layers=f["layers"],
                         steps=steps, rw=r["rw_nominal"], rw_prior_log_sd=r["rw_prior_log_sd"],
                         learn_rw=True, fixed=fixed, resistivity=ENTRY[entry]["resistivity"],
                         spatial=spatial, seed=seed, extent_km=tuple(cfg["_extent"]),
                         device=cfg.get("device", "cpu"), use_curves=use)
    return JointInversion(d["xy_km"], d["obs"], d["mask"], d["rmf_obs"], ic,
                          log_rmf_prior_sd=d["log_rmf_prior_sd"])


def well_pay(model, d):
    bvh = model.pay_indicator()
    ok = d["mask"]["RHOB"] & d["mask"]["NPHI"] & d["mask"]["LRT"]
    return np.nanmean(np.where(ok, bvh, np.nan), axis=1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/cpu_small.yaml"))
    ap.add_argument("--entry", choices=list(ENTRY), default="archie")
    ap.add_argument("--spatial", choices=["field", "per_well", "constant"], default="field")
    ap.add_argument("--standin", action="store_true")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    r = cfg["real"]
    torch.set_num_threads(cfg.get("threads", 4))
    if a.standin:
        from chertfield.data.standin import load_standin
        data = load_standin(**r.get("standin", {}))
        fold = data["fold"]
    else:
        from chertfield.data.real import load_real
        data = load_real()
        sp = pd.read_csv(ROOT / "results/splits/spatial_blocks_v1.csv", dtype={"KID": str}).set_index("KID")
        fold = sp.loc[data["kid"], "fold"].to_numpy()
    cfg["_extent"] = data["extent_km"]
    rows, recon, t0 = [], [], time.time()
    for seed in r["seeds"]:
        for k in sorted(set(fold)):
            set_seed(seed * 100 + int(k))
            te = fold == k
            dte = subset(data, te)
            trained = None
            if a.spatial != "per_well":
                trained = build(subset(data, ~te), cfg, a.entry, a.spatial, r["steps_train"], seed)
                trained.fit()
            test = build(dte, cfg, a.entry, a.spatial, r["steps_test"], seed)
            if trained is not None:
                test.freeze_shared(trained)
            test.fit()
            pay = well_pay(test, dte)
            chi2 = test.chi2_per_curve()
            rows += [dict(kid=kid, fold=int(k), seed=seed, pay=float(p), label=int(lab))
                     for kid, p, lab in zip(data["kid"][te], pay, data["label"][te], strict=True)]
            # blind curve reconstruction: refit held-out wells without one curve, predict it
            for h in (r.get("hide", []) if seed == r["seeds"][0] else []):
                m = dte["mask"][h]
                if not m.any():
                    continue
                hm = build(dte, cfg, a.entry, a.spatial, r["steps_test"], seed, drop=(h,))
                if trained is not None:
                    hm.freeze_shared(trained)
                hm.fit()
                with torch.no_grad():
                    pred = hm.predict()[0][h].cpu().numpy()
                err = (pred - dte["obs"][h])[m]
                recon.append(dict(curve=h, fold=int(k), seed=seed, n=int(m.sum()),
                                  rmse=float(np.sqrt(np.mean(err**2))), bias=float(err.mean()),
                                  sd_obs=float(dte["obs"][h][m].std())))
            print(f"seed {seed} fold {k}: {int(te.sum())} held-out wells, "
                  f"chi2 LRT {chi2.get('LRT', float('nan')):.2f}, {time.time() - t0:.0f}s", flush=True)
    out = ROOT / ("results/standin" if a.standin else "results/real")
    out.mkdir(parents=True, exist_ok=True)
    stem = f"pay_{a.entry}_{a.spatial}"
    pd.DataFrame(rows).to_csv(out / f"{stem}.csv", index=False)
    pd.DataFrame(recon).to_csv(out / f"recon_{a.entry}_{a.spatial}.csv", index=False)
    meta = {"script": "scripts/train_real.py", "config": Path(a.config).name, "entry": a.entry,
            "spatial": a.spatial, "seeds": r["seeds"], "standin": a.standin,
            "n_wells": int(len(data["kid"])), "seconds": round(time.time() - t0),
            "settings": {k: v for k, v in r.items() if k != "standin"}}
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
