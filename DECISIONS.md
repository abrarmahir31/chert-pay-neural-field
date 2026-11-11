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

Pending (owner: user): Gate 1 go/no-go; LICENSE choice (Phase 6).
