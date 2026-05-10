# Virtual Cell（虚拟细胞）科研计划

**面向：** 具有 AI/计算背景、需要补足生物学知识的研究者
**周期：** 3–5 年（博士级深度）
**版本：** v1.0 · 2026-05
**编制目的：** 为"AI × 细胞生物学"交叉学科建立一个全面、系统、可执行的长期研究路线图

---

## 0. 摘要（Executive Summary）

Virtual Cell（AIVC, AI Virtual Cell）的最终目标是构建一个**可在硅内（in silico）预测细胞在任意扰动下行为**的多模态、多尺度、可机制解释的计算模型。它被广泛视为继 AlphaFold 之后生命科学的下一个"登月级"问题，被 Arc Institute、Chan Zuckerberg Initiative (CZI)、NVIDIA、Genentech、Stanford、Broad 等机构列为核心方向。

本计划以 3–5 年为跨度，分为五个阶段：(1) 学科奠基与文献体系建设；(2) 数据/方法/基准全景掌握；(3) 单点突破（选定一个子方向做出可发表工作）；(4) 系统性贡献（多模态融合或机制可解释性）；(5) 凝练学位论文与下一步生涯路径。

预期最终产出：3–5 篇高水平论文（含至少 1 篇顶刊/顶会）、1 套开源代码与基准、1 部博士学位论文、若干领域影响力建设（开源贡献、Workshop、综述）。

---

## 1. 研究背景与科学问题

### 1.1 什么是 Virtual Cell

> "A computational model that can predict the behavior of any cell, in any state, under any perturbation."（Bunne, Roohani, Theis, Karaletsos 等于 2024 *Cell* 综述中给出的定义）

它是对细胞这一**复杂自适应系统**的可计算化建模，需要同时刻画：
- **分子层**：DNA、RNA、蛋白、代谢物、修饰
- **结构层**：染色质三维结构、细胞器、膜系统
- **状态层**：细胞类型、细胞周期、分化轨迹
- **群体层**：组织、微环境、空间互作
- **动力学**：扰动响应、信号通路、时间演化

### 1.2 为什么是现在

四个汇流的趋势：
1. **数据爆发**：单细胞测序累计已超 10 亿细胞规模（CellxGene、HCA、Tahoe-100M），Perturb-seq 数据从 100K 跃升至 100M 量级。
2. **AI 范式迁移**：Transformer / Diffusion / SSM（如 StripedHyena）证明可在生物序列与组学数据上做基础模型。
3. **结构生物学突破**：AlphaFold2/3、ESMFold、RoseTTAFold All-Atom 把蛋白结构问题"打包"成可调用模块。
4. **资金与组织化推动**：CZI 的 "AI Virtual Cell" 倡议、Arc Institute 的 Virtual Cell Initiative、NIH Bridge2AI、欧盟 LifeTime Initiative。

### 1.3 核心科学问题

**总问题**：能否构建一个**多模态、可机制解释、可扰动预测**的细胞计算模型？

可拆解为四个 **Grand Challenges**：
- **Q1 表示**：细胞的"通用嵌入空间"应当如何定义？是否存在类似自然语言中"语义"的细胞语义？
- **Q2 预测**：给定基因/化学/环境扰动，能否在未见过的细胞类型上做零样本（zero-shot）泛化？
- **Q3 因果**：模型学到的是统计关联还是因果机制？如何用干预数据验证因果？
- **Q4 多尺度**：如何把序列（DNA/RNA/蛋白）→ 结构 → 单细胞状态 → 组织行为统一在一个框架内？

### 1.4 价值与影响

- **基础科学**：理解细胞身份、命运决定、可塑性的最小充分机制。
- **药物发现**：靶点发现、化合物-细胞响应预测、毒性预测、临床前替代实验。
- **精准医学**：患者特异的疾病机制建模，个体化治疗反应预测。
- **合成生物学**：理性设计基因回路、细胞工厂、CAR-T 等细胞疗法。

---

## 2. 现状与关键参考工作（2023–2026）

### 2.1 单细胞基础模型（scFM）

