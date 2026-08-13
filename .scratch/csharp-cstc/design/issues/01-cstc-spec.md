# 任务issue 01: CSTC 门控规格（CstcGating）

> Status: claimed | Type: task | 维度: 管线 | GitHub: [#56](https://github.com/verystrongdog/game/issues/56)

## 问题（这件事要解决什么）

csharp-engine plan §十一 step 6 = **CstcGating**——Layer 3 CSTC 门控（三环路 Gurney 模型，运行时状态模型 §六）。它是每回合 Phase 3 的最后一个数值引擎：把 WC 激活 a(t) 与 DA tone 转化为 15 个 Gurney 群体激活 + 3 个 gate + 3 环路 salience。

没有它：GateState 恒为初始值 1.0（技能 gate_bonus 永远满额）、step 7 SpeedScoreCalculator 的决断分（mean(c_loop)）与执行分（a_SD1）无数据源、M1 静息 trace 无法扩展到 Layer 3。本 issue 产出 CstcGating 的精确实现规格，并裁决**三个阻塞性设计疑问**（其中两个实测暴露，一个 plan §十三-3 遗留）。

## 目标

- spec.md v1.0（§一~§七 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.4 CstcGating 全部内容 + plan §十 CstcGating 测试行
- 三个设计疑问经用户裁决后固化为偏差声明 / 设计文档修正项

## 指标

- spec 中全部数值断言（CI 成员名单、DA 混合锚点、e 表、权重、gate 扫描点、解析收敛）经 python 实测验证
- 审计 0 阻塞项；AC 全部可测（数值断言 or 性质断言）——v1.0 审计发现 1 阻塞（E1 迭代判据）+ AC-1 不可测，v1.1 修复后达标（见 audit/report.md）

## 工作方式

二层流水线：任务issue → 数据实测 + Q 裁决 → spec v1.0 → workflow 多专家审计 → sign-off → 工作issue → 实现 → 证据式自审 → feature 闭合（含设计文档修正写回）。

## 范围

- **覆盖**：`CstcGating` 构造（GameData → 三环路 CI 行索引）+ `Step(WcState a, ToneState tone, GurneyState prev) → (GurneyState, GateState, LoopSalience)`（plan §4.4 签名）
- **不覆盖**：SpeedScoreCalculator/TurnOrderBuilder（step 7）、Phase 编排与事件（step 9-11）、Phase 4 gate_bonus 结算（应用侧）、NPC salience 竞争（step 12）
- **输入**：csharp-data-layer ✅（GraphNode.cstc_roles/cstc_loops 复数聚合字段 + FunctionProfile 单数字段）、csharp-engine-types ✅（GurneyState/GateState/LoopSalience/GurneyPopulation/CstcLoop/CstcRole）、csharp-wmatrix ✅（canonical 行序契约）、csharp-wc-dynamics ✅（WcState + Δ=1.0 常量先例）、csharp-tone ✅（ToneState.DaVta/DaSnc + M1 实测值表）

## 数据实测（2026-08-13，本 issue 第一轮，python 可复算）

| # | 断言 | 实测值 |
|---|------|--------|
| 1 | CI 节点（GraphNode 复数聚合 `cstc_roles`/`cstc_loops`，tripartite_model.json 51 节点） | somatic 3 = paracentral/precentral/superiorfrontal；cognitive 5 = caudalanteriorcingulate/caudalmiddlefrontal/frontalpole/parsopercularis/rostralmiddlefrontal；limbic 8 = Amygdala/Hippocampus/caudalanteriorcingulate/insula/lateralorbitofrontal/medialorbitofrontal/rostralanteriorcingulate/superiorfrontal——**与 §6.1 表逐条一致** |
| 2 | 跨环路节点 | caudalanteriorcingulate（cognitive+limbic）+ superiorfrontal（limbic+somatic）——与 §6.1 注释一致，恰好这两个 |
| 3 | 数据字段形状 | function_profile（brain_regions.json，fid 级）= **单数** cstc_loop/cstc_role；GraphNode（tripartite_model.json，节点级）= **复数** cstc_loops/cstc_roles。plan §4.4「数据字段为复数数组」指 GraphNode 聚合字段——CI 过滤按 GraphNode 执行（公式对 function_profile 不可执行，字段不存在）→ **已被 Q3=B 取代（2026-08-13 审计修正）**：过滤按 FunctionProfile 单数字段执行（fid 级）；「字段不存在」应为「复数数组字段不存在于 function_profile」 |
| 4 | CstcLoop.Global | 0 成员（实测无任何 fid/节点归 global）→ 不参与 gating（plan §4.4 边界项确认） |
| 5 | striatal_gate 分布 | limbic 4 fid（Accumbens-area）/ somatic 2（Putamen + StriatumMatrix——§6.1 表只列 Putamen，StriatumMatrix 为表外额外成员）/ cognitive 1（Caudate）。Gurney 群体是每环路抽象变量，**Step 不消费 striatal_gate 角色**——此差异无引擎影响 |
| 6 | 静息 c_loop（M1 实测 a 值，节点均值口径） | somatic 0.665469 / cognitive 0.689439 / limbic 0.685438 |
| 7 | 静息 c_loop（fid 级口径，对比） | somatic 0.665469 / cognitive 0.696963 / limbic 0.692102（口径差 ≤0.0076，见 Q3） |
| 8 | 静息 DA_loop（VTA=0.4, SNc=0.5 混合） | limbic 0.42 / cognitive 0.46 / somatic 0.48 |
| 9 | 🔴 **gate≡1 惰性实测**（现状参数：e 全 0.2 + clamp[0,1]） | 全 c×DA 扫描（c∈[0,1]×0.2 步、DA∈{0,0.5,1}）gate 恒 = **1.0000**。根因：GPi 输入 = 0.9·O_STN − 0.3·O_GPe − 1.0·O_SD1，STN 与 SD1 同由 c 驱动且 0.9 < 1.0 → GPi 永不过阈值（a_GPi 恒 ≤ 0.02，O_GPi 恒 0）。**CstcGating 功能上完全惰性**，与 plan 测试行「c_loop=0 门控抑制」及 §6.4「O_GPi 高（tonic 抑制强）→ gate 低」叙事直接矛盾 |
| 10 | ModelDB 83560 原始实现（GPR_engine.m，GitHub 实测） | **tonic 来自 per-population 负阈值**：e_SEL=e_CONT=0.2、e_STN=−0.25、e_GPe=−0.2、**e_GPi=−0.2**；无任何输入基线项；**W_SEL_GPe 默认 = 0**（无 SD1→GPe 连接；'g' 选项才 −0.25）；**a 无 clamp**（可为负——负阈值机制要求） |
| 11 | 原始阈值下 gate 行为（per-population e + 无 clamp + W_SEL_GPe=0，固定点扫描） | c=0 → gate=0.843（门控抑制恢复 ✓）；DA≥0.5 且 c≥0.4 → gate=1.0（全放行）；静息（c≈0.67, DA≈0.45）→ gate=1.0；DA=0 时 gate 范围 0.777–0.843（窄——选择对比主要来自 DA 轴） |
| 12 | clamp[0,1] 与负阈值互斥 | a_GPi ≥ 0 → O_GPi ≥ 0.2 → gate ≤ 0.8 恒（放行上限被 clamp 锁死）→ 负阈值必须配无 clamp |
| 13 | 解析收敛 | exp(−25) = 1.39e-11；\|a−u\| ≤ 3.5（值域 [−1.5, 2.0]）时残差 ≤ 4.9e-11（🔧 2026-08-13 修正：原「2.2 → 3e-11」按旧值域 [0,1] 推导）；\|u\| ≥ 0.01 时 **a(t+Δ) 与 u 逐位相等**（float32 舍入，实测失败边界 \|u\| ≤ 0.0004） |
| 14 | DA 极端 ramp | DA=1 → m_SD2=0 → O_SD2≡0（恒零合法）；m_SD1=2 饱和点 a ≥ 0.7 |
| 15 | 文献 PDF 错标 | 参考/文献/ 两个「Gurney-2001」PDF 实测为 BMJ 论文与 White Rose eprints（文件名与内容不符，不可引用）。真源 = data/connectivity/README_gurney_model.md + ModelDBRepository/83560 GitHub（本 issue 行 #10 数据即来自后者原始代码） |

## 追问

### Q1: W_SEL_GPe 缺值处置（plan §十三-3 遗留）

GPe 输入方程引用 `W_SEL_GPe`，但设计权重表（§6.3）与 README_gurney_model.md 权重清单均无此项（缺口自文献源传播）。

**✅ 裁决（2026-08-13）：A——补 W_SEL_GPe = 0.0 入权重表**，GPe 方程保留该项。对齐 ModelDB 83560 原始默认（无 SD1→GPe 连接）；未来启用 Gurney 2004 'g' 选项（−0.25）有落点。

### Q2: gate≡1 惰性处置（本 issue 实测 #9 暴露）

现状参数下 CstcGating 恒输出 gate=1.0，门控系统无功能。

**✅ 裁决（2026-08-13）：A——对齐 ModelDB 83560 原始实现**：per-population 阈值 e（SD1/SD2=0.2、STN=−0.25、GPe=−0.2、GPi=−0.2）+ 取消 clamp（a 可为负，值域文档化）+ 设计文档修正（§6.3 e 表、§三 91-var 表 L3 值域、plan §4.4 step 5、GurneyState 值域注）。实测恢复设计意图：c=0 → gate 0.843 门控抑制，DA+salience 高 → 1.0 全放行。

### Q3: c_loop 粒度（a(ci) 聚合口径）

设计 §6.2 的 ci 是 §6.1 表中的 dk 节点，但运行时 WC 状态是 fid 级（69 维）。两种口径实测差 ≤0.0076（实测 #6/#7）。

**✅ 裁决（2026-08-13）：B——fid 级直接**：ci = FunctionProfile 过滤（单数字段 cstc_role == cortical_input && cstc_loop == loop）；a(ci) = a_j。跨环路体现为同 dk 不同 fid 分属两环（归属断言，无单点双贡献）；多 fid 节点（rostralmiddlefrontal 3 fid）权重 ∝ fid 数。与 核心机制.md 技能 salience 的 fid 级口径一致。

## 判断与取舍（草案，Q 裁决后定稿）

| D# | 决策（草案） | 依据 |
|----|------------|------|
| D1 | CI 过滤按 **FunctionProfile 单数字段**（brain_regions.json，fid 级）执行——Q3=B 裁决；plan §4.4「复数数组」表述按此修正 | 实测 #1/#3；Q3=B |
| D2 | Step 内**同时更新**：u 全部由 t 时刻 O(a(t)) 计算，镜像 WC 骨架；STN↔GPe 耦合跨回合收敛（收缩率 √0.9 ≈ 0.9487/回合，🔧 2026-08-13 审计修正——原「残差 e^(−25) 级」混淆单步瞬态与跨回合收敛） | 设计 §6.3「同 WC 骨架」（运行时状态模型 §7.1 步骤 3 同款）；顺序更新会改变首回合 O 输入（差 ~0.225 量级——e^(−25) 只保证 \|a_new−u\| ≤ 4.9e-11，不保证 O 相等），故强制同时更新（AC-11 锚点锁定） |
| D3 | Gurney 常量（权重 10 项含 W_SEL_GPe=0 + per-population e 表 + τ=0.04）为 CstcGating **私有常量**，不扩 CalibrationConfig | 设计定值（镜像 csharp-tone D2 先例） |
| D4 | 契约防御：constructor 验证三环路 CI 均非空（InvalidDataException）；Step null/形状防御（镜像 wc-dynamics D5） | 数据契约——实测三环路均 ≥3 节点，防御性不破坏 |
| D5 | CstcLoop.Global/None 不参与 gating（文档化行为） | 实测 #4：0 成员 |
| D6 | striatal_gate/pallidal_output/thalamic_relay/modulator 角色不被 Step 消费——只有 CI 成员资格影响 c_loop | 实测 #5；Gurney 5 群体是每环路抽象变量 |
| D7 | a 行序 = canonical 69（WcState.A，Wsensory.RegionIds 契约）；CI fid→行号解析镜像 WMatrixBuilder Step 1-2 | csharp-wmatrix 行序契约复用 |
| D8 | DA 混合逐字段显式公式（LoopSalience 已交付文档注明「按字段名配对不得按位置直配」） | csharp-engine-types 已交付类型语义 |
| D9 | 解析收敛断言：float32 下 a_new == u 逐位（残差 < ulp/2，实测 #13） | plan 测试行「解析收敛到 u」float32 精确化 |
| D10 | **per-population e 表**（Q2=A）：e_SEL=e_CONT=0.2、e_STN=−0.25、e_GPe=−0.2、e_GPi=−0.2——设计 §6.3 单一 e=0.2 修正 | ModelDB 83560 GPR_engine.m 原始参数（实测 #10）；恢复 tonic 抑制机制 |
| D11 | **无 clamp**（Q2=A）：a 可为负，值域文档化（实测解析界：SD1 [0,2] / SD2 [0,1] / STN [−1,1] / GPe [−1,0.9] / GPi [−1.3,0.9]）；§三 91-var 表 [0,1] 修正 + GurneyState 值域注修正 | 负阈值机制要求（实测 #12：clamp 与负阈值互斥）；exp(−25)≈0 下 a 即 u，解析界即实际界 |
| D12 | **W_SEL_GPe = 0.0 入权重表**（Q1=A），GPe 方程保留该项 | ModelDB 83560 默认；plan §十三-3 闭合 |
| D13 | **跨环路 = dk 归属断言**（Q3=B）：superiorfrontal/caudalanteriorcingulate 的 fids 分属两环——测试断言数据归属，非单点双贡献 | Q3=B；plan 测试行「跨环路节点双贡献」按 fid 级语义实现 |

## 产出

- [x] 数据实测第一轮（本 issue，已完成——见上表）
- [x] Q1/Q2/Q3 用户裁决（Q1=A / Q2=A / Q3=B）
- [x] spec.md v1.0（§一~§七 + 变更日志 + 参数速查表；AC-1~15；偏差 B1-B3）
- [x] workflow 多专家审计 → report.md（v1.0 全量审计：退回——1❌ E1 + 6⚠️ + 6ℹ️ + 1 refuted；16 CONFIRMED）
- [ ] spec v1.1 Δ审计（修复后重审变更章节 + 半径扩张）
- [ ] 人类复核 → sign-off.md（批准）
- [ ] 工作issue 01 → 实现 + 证据式自审
- [x] 设计文档修正写回（Q2 决议关联：运行时状态模型 §6.3/§三 + 权重表 + plan §4.4——commit f039f93）
- [ ] map.md 更新 + 回顾段

## Comments

- 2026-08-13：创建。数据实测第一轮完成（CI 成员/字段形状/gate≡1 惰性/ModelDB 原始实现/收敛性质）。三个阻塞疑问提交用户裁决（Q1 权重缺值、Q2 惰性处置、Q3 粒度）。
- 2026-08-13：裁决完成（Q1=A / Q2=A / Q3=B）+ 设计文档修正写回（f039f93：运行时状态模型 §6.1/§6.2/§6.3/§三/§十一、plan §4.4、README_gurney_model.md、term_registry、决策树 #33 D9/D10/D13 🔧、GurneyState 值域注）+ GitHub #33 闭合后修正评论。spec v1.0 完成（锚点经第二轮实测复算：gate 时刻语义 B1、m_SD2=0 除零防护 B2、残差上界修正 B3）。:13 行按 B3 同步修正。
- 2026-08-13：全量审计完成（3 专家 17 原始发现 → 去重 14；对抗验证 16 CONFIRMED + 1 REFUTED）。退回修改：❌ E1（AC-4/AC-10 迭代判据「max\|Δ\|<1e-7（≤100 回合）」不可达——STN↔GPe 互耦收缩率 √0.9≈0.9487/回合，实测收敛 251/253 回合）必须修复。spec 升 v1.1 修复全部 ❌/⚠️/ℹ️（迭代语义统一 300 回合、CiRows 公开访问器、ramp 内联 §4.5、§4.3 ordinal 陷阱措辞、AC-12 包含性断言声明、B4 偏差入表、C1 KeyNotFound 文档化、AC-9 SD2 ≈0 注、AC-10 端点与非单调注、AC-5/6 链参数补全）；本 issue #3 行与 D2 依据同步修正。Δ审计待跑。
