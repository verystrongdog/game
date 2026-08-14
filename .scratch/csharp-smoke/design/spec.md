# csharp-smoke — 实现规格

> Smoke 集成测试（plan step 12 收尾）——端到端完整战斗验证：数据 → 引擎 → 流程 → 结束，证明神经动力学引擎产出合理战斗结果。纯测试 feature（无新引擎代码）。版本: v1.0

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `SmokeTests`（Tests/Smoke/SmokeTests.cs 新建）——引擎级端到端战斗（TurnManager + 双方自动行动）+ 确定性 + 集成点验证 |
| 不覆盖 | 玩家交互路径（console 已覆盖）；新引擎代码（本 step 零实现）；性能基准 |
| 前置依赖 | csharp-flow ✅ / csharp-console ✅（284/284） |
| 阻塞 | 无——12 个引擎任务收尾 |

## 二、接口定义

### 2.1 SmokeTests（Tests/Smoke/）

```csharp
public class SmokeTests
{
    // helper：FullBattle(seed, provider) → (state, tm)——跑到 IsOver 或上限
}
```

- 双方自动：`new TurnManager(data, cal, new NpcActionProvider())`——NPC vs NPC（无键盘）。
- 数据：GameDataLoader.LoadAll（DataDirCandidates 镜像约定）。
- 无 static 可变状态；同种子确定性。

## 三、交叉引用约束（验证点）

### 3.1 集成验证点（plan §八 验证标准落地）

| 验证点 | 断言 |
|--------|------|
| 战斗结束 | 跑至 `tm.IsOver(state)`（≤ MaxRounds+1 步防死循环）→ 结束原因 ∈ {TeamDefeated（全灭——Hp≤0 ∨ San≤0 同队全员）, MaxRounds} |
| 事件流非空 | 每回合 TurnResult.Events 非空（NPC 自动行动必产事件——3 基础行动全部产 δ/s；等待不产出但 NpcSalience 无等待） |
| HP/SAN 变化 | 战斗期间存在 HP 扣减（DamageDealt > 0 的事件）——伤害链真正生效 |
| tone 动态 | 事件后 tone 偏离 baseline（事件接收者）；随后零事件回合回落（Phase 1 衰减——`|tone'−baseline|` 单调不增） |
| gate 动态 | 每回合 gates ∈ [0, 1]（CstcGating 输出域）；存在 gate 变化（非恒 1） |
| 速度序变化 | 长战斗（≥10 回合）中 LastRoundOrder 至少一次与首回合不同（a(t) 动态驱动排序变化） |
| 静息→战斗 | 战斗初态 a(t) = 静息不动点（active ∈ [0.535, 0.772]——M1 实测）；首回合 Phase 1 后稳定 |

### 3.2 确定性

- 同种子 + 同初始 state（重新 Create）→ 两次完整战斗逐位同（Round/事件数/终态 HP/SAN/tone/Wc.A 深度断言——record 数组引用规避同 flow AC-12）。

## 四、枚举与常量

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 战斗步数上限（防死循环） | — | MaxRounds + 1（=51） | §3.1（IsOver 必在 51 步内为 true） |
| 长战斗阈值 | — | 10 回合 | §3.1 速度序变化（排序动态需要时间） |

## 五、验收标准

| AC | 验收标准 | 锚点/断言 |
|----|---------|-----------|
| AC-1 | 完整战斗结束 | NPC vs NPC 全自动，跑至 IsOver（步数上限内）→ 结束原因 ∈ {TeamDefeated, MaxRounds}；state.History.Count == 实际回合数 |
| AC-2 | 事件流非空 | 每回合 Events 非空；全程存在 PhysicalDamageEvent（伤害链生效） |
| AC-3 | HP/SAN 合理 | 战斗结束时败方 Hp≤0 ∨ San≤0（TeamDefeated 时）；全程 HP ∈ [0, HpMax]、SAN ∈ [0, SanMax]（0.1 网格——Round1 量化不变式） |
| AC-4 | tone 动态 | 存在事件接收者 tone 偏离 baseline（|Δ| > 0.01）；随后回合（无事件接收者）回落（|Δ| 单调不增） |
| AC-5 | gate 动态 | 每回合全参与者 gates ∈ [0, 1]；存在回合间 gate 变化（max |Δgate| > 0.001） |
| AC-6 | 速度序变化 | ≥10 回合战斗中 LastRoundOrder 至少一次 ≠ 首回合序 |
| AC-7 | 静息→战斗 | 初态 active ∈ [0.535, 0.772]；首回合 a 稳定（|Δ| < 1e-3） |
| AC-8 | 确定性 | 同种子两次完整战斗深度逐位同 |
| AC-9 | 长战斗完整性 | MaxRounds 结束的战斗：全程无异常、无 NaN 毒化（全部 Hp/San/tone/gates 有限） |

## 六、本 spec 自检清单

1. **数学公式逐项对照**——无新公式（复用组件级已验证）；验证点对应 plan §八。
2. **数值断言全部实测**——静息区间 M1 实测；HP/SAN 网格不变式（Round1 量化）。
3. **计算顺序契约明确**——完整战斗循环（IsOver 上限）；验证点时序（首回合/长战斗）。
4. **接口注释先行**——SmokeTests helper 注释。
5. **边界值覆盖**——结束双口径、NaN 毒化防御、网格不变式、排序变化阈值。
6. **确定性**——AC-8 实证。
7. **偏差声明完整**——NpcSalience 全自动（无玩家）声明；速度序变化阈值 [NEW] demo。
8. **常量复用漂移注**——MaxRounds/PlayerHp 等消费不重定义；无新常量。
9. **类型变更声明**——零（纯测试）。

## 七、偏差声明

| # | 偏差 | 理由与处置 |
|----|------|-----------|
| B1 | 双方 NPC 全自动（无玩家参与） | Smoke 验证引擎端到端；玩家路径 console 已覆盖 |
| B2 | 速度序变化阈值 10 回合 [NEW] | 排序动态需时间显现；10 回合为 demo 经验值（若首回合已不同则立即成立，阈值只是保证至少观察 10 回合） |
| B3 | 战斗步数上限 = MaxRounds + 1 | 防死循环（IsOver 数学上必在 MaxRounds 步内 true——防御性断言） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |

---
*创建: 2026-08-14 | 更新: 2026-08-14 | 版本: v1.0*
*关联: [任务issue 01](issues/01-smoke-spec.md), [plan §八/§十](../../../csharp-engine/design/plan.md)*
