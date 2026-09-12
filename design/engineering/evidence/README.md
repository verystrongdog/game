# 阶段证据

> 每阶段一个文件：`<阶段>-<日期>.md`。**只放精简结论**，不放大段日志或原始报告。

## 必填字段

| 字段 | 说明 |
|---|---|
| base SHA / head SHA | 起止 commit |
| 工具版本 | dotnet / python / Unity 等实际版本 |
| 命令与退出码 | 逐条列出实际执行的命令 |
| 问题差分 | `new_finding = after − mapped(before) − expected_delta`，要求为空 |
| 测试报告定位 | 指向 artifact 或可复现命令 |
| 回滚演练结论 | `git revert` 是否恢复上一状态 |
| 工作树干净 | 检查后无非预期变化 |

判据见 [WORKFLOW.md §五/§六](../../../WORKFLOW.md)。

## 已有证据

| 文件 | 阶段 | 结论 | 未闭合项 |
|---|---|---|---|
| [P4a-2026-09-12.md](P4a-2026-09-12.md) | P4a 环境锁定与最小 CI | 9/9 校验器 · 353 测试 · 干净 restore 可复现 · `new_finding` 空 | CI 未在 GitHub 真跑 · 回滚演练未实测 · Unity `NOT_AVAILABLE` |

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [工程文档](../README.md), [WORKFLOW.md](../../../WORKFLOW.md)*
