# Progress (resume from here)

## Status: DECISION GATE 3. Real-data test failed (D33, D34); reframing approved (D35); exploratory diagnostics done (D36). Waiting for Gate 3 approval before any manuscript text.

### Key documents
- docs/identifiability.md (benchmarks v1, v2, v3), docs/real_data_results.md (D24b + exploratory),
  docs/literature_gap.md, docs/data_audit.md, docs/forward_models.md, DECISIONS.md (D1 to D36).

### Exact next steps after Gate 3 approval
1. Still-open Phase 4 items that need NO refit on real logs: School Trust 4-4 core case study
   is NOT possible without per-sample outputs (only well-level scores were saved): either drop
   it or ask the user before any new real-data fit. n sensitivity and neutron-matrix /
   environmental sensitivity: done on synthetic only (v2 rows); say so.
2. Phase 5: figures from results/ only (load the dataviz skill first): identifiability panels
   (v1 vs v2 m recovery, null controls), v3 AUC bars, real-data AUC forest plot with CIs,
   per-fold AUC, map of wells / folds / labels. Manuscript in paper/ (Computers & Geosciences
   template), cover letter, reviewers, AI-use statement. Cite only verified references.
3. Phase 6: README commands, results manifest, model card, CITATION.cff, LICENSE (ask user),
   clean-clone reproduction, tagged release.
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
