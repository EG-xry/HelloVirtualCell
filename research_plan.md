# 虚拟细胞 (Virtual Cell) 研究计划

> 充分运用开源工具与开源数据，构建一个可计算、可预测、可解释的虚拟细胞研究路径

---

## 0. 摘要 (TL;DR)

**虚拟细胞 (Virtual Cell, VC)** 是当前 AI for Science 的旗舰目标之一：用数据驱动 + 机理建模的方式，在计算机中重建一个能"对扰动做出可预测响应"的细胞。本研究计划提出一条完全基于**开源工具链 + 公开数据集**的路线，分四个阶段（基础数据底座 → 单细胞基础模型 → 扰动响应预测 → 多模态多尺度虚拟细胞）逐步推进，每阶段均给出**具体数据源、开源工具、可验证里程碑**与**评估指标**，确保结果可复现、可对照、可发表。

核心目标：
1. 建立一个跨模态（转录组 / 蛋白组 / 表观 / 影像 / 空间）的细胞状态表征空间。
2. 构建一个能预测**基因/药物/环境扰动 → 细胞状态变化**的生成式模型。
3. 与机理模型 (代谢 FBA、信号通路 ODE、Whole-Cell Model) 耦合，形成多尺度可解释的虚拟细胞原型。

---

## 1. 研究背景与意义

### 1.1 什么是虚拟细胞
- **狭义**：对单个细胞类型（如 *E. coli*、酵母、HeLa、人 iPSC）进行**全过程、全分子**的计算重建（参考 Karr et al. 2012 *Cell* 的 *M. genitalium* whole-cell model）。
- **广义 (当前 AI 时代)**：训练一个能在**任意扰动下预测细胞多组学状态**的基础模型 (Foundation Model)，作为干湿实验回路中的"硅基对照组"。
- 代表性愿景：CZI (Chan Zuckerberg Initiative) 的 *Virtual Cells* 项目、Arc Institute 的 *Evo / scGPT*、Stanford 的 *Universal Cell Embeddings (UCE)*。

### 1.2 为什么现在做
| 驱动因素 | 现状 |
|---|---|
| 数据爆炸 | CELLxGENE > 1 亿单细胞、HuBMAP / HCA 全器官图谱 |
| 算力 | 消费级 4090 / 学术 H100 已可训练 1-3B 单细胞模型 |
| 算法 | Transformer / Diffusion / Flow Matching / Graph NN 成熟 |
| 开源生态 | scanpy / scvi-tools / scGPT / Geneformer / CellOT 全部 MIT/BSD |
| 评估基准 | Open Problems、PerturBench、scPerturb 已建立公平 benchmark |

### 1.3 科学问题
1. **表征**：能否学到一个跨物种、跨组织、跨条件的"细胞通用语义空间"？
2. **预测**：给定一个未见过的扰动（基因敲除组合 / 新药 / 新剂量），能否 zero-shot 预测细胞响应？
3. **机理**：纯数据驱动模型能否被反向蒸馏成可解释的基因调控网络 / 通路图？
4. **多尺度**：如何把**分子级 (omics)** 与**细胞级 (形态/影像)** 与**群体级 (空间/组织)** 统一？

---

## 2. 总体研究框架

```
        ┌────────────────────────────────────────────────┐
        │   Stage 4: 多尺度虚拟细胞 (Omics + Imaging +    │
        │            Spatial + Mechanistic ODE/FBA)      │
        └──────────────────▲─────────────────────────────┘
                           │
        ┌──────────────────┴─────────────────────────────┐
        │   Stage 3: 扰动响应预测 (Perturbation Model)   │
        │   基因敲除 / 药物 / 细胞因子 → ΔExpression     │
        └──────────────────▲─────────────────────────────┘
                           │
        ┌──────────────────┴─────────────────────────────┐
        │   Stage 2: 单细胞基础模型 (Cell Foundation     │
        │   Model)  scGPT / Geneformer / UCE 复现 + 改进 │
        └──────────────────▲─────────────────────────────┘
                           │
        ┌──────────────────┴─────────────────────────────┐
        │   Stage 1: 数据底座 (Atlas + QC + Harmonized) │
        │   CELLxGENE / HCA / Tabula Sapiens / scPerturb │
        └────────────────────────────────────────────────┘
```

---

## 3. 开源数据资源 (Data Sources)

