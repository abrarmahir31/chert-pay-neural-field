# Real-data test (rule D24b) and exploratory diagnostics

## Confirmatory result (pre-registered; `results/real/evaluation.json`)
Lab PC run, scale_up config, 10 seeds, spatially blocked 5-fold CV, 378 producers vs 47 dry
holes scored, 2,000 stratified bootstrap resamples (seed 20261112).

| Method | AUC | 95 % interval |
|---|---|---|
| Supervised gradient boosting (best baseline) | 0.780 | 0.710 to 0.847 |
| Supervised MLP | 0.764 | 0.688 to 0.838 |
| Archie inversion, well by well | 0.726 | 0.643 to 0.801 |
| Fixed-parameter Archie | 0.686 | 0.597 to 0.767 |
| Fixed-parameter Simandoux | 0.684 | 0.597 to 0.763 |
| Dual-porosity inversion, well by well | 0.660 | 0.572 to 0.745 |
| Archie neural field (PRIMARY entry) | 0.643 | 0.563 to 0.720 |
| Archie inversion, one global m | 0.629 | 0.547 to 0.706 |
| Dual-porosity neural field (SECOND entry) | 0.573 | 0.486 to 0.658 |

Paired difference to the best baseline, Bonferroni interval (two entries): primary -0.136
(-0.228 to -0.042); second -0.207 (-0.312 to -0.100). **Verdict: fail.** Both entries are
significantly worse than the best baseline.

Blind curve reconstruction (curve hidden on held-out wells), RMSE / SD of the curve: sonic 0.81
to 1.10, PE 1.33 to 1.45, shallow resistivity 1.9 to 3.6 with bias +0.5 to +1.1 log10 units.
No method predicts a hidden curve better than its mean.

## Exploratory diagnostics (post hoc; `results/real/diagnostics_exploratory.json`)
Produced by `scripts/diagnose_real.py` from saved outputs and descriptive log statistics.
Nothing was refitted. These observations generate hypotheses; they are not tests.

1. **Raw single features beat every inversion.** Mean density-neutron porosity alone gives AUC
   0.755; LOW mean deep resistivity alone gives 0.745 (high resistivity: 0.255). Producers are
   the porous, low-resistivity wells. Any resistivity-saturation model that reads low
   resistivity as water works against the signal, which is the low-resistivity-pay problem
   itself, now measured on 425 labelled wells.
2. **Per-fold AUC is very uneven for the label-free methods** (Archie field: 0.79, 0.77, 0.41,
   0.81, 0.53 across folds; fixed Archie 0.47 to 0.93) and steadier for the supervised model
   (0.63 to 0.80). Performance depends strongly on area.
3. **The deep ensemble carries almost no spread.** AUC per ensemble member is identical to
   three decimals for all Archie runs (for example 0.642 to 0.645 for the field); only the
   dual-porosity field varies (0.54 to 0.62). Different seeds converge to the same solution, so
   ensemble spread is not a usable uncertainty measure here; the uncertainty that matters is
   between model families.
4. The field and well-by-well Archie scores are correlated (Spearman 0.73) but neither tracks
   the supervised score (0.09 and 0.20): the supervised model uses different information
   (it correlates with low gamma ray, -0.47, which the pay indicator ignores).
5. One labelled producer (KID 1025714888) has no physics-based score (no sample with density,
   neutron and deep resistivity together in the window); hence 378 of 379.
