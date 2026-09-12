---
父类: 人格障碍（Q0.5 新建父类；P1 必加新病）
疾病ID: borderline-personality
CGI-S范围: 3-7（建议；人格障碍亦可 4-7 起步——项目定案时未定，本试点按 3-7 产出，若改 4-7 则 B′ 过滤去掉轻档）
文献: "Schulze et al. (2016) Biol Psychiatry 79(9) multimodal meta: 情绪加工杏仁核过度激活 + 前额叶(vlPFC)低激活 'too much drive, too little control' | RDoC v4 负性效价+认知控制域: vlPFC 认知重评/vmPFC 调节 | 人际创伤史→情绪记忆高反应 | 5-HT 冲动性攻击假说"
创建: 2026-08-21
---

# 边缘型人格障碍（BPD）重映射试点

> 26 病重映射第二批（Grilling #88 Q0.6；**新增病**，Q0.2 P1 必加）。纯文献驱动，无旧文件。本文件把 BPD 重映射为三体模型上的 **13 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"）。核心病理 = **情绪失调**（杏仁核→PAG 高反应「太多驱动」+ vlPFC→杏仁核 抑制↓「太少控制」——Schulze 2016 "too much drive, too little control"）+ **海马高反应**（人际创伤史→情绪记忆）+ **内侧前额叶自我参照异常**（身份紊乱）。7 参数推导（NE +0.2 / 5HT −0.2 / bias_somatic +0.15 / bias_limbic +0.15）与 NPC AI §4.2 标签组合「敏化-威胁 + 抑制不足」完全一致。输出格式照 [ptsd-pilot.md](ptsd-pilot.md) §六 字段规范。

## 目录

