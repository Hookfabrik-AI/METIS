# MÉTIS research roadmap

The following are **proposed experiments**, not completed findings. [P3 progress](p3-status.md) remains project-reported.

1. Fix the entire runtime environment: Python/PyTorch/Ollama and model digests, hardware, memory, caches, seeds and source hashes.
2. Develop a separately reviewed standalone Qwen experimental runner without external proprietary runtime dependencies.
3. Run paired randomized comparisons with no hint, neutral hint, random proposal, deterministic rule, Min-Conflicts, MÉTIS and model ablations, using comparable formats and budgets.
4. Extend evaluation to harder tasks and genuinely new distributions.
5. Quantify hint anchoring, calibration, abstention and failure recovery.
6. Measure complete end-to-end cost including proposal generation, verifier work, prompt processing, loading and caching.
7. Publish full source/results, negative findings and reviewer observations only after final human approval.
