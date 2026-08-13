# map: csharp-speed

> csharp-engine step 7（plan §十一）——SpeedScoreCalculator + TurnOrderBuilder：三成分速度排序（察觉/决断/执行）+ 掷硬币破平。Status: claimed（2026-08-13）

## Notes

- 依赖 csharp-engine plan §4.5（方案B：SpeedScoreCalculator 纯数值 + TurnOrderBuilder 排序破平，2026-08-06 D4/D5 已定）+ §十 SpeedScore 测试行（3 RED 用例）+ §十二-6（决断分公式冲突：按 回合战斗流程 §3.3 mean(c_loop) 实现，运行时状态模型 §8.1 为指针）+ §十二-8（分量归一化 mean 偏差）+ §十三-4（Putamen 代理 = a_SD1_somatic，用户决策点）
- 上游交付：csharp-data-layer（GameData/FunctionProfile cstc_* 字段）、csharp-engine-types（SpeedComponents.cs 0 字节占位待实现）、csharp-wmatrix（canonical 69 行序契约）、csharp-wc-dynamics（WcState + M1 链）、csharp-tone（ToneState + M1 实测值表 69 行）、csharp-cstc（GurneyState + CstcGating——决断分 c_loop 与执行分 a_SD1 的数据源）
- 设计文档依据：回合战斗流程 §3.1-3.5（三成分模型/首次回合/后续回合/破平/等待）+ 运行时状态模型 §7.1（Phase 3 执行顺序）、§7.3/§7.3.1（初始化 + M1 静息不动点）、§8.1（输出映射表——与 §3.2/§3.3 冲突，plan §十二-6）
- 关键实测（任务issue 01 数据实测第一轮）：a_SD1 一步输出 == 300 回合固定点（逐位相等 0.9848941，SD1 纯前馈）→ 「a_SD1 静息定义」问题自动消解；首回合静息 speed = 0.7117510

## Decisions-so-far

- [任务issue 01](design/issues/01-speed-spec.md) → 数据实测第一轮（9 条：4 察觉节点存在性/静息锚点/🔑a_SD1 一步==300回合逐位相等/首回合 speed 两变体/回落粒度对比/RED 算术）→ claimed（2026-08-13）
- **Q 裁决（2026-08-13 用户）**：Q1=A（首回合 = 静息值，删 §3.2 残留注）、Q2=A（逐节点回落）、Q3=A（Putamen 代理 = a_SD1_somatic——SD1 = 壳核直接通路的 Gurney 结构同构）。Q3 用户要求详细说明后裁决
- **设计文档修正写回**（commit 223b840 + a8582fe）：回合战斗流程 §3.2 残留注删除+静息值定义+Phase 3 图行 / 运行时状态模型 §8.1 指针化+§7.3 战斗初始状态=静息不动点澄清 / plan §4.5 回落语义+§十二-6+§十三-1/4 闭合 / term_registry 速度排序 entry 更新
- **spec v1.0**（commit a8582fe）：[spec.md](design/spec.md) §一~§八 + AC-1~14 + 偏差 B1（首回合交付机制：计算器无特判，状态即静息）/B2（分量归一化 mean）/B3（Putamen 代理）/B4（权重偏移不覆盖）+ 参数速查表
- **全量审计 v1.0 完成（2026-08-13）**：[report.md](design/audit/report.md)——12 agent（3 专家 → 去重 → 9 条 error/warning 对抗验证）：**0 ❌ / 7 ⚠️ CONFIRMED / 2 REFUTED / 15 info，有条件通过**。数学公式与全部锚点经独立复算零错误；7 ⚠️ 全为 spec 层可修（引用指针/防御声明/AC 补强）
- **spec v1.1（commit 3f35d9c）**：F1-F7 全修 + L1 批 12 条 + AC-15；设计文档写回补全（cb68803 回合战斗流程 求和→均值；5387d98 技能生成机制 + 皮层动力学 §8.1 残留公式指针化）

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 ✓ → 设计文档写回 ✓ → spec v1.0 ✓ → 全量审计 ✓（0❌/7⚠️/2refuted/15info）→ spec v1.1 修复 ✓ → Δ审计 ⏳ → sign-off ⏳ → 工作issue 01 实现 + 自审 ⏳ → feature 闭合 ⏳

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [任务issue 01](design/issues/01-speed-spec.md)*
