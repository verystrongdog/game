# Blender 建模指南 — 玻璃大脑技能树

> 从脑图谱数据到 Blender 可渲染的玻璃大脑模型的建模工作流。目标：生成的 FBX/GLTF 可直接导入 Unity 作为技能树 UI。
>
> ⚠️ **2026-09-13 范围重新划定**：
> - ✅ **仍然有效**：§一 mesh 下载与来源、§二 集合结构、§三 材质做法、§五 渲染 —— 建模操作层面
> - 🔶 **已迁走**：**接 Unity 的资产形态、渲染方案与验收判据见 [Unity接入设计](Unity%E6%8E%A5%E5%85%A5%E8%AE%BE%E8%AE%A1.md)**；**资产身份、正典源与重建命令见 [脑模型资产登记](%E8%84%91%E6%A8%A1%E5%9E%8B%E8%B5%84%E4%BA%A7%E7%99%BB%E8%AE%B0.md)**
> - ⚠️ **已废弃**：本文中"按分支（认知/情绪/行为/终极）定形状与配色"的部分——分类现为**主导网络 × 主导角色**，节点形状改按**层级 L0–L5**

---

## 目录

1. [一、前置准备](#一前置准备)
2. [二、脑 mesh 导入](#二脑-mesh-导入)
3. [三、玻璃大脑材质](#三玻璃大脑材质)
4. [四、技能节点放置](#四技能节点放置)
5. [五、白质纤维束连线](#五白质纤维束连线)
6. [六、导出到 Unity](#六导出到-unity)
7. [七、参考资源](#七参考资源)

---

## 一、前置准备

### 1.1 软件
- **Blender** ≥ 4.2 / 5.x（仓库构建脚本已回植 4.2/5.x 兼容：obj 导入算子、Emission 输入名、透明阴影字段、EEVEE Next——见[脑模型资产登记](%E8%84%91%E6%A8%A1%E5%9E%8B%E8%B5%84%E4%BA%A7%E7%99%BB%E8%AE%B0.md) §8.1）
- Python 3.10+ (系统已安装)

### 1.2 数据文件下载

从 [brainder.org/research/brain-for-blender](https://brainder.org/research/brain-for-blender/) 下载：

```
# 皮层 mesh (DK atlas, pial surface)
https://s3.us-east-2.amazonaws.com/brainder/software/brain4blender/pial_DK_obj.tar.bz2

# 皮层下结构
https://s3.us-east-2.amazonaws.com/brainder/software/brain4blender/subcortical_obj.tar.bz2

# (可选) 完整半球
https://s3.us-east-2.amazonaws.com/brainder/software/brain4blender/pial_Full_obj.tar.bz2
```

下载后解压到 `design/presentation/visualization-3d/blender_assets/all_obj/` 目录（13 个子目录 · 890 个 .obj · 289 MB；provenance 登记见 [all_obj_manifest.json](all_obj_manifest.json)）。

### 1.3 项目坐标数据

⚠️ **2026-09-13**：这两个命令**不该照跑**——`brain_atlas_to_blender.py` 是 57 脑区那一代的历史生成器，
`map_skills_to_regions.py` 产出的是契约里登记为 `LEGACY` 的 `skill_coords.json`。坐标已定稿并受控：

```bash
# 脑区坐标：已定稿（69 functional_id / 50 解剖实体）；重跑会覆盖受控契约，别跑
# 需要从 OBJ 质心精炼坐标时（少数场景）：
python code/tools/refine_coords_from_objs.py
```

---

## 二、脑 mesh 导入

### 2.1 Blender 工作文件结构

```
brain_skill_tree.blend            ← 实测结构（2026-09-13 只读探针，正典源那一份）
├── Collections/
│   ├── Collection/         ← Camera ×1 + Light ×3
│   ├── BrainMesh/          ← 102 个 OBJ mesh
│   │   ├── Cortex/         ← DK 皮层分区 70
│   │   └── Subcortical/    ← 皮层下结构 32
│   ├── SkillNodes/         ← 74 节点 ⚠️ 分类口径已废弃（四分支 → 14 网络 × 8 角色）
│   │   ├── Cognition/ 25 · Emotion/ 15 · Behavior/ 21 · Ultimate/ 13
│   ├── Tracts/             ← 152 条 Bezier 曲线
│   │   ├── Functional/ 89  ← 来自 prereqs
│   │   └── Tier/ 63        ← 层级相邻 + L5→终极
└── (v1 世代另有 FullHemisphere/ 玻璃外壳 2 个；v2 世代改用逐脑区半透明，不再需要外壳)
```

> 合计 332 对象 / 533,066 顶点 / 939,079 三角面。**对比**：正典是 71 个链路上下文 / 1049 条三体边
> ——这份 .blend 是视觉参考，不是拓扑来源（见[脑模型资产登记](%E8%84%91%E6%A8%A1%E5%9E%8B%E8%B5%84%E4%BA%A7%E7%99%BB%E8%AE%B0.md) §七）。

### 2.2 导入步骤

1. File → Import → Wavefront (.obj)
2. 导航到 `blender_assets/pial_DK/`
3. 选择所有需要的脑区 .obj 文件 (或 Batch Import 插件)
4. 同样导入 `blender_assets/subcortical/` 中的皮层下 OBJ

### 2.3 清理和合并

导入后:
- 每个脑区进来是一个独立对象。保留为独立对象以便单独着色
- 应用 scale/rotation 使所有对象统一在原点
- 皮层 mesh 通常在 FreeSurfer 空间 (RAS), 原点大致在 AC 附近

### 2.4 自动导入脚本 (bpy)

可以用 BrainPainter 的 `blendHelper.py` 作为参考，或运行我们的自动化脚本:

```python
# Blender Python 控制台中运行
import bpy
import os
import glob

obj_dir = "/path/to/blender_assets/pial_DK/"
for obj_path in glob.glob(os.path.join(obj_dir, "*.obj")):
    bpy.ops.import_scene.obj(filepath=obj_path)
    # 重命名、分组等
```

---

## 三、玻璃大脑材质

### 3.1 主体玻璃 (外层)

使用 EEVEE 或 Cycles:

**Principled BSDF 节点设置:**
```
Base Color: #8899BB
Roughness: 0.3
Transmission: 0.85
IOR: 1.33
Alpha: 0.15
Emission: #112233, Strength: 0.05
```

**关键设置:**
- Material → Settings → Blend Mode: Alpha Blend
- Material → Settings → Shadow Mode: None (透明物体不投影)
- Render Properties → Screen Space Reflections: ON (玻璃反射)
- Render Properties → Bloom: ON (发光辉光)

### 3.2 线框叠加

复制一份脑 mesh, 应用 Wireframe Modifier:
```
Wireframe Modifier:
  Thickness: 0.002
  Material: 暗色线框 (#334466, Emission: #224466, Alpha: 0.06)
```

### 3.3 脑区着色 (解锁后)

当脑区被激活时，该脑区的材质从冷灰变为暖色:
```
未激活: Base Color #445566, Emission #000000
激活:   Base Color 按分支着色, Emission 对应分支色 @ 0.3
```

分支色:
- 认知: #7B8FFF (蓝紫)
- 情绪: #F0A060 (暖橙)
- 行为: #4FC3F7 (青蓝)
- 终极: #E8D070 (金色)

脑区色在 Unity 中通过 C# 脚本动态切换，Blender 中只需设置初始冷色。

---

## 四、技能节点放置

### 4.1 自动化构建脚本（2026-09-13 更正）

本文原写"运行 `code/tools/place_skill_nodes_blender.py`"——**该文件从未生成**。实际落地的是两个构建脚本：

```bash
blender.exe --background --factory-startup \
  --python code/tools/build_brain_skill_tree_windows.py -- --out <独立输出目录>
```

| 脚本 | 世代 | 产出 |
|---|---|---|
| `build_brain_skill_tree_windows.py` | **当前（v2）** | 逐脑区半透明着色：`ctx_{脑叶}` + `sub_{群组}` + 逐节点/逐连线材质，无外壳 |
| `build_brain_skill_tree.py` | v1（2026-07-11） | 玻璃外壳那一代：`brain_glass` + 线框 + 共享 `node_*` 材质 |

⚠️ **输出不要指向 `blender_assets/` 资产目录**（那里是正典源与冻结快照）；脚本默认落 `build/`，
要写资产目录须显式 `--out`。该脚本做:
1. 读 `data/brain_regions.json` + `data/skill_coords.json`（后者＝契约里的 `LEGACY`）
2. 导入 `all_obj/`（DK 皮层 70 + 皮层下 32）
3. 按数据放置节点（⚠️ `region_matched` 查表 74/74 落空 → 走 `game_xyz_new` 回退，见登记 §八）
4. 生成连线（Functional ← prereqs；Tier ← 层级相邻 + L5→终极）
5. **产出核对**：把场景内容与 `skill_coords.json` 逐分支对照并打印，不一致标 ⚠

### 4.2 手动调整

自动放置后，可能需要微调:
- 重叠节点: 同名脑区上有多个技能节点时，小幅分散 (offset ±0.02)
- 脑表面外节点: 部分皮层节点可能在 mesh 表面外 → 沿法线方向向内推

### 4.3 节点几何体参数

> ⚠️ **2026-09-13**：下表按**分支**定形状，属废弃口径。当前形状/大小按**层级 L0–L5**
> （[脑功能层级模型](../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §16.1：小八面体 → 球体 → 立方体 → 二十面体 → 十二面体，radius 0.025→0.05）。

| 分支（⚠️ 废弃口径） | 节点形状 | 基本半径 | 面数 |
|------|---------|---------|------|
| 认知 | Ico Sphere | 0.04 | Subdivision 1 |
| 情绪 | UV Sphere | 0.045 | 20×20 |
| 行为 | Cube (Box) | 0.07×0.05×0.07 | — |
| 终极 | Ico Sphere | 0.06 | Subdivision 1 |

---

## 五、白质纤维束连线

### 5.1 前置关系线

节点之间的解锁前置关系用 Bezier 曲线表示，模仿 DTI tractography:

1. 在两点之间创建 Bezier 曲线
2. 控制点沿垂直方向偏移 (模拟纤维束的弧线形态)
3. 已解锁: TubeGeometry 效果 (Blender 中用 Curve → Object Data → Bevel)
4. 未解锁: 虚线效果 (在 Unity 中用 LineRenderer)

### 5.2 Blender 中创建连线

```
Add → Curve → Bezier
→ 编辑模式, 移动端点到两个技能节点位置
→ 选中中间控制点, G Z 向上偏移 0.12
→ Object Data → Bevel → Depth: 0.004
→ Material: 分支对应色 Emission
```

### 5.3 自动化连线脚本

可以用 Python bpy 批量创建。前置关系数据从 `大脑技能树3D.html` 中的 `prereqs` 数组提取:
```javascript
prereqs = [['cog_1','cog_0'], ['cog_2','cog_0'], ...]
```

---

## 六、导出到 Unity

### 6.1 导出格式

推荐 **GLTF (.glb)**：
- 原生支持 PBR 材质
- 节点层级保留
- Collection 名称保留
- 比 FBX 更好的跨引擎兼容性

**FBX (.fbx)** 备选：
- Unity 原生支持最好
- 但材质信息可能丢失

### 6.2 导出步骤

```
File → Export → glTF 2.0 (.glb)
  勾选: Selected Objects (仅导出需要的 Collection)
  格式: GLB (二进制)
  材质: Export (保留 Principled BSDF → Unity 自动转换)

File → Export → FBX (.fbx)
  路径: Assets/SkillTree/Models/
  勾选: Selected Objects
  缩放: 1.0
```

### 6.3 Unity 导入后

1. 将 .glb/.fbx 放入 `Assets/SkillTree/Models/`
2. Unity 自动生成材质 (URP/HDRP Lit)
3. 调整玻璃材质: Surface Type → Transparent, Alpha ≈ 0.15
4. 节点和连线设为独立 GameObject，挂 SkillNode.cs 脚本

Unity 端的详细设置见 [3D可视化设计规范](3D%E5%8F%AF%E8%A7%86%E5%8C%96%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83.md)。

---

## 七、参考资源

- **BrainPainter 源码**: [github.com/mrazvan22/brain-coloring](https://github.com/mrazvan22/brain-coloring) — Blender Python 脑渲染参考实现
- **brain-for-blender**: [brainder.org/research/brain-for-blender](https://brainder.org/research/brain-for-blender) — 脑区 OBJ mesh
- **BrainPainter 论文**: Marinescu et al. (2019), *BrainPainter: A software for the visualisation of brain structures, biomarkers and associated pathological processes*
- **NeuroVR**: [github.com/openbraininstitute/NeuroVR](https://github.com/openbraininstitute/NeuroVR) — Unity 脑可视化参考

---

*创建: 2026-07-11 | 更新: 2026-09-13（范围重新划定：分支口径标注废弃；改正"运行不存在的 place_skill_nodes_blender.py"；集合结构换成实测；路径随仓库重构更新）*
*关联: [脑模型资产登记](%E8%84%91%E6%A8%A1%E5%9E%8B%E8%B5%84%E4%BA%A7%E7%99%BB%E8%AE%B0.md), [Unity接入设计](Unity%E6%8E%A5%E5%85%A5%E8%AE%BE%E8%AE%A1.md), [脑图谱数据管线](%E8%84%91%E5%9B%BE%E8%B0%B1%E6%95%B0%E6%8D%AE%E7%AE%A1%E7%BA%BF.md), [3D可视化设计规范](3D%E5%8F%AF%E8%A7%86%E5%8C%96%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83.md), [脑功能层级模型](../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md)*
