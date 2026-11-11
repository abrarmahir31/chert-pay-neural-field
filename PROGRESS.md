# Progress (resume from here)

## Status: Phase 0 and Phase 1 done. WAITING at Decision Gate 1 for user approval.

### Done
- Phase 0: skeleton, pyproject (pinned), Makefile, pre-commit, CI (ruff + pytest), 16 unit tests.
  Hardware: 4 CPU, 15 GB RAM, no GPU.
- Data: `make data` downloads KGS archives + 1,053 Barber LAS files (about 1.6 GB, 15 to 25 min).
- Phase 1: `make audit` writes results/audit/*. Summary in docs/data_audit.md.
  Result: 625 usable wells (core set), 124 with sonic, 259 with PE. Recommendation: GO.

### Exact next steps
1. Gate 1 answer from user. If GO:
2. Phase 2 literature and novelty: build docs/literature_gap.md and paper/references.bib
   (verified entries only), recommend journal. Stop at Gate 2.
3. Before Phase 3: PyTorch CPU wheel needs host `download.pytorch.org` (currently blocked);
   core analysis for School Trust 4-4 needs host `chasm.kgs.ku.edu` (blocked). Ask user via
   environment update when needed.
4. Phase 3 preprocessing to do: freeze spatial-block CV split BEFORE any model training
   (blocks on x_km, y_km in results/audit/well_inventory.csv); check density back-computation
   and neutron-matrix flags as ablation covariates.

### Environment notes
- Cloud environment `chert-pay-neural-field`; allowed hosts: www.kaggle.com, api.kaggle.com,
  storage.googleapis.com, www.kgs.ku.edu, kgsimages.blob.core.windows.net.
- Kaggle download worked without credentials (public dataset, kagglehub).
- Container is ephemeral: rerun `make data && make audit` in a fresh session.