1. [文献锚点](#一文献锚点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [BPD → 7 参数映射建议（4 tone + 3 CSTC）](#三bpd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照（新增病：不适用）](#四旧链路对照新增病不适用)
5. [行为覆盖/非线性跳变保留清单（情绪波动/冲动机制）](#五行为覆盖非线性跳变保留清单情绪波动冲动机制)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Schulze et al. (2016)** *Biol Psychiatry* 79(9)（[PMID 25935068](https://pubmed.ncbi.nlm.nih.gov/25935068/)，多模态 meta） | 情绪加工 meta | BPD 情绪加工：**杏仁核过度激活（"too much drive"）+ 前额叶（vlPFC）低激活（"too little control"）**；海马/旁海马激活↑ → e01（vlPFC 抑制↓ 核心）+ e03（杏仁核→PAG 高反应）+ e05（海马高反应） |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | 负性效价（急性威胁）：杏仁核→PAG/dPAG；认知控制（情绪调节）：vlPFC 认知重评、vmPFC 调节 → e01/e02 的回路级锚 |
| 3 | **人际创伤史（BPD 高发童年虐待/被弃）** | 流行病学+影像关联 | 创伤→情绪记忆回路过度反应（海马/ACC-海马）→ e05/e11/e13（情绪记忆边群）；被弃恐惧→自我参照不稳定 → e09 |
| 4 | **5-HT 冲动性攻击假说**（Coccaro et al.；Siever & Weinstein 2009） | 递质-行为 | 中枢 5-HT 功能↓ → 冲动/攻击 → e08（DR→vmPFC 5-HT 调控不足） |

**辅助锚（方向/范围补充）**：

- **van Zutphen et al. (2015)**——BPD 情绪调节任务中前额叶招募不足 + 杏仁核持续高反应 → e01/e02 的幅值方向支持。
- **NPC AI §4.2 标签**——「敏化-威胁」（NE +0.2, 5HT −0.2, bias_limbic +0.15）+「抑制不足」（5HT −0.2, bias_somatic +0.15）为 BPD 建议标签组合（见 §三.2）。
- **与 PTSD 的镜像/继承关系**：BPD 防御边（e03/e07）与 PTSD 试点防御域边**同端点**，但 BPD 为**过度耦合（反应性、可消退）**、PTSD 为**跨层短路（锁定）**——"情绪风暴" vs "闪回锁定"的行为区分（见 §五）。
- **偏侧说明**：Schulze 2016 存在左侧额叶/杏仁核偏向但不稳健（meta 内异质性大）→ 按 #92 成本原则 + §6.5.2 全部 **Δ = 0**。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；BPD 无旧文件，全部 m 量级为本次设计校准 `[NEW]`（核心边重档对齐 PTSD 校准量级，辅助边轻量）。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**13 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（BPD = `borderline-personality`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围` 过滤——B′ 定案**；本试点建议 3-7 → 三档全可用；若定案 4-7 则轻档被过滤）。
>
> **端点名对照速查**：vlPFC=`parsopercularis`（L5，fid ParsOpercularis——**tripartite 无 parsorbitalis/parstriangularis 节点**，IFG 唯一节点为 parsopercularis/BA44，设计师映射为 vlPFC）｜vmPFC=`medialorbitofrontal`（L5，fid MedialOrbitalPrefrontalVMPFC）｜dlPFC=`rostralmiddlefrontal`（L5）｜杏仁核=`Amygdala`（L1）｜PAG=`PeriaqueductalGray`（L0）｜海马=`Hippocampus`（L1，fid CA1/CA3 合并）｜前岛叶=`insula`（L2）｜腹侧纹状体=`Accumbens-area`（L1）｜壳核=`Putamen`（L1）｜楔前叶=`precuneus`（L4）｜后扣带=`posteriorcingulate`（L2）｜STS=`superiortemporal`（L4，fid SuperiorTemporalSulcus）。

### 2.1 情绪失调域（6 条）——「太多驱动 + 太少控制」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **borderline-personality_e01** ⭐新增 | parsopercularis | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | **−0.2/−0.4/−0.6** | 0 | Schulze 2016 vlPFC 低激活（"too little control"）；RDoC 认知控制（vlPFC 认知重评） | §五.1 行为覆盖① + §五.2 跳变（核心） |
| **borderline-personality_e02** ⭐新增 | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−4 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | RDoC 负性效价（vmPFC 情绪调节）；van Zutphen 2015 | §五.1 行为覆盖①（vmPFC 调节腿） |
| **borderline-personality_e03** ⭐新增 | Amygdala | PeriaqueductalGray | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedback, level_diff=−1（L1→L0） | **过度耦合** | **+0.2/+0.3/+0.5** | 0 | RDoC 急性威胁 dPAG；Schulze 2016 杏仁核过度激活（"too much drive"） | §五.1 行为覆盖① + §五.2 跳变①（情绪风暴核心） |
| **borderline-personality_e04** ⭐新增 | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Schulze 2016 岛叶过度激活；BPD 内感受超敏 | 行为覆盖①（内感受风暴躯体化） |
| **borderline-personality_e07** ⭐新增 | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/+0.2/+0.3 | 0 | 反应性高唤醒（人际应激触发情绪风暴；BPD 应激下 NE 反应↑） | 3.1 节 NE tone 推导锚 |
| **borderline-personality_e08** ⭐新增 | DorsalRapheNucleus | medialorbitofrontal | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | 5-HT 冲动性攻击假说（Coccaro；Siever & Weinstein 2009）——5-HT 对前额叶调节支撑不足 | 3.1 节 5HT tone 推导锚 |

### 2.2 记忆与冲动域（4 条）——「海马高反应 + 冲动」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **borderline-personality_e05** ⭐新增 | Amygdala | Hippocampus | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.6506 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Schulze 2016 海马/旁海马激活↑；人际创伤史→情绪记忆高反应 | 行为覆盖①（情绪情境匹配×2 记忆端） |
| **borderline-personality_e06** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 情绪→行动 gate 劫持 → 冲动行为（BPD 冲动性核心机制） | 3.1 节 bias_limbic 推导锚 + §五 跳变②（冲动爆发） |
| **borderline-personality_e11** ⭐新增 | rostralanteriorcingulate | Hippocampus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3339 | 过度耦合 | 0/+0.1/+0.2 | 0 | 情绪记忆检索增强（创伤重体验/情绪波动载体） | §五 跳变①（情绪波动作用域成员） |
| **borderline-personality_e12** ⭐新增 | Amygdala | Putamen | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3395 | 过度耦合 | 0/+0.1/+0.2 | 0 | 情绪→躯体行动通道（情绪性冲动攻击/自伤） | 行为覆盖②（冲动） |

### 2.3 人际关系域（3 条）——「自我参照异常 + 社会信号过度解读」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **borderline-personality_e09** ⭐新增 | precuneus | medialorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2083 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 内侧前额叶自我参照异常（身份紊乱/空虚感——自我概念随情绪状态漂移） | §五 跳变②（身份紊乱） |
| **borderline-personality_e10** ⭐新增 | superiortemporal | Amygdala | privileged_pathway | ✅ 命中：`amygdalofugal`, dir=feedback, level_diff=−3 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 人际创伤史→社会信号过度解读（拒绝敏感/敌意归因偏向） | 行为覆盖③（拒绝敏感） |
| **borderline-personality_e13** ⭐新增 | posteriorcingulate | Hippocampus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.378 | 过度耦合 | 0/+0.1/+0.2 | 0 | 被弃记忆反刍（DMN-海马 记忆反刍——空虚感/被抛弃恐惧） | 行为覆盖②（反刍侧翼） |

**图例**：⭐新增 = 新增病全部边为文献驱动新增（均命中现有三体边，非"病理新增"）；Δ 全 0 = 无稳健偏侧证据（Schulze 2016 偏侧不稳健，按 §6.5.2 取 0）。**与 PTSD 的关键区分**：e03（杏仁核→PAG）在 PTSD 为**跨层短路 +0.2/+0.4/+0.6（锁定）**、在 BPD 为**过度耦合 +0.2/+0.3/+0.5（反应性、可消退）**——同一端点、不同病理类型，对应"闪回锁定 vs 情绪风暴"两套非线性跳变（§五.2）。

---

## 三、BPD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则照 ptsd-pilot.md §6.6：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e07（LC→Amygdala 0/+0.2/+0.3） | 反应性高唤醒（人际应激触发情绪风暴）——区别于 PTSD 的持续性高唤醒（PTSD 试点 ptsd_e04/e05/e10 LC 出边群三边全命中） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | BPD 无系统性奖赏回路偏移（与躁狂/成瘾区分） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e08（DR→vmPFC 解耦沉默） | 5-HT 对前额叶情绪调节的支撑不足 → 去抑制/冲动（Soubrié 1986；Coccaro） |
| 5 | bias_somatic | **+0.15** | e01/e02（vlPFC/vmPFC→杏仁核 抑制失效）、e12（Amygdala→Putamen） | 自上而下压制失效 → 行动 gate 释放 → 冲动行为（攻击/自伤倾向） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路边群命中 | BPD 冲动是情绪性（limbic 驱动）非计划性——认知 gate 无系统性偏置 |
| 7 | bias_limbic | **+0.15** | e06（Amygdala→Accumbens-area CSTC limbic GO）、e03（防御边群） | 情绪→行动 gate 被劫持 → 情绪/本能行动倾向↑（情绪风暴） |

### 3.2 标签组合建议 + 交叉验证（敌我同构闭环）

**新增病标签建议：`敏化-威胁` + `抑制不足`**（情绪失调核心双标签——高反应驱动 + 低控制；可选追加 `反刍` 表征情绪反刍/空虚亚型，见注）。

| 参数 | 标签组合结果（敏化-威胁 + 抑制不足） | 本文边推导结果 | 一致？ |
|------|----------------------------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| 5HT_baseline | −0.2（双标签） | −0.2 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**注（亚型可选）**：情绪反刍/空虚亚型可追加 `反刍` 标签（NE −0.1, bias_cognitive +0.15）——多标签叠加取最大值会覆盖 bias_cognitive 0→+0.15（内在反刍强化），NE 取 +0.2（max(+0.2,−0.1)）不变；是否启用由设计师按 NPC 亚型取舍，本试点核心双标签已自洽。

**结论**：BPD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。BPD NPC 最终参数：NE=0.5、5HT=0.3、bias_somatic=+0.15、bias_limbic=+0.15（其余基线）。与 PTSD（NE +0.2 / bias_limbic +0.15）共享高唤醒参数面，但**行为差异在病理边层**（BPD 反应性过度耦合 vs PTSD 锁定跨层短路，见 §五）。

---

## 四、旧链路对照（新增病：不适用）

> BPD 为 **Q0.2 P1 新增病，无旧文件、无旧 link_NNN 对应**——本节按模板缺省。语义继承记录如下（供跨病一致性核验）：

| 语义源 | 继承内容 | 落点 |
|--------|---------|------|
| PTSD 试点防御域边集（ptsd_e01/e02/e04） | 同端点（Amygdala↔PAG、LC→Amygdala） | **borderline-personality_e03/e07**——病理类型从跨层短路/过度耦合调整为**反应性过度耦合**（幅值上限 +0.5 低于 PTSD 的 +0.6，行为语义"可消退"） |
| PTSD 试点记忆域设计意图（海马情绪记忆） | 海马/ACC-海马 情绪记忆过度反应 | **borderline-personality_e05/e11/e13**——从闪回（跨层短路）调整为情绪记忆过度耦合（创伤重体验但不锁定） |
| NPC AI §4.2 标签「敏化-威胁」 | 防御域过度耦合的标签锚 | 支撑 e03/e07 方向（NE +0.2） |

---

## 五、行为覆盖/非线性跳变保留清单（情绪波动/冲动机制）

> 新增病无旧「行为覆盖」表——本节为 BPD 机制（**情绪波动/冲动**）的新设计挂接，格式照 PTSD §五。

### 5.1 行为覆盖

| 条目 | 新挂接 | 说明 |
|--------|--------|------|
| 情绪风暴（情绪劫持行动选择） | **e03** m > 0.4（+e04 内感受佐证） | 当回合防御/攻击 salience 强制最高——情绪压倒 affordance competition 理性评估 |
| 冲动（行动 gate 无法关闭） | **e06** m > 0.3（+e12 佐证） | 回合内 15% 概率跳过理性行动评估直接执行冲动行动（攻击/自伤/逃离） |
| 拒绝敏感（敌意归因） | **e10** m > 0.3 | 中性社会信号被解读为威胁——社会信号→威胁评估权重 ×2（人际冲突易触发） |

### 5.2 非线性跳变（情绪波动机制核心）

| m阈值 | 作用域 | 效果 |
|------|---------|------|
| **e03 m > 0.5** | borderline-personality_e03 + e04 + e11 | **情绪风暴锁定 1 回合**：防御/攻击 salience 最高，SAN −1/回合；**随后 2 回合 tone 回落至基线**（快速消退）——与 PTSD 跨层短路（永久锁定）的机制性区分：BPD = 情绪波动周期，PTSD = 闪回锁定 |
| **e06 m > 0.5** | borderline-personality_e06 | **冲动爆发**：冲动行动强制（Softmax 温度无效化——无缓冲直接行动） |
| **e09 m > 0.4** | borderline-personality_e09 | **身份紊乱**：自我参照输出随机化（NPC 对自身意图/立场陈述不可靠——身份不稳定） |

### 5.3 组件掉落池（新增病建议）

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **borderline-personality_e01, e03, e05, e06** |
| 2（关联） | **borderline-personality_e04, e07, e09, e10, e13** |
| 1（边缘） | **borderline-personality_e02, e08, e11, e12** |

> 核心 4 条 = 情绪失调双支柱（e01 抑制↓ + e03 驱动↑）+ 海马情绪记忆（e05）+ 冲动 gate 劫持（e06）；权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6，m ∈ [0,1] 钳制 | pathology_edges.json（ptsd-pilot.md §6.1） |
| 偏侧偏离量 | laterality_delta | 全 0（无稳健偏侧证据，§6.5.2） | pathology_edges.json（§6.5） |
| NE 基线偏离（BPD） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（BPD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（BPD） | bias_somatic / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 情绪风暴触发阈值 | m_th | 0.4（当回合 salience 强制最高）/ 0.5（锁定 1 回合 + 2 回合回落） | §五.1/§五.2 |
| 冲动概率 | p_impulse | 0.15（e06 m>0.3 时）/ 强制（e06 m>0.5） | §五.1/§五.2 |
| 拒绝敏感权重 | w_reject | ×2（e10 m>0.3 时社会信号→威胁权重） | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [ptsd-pilot.md](ptsd-pilot.md), [反社会型人格障碍](aspd-pilot.md), [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4/§5.2, [偏侧化架构](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md), [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [角色与面具](../../../%E5%AE%9E%E4%BD%93/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../data/connectivity/tripartite_model.json)*
