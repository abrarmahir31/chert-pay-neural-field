#!/usr/bin/env bash
# Fresh-machine setup (Linux or WSL; no admin rights needed). Usage:
#   git clone https://github.com/abrarmahir31/chert-pay-neural-field && cd chert-pay-neural-field
#   bash scripts/setup_machine.sh            # CPU PyTorch
#   TORCH_INDEX=https://download.pytorch.org/whl/cu124 bash scripts/setup_machine.sh   # CUDA build
# Pick TORCH_INDEX to match the GPU driver (see https://pytorch.org/get-started/locally/).
set -euo pipefail
PY=${PYTHON:-python3}
$PY -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch==2.15.0 --index-url "${TORCH_INDEX:-https://download.pytorch.org/whl/cpu}"
python -m pip install -e ".[dev,data]"
python -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
python -m pytest -q
echo "Next: make data && make audit   (downloads about 1.6 GB of public KGS data)"