| 数据类型 | 数据集 | 规模 | 链接/工具 |
|---|---|---|---|
| 单细胞 RNA-seq Atlas | **CELLxGENE Census** | >1 亿 cells, >700 datasets | `cellxgene-census` Python API |
| 人类细胞图谱 | **Human Cell Atlas (HCA)** | 全器官 | `hca-cli` / `anndata` |
| 多器官 reference | **Tabula Sapiens / Muris** | 50+ 组织 | figshare 公开 |
| 扰动数据 (CRISPR) | **scPerturb** | 100+ 数据集，统一格式 | scperturb.org |
| 大规模 Perturb-seq | **Replogle 2022 (genome-wide)** | 250 万 cells × 9867 KO | GEO: GSE264667 |
| 药物扰动 | **LINCS L1000 / sci-Plex** | >1M profiles | clue.io / GEO |
| 空间转录组 | **10x Visium / Stereo-seq / MERFISH 公开集** | - | SpatialData / squidpy |
| 蛋白组 / 影像 | **Human Protein Atlas (HPA)** | 全蛋白亚细胞定位 | proteinatlas.org |
| 细胞影像 | **JUMP-CP (Cell Painting)** | 1.6 亿图像 | AWS Open Data |
| 通路 / 网络 | **Reactome / KEGG / OmniPath / STRING** | - | `omnipath` / `pypath` |
| 代谢模型 | **BiGG Models / Human-GEM** | 100+ GEMs | `cobrapy` |
| 机理模型 | **BioModels / Karr WCM (M. genitalium)** | SBML | `tellurium` / `libsbml` |
| 基因组语言模型预训练 | **Evo / Nucleotide Transformer / DNA-BERT** | 公开 weights | HuggingFace |

---

## 4. 开源工具链 (Toolchain)

**数据处理**
- `scanpy`, `anndata`, `muon` (多组学), `mudata`
- `scvi-tools` (变分推断、batch correction、scVI/scANVI/totalVI)
- `pertpy` (扰动分析专用)
- `SpatialData`, `squidpy` (空间)

**基础模型 / 表征**
- `scGPT` (Wang et al. 2024, *Nat Methods*)
- `Geneformer` (Theodoris 2023, *Nature*)
- `UCE` (Universal Cell Embeddings, Stanford)
- `scFoundation` (百图生科)
- `CellPLM`, `Nicheformer` (空间)

**扰动预测**
- `CPA` (Compositional Perturbation Autoencoder)
- `scGen`, `CellOT` (Optimal Transport)
- `GEARS` (Roohani 2023, *Nat Biotech*) — 基因敲除组合预测
- `PerturBench` — 公平 benchmark

**机理建模**
- `cobrapy`, `escher` (代谢 FBA)
- `tellurium`, `roadrunner` (ODE/SBML)
- `PySB` (规则化信号建模)
- `vivarium` (多尺度组合框架，CMU/Stanford)

**影像 / 形态**
- `cellprofiler`, `deepprofiler`, `cellpose`, `stardist`

**训练 / 部署**
- PyTorch + Lightning / HuggingFace Transformers / DeepSpeed
- Weights & Biases (实验追踪)、DVC (数据版本)、Snakemake / Nextflow (流水线)

---

## 5. 分阶段研究计划

### Stage 1：构建统一的数据底座 (Month 1–3)

**目标**：搭建一个可重复、可扩展的开源数据流水线，产出统一格式 (`AnnData` / `MuData`) 的预训练语料。

任务：
1. 用 `cellxgene-census` 抽取目标范围（如人 + 鼠 + 全组织）的 SCRNA-seq，控制在 5000 万 cells 起步。
2. 统一 QC：每细胞最小基因数、线粒体比率、doublet (`scrublet`)、批次注释。
3. 基因符号统一化：mygene / HGNC，跨物种 ortholog 对齐 (Ensembl Compara)。
4. 整合 scPerturb / Replogle / sci-Plex 作为**扰动子集**。
5. 数据版本化：DVC + S3/MinIO；写 Snakemake 流水线。

里程碑：
- [ ] M1.1：发布 `vc-corpus-v0`：≥ 50M cells，统一 18k 基因 vocab。
- [ ] M1.2：发布 `vc-perturb-v0`：scPerturb + Replogle 合并版。
- [ ] M1.3：技术报告 + GitHub repo，附带 `make all` 可一键复现。

评估：数据量、覆盖组织数、批次效应 (kBET / iLISI) 基线。

---

### Stage 2：单细胞基础模型 (Month 3–8)

**目标**：复现并改进 scGPT / Geneformer / UCE，得到可下游迁移的细胞嵌入。

