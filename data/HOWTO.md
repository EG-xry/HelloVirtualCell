# Data 目录说明

## 文件清单

| 文件 | 大小估计 | 说明 |
|---|---|---|
| `raw_census.h5ad` | ~200 MB | CELLxGENE Census 下载的原始数据，5000 个人类血液 T 细胞 × 60530 基因 |

## 数据来源

- **数据库**：[CELLxGENE Census](https://chanzuckerberg.github.io/cellxgene-census/)，由 Chan Zuckerberg Initiative 维护
- **Census 版本**：`2024-07-01`
- **物种**：Homo sapiens
- **过滤条件**：`tissue_general == "blood"` AND `cell_type == "T cell"`
- **细胞数**：5000（取符合条件的前 5000 个 joinid）

## 如何重新下载

删除缓存文件后重跑 Stage 1 即可自动重新联网下载：

```bash
rm data/raw_census.h5ad
.venv/bin/python -m openvcell.pipeline
```

或单独运行 Stage 1：

```bash
.venv/bin/python -c "from openvcell.stage1_data import build_corpus; build_corpus(force=True)"
```

> 需要联网，下载约需 1-3 分钟，取决于网速。

## 如何切换回合成数据

编辑 `openvcell/config.py`：

```python
USE_REAL_DATA = False   # 改为 False
```

再运行 `make all`，Stage 1 将在内存中生成 2000 × 200 的合成 scRNA-seq 数据，无需联网。

## 注意事项

- 真实数据有 **60530 个基因**，远大于 config 默认的 `N_GENES=200`。
  接入完整 pipeline 前需在 Stage 1 末尾做高变基因筛选（HVG selection），将基因数压缩到 `N_GENES`，否则 Stage 2 Transformer 维度会不匹配。
- 真实数据无扰动标签，`perturbation` 列统一标注为 `"control"`，Stage 3 的留一扰动评估将退化为单一类别，建议配合合成数据或 scPerturb 数据集使用。
- 此目录下的文件不纳入 git 版本控制（见 `.gitignore`）。
