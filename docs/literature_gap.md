# Phase 2: literature, gap table and novelty claim (Decision Gate 2)

Search date: 11 Nov 2026. Method: web searches (about 25 queries) on physics-informed log
interpretation, label-free or self-supervised inversion, neural fields in geoscience, variable
Archie parameters, low-resistivity pay, and Mississippian chat petrophysics.

**Honest limits of this search.** Only abstracts, catalogue records and search snippets were
read; no full texts (paywalls, and publisher hosts are not reachable from this environment).
OnePetro (SPE, SPWLA, URTeC) and SEG Library are poorly covered by general web search, so a
closely related conference paper could have been missed. "Verified" below means the title,
authors and venue were seen in a search result; DOIs are given only when seen. Before
submission a full-text read of the closest papers and a Scopus / OnePetro check are needed.

## Read status (updated 11 Nov 2026)

| Status | Papers |
|---|---|
| Read in full | none yet |
| Abstract / catalogue record / search snippet only | all works in the gap table |
| Bibliographic data confirmed on Crossref | rows 1 to 5, 9, 10 (Sun et al. 2023), 11 (three AAPG papers), 12, 13 and both Scientific Reports papers of row 8 |
| Not verifiable so far | Duren 1967; Raymer et al. 1980; Simandoux 1963; the thesis-level work of row 7; neural-field preprints of 2025 to 2026 in row 10 |

Corrections after the Crossref check: row 3 is Tian, Wang, Li and Lai 2026, Geoenergy Science
and Engineering 257, 214246; row 4 was published as Vashisth and Mukerji 2022, The Leading
Edge 41(12), 840-846; row 5 is Geophysics 89(2), M17-M32; row 12 is Interpretation 10(4),
T707-T724 (2022); row 8 authors are Bagheri et al. 2026 (m) and Kumar et al. 2025 (n).

Still to do before submission (user condition, Gate 2): full-text reading of the closest
papers and a wider search of arXiv, ESS Open Archive and SPE/SPWLA (OnePetro). Those hosts are
not reachable from this environment (arxiv.org, essopenarchive.org, onepetro.org would each need
to be allowed, or the PDFs supplied).

## Gap table

Columns: Labels = needs core or interpreted labels to train. Params = rock-physics parameters
(Archie m, n, matrix or mineral end-points). Spatial = uses well location as a model input.

| # | Work | Data and scale | Labels | Params | Spatial | Uncertainty | Relevance |
|---|---|---|---|---|---|---|---|
| 1 | Pothana and Ling 2025, Energy Geoscience, "Physics-integrated neural networks for improved mineral volumes and porosity estimation from geophysical well logs" | well logs, one CO2 storage site (Broom Creek) | yes (also a hybrid unsupervised + supervised variant) | fixed log-response constants | no | not reported in abstract | closest "physics in the network" log paper; no saturation or Archie |
| 2 | Shao, Wang and Xiao 2024, Artificial Intelligence in Geosciences 5, 100070, "Reservoir evaluation using petrophysics informed machine learning: a case study" | well logs, field case | yes | response equations as loss constraints, constants fixed | no | no | closest "response equations in the loss" paper |
| 3 | SatuNN 2025 (physics-informed attention network for water saturation, tight sandstone; DOI 10.1016/j.geoen.2025.214246) | well logs | yes (measured Sw) | petrophysical constraints, fixed | no | no | saturation, but supervised |
| 4 | Vashisth and Mukerji 2022, arXiv:2210.00042, RW-PINN | seismic traces, few or no wells | no (self-supervised through a rock-physics and wave-physics decoder) | fixed rock-physics model | no | no | closest label-free "physics decoder" design, but seismic |
| 5 | Li, Liu, Alfarraj, Tahmasebi and Grana 2024, "Probabilistic physics-informed neural network for seismic petrophysical inversion" | pre-stack seismic, North Sea | weak or none | rock-physics model inside the loss | no | yes (probabilistic) | label-scarce physics-informed inversion with uncertainty, seismic |
| 6 | Classical statistical (multi-mineral) log analysis in commercial solvers | per well, per depth | no (reconstructs logs through response equations) | fixed, set by the analyst per zone | no | sometimes | **label-free log reconstruction itself is not new** |
| 7 | Bayesian multi-well petrophysical joint inversion with a spatial correlation function (thesis-level work found; details unverified) | logs + core, field scale | uses core | rock-physics priors propagated between wells | yes (geostatistical) | yes | closest "spatial coupling of rock-physics models across wells" |
| 8 | ML prediction of Archie exponents: ensemble learning for m (Scientific Reports 2026); robust ML for n (Scientific Reports 2024) | logs + special core analysis | yes (core m, n) | m or n predicted per depth | no | no | variable m, n, but supervised by core |
| 9 | Hillier et al. 2023, Geosci. Model Dev. 16, 6987, GeoINR 1.0 | well and outcrop geometry data | n/a | none (geological surfaces) | yes (implicit neural representation) | no | neural field for geology, not petrophysics |
| 10 | Implicit full-waveform inversion (2023) and later neural-field inversions for travel time, gravity, magnetotellurics (2025 to 2026 preprints) | geophysical surveys | no | none (velocity, density, resistivity models) | yes (neural field) | some | neural field as the model parameterisation in physics-based inversion |
| 11 | Watney, Guy and Byrnes 2001, AAPG Bull. 85, 85-113; Montgomery et al. 1998, AAPG Bull. 82, 187-205; Rogers 2001, AAPG Bull. 85, 115-129; KGS Open-File Report 2002-50 | chat cores and logs, Kansas and Oklahoma | core | m from about 1.8 to above 2.5 by facies; Glick field m about 2.36, n about 1.8 (Duren 1967, as quoted by KGS) | qualitative maps | no | the geological and petrophysical basis: microporosity, low resistivity, facies-dependent m |
| 12 | Bode-Omoleye, Grammer, Zhang and Molnar, Interpretation 10 (pore systems, Mississippian carbonates, Kansas) | core, NMR | core | none | no | no | recent pore-system evidence for microporosity-bound water |
| 13 | Low-resistivity pay with ML (for example MLP + DBSCAN on conventional logs, Petroleum Science 2022) | well logs | yes (tested intervals) | none | no | no | classification, no physics inversion |
| **This study** | 625 wells, about 303,000 samples, one county | **no** | **m, n, matrix and micro-porosity fraction as outputs** | **yes: neural field f(x, y, z)** | **deep ensemble** | |

