#!/usr/bin/env python
"""EXPLORATORY diagnostics of the real-data result (after D24b; nothing is refitted).

Uses only the saved outputs in results/real/ plus descriptive per-well log statistics.
Everything here is post hoc and must be labelled exploratory in the paper.
Output: results/real/diagnostics_exploratory.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.data.real import load_real  # noqa: E402

OUT = ROOT / "results/real"


def auc(y, s):
    ok = np.isfinite(s) & (y >= 0)
    return float(roc_auc_score(y[ok], s[ok])) if len(set(y[ok])) == 2 else float("nan")


def main() -> None:
    t = pd.read_csv(OUT / "well_scores.csv", dtype={"kid": str}).set_index("kid")
    methods = [c for c in t.columns if c not in ("fold", "label") and not c.endswith("_ens_sd")]
    y = t.label.to_numpy()
    res = {"script": "scripts/diagnose_real.py", "seed": None, "status": "EXPLORATORY, post hoc"}
    res["labelled_wells_without_a_score"] = {
        m: t.index[(t.label >= 0) & t[m].isna()].tolist() for m in methods if t[m].isna().any()}
    res["auc_per_fold"] = {m: {str(k): round(auc(g.label.to_numpy(), g[m].to_numpy()), 3)
                               for k, g in t.groupby("fold")} for m in methods}
    per_seed = {}
    for f in sorted(OUT.glob("pay_*.csv")):
        p = pd.read_csv(f, dtype={"kid": str})
        a = [auc(g.label.to_numpy(), g.pay.to_numpy()) for _, g in p.groupby("seed")]
        per_seed[f.stem[4:]] = {"min": round(min(a), 3), "max": round(max(a), 3),
                                "mean": round(float(np.mean(a)), 3)}
    res["auc_single_ensemble_member"] = per_seed
    res["ensemble_sd_over_mean_median"] = {
        c[:-7]: round(float((t[c] / t[c[:-7]].abs()).median()), 3)
        for c in t.columns if c.endswith("_ens_sd")}
    # descriptive per-well log statistics over the analysis window
    d = load_real()
    o = d["obs"]
    phi = np.clip(((2.71 - o["RHOB"]) / 1.66 + o["NPHI"]) / 2, 0.0, 0.6)
    feat = pd.DataFrame({"mean_dn_porosity": np.nanmean(phi, 1), "mean_log10_rt": np.nanmean(o["LRT"], 1),
                         "mean_gr": np.nanmean(o["GR"], 1)}, index=d["kid"]).reindex(t.index)
    res["auc_single_descriptive_feature"] = {
        "mean_dn_porosity": round(auc(y, feat.mean_dn_porosity.to_numpy()), 3),
        "low_resistivity (-mean log10 Rt)": round(auc(y, -feat.mean_log10_rt.to_numpy()), 3),
        "high_resistivity (+mean log10 Rt)": round(auc(y, feat.mean_log10_rt.to_numpy()), 3),
        "low_gamma_ray": round(auc(y, -feat.mean_gr.to_numpy()), 3)}
    lab = t.label >= 0
    res["spearman_with_features_labelled_wells"] = {
        m: {c: round(float(spearmanr(t.loc[lab, m], feat.loc[lab, c], nan_policy="omit")[0]), 2)
            for c in feat.columns} for m in methods}
    key = [m for m in ("archie_field", "inversion_archie_per_well", "fixed_archie", "supervised_gbm")
           if m in methods]
    res["spearman_between_methods"] = {
        f"{a} ~ {b}": round(float(spearmanr(t.loc[lab, a], t.loc[lab, b], nan_policy="omit")[0]), 2)
        for i, a in enumerate(key) for b in key[i + 1:]}
    res["median_score_by_label"] = {m: {"producer": round(float(t.loc[t.label == 1, m].median()), 4),
                                        "dry": round(float(t.loc[t.label == 0, m].median()), 4)}
                                    for m in methods}
    (OUT / "diagnostics_exploratory.json").write_text(json.dumps(res, indent=1))
    for k in ("labelled_wells_without_a_score", "auc_single_descriptive_feature",
              "auc_single_ensemble_member", "ensemble_sd_over_mean_median", "spearman_between_methods"):
        print(k, json.dumps(res[k]))
    for m in key:
        print(m, res["auc_per_fold"][m], res["spearman_with_features_labelled_wells"][m])


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    main()
