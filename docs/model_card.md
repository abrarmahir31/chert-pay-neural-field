# Model card: label-free joint log inversion with a spatial parameter field

**What it is.** A research inversion, not a trained predictive model: for a set of wells it
optimises (a) a small coordinate network giving the cementation exponent (and optionally a
micro-porosity fraction) at each well location, (b) free per-sample rock properties and (c)
per-well nuisance terms, so that differentiable tool-response equations reproduce the measured
density, neutron, gamma-ray and resistivity logs. No weights are distributed; every use is a
new fit. Code: `src/chertfield/model/inversion.py`. Version 1.0.0.

**Intended use.** Methodological research on identifiability of physics-informed log
inversion; a worked example of pre-registered testing with null controls.

**Not intended for.** Reserve estimation, completion or drilling decisions, or any
interpretation of the fitted parameter maps or saturations.

**Evidence (see the paper and `docs/`).**
- Synthetic: saturation exponent and micro-porosity fraction not recoverable; cementation
  exponent recovered only when the benchmark shares the inversion's model family (correlation
  0.87 to 0.93), not otherwise (0.15 to 0.60); null controls fail.
- Real data, pre-registered: AUC 0.643 (Archie field) and 0.573 (dual-porosity field) for
  producers versus dry holes on held-out spatial blocks, against 0.780 for a supervised
  baseline, 0.726 for the same inversion well by well and 0.686 for fixed-parameter Archie.

**Data.** 625 wells of public Kansas Geological Survey logs, Barber County, upper 100 ft of the
Mississippian; 379 producers, 47 dry holes, 199 unlabelled. Labels are well-level production
status, used only for evaluation.

**Known limitations.** Parameters are not identifiable and are model-dependent; the ensemble
has almost no spread and is not an uncertainty measure; performance varies strongly by area;
absolute water saturation and formation-water resistivity are biased; tool physics is
simplified and no environmental corrections are applied; one county, one formation.

**Ethical and practical notes.** Built with extensive AI assistance under the author's
direction (see the declaration in the manuscript). Data remain under KGS terms of use.
