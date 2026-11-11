#!/usr/bin/env python
"""Audit pass 3: vintage/tool summary and a first look at the low-resistivity premise.

Inputs : results/audit/{las_files,well_inventory}.csv, data/interim/miss_logs.parquet,
         data/raw/kgs/ks_las_files (file -> well link)
Outputs: results/audit/premise_check.json, results/audit/vintage_summary.json
Deterministic (no random numbers). Descriptive statistics only: nothing here is tuned.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/audit"
WINDOW_FT = 50.0  # upper Mississippian window ("chat" position) used for the premise check


def main() -> None:
    inv = pd.read_csv(OUT / "well_inventory.csv", dtype={"KID": str}).set_index("KID")
    files = pd.read_csv(OUT / "las_files.csv", dtype={"file_id": str})
    logs = pd.read_parquet(ROOT / "data/interim/miss_logs.parquet")

    # ---- vintage / tool
    svc = files.service_company.fillna("unknown").str.upper().str.replace(r"[^A-Z ]", "", regex=True)
    svc = svc.str.split().str[0].replace({"": "unknown"})
    yr = files.log_date.astype(str).str.extract(r"((?:19|20)\d{2})", expand=False).astype(float)
    vintage = {
        "script": "scripts/audit_report.py", "seed": None,
        "files_parsed": int(files.parse_ok.sum()), "files_total": int(len(files)),
        "service_company_first_word_counts": svc.value_counts().head(12).to_dict(),
        "log_year_from_header_quantiles": yr.quantile([0, .1, .5, .9, 1]).to_dict(),
        "files_with_log_year": int(yr.notna().sum()),
        "step_ft_counts": files.step_ft.round(3).value_counts().head(5).to_dict(),
        "depth_flag_counts": files.depth_flag.value_counts().to_dict(),
        "wrapped_files": int((files.wrap.astype(str).str.upper().str.startswith("Y")).sum()),
        "null_value_counts": files.null.value_counts().head(5).to_dict(),
        "usable_wells_spud_before_2000": int((inv[inv.usable_min].spud_year < 2000).sum()),
    }
    (OUT / "vintage_summary.json").write_text(json.dumps(vintage, indent=1, default=str))

    # ---- premise: is producing upper Mississippian low-resistivity?
    w = logs[(logs.rel_top_ft >= 0) & (logs.rel_top_ft <= WINDOW_FT)]
    w = w.dropna(subset=["RDEEP", "DEN", "NPHI", "GR"])
    w = w.assign(phi_dn=((2.71 - w.DEN) / 1.71 + w.NPHI) / 2)  # limestone-scaled D-N porosity
    g = w.groupby("KID").agg(rdeep_med=("RDEEP", "median"), phi_dn_med=("phi_dn", "median"),
                             gr_med=("GR", "median"), n=("RDEEP", "size"))
    g = g[g.n >= 40].join(inv[["status", "produce_form", "usable_min"]])
    g = g[g.usable_min]
    miss = g.produce_form.fillna("").str.contains("MISS", case=False)
    prod = miss & g.status.isin(["OIL", "GAS", "O&G", "OIL-P&A", "GAS-P&A", "O&G-P&A"])
    dry = g.status.isin(["D&A"])

    def desc(s):
        return {"n_wells": int(len(s)), "q25": float(s.quantile(.25)),
                "median": float(s.median()), "q75": float(s.quantile(.75))}

    # porous samples only (phi_dn >= 0.15), per producing well: share with RDEEP < 5 ohm.m
    wp = w[w.KID.isin(g.index[prod]) & (w.phi_dn >= 0.15)]
    share = (wp.RDEEP < 5).groupby(wp.KID).mean()
    u = mannwhitneyu(g.rdeep_med[prod], g.rdeep_med[dry], alternative="two-sided")
    out = {
        "script": "scripts/audit_report.py", "seed": None, "window_ft_below_top": WINDOW_FT,
        "definition_producer": "status oil/gas (incl. P&A) AND KGS producing formation contains MISS",
        "definition_dry": "status D&A",
        "rdeep_median_ohmm": {"miss_producers": desc(g.rdeep_med[prod]), "dry_holes": desc(g.rdeep_med[dry])},
        "phi_dn_median": {"miss_producers": desc(g.phi_dn_med[prod]), "dry_holes": desc(g.phi_dn_med[dry])},
        "mannwhitney_rdeep_prod_vs_dry_p": float(u.pvalue),
        "producers_share_of_porous_samples_rdeep_lt_5": desc(share),
        "producers_with_median_rdeep_lt_5": int((g.rdeep_med[prod] < 5).sum()),
        "producers_with_median_rdeep_lt_10": int((g.rdeep_med[prod] < 10).sum()),
        "note": "Descriptive only. Completion intervals are not used; 'producer' is well-level.",
    }
    (OUT / "premise_check.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(vintage, default=str)[:1500])
    print(json.dumps(out)[:1500])


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
