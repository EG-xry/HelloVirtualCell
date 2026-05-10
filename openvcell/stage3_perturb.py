"""Stage 3 — Perturbation response prediction (CPA-lite).

Inputs : (cell_embedding from Stage 2, perturbation one-hot)
Output : ΔExpression vector of length n_genes  (predicted - control)

Train on (cell, perturbation, expression) triples; evaluate with
leave-perturbation-out: hold one perturbation completely out of training and
test zero-shot prediction quality.

# TODO: replace with CPA / GEARS / CellOT / Flow Matching
"""
from __future__ import annotations

import json
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import anndata as ad

from . import config as C
from .stage2_foundation import embed_cells, load_model


# ----------------------- Data -----------------------

def build_pert_dataset(adata: ad.AnnData, cell_embs: np.ndarray) -> Tuple[np.ndarray, ...]:
    """Construct (cell_emb, pert_id, expression) arrays."""
    perts: List[str] = list(C.PERTURBATIONS)
    pert2id = {p: i for i, p in enumerate(perts)}

    pert_ids = np.array([pert2id[p] for p in adata.obs["perturbation"]], dtype=np.int64)
    X = adata.X if isinstance(adata.X, np.ndarray) else adata.X.toarray()
    return cell_embs.astype(np.float32), pert_ids, X.astype(np.float32), perts


class PertDataset(Dataset):
    def __init__(self, cell_embs, pert_ids, expr):
        self.c = cell_embs
        self.p = pert_ids
        self.e = expr

    def __len__(self):
        return self.c.shape[0]

    def __getitem__(self, i):
        return self.c[i], self.p[i], self.e[i]


# ----------------------- Model -----------------------

class CPAlite(nn.Module):
    """Predict expression = decoder(cell_emb_basal) + perturbation_effect(pert_id, cell_emb)."""

    def __init__(self, emb_dim: int, n_perts: int, n_genes: int, hidden: int = C.PERTURB_HIDDEN):
        super().__init__()
        self.basal = nn.Sequential(
            nn.Linear(emb_dim, hidden), nn.GELU(), nn.Linear(hidden, n_genes),
        )
        self.pert_emb = nn.Embedding(n_perts, emb_dim)
        self.pert_dec = nn.Sequential(
            nn.Linear(emb_dim * 2, hidden), nn.GELU(), nn.Linear(hidden, n_genes),
        )

    def forward(self, cell_emb, pert_id):
        basal = self.basal(cell_emb)
        pert_vec = self.pert_emb(pert_id)
        delta = self.pert_dec(torch.cat([cell_emb, pert_vec], dim=-1))
        return basal + delta, basal, delta


# ----------------------- Train / eval -----------------------

def train_perturb(
    adata: ad.AnnData,
    cell_embs: np.ndarray,
    heldout: str = C.HELDOUT_PERTURBATION,
    epochs: int = C.PERTURB_EPOCHS,
    verbose: bool = True,
):
    torch.manual_seed(C.SEED)
    cells, pert_ids, expr, perts = build_pert_dataset(adata, cell_embs)
    pert2id = {p: i for i, p in enumerate(perts)}
    heldout_id = pert2id[heldout]

    train_mask = pert_ids != heldout_id
    test_mask = ~train_mask

    train_ds = PertDataset(cells[train_mask], pert_ids[train_mask], expr[train_mask])
    test_ds = PertDataset(cells[test_mask], pert_ids[test_mask], expr[test_mask])
    train_dl = DataLoader(train_ds, batch_size=C.PERTURB_BATCH, shuffle=True)

    model = CPAlite(emb_dim=cells.shape[1], n_perts=len(perts), n_genes=expr.shape[1])
    opt = torch.optim.AdamW(model.parameters(), lr=C.PERTURB_LR)
    mse = nn.MSELoss()

    losses = []
    model.train()
    for ep in range(epochs):
        ep_loss = 0.0
        n = 0
        for c, p, e in train_dl:
            c = torch.as_tensor(c, dtype=torch.float32)
            p = torch.as_tensor(p, dtype=torch.long)
            e = torch.as_tensor(e, dtype=torch.float32)
            pred, _, _ = model(c, p)
            loss = mse(pred, e)
            opt.zero_grad(); loss.backward(); opt.step()
            ep_loss += float(loss.item()); n += 1
        avg = ep_loss / max(1, n)
        losses.append(avg)
        if verbose:
            print(f"[stage3] epoch {ep+1}/{epochs}  MSE={avg:.4f}")

    # Evaluate zero-shot on heldout perturbation
    model.eval()
    with torch.no_grad():
        c = torch.as_tensor(cells[test_mask], dtype=torch.float32)
        p = torch.as_tensor(pert_ids[test_mask], dtype=torch.long)
        pred, _, _ = model(c, p)
        pred = pred.numpy()
    truth = expr[test_mask]

    torch.save(
        {
            "state_dict": model.state_dict(),
            "emb_dim": cells.shape[1],
            "n_perts": len(perts),
            "n_genes": expr.shape[1],
            "perts": perts,
            "losses": losses,
            "heldout": heldout,
        },
        C.PERTURB_MODEL_PATH,
    )
    return model, {"pred": pred, "truth": truth, "heldout": heldout, "perts": perts, "losses": losses}


def load_perturb_model() -> Tuple[CPAlite, dict]:
    ckpt = torch.load(C.PERTURB_MODEL_PATH, map_location="cpu", weights_only=False)
    model = CPAlite(emb_dim=ckpt["emb_dim"], n_perts=ckpt["n_perts"], n_genes=ckpt["n_genes"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model, ckpt


@torch.no_grad()
def predict_expression(model: CPAlite, cell_emb: np.ndarray, pert_id: int) -> np.ndarray:
    c = torch.as_tensor(cell_emb, dtype=torch.float32)
    if c.ndim == 1:
        c = c.unsqueeze(0)
    p = torch.as_tensor([pert_id] * c.shape[0], dtype=torch.long)
    pred, _, _ = model(c, p)
    return pred.numpy()


if __name__ == "__main__":  # pragma: no cover
    from .stage1_data import build_corpus
    a = build_corpus()
    fm = load_model()
    embs = embed_cells(fm, a.X)
    train_perturb(a, embs)
