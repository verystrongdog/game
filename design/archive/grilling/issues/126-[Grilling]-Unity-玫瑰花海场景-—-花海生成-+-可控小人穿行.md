# #126 [Grilling] Unity 玫瑰花海场景 — 花海生成 + 可控小人穿行

> 状态：关闭 · 创建 2026-09-12 · 关闭 2026-09-12
> 标签：维度:呈现, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/126

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

用户诉求（原话）：「我希望通过 unity 生成一片玫瑰花海，我能够控制一个小人在其中穿行」

即：在既有 `unity/` 呈现沙盘工程内，新增一个**玫瑰花海场景**——程序化/资产化生成大规模玫瑰植被，并让可控小人在其中自由穿行。

## 六维定位

| 维度 | 判定 | 依据 |
|------|------|------|
| **呈现**（主） | 玩家怎么感知和操作——花海视觉形态 + 小人移动/相机 | 换一种呈现方式，机制不变 → 呈现 |
| **管线**（主） | 怎么造出来——植被生成方式（Editor 烘焙 vs 运行时实例化）、资产来源 | 影响开发效率 → 管线 |
| **空间**（待定） | 花海是否作为「患者世界」的一处持久场景容器 | 待用户确认是否入正典 |

## 当前状态（Step 0 检索结论）

- 全项目 `grep 玫瑰|花海|植被` → 仅命中 `.scratch/grilling-89-npc-material` 内的书名《春姨和玫瑰花》，**与场景设计无关**。花海在现有设计文档中**不存在**。
- `docs/决策树.md` 无同名话题；`gh issue list --label grilling` 无重复 issue（唯一 open = #71 物理医院层可走区域）。
- `docs/维度/呈现.md` 待设计项：状态面板细部 / 对话界面 / 反馈动画 / 声音设计 / 输入映射 / Unity 集成。
- `docs/维度/空间.md` 三层空间模型：物理医院 / 扭曲空间 / 患者世界 —— **花海归属未定**。
- 既有 Unity 载体：`unity/Assets/Scripts/WalkerController.cs`（几何体白盒人体 + CharacterController 走/跑/跳）、`AnimatorWalker.cs`（KI 人形 + Animator）、`ActionLabDriver.cs`（Mixamo X Bot + 12 词表动作）。

## 阻塞

- 花海是否入正典（呈现沙盘实验 vs 游戏内场景）→ 决定 Six-dim 归属与是否需要写入 `空间/` 设计文档。
- 若入正典，依赖：空间维度「可走区域」+ 月光分布（空间状态变化）。

---

## 评论（1 条）

### verystrongdog · 2026-09-12

## ✅ Grilling #126 闭合 — Unity 玫瑰花海场景（真实草原 DEM + 商业化密度株丛 + 小人穿行）

维度: 呈现 + 管线 | 形态: 独立技术验证 lab（**不入正典**）| 决策数: 12

---

### 一、决策表

| # | 决策 | 内容 | 依据 |
|---|------|------|------|
| D1 | 地块数据源 | USGS 3DEP **1 m lidar** DEM（Konza Prairie 高草草原；`KS_Statewide_2018_A18` / `S_Central_NE_NW_Kansas_Lidar`），公有领域 | 实检：SRTM/Copernicus 30 m → 100 m 内仅 3×3 样本；NED 1/3 arc-sec ≈10 m → 仅 10×10。1 m 是唯一够用的公开层级 |
| D2 | 地块选取判据 | 2 km 瓦片扫全部 101×101 px 窗口，`argmin relief`，约束 `relief ≤ 3.5 m ∧ std ≤ 0.7 m` | 把「轻微起伏」换成可机械核验约束（1444 候选窗 / 中位高差 16.00 m） |
| D3 | 地块实测 | 100×100 m，101×101 @1.0 m；relief **3.1075 m**，std 0.5665 m，最大 1 m 高差 **0.1145 m（6.53°）**；中心 39.095390°N / 96.578843°W | 实测 |
| D4 | 地面实现 | 程序化 Mesh（101×101 顶点）+ MeshCollider，**不启用 Unity Terrain 模块** | `unity/Packages/manifest.json` 未列 `com.unity.modules.terrain`；高度图 1:1 无损 |
| D5 | 种植密度 | **300 株/亩**（文献区间 180–330） | 平阴县人民政府《玫瑰的栽培种植》+ 农博数据中心《平阴玫瑰栽培技术》两源互印；`1/(行距×株距)` 算术校验 → 185–333 株/亩 自洽 |
| D6 | 布置 | 六角错行 **s = 1.602 m**（行距 s√3/2，奇行偏移 s/2）→ **N = 4563**，实测 **304.2 株/亩** | 三角格每株 6 最近邻距离恒 = s |
| D7 | 覆盖率判据 | 三角格覆盖半径 `s/√3` → 全覆盖充要条件 **`D ≥ 2s/√3 = 1.8498 m`**；取 D = 1.85 m → 覆盖率 **1.0**，冠层投影比 1.209 | 把「整片区域完全覆盖」换成显式几何判据 |
| D8 | 株丛资产 | 程序化低模 5 茎 + 8 叶 + 5 花 × 6 瓣 = **106 tri**，零外部资产 | 同 `WalkerController.BuildBody` 口径 |
| D9 | 渲染 | `Graphics.DrawMeshInstanced`（每批 1023 → ≈5 draw call）+ 自定义实例化着色器（顶点色分茎/叶/花）；**株丛无碰撞体**（「穿行」语义）；阴影投射关闭 | 4563 × 106 tri ≈ 4.6×10⁵ tri |
| D10 | 小人载体 | **`WalkerController`**（几何体白盒 + 程序化步态，零资产） | 事实排除 `AnimatorWalker` 与 `ActionLabDriver`：其 locomotion clip 均指向不在仓库的 `Assets/Kevin Iglesias/...` → 走/跑态为空 |
| D11 | 场景生成 | 新 Editor builder + 菜单 `YANTF → 玫瑰实验 → 创建玫瑰花海场景` → `Assets/Scenes/RoseFieldLab.unity` | 沿 `WalkerLabBuilder` 先例 |
| D12 | 相机 | 第三人称平滑跟随，`cameraOffset = (0, 3.0, −6.5)`（略高于 1.25 m 冠层） | 沿用 `WalkerController.followCamera` |

