# 复核签字: csharp-tone spec（ToneUpdater + CorticalBias）

> 复核日期: 2026-08-13 | 复核人: 人类（用户） | 已读范围: [ ] 全表（report.md Trace Table + 缺口汇总） / [ ] 仅结论

## 审计报告关键发现（v1.0 全量审计，3 专家 + 逐发现对抗验证）

| # | 严重度 | 摘要 |
|----|--------|------|
| F1-math | ⚠️ | spec §四 4.1 DeltaSeconds 备注段引用失实——「运行时状态模型 §4.3」实为连接权重 W 章节；权威出处是皮层动力学-通用层 §4.3「Δ = 回合时长（默认 1.0 秒）」 |
| F1-contract | ⚠️ | §三 CorticalBias 声明的 3 条异常（null × 2 / target 未命中 / Role==Silent）无任何 AC 覆盖——按 spec 实现可省略全部防御检查而测试仍全绿（ToneUpdater 有 AC-7，CorticalBias 无对应项） |
| F1-data | ⚠️ | AC-11「Shell」不是数据 fid 名（实际 AccumbensShell）——按 fid 名解析的测试必挂 |
| F2-data | ⚠️ | AC-12「PAG」不是数据 fid 名（实际 PeriaqueductalGray）+「Thalamus×2」不明确（Thalamus + ThalamusPulvinar）；任务issue 数据实测表有同源错误 |
| F3-data | ⚠️ | AC-15 引用任务issue M1 预览行失真——原行「active 48 ∈ [0.3775, 0.7712] mean 0.5931」实为全 69 节点口径（0.3775 是排除节点 σ(0)）；真实 active 口径 [0.535174, 0.771229] mean 0.658196（spec AC-15 数字本身正确） |
| F2-contract | refuted | AC-13 clamp 命中集合语义歧义——spec 自带「pre-clamp 2.5 → 2.0」注释已限定「clamp 实际改变值」语义，缺陷不成立；残留 info：建议显式注明 10 个恰 2.0 的边界 fid |

审计结论：**有条件通过（0 ❌ / 5 ⚠️ / 1 refuted）**——公式推导、全部数值锚点、计数结构、行序契约经专家独立复算通过（含 1389 非零元重建、round 10 < 1e-5）。

## 逐项处置

| # | 发现 | 处置 | 状态 |
|----|------|------|------|
| 1 | F1-math | 修正spec：E1 备注改引「皮层动力学-通用层 §4.3」 | ✅ spec v1.1（commit 4344706） |
| 2 | F1-contract | 修正spec：E2 新增 AC-16（CorticalBias 契约防御三断言）+ §七 第 5 项补契约防御 | ✅ spec v1.1（commit 4344706） |
| 3 | F1-data | 修正spec：E3 AC-11 Shell→AccumbensShell | ✅ spec v1.1（commit 4344706） |
| 4 | F2-data | 修正spec：E4 AC-12 PAG→PeriaqueductalGray + Thalamus×2 明确；任务issue 15 零清单行同源修正 | ✅ spec v1.1（commit 4344706） |
| 5 | F3-data | 修正spec：E5 任务issue M1 预览行口径修正（active 48 ∈ [0.535174, 0.771229] mean 0.658196，原全节点口径保留在 🔧 注）+ AC-15 复核注释 + map.md 同源修正 | ✅ spec v1.1（commit 4344706） |
| 6 | F2-contract（info） | 采纳建议：F6 AC-13 显式注明 10 个边界 fid（pre-clamp 恰 2.0，不属命中集合） | ✅ spec v1.1（commit 4344706） |

## ⚠️ 结转清单（需在工作issue实现时验证）

v1.0 审计全部 ⚠️ 已修复为 spec 断言；Δ审计（v1.1）0 真实发现。**无结转项**——工作issue 实现时直接按 spec v1.1 执行即可。

## Δ审计结果（spec v1.1，2 专家 + 对抗验证，4 agents / 0 错误）

**结论：通过（0 ❌ / 0 ⚠️ / 2 info 均 refuted）**。

| 专家 | 重审范围 | 判定 |
|------|---------|------|
| 数学/数据 | E1 引用亲读确认；E5 独立重建 W 复算（active 48 ∈ [0.535174, 0.771229] mean 0.658196、加权一致性 ≈0.59308）；F6 边界 fid 恰 10 个；半径扩张 grep 零残留 | ✅ 0 发现 |
| 契约/交叉引用 | E2 AC-16 ↔ §三 3 异常一一对应 + 构造可行性（GameData record `with` / TripartiteModel init List 可追加 / EdgeRole.Silent 存在）；E3/E4 fid 名与 JSON 一致；版本号/footer/变更日志/map/issue 🔧 注一致 | ✅ 2 info 均 refuted |

2 项 info 发现（AC-16 编号位置非单调、§六 前言措辞精确度）经对抗验证均为可选优化建议而非缺陷，未采纳。

## 结论

- [ ] **批准** —— spec v1.1 进入实现阶段（Step 5 工作issue）
- [ ] **退回** —— 需要修改后重新审计

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [审计报告](report.md), [spec v1.1](../spec.md), [任务issue 01](../issues/01-tone-spec.md)*
