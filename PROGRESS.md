# Progress (resume from here)

## Status: benchmark v3 done; real-data run PREPARED, NOT STARTED. Waiting for the user's go-ahead (and choice of where to run it).

### Done
- Framing A approved (D26); entries and window pre-registered (D27, D28); results D25, D29.
- Benchmarks: `make identifiability`, `make identifiability-v2`, `make pay-benchmark`
  (docs/identifiability.md has all three parts).
- Spatial split frozen: results/splits/spatial_blocks_v1.csv (never regenerate).
- Real-data pipeline: src/chertfield/data/real.py, scripts/train_real.py, scripts/eval_real.py,
  scripts/run_real_all.py; self-test `make real-standin` (synthetic stand-in, no real data).
- 34 unit tests; GPU handled by `device: auto` with CPU fallback (never exercised on a GPU).
- Runbook incl. Windows 10 native steps (untested on Windows): docs/lab_gpu_workflow.md.

### Exact next steps
1. On go-ahead: `make real CONFIG=configs/cpu_small.yaml` (here) or scale_up on the lab PC.
   It runs archie/field, dual/field, archie/per_well, dual/per_well, archie/constant, then
   eval_real.py -> results/real/evaluation.json with the D24b verdict.
2. If no entry beats the best baseline (Bonferroni CI): STOP and report (rule D24b).
3. Then Phase 4 remainder: sensitivity to n (1.6 to 2.2), neutron matrix, environmental
   offsets; School Trust 4-4 case study (data/raw/kgs/core/1006015457.html, parse first);
   pay-indicator maps with ensemble + model-family + n uncertainty. Gate 3.
4. Wider full-text literature check (needs arxiv.org, essopenarchive.org, onepetro.org or PDFs).
5. Candidate titles are in DECISIONS-independent note below.

### Candidate working titles (user to choose)
1. "What can label-free physics-informed log inversion recover? Identifiability limits and a
   robust pay indicator for low-resistivity Mississippian chert, Kansas"
2. "Identifiability before interpretation: an inverse-crime test of physics-informed
   petrophysical inversion across 625 wells of Mississippian chat"
3. "Label-free petrophysical inversion of low-resistivity chert pay: what the logs constrain,
   what they do not, and an open 625-well benchmark"

### Environment notes
- Cloud environment `chert-pay-neural-field`; allowed hosts: www.kaggle.com, api.kaggle.com,
  storage.googleapis.com, www.kgs.ku.edu, kgsimages.blob.core.windows.net,
  download.pytorch.org, chasm.kgs.ku.edu, api.crossref.org. Install torch here with plain `pip install torch==2.15.0`.
- Kaggle download worked without credentials (public dataset, kagglehub).
- Container is ephemeral: rerun `make data && make audit` in a fresh session.
