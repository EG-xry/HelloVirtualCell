# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make setup        # Create .venv and install dependencies (~2 min)
make all          # Run full 4-stage pipeline (~1–3 min on CPU)
make test         # Run pytest smoke test
make app          # Launch Streamlit interactive demo
make clean        # Remove artifacts/, __pycache__, .pytest_cache
```

Run a single test file directly:
```bash
.venv/bin/pytest -q tests/test_pipeline.py
```

Run the pipeline as a module:
```bash
.venv/bin/python -m openvcell.pipeline
```

No linter is configured. Dependencies are CPU-only; no GPU required.

## Architecture

This is a 4-stage research pipeline MVP for virtual cell modeling. Each stage is an independent module in `openvcell/`; `pipeline.py` orchestrates them in sequence.

### Stage flow

```
stage1_data.py      → vc_corpus.h5ad      (AnnData: 2000 cells × 200 genes)
stage2_foundation.py → foundation.pt      (Transformer cell embeddings, 64-dim)
stage3_perturb.py   → perturb.pt          (CPA-lite perturbation predictor)
stage4_mechanism.py → metabolism.pkl      (Toy FBA metabolic model)
                    → artifacts/metrics.json + report.md
```

All generated files land in `artifacts/`. The app (`app.py`) loads all three model files and the AnnData corpus via `@st.cache_resource`.

### Key design decisions

- **`config.py` is the single source of truth** for all hyperparameters (cell counts, gene counts, embedding dims, training epochs, paths). Change here to scale up or down.
- **Synthetic data by default** (`USE_REAL_DATA=False`). Set `USE_REAL_DATA=True` to pull from CELLxGENE Census (requires internet and `cellxgene-census` package).
- **Every stage has a `# TODO: replace with <real tool>` comment** marking the path to production tools (scGPT, GEARS, cobrapy, tellurium).
- **Stage 2** uses masked-expression pretraining: cells are tokenized as (gene_id, expression_bin) pairs, a [CLS] token produces the 64-dim cell embedding.
- **Stage 3 (CPA-lite)** uses two MLPs — a basal decoder and a perturbation-effect head — evaluated via leave-one-perturbation-out (heldout perturbation: `"drug_X"`).
- **Stage 4** maps expression → enzyme abundance → FBA flux bounds → `scipy.optimize.linprog` maximizing biomass. Pathway consistency is scored as co-directionality of Δexpression within 3 KEGG-like pathways.

### Test approach

`tests/test_pipeline.py` contains a single smoke test (`test_pipeline_smoke`) that overrides config to tiny values (N_CELLS=300, N_GENES=80, 1–2 epochs) and verifies the metrics dict, QC metadata, and output files are produced. `tests/conftest.py` handles pytest setup.
