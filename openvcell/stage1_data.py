"""Stage 1 — Data foundation.

MVP: synthesize an AnnData corpus that mimics scRNA-seq with multiple cell
types and perturbations. Real research replaces this with cellxgene-census
+ scPerturb harmonization.

# TODO: replace with cellxgene-census + scvi-tools harmonization pipeline
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import anndata as ad

from . import config as C


def _make_synthetic_corpus(seed: int = C.SEED) -> ad.AnnData:
    rng = np.random.default_rng(seed)
    n_cells, n_genes = C.N_CELLS, C.N_GENES
    n_types = C.N_CELL_TYPES
    perts = C.PERTURBATIONS

    # 1. Cell-type signature: each type has its own expression "program"
    type_programs = rng.normal(0, 1.0, size=(n_types, n_genes))
    # Make a few "marker" genes per type strongly positive
    for t in range(n_types):
        marker_idx = rng.choice(n_genes, size=10, replace=False)
        type_programs[t, marker_idx] += 4.0

    # 2. Perturbation effects: each perturbation shifts a small set of genes
    pert_effects = {p: np.zeros(n_genes) for p in perts}
    for p in perts:
        if p == "control":
            continue
        idx = rng.choice(n_genes, size=15, replace=False)
        pert_effects[p][idx] = rng.normal(2.0, 0.5, size=15) * rng.choice([-1, 1], size=15)

    # 3. Assemble cells
    cell_types = rng.integers(0, n_types, size=n_cells)
    cell_perts = rng.choice(perts, size=n_cells)
    base = type_programs[cell_types]                                # (n_cells, n_genes)
    perturb = np.stack([pert_effects[p] for p in cell_perts])       # (n_cells, n_genes)
    noise = rng.normal(0, 0.5, size=(n_cells, n_genes))
    log_expr = base + perturb + noise                               # log-space
    counts = np.maximum(0, np.round(np.expm1(np.clip(log_expr, 0, 8)))).astype(np.float32)

    var = pd.DataFrame(
        {"gene_symbol": [f"G{i:04d}" for i in range(n_genes)]},
        index=[f"G{i:04d}" for i in range(n_genes)],
    )
    obs = pd.DataFrame(
        {
            "cell_type": [f"CT{t}" for t in cell_types],
            "perturbation": cell_perts,
            "n_counts": counts.sum(1),
        },
        index=[f"cell_{i}" for i in range(n_cells)],
    )

    adata = ad.AnnData(X=counts, obs=obs, var=var)
    adata.layers["counts"] = counts.copy()
    # 4. Simple log-normalize (instead of scanpy to keep deps minimal)
    libsize = counts.sum(1, keepdims=True) + 1e-8
    adata.X = np.log1p(counts / libsize * 1e4).astype(np.float32)

    # 5. Persist ground-truth perturbation effects (for evaluation)
    adata.uns["pert_effects"] = {k: v.astype(np.float32) for k, v in pert_effects.items()}
    adata.uns["type_programs"] = type_programs.astype(np.float32)
    return adata


def _try_load_real() -> ad.AnnData | None:
    """Optional: load a small CELLxGENE Census slice (requires extra deps + internet)."""
    try:
        import cellxgene_census  # type: ignore
    except Exception:
        return None
    try:
        with cellxgene_census.open_soma(census_version="stable") as census:
            adata = cellxgene_census.get_anndata(
                census,
                organism="Homo sapiens",
                obs_value_filter='tissue_general=="blood" and cell_type=="T cell"',
                var_value_filter=None,
                obs_coords=slice(0, 5000),
            )
        # No real perturbation labels here → annotate as control
        adata.obs["perturbation"] = "control"
        adata.obs["cell_type"] = adata.obs.get("cell_type", "T cell")
        return adata
    except Exception as e:  # pragma: no cover
        print(f"[stage1] real data load failed: {e}; falling back to synthetic.")
        return None


def build_corpus(force: bool = False) -> ad.AnnData:
    """Build (or load cached) AnnData corpus and write to disk."""
    if C.DATA_PATH.exists() and not force:
        return ad.read_h5ad(C.DATA_PATH)

    adata = None
    if C.USE_REAL_DATA:
        adata = _try_load_real()
    if adata is None:
        adata = _make_synthetic_corpus()

    # QC summary
    adata.uns["qc"] = {
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "median_counts": float(np.median(adata.obs["n_counts"])) if "n_counts" in adata.obs else 0.0,
        "n_cell_types": int(adata.obs["cell_type"].nunique()),
        "n_perturbations": int(adata.obs["perturbation"].nunique()),
    }
    adata.write_h5ad(C.DATA_PATH)
    return adata


if __name__ == "__main__":  # pragma: no cover
    a = build_corpus(force=True)
    print(a)
    print(a.uns["qc"])
