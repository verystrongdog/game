# Review Trace: brain_regions.json 数据反转 — 89→50解剖实体

> 审查日期: 2026-08-07 11:38 | 审查范围: brain_regions.json 删除19条目 + obj_file路径修复 + region_name_map.json同步
> 方法: 符号执行 + 限界验证 | 前置检查: run_all_checks.py (5/6 passed, 1 failed, 0 blocker)

## 前置输入
- [x] run_all_checks.py --format json — 5/6 通过（validate_link_data 8 pass / validate_disease pass / validate_spatial 3 pass 1 fail / validate_trash_isolation pass / validate_params 23 pass 4 warn / validate_cross_refs 480/481 pass）
- [x] Layer 1.5 抽查: 3/3 项独立核对（见下）
- [x] 被引用文件自动拉入: brain_regions.json, region_name_map.json, 脑功能层级模型.md, validate_spatial.py, build_link_legitimacy_matrix.py, 六维状态.md, 核心机制.md, 敌人与事件.md, build_region_name_map.py

## Trace Table

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T1 | brain_regions.json §regions — 删除19条目 | regions dict（functional_id 主键） | `Dict<枚举<89>, Region>` | 删除 7 设计节点 + 8 通路型点位 + 4 皮层下细结构 | `Dict<枚举<70>, Region>` | 全部 6 个 Layer 1 validator + build_link_legitimacy_matrix.py + 3D 管线（brain_atlas_to_blender.py）+ 文档表（脑功能层级模型.md §十八） | AmygdalaPAGPathway 已转为链路身份（P0 待生成）；is_design_node 归零 | ✅ |
| T2 | brain_regions.json §regions.*.obj_file — 路径修复 | 60 条断裂路径（缺 `规则/` 前缀 + 缺 `3D可视化/` 中间段） | `List<路径>` 60 条 | 前缀补齐：`技能树系统/` → `规则/技能树系统/3D可视化/` | `List<路径>` 60 条全可解析 | 3D 可视化管线、brain_atlas_to_blender.py、视图标记验证 | 实测 890 OBJ 文件存在于 `规则/技能树系统/3D可视化/blender_assets/all_obj/`；皮层下 aseg 文件路径模式待确认 | ✅ |
| T3 | region_name_map.json §regions — 同步删除 | nm['regions'] dict（functional_id 主键） | `Dict<枚举<89>, 文本>` | 删除 19 条映射 → `Dict<枚举<70>, 文本>` | `Dict<枚举<70>, 文本>` | 管线 rel 匹配、技能挂载、gen_skill_reference.py | 此前清扫清单未含此文件（review-trace G3）→ 本次已同步 | ✅ |
| T4 | brain_regions.json — _description 元数据 | 元数据字符串 | `文本` | "89 脑区 — functional_id 主键 (D25/D13)" → "50 解剖实体 (2026-08-07 Grilling #25 — 解剖基座重构)" | `文本` | 阅读者 + grep 清扫 | 数字从 89→50（解剖实体数），但 JSON 仍有 70 个 functional_id 条目（功能变体拆分）。_description 说 50 实体但 regions dict 有 70 key → 元数据与数据结构的 50 vs 70 差异需在文档中解释 | ⚠️ 语义不一致 |
| T5 | validate_spatial.py S4 — is_design_node 断言 | regions is_design_node 标记 | `List<functional_id>` 计数 | `len(design) >= 7` 硬编码断言 → 现在 design = [] → len=0 | PASS/FAIL | Layer 1 门禁（run_all_checks.py → validate_spatial） | 删除后 0 < 7 → **FAIL**。脚本预期值未同步 | ❌ 已知 G1 |
| T6 | 活跃文档 "89脑区" 表述 | 活跃 .md/.py 文件中的数字字面量 | `文本` 17 处（CLAUDE.md:280 / 敌人与事件.md:3,112,205 / 六维状态.md:43,296,300 / 管线.md:13 / 规则.md:11 / 核心机制.md:3,48,99,743 / README.md:3 / build_link_legitimacy_matrix.py:15,705 / build_region_name_map.py:2,4,7,164 / normalize_region_names.py:17 / rebuild_brain_regions.py:55 / gen_modulation_ceiling.py:35） | 89 → 50（解剖实体数），或 89 → 70（functional_id 条目数）— 取决于上下文 | `文本` 17 处需改 | 文档阅读者、新开发者理解项目规模 | Layer 1 cross_refs 查链接不查数字 → 只能 grep 人工清扫。决策树 24 处保留（历史记录合规） | ⚠️ G5 |
| T7 | build_link_legitimacy_matrix.py — bfb_region 键断裂 | brain_regions.json bfb_region 字段 + Kroell 网络映射 | `Dict<bfb_region, List<网络>>` | fdb33dc commit 将 bfb_region 字段改名为 dk_name → `load_brain_regions()` L95 `bfb = r.get("bfb_region")` 永远返回 None → 全部 Kroell 协同激活检查失效 | `Dict<None, List>` → 空映射 | link_legitimacy_matrix.json（364 链路）的 future regeneration | 当前 364 链路是旧版产物，尚未重新生成 → 矩阵暂时不受影响。但下次 `build_link_legitimacy_matrix.py` 运行时全部 Kroell 检查将失效，仅剩连接组+白质检查 → 链路数将剧烈减少 | ❌ P-1 |
| T8 | build_region_name_map.py — 硬编码 89 | 脚本 docstring + _description | `文本` 5 处 | 89 → 70（functional_id 条目）或 50（解剖实体） | `文本` | 脚本输出 region_name_map.json 的 _description 字段 | 当前 region_name_map.json 已手动修复为 70 条目，但脚本下次运行时将回写 "89 脑区" | ⚠️ 数据漂移 |
| T9 | 脑功能层级模型.md §十八 — 层级分布摘要表 | 旧层级表（L0=16/L1=21/L4=14/L5=23/L6=5） | `Dict<层级, 数值>` 含已删条目 | 重写：L0 16→11、L1 21→8(dk)/16(fid)、L4 14→11(dk)/13(fid)、L5 23→7(dk)/15(fid)、L6 5→0 | `Dict<层级, 数值>` 新表 | 技能生成（L0-L5 层级映射）、六维状态、敌人与事件（敌我同构）、核心机制.md | L6 归零：旧 L6 条目（前额叶极·DMN/FPN/SN, DMN+OFC, 全脑整合）全部为功能变体或设计节点，collapse 到父 dk_name 后无独立 L6 解剖区域。L6 概念层是否需要保留待设计决策 | ❌ L6 消失 |
| T10 | 脑功能层级模型.md §四 L1 功能表 — 删除条目残留 | §4.1 功能表（旧含 BNST/下丘脑/隔区/缰核） | `表格` | 删除 BNST/下丘脑/隔区/缰核 行；内嗅皮层从 L1 表移至 L4（JSON level=4） | `表格` | 技能设计者、NPC AI 行为模型（敌我同构） | 旧文档 §4.1 将内嗅皮层列在 L1 功能表中但 JSON level=4 — 文档与数据不一致（迁移后修复） | ⚠️ G4 |
| T11 | 脑功能层级模型.md §三 L0 区域列表 — 删除条目残留 | §3.2 区域表（旧含 VTA-NAcc/反射环路×3/杏仁核-PAG） | `表格` 16→11 行 | 删除 5 个设计节点/通路行 | `表格` 11 行（10 脑干核团 + 小脑皮层） | 3D 可视化管线、脑干社区颜色映射 | 小脑皮层保留在 L0（非脑干但无更高层级归属） — 需确认层级正确性 | ⚠️ |
| T12 | 脑功能层级模型.md §八 L5 功能表 — 通路条目删除 | §8.1 功能表（旧含弓状束/岛叶-ACC系列/mPFC-杏仁核/vmPFC-TPJ/前额叶-海马/额顶网络） | `表格` 14→7 行 | 删除 7 个通路/设计节点行；功能标签（传话/共感/命名等）转移到对应端点的解剖区域功能表中 | `表格` 7 行 | 技能生成、浮现式技能前置条件 | 弓状束的"传话"功能 → 需挂载到 Broca区(parsopercularis) 或 Wernicke区(superiortemporal) 作为跨区域功能；额顶网络的"切换"功能 → dlPFC(rostralmiddlefrontal) | ⚠️ 功能迁移 |
| T13 | 脑功能层级模型.md §九 L6 — 层级归零 | §九 区域表（旧含 5 条目：3 前额叶极·网络变体 + DMN+OFC + 全脑整合） | `表格` 5→0 行 | 全部 collapse 到父 dk_name 或删除（全脑整合） | `表格` 0 行 | L6 链路设计约束（§9.3：终极链路层/8-12回合冷却/月光下效果最强）— 约束仍在但锚点消失 | L6 概念（自我叙事/跨网络协调）是否应保留为 L5 的功能覆盖层？DMN/FPN/SN 三大网络的功能标签现分布在 L2(caudalanteriorcingulate=SN) 和 L5(medialorbitofrontal=DMN, rostralmiddlefrontal=FPN) | ❌ 架构断层 |
| T14 | brain_regions.json — dk_name 内层级冲突 | 3 组共享 dk_name 的功能变体（caudalanteriorcingulate/superiortemporal/lateraloccipital） | `Dict<dk_name, Set<level>>` | 未修正（本次删除未触碰 level 字段） | `Dict<dk_name, Set<level>>` — caudalanteriorcingulate: {2(ACC/ACC背侧), 5(前额叶极·SN)} / superiortemporal: {4(Wernicke/颞上沟), 5(颞上回)} / lateraloccipital: {3(枕顶联合), 4(外侧枕叶)} | 链路层级相邻规则（§十五）、3D 视图层级着色 | 同一解剖区域的功能变体跨 2 层级 → "层级相邻"规则中的"相邻"定义需要澄清：是解剖层级还是功能层级？ | ⚠️ 未解决 |

