"""Stage 2 — Single-cell foundation model (mini-Transformer).

MVP: tokenize each cell as the top-K expressed (gene_id, expr_bin) pairs and
train a small Transformer with masked-expression objective (à la scGPT/Geneformer).
Outputs a per-cell embedding usable downstream.

# TODO: replace with scGPT / Geneformer / UCE pretrained weights + LoRA fine-tune
"""
from __future__ import annotations

import math
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import anndata as ad

from . import config as C

EXPR_BINS = 8  # discretize expression into N bins (rank-value tokens)


# ----------------------- Tokenization -----------------------

def tokenize_cell(expr_row: np.ndarray, max_genes: int = C.MAX_GENES_PER_CELL):
    """Return (gene_ids, expr_bins) for the top-`max_genes` expressed genes."""
    idx = np.argsort(-expr_row)[:max_genes]
    vals = expr_row[idx]
    if vals.max() > 0:
        bins = np.clip(np.floor(vals / (vals.max() + 1e-8) * EXPR_BINS), 0, EXPR_BINS - 1).astype(np.int64)
    else:
        bins = np.zeros_like(idx, dtype=np.int64)
    return idx.astype(np.int64), bins


class CellDataset(Dataset):
    def __init__(self, X: np.ndarray, max_genes: int = C.MAX_GENES_PER_CELL):
        self.X = X.astype(np.float32)
        self.max_genes = max_genes

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, i):
        gene_ids, expr_bins = tokenize_cell(self.X[i], self.max_genes)
        # pad to fixed length for easy batching
        pad = self.max_genes - len(gene_ids)
        if pad > 0:
            gene_ids = np.concatenate([gene_ids, np.zeros(pad, dtype=np.int64)])
            expr_bins = np.concatenate([expr_bins, np.zeros(pad, dtype=np.int64)])
            mask = np.concatenate([np.ones(self.max_genes - pad), np.zeros(pad)]).astype(np.float32)
        else:
            mask = np.ones(self.max_genes, dtype=np.float32)
        return gene_ids, expr_bins, mask


# ----------------------- Model -----------------------

class CellFoundation(nn.Module):
    def __init__(
        self,
        n_genes: int,
        emb_dim: int = C.EMB_DIM,
        n_heads: int = C.N_HEADS,
        n_layers: int = C.N_LAYERS,
        n_bins: int = EXPR_BINS,
    ):
        super().__init__()
        self.gene_emb = nn.Embedding(n_genes + 1, emb_dim)        # +1 for pad
        self.expr_emb = nn.Embedding(n_bins + 1, emb_dim)         # +1 for [MASK]
        self.cls_token = nn.Parameter(torch.randn(1, 1, emb_dim) * 0.02)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=emb_dim, nhead=n_heads, dim_feedforward=emb_dim * 2,
            batch_first=True, activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.expr_head = nn.Linear(emb_dim, n_bins)               # predict masked expr bin
        self.mask_token_id = n_bins                                # special id

    def forward(self, gene_ids, expr_bins, key_padding_mask=None):
        b = gene_ids.size(0)
        h = self.gene_emb(gene_ids) + self.expr_emb(expr_bins)    # (B, L, D)
        cls = self.cls_token.expand(b, -1, -1)
        h = torch.cat([cls, h], dim=1)                             # prepend [CLS]
        if key_padding_mask is not None:
            cls_mask = torch.zeros(b, 1, dtype=key_padding_mask.dtype, device=key_padding_mask.device)
            kpm = torch.cat([cls_mask, key_padding_mask], dim=1)
        else:
            kpm = None
        h = self.encoder(h, src_key_padding_mask=kpm)
        cell_emb = h[:, 0]                                         # (B, D)
        token_logits = self.expr_head(h[:, 1:])                    # (B, L, n_bins)
        return cell_emb, token_logits


# ----------------------- Training -----------------------

def pretrain(adata: ad.AnnData, epochs: int = C.PRETRAIN_EPOCHS, verbose: bool = True):
    torch.manual_seed(C.SEED)
    X = adata.X if isinstance(adata.X, np.ndarray) else adata.X.toarray()
    n_genes = adata.n_vars
    ds = CellDataset(X)
    dl = DataLoader(ds, batch_size=C.PRETRAIN_BATCH, shuffle=True)

    model = CellFoundation(n_genes=n_genes)
    opt = torch.optim.AdamW(model.parameters(), lr=C.PRETRAIN_LR)
    ce = nn.CrossEntropyLoss(reduction="none")

    losses = []
    model.train()
    for ep in range(epochs):
        ep_loss = 0.0
        n_batches = 0
        for gene_ids, expr_bins, mask in dl:
            # random mask some positions
            rand = torch.rand_like(expr_bins, dtype=torch.float)
            mask_pos = (rand < C.MASK_RATIO) & (mask.bool())
            target = expr_bins.clone()
            corrupted = expr_bins.clone()
            corrupted[mask_pos] = model.mask_token_id

            key_padding_mask = (mask == 0)  # True = ignore
            _, logits = model(gene_ids, corrupted, key_padding_mask=key_padding_mask)
            loss_per = ce(logits.reshape(-1, EXPR_BINS), target.reshape(-1))
            loss = (loss_per * mask_pos.reshape(-1).float()).sum() / (mask_pos.sum().clamp(min=1).float())

            opt.zero_grad()
            loss.backward()
            opt.step()
            ep_loss += float(loss.item())
            n_batches += 1
        avg = ep_loss / max(1, n_batches)
        losses.append(avg)
        if verbose:
            print(f"[stage2] epoch {ep+1}/{epochs}  masked-CE loss={avg:.4f}")

    torch.save({"state_dict": model.state_dict(), "n_genes": n_genes, "losses": losses}, C.MODEL_PATH)
    return model, losses


def load_model() -> CellFoundation:
    ckpt = torch.load(C.MODEL_PATH, map_location="cpu", weights_only=False)
    model = CellFoundation(n_genes=ckpt["n_genes"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model


@torch.no_grad()
def embed_cells(model: CellFoundation, X: np.ndarray) -> np.ndarray:
    model.eval()
    ds = CellDataset(X)
    dl = DataLoader(ds, batch_size=128, shuffle=False)
    embs = []
    for gene_ids, expr_bins, mask in dl:
        kpm = (mask == 0)
        cell_emb, _ = model(gene_ids, expr_bins, key_padding_mask=kpm)
        embs.append(cell_emb.numpy())
    return np.concatenate(embs, axis=0)


if __name__ == "__main__":  # pragma: no cover
    from .stage1_data import build_corpus
    a = build_corpus()
    pretrain(a)
