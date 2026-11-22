# chert-pay-neural-field

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24433837.svg)](https://doi.org/10.5281/zenodo.24433837)

Code, decision log and results for the paper

> **Identifiability before interpretation: an inverse-crime test of physics-informed
> petrophysical inversion across 625 wells of Mississippian chat** (Abrar Mahir, 2026).

A label-free physics-informed inversion of well logs (a spatial neural field of rock-physics
parameters plus differentiable tool-response models) is tested with decision rules fixed in
advance. Result: the parameters are not identifiable, an apparent recovery of the cementation
exponent vanishes when the synthetic truth comes from a different model family, and on real
data the method does not beat simple baselines. The repository is the reproducible record of
that test. Start with `docs/identifiability.md` and `docs/real_data_results.md`.

## Install
Python 3.11 to 3.13. Linux, macOS or Windows.
```bash
git clone https://github.com/abrarmahir31/chert-pay-neural-field
```
```bash
cd chert-pay-neural-field
```
```bash
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
```
```bash
pip install -e ".[dev,data]"
```
```bash
python -m pytest -q
```
The tests (34) use tiny synthetic data only. For a CUDA build of PyTorch and for Windows see
`docs/lab_gpu_workflow.md`. Dependencies are pinned in `pyproject.toml`.

## Quick start without any data
```bash
python scripts/make_figures.py
```
redraws every figure of the paper from the committed result files (seconds).
```bash
python scripts/run_real_all.py --standin --config configs/smoke.yaml
```
runs the complete real-data pipeline on a small synthetic stand-in (about one minute).
A step-by-step walk-through is in `docs/tutorial.md`; all inputs, outputs and options are
described in `docs/user_guide.md`.

## Reproduce the paper
| Paper item | Command | Output | Time |
|---|---|---|---|
| Data (public KGS logs, about 1.6 GB) | `python scripts/download_data.py` | `data/raw/` (not committed) | 20 to 30 min |
| Data audit, Section 2 | `python scripts/audit_pass1.py`, `python scripts/audit_pass2.py --frozen-tops`, `python scripts/audit_report.py` | `results/audit/` | 2 min |
| Fig. 2 (part), identifiability v1 | `python scripts/run_identifiability.py --suite v1` | `results/identifiability/` | 30 min, 4 CPU cores |
| Fig. 2 (part), benchmark v2 | `python scripts/run_identifiability.py --suite v2` | `results/identifiability_v2/` | 25 min |
| Fig. 3, benchmark v3 | `python scripts/run_identifiability.py --suite v3` | `results/pay_indicator_benchmark/` | 25 min |
| Fig. 4, Table 1, real-data test | `python scripts/run_real_all.py --config configs/scale_up.yaml` | `results/real/` | about 12 h (one consumer GPU or 8 CPU cores) |
| Fig. 5, exploratory diagnostics | `python scripts/diagnose_real.py` | `results/real/diagnostics_exploratory.json` | seconds |
| All figures and the graphical abstract | `python scripts/make_figures.py` | `figures/` | seconds |
| Manuscript | `pdflatex main && bibtex main && pdflatex main && pdflatex main` in `paper/` | `paper/main.pdf` | |

`make` targets wrap the same commands on Linux and macOS (`make test`, `make data`,
`make audit`, `make identifiability`, `make identifiability-v2`, `make pay-benchmark`,
`make real`). The spatial split and the study wells are frozen in `results/splits/`; do not
regenerate them. `docs/traceability.md` maps every figure and number of the paper to its
source file, and `results/MANIFEST.md` lists every result file with the script, configuration
and seed that produced it.

## Computational requirements
CPU only is sufficient. Memory: about 8 GB for the audit step, under 4 GB otherwise. Disk:
about 4 GB including the downloaded logs. A GPU is used automatically when present
(`device: auto`) but brings little speed-up, because the problem is small (under 100 MB of GPU
memory).

## Repository layout
`src/chertfield/` library (data, physics, model, synthetic) · `scripts/` entry points ·
`configs/` YAML configurations · `tests/` unit tests · `results/` machine-written results ·
`figures/` · `paper/` manuscript · `docs/` documentation · `DECISIONS.md` timestamped decision
log including the pre-registered rules (D20, D24a, D24b, D27, D28) · `PROGRESS.md`.

## Data and terms
No raw data are stored here. Logs, headers, tops and core analyses are public records of the
Kansas Geological Survey (KGS) and are downloaded from its servers by
`scripts/download_data.py`. Credit line required by KGS: "The source of this material is the
Kansas Geological Survey website at http://www.kgs.ku.edu/. All Rights Reserved." Details,
including the provenance check of the Kaggle repackaging, are in `data/README.md`.

## Licence
Code: MIT (`LICENSE`). Manuscript, documentation and figures: CC BY 4.0 (`LICENSE-docs.md`).
Third-party data are not relicensed; files under `results/` that carry KGS-derived information
must be reused with the KGS credit line.

## Citation and AI-use note
See `CITATION.cff`. Archived release v1.0.0: https://doi.org/10.5281/zenodo.24433837. The code, analysis and text were produced with extensive assistance from an
AI system under the author's direction; the declaration is in the manuscript and the
full decision record is in `DECISIONS.md`.