### 二、受影响文件

**新建**
- `unity/地块数据-Konza草原.md` — 数据源/选取判据/实测/raw 口径/复现命令
- `unity/玫瑰株丛密度.md` — 密度文献/布置/覆盖率判据推导
- `unity/Assets/Resources/YANTF/konza_plot_101x101_r16.bytes` — 高度图（20 402 B，LE uint16，行 0 = 北）
- `unity/Assets/Scripts/HeightField.cs`、`RoseMeshFactory.cs`、`RoseFieldLab.cs`
- `unity/Assets/Shaders/RoseInstanced.shader`
- `unity/Assets/Editor/RoseFieldLabBuilder.cs`
- `unity/Assets/Tests/PlayMode/RoseFieldSmokeTests.cs`（4 个 PlayMode 冒烟）
- `.scratch/grilling-126-rosefield/决策记录.md` + `ref/`（DEM GeoTIFF、高度图 meta、3 份密度文献 HTML 存档）

**修改**
- `unity/README.md` — §二·F 新增 + §三 结构树 + footer（顺带修正 footer 与 §二·D 的 `../../` 断裂相对路径）
- `docs/决策树.md` — #126 条目
- `docs/设计框架-六维状态.md` — 呈现 +1 → 7、管线 +1 → 28、完成度表、footer
- `项目总览.md` — 呈现索引新增一行

**仓库外**
- memory `玫瑰花海实验-grilling-126.md`
- GitHub: 本 issue 关闭

### 三、写入验证表

| 决策 | 写入位置 | 验证 |
|------|---------|------|
| D1/D2/D3 | `unity/地块数据-Konza草原.md` §二/§三/§四/§五 | ✅ |
| D5/D6/D7 | `unity/玫瑰株丛密度.md` §一/§二/§三/§四 | ✅ |
| D4/D6/D8–D12 | 5 个 .cs + 1 shader + 高度图 bytes | ⚠️ 需本机 Unity 编译验证 |
| D3/D5/D6/D9 | `unity/README.md` §二·F | ✅ |
| D1–D12 | `docs/决策树.md` / `docs/设计框架-六维状态.md` / `项目总览.md` / 决策记录 / memory | ✅ |

### 四、校验结果（质量门禁 · 手动等效）

| 检查 | 结果 |
|------|------|
| 交叉引用 grep（`玫瑰\|花海\|Konza\|RoseField\|3DEP`） | 命中仅本次新增文件 + 无关的 `grilling-89` 书名 → 无残留、无垃圾桶引用 |
| 新增/修改文档相对链接 | 0 broken（顺带修掉 README 两处 `../../` 断裂路径） |
| C# 语法校验（Roslyn，无 Unity 引用） | 282 条错误**全部 CS0246**（缺 Unity 类型）→ **语法错误 0、自有代码引用未解析 0** |
| 高度图资产完整性 | 20 402 B = 101×101×2 ✅；uint16 min 0 / max 65535 ✅ |
| 文档格式（CLAUDE.md §md 文件格式规范） | 单 H1 / 头部摘要 / 文末关联 / 中文数字小节 / 参数速查表 ✅ |
| 目视核查 | 待用户本机 Play |

### 五、推迟清单

- **用户本机 Unity 验证**：编译 → 菜单生成场景 → Play 目视（花海覆盖观感 / 穿行手感 / 帧率）
- `Graphics.DrawMeshInstanced` 12 参重载 + 自定义 shader 编译为首验点 → 退路 `Graphics.RenderMeshInstanced` 或 `Shader.Find("Standard")`（`MakeRoseMaterial` 已内建 fallback）
- 花瓣/叶片背面偏暗（Lambert + `Cull Off`）→ 后续换双面光照
- 遮挡剔除 / LOD / 视锥分块（当前 4563 株全量提交）
- 「花海入正典」（若需要）→ 回空间维度 grilling（三层空间归属 + 月光分布接口）

### 六、流程附注（治理）

Step 3 数学语言规范打断 3 次（「一片」量词缺失 / 「轻微」阈值模糊 / 「一块」「商业化种植密度」枚举未受控）→ **用户显式豁免**：「本次实验我提供权限，不用管 CLAUDE.md」。
处理：本会话不执行该规范；**CLAUDE.md 文件本体未改动**（其自指铁律规定删规则须单独说明并获同意；会话豁免 ≠ 删除规则）。决策表内每一数值仍全部标注来源。

---
*导出: 2026-09-12 | 来源: GitHub issue*
