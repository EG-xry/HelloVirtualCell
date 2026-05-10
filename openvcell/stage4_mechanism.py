"""Stage 4 — Mechanistic coupling (toy FBA + pathway consistency).

We build a tiny synthetic metabolic network with `N_REACTIONS` reactions
producing biomass from nutrients, where each reaction has an "enzyme gene".
Predicted gene expression from Stage 3 → enzyme abundance → upper bound
on the corresponding flux. Linear program maximizes biomass flux.

Pathway consistency: a small KEGG-style pathway prior (groups of co-regulated
genes); we score how well predicted Δexpression respects within-pathway
co-direction.

# TODO: replace with cobrapy + Human-GEM + tellurium ODE coupling
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from scipy.optimize import linprog

from . import config as C


@dataclass
class ToyMetabolism:
    S: np.ndarray                 # stoichiometric matrix (n_metabolites, n_reactions)
    enzyme_gene: np.ndarray       # gene index for each reaction (n_reactions,)
    biomass_idx: int              # reaction index that represents biomass
    pathways: Dict[str, List[int]]  # pathway_name -> list of gene indices

    @property
    def n_reactions(self) -> int:
        return self.S.shape[1]


def build_toy_metabolism(n_genes: int, seed: int = C.SEED) -> ToyMetabolism:
    rng = np.random.default_rng(seed)
    n_r, n_m = C.N_REACTIONS, C.N_METABOLITES
    # Random sparse stoichiometry, ensure last reaction is biomass (consumes all metabolites)
    S = np.zeros((n_m, n_r), dtype=np.float32)
    for r in range(n_r - 1):
        consumed = rng.integers(0, n_m)
        produced = rng.integers(0, n_m)
        while produced == consumed:
            produced = rng.integers(0, n_m)
        S[consumed, r] = -1.0
        S[produced, r] = 1.0
    # biomass reaction: consumes one unit of each metabolite
    S[:, -1] = -1.0

    enzyme_gene = rng.choice(n_genes, size=n_r, replace=False)
    pathways = {
        "glycolysis": list(enzyme_gene[:4].tolist()),
        "TCA":        list(enzyme_gene[4:8].tolist()),
        "biosynth":   list(enzyme_gene[8:].tolist()),
    }
    return ToyMetabolism(S=S, enzyme_gene=enzyme_gene, biomass_idx=n_r - 1, pathways=pathways)


def expression_to_flux_bounds(metab: ToyMetabolism, expr: np.ndarray) -> np.ndarray:
    """Map per-cell expression to upper-bound on each reaction flux."""
    enz = expr[metab.enzyme_gene]
    # rescale to [0.1, 10] roughly
    enz = np.clip(enz, 0, None)
    if enz.max() > 0:
        enz = enz / (enz.max() + 1e-8) * 10.0
    enz = enz + 0.1
    return enz


def fba(metab: ToyMetabolism, ub: np.ndarray) -> Dict[str, float]:
    """Solve max biomass flux s.t. S v = 0, 0 <= v <= ub."""
    n_r = metab.n_reactions
    c_obj = np.zeros(n_r)
    c_obj[metab.biomass_idx] = -1.0  # maximize → minimize negative
    A_eq = metab.S
    b_eq = np.zeros(metab.S.shape[0])
    bounds = [(0.0, float(u)) for u in ub]
    res = linprog(c_obj, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        return {"biomass": 0.0, "fluxes": np.zeros(n_r), "status": res.message}
    return {"biomass": float(-res.fun), "fluxes": res.x.astype(np.float32), "status": "ok"}


def pathway_consistency(metab: ToyMetabolism, delta_expr: np.ndarray) -> float:
    """Mean absolute mean-direction within pathways: higher = more co-regulated."""
    scores = []
    for genes in metab.pathways.values():
        d = delta_expr[genes]
        if len(d) == 0:
            continue
        # ratio of |sum| to sum of |.| → 1 means perfectly co-directional
        denom = np.sum(np.abs(d)) + 1e-8
        scores.append(float(abs(np.sum(d)) / denom))
    return float(np.mean(scores)) if scores else 0.0


def predict_phenotype(metab: ToyMetabolism, predicted_expr: np.ndarray) -> Dict[str, float]:
    """Run the full mechanism: expression → bounds → FBA → biomass."""
    ub = expression_to_flux_bounds(metab, predicted_expr)
    out = fba(metab, ub)
    return out


if __name__ == "__main__":  # pragma: no cover
    rng = np.random.default_rng(0)
    m = build_toy_metabolism(n_genes=200)
    expr = rng.normal(2.0, 1.0, size=200)
    print(predict_phenotype(m, expr))
