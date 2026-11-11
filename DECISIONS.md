# Decisions log

| # | Date | Decision | Reason |
|---|---|---|---|
| D1 | 2026-11-11 | Use original KGS LAS files, not the Kaggle CSV. | Kaggle copy is a lossy CSV (single resistivity, no neutron matrix, no caliper, no elevations). All 1,030 Kaggle ids are KGS LAS file ids; KGS terms allow reuse with citation. |
| D2 | 2026-11-11 | Unit of analysis is the well (KGS KID, 765), not the LAS file (1,054). | Several files per well; files merged on a 0.5 ft grid, the file with most samples taking precedence. |
| D3 | 2026-11-11 | Mississippian top = shallowest KGS Mississippian-system pick; wells without picks get an IDW (k=8, power 2) subsea interpolation from 4,948 picked Barber wells. | Leave-one-out MAE 21 ft; documented in docs/data_audit.md. |
| D4 | 2026-11-11 | Neutron curves with unlabelled matrix are assumed limestone. | Identical to the limestone-labelled curve in 135/136 wells carrying both. |
| D5 | 2026-11-11 | Bulk density back-computed from limestone density porosity (2.71 / 1.0 g/cc) when RHOB is missing (81 usable wells). | Recovers wells; flagged in `den_source`. |
| D6 | 2026-11-11 | "Usable" = at least 20 ft of co-located GR + density + neutron + deep resistivity inside the Mississippian. | Minimum set for a joint density-neutron-resistivity inversion. |
| D7 | 2026-11-11 | CPU-only environment (4 cores, 15 GB RAM, no GPU): plan small MLP field (about 4 x 128), ensembles of 5, mini-batches of samples. | Hardware. To be confirmed in Phase 3. |
| D8 | 2026-11-11 | Dedicated cloud environment `chert-pay-neural-field` with hosts for Kaggle and KGS only. | Keep the Default environment unchanged. |
| D9 | 2026-11-11 | GATE 1 = GO (user). KGS LAS data, 625-well core set. | User decision. |
| D10 | 2026-11-11 | Sonic and PE are OPTIONAL loss terms, masked where absent; no headline result may depend on sonic coverage. | User condition 1. |
| D11 | 2026-11-11 | Neutron matrix / unit convention is an uncertain nuisance parameter (per-well, with documented prior) plus a sensitivity test; stated as a limitation. | User condition 2; the second neutron curve is redundant in 135/136 wells. |
| D12 | 2026-11-11 | Environmental corrections unknown per file: add sensitivity analysis (perturbed per-well offsets/gains), list as limitation. | User condition 3. |
| D13 | 2026-11-11 | Validation hierarchy: (a) blind-well + spatially blocked curve reconstruction, (b) production status (397 Mississippian producers vs 47 dry) with AUC and bootstrap CIs, (c) School Trust 4-4 core as a single-well case study only. | User condition 4. |
| D14 | 2026-11-11 | Premise check (producers less resistive than dry holes) is motivation only, never evidence for the method. | User condition 5. |
| D15 | 2026-11-11 | One YAML config drives every training/ablation run; `configs/cpu_small.yaml` runs here, `configs/scale_up.yaml` for a GPU machine; no code changes between them. | User condition 6. |
| D16 | 2026-11-11 | Lab-GPU workflow: setup script, one-command runner per experiment, results pushed to a branch (small files only). Machine specs unknown: nothing assumed. | User condition 7. |
| D17 | 2026-11-11 | References verified by web search only; DOIs recorded only when seen in a search result. Entries recalled from memory are marked TODO-VERIFY. | api.crossref.org / doi.org are not allowed hosts. |
Pending (owner: user): Gate 2 approval; lab PC specs; LICENSE choice (Phase 6).
