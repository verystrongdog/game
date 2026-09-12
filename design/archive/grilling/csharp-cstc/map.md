# map: csharp-cstc

> csharp-engine step 6（plan §十一）——CstcGating：三环路 Gurney 门控（15 群体解析解 + gate + LoopSalience）。Status: closed（2026-08-13）

## Notes

- 依赖 csharp-engine plan §4.4（CstcGating.Step 签名 + 6 步流程 + 边界项）+ §十 CstcGating 测试行 + §十三-3（W_SEL_GPe 缺值）+ step 2/3/4/5 交付（GurneyState/GateState/LoopSalience/WMatrix 行序/WcState/ToneState）
- 设计文档依据：运行时状态模型 §6.1-6.5（3 通道/CI 名单/salience c/Gurney 5 群体/权重表/DA 混合/解析解/ramp/gate/技能映射）、§三（91-var 表 L3 值域 [0,1]）、§7.1（Phase 3 执行顺序）
- 文献源：data/connectivity/README_gurney_model.md（ModelDB 83560 摘要）+ ModelDBRepository/83560 GitHub GPR_engine.m（per-population 负阈值 + W_SEL_GPe=0 + 无 clamp——本 feature 实测获取）。⚠️ reference/literature/ 两个「Gurney-2001」PDF 实测为错标文件（BMJ/White Rose），不可引用

## Decisions-so-far

- [任务issue 01](design/issues/01-cstc-spec.md) → 数据实测第一轮（CI 成员与 §6.1 逐条一致 / 字段形状 / **gate≡1 惰性实测** / ModelDB 原始阈值 / 收敛性质）→ claimed（2026-08-13）
- **Q 裁决（2026-08-13 用户）**：Q1=A（W_SEL_GPe=0.0 补入权重表）、Q2=A（per-population e 表对齐 ModelDB 83560 + 取消 clamp，值域 [−1.5, 2.0]）、Q3=B（c_loop 按 fid 级取——同 dk 不同 fid 分属两环）
- **设计文档修正写回**（commit f039f93）：运行时状态模型 §6.1/§6.2/§6.3/§三/§十一 + plan §4.4 + README_gurney_model.md + term_registry（c_loop/gate_bonus/Gurney模型）+ 决策树 #33 D9/D10/D13 🔧 + GitHub #33 闭合后修正评论 + GurneyState 值域注
- **spec v1.0**（commit a46ba24）：[spec.md](../../../spec/engine/csharp-cstc.md) 构造 + Step + AC-1~15 + 偏差 B1（gate=1−O(a_new) 时刻）/B2（m≤0→O≡0 除零防护）/B3（残差上界 3.5×e−25）。锚点经第二轮实测复算（CI fid 名单 3/7/12、c=0 fp gate 0.843421、静息 gate2=1.0、c 0.665469/0.696963/0.692102、跨环路 c 值、m_SD2=0 锚点、float32 逐位安全域 |u|≥0.01）
- **全量审计 v1.0（2026-08-13）**：3 专家（数学/架构/接口）17 原始发现 → 去重 14 条；对抗验证 16 CONFIRMED + 1 REFUTED。退回：[audit/report.md](design/audit/report.md) —— 1 ❌（E1：AC-4/AC-10 迭代判据「≤100 回合」不可达——√0.9≈0.9487/回合收敛率，实测 251/253）+ 5 ⚠️（ordinal 陷阱 / AC-1 不可测 / ramp 未内联 / AC-9/10 迭代语义含混 / AC-12 clamp 不可证伪）+ 7 ℹ️（B4 缺位 / 端点误标 / D2 依据错 / #3 行矛盾 / C1 KeyNotFound / SD2 措辞 / 非单调注）
- **spec v1.1 修复（本 commit）**：迭代语义统一固定 300 回合（我实测 gate@300 = 0.8434211 / 0.8065790 / 1.0）+ CiRows 公开访问器 + ramp 内联 §4.5 + §4.3 防 ordinal + AC-12 包含性声明 + B4 + C1 文档化 + AC-9/10 措辞 + AC-5/6 链参数；任务issue #3/D2 同步修正
- **Δ审计（2026-08-13）**：2 专家（数学 0 发现 / 契约 1ℹ️）+ 对抗验证——0❌ / 0⚠️ / 1ℹ️（I-1：变更日志计数 1❌+6⚠️+6ℹ️ 与报告缺口汇总 1❌+5⚠️+7ℹ️+1 REFUTED 不一致 → L1 已修）。结论通过，转 sign-off
- **sign-off 批准（2026-08-13，commit d1e09dd）**：用户逐项处置 15 条全部「已修复」+ 结转清单 4 项（固定 300 回合 / 配对防 ordinal / −0.4575 哨兵 / 偏差注释对应）→ [sign-off.md](design/audit/sign-off.md)
- **实现（2026-08-13，commit cce0547）**：[工作issue 01](impl/issues/01-cstc-gating.md) → CstcGating.cs（构造 + Step + Ramp B2 防护）+ CstcGatingTests.cs（AC-1~15 共 15 方法）。`dotnet build` 零错误、`dotnet test` **115/115 全绿首跑通过**（既有 100 + 新增 15）。自审：15 AC 逐条 ✅ + §七 自检 9 项 ✅ + 结转 4 项回填 ✅ + 0 spec 缺陷

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 ✓ → 设计文档写回 ✓ → spec v1.0 ✓ → 全量审计 ✓（退回：1❌+5⚠️+7ℹ️+1 REFUTED 残留）→ spec v1.1 修复 ✓ → Δ审计 ✓（0❌/0⚠️/1ℹ️ L1 已修）→ sign-off 批准 ✓ → 工作issue 01 实现 + 自审 ✓（115/115）→ **feature 闭合** ✓

