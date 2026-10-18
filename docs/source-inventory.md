# Source inventory and archival provenance

- Source package identifier: `METIS_.zip`.
- Original archive SHA-256: `7e3ffc0b82604023d417f0880deee05984fb0e5cfc211266dad498abe2c785e7`.
- Archive inspected: **1,735** ZIP entries, many of them caches or runtime artifacts.
- Curated items retained: **47**, including seven selected P2 checkpoint files and all seven P2 dataset splits.
- Excluded: machine identity keys, system caches, model process logs, surplus interim checkpoints and machine-local run directories.
- Not bundled: prior P1 sources/checkpoints and a separate historical runtime required by some archived Qwen scripts.

The original `original_sha256` values and the current repository's `repo_sha256` values are listed separately in [evidence/provenance.json](../evidence/provenance.json). The dataset manifest retains the **original** source-generator hash, even where attribution strings in the published generator are privacy-redacted. Such changes are not misrepresented as identical original bytes.
