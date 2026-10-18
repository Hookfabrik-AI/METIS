# Findings — evidence and interpretation

> **Version boundary:** P3 improvements are [reported, not independently validated](p3-status.md). The P2 and Qwen observations in this document remain historical **P2** findings.

## P2 — trained neural constraint proposals

The archived P2 sources and seven generated dataset splits are tracked using their original and, where redacted, checked-in SHA-256 digests. P2 introduced binding of variable ID, coefficient/sign and slot position within each constraint. The archived evaluation `evidence/p2/P2_EVAL.json` includes untrained controls, feedback ablations and P1 comparisons.

Because some P1 source code and checkpoints are not bundled, comparisons that require P1 are **archived findings**, not fully independently reproducible claims.

Learned strategy selection on the P2 test set also did **not** outperform a simple rule convincingly: the archived C4 result was non-significant (`p = 0.906`). This cannot be presented as a successful C4 validation.

## Historical Qwen two-arm experiment (run_01 and run_02)

The historical [two-arm research note](historical-qwen-note.md) reports twelve structured tasks: **11/12** correct for Qwen alone versus **10/12** with the full MÉTIS hint package; **48,945 versus 29,607** output tokens and **2,388 versus 1,580 seconds** of Qwen time. Both conditions solved all eight easier tasks; the hint condition was weaker on the four harder tasks.

The prompt packages differed in more than learned candidate quality. This comparison does **not** isolate a causal effect of the learned MÉTIS content.

## Four-arm candidate control study (run_03 to run_05)

According to the archived runner, candidate arms B, C and D share the same introductory hint text; they differ in candidate generation. The tasks were already represented as structured constraints. The following numbers were **reaggregated from recorded results**, not produced by a new Qwen run.

| Arm | Candidate method | Correct | Output tokens | Qwen response time | Correct candidates |
|---|---|---:|---:|---:|---:|
| A | None | 11/12 | 40,559 | 2,045.3 s | — |
| B | MÉTIS P2, greedy | 10/12 | 36,241 | 1,892.8 s | 5/12 |
| C | Uniform random | 10/12 | 52,074 | 2,819.2 s | 0/12 |
| D | Min-Conflicts, budget 256 | 11/12 | 24,910 | 1,367.5 s | 7/12 |

**Interpretation:** On mostly easier tasks, the P2 hint was sometimes associated with reduced generation, but the harder tasks exposed incorrect candidates and a risk of anchoring and additional work. The simple Min-Conflicts heuristic yielded the fewest tokens and matched or exceeded the no-hint success rate. The results do not establish whether the benefits come from learned content rather than the presence of a well-formed candidate.

**Selection and duplicate:** Task T01 appears in both run_03 and run_04. This table uses the later run_04 recording, while preserving the original run_03 record. Tasks T02–T05 come from run_03, T06–T09 from run_04, and T10–T12 from run_05. The runs had different memory and cache conditions, so the aggregate must not be represented as a single prospectively controlled, replicated study.