## What is and is not new

Not new (must be said in the paper):
- putting log-response equations in a network loss (rows 1 to 3);
- label-free training by reconstructing measurements through a physics decoder (rows 4 to 6);
- neural fields as model parameterisation in geophysical inversion (rows 9, 10);
- that chat m and n differ from 2 and vary by facies (row 11).

Not found in this search:
- a coordinate-based neural field whose outputs are rock-physics *parameters* (Archie m, n,
  matrix end-points, micro-porosity fraction) rather than rock *properties*;
- a single label-free inversion trained jointly on several hundred wells so that the
  parameters are tied together spatially;
- any physics-informed learning study on Mississippian chat or other chert low-resistivity pay.

## Refined novelty claim (proposed)

> We represent the rock-physics parameters of a low-resistivity chert reservoir (Archie
> exponents, matrix response and micro-porosity fraction) as a continuous spatial neural field
> shared by 625 wells, and estimate that field without core labels by jointly reconstructing
> the density, neutron and resistivity logs of every well through differentiable tool-response
> models, with ensemble uncertainty. To our knowledge this is the first neural-field
> formulation of spatially varying petrophysical parameters and the first physics-informed
> learning study of Mississippian chat pay.

Changes from the working claim: "1,000+ wells" becomes 625 wells; "label-free" is narrowed to
"no core labels" (KGS tops are used to select the interval; production status is used only for
validation); sonic is optional.

## The main scientific risk: identifiability

In Archie's equation Rt = a Rw / (phi^m Sw^n), the unknowns m, n, Rw and Sw trade off exactly at
a single depth. Reconstruction of a deep-resistivity curve alone cannot separate "high m" from
"high Sw". What can constrain them:
1. spatial sharing: m, n and Rw vary smoothly, Sw varies sample by sample;
2. water-bearing intervals (dry holes, deep Mississippian below the chat) where Sw is near 1,
   which fix m and Rw as in a Pickett plot;
3. shallow or medium resistivity (594 wells) as a second equation with mud-filtrate saturation;
4. priors from published core ranges (row 11).
Phase 3 must test on synthetic data which of these make m, n and the micro-porosity fraction
recoverable, and the paper must report the degeneracies that remain. If m and n are not
separable, the defensible claim shrinks to a spatial field of an *effective* resistivity
parameter (for example apparent m, or bulk-volume-water index) with uncertainty.

## Journal recommendation

| Journal | Quartile evidence found | Fit |
|---|---|---|
| **Computers & Geosciences** (recommended) | SCImago "Computers in Earth Sciences": SJR 1.033, Q1 | method + open code + reproducibility are core scope; code availability section is mandatory, which this project already satisfies |
| Geophysics (SEG) | aggregators quoting SCImago: SJR 1.073, Q1 in Geophysics | strong borehole-geophysics readership; slower, page charges |
| Mathematical Geosciences | JCR Q1 per aggregators; SJR not confirmed | fits if the identifiability analysis becomes the centre |
| Petroleum Science | aggregator: SJR 1.005, Q1 (year unclear) | fits a field-application framing |
| SPE Journal | aggregator: SJR 0.606, **Q2** (not confirmed on SCImago) | does not meet the Q1 target on this evidence |

Quartiles come from secondary pages; please confirm on scimagojr.com or JCR (I cannot reach
them from here) before we commit to the template in Phase 5.

## Public calibration and test data found

| Source | What | Access | Use |
|---|---|---|---|
| KGS Digital Petroleum Atlas, School Trust 4-4 (API 15-007-21038, Hardtner field, Barber Co.) | 30+ routine core points, 4822 to 4857 ft and deeper: porosity, maximum permeability, oil and water saturation, two rock types | retrieved from chasm.kgs.ku.edu, KGS terms of use | single-well case study only. Values look digitised (regular log-spaced permeabilities) and core saturations are not in-situ saturations |
| KGS Open-File Report 2002-50 (chat characterisation posters) | core porosity and permeability ranges, capillary pressure, NMR, Pickett-plot parameters for chat fields (Glick, Aetna, Spivey-Grabs, Tjaden well) | public web pages | prior ranges for m, n, porosity; not point data |
| KGS core-analysis database | 146 wells statewide, only 1 in Barber County | public | none beyond the well above |
| KGS well headers | status, producing formation, initial potential (158 usable wells) | already downloaded | production-status validation |
| Drill-stem tests | KGS hosts a DST database; not yet checked for Barber County | to do in Phase 4 | possible fluid-recovery validation |
