#!/usr/bin/env python
"""Freeze the spatially blocked cross-validation split (run ONCE, before any real-data fit).

Wells are grouped into square blocks; whole blocks are assigned to folds (seeded, greedy
balance of dry-hole and well counts). Output: results/splits/spatial_blocks_v1.csv and .json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.data.real import well_labels  # noqa: E402

BLOCK_KM, N_FOLDS, SEED = 8.0, 5, 20261112


def main() -> None:
    out = ROOT / "results/splits/spatial_blocks_v1.csv"
    if out.exists():
        sys.exit(f"{out} already exists: the split is frozen and will not be regenerated.")
    inv = pd.read_csv(ROOT / "results/audit/well_inventory.csv", dtype={"KID": str}).set_index("KID")
    inv = inv[inv.usable_min].copy()
    inv["label"] = well_labels(inv)
    bx = np.floor((inv.x_km - inv.x_km.min()) / BLOCK_KM).astype(int)
    by = np.floor((inv.y_km - inv.y_km.min()) / BLOCK_KM).astype(int)
    inv["block"] = bx.astype(str) + "_" + by.astype(str)
    g = inv.groupby("block").agg(n=("label", "size"), dry=("label", lambda s: int((s == 0).sum())))
    rng = np.random.default_rng(SEED)
    order = g.sample(frac=1.0, random_state=rng.integers(1 << 31)).sort_values(
        ["dry", "n"], ascending=False, kind="stable")
    load = np.zeros((N_FOLDS, 2))
    fold = {}
    for b, r in order.iterrows():           # greedy: fewest dry holes first, then fewest wells
        k = int(np.lexsort((load[:, 1], load[:, 0]))[0])
        fold[b] = k
        load[k] += (r.dry, r.n)
    inv["fold"] = inv.block.map(fold)
    inv[["block", "fold", "label"]].to_csv(out)
    tab = inv.groupby("fold").label.value_counts().unstack(fill_value=0)
    meta = {"script": "scripts/make_splits.py", "seed": SEED, "block_km": BLOCK_KM,
            "n_folds": N_FOLDS, "n_wells": int(len(inv)), "n_blocks": int(len(g)),
            "labels": {"1": "Mississippian producer", "0": "dry hole", "-1": "unlabeled"},
            "label_counts": {str(k): int(v) for k, v in inv.label.value_counts().items()},
            "per_fold": {str(k): {str(c): int(v) for c, v in r.items()} for k, r in tab.iterrows()}}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
