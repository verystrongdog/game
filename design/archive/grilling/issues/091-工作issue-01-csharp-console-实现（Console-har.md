# #91 工作issue 01: csharp-console 实现（Console harness）

> 状态：关闭 · 创建 2026-08-20 · 关闭 2026-08-30
> 标签：维度:管线, implementation
> 原始：https://github.com/verystrongdog/game/issues/91

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-console/impl/issues/01-console-implementation.md

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
- 2026-08-30：**关闭**（Grilling #91）——关闭审查发现 12 引擎测试失败，根因 = #92 数据回归（重跑生成器覆盖注释产物，EdgeRole 默认 Active 致 b_j/M1 漂移）+ 镜像契约未同步。修复：恢复数据（重跑 build_function_labels.py，commit 30108af）+ 镜像契约测试更新（d2c76db）+ 防再犯门禁（373c2a0，validate_tripartite_annotations.py）。**当前 HEAD：309/309 全绿**，AC-1~13 ✅，M1 锚点保持 HARD。见 [决策树 Grilling #91](../../../docs/决策树.md)。

---
*创建: 2026-08-14 | 更新: 2026-08-14*

---

## 评论（1 条）

### verystrongdog · 2026-08-30

## 🏁 Grilling #91 关闭总结 — csharp-console 实现（Console harness）

**形态**：关闭审查（AC-1~13 逐项对照 + 门禁复跑）。实现本身无回归（commit 1f86b67）；发现 12 个引擎测试失败，根因 = **#92 数据回归**（非本 issue 实现问题）。

### 事故根因
#92（66d1dd2，2026-08-20）重跑 build_tripartite_model.py 覆盖了两步管线的注释产物（role/function_label/gameplay_labels/description 从 4 类边全部丢失）→ EdgeRole 枚举默认 Active(0) → 99 条 modulating 边静默升值 1.0 → CorticalBias b_j 漂移 → M1 静息不动点漂移（0.535~0.771 → 0.558~0.814）→ 9 失败；另 3 个为 #92 D6 镜像契约演进（测试未同步）。

### 决策表
| # | 决策 | 内容 |
|---|------|------|
| Q1 | 边界 | 12 失败纳入 #91（#105 排队依赖 + 同根因闭环） |
| Q2 | M1 锚点 | **保持 HARD 不降级**（数据恢复后实测回原窗口；C 混合策略仅作未来政策记录） |
| Q3 | 恢复手段 | 重跑 build_function_labels.py（非 git checkout——旧数据无 lateralization） |
| Q4 | 镜像契约 | 2 测试更新为 #92 D6 语义（镜像=主变体完整剖面+mirror_of） |
| Q5 | 门禁 | ① validate_tripartite_annotations.py + ② 生成器警告；原子化重跑否决（privileged 手工数据丢失）；③ 引擎 fail-fast 后置 |

### 写入验证表
| 项 | commit | 验证 |
|----|--------|------|
| 数据恢复（4 字段逐边复原，lateralization 保留） | 30108af | ✅ 全量序列化集合与 66d1dd2^ 逐边 0 差异 |
| 镜像契约测试 + FunctionProfile 注释 | d2c76db | ✅ GameDataLoaderTests 24/24 |
| 防再犯门禁（校验脚本 + 生成器警告） | 373c2a0 | ✅ 真实数据 PASS / 损坏数据 FAIL 双向自测 |
| 关闭文档（决策树/六维状态/陈旧声明） | f690820 | ✅ 一致性清扫「待 #91 关闭」残留 0 |

### 最终门禁
**309/309 全绿**（Failed: 0, Passed: 309, Skipped: 0）——AC-1~13 逐条 ✅，结转清单 5 项 ✅。

### 推迟
- 引擎 fail-fast（EdgeRole 缺失默认 Active 静默失败）→ 独立决策（建议 #105 前定）
- #105（P2 情境系统实施）→ **阻塞解除，可启动**

---
*导出: 2026-09-12 | 来源: GitHub issue*
