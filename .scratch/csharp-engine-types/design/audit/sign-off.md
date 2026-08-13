# 复核签字: 引擎共享状态类型 spec

> 复核日期: 2026-08-13 | 复核人: dog | 已读范围: 摘要（关键发现表 + 4 取舍 + 结转清单，经终端简报）

## 审计历程

- **v1.0 全量审计**（3 专家：类型完整性 / 字段来源核实 / 架构与接口契约）：2 reject + 1 conditional → **退回**——核心 ❌ 为行序恒等式与实测数据矛盾（3/3 专家独立命中）
- **v1.1 修复**：吸收全部 15 项发现（1❌+5⚠️+9ℹ️）→ **Δ审计**（2 专家：修复充分性 / 半径扩张核查）：**pass**，无 ❌ 无 ⚠️，仅 6 info（4 项 L1 已修 + 2 项保持现状）

## 审计报告关键发现

| # | 严重度 | 发现 | 处置 |
|---|--------|------|------|
| 1 | ❌ | C1/AC-10 行序恒等式「= BrainRegionsData.Regions 顺序」与实测矛盾——两 JSON 的 69 key 集合相同、顺序第 0 位即不同（TransverseTemporal vs AccumbensCore） | ✅ 已修：唯一 canonical = `WsensoryMatrix.RegionIds`（plan §三 原文「与 W_sensory 行序一致」），spec 写入实测警示 + 取舍记录 |
| 2 | ⚠️ | GameData 聚合字段结构未定义（实现者须自行发明接口） | ✅ 已补 §2.12 字段表（5 字段，类型名与 Data 层已交付 record 逐一核对） |
| 3 | ⚠️ | gates 初值 0 与推导矛盾（Gurney=0 → O_GPi=0 → gate=1−0=1） | ✅ 已改推导值 1.0（§7.3 未定义 gate 初值；本 spec 取 §6.3+§6.4 推导，首回合 CstcGating.Step 覆盖） |
| 4 | ⚠️ | LoopSalience DA 混合位置序歧义（照抄文档序会配错 somatic/limbic） | ✅ 已改逐字段显式公式（Somatic 0.2/0.8、Cognitive 0.4/0.6、Limbic 0.8/0.2） |
| 5 | ⚠️ | C5 防御生效 A5/B1 归属——§5.5 未定义互斥，两 δ 5HT 方向相反 | ✅ 已声明为本 spec 解释（取 A5），step 9 实现时复核 |
| 6 | ⚠️ | C5 Hit=false 时 B2 m=0/0=NaN（「m<0.01 跳过」对 NaN 失效） | ✅ 已加边界约定（incoming=0 时 m=0 跳过 emit） |
| 7-15 | ℹ️ | IsValidChannelUsage 空值真值表 / DamageEvent 偏差声明 / A4 注释 / 来源表述 ×4 / WcState 身份映射建议 | ✅ 全部吸收或评估（取舍见下） |

## 逐项处置

| # | 发现 | 处置 | 理由 |
|---|------|------|------|
| 1 | WcState 不加身份映射字段（专家建议加 Fids string[69]） | 接受 spec 取舍 | fid 身份已由 `WsensoryMatrix.RegionIds`（Data 层）+ `WMatrix.RowFids`（step 3）承担两份；WcState 是每 tick 更新的运行时状态，第三份纯冗余；行序对齐由约束 C1 规范 + step 3 测试验证 |
| 2 | gates 初值取推导值 1.0（vs 「0 占位 + 声明不被消费」） | 接受 spec 选择 | 1.0 语义正确（初始全放行，gate=0 是「完全门控抑制」）；推导链 §6.3+§6.4 完整 |
| 3 | C5 防御生效 → 承受者收 A5（非 B1） | 接受为解释性选择 | §5.5 未定义互斥；已标注 step 9 实现时复核 + 判别约定（DamageBlocked>0） |
| 4 | 不加 DamageEvent 中间抽象层 | 接受 | 两子类字段集不同（plan §4.6 物理/精神公式），中间层无共享字段增量；step 9 若需统一分支再加 |

## ⚠️ 结转清单（需在工作issue实现时验证）

| # | 结转项 | 目标 |
|---|--------|------|
| 1 | 防御生效判别（DamageBlocked>0）在小伤害取整边界下的正确性（如 incoming=1 → 减半后 dealt=1 → blocked=0） | step 9 EventProcessor |
| 2 | C5 A5 归属解释（vs B1）——§5.5 未定义互斥，实现时复核 δ 方向（A5 5HT +1 vs B1 5HT −1） | step 9 |
| 3 | A4 expected 重算：忍耐被动常量（基础行动设计 §四，值 −1，未进 CalibrationConfig）与低 SAN 穿透逻辑（核心机制 §4.3） | step 9 |
| 4 | gates=1.0 在首回合 CstcGating.Step 覆盖前不被任何消费点读取（覆盖时序） | step 6 / step 10 |
| 5 | AC-10 行序对齐由 step 3 承接（W.RowFids == WsensoryMatrix.RegionIds 测试） | step 3 WMatrixBuilder |

## 结论

- [x] 批准 —— spec v1.1 可以进入实现阶段 ✅ 2026-08-13
- [ ] 退回 —— 需要修改后重新审计

---

*创建: 2026-08-13*
*关联: [审计报告](report.md), [spec v1.1](../spec.md), [任务issue 01](../issues/01-types-spec.md)*
