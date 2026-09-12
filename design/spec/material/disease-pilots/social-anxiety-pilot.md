# 社交焦虑障碍重映射试点（新增病）

> Grilling #88 试点批——**社交焦虑障碍（新增病，无旧文件）**，disease_id=`social-anxiety`，CGI-S 3-7（建议）。**DSM-5 命名**：社交焦虑障碍（社交恐惧症）Social Anxiety Disorder (Social Phobia)（DSM-5 300.23）。纯文献驱动：**13 条病理边全部命中 `tripartite_model.json` 现有边（0 条"病理新增"）**。核心病理 = **社会情境特异性**（vs GAD 泛化持续、特定恐惧对象特异、惊恐发作性突发）：**社交评估回路过度激活**——面孔/社交线索→杏仁核（fusiform/temporalpole→Amygdala）、内感受反馈环（insula↔Amygdala）、心智化过度（STS/TPJ/mPFC/precuneus 节点群：`superiortemporal`/`supramarginal`/`superiorfrontal`）+ vmPFC 调控不足 + 社交情境 NE/5-HT 唤醒。**7 参数推导与建议标签组合「敏化-威胁 + 反刍」完全一致**（社交反刍 = 事后反复咀嚼社交表现——SAD 标志性症状）。**三档全（CGI-S 3-7）；laterality_delta 全部 0（无稳健偏侧证据）。**

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [社交焦虑障碍 → 7 参数映射建议 + 标签组合建议](#三社交焦虑障碍--7-参数映射建议--标签组合建议)
4. [链路来源与映射说明（新增病——无旧链路对照）](#四链路来源与映射说明新增病无旧链路对照)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Etkin & Wager (2007)** *Am J Psychiatry* | ALE meta（PTSD/SAD/SP 对比） | **SAD 杏仁核 + 岛叶过度激活 > PTSD** → 社交情绪/内感受边群（soa_e01~e04）方向与量级锚 |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | **社会过程（心理理论）：MPFC, TPJ, STS, 楔前叶**；社会过程（affiliative）：VTA-NAcc-VP-杏仁核；急性威胁：杏仁核→vmPFC/dmPFC/ACC → 社会认知节点群映射（§四）+ 防御/调控边群 |
| 3 | **社交焦虑障碍 fMRI 共识**（杏仁核超反应 + 岛叶超激活 + mPFC 自我参照过度 + vmPFC 调控不足，系统综述级证据） | 任务态/静息态 meta | 社交评估回路：**面孔/评价刺激→杏仁核↑；前额叶自上而下调控↓** → soa_e08（vmPFC 解耦）+ 社交内感受反馈环（soa_e03/e04） |
| 4 | **Guo et al. (2026)** *Transl Psychiatry* | 跨诊断 ALFF meta | 焦虑障碍 ALFF↑ 双侧岛叶/ACC-mPFC/杏仁核/纹状体（共享模式）→ e02/e12/e13 方向补充 |

**辅助锚（方向/范围补充）**：

- **NPC AI §7.2 目标选择**——「社交突显：颞极/mPFC/STS 相关 a(t) → cognitive gate（感知 bypass）」：SAD 的社交评估节点群（temporalpole/superiorfrontal/superiortemporal）已在游戏目标选择机制中承担社交突显角色 → 本文件边群与既有 NPC 机制同构。
- **post-event processing（社交后反刍）**——SAD 患者在社交事件后反复咀嚼表现（Clark & Wells 认知模型）→ 建议标签「反刍」的临床依据（§三.2）。
- **左右脑偏侧化-文献数据源**——SAD 无稳健左右偏侧证据 → 全部边 Δ = 0。

> **转换规则声明**：同 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md)——文献脑区/网络层结论 → 三体边层为设计师翻译（文献数据源 §八）；m 偏移量级参照同类焦虑病（GAD/SP 试点）设计校准，**新增病全部数值标记 `[NEW]`，待数值校准**。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点）。**社交脑区映射（§四 详表）**：dmPFC→`superiorfrontal`（fid SuperiorFrontalMPFC）、vmPFC→`medialorbitofrontal`（fid MedialOrbitalPrefrontalVMPFC）、**TPJ→`supramarginal`（fid SupramarginalTPJ）**、**STS→`superiortemporal`（fid SuperiorTemporalSulcus）**、颞极→`temporalpole`、梭状回/FFA→`fusiform`、楔前叶→`precuneus`。**13 条全部命中现有边，0 条"病理新增"**。**三档全（CGI-S 3-7）；laterality_delta 全部 0。**

### 2.1 社会情绪域（4 条）——「社交刺激→威胁评估 过度耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **social-anxiety_e01** | fusiform | Amygdala | privileged_pathway | ✅ 命中：`ventral_stream_emotion`, dir=feedback, level_diff=−3（L4→L1） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Etkin & Wager 2007（SAD 杏仁核超激活）；面孔加工→威胁评估过度（FFA 超敏） | 非线性跳变①（社交恐慌触发端） |
| **social-anxiety_e02** | temporalpole | Amygdala | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3431 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 社交情绪语义（颞极）→威胁评估（Clark & Wells 认知模型）；RDoC 社会过程 | 行为覆盖①（社交情境触发） |
| **social-anxiety_e03** | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Etkin & Wager 2007（SAD 岛叶超激活 > PTSD）；威胁→躯体反应（脸红/心跳） | 行为覆盖②（社交内感受） |
| **social-anxiety_e04** | insula | Amygdala | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3261 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 内感受→威胁解读反馈环（心跳加速→"被发现出丑"）；Guo 2026 岛叶 ALFF↑ | 行为覆盖② + 非线性跳变①（误报累积端） |

### 2.2 社会认知域（3 条）——「心智化过度」（STS/TPJ/mPFC）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **social-anxiety_e05** | superiortemporal | supramarginal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.4718（STS→TPJ） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | RDoC 心理理论（MPFC/TPJ/STS）；社交线索过度解读（"他在看我/评判我"） | 行为覆盖①（社交情境触发） |
| **social-anxiety_e06** | supramarginal | superiorfrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.2181（TPJ→mPFC） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 被评价感——他人视角→自我参照（TPJ→mPFC）；Clark & Wells 自我聚焦 | 非线性跳变②（社交恐慌） |
| **social-anxiety_e07** | superiortemporal | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.232（STS→mPFC） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 社会情境→自我评价（STS→mPFC 心智化过度）；RDoC 心理理论 | 非线性跳变③（事后反刍锁定） |

### 2.3 抑制域（1 条）——「vmPFC 调控不足」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **social-anxiety_e08** | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | 社交焦虑共识：vmPFC 对杏仁核调控不足；RDoC 急性威胁（vmPFC 抑制端） | 行为覆盖③（L5 压制 −30%） |

### 2.4 唤醒域（3 条）——「社交情境 NE/5-HT 唤醒」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **social-anxiety_e09** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/+0.1/+0.2 | 0 | RDoC 唤醒域；社交情境 NE 唤醒（紧张/出汗） | 行为覆盖①（社交情境触发） |
| **social-anxiety_e10** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 社交内感受唤醒（脸红/心悸躯体化） | 行为覆盖② |
| **social-anxiety_e11** | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | 过度耦合 | 0/+0.1/+0.2 | 0 | SAD 一线治疗 = SSRI（5-HT 系统核心靶点）；RDoC 社会过程 5-HT | 3.1 节 5HT tone 推导锚 |

### 2.5 行动门控域（2 条）——「社交回避门控」⭐新增（均命中现有边）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **social-anxiety_e12** | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Guo 2026 共享纹状体 ALFF↑；社交威胁→回避行动门控 | 3.1 节 bias_limbic 推导锚 + 行为覆盖④ |
| **social-anxiety_e13** | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 社会疼痛/被排斥→dACC 激活（Eisenberger 社会疼痛研究）；社交焦虑认知循环过度激活 | 3.1 节 bias_cognitive 推导锚 + 非线性跳变③（反刍） |

**图例**：全部边命中现有三体边（0 条"病理新增"——新增病从严：优先语义转移，本文件无转移需求，13 条均直接命中）；Δ = 0 = 无偏侧证据；「轻/中/重」三档全 = CGI-S 3-7。

---

## 三、社交焦虑障碍 → 7 参数映射建议 + 标签组合建议

### 3.0 标签组合建议（新增病——先建议，再推导验证）

| 建议标签组合 | 理由 | §4.2 标签输出 |
|------------|------|--------------|
| **敏化-威胁 + 反刍** | ① 敏化-威胁：社交刺激被过度解读为威胁（杏仁核超激活——Etkin & Wager 2007）；② 反刍：**社交后反刍（post-event processing）**——SAD 标志性症状，社交事件后反复咀嚼表现（Clark & Wells 认知模型）→ 与 DMN/心智化边群（e05~e07）对应 | 敏化-威胁：NE +0.2, 5HT −0.2, bias_limbic +0.15；反刍：NE −0.1, bias_cognitive +0.15；**叠加取最大值**：NE +0.2, 5HT −0.2, bias_limbic +0.15, bias_cognitive +0.15 |

> **标签组合区别于**：PTSD/GAD/SP = 敏化-威胁（±抑制不足）——SAD 独有 bias_cognitive +0.15（认知/语言行动倾向↑ = 过度心智化 + 反刍的 7 参数表达）。

### 3.1 从病理边推导（4 tone + 3 CSTC）

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e09（LC→Amygdala 0/+0.1/+0.2）、e10（LC→insula 0/+0.1/+0.2） | LC 出边群 2/2 命中正偏移 → 社交情境 NE 唤醒（紧张/出汗/脸红） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | SAD 社交奖赏减退（RDoC affiliative）为下游表现，暂不建 VTA 边——奖赏轴非本文件核心 [NEW 待 #88 组件批次] |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e11（DR→Amygdala 0/+0.1/+0.2 过度耦合） | 5-HT 传递聚焦社会威胁回路 → 全局基线↓（去抑制，Soubrié 1986；SSRI 一线治疗佐证） |
| 5 | bias_somatic | **0** | 无 somatic 环路（Putamen）边群命中 | SAD 无运动启动异常（回避 = 行为覆盖层，非 CSTC gate） |
| 6 | bias_cognitive | **+0.15** | e13（caudalanteriorcingulate→Caudate CSTC cognitive GO） | 社会疼痛/被排斥→认知循环过度激活（Eisenberger dACC）→ 语言/认知行动倾向↑（过度心智化 + 反刍）——**SAD 独有偏置** |
| 7 | bias_limbic | **+0.15** | e12（Amygdala→Accumbens-area CSTC limbic GO）、e01/e04（社交情绪边群） | 边缘环路 gate 被社交威胁信号偏置 → 社交回避行动倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁 + 反刍」双标签（本文件 §3.0 建议，多标签叠加取最大值）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁 max(+0.2, −0.1)） | +0.2 | ✅ |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | +0.15（反刍） | +0.15 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：SAD 病理边集 ⇔ 7 参数偏移 ⇔ 建议标签组合「敏化-威胁 + 反刍」三方自洽。SAD NPC 最终参数：NE=0.5、5HT=0.3、bias_cognitive=+0.15、bias_limbic=+0.15（其余基线）。**7 参数签名唯一性**：bias_cognitive=+0.15 使 SAD 在四焦虑病中独有（GAD/SP 该值为 0）。

---

## 四、链路来源与映射说明（新增病——无旧链路对照）

> 新增病无旧链路表可对照；本节替代旧链路对照表，记录**文献脑区→三体节点映射**与**每条边的文献来源**（新增病病理边从严：全部为现有边命中 + 文献锚定）。

### 4.1 社交脑区 → 三体节点映射（文献名 → dk_name）

| 文献名 | 游戏节点（dk_name） | fid | 层级 | 映射依据 |
|--------|-------------------|-----|:---:|---------|
| dmPFC（背内侧前额叶） | `superiorfrontal` | SuperiorFrontalMPFC, SuperiorFrontal | L5 | fid 直接命中（mPFC 心智化/自我参照） |
| vmPFC（腹内侧前额叶） | `medialorbitofrontal` | MedialOrbitalPrefrontalVMPFC, MedialOrbitalPrefrontalDMN, FrontalPoleDMN | L5 | 同 PTSD §6.2 对照表 |
| **TPJ（颞顶联合）** | `supramarginal` | **SupramarginalTPJ**, Supramarginal | L5 | fid 直接命中——TPJ 心智化节点在游戏中存在 |
| **STS（颞上沟）** | `superiortemporal` | **SuperiorTemporalSulcus**, SuperiorTemporalWernicke, SuperiorTemporal | L4 | fid 直接命中——STS 社交线索节点存在 |
| 颞极（social emotion） | `temporalpole` | TemporalPole | L2 | fid 直接命中（NPC AI §7.2 社交突显已引用颞极） |
| 梭状回/FFA（面孔区） | `fusiform` | Fusiform | L4 | fid 直接命中 |
| 楔前叶（ToM/自我） | `precuneus` | Precuneus | L4 | RDoC 心理理论节点 |
| 杏仁核 | `Amygdala` | Amygdala | L1 | — |
| 前脑岛 | `insula` | Insula | L2 | — |

> **结论：TPJ/STS 在游戏中均有直接同名节点**（supramarginal / superiortemporal），无需近似映射——社会认知节点群全部直接落图。

### 4.2 每条边的文献来源（病理边从严核验）

| 病理边 | 文献/机制锚 | 命中详情复核 |
|--------|------------|-------------|
| e01（fusiform→Amygdala） | Etkin & Wager 2007 杏仁核超激活；面孔威胁评估 | ✅ privileged `ventral_stream_emotion`（L4→L1） |
| e02（temporalpole→Amygdala） | 社交情绪语义→威胁评估；RDoC 社会过程 | ✅ CC feedback edr=0.3431 |
| e03/e04（Amygdala↔insula） | Etkin & Wager 2007 岛叶超激活 > PTSD；内感受反馈环 | ✅ CC feedforward/feedback edr=0.3261 |
| e05（STS→TPJ） | RDoC 心理理论（STS/TPJ 心智化） | ✅ CC feedforward edr=0.4718 |
| e06（TPJ→mPFC） | 被评价感（他人视角→自我参照） | ✅ CC lateral edr=0.2181 |
| e07（STS→mPFC） | 社会情境→自我评价；社交后反刍 | ✅ CC feedforward edr=0.232 |
| e08（vmPFC→Amygdala 解耦） | 社交焦虑共识：vmPFC 调控不足 | ✅ privileged `prefrontal_limbic` level_diff=−4 |
| e09/e10（LC 出边） | RDoC 唤醒域；社交 NE 唤醒 | ✅ privileged + `LC_NE` broadcast |
| e11（DR→Amygdala） | SSRI 一线治疗；RDoC 社会过程 5-HT | ✅ `Raphe_5HT` targeted_broadcast |
| e12（Amygdala→Accumbens-area） | Guo 2026 纹状体 ALFF↑；社交回避门控 | ✅ CSTC limbic go_direct |
| e13（ACC→Caudate） | Eisenberger 社会疼痛 dACC；认知循环过度激活 | ✅ CSTC cognitive go_direct |

---

## 五、行为覆盖/非线性跳变保留清单

> 新增病——全部条目为本文件新设计（`[NEW]`，待 #88 数值校准）。

### 5.1 行为覆盖

| 条件 | 约束 |
|------|------|
| 社交情境在场 | **社会认知边群**（e05/e06/e07）额外 +0.1（叠加一次）；**社会情绪边群**（e01/e02）额外 +0.1——社交评估回路整体激活 |
| 社交情境移除 | m 偏移在 **2 回合后**恢复到基线（情境特异性——vs GAD 泛化持续） |
| 内感受边群（e03/e04）m_max ≥ 0.2 | 心跳/脸红被解读为"出丑证据"——每回合 10% 概率将**中性社交线索误判为威胁**（假阳性社交威胁检测） |
| 社交情境 + bias_limbic（e12） | 强制回避行动倾向（社交回避行为覆盖，L5 压制可抵消 30%，受 e08 解耦削弱） |

### 5.2 非线性跳变（社交恐慌 + 反刍锁定）

| m阈值 | 作用域 | 效果 |
|------|---------|------|
| **e01（fusiform→Amygdala）m ≥ 0.4**（重档 + 社交情境叠加）或 社交情境 + 内感受误报 ≥ 2 次 | **社会情绪域边群**（e01~e04） | **社交恐慌**——社交评估回路 3 回合内不可被 L5 压制，SAN −2/回合（急性社交崩溃） |
| **e07（STS→mPFC）m ≥ 0.4**（重档 + 社交情境叠加） | **社会认知边群**（e05/e06/e07） | **事后反刍锁定**——社交事件后 2 回合内心智化边群持续激活（关不掉的反刍），bias_cognitive 生效，行动窗口跳过 10% |

### 5.3 组件掉落池

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **social-anxiety_e01, social-anxiety_e03, social-anxiety_e05, social-anxiety_e06, social-anxiety_e08** |
| 2（关联） | **social-anxiety_e02, social-anxiety_e04, social-anxiety_e07, social-anxiety_e09, social-anxiety_e12** |
| 1（边缘） | **social-anxiety_e10, social-anxiety_e11, social-anxiety_e13** |

> 核心 5 条 = 社交威胁入口（e01）+ 内感受反馈（e03）+ 心智化过度（e05/e06）+ 调控不足（e08）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（SAD） | m_offset | **轻/中/重三档**（CGI-S 3-7），\|m\| ≤ 0.3，m ∈ [0,1] 钳制 | §二 |
| 偏侧偏离量（SAD） | laterality_delta | 0（全部边——无偏侧证据） | §二 |
| NE 基线偏离（SAD） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（SAD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（SAD） | bias_cognitive / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]）——**SAD 独有 bias_cognitive** | §三 |
| 社交情境叠加量 | Δm_social | +0.1（社会认知/情绪边群，单次叠加） | §五.1 |
| 情境移除回落 | t_decay | 2 回合恢复基线 | §五.1 |
| 假阳性社交威胁概率 | p_fp | 10%/回合（内感受边群 m ≥ 0.2 时） | §五.1 |
| 社交恐慌锁定阈值 | m_th | 0.4（e01 重档+叠加，锁定 3 回合，SAN −2/回合） | §五.2 |
| 反刍锁定阈值 | m_th | 0.4（e07 重档+叠加，锁定 2 回合，行动跳过 10%） | §五.2 |
| 标签组合建议 | — | 敏化-威胁 + 反刍 | §三.0 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [广泛性焦虑障碍](../../../entities/diseases/%E5%B9%BF%E6%B3%9B%E6%80%A7%E7%84%A6%E8%99%91%E9%9A%9C%E7%A2%8D.md), [特定恐惧症](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§5.2/§7.2, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §四/§七, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
*待办: 疾病目录新建 [社交焦虑障碍](../../../entities/diseases/%E7%A4%BE%E4%BA%A4%E7%84%A6%E8%99%91%E9%9A%9C%E7%A2%8D.md)（父类 焦虑唤醒障碍，Q0.5）+ term_registry 入库（Q0.4 命名标准——DSM-5 命名 + disease_id=`social-anxiety`）*
