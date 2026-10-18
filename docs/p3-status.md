# MÉTIS P3 — preliminary progress report

**Reported:** 18 October 2026 · **Evidence:** project-reported, **not independently checked against P3 checkpoints or raw evaluation data**.

P3 is an ongoing research stage, not an independently replicated release. This repository does **not** contain P3 training runs, raw P3 evaluations or P3 model weights. P2 archival assets must not be relabeled as P3.

## Changes reported relative to P2

- **Architecture:** Reportedly unchanged; P3 was trained further. The precise changes in training and data cannot yet be audited without the P3 configuration and code.
- **C2/C3:** Still passed, as reported.
- **C4 — learned control vs. a rule:** P2 failed (`p = 0.906`); P3 reportedly passed with a small difference of `+0.015`, `p < 0.001`. The gain came from fewer verifier checks despite more forward passes; ignoring verification costs, the policy was worse.
- **C5 on K4, paired P3 minus P2:** L−1 increased by **6–10 percentage points**; FB@4 by **8–19 percentage points**.
- **C6 on K1, P3 minus P2:** L−1 increased by **6–12 percentage points**; FB@4 by **9–13 percentage points**.
- **FB@4 across classes:** Reported as approximately `0.80–0.82`; the P2 reference around `0.75` was measured on its **own** test set, so these standalone numbers are **not a paired comparison**.
- **C4 decisions:** 835 repair decisions and 209 fresh attempts were reported, without independent reaggregation.

## Negative and qualified findings

- **K4 remains weak:** Reported FB@4 of `0.44–0.51`, below Min-Conflicts with 256 checks (`0.61`).
- **Feedback benefit over fresh sampling:** Reportedly only about **2–3.5 percentage points**.
- **K5 results:** Mixed, including worse hard-task performance for seed 1 than P2.
- **Ablation missing:** Both training data and numerical constants changed, so the contribution of each change is unknown.
- **Training duration:** Learning curves were still rising late in training. That does not prove that longer training would help.
- **Data filtering:** An initially over-restrictive filter could have distorted test splits. According to the report, the affected run was stopped **before training** and restarted after correction.
- **Execution environment:** Approximately half of the available CPU at low priority was reported; the original environment and timing logs are absent here.

## Evidence status

Source: project progress report dated 18 October 2026. Figures were **transcribed from a reported result summary**, not independently recomputed from machine-readable P3 artifacts. There is insufficient information to independently assess statistical methods, sample sizes, exact C2/C3 thresholds, confidence intervals or run-to-run variance.

**Do not claim** independent replication of P3 C4, generalized problem-solving ability, or use of P3 in the archived Qwen four-arm comparison (that experiment used P2).

See [P3 artifact intake](../P3_INGESTION.md) for the evidence needed before P3 can be represented as independently verified research.
