# Data (not committed)

Nothing under `data/` except this file is tracked by git. Run `make data` to rebuild it.

## Primary source: Kansas Geological Survey (KGS)

| Item | URL | Used for |
|---|---|---|
| LAS index `ks_las_files.zip` | https://www.kgs.ku.edu/PRS/Ora_Archive/ks_las_files.zip | file → well link, URLs |
| Original LAS files (Barber County, API `15-007-*`) | `https://www.kgs.ku.edu/WellLogs/<dir>/<file_id>.las` (redirects to the KGS file store) | all log data |
| Well headers `ks_wells.zip` | https://www.kgs.ku.edu/PRS/Ora_Archive/ks_wells.zip | coordinates, KB elevation, status, producing formation, IP |
| Formation tops `ks_tops.zip` | https://www.kgs.ku.edu/PRS/Ora_Archive/ks_tops.zip | Mississippian top/base |
| Core-analysis well list | https://www.kgs.ku.edu/Magellan/CoreLibrary/core_analysis_wells.xlsx | validation wells |

Snapshot used in this study: archives dated 9 Oct 2026, downloaded 11 Nov 2026.
1,053 of the 1,054 Barber County LAS files in the index were retrieved (one index row has an empty URL).

**Terms of use** (https://www.kgs.ku.edu/General/copyright.html, read 11 Nov 2026): KGS website
information "has been developed for public use and may be distributed or copied"; users may "use,
publish, distribute ... alter, modify" it free of charge and must credit the source as:
"The source of this material is the Kansas Geological Survey website at http://www.kgs.ku.edu/.
All Rights Reserved." Data are provided "as is" without warranty. KGS recommends obtaining data
directly from KGS servers, which is what `scripts/download_data.py` does.

## Secondary source: Kaggle repackaging (provenance check only)

"Barber County Well Log Dataset (Kansas)", `ainiashiqinn/barber-county-well-log-dataset-kansas`,
license shown on Kaggle: CC0 Public Domain, last updated 4 Jan 2026. It contains two CSV files
(`barber_logs_ml.csv`, 8.06 M rows; `well_metadata.csv`, 1,030 rows), **not** LAS files.
Findings of the provenance check:

- every one of its 1,030 `WELL_ID` values is a KGS LAS *file* id present in the KGS index
  (so "1,030 wells" is 1,030 log files from fewer physical wells; the KGS index links the
  1,054 Barber files to 765 wells);
- curves are collapsed to GR, RES, RHOB, NPHI, DT, SP, PE: a single resistivity (no depth of
  investigation), no neutron matrix, no caliper/density correction, no elevations or tops.

The study therefore uses the original KGS files. `python scripts/download_data.py --kaggle`
fetches the Kaggle copy as well (public; if Kaggle requests credentials they are read from the
environment variables `KAGGLE_USERNAME` / `KAGGLE_KEY`, never from files in this repo).

## Layout after `make data && make audit`

```
data/raw/kgs/{ks_las_files,ks_wells,ks_tops}/*.txt   KGS archives
data/raw/kgs/las/*.las                               original LAS files (~1.5 GB)
data/interim/miss_logs.parquet                       merged Mississippian-interval logs, 0.5 ft
```
