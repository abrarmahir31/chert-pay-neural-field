#!/usr/bin/env python
"""Audit pass 1: parse every LAS file, write per-file and per-curve summaries.

Outputs (small, header/statistics only, no log samples):
  results/audit/las_files.csv, results/audit/curve_catalog.csv
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.data.las_io import summarise_las  # noqa: E402


def main() -> None:
    files = sorted((ROOT / "data/raw/kgs/las").glob("*.las"))
    with Pool(4) as p:
        out = p.map(summarise_las, files, chunksize=8)
    recs = pd.DataFrame([r for r, _ in out])
    curves = pd.DataFrame([c for _, cs in out for c in cs])
    d = ROOT / "results/audit"
    d.mkdir(parents=True, exist_ok=True)
    recs.to_csv(d / "las_files.csv", index=False)
    curves.to_csv(d / "curve_catalog.csv", index=False)
    print(f"files={len(recs)} parsed_ok={int(recs.parse_ok.sum())} curve_rows={len(curves)}")


if __name__ == "__main__":
    main()
