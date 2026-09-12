# SSD 资格核验 — 收尾（3-5 步合成 + 裁决点）

Type: 资格核验批次 2 记录（先行项）
归属: [#116](https://github.com/verystrongdog/game/issues/116) 配额表驱动核验批次
前置: [SSD资格核验-第1-2步](../../../.scratch/grilling-89-npc-material/SSD%E8%B5%84%E6%A0%BC%E6%A0%B8%E9%AA%8C-%E7%AC%AC1-2%E6%AD%A5.md)（DSM 定位 + 原子候选 + 分类修正 A ✅）
状态: ✅ 已裁决（2026-09-06 用户照准五项）

## 〇、裁决结果（2026-09-06）

1. 三原子必要正向 AND 照准；2. 无硬排除原子（声明侧纪律）照准；3. 时长判定留声明侧照准；4. 召回门 = 生理/疾病事件类型照准；5. 归位表三原子落盘照准。

## 一、第 3-5 步合成

### 第 3 步：充分性核验（X⟹d 反样本）

三原子 AND 成立是否 ⟹ SSD？反样本（均被某个原子挡住）：

| 反样本 | 表面相似 | 拦截原子 | 区分锚（DSM） |
|--------|---------|---------|--------------|
| 疾病焦虑障碍 IAD | 高健康焦虑/过度担忧 | SOMATIC_SYMPTOM_HISTORY=0（IAD 无/轻微躯体症状——DSM 与 SSD 的分界正是症状存在性） | DSM-5 IAD vs SSD 鉴别 |
| 转换障碍（功能性神经症状） | 躯体症状 | OVERINVESTMENT=0（无过度投入要件） | DSM-5 转换障碍无 B 标准 |
| MDD 躯体化 | 躯体主诉 + 反刍 | 声明侧纪律（归因于抑郁相——非独立模式） | DSM-5 MDD 伴躯体症状 vs SSD |
| 正常慢性病患者 | 躯体症状 + 关注 | OVERINVESTMENT=0（关注与症状相称） | DSM-5 B 标准"不相称" |
| 伪装/造作 | 症状 + 陈述 | 声明侧纪律（非故意产生——factitious/malingering 排除） | DSM-5 factitious disorder 鉴别 |

**结论（结构）**：三原子 AND 作为必要正向签名在反样本上成立——过度投入（OVERINVESTMENT）承担与躯体疾病/正常反应的核心区分（#89 第 1-2 步已判："B 标准是 SSD 与单纯躯体疾病区分的核心"）。

### 第 4 步：组合规则

- 三原子 **AND**（A ∧ B ∧ C 各为 DSM 必备标准，非 polythetic——无计数问题，三原子各自 #87 声明）；
- `SYMPTOM_DURATION_6M`：时长 ≥6 月判定**留 #87 声明侧**（CYCLIC 配方：资格门不现场算病程——转化接口 :213 禁止项指向现场计算，声明侧原子合法，先例 CYCLIC_MOOD_HISTORY）；
- 任一 MISSING → UNDETERMINED；任一 =0 → INELIGIBLE。

### 第 5 步：归位（草案）

| 原子 | 语义（#87 声明） | 归位 |
|------|-----------------|------|
| SOMATIC_SYMPTOM_HISTORY | 已声明的持续躯体症状存在性（≠ 次数/部位） | SSD 必要正向（DSM A） |
| SYMPTOM_PSYCHOLOGICAL_OVERINVESTMENT | 已声明的与症状相关的心理过度投入存在性（不相称想法/持续高焦虑/过度时间精力） | SSD 必要正向（DSM B，核心区分） |
| SYMPTOM_DURATION_6M | 已声明的症状持续 ≥6 月事实（病程判定留声明侧） | SSD 必要正向（DSM C） |

**排除**：无硬排除原子（DSM-5 移除"医学无法解释"——SSD 可共病躯体疾病；伪装/造作/他病解释 = #87 声明侧纪律）。SSD 与器质性疾病的"已充分评估"关系 = 声明侧（区分 3 步反样本已覆盖）。

## 二、用户裁决点

1. 三原子必要正向 AND（SOMATIC_SYMPTOM_HISTORY ∧ SYMPTOM_PSYCHOLOGICAL_OVERINVESTMENT ∧ SYMPTOM_DURATION_6M）照准？
2. 无硬排除原子（伪装/他病 = 声明侧纪律）确认？
3. 时长判定留 #87 声明侧（CYCLIC 配方）确认？
4. 召回门 = 生理/疾病事件类型（§3.2.1 已承载：生理/疾病→{躯体症状主, 惊恐, MDD}）确认？
5. 通过后归位表：SSD 三原子必要正向 + 分类修正 A 落盘（转化接口 批次 1 签名表 SSD 行从"进行中"改定案）？

---

*创建: 2026-09-06 | 状态: 草案待裁决*
*关联: [SSD资格核验-第1-2步](../../../.scratch/grilling-89-npc-material/SSD%E8%B5%84%E6%A0%BC%E6%A0%B8%E9%AA%8C-%E7%AC%AC1-2%E6%AD%A5.md), [C阶段诊断-PTSD-SSD资格门](../../grilling-89-npc-material/C阶段诊断-PTSD-SSD资格门.md), [批次 2 总览](总览.md)*
