# #52 任务issue 01: WcDynamics 规格

> 状态：关闭 · 创建 2026-08-13 · 关闭 2026-08-13
> 标签：维度:管线, ready-for-agent
> 原始：https://github.com/verystrongdog/game/issues/52

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-wc-dynamics/design/issues/01-wc-dynamics-spec.md

## 问题（这件事要解决什么）

WcDynamics.Step 是 WC 引擎 Layer 1 的单步动力学——运行时状态模型 §四 Layer 1 更新 `a_j ← WC_step(a_j, h_j = W·a + b + s)` 的落地。没有它，step 5（tone/b_j）与 M1 静息 trace 里程碑都无法执行。本 issue 产出 `WcDynamics.Step` 的精确实现规格：解析解公式、同步更新语义、契约防御、AC 测试。

设计文档存在**两处需要规格澄清的分歧**（详见「追问」Q1/Q2 与「判断与取舍」D6），必须在本 issue 内以数据实测为依据解决。

## 目标

- spec.md v1.0（§一~§七 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.2 WcDynamics 全部内容 + plan §十 WcDynamics 测试行

## 指标

- spec 中全部数值断言（e^(−Δ/τ) 系数、σ 锚点、固定点性质）经 python 实测验证（引用即读取铁律的 spec 版）
- 审计 0 阻塞项；AC 全部可测（数值断言 or 性质断言）

## 工作方式

二层流水线：任务issue → spec v1.0 → workflow 多专家审计 → sign-off → 工作issue → 实现 → 证据式自审。
数据实测已在本 issue 完成第一轮（见下），spec 写作时逐字段复核。

## 范围

- 覆盖：`WcDynamics.Step(WcState a, float[] b, float[] s, WMatrix w) → WcState`（plan §4.2）——解析解公式、同步更新语义、排除节点行为、契约防御
- 输入：step 2 已交付 WcState（float[69] A 防御拷贝）+ step 3 已交付 WMatrix（W[69,69]/Tau[69]/RowFids[69]）+ 调用方传入 b[69]/s[69]
- 不覆盖：ToneUpdater/CorticalBias（step 5，b_j 生产方）、CstcGating（step 6）、速度排序（step 7）、CombatState 初始化 a(0)=0.10（step 10 职责）、M1 静息 trace 里程碑（见 Q1）

## 数据实测（2026-08-13，本 issue 第一轮）

| 断言 | 实测值 |
|------|--------|
| bimodal 节点数（W_sensory 行和 = 2） | 12 个：BanksSTS、InferiorParietal、InferiorParietalAngular、MiddleTemporal、Paracentral、Postcentral、RostralAnteriorCingulateCortex、SuperiorTemporal、SuperiorTemporalSulcus、SuperiorTemporalWernicke、Supramarginal、SupramarginalTPJ（🔧 2026-08-13 审计修正：原名单 5 个非双模态、漏 5 个真实双模态——凭记忆补全名单的错误，审计 3/3 专家命中） |
| e^(−Δ/τ) 解析解系数（Δ=1，τ 三档） | fast τ=0.01 → e^(−100)=3.72e-44（double 数学真值；float32 存储值 3.78e-44 次正规数非零；修正项 (a−σ)·k ≈ 2e-44 低于 float32 舍入粒度 ulp≈6e-8 → a' 与 σ(h) **逐位相等**）；medium τ=0.05 → e^(−20)=2.06e-9；slow τ=0.15 → e^(−6.67)=**1.27e-3** |
| σ 锚点（v=1, θ=0.5） | σ(0.5)=0.5（不动点 x=σ(x) 验证）；σ(0)=**0.3775**——皮层动力学 §4.2 叙述「σ(0)≈0.006」实测有误（正确 0.3775） |
| b=0 固定点预览（真实 W 归一化矩阵，a(0)=0.10，30 回合迭代 a←σ(W·a)） | 第 2-3 回合即收敛（round30 vs 31 max\|Δ\|=0.00e+00）；**48 活跃节点终态 ∈ [0.4986, 0.49951]**（≈0.5，max=0.4995055；🔧 2026-08-13 审计修正：原上界 0.4995 是把 0.4995055 舍成 6 位的产物）；21 排除节点（W 行=0）终态 = σ(0) = 0.3775 |
| 解析解推论（由 e^(−Δ/τ) 行推导） | 全部节点单回合收敛 ≥99.87%（slow 残留 0.13%；🔧 2026-08-13 审计修正：99.8727% < 99.9%，原「≥99.9%」算术不成立）→ 动力学实质 = 固定点迭代 a ← σ(W·a + b + s)，「慢节点跨回合平滑过渡、保留历史」叙述在解析解下不成立 |

## 追问

### Q1: M1 静息 trace 里程碑归属 step 4 还是 step 5？

**✅ 裁决（2026-08-13）：M1 推迟到 step 5**——CorticalBias GREEN 后立即执行真实 trace（tone=baseline、s=0、30 回合）。step 4 只交付 WcDynamics.Step + 单元测试（含 b=0 固定点收敛性质测试作铺垫）。plan §十一 step 4 行加 L1 注释「M1 随 step 5 执行」（已执行，commit 见 Comments）。

理由：M1 定义（plan §八）要求 tone=baseline 的 b_j，b_j 生产方 CorticalBias 是 step 5 的产物；step 4 做 M1 只能跑 b=0 玩具版（实测 mean=0.4623，非真实静息态）或违反文件所有权复制公式。

### Q2: 慢节点叙述与解析解数值矛盾——记录偏差并延后文档修正？

