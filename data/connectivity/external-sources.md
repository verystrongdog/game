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
| 用途 | 脑干核团（10/10 覆盖）的 MNI 坐标与皮层 FC 定性分层；**数值权威的裁定见 §二 缺口 1（2026-09-13：#132 裁定 C）** |
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
> 以下条目是 **P4c 数据契约建立过程中发现并如实登记的缺口**。

### 缺口 1 — `hansen2024/` 数据文件零消费者 + 数值权威（**2026-09-13 已裁定为 C**）

实测（2026-09-12，`git grep` 全受控文件）：

| 文件 | 受控代码引用数 |
|---|---|
| `brainstemfc_Schaefer400.npy` | 0 |
| `mesulam_schaefer400.csv` | 0 |
| `region_info_Schaefer400.csv` | 0 |
| `subcortex_coords.csv` | 0 |
| `voneconomo_schaefer400.csv` | 0 |

而 [`gen_modulation_ceiling.py`](../../code/tools/gen_modulation_ceiling.py) 当时用硬编码数值
冒充该数据集的结果，来源标注写 `Hansen2024_brainstem` / `Hansen2024:PAG↔M1`。

**已处置（2026-09-12，owner 裁定「把估计值如实标注」）**：

| 位置 | 处置 |
|---|---|
| `gen_modulation_ceiling.py` | `load_hansen_brainstem()` → `load_brainstem_strength_estimates()`；来源标注 `Hansen2024:*` → `brainstem_estimate:*`；归一化基准 `hansen_max` → `brainstem_estimate_max` |
| `gen_modulation_ceiling_v2.py` | `HANSON_COMMUNITY_GAIN`（且为拼写错误）→ `BRAINSTEM_COMMUNITY_GAIN_ESTIMATE`；头部与产出 `_metadata` 如实区分「文献依据」与「本仓估计」 |
| 两个产出 JSON | `data_source` / `_metadata` 标注如实化 + `provenance_note`。**数值一个未动**（836 个数值逐个比对相同） |
| 规范与设计文档 | [链路调制上限参考表-v2.md](../../design/rules/skill-tree/modulation/%E9%93%BE%E8%B7%AF%E8%B0%83%E5%88%B6%E4%B8%8A%E9%99%90%E5%8F%82%E8%80%83%E8%A1%A8-v2.md) 的「文献」列、[design/README.md](../../design/README.md)、[six-dimensions.md](../../design/framework/six-dimensions.md)、19 份 disease-pilot 的 `Hansen fc=…` 全部改为「脑干强度估计」 |
| [Hansen2024 数据留存](../../design/rules/skill-tree/references/Hansen2024_%E8%84%91%E5%B9%B2%E7%9A%AE%E5%B1%82%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7_%E6%95%B0%E6%8D%AE.md) | 明确为**社区划分的权威依据**，并声明本文不覆盖连接强度数值与复合结构 |

**顺带修正一处真实错误**：`中缝正中核` 的社区原标 `YELLOW`，论文 Table 1 列其为
**GREEN**（与 PAG / VTA / 上丘同组）。两处生成器俱已修正，依据见上述留存文档 §五。

#### 裁定（2026-09-13 · [#132](https://github.com/verystrongdog/game/issues/132) · owner）

**结论：选 C —— 部分接入（只做结构校验）；数值权威仍为「本仓脑干强度估计」。**

| 轴 | 从 → 到 |
|---|---|
| 链路调制上限的数值权威（Design） | `UNRESOLVED` → **`ACCEPTED`**——权威 = 本仓估计，这是**被明确接受的设计选择**，不再悬挂 |

**依据（2026-09-13 实测，base `999c973`）**：

1. 5 个数据文件的受控代码引用数**仍全为 0**——「登记了却不读」是真实缺口，不是标注问题
2. 数据集本身可用：`brainstemfc_Schaefer400.npy` **483×483**（Schaefer400 皮质 + 83 脑干/皮质下）· **69 个脑干标签**（含左右与中线）· `region_info_Schaefer400.csv` 484 行带 `structure`/`rsn`/坐标
3. 「836 个数值」核实 = 两个产出 JSON 的 `links` 内数值总数（**320 + 516**）；**真正依赖脑干强度的只有** v1 **18 条** / v2 **9 条**（其余链路重算后数值相同）
4. **A 的前置不是"读文件"**：① 项目 16 个核团条目（含 `VTA-NAcc`、`反射环路·*` 等复合条目）↔ 数据集 69 标签——**`小脑皮层` 无对应标签**；② 400 个皮质分区 → 项目脑区需**聚合规则**；③ FC 是相关系数（−0.004…0.916），项目要的是 **1.0–1.5 的增益系数**——**这层变换本身就是设计选择**，接了数据集不等于数值自动更权威
5. 连带面：v2 正典参考表 + **19 份 disease-pilot 的 47 处 `fc=…` 引用**
6. 许可：缺口 2 三项未登记——**A 会让"发布路径前必须补齐许可"从候选队列变成阻塞项**（数值成为该数据集的衍生读数）

