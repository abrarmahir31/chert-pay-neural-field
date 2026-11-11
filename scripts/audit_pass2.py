#!/usr/bin/env python
"""Audit pass 2: canonical curves, Mississippian interval, well inventory, go/no-go counts.

Inputs : data/raw/kgs/{las,ks_las_files,ks_wells,ks_tops}, configs/mnemonics.yaml
Outputs: results/audit/well_inventory.csv      one row per well (headers + coverage, no log samples)
         results/audit/mnemonic_table.csv      observed mnemonic -> canonical, with file counts
         results/audit/unmapped_mnemonics.csv
         results/audit/audit_summary.json      all numbers quoted at Decision Gate 1
         data/interim/miss_logs.parquet        merged Mississippian-interval logs (NOT committed)
Deterministic (no random numbers).
"""
from __future__ import annotations

import json
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.data.las_io import clean_values, depth_in_feet, read_las  # noqa: E402
from chertfield.data.mnemonics import (  # noqa: E402
    classify,
    harmonise,
    load_table,
    neutron_matrix_from_text,
)

KGS = ROOT / "data/raw/kgs"
OUT = ROOT / "results/audit"
GRID = 0.5  # ft, common resampling step
ABOVE, BELOW_MAX = 100.0, 400.0  # ft kept above the top / max below the top
CHAT_FT = 100.0  # upper Mississippian window reported separately
MIN_JOINT_FT = 20.0  # minimum co-located valid footage for a "usable" well
LAT0, LON0 = 37.2, -98.7
MISS_RE = re.compile(r"^(miss|erosional miss|cowley|osag|lower miss)", re.I)
BASE_RE = re.compile(
    r"^(kinderhook|chattanooga|woodford|misener|viola|maquoketa|simpson|mclish|wilcox|arbuckle|hunton)",
    re.I,
)
RHO_MA = {"LS": 2.71, "SS": 2.65, "DOL": 2.87}
CANON = list(load_table()["canonical"])


def xy_km(lat, lon):
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    x = (lon - LON0) * 111.320 * np.cos(np.radians(LAT0))
    y = (lat - LAT0) * 110.574
    return x, y


# ----------------------------------------------------------------------------- tops
def mississippian_tops(tops: pd.DataFrame) -> pd.DataFrame:
    """Per-well Mississippian top (shallowest Mississippian-system pick) and base."""
    t = tops.copy()
    t["TOP"] = pd.to_numeric(t.TOP, errors="coerce")
    t["ELEVATION"] = pd.to_numeric(t.ELEVATION, errors="coerce")
    t = t[t.TOP.between(500, 9000)]
    rows = []
    for kid, g in t.groupby("KID"):
        m = g[g.FORMATION.str.match(MISS_RE)]
        if m.empty:
            continue
        top = float(m.TOP.min())
        exact = m[m.FORMATION.str.match(r"^Mississippian( System)?$", case=False)].TOP
        b = g[g.FORMATION.str.match(BASE_RE) & (g.TOP > top + 5)]
        rows.append(
            dict(
                KID=kid, miss_top_md=top, n_miss_picks=len(m),
                pick_spread_ft=float(exact.max() - exact.min()) if len(exact) > 1 else 0.0,
                miss_base_md=float(b.TOP.min()) if len(b) else np.nan,
                base_formation=b.loc[b.TOP.idxmin(), "FORMATION"] if len(b) else "",
                elev=float(g.ELEVATION.iloc[0]), lat=float(g.LATITUDE.iloc[0]),
                lon=float(g.LONGITUDE.iloc[0]),
            )
        )
    return pd.DataFrame(rows)


def idw_subsea(known: pd.DataFrame, qx, qy, k=8, exclude_self=False):
    """Inverse-distance (power 2) interpolation of subsea top from the k nearest picked wells."""
    tree = cKDTree(np.c_[known.x.values, known.y.values])
    kk = k + 1 if exclude_self else k
    d, i = tree.query(np.c_[qx, qy], k=kk)
    if exclude_self:
        d, i = d[:, 1:], i[:, 1:]
    w = 1.0 / np.maximum(d, 0.05) ** 2
    z = known.subsea.values[i]
    return (w * z).sum(1) / w.sum(1), d[:, 0]


