---
description: 任务 md 四维质检：格式规范 / 术语正典 / 交叉引用 / 数学语言充分性。用法：/task-checker <文件路径> [--quick]
---

# /task-checker — 任务 md 四维质检

对 AI 生成的决策总结/任务规划 md（`.scratch/` 下）做四维质检。只报告问题，不做设计决策，不改写文件。

**参数**：`$ARGUMENTS` 为目标文件路径（如 `design/spec/material/患者生态索引.md`）；追加 `--quick` 跳过引用核验。

## 执行

按 [.claude/skills/task-checker/SKILL.md](../skills/task-checker/SKILL.md) 的四维流程执行：

1. **维度① 格式规范**：对照 [项目规约](../../design/conventions/README.md) §三 md 文件格式规范——文件头摘要/文末关联/目录（>200 行）/单 H1/中文编号小节/废弃标记/参数速查表
2. **维度② 术语与正典一致性**：运行 `python3 code/tools/list_deprecated_terms.py` 获取完整 deprecated 清单（**勿用记忆/硬编码**），扫描目标文件；并核对注册表定义误用、与决策树冲突
3. **维度③ 交叉引用完整性**：复用 `code/tools/validate_*.py` 核验活跃目标；手动核验任务 md 自身链接（`.scratch/` 不在脚本扫描范围）；检查垃圾桶隔离
4. **维度④ 数学语言充分性**：对照 `design/conventions/agents/math-language-writing.md`——模糊量词/无符号数值/阈值模糊/枚举未受控等，给出公式化改写建议

## 输出

写入 `.scratch/task-check-YYYY-MM-DD-HHMM-<文件名>.md`，终端打印摘要。判定语义：`❌` 阻断（术语违规/垃圾桶引用/无头无尾）/ `⚠️` 提示 / `✅` 通过。
