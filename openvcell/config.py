"""Global configuration for OpenVCell-MVP.

Modify these knobs to scale up / switch to real data.
"""
from pathlib import Path

# ----------------- Paths -----------------
ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)

DATA_PATH = ARTIFACTS / "vc_corpus.h5ad"
MODEL_PATH = ARTIFACTS / "foundation.pt"
PERTURB_MODEL_PATH = ARTIFACTS / "perturb.pt"
REPORT_PATH = ARTIFACTS / "report.md"
FIG_DIR = ARTIFACTS / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ----------------- Data -----------------
USE_REAL_DATA = False  # if True, try cellxgene-census (requires internet + extra deps)
N_CELLS = 2000
N_GENES = 200
N_CELL_TYPES = 3
PERTURBATIONS = ["control", "KO_geneA", "KO_geneB", "drug_X", "cytokine_Y"]
SEED = 42

# ----------------- Stage 2: foundation model -----------------
EMB_DIM = 64
N_HEADS = 4
N_LAYERS = 2
MAX_GENES_PER_CELL = 64           # context length (top-k expressed genes)
MASK_RATIO = 0.15
PRETRAIN_EPOCHS = 5
PRETRAIN_BATCH = 64
PRETRAIN_LR = 1e-3

# ----------------- Stage 3: perturbation model -----------------
PERTURB_HIDDEN = 128
PERTURB_EPOCHS = 20
PERTURB_BATCH = 64
PERTURB_LR = 1e-3
HELDOUT_PERTURBATION = "drug_X"   # leave-perturbation-out evaluation

# ----------------- Stage 4: mechanism -----------------
N_REACTIONS = 12
N_METABOLITES = 8
