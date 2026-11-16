# User guide: inputs, outputs, options

Every script lives in `scripts/`, is run from the repository root, and reads one YAML
configuration (`--config`, default `configs/cpu_small.yaml`). Results are written under
`results/` as CSV or JSON that record the script, configuration and seeds.

## Configurations (`configs/`)
| File | Purpose |
|---|---|
| `cpu_small.yaml` | default; 3 seeds, moderate step counts; used for the synthetic benchmarks |
| `scale_up.yaml` | the registered real-data run: 10 ensemble members, 10,000 / 5,000 steps |
| `smoke.yaml` | tiny step counts, only to check that an installation works; results meaningless |
| `mnemonics.yaml` | curve-mnemonic normalisation table and plausibility ranges |

Main keys: `device` (`auto`, `cpu`, `cuda`); `field` (`n_frequencies`, `hidden`, `layers`);
`identifiability` (`seeds`, `steps`, `steps_v2`); `real` (`seeds`, `steps_train`, `steps_test`,
`n_fixed`, `rw_nominal`, `rw_prior_log_sd`, `hide`, `bootstrap`, `standin`).

## Scripts
| Script | Input | Output | Options |
|---|---|---|---|
| `download_data.py` | internet access to KGS | `data/raw/kgs/` | `--kaggle` also fetch the Kaggle copy; `--limit N`; `--delay S` |
| `audit_pass1.py` | LAS files | `results/audit/las_files.csv`, `curve_catalog.csv` | none |
| `audit_pass2.py` | LAS files, KGS tables, `configs/mnemonics.yaml` | `results/audit/well_inventory.csv`, `audit_summary.json`, `mnemonic_table.csv`, `data/interim/miss_logs.parquet` | `--frozen-tops` reuse the frozen Mississippian tops |
| `audit_report.py` | audit outputs | `vintage_summary.json`, `premise_check.json` | none |
| `make_synthetic.py` | config | `data/synthetic/*.npz`, `results/synthetic/*.json` | `--config` |
| `run_identifiability.py` | config | `results/identifiability*/runs.csv`, `summary.json`; `results/pay_indicator_benchmark/` | `--suite v1|v2|v3`; `--only name1,name2` |
| `make_splits.py` | well inventory | `results/splits/` | none; refuses to overwrite the frozen split |
| `train_real.py` | `data/interim/miss_logs.parquet`, `results/splits/frozen_wells_v1.csv` | `results/real/pay_<entry>_<spatial>.csv`, `.json`, `recon_*.csv` | `--entry archie|dual`; `--spatial field|per_well|constant`; `--standin` |
| `eval_real.py` | `results/real/pay_*.csv` | `results/real/evaluation.json`, `well_scores.csv` | `--standin` |
| `run_real_all.py` | as above | runs all five inversions, then the evaluation | `--config`, `--standin` |
| `diagnose_real.py` | `results/real/` | `diagnostics_exploratory.json` | none (exploratory) |
| `make_figures.py` | `results/` only | `figures/*.pdf`, `*.png` | none |
| `check_env.py` | config | console: versions, device, time estimate | `--config` |
| `check_references.py` | internet access to Crossref | console | free-text queries or `--doi` |

## Library (`src/chertfield/`)
- `data/las_io.py`, `data/mnemonics.py`: robust LAS reading, mnemonic and unit harmonisation.
- `data/real.py`: the study data set (`load_real`), labels and data fingerprint.
- `data/standin.py`: synthetic stand-in with the structure of the real data set.
- `physics/forward.py`: differentiable tool-response models (see `docs/forward_models.md`).
- `synthetic/benchmark.py`: benchmark generator (`SynthConfig`, `make_benchmark`).
- `model/inversion.py`: `InversionConfig`, `ParamField`, `JointInversion`
  (`fit`, `predict`, `pay_indicator`, `freeze_shared`, `chi2_per_curve`).

## Expected behaviour
- The inversion reproduces the logs closely whatever the parameters are; goodness of fit is not
  evidence for the parameters. Parameter maps must not be interpreted (see the paper).
- `train_real.py` prints `data fingerprint matches reference: True` when the locally built data
  set equals the one the study was frozen on.
- Outputs are deterministic for a given seed on one machine; small numerical differences
  between CPU and GPU are expected.
- Depths are in feet inside the code and data files, as in the source logs.
