# AI Virtual Cell × Hantavirus 科研计划

> 将虚拟细胞技术应用于汉坦病毒感染机制研究与抗病毒药物发现

---

## 0. 摘要 (TL;DR)

本计划将 AI Virtual Cell（AI 虚拟细胞）技术应用于汉坦病毒（Hantavirus）研究，构建一个可预测汉坦病毒感染宿主细胞响应、预测抗病毒药物效果的计算平台。汉坦病毒作为一类重要的致死性人畜共患病原体，其感染机制尚未完全阐明，且缺乏有效疫苗和特异性治疗药物。通过整合单细胞多组学基础模型（scGPT/Geneformer）、扰动响应预测（GEARS/CellOT）、以及病毒-宿主相互作用组数据，本研究旨在：

1. 建立汉坦病毒感染的单细胞多组学知识图谱
2. 构建能预测病毒蛋白表达、宿主免疫响应、细胞命运转变的虚拟细胞模型
3. 实现抗病毒药物/基因扰动的 in silico 筛选
4. 与湿实验团队协作验证关键预测

核心创新：将虚拟细胞从"通用细胞模型"聚焦到"汉坦病毒感染细胞"这一特定病理场景，形成垂直领域的 AI 虚拟病原感染细胞（Virtual Infected Cell, VIC）。

---

## 1. 研究背景与意义

### 1.1 汉坦病毒概述

**汉坦病毒（Hantavirus）** 是布尼亚病毒科（Bunyavirales）的负链 RNA 病毒，分为两大临床综合征：

| 类型 | 代表毒株 | 地理分布 | 主要病理 |
|------|----------|----------|----------|
| 肾综合征出血热 (HFRS) | Hantaan (HTNV), Seoul (SEOV), Puumala (PUUV) | 欧亚大陆为主 | 肾小管损伤、出血热 |
| 汉坦病毒肺综合征 (HPS/HANT) | Sin Nombre (SNV), Andes (ANDV) | 美洲为主 | 肺毛细血管渗漏、呼吸窘迫 |

**关键科学问题**：
- 病毒如何劫持宿主细胞转录机器？
- 宿主先天免疫应答如何被调控/逃逸？
- 不同毒株为何引起不同的临床表型？
- 如何预测宿主的疾病进展？

### 1.2 为什么用 Virtual Cell 研究汉坦病毒

| 传统方法 | Virtual Cell 优势 |
|----------|-------------------|
| BSL-3 实验室要求 | In silico 安全无风险 |
| 病毒培养困难（无满意动物模型） | 可模拟多种宿主细胞类型 |
| 扰动实验成本高、周期长 | 快速预测、筛选假设 |
| 单细胞数据分散 | 整合 + 知识迁移 |
| 机制解释困难 | 可解释性 + 通路分析 |

### 1.3 核心科学问题

1. **感染动态建模**：汉坦病毒 L/M/S 节段编码的病毒蛋白如何重塑宿主细胞状态？
2. **免疫逃逸机制**：病毒如何抑制/激活 IFN、NF-κB、炎症小体等通路？
3. **细胞命运预测**：给定病毒扰动，细胞走向凋亡/坏死/存活/持续感染的命运概率？
4. **跨毒株比较**：不同汉坦病毒（HTNV vs SNV）为何引起不同器官损伤？
5. **药物靶点发现**：哪些宿主因子是最佳干预节点？

---

## 2. 总体研究框架

```
        ┌──────────────────────────────────────────────────────┐
        │   Stage 4: 汉坦病毒虚拟感染细胞 (Virtual Infected    │
        │   Cell, VIC) — 预测药物/基因干预效果 + 湿实验验证    │
        └──────────────────────▲──────────────────────────────┘
                               │
        ┌──────────────────────┴──────────────────────────────┐
        │   Stage 3: 扰动响应预测                              │
        │   病毒蛋白表达 → 宿主转录组变化 → 细胞命运           │
        └──────────────────────▲──────────────────────────────┘
                               │
        ┌──────────────────────┴──────────────────────────────┐
        │   Stage 2: 病毒-宿主单细胞基础模型                  │
        │   整合健康 + 感染 scRNA-seq → 细胞嵌入               │
        └──────────────────────▲──────────────────────────────┘
                               │
        ┌──────────────────────┴──────────────────────────────┐
        │   Stage 1: 汉坦病毒多组学知识图谱                    │
        │   整合公开数据集 + 构建病毒-宿主互作网络             │
        └──────────────────────────────────────────────────────┘
```

