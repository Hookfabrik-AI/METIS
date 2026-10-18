# Research findings

## P2

Historical sources and seven dataset splits are documented with original and curated digests. P2 introduced combined constraint-slot encoding. In the recorded P2 evaluation, learned control did **not** outperform a simple rule convincingly: C4 failed (`p = 0.906`). Full historical P1 comparisons require unavailable earlier materials.

## Earlier two-arm observation

A separate 12-task report compared Qwen alone against Qwen with a full MÉTIS P2 hint package: **11/12 versus 10/12 correct**, with **48,945 versus 29,607 output tokens**. The prompt packages differed and there was no controlled random/heuristic comparison. These results do not isolate a causal learned-model contribution. The original [historical note](historical-qwen-note.md) is preserved in German as a hash-registered research artifact.

## Later four-arm snapshot

The table is reconstructed from selected archived partial-run records (see [methods](methods.md)).

| Arm | Method | Correct | Qwen output tokens | Recorded Qwen time | Correct candidates (post hoc) |
|---|---|---:|---:|---:|---:|
| A | No proposal | 11/12 | 40,559 | 2,045.3 s | — |
| B | MÉTIS P2 | 10/12 | 36,241 | 1,892.8 s | 5 |
| C | Random candidate | 10/12 | 52,074 | 2,819.2 s | 0 |
| D | Min-Conflicts (256 checks) | 11/12 | 24,910 | 1,367.5 s | 7 |

The MÉTIS arm used **10.6% fewer output tokens than A**, but solved one fewer task. The deterministic Min-Conflicts baseline was better on both correctness and token use. Qwen response-time totals omit relevant end-to-end costs. These observations do **not** establish generalizable acceleration, a causal advantage of learned hints or improved reasoning ability.

## P3

Reported improvements in P3, including C4 learned-control utility `+0.015` against a rule (`p < 0.001`), remain **unverified by raw P3 evidence in this repository**. P3 was not used in the Qwen four-arm experiment.

See [P3 status](p3-status.md) and [limitations](limitations.md).
