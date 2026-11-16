# Traceability: every figure and reported number -> source file

All sources are files committed under `results/`. Figures are drawn by `scripts/make_figures.py`.

Figure style: Okabe-Ito colour-blind-safe colours (blue #0072B2, vermillion #D55E00, bluish green
#009E73) with marker shape repeating the colour; Arial (Helvetica / Liberation Sans fallback),
7 to 8.5 pt; widths 90 mm (single column) and 190 mm (double column); vector PDF with embedded
TrueType fonts plus 600 dpi PNG. Figure titles are left to the captions.

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

## Additional numbers used in the manuscript text (`paper/main.tex`)
| Number | Value | Source |
|---|---|---|
| v1 error ratio for m | 0.47 / 0.57 / 0.41 | `results/identifiability/runs.csv` (`base`, `m_rmse_over_sd`) |
| v2 centred error ratio for m | 1.05 / 1.48 / 1.30 | `results/identifiability_v2/runs.csv` (`v2_base`, `m_crmse_over_sd`) |
| v2 sample-level pay-indicator correlation | 0.87 to 0.93 | `results/identifiability_v2/runs.csv` (`bvh_r`, experiment means) |
| v3 Archie field AUC vs wet / vs all dry | 0.95 / 0.86 | `results/pay_indicator_benchmark/runs.csv` (`auc_pay_vs_wet`, `auc_pay_vs_dry`) |
| v3 field vs well-by-well vs global difference | 0.01 to 0.02 | same (`v3_archie_field`, `v3_archie_perwell`, `v3_archie_const`) |
| Benchmark sizes, noise, biases, 10 % wet and 15 % marginal wells | | `scripts/run_identifiability.py` (`V2_SYN`, `V3_SYN`), `src/chertfield/synthetic/benchmark.py` |
| Field architecture (6 octaves, 4 x 128), ensemble of 10 | | `configs/scale_up.yaml`, `results/real/pay_*.json` |
| Bootstrap resamples; Bonferroni level | 2,000; 0.025 per entry | `results/real/evaluation.json` (`bootstrap`, `alpha_per_entry`) |
| Fixed n | 1.8 | `configs/scale_up.yaml` (`real.n_fixed`), DECISIONS.md D23 |
| Blind reconstruction by curve: sonic 0.81 to 1.10, PE 1.33 to 1.45, shallow resistivity 1.9 to 3.6, bias 0.5 to 1.1 | | `results/real/evaluation.json` (`blind_curve_reconstruction_mean`) |
| EXPLORATORY: fold range fixed Archie 0.47 to 0.93, supervised 0.63 to 0.80 | | `results/real/diagnostics_exploratory.json` (`auc_per_fold`) |
| Run time of the registered run | about 12 h (41,744 s) | `results/real/pay_*.json` (`seconds`, summed) |
| Usable wells: neutron matrix assumed | 263 | `results/audit/audit_summary.json` (`usable_nphi_source_counts`) |
| Median spud year of usable wells | 2012 | `results/audit/audit_summary.json` (`usable_spud_year_quantiles`) |
| Dry holes per fold | 9 or 10 | `results/splits/spatial_blocks_v1.json` (`per_fold`) |
| Glick field m 2.36, n about 1.8 | | NOT from this repository: quoted from the KGS report (web pages), AUTHOR CHECK |
| Abstract and conclusions | repeat numbers listed above | |

Checked on 2026-11-16: every citation key in `main.tex` exists in `references.bib` (22 cited),
all figure files exist, labels and references match. The manuscript has NOT been compiled.
