# NOTES — 教学偏好与工作笔记

## 学员偏好（2026-08-13 建立）

- 中文授课，代码英文
- 方向：面向 Unity 的 C#（默认；首次问答未单选方向，按项目背景推定，待确认）
- 已有 Python 基础（写过模拟脚本）→ 用 Python→C# 对照
- 例子尽量贴合「面具」项目与 csharp-engine 真实代码
- 需求形式：可复用 agent 定义 + 从第一课开始正式上课（两者都要）

## 待确认

- [x] 是否已安装 .NET SDK？→ 已装（dotnet 10.0.301，Windows PowerShell）
- [x] 是否已安装 Unity？→ 已装（阶段 3 可提前安排）
- [ ] 学习节奏：每天一课 / 每周几课？
- [x] 方向确认：面向 Unity 的 C# → 已确认（2026-08-13）

## 工作笔记

- 2026-08-13：建立教学工作区。第一课定位「从 Python 到 C#：你的第一个程序」，教材用了 `src/YouAreNotTheFish.Core` 真实代码（ToneState / IRng / ToneUpdater / Program）。
- 2026-08-13：学员确认方向 = 面向 Unity 的 C#；Unity 已装；.NET SDK 确认已装（10.0.301，Windows）。等第一课任务反馈后写 learning-record 0001 并规划第 2 课。
- 2026-08-13（教学点）：`dotnet new console` 默认模板是「顶层语句」（无显式 Main），引擎代码是显式 `public static class Program` 写法——第 2 课需点破两者关系（编译器自动生成 Main）。
- 2026-08-13：第一课任务完成（输出逐字一致）→ 写 learning-record 0001；发布第 2 课「控制流与方法」。下一步：等学员交第 2 课任务输出 + 回收 ToneState 回顾题。
