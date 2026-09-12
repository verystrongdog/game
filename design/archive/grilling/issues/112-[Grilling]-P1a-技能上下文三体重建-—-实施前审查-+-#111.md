# #112 [Grilling] P1a 技能上下文三体重建 — 实施前审查 + #111 资格审查/六维验收表首个实战应用

> 状态：关闭 · 创建 2026-09-01 · 关闭 2026-09-01
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/112

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 问题
P1a（#72，2026-08-16 设计闭合）实施未启动：domain_role_map.json / link_contexts_tripartite.json / build_contexts_tripartite.py / rebuild-report.md 四产物均不存在。承接 #111（静态契约式模块化架构，2026-09-03 闭合）：三步资格审查流程 + 六维机械验收表在试点 IActionProvider（纯审查）之后，需要首个实战（非纯审查）检验。P1a 是数据产出/消费管线（脚本 → JSON → P1b/P1c/P5-2/P5-3 消费），恰好是 #111 推迟项「数据消费型试点验证 SchemaVersion 实际需求」的候选场景。

## 目标
1. P1a 实施前审查（#108 模式）：T1-T5 逐任务锁执行契约
2. #111 三步资格审查 + 六维验收表首个实战应用：对 P1a 每个新增产物走资格审查
3. 技能对接契约定稿：P1a 产物 schema 按 P1c SkillCatalog 消费需求字段级对齐（Q1 已定案：dk_name 端点 / fid 反查归 P1c / 不倒灌引擎语义）
4. 执行层决策（分支/分批/问题处置/验收）按 #109 模式并入本会话实施

## 指标
- Q 系列追问全部定案（每次带推荐答案）
- 实施前审查执行契约落盘（task-plan 更新）
- #111 六维验收表对 P1a 产物输出判定（PASS/FAIL/N/A 逐条）
- 四产物落地 + 验收标准 §九 逐项核验

## 六维定位
管线（实施/验证机制）为主，规则（数据语义：边集/角色分类/候选池）为辅。

## 当前状态
- Q0 边界：确认 = P1a 实施前审查 ∪ #111 清单实战应用（候选池产物性质显式声明，人工审核推迟）
- Q1 对接契约：采纳外部 AI 评审（t_6a9661752658819183ff820d48d7bbaf）——本轮定稿，dk_name/fid 边界锁定（4 条）
- 追问中：Q2 待提问

本地: .scratch/grilling-72-p1a-skill-context/

---

## 评论（4 条）

### verystrongdog · 2026-09-01

## 🔧 Q2 定案（采纳外部 AI 评审 t_6a96a2d7ed74819185311110b8b665eb「资格审查边界修正」）

**核心修正**：三步资格审查的对象是「是否应当成为 Module」，不是「这个产物是否存在契约」；②③不能在第①步判定「非 Module」后继续作为资格审查条件使用，最多作为数据契约强度审查另行执行。

**四产物裁决**：
1. `build_contexts_tripartite.py`：第一步本体判据不成立 → **非 Module**；参数注入 + 断言/测试保证正确性
2. `domain_role_map.json`：数据产物 → **非 Module**；值层校验（12→8 完整性/唯一性/值域）= 数据正确性约束，不进入 Module 三步资格审查
3. `link_contexts_tripartite.json`：数据产物 → **非 Module，但必须强化数据契约**——SchemaVersion ✅ / schema validation ✅ / 消费门禁 ✅ / 缺失或不兼容版本 fail-fast ✅ / 包装成 Module ❌。**「非 Module 的强契约数据产物」成为架构明确类别**（跨阶段消费 P1a→P1b→P1c→P5-2→P5-3，schema 漂移有跨阶段污染能力）。**闭合 #111 推迟项「数据消费型试点验证 SchemaVersion 实际需求」**
4. `rebuild-report.md`：文档产物，非审查对象

**推理链纠正**：`Module → 有契约 → 有版本` 错误；正确 = `Module? → Yes=Module审查 / No=数据/文档契约审查`。避免 #111 三步语义膨胀；不把 domain_role_map 的契约审查称为第②步 Module 资格审查。

外审存档：本地 .scratch/grilling-72-p1a-skill-context/外审-资格审查边界修正-t_6a96a2d7ed74819185311110b8b665eb.html + -解码.md

### verystrongdog · 2026-09-01

## 🔧 前置依赖核查 + function_label 缺口处置（Q3.5 定案）

**实测核查（2026-09-01）**：P1a 主路径（T1-T3）输入全部就绪——tripartite 776 CC + 112 PP + 114 BS + 47 CSTC ✅ / gameplay_labels 全量 ✅ / kroell14 14 网络 gameplay_domains 机器可读 ✅ / 边 role 全含（#106/#107 保障）✅ / 边端点 = dk_name（Q1 契约可行）✅。hansen_communities.json 缺失为已知 F-6 推迟项，不阻塞。

**发现的缺口（function_label 覆盖率）**：
- task-plan §一 声明「588 边含 function_label」，实测仅 432/888（49%）：cc 368/776、pp 64/112
- **根因（git 证据）**：66d1dd2（#92 偏侧化重建，2026-08-20）用 build_tripartite_model.py 重生成 tripartite_model.json，**覆盖了 2026-08-07 build_function_labels.py 的产物**；30108af 只修了边注释字段，未恢复 function_label 全量。`_function_labels_applied: True` 为元数据残留（声称已应用，实际部分丢失）
- task-plan 588 值为 2026-08-16 实测（#92 之前），未同步——「讨论落后」实例

