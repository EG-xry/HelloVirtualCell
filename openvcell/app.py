"""Streamlit interactive Virtual Cell demo — 4-stage pipeline visualization.

Run with:
    streamlit run openvcell/app.py
"""
from __future__ import annotations

import sys
import json
import pickle
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.decomposition import PCA
import streamlit as st
import anndata as ad
import torch
import torch.nn as nn

from openvcell import config as C
from openvcell.stage2_foundation import load_model, embed_cells, tokenize_cell, EXPR_BINS
from openvcell.stage3_perturb import load_perturb_model, predict_expression
from openvcell.stage4_mechanism import (
    build_toy_metabolism, predict_phenotype, pathway_consistency,
    expression_to_flux_bounds, fba,
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _fig(w=7, h=4):
    return plt.subplots(figsize=(w, h))


def _show(fig):
    st.pyplot(fig)
    plt.close(fig)


@st.cache_resource
def load_all():
    missing = [p for p in (C.DATA_PATH, C.MODEL_PATH, C.PERTURB_MODEL_PATH) if not p.exists()]
    if missing:
        st.error(f"Artifacts not found: {missing}\n\nRun `python -m openvcell.pipeline` first.")
        st.stop()
    adata = ad.read_h5ad(C.DATA_PATH)
    fm = load_model()
    pert_model, pert_ckpt = load_perturb_model()
    embs = embed_cells(fm, adata.X)
    metab_path = C.ARTIFACTS / "metabolism.pkl"
    metab = pickle.load(open(metab_path, "rb")) if metab_path.exists() else build_toy_metabolism(adata.n_vars)
    metrics = json.loads((C.ARTIFACTS / "metrics.json").read_text()) if (C.ARTIFACTS / "metrics.json").exists() else {}
    return adata, fm, pert_model, pert_ckpt, embs, metab, metrics


# ──────────────────────────────────────────────
# Stage 1 — Data
# ──────────────────────────────────────────────

def show_stage1(adata: ad.AnnData, metrics: dict):
    st.header("Stage 1 — Data Corpus")
    qc = metrics.get("qc", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cells", f"{adata.n_obs:,}")
    c2.metric("Genes (HVG)", f"{adata.n_vars:,}")
    c3.metric("Cell types", str(qc.get("n_cell_types", adata.obs["cell_type"].nunique())))
    c4.metric("Perturbations", str(qc.get("n_perturbations", adata.obs["perturbation"].nunique())))

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Perturbation distribution")
        vc = adata.obs["perturbation"].value_counts()
        fig, ax = _fig(5, 3)
        ax.barh(vc.index.tolist(), vc.values, color="steelblue")
        ax.set_xlabel("# cells"); ax.set_title("Cells per perturbation")
        _show(fig)

    with col_b:
        st.subheader("Cell type distribution")
        vc2 = adata.obs["cell_type"].value_counts()
        fig, ax = _fig(5, 3)
        ax.barh(vc2.index.tolist(), vc2.values, color="darkorange")
        ax.set_xlabel("# cells"); ax.set_title("Cells per cell type")
        _show(fig)

    st.subheader("Gene expression distribution (log-normalized)")
    X = adata.X if isinstance(adata.X, np.ndarray) else np.array(adata.X)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
    axes[0].hist(X.mean(0), bins=50, color="mediumseagreen", edgecolor="white")
    axes[0].set_xlabel("mean log-expr per gene"); axes[0].set_ylabel("# genes")
    axes[0].set_title("Per-gene mean expression")
    axes[1].hist(X.sum(1), bins=50, color="slateblue", edgecolor="white")
    axes[1].set_xlabel("total log-expr per cell"); axes[1].set_ylabel("# cells")
    axes[1].set_title("Per-cell total expression")
    fig.tight_layout(); _show(fig)

    st.subheader("Top 20 most variable genes")
    gene_var = X.var(0)
    top_idx = np.argsort(-gene_var)[:20]
    st.dataframe(pd.DataFrame({
        "gene": adata.var_names[top_idx],
        "variance": gene_var[top_idx].round(4),
        "mean": X.mean(0)[top_idx].round(4),
    }), use_container_width=True)


# ──────────────────────────────────────────────
# Stage 2 — Foundation model + process
# ──────────────────────────────────────────────

def _extract_attentions(fm, gene_ids: torch.Tensor, expr_bins: torch.Tensor):
    """Return list of attention weight tensors from each TransformerEncoderLayer."""
    attn_weights = []

    def make_hook(layer_idx):
        original_self_attn = fm.encoder.layers[layer_idx].self_attn

        def hook(module, inp, out):
            # out is (attn_output, attn_weights) when need_weights=True
            pass

        return hook

    # Re-run forward with need_weights via manual layer iteration
    with torch.no_grad():
        b = gene_ids.unsqueeze(0)
        e = expr_bins.unsqueeze(0)
        h = fm.gene_emb(b) + fm.expr_emb(e)
        cls = fm.cls_token.expand(1, -1, -1)
        h = torch.cat([cls, h], dim=1)  # (1, L+1, D)

        for layer in fm.encoder.layers:
            # self_attn returns (output, attn_weight) when average_attn_weights=False
            attn_out, w = layer.self_attn(h, h, h, need_weights=True, average_heads=False)
            attn_weights.append(w.squeeze(0).detach().numpy())  # (n_heads, L+1, L+1)
            # continue through rest of layer manually
            h2 = layer.norm1(h + layer.dropout1(attn_out))
            h3 = layer.norm2(h2 + layer.dropout2(layer.linear2(layer.dropout(layer.activation(layer.linear1(h2))))))
            h = h3
    return attn_weights  # list of (n_heads, L+1, L+1)


def show_stage2(adata: ad.AnnData, fm, embs: np.ndarray, metrics: dict):
    st.header("Stage 2 — Cell Foundation Model (mini-Transformer)")

    c1, c2, c3 = st.columns(3)
    c1.metric("Embedding dim", str(C.EMB_DIM))
    c2.metric("Transformer layers", str(C.N_LAYERS))
    c3.metric("Cell-type macro-F1", f"{metrics.get('stage2_macro_f1_celltype', 0):.3f}")

    # ── Overview plots ──
    col_a, col_b = st.columns(2)
    with col_a:
        loss_png = C.FIG_DIR / "pretrain_loss.png"
        if loss_png.exists():
            st.subheader("Pretraining loss curve")
            st.image(str(loss_png))
    with col_b:
        st.subheader("Cell embeddings PCA (by perturbation)")
        pca2 = PCA(n_components=2).fit_transform(embs)
        palette = plt.cm.tab10.colors
        perts_obs = adata.obs["perturbation"].tolist()
        unique_p = sorted(set(perts_obs))
        fig, ax = _fig(5, 4)
        for i, p in enumerate(unique_p):
            m = np.array(perts_obs) == p
            ax.scatter(pca2[m, 0], pca2[m, 1], s=5, alpha=0.4, label=p, color=palette[i % 10])
        ax.legend(fontsize=7, markerscale=2, ncol=2)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        fig.tight_layout(); _show(fig)

    # ── Tokenization process ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 1: Cell Tokenization")
    st.markdown(
        "Transformer 输入不是原始表达量，而是把每个细胞编码成 **Top-K (gene\_id, expr\_bin)** token 序列。"
        "下面选一个真实细胞，展示完整 tokenization 过程。"
    )

    X = adata.X if isinstance(adata.X, np.ndarray) else np.array(adata.X)
    cell_idx = st.slider("选择细胞 index", 0, adata.n_obs - 1, 0, key="s2_cell")
    expr_row = X[cell_idx]
    gene_ids, expr_bins = tokenize_cell(expr_row, C.MAX_GENES_PER_CELL)
    gene_names = adata.var_names.to_numpy()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Top-{C.MAX_GENES_PER_CELL} expressed genes → token 表**")
        df_tok = pd.DataFrame({
            "rank": np.arange(1, len(gene_ids) + 1),
            "gene_id": gene_ids,
            "gene_name": gene_names[gene_ids],
            "raw_expr": expr_row[gene_ids].round(4),
            "expr_bin (0-7)": expr_bins,
        })
        st.dataframe(df_tok, use_container_width=True, height=260)

    with col2:
        st.markdown("**expr_bin 分布（离散化后的表达等级）**")
        fig, ax = _fig(4, 3)
        ax.bar(np.arange(EXPR_BINS), np.bincount(expr_bins, minlength=EXPR_BINS), color="steelblue")
        ax.set_xlabel("expr bin (0=low, 7=high)"); ax.set_ylabel("# tokens")
        ax.set_title("Token expr-bin distribution"); fig.tight_layout(); _show(fig)

    # Expression rank visualization
    st.markdown("**细胞基因表达 rank 曲线（选中细胞）**")
    sorted_expr = np.sort(expr_row)[::-1]
    fig, ax = _fig(9, 2.5)
    ax.plot(sorted_expr, color="steelblue", linewidth=0.8)
    ax.axvline(C.MAX_GENES_PER_CELL, color="tomato", linestyle="--", linewidth=1, label=f"Top-{C.MAX_GENES_PER_CELL} cutoff")
    ax.fill_between(np.arange(C.MAX_GENES_PER_CELL), sorted_expr[:C.MAX_GENES_PER_CELL], alpha=0.2, color="tomato")
    ax.set_xlabel("gene rank"); ax.set_ylabel("log-expr"); ax.set_title("Gene expression rank curve")
    ax.legend(fontsize=8); fig.tight_layout(); _show(fig)

    # ── Transformer forward ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 2: Transformer 编码 & Attention")
    st.markdown(
        "每个 token = gene\_emb + expr\_emb，前置 `[CLS]` token，经过 "
        f"**{C.N_LAYERS} 层 Transformer Encoder**，取 CLS 位输出作为 64-dim 细胞嵌入。"
    )

    g_tensor = torch.as_tensor(gene_ids, dtype=torch.long)
    e_tensor = torch.as_tensor(expr_bins, dtype=torch.long)

    try:
        attn_list = _extract_attentions(fm, g_tensor, e_tensor)
        for layer_i, attn in enumerate(attn_list):
            st.markdown(f"**Layer {layer_i + 1} — attention weights** (头平均，CLS 行 = CLS 对各 token 的注意力)")
            avg_attn = attn.mean(0)  # (L+1, L+1)
            cls_attn = avg_attn[0, 1:]  # CLS 对 gene tokens 的注意力

            col_attn1, col_attn2 = st.columns([2, 1])
            with col_attn1:
                fig, ax = _fig(9, 2.5)
                im = ax.imshow(avg_attn[:16, :16], cmap="Blues", aspect="auto")
                ax.set_title(f"Layer {layer_i + 1} attention map (first 16 tokens, incl. CLS)")
                ax.set_xlabel("key token"); ax.set_ylabel("query token")
                ticks = ["CLS"] + [f"G{gene_ids[j]}" for j in range(min(15, len(gene_ids)))]
                ax.set_xticks(range(len(ticks))); ax.set_xticklabels(ticks, rotation=45, ha="right", fontsize=7)
                ax.set_yticks(range(len(ticks))); ax.set_yticklabels(ticks, fontsize=7)
                fig.colorbar(im, ax=ax); fig.tight_layout(); _show(fig)

            with col_attn2:
                top_attended = np.argsort(-cls_attn)[:10]
                fig, ax = _fig(3.5, 2.5)
                ax.barh(
                    [gene_names[gene_ids[j]] for j in top_attended][::-1],
                    cls_attn[top_attended][::-1],
                    color="steelblue"
                )
                ax.set_xlabel("attention weight"); ax.set_title("Top genes attended by CLS")
                fig.tight_layout(); _show(fig)
    except Exception as ex:
        st.warning(f"Attention 提取跳过: {ex}")

    # ── Embedding space ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 3: 嵌入空间分析")
    st.markdown("64-dim 嵌入经 PCA 降维，观察扰动间是否有几何分离。")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        # Variance explained
        pca_full = PCA(n_components=min(20, embs.shape[1])).fit(embs)
        fig, ax = _fig(5, 3)
        ax.bar(np.arange(1, len(pca_full.explained_variance_ratio_) + 1),
               np.cumsum(pca_full.explained_variance_ratio_), color="mediumseagreen")
        ax.axhline(0.9, color="tomato", linestyle="--", linewidth=1, label="90%")
        ax.set_xlabel("# PCs"); ax.set_ylabel("cumulative variance explained")
        ax.set_title("Embedding PCA variance"); ax.legend(fontsize=8)
        fig.tight_layout(); _show(fig)

    with col_e2:
        # Per-perturbation embedding distance from control
        pert_arr = np.array(adata.obs["perturbation"].tolist())
        ctrl_center = embs[pert_arr == "control"].mean(0)
        dists = {}
        for p in sorted(set(pert_arr)):
            if p == "control":
                continue
            center = embs[pert_arr == p].mean(0)
            dists[p] = float(np.linalg.norm(center - ctrl_center))
        fig, ax = _fig(5, 3)
        ax.bar(list(dists.keys()), list(dists.values()), color="coral")
        ax.set_ylabel("L2 distance from control centroid")
        ax.set_title("Embedding distance from control per perturbation")
        plt.xticks(rotation=15, ha="right"); fig.tight_layout(); _show(fig)

    # Perturbation cosine similarity matrix
    unique_p2 = sorted(set(pert_arr))
    mean_embs = {p: embs[pert_arr == p].mean(0) for p in unique_p2}
    mat = np.array([[
        float(np.dot(mean_embs[a], mean_embs[b]) /
              (np.linalg.norm(mean_embs[a]) * np.linalg.norm(mean_embs[b]) + 1e-8))
        for b in unique_p2] for a in unique_p2])
    fig, ax = _fig(5, 4)
    im = ax.imshow(mat, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(unique_p2))); ax.set_xticklabels(unique_p2, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(unique_p2))); ax.set_yticklabels(unique_p2, fontsize=8)
    fig.colorbar(im, ax=ax, label="cosine sim")
    ax.set_title("Perturbation mean-embedding cosine similarity"); fig.tight_layout(); _show(fig)


