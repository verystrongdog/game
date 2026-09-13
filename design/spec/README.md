# 规格 — 实现规格与输入素材

> 从 `.scratch/` 迁入的**承重内容**：被代码或设计正典直接消费、而非仅作过程记录的文件。本目录内容属于项目资产，不是过程存档。

> **为什么在这里**：这些文件的原始位置是 `.scratch/<slug>/`（过程工作区）。但它们被 `code/src/` 的 XML 注释、`data/term_registry.json` 的 `numerical_locations`、以及设计正典以稳定路径引用——把它们随过程存档一起移出仓库会打断这些引用。2026-09-12 仓库重构 Phase 2 迁入此处。

## 目录

1. [引擎](#一引擎)
2. [素材](#二素材)
3. [数据源](#三数据源)

---

## 一、引擎

C# 引擎各子系统的实现规格，源自 `.scratch/csharp-*/design/spec.md` 与 `.scratch/csharp-engine/design/plan.md`。

| 文件 | 内容 | 消费方 |
|------|------|--------|
| [csharp-engine-roadmap.md](engine/csharp-engine-roadmap.md) | 引擎实施路线图（plan §十一 分步） | `code/src/` 全部子系统 |
| [csharp-data-layer.md](engine/csharp-data-layer.md) | 数据层加载器规格 | `GameDataLoader` 等 |
| [csharp-engine-types.md](engine/csharp-engine-types.md) | CalibrationConfig / ParticipantState 等类型契约 | `Types/` |
| [csharp-damage.md](engine/csharp-damage.md) | 伤害结算 | `DamageCalculator` |
| [csharp-speed.md](engine/csharp-speed.md) | 速度排序 | `SpeedScoreCalculator` / `TurnOrderBuilder` |
| [csharp-cstc.md](engine/csharp-cstc.md) | CSTC 门控 | `CstcGating` |
| [csharp-tone.md](engine/csharp-tone.md) | tone 动力学与 b_j 注入 | `ToneUpdater` / `CorticalBias` |
| [csharp-wmatrix.md](engine/csharp-wmatrix.md) | W 矩阵构建 | `WMatrixBuilder` |
| [csharp-wc-dynamics.md](engine/csharp-wc-dynamics.md) | Wilson-Cowan 单步动力学 | `WcDynamics` |
| [csharp-events.md](engine/csharp-events.md) | 事件处理与 s(t) 打包 | `EventProcessor` |
| [csharp-flow.md](engine/csharp-flow.md) | 回合流程 | `Flow/` |
| [csharp-console.md](engine/csharp-console.md) | 控制台 harness | `Console/` |
| [csharp-smoke.md](engine/csharp-smoke.md) | 冒烟测试契约 | 测试工程 |

**引用格式约定**：代码注释以 `（csharp-<name>.md）§六 AC-1~AC-12` 形式引用本目录，不再带路径前缀。

## 二、素材

NPC / 病种起草的输入材料与实例化产物。`design/rules/skill-tree/素材起草规范.md` 要求起草前先读这些文件。

| 文件 | 内容 |
|------|------|
| [患者生态索引.md](material/%E6%82%A3%E8%80%85%E7%94%9F%E6%80%81%E7%B4%A2%E5%BC%95.md) | 查目标病种/地域/时代/机制是否与存量冲突（起草第 1 步） |
| [多样性记账表.md](material/%E5%A4%9A%E6%A0%B7%E6%80%A7%E8%AE%B0%E8%B4%A6%E8%A1%A8.md) | 六轴缺口 + 地域/时代/性别池（起草第 2 步） |
| [批次配额表-P1补充.md](material/%E6%89%B9%E6%AC%A1%E9%85%8D%E9%A2%9D%E8%A1%A8-P1%E8%A1%A5%E5%85%85.md) | 目标病种 × 六轴缺口 × 创伤通道的配额位定义（起草第 3 步） |
| [叙事多样化维度定义.md](material/%E5%8F%99%E4%BA%8B%E5%A4%9A%E6%A0%B7%E5%8C%96%E7%BB%B4%E5%BA%A6%E5%AE%9A%E4%B9%89.md) | 六轴多样性的指标定义（指标锁、数值不锁） |
| [C阶段诊断-PTSD-SSD资格门.md](material/C%E9%98%B6%E6%AE%B5%E8%AF%8A%E6%96%AD-PTSD-SSD%E8%B5%84%E6%A0%BC%E9%97%A8.md) | PTSD/SSD 资格门诊断依据 |
| [社会演化矩阵.md](material/%E7%A4%BE%E4%BC%9A%E6%BC%94%E5%8C%96%E7%9F%A9%E9%98%B5.md) | 社会演化矩阵（NPC 背景推导依据） |
| `病种试点/` | 26 个病种 pilot（+`grilling-88.md` 总览）——`design/entities/diseases/*.md` 的源材料 |
| `ref/` | 一手叙事与书目检索索引（素材库落点） |
| `drafts/` | NPC 起草实例（`*.gen.json` + 叙事视图） |

## 三、数据源

特征构建的**复算依据**（原始数据 + API 响应存档），证明数据可复现。

| 文件 | 内容 |
|------|------|
| `plot_f32.tif` | Konza 草原 F32 GeoTIFF 原始高程（玫瑰实验地形复算依据） |
| `konza_plot_101x101_r16.raw` | 高度图原始副本（16 bit，101×101） |
| `3dep_info.json` 等 | USGS 3DEP ImageServer / TNM API 响应存档（证明 1 m 源可用） |

消费方：[design/presentation/地块数据-Konza草原.md](../presentation/%E5%9C%B0%E5%9D%97%E6%95%B0%E6%8D%AE-Konza%E8%8D%89%E5%8E%9F.md)、[design/presentation/玫瑰株丛密度.md](../presentation/%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md)——⚠️ 2026-09-13 两篇均已标记**已废弃**（#126 花海 lab 按 owner 裁定移除）。Unity 侧入库副本 `code/unity/Assets/Resources/YANTF/konza_plot_101x101_r16.bytes` 已随之删除；本节原始数据仅作为 USGS 公开数据源的**复算依据**保留。

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [设计归档](../archive/README.md), [原工作区说明](../../README.md)*
