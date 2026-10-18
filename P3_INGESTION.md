# P3 research artifact intake

The reported P3 progress is **not** a release of independently reproducible P3 evidence. Add P3 assets only after selection, source inspection, privacy review and separate research acceptance.

## Required acceptance checklist

- [ ] P3 implementation snapshot and P2-to-P3 source diff, without machine-specific paths.
- [ ] Training configurations, hyperparameters, seeds, version identifiers and details of data/numerical-constant changes.
- [ ] P3 train/dev/test splits, generator sources and SHA-256 manifests, including the documented data-filter correction.
- [ ] P3 checkpoint selection and exact correspondence between model, seed, run and test set.
- [ ] Machine-readable C2–C6 results with per-instance paired task outcomes and definitions of FB@4 and L−1.
- [ ] Recomputable C4 significance tests (rule baseline, sample size, seeds, effect size) and verifier/forward-pass costs.
- [ ] K4/K5 failure examples, Min-Conflicts records and aligned baseline conditions.
- [ ] Independently executable aggregation scripts and a reproducibility report.
- [ ] Secret, privacy, licensing, ownership and provenance review of each proposed artifact.
- [ ] Independent reviewer sign-off and explicit human acceptance.

## Paths, if approved

```text
research/p3/     versioned P3 implementation and configuration
datasets/p3/     approved data splits and hashes
models/p3/       approved checkpoints and model cards
evidence/p3/     raw evaluations, seeds, analysis and provenance
scripts/         independent P3 integrity and reaggregation checks
```

Do **not** fabricate placeholder raw records to populate these paths. Until actual P3 artifacts are verified, all P3 results remain labeled as project-reported findings in [docs/p3-status.md](docs/p3-status.md).
