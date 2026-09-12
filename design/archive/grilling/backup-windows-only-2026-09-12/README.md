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

**🔧 已归位（2026-09-12，owner 直接指令）**：四个文件（两个 `.cs` + 两个 `.meta`）已 `git mv` 至 `code/unity/Assets/Scripts/`，`.meta` 的 GUID 原样保留（`CameraOrbit.cs` = `7f53b3f6ab58810478fb72f683000283`；`SitPoint.cs` = `cde9f27400a41884eaedaf1a715cac90`）——保留 GUID 是刻意的：这两个 `.meta` 由 Windows 侧 Unity 生成，字节一致，换 GUID 会让 Inspector 里对它们的引用失效。

- 版本关系已核：`feat/unity-presentation-slice` 是 `main` 的**祖先**（旧路径线），其内容已在 main 历史里；这两个文件是**唯一**未被任何分支收容的残留。故并入 main 不引入版本冲突。
- 文件权限归一到 `100644`（与既有 `.cs` 一致；原件带 Windows 的 777）。
- `SitPoint.cs` 的归位落在 issue [#137](https://github.com/verystrongdog/game/issues/137) 声明的「预期差分」内；`CameraOrbit.cs` 不属任何 issue，是 owner 直接指令的运维动作。
- **本目录此后仅存本 README**（历史记录），不再持有文件副本。

---

*创建: 2026-09-12 | 更新: 2026-09-12（归位完成）*
*关联: [决策记录 #126](../grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)*
