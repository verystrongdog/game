# 特定恐惧症重映射试点

> Grilling #88 试点批——特定恐惧症（disease_id=`specific-phobia`，CGI-S 2-4）。旧 5 条链路（link_312 等，挂已废弃 link_registry.json）重映射为三体模型上的 **9 条病理边**（9 条全部命中 `tripartite_model.json` 现有边，0 条"病理新增"；其中 4 条 ⭐新增边均命中现有边）。核心病理 = **刺激特异性**（vs GAD 泛化持续、PTSD 跨层短路、惊恐发作性突发）：防御域 PAG→杏仁核 刺激特异性过度耦合（仅特定对象触发）+ 快速威胁通路（上丘）+ 唤醒域刺激触发 + 记忆域恐惧条件化；**无跨层短路、无认知控制域异常、ACC/vmPFC 功能保留**（vs PTSD 的关键区别）。7 参数推导与 NPC AI §4.2 标签「敏化-威胁」完全一致。**B′ 档位过滤：CGI-S 2-4 → 无重档（只有轻/中，|m| ≤ 0.4）；laterality_delta 全部 0（无稳健偏侧证据）。**

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [特定恐惧症 → 7 参数映射建议（4 tone + 3 CSTC）](#三特定恐惧症--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_312 等 → 新病理边）](#四旧链路对照表link_312-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Etkin & Wager (2007)** *Am J Psychiatry* | ALE meta（PTSD/SAD/SP 对比） | **SP 杏仁核 + 岛叶过度激活 > PTSD**；且 SP **无** PTSD 特有的 ACC 背侧/喙侧 + vmPFC 低激活 → 防御/内感受边群方向（specific-phobia_e01/e06）+ **抑制域缺位**（无 vmPFC 解耦边——机制表达） |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | 急性威胁回路：杏仁核→vmPFC/dmPFC/ACC + **dPAG**；dPAG 快速防御 → PAG→杏仁核 上行 + 上丘快速通路（e01/e02） |
| 3 | **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）** | 数据源 | 5 条旧链路（link_312/317/332/326/003_L）的方向/量级（LeDoux 2000 / Paxinos 2004 / 脑干强度估计）作为语义继承源，见 §四 |
| 4 | **Guo et al. (2026)** *Transl Psychiatry* | 跨诊断 ALFF meta | 焦虑障碍 ALFF↑ 双侧岛叶/ACC-mPFC/杏仁核/纹状体（共享模式）→ e06/e09 方向补充 |

**辅助锚（方向/范围补充）**：

- **[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 思路链**——「[推导: PTSD 防御域对标 ×0.6，刺激特异性缩减]」：SP 防御域量级 = PTSD 防御域 × 0.6 且不泛化（CGI-S 上限 4——回避行为高度可控）。
- **左右脑偏侧化-文献数据源**——SP 无稳健左右偏侧证据 → **全部边 laterality_delta = 0**（§6.5 规则 2）。

> **转换规则声明**：同 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md)——文献脑区/网络层结论 → 三体边层为设计师翻译；m 偏移量级沿用旧文件设计校准（重档量级按 B′ 过滤淘汰），**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点）；病理边禁触镜像实体。**9 条全部命中现有边，0 条"病理新增"**。**B′ 档位过滤：CGI-S 2-4 → 无重档，m 仅轻/中两档**（旧文件 link_312/317/332/326/003_L 的第三档值 = 第二档值的复制，即"重档已被档位过滤吞并"的旧表达；新格式直接呈现轻/中两档）。laterality_delta 全部 0。

### 2.1 防御域（2 条）——「刺激特异性过度耦合」（核心）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e01** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1（L0→L1） | 过度耦合 | +0.2/+0.4 | 0 | 旧 link_312（PAG→杏仁核，LeDoux 2000 / Paxinos 2004）；RDoC 急性威胁 dPAG；Etkin & Wager 2007 杏仁核超激活 | 行为覆盖①（刺激触发 +0.2 叠加） |
| **specific-phobia_e02** | SuperiorColliculus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1（L0→L1） | 过度耦合 | +0.1/+0.2 | 0 | 旧 link_317（上丘→杏仁核经丘脑枕快速通路，Paxinos 2004）——刺激快速检测→恐惧 | 行为覆盖①（刺激出现瞬时触发） |

> **方向说明**：核心病理写作「杏仁核→PAG 刺激特异性过度耦合」（[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 摘要），旧链路表实际以 PAG→杏仁核 上行表达（link_312）；SP **无** L1→L0 下行劫持（跨层短路）——这是与 PTSD/惊恐的机制分界（§6.3 判定 + PTSD 试点方向惯例）。「刺激特异性」由行为覆盖①（刺激在场才叠加、移除后 2 回合回落）落行为层。

### 2.2 唤醒域（2 条）——「刺激触发式唤醒」（非持续）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e03** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/+0.2 | 0 | 旧 link_332（蓝斑→杏仁核 NE，脑干强度估计 fc=0.7）；[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 唤醒域（刺激触发） | 行为覆盖①（恐惧刺激→NE 唤醒） |
| **specific-phobia_e04** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1 | 0 | 旧 link_326（蓝斑→前脑岛 NE，脑干强度估计 fc=0.85） | 行为覆盖①（躯体恐惧反应） |

### 2.3 记忆域（1 条）——「恐惧条件化」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e05** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939 | 过度耦合 | 0/+0.1 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89 L）；[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 记忆域恐惧条件化↑ | 行为覆盖①（情境匹配——刺激识别端） |

> **注意**：e05 端点 caudalanteriorcingulate 含 L5 fid（FrontalPoleSN），按 §6.3 规则 (b) 本可判「跨层短路」——但 SP 该边 **m 极低（0/+0.1）且非核心**，语义为条件化记忆检索而非叙事监控劫持（PTSD e06 判跨层短路的核心依据是 m 高 + 闪回挂接）；SP 以「无跨层短路」为设计不变式，此边按 过度耦合 处理并在核验列注明。

### 2.4 内感受域（1 条）——「岛叶超激活 > PTSD」（Etkin & Wager）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e06** ⭐新增 | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 过度耦合 | 0/+0.1 | 0 | Etkin & Wager 2007（SP 岛叶过度激活 > PTSD）；Guo 2026 岛叶 ALFF↑ | 行为覆盖②（躯体恐惧反应内感受） |

### 2.5 记忆/情绪域（2 条）——「恐惧条件化记忆」⭐新增

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e07** ⭐新增 | Amygdala | parahippocampal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3496 | 过度耦合 | 0/+0.1 | 0 | RDoC 恐惧条件化（杏仁核-海马旁 情景记忆被恐惧条件化劫持）；Etkin & Wager 2007 | 行为覆盖①（刺激-情境关联） |
| **specific-phobia_e08** ⭐新增 | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | 过度耦合 | 0/+0.1 | 0 | RDoC 急性威胁（5-HT 调制恐惧回路） | 3.1 节 5HT tone 推导锚 |

### 2.6 行动门控域（1 条）——「恐惧→回避门控」⭐新增

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **specific-phobia_e09** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1 | 0 | Guo 2026 共享纹状体 ALFF↑；CSTC limbic 门控被恐惧信号偏置（回避行动） | 3.1 节 bias_limbic 推导锚 + 行为覆盖①（回避·主动 强制激活） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ = 0 = 无偏侧证据；「轻/中」两档 = B′ 档位过滤（CGI-S 2-4 无重档）；**抑制域整体缺位**（无 vmPFC→杏仁核 边）= 设计不变式（ACC/vmPFC 功能保留，vs PTSD）。

---

## 三、特定恐惧症 → 7 参数映射建议（4 tone + 3 CSTC）

> 规则同 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §6.6：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e03（LC→Amygdala 0/+0.2）、e04（LC→insula 0/+0.1） | LC 出边群 2/2 命中正偏移 → 蓝斑 NE 上调（刺激触发式高唤醒；[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 唤醒域） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | SP 不累及奖赏回路 |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e08（DR→Amygdala 0/+0.1 过度耦合） | 5-HT 传递聚焦恐惧回路 → 全局基线↓（去抑制，Soubrié 1986；同 PTSD/GAD 推导链） |
| 5 | bias_somatic | **0** | 无 somatic 环路（Putamen）边群命中 | SP 无运动启动异常（回避是行为覆盖层，非 CSTC gate 偏置） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）边群命中 | **认知控制保留**（vs PTSD——SP 无 vmPFC 解耦、无 dlPFC 结构受损） |
| 7 | bias_limbic | **+0.15** | e09（Amygdala→Accumbens-area CSTC limbic GO）、e01（防御边群） | 边缘环路 gate 被刺激触发恐惧偏置 → 回避行动倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」单标签（SP 默认标签，[特定恐惧症.md](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md) 默认标签）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：SP 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。SP NPC 最终参数：NE=0.5、5HT=0.3、bias_limbic=+0.15（其余基线）。**与 PTSD 的 7 参数差异 = bias_somatic（0 vs +0.15）**；与 GAD 的 7 参数相同，**机制区分全在边层**：SP 无 DMN 边群（无泛化担忧）、无 vmPFC 解耦（认知控制保留）、防御边 m 更高（e01 +0.2/+0.4）+ 刺激触发行为覆盖（不泛化）。

---

## 四、旧链路对照表（link_312 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_312 | PAG→Amygdala | 过度耦合 +0.2/+0.4/+0.4 | **specific-phobia_e01** | ✅ 保留语义（端点/类型/量级不变；重档 = 中档复制 → 直接呈现轻/中 +0.2/+0.4） |
| link_317 | SuperiorColliculus→Amygdala | 过度耦合 +0.1/+0.2/+0.2 | **specific-phobia_e02** | ✅ 保留语义（→ +0.1/+0.2） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 0/+0.2/+0.2 | **specific-phobia_e03** | ✅ 保留语义（→ 0/+0.2） |
| link_326 | LocusCoeruleus→Insula | 过度耦合 0/+0.1/+0.1 | **specific-phobia_e04** | ✅ 保留语义（→ 0/+0.1） |
| link_003_L | ACC(L)→Parahippocampal | 过度耦合 0/+0.1/+0.1 | **specific-phobia_e05** | ✅ 保留语义 + **偏侧显式化**（无偏侧证据 → Δ=0，原 L 后缀入字段不保留） |
| （旧表无） | 杏仁核→前脑岛（Etkin & Wager 岛叶超激活 > PTSD） | — | **specific-phobia_e06** | ⭐ 新增 |
| （旧表无） | 杏仁核→海马旁回（恐惧条件化记忆） | — | **specific-phobia_e07** | ⭐ 新增 |
| （旧表无） | 中缝背核→杏仁核（RDoC 急性威胁 5-HT） | — | **specific-phobia_e08** | ⭐ 新增——5HT tone 机制锚 |
| （旧表无） | 杏仁核→腹侧纹状体（恐惧→回避门控） | — | **specific-phobia_e09** | ⭐ 新增——bias_limbic 机制锚 |

**处置规则总结**：5 条旧链路全部直接映射保留（无语义转移、无废弃）——SP 旧链路端点对在三体图中全部存在；4 条 ⭐新增边全部命中现有边（「病理新增」从严，见 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §6.4）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 恐惧刺激出现 → link_312 额外 +0.2（叠加一次），回避·主动 强制激活 | ✅ 保留 | **specific-phobia_e01** + **specific-phobia_e09**（回避行动门控） | 刺激在场 → e01 瞬时 +0.2（中档 0.4→峰值 0.6，`[NEW]` 注：仅刺激在场瞬时，非持久重档）+ limbic gate 强制回避倾向 |
| 恐惧刺激移除 → m 偏移在 2 回合后恢复到基线 | ✅ 保留 | **防御域/唤醒域边群**（e01/e02/e03，刺激移除后 2 回合回落） | 刺激特异性 = 时间上不延续（vs GAD 泛化持续） |
| vmPFC/ACC 功能保留 → L5 控制·主动 对防御域压制有效——不同于 PTSD | ✅ 保留（设计不变式） | **抑制域边群缺位**（无 vmPFC→杏仁核 解耦边） | SP 无抑制不足边——L5 压制有效性是"缺边即机制"的表达 |

### 5.2 非线性跳变（旧文件无此表 → ⭐新增）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| （旧表无） | — | **specific-phobia_e01** 刺激在场且 m ≥ 0.4（中档+叠加）→ **防御域锁定 1 回合**：强制回避行动，SAN −1，不可被 L5 压制 | ⭐ 新增 `[NEW]`——刺激特异性峰值机制（恐惧刺激在场时的短暂锁定，区别于 GAD 的持续警觉锁定、PTSD 的创伤触发持续锁定） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_312, link_317, link_332 | **specific-phobia_e01, specific-phobia_e02, specific-phobia_e03** |
| 2（关联） | link_326, link_003_L | **specific-phobia_e04, specific-phobia_e05, specific-phobia_e06, specific-phobia_e07** |
| 1（边缘） | — | **specific-phobia_e08, specific-phobia_e09** |

> 核心 3 条 = 刺激特异防御（e01）+ 快速通路（e02）+ 刺激唤醒（e03）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（SP） | m_offset | **轻/中两档**（B′ 过滤无重档），m ∈ {0, +0.1, +0.2, +0.4}，\|m\| ≤ 0.4；刺激在场瞬时峰值可达 +0.6（e01 中档+叠加） | §二/§五.1 |
| 偏侧偏离量（SP） | laterality_delta | 0（全部边——无偏侧证据） | §二 |
| NE 基线偏离（SP） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（SP） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（SP） | bias_limbic | +0.15（值域 [−0.3,+0.3]） | §三 |
| 刺激叠加量 | Δm_stim | +0.2（e01，刺激在场单次叠加） | §五.1 |
| 刺激移除回落 | t_decay | 2 回合恢复基线 | §五.1 |
| 防御锁定阈值 | m_th | 0.4（刺激在场，锁定 1 回合，SAN −1） | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [特定恐惧症](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md), [广泛性焦虑障碍](../../../entities/diseases/%E5%B9%BF%E6%B3%9B%E6%80%A7%E7%84%A6%E8%99%91%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§5.2, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七（特定恐惧症）, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../../data/connectivity/link_registry.json)（⚠️ 已废弃）*
