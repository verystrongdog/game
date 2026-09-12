# 外部数据来源登记

> **登记范围**：`data/connectivity/` 下从公开数据集下载、**不由本仓生成**的原始数据。
> 本表是这些文件的 provenance 权威记录——`data/manifest.json` 的 `origin: external`
> 属性以此为依据。
>
> **为何单列一表**：这批文件是"派生数据的上游"。它们的**下载 URL、版本、许可**
> 无法从本仓内容推导，只能登记。缺了它，P4c 数据契约的 `provenance` 字段就是空话，
> 也无法回答 owner 方案 §9.3 的 `provenance/license` 要求。

---

## 目录

1. [一、登记项](#一登记项)
2. [二、已知缺口](#二已知缺口)
3. [三、维护规则](#三维护规则)

---

## 一、登记项

### 1.1 `data/connectivity/yeo2011/` — Yeo 7 网络分区

| 项 | 值 |
|---|---|
| 来源数据集 | Yeo BT, et al. (2011). *The organization of the human cerebral cortex estimated by intrinsic functional connectivity.* J Neurophysiol 106(3):1125-1165. [doi:10.1152/jn.00338.2011](https://doi.org/10.1152/jn.00338.2011) |
| 获取方式 | [nilearn](https://nilearn.github.io/0.14.0/modules/generated/nilearn.datasets.fetch_atlas_yeo_2011.html) `fetch_atlas_yeo_2011()` 的下载缓存目录（子目录 `README.md` 为 nilearn 自动写入） |
| 许可 | FreeSurfer 数据许可（Yeo 2011 的 MIT/哈佛发布条款）；**发布前需复核** |
| 本仓文件 | `Yeo2011_7Networks_MNI152_2mm.nii.gz` · `lh./rh.Yeo2011_7Networks_N1000.annot` · `*.split_components.txt` · `dk_yeo7_mapping.json` |
| 用途 | 皮层 7 网络覆盖的原始底图；`dk_yeo7_mapping.json` 是 DK↔Yeo 映射的落库形式 |
| 消费方 | 无受控代码直接读取（映射结论已落库） |
| 设计依据 | [决策树 §D8](../decisions/03-topics-2026-08-01-to-08-11.md) 三层功能网络覆盖框架 |

### 1.2 `data/connectivity/hansen2024/` — 脑干-皮层功能连接

| 项 | 值 |
|---|---|
| 来源数据集 | Hansen JY, et al. (2024). *Integrating brainstem and cortical functional architectures.* Nature Neuroscience 27(12):2500-2511. [doi:10.1038/s41593-024-01787-0](https://doi.org/10.1038/s41593-024-01787-0) |
| 获取方式 | 数据集仓库 [netneurolab/hansen_brainstemfc](https://github.com/netneurolab/hansen_brainstemfc)（亦见 [netneurotools.datasets.fetch_hansen_brainstemfc](https://netneurolab.github.io/netneurotools/generated/netneurotools.datasets.fetch_hansen_brainstemfc.html)） |
| 许可 | **未登记**——见 [§二](#二已知缺口) |
| 本仓文件 | `brainstemfc_Schaefer400.npy` · `mesulam_schaefer400.csv` · `region_info_Schaefer400.csv` · `subcortex_coords.csv` · `voneconomo_schaefer400.csv` · `brainstem_coords.txt` · `brainstem_coords_labels.txt` |
| 用途 | 脑干核团（10/10 覆盖）的 MNI 坐标与皮层 FC 定性分层 |
| 消费方 | ⚠️ **无受控代码读取**——见 [§二](#二已知缺口) |
| 设计依据 | [决策树 §D8](../decisions/03-topics-2026-08-01-to-08-11.md)；脑干核团坐标的落库形式是 `data/brain_regions.json` |

### 1.3 `data/connectivity/cab-np/` — 皮层下网络分配（CAB-NP v1.1）

| 项 | 值 |
|---|---|
| 来源数据集 | Ji JL, et al. (2019). *Mapping the human brain's cortical-subcortical functional network organization.* NeuroImage 185:35-57. [doi:10.1016/j.neuroimage.2018.10.006](https://doi.org/10.1016/j.neuroimage.2018.10.006) |
| 获取方式 | Cole Neurocognition Lab 发布页（CAB-NP v1.1） |
| 许可 | **未登记**——见 [§二](#二已知缺口) |
| 本仓文件 | `CAB-NP_netassignments_LR.dlabel.nii` · `CAB-NP_v1.1_Labels-ReorderedbyNetworks.xlsx` · `CortexSubcortex_ColeAnticevic_NetPartition_..._LR_ReorderedByNetworks.txt` |
| 用途 | 皮层下 8/8 结构覆盖的网络分配 |
| 消费方 | ⚠️ **无受控代码读取**——见 [§二](#二已知缺口) |
| 设计依据 | [决策树 §D8](../decisions/03-topics-2026-08-01-to-08-11.md) |

### 1.4 `data/connectivity/` 根下 — ENIGMA HCP 结构连接

| 项 | 值 |
|---|---|
| 来源数据集 | Lariviere S, et al. (2021). *The ENIGMA Toolbox.* Nature Methods 18:698-700. [doi:10.1038/s41592-021-01186-6](https://doi.org/10.1038/s41592-021-01186-6) |
| 获取方式 | ENIGMA Toolbox（工具说明与文件清单见 [enigma_dk_connectivity.md](enigma_dk_connectivity.md)、[sources.md](sources.md) §1） |
| 许可 | 见 ENIGMA Toolbox 条款；**发布前需复核** |
| 本仓文件 | `enigma_sc_ctx_matrix.npy` · `enigma_sc_ctx_labels.npy` · `enigma_sc_sctx_matrix.npy` · `enigma_sc_sctx_labels.npy` · `enigma_sc_summary.json` · `enigma_all_connections.csv` · `enigma_top200_connections.csv` |
| 用途 | 皮层-皮层 68×68 与皮层下-皮层 14×68 结构连接矩阵 → 链路调制上限 |
| 消费方 | [`code/tools/gen_modulation_ceiling.py`](../../code/tools/gen_modulation_ceiling.py)（4 个矩阵 + `enigma_sc_summary.json`） |
| 设计依据 | [sources.md](sources.md) §1 |

### 1.5 `data/connectivity/kroell14_networks.json` — Kroell 14 网络

| 项 | 值 |
|---|---|
| 来源数据集 | Kroell JP, Eickhoff SB, et al. (2024). *Definition of 14 canonical functional networks from meta-analytic coactivation data.* Research Centre Juelich (INM-1) |
| 获取方式 | [Juelich 记录](https://juser.fz-juelich.de/record/1006698/files/Manuscript_Kroell.pdf)；归属说明见 [sources.md](sources.md) §3 |
| 许可 | 见原文；**发布前需复核** |
| 用途 | 主导网络分类（14 网络）的集合定义 |
| 消费方 | [`code/tools/build_contexts_tripartite.py`](../../code/tools/build_contexts_tripartite.py) |

### 1.6 `data/connectivity/abagen/` — ⚠️ 未受控

该目录被 [.gitignore](../../.gitignore) 排除（`data/connectivity/abagen/`），
**不在版本控制内**，故不进入 `data/manifest.json` 的盘点范围。
abagen 基因表达数据当前无任何 runtime 或生成链消费者。
若将来需要，须先决定入库策略（数据体量 vs. 可复现性），再登记到本表。

---

## 二、已知缺口

> 按 [WORKFLOW.md §五](../../WORKFLOW.md)：「本阶段产生的新问题不得事后倒填为『已知债务』」。
> 以下两项是 **P4c 数据契约建立过程中发现并如实登记的缺口**，不是"已经解决了"。

### 缺口 1 — `hansen2024/` 的 5 个数据文件**零消费者**

实测（2026-09-12，`git grep` 全受控文件）：

| 文件 | 受控代码引用数 |
|---|---|
| `brainstemfc_Schaefer400.npy` | 0 |
| `mesulam_schaefer400.csv` | 0 |
| `region_info_Schaefer400.csv` | 0 |
| `subcortex_coords.csv` | 0 |
| `voneconomo_schaefer400.csv` | 0 |

而 [`gen_modulation_ceiling.py`](../../code/tools/gen_modulation_ceiling.py) 的
`load_hansen_brainstem()` 头部自述：

> 「由于我们没有原始 FC 矩阵，使用基于 Hansen 社区分类的估计值。」

即：**数据文件在仓库里，生成器却不读它，改用硬编码估计值**。
后果是「Hansen 2024」作为参数来源的标注与代码实际行为不一致。

**处置**：这是一项需要裁定的事项，不由数据契约阶段单方面决定——
要么改为真读 `brainstemfc_Schaefer400.npy`，要么在生成器与设计文档中
把"估计值"标注为估计值。两个选项都改设计/代码行为，超出「只动结构与引用」的范围。

### 缺口 2 — 三项外部数据的**许可未登记**

`hansen2024/`、`cab-np/`、`kroell14_networks.json` 的许可条款未在本仓记录。
当前无发布行为，故不阻塞；**进入发布路径前必须补齐**（owner 方案 §12.3
「许可证不清的资产进入发布路径」列为需固定处理的问题）。

---

## 三、维护规则

1. 新增外部数据目录时，**先登记本表再入库**——`origin: external` 的判据是本表
2. 每个外部目录必须写明：来源 URL、版本、许可、本仓文件清单、消费方、设计依据
3. 许可未知时显式写「未登记」并计入 [§二](#二已知缺口)，不得留空
4. 数据文件增加时同步本表清单；`data/manifest.json` 的属性更新用
   `code/tools/build_data_manifest.py --refresh`

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [数据层说明](../README.md), [sources.md](sources.md), [ENIGMA 结构连接说明](enigma_dk_connectivity.md), [数据契约](../../data/manifest.json)*