## 缺口汇总

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| G1 | validate_spatial.py:77 | ❌ 高 | 硬编码 `len(design) >= 7` — 删除后 0 → FAIL。Layer 1 门禁断裂。修复：改为 `>= 0` 或语义化断言 |
| G2 | build_link_legitimacy_matrix.py:95 | ❌ 高 | `bfb_region` 键断裂（fdb33dc 改名未同步）— 下次运行全部 Kroell 协同激活检查失效 |
| G3 | brain_regions.json _description | ⚠️ 中 | "50 解剖实体"但 regions dict 有 70 key（功能变体拆分）。数字语义不一致 |
| G4 | 脑功能层级模型.md §九 | ❌ 高 | L6 归零 — 旧 L6 条目全部 collapse。L6 概念（自我叙事/跨网络协调/终极链路层）失去解剖锚点 |
| G5 | 活跃文档 | ⚠️ 中 | "89脑区" 17 处待更新。Layer 1 不查数字 → 需 grep 人工清扫 |
| G6 | build_region_name_map.py | ⚠️ 中 | 硬编码 89 在 docstring 和 _description — 下次运行回写错误数据 |
| G7 | 脑功能层级模型.md §3.2/§4.1/§8.1/§9.2 | ⚠️ 中 | 删除条目的功能表行仍需清理：L0 删 5 行、L1 删 4 行、L5 删 7 行、L6 全删 |
| G8 | dk_name 内层级冲突 | ⚠️ 中 | 3 组功能变体的 level 跨越 2 层 — 链路层级相邻规则的定义模糊 |
| G9 | 通路功能迁移 | ⚠️ 低 | 8 个通路点的功能标签（传话/共感/命名/换位等）需挂载到对应解剖端点的功能表中 |
| G10 | L0 小脑皮层 | ⚠️ 低 | 小脑皮层在 L0（与脑干核团并列）— 层级归属需确认（小脑具有独立层级组织） |
| G11 | ENIGMA_SUBCORTICAL_MAP | ⚠️ 中 | build_link_legitimacy_matrix.py:52 中文 key 映射 — 部分 key 可能不匹配改名后的 functional_id |
| G12 | 脑功能层级模型.md §4.1 | ⚠️ 低 | 内嗅皮层在旧 L1 功能表中但 JSON level=4 — 文档写错了，迁移到 L4 时纠正 |

