# Review Trace: 脑区数据反转 — 最终状态确认

> 审查日期: 2026-08-07 11:54 | 审查范围: brain_regions.json 最终状态（19删除 + 路径修复 + L6归零 + 层级冲突解决）
> 方法: 符号执行 + 限界验证 | 前置检查: run_all_checks.py (5/6 passed, 1 failed, 0 blocker)

## 前置输入
- [x] run_all_checks.py — 5/6 PASS（同上一轮）
- [x] 上一轮 trace: `.scratch/review-trace-2026-08-07-1138-brain-regions-data-refactor.md`
- [x] 用户决策: L6 删除（"删掉L6可以"）

## 与上一轮 trace 的增量变化

| 旧缺口 | 本轮状态 | 说明 |
|--------|---------|------|
| G1 S4 断言 | ❌ → ❌ | 未修复 |
| G2 bfb_region | ❌ → ❌ | 未修复 |
| G3 50 vs 70 | ⚠️ → ⚠️ | 未修复 |
| G4 L6 归零 | ❌ → ✅ | **用户决策确认：L6 删除，不保留涌现层** |
| G5 "89"清扫 | ⚠️ → ⚠️ | 未修复 |
| G6 build_region_name_map | ⚠️ → ⚠️ | 未修复 |
| G7 功能表残留 | ⚠️ → ⚠️ | 未修复（等文档重写） |
| G8 dk_name层级冲突 | ⚠️ → ⚠️ 减半 | 2/3 解决（见 T1） |
| G9 通路功能迁移 | ⚠️ → ⚠️ | 未修复（等文档重写） |
| G10 小脑L0 | ⚠️ → ⚠️ | 未决策 |
| G11 ENIGMA中文key | ⚠️ → ⚠️ | 未修复 |
| G12 内嗅皮层L1/L4 | ⚠️ → ✅ | 已确认 L4（JSON同文档一致） |

## Trace Table（仅增量行）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T1 | brain_regions.json — 层级冲突解决（dk_canonical） | 2 组 dk_name 内 level 不一致（superiortemporal: {L4,L5}, lateraloccipital: {L3,L4}） | `Dict<dk_name, Set<level>>` | superiortemporal 统一 L4（颞上回 L5→L4）；lateraloccipital 统一 L4（枕顶联合 L3→L4） | 15 dk_names 层级一致（全部确认） | 链路层级相邻规则 — 现在同一 dk_name 内不再有层级分歧 | caudalanteriorcingulate 仍残留 {L2, L5}：前额叶极·SN（L5）与 ACC/ACC背侧（L2）共享 dk_name。解剖实体 caudalanteriorcingulate 是 L2 旁边缘区域，但 SN 突显网络的"最高裁决"功能曾赋予 L5。 | ⚠️ 1 组残留 |
| T2 | 脑功能层级模型.md — L6 层级删除 | L6 曾含 5 条目（3 网络变体 + DMN+OFC + 全脑整合）→ 全部 collapse 到父 dk_name 或已删除（全脑整合） | 0 实体残留 | L6 从层级架构中移除。§九 L6 章节整体改写为"⚠️ 已废弃"。§二 总览 ASCII 图删除 L6 行。§十八 摘要表 L6 行删除。L6 功能（自我叙事/网络协调）标注为 L5 dmPFC/vmPFC + L2 ACC（SN）的涌现属性 | `Dict<5,0>` | §9.3 L6 设计约束（终极链路层/8-12回合冷却/月光最强）→ 需迁移到 L5 的最顶级链路约束中 | L5 的"最顶级链路"现在替代了旧 L6 的"终极链路"定位。旧 L6 链路格言"重新定义这场战斗的意义"是否保留到 L5 → 文档重写时决定 | ✅ 决策确认 |
| T3 | L5 dk_name 变化 | 原 L5 7 dk_names + superiortemporal 移出(L5→L4) = 6 dk_names？ | `枚举<dk_name>` | 实测 L5 有 8 dk_names — 比预期多 1。排查：caudalanteriorcingulate 的 FrontalPoleSN 仍标记 L5，其 dk_name=caudalanteriorcingulate 被计入 L5（尽管 ACC/ACC背侧 在 L2） | L5: 8 dk_names（含 1 个跨层 dk） | 技能生成、链路层级映射 | caudalanteriorcingulate 跨越 L2 和 L5 → 一个解剖区域同时参与两个层级的功能。这是"实体归层"范式下的合理现象（同区域不同功能在不同层级操作），但需在文档中显式说明 | ⚠️ 计数歧义 |
| T4 | L3 计数变化 | 原 L3 7 fids → 6 fids | 减 1（枕顶联合 L3→L4） | L3 现在严格为初级感觉皮层（无跨模态变体混入） | 6 fids / 6 dk_names | 技能设计 — L3 操作现在全部为单模态感觉 | L3 更干净，但"枕顶联合"(视觉-空间整合)从 L3 移除意味着 L3 不再提供空间定位功能 → 需要 L4 顶上 | ⚠️ 功能重定位 |

## 缺口汇总

| # | 位置 | 严重度 | 状态变化 |
|----|------|--------|---------|
| G1 | validate_spatial.py:77 | ❌ | 未变 |
| G2 | build_link_legitimacy_matrix.py:95 | ❌ | 未变 |
| G3 | brain_regions.json _description | ⚠️ | 未变 |
| G4 | L6 归零 | ✅ 关闭 | 用户确认删除 |
| G5 | "89脑区" 17处 | ⚠️ | 未变 |
| G6 | build_region_name_map.py | ⚠️ | 未变 |
| G7 | 功能表残留 | ⚠️ | 等文档重写 |
| G8 | dk_name层级冲突 | ⚠️→⚠️ | 3→1 残留（caudalanteriorcingulate {L2,L5}） |
| G8a | caudalanteriorcingulate 跨层 | 🆕 ⚠️ | 前额叶极·SN(L5) 与 ACC(L2) 同 dk_name — 解剖实体归 L2 但 SN 功能在 L5 操作 |
| G9 | 通路功能迁移 | ⚠️ | 等文档重写 |
| G10 | 小脑 L0 归属 | ⚠️ | 未决策 |
| G11 | ENIGMA 中文 key | ⚠️ | 未修复 |
| G12 | 内嗅皮层 L1/L4 | ✅ 关闭 | 确认 L4 |
| — | 颞上回 L5→L4 | 🆕 ⚠️ | 语言理解功能从"跨模态认知"变为"高级听觉模式识别" |
| — | 枕顶联合 L3→L4 | 🆕 ⚠️ | 视觉-空间整合从"初级感觉"变为"高级模式识别" |

## 最终数据状态

| 度量 | 值 |
|------|-----|
| functional_id 条目 | 70 |
| dk_name（网格） | 40 |
| 脑干核团点 | 10 |
| **解剖实体总计** | **50** |
| is_design_node | 0 |
| obj_file 可解析 | 60/60 |
| L6 条目 | 0 ✅ |
| 层级冲突 | 1 组残留（caudalanteriorcingulate） |
| 层级分布 | L0:11 L1:16 L2:8 L3:6 L4:15 L5:14 |

## 统计
- 增量 trace 行数 4 / ✅ 1 / ⚠️ 3 / ❌ 0
- 累计缺口: 11（2❌ + 8⚠️ + 1🆕）
- 本次关闭: G4(L6), G12(内嗅皮层)

---
*创建: 2026-08-07 | 基于上一轮 trace: review-trace-2026-08-07-1138-brain-regions-data-refactor.md*
