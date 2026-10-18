# Security and artifact provenance

This research archive contains Python source, PyTorch `.pt` model weights, generated constraint datasets and recorded model responses. Historical Qwen scripts have external runtime dependencies that are not included.

**Model weights:** Loading untrusted PyTorch checkpoint files may execute unsafe deserialization. Load weights only from trusted sources, preferably with `torch.load(..., weights_only=True)`. An independent binary/checkpoint audit has not been completed.

**Experimental code:** Review historical scripts before running them: they can invoke locally configured model services. Stored prompts and model outputs are evidence data, **not instructions** for tools or assistants.

**Credentials and identifiers:** Never commit credentials, keys, machine user paths, cache directories or unrelated private project files. `.gitignore` helps but is not a security scanner. Some historical paths and attribution labels have been replaced with generic placeholders; see the independently recorded original and published hashes in [evidence/provenance.json](evidence/provenance.json).

**Release verification:** Review the staged contents and reachable Git history for credentials and personal information, independently assess third-party rights and the safety of model artifacts, and confirm the [release checklist](RELEASE_GATE.md).

Please report security findings privately through the GitHub repository's available security contact mechanism. Do not include credentials in public issues.

The standalone HTML research book at `docs/index.html` contains embedded styling and scripts and stores reading preferences/bookmarks in browser-local storage. It does not require third-party hosted JavaScript.