## 半径扩张 — 待复查

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| S4 预期值（G1） | Layer 1 门禁、review-plan Step 0 | 待修复 |
| bfb_region 键（G2） | link_legitimacy_matrix.json 下次生成 | P-1 待修复 |
| "89脑区" 清扫（G5） | CLAUDE.md / 核心机制.md / 敌人与事件.md / 六维状态.md / 管线.md / 规则.md / README.md × 7 + .py × 5 | 待执行 |
| build_region_name_map.py（G6） | region_name_map.json 下次重建 | 待修复 |
| 脑功能层级模型.md 重写（G4/G7/G9/G10） | 技能生成、六维状态、敌人与事件、核心机制 | 本文档待建 |
| 层级冲突（G8） | 链路合法性的"层级相邻"规则 | 待 grilling 决策 |
| _description 不一致（G3） | 阅读者 | 待决策：50 实体 vs 70 functional_id 哪个是"官方计数" |

## 变更追踪

| 上次缺口（2026-08-06 trace） | 本次状态 | 备注 |
|---------|---------|------|
| G1 validate_spatial S4 | ❌ → ❌ 仍存在 | 未修复（本次未触碰） |
| G2 AmygdalaPAGPathway 去留 | ❌ → ✅ 已解决 | 本次删除（将作为链路在 P0 生成） |
| G3 region_name_map.json | ⚠️ → ✅ 已同步 | 本次已删 19 条 |
| G4 层级表重写 | ⚠️ → ❌ 升级 | 新增 L6 归零问题 |
| G5 "89" 清扫 | ⚠️ → ⚠️ 仍存在 | 新增 5 个 .py 文件引用 |
| G6 obj_file 60 条 | ⚠️ → ✅ 已修复 | 60/60 路径可解析 |
| G7 变体坐标偏差 | ⚠️ → ⚠️ 仍存在 | 未修复（本次未触碰） |
| G8 新文献实体文件 | ⚠️ → 待确认 | 未修复 |
| G9 链路重放路径 | ⚠️ → ⚠️ 仍存在 | 用户未选 A/B/C |
| G10 决策树 24 处 "89" | ⚠️ → ✅ 合规 | 历史记录保留 |
| — 本次新增 G11 | 🆕 | ENIGMA_SUBCORTICAL_MAP 中文 key |
| — 本次新增 G12 | 🆕 | 内嗅皮层 L1/L4 文档错误 |

## 统计
- 总 trace 行数 14 / ✅ 2 / ⚠️ 8 / ❌ 4 / 待复查 7
- 本次新增缺口 4 个（G8/G9/G10/G11/G12 中 4 个为新发现）
- 上次缺口关闭 3 个（G2/G3/G6）

---
*创建: 2026-08-07 | 基于 review-plan SKILL v2*
