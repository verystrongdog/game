# #22 [Grilling] 月光场数值校准 — η→游戏参数精确映射

> 状态：关闭 · 创建 2026-08-05 · 关闭 2026-08-05
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/22

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
月光场 v2 标量场物理模型（#19 闭合，2026-08-04）中标注为"留给数值校准 grilling"的全部自由参数的系统化数值锚定。

## 六维定位
- **维度**: 规则
- **依赖**: 月光场 v2 物理模型 ✅ / SAN 系统 ✅ / 实体类型参数表 ✅ / 数值校准（奠基）✅
- **阻塞**: 月光场在战斗/探索中的实际数值表现 / 旧月相表 η 空间重校准 / 难度缩放公式更新

## 待校准参数
1. SAN → C(ρ_O) 曲线精确系数
2. κ_structure 标度（标签集中度 × 疾病固化度）
3. g_0 月相调制振幅
4. d_eff 昼夜变化率
5. ρ_off → 具体游戏内容映射表
6. 旧月相表（1.0-2.0×）→ η 空间重校准
7. 多观察者 Q 一致性规则

## 当前状态
sim_moonlight_v2_sanity.py 中有分段线性 C_baseline(SAN) 草稿和 η 计算草稿，但所有参数标注为"留给数值校准"。

---

## 评论（2 条）

### verystrongdog · 2026-08-05

## Grilling #22 闭合 — 月光场数值校准

### 决策表

| # | 决策 | 值 |
|----|------|-----|
| D1 | η 公式 | η = g_0 × c(SAN) × κ |
| D2 | c(SAN) 锚点 | c_min=0.03, c_60=0.08, c_30=0.50, c_0=1.00 |
| D3 | κ 查表 | 实体类型查表 ∈ [0.6, 4.5]，默认=1.0 |
| D4 | g_0 月相调制 | g_0 = 0.9 × lunar, lunar ∈ {0.75, 0.88, 1.00} |
| D5 | η_crit 相变 | ≈0.3，昼夜=η自然相变，不设独立f_day |
| D6 | ρ_off 方向 | V = T + D, axis=argmax, conc=|V_axis|/Σ|V_i|
| D7 | 多观察者叠加 | φ(point) = Σ η_i × e^(-r_i/R) / r_i |
| D8 | HP/SAN | = base + equipment + component，阈值保持绝对值 |

### 受影响文件 (13)

- 事件/月光场-标量场模型.md (§七重写)
- 规则/核心机制.md, 实体/敌人与事件.md, 实体/角色与面具.md, 事件/游戏循环.md, 事件/世界观与叙事.md
- 空间/空间与关卡设计.md, 规则/回合战斗流程.md, 规则/技能树系统/NPC AI 行为模型.md
- docs/设计框架-六维状态.md, docs/决策树.md, docs/维度/事件.md
- data/term_registry.json (+7条, 53→60)

### 延迟

- κ_label × κ_disease 动态公式 → 独立grilling
- Δ_situation_max[axis] / direction_weight[axis] 逐轴分化 → 内容设计
- 连续月相→3档平滑过渡 → 实现阶段

### 校验

review-plan v2: 4❌/8⚠️/5✅。❌全在ρ_off权重参数(内容填充性质)，核心公式链闭合。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

### verystrongdog · 2026-08-06

## 🔧 闭合后修正 (2026-08-06)

Grilling #22 闭合后发现以下缺口，已修正并提交 (0aeea35)：

### 修正项

| # | 修正内容 | 原决策 | 修正后 |
|---|---------|--------|--------|
| C1 | SAN 阈值类型 | 绝对值（≥60 稳定） | **相对值**（≥60% 稳定），按 SAN_max 百分比计算 |
| C2 | SAN_max 公式 | SAN_base + equipment_SAN + component_SAN（三项） | SAN_base + **link_SAN** + equipment_SAN（三项，删 component_SAN） |
| C3 | link_SAN 稳定链路加权 | 未定义 | k_stab × mean(m_stabilizing) × SAN_base, k_stab=0.3, 20 条链路 (ER+CAC) |
| C4 | component_SAN 独立项 | 存在但无映射 | **删除**——组件改变链路 m，通过 link_SAN 间接影响 SAN |
| C5 | 公式未写入正典 | 仅存决策树 | 写入 核心机制.md §5.0 + §十 + §十一 |

### 受影响文件
- 规则/核心机制.md (新增 §5.0, §十/§十一 更新)
- 实体/武器与装备.md (§1.6 装备 SAN/HP, 25 件护甲 +1/+1 占位)
- 规则/技能树系统/NPC AI 行为模型.md (阈值 %)
- 实体/敌人与事件.md (阈值 %)
- 实体/角色与面具.md (阈值 %)
- 规则/回合战斗流程.md (阈值 %)
- docs/决策树.md (修正记录)

### 根因
闭合时阈值保持绝对值的判断未充分考虑 SAN_max 浮动的影响。低 SAN_max (50) 的人和高 SAN_max (110) 的人在相同绝对阈值下触发时机不对称。

---
*导出: 2026-09-12 | 来源: GitHub issue*
