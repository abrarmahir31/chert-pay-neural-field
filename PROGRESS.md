# Progress (resume from here)

## Status: real-data run (D24b) handed to the user's lab PC. Waiting for results branch `results/lab-4060ti-*`.

### Done
- Benchmarks v1, v2, v3 (docs/identifiability.md); decisions D1 to D32.
- Frozen: results/splits/frozen_wells_v1.csv (wells, xy, tops, folds, labels),
  spatial_blocks_v1.csv, dataset_fingerprint_v1.json. Never regenerate.
- Real pipeline: scripts/train_real.py, eval_real.py, run_real_all.py, check_env.py,
  run_lab.bat; configs/smoke.yaml, scale_up.yaml. Runbook: docs/lab_gpu_workflow.md.
- No real-data fit has been run in the cloud session.

### Exact next steps
1. When the results branch arrives: read results/real/evaluation.json. Check
   `fingerprint_matches_reference` and `device` in results/real/pay_*.json.
2. If `D24b_any_entry_beats_best_baseline` is false: STOP, report to the user, write nothing.
3. Otherwise / after the user's framing decision: sensitivity runs (n 1.6 to 2.2, neutron
   matrix, environmental offsets), School Trust 4-4 case study, pay maps, Gate 3.
4. Wider full-text literature check (needs arxiv.org, essopenarchive.org, onepetro.org or PDFs).

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
