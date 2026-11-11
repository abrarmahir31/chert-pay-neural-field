# Forward (tool-response) models and their assumptions

Code: `src/chertfield/physics/forward.py`; tests: `tests/test_forward.py`.

Volumes per sample (sum to 1): total porosity `phi`, shale `vsh`, chert/quartz `v_qtz`,
calcite `v_cal`, dolomite `v_dol`.

| Curve | Model | Zone read | Notes |
|---|---|---|---|
| Bulk density | linear volumetric mixing | flushed (mud filtrate + residual hydrocarbon) | exact for density |
| Neutron (limestone units) | linear volumetric mixing | flushed | approximation: real response is non-linear in sandstone and dolomite |
| Photoelectric (optional) | volumetric cross-section U, Pe = U / electron density | flushed | barite mud not modelled |
| Gamma ray | linear index between per-well clean and shale values | | end-points are per-well nuisance terms (vintage, calibration) |
| Sonic (optional) | Wyllie time-average or Raymer-Hunt-Gardner | | no gas or vug correction |
| Deep resistivity | Archie; Simandoux-type shaly; dual-porosity parallel conduction | uninvaded (Rw, Sw) | see below |
| Shallow resistivity | same models with Rmf and flushed saturation | flushed | invasion depth not modelled |

**Dual-porosity model.** Micro-pores (fraction `f_micro` of porosity) stay water-filled
(capillary-bound) and conduct in parallel with macro-pores that may hold hydrocarbon:
`1/Rt = phi_mic^m / (a Rw) + phi_mac^m Sw_mac^n / (a Rw) [+ Vsh/Rsh]`. With `f_micro = 0`
it reduces to Archie (tested). It is a modelling assumption motivated by the capillary-pressure
evidence for chat microporosity (Watney et al. 2001), not a calibrated law.

**Environmental corrections.** None are applied: curves are taken as delivered. Unknown
corrections, tool calibration and the neutron matrix convention are represented by per-well
additive/multiplicative nuisance terms (`apply_nuisance`) with priors, and probed by
sensitivity analysis (Phase 4). `NEUTRON_MATRIX_SHIFT` gives the approximate prior shift if a
curve was recorded on a sandstone or dolomite matrix.

**End-points.** Textbook mineral and fluid constants in `EndPoints` (to be cited to a log
interpretation chart book in the paper; reference still to verify).

**Known degeneracy.** At one depth, m and Sw (and Rw) trade off exactly in Archie's equation
(`test_archie_single_sample_degeneracy_documented`). Identifiability must come from spatial
sharing, water-bearing intervals, the shallow resistivity and priors; Phase 3 quantifies this
on the synthetic benchmark.
