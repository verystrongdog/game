---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

> ## ⚠️ 本项目已停用此流程（2026-09-12）
>
> 这个 skill 是**通用工具**：需要就某个决策被逐题追问时，仍可手动调用。但它**不再是本项目的默认流程**——
>
> - 原先承载它的 `CLAUDE.md`（十步强制流程）**已删除**
> - 停用理由：它产出了本仓库 **47% 的 markdown 行数**，却只贡献 **31% 的硬约束**（其余是过程纪律与格式规范），投入产出比不成立；而且它**没防住 5 个真实正确性断裂**（敌人 HP 静默漂移、模态迁移只做一半、21 处归档隔离违规等），那些是机械校验发现的
> - 历史记录保留在：[决策树](../../../design/decisions/README.md)（93 条目）· [各轮源记录](../../../design/archive/grilling/) · [122 个 issue 存档](../../../design/archive/grilling/issues/README.md)
> - 现行规约见：[项目规约](../../../design/conventions/README.md) · [协作指南](../../../CONTRIBUTING.md)
>
> 下文 Step 0-3。若你确实要跑一轮 grilling，把它当作**可选的自律工具**，不是必须走完的仪式。

## 核心原则

**引用即读取**：任何事实性引用（参数、公式、已有决策、文件路径、数据结构、交叉引用），必须先 `Read` 源文件确认。不得凭记忆引用。规范正文见 [写作与引用规范](../../../design/conventions/writing-and-references.md) 与 [项目规约](../../../design/conventions/README.md) §四。

---

## Step 0 — 定位（每次 grilling 前）

### 0.1-0.2 基础定位
1. **读取路由表**：`design/framework/six-dimensions.md`（项目根目录下），确认本次话题属于哪个维度，在全局优先级中的位置
2. **读取维度索引**：`design/framework/dimensions/<维度名>.md`，确认该维度已有设计和空缺

### 0.3-0.5 前置资料包（v2 新增）
3. **读取所有直接相关的设计文档**，建立"已读清单"。容量规则：如相关文件 > 5 个，优先读取索引文件（维度 .md）和最高层级设计文档，具体子系统文件标记为"待按需读取"（追问涉及时再读）
4. **读取决策树中相关分支的历史记录**（`grep` 话题关键词 → 读取命中段）
5. **读取相关数据文件**（如涉及 JSON 数据/参数表）

### 0.6 资料包完整性声明（v2 新增）
6. **输出声明**，格式如下：

```markdown
## Step 0 — 前置资料包

### 预读（已完整读入上下文）
- [x] `design/framework/six-dimensions.md`
- [x] `design/framework/dimensions/<维度名>.md`
- [x] ...

### 待按需读取（标记为可能相关，追问涉及时再读）
- [ ] `xxx.md` — 理由

### 声明
以上"预读"清单中的文件构成本次 grilling 的资料基础。
未在预读或按需读取清单中的事实性引用一律视为违规。
共 N 个预读 + M 个待按需读取，在上下文容量安全范围内。
```

7. **确认话题边界**：向用户确认"本次 grilling 聚焦 [维度] 的 [具体话题]，依赖 [X]，阻塞 [Y]"

---

## Step 1 — 话题验证

`grep` `design/decisions/` 中是否已有同名话题的「决策」或「被否决」→ 有则告知用户。

---

## Step 2 — 追问（逐题进行）

### 2.0 定义基线声明（v3 新增 — 术语复用认知陷阱防御）

在设计提案之前，AI 必须先查询 `data/term_registry.json`，获取本次提案涉及术语的项目内定义和已否决的默认模型。

**为什么需要这个步骤**：项目大量使用现实世界已有词汇（月光/感染/场/链路/防御）来承载自定义游戏概念。只要这些词汇的默认现实含义还在 AI 认知中处于"更快激活"的位置，旧模型就会在生成时劫持输出——即使新定义已被读过。术语注册表将定义和旧模型集中管理，AI 不再依赖临时搜索和回忆。

**触发条件**：每轮追问在陈述"我的建议"之前，必须查询注册表并输出基线。无例外。

**格式**：

```markdown
### 第 N 题 — [问题]

#### 定义基线（从 term_registry.json 查询）

| 术语 | 项目定义 | 来源 | 旧模型（已否决的默认模型） |
|------|---------|------|---------------------------|
| [术语A] | [来自 term_registry.json 的 definition 字段] | `term_registry.json` + `源文件.md` §N | [来自 old_model 字段，或 —（无偏离）] |
| [术语B] | [同上] | ... | — |

#### 检查

- 术语A → 注册表命中 ✅
- 术语B → 注册表命中 ✅
- 术语C → ⚠️ 不在注册表中 → **本次新假设。建议 grilling 结束后评估是否追加到注册表。**
```

