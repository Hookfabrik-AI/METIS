# MÉTIS P2 × Qwen — Historical two-arm research note

**Status at the time:** Experiment completed; an independent reviewer reportedly marked the result `VERIFIED_WITH_NOTES`. This document is an edited English rendition of an archived project report, not a newly executed validation.

**Version distinction:** The experiment used a fixed **P2 checkpoint**. A working title referring to “P3” in the old report did not mean that the later trained P3 model was used. The later four-arm comparison is covered separately in [findings](findings.md), with recorded task data under [evidence/qwen](../evidence/qwen/).

## 1. Research questions

Can a small CPU model trained on structured constraints (MÉTIS P2) provide candidates that help a larger local LLM (`qwen3.5:latest`) solve problems with less generation work and no loss of accuracy?

A narrower question remains: does **learned MÉTIS content** add value beyond any candidate or prompt-format change?

## 2. Experimental setup

- **MÉTIS:** Fixed P2 checkpoint. An adapter generated a proposed solution, top-two values per variable and an estimated confidence. The planned repair hint was not triggered in the evaluated runs.
- **Qwen:** `qwen3.5:latest`, reasoning disabled, temperature 0.
- **Tasks:** Twelve new structured constraint problems; translating ordinary natural-language requests into constraints was **not** tested.
- **Conditions:** Qwen with no candidate versus Qwen with the full MÉTIS hint package.
- **Feedback:** If a parseable response was incorrect, the verifier would report violated constraints in either condition. No model-side MÉTIS repair was activated in the evaluated run.
- **Controls missing:** No random candidate, rule candidate, matched neutral hint or repeated runs per condition.

## 3. Observations

| Measurement | Qwen alone | Qwen + MÉTIS hint |
|---|---:|---:|
| Easier problems correct | 8/8 | 8/8 |
| Harder problems correct | 3/4 | 2/4 |
| Total correct | **11/12** | **10/12** |
| Easier output tokens | 26,277 | 8,595 |
| Harder output tokens | 22,668 | 21,012 |
| Total output tokens | **48,945** | **29,607** |
| Measured Qwen time | **2,388 s** | **1,580 s** |

Across twelve tasks, output decreased by **19,338 tokens (39.5%)** and summed observed Qwen time decreased by **808 seconds (33.8%)**. On the easier group, output-token use decreased by approximately **67.3%**; on harder tasks the decrease was approximately **7.3%**.

These are differences between **two prompt packages**, not a causal demonstration of a learned-model advantage.

## 4. Observed failure patterns

- Among eight easier tasks, MÉTIS produced a directly correct candidate five times. Qwen could inspect the constraints and reuse valid candidates.
- Qwen recognized and discarded several incorrect hints on other easier tasks.
- On **all four harder tasks**, the MÉTIS candidate was incorrect.
- **T11 (logic):** Qwen succeeded alone but failed with the hint. It discarded a potentially valid approach while referring to a high-confidence MÉTIS proposal (`x4 = 1`, 97%). This supports an *anchoring observation*, not proof that the hint was the sole failure cause; Qwen also made independent errors.
- **T09:** Both conditions failed. Text from an aborted, non-evaluated part was not archived.
- **T10/T12:** Both conditions succeeded despite wrong MÉTIS candidates, with somewhat lower observed Qwen time under the hint condition.

## 5. Reported independent review

The accompanying project review summary assigned `VERIFIED_WITH_NOTES`. It reported that all twelve candidate outputs had been reproduced from a saved checkpoint, timing totals agreed within approximately 0.05 seconds of Ollama records, and six reporting clarifications had been incorporated.

**Causality was not verified.** The comparison tested complete hint packages, not the incremental effect of learned content compared with generic candidates. This archive does not itself include all inputs necessary to independently repeat those historical reviewer checks.

## 6. Evidence limitations

1. Observed generation rate fluctuated around **18–31 tokens/s**; the reason was not established.
2. Hint prompts were approximately **twice as long** as no-hint prompts.
3. Some input reuse/caching could affect wall-clock time; output-token counts are a more stable descriptive measure here.
4. Two Ollama timing components (loading and prompt evaluation) were not persisted in `results.json`.
5. For the four harder tasks, MÉTIS CPU time summed to **0.28 s**; a corresponding first-run value was unavailable and must not be extrapolated.
6. Twelve tasks with one run per condition do not permit robust generalization or a fair candidate-method comparison.
7. Natural-language task formalization, larger model families and unrelated agent systems were not evaluated.

## 7. Research conclusion

**Observed:** A small trained model produced real candidate hints that Qwen sometimes used. The complete hint condition reduced token use markedly on easier structured problems, but reduced the number of correct answers on hard problems.

**Not established:** Whether learned candidate content caused the savings; a general improvement in problem solving; or transfer to other model sizes, tasks or domains.

A useful follow-up study would independently compare learned hints against rule-generated, random and equally formatted neutral hints, with calibration and anchoring risk as explicit outcomes.

## 8. Provenance and next steps

This is a **historical observation with mixed outcomes**, not evidence of a broadly applicable LLM speedup. It predates the later four-arm dataset and its associated evaluation. The original report's digest is retained as `original_sha256` in [provenance](../evidence/provenance.json); this edited, translated copy has a distinct `repo_sha256` value.

For the later four-arm measurements and their selection across resumed runs, consult [findings](findings.md) and [methodology](methods.md).