---

## 3. 数据资源 (Data Sources)

### 3.1 汉坦病毒相关组学数据

| 数据类型 | 数据集 | 规模 | 来源/链接 |
|----------|--------|------|-----------|
| 病毒基因组 | HTNV, SEOV, SNV, ANDV 参考基因组 | 3 segments each | NCBI/GenBank |
| 病毒-宿主蛋白互作 | VirusHostDB, PHI-base, STRING | ~200 相互作用 | virus-host-db.jp |
| 感染细胞 scRNA-seq | 已有公开数据搜索 | 待整合 | GEO/ArrayExpress |
| 宿主通路注释 | KEGG, Reactome, OmniPath | — | KEGG REST API |
| 抗病毒药物靶点 | DrugBank, ChEMBL, Connectivity Map | >10K compounds | Broad LINCS |

### 3.2 关键文献与数据集

```
# 汉坦病毒细胞感染模型相关研究
1. LaRonde et al. (2021). "Hijacking the hub: Hantavirus infection mechanisms." 
   Advances in Virus Research (综述)

2. Ma et al. (2022). "Single-cell transcriptomics reveals immune cell landscape 
   in HFRS patients." J Immunol (如果有)

3.暂无系统性汉坦病毒scRNA-seq数据 → 需要协作或自主产生
   → 这是一个研究机会点！
```

### 3.3 通用单细胞基础模型训练数据

| 数据集 | 规模 | 用途 |
|--------|------|------|
| CELLxGENE Census | >1 亿 cells | 基础模型预训练 |
| HCA Atlas | 多器官 | 跨组织泛化 |
| scPerturb | 100+ 扰动数据集 | 扰动预测微调 |
| Replogle 2022 | 250 万 CRISPR 扰动 | 组合扰动 |

---

## 4. 开源工具链 (Toolchain)

**数据处理**
- `scanpy`, `anndata` — 单细胞数据处理
- `muon` — 多组学整合
- `scvi-tools` — 批次校正、变分推断

**病毒-宿主分析**
- `squidpy` — 空间转录组（如果有组织数据）
- `decoupler-py` — 通路活性推断
- `pyComplex` — 蛋白互作网络分析

**基础模型 / 表征**
- `scGPT` — 单细胞生成式基础模型
- `Geneformer` — 基因上下文建模
- `UCE` — 通用细胞嵌入
- `CellOT` — 最优传输扰动预测

**扰动预测**
- `GEARS` — 组合基因扰动预测
- `CPA` — 药物扰动自编码器
- `scGen` — 空间扰动转移

**病毒建模**
- `Biopython` — 病毒序列分析
- `ETYK` — 病毒-宿主蛋白互作推理
- `cobrapy` — 代谢建模（宿主代谢重编程）

**可视化**
- `scVelo` / `PAGA` — 细胞轨迹
- `CellRank2` — 细胞命运预测
- `Streamlit` — 交互式结果展示

---

## 5. 分阶段研究计划

### Stage 1：汉坦病毒多组学知识图谱构建 (Month 1–4)

**目标**：整合公开数据 + 文献挖掘，构建首个汉坦病毒-宿主细胞知识图谱。

**任务**：

#### 1.1 病毒-宿主蛋白互作网络构建
- 收集已报道的 HTNV/SNV/ANDV 病毒蛋白与宿主因子互作
- 来源：VirusHostDB, PHI-base, STRING, 手动文献挖掘
- 覆盖：G N 蛋白、L 聚合酶、M 糖蛋白 与宿主受体（β3整合素、管家蛋白）、转录因子、免疫因子的互作

#### 1.2 感染细胞转录响应数据库
- 搜索 GEO/ArrayExpress/SRA 获取汉坦病毒感染细胞系的 scRNA-seq/bulk RNA-seq
- 若数据不足：
  - 方案 A：与合作实验室协作产生数据
  - 方案 B：聚焦于 IFN/炎症通路的 bulk RNA-seq 数据，用 Imputation 扩展
