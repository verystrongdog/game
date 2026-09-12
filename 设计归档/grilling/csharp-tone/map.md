# map: csharp-tone

> csharp-engine step 5（plan §十一）——ToneUpdater.Step（4 tone 解析解）+ CorticalBias.Compute（tone → b_j 69 维）+ M1 静息 trace 里程碑。Status: closed（2026-08-13）

## Notes

- 依赖 csharp-engine plan §4.3（ToneUpdater 解析解公式 + τ/baseline + b_j 公式 + 修复 #5/#8b）+ §八（M1 里程碑）+ §十二-2（tone 解析解偏差）§十二-7（baseline 范围冲突裁决）+ step 2/3/4 交付（ToneState/CalibrationConfig/WMatrix/WcDynamics）
- 设计文档依据：运行时状态模型 §5.1-5.7（脑干广播/动力学/τ_tone/baseline/δ_event/b_j 公式/未广播节点）、§7.2（b_j ∈ [0,2]）、§7.3（初始化 tone=baseline）
- **数据实测已完成**（任务issue「数据实测」表，2026-08-13 python 实测）：114 边结构 / Raphe 双源 100% 重叠 / role 分布 / b_j 两口径对比 / k_t 锚点 / 解析解样例 / M1 预览（基线 b_j 不动点 active 48 ∈ [0.535174, 0.771229] mean 0.658196——plan §八「略高」预测被推翻；审计修正口径）
- **Q1/Q2 用户裁决完成（2026-08-13）**：Q1=A per-target 唯一（Raphe 重复边不叠加）；Q2=A Step 加参注入 CalibrationConfig（plan §4.3 签名变更记偏差声明 B）

## Decisions-so-far

- [任务issue 01](design/issues/01-tone-spec.md) → 数据实测表 + Q1/Q2 裁决 + D1-D12 → claimed（2026-08-13）
- spec v1.0 → 全量审计 conditional（0❌/5⚠️/1 refuted，[report.md](design/audit/report.md)）→ v1.1 修复（E1-E5+F6，2026-08-13）→ Δ审计（通过，2 info refuted）→ [sign-off.md](design/audit/sign-off.md) 批准（2026-08-13，无结转项）
- [工作issue 01](impl/issues/01-tone.md) → 实现（ToneUpdater/CorticalBias/M1 测试）→ 自审（AC-1~16 全 ✅，100/100 绿）→ 文档写回（plan §十三-8 清扫 + M1 实测入运行时状态模型 §7.3.1）→ resolved
- **闭合总结**：ToneUpdater.Step（解析解 + δ_scale，偏差 B1-B3）+ CorticalBias.Compute（role 两档 + per-target 唯一 + clamp [0,2]，C1-C6）+ M1 静息不动点实测（active 48 ∈ [0.535174, 0.771229]、排除 21 = σ(b_j) 三组 14/3/4、maxΔ=0）。24 新测试，全库 100/100 绿。

## Fog

- spec v1.0 写作 ✓ → 全量审计 ✓（conditional）→ v1.1 修复 ✓ → Δ审计 ✓ → sign-off ✓ → 实现 + M1 ✓ → 文档写回（plan §十三-8 + wc-dynamics 结转 #4）✓ → feature 闭合 ✓
- 向后结转：δ 聚合/实时发射时序归 step 9 EventProcessor；7 参数化性格→baseline 映射为设计延迟项；fid→dk「名不符实」陷阱（dk 名 ≠ fid 名前缀）进预防性结转——step 6+ 数据依赖断言继续 RowOf/数据推导模式
