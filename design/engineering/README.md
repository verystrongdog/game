# 工程文档与证据

> 关于**怎么造、怎么验证**的工程侧文档，与设计正典（`design/rules` 等）分开。`evidence/` 只放**精简阶段结论**。
>
> 🔧 **2026-09-17（owner 裁定）：全部门禁已撤销。** 本节原列的 `gates.json` 门禁能力表、`code/tools/` 下的 26 个校验器，以及 CI 的 `docs-integrity` / `issues-snapshot` / `unity` 三个 job 已一并删除。**现在没有任何机械校验在跑**——CI 只做构建与测试（`dotnet test code/src/YouAreNotTheFish.sln`），校验改人工。

## 内容

| 位置 | 作用 |
|---|---|
| [ARCHITECTURE.md](../../ARCHITECTURE.md)（根目录） | 设计与代码的边界声明、已知越界点 |
| [build-and-test.md](build-and-test.md) | **构建与测试权威**：环境锁定版本、命令、CI、判据、已知缺口（⚠️ 校验器与三个门禁 job 部分已成历史记录） |
| [issue-process.md](issue-process.md) | **issue 创建约束与需求分解权威**：导入门、分解算法、字段（⚠️ 原「机械校验规则」§5.2/§5.3 描述的 `validate_issues.py` 已删，字段完整性改人工） |
| ~~`gates.json`~~ | **2026-09-17 已删除**——原门禁能力表（gate id、命令、本机可用性、不可用时阻塞什么），随全部门禁一并移除 |
| [危险点表.md](危险点表.md) | **按位置检索的排障索引**（非权威）：一个位置反复出什么事、判据是什么、怎么躲。收录门见其 §一；~~已可机械判的条目转 `code/tools/`（其 §十）~~——⚠️ 2026-09-17 起 §十 的机械校验器已删，那些条目回到人工核对 |
| [backlog-decomposition-2026-09-12.md](backlog-decomposition-2026-09-12.md) | 用上述约束对当前 backlog 做的一次实际分解（示范 + 第一批 issue 的依据） |
| [evidence/](evidence/README.md) | 阶段证据摘要（base/head SHA · 工具版本 · 命令与退出码 · 问题差分 · 回滚结论） |
| `code/tools/` | 数据生成 / 迁移 / 测量工具与 Blender 桥（可执行的那部分）；校验器已于 2026-09-17 删除 |

## 约定

- **完整机器报告不入库**（放 CI artifact 或被忽略的本地目录）；仓库只提交精简结论
- 证据必须绑定 **base/head SHA** 与工具版本，否则不可复现
- 证据判据见 [WORKFLOW.md §六](../../WORKFLOW.md)

---
*创建: 2026-09-12 | 更新: 2026-09-17（门禁撤销：`gates.json` 行标为已删，`code/tools/` 改为生成 / 测量工具）*
*关联: [ARCHITECTURE.md](../../ARCHITECTURE.md), [WORKFLOW.md](../../WORKFLOW.md)*
