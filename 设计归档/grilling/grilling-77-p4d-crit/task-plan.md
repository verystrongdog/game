# Grilling #77 P4d 暴击机制补全 — 实施任务计划

> Grilling #77 (GitHub #77) 结论：补全暴击机制规则空缺（F-3）。4 项共识：a(t) 执行强度驱动物理暴击（精神无随机）/ ×1.5 + A3/B3 接线 / L4 识别主动观察+弱点状态（物理 crit+15%、精神 SAN+50%）/ 初始值 [NEW] 全落点 + 正典 3 处。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [暴击规则正典](#三暴击规则正典)
4. [弱点状态机制](#四弱点状态机制)
5. [A3/B3 事件接线](#五a3b3-事件接线)
6. [参数速查（[NEW]）](#六参数速查new)
7. [任务分解](#七任务分解)
8. [正典写入清单](#八正典写入清单)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

F-3 发现：全规则库仅「L4 识别揭示物理弱点→暴击率↑」效果方向（基础行动设计 L123 / 核心机制 L300），无暴击率基线/倍率/触发判定正典。A3/B3 暴击事件 pattern 已定义（运行时 §4.5/§5.5）但无触发源——E-2 的 A3/B3 无法落地根因。本批补全规则并接线引擎。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 物理暴击 = **a(t) 执行强度驱动**：`crit_rate = clip(base_crit + k_crit × (a_exec − θ_crit), 0, cap)`，`a_exec = mean(a(Precentral), a_SD1_somatic)`（速度执行分同源）；**精神无随机暴击**（用户裁定：永远命中+随机=双重随机粗糙） | 规则 |
| D2 | 效果 = 物理暴击伤害 ×1.5（倍率最后乘：基础 → gate×防御 → ×1.5 → 量化）；暴击判定通过 emit **A3+B3**；精神增强 = 确定性弱点状态 | 规则 |
| D3 | L4 识别 = 主动观察动作（占行动窗口 1 动作，**不占 M1/Broca 通道**——bypass gate）+ 弱点状态：物理弱点 → 对目标 crit+15%、精神弱点 → 精神攻击 SAN +50%、持续 2 回合 | 规则 |
| D4 | 初始值全 [NEW] 待 #35（base_crit 0.05/θ_crit 0.6/k_crit 0.5/cap 0.30）；引擎落点 = DamageCalculator/EventProcessor/StatusKind/识别技能；正典 3 处写入 | 范围 |

## 三、暴击规则正典

```
物理攻击暴击（新增段，基础行动设计 §二）:

命中判定（85% − 回避等修正）通过后 → 暴击判定:
  crit_rate = clip(base_crit + k_crit × (a_exec − θ_crit), 0, cap)
  a_exec = mean(a(Precentral), a_SD1_somatic)     —— 速度执行分同源（越出力越易暴击）

暴击效果:
  伤害 = round1(基础伤害 × gate × 防御 × 1.5)      —— 倍率最后乘，之后一位小数量化
  暴击事件: emit A3（暴击者）+ B3（被暴击者）       —— §五

精神攻击（无随机暴击）:
  永远命中 → 无暴击判定；"效果↑" = 弱点状态机制（§四）——确定性

精神弱点目标的低 SAN 穿透仍照常（×1.3/×2 与弱点 +50% 叠加，互不冲突）
```

## 四、弱点状态机制

```
L4 识别（perceive 技能，P1c 效果类型扩展）:
  执行 = 主动观察动作（占行动窗口 1 动作，不占 M1/Broca——bypass gate，运行时 §6.5）
  选择: 揭示物理弱点 → 目标 StatusKind.PhysicalWeakness
        揭示精神弱点 → 目标 StatusKind.MentalWeakness

状态效果（持续 WeaknessDuration 回合 [NEW] = 2）:
  PhysicalWeakness: 攻击者对目标 crit_rate + WeaknessCritBonus [NEW] = +0.15
  MentalWeakness:   精神攻击对该目标 SAN 伤害 ×1.5（确定性）

状态刷新: 重复识别刷新持续时间；弱点状态与 L3 身体感知"揭示弱点→伤害+2"并存（不同机制）
```

## 五、A3/B3 事件接线

```
触发源（E-2 A3/B3 闭环，#70 归属）:
  物理暴击判定通过 → 结算伤害后 emit:
    A3（暴击者）: δ (0,+1,+1,0) + α [1,0,1,0,0,0,0,0]（视觉+躯体）——m = actual/expected
    B3（被暴击者）: δ (1,0,0,−1) + α [1,0,1,1,0,0,0,0]（视觉+听觉+躯体+痛觉）——m = |ΔHP|/HP_max

EventProcessor: A3/B3 与 A1/B1 同路径（δ 实时注入 + s 打包）——A3 在 A1 后追加 emit
```

## 六、参数速查（[NEW]）

| 参数 | 符号 | 初始值 | 位置 |
|------|------|--------|------|
| 基础暴击率 | base_crit | 0.05 [NEW] | CalibrationConfig |
| 暴击阈值 | θ_crit | 0.6 [NEW] | CalibrationConfig |
| 暴击斜率 | k_crit | 0.5 [NEW] | CalibrationConfig |
| 暴击率上限 | cap | 0.30 [NEW] | CalibrationConfig |
| 暴击倍率 | — | ×1.5 [NEW] | DamageCalculator |
| 弱点暴击修正 | WeaknessCritBonus | +0.15 [NEW] | CalibrationConfig |
| 精神弱点效果 | — | SAN ×1.5 [NEW] | DamageCalculator |
| 弱点持续 | WeaknessDuration | 2 回合 [NEW] | CalibrationConfig |

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | 正典写入 3 处（§八） | 文档 | 基础行动设计/核心机制/运行时状态模型 | D1-D4 |
| T2 | `DamageCalculator` 暴击判定（物理：命中后 crit_rate → ×1.5）+ 弱点修正接入 | 代码 | `Engine/DamageCalculator.cs` | T1 |
| T3 | `EventProcessor` A3/B3 接线（暴击事件 → δ/α 注入） | 代码 | `Engine/EventProcessor.cs` | T2 |
| T4 | 弱点状态：`StatusKind.PhysicalWeakness/MentalWeakness` + 持续回合计时 | 代码 | `Types/Enums.cs` + `Entity/CombatState.cs` | T2 |
| T5 | L4 识别技能效果（P1c 效果类型扩展：perceive 无通道动作 + 弱点揭示） | 代码 | `Engine/SkillResolver.cs`（扩展） | T4 + P1c |
| T6 | 测试（crit_rate 公式/边界/×1.5 量化/A3/B3 emit/弱点持续与刷新/识别动作）+ 决策树/六维状态/memory | 测试+文档 | 测试绿 + 文档 | T1-T5 |

## 八、正典写入清单

| 文件 | 位置 | 内容 |
|------|------|------|
| `规则/技能树系统/操作层/基础行动设计.md` | §二 物理攻击 | 新增「暴击判定」段（crit_rate 公式/×1.5/A3B3 触发）；§三 L4 识别行细化（主动观察/弱点状态引用） |
| `规则/核心机制.md` | §4.2 | 暴击公式 + 参数速查新增暴击行 |
| `规则/技能树系统/运行时状态模型.md` | §5.5 | A3/B3 行补触发源注（物理暴击判定通过；A3 追加于 A1 后） |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `规则/技能树系统/操作层/基础行动设计.md` | 改写（暴击段） | 文档 |
| `规则/核心机制.md` | 改写（§4.2 + 速查） | 文档 |
| `规则/技能树系统/运行时状态模型.md` | 改写（§5.5 注） | 文档 |
| `src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` | 改写（暴击） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` | 改写（A3/B3） | 代码 |
| `src/YouAreNotTheFish.Core/Types/Enums.cs` + `Entity/CombatState.cs` | 改写（弱点状态） | 代码 |
| `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+5 [NEW] 参数） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/SkillResolver.cs` | 改写（识别效果） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `docs/决策树.md` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- crit_rate ∈ [0, cap]（clip）；a_exec 用速度执行分同源节点（Precentral + SD1_somatic）
- 结算顺序：基础 → gate × 防御 → ×1.5 → round1 量化（一位小数契约延续）
- 精神攻击无暴击判定（永远命中 + 弱点确定性 +50%）
- 弱点状态：持续 WeaknessDuration 回合、重复识别刷新、物理/精神独立
- A3/B3 emit：物理暴击判定通过必然 emit（事件不丢失）

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| crit_rate 边界 | base/θ/k/cap 单测（a_exec 低→base，高→cap） |
| ×1.5 量化 | round1 后一位小数断言 |
| A3/B3 | 暴击时事件列表含 A3+B3；δ/α pattern 断言 |
| 弱点状态 | 持续/刷新/精神 ×1.5 单测 |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] 正典 3 处写入完成（基础行动设计暴击段/核心机制 §4.2/运行时 §5.5 触发注）
- [ ] DamageCalculator 物理暴击判定 + ×1.5 + 弱点修正；精神无暴击判定
- [ ] EventProcessor A3/B3 接线（E-2 闭环）
- [ ] 弱点状态（物理/精神/持续/刷新）生效
- [ ] L4 识别技能（perceive 无通道动作 + 弱点揭示）可用
- [ ] 测试绿；决策树 #77 / 六维状态（规则空缺 F-3 闭合）/ memory 落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 暴击参数校准（base/θ/k/cap/弱点值） | 初始值为 [NEW] | #35 数值校准 |
| 弱点状态 UI 显示 | 呈现层 | 状态面板细部 grilling |
| 暴击在 NPC 侧的可读性 | NPC 信息展示 | 战斗界面 grilling |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [基础行动设计](./../../规则/技能树系统/操作层/基础行动设计.md), [核心机制](./../../规则/核心机制.md), [运行时状态模型](./../../规则/技能树系统/运行时状态模型.md), [Grilling #74 P1c task-plan](./../grilling-74-p1c-skill-execution/task-plan.md), [数学语言书写规范](./../../docs/agents/math-language-writing.md)*
