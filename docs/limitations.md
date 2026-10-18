# Limitations and reproducibility gaps

1. **No independent experiment reruns:** Archived bytes and aggregates were checked. The original neural training and Qwen generation were not re-executed.
2. **Small and assembled sample:** Twelve structured tasks in the four-arm comparison were selected from partial runs 03–05. T01 was run more than once; the selection rule is explicit and raw data remain unchanged.
3. **External Qwen runtime:** Historical runners still import `res1_instance` and `resource_profile` from an external, unbundled runtime. Machine-local paths were replaced with placeholders; these scripts are **not** independently runnable as released.
4. **Non-pinned Qwen weights and costs:** `qwen3.5:latest` is mutable. System state and some Ollama load/prompt costs were not recorded as consistent end-to-end cost measurements.
5. **Missing P1 comparison files:** The archived P2 evaluation refers to P1 code and weights that are not included. Some comparisons cannot be fully rerun using this repository alone.
6. **Checkpoint safety:** Seven selected `.pt` weights remain unaudited binary artifacts. Load only from trusted sources and prefer `torch.load(..., weights_only=True)`.
7. **Structured tasks only:** Task statements were formalized before reaching Qwen. No claim about natural-language problem formalization, unrelated domains, larger LLMs or multi-agent reasoning is warranted.
8. **Quality degradation:** In the four-arm snapshot, MÉTIS hints solved 10/12 versus 11/12 without a hint. The earlier two-arm experiment showed a potential anchoring failure.
9. **Licensing:** Apache 2.0 covers owned source and project documentation. Redistribution and reuse rights for archival datasets and model weights still require explicit review; see [LICENSE_SCOPE.md](../LICENSE_SCOPE.md).
10. **P3 is only reported:** P3 checkpoints, run configurations, raw tasks and independently reproducible test outputs are not included. See [P3 status](p3-status.md).

These limitations constrain the conclusions; they do not invalidate the accurately archived observations.
