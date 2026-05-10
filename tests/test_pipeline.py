"""Smoke test for the OpenVCell-MVP pipeline."""
import json
from pathlib import Path

from openvcell import config as C
from openvcell.pipeline import run


def test_pipeline_smoke(tmp_path, monkeypatch):
    # speed up: smaller everything
    monkeypatch.setattr(C, "N_CELLS", 300)
    monkeypatch.setattr(C, "N_GENES", 80)
    monkeypatch.setattr(C, "MAX_GENES_PER_CELL", 32)
    monkeypatch.setattr(C, "PRETRAIN_EPOCHS", 1)
    monkeypatch.setattr(C, "PERTURB_EPOCHS", 2)

    metrics = run()
    assert "qc" in metrics
    assert metrics["qc"]["n_cells"] > 0
    assert C.REPORT_PATH.exists()
    data = json.loads((C.ARTIFACTS / "metrics.json").read_text())
    assert "stage3_per_gene_pearson" in data
