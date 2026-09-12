# 审计报告: csharp-damage spec v1.0

> 审计日期: 2026-08-13 | 审计方法: workflow 3 专家（数学公式 / 接口契约 / 规格完整性）+ 逐条对抗验证 | spec版本: v1.0

## Trace Table

| # | spec位置 | 检查项 | 输入 | 判定 | 详情 |
|----|---------|--------|------|------|------|
| F1 | §三 3.3 + AC-14 第二行 + 变更日志 | MathF.Round 语义模型 | 本地 .NET SDK 8.0.29 实测 + dotnet/runtime v8.0.0 源码 + python 双模型全锚点复算 | ❌ CONFIRMED | spec 声称「委托 double 精度」错误——.NET 8 MathF.Round(float,int,AwayFromZero) 为全 f32 域（`x*=power10 → Truncate(x+CopySign(0.49999997f,x)) → x/=power10`）。实测 MathF.Round(1.94999993f,1,AFZ)=2.0、完整精神链 san 2.0/hp 1.0——AC-14 第二行锚点 1.9/0.9 按 spec 写测试必失败。其余全部 Round1/Floor1 锚点两模型逐位一致（复算 + 本地实测） |
| F2 | §三 3.2 公式 + 签名 + B6/D8 | 精神公式死参数 | python f32 全域扫描（baseDamage=2 vs 3 零差异） | ⚠️ CONFIRMED | 公式写死 `2f ×`，签名 baseDamage 不进公式——与 spec 自身「语义 = 基础 SAN 伤害」、B6「参数化支撑校准 sweep」矛盾；全部精神 AC 传 2，测试无法暴露。修复：`raw = (float)baseDamage × (1f+motivationMod) − (float)endurance`（AC 安全） |
| F3 | AC-13 | 锚点字面量 | python 复算 | ℹ️ | 「0.2999…」应为具体 f32 字面量 0.2999f |
| C-F1 | §二 2.2 | xUnit 兼容性声明机制 | 临时工程实编译（xunit 2.5.3 + net8.0，14 条断言全过）+ 泛型推断探针 | ⚠️ CONFIRMED | 结论（编译+通过）成立；机制陈述不准确——绑定为泛型推断 `Assert.Equal<float>`（int 字面量调用点转换），且大整数（16777217）会失真、无 f 后缀 double 字面量绑定 `Assert.Equal<double>` 逐位失败——边界未声明 |
| C-F2 | AC-17 | demo 模板「float 类型断言」 | 实读 AC-17 行 | ⚠️ CONFIRMED | 「float 类型断言」未指定机制——值断言无法区分 int/float。修复：编译期绑定（`float hp = cal.PlayerHp;` int 侧字段赋值即编译错误）+ 值逐位断言 |
| C-F3 | §四 4.1 + 参数速查表 | L0EvadeHitPenalty 数值来源 | grep 回合战斗流程 §6.2 | ℹ️ | −10% 数值不在 回合战斗流程 §6.2（该节只载「自动触发」）——数值在 基础行动设计 §二 行动1 命中判定 / §三 链路调制表 |
| C-F4 | §五 6 | 「12 常量不内置」措辞 vs 实际消费路径 | 对照 §三 公式 | ℹ️ | BasePhysicalDamage/BaseMentalDamage 走参数、DamagePrecision 为文档常量——3/12 不直接消费，措辞需区分 |
| K-F1 | §三 3.2 / §五 1 / B6 | 精神死参数（契约歧义） | 实读 spec+plan+issue | ⚠️ CONFIRMED | 与 F2 同源——公式不消费 baseDamage 且全部 AC 传 2，实现解释不可区分 |
| K-F2 | AC-5 / AC-6 | miss 时 Damage 值无锚定 | 覆盖矩阵 | ⚠️ CONFIRMED | 实现若把伤害计算放进 if(hit) 分支（miss 返回 0），全部 AC 仍通过。修复：AC-5 增 miss 伤害锚点 |
| K-F3 | §二 2.2 / §七 9 / AC-18 | types spec 🔧 修正行动无承接 | 实读 csharp-engine-types spec 变更日志（确无此行） | ⚠️ CONFIRMED | 跨 feature 动作只在正文/自检提及，无 AC 承接——实现完成即静默丢失。修复：并入 AC-18 |
| K-F4 | AC-2 / AC-14 | 实测标签「A/H/J」与实测表编号不符 | 对照任务issue 实测表 | ⚠️ CONFIRMED | 实测表仅 #1-#14；「实测 J」（3.6/1.8）任何行都找不到。修复：对齐编号 + 补第三轮实测行 |
| K-F5 | §四 4.1 / 参数速查表 | L0EvadeHitPenalty 来源引用漂移 | 实读 回合战斗流程 §6.2 + 基础行动设计 | ⚠️ CONFIRMED | 同 C-F3——数值正确、引用归属偏差 |
| K-F6 | 任务issue 范围段 vs D7/spec | 常量数 11 vs 12 | 实读 | ℹ️ | 任务issue「11 个 [NEW]」为 Q3=D 前遗留；D7/spec 12 个正确 |
| K-F7 | §三 3.1/3.2 未定义行为 | 未定义行为清单覆盖 | 覆盖矩阵 | ℹ️ | 负 weaponBonus、gateBonus ∉ [0,1]、motivationMod 越域未声明 |

