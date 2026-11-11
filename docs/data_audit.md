# Phase 1 data audit (Decision Gate 1)

All numbers are copied from `results/audit/*.json|csv`, produced by `make audit`
(`scripts/audit_pass1.py`, `audit_pass2.py`, `audit_report.py`; deterministic, no seed).

## What the data actually are
- The Kaggle dataset is two CSVs, not LAS files; it is a lossy repackaging of KGS data
  (see `data/README.md`). We use the original KGS LAS files instead.
- 1,054 Barber County LAS files in the KGS index, 1,053 downloaded, 1,050 parsed
  (3 unreadable), linked to **765 wells**, all with coordinates; elevation reference KB for 741.
- Vintage: median spud year 2011 (10th percentile 1981); 802 files at 0.5 ft step, 135 at 1 ft,
  98 finer. All depths in feet (3 files with no unit). 8 wrapped files. Service-company header
  text is too inconsistent to infer tool type for about a third of files.

## Curve availability (wells with >= 20 ft of valid data inside the Mississippian)
| Curve | Wells | Note |
|---|---|---|
| GR | 729 | |
| Deep resistivity | 683 | induction / array induction; conductivity inverted where needed |
| Medium / shallow resistivity | 598 / 602 | |
| Bulk density (RHOB) | 551 | 644 when back-computed from limestone density porosity |
| Density porosity, limestone | 635 | sandstone 30, dolomite 29 |
| Neutron porosity, any | 636 | limestone-labelled 363; matrix unlabelled 409 |
| PE | 266 | |
| Sonic DT | 132 | sonic porosity 114 |
| Caliper / density correction | 634 / 590 | |
| Microlog | 274 | |

Neutron matrix: where the mnemonic does not state the matrix (263 usable wells) limestone is
**assumed**. Evidence: in 135 of 136 wells that carry both an unlabelled and a limestone-labelled
neutron curve, the two are identical (median abs. difference < 0.002 v/v).
Units: porosity in percent or fraction resolved by unit string and magnitude; 40 wells had a
unit string contradicting the values (flagged in `qc_flags`).

## Mississippian interval
- Top: shallowest KGS pick of a Mississippian-system unit (615 wells). For the 150 wells
  without a pick: inverse-distance interpolation of the subsea top from the 8 nearest of
  4,948 Barber County wells with picks. Leave-one-out error of this heuristic: MAE 21 ft,
  90th percentile 36 ft.
- Base: shallowest deeper pick (Kinderhook, Chattanooga, Viola, Simpson, ...) for 469 wells,
  otherwise end of log (capped at top + 400 ft). Median picked thickness 206 ft.

## Usable set for the joint inversion
| Curve set (co-located, >= 20 ft) | Wells |
|---|---|
| GR + density + neutron + deep resistivity (core set) | **625** |
| core + shallow or medium resistivity | 594 |
| core + PE | 259 |
| core + DT | 124 |
| core + DT + PE | 59 |

Core set: 151,747 ft (303,493 samples at 0.5 ft); 61,589 ft in the upper 100 ft ("chat"
position). Median 232 ft per well. Extent about 57 x 52 km. 397 of the 625 wells are recorded
as producing from the Mississippian; 47 are dry holes; 158 report initial potential.

## First look at the scientific premise (descriptive, nothing tuned)
Upper 50 ft of the Mississippian, well medians (`premise_check.json`):
- Mississippian producers (n = 378): deep resistivity 6.0 ohm.m (IQR 4.2 to 8.1),
  density-neutron porosity 0.19.
- Dry holes (n = 47): 9.8 ohm.m (IQR 6.1 to 14.4), porosity 0.13. Mann-Whitney p = 2.6e-6.
- 139 producers have a median deep resistivity below 5 ohm.m.
Producing wells are *less* resistive than dry holes, consistent with the low-resistivity pay
problem. Caveat: "producer" is a well-level label, not a perforated interval.

## Calibration data found
- KGS core-analysis database lists one Barber County well: School Trust 4-4,
  API 15-007-21038, Hardtner field; it has 100.5 ft of core-set logs in the interval.
  The analysis table itself sits on `chasm.kgs.ku.edu` (not yet retrieved). KGS terms of use apply.
- KGS tops (39,689 Barber rows) and well headers with status, producing formation and IP.

## Risks
1. Sonic exists in only 124 usable wells: the sonic term can constrain a subset only.
2. No core labels in the county beyond one well: validation will rely mostly on blind
   curve reconstruction, production status and that single core.
3. Environmental corrections are unknown per file; vendor-processed curves are taken as delivered.
