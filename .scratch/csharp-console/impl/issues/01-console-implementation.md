# 工作issue 01: csharp-console 实现（Console harness）

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.2 | Blocked by: sign-off ✅（2026-08-14 批准）

## 范围

实现 [spec v1.2](../../design/spec.md) 全部内容，覆盖 AC-1~13：

- `YouAreNotTheFish.Console` 可执行项目（src/YouAreNotTheFish.Console/，引用 Core）
- `CliArgs`（--seed/--trace-resting 解析，非法值/重复参数）
- `PlayerActionProvider`（键盘 IActionProvider——TextReader/Writer 注入、3 次重试、EOF 处理）
- `CompositeActionProvider`（p==0 玩家 / p!=0 NPC 分派）+ `WaitProvider`（静息 trace）
- `RoundRenderer`（9 段渲染：速度/顺序/a(t)/状态/行动/结算/因子/结束）
- `Program`（主循环 + 静息 trace 模式 + dataDir 回溯）
- **TurnManager.LastRoundActions/LastRoundOrder 落地**（决策 D1——flow spec 🔧 行承接，console 阶段实现）
- 结转清单 5 项验证（sign-off 结转表 #1-#5）

## 实现

| commit | 类型 | 内容 |
|--------|------|------|
| （step 11 实现批） | feat | Console 项目全部 + TurnManager LastRound* 属性 + ConsoleAppTests 23 项 |

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— 全部项目 Build succeeded
- [x] `dotnet test` 全绿 —— `Passed! - Failed: 0, Passed: 284, Skipped: 0, Total: 284`（既有 261 + 新增 23；net8.0）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | CliArgs 解析 | ✅ | `CliArgs_Valid`（默认/组合/重复参数后者覆盖）+ `CliArgs_Invalid_Throws`（8 种非法：缺值/非数字/负数/0/未知） |
| AC-2 | PlayerActionProvider 输入映射 | ✅ | `PlayerProvider_InputMapping`（1/2/3/0 四态 + 目标=对方）+ `InvalidRetry_ThenValid` + `ThreeInvalid_DefaultsToWait` + `Eof_DefaultsToWait` |
| AC-3 | RenderSetup | ✅ | `RenderSetup_ContainsParticipants`（玩家/杂兵 HP/SAN/队伍行） |
| AC-4 | 速度段 | ✅ | `RenderRound_AllSections`（[速度] ×2 + 总分） |
| AC-5 | 行动段 | ✅ | 同上（[行动] p0 物理攻击 → p1 + p1 NPC 行） |
| AC-6 | 结算段 | ✅ | 同上（[结算] A1 m=F4 正则 `\d\.\d{4}`） |
| AC-7 | 状态段 | ✅ | 同上（HP/tone/gates） |
| AC-8 | 结束输出 | ✅ | `RenderRound_EndReason_MaxRounds`（[结束] MaxRounds + **唯一输出源 Regex 计数**——v1.2 裁决） |
| AC-9 | 完整战斗冒烟 | ✅ | `FullBattle_Smoke_Exit0`（进程级：脚本化输入 60 次物理攻击 → 退出 0 + 战斗头 + [结束]） |
| AC-10 | 静息 trace | ✅ | `RestingTrace_M1Range`（进程级：active 0.535~0.771 与 M1 实测一致） |
| AC-11 | 确定性 | ✅ | `Determinism_ScriptedInput_SameOutput`（同种子同脚本化输入 → 逐字符相同） |
| AC-12 | 异常 | ✅ | `InvalidArgs_Exit1`（--seed abc → 退出 1 + stderr 用法） |
| AC-13 | 渲染格式 | ✅ | `RenderRound_AllSections`（[顺序]/[a(t)]/[因子] 行 + F4 格式） |

### spec §七 自检清单

1. [x] **数学公式逐项对照**——结算 m 重算与 events §5.3 同式（A1=A dealt/ExpectedDamage；A4 expected=cal.BaseMentalDamage×(1+mot)−cal.EndurancePassivePenalty）
2. [x] **数值断言全部实测**——静息区间 M1 实测（进程级）；无新数值锚点（组件级已验证）
3. [x] **计算顺序契约明确**——RenderSetup 循环前；RenderRound 回合末快照；[结束] 唯一源（v1.2 裁决）
4. [x] **接口注释先行**——全部新类 XML doc（CliArgs/PlayerActionProvider/CompositeActionProvider/WaitProvider/RoundRenderer/Program）
5. [x] **边界值覆盖**——CLI 非法 8 态、输入重试 3 次、EOF、空声明、miss 行、F4 格式、上限结束
6. [x] **确定性**——RoundRenderer 纯函数；AC-11 进程级实证
7. [x] **偏差声明完整**——B1-B8 实现对应（LastRound* 属性已落地/D1；回合末快照/3 次重试/m 重算/dataDir/名字映射/组合 provider）
8. [x] **常量复用漂移注**——PlayerHp/PlayerSan/NpcHp/NpcSan 消费；MaxRounds 结束原因；无新常量
9. [x] **类型变更声明**——无 L2 类型变更（LastRound* 是 Flow 层属性）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | TurnManager.LastRoundActions/LastRoundOrder 落地 | ✅ TurnManager.cs：StepRound 末尾写入 `_lastActions`/`_lastOrder`（决策 D1——flow spec 🔧 行承接，console 阶段实现） |
| 2 | CombatState.Salience 访问器 | ✅ flow 实现已交付（step 10）；console 渲染消费（AC-2 渲染重算） |
| 3 | 全部 AC 锚点写测试 | ✅ 23 项（渲染格式/CLI 边界/输入映射） |
| 4 | AC-11 脚本化输入 | ✅ 进程级同种子同输入逐字符相同 |
| 5 | AC-10 静息 trace | ✅ M1 实测区间（F3 渲染串 0.535~0.771） |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | FindDataDir 回溯 8 层未命中（console bin 路径层级） | 补绝对路径候选（镜像测试项目 DataDirCandidates）——环境级 |
| 2 | PlayerActionProvider 初版 EOF 立即返回（违 spec 3 次重试语义） | 修正：EOF 计为非法重试（case null 移除）——实现级 |
| 3 | 进程级测试 exe 路径层数错 | ConsoleDll() helper 统一（4 层回溯）——测试基建 |

## Comments

- 2026-08-14：创建。sign-off ✅（dog，2026-08-14）。spec v1.2（审计链：v1.0 全量 31 CONFIRMED → v1.1 → Δ 21 CONFIRMED → v1.2 → 终审 PASS + flow spec 补记）。
- 2026-08-14：实现完成——284/284 全绿（新增 23），AC-1~13 逐条 ✅，结转 5 项全部回填。

---
*创建: 2026-08-14 | 更新: 2026-08-14*
