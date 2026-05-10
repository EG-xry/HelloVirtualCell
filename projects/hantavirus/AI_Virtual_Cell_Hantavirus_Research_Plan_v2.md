# AI Virtual Cell × Hantavirus 科研计划 v2
## 整合单细胞多组学 + 分子动力学的病毒感染虚拟细胞

> 将虚拟细胞技术与分子动力学模拟深度融合，从原子-分子到细胞多尺度研究汉坦病毒感染机制

*v2 相较 v1 新增：分子动力学（MD）模拟模块（Stage 0）、结构-序列-功能多尺度整合、AI × MD 融合预测管道*

---

## 0. 摘要 (TL;DR)

本计划在 v1（AI Virtual Cell × Hantavirus）基础上，引入**分子动力学（MD）模拟**作为原子尺度基础层，构建从**原子 → 蛋白 → 细胞 → 器官**的多尺度虚拟感染细胞（Multi-scale Virtual Infected Cell, MS-VIC）平台。

**v2 核心新增**：
1. 汉坦病毒结构蛋白（Gn/Gc 糖蛋白、N 核蛋白、RdRp L 蛋白）的 MD 模拟与自由能计算
2. 病毒-受体结合（Gc/β3 integrin）的结合自由能预测
3. AI 辅助 MD 力场（Neural Network Potential, NNP）加速模拟
4. 将 MD 产生的结构信息反馈至单细胞预测模型（结构-表达联合建模）
5. 基于 MD 的抗病毒候选化合物结合位点分析（Structure-based Drug Design）

**多尺度闭环**：
```
MD（原子尺度）→ 结构变化预测 → 蛋白互作网络 → 细胞转录响应 → 细胞命运
         ↑                                                          ↓
    AI NNP 加速                                         湿实验验证 (BSL-3)
```

---

## 1. 研究背景（MD 扩展部分）

### 1.1 为什么需要分子动力学

v1 计划主要从**细胞尺度**建模汉坦病毒感染：单细胞转录组、扰动预测、细胞命运。  
然而，许多关键科学问题需要**原子/分子尺度**的理解：

| 科学问题 | 尺度 | 为何 MD 是必要工具 |
|----------|------|-------------------|
| Gc 如何识别 β3 integrin 并触发膜融合？ | 原子 | 识别界面残基、计算结合亲和力 |
| N 蛋白与 RNA 的动态相互作用如何影响复制？ | 分子 | RNA 结合构象变化 |
| 病毒糖蛋白的构象变化如何触发宿主受体激活？ | 蛋白 | 构象动力学、隐匿结合口袋 |
| 哪些小分子可稳定/破坏 Gc trimer？ | 药物 | 结合自由能、选择性 |
| 病毒进化突变如何影响蛋白稳定性？ | 进化 | ΔΔG 突变效应预测 |

### 1.2 汉坦病毒结构蛋白现状

| 蛋白 | 已解析结构 | 分辨率 | PDB/EMDB |
|------|-----------|--------|----------|
| Gc glycoprotein (ANDV) | 晶体结构 | 1.8 Å | 5J5N |
| Gc post-fusion (HTNV) | Cryo-EM | 3.2 Å | 7Y8Y |
| N nucleoprotein | 晶体结构 | 2.0 Å | 2K9H |
| L RdRp (HTNV) | Cryo-EM | 3.8 Å | 7Y8Z |
| Gn/Gc heterotrimer | 部分已解析 | — | 待更新 |

### 1.3 AI × MD 研究机遇

近年 AI 在 MD 领域的突破使本计划可行：
- **AlphaFold2/3**：提供无结构汉坦病毒蛋白的高精度预测结构
- **OpenMM + ML force fields**：AMOEBA、ANI-2x 等神经网络势能面
- **MDAnalysis + MDTraj**：高效轨迹分析
- **Graph Neural Network + MD**：将 MD 轨迹特征融入图网络预测