# ----------------------------------------------------------------------------- LAS
def process_file(args):
    path, top, base = args
    fid = Path(path).stem
    info = {"file_id": fid, "ok": False, "nphi_unk_matrix": None, "flags": []}
    try:
        las = read_las(path)
        null = None
        try:
            null = float(las.well["NULL"].value)
        except Exception:  # noqa: BLE001
            pass
        depth, dflag = depth_in_feet(np.asarray(las.index, float), las.curves[0].unit)
        if dflag != "ft":
            info["flags"].append(dflag)
        lo = top - ABOVE
        hi = min(base if np.isfinite(base) else np.inf, top + BELOW_MAX)
        sel = np.isfinite(depth) & (depth >= lo) & (depth <= hi)
        mapping = []
        best: dict[str, tuple[int, int, np.ndarray, str]] = {}
        try:
            ptxt = str(las.params["MATR"].value) + " " + str(las.params["MATR"].descr)
        except Exception:  # noqa: BLE001
            ptxt = ""
        for c in las.curves[1:]:
            canon, prio = classify(c.original_mnemonic)
            mapping.append((fid, c.original_mnemonic.upper(), (c.unit or "").upper(), canon or ""))
            if canon is None or not sel.any():
                continue
            try:
                v = clean_values(c.data, null)[sel]
            except (TypeError, ValueError):
                continue
            v, fl = harmonise(canon, v, c.unit)
            n = int(np.isfinite(v).sum())
            if n == 0:
                continue
            if fl and "says" in fl:
                info["flags"].append(f"{canon}:{fl}")
            if canon not in best or (prio, -n) < (best[canon][0], -best[canon][1]):
                best[canon] = (prio, n, v, c.descr or "")
        info["mapping"] = mapping
        if not best:
            info["ok"] = True
            info["data"] = None
            return info
        if "NPHI_UNK" in best:
            info["nphi_unk_matrix"] = neutron_matrix_from_text(best["NPHI_UNK"][3], ptxt)
        d = depth[sel]
        gi = np.round(d / GRID).astype(np.int64)
        df = pd.DataFrame({k: b[2] for k, b in best.items()})
        df["gi"] = gi
        df = df.groupby("gi").mean()  # average finer-than-grid samples
        info["data"] = df
        info["ok"] = True
    except Exception as e:  # noqa: BLE001
        info["error"] = f"{type(e).__name__}: {e}"[:160]
    return info


