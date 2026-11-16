# Traceability: every figure and reported number -> source file

All sources are files committed under `results/`. Figures are drawn by `scripts/make_figures.py`.

## Figures
| Figure | Content | Source file(s) | Produced by |
|---|---|---|---|
| Fig. 1 | Study wells, labels, 8 km blocks | `results/splits/frozen_wells_v1.csv` | `scripts/make_splits.py` (seed 20261112) |
| Fig. 2a | Correlation of recovered vs true m, n, f_micro per seed | `results/identifiability/runs.csv` (experiment `base`), `results/identifiability_v2/runs.csv` (`v2_same_family`, `v2_base`) | `scripts/run_identifiability.py --suite v1 / v2`, seeds 0,1,2 |
| Fig. 2b | Null controls and limits | `results/identifiability/runs.csv` (`null_n`), `results/identifiability/summary.json`, `results/identifiability_v2/summary.json` | same |
| Fig. 3 | Synthetic pay-indicator AUC (v3) | `results/pay_indicator_benchmark/runs.csv` | `scripts/run_identifiability.py --suite v3` |
| Fig. 4 | Real-data AUC with 95 % intervals | `results/real/evaluation.json` | `scripts/train_real.py`, `scripts/eval_real.py` (lab PC, scale_up, 10 seeds; bootstrap seed 20261112) |
| Fig. 5 | EXPLORATORY per-fold AUC and single-feature AUC | `results/real/diagnostics_exploratory.json`, `results/real/evaluation.json` | `scripts/diagnose_real.py` |

## Numbers quoted in the text
| Number | Value | Source |
|---|---|---|
| LAS files in index / downloaded / parsed | 1,054 / 1,053 / 1,050 | `results/audit/audit_summary.json` |
| Wells; usable wells (core curve set) | 765; 625 | `results/audit/audit_summary.json` |
| Wells with shallow-or-medium resistivity / PE / sonic | 594 / 259 / 124 | `results/audit/audit_summary.json` |
| Tops: picked / interpolated; leave-one-out MAE | 615 / 150; 21 ft | `results/audit/audit_summary.json` |
| Neutron curves identical where both exist | 135 of 136 wells | `results/audit/audit_summary.json` |
| Premise (descriptive): producers 6.0 vs dry 9.8 ohm.m, p = 2.6e-6 | | `results/audit/premise_check.json` |
| Folds, blocks, labels (379 / 47 / 199) | 5, 47 | `results/splits/spatial_blocks_v1.json` |
| v1: m r 0.93 / 0.87 / 0.92; n, f_micro fail; null n SD 0.153 vs 0.054 | | `results/identifiability/runs.csv`, `summary.json` |
| v2: m r 0.60 / 0.15 / 0.50; null m SD 0.235 / 0.166 / 0.245 vs 0.106; same-family r 0.92 | | `results/identifiability_v2/runs.csv`, `summary.json` |
| v2: total Sw RMSE about 0.2; Rw 0.024 vs 0.042 | | `results/identifiability_v2/runs.csv` (`sw_total_rmse`, `rw_hat`, `rw_true_mean`) |
| v3: AUC vs all dry 0.82 to 0.86 (inversions), 0.88 (fixed Archie) | | `results/pay_indicator_benchmark/runs.csv` |
| Real data: AUC and intervals of all nine methods | 0.573 to 0.780 | `results/real/evaluation.json` (`auc`) |
| Real data: paired differences -0.136 [-0.228, -0.042], -0.207 [-0.312, -0.100] | | `results/real/evaluation.json` (`paired_difference_vs_best_baseline`) |
| Producers / dry holes scored | 378 / 47 | `results/real/evaluation.json` |
| Blind curve reconstruction RMSE/SD | 0.81 to 3.6 | `results/real/evaluation.json` (`blind_curve_reconstruction_mean`) |
| EXPLORATORY: single-feature AUC 0.755, 0.745, 0.653 | | `results/real/diagnostics_exploratory.json` |
| EXPLORATORY: per-fold AUC 0.41 to 0.81 (Archie field) | | `results/real/diagnostics_exploratory.json` (`auc_per_fold`) |
| EXPLORATORY: ensemble member AUC 0.642 to 0.645 | | `results/real/diagnostics_exploratory.json` (`auc_single_ensemble_member`) |
| Run provenance (device, versions, fingerprint) | | `results/real/pay_*.json`, `results/real/run_logs/` |

To be extended when the manuscript text is written (every new number gets a row).
