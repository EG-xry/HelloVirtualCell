# OpenVCell-MVP — Run Report

## Data (Stage 1)
- cells: **5000**, genes: **200**
- cell types: 1, perturbations: 5
- median counts/cell: 1129.5

## Foundation model (Stage 2)
- final masked-CE loss: **0.924**
- cell-type macro-F1 from embeddings: **0.000**
- ![pca](figures/embeddings_pca.png)
- ![loss](figures/pretrain_loss.png)

## Perturbation prediction (Stage 3, leave-perturb-out)
- held-out perturbation: **drug_X**
- per-gene Pearson  : **0.572**
- Top-20 DEG recall : **0.100**
- ![scatter](figures/perturb_scatter.png)

## Mechanism coupling (Stage 4)
- biomass R² (pred vs truth): **0.000**
- pathway co-direction score: **0.357**
- ![biomass](figures/biomass_scatter.png)

---
Run `streamlit run openvcell/app.py` to launch the interactive demo.
