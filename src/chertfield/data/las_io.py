"""Robust LAS reading and per-file summarisation (header items + per-curve statistics)."""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import numpy as np

FT_PER_M = 3.280839895

# Values that vendors use as nulls in addition to the declared NULL.
COMMON_NULLS = (-999.25, -999.0, -9999.0, -99999.0, 999.25, 9999.0, -999.2500)


def read_las(path: str | Path):
    """Read a LAS file with lasio, tolerating header errors and odd encodings."""
    import lasio

    last = None
    for kw in (
        {"ignore_header_errors": True},
        {"ignore_header_errors": True, "encoding": "latin-1"},
        {"ignore_header_errors": True, "engine": "normal"},  # wrapped files
        {"ignore_header_errors": True, "engine": "normal", "encoding": "latin-1"},
        {"ignore_header_errors": True, "encoding": "latin-1", "read_policy": ()},
    ):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return lasio.read(str(path), **kw)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last  # type: ignore[misc]


def _item(section, names):
    for n in names:
        try:
            it = section[n]
        except (KeyError, IndexError):
            continue
        v = it.value if str(it.value).strip() != "" else it.descr
        if v is not None and str(v).strip() != "":
            return str(v).strip(), (it.unit or "").strip()
    return None, ""


def _num(x):
    if x is None:
        return np.nan
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    return float(m.group()) if m else np.nan


def clean_values(v: np.ndarray, null: float | None) -> np.ndarray:
    """Replace declared and common null sentinels with NaN."""
    v = np.asarray(v, dtype=float).copy()
    nulls = set(COMMON_NULLS)
    if null is not None and np.isfinite(null):
        nulls.add(float(null))
    for s in nulls:
        v[np.isclose(v, s, rtol=0, atol=1e-3)] = np.nan
    v[~np.isfinite(v)] = np.nan
    return v


def depth_in_feet(depth: np.ndarray, unit: str) -> tuple[np.ndarray, str]:
    """Convert the index to feet. Returns (depth_ft, flag)."""
    u = (unit or "").upper().strip().strip(".")
    if u in ("M", "METER", "METERS", "METRES", "METRE"):
        return depth * FT_PER_M, "converted_m_to_ft"
    if u in ("F", "FT", "FEET", "FOOT"):
        return depth, "ft"
    return depth, f"unknown_unit:{u}"


def summarise_las(path: str | Path) -> tuple[dict, list[dict]]:
    """Return (file_record, curve_records) for one LAS file. Never raises."""
    path = Path(path)
    rec: dict = {"file_id": path.stem, "parse_ok": False, "error": ""}
    try:
        las = read_las(path)
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"[:200]
        return rec, []
    try:
        W, P = las.well, las.params
        rec["las_version"] = _item(las.version, ["VERS"])[0]
        rec["wrap"] = _item(las.version, ["WRAP"])[0]
        null = _num(_item(W, ["NULL"])[0])
        rec["null"] = null
        for k, names in {
            "api_header": ["API", "UWI"],
            "well_name": ["WELL"],
            "company": ["COMP"],
            "field": ["FLD"],
            "service_company": ["SRVC"],
            "log_date": ["DATE"],
        }.items():
            rec[k] = _item(W, names)[0]
        for k, names in {
            "kb_header": ["EKB", "KB", "EREF", "APD"],
            "gl_header": ["EGL", "GL", "ELEV"],
            "bht_degf": ["BHT", "MRT"],
            "rmf": ["RMF", "RMFS"],
            "rm": ["RM", "RMS"],
            "mud_density": ["DFD", "MUDD"],
            "matrix_density": ["MDEN"],
            "bit_size": ["BS", "BITS"],
        }.items():
            v, _ = _item(P, names)
            if v is None:
                v, _ = _item(W, names)
            rec[k] = _num(v)
        rec["matrix_text"] = _item(P, ["MATR", "MATRIX", "LITH"])[0]
        depth = np.asarray(las.index, dtype=float)
        idx_unit = las.curves[0].unit if len(las.curves) else ""
        depth, dflag = depth_in_feet(depth, idx_unit)
        rec["index_mnemonic"] = las.curves[0].mnemonic if len(las.curves) else ""
        rec["depth_flag"] = dflag
        ok = np.isfinite(depth)
        rec["n_samples"] = int(ok.sum())
        if ok.sum() > 1:
            rec["depth_top_ft"] = float(np.nanmin(depth))
            rec["depth_base_ft"] = float(np.nanmax(depth))
            d = np.diff(depth[ok])
            rec["step_ft"] = float(np.median(np.abs(d)))
            rec["depth_monotonic"] = bool(np.all(d > 0) or np.all(d < 0))
        curves = []
        for c in las.curves[1:]:
            try:
                v = clean_values(c.data, null)
            except (TypeError, ValueError):
                continue
            good = np.isfinite(v)
            cr = {
                "file_id": path.stem,
                "mnemonic": c.mnemonic,
                "orig_mnemonic": c.original_mnemonic,
                "unit": (c.unit or "").strip(),
                "descr": (c.descr or "").strip()[:80],
                "n_valid": int(good.sum()),
            }
            if good.any():
                q = np.nanpercentile(v, [1, 5, 50, 95, 99])
                cr.update(
                    vmin=float(np.nanmin(v)), p01=q[0], p05=q[1], p50=q[2], p95=q[3], p99=q[4],
                    vmax=float(np.nanmax(v)),
                    top_ft=float(np.nanmin(depth[good & ok])) if (good & ok).any() else np.nan,
                    base_ft=float(np.nanmax(depth[good & ok])) if (good & ok).any() else np.nan,
                )
            curves.append(cr)
        rec["n_curves"] = len(curves)
        rec["parse_ok"] = True
        return rec, curves
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"summary {type(e).__name__}: {e}"[:200]
        return rec, []
