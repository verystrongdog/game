# 玫瑰花海地块数据 — Konza 高草草原（USGS 3DEP 1 m lidar）⚠️ 已废弃

> ⚠️ 已废弃（2026-09-13）：本文件描述的 #126 花海 lab 已按 owner 裁定从 `code/unity/` 整体移除（6 个源文件 + `Assets/Shaders/` + `Assets/Resources/YANTF/` 高度图 + 4 项 PlayMode 测试）。**本文件不再对应任何现存实现**——文中「位置」列引用的 `RoseFieldLab.*` 符号已不存在。保留原因：决策树 #126 与 `design/archive/grilling/grilling-126-rosefield/` 是**冻结历史**，以稳定路径引用本文件，删除会打断历史引用。USGS 数据获取管线本身可复用，记录见[六维状态 §管线](../framework/six-dimensions.md)。

> 玫瑰花海实验场景（Grilling #126）的地形数据来源、地块选取判据与复现命令。数据为美国公有领域（USGS），可入版本控制。

**维度: 呈现 + 管线** — Issue [#126](https://github.com/verystrongdog/game/issues/126)。

## 一、为什么用真实 DEM 而不是参数化描述

「草原地形，有轻微起伏」这类程度副词无法机械核验，也无法在 Unity 侧复现。改用**公开实测高程数据 + 显式选取判据**后，地块唯一确定、可被任何人在本机重跑同一命令复现。

## 二、数据源

| 项 | 值 |
|----|-----|
| 数据集 | USGS 3D Elevation Program（3DEP）Bare Earth DEM，**1 m** lidar 源 |
| 源产品 | `KS_Statewide_2018_A18` / `S_Central_NE_NW_Kansas_Lidar`（Original Project Resolution） |
| 站点 | Konza Prairie Biological Station，高草草原（tallgrass prairie），堪萨斯州，美国 |
| 服务 | [3DEPElevation ImageServer](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer) `exportImage`（EPSG:3857，F32） |
| 许可 | USGS 公有领域 |

**为何不用全球 DEM**：100×100 m 地块下，SRTM / Copernicus GLO-30（30 m）仅 3×3 样本，NED 1/3 arc-second（≈10 m）仅 10×10 样本——都不足以承载可行走地形。1 m lidar 是唯一密度够用的公开层级（覆盖仅美国）。

## 三、地块选取判据（把「轻微起伏」变成可核验约束）

在 Konza Prairie 中心（39.0900°N, 96.5800°W）取 2 km × 2 km 瓦片，扫描全部 101×101 px 窗口：

| 判据 | 取值 |
|------|------|
| 目标 | 高差最小窗口 `argmin relief` |
| 约束 | `relief ≤ 3.5 m ∧ std ≤ 0.7 m` |
| 候选窗口总数 | 1444 |
| 瓦片中位高差（对照） | 16.00 m |
| 整瓦片高差（对照） | 94.56 m |

**选定地块**：

| 指标 | 实测值 |
|------|--------|
| 范围 | 100 × 100 m = 10⁴ m² |
| 采样 | 101 × 101 @ 1.0 m |
| 高程 min / max / mean | 406.7568 / 409.8644 / 409.2104 m |
| **高差 relief** | **3.1075 m** |
| 高程 std | 0.5665 m |
| **最大 1 m 高差** | **0.1145 m/m（6.53°）** |
| 中心经纬度 | 39.095390°N, 96.578843°W |
| NE / SW 角 | 39.095839,-96.579421 / 39.094941,-96.578264 |

> 最大 1 m 高差 0.1145 m ≪ `tan(45°) = 1.0`（`CharacterController.slopeLimit`）→ 全程可走，无卡坡。

## 四、落盘产物与口径

| 路径 | 内容 |
|------|------|
| `code/unity/Assets/Resources/YANTF/konza_plot_101x101_r16.bytes` | 高度图（20 402 字节）——**入库** |
| `../规格/数据源/plot_f32.tif` | 原始 F32 GeoTIFF（复算依据，66 KB）——入库 |
| `../规格/数据源/konza_plot_101x101_r16.raw`、`konza_plot_101x101_r16.meta.txt` | 高度图副本 + 元数据全文——入库 |
| `../规格/数据源/3dep_info.json`、`tnm_datasets.json`、`tnm_ned.json` | ImageServer / TNM API 响应存档（证明 1 m 源可用）——入库 |
| `.scratch/grilling-126-rosefield/ref/*.html` | 种植密度文献原文——**不入库**（`.gitignore` §56 `.scratch/**/*.html`，本地留存） |

**raw 口径**：little-endian uint16，行主序，**行 0 = 北边缘**，值域 [0, 65535] 线性映射到 [0, 3.1075] m。
解码：`height_m = value / 65535 × 3.1075`。

**世界口径**（`HeightField` 采用）：x ∈ [0, 100] 向东，z ∈ [0, 100] 向北；raw 行 0 ↔ z = 100。

## 五、复现命令

```bash
# 1) 取地块高程（1 m 地面分辨率，101×101 采样），输出 F32 GeoTIFF
python3 - <<'PY'
import math, json, urllib.request, urllib.parse
R = 6378137.0
lat0, lon0 = 39.095390, -96.578843          # §三 选定地块中心
N, SIZE = 101, 100.0
merc = lambda lon, lat: (R*math.radians(lon), R*math.log(math.tan(math.pi/4+math.radians(lat)/2)))
cx, cy = merc(lon0, lat0)
half = SIZE/2.0/math.cos(math.radians(lat0))  # 地面 100 m → 墨卡托米
p = {"bbox": f"{cx-half},{cy-half},{cx+half},{cy+half}", "bboxSR": 3857, "imageSR": 3857,
     "size": f"{N},{N}", "format": "tiff", "pixelType": "F32",
     "interpolation": "RSP_BilinearInterpolation", "f": "json"}
u = ("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
     + urllib.parse.urlencode(p))
meta = json.load(urllib.request.urlopen(u, timeout=120))
open("plot_f32.tif", "wb").write(urllib.request.urlopen(meta["href"], timeout=120).read())
PY

# 2) F32 → 16 位 raw（行 0 = 北）
python3 - <<'PY'
import numpy as np
from PIL import Image
a = np.array(Image.open("plot_f32.tif"), dtype=np.float64)
relief = float(a.max() - a.min())            # 期望 3.1075
q = np.rint((a - a.min())/relief*65535.0).astype('<u2')
q.tofile("konza_plot_101x101_r16.bytes")     # 20 402 字节
print("relief", relief, "std", a.std())
PY
```

## 六、参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 地块边长 | `fieldSize` | 100 m | `RoseFieldLab.fieldSize` |
| 高度图采样数 | `heightmapSamples` | 101 | `RoseFieldLab.heightmapSamples` |
| 高度图高差（解码系数） | `heightmapReliefMeters` | 3.1075 m | `RoseFieldLab.heightmapReliefMeters` |
| 资源路径 | `heightmapResource` | `YANTF/konza_plot_101x101_r16` | `RoseFieldLab.heightmapResource` |

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [code/unity/README.md](../../code/unity/README.md), [玫瑰株丛密度](%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md), [决策记录 #126](../archive/grilling/grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)*
