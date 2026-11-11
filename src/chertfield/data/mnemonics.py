"""Curve-mnemonic normalisation and unit harmonisation."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

CONFIG = Path(__file__).resolve().parents[3] / "configs" / "mnemonics.yaml"


@lru_cache(maxsize=4)
def load_table(path: str | None = None) -> dict:
    with open(path or CONFIG) as f:
        return yaml.safe_load(f)


def alias_map(table: dict | None = None) -> dict[str, tuple[str, int]]:
    """ALIAS -> (canonical, priority). Lower priority value = preferred."""
    table = table or load_table()
    out: dict[str, tuple[str, int]] = {}
    for canon, spec in table["canonical"].items():
        for i, a in enumerate(spec["aliases"]):
            out.setdefault(a.upper(), (canon, i))
    return out


def base_mnemonic(m: str) -> str:
    """Upper-case and strip lasio duplicate suffixes (':1') and vendor run suffixes ('_1')."""
    m = (m or "").upper().strip()
    m = re.sub(r":\d+$", "", m)
    return m


def classify(mnemonic: str, table: dict | None = None) -> tuple[str | None, int]:
    amap = alias_map(table)
    m = base_mnemonic(mnemonic)
    if m in amap:
        return amap[m]
    m2 = re.sub(r"[_.]?\d$", "", m)  # e.g. GR_1, RHOB2
    if m2 != m and m2 in amap:
        c, p = amap[m2]
        return c, p + 100
    return None, -1


def neutron_matrix_from_text(*texts: str | None) -> str | None:
    t = " ".join(x for x in texts if isinstance(x, str)).upper()
    # coded header item, e.g. "MATR. 0.0000: NEUTRON MATRIX (0=LIME,1=SAND,2=DOLO)"
    code = re.search(r"(-?\d+(?:\.\d+)?)\s.*0=LIME,\s*1=SAND,\s*2=DOLO", t)
    if code:
        return {0: "LS", 1: "SS", 2: "DOL"}.get(int(float(code.group(1))))
    if re.search(r"LIME|\bLS\b|LMST|2\.71", t):
        return "LS"
    if re.search(r"SAND|\bSS\b|2\.65", t):
        return "SS"
    if re.search(r"DOLO|\bDOL\b|2\.87", t):
        return "DOL"
    return None


def to_fraction(v: np.ndarray, unit: str) -> tuple[np.ndarray, str]:
    """Porosity to v/v. Uses the declared unit, falls back on magnitude. Returns (v, how)."""
    u = (unit or "").upper().strip()
    finite = v[np.isfinite(v)]
    p95 = np.percentile(finite, 95) if finite.size else np.nan
    if u in ("PU", "%", "PERC", "PERCENT", "P.U.", "PCT", "CFCF%"):
        if np.isfinite(p95) and p95 < 1.0:
            return v, "unit_says_percent_values_fractional"
        return v / 100.0, "percent"
    if u in ("DECP", "DEC", "V/V", "FRAC", "CFCF", "FT3/FT3", "M3/M3", "DECIMAL", "FRACTION"):
        if np.isfinite(p95) and p95 > 2.0:
            return v / 100.0, "unit_says_fraction_values_percent"
        return v, "fraction"
    if np.isfinite(p95) and p95 > 1.5:
        return v / 100.0, "guessed_percent"
    return v, "guessed_fraction"


def harmonise(canon: str, v: np.ndarray, unit: str, table: dict | None = None):
    """Convert a classified curve to canonical units and mask implausible values.

    Returns (values, flag)."""
    table = table or load_table()
    kind = table["canonical"][canon]["kind"]
    rng = table["valid_range"]
    v = np.asarray(v, dtype=float).copy()
    flag = ""
    u = (unit or "").upper().strip()
    if kind == "phi":
        v, flag = to_fraction(v, unit)
        lo, hi = rng["phi"]
    elif kind == "res":
        lo, hi = rng["res"]
    elif kind == "rhob":
        if u in ("KG/M3", "K/M3"):
            v, flag = v / 1000.0, "kgm3_to_gcc"
        lo, hi = rng["RHOB"]
    elif kind == "dt":
        if u in ("US/M", "USEC/M", "US/METER"):
            v, flag = v * 0.3048, "usm_to_usft"
        lo, hi = rng["DT"]
    elif kind == "cali":
        if u in ("MM",):
            v, flag = v / 25.4, "mm_to_in"
        elif u in ("CM",):
            v, flag = v / 2.54, "cm_to_in"
        lo, hi = rng["CALI"]
    elif kind == "gr":
        lo, hi = rng["GR"]
    elif kind == "pe":
        lo, hi = rng["PE"]
    else:
        return v, flag
    v[(v < lo) | (v > hi)] = np.nan
    return v, flag
