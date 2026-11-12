# Lab machine runbook

Machine specs are not yet known, so nothing here assumes a GPU model, VRAM, RAM or admin
rights. Everything runs without admin rights inside a Python virtual environment. Tested on
CPU (Linux, Python 3.13, 4 cores, 15 GB RAM).

## 1. Setup (once)
```bash
git clone https://github.com/abrarmahir31/chert-pay-neural-field
```
```bash
cd chert-pay-neural-field
```
CPU build:
```bash
bash scripts/setup_machine.sh
```
CUDA build (pick the index that matches the driver, see pytorch.org "Get started"):
```bash
TORCH_INDEX=https://download.pytorch.org/whl/cu124 bash scripts/setup_machine.sh
```
The script creates `.venv`, installs pinned packages, prints whether CUDA is visible and runs
the unit tests. On Windows use WSL2, or run the same `pip` commands in a PowerShell venv.

## 2. Data (once, about 1.6 GB, 15 to 25 minutes)
```bash
source .venv/bin/activate && make data && make audit
```
`make audit` must reproduce `results/audit/audit_summary.json` (625 usable wells).

## 3. One-command runners
Every runner takes `CONFIG=`; `configs/cpu_small.yaml` is the default, `configs/scale_up.yaml`
is the GPU configuration. `device: auto` in the config uses CUDA when available.

| Experiment | Command | Output |
|---|---|---|
| Unit tests | `make test` | |
| Synthetic benchmark | `make synthetic CONFIG=configs/scale_up.yaml` | `results/synthetic/` |
| Identifiability study (D20) | `make identifiability CONFIG=configs/scale_up.yaml` | `results/identifiability/` |
| Benchmark v2 (D24a) | `make identifiability-v2 CONFIG=configs/scale_up.yaml` | `results/identifiability_v2/` |
| Real-data training, baselines, ablations | added in Phase 3 and 4 after the Gate decision | |

Approximate CPU cost of the identifiability study at the small configuration: 33 runs of about
50 s each.

## 4. Sending results back
Only small files under `results/` and `figures/` (CSV, JSON, PDF). Never anything under `data/`
(git ignores it) and no model checkpoints.
```bash
git checkout -b results/<machine>-<yyyymmdd>
```
```bash
git add results figures && git commit -m "Results from <machine>: <experiment>, config <name>"
```
```bash
git push -u origin HEAD
```
Each results file records the script, config name and seeds that produced it.