**三选项的代价与回滚**（裁定前评估，留档）：

| 选项 | 代价 / 风险 | 可回滚性 |
|---|---|---|
| A 真正接入 | 两张映射表 + FC→增益变换设计（其本身是一次设计决策）· 脑干相关 ceiling 变化（v1 18 / v2 9 条）· v2 参考表与 19 份 pilot 同步 · v1 的 `provenance_note` 一旦重算即被覆盖（#134 实测重算 = 273 行全变）· 许可成为发布阻塞 | 文件可 `git revert`；**基于新数值写下的设计结论/平衡文本不可回滚**，快照标注只剩 git 历史 |
| B 明确降级 | 归档 7 个数据文件 + 撤回 §1.2 的接入承诺 | ≈0 |
| **C 部分接入** | 一个**只读**结构校验（核团覆盖 + 坐标一致性），**不改任何数值** | ≈0 |

**为什么选 C**：它同时消掉「登记了却不读」与「数值权威悬空」两件事，代价近乎为零；而 A 的收益（"数值来自文献"）在缺少映射与变换设计时并不成立——那两件事应当先作为独立设计决策讨论，而不是顺手在数据接入里定下来。

**C 的实施条件**（由 [#133](https://github.com/verystrongdog/game/issues/133) 消费；该 issue 已于 2026-09-13 按本裁定**重写为「只读结构校验器」**，其原标题假设的 A 范围被撤销，标签回到 `state:ready-for-agent`）：

- **前置**：本目录 7 个受控文件；项目核团清单取 `BRAINSTEM_COMMUNITY_GAIN_ESTIMATE` 的 16 条——其中复合条目（`VTA-NAcc` / `杏仁核-PAG` / `反射环路·*`）**不参与映射，须显式登记为"无对应"**
- **做什么**：只读 `region_info_Schaefer400.csv` + `subcortex_coords.csv` + `brainstem_coords*.txt`，断言 ① 项目每个脑干核团在数据集标签中有对应（列出对应表；缺项显式豁免并写理由——已知 `小脑皮层` 缺）② 坐标一致性（同一核团两处坐标在容差内）③ **不写任何受控产物**
- **验证方式**：新增一个只读校验器（退出码 0/1）并接进 `docs-integrity`；**不改生成器、不重算、不动两个产出 JSON**
- **差分对比方法**（留给未来的 A）：重算前后对 v2 JSON 做**逐链路差分**（43 行 × `modulation_ceiling`/`gain_coeff`/`excitability`），并按第 5 条清单同步 pilot 引用；比对跑在临时 worktree，**不得顺手改数据**（#134 的 `--md-only` 正是为此存在）

**数值权威声明**：无论 C 是否落地，两个产出 JSON 的脑干增益都来自 `BRAINSTEM_COMMUNITY_GAIN_ESTIMATE` / `load_brainstem_strength_estimates()`（本仓人工估计，依 Hansen et al. 2024 的**社区划分**）——设计侧引用时**必须写明"本仓估计"**，不得写成数据集读数（这正是 2026-09-12 那次标注修正要防的事）。

**仍未闭合**（裁定不等于实施）：C **尚未实施**——生成器依然不读数据集，悬空状态在实施前仍然成立；
两个产出 JSON 仍是 2026-07-27 快照（v1 已于 [#134](https://github.com/verystrongdog/game/issues/134) 解耦出 `--md-only`，重算仍会改写 273 行），快照的命运与 C 无关。

> **本裁定为什么不落 `design/decisions/`**：该目录 2026-09-12 **已冻结只读**（其 README 明写"不再追加新条目；新决策写进 `design/` 对应正典文档 + 一条短记录"）。#132 的「允许变化」写的是往那里加记录，与之冲突——按冻结声明办：裁定落在本文件（正是 issue 要求的回写处），并在 [链路调制上限参考表-v2.md](../../design/rules/skill-tree/modulation/链路调制上限参考表-v2.md) 留一行指针。

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
*创建: 2026-09-12 | 更新: 2026-09-13（§1.2/§二 缺口 1：hansen2024 数值权威裁定 C · #132）*
*关联: [数据层说明](../README.md), [sources.md](sources.md), [ENIGMA 结构连接说明](enigma_dk_connectivity.md), [数据契约](../../data/manifest.json)*