## 回顾段（2026-08-13，csharp-cstc feature closed）

### 审计效果统计

- v1.0 全量审计（3 专家）：退回——1 ❌ + 5 ⚠️ + 7 ℹ️ + 1 REFUTED 残留。唯一的 ❌（E1：AC-4/AC-10 迭代判据「max|Δ|<1e-7（≤100 回合）」不可达）被三专家独立命中且实测确认——**spec 作者（AI）凭直觉写「100 回合收敛」而非实测**（真实收敛 251/253 回合，f32 下 AC-9 存在 ~3.9e-7 极限环永不达标）。若按 v1.0 直接实现，测试会死循环或非确定失败。
- v1.1 Δ审计（2 专家 + 对抗验证）：通过——0 ❌ / 0 ⚠️ / 1 ℹ️（I-1 计数不一致，L1 免重审）。与四航/五航的残留发现率对比：本航 v1.1 修复质量高，Δ审计仅 1 个 info。
- 实现阶段：**0 spec 缺陷**。引擎 + 测试一次成型，115/115 首跑全绿。

### 流程观察

1. **迭代语义类 AC 必须显式写终止方式**：本航唯一 ❌ 的根因是 spec 把「收敛」当隐式概念。修复模式有效：§六 统一迭代语义声明（固定 300 回合 + 实测锚点 + 禁止 max|Δ| 依据）一处定义、三处 AC 引用——避免每个迭代 AC 各自发明判据。
2. **哨兵测试写入结转清单的模式第二次兑现**（继 wmatrix 结转 #1 后）：结转 #3（AC-11 负锚点 −0.4575 逐位断言必须存在）是因为 AC-12 的值域网格是包含性断言、对域内 clamp 不可证伪——审计把「什么断言能证伪什么实现」想清楚后，把唯一哨兵升格为独立 AC（AC-11），sign-off 再锁进结转。实现侧哨兵测试一行不多一行不少。
3. **float32 极限环发现的价值**：AC-9 的 ~3.9e-7 极限环（STN↔GPe 互耦在 f32 舍入下不收敛到 1e-7）是审计 E1 复算中发现的——它把「收敛断言」从数值问题变成语义问题（gate 已达 1.0 但 max|Δ| 永不达标），固定回合数 + 终态锚点比任何自适应判据都稳。
4. **镜像公式逐回合对照模式**（测试侧 ExpectedLoop 与引擎同序同算）让 300 回合迭代的每一回合都被验证——比只断言终态强得多，且零额外成本（两遍计算 bitwise 相同）。

### 对未来 feature 的建议

- 涉及迭代收敛的 spec：必须 python 实测收敛回合数 + 检查 f32 舍入极限环，写进「迭代语义」统一声明；禁止写「≤100 回合」这类拍脑袋上界。
- 审计发现「断言不可证伪」时（如值域包含性断言），把可证伪的哨兵升格为独立 AC 并进结转清单——本航 AC-11/结转 #3 是标准操作。
- 本航是 csharp-engine plan §十一 六步中的第 5 个 feature（wmatrix → wc-dynamics → tone → cstc 依次闭合）——下一步 step 7 csharp-speed（SpeedScoreCalculator，消费 LoopSalience mean(c_loop) 与 a_SD1）。

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [任务issue 01](design/issues/01-cstc-spec.md), [spec.md](../../../spec/engine/csharp-cstc.md) v1.1, [audit/report.md](design/audit/report.md), [sign-off.md](design/audit/sign-off.md), [工作issue 01](impl/issues/01-cstc-gating.md)*
