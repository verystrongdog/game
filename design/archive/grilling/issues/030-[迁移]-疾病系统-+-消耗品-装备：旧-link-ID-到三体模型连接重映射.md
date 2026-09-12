# #30 [迁移] 疾病系统 + 消耗品/装备：旧 link ID 到三体模型连接重映射

> 状态：开放 · 创建 2026-08-07
> 标签：维度:规则, 维度:实体, needs-triage
> 原始：https://github.com/verystrongdog/game/issues/30

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 背景

19 个疾病配置文件 + 消耗品/装备效果表使用旧 `link_XXX` ID（如 `link_336`, `link_007_L`）。这些 ID 指向已删除的 `link_registry.json` / `link_legitimacy_matrix.json`。需要全部重映射到三体模型连接表示法（`source_dk→target_dk` + `signal_type`）。

## 当前状态

- ✅ `tripartite_model.json` — 1049 连接，全部有 function_label + gameplay_labels
- ❌ **19 个疾病配置文件**（`实体/疾病目录/*.md`）— 使用旧 link ID
  - 示例：`偏执型精神分裂症.md` 引用 `link_336`, `link_344`, `link_007_L`, `link_327` 等 15 条
  - 每个疾病配置有：链路配置表（m 偏移量）+ 组件掉落池（权重 + link ID）
- ❌ **消耗品/装备效果表** — 物品效果引用旧 link ID
- ❌ **面具组件系统** — `实体/角色与面具.md` §8.8 引用 "364+病理链路"

## 需要做

1. **疾病配置迁移**（19 文件）：
   - 逐链路查旧 link ID → 对应的脑区对
   - 在三体模型中找到对应的 connection（source→target + signal_type 交集）
   - 更新 m 偏移量表、非线性跳变条件、组件掉落池
2. **消耗品/装备效果迁移**：
   - 用 dk_name→dk_name 替代 link_XXX 引用
   - 标注 signal_type（药物可能只影响特定信号类型）
3. **面具组件迁移**：
   - `实体/角色与面具.md` 中 "364+病理链路" → 三体模型

## 阻塞

- 无直接阻塞
- 疾病配置的病理链路映射可能需要 #28（技能遴选）的 domain 分析结果辅助

## 参考

- `实体/疾病目录/偏执型精神分裂症.md`（典型示例）
- `实体/角色与面具.md` §8
- `data/connectivity/tripartite_model.json`
- memory: `disease-system-grilling-2026-08-01.md`

---
*导出: 2026-09-12 | 来源: GitHub issue*
