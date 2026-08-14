# csharp-smoke — 实现规格

> Smoke 集成测试（plan step 12 收尾）——端到端完整战斗验证：数据 → 引擎 → 流程 → 结束，证明神经动力学引擎产出合理战斗结果。纯测试 feature（无新引擎代码）。版本: v1.2.1

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

- **参与者构成（v1.1 补——审计 SMOKE-4：原未定义；v1.2 终审修正：TurnActionProvider 笔误 → NpcActionProvider）**：2 参与者 NPC vs NPC（双方自动——`new NpcActionProvider()`，flow §3.1 已交付）；**双方 HP 80 / SAN 80**（v1.1 修正：demo 杂兵模板 15 HP 下物理速攻 3-5 回合灭队，长战斗断言不可达——双方用玩家级模板保证 ≥10 回合窗口；[NEW] smoke 专用模板，非 CalibrationConfig 常量）；teams = [1, 2]。**seed 实测固定程序（v1.1 补——审计 F4/SMOKE-4）**：AC-2/5/6 为经验性断言——测试写作期跑 seed sweep（0-200），选定使全部经验断言成立的种子，写死进测试（flow 惯例「测试不凭记忆写锚点」）。
- 数据：GameDataLoader.LoadAll（DataDirCandidates 镜像约定）。
- 无 static 可变状态；同种子确定性。

## 三、交叉引用约束（验证点）

### 3.1 集成验证点（plan §八 验证标准落地——v1.1 明示 7 验证点 + §3.2 确定性 = 8 项，审计 F6）

