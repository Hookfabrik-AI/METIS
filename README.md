# MÉTIS — Research Repository

**HOOKFABRIK · Independent AI Research · Documentation updated 18 October 2026**

MÉTIS is an experimental, small Transformer for **structured constraint problems**, not a general-purpose language model. The archived P2 configuration has **679,571 trainable parameters**. Its candidates can be checked by a separate deterministic verifier. The research asks whether model-generated candidates can help a larger local language model solve constrained tasks more efficiently than simple alternatives.

**Evidence status:** P2 source code, seven checkpoints, seven data splits and evaluation records are archived. P3 is a **project-reported** training result; P3 checkpoints and raw evaluations have **not** been provided or independently reproduced. The historical Qwen comparisons used **P2**, not P3.

[Research book (standalone HTML)](docs/index.html) · [Methodology](docs/methods.md) · [Findings](docs/findings.md) · [Limitations](docs/limitations.md) · [Reproducibility](REPRODUCIBILITY.md)

> GitHub displays the HTML file as source; to use the interactive research book, download `docs/index.html` and open it in a browser. The book contains its own styling and scripts and does not depend on the private reader-building toolkit.

## Research phases

| Phase | Evidence status | Available materials |
|---|---|---|
| **P2** | Archived; integrity checkable | Source, seven data splits, seven selected weights and evaluations |
| **P3** | Reported, **not independently verified** | Progress report dated 18 October 2026; no raw P3 data or weights |
| **Qwen comparison** | Archived P2 runs, reaggregated | Recorded tasks and responses; no newly executed benchmark |

The reported P3 results describe the same model architecture trained further, and claim success on C2–C6, including the previously failed learned-control criterion C4. See [P3 status](docs/p3-status.md) and [P3 artifact requirements](P3_INGESTION.md). Reported significance or accuracy is not treated as independently verified P3 evidence.

## Historical twelve-task Qwen comparison

The four-arm snapshot combines prior partial runs: T01 from run_04; T02–T05 from run_03; T06–T09 from run_04; and T10–T12 from run_05. The earlier T01 recording remains archived. **This is not a pre-registered, independently replicated benchmark.**

| Arm | Correct | Qwen output tokens | Summed Qwen response time |
|---|---:|---:|---:|
| A — Qwen without a candidate | 11/12 | 40,559 | 2,045.3 s |
| B — Qwen + MÉTIS P2 candidate | 10/12 | 36,241 | 1,892.8 s |
| C — Qwen + random candidate | 10/12 | 52,074 | 2,819.2 s |
| D — Qwen + Min-Conflicts (256 checks) | 11/12 | 24,910 | 1,367.5 s |

MÉTIS reduced Qwen output-token use by **10.6%** compared with A, **but solved one fewer task**. The deterministic Min-Conflicts baseline did better in this snapshot. These numbers do **not** demonstrate a general speedup, a causal benefit of the learned candidate content or complete end-to-end speed: candidate generation, verification and some model-loading/prompt-processing costs are separate.

An earlier two-arm P2 study recorded larger savings on easier tasks, but used different hint packages and cannot isolate the effect of learned model content. See [historical two-arm note](docs/historical-qwen-note.md) and [findings](docs/findings.md).

## Archive layout

```text
research/p2/               archived P2 model, generator, training and evaluation code
research/qwen/historical/   historic Qwen experiment sources; external runtime not bundled
models/p2/                 seven selected P2 checkpoints (three seeds)
datasets/p2/               seven synthetic data splits and their manifest
evidence/p2/               archived P2 evaluation and probes
evidence/qwen/             recorded Qwen tasks, responses and run summaries
evidence/index.json        machine-readable four-arm statistics and research scope
evidence/provenance.json   original and sanitized artifact hashes
reports/p3/                reported, unverified P3 progress
docs/                      architecture, methods, results and limitations
scripts/                   integrity and reaggregation utilities
tests/                     offline regression tests
```

## Verify the archived evidence

```bash
python3 scripts/verify_evidence.py
python3 scripts/summarize_qwen.py
python3 -m unittest discover -s tests -v
```

These checks confirm **bytes and arithmetic**, not that historical training or the original Qwen trials have been rerun. For a new P2 training run, consult [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Full historical P2 comparison requires unavailable P1 artifacts, while the archived Qwen runners require external runtime components.

## Provenance, licensing and release

Selected archival sources contain **documented identifier/path redactions**. Original SHA-256 digests remain in [evidence/provenance.json](evidence/provenance.json) alongside the hashes of the checked-in versions. Historical experiment measurements and checkpoint bytes are not rewritten as if they were newly observed.

Original HOOKFABRIK-owned source code and project documentation are licensed under **[Apache License 2.0](LICENSE)**. Research datasets, recorded evidence and model weights require separate ownership and license clearance: see [LICENSE_SCOPE.md](LICENSE_SCOPE.md). Scientific publication, repository visibility and license permission are separate decisions. The [release checklist](RELEASE_GATE.md) has not been signed off.
