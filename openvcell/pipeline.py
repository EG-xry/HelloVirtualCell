"""End-to-end pipeline that runs all 4 stages and writes a Markdown report."""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from . import config as C
from .stage1_data import build_corpus
from .stage2_foundation import pretrain, embed_cells, load_model
from .stage3_perturb import train_perturb, predict_expression
from .stage4_mechanism import (
    build_toy_metabolism, predict_phenotype, pathway_consistency,
)
from .evaluate import per_gene_pearson, topk_deg_recall, cell_type_macro_f1, biomass_r2


METAB_PATH = C.ARTIFACTS / "metabolism.pkl"


def run() -> dict:
    print("=" * 60)
    print("OpenVCell-MVP — running 4-stage pipeline")
    print("=" * 60)

    # ---------- Stage 1 ----------
    print("\n[Stage 1] Build data corpus ...")
    adata = build_corpus(force=True)
    print(f"  AnnData: {adata.n_obs} cells × {adata.n_vars} genes")
    print(f"  QC: {adata.uns['qc']}")

    # ---------- Stage 2 ----------
    print("\n[Stage 2] Pretrain mini cell foundation model ...")
    fm, pretrain_losses = pretrain(adata)
    cell_embs = embed_cells(fm, adata.X)
    macro_f1 = cell_type_macro_f1(cell_embs, adata.obs["cell_type"].tolist())
    print(f"  Cell-type macro-F1 from embeddings: {macro_f1:.3f}")

    # PCA plot
    pca = PCA(n_components=2).fit_transform(cell_embs)
    fig, ax = plt.subplots(figsize=(5, 4))
    for ct in sorted(adata.obs["cell_type"].unique()):
        m = adata.obs["cell_type"].values == ct
        ax.scatter(pca[m, 0], pca[m, 1], s=6, alpha=0.6, label=ct)
    ax.legend(fontsize=7); ax.set_title("Cell embeddings (PCA, colored by cell type)")
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "embeddings_pca.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(pretrain_losses, marker="o"); ax.set_xlabel("epoch"); ax.set_ylabel("masked-CE loss")
    ax.set_title("Stage 2 pretraining"); fig.tight_layout()
    fig.savefig(C.FIG_DIR / "pretrain_loss.png", dpi=120); plt.close(fig)

    # ---------- Stage 3 ----------
    print("\n[Stage 3] Train perturbation predictor (CPA-lite) ...")
    pert_model, eval_data = train_perturb(adata, cell_embs)

    pred = eval_data["pred"]
    truth = eval_data["truth"]
    heldout = eval_data["heldout"]

    # control mean (from training data) for DEG recall
    ctrl_mask = adata.obs["perturbation"].values == "control"
    control_mean = adata.X[ctrl_mask].mean(axis=0)

    pearson = per_gene_pearson(pred, truth)
    deg_recall = topk_deg_recall(pred.mean(0), truth.mean(0), np.asarray(control_mean), k=20)
    print(f"  Heldout perturbation: {heldout}")
    print(f"  Per-gene Pearson  : {pearson:.3f}")
    print(f"  Top-20 DEG recall : {deg_recall:.3f}")

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(truth.mean(0), pred.mean(0), s=6, alpha=0.5)
    lim = [min(truth.mean(0).min(), pred.mean(0).min()),
           max(truth.mean(0).max(), pred.mean(0).max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlabel("Ground-truth mean expression")
    ax.set_ylabel("Predicted mean expression")
    ax.set_title(f"Stage 3 zero-shot ({heldout})\nPearson={pearson:.3f}, DEG-recall={deg_recall:.2f}")
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "perturb_scatter.png", dpi=120); plt.close(fig)

    # ---------- Stage 4 ----------
    print("\n[Stage 4] Mechanism coupling: expression → FBA biomass ...")
    metab = build_toy_metabolism(n_genes=adata.n_vars)
    with open(METAB_PATH, "wb") as f:
        pickle.dump(metab, f)

    # For each perturbation, take 50 cells, compute predicted vs truth biomass
    perts = list(C.PERTURBATIONS)
    pred_biomass, truth_biomass, pathway_scores = [], [], []
    for p_idx, p in enumerate(perts):
        sel = np.where(adata.obs["perturbation"].values == p)[0][:50]
        if len(sel) == 0:
            continue
        # truth biomass: from real expression
        for i in sel:
            tb = predict_phenotype(metab, np.asarray(adata.X[i]))["biomass"]
            truth_biomass.append(tb)
        # predicted biomass: feed cell embedding through perturb model
        c_embs_sel = cell_embs[sel]
        pred_expr = predict_expression(pert_model, c_embs_sel, p_idx)
        for j in range(pred_expr.shape[0]):
            pb = predict_phenotype(metab, pred_expr[j])["biomass"]
            pred_biomass.append(pb)
        # pathway consistency on Δ vs control
        delta = pred_expr.mean(0) - np.asarray(control_mean)
        pathway_scores.append(pathway_consistency(metab, delta))

    pred_biomass = np.array(pred_biomass)
    truth_biomass = np.array(truth_biomass)
    r2 = biomass_r2(pred_biomass, truth_biomass)
    avg_pw = float(np.mean(pathway_scores)) if pathway_scores else 0.0
    print(f"  Biomass R² (pred vs truth)     : {r2:.3f}")
    print(f"  Mean pathway co-direction score: {avg_pw:.3f}")

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(truth_biomass, pred_biomass, s=8, alpha=0.6)
    lim = [min(truth_biomass.min(), pred_biomass.min()),
           max(truth_biomass.max(), pred_biomass.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlabel("FBA biomass from true expression")
    ax.set_ylabel("FBA biomass from predicted expression")
    ax.set_title(f"Stage 4 metabolic coupling — R²={r2:.3f}")
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "biomass_scatter.png", dpi=120); plt.close(fig)

    # ---------- Report ----------
    metrics = {
        "qc": adata.uns["qc"],
        "stage2_macro_f1_celltype": macro_f1,
        "stage2_final_loss": float(pretrain_losses[-1]) if pretrain_losses else None,
        "stage3_heldout_perturbation": heldout,
        "stage3_per_gene_pearson": pearson,
        "stage3_top20_deg_recall": deg_recall,
        "stage4_biomass_r2": r2,
        "stage4_pathway_codirection": avg_pw,
    }
    with open(C.ARTIFACTS / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    report = f"""# OpenVCell-MVP — Run Report

## Data (Stage 1)
- cells: **{metrics['qc']['n_cells']}**, genes: **{metrics['qc']['n_genes']}**
- cell types: {metrics['qc']['n_cell_types']}, perturbations: {metrics['qc']['n_perturbations']}
- median counts/cell: {metrics['qc']['median_counts']:.1f}

## Foundation model (Stage 2)
- final masked-CE loss: **{metrics['stage2_final_loss']:.3f}**
- cell-type macro-F1 from embeddings: **{metrics['stage2_macro_f1_celltype']:.3f}**
- ![pca](figures/embeddings_pca.png)
- ![loss](figures/pretrain_loss.png)

## Perturbation prediction (Stage 3, leave-perturb-out)
- held-out perturbation: **{metrics['stage3_heldout_perturbation']}**
- per-gene Pearson  : **{metrics['stage3_per_gene_pearson']:.3f}**
- Top-20 DEG recall : **{metrics['stage3_top20_deg_recall']:.3f}**
- ![scatter](figures/perturb_scatter.png)

## Mechanism coupling (Stage 4)
- biomass R² (pred vs truth): **{metrics['stage4_biomass_r2']:.3f}**
- pathway co-direction score: **{metrics['stage4_pathway_codirection']:.3f}**
- ![biomass](figures/biomass_scatter.png)

---
Run `streamlit run openvcell/app.py` to launch the interactive demo.
"""
    C.REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\n✅ All done. Report → {C.REPORT_PATH}")
    print(f"   Figures → {C.FIG_DIR}")
    return metrics


if __name__ == "__main__":
    run()