# ──────────────────────────────────────────────
# Stage 3 — Perturbation + process
# ──────────────────────────────────────────────

def show_stage3(adata: ad.AnnData, pert_model, pert_ckpt: dict, embs: np.ndarray, metrics: dict):
    st.header("Stage 3 — Perturbation Predictor (CPA-lite)")

    heldout = metrics.get("stage3_heldout_perturbation", C.HELDOUT_PERTURBATION)
    c1, c2, c3 = st.columns(3)
    c1.metric("Held-out perturbation", heldout)
    c2.metric("Per-gene Pearson", f"{metrics.get('stage3_per_gene_pearson', 0):.3f}")
    c3.metric("Top-20 DEG recall", f"{metrics.get('stage3_top20_deg_recall', 0):.3f}")

    col_a, col_b = st.columns(2)
    with col_a:
        scatter_png = C.FIG_DIR / "perturb_scatter.png"
        if scatter_png.exists():
            st.subheader("零样本预测散点图")
            st.image(str(scatter_png))
    with col_b:
        losses = pert_ckpt.get("losses", [])
        if losses:
            st.subheader("CPA-lite 训练 loss")
            fig, ax = _fig(5, 3)
            ax.plot(range(1, len(losses) + 1), losses, marker="o", markersize=3, color="tomato")
            ax.set_xlabel("epoch"); ax.set_ylabel("MSE loss")
            ax.set_title("Stage 3 perturbation model training"); fig.tight_layout(); _show(fig)

    # ── Basal / Delta decomposition ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 1: Basal + Delta 分解")
    st.markdown(
        r"""
CPA-lite 把预测拆成两路：

$$\hat{x} = \underbrace{f_\text{basal}(z)}_{\text{细胞基础状态}} + \underbrace{f_\text{pert}([z \| e_k])}_{\Delta\text{ 扰动效应}}$$

选一个细胞，逐基因对比 basal 和 delta 的贡献。
        """
    )

    perts = pert_ckpt["perts"]
    pert2id = {p: i for i, p in enumerate(perts)}
    X = adata.X if isinstance(adata.X, np.ndarray) else np.array(adata.X)
    gene_names = adata.var_names.to_numpy()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        pert_sel = st.selectbox("选择扰动", perts, key="s3_pert")
    with col_s2:
        demo_cell_idx = st.slider("选择细胞 index", 0, adata.n_obs - 1, 0, key="s3_cell")

    demo_emb = torch.as_tensor(embs[demo_cell_idx : demo_cell_idx + 1], dtype=torch.float32)
    demo_pid = torch.as_tensor([pert2id[pert_sel]], dtype=torch.long)

    pert_model.eval()
    with torch.no_grad():
        pred_t, basal_t, delta_t = pert_model(demo_emb, demo_pid)

    pred_np  = pred_t.numpy()[0]
    basal_np = basal_t.numpy()[0]
    delta_np = delta_t.numpy()[0]
    truth_np = X[demo_cell_idx]

    top20 = np.argsort(-np.abs(delta_np))[:20]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    # basal
    axes[0].bar(np.arange(20), basal_np[top20], color="steelblue")
    axes[0].set_xticks(np.arange(20)); axes[0].set_xticklabels(gene_names[top20], rotation=45, ha="right", fontsize=7)
    axes[0].set_title("Basal (baseline state)"); axes[0].set_ylabel("predicted expr")
    # delta
    colors = ["tomato" if d > 0 else "steelblue" for d in delta_np[top20]]
    axes[1].bar(np.arange(20), delta_np[top20], color=colors)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_xticks(np.arange(20)); axes[1].set_xticklabels(gene_names[top20], rotation=45, ha="right", fontsize=7)
    axes[1].set_title(f"Delta (perturbation effect: {pert_sel})"); axes[1].set_ylabel("delta expr")
    # pred vs truth
    axes[2].scatter(truth_np, pred_np, s=6, alpha=0.4, color="slateblue")
    for idx in top20[:5]:
        axes[2].annotate(gene_names[idx], (truth_np[idx], pred_np[idx]), fontsize=6)
    lim = [min(truth_np.min(), pred_np.min()), max(truth_np.max(), pred_np.max())]
    axes[2].plot(lim, lim, "k--", lw=0.8)
    axes[2].set_xlabel("truth expr"); axes[2].set_ylabel("predicted expr")
    axes[2].set_title("Pred vs Truth (single cell)")
    fig.suptitle(f"Basal + Delta decomposition — cell {demo_cell_idx}, pert={pert_sel}", fontsize=10)
    fig.tight_layout(); _show(fig)

    # stacked bar: basal + delta for top genes
    st.markdown("**Top-20 Δ 基因的 Basal / Delta 堆叠图**")
    fig, ax = _fig(11, 3.5)
    x = np.arange(20)
    ax.bar(x, basal_np[top20], label="basal", color="steelblue", alpha=0.8)
    ax.bar(x, delta_np[top20], bottom=basal_np[top20], label="delta", color="tomato", alpha=0.8)
    ax.scatter(x, truth_np[top20], marker="x", color="black", s=40, zorder=5, label="truth")
    ax.set_xticks(x); ax.set_xticklabels(gene_names[top20], rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=8); ax.set_title("basal + delta = prediction (vs truth)")
    ax.set_ylabel("expression"); fig.tight_layout(); _show(fig)

    # ── Perturbation embedding space ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 2: 扰动 Embedding 向量空间")
    st.markdown(
        "每种扰动有一个 **可学习的 64-dim 向量**（`nn.Embedding`）。"
        "下面展示所有扰动向量的 PCA 投影和成对距离。"
    )

    pert_vecs = pert_model.pert_emb.weight.detach().numpy()  # (n_perts, emb_dim)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if pert_vecs.shape[0] >= 2:
            n_comp = min(2, pert_vecs.shape[0])
            pca_p = PCA(n_components=n_comp).fit_transform(pert_vecs)
            fig, ax = _fig(4.5, 3.5)
            ax.scatter(pca_p[:, 0], pca_p[:, 1] if n_comp > 1 else np.zeros(len(perts)), s=80, color="coral")
            for i, p in enumerate(perts):
                ax.annotate(p, (pca_p[i, 0], pca_p[i, 1] if n_comp > 1 else 0), fontsize=8)
            ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
            ax.set_title("Perturbation vector PCA (learned embedding)"); fig.tight_layout(); _show(fig)

    with col_p2:
        # cosine sim between pert vectors
        norms = np.linalg.norm(pert_vecs, axis=1, keepdims=True) + 1e-8
        pert_norm = pert_vecs / norms
        sim_mat = pert_norm @ pert_norm.T
        fig, ax = _fig(4.5, 3.5)
        im = ax.imshow(sim_mat, vmin=-1, vmax=1, cmap="RdBu_r")
        ax.set_xticks(range(len(perts))); ax.set_xticklabels(perts, rotation=30, ha="right", fontsize=8)
        ax.set_yticks(range(len(perts))); ax.set_yticklabels(perts, fontsize=8)
        fig.colorbar(im, ax=ax); ax.set_title("Perturbation vector cosine similarity")
        fig.tight_layout(); _show(fig)

    # Pert vector magnitude
    mags = np.linalg.norm(pert_vecs, axis=1)
    fig, ax = _fig(6, 2.5)
    ax.bar(perts, mags, color="mediumseagreen")
    ax.set_ylabel("L2 norm"); ax.set_title("Perturbation vector magnitude (larger = stronger effect)")
    fig.tight_layout(); _show(fig)

    # ── DEG heatmap across perturbations ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 3: 各扰动 Δ 表达热力图")
    ctrl_mean = X[adata.obs["perturbation"].values == "control"].mean(0)
    delta_mat = []
    for p in perts:
        sel = np.where(adata.obs["perturbation"].values == p)[0][:30]
        if len(sel) == 0:
            delta_mat.append(np.zeros(len(gene_names)))
            continue
        pred_all = predict_expression(pert_model, embs[sel], pert2id[p])
        delta_mat.append(pred_all.mean(0) - ctrl_mean)
    delta_mat = np.array(delta_mat)

    top_deg = np.argsort(-np.abs(delta_mat).max(0))[:40]
    fig, ax = _fig(12, 4)
    im = ax.imshow(delta_mat[:, top_deg], aspect="auto", cmap="RdBu_r",
                   norm=mcolors.CenteredNorm())
    ax.set_yticks(range(len(perts))); ax.set_yticklabels(perts, fontsize=8)
    ax.set_xticks(range(len(top_deg)))
    ax.set_xticklabels(gene_names[top_deg], rotation=45, ha="right", fontsize=6)
    ax.set_title("Predicted delta expression heatmap — perturbation x gene (Top-40 by |delta|)")
    fig.colorbar(im, ax=ax, label="delta expr"); fig.tight_layout(); _show(fig)


