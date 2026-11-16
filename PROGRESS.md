# Progress (resume from here)

## Status: Phase 5 started. Draft figures 1 to 5 made and shown to the user. WAITING for figure approval before writing manuscript text.

### Done in Phase 5
- scripts/make_figures.py -> figures/fig1..fig5 (.pdf vector + .png preview), results-only inputs.
- docs/traceability.md (figure and number -> source file). LICENSE (MIT), LICENSE-docs.md (CC BY 4.0).

### Exact next steps
1. Apply the user's figure comments; re-run `python scripts/make_figures.py`.
2. Manuscript in paper/ (Computers & Geosciences, elsarticle class): abstract, highlights,
   introduction + gap, geological setting, data, method, pre-registration, results
   (confirmatory, then clearly separated exploratory), discussion + limitations (D37 list,
   core comparison not performed, no absolute Sw / Rw, tool-physics and environmental
   assumptions, data vintage, literature read as abstracts only), conclusions, data/code
   availability, AI-use statement. Cite only verified entries of paper/references.bib.
   Placeholders [AUTHOR NAMES], [AFFILIATIONS]. Cover letter, suggested reviewers.
3. Extend docs/traceability.md with every number used in the text.
4. STOP at the Phase 6 gate (README commands, manifest, model card, CITATION.cff, clean-clone
   reproduction, tagged release) and wait for approval.
5. Wider full-text literature check (needs arxiv.org, essopenarchive.org, onepetro.org or PDFs).

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