任务：
1. **复现基线**：在 `vc-corpus-v0` 上训练 scGPT-small (10M)、Geneformer-12L。
2. **改进点候选**（选 1–2 落地）：
   - (a) **Rank-value tokenization v2**：引入相对表达 + 通路 token，缓解 dropout 噪声。
   - (b) **多模态扩展**：联合 scRNA + scATAC (10x Multiome) → MuFormer。
   - (c) **跨物种共享词表**：通过 ortholog 图嵌入实现 zero-shot 跨物种。
   - (d) **长上下文**：FlashAttention-2 + Mamba，将 context 从 2k 扩到 16k 基因。
3. **下游任务评估**（Open Problems benchmark）：
   - cell type annotation (zero-shot / fine-tune)
   - batch integration (scIB metrics)
   - gene perturbation response retrieval

里程碑：
- [ ] M2.1：复现 scGPT，性能持平 ±2%。
- [ ] M2.2：改进版在 ≥ 2 个 benchmark 上 SOTA 或可比。
- [ ] M2.3：发布预训练 checkpoint + HuggingFace card。

评估：scIB 综合分、注释 macro-F1、嵌入 KNN 召回。

---

### Stage 3：扰动响应预测 (Month 6–12，可与 Stage 2 并行)

**目标**：构建一个能在 unseen 扰动 / unseen cell type 上 zero/few-shot 预测表达变化的模型。

任务：
1. **基线**：CPA、scGen、GEARS、CellOT 在 scPerturb 上复跑。
2. **方法创新**（候选）：
   - (a) **基础模型 + 扰动 prompt**：把 Stage 2 的 cell embedding + 扰动 token (基因 KO / 化合物 SMILES via `ChemBERTa`) 拼接，做 conditional generation。
   - (b) **Flow Matching for Cells**：把"对照态 → 扰动态"建成连续 ODE，OT 路径学习 (借鉴 CellOT、scFM)。
   - (c) **组合扰动外推**：双基因 / 三基因 KO 组合，检验加性 vs 上位性 (epistasis)。
3. **可解释性**：用 integrated gradients 反推关键调控基因，跟 OmniPath / Reactome 对比验证。

里程碑：
- [ ] M3.1：在 GEARS benchmark 上达到或超越原文。
- [ ] M3.2：在 Replogle genome-wide 子集上做 leave-genes-out 评估。
- [ ] M3.3：组合 KO 上位性预测 case study + 湿实验合作验证 (可选)。

评估：Pearson Δ、Top-K DEG 召回、组合扰动 R²、unseen-cell-type 泛化。

---

### Stage 4：多尺度虚拟细胞原型 (Month 10–18)

**目标**：把数据驱动模型与机理模型、影像模型耦合，形成可"运行"的虚拟细胞 demo。

任务：
1. **机理底座**：在 `cobrapy` 上跑 Human-GEM / iJO1366 (E. coli)，做 FBA 通量预测，作为代谢约束。
2. **信号通路**：用 `tellurium` 加载 BioModels 中 MAPK / NF-κB ODE，做时序响应。
3. **耦合**：
   - 用 Stage 3 模型预测**转录组变化** → 转化为**酶丰度** → 输入 FBA 约束 → 输出代谢通量。
   - 反向用 FBA 通量回写到表达 prior，形成**闭环 (digital twin loop)**。
4. **影像耦合**：用 JUMP-CP + Cell Painting 模型预测形态变化，与转录组扰动对齐 (如 CLIP-style 对比学习)。
5. **空间扩展**：在 Visium / Stereo-seq 数据上，用 `Nicheformer` / `SpatialGlue` 把单细胞模型拓展到组织 niche 层级。

里程碑：
- [ ] M4.1：单一细胞类型 (e.g. K562) 的"omics + 形态 + 代谢"三模态虚拟细胞 demo。
- [ ] M4.2：交互式可视化 (Streamlit / Dash) — 用户输入扰动，输出多模态预测。
- [ ] M4.3：白皮书 + 开源 release `OpenVCell-v0.1`。

评估：交叉模态预测一致性、与已知通路一致性、用户可用性测试。

---

## 6. 创新点与差异化 (Novelty)

1. **统一跨物种 ortholog 词表**：现有 scGPT/Geneformer 都局限单物种或简单合并；我们用图嵌入对齐。
2. **Flow-Matching 扰动模型**：将"细胞状态演化"建成连续 ODE，比 GEARS 离散预测更自然，可做时间外推。
3. **数据驱动 + 机理闭环**：与纯黑箱 FM 不同，强调与 FBA / ODE / 通路图的可微耦合。
4. **多模态对齐**：转录组 + Cell Painting + 空间 niche 的三方对齐，是当前 VC 仍未充分探索的方向。
5. **完全开源、可复现**：所有数据、代码、checkpoint、流水线 MIT/CC-BY，配套 Snakemake one-click。

