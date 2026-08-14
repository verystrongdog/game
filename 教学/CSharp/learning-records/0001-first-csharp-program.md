# 第一个 C# 程序跑通（角色卡任务）

学员首次独立完成 C# 控制台程序的创建、改写与运行全流程：`dotnet new console` → 替换 Program.cs（变量声明 + 字符串插值 + Console.WriteLine）→ `dotnet run` 输出角色卡，与任务预期逐字一致。这确立了阶段 1 的基线：建项目 / 改代码 / 运行不再需要引导。

## Status

active

## Evidence

- 2026-08-13：`dotnet run` 实际输出与任务预期完全一致（========== / 角色：玩家 / HP：78.5 / SAN：100 / ==========）。
- 环境：dotnet SDK 10.0.301（Windows PowerShell）。

## Implications

- 后续课程可直接让学员改造现有项目，不再教「如何新建 / 运行」。
- 第 2 课（控制流 + 方法）让学员在 HelloMask 里扩展：方法 + for 循环——「方法」意识是理解 MonoBehaviour 回调（Unity 阶段）的前置。
- 待回收的悬置问题：第 1 课第 6 节的 ToneState 回顾题（4 个脑干 tone）——学员答出后补记 record 0002。
