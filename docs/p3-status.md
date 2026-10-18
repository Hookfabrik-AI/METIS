# MÉTIS P3 — Reported progress

**18 October 2026 · Project-reported, not independently verified.** This is not a release of independently reproduced P3 evidence. The archive contains no P3 checkpoints, raw evaluations or complete training configuration.

## Reported results

- Architecture reportedly unchanged from P2, with additional/further training.
- C2 and C3 reportedly passed.
- C4 learned control reportedly passed with utility `+0.015` against the rule (`p < 0.001`); P2 had failed (`p = 0.906`). The reported advantage came from saved verification costs even though the model required more forward passes. Without check costs, the learned policy performed worse.
- C5 on K4 paired tasks: L−1 `+6` to `+10` percentage points and FB@4 `+8` to `+19` points versus P2.
- C6 on K1: L−1 `+6` to `+12` points and FB@4 `+9` to `+13` points.
- Aggregate FB@4 was reported as roughly `0.80–0.82`. A cited P2 value around `0.75` comes from P2's own test set and is **not itself a paired comparison**.
- The report lists 835 C4 repair decisions and 209 new-solve decisions; not independently reaggregated.

## Negative findings and unknowns

- K4 FB@4 reportedly remained weak (`0.44–0.51`) compared with Min-Conflicts at 256 checks (`0.61`).
- Feedback versus resampling reportedly gained only about 2–3.5 percentage points.
- Results on K5 were mixed; one seed was worse than P2 on hard tasks.
- Dataset quantity and numeric constants changed together; an isolated ablation is missing.
- A too-strict filter was reportedly corrected before the training run; original logs are not available here.
- Reported late-stage training improvement does not prove longer training would improve the model.

The numbers were transcribed from a project progress report rather than calculated from machine-readable P3 results. Do not describe C4 as independently replicated, conflate P2 and P3, or claim the Qwen experiment used P3.

See [P3 evidence intake](../P3_INGESTION.md).
