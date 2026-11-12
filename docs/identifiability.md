# Identifiability study on the synthetic benchmark (rule D20)

Source: `results/identifiability/runs.csv` and `summary.json`, produced by
`make identifiability` (`scripts/run_identifiability.py`, `configs/cpu_small.yaml`; benchmark
seeds 0, 1, 2; optimiser seed 1000 + seed; 6,000 Adam steps; convergence checked at 3k, 10k
and 30k steps before the suite was run). 60 wells x 200 samples, dual-porosity truth, real
curve coverage, unknown per-well flushing exponent, Rmf known to within 15 %.

## Verdict of the pre-registered rule: outcome 2
| Parameter | Base case, seeds 0 / 1 / 2: r | RMSE / SD(true) | Seeds passing | Separable |
|---|---|---|---|---|
| m | 0.93 / 0.87 / 0.92 | 0.47 / 0.57 / 0.41 | 2 of 3 | **yes (narrowly)** |
| n | 0.10 / 0.44 / 0.04 | 3.3 / 2.5 / 3.7 | 0 of 3 | **no** |
| f_micro | 0.52 / 0.43 / 0.72 | 1.5 / 2.7 / 1.2 | 0 of 3 | **no** |

Null control (true n constant): the model still produces an n field with SD 0.153 against a
limit of 0.054. **Failed**: spatial structure in an estimated n map would be an artefact.

## Diagnostics (means over 3 seeds; cannot change the verdict)
| Experiment | m: r | m: RMSE/SD | total Sw RMSE | BVH r | pay vs wet AUC |
|---|---|---|---|---|---|
| base (m, n, f_micro fields) | 0.91 | 0.48 | 0.113 | 0.92 | 0.95 |
| n fixed at 1.9 | 0.90 | 0.52 | 0.129 | 0.92 | 0.95 |
| n one learned scalar | 0.91 | 0.52 | 0.122 | 0.92 | 0.95 |
| n and f_micro fixed, m only | 0.76 | 0.94 | 0.116 | 0.92 | 0.97 |
| flushing exponent and Rmf exactly known | 0.95 | 0.35 | 0.109 | 0.91 | 0.99 |
| flushing exponent fixed at its mean, header Rmf trusted | 0.91 | 0.51 | 0.115 | 0.90 | 0.99 |
| no shallow resistivity | 0.76 | 0.78 | 0.182 | 0.87 | 0.90 |
| noise doubled | 0.85 | 0.70 | 0.157 | 0.84 | 0.94 |
| plain Archie model (n = 2, no micro-porosity) on dual-porosity truth | 0.10 | 2.18 | 0.420 | 0.75 | 0.80 |
| Archie truth, Archie model (m, n) | 0.92 | 0.80 | 0.165 | 0.95 | 1.00 |

BVH = bulk-volume hydrocarbon. AUC = separation of wells with a hydrocarbon column from wet
wells using the mean estimated BVH of the upper 20 ft.

## Reading
1. **n is not identifiable**, in any variant, including the oracle ones. In the resistivity
   equations n only appears multiplied by log Sw, and Sw is itself unknown at every sample.
   Fixing n changes nothing measurable (rows 1 to 3).
2. **m is recoverable but with thin margin.** It passes at the stated noise with shallow
   resistivity; it would not pass with doubled noise or without the shallow curve
   (RMSE/SD 0.70 and 0.78). Typical error is about 0.07 to 0.12 in m.
3. **f_micro is not recoverable as a map** (biased low by about 0.19) unless the flushing
   behaviour is known exactly, which it never is in practice. It trades off against the
   flushing exponent and macro-pore saturation.
4. **The dual-porosity structure still matters.** With micro-porosity in the model, total Sw
   error is about 0.11 and wet/pay wells separate with AUC 0.95; plain Archie gives Sw error
   0.42 and AUC 0.80. So the rock *properties* and the pay indicator are far better
   constrained than the micro-porosity *parameter* itself.
