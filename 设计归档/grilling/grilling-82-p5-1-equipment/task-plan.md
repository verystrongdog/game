# Grilling #82 P5-1 武器与护甲进引擎 — 实施任务计划

> Grilling #82 (GitHub #82) 结论：武器/护甲系统落地引擎。4 项共识：equipment.json 数据+槽位校验 / 数值类全实现+4 简单状态 / 精神武器结构+m 阈值校验+效果接口预留 / EquipmentSet 构建层→战斗快照+demo。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [装备数据与槽位](#三装备数据与槽位)
4. [数值集成](#四数值集成)
5. [简单状态实现](#五简单状态实现)
6. [精神武器](#六精神武器)
7. [任务分解](#七任务分解)
8. [文件清单](#八文件清单)
9. [数据契约与校验](#九数据契约与校验)
10. [验收标准](#十验收标准)
11. [推迟清单](#十一推迟清单)

---

## 一、背景与动机

武器与装备.md 正典完整（11 物理武器 + 25 护甲 + 12 精神武器 + Boss 6 件），引擎 DamageCalculator 已有 weaponBonus 参数（#24 核查）但无装备数据结构/槽位。P5-1 落地：数值公式集成 + 效果框架建立。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | `equipment.json` [NEW] 数据文件（11+25+12 全量）+ 槽位校验（主手/副手/饰品×5/精神防护——正典 §4.1）+ 构建层→战斗快照 | 数据 |
| D2 | 数值类全实现（weapon_bonus/hit_mod/被动减伤/SAN 阈值偏移/equipment_SAN/HP/防御替换）+ **4 简单状态**（流血 DoT/暴击+10%/反伤/命中 debuff）；复杂效果接口预留 | 范围 |
| D3 | 精神武器 = 数据 + **m 阈值校验**（P1b LinkState）+ 占 M1 校验 + 12 件效果接口预留（demo no-op 标注） | 范围 |
| D4 | `EquipmentSet` 构建层（槽位→装备 id）→ CombatState 快照（与 LinkState/FocusSet 同模式）+ DamageCalculator 全接入 + Console demo | 落点 |

## 三、装备数据与槽位

### 3.1 `data/equipment.json`（新建）

```json
{
  "schema": "equipment", "version": 1,
  "weapons": [
    {"id": "iv_stand", "name": "输液架", "slot": "main_hand", "type": "长杆",
     "damage": 2, "hit": -0.05, "range": "near", "effects": ["range_near"]},
    {"id": "scalpel", "name": "手术刀", "slot": "main_hand", "type": "轻型锐器",
     "damage": 1, "hit": 0.10, "effects": ["bleed_3t_1hp"]},
    {"id": "tray", "name": "金属托盘", "slot": "off_hand", "type": "盾类",
     "damage": 1, "hit": 0.0, "effects": ["block_extra_10"]}
  ],
  "armors": [
    {"id": "straitjacket", "name": "约束衣", "slot": "accessory_torso",
     "passive_reduction": 0.10, "san_threshold_shift": 0.05, "san": 1, "hp": 1,
     "effects": ["perception_penalty_2"]}
  ],
  "mental_weapons": [
    {"id": "screen_of_edmund", "name": "埃蒙·安德鲁斯的银幕",
     "m_threshold": 0.5, "m_edge": "cc:NNN", "cooldown": 5, "channel": "m1+broca",
     "effects": ["force_attack_target"]}
  ]
}
```

- 槽位枚举：`MainHand / OffHand / AccessoryHead / AccessoryTorso / AccessoryArm / AccessoryHand / AccessoryLeg / Mental`
- 校验（§4.1）：盾类占 OffHand 与副手武器互斥；同部位 1 件；精神防护不互斥

### 3.2 EquipmentSet 构建层

```csharp
public sealed record EquipmentSet(IReadOnlyDictionary<EquipmentSlot, string> SlotToItemId);
// 构建层配置（非战斗）→ CombatState 创建时传入（与 LinkState/FocusSet 同参数模式）
```

## 四、数值集成

```
物理伤害 = (4 + weapon_bonus) × (1 + force_mod + motivation_mod)   // DamageCalculator 已有 weaponBonus 参数
命中率   = 85% + weapon_hit_mod + 链路命中调制                      // hit 判定接入 weapon_hit_mod
总物理减伤 = 主动防御(−50% 或盾替换 −70%) + Σ 被动减伤              // 累加无上限（§1.4）
SAN 恐慌阈值偏移 = Σ 各护甲偏移（累加，§1.5）
SAN_max = SAN_base + link_SAN + equipment_SAN                      // equipment_SAN 接入（核心机制 §5.0）
HP_max  = HP_base + equipment_HP
```

## 五、简单状态实现（4 个）

| 效果 | 来源 | 实现 |
|------|------|------|
| 流血 DoT | 手术刀 | `StatusKind.Bleed`（3 回合 1 HP/回合，窗口结束结算） |
| 暴击 +10% | 手术刀"找缝" | crit_rate 计算 +0.10（P4d 暴击接入——不与识别/读意图叠加，取高） |
| 反伤 1 HP | 铁丝网护臂 | 近战命中攻击者时反伤（物理攻击结算后） |
| 命中 debuff | 约束带 | 目标下次 M1 命中 −10%（一窗口后消失） |

- 效果类型枚举 `EffectKind` 建立（数值类/简单状态/预留）；复杂效果（灭火器 AOE/破门/免疫/移动力/武器解锁 §三）接口字段预留

## 六、精神武器

```
装备校验: LinkState.M[m_edge] ≥ m_threshold（P1b 衔接——药物临时调制可临时达标）
使用校验: 占 M1 通道（与物理攻击互斥）+ 冷却
效果: 12 件全部接口预留（EffectKind 枚举扩展——force_attack/observer_mode/delayed_damage/freeze 等）
  demo: no-op 标注（效果描述保留在数据，引擎不实现——随状态系统扩展批次）
```

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `equipment.json`（11 武器 + 25 护甲 + 12 精神武器数据全量） | 数据 | `data/equipment.json` | D1 |
| T2 | `Equipment` 数据 + 槽位校验 + `EquipmentSet` | 代码 | `Types/Equipment.cs` + `Types/EquipmentSet.cs` | T1 |
| T3 | DamageCalculator 数值接入（weapon_bonus/hit_mod/减伤累加/阈值偏移/equipment_SAN/HP） | 代码 | `Engine/DamageCalculator.cs` + `Entity/CombatState.cs`（SAN_max/HP_max） | T2 |
| T4 | 简单状态 4 个（流血/暴击+10%/反伤/命中 debuff）+ EffectKind 枚举 | 代码 | `Types/Enums.cs` + `Engine/StatusEffects.cs` | T3 |
| T5 | 精神武器：m 阈值校验（P1b LinkState）+ M1 占用 + 冷却 + 效果接口 | 代码 | `Engine/MentalWeaponResolver.cs` | T2 + P1b |
| T6 | Console demo：`equip <名称>` / `unequip <槽位>` + 伤害/减伤/阈值显示 + 状态触发日志 | 代码 | `YouAreNotTheFish.Console` | T3-T5 |
| T7 | 测试 + 决策树/六维状态/memory | 测试+文档 | 测试绿 + 文档 | T1-T6 |

## 八、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/equipment.json` | 新建 | 数据 |
| `src/YouAreNotTheFish.Core/Types/Equipment.cs` + `EquipmentSet.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` | 改写（数值接入） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/StatusEffects.cs` | 新建（简单状态） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/MentalWeaponResolver.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Types/Enums.cs`（EquipmentSlot/EffectKind/StatusKind） | 改写 | 代码 |
| `src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（EquipmentSet/SAN_max/HP_max） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `docs/决策树/` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 九、数据契约与校验

### 不变量

- 槽位互斥（§4.1）：盾类 OffHand vs 副手武器；同部位 1 件
- 伤害公式与正典一致：(4+weapon_bonus)×(1+force+motivation)；weapon_bonus ∈ [0,6]
- 被动减伤累加无上限；SAN 阈值偏移累加；equipment_SAN/HP 接入上限公式
- 精神武器：m 阈值校验（P1b）+ M1 占用 + 冷却；效果 no-op（接口预留）
- 确定性：装备为构建层快照（战斗中不变），同输入同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| 槽位冲突 | 双主手/副手冲突 单测 |
| 数值公式 | weapon_bonus/减伤累加/阈值偏移 单测 |
| 简单状态 | 流血回合结算/暴击+10%/反伤/debuff 单测 |
| 精神武器 | m 阈值边界/M1 占用/冷却 单测 |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十、验收标准

- [ ] equipment.json 全量（11+25+12）；槽位校验生效
- [ ] DamageCalculator 数值接入完整（伤害/命中/减伤/阈值/上限）
- [ ] 4 简单状态实现 + EffectKind 枚举建立
- [ ] 精神武器 m 阈值校验 + M1 占用 + 冷却 + 效果接口
- [ ] EquipmentSet 构建层→战斗快照；Console demo equip/unequip 可用
- [ ] 测试绿；决策树 #82 / 六维状态 / memory 落位

## 十一、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 复杂效果（灭火器 AOE/破门/免疫/移动力修正） | 状态系统扩展超实体批次范围 | 状态系统扩展批次 |
| 武器链路解锁（§三 m 阈值解锁效果） | 依赖 P1b LinkState + L 级边 m 查询 | P1b 实施后 |
| 精神武器 12 件效果 | 复杂状态（强制攻击/观察者模式/延迟伤害） | 状态系统扩展批次 |
| 稀有/Boss 专属装备效果 | 数值类同构，特殊效果后置 | Boss 设计批次 |
| 装备数值校准（equipment_SAN/HP 占位 +1） | 正典占位值 | #35 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [武器与装备](../../../%E5%AE%9E%E4%BD%93/%E6%AD%A6%E5%99%A8%E4%B8%8E%E8%A3%85%E5%A4%87.md), [核心机制](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [Grilling #73 P1b task-plan](./../grilling-73-p1b-linkstate/task-plan.md), [Grilling #77 P4d task-plan](./../grilling-77-p4d-crit/task-plan.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
