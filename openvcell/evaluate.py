"""Evaluation utilities — gene-level Pearson, Top-K DEG recall, classifier metrics."""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from scipy.stats import pearsonr


def per_gene_pearson(pred: np.ndarray, truth: np.ndarray) -> float:
    """Mean Pearson correlation across genes (over cells)."""
    rs = []
    for g in range(pred.shape[1]):
        if pred[:, g].std() < 1e-8 or truth[:, g].std() < 1e-8:
            continue
        r, _ = pearsonr(pred[:, g], truth[:, g])
        if not np.isnan(r):
            rs.append(r)
    return float(np.mean(rs)) if rs else 0.0


def topk_deg_recall(pred_mean: np.ndarray, truth_mean: np.ndarray, control_mean: np.ndarray, k: int = 20) -> float:
    """Recall of top-K DEGs (by |Δ vs control|) between predicted and ground truth."""
    pred_delta = np.abs(pred_mean - control_mean)
    truth_delta = np.abs(truth_mean - control_mean)
    pred_top = set(np.argsort(-pred_delta)[:k].tolist())
    truth_top = set(np.argsort(-truth_delta)[:k].tolist())
    if not truth_top:
        return 0.0
    return len(pred_top & truth_top) / len(truth_top)


def cell_type_macro_f1(embs: np.ndarray, labels) -> float:
    """Train a simple logistic-regression classifier on embeddings; report macro-F1."""
    y = np.array(labels)
    if len(set(y)) < 2:
        return 0.0
    Xtr, Xte, ytr, yte = train_test_split(embs, y, test_size=0.3, random_state=0, stratify=y)
    clf = LogisticRegression(max_iter=500, multi_class="auto")
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    return float(f1_score(yte, pred, average="macro"))


def biomass_r2(pred: np.ndarray, truth: np.ndarray) -> float:
    if len(pred) < 2 or np.std(truth) < 1e-8:
        return 0.0
    ss_res = np.sum((pred - truth) ** 2)
    ss_tot = np.sum((truth - truth.mean()) ** 2) + 1e-8
    return float(1 - ss_res / ss_tot)