- 建立统一的 `AnnData` 格式存储

#### 1.3 宿主通路与基因调控网络
- 整合 Reactome/KEGG 中 IFN 信号、NF-κB、凋亡、细胞周期通路
- 用 `OmniPath` 提取转录因子-target 调控关系
- 构建感染响应的先验网络（Prior Knowledge Network）

#### 1.4 病毒序列与蛋白特征嵌入
- 对 HTNV/SNV/ANDV 三段基因组做 k-mer embedding
- 提取病毒蛋白理化性质（疏水性、跨膜域、信号肽）
- 构建"病毒特征 → 宿主响应"的映射字典

**里程碑**：
- [ ] M1.1：发布 `HV-KG-v0.1`：汉坦病毒-宿主蛋白互作网络（含 ≥150 互作对）
- [ ] M1.2：发布 `HV-Infection-Atlas`：感染细胞转录响应数据库（≥ 5 数据集）
- [ ] M1.3：发布通路调控网络 `HV-PathwayNet`
- [ ] M1.4：技术报告 + GitHub repo + 数据可视化

**评估**：互作对数量、文献覆盖度、通路富集一致性（Fisher exact test）

---

### Stage 2：病毒-宿主单细胞基础模型 (Month 4–10)

**目标**：基于 Stage 1 数据 + 通用单细胞模型，构建能区分"健康 vs 感染"细胞状态的嵌入模型。

**任务**：

#### 2.1 基础模型选型与预训练
- 以 scGPT 或 Geneformer 为基座模型
- 预训练语料：CELLxGENE Census（侧重人内皮细胞、免疫细胞）
- 添加**病毒扰动 token**：为 HTNV/SNV/ANDV 各添加特殊 token

#### 2.2 感染状态分类微调
- 在 `HV-Infection-Atlas` 上做多标签分类：
  - 细胞类型（内皮细胞/巨噬细胞/上皮细胞）
  - 感染状态（对照/感染早期/感染晚期）
  - 响应类型（强 IFN/弱 IFN/凋亡倾向）
- 使用 LoRA 高效微调，保持基座模型泛化能力

#### 2.3 病毒蛋白表达预测模块
- 输入：宿主细胞嵌入 + 病毒基因组片段
- 输出：预测病毒蛋白（N/G/L）在宿主细胞的表达水平
- 方法：Adapter + 病毒序列 encoder（参考 ViralBERT 设计）

#### 2.4 细胞类型特异性分析
- 构建不同宿主细胞类型（内皮细胞 vs 免疫细胞）对汉坦病毒感染的差异化响应模型
- 识别细胞类型特异的病毒易感因子（SUSCEPTIBILITY genes）

**里程碑**：
- [ ] M2.1：感染状态分类器在 `HV-Infection-Atlas` 上达到 AUC ≥ 0.85
- [ ] M2.2：发布 `scGPT-HV`：汉坦病毒专用单细胞模型（HuggingFace）
- [ ] M2.3：细胞类型特异性分析报告，识别 ≥ 20 个差异响应基因
- [ ] M2.4：与已有 bulk RNA-seq 验证一致性（Pearson ≥ 0.6）

**评估**：AUC/F1（分类）、Pearson/MAE（表达预测）、通路富集（GO/KEGG overlap）

---

### Stage 3：扰动响应预测 — 病毒感染虚拟细胞 (Month 8–16)

**目标**：构建能预测"基因/药物扰动 → 汉坦病毒感染响应变化"的生成式模型。

**任务**：

#### 3.1 病毒扰动响应基准模型
- 实现基线方法：CellOT、GEARS、CPA 在汉坦病毒感染数据集上
- 用 leave-virus-strain-out（HTNV → SNV）测试跨毒株泛化
- 评估指标：ΔGene Expression Pearson、Top-K DEG 召回率

