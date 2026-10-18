# MÉTIS — Research release checklist

A passing technical test suite is not automatic scientific, legal or public-release approval.

- [ ] Audit all files and reachable Git history for identifying private paths, secrets and unapproved material.
- [ ] Review copyright, provenance and redistribution rights for code, datasets, model weights and archived external resources; see [LICENSING.md](LICENSING.md).
- [ ] Admit P3 source, checkpoints and raw results only through separate security/provenance checks and independent reaggregation.
- [ ] Pin models, digests, inputs, seeds and dependencies; document the exact compute environment.
- [ ] Run sufficiently powered paired evaluations including no hint, neutral hint, random proposal, rule, Min-Conflicts and MÉTIS.
- [ ] Document correctness, statistical uncertainty, anchoring failures, OOD behavior and complete end-to-end cost.
- [ ] Provide missing P1 evidence for historical comparisons or narrow the corresponding claims.
- [ ] Obtain independent technical/evidence review and explicit human acceptance for the exact public snapshot.

The current 12-task results do **not** establish general LLM acceleration. Repository visibility and open-source licensing are separate from scientific validation.