| 模型 | 机构 | 规模 | 主要能力 | 备注 |
|---|---|---|---|---|
| Geneformer | Broad/Harvard | ~30M cells | 基因排序+masked LM | 早期代表 |
| scGPT | Toronto/CZI | 33M cells | 多任务 generative | 应用最广 |
| scFoundation | 清华/水木 | 50M cells | 连续表达建模 | 中国团队 |
| UCE | Stanford | 36M cells | 跨物种、跨实验 | Universal Cell Embedding |
| scBERT, scTab, Nicheformer | … | 多 | 各有侧重 | 持续涌现 |
| **STATE** | Arc Institute (2025) | 167M obs + 100M perturb cells | 扰动-响应专用 | "状态嵌入 + 状态转移"双模块 |
| TranscriptFormer | CZI (2025) | 跨物种 | 跨物种泛化 | 与 scGenePT 配套 |

### 2.2 序列基础模型（Genomic FM）

- **Evo / Evo 2**（Arc + NVIDIA, 2024–2025）：DNA 基础模型，Evo 2 含 40B 参数，1Mb 上下文，9T 核苷酸训练，覆盖三域生命之 100K+ 物种；可零样本预测变异致病性、设计合成基因组；架构基于 StripedHyena 2（SSM）。
- **HyenaDNA、Nucleotide Transformer、Caduceus**：长上下文 DNA 模型路线。
- **ESM-3 / ESMFold、AlphaFold 2/3、RoseTTAFold All-Atom**：蛋白结构与多模态生成。

### 2.3 扰动预测与基准

- **GEARS / CPA / scGen / chemCPA**：早期扰动响应模型。
- **PerturBench, scPerturb, PerturbBench**：扰动数据基准库。
- **Virtual Cell Challenge 2025**（Arc Institute, 6 月发布于 *Cell*；终轮 5,000+ 注册者、114 国家、1,200+ 队伍）：以 H1 hESC 上 300 个基因扰动 + 30 万细胞为测试集，10 万美元奖金，对标 CASP。
- **关键负面发现**（Ahlmann-Eltze et al., *Nature Methods* 2025；Zedzierska et al. 2025）：5 个 scFM 在扰动预测上**未能稳定胜过线性回归与"均值基线"**——这是当下最重要的"清醒提醒"，也是新方法的设计起点。

### 2.4 空间与多模态

- **Spatia**（2025）：图像形态 + 转录组的 cross-attention 融合，多尺度 cell→niche→tissue。
- **SToFM**（2025）：基于 88M 细胞、~2,000 切片的空间转录组语料 SToCorpus-88M。
- **STAMP**（*Cell*, 2025）：在 Xenium / CosMx / MERSCOPE / PhenoCycler 上做高通量单细胞多模态成像。
- **Nicheformer**：53M 空间细胞，组织微环境建模。
- **scDiffusion-X**：跨模态 diffusion 生成。

### 2.5 全细胞模拟（Whole-Cell Simulation）

- 经典代表：Karr 2012 *Mycoplasma genitalium*、JCVI-Syn3A 最小细胞、E-Cell、Virtual Cell (UConn) 等基于 ODE/PDE/SSA 的机制模型。
- 2023 年 Stevens et al. 公布 1.14 亿粒子 Martini 最小细胞模型；2025 年 VTX 提供实时可视化。
- **方向**：把"机制驱动 + 数据驱动"耦合，是 2027–2030 年的关键议题。

### 2.6 数据资源（必须熟悉的"核心数据集"）

- CellxGene Discover（CZI）、Human Cell Atlas、Tabula Sapiens / Muris
- Tahoe-100M（Tahoe + Arc + Biohub, 2025）：迄今最大扰动数据集
- Arc Virtual Cell Atlas、scBaseCount
- Replogle Perturb-seq、Adamson、Norman、Frangieh 等经典扰动集
- ENCODE、Roadmap Epigenomics、4D Nucleome
- HuBMAP、SpatialDB（空间组学）
- DepMap、LINCS L1000、JUMP-Cell Painting（药物-细胞响应）