## 缺口汇总

| # | 严重度 | 描述 |
|----|--------|------|
| 1 | ❌ | Round1 语义模型错误（double 委托 vs 真实全 f32 域）——AC-14 第二行锚点必失败 |
| 2 | ⚠️ | 精神公式 baseDamage 死参数（与 B6/D8 矛盾） |
| 3 | ⚠️ | miss 时 Damage 返回值无 AC 锚定 |
| 4 | ⚠️ | §二 2.2 xUnit 机制陈述不准确 + 边界未声明 |
| 5 | ⚠️ | AC-17 类型断言无实现机制 |
| 6 | ⚠️ | types spec 🔧 修正行动无 AC 承接 |
| 7 | ⚠️ | AC 实测标签与实测表编号错位（A/H/J） |
| 8 | ⚠️ | L0EvadeHitPenalty 数值来源引用漂移 |
| 9 | ⚠️ | §五 6 常量消费措辞与实际路径张力（info 级修复） |

## 审计结论

- [ ] 通过（无阻塞项）
- [ ] 有条件通过（⚠️ 项需人类确认）
- [x] **退回修改（1 ❌ 必须修复 + 8 ⚠️）**

## 半径扩张

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| F1 Round1 语义 + AC-14 第二行 | §三 3.3、AC-3（直接锚）、AC-12（负 raw）、AC-13/14 其余行、变更日志、任务issue :44 注/:127 注释/第二轮表、plan §4.6 bullet、term_registry round1/floor1 定义、map.md D13 行 | ✅ 见 Δ审计段 |
| F2 精神公式消费 baseDamage | §三 3.2、B6/D8 表述、plan §4.6 精神公式、任务issue D3 | ✅ 见 Δ审计段 |
| K-F2 miss 伤害锚点 | AC-5 | ✅ 见 Δ审计段 |
| C-F1/C-F2/K-F3 声明机制修正 | §二 2.2、AC-17、AC-18 | ✅ 见 Δ审计段 |
| K-F4 实测标签对齐 + 第三轮实测 | AC-2/AC-14、任务issue 实测表新增 #15-#19 | ✅ 见 Δ审计段 |
| K-F5/C-F3 来源引用修正 | §四 4.1、参数速查表 | ✅ 见 Δ审计段 |
| C-F4 常量消费措辞 | §五 6 | ✅ 见 Δ审计段 |
| F3/K-F6/K-F7 info 清扫 | AC-13、任务issue 范围段、§三 未定义行为 | ✅ 见 Δ审计段 |

## Δ审计（2026-08-13，spec v1.1）

> 审计方法: workflow 4 代理——2 专家（数学公式 / 接口契约）+ 半径扩张复查 + 对抗验证。radius 代理被安全分类器拦截（未产出），半径复查由编排者手工执行（下表）。对抗验证代理独立 dotnet 实测 AC-1~14 全部锚点（40+ 断言逐位 PASS）。

