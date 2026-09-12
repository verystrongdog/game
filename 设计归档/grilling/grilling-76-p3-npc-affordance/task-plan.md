# Grilling #76 P3 NPC Affordance 全量 — 实施任务计划

> Grilling #76 (GitHub #76) 结论：NpcSalience 从 demo 占位升级为正式 Affordance Competition。4 项共识：数据文件+record 落点 / 基础行动+浮现技能候选集 / 规则全实现+目标框架 / E-4 全闭合+双模板。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [数据结构](#三数据结构)
4. [行动候选集](#四行动候选集)
5. [选择规则](#五选择规则)
6. [目标选择框架](#六目标选择框架)
7. [E-4 闭合清单](#七e-4-闭合清单)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

NPC AI 正典已完整定义（NPC AI 行为模型 §三/§四：Salience 公式 / tone_bias 权重表 / T_SAN / 7 参数化 / 6 标签映射表 / 目标选择 §7.2），但引擎 `NpcSalience.cs` 仍是 demo 占位（3 行动硬编码节点集 + FirstEnemy + 硬编码 baseline/tone_bias——plan §4.8 [NEW]）。P3 落地正式实现并闭合 E-4（#24 延迟项）。P1a 候选池 + P1b LinkState（NPC 静态 m 模板）+ P1c 通道映射 + P2 情境只读状态已就绪。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 7 参数落点 = `personality_tags.json`（6 标签→7 参数映射，§4.2 表落地）+ `NpcPersonality` record（Types/）+ per-participant baseline（战斗开始 tone = baseline） | 数据 |
| D2 | 候选集 = **3 基础行动（节点模板正式化）+ 已浮现技能**（NPC 静态 LinkState ∩ 涌现条件 m≥0.5 组 ≥2 边 ≥1 聚焦）；杂兵（m_default=0.3）→ 基础行动；Boss → 可浮现 | 规则 |
| D3 | 选择规则全实现（Boss argmax / 杂兵 Softmax + T_SAN 0/+0.10/+0.30/∞ + SAN=0 均匀随机）+ 恐慌配置占位（PanicToneShift [NEW] = NE+0.2/5HT−0.2，方向对齐 §9.1）+ **目标选择框架**（目标数组 → 目标 salience → argmax；四节点群全量留 P4e） | 规则 |
| D4 | E-4 全闭合：demo 占位全删；tone_bias 权重表 = 代码常量 `RoleToneWeights`（8×4，与 A6 sign **同源派生**）；Console 双模板（杂兵 Softmax / Boss argmax）对比验证 | 范围 |

## 三、数据结构

```csharp
// Types/NpcPersonality.cs（不可变——NPC 性格参数，NPC AI §4.1）
public sealed record NpcPersonality
{
    public float NeBaseline { get; init; }        // [0,1] 默认 0.3
    public float DaVtaBaseline { get; init; }     // [0,1] 默认 0.4
    public float DaSncBaseline { get; init; }     // [0,1] 默认 0.5
    public float Ht5Baseline { get; init; }       // [0,1] 默认 0.5
    public float BiasSomatic { get; init; }       // [-0.3,0.3] 默认 0
    public float BiasCognitive { get; init; }     // [-0.3,0.3] 默认 0
    public float BiasLimbic { get; init; }        // [-0.3,0.3] 默认 0
    public static NpcPersonality Default { get; } // 正常人默认（§4.1 表）
    public static NpcPersonality FromTags(IEnumerable<string> tags); // personality_tags.json 映射，多标签取 max()（§4.2）
}

// Engine/RoleToneWeights.cs（代码常量——NPC AI §3.3 表；与 A6 sign 同源派生 D4）
public static class RoleToneWeights
{
    // 8 role × 4 tone (NE, DA_VTA, DA_SNc, 5HT) 权重表（§3.3）
    // A6Sign(role) = sign(RoleToneWeights[role]) —— 单源，防两表漂移
}
```

```json
// data/connectivity/personality_tags.json（新建，NPC AI §4.2 表落地）
{
  "schema": "personality_tags", "version": 1,
  "tags": {
    "敏化-威胁":    {"tone": {"NE": 0.2, "5HT": -0.2}, "bias": {"limbic": 0.15}},
    "敏化-奖励":    {"tone": {"DA_VTA": 0.2, "5HT": -0.2}, "bias": {"limbic": 0.15}},
    "抑制不足":     {"tone": {"5HT": -0.2}, "bias": {"somatic": 0.15}},
    "过度抑制":     {"tone": {"5HT": 0.2}, "bias": {"somatic": -0.15}},
    "反刍":         {"tone": {"NE": -0.1}, "bias": {"cognitive": 0.15}},
    "社交钝化":     {"tone": {}, "bias": {"cognitive": -0.15}}
  }
}
```

**Per-participant baseline**：`ParticipantState` 增加 `NpcPersonality? Personality`（玩家 = null → 用角色默认/玩家角色数据）；战斗开始 `tone = baseline`；ToneUpdater 衰减目标 = baseline（替换 demo 硬编码常量）。

## 四、行动候选集

```
候选集(self) = 基础行动 3 个 ∪ 已浮现技能（self 的静态 LinkState）

基础行动模板（demo 节点集正式化，plan §4.8 节点 + fid 映射保留）:
  physical_attack: cortical_nodes = [Precentral] + SD1_somatic 代理（Putamen 代理，plan §十三-4）role=attack_physical
  mental_attack:   cortical_nodes = [RostralMiddleFrontalDLPFC, ParsOpercularis, AnteriorCingulateCortex] role=attack_mental
  defend:          cortical_nodes = [Insula, Amygdala] role=defend

已浮现技能: SkillCatalog 中满足涌现条件（组内 ≥2 边 m≥0.5 且 ≥1 聚焦）的候选技能
  NPC 的 LinkState = 静态模板（杂兵 m_default=0.3 → 无浮现；Boss/高级 NPC m 模板 → 可浮现，§10.1 敌我同构）
```

- 基础行动模板与 P1c SkillDefinition 同构（可统一为"行动定义"接口——基础行动 = 无 EdgeIds 的特殊 SkillDefinition 或独立 record）
- 通道映射复用 P1c 全表（M1/Broca）

## 五、选择规则

```
每回合 Phase 1 后，对每个候选行动 i:
  Salience_i = mean(a_j, j ∈ i.cortical_nodes) × gate_bonus_effective(role) × (1 + tone_bias(role))

  gate_bonus_effective(loop) = clamp(gate_loop + bias_loop, 0, 1)   // §4.1 bias 生效
  tone_bias(role) = Σ_t RoleToneWeights[role][t] × (tone_t − baseline_t)   // §3.3

选择:
  Boss（模板 difficulty 字段标记）→ argmax_i Salience_i          // 确定性
  杂兵 → Softmax P(i) ∝ exp(Salience_i / T)                      // 概率性
    T = T_base(0.15) + T_SAN（SAN%≥60: 0 / 30-59: +0.10 / <30: +0.30 / =0: ∞）

SAN 特殊状态:
  SAN<30%（恐慌）→ tone 临时偏移 PanicToneShift（[NEW] NE+0.2 / 5HT−0.2，§9.1 方向，数值待 #35）
  SAN=0 → 候选行动均匀随机（T=∞，§9.1/§3.4）
```

## 六、目标选择框架

```
目标候选 = 敌方参与者数组（demo 单目标——唯一敌方）
目标 salience（§7.2 简化版——单目标 = 恒 1）:
  框架: 目标数组 → 目标 salience → argmax 选目标
  四节点群（恐惧/奖赏/认知/社交）全量实现 → 推迟 P4e 多敌方
行动目标的通道目标（攻击 target / 防御自指）→ 复用 CombatAction.TargetId
```

## 七、E-4 闭合清单

| demo 占位 | 闭合方式 |
|-----------|---------|
| PhysicalNodes/MentalNodes/DefendNodes 硬编码 | → 基础行动模板（§四，正式定义） |
| FirstEnemy 单目标 | → 目标选择框架（§六） |
| 硬编码 BaselineNe/DaVta/DaSnc/Ht5 | → per-participant NpcPersonality（§三） |
| 硬编码 tone_bias 权重（0.3/0.5/-0.3 内联） | → RoleToneWeights 常量（§三） |
| plan §4.8 [NEW] 标注 | 摘除（issue #76 关闭后） |

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `NpcPersonality` record + `personality_tags.json` + `RoleToneWeights` 常量（含 A6Sign 派生） | 代码+数据 | `Types/NpcPersonality.cs` + `data/connectivity/personality_tags.json` + `Engine/RoleToneWeights.cs` | D1/D4 |
| T2 | per-participant baseline：`ParticipantState.Personality` + ToneUpdater 用 baseline 替代硬编码 | 代码 | `Types/ParticipantState.cs` + `Engine/ToneUpdater.cs` | T1 |
| T3 | 基础行动模板正式化 + 候选集构建（基础 + 浮现技能，NPC 静态 LinkState） | 代码 | `Types/ActionTemplate.cs`（或 SkillDefinition 扩展）+ `Engine/CandidateSetBuilder.cs` | T1 + P1a/P1b 产物 |
| T4 | `NpcSalience` 重写：Salience 全量公式 + bias 生效 + argmax/Softmax/T_SAN/恐慌配置/SAN=0 + 目标框架 | 代码 | `Engine/NpcSalience.cs` | T2/T3 |
| T5 | E-4 清理（删 demo 常量/FirstEnemy）+ plan [NEW] 标注摘除 | 代码 | `Engine/NpcSalience.cs` 净化 | T4 |
| T6 | Console demo 接线：标签→NPC 模板（杂兵 Softmax / Boss argmax）双模式对比 + salience 摘要显示 | 代码 | `YouAreNotTheFish.Console` | T5 |
| T7 | 测试（salience 公式逐项/tone_bias 8 角色/T_SAN 分段/恐慌偏移/argmax vs Softmax 分布/目标框架）+ 文档同步 | 测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T6 |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `src/YouAreNotTheFish.Core/Types/NpcPersonality.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Engine/RoleToneWeights.cs` | 新建 | 代码 |
| `data/connectivity/personality_tags.json` | 新建 | 数据 |
| `src/YouAreNotTheFish.Core/Engine/NpcSalience.cs` | 重写 | 代码 |
| `src/YouAreNotTheFish.Core/Types/ParticipantState.cs` + `Engine/ToneUpdater.cs` | 改写（baseline） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/CandidateSetBuilder.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `docs/决策树/` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- `personality_tags.json` 6 标签全；偏移量 ∈ §4.2 表（tone ±0.1~0.2 / bias ±0.15）；多标签取 max()（§4.2）
- `RoleToneWeights` 8 role × 4 tone 与 NPC AI §3.3 表逐值一致；`A6Sign(role) = sign(RoleToneWeights[role])` 单源
- gate_bonus_effective = clamp(gate + bias, 0, 1)；ToneUpdater 衰减目标 = per-participant baseline
- 确定性：NpcSalience 纯函数 + ctx.Rng 注入（Softmax 抽样），同种子同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| tone_bias 逐项 | 8 角色 × 4 tone 单测断言 |
| T_SAN 分段 | SAN 边界（60/30/0）单测 |
| argmax vs Softmax | Boss 同种子同行动；杂兵分布非退化 |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] NpcPersonality + personality_tags.json（6 标签）+ RoleToneWeights（与 A6 sign 同源）
- [ ] per-participant baseline 生效（ToneUpdater 无硬编码常量）
- [ ] 候选集 = 基础行动模板 + 已浮现技能（NPC 静态 LinkState）
- [ ] NpcSalience 全量：Salience 公式 + bias + argmax/Softmax/T_SAN/恐慌配置/SAN=0 + 目标框架
- [ ] E-4 闭合：demo 占位全删，[NEW] 标注摘除
- [ ] Console 双模板对比（杂兵 Softmax 分布 / Boss 确定性）可见
- [ ] 测试绿；决策树 #76 / 六维状态 / memory 落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 目标 salience 四节点群全量 | 1v1 无多目标 | P4e 多敌方 |
| 恐慌配置数值校准 | §9.1 无正典数值 | #35（PanicToneShift 解占位） |
| NPC 持久髓鞘化/跨战斗记忆 | Boss 跨战斗系统（NPC AI §六/§十一） | Boss 详细设计批次 |
| 多标签 max() 叠加验证 | 需 2-3 标签组合样例 | 敌人 Stat 实例批次 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [NPC AI 行为模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md), [运行时状态模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [Grilling #74 P1c task-plan](./../grilling-74-p1c-skill-execution/task-plan.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