# ──────────────────────────────────────────────
# Stage 4 — Mechanism + process
# ──────────────────────────────────────────────

def show_stage4(adata: ad.AnnData, pert_model, pert_ckpt: dict, embs: np.ndarray, metab, metrics: dict):
    st.header("Stage 4 — Mechanism Coupling (FBA)")

    c1, c2 = st.columns(2)
    c1.metric("Biomass R² (pred vs truth)", f"{metrics.get('stage4_biomass_r2', 0):.3f}")
    c2.metric("Mean pathway co-direction", f"{metrics.get('stage4_pathway_codirection', 0):.3f}")

    col_a, col_b = st.columns(2)
    with col_a:
        biomass_png = C.FIG_DIR / "biomass_scatter.png"
        if biomass_png.exists():
            st.subheader("Biomass: pred vs truth")
            st.image(str(biomass_png))
    with col_b:
        st.subheader("各通路一致性得分")
        perts = pert_ckpt["perts"]
        pert2id = {p: i for i, p in enumerate(perts)}
        X = adata.X if isinstance(adata.X, np.ndarray) else np.array(adata.X)
        ctrl_mean = X[adata.obs["perturbation"].values == "control"].mean(0)
        pw_scores = {}
        for p in perts:
            sel = np.where(adata.obs["perturbation"].values == p)[0][:50]
            if len(sel) == 0:
                continue
            pred_expr = predict_expression(pert_model, embs[sel], pert2id[p])
            delta = pred_expr.mean(0) - ctrl_mean
            pw_scores[p] = pathway_consistency(metab, delta)
        fig, ax = _fig(5, 3)
        colors = ["tomato" if v < 0.5 else "steelblue" for v in pw_scores.values()]
        ax.bar(list(pw_scores.keys()), list(pw_scores.values()), color=colors)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, label="random baseline")
        ax.set_ylabel("co-direction score"); ax.legend(fontsize=8)
        plt.xticks(rotation=15, ha="right"); fig.tight_layout(); _show(fig)

    # ── Stoichiometric matrix ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 1: 化学计量矩阵 S")
    st.markdown(
        "代谢网络由化学计量矩阵 **S** 描述，形状 `(n_metabolites, n_reactions)`。"
        "每列是一个反应：消耗 (-1) 或产生 (+1) 某代谢物。最后一列是生物量反应（消耗所有代谢物）。"
    )
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        fig, ax = _fig(5, 3.5)
        im = ax.imshow(metab.S, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        ax.set_xlabel("reaction"); ax.set_ylabel("metabolite")
        ax.set_title(f"S matrix ({metab.S.shape[0]} x {metab.S.shape[1]})")
        fig.colorbar(im, ax=ax); fig.tight_layout(); _show(fig)
    with col_s2:
        st.markdown("**酶-基因对应表**（每个反应由哪个基因的表达量控制）")
        gene_names = adata.var_names.to_numpy()
        df_enz = pd.DataFrame({
            "reaction": np.arange(metab.n_reactions),
            "enzyme_gene_id": metab.enzyme_gene,
            "gene_name": gene_names[metab.enzyme_gene],
            "is_biomass": [i == metab.biomass_idx for i in range(metab.n_reactions)],
        })
        st.dataframe(df_enz, use_container_width=True, height=280)

    # ── Expression → flux bounds (step-by-step) ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 2: Expression → Enzyme → Flux Bounds")
    st.markdown(
        "对选定细胞，展示 **表达量 → 酶丰度 → FBA 上界** 的逐步转换过程。"
    )
    demo_idx2 = st.slider("选择细胞 index", 0, adata.n_obs - 1, 0, key="s4_cell")
    pert_sel2 = st.selectbox("选择扰动", perts, key="s4_pert")

    sel2 = np.where(adata.obs["perturbation"].values == pert_sel2)[0][:1]
    if len(sel2) == 0:
        sel2 = np.array([demo_idx2])
    pred_expr = predict_expression(pert_model, embs[sel2], pert2id[pert_sel2])[0]
    ub = expression_to_flux_bounds(metab, pred_expr)
    result = fba(metab, ub)

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.5))
    # enzyme expression
    enz_expr = pred_expr[metab.enzyme_gene]
    axes[0].bar(np.arange(metab.n_reactions), enz_expr, color="steelblue")
    axes[0].set_xlabel("reaction"); axes[0].set_ylabel("log-expr")
    axes[0].set_title("Step 1: Enzyme gene predicted expression")
    # upper bounds
    axes[1].bar(np.arange(metab.n_reactions), ub, color="mediumseagreen")
    axes[1].set_xlabel("reaction"); axes[1].set_ylabel("flux upper bound")
    axes[1].set_title("Step 2: Normalized enzyme abundance (flux upper bound)")
    # actual flux
    fluxes = result["fluxes"]
    colors = ["gold" if i == metab.biomass_idx else "coral" for i in range(metab.n_reactions)]
    axes[2].bar(np.arange(metab.n_reactions), fluxes, color=colors)
    axes[2].set_xlabel("reaction"); axes[2].set_ylabel("flux")
    axes[2].set_title(f"Step 3: FBA solution — flux (biomass={result['biomass']:.3f})")
    fig.tight_layout(); _show(fig)

    # Constraint satisfaction check
    st.markdown("**约束满足检验：S · v ≈ 0（稳态约束）**")
    sv = metab.S @ fluxes
    fig, ax = _fig(6, 2.5)
    ax.bar(np.arange(len(sv)), sv, color=["tomato" if abs(x) > 0.01 else "steelblue" for x in sv])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("metabolite"); ax.set_ylabel("S.v residual")
    ax.set_title("Steady-state constraint residual (S*v, should be ~0)"); fig.tight_layout(); _show(fig)

    # ── Pathway consistency process ──
    st.divider()
    st.subheader("🔬 模型推理过程 — Step 3: 通路一致性计算")
    st.markdown(
        "KEGG-style 通路由若干酶基因组成。对每个通路，计算 Δ 表达方向的一致性：\n\n"
        r"$$\text{score} = \frac{|\sum_i \Delta g_i|}{\sum_i |\Delta g_i|}$$"
        "\n\n1 = 完全同向；0 = 完全抵消。"
    )
    delta2 = pred_expr - ctrl_mean

    for pw_name, pw_genes in metab.pathways.items():
        d = delta2[pw_genes]
        score = float(abs(d.sum()) / (np.abs(d).sum() + 1e-8))
        with st.expander(f"通路: {pw_name}  |  一致性得分: {score:.3f}"):
            col_pw1, col_pw2 = st.columns(2)
            with col_pw1:
                df_pw = pd.DataFrame({
                    "gene_id": pw_genes,
                    "gene_name": gene_names[pw_genes],
                    "delta_expr": d.round(4),
                    "direction": ["up" if x > 0 else "down" for x in d],
                })
                st.dataframe(df_pw, use_container_width=True)
            with col_pw2:
                fig, ax = _fig(4, 2.5)
                ax.bar(gene_names[pw_genes], d,
                       color=["tomato" if x > 0 else "steelblue" for x in d])
                ax.axhline(0, color="black", linewidth=0.8)
                ax.set_ylabel("delta expr"); ax.set_title(f"{pw_name} pathway delta expression")
                plt.xticks(rotation=20, ha="right"); fig.tight_layout(); _show(fig)

    # ── Flux heatmap across perturbations ──
    st.divider()
    st.subheader("扰动 × 反应 Flux 热力图")
    flux_mat = []
    for p in perts:
        sel = np.where(adata.obs["perturbation"].values == p)[0][:30]
        if len(sel) == 0:
            flux_mat.append(np.zeros(metab.n_reactions)); continue
        pe = predict_expression(pert_model, embs[sel], pert2id[p])
        fvecs = [fba(metab, expression_to_flux_bounds(metab, pe[j]))["fluxes"] for j in range(len(sel))]
        flux_mat.append(np.mean(fvecs, axis=0))
    flux_mat = np.array(flux_mat)
    fig, ax = _fig(9, 3.5)
    im = ax.imshow(flux_mat, aspect="auto", cmap="YlOrRd")
    ax.set_yticks(range(len(perts))); ax.set_yticklabels(perts, fontsize=8)
    ax.set_xlabel("reaction id"); ax.set_title("Mean FBA flux heatmap — perturbation x reaction")
    fig.colorbar(im, ax=ax, label="flux"); fig.tight_layout(); _show(fig)