def run_ft(mask: np.ndarray) -> float:
    return float(mask.sum() * GRID)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / "data/interim").mkdir(parents=True, exist_ok=True)
    idx = pd.read_csv(KGS / "ks_las_files/ks_las_files.txt", dtype=str, encoding="latin-1")
    idx = idx[idx.API.fillna("").str.startswith("15-007")].copy()
    idx["file_id"] = idx.URL.str.extract(r"/(\d+)\.las", expand=False)
    idx["have"] = idx.file_id.map(lambda f: (KGS / "las" / f"{f}.las").exists())
    wells = pd.read_csv(KGS / "ks_wells/ks_wells.txt", dtype=str, encoding="latin-1")
    wells = wells[wells.KID.isin(idx.KGS_ID)].drop_duplicates("KID").set_index("KID")
    tops = pd.read_csv(KGS / "ks_tops/ks_tops.txt", dtype=str, encoding="latin-1")
    tops = tops[tops.API_NUMBER.fillna("").str.startswith("15-007")]

    # ---- Mississippian top/base for every Barber well with picks (dense control surface)
    mt = mississippian_tops(tops)
    mt["subsea"] = mt.elev - mt.miss_top_md
    mt = mt[np.isfinite(mt.subsea) & np.isfinite(mt.lat) & mt.subsea.between(-4500, -1500)]
    mt["x"], mt["y"] = xy_km(mt.lat, mt.lon)
    loo, _ = idw_subsea(mt, mt.x.values, mt.y.values, exclude_self=True)
    loo_err = loo - mt.subsea.values
    thick = (mt.miss_base_md - mt.miss_top_md).dropna()

    inv = pd.DataFrame(index=pd.Index(sorted(idx.KGS_ID.unique()), name="KID"))
    w = wells.reindex(inv.index)
    inv["api"] = w.API_NUMBER
    inv["lease"], inv["well"], inv["field"] = w.LEASE, w.WELL, w.FIELD
    inv["lat"] = pd.to_numeric(w.LATITUDE, errors="coerce")
    inv["lon"] = pd.to_numeric(w.LONGITUDE, errors="coerce")
    inv["x_km"], inv["y_km"] = xy_km(inv.lat, inv.lon)
    inv["elev_ft"] = pd.to_numeric(w.ELEVATION, errors="coerce")
    inv["elev_ref"] = w.ELEV_REF.str.strip()
    inv["td_ft"] = pd.to_numeric(w.DEPTH, errors="coerce")
    inv["spud_year"] = pd.to_datetime(w.SPUD, errors="coerce", format="%d-%b-%Y").dt.year
    inv["status"], inv["produce_form"] = w.STATUS, w.PRODUCE_FORM
    for k in ("IP_OIL", "IP_GAS", "IP_WATER"):
        inv[k.lower()] = pd.to_numeric(w[k], errors="coerce")
    inv["n_las_files"] = idx[idx.have].groupby("KGS_ID").size().reindex(inv.index).fillna(0)
    p = mt.set_index("KID").reindex(inv.index)
    inv["miss_top_md"] = p.miss_top_md
    inv["miss_top_source"] = np.where(p.miss_top_md.notna(), "kgs_pick", "")
    inv["pick_spread_ft"] = p.pick_spread_ft
    inv["miss_base_md"] = p.miss_base_md
    inv["base_formation"] = p.base_formation
    need = inv.miss_top_md.isna() & inv.lat.notna() & inv.elev_ft.notna()
    if need.any():
        z, dnn = idw_subsea(mt, inv.x_km[need].values, inv.y_km[need].values)
        inv.loc[need, "miss_top_md"] = inv.elev_ft[need] - z
        inv.loc[need, "miss_top_source"] = "idw_interp"
        inv.loc[need, "nearest_pick_km"] = dnn

    # ---- LAS processing
    jobs = []
    for r in idx[idx.have].itertuples():
        top = inv.miss_top_md.get(r.KGS_ID, np.nan)
        if np.isfinite(top):
            jobs.append((str(KGS / "las" / f"{r.file_id}.las"), float(top),
                         float(inv.miss_base_md.get(r.KGS_ID, np.nan))))
    with Pool(4) as pool:
        res = pool.map(process_file, jobs, chunksize=8)
    f2k = dict(zip(idx.file_id, idx.KGS_ID, strict=True))
    mp = pd.DataFrame([m for r in res for m in r.get("mapping", [])],
                      columns=["file_id", "mnemonic", "unit", "canonical"])
    mp["KID"] = mp.file_id.map(f2k)
    tab = (mp.groupby(["mnemonic", "canonical"])
           .agg(n_files=("file_id", "nunique"), n_wells=("KID", "nunique"),
                units=("unit", lambda s: "|".join(s.value_counts().index[:3])))
           .reset_index().sort_values("n_files", ascending=False))
    tab[tab.canonical != ""].to_csv(OUT / "mnemonic_table.csv", index=False)
    tab[tab.canonical == ""].drop(columns="canonical").to_csv(
        OUT / "unmapped_mnemonics.csv", index=False)

    # ---- merge files per well on the 0.5-ft grid; file with most samples has precedence
    per_well: dict[str, list] = {}
    nmat: dict[str, str] = {}
    flags: dict[str, list] = {}
    for r in res:
        kid = f2k[r["file_id"]]
        flags.setdefault(kid, []).extend(r.get("flags", []))
        if r.get("error"):
            flags[kid].append("parse_error")
        if r.get("data") is not None:
            per_well.setdefault(kid, []).append(r["data"])
            if r["nphi_unk_matrix"]:
                nmat[kid] = r["nphi_unk_matrix"]
    merged = []
    cov_rows = {}
    for kid, dfs in per_well.items():
        dfs = sorted(dfs, key=lambda d: -d.notna().sum().sum())
        m = dfs[0]
        for d in dfs[1:]:
            m = m.combine_first(d)
        m = m.reindex(columns=CANON)
        top = inv.miss_top_md[kid]
        base = inv.miss_base_md[kid]
        dep = m.index.values * GRID
        # neutron: prefer limestone-matrix curve; else unknown-matrix curve (matrix recorded)
        neu = m.NPHI_LS.copy()
        nsrc = "LS" if neu.notna().any() else ""
        if not nsrc and m.NPHI_UNK.notna().any():
            # matrix not in the mnemonic: header value if present, else ASSUMED limestone
            # (in every well that has both curves the two are identical; see audit_summary)
            neu, nsrc = m.NPHI_UNK, nmat.get(kid) or "assumed_LS"
            nsrc = "header_" + nsrc if kid in nmat else nsrc
        elif not nsrc and m.NPHI_SS.notna().any():
            neu, nsrc = m.NPHI_SS, "SS"
        elif not nsrc and m.NPHI_DOL.notna().any():
            neu, nsrc = m.NPHI_DOL, "DOL"
        # bulk density: measured RHOB, else back-computed from density porosity (fluid 1.0 g/cc)
        den = m.RHOB.copy()
        dsrc = "RHOB" if den.notna().any() else ""
        for mat in ("LS", "SS", "DOL"):
            col = m[f"DPHI_{mat}"]
            if col.notna().any():
                back = RHO_MA[mat] - col * (RHO_MA[mat] - 1.0)
                if not dsrc:
                    dsrc = f"from_DPHI_{mat}"
                den = den.fillna(back)
        rdeep = m.RDEEP.copy()
        if m.CDEEP.notna().any():
            c = m.CDEEP.where(m.CDEEP > 0.05)
            rdeep = rdeep.fillna(1000.0 / c)
        m = m.assign(NPHI=neu, DEN=den, RDEEP=rdeep)
        inm = (dep >= top) & (dep <= (base if np.isfinite(base) else np.inf))
        chat = inm & (dep <= top + CHAT_FT)
        core = m.GR.notna() & m.DEN.notna() & m.NPHI.notna() & m.RDEEP.notna()
        row = {f"ft_{c}": run_ft(m[c].notna().values & inm) for c in CANON + ["NPHI", "DEN"]}
        row.update(
            logged_miss_ft=run_ft(m.notna().any(axis=1).values & inm),
            ft_joint=run_ft(core.values & inm),
            ft_joint_chat=run_ft(core.values & chat),
            ft_joint_dt=run_ft((core & m.DT.notna()).values & inm),
            ft_joint_pe=run_ft((core & m.PE.notna()).values & inm),
            ft_joint_shal=run_ft((core & (m.RSHAL.notna() | m.RMED.notna())).values & inm),
            ft_joint_all=run_ft((core & m.DT.notna() & m.PE.notna()).values & inm),
            nphi_source=nsrc, den_source=dsrc,
        )
        if inm.any() and m.CALI.notna().any():
            cal = m.CALI[inm].dropna()
            bit = float(np.round(np.nanpercentile(cal, 10) * 8) / 8) if len(cal) else np.nan
            row["washout_frac"] = float((cal > bit + 1.5).mean()) if len(cal) else np.nan
        if inm.any() and m.DRHO.notna().any():
            row["bad_drho_frac"] = float((m.DRHO[inm].abs() > 0.15).mean())
        cov_rows[kid] = row
        m = m.reset_index()
        m.insert(0, "KID", kid)
        m.insert(1, "depth_ft", m.gi * GRID)
        m["rel_top_ft"] = m.depth_ft - top
        merged.append(m.drop(columns="gi"))
    logs = pd.concat(merged, ignore_index=True)
    logs.to_parquet(ROOT / "data/interim/miss_logs.parquet", index=False)
    inv = inv.join(pd.DataFrame.from_dict(cov_rows, orient="index"))
    inv["qc_flags"] = pd.Series({k: ";".join(sorted(set(v))) for k, v in flags.items()})
    inv["usable_min"] = inv.ft_joint.fillna(0) >= MIN_JOINT_FT
    inv.to_csv(OUT / "well_inventory.csv")

    # ---- summary numbers
    def nwell(col, thr=MIN_JOINT_FT):
        return int((inv[col].fillna(0) >= thr).sum())

    u = inv[inv.usable_min]
    inm_logs = logs[(logs.rel_top_ft >= 0)]
    both = logs.dropna(subset=["NPHI_LS", "NPHI_UNK"])
    dmed = (both.NPHI_UNK - both.NPHI_LS).abs().groupby(both.KID).median()
    summary = {
        "nphi_unk_vs_ls_wells_with_both": int(len(dmed)),
        "nphi_unk_vs_ls_wells_identical_lt_0p002": int((dmed < 0.002).sum()),
        "script": "scripts/audit_pass2.py", "seed": None,
        "las_files_in_kgs_index": int(len(idx)), "las_files_downloaded": int(idx.have.sum()),
        "las_files_processed_ok": int(sum(r["ok"] for r in res)),
        "las_files_parse_error": int(sum(bool(r.get("error")) for r in res)),
        "wells_total": int(len(inv)),
        "wells_with_coordinates": int(inv.lat.notna().sum()),
        "elev_ref_counts": inv.elev_ref.value_counts().to_dict(),
        "spud_year_quantiles": inv.spud_year.quantile([0, .1, .25, .5, .75, 1]).round(0).to_dict(),
        "miss_top_source_counts": inv.miss_top_source.value_counts().to_dict(),
        "miss_control_wells_all_barber": int(len(mt)),
        "idw_loo_mae_ft": float(np.mean(np.abs(loo_err))),
        "idw_loo_p90_abs_ft": float(np.percentile(np.abs(loo_err), 90)),
        "miss_thickness_ft_quantiles": thick.quantile([.1, .5, .9]).round(1).to_dict(),
        "wells_base_picked": int(inv.miss_base_md.notna().sum()),
        "wells_logged_in_miss": nwell("logged_miss_ft", GRID),
        "min_joint_ft_threshold": MIN_JOINT_FT,
        "wells_ge_thr_by_curve": {c: nwell(f"ft_{c}") for c in CANON + ["NPHI", "DEN"]},
        "wells_usable_core_set_GR_DEN_NPHI_RDEEP": nwell("ft_joint"),
        "wells_core_plus_DT": nwell("ft_joint_dt"),
        "wells_core_plus_PE": nwell("ft_joint_pe"),
        "wells_core_plus_shallow_or_medium_res": nwell("ft_joint_shal"),
        "wells_core_plus_DT_and_PE": nwell("ft_joint_all"),
        "usable_nphi_source_counts": u.nphi_source.value_counts().to_dict(),
        "usable_den_source_counts": u.den_source.value_counts().to_dict(),
        "usable_joint_ft_total": float(u.ft_joint.sum()),
        "usable_joint_samples_0p5ft": int(u.ft_joint.sum() / GRID),
        "usable_joint_ft_chat_top100": float(u.ft_joint_chat.sum()),
        "usable_joint_ft_median_per_well": float(u.ft_joint.median()),
        "usable_top_source_counts": u.miss_top_source.value_counts().to_dict(),
        "usable_status_counts": u.status.value_counts().head(10).to_dict(),
        "usable_producing_from_miss": int(
            u.produce_form.fillna("").str.contains("MISS", case=False).sum()),
        "usable_with_ip_reported": int((u.ip_oil.notna() | u.ip_gas.notna()).sum()),
        "usable_spud_year_quantiles": u.spud_year.quantile([0, .1, .5, .9, 1]).round(0).to_dict(),
        "usable_extent_km": [float(u.x_km.max() - u.x_km.min()),
                             float(u.y_km.max() - u.y_km.min())],
        "usable_washout_frac_median": float(u.washout_frac.median()),
        "medians_in_miss": {c: float(inm_logs[c].median())
                            for c in ["GR", "DEN", "NPHI", "RDEEP", "DT", "PE"]},
        "frac_miss_samples_rdeep_lt_5ohmm": float((inm_logs.RDEEP.dropna() < 5).mean()),
        "wells_flagged_unit_conflict": int(inv.qc_flags.fillna("").str.contains("says").sum()),
        "unmapped_mnemonics_in_ge5_files": int((tab[tab.canonical == ""].n_files >= 5).sum()),
    }
    (OUT / "audit_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