---

## 2. 研究框架（v2 多尺度版）

```
┌────────────────────────────────────────────────────────────────────┐
│  Stage 5: 多尺度整合 + 湿实验验证 + 平台发布                       │
│  MD 预测 ←→ 细胞预测 → 候选药物/靶点 → BSL-3 验证                  │
└────────────────────────▲───────────────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────────────┐
│  Stage 4: 抗病毒干预虚拟筛选（SBDD + 细胞水平预测）                │
│  基于 MD 的结构药物设计 + VIC 模型联合筛选                          │
└────────────────────────▲───────────────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────────────┐
│  Stage 3: Virtual Infected Cell (VIC) 模型                         │
│  扰动响应预测 + 免疫逃逸 + 细胞命运（继承 v1 Stage 3）              │
└────────────────────────▲───────────────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────────────┐
│  Stage 2: 病毒-宿主单细胞基础模型（继承 v1 Stage 2）               │
│  引入 MD 结构特征作为辅助输入                                        │
└────────────────────────▲───────────────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────────────┐
│  Stage 1: 多组学知识图谱 + MD 结构数据整合（继承 v1 Stage 1）       │
└────────────────────────▲───────────────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────────────┐
│  Stage 0 [NEW]: 分子动力学模拟基础层                                │
│  汉坦病毒结构蛋白 MD + AI NNP + 结合自由能 + 隐匿口袋              │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stage 0（新增）：分子动力学模拟基础层 (Month 1–8)

### 3.0 总体目标

构建汉坦病毒关键结构蛋白的 MD 模拟管线，产生：
- 蛋白构象集合（用于口袋发现）
- 结合自由能数据（用于药物预筛选）
- 动力学特征向量（用于整合至细胞尺度模型）

### 3.1 结构准备与系统搭建

#### 3.1.1 结构来源

```python
# 优先级：晶体结构 > AlphaFold3 > Rosetta 同源建模
structures = {
    "Gc_ANDV":   "5J5N",          # 已解析晶体
    "Gc_HTNV":   "7Y8Y",          # Cryo-EM
    "N_protein":  "2K9H",          # 已解析
    "L_RdRp":    "7Y8Z",           # Cryo-EM
    "Gn":        "AlphaFold3",     # 无结构，用 AF3 预测
    "Gc_receptor_complex": "build" # Gc + β3 integrin 复合物
}
```

#### 3.1.2 系统准备工具链

| 工具 | 用途 | 说明 |
|------|------|------|
| `AmberTools24` + `tleap` | AMBER ff19SB 蛋白力场拓扑 | 标准蛋白 MD |
| `CHARMM-GUI` | 膜蛋白系统搭建（Gc 糖蛋白跨膜部分） | 磷脂双分子层 |
| `OpenMM 8.x` | GPU 加速 MD 模拟引擎 | Python API |
| `GROMACS 2024` | 大规模并行 MD（集群） | CPU 集群 |
| `Glycan Builder` | 糖蛋白糖链建模（Gc 有 N-glycan） | 关键！ |
| `PropKa` + `HTMD` | pKa 预测、His 质子化 | 系统准备 |

#### 3.1.3 模拟体系参数

```yaml
# 标准 MD 参数
force_field: "ff19SB"         # 蛋白
water_model: "TIP3P"          # 溶剂
ion: "NaCl 150 mM"            # 生理盐浓度
box_padding: 12 Å
cutoff: 10 Å
timestep: 2 fs
production_time: 500 ns       # 每个体系
replicas: 3                    # 三副本
temperature: 310 K             # 体温
```

### 3.2 核心 MD 模拟任务

#### 3.2.1 Gc 糖蛋白构象动力学

**科学目标**：揭示 Gc 从预融合态（pre-fusion）到后融合态（post-fusion）的构象变化途径。

```
任务清单：
□ 建立 Gc pre-fusion trimer (ANDV, 5J5N) MD 体系
□ 建立 Gc post-fusion conformation (HTNV, 7Y8Y) MD 体系
□ 500 ns 常规 MD（×3 副本）
□ Enhanced sampling: Replica Exchange MD (REMD) 揭示稀有构象
□ 识别融合loop（fusion loop）的动态行为
□ 计算 β-hairpin fusion loop 的 RMSD/RMSF
□ 识别构象变化过程中的隐匿口袋（cryptic pockets）
```

**关键指标**：
- Gc trimer RMSD < 3 Å（稳定性验证）
- fusion loop RMSF 分布
- 隐匿口袋体积（> 300 Å³ 视为有成药性）

#### 3.2.2 Gc × β3 Integrin 结合界面模拟

**科学目标**：确定 Gc 与宿主受体 β3 integrin 的结合模式、关键接触残基和结合亲和力。

```
任务清单：
□ 构建 Gc-β3 integrin 复合物（RGD 或 RGD-like motif 对接起始构型）
□ 分子对接（AutoDock Vina / HADDOCK）获取初始复合物
□ 200 ns MD 稳定化
□ MM-GBSA 计算结合自由能（ΔG_bind）
□ 逐残基能量分解（per-residue energy decomposition）
□ 突变扫描（alanine scanning）验证关键残基
□ 与已知 β3 integrin 配体竞争结合口袋分析
```

**关键指标**：
- ΔG_bind（目标：< -10 kcal/mol）
- Hot spot 残基（贡献 > 2 kcal/mol）
- 与文献报道 SNV Gc 结合数据对比

#### 3.2.3 N 核蛋白与 RNA 的相互作用

**科学目标**：N 蛋白 RNA 结合环（RNA-binding loop）如何封装病毒 RNA，与 L RdRp 的协同机制。

```
任务清单：
□ N 蛋白单体/三聚体 MD 模拟（apo 形式，300 ns）
□ N + RNA（8-nt ssRNA）复合物构建与 MD
□ RNA 解离自由能：Umbrella Sampling
□ N 三聚体界面稳定性分析
□ N-L 蛋白接触界面预测（AlphaFold-Multimer + MD 验证）
```

#### 3.2.4 L 蛋白（RdRp）催化机制

**科学目标**：L 蛋白催化口袋的动力学，寻找新型抑制剂结合位点。

```
任务清单：
□ L RdRp apo MD 模拟（200 ns，HTNV 7Y8Z）
□ L + NTP（底物）复合物 MD
□ 催化Mg²⁺ 离子动力学分析
□ 与已知 RdRp 抑制剂（Favipiravir, Ribavirin）的结合模拟
□ FPocket 隐匿口袋扫描
□ QM/MM 模拟（ONIOM）验证催化机制（20 Å 活性位点 QM 区）
```

### 3.3 AI × MD 加速（Neural Network Potential）

#### 3.3.1 NNP 力场选型与应用

| NNP 力场 | 适用范围 | 精度 | 速度提升 |
|----------|----------|------|----------|
| ANI-2x | 有机小分子 | DFT 级 | 10³×（vs QM） |
| MACE-MP-0 | 通用材料/生物分子 | CCSD(T) 级 | 10²× |
| ESM-MD (Meta) | 蛋白 MD | Coarse-grained | 10³× |
| OpenMM-ML | AMBER + NNP 混合 | 可定制 | 10-50× |

**本计划策略**：
- 小分子（候选药物）：ANI-2x 进行量子精度自由能计算
- 蛋白大体系（Gc trimer + 膜）：经典 MD + NNP 精修关键区域
- 蛋白折叠稳定性：MACE-MP-0 验证 AlphaFold 预测构象

#### 3.3.2 MD 数据驱动的 AI 模型

```python
# 将 MD 轨迹特征输入至细胞尺度模型
class StructuralFeatureExtractor:
    """从 MD 轨迹提取动力学特征，作为细胞模型的辅助输入"""
    
    def extract_features(self, trajectory):
        features = {
            "per_residue_rmsf":   self._compute_rmsf(trajectory),
            "contact_map_variance": self._contact_variance(trajectory),
            "pocket_volume":       self._pocket_dynamics(trajectory),
            "binding_energy":     self._mmgbsa(trajectory),
            "coevolution_signal": self._dca_coupling(trajectory)
        }
        return features  # shape: (n_residues, n_features)
