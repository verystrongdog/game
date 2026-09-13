# 工程文档与证据

> 关于**怎么造、怎么验证**的工程侧文档，与设计正典（`design/rules` 等）分开。`evidence/` 只放**精简阶段结论**。

## 内容

| 位置 | 作用 |
|---|---|
| [ARCHITECTURE.md](../../ARCHITECTURE.md)（根目录） | 设计与代码的边界声明、已知越界点 |
| [build-and-test.md](build-and-test.md) | **构建与测试权威**：环境锁定版本、命令、CI、判据、已知缺口 |
| [issue-process.md](issue-process.md) | **issue 创建约束与需求分解权威**：导入门、分解算法、字段、机械校验规则 |
| [gates.json](gates.json) | **门禁能力表**（机器可读）：gate id、命令、本机可用性、不可用时阻塞什么 |
| [危险点表.md](危险点表.md) | **按位置检索的排障索引**（非权威）：一个位置反复出什么事、判据是什么、怎么躲。收录门见其 §一；已可机械判的条目转 `code/tools/`（其 §十） |
| [backlog-decomposition-2026-09-12.md](backlog-decomposition-2026-09-12.md) | 用上述约束对当前 backlog 做的一次实际分解（示范 + 第一批 issue 的依据） |
| [evidence/](evidence/README.md) | 阶段证据摘要（base/head SHA · 工具版本 · 命令与退出码 · 问题差分 · 回滚结论） |
| `code/tools/` | 校验器与生成器（可执行的那部分） |

## 约定

- **完整机器报告不入库**（放 CI artifact 或被忽略的本地目录）；仓库只提交精简结论
- 证据必须绑定 **base/head SHA** 与工具版本，否则不可复现
- 证据判据见 [WORKFLOW.md §六](../../WORKFLOW.md)

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [ARCHITECTURE.md](../../ARCHITECTURE.md), [WORKFLOW.md](../../WORKFLOW.md)*
