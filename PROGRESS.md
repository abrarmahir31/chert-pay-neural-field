# Progress (resume from here)

## Status: Phase 3 step 1 done (identifiability). STOPPED per rule D20, outcome 2. Waiting for user approval of the reframed claim.

### Done
- Phases 0 to 2 (see DECISIONS.md D1 to D19). Gate 1 GO, Gate 2 approved with conditions.
- References: paper/references.bib verified on Crossref (19 entries); 6 items remain
  TODO-VERIFY as comments and must not be cited.
- Inversion model: src/chertfield/model/inversion.py (Fourier-feature field for m, n, f_micro;
  free per-sample properties; per-well nuisance terms; fixed-sigma masked misfit).
- Identifiability study: `make identifiability` -> results/identifiability/, docs/identifiability.md.
  m recoverable (narrowly), n and f_micro not; dual-porosity model still needed for Sw / pay.
- Lab runbook: docs/lab_gpu_workflow.md, scripts/setup_machine.sh, Makefile runners.

### Proposed reframing (needs approval)
Spatially varying cementation exponent m (relative variation), n fixed from published chat
values, f_micro kept as a weakly constrained nuisance field; headline deliverable = pay
indicator (bulk-volume hydrocarbon) maps with ensemble uncertainty, validated by blind-well
reconstruction and production status.

### Exact next steps after approval
1. Add `device` handling (config `device: auto`) to JointInversion / scripts; mini-batching
   over wells for the 625-well real data set.
2. Real-data loader from data/interim/miss_logs.parquet (core set + LRXO from RSHAL, optional
   DT, PE); Rmf from LAS headers (results/audit/las_files.csv `rmf`) with wide prior.
3. Freeze spatial-block CV split in results/splits/ BEFORE any real-data fit.
4. Deep ensemble of 5; pay-probability and uncertainty maps; scripts/train.py --config.
5. Phase 4: baselines (fixed Archie, Simandoux, well-by-well, plain ANN / XGBoost, no-physics
   net), ablations, production-status AUC with bootstrap CIs, School Trust 4-4 case study,
   sensitivity to neutron matrix and environmental corrections. Gate 3.
6. Wider full-text literature check (needs arxiv.org, essopenarchive.org, onepetro.org or PDFs).

### Open requests to the user
- Approve or adjust the reframed claim. Lab PC specs. Journal quartile confirmation.

### Environment notes
- Cloud environment `chert-pay-neural-field`; allowed hosts: www.kaggle.com, api.kaggle.com,
  storage.googleapis.com, www.kgs.ku.edu, kgsimages.blob.core.windows.net,
  download.pytorch.org, chasm.kgs.ku.edu, api.crossref.org. Install torch here with plain `pip install torch==2.15.0`.
- Kaggle download worked without credentials (public dataset, kagglehub).
- Container is ephemeral: rerun `make data && make audit` in a fresh session.
