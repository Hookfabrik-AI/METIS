# Research methodology

## Research questions

- Can a small trained neural model represent structured constraints well enough to distinguish deceptively similar variable/coefficient bindings?
- Do P2-generated candidates improve accuracy or reduce a larger language model's output tokens and true end-to-end cost?
- What **incremental** value does learned content provide over a neutral hint, random candidate, simple rules, Min-Conflicts and deterministic verification?
- How can the model avoid misleading a larger LLM with high-confidence incorrect proposals?

## P2 protocol

The original four classes were `K1_numbers`, `K2_schedule`, `K3_logic` and `K4_equations`, with external tests on `K5_coloring`. Problem generation was synthetic, with train/dev/test separation and dataset settings recorded in `datasets/p2/manifest.json`.

`problems.violations` implements an external deterministic verifier. The network receives structured problem inputs and, in feedback mode, previous candidates and violation flags. It does **not** receive a solver trace or a correct answer as part of the input. See `research/p2/model.py`, `cog.py` and `evaluate.py`.

## Four-arm Qwen protocol

- **A:** No candidate.
- **B:** Greedy MÉTIS P2 candidate.
- **C:** Uniformly random value per variable, under a fixed seed.
- **D:** Min-Conflicts candidate using at most 256 verifier evaluations; the best observed candidate is retained.
- **B/C/D:** The same introductory text: an unverified solution proposal that may be wrong (original historical prompts were in German).
- **Qwen:** Historical settings were `qwen3.5:latest`, `think=false`, temperature `0`, seed `0`, `num_predict=4096`, up to three attempts and a bounded runtime per task. `latest` is **not** an immutable model digest.
- **Feedback:** Incorrect parseable responses receive only violated constraints. The historical, path-redacted runner is `research/qwen/historical/metis_qwen_4arm.py`.
- **Measures:** Correct/12, output tokens (sum of `eval_count` across attempts), and recorded `wall_s` per arm. Verifier CPU, MÉTIS CPU, Min-Conflicts CPU, prompt processing, model loading and warmup must all be considered in a complete end-to-end cost analysis.

## Statistical boundary

There are only twelve tasks, no repeated paired sampling per condition, and variable memory/cache conditions. The four-arm summary joins three partial runs, including a documented duplicate, instead of a single pre-registered uninterrupted run. These observations establish neither a generalizable causal benefit nor spontaneous reflection or general intelligence.
