# Grilling #73 P1b LinkState + m 成长进引擎 — 实施任务计划

> Grilling #73 (GitHub #73) 结论：把髓鞘化 m 从 demo 常量升级为三体边级 LinkState。5 项共识：CC+PP 载体 / §10.3 层级表 max 初始值 / P1a 角色分类驱动 Δm 激活（g(n) 单场）/ 引擎巩固结算接口 / Build(data, LinkState, FocusSet) 独立参数。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [LinkState 数据结构](#三linkstate-数据结构)
4. [m 初始化规则](#四m-初始化规则)
5. [Δm 结算规则](#五δm-结算规则)
6. [可塑性巩固接口](#六可塑性巩固接口)
7. [聚焦接口与 Build 签名](#七聚焦接口与-build-签名)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

引擎 demo 阶段 m_mean ≡ `CalibrationConfig.Default.MDefault = 0.3`（`WMatrixBuilder.cs:63` B4 偏差声明），focus ≡ 1.0，`LinkGrowthEvent` 存在但 EventProcessor no-op——髓鞘化成长（核心机制 §1.3）、可塑性巩固（§八）、聚焦（§2.2）全部未进引擎。P1b 把 m 升级为构建层慢变量（运行时状态模型 §三：「m 是构建层慢变量，战斗中不变」），是 P1c 技能执行 / P5 装备消耗品（调制 m）/ 数值平衡工具 T3（Δm 引擎内验证）的共同基础。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | m 载体 = **CC + PP 边（888 条）**——与 P1a 边集一致；brainstem/CSTC 权重由 role/常量表定（运行时 §5.6/§6.3），无使用频率语义 | 范围 |
| D2 | m 初始值 = **核心机制 §10.3 层级表中值**，边层级 = `max(source.L, target.L)`；角色疾病偏移后置 | 规则 |
| D3 | Δm 激活 = **P1a 角色分类驱动基础行动**：物理攻击(M1)→attack_physical 边 n+1、精神攻击(Broca)→attack_mental 边 n+1、防御→defend 边 n+1；**g(n) = 单场战斗内激活次数**（累计则 g 永衰减无意义）；P1c 后扩展技能使用边 | 规则 |
| D4 | 可塑性巩固 = **引擎数据 + 结算接口**（LinkState.Marked 位 + `ApplyConsolidation`），UI/强度计算归上层 | 范围 |
| D5 | 聚焦 = **Build(data, LinkState, FocusSet) 独立参数**（构建层状态），聚焦边 ×2.0 | 接口 |

## 三、LinkState 数据结构

```csharp
// Entity/LinkState.cs（构建层可变慢变量——战斗内不变，战斗快照传入）
public sealed class LinkState
{
    // edgeId → m ∈ [0,1]（仅 CC+PP 888 边；键 = "cc:NNN" / "pp:NNN"，与 P1a 边键一致）
    public IReadOnlyDictionary<string, float> M { get; }
    // edgeId → 已标记（可塑性巩固标记，Δm 永久 ×2，不可重复）
    public IReadOnlySet<string> Marked { get; }

    public static LinkState CreateInitial(GameData data);  // D2 层级表初始化
    public bool TrySetM(string edgeId, float m);           // clamp [0,1]
    public bool TryMark(string edgeId);                    // 不可重复标记
}

// Types/ 或 Entity/ FocusSet（构建层聚焦配置——激活点容量决定集合大小）
public sealed record FocusSet(IReadOnlySet<string> EdgeIds);
```

- 边键契约与 `link_contexts_tripartite.json`（P1a）一致（cc:NNN/pp:NNN = tripartite 数组索引）
- WMatrixBuilder 消费：`m_mean(edge) = linkState.M[edgeId]`；聚焦边 `focus = 2.0f` 否则 `1.0f`
- 未在 LinkState 中的边（理论上不应发生——888 全覆盖）→ 抛 InvalidDataException

## 四、m 初始化规则

```
边层级 L(edge) = max(level(dk(source)), level(dk(target)))
边 m(0) = 层级表中值（核心机制 §10.3）:
  L0: 0.15-0.30 → 0.225
  L1: 0.10-0.25 → 0.175
  L2: 0.05-0.20 → 0.125
  L3: 0.10-0.25 → 0.175
  L4: 0.00-0.05 → 0.025
  L5: 0.00-0.05 → 0.025
```

- dk 层级来源：`brain_regions.json` level 字段（dk 聚合取端点层级）
- 角色疾病标签偏移（§10.3 注）→ 推迟（角色/敌人批次）

## 五、Δm 结算规则

```
战后结算（战斗结束 Phase 5 后）:
  for edge e 参与本场战斗（激活次数 n_e ≥ 1）:
    Δm_e = base(L(e)) × (1 − sigmoid(m_e, 0.45, 10)) × g(n_e) × 标记倍率
  base(L): L0 0.03 / L1 0.04 / L2 0.05 / L3 0.05 / L4 0.06 / L5 0.07（核心机制 §1.3）
  g(n): 1.0 / 0.5 / 0.25 / 0.1（n=1/2/3/4+）——单场战斗内激活次数（D3）
  标记倍率: 2.0 if e ∈ Marked else 1.0
  m_e ← clamp(m_e + Δm_e, 0, 1)
```

**激活计数（D3，P1a 角色驱动）**：

| 行动（引擎现有基础行动） | 通道 | 激活边 |
|--------------------------|------|--------|
| 物理攻击 | M1 | `primary_role = attack_physical` 的边 n+1 |
| 精神攻击 | Broca | `primary_role = attack_mental` 的边 n+1 |
| 防御 | — | `primary_role = defend` 的边 n+1 |

- 角色来源：P1a `link_contexts_tripartite.json` 的 `edge_contexts[].primary_role`（依赖 P1a 实施）；P1a 未就绪时用 `domain_role_map.json` + 边 gameplay_labels 临时直算
- P1c 后扩展：技能执行 → 技能 cortical_nodes 关联边（待 P1c 定义）

## 六、可塑性巩固接口

```csharp
// Entity/LinkState.cs
public enum ConsolidationAction { Mark, Boost }

// 战后调用——引擎只做状态变更正确性，UI/事件强度计算归上层
// 校验: Mark 仅当 !Marked（不可重复）; Boost 仅当 m ≤ 0.3（增强上限 §8.4）
public bool TryConsolidate(string edgeId, ConsolidationAction action, float strength);
//   Mark: Marked.Add(edgeId)（后续 Δm 永久 ×2）
//   Boost: m ← clamp(m + boost(strength), 0, 1)
//     boost: 低强度(<1.0) 0.03-0.07 / 中(1.0-2.0) 0.07-0.12 / 高(>2.0) 0.12-0.20（§8.2 映射）
```

## 七、聚焦接口与 Build 签名

```csharp
// 签名变化（B4 偏差闭合）:
public static WMatrix Build(GameData data, LinkState linkState, FocusSet focus)
// 原 Build(GameData) 保留为便捷重载（内部用 LinkState.CreateInitial + 空 FocusSet）
```

- WMatrixBuilder Step 4：`mMean(edge) = linkState.M[edgeId]`；`focusMultiplier = focus.EdgeIds.Contains(edgeId) ? 2.0f : 1.0f`（皮层动力学 §5.2）
- 调用方更新：TurnManager ctor / CombatState.Create 接收 LinkState + FocusSet
- 确定性保持：LinkState/FocusSet 作为参数传入（纯函数不变式维持）

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `LinkState` + `FocusSet` 类型（含 CreateInitial 层级表初始化） | 代码 | `Entity/LinkState.cs` + `Types/FocusSet.cs` | D1/D2 |
| T2 | `WMatrixBuilder.Build` 签名扩展 + m_mean/focus 消费 + 便捷重载 + 调用方更新 | 代码 | `WMatrixBuilder.cs` + `TurnManager.cs` + `CombatState.cs` | T1 |
| T3 | Δm 结算器（战后）：角色匹配（P1a 数据）→ 激活计数 → Δm 公式 → LinkState 更新 | 代码 | `Engine/MyleinGrowth.cs`（Δm 结算） | T1 + P1a 产物 |
| T4 | 可塑性巩固接口 `TryConsolidate`（Mark/Boost + 校验 + 强度映射） | 代码 | `LinkState.cs` | T1 |
| T5 | Console demo 接线：CreateInitial + 战斗内激活计数 + 战后 Δm 摘要 + 巩固输入 | 代码 | `YouAreNotTheFish.Console` | T2-T4 |
| T6 | 测试（初始化分布/Δm 公式逐项/标记倍率/增强上限/聚焦 ×2.0）+ 文档同步 | 测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T5 |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `src/YouAreNotTheFish.Core/Entity/LinkState.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Types/FocusSet.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs` | 改写（签名+m_mean+focus） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/MyleinGrowth.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Flow/TurnManager.cs` + `Entity/CombatState.cs` | 改写（传参） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/`（LinkState/MyleinGrowth/WMatrix 测试） | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/`（接线） | 改写 | 代码 |
| `data/connectivity/link_contexts_tripartite.json`（P1a 产物，T3 消费） | 依赖 | 数据 |
| `docs/决策树/` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- `LinkState.M` 键 = CC+PP 888 边键（cc:NNN/pp:NNN），全覆盖双射
- m ∈ [0,1]；Marked 集合不可重复；Boost 仅 m ≤ 0.3
- `w = edr × m_mean × focus`（皮层动力学 §5.2）；聚焦 ×2.0
- 确定性：LinkState/FocusSet 参数传入，同输入同输出（SmokeTests AC-8 契约延续）
- Δm 结算：g(n) 单场战斗内计数；标记倍率仅 Marked 边

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿（含新增） | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| m 初始化分布 | Console demo 输出各层级 m 摘要 vs §10.3 中值 |
| Δm 逐项 | 单测：base/f(m)/g(n)/标记倍率 4 因子逐项断言 |
| 确定性 | 同 seed 跑两次 diff |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] LinkState 888 边全覆盖，CreateInitial 按 §10.3 层级表（max 端点层级）初始化
- [ ] WMatrixBuilder 消费真实 m + focus ×2.0；原单参重载保留（B4 偏差声明闭合）
- [ ] 战后 Δm 结算：角色驱动激活计数 + g(n) 单场 + 标记倍率，公式与 §1.3 逐项一致
- [ ] TryConsolidate 校验生效（不可重复标记 / 增强上限 m≤0.3 / 强度映射）
- [ ] Console demo 显示 m 摘要 + 战后 Δm + 巩固输入可用
- [ ] 测试绿；决策树 #73 / 六维状态 / memory 落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 技能使用激活边 | 技能执行未实现（P1c 才定义 cortical_nodes） | P1c 扩展 Δm 结算 |
| 角色疾病标签 m 偏移 | 依赖角色/敌人数据批次 | 角色批次 |
| 事件强度计算（挑战度/激活广度/叙事权重） | 强度=上层输入；挑战度需敌方 m 模板 | P1b 只做接口；强度计算随数值平衡工具 |
| NPC 静态 m 模板 | 7 参数化性格（P3） | P3 NPC 批次 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [Grilling #72 P1a task-plan](./../grilling-72-p1a-skill-context/task-plan.md), [核心机制](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [皮层动力学-通用层](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md), [运行时状态模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [csharp-engine plan](../../../规格/引擎/csharp-engine-roadmap.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
