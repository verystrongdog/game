# map: csharp-tone

> csharp-engine step 5（plan §十一）——ToneUpdater.Step（4 tone 解析解）+ CorticalBias.Compute（tone → b_j 69 维）+ M1 静息 trace 里程碑。Status: open

## Notes

- 依赖 csharp-engine plan §4.3（ToneUpdater 解析解公式 + τ/baseline + b_j 公式 + 修复 #5/#8b）+ §八（M1 里程碑）+ §十二-2（tone 解析解偏差）§十二-7（baseline 范围冲突裁决）+ step 2/3/4 交付（ToneState/CalibrationConfig/WMatrix/WcDynamics）
- 设计文档依据：运行时状态模型 §5.1-5.7（脑干广播/动力学/τ_tone/baseline/δ_event/b_j 公式/未广播节点）、§7.2（b_j ∈ [0,2]）、§7.3（初始化 tone=baseline）
- **数据实测已完成**（任务issue「数据实测」表，2026-08-13 python 实测）：114 边结构 / Raphe 双源 100% 重叠 / role 分布 / b_j 两口径对比 / k_t 锚点 / 解析解样例 / M1 预览（基线 b_j 不动点 active ∈ [0.3775, 0.7712] mean 0.5931——plan §八「略高」预测被推翻）
- **Q1/Q2 用户裁决完成（2026-08-13）**：Q1=A per-target 唯一（Raphe 重复边不叠加）；Q2=A Step 加参注入 CalibrationConfig（plan §4.3 签名变更记偏差声明 B）

## Decisions-so-far

- [任务issue 01](design/issues/01-tone-spec.md) → 数据实测表 + Q1/Q2 裁决 + D1-D12 → claimed（2026-08-13）

## Fog

- spec v1.0 写作 → workflow 审计 → sign-off → 实现 + M1 → 文档写回（plan §十三-8 + wc-dynamics 结转 #4）
- 向后结转：δ 聚合/实时发射时序归 step 9 EventProcessor；7 参数化性格→baseline 映射为设计延迟项
