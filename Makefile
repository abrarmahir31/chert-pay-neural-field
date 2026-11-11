.PHONY: install data audit test lint
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
