# Issue tracker: Local Markdown

Issues and specs (you may know a spec as a PRD) for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## 二层布局（2026-08-12 新增）

开发流水线将 `.scratch/<feature-slug>/` 分为两层：

```
.scratch/<feature-slug>/
├── map.md                  ← 顶层 wayfinding
├── design/                 ← 任务层：规格定义 + 审计 + 签字
│   ├── spec.md             ← 实现规格（带版本号 + 变更日志）
│   ├── issues/             ← 任务issue（task 类型）
│   └── audit/              ← report.md + sign-off.md
└── impl/                   ← 实现层：代码 + 证据式自审
    ├── issues/             ← 工作issue（implementation 类型）
    └── fixtures/           ← 共享测试数据，归 01 号工作issue 管理
```

- 任务issue 产出 spec.md → AI workflow 审计 → 人类 sign-off 批准 → 工作issue 按 spec@版本号实现
- 工作issue 内完成证据式自审（build/test 输出 + AC 逐条对照）后置 `resolved`
- 变更管理：实现中发现 spec 缺陷时分级处理（L1 笔误直接修 / L2 语义修正→升版+Δ审计 / L3 推翻设计→退回任务层）
- 完整流水线定义见 `/home/dog/.claude/plans/enumerated-wandering-mitten.md`

## GitHub 镜像同步（2026-08-12 新增）

本地 issue 文件为真相源，通过 `code/tools/sync_issues.py` 镜像到 GitHub（幂等，可随时重复运行）：

```bash
python3 code/tools/sync_issues.py           # 全量同步
python3 code/tools/sync_issues.py --dry-run # 预览将执行的操作
```

约定：

- 每个 issue 文件的元数据行包含 `Status:` / `Type:` / `维度:` / `GitHub: #NN`（`维度:` 用于 GitHub label `维度:X`）
- H1 标题 = GitHub issue 标题；元数据行之后的内容 = GitHub issue body（body 首行自动加 `本地: <相对路径>` 指针）
- 无 `GitHub:` ref → 脚本创建 GitHub issue 并把 ref 写回本地文件
- 有 ref → 脚本用本地内容覆盖更新 GitHub body
- 本地 `Status: resolved` 或 `closed` → 脚本关闭对应 GitHub issue
- Type → GitHub label 映射：`task`→`ready-for-agent`，`implementation`→`implementation`，`hotfix`→`hotfix`，`grilling`→`grilling, needs-triage`

流水线操作本地 issue（创建/更新状态）后立即运行一次同步脚本。

## Issue 内容充实规范（2026-08-13 新增）

GitHub issue 的读者是人类——issue 是 **brief 层**（目标/指标/判断），资产细节留在 spec.md / plan.md / audit/report.md。每个 issue 元数据行之后必须携带以下章节，默认顺序：

**任务issue**（design/issues/）：

```markdown
## 问题（这件事要解决什么）
<!-- 先讲问题再讲交付物：本 feature 的使命、为什么是现在、不做会怎样。
     如 csharp-engine 的使命=端到端验证神经动力学公式，Unity 前先在 C# 暴露数值问题 -->

## 目标
<!-- 一段话：本 issue 要达成什么（交付物），解决 ## 问题 中的哪一环 -->

## 指标
<!-- 可衡量的成功标准（数字）：修复数/AC 数/测试数/专家 verdict/门禁 -->

## 工作方式
<!-- agent 怎么干活的：读了什么、workflow 结构（几个专家、什么角色）、核实路径 -->

## 判断与取舍
<!-- 关键整合判断 + 理由：采纳/不采纳什么、冲突怎么升级、风险怎么处置 -->

## 范围
## 追问
## 决策
## 产出
## Comments
```

**工作issue**（impl/issues/）：`问题` + `目标` + `指标` 必须，`工作方式`/`判断与取舍` 按实际复杂度取舍。

**收尾简要**：issue 置 `resolved` 时，在 `## Comments` 末尾追加一条 dated 条目：目标达成与否 → 指标实际值 → 遗留项。格式参考 `csharp-data-layer/impl/issues/01-data-loaders.md`。

**不进 issue 的内容**：完整思考轨迹（tool 调用日志）——那会让 issue 不可读；保留 distilled 判断链 + 指向 report.md Trace Table / 会话 transcript 的链接。

**资产嵌入规则**：GitHub 镜像只同步 issue 文件本身——spec.md / plan.md / audit/report.md / sign-off.md 等资产在 GitHub 上**打不开**。issue 引用审计发现、关键参数、结转清单时，必须把内容本身嵌入 issue 正文（表格），裸相对链接在 GitHub 不可点击。可附 `（本地: .scratch/...）` 标注供本地查阅。参照 `csharp-engine/design/issues/00-plan-revision.md`（Trace Table 全表 + 结转清单嵌入）。
