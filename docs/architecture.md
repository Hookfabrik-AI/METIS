# MÉTIS P2 — Model architecture

The archived `research/p2/model.py` defines a small Transformer encoder for **formalized constraint problems**, not unrestricted natural language. The default P2 `Net()` has **679,571 trainable parameters**.

| Property | P2 configuration |
|---|---|
| Encoder layers / attention heads | 4 / 4 |
| Model width / feed-forward width | 128 / 256 |
| Dropout | 0.0 |
| Structured input | One class token, up to 24 constraint tokens, up to 12 variable tokens |
| Output | Domain-masked logits over 16 values per variable and two auxiliary heads |

P2 combines variable identity, coefficient/sign and constraint-slot position through a small MLP before aggregating slot representations. The two auxiliary heads support self-assessment and strategy selection; a separate constraint verifier checks validity.

P2 was developed to address an observed representational ambiguity in P1. The architecture itself is **not** proof of general reasoning ability. See [methods](methods.md) and [limitations](limitations.md).
