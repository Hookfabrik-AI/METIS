# MÉTIS — Research Archive

**HOOKFABRIK · Independent AI Research · 18 October 2026**

MÉTIS is a small Transformer specialized in structured constraint-solving tasks, not a general-purpose language model. The archived **P2 architecture has 679,571 trainable parameters**. It proposes candidates that can be independently checked.

**Evidence status:** P2 includes archived source code, seven selected checkpoints, synthetic datasets and recorded evaluations. P3 is **project-reported, not independently verified here**: no P3 weights, raw evaluation records or training logs are included. Neither historical training nor Qwen execution has been rerun for this repository.

[Research book](docs/index.html) (standalone HTML; open in a browser) · [Methods](docs/methods.md) · [Findings](docs/findings.md) · [Reproducibility](REPRODUCIBILITY.md)

## Research question

Do learned proposals from a small specialized model help a larger local language model solve structured tasks more efficiently **without sacrificing correctness**? In particular, can any benefit be attributed to the *learned model* rather than simply supplying a candidate or using a deterministic heuristic?

## Research stages

| Stage | Evidence | Limitation |
|---|---|---|
| P2 | Code, seven selected checkpoints, seven dataset splits and historical evaluation records | Experiments not independently rerun; some P1 dependencies missing |
| P3 | Progress report dated 18 October 2026 | No machine-readable P3 raw evidence or checkpoints |
| Qwen comparison | Archived tasks, responses and reaggregated results | Uses **P2**, assembled from resumed partial runs |

Reported P3 improvements, including learned control C4, are documented separately under [P3 status](docs/p3-status.md) and require further evidence as described in [P3 evidence intake](P3_INGESTION.md).

## Historical Qwen four-arm comparison

A 12-task descriptive snapshot selected T01 from run_04, T02–T05 from run_03, T06–T09 from run_04 and T10–T12 from run_05. **This is not a single pre-registered, independently replicated experiment.**

| Condition | Correct | Qwen output tokens | Recorded Qwen time |
|---|---:|---:|---:|
| A — no proposal | 11/12 | 40,559 | 2,045.3 s |
| B — MÉTIS P2 | 10/12 | 36,241 | 1,892.8 s |
| C — random proposal | 10/12 | 52,074 | 2,819.2 s |
| D — Min-Conflicts (256 checks) | 11/12 | 24,910 | 1,367.5 s |

MÉTIS P2 reduced Qwen output tokens by **10.6%** relative to A, but solved **one fewer task**. The deterministic Min-Conflicts baseline performed better in this snapshot. Times exclude relevant end-to-end costs. These results **do not establish causal or generalizable LLM acceleration**.

## Repository

```text
research/p2/             P2 source, model and training code
research/qwen/historical/ Historical, path-redacted runners; external runtime required
datasets/p2/             Seven synthetic splits and hash manifest
models/p2/               Seven selected checkpoints
evidence/p2/             Historical P2 evaluations
evidence/qwen/           Tasks, results and run summaries
evidence/provenance.json Original/curated hashes and redaction records
reports/p3/              Reported P3 progress, not independently verified
docs/                    Research book, methods, findings and limitations
scripts/                 Integrity and offline aggregation
tests/                   Offline regression checks
```

## Offline checks

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

Passing these checks establishes internal archive consistency, **not** successful re-execution of the original experiments. See [reproducibility](REPRODUCIBILITY.md) and [limitations](docs/limitations.md).

## License and provenance

Original, rights-cleared HOOKFABRIK source and research documentation are covered by the **Apache License 2.0**. Datasets, archived weights and externally sourced historical material require separate rights verification. See [LICENSING.md](LICENSING.md) for the explicit scope; no redistribution rights are implied for excluded materials.

The repository records its provenance in [evidence/provenance.json](evidence/provenance.json). [SECURITY.md](SECURITY.md) and [RELEASE_GATE.md](RELEASE_GATE.md) describe the additional checks needed before public publication.
