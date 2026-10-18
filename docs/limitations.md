# Limitations

1. Historic training and Qwen runs were not independently rerun; the available reproducibility checks validate archive integrity and saved-result aggregation.
2. Only 12 structured tasks were used in the Qwen snapshot, assembled across runs 03–05, with an explicitly documented repeated task.
3. Historic Qwen runners depend on external, unavailable modules; privacy-redacted local paths are deliberately not executable.
4. The Qwen `latest` model tag is not a fixed digest, and hardware/cache/model-loading overhead was not comprehensively controlled.
5. The archived P2 evaluation requires missing P1 sources and checkpoints for complete C5/C6 reproduction.
6. Seven selected PyTorch `.pt` checkpoints have not been independently safety-audited; only load files from trusted sources with safe deserialization.
7. Formalized constraints were provided to the models; unrestricted natural-language reasoning, new domains and larger models were not evaluated.
8. Incorrect high-confidence hints can anchor subsequent reasoning and lower accuracy.
9. Rights to datasets, model weights and externally sourced archival material must be reviewed separately; see [LICENSING.md](../LICENSING.md).
10. P3 is only a project report here: no raw evaluations, checkpoints, source snapshot or independent verification are available.

These limits should be cited with any performance discussion.
