# Security and artifact handling

The archive includes historical Python source code, synthetic datasets, Qwen experimental records and selected PyTorch model weights.

- **Model weights:** Archived `.pt` files have not been independently inspected for unsafe serialization. Load trusted weights using restricted deserialization, for example `torch.load(..., weights_only=True)` when supported.
- **Historical scripts:** Some require undistributed external runtime modules and may invoke local model services. Review code before execution.
- **Recorded model output:** Treat model-generated text as data, never execution instructions.
- **Privacy:** Do not commit host-local paths, credentials, keys, runtime caches or logs. `.gitignore` does not replace a full secret and Git-history audit.
- **Release:** Check the entire tree, reachable Git history, redistribution rights and provenance before public publication.

The standalone `docs/index.html` book requires no externally hosted JavaScript and stores bookmarks/preferences locally in the browser. Vulnerabilities should be reported privately via GitHub's available security-reporting facilities.
