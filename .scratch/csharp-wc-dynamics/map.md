# map: csharp-wc-dynamics

> csharp-engine step 4（plan §十一）——WcDynamics.Step：WC 69 节点单步动力学（解析解）。Status: in-progress（2026-08-13）——任务issue 01 claimed（Q1/Q2 已裁决 ✅），spec v1.1 Δ审计 conditional，待人类 sign-off

## Notes

- 依赖 csharp-engine plan §4.2（解析解公式）+ 偏差 §十二-1（Euler→解析解）§十二-5（静息吸引子≠0.10）+ step 3 交付的 WMatrix（W/Tau/RowFids）+ step 2 交付的 WcState（float[69] A）
- **结转：无**——engine-types 结转 #1-3 归 step 9、#4 归 step 6/10；wmatrix 结转已全部闭合（含用户批准的 §5.1 方向公式修正）
- 数据实测已完成（任务issue「数据实测」表，2026-08-13 python + 审计复算）：12 bimodal / e^(−Δ/τ) 3.72e-44（double 真值；float32 存储 3.78e-44 次正规，修正项低于舍入粒度 → a'=σ(h) 逐位）、2.06e-9、1.27e-3 / σ(0)=0.3775（文档 0.006 有误）/ b=0 固定点 2-3 回合收敛、48 活跃 ∈ [0.4986, 0.49951]、21 排除 = 0.3775
- 解析解推论：全节点单回合收敛 ≥99.87% → 动力学=固定点迭代（偏差 B3，Q2 已裁决）

## Decisions-so-far

- [任务issue 01](design/issues/01-wc-dynamics-spec.md) → 数据实测表 + D1-D8 + 追问 Q1/Q2 → claimed（2026-08-13）
- spec v1.0 全量审计（3 专家）→ 退回（3❌/5⚠️/7ℹ️：B3 99.9% 算术错、AC-9 pericalcarine 大小写、AC-5 上界舍入）→ [report.md](design/audit/report.md)
- spec v1.1 修正（E1-E3 + F4-F8 全部落地）→ Δ审计（2 专家）conditional：0 ❌，残留 N1-N5（修复半径覆盖不全）全部 L1 已清扫 → 待人类 sign-off

## Fog

- ~~Q1：M1 静息 trace 里程碑归属~~ ✅ 裁决：推迟到 step 5（plan §十一 已加 L1 注释，CorticalBias GREEN 后执行）
- ~~Q2：慢节点叙述矛盾处置~~ ✅ 裁决：偏差 B + 延后修正（并入 plan §十三-8 清扫，σ(0) 笔误显式追加）
- sign-off 待人类复核 → 工作issue 01 实现（WcDynamics.Step + AC-1~12）——**下一步**
