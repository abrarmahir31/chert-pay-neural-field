"""Synthetic stand-in with the same structure as the real data set (pipeline tests only)."""
from __future__ import annotations

import numpy as np

from chertfield.synthetic.benchmark import SynthConfig, make_benchmark


def load_standin(n_wells: int = 40, n_samples: int = 60, seed: int = 0) -> dict:
    cfg = SynthConfig(n_wells=n_wells, n_samples=n_samples, seed=seed, truth_family="v2",
                      rw_log_sd=0.25, frac_wet_wells=0.15, frac_marginal_wells=0.15)
    d = make_benchmark(cfg)
    t = d["truth"]
    label = np.where(t["wet_well"] | t["marginal_well"], 0, 1)
    fold = np.minimum((d["xy_km"][:, 0] / cfg.extent_km[0] * 5).astype(int), 4)
    return dict(kid=np.array([f"S{i:04d}" for i in range(n_wells)]), xy_km=d["xy_km"],
                obs=d["obs"], mask=d["mask"], rmf_obs=d["rmf_obs"],
                log_rmf_prior_sd=np.full(n_wells, 0.15), label=label, fold=fold,
                extent_km=tuple(cfg.extent_km), truth_bvh=t["bvh"])
