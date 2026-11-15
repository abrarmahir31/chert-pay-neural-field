#!/usr/bin/env python
"""Environment check and timing before the real-data run. Touches NO real logs.

Prints versions, GPU, runs a short fit on a synthetic stand-in of the real data size on the
device the config selects, and extrapolates the run time of `run_real_all.py`.
Usage: python scripts/check_env.py --config configs/scale_up.yaml
"""
from __future__ import annotations

import argparse
import platform
import sys
import time
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from chertfield.data.standin import load_standin  # noqa: E402
from chertfield.model.inversion import InversionConfig, JointInversion  # noqa: E402

N_TRAIN_WELLS, N_SAMPLES, STEPS = 500, 201, 150


def time_fit(d, device, resistivity, fixed):
    cfg = InversionConfig(steps=STEPS, fixed=fixed, resistivity=resistivity, learn_rw=True,
                          device=device)
    m = JointInversion(d["xy_km"], d["obs"], d["mask"], d["rmf_obs"], cfg,
                       log_rmf_prior_sd=d["log_rmf_prior_sd"])
    m.fit()                                   # warm-up (CUDA initialisation, kernels)
    if next(m.parameters()).is_cuda:
        torch.cuda.synchronize()
    t = time.time()
    m.fit()
    if next(m.parameters()).is_cuda:
        torch.cuda.synchronize()
    return (time.time() - t) / STEPS, str(next(m.parameters()).device)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/scale_up.yaml"))
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    r = cfg["real"]
    print("python", platform.python_version(), "|", platform.platform())
    print("torch", torch.__version__, "| cuda available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        print("gpu:", p.name, f"| {p.total_memory / 2**30:.1f} GiB")
    else:
        print("NO CUDA DEVICE VISIBLE: the run will use the CPU (slower, same results pipeline).")
    d = load_standin(n_wells=N_TRAIN_WELLS, n_samples=N_SAMPLES, seed=0)
    dev = cfg.get("device", "cpu")
    ms_a, used = time_fit(d, dev, "archie", {"n": 1.8, "f_micro": 0.0})
    ms_d, _ = time_fit(d, dev, "dual_porosity", {"n": 1.8})
    print(f"device used: {used} | seconds per step: archie {ms_a:.4f}, dual-porosity {ms_d:.4f}")
    if torch.cuda.is_available():
        print(f"peak GPU memory in this test: {torch.cuda.max_memory_allocated() / 2**20:.0f} MiB")
    n_sf = len(r["seeds"]) * 5                       # seeds x folds
    shared = r["steps_train"] + 0.25 * r["steps_test"]   # held-out wells are about 1/4 the size
    per_well = 0.25 * r["steps_test"]
    hide = 5 * len(r.get("hide", [])) * 0.25 * r["steps_test"]
    steps_a = n_sf * (2 * shared + per_well) + 3 * hide      # archie: field, constant, per_well
    steps_d = n_sf * (shared + per_well) + 2 * hide          # dual: field, per_well
    hours = (steps_a * ms_a + steps_d * ms_d) / 3600
    print(f"estimated time for the full real-data run with {Path(a.config).name}: about {hours:.1f} h")
    cpu_ms_a, _ = time_fit(d, "cpu", "archie", {"n": 1.8, "f_micro": 0.0}) if used != "cpu" else (ms_a, "")
    print(f"for reference, CPU seconds per step (archie): {cpu_ms_a:.4f}")
    print("CHECK PASSED")


if __name__ == "__main__":
    main()