5. Fixing f_micro at a constant degrades m (row 4): f_micro should stay in the model as a
   weakly constrained nuisance field, reported with its uncertainty but not interpreted.

## Caveats
- The benchmark is generated with the same forward-model family that the inversion uses
  (apart from unknown flushing exponents, offsets and noise). Real rocks will be less kind.
- 60 wells here versus 625 real wells; more wells should help the field, not the per-sample
  degeneracy.
- Rw is taken as known and constant. On real data Rw and m trade off (a constant shift), so
  only *relative* spatial variation of m is defensible without water-zone calibration.

---

# Benchmark v2 (rule D24a): different-family truth, 200 wells, unknown Rw

Source: `results/identifiability_v2/runs.csv`, `summary.json`; `make identifiability-v2`
(seeds 0, 1, 2; optimiser seed 1000 + seed; 4,000 Adam steps). Truth: Waxman-Smits-type
total-porosity resistivity, non-linear neutron, Wyllie sonic, per-well biases on every curve,
washout spikes, unknown Rw with a spatial trend. Inversion: parallel dual-porosity model, n
fixed at 1.8, one global Rw estimated.

## Verdict of the pre-registered rule: m FAILS
| Test | Seeds 0 / 1 / 2 | Threshold | Passing |
|---|---|---|---|
| m, r | 0.60 / 0.15 / 0.50 | >= 0.70 | 0 of 3 |
| m, centred RMSE / SD | 1.05 / 1.48 / 1.30 | <= 0.5 | 0 of 3 |
| m null control, SD(m_hat) | 0.235 / 0.166 / 0.245 | <= 0.106 | 0 of 3 |

With a truly constant m the inversion still returns an m map with as much spread as a real one.

## Diagnostics (means over seeds; single seed for the n and Rw rows)
| Experiment | m: r | m: centred RMSE/SD | total Sw RMSE | BVH r | pay vs wet AUC |
|---|---|---|---|---|---|
| v2 base | 0.42 | 1.28 | 0.21 | 0.89 | 0.93 |
| same-family truth, all other v2 settings | 0.92 | 0.39 | 0.18 | 0.92 | 0.93 |
| plain Archie inversion (no micro-porosity) on v2 truth | 0.73 | 0.75 | 0.19 | 0.93 | 0.97 |
| noise doubled | 0.54 | 1.28 | 0.27 | 0.87 | 0.93 |
| Rw exactly known | 0.64 | 1.00 | 0.17 | 0.92 | 0.95 |
| n fixed 1.6 / 2.0 / 2.2 | 0.61 / 0.58 / 0.51 | 1.03 / 1.06 / 1.08 | 0.24 / 0.20 / 0.19 | 0.91 / 0.91 / 0.91 | 0.91 / 0.91 / 0.90 |

Estimated Rw was 0.024 against a true mean of 0.042 in the base case (biased low by about 40 %).

## Reading
1. **The m map is model-dependent.** With every v2 difficulty except the model family
   (biases, unknown Rw, 200 wells) m is still recovered (r 0.92). Changing only the
   resistivity model family of the truth destroys it. The v1 success was an inverse-crime result.
2. **The v1 advantage of the dual-porosity model was also an artefact.** On the v2 truth the
   plain Archie inversion is as good or better on every measure, including m.
3. **The pay indicator is robust.** Bulk-volume hydrocarbon correlates 0.87 to 0.93 with truth
   and separates hydrocarbon wells from wet wells with AUC 0.90 to 0.97 across all variants,
   model families, noise levels and n choices. Absolute total Sw is poor (RMSE about 0.2).
4. **n choice** (1.6 to 2.2) moves the Sw error (0.19 to 0.24) but hardly the BVH ranking.
5. 200 wells did not rescue m: the degeneracy is per sample and structural, not a data-volume problem.

## Consequence
Neither n, nor f_micro, nor (under model-family uncertainty) m can be claimed as a recovered
spatial field. What the label-free inversion does deliver robustly in these tests is a relative
pay indicator. Caveat: the synthetic wet wells are fully water-bearing, which is an easier
contrast than real dry holes.
