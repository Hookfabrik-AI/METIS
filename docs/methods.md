# Methods

## Questions

Can P2 handle structured constraint tasks? Can its proposals improve a larger local language model's efficiency **without reducing correctness**? Are any savings caused by learned information rather than merely the inclusion of a candidate or a different prompt?

## Archived P2 evidence

P2 code, seven synthetic dataset splits, seven selected checkpoints and historic evaluations are archived and hash-registered. These files can be checked for integrity, but original model training and earlier P1 comparisons have not been independently rerun.

## Historical four-arm Qwen comparison

The study used 12 already-formalized constraint tasks and `qwen3.5:latest` with temperature 0 and thinking disabled. Arms: **A** no proposal; **B** MÉTIS P2 greedy proposal; **C** random candidate; **D** Min-Conflicts candidate at 256 checks.

The registered aggregation selects T01 from run_04, T02–T05 from run_03, T06–T09 from run_04 and T10–T12 from run_05. T01 appears in more than one run; the unused historical record is preserved separately. These were resumed partial runs, **not** one pre-registered sequence.

Metrics: correct answers, Qwen output tokens and recorded Qwen response time; candidate production, verification, model loading and caching are additional costs.

## Limitations

The small sample, single evaluations, interrupted runs, uncontrolled cache/hardware state and unpinned `latest` model tag preclude strong statistical or causal claims. Natural-language problem extraction was not tested.

See [findings](findings.md), [limitations](limitations.md) and [the registered evidence](../evidence/index.json).
