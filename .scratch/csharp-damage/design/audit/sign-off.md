# 复核签字: csharp-damage spec v1.1（Δ审计通过后）

> 复核日期: 2026-08-13 | 复核人: dog | 已读范围: 仅结论（基于会话 Δ审计总结批准）

## 审计报告关键发现

### 全量审计（v1.0，report.md Trace Table 14 项）

| # | 严重度 | 发现 |
|---|--------|------|
| F1 | ❌ | MathF.Round 语义模型错误——「委托 double 精度」为假：.NET 8 全 f32 域实现，AC-14 第二行锚点 1.9/0.9 按 v1.0 写测试必失败（真实输出 2.0/1.0） |
| F2 | ⚠️ | 精神公式写死 2f 使 baseDamage 死参数（与 B6/D8 矛盾） |
| K-F2 | ⚠️ | miss 时 Damage 返回值无 AC 锚定 |
| C-F1 | ⚠️ | §二 2.2 xUnit 机制陈述不准确 + 边界未声明 |
| C-F2 | ⚠️ | AC-17 类型断言无实现机制 |
| K-F3 | ⚠️ | types spec 🔧 修正行动无 AC 承接 |
| K-F4 | ⚠️ | AC 实测标签（A/H/J）与实测表编号错位 |
| K-F5/C-F3 | ⚠️ | L0EvadeHitPenalty 数值来源引用漂移 |
| C-F4/F3/K-F6/K-F7 | ℹ️ | 常量消费措辞 / 0.2999f 字面量 / 11→12 / 未定义行为补漏 |

### Δ审计（v1.1，report.md Δ审计段）

- 结论：**通过（残差清扫后）**——0 ❌ / 0 ⚠️ 阻塞；2 WARN + 1 INFO + 2 refute 发现全部已修。
- 关键新发现（refute）：**AC-17 的「float 赋值编译失败」机制实测不成立**（int→float 隐式转换）——已替换为重载绑定探针（本地 dotnet 实测区分有效）。
- 对抗验证：AC-1~14 全部锚点独立 dotnet 实测逐位 PASS；全仓三攻击面 grep 零残留。

## 逐项处置

| # | 发现 | 处置 | 理由 |
|---|------|------|------|
| 1 | F1 Round1 语义 | ✅ 修正 spec（v1.1）——真实 f32 域语义 + AC-14 第二行回 2.0f/1.0f（本地 runtime 8.0.29 实测 0x40000000） | 按 v1.0 写测试必失败；审计前自修正方向系误修正已回退 |
| 2 | F2 死参数 | ✅ 精神公式消费 baseDamage（spec/plan/issue D3 同步） | 死参数与 B6/D8 矛盾 |
| 3 | K-F2 miss 锚点 | ✅ AC-5 增「miss 仍返回完整伤害值 4.0f」 | 实现若把结算放进 if(hit) 分支将挂 |
| 4 | C-F1 xUnit 机制 | ✅ §二 2.2 泛型推断 + ≤80/2^24 精确域 + double 字面量边界 | 机制陈述经 Δ审计二次修正（≤60 表述与实读不符） |
| 5 | C-F2 AC-17 机制 | ✅ **重载绑定探针** IsFloat(float)/IsFloat(int)（Δ审计 refute 推翻原「赋值编译失败」方案后替换；本地实测区分有效） | v1.0 建议本身错误，被第三层对抗验证捕获 |
| 6 | K-F3 types 🔧 行 | ✅ AC-18 承接（文件所有权归 damage 工作issue） | 防跨 feature 行动静默丢失 |
| 7 | K-F4 标签错位 | ✅ 对齐 # 编号 + 第三轮实测表 #15-#19（本地 runtime 输出） | A/H/J 标签不存在 |
| 8 | K-F5 来源漂移 | ✅ §四 4.1 + 参数速查表修正（基础行动设计 §二/§三 数值 + 回合战斗流程 §6.2 自动触发） | 引用归属准确 |
| 9 | ℹ️ 组 | ✅ C-F4 消费措辞 / AC-13 0.2999f / issue 范围段 12 / §三 未定义行为补漏 | info 级一并清扫 |
| 10 | Δ审计 INFO 哨兵缺口 | ✅ AC-8 增精神 baseDamage=3 消费哨兵（写死 2f 实现必挂） | F2 修复的回归防线 |
| 11 | Δ审计 refute 措辞 | ✅ SDK 8.0.29 → runtime 8.0.29（SDK 8.0.423）全链修正；map.md floor(san/2) → 向下取至 0.1 | 事实性表述精确 |

## ⚠️ 结转清单（需在工作issue实现时验证）

| # | 结转项 | 目标 work issue |
|----|--------|----------------|
| 1 | types spec（csharp-engine-types）变更日志补 `🔧 修正` 行指向本 spec 偏差 B5——实现时执行（AC-18 承接） | damage 工作issue 01 |
| 2 | AC-5 miss 锚点 + AC-8 精神哨兵必须写测试——防「结算入 if(hit) 分支」「写死 2f」两类实现偏差 | damage 工作issue 01 |
| 3 | AC-17 重载探针按 spec 机制写（IsFloat 重载决议）——4 个 demo 模板字段的 int→float 变更靠它捕获 | damage 工作issue 01 |
| 4 | 现有 types 测试在新 float 类型下编译+通过验证（AC-18）；不改断言值；grep 复核全部现有断言值 ≤80 且在 f32 精确整数域 | damage 工作issue 01 |
| 5 | 22 字段 int→float 变更含 CalibrationConfig 4 demo 模板（PlayerHp/PlayerSan/NpcHp/NpcSan）——易漏点，实现后逐字段对照 §二 2.2 表 | damage 工作issue 01 |

## 结论

- [x] 批准 —— spec v1.1 可以进入实现阶段（工作issue 01）✅ 2026-08-13 dog
- [ ] 退回 —— 需要修改后重新审计

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [审计报告](report.md), [spec v1.1](../spec.md), [任务issue 01](../issues/01-damage-spec.md)*
