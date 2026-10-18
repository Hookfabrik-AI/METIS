# Reproducibility

## 1. Offline integrity and aggregation checks

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

The integrity check compares checked-in files with `evidence/provenance.json` and verifies the P2 dataset manifest. Historical source hashes are retained separately from the hashes of privacy-redacted copies. The manifest's original generator hash is checked against its `original_sha256` provenance entry; the current published generator is checked against its separate `repo_sha256`.

The Qwen script reaggregates the explicitly selected twelve task records and checks the result against `evidence/index.json`. Neither step proves that the historical experiments were carried out correctly.

## 2. P2 data generation and new training

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Generate a new dataset in a directory that does not yet exist:
python3 -I -B research/p2/dataset.py /tmp/metis-regenerated-p2

# CPU-intensive fresh training; does not replace the archived checkpoints:
METIS_PYTHON="$PWD/.venv/bin/python" bash scripts/train_p2.sh
```

The launcher resolves its root from the parent of `scripts/`; stages A and B run for seeds 0–2 and C runs for seed 0. Tests verify the shell syntax and directory layout, **not** the entire training run. Version pinning, system libraries, hardware and timing must be recorded to compare a new run scientifically. `requirements.txt` presently lists dependency families without an independently validated environment lock.

The historical P2 evaluation requires additional P1 source and weights that are not bundled. Thus a complete re-run of the original P2 C5/C6 comparison is not yet possible from this repository alone.

## 3. Qwen historical experiments

Sources under `research/qwen/historical/` retain external runtime imports, and several absolute paths have been replaced with explicit placeholders. They are preserved for provenance and review, **not as a standalone runner**.

A new controlled end-to-end experiment requires an independent runner and pinned Qwen model digest, task set, seeds, prompt/candidate formats, execution order, cache conditions, available memory and all candidate/verification/model-load costs. The offline aggregation requires neither an Ollama installation nor the original P2 model weights.

## 4. Levels of evidence

- **Reproducible now:** hash checks for curated files, P2 data-manifest consistency, and arithmetic reaggregation of selected historic Qwen results.
- **Archived, not rerun here:** P2 training, model evaluations and Qwen generation.
- **Not established:** causal performance improvements or generalization to different LLMs/tasks.
- **P3:** project-reported progress only; no raw checkpoints or evaluations. See [P3 artifact intake](P3_INGESTION.md).

The release criteria are listed in [RELEASE_GATE.md](RELEASE_GATE.md).
