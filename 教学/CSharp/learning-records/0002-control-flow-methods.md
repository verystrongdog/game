# 控制流与方法：会改、会跑、会预测

学员完成第 2 课任务：补全 for 循环次数（3 次）、把 `san` 从 100 改为 30 后重跑，两次输出均与预期一致（100→精神稳定、30→濒临崩溃）。这证明学员能读懂并修改含方法定义（JudgeSan）、if 链、for 循环的程序，且能预测输出——阶段 1 的「读-改-预测」闭环能力已建立。

## Status

active

## Evidence

- 2026-08-13：san=100 输出 3 张卡均显示「精神稳定」；san=30 输出 3 张卡均显示「濒临崩溃」。
- 学员未回答 ToneState 4-tone 回顾题（第 1 课彩蛋）——该理解未获证据，record 不记录，留待回收。

## Implications

- 第 3 课引入集合（数组 / List / Dictionary，Python 对照），并把集合与 foreach / 方法结合（交错练习）。
- JudgeSan 这类「if 链返回字符串」的模式是引擎 NpcSalience / EventProcessor 判定的雏形，后续课程可指认对应真实代码。
- 待回收：ToneState 回顾题。