**✅ 裁决（2026-08-13）：偏差 B + 延后修正**——spec 记偏差声明 B（推论：动力学实质为固定点迭代 a ← σ(W·a+b+s)，与 plan §十二-5 静息吸引子偏差同源）；文档叙述修正并入 plan §十三-8 的 Euler 一致性清扫（皮层动力学 §4.3 已在清扫清单内），「σ(0)≈0.006 → 0.3775」笔误显式追加进清扫清单（σ 段落 §4.2 不在原清单内）。不单独行动，M1 实测后统一修。

理由：e^(−6.67)=1.27e-3 → slow 节点一回合收敛 99.87%；叙述在 Euler 下也不成立（bang-bang 振荡）。根因是 Δ=1 秒比全部 τ 大一个数量级。让「慢节点真的慢」需调 τ 或 Δ，属 L3 设计变更，非本 feature spec 可裁定。

## 判断与取舍（关键决策，spec 将固化为规范）

| D# | 决策 | 依据与取舍 |
|----|------|-----------|
| D1 | **统一解析解、无分支**：a' = σ(h) + (a − σ(h))·e^(−Δ/τ)，全部节点同一条公式 | plan §十二-1 已裁定（设计自身参数 Δ=1、τ=0.01-0.15 下 Euler 产生 bang-bang 振荡）；快节点 e^(−100) float32 下溢为 0 → a' = σ(h) 精确成立，无需原文档 Δ/τ≥50 特判 |
| D2 | Δ = 1.0 私有常量（不在 Step 签名中） | 回合时长默认 1.0 秒（运行时状态模型 §4.3）；plan §4.2 签名无 Δ 参数 |
| D3 | σ 参数 v=1.0、θ=0.5 私有常量，**不扩 CalibrationConfig** | CalibrationConfig 现无 σ 字段（已核实）；两参数设计文档已定值、无校准需求；待日后校准需求出现再走 L2 |
| D4 | **同步更新**：h_j 全部由旧 a 计算完毕后再统一写新 a | 运行时状态模型 §7.1 步骤 3（W·a 用上一回合末 a） |
| D5 | 契约防御：null → ArgumentNullException；b/s 长度≠69、W 非 69×69、Tau 长度≠69、τ_j ≤ 0 → ArgumentException | wmatrix 同款防御姿态；τ_j ≤ 0 导致除零/负指数（当前数据无此情形，纯防御） |
| D6 | **偏差声明 B**：解析解推论——全节点单回合收敛 ≥99.87%，动力学=固定点迭代；「慢节点跨回合保留历史」叙述不成立。实现照解析解，文档叙述修正延后 | 数据实测表 e^(−Δ/τ) 行；plan §十二-1 已裁定解析解，此为推论声明；修正并入 §十三-8 清扫（Q2 已裁决 ✅；🔧 2026-08-13 Δ审计后修正 99.9%→99.87%） |
| D7 | **排除节点无特判**：W 行=0 → Σ_k 0·a_k = 0 → h_j = b_j + s_j 由统一公式自然覆盖 | plan §4.2 边界；免分支 |
| D8 | a(0)=0.10 是调用方职责（step 10 CombatState），Step 不初始化；测试以 0.10 为输入 | 运行时状态模型 §7.3；plan §十二-5（0.10 是初始值非吸引子） |

## 产出

- [x] spec.md v1.0→v1.1（§一~§七 + 变更日志，AC 覆盖 plan §十 WcDynamics 行）
- [x] workflow 多专家审计 → report.md（v1.0 全量 3 专家退回 → v1.1 Δ审计 2 专家 conditional → 残留 L1 清扫）
- [x] 人类复核 → sign-off.md（2026-08-13 批准 ✅）
- [x] 工作issue 01 → 实现 + 证据式自审（2026-08-13 resolved，76/76 绿）
- [x] map.md 更新 + 回顾段

## Comments

- 2026-08-13：Q1/Q2 用户裁决完成（Q1 推迟 step 5；Q2 偏差 B + 延后修正），进入 spec 写作。
- 2026-08-13：feature 闭合——spec v1.1 审计两轮（全量退回 → Δ审计 conditional → L1 清扫）、sign-off 批准、工作issue 01 实现 76/76 全绿。结转 #4（文档叙述修正）并入 plan §十三-8，M1 实测后执行。

---

## 评论（1 条）

### verystrongdog · 2026-08-13

## ✅ 闭合总结（2026-08-13）

**csharp-wc-dynamics feature closed**——WcDynamics.Step 解析解实现，76/76 测试全绿。

| 阶段 | 结果 |
|------|------|
| spec v1.0 全量审计（3 专家） | 退回：3 ❌（B3 99.9% 算术错 / AC-9 dk-fid 大小写 / AC-5 上界舍入）+ 5 ⚠️ + 7 ℹ️ |
| spec v1.1 Δ审计（2 专家） | conditional：0 ❌，残留 N1-N5 全为修复半径盲区 → L1 清扫 → 等效通过 |
| 人类 sign-off | ✅ 批准 |
| 实现 | WcDynamics.Step + AC-1~12（14 测试），0 spec 缺陷，全量 76/76 绿 |

**关键决策落地**：D1-D8 + Q1（M1 推迟 step 5）/ Q2（偏差 B + 延后修正）——B1 解析解、B2 吸引子 ≈0.5、B3 固定点迭代（全节点单回合收敛 ≥99.87%）。

**结转**：文档叙述修正（皮层动力学 §4.2 σ(0) 笔误、§4.3 Euler 叙述、Δ/τ 矛盾）并入 plan §十三-8，M1 实测后执行。

---
*导出: 2026-09-12 | 来源: GitHub issue*
