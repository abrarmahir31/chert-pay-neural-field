# Progress (resume from here)

## Status: Phase 2 done, Phase 3 groundwork done. WAITING at Decision Gate 2.

### Done
- Phase 0: skeleton, pinned deps, Makefile, pre-commit, CI. Hardware here: 4 CPU, 15 GB, no GPU.
- Phase 1: `make data` + `make audit`; 625 usable wells. Gate 1 = GO with conditions D9-D16.
- Phase 2: docs/literature_gap.md (gap table, refined claim, identifiability risk, journal
  recommendation = Computers & Geosciences), paper/references.bib (search-verified only).
- Core data: School Trust 4-4 routine core table downloaded to data/raw/kgs/core (case study).
- Phase 3 groundwork: forward models (src/chertfield/physics/forward.py), synthetic benchmark
  (src/chertfield/synthetic/benchmark.py, scripts/make_synthetic.py), 28 unit tests pass,
  configs/cpu_small.yaml and configs/scale_up.yaml, scripts/setup_machine.sh,
  docs/forward_models.md, docs/lab_gpu_workflow.md.

### Exact next steps (after Gate 2 approval)
1. Phase 3 proper, in src/chertfield/model/: (a) coordinate encoder (Fourier; hash grid as
   ablation) + bounded-output MLP field for m, n, f_micro (and per-well nuisance terms:
   neutron offset, GR end-points); (b) per-sample property network or free variables for
   phi, vsh, mineral fractions, Sw_macro, Sxo; (c) masked joint loss over RHOB, NPHI, GR,
   log Rt, log Rxo, optional DT and PE, with uncertainty weighting, bounds and smoothness;
   (d) deep ensemble of 5; (e) pay probability maps. Script: scripts/train.py --config.
2. Synthetic recovery + identifiability study FIRST (profile m vs Sw vs f_micro; with and
   without wet wells, shallow resistivity, priors). Report degeneracies in docs/.
3. Freeze the spatial-block CV split (results/splits/) before any real-data training.
4. Parse the core HTML into a table for the case-study check (Phase 4).
5. Check the KGS drill-stem-test database for Barber County (Phase 4 validation).

### Open requests to the user
- Optional hosts: api.crossref.org (DOI verification of references), download-r2.pytorch.org
  (lean CPU PyTorch wheel; the PyPI build with CUDA libraries is installed instead and works).
- Lab PC specs; journal quartile confirmation on scimagojr.com / JCR.

### Environment notes
- Cloud environment `chert-pay-neural-field`; allowed hosts: www.kaggle.com, api.kaggle.com,
  storage.googleapis.com, www.kgs.ku.edu, kgsimages.blob.core.windows.net,
  download.pytorch.org, chasm.kgs.ku.edu. Install torch here with plain `pip install torch==2.15.0`.
- Kaggle download worked without credentials (public dataset, kagglehub).
- Container is ephemeral: rerun `make data && make audit` in a fresh session.