#### 3.2 虚拟感染细胞 (Virtual Infected Cell, VIC) 模型
- **核心创新**：将"感染状态"作为一个可操纵的扰动变量
- 输入：`(细胞嵌入, 感染病毒类型, 时间点)`
- 输出：预测的宿主转录组变化（表达矩阵）
- 方法候选：
  - (a) **Conditional Flow Matching**：学习 健康→感染 的向量场
  - (b) **Latent ODE**：时序感染动态建模
  - (c) **Epi-Context Transformer**：上下文感知扰动预测

#### 3.3 免疫逃逸机制预测
- 聚焦 IFN 信号通路：预测病毒蛋白对 IFN 激活/抑制效果
- 预测宿主因子（STAT1/2, IRF3/7, ISG15）的表达变化
- 与已知免疫逃逸机制对比验证

#### 3.4 细胞命运预测
- 用 CellRank2 分析感染进程轨迹
- 预测：感染细胞 → 凋亡 / 坏死性凋亡 / 存活 / 病毒释放 的命运概率
- 识别命运决定的"决策点"基因

#### 3.5 组合扰动预测
- 预测双基因敲除（如 KO IFN 抑制因子 + KO 病毒 N 蛋白）对感染的影响
- 检验加性 vs 上位性（Epistasis）效应

**里程碑**：
- [ ] M3.1：VIC 模型在已知数据集上 ΔExpression Pearson ≥ 0.5
- [ ] M3.2：跨毒株泛化实验（HTNV 训练 → SNV 预测）验证
- [ ] M3.3：IFN 响应预测与实验数据一致率 ≥ 70%
- [ ] M3.4：细胞命运预测与文献报道吻合（≥ 3 案例验证）
- [ ] M3.5：组合扰动预测，Top-10 候选干预点

**评估**：预测-实验相关性、跨毒株泛化、生物学合理性（专家评审）

---

### Stage 4：抗病毒干预虚拟筛选与验证 (Month 14–24)

**目标**：利用 VIC 模型进行 in silico 药物筛选，并与湿实验协作验证。

**任务**：

#### 4.1 药物扰动库构建
- 收集 FDA 批准抗病毒药物靶点库（~300 药物）
- 整合 Connectivity Map (CMap) 表达谱
- 添加宿主靶向药物（而非病毒靶向），绕过病毒耐药性

#### 4.2 In Silico 药物筛选
- 输入：候选药物（如 Ribavirin, Favipiravir, 候选宿主靶向药）
- 预测：用药后宿主转录组变化、对病毒复制的影响、对 IFN 的激活效果
- 筛选策略：
  - **正向**：激活 IFN 通路 + 抑制病毒复制相关基因
  - **负向**：避免过度免疫激活（细胞因子风暴风险）
- 优先级排序：Top-50 候选药物

#### 4.3 基因干预靶点发现
- 预测宿主基因敲除/KD 对病毒复制和细胞存活的影响
- 优先选择"致死率低但抗病毒效果好"的靶点
- 与 CRISPR 筛选数据（如有）对比验证

#### 4.4 湿实验验证（协作）
- 与 BSL-3 合作实验室建立协作关系
- 验证 Top-5 药物预测 + Top-5 基因靶点
- 检测指标：病毒滴度、细胞存活率、IFN 相关基因表达

#### 4.5 跨毒株药物效果预测
- 测试 Top 候选药物对 HTNV、SNV、ANDV 的预测效果差异
- 识别"广谱药物"vs"毒株特异性药物"

**里程碑**：
- [ ] M4.1：发布 Top-50 候选药物列表（附预测依据）
- [ ] M4.2：发布 Top-20 基因干预靶点列表
- [ ] M4.3：完成湿实验验证（≥ 3 候选药物/靶点）
- [ ] M4.4：建立汉坦病毒虚拟药物筛选平台（Web 界面）
- [ ] M4.5：发表论文或预印本

**评估**：湿实验验证成功率、预测相关性、受试专家评价

---

## 6. 创新点与差异化

| 创新点 | 描述 | 现有工作对比 |
|--------|------|--------------|
| **垂直领域虚拟细胞** | 从通用虚拟细胞聚焦到汉坦病毒感染这一垂直场景 | 现有 Virtual Cell Challenge 为通用框架 |
| **病毒-宿主联合建模** | 将病毒基因组作为"扰动"统一编码 | scGPT/GEARS 主要针对宿主基因扰动 |
| **跨毒株泛化** | 模型能跨 HTNV/SNV/ANDV 迁移 | 现有研究多聚焦单一毒株 |
| **免疫逃逸预测** | 系统预测病毒对 IFN/NF-κB 的调控 | 缺乏系统性计算预测 |
| **药物-靶点-表型闭环** | 整合药物筛选、基因干预、湿实验验证 | 多为 dry-only 研究 |

