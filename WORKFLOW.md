# 工作流程

> 本仓库**本地工作与 Issue 流程的唯一权威**。执行顺序、状态定义、阶段闭合与问题判定以本文为准。
>
> **issue 的创建约束与需求分解**（字段、依赖、门禁绑定、分解算法、创建通道）见 [design/engineering/issue-process.md](design/engineering/issue-process.md)。本文定义**类型与判据**，那份文档定义**怎么把需求变成 issue**；两者冲突时以本文为准。
>
> **来源**：2026-09-12 从 owner 的《仓库重构方案》§三/§四/§十三/§十四 迁入并适配本仓目录结构。原方案存于 [design/archive/](design/archive/)。

## 目录

1. [一、单线程约束](#一单线程约束)
2. [二、状态模型](#二状态模型)
3. [三、Issue 类型的最小用途](#三issue-类型的最小用途)
4. [四、阶段的两次闭合](#四阶段的两次闭合)
5. [五、阶段通用处置流程](#五阶段通用处置流程)
6. [六、问题判定判据](#六问题判定判据)
7. [七、新种类问题升级](#七新种类问题升级)

---

## 一、单线程约束

- 同一时刻只有**一个 current playable**（见 [PLAYABLE.md](PLAYABLE.md)）
- 同一时刻只推进**一个主要成果或变更集**
- 若使用 Issue，同一时刻只有一个主要叶子 Issue 处于 `state:in-progress`
- 一个**阻塞当前成果**的 Bug / Experiment / RFC 可以抢占；原工作必须先标记 `blocked`
- **非阻塞发现进入候选队列**，不在当前变更中顺手解决
- **上一阶段未达到退出门禁，下一阶段不得开始**

> Issue 是记录与准入载体，**不是本地工作的目的**。外部标签同步、Issue 编辑与自动化不属于本流程的隐式权限——如需 agent 直接创建或编辑 issue，须按 [issue-process.md §7.2](design/engineering/issue-process.md) 显式授权一次并记录授权范围。

## 二、状态模型

### 2.1 能力四轴

每项**被当前切片消费的能力**分别记录四轴状态——不得给一个笼统的"完成了"：

| 轴 | 合法状态 | 证据 |
|---|---|---|
| **Design** | `UNRESOLVED` / `CANDIDATE` / `ACCEPTED` / `SUPERSEDED` | 当前设计文档或短决策记录 |
| **Implementation** | `NONE` / `FAKE` / `PARTIAL` / `DONE_FOR_SLICE` | 源码与单元测试 |
| **Integration** | `ISOLATED` / `CONNECTED` / `E2E` | 集成测试、场景 trace 或构建 |
| **Health** | `UNKNOWN` / `PASS` / `REGRESSED` | 当前版本回归结果 |

`DONE_FOR_SLICE` **只表示满足当前切片范围，不表示永久完成**。

### 2.2 试玩状态（逐条 must-prove）

**不给整项能力打总分**，对每条 must-prove 分别记录：

`UNTESTED` / `OBSERVED` / `SUPPORTED` / `REFUTED` / `INCONCLUSIVE`

### 2.3 状态必须绑定

所有状态必须绑定 **Slice + build/commit + 证据**。无绑定的状态视为未记录。

## 三、Issue 类型的最小用途

| 情况 | 类型 |
|---|---|
| 当前可玩目标 | `Slice` |
| 已接受玩家行为的实现 | `Implementation` |
| 明确且**不决定新玩法**的交付 | `Task` |
| 可复现行为违背已接受预期 | `Bug` |
| 玩家体验或技术可行性**未知** | `Experiment` |
| 跨系统、**难回滚**的决定 | `RFC` |

**实质修改 Issue 的范围、行为、证据标准或依赖后，必须返回 triage 重新准入。**

**创建一条 issue 需要哪些字段、依赖怎么写、门禁怎么绑、需求怎么分解成有序的多条**——见 [design/engineering/issue-process.md](design/engineering/issue-process.md)。该文档还规定了两件事：讨论阶段**不建 issue**（讨论的产物是决策，落 `design/`），以及新建 issue 必须过 `code/tools/validate_issues.py` 的门禁。

## 四、阶段的两次闭合

1. **门禁闭合**——本阶段验收通过，可以进入下一阶段
2. **消费闭合**——下一阶段**成功使用**本阶段产物，且没有暴露结构性错误

> 门禁通过只说明*当前证据支持继续前进*。**下游无法消费时，应回到产生错误假设的阶段修订**，不能只在下游添加兼容补丁。

## 五、阶段通用处置流程

每个阶段执行以下最小循环：

1. 记录 base commit、工作树与前序门禁
2. **在开始前列出允许变化与预期差分**
3. 建立改前复现、trace、hash、依赖图或体验假设
4. **一个提交只做一种变化**
5. 每个提交跑快速相关检查；阶段退出跑全部适用回归
6. 比较改前/改后问题集合与非预期 diff
7. 在临时 worktree 或临时分支验证 `git revert` 能恢复上一状态
8. 保存精简证据摘要并签出阶段

### 5.1 问题差分

```
new_finding = after − mapped(before) − expected_delta
```

- `before` 必须能在 base commit **稳定复现**
- `expected_delta` 必须在**阶段开始前登记**
- 本阶段产生的新问题**不得事后倒填为"已知债务"**
- 阶段退出要求 `new_finding` **为空**
- **未运行、超时、工具异常和零测试不是通过**；它们只阻塞实际依赖该能力的阶段或子门禁

### 5.2 问题指纹

```
validator_id + rule_id + stable_subject_id + semantic_fingerprint
```

**路径、行号和自然语言消息只作展示**，不参与指纹——否则每次搬迁都会让所有问题"变成新问题"。发生搬迁时必须先建立旧/新 subject 映射。

### 5.3 证据存放

完整机器报告放 CI artifact 或**被忽略的本地 artifact 目录**；仓库只提交 [design/engineering/evidence/](design/engineering/evidence/) 下的**精简结论**。

证据摘要至少包含：base/head SHA · 工具版本 · 命令与退出码 · 问题差分 · 测试报告定位 · 回滚演练结论。

## 六、问题判定判据

| 类型 | 解决证据 |
|---|---|
| `Bug` | 修复前**稳定失败**；修复后通过；有回归测试与受影响范围检查 |
| `Experiment` | 得到支持/否定/证据不足的结论；**原型去向明确** |
| `RFC` | 真实选项、代价、回滚与 owner 决策完成；必要实施工作已建立 |
| `Task` | 交付物存在、接入目标位置、直接验证与阶段回归通过 |
| `Implementation` | **玩家可观察行为**符合已接受设计，且进入指定 build/场景 |
| `Slice` | **玩家能从入口到出口**；must-prove 有试玩证据；owner 决定接受/迭代/放弃 |

> **代码写完、文档写完、测试文件存在、CI 表面绿色、Agent 汇报完成，都不能单独作为关闭证据。**

### 6.1 阶段如何证明没有新增问题

绝对无缺陷无法证明。阶段退出必须提供：

1. 实际 diff 与**预先登记的允许范围**一致
2. `new_finding` 为空
3. 当前专项门禁与所有适用前序门禁通过
4. 检查后工作树**无非预期变化**
5. **干净检出**可以复现结果
6. 临时环境中的**回滚演练**恢复上一稳定状态
7. 下一阶段或下一项正常工作**成功消费**本阶段产物

玩家体验相关变化还必须增加**绑定 build / 场景 / Slice / must-prove 的试玩证据**。

## 七、新种类问题升级

遇到流程未覆盖的问题类型时：

1. **停止**当前阶段推进
2. 记录问题与为什么现有判据不适用
3. 提交为 `RFC`（跨系统或难回滚）或 `Experiment`（可行性未知）
4. 得到 owner 决策后再恢复——**不得自行扩大流程权限**

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [AGENTS.md](AGENTS.md), [可玩状态](PLAYABLE.md), [架构](ARCHITECTURE.md), [协作指南](CONTRIBUTING.md)*
