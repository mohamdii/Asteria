# Optional synthetic recovery experiment

Not submission data. Main results are generated from conservatively cleaned supplied records in `data/curated` and `analysis`.

- `curated/`: regenerate with `python scripts/clean_assessment.py --recover-synthetic` from the repository root. This command cannot overwrite main outputs.
- `previous_run/`: archived outputs from the earlier recovered-data pipeline, with its historical manifest. These are retained for comparison, not rebuilt by the main pipeline.
- Details and limitations: `docs/source-recovery.md` in the repository root.