---

## 7. 风险与对策

| 风险 | 对策 |
|------|------|
| 汉坦病毒 scRNA-seq 数据不足 | 优先利用 bulk RNA-seq + Imputation；与实验室协作产生数据 |
| BSL-3 限制导致湿实验验证困难 | 与国内 BSL-3 实验室（如 CDC、军科院）建立合作 |
| 病毒变异快速导致模型过时 | 设计增量学习框架，持续更新模型 |
| 药物预测准确率不足 | 采用保守策略：仅发布高置信度预测；强调辅助而非替代实验 |
| 跨物种（啮齿类-人）泛化 | 使用 ortholog mapping；优先建模人类细胞系 |

---

## 8. 时间表与人力

> 假设 1 PI + 1 博后 + 1 工程师 + 硕士生

| 阶段 | 时间 | 主线任务 | 副线任务 |
|------|------|----------|----------|
| Stage 1 | M1–M4 | 知识图谱构建 | 文献调研、数据搜索 |
| Stage 2 | M4–M10 | 基础模型训练 | Stage 1 迭代 |
| Stage 3 | M8–M16 | VIC 模型开发 | 论文写作 (Stage 1-2) |
| Stage 4 | M14–M24 | 药物筛选 + 湿实验验证 | 论文投稿、平台建设 |

**关键节点**：
- Month 4：Stage 1 交付 + 项目中期报告
- Month 10：Stage 2 交付 + 预印本 v1
- Month 16：Stage 3 交付 + 论文投稿
- Month 24：Stage 4 交付 + 湿实验验证 + 平台开源

---

## 9. 交付物

1. **代码仓库**：`github.com/<org>/Hantavirus-VirtualCell`
2. **数据集**：`HV-KG-v0.1`, `HV-Infection-Atlas` (HuggingFace/Figshare)
3. **预训练模型**：`scGPT-HV`, `VIC-model` (HuggingFace Hub)
4. **论文**：≥ 2 篇（1 篇方法 + 1 篇应用/实验验证）
5. **虚拟筛选平台**：Web 界面，支持药物/基因扰动预测
6. **湿实验验证**：至少 3 个候选药物/靶点通过实验验证

---

## 10. 立刻可执行的 Next Steps (Week 1–2)

1. **文献检索**：系统检索汉坦病毒 scRNA-seq/GEO 数据，记录可用数据集
2. **数据获取**：从 VirusHostDB、STRING 下载病毒-宿主蛋白互作数据
3. **环境搭建**：配置 `scanpy + scvi-tools + scGPT` 环境
4. **知识图谱原型**：用 NetworkX 构建小型病毒-宿主互作网络
5. **合作探索**：联系 BSL-3 实验室，建立湿实验验证合作意向
6. **基线模型**：在 CELLxGENE 上跑通 scGPT 基线，测试感染状态分类可行性

---

## 参考文献

1. LaRonde et al. (2021). "Hijacking the hub: Hantavirus infection mechanisms." *Advances in Virus Research*.
2. Jenson et al. (2023). "Hantavirus entry and pathogenesis." *Viruses*.
3. MacNeil et al. (2022). "Hantavirus pulmonary syndrome." *Clinical Microbiology Reviews*.
4. Klemperer et al. (2021). "Hantavirus replication." *Current Opinion in Virology*.
5. Bunne et al. (2024). "How to build the virtual cell with AI." *Cell*.
6. Cui et al. (2024). "scGPT: toward building a foundation model for single-cell multi-omics." *Nat Methods*.
7. Roohani et al. (2023). "GEARS: predicting transcriptional outcomes of multi-gene perturbations." *Nat Biotech*.
8. Bunne et al. (2023). "CellOT: Learning optimal transport for perturbation response." *Nat Methods*.

---

*Last updated: 2026-05-10*
