# Blender 建模指南 — 玻璃大脑技能树

> 从脑图谱数据到 Blender 可渲染的玻璃大脑模型的建模工作流。目标：生成的 FBX/GLTF 可直接导入 Unity 作为技能树 UI。

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
- **Blender** ≥ 4.0
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

下载后解压到 `技能树系统/blender_assets/` 目录。

### 1.3 项目坐标数据

运行数据管线确保坐标文件最新:
```bash
python code/tools/brain_atlas_to_blender.py
python code/tools/map_skills_to_regions.py
```

---

## 二、脑 mesh 导入

### 2.1 Blender 工作文件结构

```
brain_skill_tree.blend
├── Collections/
│   ├── BrainMesh/          ← 所有脑区 OBJ
│   │   ├── Cortex/         ← DK 皮层区 (60+ 个独立 mesh)
│   │   └── Subcortical/    ← 皮层下结构 (amygdala, hippocampus, thalamus, etc.)
│   ├── SkillNodes/         ← 74 技能节点 (Empty + 几何体)
│   │   ├── Cognition/      ← 二十五面体节点
│   │   ├── Emotion/        ← 球体节点
│   │   ├── Behavior/       ← 棱柱节点
│   │   └── Ultimate/       ← 大十二面体节点
│   ├── Tracts/             ← Bezier 曲线连线
│   └── Lighting/           ← 灯光设置
```

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

### 4.1 自动化放置脚本

运行 `code/tools/place_skill_nodes_blender.py`:

```bash
blender --background --python code/tools/place_skill_nodes_blender.py
```

或在 Blender Scripting 面板中加载运行。

该脚本:
1. 读取 `data/brain_regions.json` 获取脑区游戏空间坐标
2. 读取 `data/skill_coords.json` 获取 74 技能→脑区映射
3. 为每个技能创建对应几何体 (二十面体/球体/棱柱/十二面体)
4. 创建基础材质 (解锁前灰色半透明)
5. 放入对应 Collection

### 4.2 手动调整

自动放置后，可能需要微调:
- 重叠节点: 同名脑区上有多个技能节点时，小幅分散 (offset ±0.02)
- 脑表面外节点: 部分皮层节点可能在 mesh 表面外 → 沿法线方向向内推

### 4.3 节点几何体参数

| 分支 | 节点形状 | 基本半径 | 面数 |
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

*创建: 2026-07-11*
*关联: [脑图谱数据管线](%E8%84%91%E5%9B%BE%E8%B0%B1%E6%95%B0%E6%8D%AE%E7%AE%A1%E7%BA%BF.md), [大脑形态技能树-设计](../../rules/skill-tree/deprecated/%E5%A4%A7%E8%84%91%E5%BD%A2%E6%80%81%E6%8A%80%E8%83%BD%E6%A0%91-%E8%AE%BE%E8%AE%A1.md), [3D可视化设计规范](3D%E5%8F%AF%E8%A7%86%E5%8C%96%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83.md)*
