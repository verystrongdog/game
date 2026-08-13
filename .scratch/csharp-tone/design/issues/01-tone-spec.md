# 任务issue 01: Tone 规格（ToneUpdater + CorticalBias + M1 里程碑）

> Status: claimed | Type: task | 维度: 管线

## 问题（这件事要解决什么）

Layer 2（脑干广播调制）的两个引擎函数是 csharp-engine plan §十一 step 5 的交付物：

- `ToneUpdater.Step`——4 tone 的单步动力学（解析解 + clip）
- `CorticalBias.Compute`——tone → b_j 的 69 维注入权重计算

没有它们，**M1 静息 trace 里程碑**（plan §八：tone=baseline、s=0、30 回合实测 a(t) 静息不动点）无法执行，step 6 CstcGating 也被阻塞。本 issue 产出两个函数的精确实现规格 + M1 里程碑执行方案，数据实测已在本 issue 完成第一轮（见下）。

## 目标

- spec.md v1.0（§一~§七 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.3 ToneUpdater/CorticalBias 全部内容 + plan §十 ToneUpdater 测试行 + plan §八 M1 里程碑

## 指标

- spec 中全部数值断言（k_t 系数、解析解样例、b_j 分布、M1 不动点）经 python 实测验证
- 审计 0 阻塞项；AC 全部可测（数值断言 or 性质断言）

## 工作方式

二层流水线：任务issue → spec v1.0 → workflow 多专家审计 → sign-off → 工作issue → 实现 + M1 里程碑 → 证据式自审 → 文档写回（§十三-8 清扫 + wc-dynamics sign-off 结转 #4）。

## 范围

- 覆盖：`ToneUpdater.Step(ToneState, float[], CalibrationConfig) → ToneState` + `CorticalBias.Compute(ToneState, GameData) → float[69]` + M1 静息 trace 里程碑（AC 化 + 实测值写回设计文档）
- 不覆盖：δ 事件生产/聚合语义（step 9 EventProcessor）、CstcGating（step 6）、战斗初始化 tone=baseline（step 10 职责）、7 参数化性格→baseline 映射（设计延迟项）
- 输入：csharp-data-layer ✅（GameData/TripartiteModel.Brainstem 114 边）、csharp-engine-types ✅（ToneState/CalibrationConfig.DeltaScale）、csharp-wmatrix ✅（WMatrix 行序契约）、csharp-wc-dynamics ✅（WcDynamics.Step + Δ=1.0 常量先例）

## 数据实测（2026-08-13，本 issue 第一轮，python 可复算）

