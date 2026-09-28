# Code structure and commands

The supported offline entry point remains `python scripts/run_pipeline.py`. Add `--verify-reproducibility` to build twice and compare output hashes. Run it from the repository root, or use the absolute script path from another directory. No editable installation is required; retain the `asteria` package alongside `scripts` when copying the project.

## Package responsibilities

- `asteria/pipeline.py`: orchestrates offline stages, verifies evidence, runs tests and writes the success manifest. Cleaning runs once, before all three metric calculations.
- `asteria/quality/`: raw schema validation and conservative curation. Raw source files remain unchanged.
- `asteria/metrics/`: six-month retention, senior twelve-month retention and regretted turnover. These modules consume curated data; they no longer clean as a side effect.
- `asteria/external/`: HTML/PDF parsing, canonical historical features, publication-aware selection, coverage reporting and metric joins. These modules process saved evidence offline.
- `asteria/reporting/`: SQL reconciliation, descriptive associations and HTML dashboard generation.
- `asteria/acquisition/`: HTTP handling and explicit online commands for current coverage probes, initial evidence, expanded historical evidence and PDFs. The normal pipeline does not invoke these commands.
- `asteria/common.py` and `asteria/paths.py`: shared calendar/CSV helpers and the repository root. Processing no longer imports utilities from demo or acquisition scripts.

The old `build_historical_join_demo.py` is retired. Its reusable table parser is now in `asteria/external/html.py`. Older demo outputs are historical artifacts, not current pipeline outputs. The separate initial-evidence downloader remains available because expanded acquisition uses the saved WDI archive-version list it obtains.

Refactor verification on 2026-09-28: the full test suite and dashboard checks passed. All 34 generated output hashes matched both the pre-refactor baseline and a repeated build. The pipeline manifest changed to record the new code paths; analytical results and dashboard bytes did not change. Online acquisition was not executed as part of this verification.

## Typical commands

Full offline build:

```powershell
python scripts/run_pipeline.py --verify-reproducibility
```

Tests and dashboard checks:

```powershell
python -m unittest discover -s tests
node dashboard/check.cjs
```

Explicit online acquisition, only when intentionally updating the saved evidence:

```powershell
python -m asteria.acquisition.coverage_probe
python -m asteria.acquisition.initial_evidence
python -m asteria.acquisition.historical
python -m asteria.acquisition.pdfs
```

Individual offline modules can be run with `python -m asteria.<group>.<module>` from the repository root. They require their upstream outputs; prefer the full pipeline for normal use. In particular, running a metric module alone does not refresh curation. Acquisition changes inputs and may change results; it is not part of repeatable offline replay.

## What remains outside the package

`dashboard/` contains the HTML/CSS/JavaScript template and UI checks; `sql/` contains the reporting schema/views; `tests/` verifies domain and extraction behavior; `config/` stores static contracts and references; `data/` stores source and curated evidence; `analysis/` contains generated outputs; `docs/` explains the decisions. The project is a local data pipeline with an HTML interface, not a deployed cloud service.
