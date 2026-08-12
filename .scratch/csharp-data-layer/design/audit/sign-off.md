# 复核签字: C# Data Layer 实现规格 v1.2

> 复核日期: 2026-08-12 | 复核人: （待签） | 已读范围: （全表 Trace Table / 仅结论）

## 审计报告关键发现

**v1.0 全量审计**：❌ 退回修改（6 Error + 10 Warning）——§2.2 待实现部分 [JsonPropertyName] 全面缺失、词表过时、类型错误；§2.1 已实现 100 字段全部正确。

**v1.1 Δ审计**：⚠️ 有条件通过——数据侧三路实测 11/11 约束通过、E1-E6 修复全部确认；规格侧 2 个 AC 覆盖缺口（E-Δ1 mirror_of、E-Δ2 1049 三体边）。

**v1.2 补修**：AC-13/AC-14 新增 + auto_activated_links 豁免 AC 层注明 + 5 项文本修正。审计结论：条件已满足，数据侧免重审。

## 逐项处置

| # | 发现 | 处置 | 理由 |
|----|------|------|------|
| 1 | E1-E6（v1.0 阻断项） | ✅ 已修复（v1.1），三路实测确认 | 数据侧闭环 |
| 2 | E-Δ1/E-Δ2（AC 覆盖缺口） | ✅ 已修复（v1.2 AC-13/AC-14） | 免重审 |
| 3 | W-6 Matrix 行序依赖 Dictionary 保序 | 接受风险，测试加显式断言（结转） | 反序列化保序是 .NET 实践行为，加断言即可防护 |
| 4 | W-7 agency/valence 值域仅注释声明 | 接受风险（结转） | 已记录设计决定：保持 string，不进 enum |
| 5 | auto_activated_links 指向废弃 364 链路 | 标注 legacy 不校验（§五 C11 + §2.2 + §六 注） | 待 CSTC 词表迁移决策后再处理 |
| 6 | 有意不映射 key 清单（4 组） | ✅ 已在 §2.1/§2.2 显式声明 | 满足垃圾桶隔离原则 |

## ⚠️ 结转清单（需在工作issue实现时验证）

| # | 结转项 | 目标 work issue |
|----|--------|----------------|
| 1 | Matrix 行序 == Rows.Keys 序的显式断言（W-6） | 数据加载工作issue |
| 2 | AC-11 异常三分支测试（FileNotFoundException/JsonException/InvalidOperationException） | 数据加载工作issue |
| 3 | AC-14 需覆盖 brainstem target + privileged_pathways source/target membership | 数据加载工作issue |
| 4 | AC-12 测试需另读原始 JSON 获取 functional_networks 注册表 | 数据加载工作issue |
| 5 | 现有测试扩展：mirror_of membership 断言 + PrivilegedPathway membership 校验 | 数据加载工作issue |

## 结论

- [ ] 批准 —— spec v1.2 可以进入实现阶段（工作issue 创建）
- [ ] 退回 —— 需要修改后重新审计

---
*创建: 2026-08-12*
*关联: [审计报告](report.md), [spec](../spec.md) v1.2, [任务issue 01](../issues/01-data-layer-spec.md)*