| 断言 | 实测值 |
|------|--------|
| brainstem 边总数 | 114 = LC_NE 32 + Raphe_5HT 68 + VTA_DA 11 + SNc_DA 3（`data/connectivity/tripartite_model.json` brainstem） |
| role 分布 | active 15 / modulating 99 / silent 0 |
| projection 分布 | diffuse_broadcast 96 / targeted_broadcast 18（不参与权重——修复 #8b） |
| 目标可解析性 | 114/114 target 均为 graph_nodes 的 dk 键 |
| Raphe 双源 | DR 34 条 + MnR 34 条，34 目标 100% 重叠（§5.1「100% 重叠」），同 target 两边的 role+projection 完全相同 |
| 每系统 role 分布（唯一 dk） | LC active 3（caudalanteriorcingulate/parahippocampal/rostralmiddlefrontal）+ modulating 29；Raphe active 3（medialorbitofrontal/rostralanteriorcingulate/superiorfrontal）+ modulating 31（含 Amygdala/Hippocampus）；VTA active 3（Accumbens-area/lateralorbitofrontal/medialorbitofrontal）+ modulating 8；SNc active 3（Accumbens-area/Caudate/Putamen） |
| 排除 fid（21）中接收 b_j | 7 个纹状体：AccumbensCore/AccumbensShell/NucleusAccumbens/VentralStriatum/Caudate/StriatumMatrix/Putamen（VTA+SNc DA tone——§7.2 锚点确认） |
| 全脑 b_j=0 的 fid | 15 个：10 脑干源（LocusCoeruleus×2、DorsalRapheNucleus、MedianRapheNucleus、SNc×2、VTA、PAG、SuperiorColliculus、PontineReticularNucleus）+ CerebellumCortex + Pallidum + SubthalamicNucleus + Thalamus×2。§5.7 列的 PAG/上丘/脑桥网状核/小脑皮层实测均 b_j=0 ✓，但零清单不止这四个（spec 记录完整清单） |
| b_j @ baseline（A 口径） | max = 1.05 @ medialorbitofrontal 3 fid（5HT act 1.0×0.5 + VTA act 1.0×0.4 + LC mod 0.5×0.3）；非零 54/69；无 clamp 触发 |
| b_j @ tone=1（A 口径） | max = 2.5（同 3 fid）→ 3 fid 超 2.0 被 clamp [0,2]；§7.2「max=2.0 全脑最高为 Accumbens-area」实测不完整（mOFC 三 fid 亦达 2.0+，clamp 兜底——文档清扫候选） |
| b_j @ baseline（B 口径，Q1 已否决） | max = 1.55；tone=1 max = 3.5（10 fid 超 clamp） |
| k_t = e^(−Δ/τ_t)（Δ=1） | NE 0.135335283 / DA_VTA 0.035673993 / DA_SNc 0.286504797 / 5HT 0.513417119 |
| 解析解样例（δ_scale=0.3） | NE 0.3 +d1 → 0.559399415；DA_VTA 0.4 +d1 → 0.689297802；DA_SNc 0.5 +d1 → 0.714048561；5HT 0.5 +d1 → 0.645974864；NE +10 → clip 1.0；5HT 1.0 −10 → clip 0.0 |
| back-to-back 双脉冲 | NE +1,+1：0.559399415 → 0.594505308（连续两次 Step ≠ 聚合一次 Step——δ 聚合语义唯一归属 step 9，本 feature 只定义单次 Step 契约） |
| DA_VTA 无 δ_scale 饱和 | 0.4 +d1 unscaled → 1.3643 → clip 1.0（印证 §5.5 ⚠️ 注；×0.3 后 0.6893） |
| M1 预览（python 按 csharp-wmatrix spec 算法重建 W：非零元 1389 ✓、b=0 不动点 active [0.49861,0.49951] ✓ 排除=σ(0)=0.3775407 ✓，重建可信） | baseline b_j（A 口径）30 回合静息不动点：**active 48 ∈ [0.3775, 0.7712]，mean 0.5931**；排除节点 = σ(b_j) 精确（b=0→0.3775 / b=0.7→0.5498 / b=0.9→0.5987）。**plan §八「b_j>0 会略高」的预测被实测推翻**——不是略高，max 从 0.4995 → 0.7712。M1 实测值写回文档时以此为准 |

## 追问

### Q1: Raphe 双源重复边——w_t(j) 算一次还是算两次？

**✅ 裁决（2026-08-13）：A——per-target 唯一**。同 system 同 target 多条边取 role 权重一次（active=1.0 / modulating=0.5），重复边不叠加。

理由：① DR+MnR 共用同一个 5HT_tone 变量（§5.1 双核团是该变量的解剖源），per-edge 求和把同一变量贡献乘 2；② 保持 §5.6 两档语义（求和下 Raphe modulating=1.0 与 LC active 同档，层级塌缩）；③ 基线 b_j max=1.05、tone=1 时 3 节点触 clamp，贴合 §7.2 [0,2] 契约描述。

### Q2: δ_scale=0.3 在哪一步应用？

**✅ 裁决（2026-08-13）：A——Step 加参注入**。签名改为 `Step(ToneState tone, float[] delta, CalibrationConfig cfg)`，Step 内部应用 `cfg.DeltaScale`。plan §4.3 原签名无 config 参数——加参记为偏差声明 B（新，spec 记录）。

理由：可注入（配合 csharp-engine-types 结转 #4 蒙特卡洛 sweep 模式）；杠杆位置对齐 plan §4.3（δ_scale 列在 ToneUpdater 条目下）；CalibrationConfig.DeltaScale 已交付（0.3f，[NEW] 待校准）。

## 判断与取舍（关键决策，spec 将固化为规范）

