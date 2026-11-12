.PHONY: install data audit test lint synthetic identifiability identifiability-v2 pay-benchmark real real-standin
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

identifiability-v2: ## benchmark v2: different-family truth, 200 wells, unknown Rw (DECISIONS.md D24a)
	$(PY) scripts/run_identifiability.py --suite v2 --config $(CONFIG)

pay-benchmark:   ## benchmark v3: marginal (low-contrast) wells; field vs well-by-well vs global parameters
	$(PY) scripts/run_identifiability.py --suite v3 --config $(CONFIG)

real:            ## real-data test D24b: all entries + evaluation (heavy; see docs/lab_gpu_workflow.md)
	$(PY) scripts/run_real_all.py --config $(CONFIG)

real-standin:    ## same pipeline on a small synthetic stand-in (self-test, no real data needed)
	$(PY) scripts/run_real_all.py --config $(CONFIG) --standin
