# 任务issue 01: WMatrixBuilder 规格

> Status: claimed | Type: task | 维度: 管线

## 问题（这件事要解决什么）

W 矩阵（69×69 皮层-皮层连接权重 + τ[69]）是 WC 引擎的输入——没有它，step 4（WcDynamics）无法编译、运行时状态模型 §四 Layer 1 无法落地。本 issue 产出 `WMatrixBuilder.Build` 的精确实现规格：节点集分界、权重公式、归一化、行序契约、τ 查表。

设计文档之间存在**需要规格澄清的分歧**（详见「判断与取舍」D1），必须在本 issue 内以数据实测为依据解决——这正是二层流水线审计环节的用武之地。

## 目标

- spec.md v1.0（§一~§七 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.1 WMatrixBuilder 全部 6 条 + 结转 #5（行序对齐断言）

## 指标

- spec 中全部数据断言（节点数/边数/归一化性质/τ 分布）经 python 实测验证（引用即读取铁律的 spec 版）
- 审计 0 阻塞项；AC 全部可测（数值断言 or 性质断言）

## 工作方式

二层流水线：任务issue → spec v1.0 → workflow 多专家审计 → sign-off → 工作issue → 实现 → 证据式自审。
数据实测已在本 issue 完成第一轮（见下），spec 写作时逐字段复核。

## 范围

- 覆盖：`WMatrixBuilder.Build(GameData data) → WMatrix`（Types 已交付的契约类型：W[69,69] / Tau[69] / RowFids[69]）
- 输入：GameData.Tripartite（graph_nodes / corticocortical / privileged_pathways）+ GameData.BrainRegions（function_profile.timescale）+ GameData.Wsensory（RegionIds canonical 行序）
- 不覆盖：WcDynamics（step 4）、脑干 b_j 计算（step 5）、m 运行时值（demo 全 m_default）、focus 配置（demo 全 1.0）

## 数据实测（2026-08-13，本 issue 第一轮）

| 断言 | 实测值 |
|------|--------|
| graph_nodes | 51 键（cortical 32 / subcortical 8 / brainstem 11），69 functional_ids 唯一 |
| corticocortical 边 | 776 条、776 唯一 dk 对、无自环、全双向（388 对）、edr ∈ [0.103, 0.759]、40 个 dk |
| privileged_pathways 边 | 112 条、112 唯一 dk 对、与 CC 零重叠、无自环 |
| PP/CC 端点可解析性 | CC 40 dk 全部 ∈ graph_nodes；PP 端点全部可解析（100% 按 dk_name）；15 个 dk/fid 同名（歧义名） |
| 排除集（CSTC 6 + brainstem） | 21 fids（10 皮下 CSTC + 11 脑干）→ W 活跃节点 = 48 fids |
| 触及排除 dk 的边 | CC 130 / PP 23 → 幸存边 646 + 89 = 735（CC∩PP 重叠 0） |
| 孤立节点 | **无**——48 个参与 fids 全部有边；PP-only 的皮层 dk = 0（PP 端点全部同时有 CC 边）；CC-only 三种口径（审计澄清）：有 CC 边且无 PP 边 6 个（Caudate/Pallidum/Putamen/inferiorparietal/lateralorbitofrontal/superiorparietal，前 3 为 CSTC 排除 dk；另有 5 个 brainstem dk 两边皆无，不计入）；活跃 dk 中无幸存 PP 边 5 个（cuneus/inferiorparietal/lateralorbitofrontal/superiorparietal/transversetemporal——cuneus 与 transversetemporal 的 PP 边全部触及排除 dk）；活跃且无 PP 边 3 个（inferiorparietal/lateralorbitofrontal/superiorparietal） |
| 无对向边的幸存对 | 仅 1 条：pericalcarine→Amygdala（amygdalofugal, edr 0.2813）；其余全部双向且双向 edr 相等 → **归一化前权重全对称；归一化后一般不对称**（行和不同，实测 tt↔cac 归一化后 0.02819 vs 0.03621），唯一例外单元格对 pericalcarine→Amygdala |
| fan-out 后 fid 级非零元 | 1389（= Σ|fids(source)|×|fids(target)| over 735 幸存对） |
| Amygdala/HC/Cerebellum 参与 | CC 40 条 + PP 51 条（三 dk **并集**幸存口径；Cerebellum-Cortex 单节点幸存 CC 6 + PP 12）——它们在 W 内有真实连接（支撑 D1） |
| timescale 分布（brain_regions.function_profile） | fast 27 / medium 29 / slow 11 / mirror 2（LC-Right、SNc-Right 无 timescale 字段，只有 mirror_of） |
| brainstem 的 brain_regions.dk_name | 全部 None（11 个）——「dk_name=None」指 brain_regions 数据，非 graph_nodes |

## 判断与取舍（关键决策，spec 将固化为规范）