### 2.7 关键综述（必读 10 篇起点）

1. Bunne, Roohani, Rosen, Gupta, Karaletsos, … Theis (2024). *How to build the virtual cell with AI.* **Cell**. — 学科宣言。
   - Cell 全文：[cell.com/cell/fulltext/S0092-8674(24)01332-1](https://www.cell.com/cell/fulltext/S0092-8674(24)01332-1)
   - arXiv 预印本：[arxiv.org/abs/2409.11654](https://arxiv.org/abs/2409.11654)

2. Theofanis Karaletsos et al. (2024). CZI AI Virtual Cell white paper.
   - CZI Virtual Cell Models 平台：[virtualcellmodels.cziscience.com](https://virtualcellmodels.cziscience.com/)
   - 关联论文（同为宣言文件）：[arxiv.org/abs/2409.11654](https://arxiv.org/abs/2409.11654)

3. Heumos et al. (2023). *Best practices for single-cell analysis across modalities.* **Nat Rev Genet**.
   - Nature Reviews Genetics：[nature.com/articles/s41576-023-00586-w](https://www.nature.com/articles/s41576-023-00586-w)
   - 配套在线书：[sc-best-practices.org](https://www.sc-best-practices.org/)

4. Lopez et al. (2018). *Deep generative modeling for single-cell transcriptomics.* **Nat Methods**. — scVI 原始论文。
   - Nature Methods：[nature.com/articles/s41592-018-0229-2](https://www.nature.com/articles/s41592-018-0229-2)

5. Marx (2024). *Structural biology in the age of AI.* **Nat Methods**.
   - Nature Methods：[nature.com/articles/s41592-023-02123-3](https://www.nature.com/articles/s41592-023-02123-3)

6. Ahlmann-Eltze et al. (2025). *Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines.* **Nature Methods**.
   - Nature Methods：[nature.com/articles/s41592-025-02772-6](https://www.nature.com/articles/s41592-025-02772-6)

7. Roohani et al. (2025). *Predicting cellular responses to perturbation across diverse contexts with STATE.* bioRxiv / NeurIPS 2025.
   - bioRxiv：[biorxiv.org/content/10.1101/2025.06.26.661135v1](https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1)

8. *Virtual Cell Challenge: Toward a Turing test for the virtual cell* (2025). **Cell**.
   - Cell 全文：[cell.com/cell/fulltext/S0092-8674(25)00675-0](https://www.cell.com/cell/fulltext/S0092-8674(25)00675-0)
   - PDF：[cell.com/cell/pdf/S0092-8674(25)00675-0.pdf](https://www.cell.com/cell/pdf/S0092-8674(25)00675-0.pdf)

9. Brixi, Hie et al. (2025). *Genome modeling and design across all domains of life with Evo 2.* bioRxiv → Nature.
   - bioRxiv：[biorxiv.org/content/10.1101/2025.02.18.638918v1](https://www.biorxiv.org/content/10.1101/2025.02.18.638918v1)

10. *Virtual Cells: From Conceptual Frameworks to Biomedical Applications* (2025). arXiv 2509.18220.
    - arXiv：[arxiv.org/abs/2509.18220](https://arxiv.org/abs/2509.18220)

---

## 3. 学科知识体系（针对 AI 背景的"补生物"路线）

由于研究者具备 AI/计算背景，知识缺口主要在**分子细胞生物学、遗传学、系统生物学、实验技术**。建议在第 1 年用 30–40% 时间打通以下"双柱"。

### 3.1 必修知识柱（约 12 个月）

**Pillar A · 分子与细胞生物学基础**
- 教材：Alberts *Molecular Biology of the Cell*（精读 1–5、12–18、21–22 章）；Lodish *Molecular Cell Biology*。
- 课程：MIT 7.06 / 7.016（OCW）、Harvard EdX *Cell Biology: Mitochondria*；Coursera *Genomic Data Science Specialization*。
- 关键概念清单：中心法则、转录调控、染色质修饰、信号通路（MAPK/PI3K/Wnt/TGF-β）、细胞周期、细胞凋亡/自噬、干细胞与分化、肿瘤十大特征（Hallmarks of Cancer）。

**Pillar B · 基因组学 / 系统生物学 / 实验方法**
- 教材：*Bioinformatics and Functional Genomics* (Pevsner)；*An Introduction to Systems Biology* (Alon)。
- 实验方法理解（不必动手，但要理解原理与噪声特征）：bulk/scRNA-seq、ATAC-seq、ChIP-seq、Hi-C、CUT&RUN、MERFISH/Xenium、流式、CRISPR(i/a) Perturb-seq、CITE-seq。
- 推荐读物：*Single Cell Best Practices* (Heumos et al., 在线书)。

**Pillar C · AI 方向深化（在已有基础上）**
- Transformer 长上下文（Hyena, Mamba/SSM, RWKV）
- Diffusion / Flow Matching 在生物数据上的用法
- Graph Neural Network（用于 GRN、PPI、组织图）
- Geometric DL（蛋白结构、SE(3) 等变性）
- Causal ML / Do-calculus / Invariant Risk Minimization
- Probabilistic Programming（Pyro/NumPyro）与变分推断

### 3.2 工程与工具链（持续进行）

- **生信生态**：Python 端 `scanpy`, `anndata`, `scvi-tools`, `cellrank`, `squidpy`, `decoupler`；R 端 `Seurat`, `Bioconductor`。
- **基础模型生态**：HuggingFace、`scgpt`, `geneformer`, `scfoundation`, `evo`（Arc 官方仓库）, NVIDIA `BioNeMo`。
- **HPC / GPU**：分布式训练（DeepSpeed, FSDP）、混合精度、梯度检查点；单节点 8×H100 是当前主流配置。
- **数据工程**：Zarr、TileDB-SOMA（CZI 标准）、Parquet/Arrow，TB-级数据流式训练。
- **复现性**：Nextflow/Snakemake、DVC、MLflow、W&B。

### 3.3 学习节奏建议

| 月份 | 任务 |
|---|---|
| M1–2 | Alberts 1–5 章 + scanpy tutorial + Bunne 2024 综述精读 |
| M3–4 | Perturb-seq 数据复现（Replogle 2022），跑通 GEARS / scGPT |
| M5–6 | Evo 2 / STATE 论文精读 + 复现小型版本 |
| M7–9 | 选定子方向，提交一个 workshop 论文 |
| M10–12 | 第 1 年总结报告 + 开题答辩 |

---

## 4. 研究路线图（3–5 年）

### 4.1 总体技术路线

```
       ┌─────────────────────────────────────────────────────┐
       │   AI Virtual Cell  (5 yr Goal)                      │
       │   多模态 / 多尺度 / 可扰动 / 可解释 / 可验证          │
       └─────────────────────────────────────────────────────┘
                           ▲
        ┌─────────┬────────┴────────┬──────────┐
   表示学习      扰动预测         多模态融合    机制可解释性
  (Pillar 1)    (Pillar 2)       (Pillar 3)    (Pillar 4)
        │            │                 │              │
        └────────────┴────────┬────────┴──────────────┘
                              │
                  统一基准、数据、评测、闭环实验
                       (Pillar 5: Benchmarking)
```

### 4.2 五年阶段划分

#### Year 1：奠基（Foundation）
- 完成知识体系学习（§3）。
- 完成一次完整的"端到端"小项目：例如复现 STATE 或 scGPT，并在 Replogle 数据集上做小幅度改进。
- 选定**主攻子方向**（建议 §4.3 的 P1 或 P2）。
- 产出：1 篇 workshop 论文（NeurIPS LMRL / ICML CompBio / ICLR MLDD）、1 份开题报告。

#### Year 2：单点突破（Depth）
- 在选定子方向上提出第 1 个原创方法。
- 与湿实验合作者（建议从导师网络或 CZI/Arc 公开数据计划获得）建立合作。
- 产出：1 篇会议或期刊文章（如 NeurIPS / Genome Biology / Cell Systems）。

#### Year 3：广度拓展（Breadth）
- 引入第 2 个模态（如空间转录组、图像、蛋白结构）。
- 参加 Virtual Cell Challenge（年度）并争取 Top-10。
- 发起或加入开源基准与社区。
- 产出：1 篇高水平期刊（Nature Methods / Nature Communications / Cell Systems）。

#### Year 4：系统化（Synthesis）
- 把前期方法整合为统一框架；撰写综述。
- 推动一次"湿干闭环"实验：模型预测 → 实验验证 → 模型反馈。
- 产出：1 篇综述（Nature Reviews 子刊）、1 篇主结果（顶刊投稿）。

#### Year 5：收官与跃迁（Defense & Transition）
- 完成博士论文。
- 释放数据集 / 模型 / 软件包，建立长期影响力。
- 学术或产业 next step（博后 / 创业 / 公司研究院）。

### 4.3 备选子方向（建议三选一作为博士主线）

#### P1. 因果可解释的扰动预测（高推荐）
- **动机**：2025 年的"基线击败基础模型"事件揭示当前模型大多在学关联，而非因果。
- **关键技术**：do-calculus、interventional representation learning、CausalVAE、可识别 ICA、不变性预测（IRM/REx）、反事实评估。
- **数据**：Replogle K562/RPE-1、Norman、CRISPRi/a Perturb-seq、Tahoe-100M。
- **里程碑**：在 Virtual Cell Challenge 评测上稳定击败"均值/线性"基线 + 提供因果可视化。

#### P2. 多模态多尺度统一表示（中-高推荐）
- **动机**：DNA → 表达 → 形态 → 空间是天然层级，目前缺乏单一框架。
- **关键技术**：跨模态对比学习、Perceiver/Mixture-of-Experts、SE(3) 等变 Transformer、长上下文 SSM（继承 Evo 2 思路）。
- **数据**：CellxGene + ENCODE + JUMP-Cell Painting + Spatial 数据集。
- **里程碑**：发布一个开源多模态 cell foundation model。

#### P3. 全细胞动力学的"机制 + 数据"混合模型（高难度）
- **动机**：传统 whole-cell 模型在小生物体（Mycoplasma、Syn3A）已实现，但缺乏数据驱动的可扩展性。
- **关键技术**：Neural ODE / PINN、SBML 与神经网络混合、可微 Gillespie。
- **风险**：高、可能 5 年内难以登顶刊；适合作为副线或博士后议题。

#### P4. 临床转化导向的患者特异虚拟细胞（应用驱动）
- **动机**：肿瘤、自免、神经退行性疾病的临床数据丰富。
- **关键技术**：迁移学习、领域适应、患者级嵌入、不确定性量化。
- **数据**：TCGA / GTEx / single-cell tumor atlases。
- **风险**：与临床合作是关键瓶颈。

> **个人建议**：以 **P1 为主线 + P2 作为方法工具箱**。P1 与 2025 年最热的"评测危机"高度相关，容易做出影响力；P2 提供基础模型的工程能力沉淀。

---

## 5. 拟开展的具体研究任务（Year 2–4 细化）

### 5.1 Task A · 因果不变性扰动预测器（CIPP）
**问题**：现有 scFM 在"未见过的扰动 × 未见过的细胞类型"组合上崩溃。
**思路**：
1. 引入 invariant causal representation：把"细胞类型"作为环境变量，强制模型学习跨环境不变的扰动效应。
2. 利用 Tahoe-100M 多细胞类型扰动数据做训练。
3. 评测：Virtual Cell Challenge + 内部 leave-one-celltype-out。
**预期产出**：1 篇 NeurIPS 主会 / Nature Methods。

### 5.2 Task B · 模态对齐的多尺度细胞编码器（MultiCell-Encoder）
**思路**：以 Perceiver IO 为骨干，对 (DNA window, expression vector, image patches, spatial coords) 四模态做 token 化，使用对比学习 + masked prediction 联合预训练。
**评测**：在 cell type annotation, batch correction, perturbation prediction, image–transcriptome retrieval 四类任务上做"瑞士军刀"评测。

### 5.3 Task C · 闭环湿干实验（Active Learning Loop）
**思路**：与合作湿实验组建立小规模 Perturb-seq 平台（或购买商业服务），用主动学习选择信息量最大的扰动，验证模型预测，反馈再训练。这是把 AIVC 落到"科学方法论"层面的关键一步，也是申请大型基金时极有说服力的论据。

### 5.4 Task D · 评测与基准重构（Benchmark Refoundation）
**动机**：当前 benchmark（Adamson、Norman 等）扰动方差小、易被均值基线打败。
**思路**：构建一个新的 evaluation suite（rank-based metrics, perturbation-specific variance, distribution shift splits），并将其开源、推动社区采纳。
**潜在合作**：Open Problems in Single-Cell Analysis、CZI、Arc。

---

## 6. 资源、协作与基础设施

### 6.1 计算资源
- 起步配置：1×8×A100/H100 节点用于中等规模实验。
- 大规模训练：申请国家超算（如 Frontier、LUMI）、企业云（NVIDIA Inception、AWS Open Data Sponsorship、Microsoft AI for Health）。
- 备选：BioNeMo + Modal / RunPod 弹性 GPU。

### 6.2 数据访问
- 公开数据：CellxGene、Arc Virtual Cell Atlas、Tahoe-100M、HCA、ENCODE。
- 受控访问：dbGaP（人体基因组）、UK Biobank、All of Us（如做临床方向）。

### 6.3 合作网络
- **湿实验合作**：本校生物系/医学院 PI；CZI Single-Cell Biology Network；Arc 公开数据生成计划。
- **AI 方法合作**：参加 NeurIPS LMRL、ICML CompBio、Cold Spring Harbor BoG、RECOMB。
- **工业合作**：Genentech、Recursion、Insitro、Isomorphic Labs、BioMap、Owkin、Cradle、Latent Labs。

### 6.4 资金渠道（择适用申请）
- NIH F31/F99、NSF GRFP（美国）；MRC/Wellcome（英国）；ERC Starting/StG（欧洲）；NSFC、青年基金（中国）；MSCA（欧盟）。
- 私募：CZI Ben Barres、Arc Beyond/Ignite、Schmidt AI in Science Postdoctoral Fellowship。

---

## 7. 评测与成功标准（OKR）

| 维度 | KR（关键结果） | 度量 |
|---|---|---|
| 学术影响 | ≥3 篇一作论文，含 ≥1 篇顶刊 | 引用、影响因子 |
| 方法贡献 | ≥1 个开源模型/基准被 ≥3 个外部团队使用 | GitHub stars, citations |
| 社区参与 | Virtual Cell Challenge Top-10 至少 1 次 | Leaderboard |
| 科学验证 | 至少 1 个模型预测被湿实验验证 | 实验记录、合作论文 |
| 个人成长 | 完成博士论文，进入下一阶段（博后/PI/公司研究院） | 学位、Offer |

---

## 8. 风险识别与应对

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 基础模型方向"泡沫"破裂，方法被证伪 | 中 | 高 | 选 P1（因果方向）天然抗周期；积累工程能力可迁移 |
| 计算资源不足 | 中 | 高 | 早申请云额度；与产业合作；做小模型证概念 |
| 数据访问受限 | 中 | 中 | 优先用公开数据；同行复制实验 |
| 缺乏湿实验合作 | 高 | 中 | 把"评测/基准"作为退路；参与 Open Problems |
| 学科切换学习曲线陡 | 中 | 中 | Y1 用足时间补生物；找生物背景 buddy |
| 个人 burnout | 中 | 高 | 半年节奏复盘；保持运动与睡眠 |

---

## 9. 时间表（Gantt 简化版）

```
Y1  ████ 知识补全 ████ 复现 STATE/scGPT ████ Workshop 论文
Y2       ████ Task A 方法 ██ 投稿 ████ Workshop+主会 ████
Y3              ████ Task B 多模态 ████ 顶刊投稿 ████ VCC 参赛
Y4                     ████ Task C 闭环实验 ████ 综述 ████
Y5                            ████ 学位论文 ████ 答辩+择业
```

---

## 10. 第 1 年立即可执行清单（Next 12 Months Action Items）

1. **Month 1**：建立文献库（Zotero / Notion），完成 §2.7 十篇综述与原始论文精读笔记。
2. **Month 1–2**：注册 CellxGene、HuggingFace、Arc Virtual Cell Atlas；本地搭好 `scanpy + scvi-tools + scgpt + evo` 环境。
3. **Month 2**：跑通 Replogle 2022 K562 Perturb-seq 数据的 EDA + GEARS baseline。
4. **Month 3**：复现 scGPT 在 perturbation 任务上的官方 notebook，并在数据上加一个简单线性基线，亲自验证 Ahlmann-Eltze 2025 的发现。
5. **Month 4–5**：精读并复现 STATE（部分）；动手实现 State Embedding 模块。
6. **Month 6**：参加 Virtual Cell Challenge 2026（如开放）作为练手。
7. **Month 7–9**：写一篇 workshop 论文，主题建议："Revisiting baselines for perturbation prediction with X."
8. **Month 10–12**：完成开题报告，明确 Y2 主线（建议 P1）。

---

## 11. 参考资料与链接

### 关键论文与项目页面
- Bunne, Roohani, Karaletsos, Theis et al. *How to build the virtual cell with AI*. **Cell** (2024).
- Ahlmann-Eltze et al. *Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines*. **Nature Methods** (2025). https://www.nature.com/articles/s41592-025-02772-6
- Roohani et al. *STATE: Predicting cellular responses to perturbation across diverse contexts*. bioRxiv (2025).
- Brixi, Hie et al. *Genome modeling and design across all domains of life with Evo 2*. https://www.biorxiv.org/content/10.1101/2025.02.18.638918v1
- *Virtual Cell Challenge: Toward a Turing test for the virtual cell*. **Cell** (2025). https://www.cell.com/cell/fulltext/S0092-8674(25)00675-0
- *Virtual Cells: From Conceptual Frameworks to Biomedical Applications* (2025). https://arxiv.org/html/2509.18220v1
- *AI-driven virtual cell models in preclinical research* (2025). **npj Digital Medicine**. https://www.nature.com/articles/s41746-025-02198-6

### 机构与门户
- Arc Institute Virtual Cell Initiative — https://arcinstitute.org/virtual-cell-initiative
- Arc Institute Evo 2 — https://arcinstitute.org/tools/evo
- Virtual Cell Challenge — https://virtualcellchallenge.org/
- CZI Virtual Cell Models 平台 — https://virtualcellmodels.cziscience.com/
- CellxGene Discover — https://cellxgene.cziscience.com/
- Open Problems in Single-Cell Analysis — https://openproblems.bio/

### 教材与课程
- Alberts et al., *Molecular Biology of the Cell*, 7th ed.
- Heumos et al., *Single Cell Best Practices* — https://www.sc-best-practices.org/
- MIT OCW 7.06 / 7.016；Coursera *Genomic Data Science Specialization*

---

## 附录 A · 术语表（节选）

- **scRNA-seq**：单细胞转录组测序。
- **Perturb-seq**：把 CRISPR 扰动与 scRNA-seq 结合，用以测量基因敲低/敲除对全转录组的影响。
- **Foundation Model（FM）**：在大规模未标注数据上预训练、可迁移到多种下游任务的大模型。
- **Zero-shot generalization**：对训练分布外的输入直接预测能力。
- **Causal inference**：从观测/干预数据中识别因果关系的统计与计算方法。
- **Whole-cell model**：试图刻画细胞内所有已知分子过程的机制模型。

## 附录 B · 月度复盘模板

> 每月最后一个周五，用 30 分钟回答以下五题：
> 1. 本月最重要的 1 个进展是？
> 2. 本月最大的认知更新是？
> 3. 哪 1 个假设被否证？
> 4. 下月 1 个最关键的实验/写作任务是？
> 5. 我的精力/动力评分（1–10）？是否需要调整节奏？

---

*本计划是活文档（living document），建议每季度复盘一次、每年大版本更新一次。*
