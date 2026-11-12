# Decisions log

| # | Date | Decision | Reason |
|---|---|---|---|
| D1 | 2026-11-11 | Use original KGS LAS files, not the Kaggle CSV. | Kaggle copy is a lossy CSV (single resistivity, no neutron matrix, no caliper, no elevations). All 1,030 Kaggle ids are KGS LAS file ids; KGS terms allow reuse with citation. |
| D2 | 2026-11-11 | Unit of analysis is the well (KGS KID, 765), not the LAS file (1,054). | Several files per well; files merged on a 0.5 ft grid, the file with most samples taking precedence. |
| D3 | 2026-11-11 | Mississippian top = shallowest KGS Mississippian-system pick; wells without picks get an IDW (k=8, power 2) subsea interpolation from 4,948 picked Barber wells. | Leave-one-out MAE 21 ft; documented in docs/data_audit.md. |
| D4 | 2026-11-11 | Neutron curves with unlabelled matrix are assumed limestone. | Identical to the limestone-labelled curve in 135/136 wells carrying both. |
| D5 | 2026-11-11 | Bulk density back-computed from limestone density porosity (2.71 / 1.0 g/cc) when RHOB is missing (81 usable wells). | Recovers wells; flagged in `den_source`. |
| D6 | 2026-11-11 | "Usable" = at least 20 ft of co-located GR + density + neutron + deep resistivity inside the Mississippian. | Minimum set for a joint density-neutron-resistivity inversion. |
| D7 | 2026-11-11 | CPU-only environment (4 cores, 15 GB RAM, no GPU): plan small MLP field (about 4 x 128), ensembles of 5, mini-batches of samples. | Hardware. To be confirmed in Phase 3. |
| D8 | 2026-11-11 | Dedicated cloud environment `chert-pay-neural-field` with hosts for Kaggle and KGS only. | Keep the Default environment unchanged. |
| D9 | 2026-11-11 | GATE 1 = GO (user). KGS LAS data, 625-well core set. | User decision. |
| D10 | 2026-11-11 | Sonic and PE are OPTIONAL loss terms, masked where absent; no headline result may depend on sonic coverage. | User condition 1. |
| D11 | 2026-11-11 | Neutron matrix / unit convention is an uncertain nuisance parameter (per-well, with documented prior) plus a sensitivity test; stated as a limitation. | User condition 2; the second neutron curve is redundant in 135/136 wells. |
| D12 | 2026-11-11 | Environmental corrections unknown per file: add sensitivity analysis (perturbed per-well offsets/gains), list as limitation. | User condition 3. |
| D13 | 2026-11-11 | Validation hierarchy: (a) blind-well + spatially blocked curve reconstruction, (b) production status (397 Mississippian producers vs 47 dry) with AUC and bootstrap CIs, (c) School Trust 4-4 core as a single-well case study only. | User condition 4. |
| D14 | 2026-11-11 | Premise check (producers less resistive than dry holes) is motivation only, never evidence for the method. | User condition 5. |
| D15 | 2026-11-11 | One YAML config drives every training/ablation run; `configs/cpu_small.yaml` runs here, `configs/scale_up.yaml` for a GPU machine; no code changes between them. | User condition 6. |
| D16 | 2026-11-11 | Lab-GPU workflow: setup script, one-command runner per experiment, results pushed to a branch (small files only). Machine specs unknown: nothing assumed. | User condition 7. |
| D17 | 2026-11-11 | References verified by web search only; DOIs recorded only when seen in a search result. Entries recalled from memory are marked TODO-VERIFY. | api.crossref.org / doi.org are not allowed hosts. || D18 | 2026-11-11 | GATE 2 = APPROVED (user). Claim wording "to our knowledge"; primary journal Computers & Geosciences, alternatives Mathematical Geosciences and Petroleum Science. Wider full-text check before submission, read-status recorded in docs/literature_gap.md. | User decision. |
| D19 | 2026-11-11 | School Trust 4-4 core = labelled case study only (digitised values; core saturations are not in-situ). | User condition 5. |
| D20 | 2026-11-11 | PRE-REGISTERED DECISION RULE (written before any inversion training; see section below). | User condition 3. || D21 | 2026-11-11 | D20 result: OUTCOME 2. m separable (2 of 3 seeds, narrow margin); n not separable (0 of 3; null control failed); f_micro not separable (0 of 3). Spatially varying m AND n claim is dropped. Stopped for user approval of the reframed claim. | results/identifiability/summary.json, docs/identifiability.md. || D22 | 2026-11-12 | Reframed claim APPROVED (user): spatially varying m (RELATIVE variation only on real data, never absolute values), n fixed from published chat values with sensitivity analysis propagated into Sw and pay uncertainty, f_micro an uninterpreted nuisance field, headline = bulk-volume-hydrocarbon (pay) maps with ensemble uncertainty. Wording "to our knowledge". | User decision. |
| D23 | 2026-11-12 | n fixed at 1.8 (Glick field chat value quoted in KGS Open-File Report 2002-50); sensitivity range 1.6 to 2.2. | Only published chat n found; original source (Duren 1967) unverified, so the KGS report is cited. |
| D24 | 2026-11-12 | Benchmark v2 criteria and real-data rule pre-registered (sections below) before any v2 run or real-data fit. | User conditions 3 and 4. |
Pending (owner: user): review of benchmark v2 results; lab PC specs; LICENSE choice (Phase 6).


