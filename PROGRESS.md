# Progress (resume from here)

## Status: benchmark v2 done. m claim FAILED (D25). Waiting for the user's framing decision. No real-data training has been run.

### Done
- Phases 0 to 2; Gate 1 GO; Gate 2 approved; reframed claim D22 approved with conditions.
- Pre-registered rules: D20 (v1), D24a (benchmark v2), D24b (real-data rule) in DECISIONS.md.
- v1 identifiability (`make identifiability`): m passes narrowly, n and f_micro fail.
- v2 (`make identifiability-v2`, 19 runs, about 25 min on 4 CPUs): m fails under a
  different-family truth; pay indicator robust. See docs/identifiability.md (both parts).
- Inversion model has `device` (auto = CUDA if available) and optional global Rw estimation.
- References Crossref-verified (19); six TODO-VERIFY items are comments only, not citable.

### Options put to the user (recommendation: A)
A. Identifiability paper with a positive core: "what a label-free physics-informed inversion
   can and cannot recover in low-resistivity chert pay". Parameters (m, n, f_micro) shown to be
   non-identifiable or model-dependent; robust deliverable = spatial pay-indicator (BVH) maps
   with ensemble + model-family + n uncertainty; real-data test by D24b (unchanged).
B. Pure negative-results / identifiability study, synthetic plus a short real-data illustration.

### Exact next steps after the decision (option A)
1. Real-data loader from data/interim/miss_logs.parquet (core set, LRXO from RSHAL, optional
   DT, PE; Rmf from LAS headers with a wide prior); mini-batching over wells.
2. Freeze the spatial-block CV split in results/splits/ BEFORE any real-data fit.
3. scripts/train.py --config (ensemble of 5; both resistivity model families as members of
   the uncertainty analysis, to be pre-registered); pay maps and uncertainty.
4. Baselines and D24b evaluation; STOP at Gate 3 (or earlier if D24b fails).
5. Wider full-text literature check (needs arxiv.org, essopenarchive.org, onepetro.org or PDFs).
6. Lab runbook: add the real-data runners once they exist.

### Environment notes
- Cloud environment `chert-pay-neural-field`; allowed hosts: www.kaggle.com, api.kaggle.com,
  storage.googleapis.com, www.kgs.ku.edu, kgsimages.blob.core.windows.net,
  download.pytorch.org, chasm.kgs.ku.edu, api.crossref.org. Install torch here with plain `pip install torch==2.15.0`.
- Kaggle download worked without credentials (public dataset, kagglehub).
- Container is ephemeral: rerun `make data && make audit` in a fresh session.