```

### 3.4 隐匿口袋发现与 SBDD

**目标**：基于 MD 轨迹（而非单一静态结构）发现汉坦病毒蛋白的成药口袋。

#### 工具链

| 工具 | 用途 |
|------|------|
| `fpocket` / `DoGSiteScorer` | 静态口袋检测 |
| `MDpocket` | 轨迹口袋时序分析 |
| `POVME3` | 口袋体积定量 |
| `RDKit + AutoDock-GPU` | 高通量虚拟筛选 |
| `Glide (Schrödinger)` | 精确对接（可选） |
| `FEP+` | 绝对自由能微扰（关键候选） |

#### 流程

```
MD 轨迹（500 ns）
    ↓ MDpocket
口袋时序分布（出现频率 + 体积）
    ↓ 筛选（频率>30%，体积>300 Å³）
成药口袋列表
    ↓ 分子对接（Enamine/DrugBank 库，~5M 化合物）
初筛 Top-1000
    ↓ MM-GBSA 重打分
Top-50 候选
    ↓ NNP/MD 验证结合稳定性
Top-10 → 湿实验验证
```

### 3.5 Stage 0 里程碑

- [ ] **M0.1**（Month 2）：完成 Gc, N, L 蛋白 MD 体系搭建，跑通第一批 100 ns 轨迹
- [ ] **M0.2**（Month 4）：Gc × β3 integrin 复合物 ΔG_bind 计算完成，与文献对比
- [ ] **M0.3**（Month 6）：隐匿口袋发现报告（Gc trimer + L RdRp），口袋列表发布
- [ ] **M0.4**（Month 7）：完成基于 MD 口袋的初级虚拟筛选（Top-50 候选化合物）
- [ ] **M0.5**（Month 8）：MD 动力学特征提取器集成至 Stage 2 细胞模型（特征 API）

**评估**：MD 稳定性（RMSD 收敛）、ΔG_bind 实验对比（ΔΔG < 1.5 kcal/mol）、口袋成药性评分（Fdruggability > 0.5）

---

## 4. Stage 1（v2 更新）：多组学知识图谱 + 结构数据整合

在 v1 Stage 1 基础上，新增：

### 4.1 结构-序列-功能三位一体知识图谱

```python
# 知识图谱节点类型（v2 扩展）
node_types = {
    "viral_protein":    ["Gc", "Gn", "N", "L"],
    "host_protein":     ["β3-integrin", "STAT1", "IRF3", ...],
    "protein_domain":   ["fusion_loop", "RNA_binding_loop", ...],  # 新增
    "binding_site":     ["cryptic_pocket_1", "active_site_L", ...],  # 新增
    "residue":          ["Gc_K256", "N_R48", ...],                   # 新增
    "small_molecule":   ["Ribavirin", "candidate_001", ...],
    "gene":             [...],
    "pathway":          [...]
}
```

### 4.2 MD 与 omics 联合数据库

| 数据类型 | 来源 | 格式 | 用途 |
|----------|------|------|------|
| MD 轨迹摘要 | Stage 0 计算 | HDF5 | 动力学特征 |
| 已知 SAR 数据 | ChEMBL/BindingDB | CSV | 模型验证 |
| 已知突变效应（ΔΔG） | ProThermDB | JSON | 突变预测验证 |
| Cryo-EM 密度图 | EMDB | MRC | 结构验证 |

---

## 5. Stage 2（v2 更新）：结构感知的单细胞基础模型

在 v1 Stage 2 基础上，新增**结构辅助输入**：

### 5.1 结构特征融合架构

```
┌─────────────────────────────────────────────────────────┐
│                   结构-感知 scGPT-HV                     │
│                                                          │
│  scRNA-seq token ──→ Transformer ──┐                    │
│                                    ├──→ 联合嵌入 → 输出  │
│  MD 结构特征 ──→ Structure Encoder─┘                    │
│  (RMSF, ΔG_bind, 口袋体积)                              │
└─────────────────────────────────────────────────────────┘
```

**新增输入特征**（每个病毒蛋白）：
- `rmsf_vector`：蛋白柔性分布（512 dim）
- `binding_energy`：与宿主受体 ΔG_bind（scalar）
- `pocket_volume`：主要口袋体积时序特征（64 dim）
- `contact_change`：感染前后关键接触变化（binary vector）

### 5.2 结构驱动的感染状态预测

- 假设：Gc 的构象状态（pre-/post-fusion）直接预测细胞感染进程
- 验证：MD 模拟的构象集合 → 映射至细胞感染状态轨迹

---

## 6. Stage 3（v2 不变，沿用 v1）

Virtual Infected Cell (VIC) 扰动响应预测，见 v1 Stage 3 详细计划。

---

## 7. Stage 4（v2 更新）：SBDD + 细胞水平联合筛选

### 7.1 双层筛选策略

```
候选化合物库（DrugBank + Enamine, ~5M 化合物）
         │
         ▼ Layer 1: 结构层筛选（Stage 0 MD 口袋）
    AutoDock-GPU 高通量对接（~5M → 10K）
         │
         ▼ MM-GBSA 精筛（10K → 200）
    Top-200 候选（结合亲和力 + 选择性）
         │
         ▼ Layer 2: 细胞层筛选（VIC 模型）
    CPA/GEARS 预测药物处理后宿主转录响应
         │
         ▼ 双层 Score：ΔG_bind × Cell_Efficacy_Score
    Top-20 联合评分候选
         │
         ▼ FEP/MD 精确自由能验证
    Top-10 → BSL-3 湿实验
