# Tutorial: four typical uses

## 1. Check an installation and see the method run (no data, about 2 minutes)
```bash
python -m pytest -q
```
```bash
python scripts/run_real_all.py --standin --config configs/smoke.yaml
```
The second command fits the inversion on a synthetic stand-in in every variant (spatial field,
well by well, global parameter), evaluates it with the same code as the real test and writes
`results/standin/evaluation.json`. The numbers are meaningless at these step counts.

## 2. Run a null control on your own inversion settings
```bash
python scripts/run_identifiability.py --suite v2 --only v2_base,v2_null_m
```
`results/identifiability_v2/runs.csv` then holds, per seed, the correlation between recovered
and true cementation exponent (`m_r`) and the spread of the recovered map when the truth is
constant (`m_sd_est` of experiment `v2_null_m`). To test another model, add an entry to
`EXPERIMENTS_V2` in `scripts/run_identifiability.py`: the first dictionary overrides the
benchmark (`SynthConfig`), the second the inversion (`InversionConfig`).

## 3. Reproduce the real-data test
```bash
python scripts/download_data.py
```
```bash
python scripts/audit_pass1.py
```
```bash
python scripts/audit_pass2.py --frozen-tops
```
```bash
python scripts/run_real_all.py --config configs/scale_up.yaml
```
About 12 hours. Compare `results/real/evaluation.json` with the committed version; AUC values
should agree to about two decimals (hardware-dependent rounding).

## 4. Apply the pipeline to another area
1. In `scripts/download_data.py` change `COUNTY_API_PREFIX` (Kansas county code) or place your
   own LAS files in `data/raw/kgs/las/` with an index file of the same columns.
2. Run the audit; check `results/audit/unmapped_mnemonics.csv` and extend
   `configs/mnemonics.yaml` for curves that were not recognised.
3. Adapt the formation-top patterns (`MISS_RE`, `BASE_RE`) in `scripts/audit_pass2.py`.
4. Define labels in `src/chertfield/data/real.py` (`well_labels`) and create a new split with
   `scripts/make_splits.py` (delete the old files in `results/splits/` first: they belong to
   this study).
5. Before interpreting anything, run the different-family benchmark and the null controls
   (use 2 above) with noise levels and curve coverage that match your data.
