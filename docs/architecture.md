# Model architecture — MÉTIS P2

The archived `research/p2/model.py` implements the experimental P2 model, **not a general-language model**. The default `Net()` configuration has **679,571 trainable parameters**, counted from the implementation without loading checkpoints.

## Design

- **Model:** compact Transformer encoder for symbolic constraints and variables.
- **Dimensions:** width `128`, four encoder layers, four attention heads, feed-forward width `256`, dropout `0.0`.
- **Representation:** one class token, up to 24 constraint tokens, and up to 12 variable tokens; domains and constraints are represented structurally.
- **P2-specific change:** each constraint slot jointly encodes variable ID, coefficient/sign and slot position through a small MLP (`bind`), then accumulates them. This targets ambiguous coefficient–variable binding observed in P1.
- **Output:** per-variable logits over 16 values (`0..15`), with domain masking; two auxiliary heads (`head_p`, `head_q`) for self-assessment and strategy selection, trained in stage C.
- **Feedback modes:** fresh candidate, repair with prior candidate and verifier flags, or a prior candidate without flags. A deterministic verifier operates outside the neural network.

## Scope

The model takes structured problem objects, **not free-form natural language**. The P2 slot-binding change is an implementation-level improvement, not evidence of general reasoning ability. The historical training and evaluation details are in the accompanying source and recorded results. The four-arm Qwen experiment used `models/p2/seed0/C/best.pt`.