# ──────────────────────────────────────────────
# Interactive
# ──────────────────────────────────────────────

def show_interactive(adata: ad.AnnData, pert_model, pert_ckpt: dict, embs: np.ndarray, metab):
    st.header("Interactive Prediction")
    st.caption("选择细胞类型和扰动，实时预测 Δ 表达、FBA 通量、DEG。")

    perts = pert_ckpt["perts"]
    col1, col2 = st.columns(2)
    with col1:
        cell_type = st.selectbox("Cell type", sorted(adata.obs["cell_type"].unique()))
    with col2:
        pert = st.selectbox("Perturbation", perts)

    mask = (adata.obs["cell_type"].values == cell_type) & (adata.obs["perturbation"].values == "control")
    if mask.sum() == 0:
        mask = adata.obs["cell_type"].values == cell_type
    idx = np.where(mask)[0][:50]
    if len(idx) == 0:
        st.warning("No cells available."); return

    cell_emb = embs[idx]
    pred_expr = predict_expression(pert_model, cell_emb, perts.index(pert))
    pred_mean = pred_expr.mean(0)
    ctrl_idx = np.where(adata.obs["perturbation"].values == "control")[0]
    ctrl_mean = np.asarray(adata.X[ctrl_idx]).mean(0)
    delta = pred_mean - ctrl_mean

    flux = predict_phenotype(metab, pred_mean)
    pw = pathway_consistency(metab, delta)

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted biomass flux", f"{flux['biomass']:.3f}")
    c2.metric("Pathway co-direction", f"{pw:.3f}")
    c3.metric("Cells used", str(len(idx)))

    col_a, col_b = st.columns(2)
    gene_names = adata.var_names.to_numpy()
    order = np.argsort(-np.abs(delta))[:20]

    with col_a:
        st.subheader("Top 20 DEGs")
        st.dataframe(pd.DataFrame({
            "gene": gene_names[order],
            "control_mean": ctrl_mean[order].round(3),
            "predicted_mean": pred_mean[order].round(3),
            "delta": delta[order].round(3),
        }), use_container_width=True)

    with col_b:
        st.subheader("FBA reaction fluxes")
        fig, ax = _fig(5, 3)
        ax.bar(np.arange(metab.n_reactions), flux["fluxes"], color="mediumseagreen")
        ax.set_xlabel("reaction"); ax.set_ylabel("flux"); fig.tight_layout(); _show(fig)

    st.subheader("Δ Expression distribution")
    fig, ax = _fig(9, 3)
    ax.hist(delta, bins=50, color="steelblue", edgecolor="white")
    ax.axvline(0, color="tomato", linewidth=1)
    ax.set_xlabel("predicted − control"); ax.set_ylabel("# genes")
    fig.tight_layout(); _show(fig)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    st.set_page_config(page_title="OpenVCell-MVP", page_icon="🧬", layout="wide")
    st.title("OpenVCell-MVP — Virtual Cell Pipeline")
    st.caption("4-stage pipeline: Data -> Foundation Model -> Perturbation -> Mechanism")

    adata, fm, pert_model, pert_ckpt, embs, metab, metrics = load_all()

    tabs = st.tabs([
        "Stage 1 · Data",
        "Stage 2 · Foundation Model",
        "Stage 3 · Perturbation",
        "Stage 4 · Mechanism",
        "Interactive",
    ])
    with tabs[0]:
        show_stage1(adata, metrics)
    with tabs[1]:
        show_stage2(adata, fm, embs, metrics)
    with tabs[2]:
        show_stage3(adata, pert_model, pert_ckpt, embs, metrics)
    with tabs[3]:
        show_stage4(adata, pert_model, pert_ckpt, embs, metab, metrics)
    with tabs[4]:
        show_interactive(adata, pert_model, pert_ckpt, embs, metab)


if __name__ == "__main__":
    main()
