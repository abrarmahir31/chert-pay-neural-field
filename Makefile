.PHONY: install data audit test lint synthetic identifiability
CONFIG ?= configs/cpu_small.yaml
PY ?= python

install:
	$(PY) -m pip install -e ".[dev,data]"

data:            ## download KGS archives + Barber County LAS files into data/raw (not committed)
	$(PY) scripts/download_data.py

audit:           ## Phase 1: parse all LAS, build inventory and audit tables in results/audit
	$(PY) scripts/audit_pass1.py
	$(PY) scripts/audit_pass2.py
	$(PY) scripts/audit_report.py

test:
	$(PY) -m pytest -q

lint:
	ruff check src scripts tests

synthetic:       ## synthetic benchmark with known truth (CONFIG=configs/scale_up.yaml on a GPU machine)
	$(PY) scripts/make_synthetic.py --config $(CONFIG)

identifiability: ## pre-registered identifiability study (DECISIONS.md D20)
	$(PY) scripts/run_identifiability.py --config $(CONFIG)
