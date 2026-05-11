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
    """Optional: load a small CELLxGENE Census slice (requires extra deps + internet).

    Caches the raw download to data/raw_census.h5ad so subsequent runs are offline.
    """
    data_dir = C.ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    cache_path = data_dir / "raw_census.h5ad"

    if cache_path.exists():
        print(f"[stage1] loading real data from cache: {cache_path}")
        return ad.read_h5ad(cache_path)

    try:
        import cellxgene_census  # type: ignore
    except Exception:
        return None
    try:
        print("[stage1] downloading CELLxGENE Census slice (blood T cells, n=5000)…")
        with cellxgene_census.open_soma(census_version="2024-07-01") as census:
            # First collect joinids matching the filter, then take at most 5000
            obs_df = (
                census["census_data"]["homo_sapiens"]["obs"]
                .read(
                    value_filter='tissue_general=="blood" and cell_type=="T cell"',
                    column_names=["soma_joinid"],
                )
                .concat()
                .to_pandas()
            )
            joinids = obs_df["soma_joinid"].values[:5000].tolist()
            adata = cellxgene_census.get_anndata(
                census,
                organism="Homo sapiens",
                obs_coords=joinids,
            )
        # Normalize: log1p CPM (same as synthetic pipeline)
        X = np.array(adata.X) if isinstance(adata.X, np.ndarray) else np.asarray(adata.X.todense() if hasattr(adata.X, "todense") else adata.X)  # type: ignore[union-attr]
        libsize = X.sum(1, keepdims=True) + 1e-8
        X_norm = np.log1p(X / libsize * 1e4).astype(np.float32)

        # HVG selection: keep top N_GENES most variable genes
        gene_var = X_norm.var(axis=0)
        hvg_idx = np.argsort(-gene_var)[: C.N_GENES]
        adata = adata[:, hvg_idx].copy()
        adata.X = X_norm[:, hvg_idx]
        adata.obs["n_counts"] = X[:, hvg_idx].sum(1)

        # Assign synthetic perturbation labels (demo only — no real perturbation data)
        rng = np.random.default_rng(C.SEED)
        adata.obs["perturbation"] = rng.choice(list(C.PERTURBATIONS), size=adata.n_obs)
        adata.obs["cell_type"] = adata.obs.get("cell_type", "T cell")

        adata.write_h5ad(cache_path)
        print(f"[stage1] cached to {cache_path} ({adata.n_obs} cells × {adata.n_vars} genes)")
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
