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
| D24 | 2026-11-12 | Benchmark v2 criteria and real-data rule pre-registered (sections below) before any v2 run or real-data fit. | User conditions 3 and 4. || D25 | 2026-11-12 | D24a result: m FAILS benchmark v2 (0 of 3 seeds; m null control failed 0 of 3). Same-family diagnostic passes (r 0.92), so the failure is caused by model-family mismatch: the m map is model-dependent. Plain Archie inversion matches or beats the dual-porosity inversion on v2 truth. Pay indicator (BVH) stays robust (r 0.87 to 0.93, AUC 0.90 to 0.97). Spatially varying m claim cannot be defended. Stopped to show results before any real-data training. | results/identifiability_v2/summary.json, docs/identifiability.md. || D26 | 2026-11-12 | Framing A approved (user): identifiability paper with a positive core. Claims limited to (a) identifiability analysis incl. the inverse-crime demonstration, (b) pay indicator (bulk-volume hydrocarbon) robust across model families, noise and n, with uncertainty incl. model family and n, (c) real-data test by production status, (d) open 625-well pipeline. NO claims about recovered m, n, f_micro fields; NO dual-porosity advantage claim; NO absolute Sw maps or Rw estimates (reported as limitations); only relative pay-indicator maps. | User decision after D25. |
| D27 | 2026-11-12 | D24b entries, fixed BEFORE any real-data fit: PRIMARY neural-field entry = plain Archie inversion; SECOND entry = dual-porosity inversion. Both reported. Multiplicity: with two entries, each paired AUC difference against the best baseline uses a Bonferroni-corrected interval (97.5 % bootstrap CI instead of 95 %). The well-by-well inversion (same model, no spatial field) is a mandatory baseline; if the field does not beat it, the paper says so. | User conditions 1, 5, 6. |
| D28 | 2026-11-12 | Real-data analysis window fixed before training: Mississippian top to top + 100 ft (the "chat" position), 0.5 ft samples; well-level pay indicator = mean estimated bulk-volume hydrocarbon over the window. Labels: producer = KGS status oil/gas (incl. plugged) AND producing formation contains "Miss"; dry = status D&A. Other wells are unlabeled (used for training the label-free inversion, not for AUC). | Needed to make D24b operational; chosen without looking at any model output. || D29 | 2026-11-12 | Benchmark v3 (marginal wells; field vs well-by-well vs global): AUC pay vs all dry 0.82 to 0.86 for inversions, 0.88 for fixed-parameter Archie without inversion; spatial sharing changes AUC by 0.01 to 0.02 (inside seed range). Reported as is; no claim that spatial sharing helps. Spatial split frozen (results/splits/spatial_blocks_v1.csv: 625 wells, 47 blocks of 8 km, 5 folds; 379 producers, 47 dry, 199 unlabeled). Real-data run prepared, NOT started. | results/pay_indicator_benchmark/, docs/identifiability.md. |
| D30 | 2026-11-12 | Producer count under the D28 label is 379, not 397: the earlier 397 counted every usable well whose producing formation is Mississippian regardless of status (e.g. salt-water disposal). D28 definition stands. | results/splits/spatial_blocks_v1.json. |
| D31 | 2026-11-12 | Supervised baseline = scikit-learn gradient boosting and a small MLP on per-well curve percentiles (stands in for "ANN or XGBoost"; avoids an extra dependency). Rmf from LAS headers is at surface temperature and uncorrected, so its prior is deliberately wide (ln sd 0.7; 1.0 when missing). Rw nominal 0.05 ohm.m with ln sd 0.5 is an uncited working value, never reported as a result. | Implementation choices fixed before the real-data run. || D32 | 2026-11-15 | Real-data run goes ahead on the lab PC with configs/scale_up.yaml (user). Before any real fit: scale_up uses the SAME field architecture as the benchmarks (6 frequencies, 128 x 4) and differs only in ensemble size (10) and steps (10,000 train / 5,000 held-out). Study wells, coordinates, tops, folds and labels are read from the frozen file results/splits/frozen_wells_v1.csv; a data fingerprint (results/splits/dataset_fingerprint_v1.json) flags any difference between machines. No setting may change after real results are seen. | Keeps the real run consistent with what was tested; guards against KGS database updates. || D33 | 2026-11-16 | D24b RESULT: FAIL. Real-data run on the lab PC (RTX 4060 Ti, scale_up, fingerprint matched). Numbers VERIFIED on 2026-11-16 against results/real/evaluation.json (branch results/lab-4060ti-20261116, merged into main; all five runs: cuda:0, torch 2.15.0+cu132, scale_up.yaml, 10 seeds, 625 wells, fingerprint matched; 378 producers and 47 dry holes scored, 2000 bootstrap resamples). AUC pay vs dry on held-out blocks: supervised gradient boosting 0.780 (best baseline), supervised MLP 0.764, Archie inversion well-by-well 0.726, fixed Archie 0.686, fixed Simandoux 0.684, dual-porosity well-by-well 0.660, Archie field (PRIMARY) 0.643, Archie global m 0.629, dual-porosity field (SECOND) 0.573. Paired difference vs best baseline, Bonferroni interval: Archie field -0.136 [-0.228, -0.042]; dual-porosity field -0.207 [-0.312, -0.100]. Both entries are significantly WORSE than the best baseline. Per the rule: STOPPED, nothing written; user decides the reframing. No setting is to be changed or re-run. | User condition 6; rule D24b. || D34 | 2026-11-16 | Secondary D24b outcome, blind curve reconstruction on held-out wells (curve hidden, predicted from the others): also poor. RMSE / SD of the observed curve: sonic 0.81 to 1.10, PE 1.33 to 1.45, shallow resistivity 1.9 to 3.6 with a large positive bias (0.5 to 1.1 log10 units). No method predicts a hidden curve better than its mean. Reported as a negative result. The audit files rebuilt on the lab PC differ from the committed ones only in row order of the mnemonic tables and in 4 inventory rows; the committed cloud versions are kept. | results/real/evaluation.json. || D35 | 2026-11-16 | Reframing after the D24b fail (user): identifiability and negative-results paper. Working title "Identifiability before interpretation: an inverse-crime test of physics-informed petrophysical inversion across 625 wells of Mississippian chat". Claims: (a) identifiability analysis incl. inverse-crime demonstration, (b) pre-registered real-data test reported as negative, (c) open pipeline and benchmark. The "robust pay indicator" claim is dropped. Post-hoc diagnostics allowed only from saved outputs, no refitting on real logs, labelled exploratory. | User decision. |
| D36 | 2026-11-16 | Exploratory findings recorded (docs/real_data_results.md): single raw features (mean porosity 0.755, low resistivity 0.745) out-rank every inversion; per-fold AUC very uneven; deep-ensemble spread is negligible (not a usable uncertainty); one producer unscored. To be reported as exploratory and as limitations. | results/real/diagnostics_exploratory.json. || D37 | 2026-11-16 | Gate 3 APPROVED (user). Phase 5 on the D35 framing. Core case study DROPPED (no extra fit); limitation line required. Licences: MIT for code, CC BY 4.0 for manuscript, docs and figures; third-party (KGS) data not relicensed. Phase 5 constraints: no refitting, saved outputs only; pre-registered vs exploratory kept separate; limitations to state (ensemble has no usable spread; AUC 0.41 to 0.81 across folds; 378 of 379 producers scored); docs/traceability.md maps every figure and number to its source; figures shown to the user BEFORE manuscript text; stop at the Phase 6 gate. | User decision. || D38 | 2026-11-16 | Figures approved by the user after cross-check (lab-PC renders match the cloud renders in every value). Style: Okabe-Ito colours, Arial, Elsevier column widths. Manuscript draft, highlights, cover letter, reviewers and submission to-do written in paper/. The manuscript could not be compiled in the cloud session (LaTeX install not permitted); static checks only. Stopped at the Phase 6 gate. | User instruction to stop before the repository release. || D39 | 2026-11-16 | Phase 6 approved (user). Manuscript conformed to the Computers & Geosciences guide (docs/journal_guide_check.md). Release name v1.0.0 (chosen by the assistant because none was given; can be changed). The tag could NOT be pushed from the cloud session (the session's git access accepts branches only); the author creates the v1.0.0 release on GitHub from the head of main. Clean-clone check on Linux/CPU with the existing Python environment: 34 tests pass, figures regenerate (PNG files byte-identical to the committed ones), synthetic benchmark and stand-in pipeline run. NOT re-verified in a clean clone: a fresh dependency install here, the data download, the audit and the 12 h real-data run (those ran once on the lab PC from a fresh Windows install, with a matching data fingerprint). | User decision; journal guide repository requirements. |
| D40 | 2026-11-22 | Commit authorship on main rewritten to Abrar Mahir at the author's request (contents, messages, Co-Authored-By lines and timestamps unchanged; old-to-new commit table in docs/history_rewrite.md). The v1.0.0 release keeps pointing to the original commits. | Author wants to be listed as the repository's contributor. |
Pending (owner: author): items in paper/TODO_before_submission.md; scope decision for the journal.

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
