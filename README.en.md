# MÉTIS — Research Repository

**HOOKFABRIK · Independent research · Documentation dated 18 October 2026.**

MÉTIS is a small trained Transformer (**679,571 trainable parameters in the archived P2 standard configuration**) used to propose solutions to structured constraint problems. P2 includes joint embedding of constraint-slot identity and coefficient/sign. A later experiment asked whether MÉTIS proposals could improve the output efficiency of a larger local Qwen model, compared with no hint, a random hint, and a Min-Conflicts heuristic.

**Twelve-task four-arm snapshot** (T01 from run_04; T02–05 from run_03; T06–09 from run_04; T10–12 from run_05): no hint 11/12, 40,559 output tokens; MÉTIS hint 10/12, 36,241; random hint 10/12, 52,074; Min-Conflicts hint 11/12, 24,910. This is an assembled snapshot across resumed runs, **not a causal proof** or an independently replicated benchmark. Qwen time totals exclude several end-to-end costs.

See [methods](docs/methods.md), [findings](docs/findings.md), [limitations](docs/limitations.md), [reproducibility](REPRODUCIBILITY.md), and the machine-readable [`evidence/index.json`](evidence/index.json).

Offline verification: `python3 scripts/verify_evidence.py && python3 scripts/summarize_qwen.py`.

Historical P2 code and synthetic datasets are included, together with seven selected model weights and archived evaluation results. The historical Qwen runners still depend on private external runtime components and were deliberately not advertised as standalone. Check security, licensing, evidence scope and the [release gate](RELEASE_GATE.md) before changing repository visibility. No open-source license is implied by the presence of these research files.

## P3 status (reported, not independently verified)

A project report dated 2026-10-18 states that the unchanged P2 architecture was trained into P3, meeting reported criteria C2–C6, including learned control C4. **No P3 weights, raw evaluation records, or training run are present in this repository.** See [P3 status (German)](docs/p3-status.md) and [artifact intake checklist](P3_INGESTION.md). The Qwen comparison in this repository used P2, not P3.

## Research book

[Read the MÉTIS research book](docs/index.html). Evidence and methods are documented in the versioned research files.
