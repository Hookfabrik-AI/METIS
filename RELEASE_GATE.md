# MÉTIS — Public-release acceptance gate

This checklist is **not automatically satisfied** by a successful test run, an Apache license file, or GitHub visibility. Checkpoints, research claims, redistribution rights and the actual code/document set need separate acceptance.

- [ ] Security and privacy scan covering the **current files, full reachable Git history and all archival artifacts**; no secrets, private paths, undisclosed runtime code or identifying information.
- [ ] Rights/ownership verification for original code, documentation, synthetic datasets, model checkpoints and historical records. Confirm separate artifact license statements in `LICENSE_SCOPE.md`.
- [ ] P2 original and repository SHA-256 provenance verified; all redactions explained without replacing historical source hashes.
- [ ] Training launcher and basic runtime smoke test in an appropriately isolated environment; pinned Python, library, model and system versions.
- [ ] External missing P1 and Qwen runtime dependencies accurately described; unsupported reproduction claims removed.
- [ ] P3 checkpoints, raw per-task evaluations and training configuration reviewed independently **before** converting reported P3 results to verified findings.
- [ ] Repeated, paired and adequately powered evaluations with confidence/uncertainty measures; fair baseline conditions including rules, random candidates, neutral prompts and Min-Conflicts.
- [ ] Correctness, hint-anchoring failures, out-of-distribution behavior and complete end-to-end cost accounting documented.
- [ ] Independent reviewer signs off the scope of conclusions, raw evidence and public-facing documentation.
- [ ] Explicit human acceptance for public artifacts, claims and rights.

Do not claim that MÉTIS generally speeds up large language models. The archived evidence does not support that conclusion. Repository visibility does not determine scientific validity or grant third-party intellectual-property rights.
