# Windows 侧独占文件备份（2026-09-12）

> `C:\Users\9527\game`（Unity 打开的那份仓库拷贝）上存在、但**不在任何 git 分支/远端**的两个文件。此目录是它们的第二份拷贝。

## 来源与风险

| 文件 | 大小 | Windows mtime | 内容 |
|------|------|---------------|------|
| `CameraOrbit.cs` | 4 663 B | 2026-09-07 21:51 | 环绕跟随相机（右键拖拽环绕 / 滚轮缩放），命名空间 `YANTF.WalkerLab` |
| `SitPoint.cs` | 3 570 B | 2026-09-07 21:56 | 椅子就座锚点（参数取自 Mixamo StandToSit 实测） |

发现过程：Grilling #126 排查「Unity 打开的是哪份工程」时，`git log --all` 在 WSL 侧仓库**查不到这两个文件**（含 `origin/feat/repository-refactor`、`origin/feat/unity-presentation-slice`、`origin/main` 全部远端分支）。它们只存在于那块 C 盘上。

已用 md5 与 Windows 侧逐字节比对一致；`.meta` 一并备下（Windows 侧 Unity 生成）。

## 处置

- 本目录仅为**止损备份**，内容未并入 `code/unity/Assets/Scripts/` —— 归位方式由用户决定。
- 归位时注意：`CameraOrbit.cs` / `SitPoint.cs` 属 `feat/unity-presentation-slice` 那条线的工作，与 `main` 上 #122–#126 的 Unity 沙盘不是同一条；直接并入 main 前建议先确认版本关系。

---
*创建: 2026-09-12*
*关联: [决策记录 #126](../grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)*
