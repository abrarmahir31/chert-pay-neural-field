#!/usr/bin/env python
"""Generate the synthetic benchmark (known truth) used to verify the inversion.

Usage: python scripts/make_synthetic.py --config configs/cpu_small.yaml
Writes data/synthetic/benchmark_seed<seed>.npz (not committed) and
results/synthetic/benchmark_meta_seed<seed>.json (config, seed, summary statistics).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.synthetic.benchmark import SynthConfig, make_benchmark  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/cpu_small.yaml"))
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    sc = SynthConfig(**cfg["synthetic"])
    d = make_benchmark(sc)
    out = ROOT / "data/synthetic"
    out.mkdir(parents=True, exist_ok=True)
    flat = {"xy_km": d["xy_km"], "z_ft": d["z_ft"], "rmf_obs": d["rmf_obs"]}
    for grp in ("obs", "mask", "truth", "clean"):
        flat.update({f"{grp}/{k}": v for k, v in d[grp].items()})
    np.savez_compressed(out / f"benchmark_seed{sc.seed}.npz", **flat)
    t = d["truth"]
    meta = {
        "script": "scripts/make_synthetic.py", "config_file": Path(a.config).name, "seed": sc.seed,
        "config": d["config"], "n_wells": sc.n_wells, "n_samples_per_well": sc.n_samples,
        "wet_wells": int(t["wet_well"].sum()),
        "wells_with": {k: int(v[:, 0].sum()) for k, v in d["mask"].items()},
        "truth_ranges": {k: [float(t[k].min()), float(t[k].max())] for k in ("m", "n", "f_micro")},
        "median_rt_pay_ohmm": float(10 ** np.median(d["clean"]["LRT"][t["sw_macro"] < 0.5])),
        "median_rt_wet_ohmm": float(10 ** np.median(d["clean"]["LRT"][t["sw_macro"] > 0.95])),
    }
    r = ROOT / "results/synthetic"
    r.mkdir(parents=True, exist_ok=True)
    (r / f"benchmark_meta_seed{sc.seed}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: meta[k] for k in ("seed", "n_wells", "wet_wells", "wells_with",
                                           "truth_ranges", "median_rt_pay_ohmm",
                                           "median_rt_wet_ohmm")}))


if __name__ == "__main__":
    main()
