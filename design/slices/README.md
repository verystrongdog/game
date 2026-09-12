# 切片

> 每个**当前可玩目标**一个目录。切片是唯一的"可玩"单位——代码写完或文档写完都不算，**玩家能从入口走到出口且有试玩证据**才算。

## 目录

- [CP-01 — 住院楼 1F](CP-01-ward-1f/slice.md) — `CANDIDATE`（未经 owner 准入）

## 约定

| 文件 | 作用 |
|---|---|
| `slice.md` | 切片合同：玩家路径 / must-prove / 明确排除 / 消费能力的四轴状态 / 假实现与阻塞 |
| `playtest.md` | 试玩证据：**绑定 build 与 commit**，逐条记录 must-prove 的观察事实 |

- 同一时刻只有**一个** current playable（见 [WORKFLOW.md §一](../../WORKFLOW.md)）
- 准入状态记录在 [PLAYABLE.md](../../PLAYABLE.md)，不记录在本目录
- 四轴状态定义见 [WORKFLOW.md §二](../../WORKFLOW.md)

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [PLAYABLE.md](../../PLAYABLE.md), [WORKFLOW.md](../../WORKFLOW.md)*
