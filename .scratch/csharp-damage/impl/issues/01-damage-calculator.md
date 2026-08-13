# 工作issue 01: DamageCalculator 实现 + L2 类型变更

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅（2026-08-13 批准） | GitHub: [#63](https://github.com/verystrongdog/game/issues/63)

## 范围

实现 [spec v1.1](../../design/spec.md) 全部内容，覆盖 AC-1~18：

- `DamageCalculator`（Engine/DamageCalculator.cs 新建）——CalcPhysicalDamage / CalcMentalDamage / Round1 / Floor1
- CalibrationConfig 新增 12 伤害常量 [NEW] + 4 demo 模板常量 int→float
- L2 跨 feature 类型变更 22 字段 int→float（§二 2.2 清单）
- 结转清单 5 项验证（sign-off 结转表 #1-#5）

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` — 新建
- `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` — 修改（12 常量 + 4 模板 int→float）
- `src/YouAreNotTheFish.Core/Types/ParticipantState.cs` — 修改（Hp/HpMax/San/SanMax int→float + CreateDefault(float,float)）
- `src/YouAreNotTheFish.Core/Types/CombatEvents.cs` — 修改（PhysicalDamageEvent 6 + MentalDamageEvent 8 int→float）
- `src/YouAreNotTheFish.Core.Tests/Engine/DamageCalculatorTests.cs` — 新建（AC-1~17）
- `src/YouAreNotTheFish.Core.Tests/Types/ParticipantStateTests.cs` / `CombatEventsTests.cs` — 验证（不改断言值，AC-18 回执）
- `.scratch/csharp-engine-types/design/spec.md` — 变更日志补 🔧 修正行（结转 #1）

grep 检查：其他进行中 work issue 无上述文件所有权（全部 prior issue 已 resolved）。

## 完成标准

spec §六 AC-1~18 逐条对照 + spec §七 自检清单 9 项 + sign-off 结转清单 5 项。

## 实现

提交（4 批，按 CLAUDE.md 小步提交）：

| commit | 类型 | 内容 |
|--------|------|------|
| 1d02ff5 | feat | L2 类型变更 22 字段 int→float（CalibrationConfig / ParticipantState / CombatEvents） |
| 2fe45f1 | feat | Engine/DamageCalculator.cs（99 行） |
| 4998602 | test | Tests/Engine/DamageCalculatorTests.cs（38 项） |
| 341dc9a | docs | types spec 变更日志 🔧 修正行（结转 #1） |

实现按 spec §三 3.1/3.2 求值序逐字落地，一次成型零 spec 缺陷（唯一首跑修正：实现文件补 `using YouAreNotTheFish.Core.Types;`——工程细节非 spec 缺陷）。

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— 输出：`Build succeeded. 2 Warning(s) 0 Error(s)`（2 警告均为 NU1900 NuGet 漏洞数据网络不可达——离线环境 pre-existing，与本次改动无关）
- [x] `dotnet test` 全绿 —— 输出：`Passed! - Failed: 0, Passed: 178, Skipped: 0, Total: 178`（既有 140 + 新增 38；net8.0）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | 物理基线 4.0f | ✅ | `Physical_DefaultBaseline_Returns4`（4.0f 逐位 + hit） |
| AC-2 | 物理全乘区 10.0f / 5.6f | ✅ | `Physical_FullModulation_Returns10` / `Physical_PartialModulationWithGate_Returns5_6`（5.6f 逐位） |
| AC-3 | 量化函数直接锚 | ✅ | `Round1_HalfAwayFromZero_MatchesAnchors` ×5 / `Floor1_FloorToTenth_MatchesAnchors` ×3 |
| AC-4 | 物理 clamp | ✅ | `Physical_ClampsForceAndMotivation` ×3（0.7→6.0f / 1.5→8.0f / 负→4.0f） |
| AC-5 | 命中边界 + miss 哨兵 | ✅ | `Physical_HitBoundary_MatchesSequence`（5 序列 [T,T,F,T,F]）/ `Physical_Miss_StillReturnsFullDamage`（miss 仍 4.0f——结转 #2 哨兵） |
| AC-6 | 命中率分布 | ✅ | `Physical_Roll080_IsMiss`（0.80 miss 证明 −10% 无条件生效）/ `Physical_HitDistribution_MirrorsRngThresholdCount`（同种子 1000 次镜像计数相等） |
| AC-7 | 防御 −50% 仅物理 | ✅ | `Physical_Defending_HalvesDamage`（5.0f/10.0f）/ `Mental_Signature_HasNoDefenderIsDefending`（反射断言签名） |
| AC-8 | 武器加成 + baseDamage + 精神消费哨兵 | ✅ | `Physical_WeaponBonus_AddsBeforeModulation`（10.0f/1.0f）/ `Mental_BaseDamage3_ConsumedNotHardcoded2`（3.0f/1.5f——写死 2f 必挂，结转 #2） |
| AC-9 | RNG 消费契约 | ✅ | `Physical_ThrowingRng_Propagates`（InvalidOperationException）/ `Mental_NoRng_Completes` |
| AC-10 | 精神基线 | ✅ | `Mental_DefaultBaseline_Returns2And1`（2.0f/1.0f 逐位） |
| AC-11 | 精神动机保留 | ✅ | `Mental_MotivationAndEndurance_QuantizedInner`（inner 镜像式 Round1(2×1.25−1)=1.5f + san 1.5f/hp 0.7f 逐位；inner 系内部量——经 pen=1/gate=1 时 san=Round1(inner)=inner 传递性 + 镜像式计算双重锁定，见发现的问题 #1） |
| AC-12 | 忍耐 + 最低 1.0 + gate=0 | ✅ | `Mental_NegativeRaw_ClampsTo1` ×3 组（1.0f/0.5f、1.0f/0.5f、0.0f/0.0f） |
| AC-13 | 穿透边界 | ✅ | `Mental_PenetrationTiers_StrictLess` ×4（0.30→1.0f / 0.2999f→1.3f / 0.15→1.3f / 0.149→2.0f） |
| AC-14 | 穿透 + 量化组合 | ✅ | `Mental_PenetrationCombos_MatchAnchors` ×3 组（2.6f/1.3f、2.0f/1.0f——F1 f32 域关键锚、3.6f/1.8f，全部逐位） |
| AC-15 | 确定性 + 输入不可变 | ✅ | `Determinism_SameSeedSameResult`（同种子 5 次逐位一致；输入为值类型参数天然快照；实现无 static 可变状态） |
| AC-16 | 异常契约 | ✅ | `Ctor_NullCal_ThrowsArgumentNull` / `Physical_NullRng_ThrowsArgumentNull` |
| AC-17 | 12 新常量 + 4 模板 float 化 | ✅ | `CalibrationConfig_DamageConstants_DefaultValues`（12 常量逐值）/ `CalibrationConfig_DemoTemplates_AreFloat`（IsFloat 重载绑定探针 ×4——结转 #3 机制 + 值 50f/80f/15f/60f） |
| AC-18 | L2 类型变更回执 | ✅ | 现有 ParticipantStateTests/CombatEventsTests **零改动**在全量 178/178 中通过（int 字面量经泛型推断 `Assert.Equal<float>` 绑定）；`Types_FloatFields_StoreAndReadBitwise`（5.6f 存读回逐位 + CreateDefault(50f,80f)→Hp 50f 逐位）；types spec 🔧 行 commit 341dc9a |

### spec §七 自检清单

1. [x] **数学公式逐项对照**——实现注释逐项引用核心机制 §4.2/§4.3、基础行动设计 §四、plan §4.6；max 在 gate 前（inner→s1 序）、motivation 物理 clamp 精神不 clamp、防御仅物理（精神签名无该参数，AC-7 反射锁定）、L0 回避无条件（常量差 0.75f）
2. [x] **数值断言全部实测**——全部锚点来自任务issue 01 实测表第三轮 #15-#19（runtime 8.0.29）+ Δ审计独立复算（refute agent dotnet 复跑 AC-1~14 逐位）；测试文件未凭记忆写任何锚点
3. [x] **计算顺序契约明确**——s2 左结合、Round1/Floor1 位置按 §五 1 写死并在代码标注；AC-2/AC-11/AC-14 锚点全绿即哨兵在位
4. [x] **接口注释先行**——类头 + 构造 + Round1/Floor1 + 两计算方法 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注（B1-B6 类头逐条对照表）
5. [x] **边界值覆盖**——穿透端点 0.30/0.15、命中阈值 0.75 与次邻 0.74999994、clamp 上下界与负值、gate=0、最低 1.0、量化 half 案例 1.95/0.75、武器加成 6、忍耐 2——全部有测试
6. [x] **确定性**——无 static 可变状态（Round1/Floor1 纯函数）；RNG 仅经 IRng 注入且物理恰好 1 次（AC-9 ThrowingRng + AC-6 分布镜像双锁定）；AC-15 实证逐位相等
7. [x] **偏差声明完整**——B1（第 7 参）/B2（精神武器不覆盖）/B3（生产者不实现）/B4（一位小数）/B5（类型变更）/B6（baseDamage 参数化）在实现注释逐条对应
8. [x] **常量复用漂移注**——12 新常量带来源注释（§四 4.1 逐条）；ScaleMental/ExpectedDamage 未重定义；4 模板类型变更注（B5 标记）
9. [x] **类型变更声明完整**——22 字段对照 §二 2.2 表逐字段核对（见结转 #5）；AC-18 回执（178/178 零改动）；types spec 变更日志 🔧 修正行已提交（341dc9a）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | types spec 变更日志 🔧 修正行 | ✅ commit 341dc9a——v1.1 追加 L2 语义行，指向 csharp-damage spec §二 2.2 B5（类型变更已随其规格审计） |
| 2 | AC-5 miss 哨兵 + AC-8 精神哨兵测试 | ✅ `Physical_Miss_StillReturnsFullDamage`（结算不可入 if(hit) 分支）+ `Mental_BaseDamage3_ConsumedNotHardcoded2`（写死 2f 必挂） |
| 3 | AC-17 重载探针按 spec 机制 | ✅ `CalibrationConfig_DemoTemplates_AreFloat` 用 IsFloat(float)/IsFloat(int) 重载决议捕获 4 demo 模板类型——赋值探针（已证伪）未采用 |
| 4 | 现有 types 测试零改动编译+通过 + 断言值 grep 复核 | ✅ 178/178 全绿（含 ParticipantStateTests/CombatEventsTests 零改动）；grep 复核：两文件 int 字面量断言值最大 80（<2^24 f32 精确整数域），float 字面量断言全部带 f 后缀 |
| 5 | 22 字段逐字段对照 §二 2.2 表 | ✅ 逐字段核对：CalibrationConfig 4（PlayerHp 50f/PlayerSan 80f/NpcHp 15f/NpcSan 60f）+ ParticipantState 4（Hp/HpMax/San/SanMax + CreateDefault(float,float)）+ PhysicalDamageEvent 6 + MentalDamageEvent 8 = 22；BaseDamage/WeaponBonus/HealAmount 保持 int ✓ |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | AC-11 的 inner 是方法内部量，无直接断言路径——spec 锚点「inner 1.5f」无法直接观测 | 测试经双通道间接锁定：镜像式独立计算 Round1(2×1.25−1)=1.5f + pen=1/gate=1 时 san=Round1(inner×1×1)=inner 的传递性（san 1.5f 逐位 ⟹ inner 1.5f）。非 spec 缺陷——内部量锚点类 AC 建议在 spec 标注「经传递性/镜像式验证」 |
| 2 | NU1900 NuGet 漏洞数据网络不可达警告（构建 2 Warning） | 环境级（离线），pre-existing，非本次改动引入；门禁以 0 Error 为准 |

## Comments

- 2026-08-13：创建。sign-off ✅（dog，2026-08-13）。spec v1.1（全量审计退回修复 + Δ审计通过 + 残差清扫 cb129c1）。
- 2026-08-13：实现完成——4 批提交（1d02ff5/2fe45f1/4998602/341dc9a），178/178 全绿（新增 38），AC-1~18 逐条 ✅，§七 9 项全勾，结转 5 项全部回填。

## Comments

- 2026-08-13：创建。sign-off ✅（dog，2026-08-13）。spec v1.1（全量审计退回修复 + Δ审计通过 + 残差清扫 cb129c1）。