## D20: pre-registered identifiability decision rule (fixed before any training run)

Test bed: synthetic benchmark (`chertfield.synthetic.benchmark`), 60 wells x 200 samples,
dual-porosity truth, noise as in `SynthConfig.noise`, curve coverage as in the real data
(shallow resistivity in about 95 % of wells, sonic about 20 %, PE about 41 %), per-well neutron
and density offsets, per-well mud-filtrate resistivity known only to within 15 %, and a per-well
flushing exponent that the model does not know. Three benchmark seeds (0, 1, 2).

Metric, per parameter p in {m, n, f_micro}, at well level (model value at the well location
versus true value): Pearson r and RMSE / SD(true).

A parameter is declared **separable** only if, in the realistic base case, in at least 2 of 3
seeds: r >= 0.70 AND RMSE <= 0.5 x SD(true). In addition a null control must pass: when the
true n is constant, the estimated n field must not show structure
(SD(n_hat) <= 0.5 x SD(n_true of the base case)).

Outcomes:
1. m and n both separable -> proceed with the spatially varying m and n claim.
2. m separable, n not -> propose "n fixed, m spatially varying"; STOP for user approval.
3. neither separable -> propose a field of ONE effective resistivity parameter; STOP for approval.
The thresholds will not be changed after seeing results. Oracle variants (known flushing
exponent, exact Rmf, no noise) are diagnostic only and cannot rescue a failed base case.
Rock-property recovery (porosity, total Sw, bulk-volume hydrocarbon) is reported alongside
but does not enter the rule.


## D24a: benchmark v2 (pre-registered before running)

Changes against v1: (a) truth from a DIFFERENT model family than the inversion: resistivity from
a Waxman-Smits-type total-porosity model with excess conductivity tied to micro-porosity (the
inversion keeps the parallel dual-porosity model), non-linear neutron matrix effect, Wyllie
sonic with compaction factor (inversion: Raymer), per-well environmental biases on every curve
(neutron gain, density offset, deep and shallow resistivity offsets) and washout spikes;
(b) 200 wells; doubled-noise variant; (c) Rw unknown: one global value drawn per benchmark
(log-normal, sigma 0.25 around the nominal) with a smooth +/-10 % spatial trend, estimated by
the inversion as one scalar with a prior; (d) null control for m (true m constant).
Inversion: n fixed at 1.8 (true n varies around 1.9), f_micro field as nuisance.

Because only RELATIVE variation of m is claimed (D22), the metric for m is Pearson r and the
MEAN-CENTRED RMSE / SD(true) at well level.
m passes v2 only if, in the base case, at least 2 of 3 seeds have r >= 0.70 and centred
RMSE/SD <= 0.5, AND the m null control passes (SD(m_hat) <= 0.5 x mean SD(m_true) of the base
case, in at least 2 of 3 seeds). Reported but not part of the rule: doubled noise, n
sensitivity (1.6, 2.0, 2.2), known-Rw and same-family diagnostics, total Sw and BVH errors,
pay-vs-wet AUC. Thresholds will not be changed after seeing results. Failures are reported.

## D24b: real-data rule (pre-registered before any real-data fit)

Primary test: well-level pay-vs-dry classification by KGS production status (Mississippian
producers vs dry holes; 397 vs 47 among usable wells), score = model pay indicator for the
upper Mississippian, evaluated ONLY on wells in held-out spatial blocks (spatially blocked
cross-validation, split frozen in results/splits/ before training). Metric: ROC AUC with
bootstrap 95 % confidence intervals (wells resampled, stratified).
Baselines, same folds and same score definition where applicable: (1) Archie, fixed parameters;
(2) Simandoux or dual-water, fixed parameters; (3) well-by-well physics-informed inversion
(no spatial field); (4) plain ANN or XGBoost trained on the production labels of training
blocks. Secondary: blind-well curve reconstruction error.
Decision: the neural field "beats" the best baseline only if the 95 % bootstrap interval of the
paired AUC difference (field minus best baseline) excludes zero. Otherwise STOP and report to
the user; the paper then becomes an identifiability and negative-results study.
No hyper-parameter is tuned on held-out blocks. Production labels are never used to train the
neural field.