**规则**：
- **D1**: 注册表是基线声明的唯一数据源——如果术语不在注册表中，它就是"新假设"。AI 不在 2.0 阶段做临时的定义搜索
- **D2**: "旧模型"列直接从注册表 `old_model` 字段读取，AI 不自己回忆现实含义
- **D3**: 未在注册表中的术语 → 声明"本次新假设" → grilling 结束后评估是否入库（入库触发见 `term_registry.json` 的 `_maintenance` 字段；修订流程见 [项目规约 §五](../../../design/conventions/README.md)）
- **D4**: 注册表中 `old_model` 标注 `—（与项目定义一致，无偏离）` 的术语可省略旧模型列内容（填 `—`），但**术语本身不能跳过**——仍需确认"本问题中正确使用了该术语"
- **D5**: 每轮仍输出基线表。术语集与前轮完全相同时可去重引用（`术语集复用第N题基线`），但必须满足时效前提：同一次 grilling 会话 + 中间轮次未修改该术语集中任一术语的定义 + 中间轮次未新增冲突新假设。任一不满足 → 输出完整基线表
- **D6**: §2.0 在 §2.1 之前执行——先建立约束集，再在约束集内做事实锚定
- **D7**: 入库触发——新核心术语 | 定义被修改 | 写入步（Step 3）清扫发现未注册高频术语。AI 在写入（Step 3）前列出候选清单，用户确认后写入注册表

### 2.1 基本规则
Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

### 2.2 事实锚定（v2 新增）

每轮回答如包含事实性主张，必须标注来源。格式：

```markdown
### 第 N 题 — [问题]

[问题陈述]

**我的建议**：[建议内容]

**事实依据**：
- `design/rules/核心机制.md` §5.1 — SAN ≥ 60 稳定，< 30 恐慌，= 0 随机行为
- `memory/xxx.md` — [事实描述]
- 以下为新建议，非已有事实：[列出新提出的参数/规则]
```

- 段引用（`§5.1`）优先于行号（`:314`）——行号随编辑漂移
- 新参数/公式 → 显式声明"此为本次新增"

### 2.3 决策深度自检（v2 新增）

**何时不能停**（以下任一触发，必须继续追问）：
- 涉及新的数值参数 → 追问来源/依据/可调范围
- 涉及新的机制交互 → 追问与已有机制的冲突处理
- 涉及新的实体类型 → 追问与已有实体的关系
- 涉及跨维度影响 → 逐维度检查影响
- **【v3 新增】基线表中出现不在注册表中的术语，且该术语在现实世界中有常用含义 → 追问用户：是否将此术语加入注册表？其旧模型和偏离理由是什么？**

**何时可以停**（以下全部满足时，话题可关闭）：
- 所有数值参数有来源依据（文献或已有设计文档）
- 所有机制交互已检查与相关系统的冲突（至少 grep 确认）
- 跨维度影响已逐维确认（六维各检查一遍）
- 影响范围已明确（涉及哪些文件，阻塞哪些下游话题）

---

## Step 3 — 写入（达成共识后）

1. **写入设计文档**：将决策写入受影响的具体 md 文件
2. **更新决策树**：追加到 `design/decisions/`。追加前 `grep` 与本次相关的「延迟」项 → 新记录标注来源，旧记录加注「→ 见」
3. **更新六维状态**：修改 `design/framework/six-dimensions.md` 对应维度的状态（✅/⚠️/❌）和 grilling 队列
4. **检查项目总览**：确认 `design/README.md` 的设计共识和待解决问题是否需要同步更新
5. **写入验证表**（v2 新增）：逐条对照 grilling 决策 → 写入内容，输出验证表：

```markdown
### 写入验证表

| 决策编号 | 决策摘要 | 写入文件 | 写入位置 | 验证状态 |
|----------|----------|----------|----------|----------|
| D1 | [摘要] | `xxx.md` | §N | ✅ 已验证 |
| D2 | [摘要] | `xxx.md` | §N | ⚠️ 需要人类复查 |
```

6. **一致性清扫**（v2 强化）：
   - grep 关键词：本次修改的所有术语 + 参数名 + 文件名 + 废弃/替换的概念名 + **废弃文件路径片段**
   - 命中 ≤ 10 个 → 全部 Read 确认
   - 命中 > 10 个 → 按优先级（设计文档 > 索引文件 > 数据 JSON > 工具脚本）分批 Read
   - **必须额外检查**：(a) 移动进垃圾桶的文件是否还有活跃文档引用它（路径断裂），(b) 废弃的数字/术语是否仍在活跃规格文档中以非废弃标注的方式出现（语义断裂——对照 `term_registry.json` 的 numerical_locations 复查）
6b. **术语含义变更时的兼容性检查（v3 新增）**：如果本次 grilling 修改了术语定义：
   - 从 `term_registry.json` 读取该术语的 `numerical_locations`
   - 逐位置检查：文档是否仍存在？段落是否仍存在？
   - 检查注册表 `updated` 日期是否晚于源文件的 git 最后修改日期（注册表更旧 → WARN）
   - 输出兼容性表：位置 / 原数值 / 新定义下状态（兼容/需修订/不确定）/ 操作
   - "不确定"标记 ⚠️ 需人类复查——AI 不单独判定语义兼容性
7. **告知用户**：列出本次 grilling 修改了哪些文件，建议 `git add` + `git commit`