### 结论

- [ ] 通过（无残差）
- [x] **通过（残差清扫后）**——0 ❌ / 0 ⚠️ 阻塞；2 WARN + 1 INFO + 2 refute 发现，全部已修

### 残差处置

| # | 来源 | 发现 | 处置 |
|---|------|------|------|
| 1 | refute | **AC-17 类型断言机制不成立**：v1.0 审计 C-F2 建议的「`float hp = cal.PlayerHp` 编译失败」实测推翻——int→float 隐式转换使赋值探针对 int 字段同样编译通过（/tmp 实测「compiled OK, value = 50」），4 个 demo 模板字段的 int→float 变更在 AC-17 下不可捕获 | 机制替换为**重载绑定探针** `IsFloat(float)/IsFloat(int)`（重载决议精确匹配优先于隐式转换——本地 dotnet 实测 int→False/float→True，属性与字段形态均验证） |
| 2 | math/contract WARN (C-F1) | §二 2.2「断言值均 ≤60」与实读不符（ParticipantStateTests 断言 80）；大整数失真边界未显式声明 | 「≤80 的整数（f32 精确整数域 ≤2^24）」+ 边界①大整数 >2^24 失真 |
| 3 | math WARN (W1) | §五 1 残留 `2f×` 字面 | 已在 Δ审计期间 commit 22e6589 清扫（contract 专家基于当前文件复核 PASS） |
| 4 | contract INFO | 全部精神 AC 传 baseDamage=2——写死 2f 实现仍全绿，F2 修复无回归防线 | AC-8 增精神消费哨兵 (3,0,0,1.0f,1.0f)→san 3.0f/hp 1.5f |
| 5 | refute INFO | 「本地 SDK 8.0.29」表述错误——8.0.29 是 runtime 版（SDK 实为 8.0.423） | 全链措辞改「本地 .NET 8 runtime 8.0.29（SDK 8.0.423）」 |
| 6 | contract REDLINE 附注 | map.md 笔记行「精神 HP 成分 floor(san/2)」未随 Q3=D 更新 | →「向下取至 0.1（floor1）」 |

### 对抗验证 passed 摘录

- AC-1~14 全部锚点独立 dotnet 实测（Microsoft.NETCore.App 8.0.29）逐位 PASS——含 AC-14 第二行 0x40000000、AC-5 miss 锚点、穿透边界 0.30/0.15 严格小于。
- 第三轮实测表 #15-#19 位模式全部独立复现（0x3FF99999 = f32(1.9499999) 等）。
- 全仓 grep 三攻击面（double 委托 / 精神公式写死 2 / floor1 ×0.1f）零事实语气残留。
- F2 半径扩张各消费者（plan :179/:187、term_registry :402、map D13）同步确认；「types 文件零消费者」声明成立。

### 半径扩张手工复查（radius 代理被拦截，编排者手工执行）

| 修复点 | 消费者 | 状态 |
|--------|--------|------|
| F1 | spec §三 3.3 / AC-3 / AC-12 / AC-13/14 / 变更日志 / issue 第二轮注+D13+第三轮表 / plan :187 / registry :402 / map D13 | ✅ 全部已修 |
| F2 | spec §三 3.2 / §五 1 / B6 / plan :179 / issue D3 | ✅ 全部已修（§五 1 系 22e6589 清扫） |
| K-F2 | AC-5 | ✅ |
| C-F1/C-F2/K-F3 | §二 2.2 / AC-17 / AC-18 | ✅（AC-17 机制经残差 #1 替换） |
| K-F4 | AC-2 / AC-14 / issue 第三轮 #15-#19 | ✅ |
| K-F5/C-F3 | §四 4.1 / 参数速查表 | ✅ |
| C-F4 | §五 6 | ✅ |
| F3/K-F6/K-F7 | AC-13 0.2999f / issue 范围段 12 / §三 未定义行为 | ✅ |
