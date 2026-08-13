# map: csharp-cstc

> csharp-engine step 6（plan §十一）——CstcGating：三环路 Gurney 门控（15 群体解析解 + gate + LoopSalience）。Status: in progress

## Notes

- 依赖 csharp-engine plan §4.4（CstcGating.Step 签名 + 6 步流程 + 边界项）+ §十 CstcGating 测试行 + §十三-3（W_SEL_GPe 缺值）+ step 2/3/4/5 交付（GurneyState/GateState/LoopSalience/WMatrix 行序/WcState/ToneState）
- 设计文档依据：运行时状态模型 §6.1-6.5（3 通道/CI 名单/salience c/Gurney 5 群体/权重表/DA 混合/解析解/ramp/gate/技能映射）、§三（91-var 表 L3 值域 [0,1]）、§7.1（Phase 3 执行顺序）
- 文献源：data/connectivity/README_gurney_model.md（ModelDB 83560 摘要）+ ModelDBRepository/83560 GitHub GPR_engine.m（per-population 负阈值 + W_SEL_GPe=0 + 无 clamp——本 feature 实测获取）。⚠️ 参考/文献/ 两个「Gurney-2001」PDF 实测为错标文件（BMJ/White Rose），不可引用

## Decisions-so-far

- [任务issue 01](design/issues/01-cstc-spec.md) → 数据实测第一轮（CI 成员与 §6.1 逐条一致 / 字段形状 / **gate≡1 惰性实测** / ModelDB 原始阈值 / 收敛性质）+ Q1-Q3 草案 → claimed（2026-08-13）

## Fog

- 任务issue 数据实测 ✓ → Q1/Q2/Q3 用户裁决 → spec v1.0 → 全量审计 → Δ审计（如需）→ sign-off → 工作issue 01 实现 → 自审 → 设计文档修正写回 → feature 闭合
- 待办：Q2 决议关联的设计文档修正清单（§6.3 e 表 / §三 值域 / 权重表补 W_SEL_GPe / plan §4.4 step 5 文本）
