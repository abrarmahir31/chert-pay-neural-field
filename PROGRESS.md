# Progress (resume from here)

## Status: D24b FAILED on real data (D33). STOPPED. Results branch received, verified and merged (results/real/). Waiting for the user's reframing decision. Nothing has been written for the paper.

### What happened
- Lab-PC run finished (about 20 h wall clock incl. restart; fingerprint matched; GPU used).
- Neither neural-field entry beats the best baseline; both are significantly worse (see D33).
- Also visible: the spatial field is worse than the same inversion well by well (0.643 vs 0.726)
  and than fixed-parameter Archie (0.686). Label-free inversions all trail the supervised models.

### Exact next steps
1. DONE: results verified against results/real/evaluation.json and merged into main (D33, D34).
2. Do NOT tune or re-run anything on real logs.
3. After the user's decision (expected: identifiability and negative-results paper):
   diagnostics that do not change the registered test (why the field hurts: compare per-fold
   AUC, ensemble spread, blind curve reconstruction), n sensitivity, School Trust 4-4 case
   study, figures, manuscript. Gate 3 summary first.
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