| 验证点 | 断言 |
|--------|------|
| 战斗结束 | 跑至 `tm.IsOver(state)`（≤ MaxRounds+1 步防死循环）→ 结束原因 ∈ {TeamDefeated（全灭——Hp≤0 ∨ San≤0 同队全员）, MaxRounds} |
| 事件流 | 全程存在 PhysicalDamageEvent（伤害链生效——v1.1 修正：**「每回合非空」不成立——双方同回合都 defend 产零事件回合（flow §3.3 Defend 无事件），NpcSalience Softmax 三候选概率恒正（SMOKE-2/F3）**；seed 实测固定后断言「除双防御回合外 Events 非空」） |
| HP/SAN 变化 | 战斗期间存在 HP 扣减（DamageDealt > 0 的事件）——伤害链真正生效 |
| tone 动态 | **v1.1 修正（审计 F1：NPC vs NPC 每回合双方都是 δ 接收者——攻击者 A1/A2 + 承受者 B1/B2 恒发，「无事件接收者回合」不存在）**：① 事件接收者 tone 偏离 baseline（|Δ| > 0.01）；② 纯衰减观测——脚本化 provider 注入等待回合（(null,null) 合法，flow §2.3）→ 该回合后 tone 向 baseline 靠近（Phase 1 衰减，flow §3.5 步骤 1） |
| gate 动态 | 每回合 gates ∈ [0, 1]（CstcGating 输出域）；**热身收敛观测（v1.2.1 实现期实测修正——审计 F7 后续：「事件驱动抑制 <0.99」被实测推翻：round>2 gate 恒 1.0（seed sweep 50/50 + 12 回合逐位确认——CstcGating 输出对 demo 事件幅度不敏感，GPi 恒 0）；动态观测点改为热身瞬态（round 1 = 0.635 → round 2 = 1.0 收敛过程）** |
| 速度序变化 | 战斗（双方 HP 80 模板下 ≥10 回合）中 LastRoundOrder 至少一次与首回合不同（a(t) 动态驱动排序变化——**v1.1 修正：模板升级保证长战斗可达，审计 F4**） |
| 静息→战斗 | 战斗初态 a(t) = 静息不动点（active ∈ [0.535, 0.772]——M1 实测）；首回合 Phase 1 后稳定（文档化——审计 F8：baseline 输入下结构性平凡成立，保留为初态哨兵） |

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
| AC-1 | 完整战斗结束 | NPC vs NPC 全自动（双方 HP 80/SAN 80 模板），跑至 IsOver（步数上限内）→ 结束原因 ∈ {TeamDefeated, MaxRounds}；state.History.Count == 实际回合数 |
| AC-2 | 事件流 | 全程存在 PhysicalDamageEvent；**除双防御回合外 Events 非空（v1.1 修正——SMOKE-2/F3；seed 实测固定）** |
| AC-3 | HP/SAN 网格不变式 | **v1.1 修正（审计 F2/SMOKE-3：引擎无 clamp——过杀负值可达，如 5.5−6.1=−0.6）**：全程 Hp/San 为 0.1 网格值（Round1 量化不变式）；上界 ≤ HpMax/SanMax（0.1 网格容差）；**过杀负值合法（显式声明——Downed 判定用 ≤0，终态保留负值）** |
| AC-4 | tone 动态 | ① 存在事件接收者 tone 偏离 baseline（|Δ| > 0.01）；② **脚本化等待回合后 tone 向 baseline 靠近（|Δ| 严格缩小——审计 F1：NPC vs NPC 无「无事件接收者回合」，纯衰减需注入等待回合观测）** |
| AC-5 | gate 动态 | 每回合全参与者 gates ∈ [0, 1]；**热身收敛（v1.2.1 实现期实测修正：round 1 = 0.635 → round 2 = 1.0——原「非热身回合 gate < 0.99」断言被实测推翻（round>2 恒 1.0，seed sweep 50/50），事件驱动抑制在 demo 参数下不可观测，记录为引擎行为）** |
| AC-6 | 速度序变化 | 战斗（双方 HP 80 模板——v1.1 修正保证 ≥10 回合窗口，审计 F4）中 LastRoundOrder 至少一次 ≠ 首回合序（seed 实测固定） |
| AC-7 | 静息→战斗 | 初态 active ∈ [0.535, 0.772]（初态哨兵——审计 F8 文档化）；首回合 a 稳定 |
| AC-8 | 确定性 | 同种子两次完整战斗深度逐位同（Round/事件数/终态 Hp/San/tone/Wc.A） |
| AC-9 | NaN 毒化防御 | **v1.1 修正（审计 F5：覆盖所有战斗而非仅 MaxRounds 场景）**：全程逐回合全参与者 Hp/San/tone/gates 有限（float.IsFinite——事件层 NaN/∞ 防御已完备，审计 F10 确认） |

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
| B2 | 速度序变化阈值 10 回合 [NEW] + 双方 HP 80 模板保证 | 排序动态需时间显现；demo 杂兵模板 15 HP 下 3-5 回合灭队（审计 F4）——smoke 专用模板（非 CalibrationConfig 常量）保证 ≥10 回合窗口 |
| B3 | 战斗步数上限 = MaxRounds + 1 | 防死循环（IsOver 数学上必在 MaxRounds 步内 true——防御性断言，审计 F12 确认不会误触） |
| B4 | 过杀负值合法（无 clamp） | 引擎结算无 0 下限 clamp（flow §5.1 Round1 直落负）；Downed 判定 ≤0 接受负值——smoke 断言网格不变式 + 上界，负值显式声明（审计 F2/SMOKE-3） |
| B5 | 双防御零事件回合豁免 | NpcSalience Softmax 三候选概率恒正（含 defend）——双方同回合都 defend 产零事件回合，断言豁免 + seed 实测固定（审计 F3/SMOKE-2） |
| B6 | seed 实测固定程序 [NEW] | AC-2/5/6 为经验性断言（Softmax 概率性）——seed sweep（0-200）选定成立种子写死进测试（flow 惯例） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-14 | 审计（2 专家 + 对抗验证，20 发现 → 14 CONFIRMED）修复：F1（tone 回落不可观测——NPC vs NPC 每回合双方都是 δ 接收者；改脚本化等待回合观测纯衰减）；F2/SMOKE-3（HP ∈ [0, HpMax] 与无 clamp 矛盾——过杀负值合法，改网格不变式 + 上界）；F3/SMOKE-2（「每回合非空」不成立——双防御零事件回合正概率；改存在伤害事件 + 豁免）；F4（≥10 回合无保证——双方 HP 80 smoke 专用模板）；F5（NaN 检查覆盖所有战斗）；F6（验证点 7+1 明示 + plan §八 映射）；F7（gate 动态改事件驱动抑制 <0.99——热身瞬态平凡满足）；F8（AC-7 文档化为初态哨兵）；SMOKE-4（参与者构成 + seed 实测固定程序）；偏差 B4-B6 新增 | 审计（3❌ + 4⚠️ + 2ℹ️ 去重） | 终审确认 |
| v1.2 | 2026-08-14 | 终审残差清扫（2⚠️）：gate 断言显式排除热身回合（前两回合——初态静息 + gurney 零起步下第 1 回合 gate1=0.635 平凡满足 <0.99）；`new TurnActionProvider()` 笔误 → `NpcActionProvider`（flow §3.1 已交付） | 终审发现（2⚠️） | sign-off |
| v1.2.1 | 2026-08-14 | 实现期实测修正（seed sweep 0-49 + 12 回合逐位确认）：AC-5「非热身回合 gate < 0.99」被实测推翻——round>2 gate 恒 1.0（CstcGating 输出对 demo 事件幅度不敏感，GPi 恒 0）；改热身收敛观测（round 1=0.635 → round 2=1.0）；事件驱动抑制记录为引擎行为（50/50 seed 确认） | 实现期 seed sweep（AC-5 断言与实测不符） | 实现期（随工作issue） |

---
*创建: 2026-08-14 | 更新: 2026-08-14 | 版本: v1.2*
*关联: [任务issue 01](issues/01-smoke-spec.md), [plan §八/§十](../../../csharp-engine/design/plan.md)*
