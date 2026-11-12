#!/usr/bin/env python
"""One command for the real-data test (rule D24b): all inversion entries, then evaluation.

Runs, in order: archie/field (primary entry), dual/field (second entry), archie/per_well and
dual/per_well (well-by-well baselines), archie/constant, then scripts/eval_real.py.
Usage: python scripts/run_real_all.py --config configs/cpu_small.yaml [--standin]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = [("archie", "field"), ("dual", "field"), ("archie", "per_well"), ("dual", "per_well"),
        ("archie", "constant")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/cpu_small.yaml"))
    ap.add_argument("--standin", action="store_true")
    a = ap.parse_args()
    extra = ["--standin"] if a.standin else []
    for entry, spatial in RUNS:
        print(f"== {entry} / {spatial}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/train_real.py"), "--config", a.config,
                        "--entry", entry, "--spatial", spatial, *extra], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/eval_real.py"), "--config", a.config, *extra],
                   check=True)


if __name__ == "__main__":
    main()