| D# | 决策 | 依据与取舍 |
|----|------|-----------|
| D1 | **W 节点集 = 48 fids**（44 皮层 + Amygdala + Hippocampus×2 + Cerebellum-Cortex）；排除 = category=brainstem + 6 个 CSTC dk（Pallidum/Thalamus-Proper/Putamen/Caudate/Accumbens-area/SubthalamicNucleus）。排除节点 W 行=列=0，仍由 WC 驱动（h_j = b_j + s_j） | 运行时状态模型 §4.2 的排除清单是操作性规则；皮层动力学-通用层 §5.1「W 仅包含 category=cortical」措辞与 §5.5（特权通路 EC→HC 必须落 W 内）、§4.5（Amygdala 经皮层连接间接接收）矛盾——取运行时状态模型为正典。plan §4.1-3 括注「brainstem dk_name=None 节点（PAG、上丘、脑桥网状核、小脑皮层）」中「小脑皮层」归类有误（实测 category=subcortical 且不在排除清单）——spec 记录偏差声明 |
| D2 | demo 无 LinkState → m_mean ≡ m_default = 0.3（CalibrationConfig.MDefault）；focus_multiplier ≡ 1.0 | plan §4.1（demo 范围）；Build 签名无 focus 参数，接口以注释预留 |
| D3 | **行序契约：canonical = WsensoryMatrix.RegionIds**（69）；W.RowFids = RegionIds；W 行=接收者（target） | csharp-engine-types spec §2.1/§2.8 已确立；结转 #5 在本 feature 落地（测试断言 RowFids == RegionIds） |
| D4 | 边端点解析：dk_name 优先（graph_nodes key），无法匹配时按 functional_id 解析；解析失败 = 数据错误（测试拦截） | 实测当前数据 100% 可解析；15 个歧义名（如 Amygdala 既是 dk 又是 fid）中非排除 dk 全为单 fid（仅 Amygdala）；Caudate（2 fids）∈ CSTC 排除集，排除检查先于解析，歧义永不触达（Δ审计修正） |
| D5 | 自连接 w(A,A)=0 + fan-out 推论：**同 dk 内 fid 对 = 0**；CC∩PP 无重复 dk 对（实测 0）→ 无需去重策略 | 皮层动力学-通用层 §5.2 + 实测 |
| D6 | τ 查表 per-fid：brain_regions.function_profile.timescale（fast 0.01 / medium 0.05 / slow 0.15）；2 个 mirror fid 继承 mirror_of 目标的 timescale；缺失 → 0.05（§4.4 默认） | 皮层动力学-通用层 §4.4 + 实测（67 有值 + 2 mirror） |
| D7 | 触及排除 dk 的边不入 W（CC 130 + PP 23 跳过）；零行仅 21 个排除 fids（48 参与 fids 全部有边，无孤岛）；归一化分母 ε=0.01 兜底 | 运行时状态模型 §4.2「行=列=0」+ 实测（修正：早前误测「3 孤岛皮层 dk」为脚本 bug，已澄清） |
| D8 | **方向契约：W[行=接收者][列=发送者]**（h_j = Σ_k W_jk·a_k，运行时状态模型 §4.1）；皮层动力学-通用层 §5.1 的 `W[fid_A][fid_B]=w(dk(A),dk(B))` 是 [源][目标] 序——两者互为转置，demo 归一化前对称时数值无差，但归一化后行和不同会分叉 → spec 以运行时方程方向为准 | 运行时状态模型 §4.1 方程是 step 4 WcDynamics 的直接消费端；索引序旧文记为偏差声明 |

## 追问

### Q1: 设计文档冲突（D1）是否需要先改文档？

皮层动力学-通用层 §5.1「W 矩阵仅包含 category=cortical 的纯皮层节点」与运行时状态模型 §4.2 排除清单（CSTC 6 + 脑干）不一致——按后者，Amygdala/Hippocampus/Cerebellum-Cortex 在 W 内（实测有 91 条边支撑）。

**建议**：spec 按运行时状态模型 §4.2 写（操作性规则明确 + 特权通路/间接输入机制依赖它）；皮层动力学-通用层 §5.1 措辞在 spec 审计后一并修正（L1 级文档清理，`🔧 修正` 记入变更日志）。不改运行时状态模型。

### Q2: 归一化范围

§5.4 行归一化 `W[j][k]/(Σ_i W[j][i] + 0.01)`——归一化在 fan-out 广播**之后**、按 69 行逐行做（排除节点行 = 0/0.01 = 0 自然成立）。

**建议**：按上句理解实现，无异常分支。

## 产出

- [x] spec.md v1.0 → v1.1（v1.0 全量审计退回 → v1.1 修正 + Δ审计 conditional 通过 + L1 修正）
- [x] spec.md 通过审计（[report.md](../audit/report.md)：两轮审计闭环）
- [x] sign-off.md 获批（2026-08-13，[sign-off.md](../audit/sign-off.md)）

## Comments
