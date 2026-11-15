# Lab PC runbook: real-data run (rule D24b)

Target machine: Windows, NVIDIA RTX 4060 Ti 16 GB (driver 610.88, CUDA 13.3), about 16 GB RAM,
admin account, project on `E:`. **Nothing here has been tested on Windows or on a GPU**; the
same scripts were run on Linux / CPU only. Each step says how to tell that it worked.

Does it fit? Yes, with a wide margin. The data set is 625 wells x 201 samples; the model has
about 1 million parameters. Expect well under 1 GB of VRAM and under 4 GB of RAM for the run
itself. The audit step is the heaviest on RAM (it reads two KGS tables of 200 to 335 MB as
text; about 6 to 8 GB peak): close other applications for that step.

## 0. Which Windows?
```powershell
(Get-CimInstance Win32_OperatingSystem).Caption
```
The steps are identical for Windows 10 and 11.

## 1. Install (once, PowerShell)
1. Git for Windows (git-scm.com) and Python 3.12 or 3.13, 64-bit (python.org, tick "Add
   python.exe to PATH"). Check: `python --version` and `git --version` print versions.
2. Clone and create the environment:
```powershell
E:; git clone https://github.com/abrarmahir31/chert-pay-neural-field; cd chert-pay-neural-field
```
```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
```
   If activation is refused: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry.
3. PyTorch with CUDA. The pinned version 2.15.0 has exactly one Windows CUDA build, `cu132`
   (checked on the PyTorch wheel index on 15 Nov 2026); your driver reports CUDA 13.3, which
   should be new enough:
```powershell
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cu132
```
4. Project, then unit tests (expect "34 passed"):
```powershell
pip install -e ".[dev,data]"; python -m pytest -q
```

## 2. GPU check and smoke test (about 5 minutes, touches no real logs)
```powershell
scripts\run_lab.bat smoke
```
It prints the GPU name, the device actually used, seconds per step, peak GPU memory and an
**estimated duration of the full run on this machine**, then runs the whole pipeline on a
small synthetic stand-in. Success = `CHECK PASSED` and `SMOKE TEST PASSED`.

- If it prints `NO CUDA DEVICE VISIBLE`: the run still works on the CPU (automatic fallback).
  To fix the GPU instead, run `nvidia-smi` and `python -c "import torch; print(torch.__version__)"`;
  the version must end in `+cu132`, not `+cpu`.
- CPU-only fallback install: `pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu`.

## 3. Data (once; about 1.6 GB download, 20 to 30 minutes)
```powershell
python scripts\download_data.py
```
```powershell
python scripts\audit_pass1.py; python scripts\audit_pass2.py --frozen-tops; python scripts\audit_report.py
```
`--frozen-tops` reuses the Mississippian tops frozen in `results/splits/frozen_wells_v1.csv`,
so a later change of the KGS tops database cannot move the analysis windows. The audit rewrites
files under `results/audit/`; small differences from the committed versions are expected if KGS
updated its tables. **Do not run `scripts/make_splits.py`** (the split is frozen; it refuses anyway).

## 4. The registered run
```powershell
scripts\run_lab.bat full
```
Watch progress in a second window:
```powershell
Get-Content logs\real_run.log -Wait
```
The first line of each of the five parts reads `data fingerprint matches reference: True`.
If it says `False`, let it finish anyway and tell me: it means the logs downloaded on the lab PC
differ from the ones used to freeze the study (I will compare the fingerprints).
The run does, in order: Archie field (primary entry), dual-porosity field (second entry),
Archie and dual-porosity well by well, Archie with one global m, then the evaluation.

Time: about 8 hours on 4 CPU cores (measured on Linux). On the 4060 Ti I expect roughly 1.5 to
4 hours, but that is a guess; use the estimate printed by the smoke step. The run can be left
overnight. If it is interrupted, start `scripts\run_lab.bat full` again (finished parts are
recomputed; there is no resume).

Do not change any setting between the smoke test and the full run, and do not re-run with
different settings after seeing `evaluation.json`.

## 5. Send the results back
```powershell
git checkout -b results/lab-4060ti-20261115
```
```powershell
git add results/real results/audit; git commit -m "Real-data run D24b on lab PC, scale_up config"
```
```powershell
git push -u origin HEAD
```
That branch then contains everything needed for the write-up:
- `results/real/evaluation.json`: AUC and 95 % bootstrap interval per method, best baseline,
  Bonferroni interval of each entry's difference, the D24b verdict, blind curve reconstruction;
- `results/real/well_scores.csv`: per-well scores of every method and ensemble spread;
- `results/real/pay_*.csv`, `recon_*.csv`, `pay_*.json`: raw per-seed outputs, device, versions, fingerprint;
- `results/real/run_logs/`: `check_env.log` and `real_run.log`;
- `results/audit/`: so that I can see whether the rebuilt inventory differs.
No raw logs are included (git ignores `data/`). If the push fails, send me the `results/real`
folder as a zip instead.

## Other runners (all platforms)
| Experiment | Command | Output |
|---|---|---|
| Identifiability v1 | `python scripts/run_identifiability.py --suite v1 --config configs/cpu_small.yaml` | `results/identifiability/` |
| Benchmark v2 | `python scripts/run_identifiability.py --suite v2 --config configs/cpu_small.yaml` | `results/identifiability_v2/` |
| Pay benchmark v3 | `python scripts/run_identifiability.py --suite v3 --config configs/cpu_small.yaml` | `results/pay_indicator_benchmark/` |
| Environment check only | `python scripts/check_env.py --config configs/scale_up.yaml` | console |

Linux or WSL: `bash scripts/setup_machine.sh`, then `make data && make audit && make real CONFIG=configs/scale_up.yaml`.
