# Progress (resume from here)

## Status: Phase 5 complete (draft). STOPPED at the Phase 6 gate, waiting for the user's approval to prepare the release.

### Done in Phase 5
- Figures 1 to 5 (scripts/make_figures.py), approved by the user (D38).
- paper/main.tex (about 3,700 words, abstract 248 words), highlights, cover letter, suggested
  reviewers, TODO_before_submission.md, references.bib (25 verified entries).
- docs/traceability.md covers every figure and every number in the text.
- NOT done: compiling main.tex (no LaTeX here; user must compile locally or on Overleaf).

### Exact next steps (Phase 6, only after approval)
1. Apply the user's comments on the manuscript; fix any LaTeX compile errors they report.
2. README: exact commands for every figure and table; results manifest (file, script, config,
   seed); model card; CITATION.cff; check LICENSE placeholders.
3. Clean-clone reproduction: fresh clone -> install -> tests -> make_figures (results-only);
   document what needs the data download and the lab-PC run (about 12 h).
4. Tag a release (ask the user for the version name) and add the tag / archive DOI to the
   code-availability section.
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
