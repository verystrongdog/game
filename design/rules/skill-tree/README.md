# 技能树系统 — 目录索引

> 脑区链路技能树系统。正典：[脑功能层级模型](%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) — 50 解剖实体 L0-L5 六层功能层级。

---

## 目录结构

### 正典

| 文件 | 说明 |
|------|------|
| [脑功能层级模型](%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) | 六层功能层级、三体神经模型、髓鞘化、聚焦容量 |

### 操作层

| 文件 | 层级 | 说明 |
|------|------|------|
| [基础行动设计](operations/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md) | — | 物理攻击/精神攻击/防御，开局即存在 |

### 技能生成

| 文件 | 说明 |
|------|------|
| [技能生成机制](%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md) | 链路上下文技能（网络集合×主导角色），60候选池 + 涌现触发 |

> ⚠️ 37 个 AI 操作技能（L0-L6）已于 2026-08-03 废弃（D20），移入垃圾桶/废弃技能树/。技能系统已改为链路上下文范式（Grilling #20）。

### 激活系统

| 文件 | 说明 |
|------|------|
### NPC AI

| 文件 | 说明 |
|------|------|
| [NPC AI 行为模型](NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) | Affordance Competition 实时决策、7参数化性格（tone+CSTC）、正常人模板、NPC 类型、协调、SAN、工作流 |

### 调制参数

| 文件 | 说明 |
|------|------|
| [链路调制上限参考表-v2](modulation/%E9%93%BE%E8%B7%AF%E8%B0%83%E5%88%B6%E4%B8%8A%E9%99%90%E5%8F%82%E8%80%83%E8%A1%A8-v2.md) | 三因子模型（兴奋性×增益×髓鞘化） |

### 3D 可视化

| 文件 | 说明 |
|------|------|
| [3D可视化设计规范](../../presentation/visualization-3d/3D%E5%8F%AF%E8%A7%86%E5%8C%96%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83.md) | 节点颜色/形状/大小、相机操作 |
| [Blender建模指南](../../presentation/visualization-3d/Blender%E5%BB%BA%E6%A8%A1%E6%8C%87%E5%8D%97.md) | Blender 导出管线 |
| [脑图谱数据管线](../../presentation/visualization-3d/%E8%84%91%E5%9B%BE%E8%B0%B1%E6%95%B0%E6%8D%AE%E7%AE%A1%E7%BA%BF.md) | MNI→游戏坐标转换 |
| [大脑技能树3D.html](../../presentation/visualization-3d/%E5%A4%A7%E8%84%91%E6%8A%80%E8%83%BD%E6%A0%913D.html) | 3D 原型页面 |
| [技能树3D可视化.html](../../presentation/visualization-3d/%E6%8A%80%E8%83%BD%E6%A0%913D%E5%8F%AF%E8%A7%86%E5%8C%96.html) | 可视化原型 |

### 数据文件

| 文件 | 说明 |
|------|------|
| [brain_regions.json](../../../data/brain_regions.json) | 50 解剖实体 MNI/游戏坐标、层级 |
| [tripartite_model.json](../../../data/connectivity/tripartite_model.json) | 三体神经模型（CSTC环路+皮层-皮层+脑干广播） |
| [link_modulation_ceiling_v2.json](../../../data/connectivity/link_modulation_ceiling_v2.json) | 链路调制天花板 |
| [situation_primitives.json](../../../data/connectivity/situation_primitives.json) | 27 情境原型 |

### 参考文献

| 文件 | 说明 |
|------|------|
| [Hansen2024 数据](references/Hansen2024_%E8%84%91%E5%B9%B2%E7%9A%AE%E5%B1%82%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7_%E6%95%B0%E6%8D%AE.md) | 脑干-皮层 FC 层级 |
| [Magrou2024 数据](references/Magrou2024_%E8%B7%A8%E7%89%A9%E7%A7%8D%E6%AF%94%E8%BE%83_%E6%95%B0%E6%8D%AE.md) | 跨物种比较 |
| [Pessoa2024 数据](references/Pessoa2024_CRR%E7%A5%9E%E7%BB%8F%E6%9E%B6%E6%9E%84_%E6%95%B0%E6%8D%AE.md) | CRR 神经架构 |

### 已废弃

旧 PAD 态度空间坐标系、认知/情绪/行为三分支框架、卡牌系统。保留为设计考古参考。

| 文件 | 废弃原因 |
|------|---------|
| 技能树架构.md | 三分支框架 → 脑功能层级模型 |
| 大脑形态技能树-设计.md | PAD坐标系 → MNI解剖坐标 |
| 情绪/认知/行为技能设计.md | 三分支 → L0-L6 层级 |
| 终极技能设计.md | 旧态度组合 → 浮现式特殊技能 |
| 技能点经济.md | 技能点 → 髓鞘化成长 |
| 链路调制上限参考表.md | v1 SC/FC模型 → v2 三因子模型 |

---

*创建: 2026-07-27*
