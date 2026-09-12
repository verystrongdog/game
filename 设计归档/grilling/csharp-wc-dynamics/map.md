# map: csharp-wc-dynamics

> csharp-engine step 4（plan §十一）——WcDynamics.Step：WC 69 节点单步动力学（解析解）。Status: closed（2026-08-13）——工作issue 01 resolved，AC-1~12 全 ✅，76/76 测试全绿

## Notes

- 依赖 csharp-engine plan §4.2（解析解公式）+ 偏差 §十二-1（Euler→解析解）§十二-5（静息吸引子≠0.10）+ step 3 交付的 WMatrix（W/Tau/RowFids）+ step 2 交付的 WcState（float[69] A）
- **结转：无**——engine-types 结转 #1-3 归 step 9、#4 归 step 6/10；wmatrix 结转已全部闭合（含用户批准的 §5.1 方向公式修正）
- 数据实测已完成（任务issue「数据实测」表，2026-08-13 python + 审计复算）：12 bimodal / e^(−Δ/τ) 3.72e-44（double 真值；float32 存储 3.78e-44 次正规，修正项低于舍入粒度 → a'=σ(h) 逐位）、2.06e-9、1.27e-3 / σ(0)=0.3775（文档 0.006 有误）/ b=0 固定点 2-3 回合收敛、48 活跃 ∈ [0.4986, 0.49951]、21 排除 = 0.3775
- 解析解推论：全节点单回合收敛 ≥99.87% → 动力学=固定点迭代（偏差 B3，Q2 已裁决）
- **spec v1.0 全量审计（3 专家）退回**：3 ❌（B3「≥99.9%」算术错应为 99.8727% / AC-9 小写 dk 键 pericalcarine / AC-5 上界 0.4995 是 6 位舍入）+ 5 ⚠️ + 7 ℹ️；解析解推导、σ 公式、全部锚点、float32 逐位论断经独立复算通过 → [report.md](design/audit/report.md)
- **spec v1.1 修正**（E1-E3 + F4-F8 全部落地）→ **Δ审计（2 专家）conditional**：0 ❌，残留 N1-N5 全为修复半径覆盖不全的 L1 级 → 全部 L1 清扫 → [sign-off.md](design/audit/sign-off.md) 批准（2026-08-13）
- **实现闭合**（`7c0fc8a`）：WcDynamics.Step 解析解 + 14 测试（AC-1~12），76/76 全绿（既有 62 + 新增 14）。实现 0 spec 缺陷；sign-off 结转 #1/#2/#3 全部落地（fid 大写 / MathF 自算 / B1-B3 注释对应）
- 偏差 B 关联文档清扫（皮层动力学 §4.2 σ(0)≈0.006 笔误、§4.3 Euler 叙述、Δ/τ 数量级矛盾）→ 并入 plan §十三-8，M1 实测后执行（结转 #4）

## Decisions-so-far

- [任务issue 01](design/issues/01-wc-dynamics-spec.md) → 数据实测表 + D1-D8 + 追问 Q1/Q2 → claimed（2026-08-13）
- spec v1.0 全量审计（3 专家）→ 退回（3❌/5⚠️/7ℹ️：B3 99.9% 算术错、AC-9 pericalcarine 大小写、AC-5 上界舍入）→ [report.md](design/audit/report.md)
- spec v1.1 修正（E1-E3 + F4-F8 全部落地）→ Δ审计（2 专家）conditional：0 ❌，残留 N1-N5（修复半径覆盖不全）全部 L1 已清扫 → 人类 sign-off ✅ 批准（2026-08-13）
- [工作issue 01](impl/issues/01-wc-dynamics.md) → 实现 + 证据式自审 → resolved（2026-08-13，76/76 绿，结转 #1-3 回填）

## Fog

- ~~Q1：M1 静息 trace 里程碑归属~~ ✅ 裁决：推迟到 step 5（plan §十一 已加 L1 注释，CorticalBias GREEN 后执行）
- ~~Q2：慢节点叙述矛盾处置~~ ✅ 裁决：偏差 B + 延后修正（并入 plan §十三-8 清扫，σ(0) 笔误显式追加）
- 文档叙述修正（B 偏差清扫）并入 plan §十三-8——M1 实测后执行（sign-off 结转 #4）
- **下一步**：step 5 csharp-tone（CorticalBias/ToneUpdater——M1 静息 trace 里程碑随其执行）
