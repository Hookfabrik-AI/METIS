# P3 evidence intake

The current P3 material is a **project progress report**, not an independently reproducible model release. P2 sources/checkpoints must not be relabeled as P3.

Required before promoting P3 to verified research evidence:

- [ ] Source snapshot and diff against P2, complete training configuration and architecture specification.
- [ ] Dataset generator, changed numerical constants, splits, random seeds, hashes and correction of the early filter issue.
- [ ] P3 checkpoints mapped to their exact source, seed, training run and evaluation.
- [ ] Per-task C2–C6 results, with defined FB@4 and L−1 metrics and paired comparisons.
- [ ] C4 statistical test, sample size, rule baseline, effects and full cost accounting including checks and forward passes.
- [ ] K4/K5 failure cases and consistent Min-Conflicts baseline specification.
- [ ] Reaggregation scripts and independent review.
- [ ] Privacy, secret, license and rights review; explicit human approval.

Proposed destinations after review: `research/p3/`, `datasets/p3/`, `models/p3/`, `evidence/p3/`. No placeholder raw artifacts should be created.

Until then see [reported P3 status](docs/p3-status.md).
