# #81 [Grilling] P4c 响应窗口进引擎 — L4 读意图 + 忍耐主动 + 叙事重构

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/81

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P4c：响应窗口（回合战斗流程 §六）落地引擎——IResponseResolver 从 Noop stub 实现为正式响应解析器（L4 读意图 / 忍耐·主动 / L5 叙事重构 B），闭合响应窗口 stub。

## 六维定位

- **维度**: 规则（响应语义/链路交互）+ 管线（引擎实现）
- **依赖**: 回合战斗流程 §六（4 种响应类型正典）+ 引擎 IResponseResolver 接口（已设计，Noop stub）+ DamageCalculator（L0 回避已在；忍耐被动参数）+ P1c（perceive 预留——L4 读意图是响应型感知技能）+ P1a/P3（"链路激活"语义）+ 基础行动设计（忍耐主动 CD2 占 Broca）
- **承接**: #70 路线图 P4c（响应窗口 stub 归属）+ E-2 残余

## 当前状态

- 正典（回合战斗流程 §6.2）4 种响应：
  - L0 趋向（回避）自动触发：被物理攻击瞄准 → 免费自动（引擎 DamageCalculator 已实现 -10% 命中 ✅）
  - L4 读意图：读意图链路已激活 + 目标在行动 → 声明后结算前调整自己的防御/行动（"已在占槽"）
  - 忍耐·主动：被精神攻击命中（声明后）→ 占 Broca 通道 CD2 → SAN 减免翻倍（-2 而非 -1）
  - L5 叙事重构 B（条件触发）：友方被伤害时 → 攻击 +25%（下个行动窗口生效）
- 边界（§6.3）：响应不取消对方行动——即时调整承受方式
- 引擎：IResponseResolver.Resolve(declared, state, ctx) → IReadOnlyList<CombatEvent>；NoopResponseResolver 恒空；ActionResolver 已注入

## 关键待决

1. 响应实现范围（L0 已有——L4/忍耐主动/叙事重构 B 本批实现？）
2. "链路激活"语义（L4 读意图触发条件：a(t) 驱动 vs 技能状态）
3. 忍耐·主动实现（响应时占 Broca + SAN 减免翻倍——DamageCalculator 忍耐参数接入）
4. L5 叙事重构 B（友方受伤 → 攻击 +25% 下窗口）+ "防御主动"澄清（#70 范围表提及——正典无此名词）

## 预期产出

- `.scratch/grilling-81-p4c-response-window/task-plan.md` + 决策树 + 六维状态 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #81 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | 三响应全实现（L4/忍耐主动/叙事重构 B）；L0 保持现状 | ResponseResolver |
| D2 | L4 a(t) 驱动（社会认知节点阈值）+ 自动防御无冷却 | SocialCognitionNodes |
| D3 | 忍耐主动自动触发（CD=0+Broca 未用）+ 减免翻倍 + CD2 | DamageCalculator |
| D4 | 叙事重构 B 条件触发 → NarrativeBoost（下窗口+25%）；"防御主动"判为表述残留 | StatusKind |

### 受影响文件

- `.scratch/grilling-81-p4c-response-window/task-plan.md`（新建）
- `规则/回合战斗流程.md`（§6.2 补注）✅ 已写入
- `docs/决策树.md`（#81）、`docs/设计框架-六维状态.md`（P4c ✅——**P4 全部闭合**）、memory
- 实施后：ResponseResolver + SocialCognitionNodes + DamageCalculator + StatusKind.NarrativeBoost + CombatState + CalibrationConfig(+2 [NEW]) + Console/Tests

### 推迟清单

- 响应选择 UI → 战斗界面；L5 控制 → L5 技能批次；NPC 响应策略 → NPC 精细化；阈值 → #35

### 质量门禁

- 4 决策全落位；响应 stub 闭合条件齐备；P4 设计全部闭合（里程碑）
- 后续：T2-T6 实施

---
*导出: 2026-09-12 | 来源: GitHub issue*
