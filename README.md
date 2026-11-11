# chert-pay-neural-field

Spatial physics-informed neural field for label-free petrophysical inversion of low-resistivity
microporous chert pay (Mississippian "chat", Barber County, Kansas).

**Status:** work in progress (data audit complete). See `PROGRESS.md` and `DECISIONS.md`.

## Quick start
```bash
python -m pip install -e ".[dev,data]"
make data     # KGS archives + original LAS files into data/raw (not committed)
make audit    # results/audit/*  (inventory, mnemonic table, summary JSON)
make test
python scripts/make_synthetic.py --config configs/cpu_small.yaml
```

## Data
Well logs, tops and headers are public data of the Kansas Geological Survey; see
`data/README.md` for sources, terms of use and the required credit line. No raw data are
stored in this repository.

## Layout
`src/chertfield/` library, `scripts/` entry points, `configs/` settings, `tests/` unit tests,
`results/` machine-written tables and JSON, `figures/`, `paper/`, `docs/`.
