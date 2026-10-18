# MÉTIS — research roadmap (proposed work, not completed results)

**P3:** [Reported progress and limits](p3-status.md) · [P3 artifact requirements](../P3_INGESTION.md). Neither document constitutes independent P3 validation.

1. **Freeze an experimental environment:** Record specific Python, PyTorch and Ollama versions, immutable Qwen model digests, memory/cache status, fixed task IDs and source hashes.
2. **Make Qwen experiments standalone:** Replace the unavailable external runtime without silently rewriting the historical experiment; independently review the new implementation.
3. **Run a paired controlled study:** Compare no hint, neutral filler, uniform random candidates, deterministic rules, Min-Conflicts, MÉTIS and optional model ablations under comparable formats/token budgets and randomized arm order.
4. **Evaluate difficulty and distribution shift:** Expand task families; distinguish hard in-distribution tasks from genuinely new constraint types.
5. **Assess calibration and risks:** Measure candidate confidence, abstention, misleading-hint sensitivity, anchoring and degraded correctness.
6. **Account for total cost:** Include candidate generation, verifier, tokenization, model loads, caches, prompt processing and memory use in end-to-end time under constrained hardware budgets.
7. **Obtain independent acceptance:** Review sources and data, repeat paired experiments, preserve negative findings, and obtain explicit human approval before publication.