```

### 7.2 药物优先级评分

```python
def compute_priority_score(candidate):
    score = (
        0.4 * normalize(candidate.binding_energy)   # 结合亲和力
      + 0.3 * normalize(candidate.cell_efficacy)    # VIC 预测抗病毒效果
      + 0.2 * normalize(candidate.selectivity)      # 脱靶毒性（反选）
      + 0.1 * normalize(candidate.druggability)     # ADMET 性质
    )
    return score
```

---

## 8. 工具链汇总（v2 新增部分）

### 8.1 MD 模拟工具

```bash
# 力场与模拟引擎
OpenMM 8.x              # GPU 加速 MD（Python API）
GROMACS 2024            # 集群并行 MD
AMBER 24                # 蛋白 + 小分子力场

# 系统准备
CHARMM-GUI              # 膜蛋白体系
AmberTools24 (tleap)    # 拓扑生成
Glycan Builder (CHARMM) # 糖链建模

# AI 力场
MACE-MP-0               # 通用神经网络势能
ANI-2x (torchani)       # 有机小分子 NNP
OpenMM-ML               # AMBER + NNP 混合

# 轨迹分析
MDAnalysis              # 轨迹分析 (Python)
MDTraj                  # 快速轨迹处理
PyContact               # 接触分析

# 口袋发现
fpocket / MDpocket      # 静态/动态口袋
DoGSiteScorer           # 成药性评估
POVME3                  # 口袋体积

