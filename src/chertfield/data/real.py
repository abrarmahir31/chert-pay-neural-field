"""Real-data set for the inversion: upper-Mississippian window on a fixed grid (D28)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WINDOW_FT, STEP_FT = 100.0, 0.5
PRODUCING = {"OIL", "GAS", "O&G", "OIL-P&A", "GAS-P&A", "O&G-P&A"}
CURVES = {"RHOB": "DEN", "NPHI": "NPHI", "GR": "GR", "LRT": "RDEEP", "LRXO": "RSHAL",
          "DT": "DT", "PE": "PE"}
RMF_DEFAULT, RMF_SD_HEADER, RMF_SD_MISSING = 0.5, 0.7, 1.0  # ln-units; wide on purpose (see docs)


def well_labels(inv: pd.DataFrame) -> pd.Series:
    """1 = Mississippian producer, 0 = dry hole (D&A), -1 = unlabeled (D28)."""
    miss = inv.produce_form.fillna("").str.contains("MISS", case=False)
    lab = pd.Series(-1, index=inv.index)
    lab[miss & inv.status.isin(PRODUCING)] = 1
    lab[inv.status == "D&A"] = 0
    return lab


def load_real(root: Path = ROOT) -> dict:
    inv = pd.read_csv(root / "results/audit/well_inventory.csv", dtype={"KID": str}).set_index("KID")
    inv = inv[inv.usable_min]
    logs = pd.read_parquet(root / "data/interim/miss_logs.parquet")
    logs = logs[logs.KID.isin(inv.index) & (logs.rel_top_ft >= 0) & (logs.rel_top_ft <= WINDOW_FT)]
    n = int(WINDOW_FT / STEP_FT) + 1
    kids = sorted(set(logs.KID))
    row = {k: i for i, k in enumerate(kids)}
    wi = logs.KID.map(row).to_numpy()
    si = np.clip(np.round(logs.rel_top_ft.to_numpy() / STEP_FT).astype(int), 0, n - 1)
    obs, mask = {}, {}
    for name, col in CURVES.items():
        a = np.full((len(kids), n), np.nan)
        v = logs[col].to_numpy(float)
        if name in ("LRT", "LRXO"):
            v = np.log10(np.where(v > 0, v, np.nan))
        a[wi, si] = v
        obs[name], mask[name] = a, np.isfinite(a)
    inv = inv.loc[kids]
    files = pd.read_csv(root / "results/audit/las_files.csv", dtype={"file_id": str})
    idx = pd.read_csv(root / "data/raw/kgs/ks_las_files/ks_las_files.txt", dtype=str, encoding="latin-1")
    idx["file_id"] = idx.URL.str.extract(r"/(\d+)\.las", expand=False)
    files["KID"] = files.file_id.map(dict(zip(idx.file_id, idx.KGS_ID, strict=False)))
    rmf = files[files.rmf.between(0.01, 5.0)].groupby("KID").rmf.median().reindex(kids)
    xy = np.c_[inv.x_km - inv.x_km.min(), inv.y_km - inv.y_km.min()]
    return dict(kid=np.array(kids), xy_km=xy, obs=obs, mask=mask,
                rmf_obs=rmf.fillna(RMF_DEFAULT).to_numpy(),
                log_rmf_prior_sd=np.where(rmf.notna(), RMF_SD_HEADER, RMF_SD_MISSING),
                label=well_labels(inv).to_numpy(),
                extent_km=(float(xy[:, 0].max()), float(xy[:, 1].max())))
