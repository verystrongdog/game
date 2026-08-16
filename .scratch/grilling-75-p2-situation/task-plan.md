# Grilling #75 P2 情境系统进引擎 — 实施任务计划

> Grilling #75 (GitHub #75) 结论：情境系统进引擎——α_patterns 数据化 + 27 原型选择器 + s_env/m_field 三通道 + 情境只读状态接口。4 项共识：事件/持续场分离 / 映射表+SAN 调制+节点注入 / 三通道并入 s 数组 / 隐式涌现+只读接口。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [数据文件](#三数据文件)
4. [情境选择器](#四情境选择器)
5. [三通道输入落点](#五三通道输入落点)
6. [情境只读状态接口](#六情境只读状态接口)
7. [任务分解](#七任务分解)
8. [文件清单](#八文件清单)
9. [数据契约与校验](#九数据契约与校验)
10. [验收标准](#十验收标准)
11. [推迟清单](#十一推迟清单)

---

## 一、背景与动机

#69 确立 s(t) 三通道语义（s_事件/s_env/m_field）与 D9（α pattern 数据化），但实施未落地：EventProcessor 仍硬编码 6 元素 α pattern（`EventProcessor.cs:123` `new[] {1,0,1,0,0,0}`）；situation_primitives.json（27 原型）已加载但 demo 未消费（引擎数据关系规格 §六 接缝 🔶）；W_sensory 仍 69×6。P2 落地情境系统，为 P3 NPC 全量提供情境输入。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 事件/持续场分离：`alpha_patterns.json` 只放 14 战斗事件（#69 schema 原样，8 模态）；`env_tones.json` 独立放环境基调 α_env（空间类型 → 8 模态强度） | 数据 |
| D2 | 情境选择器 = 空间→原型映射表（`typical_game_scenario` 辅助建表）+ 低 SAN 概率偏移（恐慌→诡异/负面原型）+ **key_brain_regions 直接节点注入**（心理情境非感官，不走 W_sensory）+ 刷新时机 = 空间切换 + SAN 阈值跨越（C1） | 算法 |
| D3 | 三通道并入 s 数组：`s_total[69] = s_事件 + s_env + m_field`（m_field 占位全 0）——`WcDynamics.Step` 签名零改动；正典文档层写 `h = ΣW·a + b + s_total`；m_field 节点落点 #38 后填 | 落点 |
| D4 | 情境 salience = 隐式涌现（原型注入 → a(t) → salience 自然反映，不查表）+ **只读情境状态接口**（当前原型 id + 强度，供 P3/UI/叙事） | 接口 |

## 三、数据文件

### 3.1 `data/connectivity/alpha_patterns.json`（新建，#69 D9 落地）

```json
{
  "schema": "alpha_patterns", "version": 1,
  "modalities": ["visual","auditory","somatosensory","pain","social_cognition","language_cognition","olfactory","thermoreception"],
  "events": {
    "A1": {"trigger": "物理攻击命中", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A2": {"trigger": "被格挡/闪避", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A3": {"trigger": "物理暴击", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A4": {"trigger": "精神攻击执行", "pattern": [0,0,0,0,1,1,0,0], "m_alpha": 1.0},
    "A5": {"trigger": "防御成功", "pattern": [0,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A6": {"trigger": "技能使用成功", "pattern": [0,0,0,0,0,0,0,0], "m_alpha": 0.0},
    "A7": {"trigger": "逃跑", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "B1": {"trigger": "被物理击中", "pattern": [1,0,1,1,0,0,0,0], "m_alpha": "m"},
    "B2": {"trigger": "闪避/格挡", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": "m"},
    "B3": {"trigger": "被暴击", "pattern": [1,0,1,1,0,0,0,0], "m_alpha": "m"},
    "B4": {"trigger": "被精神攻击", "pattern": [0,0,0,1,1,1,0,0], "m_alpha": "m"},
    "C1": {"trigger": "SAN<30%", "pattern": [0,0,0,1,0,0,0,0], "m_alpha": 1.0},
    "D1": {"trigger": "队友倒下", "pattern": [1,1,0,0,1,0,0,0], "m_alpha": 1.0},
    "D2": {"trigger": "敌人倒下", "pattern": [1,1,0,0,1,0,0,0], "m_alpha": 1.0}
  }
}
```

- pattern 前 6 位 = 现有硬编码值原样迁移；末 2 位（嗅觉/热觉）战斗事件补 0
- `m_alpha` 沿用 A 类 1.0 / B·C·D 类 m 语义（#69 schema）

### 3.2 `data/connectivity/env_tones.json`（新建，环境基调）

```json
{
  "schema": "env_tones", "version": 1,
  "modalities": ["visual","auditory","somatosensory","pain","social_cognition","language_cognition","olfactory","thermoreception"],
  "environments": {
    "病房":     {"alpha_env": [0.3, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2]},
    "走廊":     {"alpha_env": [0.4, 0.3, 0.1, 0.0, 0.1, 0.0, 0.2, 0.1]},
    "护士站":   {"alpha_env": [0.6, 0.4, 0.1, 0.0, 0.3, 0.2, 0.3, 0.2]},
    "...": "..."
  }
}
```

- 环境类型初版 = 空间与关卡设计的地图元素（病房/走廊/活动室/楼梯间/户外等），具体表值 = 设计层 [NEW] 可调
- 初始值由空间 grilling/内容填充补充；P2 提供 schema + demo 2-3 个环境

### 3.3 W_sensory 扩列 69×8

`W_sensory.json` 追加 olfactory/thermoreception 两列（#69 D4' 已定；原 6 列数据逐位不变）——嗅觉锚点：梨状皮层/OFC；热觉锚点：躯体感觉皮层温度区（#69 task-plan §4.2）。

## 四、情境选择器

```
SituationSelector.Select(environment, sanState, rng) → (archetypeId, strength)

1. 空间→原型候选池: env_map[environment] = {primary: archetypeId, alternates: [id...]}
   （typical_game_scenario 字段辅助人工建表；demo 覆盖主要空间类型）
2. SAN 调制: san < 30%（恐慌）→ 以 p_panic 概率从候选池偏移到"诡异/负面"原型
   （原型按 rdoc_profile.negative_valence / appraisal valence=negative 分组）
   p_panic = CalibrationConfig.SituationPanicShift [NEW] 初始 0.5
3. 刷新时机: 空间切换 + C1 事件（SAN 阈值跨越）→ 重选
4. 输出: 原型 id + 强度（原型注入强度 = 1.0 基础，SAN 越低越强 [NEW] 系数可调）
```

**神经落点（直接节点注入）**：

```
key_brain_regions（规范名）→ functional_id 集（normalize_region_names 工具扩展）
选中原型 → s_env_j += 强度 for j ∈ 原型 fid 集（直接节点驱动，非 W_sensory 展开）
```

- `key_brain_regions` 混合 fid/dk 名（如 SupramarginalTPJ=fid、Amygdala=dk）→ 规范名映射表（复用 region_name_map + normalize 经验，100% 命中目标）

## 五、三通道输入落点

```
s_total[69] = s_事件（EventProcessor 现有路径，读 alpha_patterns.json）
            + s_env（环境基调: W_sensory × α_env + 情境原型节点注入）
            + m_field（月光场: 占位全 0，CalibrationConfig.MFieldStrength = 0 [NEW]，#38 后填节点落点）

h_j = Σ W·a + b_j + s_total_j        （文档层公式；引擎 WcDynamics.Step 签名不变）
```

- s 累加归 CombatState.SPending（现有机制）；s_env 在空间切换时刷新为稳定值（#69 D7 时序）
- `CurrentEnvironment`（字符串/枚举）传入 CombatState（demo 由 Console 指定；战斗外空间切换由上层驱动）

## 六、情境只读状态接口

```csharp
// Entity/CombatState.cs
public SituationState Situation { get; }   // 只读——当前情境原型 id + 强度 + 环境 id
public sealed record SituationState(string ArchetypeId, float Strength, string EnvironmentId);
```

- 消费方：P3 NPC 行为偏置参考（非 salience 乘子）、UI 情境标签、叙事、玩家观察
- 战斗内刷新：空间切换（战斗外）+ C1 事件（战斗内重选）

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | W_sensory.json 扩列 69×8（嗅觉/热觉，原 6 列不变） | 数据 | `W_sensory.json` | D1 |
| T2 | alpha_patterns.json（14 事件迁移 8 模态）+ EventProcessor 去硬编码（读 JSON） | 数据+代码 | `alpha_patterns.json` + `EventProcessor.cs` | T1 |
| T3 | env_tones.json（空间→8 模态 α_env，demo 2-3 环境） | 数据 | `env_tones.json` | D1 |
| T4 | key_brain_regions 规范名映射（→ fid 集，扩展 normalize_region_names 或新工具） | 代码 | 映射工具 + 27 原型 fid 集验证 | T3 |
| T5 | SituationSelector（env_map + SAN 调制 + 刷新时机 + 节点注入）+ `CurrentEnvironment` 传入 | 代码 | `Engine/SituationSelector.cs` + `CombatState.Situation` | T4 |
| T6 | 三通道累加（s_total）+ m_field 占位（MFieldStrength=0）+ 只读 SituationState | 代码 | `CombatState.SPending` 扩展 + `CalibrationConfig` | T2/T5 |
| T7 | Console demo 接线（指定环境 → 情境显示 + s 注入效果）+ 测试 + 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T5/T6 |

## 八、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/connectivity/W_sensory.json` | 改写（+2 模态列） | 数据 |
| `data/connectivity/alpha_patterns.json` | 新建 | 数据 |
| `data/connectivity/env_tones.json` | 新建 | 数据 |
| `src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` | 改写（读 JSON 去硬编码） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/SituationSelector.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（Situation + s_total） | 代码 |
| `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+SituationPanicShift/MFieldStrength [NEW]） | 代码 |
| `tools/`（规范名映射扩展） | 改写 | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `docs/决策树.md` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 九、数据契约与校验

### 不变量

- `alpha_patterns.json` pattern 前 6 位 = 现有硬编码逐位一致（迁移防错位）
- `W_sensory` 69×8 行序 = canonical 69（C1 约束延续）；原 6 列数据逐位不变
- `env_tones.json` 模态列表与 alpha_patterns 一致（8 模态）
- 情境注入：s_total ∈ 合理范围（s_env + 原型注入叠加，W·a+b+s 输入范围由 sigmoid 自然饱和）
- 确定性：SituationSelector 用注入 RNG（SAN 调制概率），同种子同选择

### 校验

| 校验 | 命令 |
|------|------|
| α pattern 迁移比对 | 迁移前后 6 位逐位比对（脚本） |
| W_sensory 形状 | 69×8 断言（validate 工具扩展） |
| key_brain_regions 映射 | 27 原型 fid 集 100% 命中报告 |
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十、验收标准

- [ ] W_sensory 69×8（原 6 列逐位不变）；alpha_patterns.json 14 事件（前 6 位与现有一致）
- [ ] EventProcessor 无硬编码 α pattern，全部读 JSON
- [ ] env_tones.json schema + demo 环境；SituationSelector 空间映射 + SAN 调制 + 刷新生效
- [ ] key_brain_regions → fid 集 100% 命中（27 原型）
- [ ] s_total = s_事件 + s_env + m_field（m_field 占位 0）；SituationState 只读接口可用
- [ ] Console demo 指定环境 → 情境显示 + s 注入后 a(t) 变化可见
- [ ] 测试绿；决策树 #75 / 六维状态 / memory 落位

## 十一、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| m_field 参数集与节点落点 | #38 月光场重建开放中 | #38 闭合后填（MFieldStrength 解占位） |
| env_tones 全环境表值 | 空间内容未全设计 | 空间 grilling/内容填充 |
| 情境原型 SAN 偏移分组表（诡异/负面分组） | 需 27 原型逐条标注 | 本批提供分组规则，标注随内容填充 |
| 情境强度系数校准 | 无正典值 | #35 数值校准 |
| 白天无月光渗透过渡态 | 空间遭遇规则延迟项 | 独立话题 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #69 task-plan](./../grilling-69-external-stimulus/task-plan.md), [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [运行时状态模型](./../../规则/技能树系统/运行时状态模型.md), [situation_primitives.json](./../../data/connectivity/situation_primitives.json), [核心机制](./../../规则/核心机制.md), [数学语言书写规范](./../../docs/agents/math-language-writing.md)*
