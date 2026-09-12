# Grilling #84 P5-3 面具组件进引擎 — 实施任务计划

> Grilling #84 (GitHub #84) 结论：面具组件系统引擎机制先行落地——组件内容（components.json/病理边）等 14 角色映射表批次（§8.12）。4 项共识：机制先行+内容推迟 / 共享 EffectiveM / 同角色加成偏移×倍率 / MaskSet+疾病重叠+互斥接口。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [处理方式：机制先行 + 内容推迟](#三处理方式机制先行--内容推迟)
4. [MaskSet 数据结构](#四maskset-数据结构)
5. [组件调制（共享 EffectiveM）](#五组件调制共享-effectivem)
6. [同角色加成](#六同角色加成)
7. [疾病重叠与拮抗互斥](#七疾病重叠与拮抗互斥)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

角色与面具 §8 正典完整（组件两层结构/5 槽/稀有度/操作规则/病理链路/同角色加成修正/疾病重叠/拮抗互斥），但 §8.12 明确病理链路完整列表、拮抗对列表、14 角色→组件映射表为"待解决/后续讨论"——组件**内容**必须从角色疾病推导（§8.8.2：病理链路只能从已定义疾病中推导），不能拍脑袋造。P5-3 落地**引擎机制骨架**（不依赖具体组件内容），内容随 14 角色映射表批次补充。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | **机制先行 + 内容推迟**：MaskSet/调制/加成/重叠互斥机制本批落地；components.json/pathology_edges.json 内容随 14 角色映射表批次（demo 用 1-2 占位组件 [NEW] 验证机制） | 范围 |
| D2 | 组件调制 = **共享 P5-2 `EffectiveM` 表**：`EffectiveM[edge] = clamp(LinkState.M + Σ药物偏移 + Σ组件偏移, 0, 1)`——组件+药物共享拮抗限额（Σ 偏移 ≤ 1.4，决策树 #4）；冲突取绝对值最大 | 机制 |
| D3 | 同角色加成 = 面具组件按 `primary_role`（P1a 上下文键 role）分组 → 该角色组件**调制偏移量 × (1 + bonus)**（2 件 15% / 3 件 25% / 4 件 30% / 5 件 35%，§8.9.1）；专属被动接口预留；网络仅展示 | 规则 |
| D4 | 操作/重叠/互斥：`MaskSet`（5 槽构建层——非战斗编辑/战斗锁死/替换不升级/多面具=皮肤）+ **疾病重叠判定**（组件 edge ∈ 角色初始疾病边 → 无效，§8.10.3）+ **拮抗互斥接口预留**（互斥对数据随映射批次） | 规则 |

## 三、处理方式：机制先行 + 内容推迟

```
本批（机制骨架）:             后续（内容——14 角色映射表批次）:
  MaskSet 5 槽                 components.json 全量（角色疾病推导）
  共享 EffectiveM 调制           pathology_edges.json（4 类病理边完整列表）
  同角色加成（primary_role）     拮抗对列表
  疾病重叠判定（接口+1-2 角色）   各角色专属被动
  拮抗互斥（接口预留）
demo 占位组件 1-2（[NEW] 待映射表——机制验证用，非正典组件内容）
```

## 四、MaskSet 数据结构

```csharp
// Types/MaskComponent.cs（占位——内容随映射表）
public sealed record MaskComponent
{
    public string Id { get; init; }              // 占位: "demo_ptsd_flashback"
    public string Slot { get; init; }            // 额头/眼周/口部/脸颊/下巴（§8.4 5 位）
    public string Context { get; init; }         // P1a 上下文键（network/role——分类归属，后台黑箱）
    public string Edge { get; init; }            // 病理边或正常边（source→target 或边键）
    public EffectKind Effect { get; init; }      // Activate(+) / Inhibit(−)
    public float Strength { get; init; }         // 稀有度级偏移（N ±0.1-0.2 / R ±0.3-0.4 / SR ±0.5+）
    public bool IsPathological { get; init; }    // 病理边组件（带代价/3D 区分）
}

// Types/MaskSet.cs（构建层——非战斗配置）
public sealed record MaskSet(IReadOnlyDictionary<string, string> SlotToComponentId);
// 校验: 5 槽各 1 件/槽位不重叠/拮抗互斥（接口）/战斗快照锁死
// 多面具: 构建层多 MaskSet 切换（皮肤语义——同一套 5 槽功能）
```

## 五、组件调制（共享 EffectiveM）

```
CombatState.EffectiveM[edge] = clamp(LinkState.M[edge] + Σ药物偏移 + Σ组件偏移(×同角色加成), 0, 1)

组件偏移: 面具组件生效部分（疾病重叠无效的排除——§七）
拮抗限额: Σ(药物+组件) 偏移 ≤ 1.4（决策树 #4）；冲突取绝对值最大
战斗结束: EffectiveM 归 LinkState.M（构建层不污染）

与 P5-2 完全共享——组件使用同一 EffectiveM 表与 W 重算机制
```

## 六、同角色加成

```
面具 5 槽组件按 primary_role 分组计数（P1a 上下文键 role 部分）:
  2 件同角色 → 该角色组件偏移 × 1.15
  3 件 → × 1.25
  4 件 → × 1.30 + 专属被动（接口预留——效果描述字段，内容随映射表）
  5 件 → × 1.35 + 专属被动
网络维度仅展示标签（不参与判定——§8.9.1 修正）
```

## 七、疾病重叠与拮抗互斥

```
疾病重叠判定（§8.10.3）:
  组件 edge ∈ 角色初始疾病已调制的边 → 组件无效（不叠加）
  判定数据: 疾病目录（实体/疾病目录/——14 角色已引用疾病，边级调制数据）
  demo: 1-2 角色验证（如 PTSD 角色 + 闪回组件）

拮抗互斥（§8.9.2——接口预留）:
  AntagonisticPairs [NEW] 数据（对立边对——内容随组件映射批次）
  校验: 同面具组件互斥对 → 拒绝装备
  demo: 不启用或 1 占位对
```

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `MaskComponent` + `MaskSet`（5 槽构建层——编辑/锁死/替换/多面具）+ 占位组件 1-2（[NEW]） | 代码 | `Types/MaskComponent.cs` + `Types/MaskSet.cs` | D1 |
| T2 | 组件调制接入共享 `EffectiveM`（P5-2 扩展——Σ组件偏移 + 拮抗限额） | 代码 | `Entity/CombatState.cs`（EffectiveM 扩展） | T1 + P5-2 |
| T3 | 同角色加成（primary_role 分组 × 倍率 + 专属被动接口） | 代码 | `Engine/MaskBonus.cs` | T2 |
| T4 | 疾病重叠判定（疾病目录边级数据——demo 1-2 角色） | 代码 | `Engine/MaskOverlap.cs` | T1 |
| T5 | 拮抗互斥接口（AntagonisticPairs [NEW] 数据占位 + 校验） | 代码 | `Types/AntagonisticPairs.cs` | T1 |
| T6 | Console demo（装备组件/加成显示/重叠提示/EffectiveM 变化）+ 测试 + 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T5 |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `src/YouAreNotTheFish.Core/Types/MaskComponent.cs` + `MaskSet.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Engine/MaskBonus.cs` + `MaskOverlap.cs` | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Types/AntagonisticPairs.cs` | 新建（接口占位） | 代码 |
| `src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（EffectiveM 扩展） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `docs/决策树.md` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- MaskSet 5 槽各 1 件、槽位不重叠；战斗快照锁死（战斗内不可换）
- 组件偏移并入 EffectiveM：Σ(药物+组件) ≤ 1.4；冲突取绝对值最大；战斗结束归 LinkState
- 同角色加成：偏移 × (1+bonus)；bonus 表（15/25/30/35%）与 §8.9.1 一致
- 疾病重叠：edge ∈ 疾病边 → 无效；拮抗互斥：互斥对拒绝装备
- 占位组件 [NEW] 标注（待 14 角色映射表批次替换）
- 确定性：同输入同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| MaskSet | 槽位/锁死/多面具 单测 |
| 组件调制 | 叠加/拮抗/冲突 单测 |
| 同角色加成 | 2-5 件倍率 单测 |
| 疾病重叠 | edge ∈ 疾病边无效 单测 |
| 拮抗互斥 | 互斥对拒绝 单测 |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] MaskSet 5 槽构建层（编辑/锁死/替换/多面具）+ 占位组件 1-2（[NEW]）
- [ ] 组件调制并入 EffectiveM（与 P5-2 共享 + 拮抗限额）
- [ ] 同角色加成（primary_role × 倍率 + 被动接口）
- [ ] 疾病重叠判定（demo 1-2 角色）+ 拮抗互斥接口
- [ ] Console demo 装备组件/加成/重叠可见
- [ ] 测试绿；决策树 #84 / 六维状态 / memory 落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| components.json 全量（角色疾病推导） | §8.12 待解决 + §8.8.2 只能从已定义疾病推导 | 14 角色映射表批次（逐角色开 issue） |
| pathology_edges.json（4 类病理边完整列表） | 同上 | 同上 |
| 拮抗对列表 | §8.12 待解决 | 逐角色拆解批次 |
| 各角色专属被动 | §8.12 待解决 | 同上 |
| 病理链路激活代价实现（§8.8.1） | 依赖病理边内容 + 状态系统 | 映射表批次 + 状态系统扩展 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [角色与面具](./../../实体/角色与面具.md), [Grilling #72 P1a task-plan](./../grilling-72-p1a-skill-context/task-plan.md), [Grilling #73 P1b task-plan](./../grilling-73-p1b-linkstate/task-plan.md), [Grilling #83 P5-2 task-plan](./../grilling-83-p5-2-consumables/task-plan.md), [数学语言书写规范](./../../docs/agents/math-language-writing.md)*
