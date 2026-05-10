# Stage 3 扰动预测模块（CPAlite）问答笔记

> 整理自对话，日期：2026-05-11

---

## Q1：这三行代码是什么意思？

```python
# 2. 扰动嵌入：每种扰动都有学习到的向量表示
self.pert_emb = nn.Embedding(n_perts, emb_dim)

# 3. 扰动解码器：(细胞嵌入 + 扰动嵌入) → 扰动效应
self.pert_dec = nn.Sequential(
    nn.Linear(emb_dim * 2, hidden),
    nn.GELU(),
    nn.Linear(hidden, n_genes)
)
```

**A：**

这三行是 `CPAlite` 模型（`openvcell/stage3_perturb.py:62-64`）的核心架构：

1. **`self.pert_emb = nn.Embedding(n_perts, emb_dim)`**
   为每种扰动（药物/基因敲除）学习一个 `emb_dim` 维向量，类似 NLP 里的 word embedding。

2. **`self.pert_dec`**
   把 `[cell_emb; pert_vec]`（拼接后 `emb_dim*2` 维）映射到 `n_genes` 维的 Δ 表达量预测值（扰动效应）。

完整前向传播（`stage3_perturb.py:69-70`）：

```python
pert_vec = self.pert_emb(pert_id)                              # 查表取扰动向量
delta    = self.pert_dec(torch.cat([cell_emb, pert_vec], dim=-1))  # 预测 Δgene
```

---

## Q2：底层的逻辑和代码实现

### 一、生物直觉

一个细胞的基因表达可以拆成两部分：

```
观测到的表达量 = 细胞本身的基础状态 + 扰动带来的偏移
```

"基础状态"由细胞类型决定（免疫细胞 vs 神经元）；"扰动偏移"由施加的药物/基因敲除决定，但同一种扰动在不同细胞上效果也不同——所以偏移还要依赖细胞自身的嵌入。

这正是 CPA（Compositional Perturbation Autoencoder）的核心假设，这里实现的是简化版 CPAlite。

---

### 二、数学建模

设：
- $z \in \mathbb{R}^d$：来自 Stage 2 Transformer 的细胞嵌入
- $e_k \in \mathbb{R}^d$：第 $k$ 种扰动的可学习向量（Embedding 表）

前向公式：

$$\hat{x} = \underbrace{f_\text{basal}(z)}_{\text{基础解码}} + \underbrace{f_\text{pert}\bigl([z \| e_k]\bigr)}_{\text{扰动效应}}$$

- $f_\text{basal}$：Linear → GELU → Linear，$d \to n_\text{genes}$
- $f_\text{pert}$：Linear → GELU → Linear，$2d \to n_\text{genes}$
- 损失：$\mathcal{L} = \|\hat{x} - x\|^2$（MSE，对原始表达量回归）

---

### 三、代码逐层拆解

#### 3.1 数据准备（`stage3_perturb.py:29-49`）

```python
def build_pert_dataset(adata, cell_embs):
    perts = list(C.PERTURBATIONS)          # ["ctrl", "drug_A", "drug_X", ...]
    pert2id = {p: i for i, p in enumerate(perts)}   # 字符串 → 整数 ID

    pert_ids = np.array([pert2id[p] for p in adata.obs["perturbation"]])
    X = adata.X  # shape: (n_cells, n_genes)，原始表达矩阵
    return cell_embs, pert_ids, X, perts
```

每个样本是一个三元组 `(cell_emb, pert_id, expr)`，其中 `expr` 是目标（要预测的真实表达量）。

---

#### 3.2 模型结构（`stage3_perturb.py:54-71`）

```python
class CPAlite(nn.Module):
    def __init__(self, emb_dim, n_perts, n_genes, hidden):
        # 路径1：基础解码器 —— 只看细胞自身
        self.basal = nn.Sequential(
            nn.Linear(emb_dim, hidden), nn.GELU(), nn.Linear(hidden, n_genes)
        )
        # 路径2a：扰动 Embedding 表 —— 每种扰动学一个向量
        self.pert_emb = nn.Embedding(n_perts, emb_dim)
        # 路径2b：扰动解码器 —— 拼接后预测偏移量
        self.pert_dec = nn.Sequential(
            nn.Linear(emb_dim * 2, hidden), nn.GELU(), nn.Linear(hidden, n_genes)
        )

    def forward(self, cell_emb, pert_id):
        basal = self.basal(cell_emb)                          # (B, n_genes)
        pert_vec = self.pert_emb(pert_id)                    # (B, emb_dim)
        delta = self.pert_dec(torch.cat([cell_emb, pert_vec], dim=-1))  # (B, n_genes)
        return basal + delta, basal, delta   # 返回三份，方便调试
```

`forward` 返回 `(pred, basal, delta)` 三元组：训练时只用 `pred`，但 `basal` 和 `delta` 可以单独分析（如验证"不加扰动时 delta 是否接近 0"）。

---

#### 3.3 训练：留一扰动评估（`stage3_perturb.py:76-138`）

```python
heldout_id = pert2id[heldout]            # 比如 "drug_X" → id=3
train_mask = pert_ids != heldout_id      # 其余扰动参与训练
test_mask  = ~train_mask                 # heldout 扰动只在测试时出现
```

这叫 **zero-shot perturbation generalization**：模型在训练时从未见过 `drug_X`，但它的 Embedding 向量仍存在于参数表中。

> **细节**：`drug_X` 的样本不在训练集里，它的 embedding 行**从未被更新，保持随机初始化**。PyTorch 的 `nn.Embedding` 只对实际被 `forward` 访问到的行计算梯度（稀疏梯度）。这意味着测试时用的是随机向量——这是当前实现的局限，真实 CPA 需要额外的组合推断来处理未见扰动。

---

#### 3.4 损失与优化（`stage3_perturb.py:96-115`）

```python
opt = torch.optim.AdamW(model.parameters(), lr=C.PERTURB_LR)
mse = nn.MSELoss()

for c, p, e in train_dl:
    pred, _, _ = model(c, p)
    loss = mse(pred, e)           # 预测表达量 vs 真实表达量
    opt.zero_grad(); loss.backward(); opt.step()
```

直接对**绝对表达量**做 MSE，而非对 Δ 表达量（相对于对照组的差值）。这是简化处理，真实 CPA 会对控制组归一化后预测差值。

---

### 四、整体数据流

```
Stage 2 输出
cell_embs (N, 64)
       │
       ├──► basal MLP ──────────────────────────► basal (N, 200)
       │                                                │
       └──► cat([cell_emb, pert_vec]) → pert MLP ──► delta (N, 200)
                          ▲                              │
              pert_emb[pert_id]                          ▼
              (n_perts, 64)                        pred = basal + delta
                                                         │
                                                    MSE(pred, X_真实)
```

---

### 五、与真实 CPA 的差距（TODO 注释标注的方向）

| 当前 CPAlite | 真实 CPA / GEARS |
|---|---|
| 直接回归绝对表达量 | 预测相对于对照组的 Δ |
| 未见扰动 = 随机向量 | 用已知扰动的组合推断新扰动 |
| 单一扰动 | 支持多扰动组合 |
| MSE 损失 | MSE + MMD/对抗损失 |

`stage3_perturb.py:10` 的 `TODO` 注释指向了替换路径：CPA、GEARS、CellOT、Flow Matching。
