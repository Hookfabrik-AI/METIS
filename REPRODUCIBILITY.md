# Reproducibility

## Verify the archive offline

Run from the repository root:

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

The integrity checker compares 47 curated artifacts, seven P2 dataset splits and their registered SHA-256 digests. The Qwen script reconstructs the preselected 12-task four-arm summary from stored results. These checks **do not** rerun historical training, demonstrate causation or validate P3 reports.

## P2 dataset regeneration and training

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 -I -B research/p2/dataset.py /tmp/metis-regenerated-p2
METIS_PYTHON="$PWD/.venv/bin/python" bash scripts/train_p2.sh
```

The training launcher resolves the repository root relative to its own location; training can require substantial CPU time and storage, and writes new checkpoints rather than replacing archived weights. The dependencies are not pinned to an original environment. Historical P2 C5/C6 comparisons require P1 sources/checkpoints that are not supplied, so full historical reproduction is not self-contained.

## Historical Qwen study

The original Qwen runners remain under `research/qwen/historical/`. Local paths were replaced with non-resolving labels; additional external runtime modules are not distributed. **These scripts are not standalone runners.** The saved task/response records can be independently reaggregated without Qwen, a GPU or model weights.

To repeat the study, a new independently reviewed runner must record fixed model digests, prompt variants, task IDs, trial ordering, hardware/cache state, and all generation/verification/load costs.

## Evidence boundaries

- P2 and Qwen data integrity and statistical reaggregation: checkable offline.
- Original neural training and Qwen experiments: historical, not rerun here.
- P3: project-reported progress only, without raw results or checkpoints.
- Causal or generalized efficiency: not established.

See [limitations](docs/limitations.md) and [P3 evidence intake](P3_INGESTION.md).