# 分子对接与自由能
AutoDock-GPU            # 高通量虚拟筛选
HADDOCK 3.0             # 蛋白-蛋白对接
FEP+ (Schrödinger)      # 精确 FEP（可选）
Pymbar                  # 自由能估算 (MBAR)

# 可视化
VMD                     # MD 可视化
PyMol                   # 结构展示
NGLview                 # Jupyter 内嵌
```

### 8.2 新增 Python 包

```toml
# requirements_md.txt
openmm>=8.1.0
openmmforcefields
mdanalysis>=2.7.0
mdtraj>=1.9.9
mace-torch            # MACE NNP
torchani              # ANI-2x
fpocket               # 口袋发现（系统安装）
pytraj                # AMBER 轨迹
parmed                # 参数文件处理
rdkit-pypi            # 化学信息学
vina                  # AutoDock Vina Python API
openff-toolkit        # Open Force Field
```

---

## 9. 计算资源规划

| 任务 | 硬件需求 | 估计机时 | 备注 |
|------|----------|----------|------|
| 单蛋白 500 ns MD | 4× A100 GPU | ~200 GPU·h | 3 副本 |
| Gc trimer + 膜 500 ns | 8× A100 GPU | ~800 GPU·h | 大体系 |
| REMD (16 replicas) | 16× A100 GPU | ~500 GPU·h | 增强采样 |
| 高通量对接 (5M 化合物) | 4× A100 GPU | ~100 GPU·h | AutoDock-GPU |
| MM-GBSA (200 复合物) | 4× A100 GPU | ~50 GPU·h | — |
| NNP 精修 | 2× A100 GPU | ~100 GPU·h | 候选小分子 |
| **总计（Stage 0）** | A100 集群 | **~1800 GPU·h** | ≈ $1800（$1/GPU·h 估算） |

**经济方案**：
- 优先使用 HPC 集群（学校/国家中心）
- 免费资源：XSEDE/ACCESS（美国）、国家超算（中国）、Google TPU Research Cloud
- 付费：AWS/Azure 按需 GPU（估算总成本 $3000–8000）

---

## 10. 时间表（v2 完整版）

> 假设 1 PI + 1 MD 博后 + 1 scRNA 博后 + 1 工程师

| 阶段 | 时间 | 主要负责 | 交付 |
|------|------|----------|------|
| **Stage 0** MD 基础 | M1–M8 | MD 博后 | Gc/N/L MD 轨迹、ΔG_bind、隐匿口袋列表 |
| **Stage 1** 知识图谱 | M1–M4 | 工程师 + scRNA 博后 | HV-KG-v0.1，含结构节点 |
| **Stage 2** 基础模型 | M4–M12 | scRNA 博后 | scGPT-HV v2（含结构特征） |
| **Stage 3** VIC 模型 | M8–M18 | scRNA 博后 + 工程师 | VIC-HV v1，跨毒株验证 |
| **Stage 4** 联合筛选 | M12–M24 | MD 博后 + scRNA 博后 | Top-20 候选，双层筛选报告 |
| **Stage 5** 验证 + 平台 | M20–M30 | 全组 | 湿实验 ≥5 候选，Web 平台，论文 |

**关键节点**：
- Month 4：MD 初步轨迹 + 知识图谱 → Stage 1 中期报告
- Month 8：MD 口袋报告 + 基础模型预训练完成
- Month 14：VIC 模型 + SBDD 初步筛选 → 预印本 v1
- Month 20：双层筛选 Top-20 → 提交湿实验合作申请
- Month 30：全流程交付 + 顶刊论文投稿

---

## 11. 创新点（v2 新增）

| 创新点 | 描述 | 现有工作差距 |
|--------|------|-------------|
| **多尺度 VIC** | 原子→蛋白→细胞闭环建模 | 现有研究不跨尺度 |
| **AI NNP × Hantavirus** | 首次将 NNP 用于汉坦病毒蛋白 MD | 无先例 |
| **动态口袋 → 细胞响应** | MD 构象集合驱动细胞状态预测 | 缺少此类整合 |
| **双层筛选管线** | SBDD 结构层 + VIC 细胞层联合评分 | 现有筛选仅选其一 |
| **结构-感知 scGPT-HV** | 结构动力学特征输入细胞 AI 模型 | scGPT 无结构输入 |

---

## 12. 风险与对策（v2 新增部分）

| 风险 | 对策 |
|------|------|
| MD 计算资源不足 | 优先模拟高优先级体系（Gc, N）；使用粗粒化 MD（MARTINI）加速 |
| 现有 Gc 结构分辨率限制（3.2 Å Cryo-EM） | AlphaFold3 补全缺失环，MD 平衡化后验证稳定性 |
| NNP 在新体系精度未知 | 用小体系 QM 计算验证 NNP；报告不确定性 |
| 结构-细胞特征整合困难 | 先验证特征对细胞模型的提升，若无提升降级为辅助验证 |
| 糖蛋白糖链建模复杂 | 先模拟无糖链版本；用 GlycoFold 评估糖链影响 |

---

## 13. 交付物（v2 新增）

在 v1 交付物基础上，新增：

7. **MD 数据集**：`HV-MD-Atlas`（Gc/N/L 蛋白 500 ns 轨迹摘要）发布于 Figshare/Zenodo
8. **口袋数据库**：`HV-PocketDB`（动态口袋 + 成药性评分）
9. **双层筛选管线**：开源代码（SBDD + VIC 联合评分）
10. **MD 论文**：≥ 1 篇 MD/结构生物信息学期刊论文
11. **结构-感知模型**：`scGPT-HV-struct`（HuggingFace Hub）

---

## 14. Next Steps (Week 1–4，v2 版)

**MD 方向**（MD 博后）：
1. 下载 PDB: 5J5N (Gc_ANDV)，运行 AmberTools + CHARMM-GUI 准备体系
2. 配置 OpenMM + CUDA 环境，跑 10 ns 试验性模拟验证稳定性
3. 申请 HPC 计算时间（预估 1000 GPU·h）
4. 文献调研：汉坦病毒 MD 已有工作（检索"Hantavirus Gn/Gc molecular dynamics"）

**scRNA 方向**（继承 v1）：
5. 同 v1 Week 1–2 任务

**整合**：
6. 定义 MD 特征向量格式（JSON Schema），为 Stage 2 整合预定义接口
7. 建立 MD + scRNA 联合分析 Jupyter notebook 模板

---

## 参考文献（v2 新增）

**分子动力学与汉坦病毒结构**：
- Pensiero et al. (2023). "Hantavirus Gc glycoprotein structure and membrane fusion." *PNAS*.
- Li et al. (2022). "Cryo-EM structure of HTNV L protein." *Nature Commun*.
- Devignot et al. (2021). "Hantavirus N protein and RNA interactions." *J Virol*.

**AI × MD**：
- Batatia et al. (2023). "MACE: Higher order equivariant message passing neural networks." *NeurIPS*.
- Smith et al. (2021). "Approaching coupled cluster accuracy with a general-purpose neural network potential through transfer learning." *Nat Commun*.
- Hollingsworth & Bhattacharyya (2023). "Cryptic binding sites from MD simulations." *Drug Discovery Today*.

**SBDD 与自由能**：
- Abel et al. (2017). "Advancing Drug Discovery through Enhanced Free Energy Calculations." *Acc Chem Res*.
- Wang et al. (2015). "Accurate and reliable prediction of relative ligand binding potency in prospective drug discovery." *J Am Chem Soc*.

**多尺度建模**：
- Schlick et al. (2021). "Multiscale molecular dynamics." *Chem Rev*.
- Noé et al. (2020). "Machine learning for molecular simulation." *Ann Rev Phys Chem*.

---

*Version: 2.0 | Last updated: 2026-05-10 | 相较 v1 新增：Stage 0 MD 基础层，MD 工具链，结构-感知 scGPT-HV，双层筛选管线*
