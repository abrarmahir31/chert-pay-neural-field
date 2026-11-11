# Running on a lab machine (draft; machine specs not yet known, nothing assumed)

```bash
git clone https://github.com/abrarmahir31/chert-pay-neural-field
```
```bash
cd chert-pay-neural-field
```
```bash
bash scripts/setup_machine.sh
```
For a CUDA build set `TORCH_INDEX` as described at the top of `scripts/setup_machine.sh`.
```bash
source .venv/bin/activate && make data && make audit
```
```bash
python scripts/make_synthetic.py --config configs/scale_up.yaml
```
Experiment runners (one command each, all reading `--config`) are added in Phase 3 and 4 and
will be listed here.

## Pushing results back
Only small files under `results/` and `figures/` (JSON, CSV, PDF). Never `data/`.
```bash
git checkout -b results/<machine>-<date>
```
```bash
git add results figures && git commit -m "Results from <machine>: <experiment>" && git push -u origin HEAD
```
The pre-commit hook rejects files above 2 MB.
