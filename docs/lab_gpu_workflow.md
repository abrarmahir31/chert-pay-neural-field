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

## 1b. Windows 10 native setup (NOT TESTED ON WINDOWS)

Written for the candidate lab PC (Ryzen 7 5700X, 32 GB RAM, Windows 10 Pro 19045). GPU model,
VRAM, free disk and admin rights are not yet known. Nothing below needs admin rights if Python
and Git are installed "for the current user". Run in PowerShell.

1. Install Git for Windows (git-scm.com) and Python 3.11 to 3.13 (python.org, tick "Add to PATH").
2. Clone and create the environment:
```powershell
git clone https://github.com/abrarmahir31/chert-pay-neural-field; cd chert-pay-neural-field
```
```powershell
py -3 -m venv .venv; .venv\Scripts\Activate.ps1
```
   If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
3. PyTorch. With an NVIDIA GPU, check the driver with `nvidia-smi`, then pick the matching
   CUDA wheel index from pytorch.org (example for CUDA 12.4):
```powershell
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cu124
```
   Without an NVIDIA GPU (or to test first): `pip install torch==2.15.0` (CPU). The code falls
   back to CPU automatically (`device: auto`); 8 cores are enough for every run in this repo.
4. Project and tests:
```powershell
pip install -e ".[dev,data]"; python -m pytest -q
```
```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```
5. Data and audit (about 1.6 GB download; about 4 GB of free disk is enough):
```powershell
python scripts/download_data.py; python scripts/audit_pass1.py; python scripts/audit_pass2.py; python scripts/audit_report.py
```
`make` is not available on Windows by default: use the `python scripts/...` form of each
command in the table below (the Makefile targets are one-line wrappers around them).

## 3. One-command runners
Every runner takes `--config` (`CONFIG=` with make). `configs/cpu_small.yaml` is the default;
`configs/scale_up.yaml` is larger (more seeds and steps). `device: auto` uses CUDA when
available and otherwise the CPU.

| Experiment | make | python (all platforms) | Output |
|---|---|---|---|
| Unit tests | `make test` | `python -m pytest -q` | |
| Identifiability v1 (D20) | `make identifiability` | `python scripts/run_identifiability.py --suite v1 --config configs/scale_up.yaml` | `results/identifiability/` |
| Benchmark v2 (D24a) | `make identifiability-v2` | `python scripts/run_identifiability.py --suite v2 --config configs/scale_up.yaml` | `results/identifiability_v2/` |
| Pay benchmark v3 | `make pay-benchmark` | `python scripts/run_identifiability.py --suite v3 --config configs/scale_up.yaml` | `results/pay_indicator_benchmark/` |
| Real data, all entries + evaluation (D24b) | `make real` | `python scripts/run_real_all.py --config configs/scale_up.yaml` | `results/real/` |
| Pipeline self-test on synthetic stand-in | `make real-standin` | `python scripts/run_real_all.py --standin` | `results/standin/` |

CPU cost at the small configuration (4 cores): v2 about 25 min, v3 about 25 min. The real-data
run has not been timed yet; it is the heavy job intended for this machine. Do NOT start it
before the split file `results/splits/spatial_blocks_v1.csv` is in your clone (it is committed).

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
