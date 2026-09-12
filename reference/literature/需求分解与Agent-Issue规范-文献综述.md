# 需求分解与 Agent Issue 规范：文献综述与可操作规则

> 把需求切成"可逐步实现的小步"的成熟方法论（INVEST / 纵切 / walking skeleton / SPIDR / expand-contract / spike / GWT / 依赖 DAG），以及 AI Agent 场景的 issue 规范（AGENTS.md、agent-ready 判据、ready-for-agent brief）。每条给出源 URL、原文摘录、落地字段与反例。
>
> **来源**：2026-09-12 由 subagent 联网检索一手资料（xp123.com、martinfowler.com、humanizingwork.com、alistair.cockburn.us 存档、agents.md、pragprog.com、cucumber.io、GitHub Docs、code.claude.com、mattpocock/skills、arXiv/SWE-bench）整理，未做本地实验验证。
>
> **定位**：本文是**文献侧输入**，不是本仓规约。落地产物见 [issue 创建约束与需求分解](../../design/engineering/issue-process.md)（其 §八 记录了逐条借鉴与取舍）。文中提到的 `.scratch/<feature>/issues/` 本地 issue 模型属**历史**：该路径已在 2026-09-12 重构中移出仓库，`design/conventions/agents/issue-tracker.md` 是保留原样的死规范。

---

## 目录

