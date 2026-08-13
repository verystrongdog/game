# map: csharp-cstc

> csharp-engine step 6（plan §十一）——CstcGating：三环路 Gurney 门控（15 群体解析解 + gate + LoopSalience）。Status: in progress

## Notes

- 依赖 csharp-engine plan §4.4（CstcGating.Step 签名 + 6 步流程 + 边界项）+ §十 CstcGating 测试行 + §十三-3（W_SEL_GPe 缺值）+ step 2/3/4/5 交付（GurneyState/GateState/LoopSalience/WMatrix 行序/WcState/ToneState）
- 设计文档依据：运行时状态模型 §6.1-6.5（3 通道/CI 名单/salience c/Gurney 5 群体/权重表/DA 混合/解析解/ramp/gate/技能映射）、§三（91-var 表 L3 值域 [0,1]）、§7.1（Phase 3 执行顺序）
- 文献源：data/connectivity/README_gurney_model.md（ModelDB 83560 摘要）+ ModelDBRepository/83560 GitHub GPR_engine.m（per-population 负阈值 + W_SEL_GPe=0 + 无 clamp——本 feature 实测获取）。⚠️ 参考/文献/ 两个「Gurney-2001」PDF 实测为错标文件（BMJ/White Rose），不可引用

## Decisions-so-far

- [任务issue 01](design/issues/01-cstc-spec.md) → 数据实测第一轮（CI 成员与 §6.1 逐条一致 / 字段形状 / **gate≡1 惰性实测** / ModelDB 原始阈值 / 收敛性质）→ claimed（2026-08-13）
- **Q 裁决（2026-08-13 用户）**：Q1=A（W_SEL_GPe=0.0 补入权重表）、Q2=A（per-population e 表对齐 ModelDB 83560 + 取消 clamp，值域 [−1.5, 2.0]）、Q3=B（c_loop 按 fid 级取——同 dk 不同 fid 分属两环）
- **设计文档修正写回**（commit f039f93）：运行时状态模型 §6.1/§6.2/§6.3/§三/§十一 + plan §4.4 + README_gurney_model.md + term_registry（c_loop/gate_bonus/Gurney模型）+ 决策树 #33 D9/D10/D13 🔧 + GitHub #33 闭合后修正评论 + GurneyState 值域注
- **spec v1.0**（commit a46ba24）：[spec.md](design/spec.md) 构造 + Step + AC-1~15 + 偏差 B1（gate=1−O(a_new) 时刻）/B2（m≤0→O≡0 除零防护）/B3（残差上界 3.5×e−25）。锚点经第二轮实测复算（CI fid 名单 3/7/12、c=0 fp gate 0.843421、静息 gate2=1.0、c 0.665469/0.696963/0.692102、跨环路 c 值、m_SD2=0 锚点、float32 逐位安全域 |u|≥0.01）
- **全量审计 v1.0（2026-08-13）**：3 专家（数学/架构/接口）17 原始发现 → 去重 14 条；对抗验证 16 CONFIRMED + 1 REFUTED。退回：[audit/report.md](design/audit/report.md) —— 1 ❌（E1：AC-4/AC-10 迭代判据「≤100 回合」不可达——√0.9≈0.9487/回合收敛率，实测 251/253）+ 5 ⚠️（ordinal 陷阱 / AC-1 不可测 / ramp 未内联 / AC-9/10 迭代语义含混 / AC-12 clamp 不可证伪）+ 7 ℹ️（B4 缺位 / 端点误标 / D2 依据错 / #3 行矛盾 / C1 KeyNotFound / SD2 措辞 / 非单调注）
- **spec v1.1 修复（本 commit）**：迭代语义统一固定 300 回合（我实测 gate@300 = 0.8434211 / 0.8065790 / 1.0）+ CiRows 公开访问器 + ramp 内联 §4.5 + §4.3 防 ordinal + AC-12 包含性声明 + B4 + C1 文档化 + AC-9/10 措辞 + AC-5/6 链参数；任务issue #3/D2 同步修正
- **Δ审计（2026-08-13）**：2 专家（数学 0 发现 / 契约 1ℹ️）+ 对抗验证——0❌ / 0⚠️ / 1ℹ️（I-1：变更日志计数 1❌+6⚠️+6ℹ️ 与报告缺口汇总 1❌+5⚠️+7ℹ️+1 REFUTED 不一致 → L1 已修）。结论通过，转 sign-off

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 ✓ → 设计文档写回 ✓ → spec v1.0 ✓ → 全量审计 ✓（退回：1❌+5⚠️+7ℹ️+1 REFUTED 残留）→ spec v1.1 修复 ✓ → Δ审计 ✓（0❌/0⚠️/1ℹ️ L1 已修）→ **sign-off（待用户逐项处置）** → 工作issue 01 实现 → 自审 → map.md 回顾 → feature 闭合
