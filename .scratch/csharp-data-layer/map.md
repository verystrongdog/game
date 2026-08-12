# map: csharp-data-layer

> C# Data Layer feature — 加载全部 JSON 脑数据文件到 C# record。Status: closed (2026-08-12)

## Notes

- 二层流水线首航：任务issue 01 → spec v1.0 → 审计退回 → 数据修复 + spec v1.1/v1.2 → Δ审计有条件通过 → sign-off 批准 → 工作issue 01 → 实现 + 自审 → 关闭
- 审计副产品：发现并修复 situation_primitives.json 两类数据问题（3 悬挂引用 per #25 代偿方案 + 16 处 primary_networks 注册表失配）
- GitHub 镜像：tools/sync_issues.py（幂等同步，本地为真相源）

## Decisions-so-far

- [任务issue 01](design/issues/01-data-layer-spec.md) → 4 决策（D1-D4），GitHub #42
- [spec v1.2](design/spec.md) → 13 enum + 18 record + 5 loader 方法 + 14 AC，GitHub 审计报告见 [report.md](design/audit/report.md)
- [sign-off](design/audit/sign-off.md) → 批准 (2026-08-12)，5 项结转已全部回填 ✅
- [工作issue 01](impl/issues/01-data-loaders.md) → resolved，GitHub #43，14/14 AC ✅，24/24 测试绿

## Fog

- link_modulation_ceiling_v2.json 加载 → 待 Engine 层确认需求（spec §一 不覆盖）
- auto_activated_links legacy 字段 → 待 CSTC 词表迁移决策
- term_registry.json → 设计期参考，不入 Data Layer（D2）