1. [一、A 组：分解方法论](#一a-组分解方法论)
2. [二、B 组：AI Agent 场景](#二b-组ai-agent-场景)
3. [三、分解质量判据清单](#三分解质量判据清单)
4. [四、模板字段](#四模板字段)
5. [五、与本仓的对接](#五与本仓的对接)

---

## 一、A 组：分解方法论

### A1 INVEST（Bill Wake，2003）

**规则**：六个属性 Independent / Negotiable / Valuable / Estimable / Small / Testable。Independent 允许"暂时搭脚手架让故事能独立验证"。

> 原文（<https://xp123.com/invest-in-good-stories-and-smart-tasks/>）：
> I – Independent … we'd like them to not overlap in concept, and we'd like to be able to schedule and implement them in any order.
> E – Estimable … Sometimes a team may have to split a story into a (time-boxed) "spike" that will give the team enough information to make a decent estimate, and the rest of the story that will actually implement the desired feature.
> S – Small … Stories typically represent at most a few person-weeks worth of work.
> T – Testable … Writing a story card carries an implicit promise: "I understand what I want well enough that I could write a test for it."
> V – Valuable … Think of a whole story as a multi-layer cake … We want to give the customer the essence of the whole cake, and the best way is to slice vertically through the layers. … a full database layer (for example) has little value to the customer if there's no presentation layer.

**落地字段**：`Independent`→ 必须写 `Blocked by:`；`Estimable`→ 超过一人日先开 `Type: spike`；`Testable`→ `## AC` 段不得为空。

**反例**：`As a developer, I want a database diagram, so that I know the structure` —— Humanizing Work 明确判定"仍是 task，不是 story"。

### A2 纵切 vs 横切 / walking skeleton / tracer bullet

**三条"可独立验证"判据**：① 能写出一句**用户可观察的行为前后差**；② 完成后系统整体**仍可运行**；③ 起点是**最小端到端连接**，而非先把某层做"对"。

> Cockburn（《Crystal Clear》2004，站点存档 <https://web.archive.org/web/20080511171042/https://alistair.cockburn.us/index.php/Walking_skeleton>）：
> A Walking Skeleton is a tiny implementation of the system that performs a small end-to-end function. It need not use the final architecture, but it should link together the main architectural components.
> Note that each subsystem is incomplete, but they are hooked together, and will stay hooked together from this point on.
> Other authors have other names for similar sorts of ideas. … Dave Thomas and Andy Hunt use what they call "tracer bullets" (Hunt 1999).
> A walking skeleton, on the other hand, is permanent code, built with production coding habits, regression tests, and is intended to grow with the system.

> Pragmatic Programmer Tip #20（<https://pragprog.com/tips/>）：Use Tracer Bullets to Find the Target —— Tracer bullets let you home in on your target by trying things and seeing how close they land.

> Humanizing Work（<https://www.humanizingwork.com/the-humanizing-work-guide-to-splitting-user-stories/>）：
> Vertical slice is a shorthand for "a work item that delivers a valuable change in system behavior such that you'll probably have to touch multiple architectural layers to implement the change." When you call the slice "done," the system is observably more valuable to a user.
> This is in contrast with a horizontal slice, which refers to a work item representing changes to one component or architectural layer that will need to be combined with changes to other components or layers to have observable value to users.

**反例**：先"把 DB 层做完"再"把 API 做完"再"把 UI 做完"——每片单独都不可验证。

### A3 SPIDR 与九种拆分模式

**规则**：五轴 **S**pike / **P**aths / **I**nterfaces / **D**ata / **R**ules。Humanizing Work 现行展开为九模式（Workflow Steps、CRUD、Business Rules、Data Variations、Data Entry、Major Effort、Simple/Complex、Defer Performance、Spike），元模式是"找到核心复杂度 → 变化降到一"。两条选择标准：**选允许你扔掉低价值切片的拆法**、**选尺寸更均匀的拆法**。

> TeamRetro（二手，<https://www.teamretro.com/guides/agile-estimation-guide/spidr-story-splitting/>）：
> SPIDR is five reliable ways to split a user story: Spike, Path, Interface, Data, Rules. … The test for every cut: if slice one needs slice two to function, it's a horizontal split in disguise, not SPIDR.

> Humanizing Work 原文：
> Pattern #9: Break Out a Spike … Do a time-boxed spike first to resolve uncertainty around the implementation. … The spike split is last because it should be your last resort.
> Meta-Pattern: Find the core complexity. … Identify the variations. … Reduce all the variations to one.
> Choose the split that lets you deprioritize or throw away a story. … Choose the split that gets you more equally sized small stories.
> （Workflow Steps）the most obvious split—one step at a time from beginning to end—is the wrong way to go.

**归属提示**：TeamRetro 记为 Mike Cohn 提出，Humanizing Work 的流程图署 Richard Lawrence；引用时注明归属有分歧更稳。

**反例**：按"workflow 从头到尾一步一个 issue"拆——HW 明确说这是错的拆法。

### A4 Expand/Contract（parallel change）与 Strangler Fig

**规则**：不可回滚的接口变更强制三段：**expand**（新旧并存）→ **migrate**（消费者迁移）→ **contract**（删除旧路径）。难回滚的整体替换走 strangler：新东西先建在旁边，逐块搬行为，不做大爆炸替换。

> Fowler/Sato, Parallel Change（<https://martinfowler.com/bliki/ParallelChange.html>）：
> Parallel change, also known as expand and contract, is a pattern to implement backward-incompatible changes to an interface in a safe manner, by breaking the change into three distinct phases: expand, migrate, and contract.
> In the expand phase you augment the interface to support both the old and the new versions.

> Fowler, Strangler Fig（<https://martinfowler.com/bliki/StranglerFigApplication.html>）：
> Like the fig, it begins with small additions, often new features, that are built on top of, yet separate to the legacy code base. As we do this we move bits of behavior from the legacy system into the new code base.
> （四活动）Understand the outcomes you want to achieve / Decide how to break the problem up into smaller parts / Successfully deliver the parts / Change the organization …

**落地**：`RFC` 至少拆三个 issue，各标 `Phase: expand|migrate|contract`，各自可回滚。

**反例**：同一个 PR 里改接口签名 + 改所有调用点。

### A5 Spike 与实现分离

**规则**：spike 是**被丢弃的学习载体**，产出结论与估算而非代码；用生产规范写的端到端最小实现叫 walking skeleton，两者不可混。

> Cockburn 同页：
> A spike is "the smallest implementation that demonstrates plausible technical success." The spike typically takes between a few hours and a few days to complete, and is thrown away afterward, since it was built with nonproduction coding habits. A spike serves to answer the question: Are we headed in the wrong direction?

> Humanizing Work：In the "investigate" story, the acceptance criteria should be questions you need answered. Do just enough investigation to answer the questions and stop.

**落地字段**：`Type: spike` + `Timebox:` + `AC = 待回答问题列表` + `Output: 结论写入 design/…` + 明确"不产出主干部代码"。

**反例**：spike 分支直接合入主干，成为无测试的生产代码。

### A6 ATDD / Given-When-Then 验收标准

**规则**：先写客户测试再实现；每条 AC 用 GWT 三段写，一个场景 = 一个具体例子，同构变体用 Examples 表。

> Wake：Several teams have reported that by requiring customer tests before implementing a story, the team is more productive.

> Fowler, Given-When-Then（<https://martinfowler.com/bliki/GivenWhenThen.html>）：
> The given part describes the state of the world before you begin the behavior you're specifying in this scenario. … The when section is that behavior that you're specifying. … the then section describes the changes you expect due to the specified behavior.

> Gherkin 参考（<https://cucumber.io/docs/gherkin/reference/>）：Scenario Outline 用 `Examples` 表替代重复场景；一个 Scenario 表达一个业务规则。

**落地**：AC 每条 = GWT 三行 + 一行可执行命令与期望输出（对应 Anthropic 的"给 agent 一个能跑的检查"）。

**反例**：`Triage should work correctly`（Matt Pocock 模板里标注的 Bad 例）。

### A7 依赖建模：DAG / critical path / 显式 blocked-by

**规则**：把 issue 集合当 DAG。关键路径 = 依赖链最长的那条；每条依赖必须字段化，不能只写在正文里。可并行轴 = 不碰同一批文件/同一契约的独立面。

> Critical path method（<https://en.wikipedia.org/wiki/Critical_path_method>）：
> A critical path is determined by identifying the longest stretch of dependent activities and measuring the time required to complete them from start to finish.

> GitHub Docs, Creating issue dependencies（<https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies>）：
> Issue dependencies let you define issues that are blocked by, or blocking, other work.
> `gh issue create --title "TITLE" --body "ISSUE-DESCRIPTION" --blocked-by N --blocking M`
> Blocked issues are marked with a "Blocked" icon on your project boards or repository's Issues page, so you can easily identify bottlenecks.

**落地**：每个 issue 头部 `Blocked by:` / `Blocks:` / `Parallel-axes:`；先做关键路径上的一环。

**反例**：把"其实要先改 X"埋在执行步骤段落里，下游开工才发现，返工。

---

## 二、B 组：AI Agent 场景

### B8 AGENTS.md 与 agent-ready 判据

**规则**：AGENTS.md 是给 agent 的 README（安装/构建/测试命令 + 约定）；任务侧要求**可运行的验证手段**与**明确边界**。GitHub 另给**不该委派**清单，可反向当 needs-human 判据。

> agents.md（<https://agents.md/>）：
> Think of AGENTS.md as a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.
> README.md files are for humans … AGENTS.md complements this by containing the extra, sometimes detailed context coding agents need.

> GitHub Copilot cloud agent 最佳实践（<https://docs.github.com/en/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks>）：
> An ideal task includes: A clear description of the problem to be solved or the work required. / Complete acceptance criteria on what a good solution looks like (for example, should there be unit tests?). / Directions about which files need to be changed.
> Issues that you may choose to work on yourself, rather than assigning to Copilot, include: Complex and broadly scoped tasks … Broad-scoped, context-rich refactoring problems requiring cross-repository knowledge and testing … Sensitive and critical tasks … Ambiguous tasks … Learning tasks.

> Anthropic, Claude Code best practices（<https://code.claude.com/docs/en/best-practices>）：
> Give Claude a check it can run: tests, a build, a screenshot to compare. It's the difference between a session you watch and one you walk away from.
> Explore first, then plan, then code. … If you could describe the diff in one sentence, skip the plan.
> Provide specific context in your prompts … Scope the task. Specify which file, what scenario, and testing preferences.
> （AGENTS.md/CLAUDE.md 写法）For each line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it.

**落地**：issue 必须含"验证命令 + 期望输出"；CLAUDE/AGENTS 只放全局适用项，领域知识放按需加载的文档。

**反例**：把"提升代码质量"当作可委派 issue——属 Ambiguous tasks。

### B9 公开仓库中的 agent brief 实例

**Pocock 的 `ready-for-agent` + AGENT-BRIEF**（<https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/AGENT-BRIEF.md>、<https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md>）。状态机：`needs-triage → needs-info / ready-for-agent / ready-for-human / wontfix`。四条硬规则：

> An agent brief is a structured comment posted on a GitHub issue or PR when it moves to `ready-for-agent`. It is the authoritative specification that an AFK agent will work from. … the agent brief is the contract.
> **Durability over precision** … **Don't** reference file paths: they go stale. **Don't** reference line numbers.
> **Behavioral, not procedural** — Good: "The `SkillConfig` type should accept an optional `schedule` field of type `CronExpression`" / Bad: "Open src/types/skill.ts and add a schedule field on line 42".
> **Complete acceptance criteria** … Each criterion should be independently verifiable.
> **Explicit scope boundaries** — State what is out of scope. This prevents the agent from gold-plating.
> （模板骨架）Category / Summary / Current behavior / Desired behavior / Key interfaces / Acceptance criteria / Out of scope
> （`ready-for-human`）same structure as an agent brief, but note why it can't be delegated (judgment calls, external access, design decisions, manual testing).

**SWE-bench 的任务描述特征**（<https://arxiv.org/abs/2310.06770>、<https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf>）：

> SWE-bench, an evaluation framework consisting of 2,294 software engineering problems drawn from real GitHub issues and corresponding pull requests across 12 popular Python repositories. Given a codebase along with a description of an issue to be resolved, a language model is tasked with editing the codebase to address the issue.
> （人工标注的前置假设）The issue description is sufficiently well-specified to understand what the problem is, and what the correct solution should look like. / The tests are correctly scoped to the issue i.e. they correctly test for a solution exactly as described in the issue description.
> （Issue 明确度 0–3 分档）0: well-specified and it is clear what is required for a successful solution. … 3: It is almost impossible to understand what you are being asked to do without further information.

即：**issue 是否足够明确**与**验证是否恰好覆盖该 issue** 是 benchmark 的两个过滤条件——正是 issue 质量判据本身。

**本仓现状**：`.scratch/<feature>/issues/NN-<slug>.md` + `Status:` + `Blocked by:` + 五角色标签已落地；缺口是 AGENT-BRIEF 的四条硬规则（不写路径行号 / 行为化 / AC 独立可验 / 显式 Out of scope）。

### B10 应避免的失败模式

| 失败模式 | 症状 | 修法 | 依据 |
|---|---|---|---|
| 巨型不可验证 issue | 说不出"跑什么命令算过" | 先切 walking skeleton，补可运行验证 | Anthropic"给一个能跑的检查" |
| 伪分解（按文件/层） | "建 DB 表""改 UI 组件" | 纵切：穿层 + 用户可观察行为 | Wake 蛋糕段 / HW 纵切定义 |
| 隐藏依赖导致返工 | 开工才发现要先改 X | `Blocked by:` 字段化 + 关键路径排序 | GitHub deps / CPM |
| 验收标准不可测 | "正确""合理""优化" | GWT + 命令 + 期望输出 | Fowler GWT / Pocock |
| task 冒充 story | "As a developer, I want a diagram" | 归 `Type: task`，不计入切片 | HW 原文判定 |
| spike 产物落地成代码 | 实验代码进主干 | spike 只交结论，代码丢弃 | Cockburn spike 定义 |
| 大爆炸替换/接口硬改 | 一个 PR 改签名 + 全部调用点 | expand → migrate → contract | Fowler Parallel Change |
| 把高不确定任务直接委派 | agent 产出一个"看似合理"的方案 | 先 spike/plan，再实现 | Copilot 的 Ambiguous 清单 |
| 伪并行 | 两个 issue 改同一文件/契约 | 声明 `Parallel-axes:` | SPIDR 的"横切伪装"检验 |

---

## 三、分解质量判据清单

对每个 issue 逐条自检，**出现一个 No 就退回 triage**：

1. 能一句话说出用户/下游可观察的行为变化吗？
2. 有跑完即能判定通过的命令或场景吗？
3. AC 是否逐条独立可验，而非互相配合才能判断？
4. 是否明确列出 Out of scope？
5. 是否声明 `Blocked by:`（没有也写 none，不留空）？
6. `Blocked by` 链上前置是否都已 resolved，或本 issue 不在关键路径？
7. 是否声明 `Parallel-axes:`（不共享文件与契约）？
8. 产物是否被下一个 issue 消费？无人消费则为何现在做？
9. 是否端到端穿过必要层并连通（walking skeleton 判据）？
10. 完成后系统仍可运行/可试玩，而非"某一层做完了"？
11. 拆分轴是行为/流程/数据/规则，而非"按文件"或"按层"？
12. 是否给了执行者可运行的验证手段（测试/构建/截图）？
13. 能否去掉文件路径与行号，只留行为契约？
14. 无人可问时信息是否足够完成（AFK / well-specified）？
15. 做不完时能否 1 天内退化成 spike 并把结论写回设计？
16. 是否属于"该自己做"（广泛重构、安全与鉴权、生产事故、架构一致性）？
17. 难回滚改动是否拆成 expand/migrate/contract 三段？
18. 产出是结论还是代码，是否写明（spike 不产主干部代码）？
19. 范围/证据标准/依赖实质变动后是否回到 triage 重新准入？

---

## 四、模板字段

```markdown
Status: needs-triage | needs-info | ready-for-agent | ready-for-human | wontfix
Type: task | implementation | research(spike) | bug | rfc
Blocked by: NN, NN            # 无则 none
Blocks: NN
Parallel-axes: <不共享文件/契约的独立面>
Phase: expand | migrate | contract   # 仅 rfc
Timebox: 1d                   # 仅 spike

## 目标行为（一句话，可观察）
## 现状 → 期望
Given … / When … / Then …
## 关键接口（类型、签名、配置形状；不写文件路径与行号）
## AC
- [ ] Given … When … Then …（可独立验证）
- [ ] 验证命令：`…` → 期望输出：…
## Out of scope
## 消费方：<下一个 issue 用它做什么>
```

---

## 五、与本仓的对接

- `WORKFLOW.md` 的"两次闭合"（门禁 + 消费）对应 INVEST 的 Testable 与判据 8，可直接作为本地分解标准。
- `Type: Experiment` ≈ spike：需补 `Timebox` 与"结论写入哪份 design 文档"。
- `Type: RFC` ≈ 难回滚决定：应强制 expand/migrate/contract 三段拆分。
- 能力四轴（Design/Implementation/Integration/Health）已是证据绑定字段，可直接当 issue 的证据格式。

---

*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [issue 创建约束与需求分解](../../design/engineering/issue-process.md), [WORKFLOW.md](../../WORKFLOW.md), [Triage 标签](../../design/conventions/agents/triage-labels.md)*