**处置（用户裁决 A′）**：
1. **T4（signal_type 辅助修正）本轮推迟**——输入覆盖不足，且本就是「可选增强」（task-plan :109）
2. rebuild-report 记录根因：`function_label 实测 49% / 588 声明已失效 / 根因 #92 重生成覆盖`
3. **上游修复项单列**：build_tripartite_model.py 重生成后需重跑 build_function_labels.py（或修元数据语义）——非 P1a 范围，登记推迟
4. 主路径 T1-T3 不受影响

### verystrongdog · 2026-09-01

## 🔧 flee/disrupt 零主角色处置（Q3.6 定案，采纳外部 AI 评审 t_6a96a92648ec8191923ca4178399fee5）

**实测**：flee 出现在 148 条候选边 score 但主角色 0 次；disrupt 出现在 422 条但主角色 0 次。根因 = task-plan §四 初始权重下同域高权重角色稳定支配（threat_defense defend 0.6 > flee 0.4；social/cognitive 域 support/perceive 高于 disrupt 0.2-0.3）。

**裁决 C（外审修正版）**：
1. **本轮不改权重**——P1a 严格按既定初始权重重建，不越界重新设计角色权重
2. **§六「无全零角色」不放宽、不伪造 PASS**——标记为 **KNOWN DESIGN LIMITATION**（FAIL 类），归因既定权重参数而非重建实现错误
3. **转交 #35 校准轨**：flee/disrupt 权重修正属 #35；校准后重新验证
4. **rebuild-report 锁死 4 件事**：flee 148 候选/0 主角色；disrupt 422 候选/0 主角色；根因（同域支配）；本轮禁改权重
5. **边界声明**：「flee=0 不是没有 flee 上下文，而是当前权重无法使其成为胜出角色」——防 P4 误读为游戏无逃跑能力

外审存档：本地 .scratch/grilling-72-p1a-skill-context/外审-验收标准六修正-*.html + -解码.md

### verystrongdog · 2026-09-01

## ✅ P1a 实施完成 — 总结评论

### 决策表

| Q | 决策 | 来源 |
|---|------|------|
| Q0 | 边界 = P1a 实施前审查 ∪ #111 清单首个实战应用 | 用户 |
| Q1 | 对接契约：edge_contexts 端点 = dk_name；fid 反查归 P1c；P1a 不承担引擎语义 | 外审 t_6a966 |
| Q2 | 四产物全非 Module；link_contexts_tripartite = **非 Module 强契约数据产物**（SchemaVersion + 消费门禁）→ 闭合 #111 推迟项 | 外审 t_6a96a |
| Q3 | 六维验收表适配数据产物，6 条全判定 | 用户 |
| Q3.5 | function_label 缺口（49%）：T4 推迟 + 上游修复单列 | 用户（A′） |
| Q3.6 | flee/disrupt 零主角色 = KNOWN DESIGN LIMITATION；本轮禁改权重；归 #35 | 外审 t_6a96a926 |

### 实施结果（feat/p1a-context，4 commit）

| commit | 内容 |
|--------|------|
| 5de8968 | domain_role_map.json + build_contexts_tripartite.py + link_contexts_tripartite.json（schema v1） |
| 9eed1c9 | rebuild-report.md（重建结果/角色健康/function_label 缺口/契约字段） |
| 25a63a1 | T5 文档同步（决策树/六维状态/技能生成机制/外审归档 ×3/memory 镜像） |
| d45bb4e | 一致性清扫：技能生成机制 §二 数据源引用更新 |

**实测**：888 边 → 71 contexts → **71 候选技能**（uncovered 0）；角色分布 perceive 366 / attack_physical 246 / support 110 / approach 103 / defend 57 / attack_mental 6 / **flee 0 / disrupt 0（KNOWN DESIGN LIMITATION）**

### 六维验收表（Q3 定案——首个 6 条全判定实战）

| # | 判定 | 证据 |
|---|------|------|
| ① 独立能力边界 | **PASS** | 双视图互为转置（脚本断言 + 独立复验） |
| ② 多实现同一契约 | **PASS** | schema/version 契约字段就绪（P1b/P1c/P5-2/P5-3 四方消费同一结构） |
| ③ 消费者依赖接口 | **PASS** | 消费方按 schema/version 解析（对标 alpha_patterns/env_tones 先例） |
| ④ 版本敏感性 | **PASS**（试点 N/A → 首次实判） | 跨阶段 schema 漂移 → 版本契约必要；**闭合 #111 推迟项** |
| ⑤ 装配失败前置 | **PASS** | version 不匹配 → 加载期 fail-fast（消费门禁就绪） |
| ⑥ 无多余抽象 | **PASS** | 无 Module 包装/无运行时状态字段（顶层键 7 个纯数据） |

### 验收（task-plan §九）

✅ 7/7 全过；cross_refs 718/723（2 dead + 2 warning 均为既有问题）；list_deprecated_terms 无 P1a 相关新增

### 推迟清单

- T4 signal_type 辅助修正（function_label 49% 输入不足）→ 上游补跑 build_function_labels.py 后评估
- flee/disrupt 权重校准 → #35 数值校准轨（校准后复验 §六）
- 上游修复：build_tripartite_model.py 重生成后需重跑 build_function_labels.py（git 66d1dd2/30108af）
- hansen_communities.json 补齐（F-6 独立话题）
- 技能命名/独特效果/锚点对齐 → 技能系统 grilling（P1c 后）
- P1b/P1c 实施（技能可执行管线；P1a 为第 1 段，对接完成 ≠ 技能可玩）

---
*导出: 2026-09-12 | 来源: GitHub issue*