| D# | 决策 | 依据与取舍 |
|----|------|-----------|
| D1 | **Δ=1.0 私有常量**，注释引用 csharp-wc-dynamics spec §四 常量来源（Δ=1.0 复用漂移风险注——不重新定义） | wc-dynamics sign-off 结转 F8；plan §4.3 无 Δ 参数 |
| D2 | τ_tone 4 值（NE 0.5/DA_VTA 0.3/DA_SNc 0.8/5HT 1.5）+ baseline 4 值（0.3/0.4/0.5/0.5）= ToneUpdater **私有常量**，不扩 CalibrationConfig | 设计定值无校准需求（§5.3/§5.4）；同 wc-dynamics D3 先例 |
| D3 | δ 输入 float[4]，分量顺序 = (NE, DA_VTA, DA_SNc, 5HT)（§5.3 表序）；null / 长度≠4 → ArgumentException | 契约防御同 wc-dynamics D5 姿态 |
| D4 | **Step 签名加参**（Q2 裁决）：`Step(ToneState, float[], CalibrationConfig)`；Step 内部 `δ_eff = δ × cfg.DeltaScale`；cfg null → ArgumentNullException | plan §4.3 签名变更 = 新偏差声明 B；注入模式对齐 engine-types D3 |
| D5 | Step = 单次 δ 应用的解析解；同窗口多事件 δ 聚合（Σ）与实时发射时序（Phase 4 发射时刻）是 step 9 EventProcessor 职责 | 实测连续 Step ≠ 聚合一次（数学不等价），语义归属必须唯一；plan §4.3「δ 实时注入」括号注由 step 9 实现 |
| D6 | **CorticalBias w_t(j) = per-target 唯一**（Q1 裁决）：同 system 同 target 多条边取 role 权重一次；实测同 target 两边 role 相同，取首边即等价 | 数据实测表 Raphe 双源行 |
| D7 | w 从 **role 字段**取（active→1.0 / modulating→0.5——plan 修复 #8b，不是 projection 字段）；role==Silent → InvalidDataException | brainstem 边数据契约只允许 active\|modulating（实测 114/114 无 silent） |
| D8 | 目标解析：target 按 graph_nodes dk 键直查 → functional_ids fan-out 到 canonical 行序；未命中 → InvalidDataException（含边描述） | 同 WMatrixBuilder Step 4 端点解析姿态；实测 114/114 命中 |
| D9 | 输出 float[69] 行序 = Wsensory.RegionIds（canonical 行序契约，引用 csharp-wmatrix spec Step 1）；新数组输出 | b_j 供 WcDynamics.Step 直接消费 |
| D10 | b_j = Σ_t tone_t × w_t(j) 求和后逐分量 clamp [0,2]（§7.2）；输入 tone 值域 [0,1]（ToneState 契约）不校验 | §7.2 层间接口；clamp 兜底（tone=1 时 3 fid 超 2.0） |
| D11 | **M1 里程碑 AC 化**：30 回合静息 trace（tone=baseline、s=0、a(0)=0.10、WMatrixBuilder+WcDynamics+CorticalBias 真实组合）→ 断言收敛 + 实测值经 ITestOutputHelper 输出 → 写入设计文档（plan §八 + §十三-8 清扫 + wc-dynamics 结转 #4 一并执行） | M1 归属 step 5 已由 csharp-wc-dynamics Q1 裁决 |
| D12 | ToneUpdater 无 sigmoid（§5.2「无 sigmoid——tone 是调质浓度」）；clip [0,1] 是唯一非线性 | 设计正典；clip 提供饱和保护（§5.5） |

## 产出

- [ ] spec.md v1.0（§一~§七 + 变更日志，AC 覆盖 plan §十 ToneUpdater 行 + M1）
- [ ] workflow 多专家审计 → report.md
- [ ] 人类复核 → sign-off.md（批准）
- [ ] 工作issue 01 → 实现 + M1 里程碑 + 证据式自审
- [ ] M1 实测值写回设计文档（plan §十三-8 清扫 + wc-dynamics 结转 #4）
- [ ] map.md 更新 + 回顾段

## Comments

- 2026-08-13：创建。数据实测第一轮完成（114 边结构 / w 权重两口径 / b_j 分布 / k_t 锚点 / M1 预览）。Q1/Q2 用户裁决完成（Q1=A per-target 唯一；Q2=A Step 加参），进入 spec 写作。
