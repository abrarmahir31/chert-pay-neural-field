# Progress (resume from here)

## Status: Phase 6 complete. Release v1.0.0 tagged. All six phases done; remaining items are the author's (paper/TODO_before_submission.md).

### State of the deliverables
- Manuscript: paper/main.tex (compiles on MiKTeX; conformed to the journal guide, see
  docs/journal_guide_check.md), highlights, cover letter, suggested reviewers, graphical
  abstract (figures/graphical_abstract.pdf|png).
- Repository: README (install, quick start, reproduction table, requirements), docs/user_guide.md,
  docs/tutorial.md, docs/model_card.md, results/MANIFEST.md, CITATION.cff, LICENSE (MIT),
  LICENSE-docs.md (CC BY 4.0), docs/traceability.md.
- Results: synthetic benchmarks v1 to v3, real-data test (failed, D33/D34), exploratory diagnostics.

### If work resumes
1. Author items: verify text and references personally; CRediT roles; Elsevier declarations
   tool; full-text literature check; decide on journal given the scope risk.
2. After any manuscript edit: recompile, keep docs/traceability.md in step, re-run
   `python scripts/make_manifest.py` if result files change.
3. Optional: Zenodo archive DOI for v1.0.0; add to the code-availability section.

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
