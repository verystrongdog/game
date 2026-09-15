# 管线

> 本维度的**文档索引**。维度定义与分拣标准见 [六维框架 §六维定义与分拣标准](../six-dimensions.md#六维定义与分拣标准)。

## 索引

### 核心文档
- [动作描述口径.md](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) — ✅ 2026-09-14 — owner ↔ agent 的**动作描述对接口径**（三问骨架 / 回显卡 / 自由度表 / 三系参考系 / 容差 ε / 验收判据，D1–D10 经 owner 逐题接受）。分拣依据：它影响的是**开发效率**（怎么造出来、怎么验证）⇒ 管线。"弯腰抓椅背"的重做是它的回归样本（该文 §十）
  - 🔧 **2026-09-15 扩章**：新增 **§十三 手部基准卡片**（手与物体的接触引用件）——脊柱 = **三轴映射 × 分区接触对** · F1–F12 字段表 · 判据形态 5 种受控枚举 · **改族阈值** · 卡 1「掐棱」基准方向 = **侧握**（上罩登记为对照）。机器源将落 `data/hand_grip_cards.json`（**尚未产出，不建空表**）。owner 逐题接受
- [Blender动作制作管线.md](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) — Blender 线的**口径正典**：X Bot → 控制骨母版 → animation-only FBX → Unity Humanoid → 逐帧回导检查（母版契约 / V1–V9 / E0–E6 / 活体桥 / 参数速查）。🔧 2026-09-14 补登记——本行此前**缺失**（六维索引全文 grep 只命中"动作系统分解"），而它已是 #156 交付能力的正典
- [动画处理能力对照实验.md](../../presentation/%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) — 两条线共用的**可比性契约**（同一资产 / 同一动作段 / 同一取帧规则 / M1–M7 观测量 / C1–C9 成本面），`Design: ACCEPTED`（owner 2026-09-14）。分拣依据：它的产物是**工具链裁定**，服务开发效率 ⇒ 管线。🔧 2026-09-14 补登记——本行此前同样缺失
- [预烘焙管线脚本设计.md](../../pipeline/%E9%A2%84%E7%83%98%E7%84%99%E7%AE%A1%E7%BA%BF%E8%84%9A%E6%9C%AC%E8%AE%BE%E8%AE%A1.md) — ⚠️ 已废弃（2026-08-09）—— Softmax/β动态/模型A分层门控基于旧 pairwise 364 链路。NPC 行动选择改用 Affordance Competition 实时 salience。

### 数据
- [brain_regions.json](../../../data/brain_regions.json) — 50解剖实体 MNI/游戏坐标
- [tripartite_model.json](../../../data/connectivity/tripartite_model.json) — 三体神经模型（CSTC环路+皮层-皮层+脑干广播）
- [link_modulation_ceiling_v2.json](../../../data/connectivity/link_modulation_ceiling_v2.json) — 链路调制天花板
- [situation_primitives.json](../../../data/connectivity/situation_primitives.json) — 27情境原型（名称已规范化）
- [personality_tag_links.json](../../../data/connectivity/personality_tag_links.json) — ⚠️ 已废弃（2026-08-09）—— 6标签→链路映射基于旧 link_NNN IDs (auto_generated)。NPC 参数化改用 7 连续参数（4 tone baseline + 3 CSTC bias）。
- [data/README.md](../../../data/README.md)

### 工具
- [code/tools/](../../../code/tools) — Blender自动化/数据生成/前置关系提取
- [normalize_region_names.py](../../../code/tools/normalize_region_names.py) — 情境脑区名规范化验证
- [classify_link_roles.py](../../../code/tools/build_function_labels.py) — 链路行为角色自动分类
- [generate_tag_links.py](../../../code/tools/generate_tag_links.py) — ⚠️ 已废弃（2026-08-09）—— 生成逻辑基于旧 link_NNN IDs

### 模拟
- ⚠️ sim_battle.py / sim_battle_v4.py 已废弃进垃圾桶（2026-08-03 #20，模拟已废弃三代态度引擎）
- ⚠️ sim_cog_evo.py / sim_evo_ctrnn.py 已废弃进垃圾桶（2026-08-03 #20）

### 基础设施
- [design/conventions/agents/](../../conventions/agents) — Agent定义/issue-tracker/triage
- [项目规约](../../conventions/README.md) — AI行为规范
- [时空结构数学框架.md](../../rules/%E6%97%B6%E7%A9%BA%E7%BB%93%E6%9E%84%E6%95%B0%E5%AD%A6%E6%A1%86%E6%9E%B6.md) — 时空分布量数学框架/CGL+AGC身份/五框架构建
- [记忆内容层.md](../../rules/skill-tree/%E8%AE%B0%E5%BF%86%E5%86%85%E5%AE%B9%E5%B1%82.md) — 记忆内容层存储（运行时基础设施），2026-08-20 grilling #90

### 待建设
- 预烘焙管线主脚本 `bake_npc_behavior.py` — ⚠️ 已废弃（2026-08-09）—— NPC 行动选择改用 Affordance Competition 实时 salience，无需离线烘焙
- 数值平衡工具（参数校准/蒙特卡洛验证）
- Unity项目结构
- 测试策略

---

*创建: 2026-07-28 | 更新: 2026-07-31*
*关联: [设计框架-六维状态](../six-dimensions.md)*