---

## 7. 评估与基准 (Benchmark)

- **Open Problems in Single-Cell Analysis** — 注释 / 整合 / 去噪 / 轨迹 / 扰动
- **PerturBench** — 扰动响应统一评估
- **scIB** — 批次整合 7 项指标
- **CASCADE / GEARS test split** — 组合 KO
- **湿实验回路** (合作组)：选 5–10 个 top 预测做 CRISPRi / 小分子验证

成功定义：在 ≥ 3 个公开 benchmark 上达到 SOTA 或前 3，且至少 1 个 case study 经湿实验确证。

---

## 8. 风险与对策 (Risk)

| 风险 | 对策 |
|---|---|
| 算力不足 (>1B 模型) | 先做 small/base 版；申请 CZI / 国家超算 / lambda labs 学术额度；用 LoRA 微调代替全量训练 |
| 数据偏差 (人类细胞主导) | 跨物种 + 加权采样 + 报告分布卡 |
| 机理-数据耦合不稳定 | 先做单向 (data → mechanism) 再做闭环；引入 PINN 软约束 |
| 评估泄漏 | 严格按数据集划分 (leave-cell-line/leave-gene-out)；预注册评估脚本 |
| 可解释性弱 | 对比 OmniPath ground truth；与生物学家共审 |
| 工具更新过快 | 用 lockfile + Docker；每季度同步 upstream |

---

## 9. 时间表与人力 (Timeline)

> 假设 1 PI + 2 博士生 + 1 工程师 + 偶发本科 RA

| 月份 | 主线 | 副线 |
|---|---|---|
| M1–M3 | Stage 1 数据底座 | 文献综述、benchmark 调研 |
| M3–M6 | Stage 2 基线复现 | Stage 1 持续迭代 |
| M6–M9 | Stage 2 改进 + Stage 3 基线 | 准备第一篇方法论文 |
| M9–M12 | Stage 3 创新方法 | 投稿 ICML/NeurIPS/Nat Methods |
| M12–M15 | Stage 4 机理耦合 | 第二篇论文 |
| M15–M18 | OpenVCell-v0.1 release + 白皮书 | 社区建设、tutorial |

---

## 10. 交付物 (Deliverables)

1. **代码仓库**：`github.com/<org>/OpenVCell` — 数据流水线 + 模型 + 评估。
2. **数据集**：`vc-corpus-v0`、`vc-perturb-v0` (HuggingFace Datasets)。
3. **预训练模型**：scGPT-improved、Perturb-FlowMatcher (HuggingFace Hub)。
4. **论文**：≥ 2 篇方法论文 + 1 篇资源/系统论文。
5. **白皮书 + 网站**：`openvcell.org`，含交互 demo。
6. **教程**：Jupyter notebooks，配 Open Problems 风格的 reproducible workflow。

---

## 11. 立刻可执行的 Next Steps (Week 1–2)

1. 创建 GitHub repo 与 monorepo 结构 (`/data`, `/models`, `/eval`, `/notebooks`, `/docs`)。
2. 用 `cellxgene-census` 拉取 100k cells 子集，跑通 scanpy + scvi-tools pipeline。
3. 在 1×A100 / 4090 上用 scGPT 官方代码复现一个 small 模型，记录基线指标。
4. 建立 W&B 项目 + DVC remote。
5. 列一份"每周文献会"清单：CZI VC、Arc Evo2、scFoundation、CellPLM、Nicheformer、Flow Matching 系列。

---

## 参考文献 (精选)

- Karr et al., *A Whole-Cell Computational Model Predicts Phenotype from Genotype*, **Cell** 2012.
- Theodoris et al., *Transfer learning enables predictions in network biology*, **Nature** 2023 (Geneformer).
- Cui et al., *scGPT: toward building a foundation model for single-cell multi-omics*, **Nat Methods** 2024.
- Rosen et al., *Universal Cell Embeddings*, bioRxiv 2023.
- Roohani et al., *Predicting transcriptional outcomes of novel multi-gene perturbations with GEARS*, **Nat Biotech** 2023.
- Lotfollahi et al., *Predicting cellular responses to complex perturbations in high-throughput screens (CPA)*, **Mol Syst Biol** 2023.
- Bunne et al., *Learning single-cell perturbation responses using neural optimal transport (CellOT)*, **Nat Methods** 2023.
- Replogle et al., *Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq*, **Cell** 2022.
- Chan Zuckerberg Initiative, *Virtual Cells Initiative* white paper, 2024.
- Arc Institute, *Evo / Evo-2: DNA Foundation Models*, 2024.

---

*Last updated: 2026-05-10*
