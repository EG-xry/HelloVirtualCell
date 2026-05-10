"""Streamlit interactive Virtual Cell demo.

Pick a cell type and a perturbation → predict expression, biomass flux, and
top differentially expressed genes. Run with:

    streamlit run openvcell/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `streamlit run openvcell/app.py` (no package context) to find the package.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import anndata as ad

from openvcell import config as C
from openvcell.stage1_data import build_corpus
from openvcell.stage2_foundation import load_model, embed_cells
from openvcell.stage3_perturb import load_perturb_model, predict_expression
from openvcell.stage4_mechanism import (
    build_toy_metabolism, predict_phenotype, pathway_consistency,
)


@st.cache_resource
def load_all():
    if not C.DATA_PATH.exists() or not C.MODEL_PATH.exists() or not C.PERTURB_MODEL_PATH.exists():
        st.error("⚠️ Pipeline artifacts not found. Please run `python -m openvcell.pipeline` first.")
        st.stop()
    adata = ad.read_h5ad(C.DATA_PATH)
    fm = load_model()
    pert_model, pert_ckpt = load_perturb_model()
    embs = embed_cells(fm, adata.X)
    metab_path = C.ARTIFACTS / "metabolism.pkl"
    if metab_path.exists():
        with open(metab_path, "rb") as f:
            metab = pickle.load(f)
    else:
        metab = build_toy_metabolism(adata.n_vars)
    return adata, fm, pert_model, pert_ckpt, embs, metab


def main():
    st.set_page_config(page_title="OpenVCell-MVP", page_icon="🧬", layout="wide")
    st.title("🧬 OpenVCell-MVP — Interactive Virtual Cell Demo")
    st.caption("Pick a cell type & perturbation → predict expression, metabolic flux, and key DEGs.")

    adata, fm, pert_model, pert_ckpt, embs, metab = load_all()
    perts = pert_ckpt["perts"]

    col1, col2 = st.columns(2)
    with col1:
        cell_type = st.selectbox("Cell type", sorted(adata.obs["cell_type"].unique()))
    with col2:
        pert = st.selectbox("Perturbation", perts)

    # Sample cells from the chosen cell type (under control as basal state)
    mask = (adata.obs["cell_type"].values == cell_type) & (adata.obs["perturbation"].values == "control")
    if mask.sum() == 0:
        mask = adata.obs["cell_type"].values == cell_type
    idx = np.where(mask)[0][:50]
    if len(idx) == 0:
        st.warning("No cells available for this combination."); st.stop()

    cell_emb = embs[idx]
    pred_expr = predict_expression(pert_model, cell_emb, perts.index(pert))
    pred_mean = pred_expr.mean(0)

    # Compare to control mean
    ctrl_idx = np.where(adata.obs["perturbation"].values == "control")[0]
    control_mean = np.asarray(adata.X[ctrl_idx]).mean(0)
    delta = pred_mean - control_mean

    # ----- panel: metabolic flux -----
    flux = predict_phenotype(metab, pred_mean)
    pw = pathway_consistency(metab, delta)

    st.subheader("📊 Predicted phenotype")
    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted biomass flux", f"{flux['biomass']:.3f}")
    c2.metric("Pathway co-direction", f"{pw:.3f}")
    c3.metric("# cells used", f"{len(idx)}")

    # ----- panel: top DEGs -----
    st.subheader("🔬 Top up/down regulated genes (pred vs control)")
    gene_names = adata.var_names.to_numpy()
    order = np.argsort(-np.abs(delta))[:20]
    df = pd.DataFrame({
        "gene": gene_names[order],
        "control_mean": control_mean[order].round(3),
        "predicted_mean": pred_mean[order].round(3),
        "delta": delta[order].round(3),
    })
    st.dataframe(df, use_container_width=True)

    # ----- panel: flux barplot -----
    st.subheader("⚙️ Per-reaction flux (toy FBA)")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.bar(np.arange(metab.n_reactions), flux["fluxes"])
    ax.set_xlabel("reaction id"); ax.set_ylabel("flux")
    ax.set_title("FBA-predicted reaction fluxes")
    st.pyplot(fig)

    # ----- panel: delta histogram -----
    st.subheader("📈 Δ Expression histogram")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.hist(delta, bins=40, color="steelblue", edgecolor="white")
    ax.set_xlabel("predicted - control"); ax.set_ylabel("# genes")
    st.pyplot(fig)

    with st.expander("ℹ️ How this maps to the research plan"):
        st.markdown("""
        - **Stage 1** — `stage1_data.py` : build / load AnnData corpus
        - **Stage 2** — `stage2_foundation.py` : mini-Transformer cell embedding
        - **Stage 3** — `stage3_perturb.py` : CPA-lite for ΔExpression
        - **Stage 4** — `stage4_mechanism.py` : toy FBA + pathway prior

        Each module has `# TODO: replace with <real tool>` markers showing how to
        upgrade to scGPT / GEARS / cobrapy / Human-GEM in real research.
        """)


if __name__ == "__main__":
    main()
