# 惊恐障碍重映射试点（新增病）

> Grilling #88 试点批——**惊恐障碍（新增病，无旧文件）**，disease_id=`panic-disorder`，CGI-S 3-7（建议，惊恐发作可 3-7）。**DSM-5 命名**：惊恐障碍 Panic Disorder（DSM-5 300.01；伴/不伴广场恐惧 300.22）。纯文献驱动：**12 条病理边全部命中 `tripartite_model.json` 现有边（0 条"病理新增"）**。核心病理 = **发作性突发**（vs GAD 泛化持续、特定恐惧刺激特异、社交焦虑社会情境）：**惊恐发作回路**——杏仁核→PAG 跨层短路（L1→L0 突发劫持，dPAG 窒息警报/防御反应）+ 蓝斑 NE 风暴 + **内感受误报反馈环**（insula↔Amygdala，心悸/气促→"我要死了"）+ 发作间期预期焦虑（vmPFC 调控不足）。**7 参数推导与建议标签组合「敏化-威胁 + 抑制不足」完全一致**（发作运动输出超驱动 → bias_somatic）。**三档全（CGI-S 3-7）；laterality_delta 全部 0（无稳健偏侧证据）。**

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [惊恐障碍 → 7 参数映射建议 + 标签组合建议](#三惊恐障碍--7-参数映射建议--标签组合建议)
4. [链路来源与映射说明（新增病——无旧链路对照）](#四链路来源与映射说明新增病无旧链路对照)
5. [行为覆盖/非线性跳变保留清单（含惊恐发作突发机制）](#五行为覆盖非线性跳变保留清单含惊恐发作突发机制)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Klein (1993) 窒息误报警假说**（Suffocation False Alarm Theory，*Arch Gen Psychiatry*） | 理论模型 | **惊恐发作 = 窒息警报的假阳性触发**——PAG/脑干 呼吸-自主警报 + 岛叶内感受 → 发作回路（pan_e01/e05/e06/e07） |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | 急性威胁回路：杏仁核→vmPFC/dmPFC/ACC + **dPAG**；唤醒域蓝斑 NE → 防御/唤醒边群锚 |
| 3 | **Brandão et al. (dPAG 电刺激研究)** | 动物模型 | **dPAG 刺激诱发逃跑/僵直/自主爆发**（惊恐样反应）→ 杏仁核→PAG 跨层短路（pan_e01）+ 运动输出超驱动（pan_e12） |
| 4 | **惊恐障碍 fMRI 共识**（发作期杏仁核/PAG 超激活 + 发作间期 vmPFC 调控不足 + 岛叶内感受超敏） | 任务态/静息态 meta | 内感受误报环（pan_e05/e06）+ 预期焦虑（pan_e11） |

**辅助锚（方向/范围补充）**：

- **Guo et al. (2026)** *Transl Psychiatry*——焦虑障碍 ALFF↑ 岛叶/ACC-mPFC/杏仁核/纹状体（共享模式）→ e05/e09/e12 方向补充。
- **PAG 在游戏中的既有表达**——[ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) e01/e02（Amygdala↔PAG 特权通路）已承载防御域；惊恐障碍复用同一通路但**触发语义不同**：PTSD = 创伤线索触发持续锁定，惊恐 = 内感受误报触发**自限性**发作（§五.2）。
- **PontineReticularNucleus（脑桥网状核）无三体边**——呼吸/自主爆发（过度换气）语义由 PAG（pan_e01）+ LC 广播（pan_e03/e04）+ 岛叶内感受（pan_e05/e06/e07）承载（语义转移，见 §四）。
- **左右脑偏侧化-文献数据源**——惊恐障碍无稳健左右偏侧证据 → 全部边 Δ = 0。

> **转换规则声明**：同 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md)——文献脑区/网络层结论 → 三体边层为设计师翻译；m 偏移量级参照 PTSD（防御域）与 GAD/SP（唤醒/内感受域）试点设计校准，**新增病全部数值标记 `[NEW]`，待数值校准**。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点）。**12 条全部命中现有边，0 条"病理新增"**。**三档全（CGI-S 3-7，惊恐发作可 3-7）；laterality_delta 全部 0。** 防御域量级参照 PTSD e01/e02 校准，但**无记忆域边、无左偏 Δ**——发作是突发-自限的，不固化为创伤记忆。

### 2.1 防御域（2 条）——「惊恐发作跨层短路」（核心）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e01** | Amygdala | PeriaqueductalGray | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedback, level_diff=−1（L1→L0） | **跨层短路** | +0.2/+0.4/+0.6 | 0 | Klein 1993 窒息误报警（dPAG）；Brandão dPAG 刺激诱发惊恐样反应；RDoC 急性威胁 dPAG | 非线性跳变①（惊恐发作触发/锁定） |
| **panic-disorder_e02** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1（L0→L1） | 过度耦合 | +0.2/+0.4/+0.5 | 0 | 发作时 PAG→杏仁核 反馈放大（恐惧-防御循环）；RDoC dPAG | 非线性跳变①（作用域成员） |

> **与 PTSD e01 的区别**：同为 L1→L0 跨层短路，但 PTSD = 创伤线索触发 + 持续锁定（闪回），惊恐 = **内感受误报触发 + 自限性**（3 回合后回落，§五.2）——四病机制区分的第三道分界。

### 2.2 唤醒域（2 条）——「发作 NE 风暴」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e03** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | +0.1/+0.3/+0.5 | 0 | RDoC 唤醒域；发作时 NE 风暴（心悸/出汗/震颤）；GAD 试点 e02 量级对标 | 非线性跳变①（NE 瞬时冲击，NPC AI §3.5 反射级） |
| **panic-disorder_e04** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | +0.1/+0.2/+0.4 | 0 | 发作躯体症状（心悸/气促/胸闷）NE 驱动；脑干强度估计 fc=0.85 | 非线性跳变①（躯体症状端） |

### 2.3 内感受域（3 条）——「内感受误报反馈环」（发作诱因核心）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e05** | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 过度耦合 | +0.1/+0.3/+0.5 | 0 | Klein 1993 窒息误报警（岛叶内感受端）；威胁→躯体反应 | 行为覆盖①（内感受误报累积） |
| **panic-disorder_e06** | insula | Amygdala | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3261 | 过度耦合 | +0.1/+0.3/+0.5 | 0 | **内感受→威胁解读反馈环**（心悸→"我要死了"→更恐慌）；惊恐障碍 fMRI 共识岛叶超敏 | 行为覆盖① + 非线性跳变①（误报计数触发） |
| **panic-disorder_e07** | Thalamus-Proper | insula | cstc | ✅ 命中：limbic 环路 `thalamocortical`, thalamic_relay→cortical_input（另命中 CC feedforward edr=0.5042） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 躯体感觉（心跳/呼吸）经丘脑中继→岛叶内感受放大 | 行为覆盖①（误报信号源） |

### 2.4 快速通路域（1 条）——「突发威胁检测」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e08** | SuperiorColliculus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 突发刺激→杏仁核快速通路（Paxinos 2004；同 SP 试点 e02）；发作诱因感知端 | 行为覆盖①（突发触发检查） |

### 2.5 调制/抑制域（2 条）——「5-HT 去抑制 + vmPFC 调控不足」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e10** | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | 过度耦合 | 0/+0.1/+0.2 | 0 | 惊恐障碍一线治疗 = SSRI（5-HT 核心靶点）；RDoC 急性威胁 5-HT | 3.1 节 5HT tone 推导锚 |
| **panic-disorder_e11** | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | 发作间期预期焦虑（vmPFC 调控不足——"担心再次发作"）；惊恐 fMRI 共识 | 行为覆盖②（预期焦虑）+ 非线性跳变①（发作时压制失效） |

### 2.6 行动门控域（2 条）——「发作逃避 + 运动输出超驱动」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **panic-disorder_e09** | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Guo 2026 共享纹状体 ALFF↑；发作→逃避行动门控 | 3.1 节 bias_limbic 推导锚 |
| **panic-disorder_e12** | precentral | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Brandão dPAG 诱发逃跑/僵直→运动输出；发作时躯体行动门控超驱动 | 3.1 节 bias_somatic 推导锚 |

**图例**：全部边命中现有三体边（0 条"病理新增"）；Δ = 0 = 无偏侧证据；「轻/中/重」三档全 = CGI-S 3-7；**无记忆域边**（vs PTSD——发作不固化为闪回记忆）。

---

## 三、惊恐障碍 → 7 参数映射建议 + 标签组合建议

### 3.0 标签组合建议（新增病——先建议，再推导验证）

| 建议标签组合 | 理由 | §4.2 标签输出 |
|------------|------|--------------|
| **敏化-威胁 + 抑制不足** | ① 敏化-威胁：发作性威胁超敏（杏仁核/PAG 过度激活——Klein 1993）；② 抑制不足：发作时 L5 压制完全失效 + 发作间期预期焦虑（vmPFC 调控不足——惊恐 fMRI 共识）→ 与 e11 解耦 + e12 运动超驱动对应 | 敏化-威胁：NE +0.2, 5HT −0.2, bias_limbic +0.15；抑制不足：5HT −0.2, bias_somatic +0.15；**叠加取最大值**：NE +0.2, 5HT −0.2, bias_limbic +0.15, bias_somatic +0.15 |

> **标签组合与 PTSD 相同（敏化-威胁 + 抑制不足）**——差异全在边层：PTSD = 跨层短路 + 闪回记忆 + LC→dlPFC 结构受损 + 左偏 Δ；惊恐 = 跨层短路 + 内感受误报环 + 发作自限机制 + Δ=0。7 参数不承担病种唯一性（标签仅 6 个设计简写），机制区分由 pathology_edges + 行为覆盖/跳变承担。

### 3.1 从病理边推导（4 tone + 3 CSTC）

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e03（LC→Amygdala +0.1/+0.3/+0.5）、e04（LC→insula +0.1/+0.2/+0.4） | LC 出边群 2/2 命中强正偏移 → 发作 NE 风暴 + 发作间期高警觉；**发作时 δ_event 瞬时冲击 +0.3（NPC AI §3.5 反射级）** |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | 惊恐不累及奖赏回路 |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e10（DR→Amygdala 0/+0.1/+0.2 过度耦合） | 5-HT 聚焦恐惧回路 → 全局基线↓（去抑制，Soubrié 1986；SSRI 一线佐证） |
| 5 | bias_somatic | **+0.15** | e12（precentral→Putamen CSTC somatic GO） | 发作运动输出超驱动（dPAG 防御反应→躯体行动门控，Brandão）→ 逃跑/僵直躯体行动倾向↑——**惊恐独有**（GAD/SP/SAD 均为 0） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）边群命中 | vmPFC 边属 prefrontal_limbic 特权通路（同 PTSD 判定） |
| 7 | bias_limbic | **+0.15** | e09（Amygdala→Accumbens-area CSTC limbic GO）、e01/e02（防御边群） | 边缘环路 gate 被发作威胁信号偏置 → 逃避行动倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁 + 抑制不足」双标签（本文件 §3.0 建议，多标签叠加取最大值）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| 5HT_baseline | −0.2（双标签 max） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：惊恐病理边集 ⇔ 7 参数偏移 ⇔ 建议标签组合「敏化-威胁 + 抑制不足」三方自洽。惊恐 NPC 最终参数：NE=0.5、5HT=0.3、bias_somatic=+0.15、bias_limbic=+0.15（其余基线）。**7 参数签名**：与 PTSD 相同（双标签同构），但与 GAD/SP/SAD 的差异 = bias_somatic=+0.15（躯体行动倾向——发作性躯体防御的 7 参数表达）。

---

## 四、链路来源与映射说明（新增病——无旧链路对照）

> 新增病无旧链路表可对照；本节替代旧链路对照表，记录**文献脑区→三体节点映射**、**语义转移**与**每条边的文献来源**。

### 4.1 文献脑区 → 三体节点映射 + 语义转移

| 文献脑区 | 游戏节点（dk_name） | 层级 | 处置 |
|---------|-------------------|:---:|------|
| dPAG（导水管周围灰质背侧） | `PeriaqueductalGray` | L0 | ✅ 直接命中（特权通路 Amygdala↔PAG） |
| 蓝斑 | `LocusCoeruleus` | L0 | ✅ 直接命中（禁 LC_R 镜像） |
| 杏仁核 | `Amygdala` | L1 | ✅ 直接命中 |
| 前脑岛（内感受） | `insula` | L2 | ✅ 直接命中 |
| 丘脑（躯体感觉中继） | `Thalamus-Proper` | L1 | ✅ 直接命中 |
| 上丘（突发检测） | `SuperiorColliculus` | L0 | ✅ 直接命中 |
| vmPFC | `medialorbitofrontal` | L5 | ✅ 直接命中（同 PTSD §6.2） |
| M1（运动输出） | `precentral` | L3 | ✅ 直接命中（CSTC somatic cortical_input） |
| 中缝背核 | `DorsalRapheNucleus` | L0 | ✅ 直接命中 |
| **脑桥网状核（呼吸/自主爆发）** | `PontineReticularNucleus` | L0 | ⚠️ **无三体边（孤立节点）**——过度换气/自主爆发语义转移至：PAG（e01 跨层短路）+ LC 广播（e03/e04）+ 岛叶内感受（e05/e06/e07） |
| **BNST** | — | — | 不涉及（惊恐无持续警觉特征；持续警觉属 GAD） |

### 4.2 每条边的文献来源（病理边从严核验）

| 病理边 | 文献/机制锚 | 命中详情复核 |
|--------|------------|-------------|
| e01（Amygdala→PAG） | Klein 1993 窒息误报警；Brandão dPAG 惊恐样反应 | ✅ privileged `brainstem_subcortical` L1→L0 |
| e02（PAG→Amygdala） | 发作恐惧-防御反馈循环 | ✅ privileged feedforward |
| e03/e04（LC 出边） | 发作 NE 风暴；RDoC 唤醒域 | ✅ privileged + `LC_NE` broadcast |
| e05/e06（Amygdala↔insula） | Klein 1993 内感受误报；惊恐岛叶超敏 | ✅ CC feedforward/feedback edr=0.3261 |
| e07（Thalamus→insula） | 躯体感觉中继→内感受放大 | ✅ CSTC limbic relay + CC |
| e08（SC→Amygdala） | 突发刺激快速通路 | ✅ privileged feedforward |
| e09（Amygdala→Accumbens-area） | 发作逃避门控；Guo 2026 纹状体 | ✅ CSTC limbic go_direct |
| e10（DR→Amygdala） | SSRI 一线；5-HT 去抑制 | ✅ `Raphe_5HT` targeted_broadcast |
| e11（vmPFC→Amygdala 解耦） | 发作间期预期焦虑调控不足 | ✅ privileged `prefrontal_limbic` level_diff=−4 |
| e12（precentral→Putamen） | dPAG 诱发逃跑/僵直→运动输出 | ✅ CSTC somatic go_direct |

---

## 五、行为覆盖/非线性跳变保留清单（含惊恐发作突发机制）

> 新增病——全部条目为本文件新设计（`[NEW]`，待 #88 数值校准）。**惊恐发作 = 本病的标志性突发机制**（任务硬性要求）。

### 5.1 行为覆盖（发作间期）

| 条件 | 约束 |
|------|------|
| 内感受边群（e05/e06/e07）m_max ≥ 0.2 | **内感受误报累积**——每回合 10% 概率产生一次误报（心悸/气促→威胁）；误报计数 ≥ 2 → 触发发作检查（§5.2） |
| 发作间期（e11 解耦生效） | **预期焦虑**——每 5 回合一次"预期发作"检查（5% 概率误触发低强度警觉，不进入发作） |
| 突发刺激（e08 快速通路） | 突发刺激在场 → 发作检查概率 +10%/回合（情境触发端） |

### 5.2 非线性跳变（惊恐发作突发机制——核心）

| 触发条件 | 效果 | 说明 |
|---------|------|------|
| **发作触发**：e01（Amygdala→PAG）m ≥ 0.4（中档——跨层短路阈值跨越）**或** 内感受误报计数 ≥ 2 | 进入**惊恐发作**状态（3 回合） | 内感受误报累积 → 跨层短路阈值跨越 = 发作起点（误报计数 ≥ 2 为轻/中档主要触发路径；e01 中档起可直接跨越） |
| **发作进行**（3 回合内） | ① **L0 防御锁定**——防御域边群（e01/e02）不可被任何 L5 压制（同 PTSD e01 锁定语义，时长更短）；② **NE 瞬时 +0.3**（δ_event 冲击，NPC AI §3.5 反射级同回合生效）；③ **SAN −3/回合**；④ **行动窗口 40% 概率跳过**（瘫痪/僵直——dPAG 防御反应） | 突发-不可控-躯体化的"惊恐体验" |
| **发作消退** | 3 回合后 m 回落至基线（**发作自限性**）——区别于 PTSD 创伤触发的持续锁定 | 自限性 = 惊恐 vs PTSD 的核心机制分界 |
| **回避泛化** | 发作后 5 回合内，触发情境的相似情境 20% 概率触发预期性回避（e09 limbic gate 强制回避倾向） | 广场恐惧化轨迹（DSM-5 伴广场恐惧） |

### 5.3 组件掉落池

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **panic-disorder_e01, panic-disorder_e02, panic-disorder_e05, panic-disorder_e06, panic-disorder_e03** |
| 2（关联） | **panic-disorder_e04, panic-disorder_e07, panic-disorder_e09, panic-disorder_e11** |
| 1（边缘） | **panic-disorder_e08, panic-disorder_e10, panic-disorder_e12** |

> 核心 5 条 = 发作短路（e01/e02）+ 内感受误报环（e05/e06）+ NE 风暴（e03）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（惊恐） | m_offset | **轻/中/重三档**（CGI-S 3-7），\|m\| ≤ 0.6，m ∈ [0,1] 钳制 | §二 |
| 偏侧偏离量（惊恐） | laterality_delta | 0（全部边——无偏侧证据） | §二 |
| NE 基线偏离（惊恐） | ΔNE_baseline | +0.2（基线 0.3 → 0.5）；发作时瞬时 +0.3 | §三/§五.2 |
| 5HT 基线偏离（惊恐） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（惊恐） | bias_somatic / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]）——**惊恐独有 bias_somatic** | §三 |
| 内感受误报概率 | p_fp | 10%/回合（e05/e06/e07 m ≥ 0.2 时） | §五.1 |
| 发作触发条件 | — | e01 m ≥ 0.4（中档）或 误报计数 ≥ 2 | §五.2 |
| 发作时长 | t_attack | 3 回合（自限性） | §五.2 |
| 发作 NE 冲击 | ΔNE_attack | +0.3（δ_event，反射级） | §五.2 |
| 发作 SAN 损耗 | ΔSAN_attack | −3/回合 | §五.2 |
| 发作行动跳过概率 | p_skip | 40%/回合 | §五.2 |
| 回避泛化概率 | p_avoid | 20%（发作后 5 回合，相似情境） | §五.2 |
| 标签组合建议 | — | 敏化-威胁 + 抑制不足 | §三.0 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [广泛性焦虑障碍](../../../entities/diseases/%E5%B9%BF%E6%B3%9B%E6%80%A7%E7%84%A6%E8%99%91%E9%9A%9C%E7%A2%8D.md), [特定恐惧症](../../../entities/diseases/%E7%89%B9%E5%AE%9A%E6%81%90%E6%83%A7%E7%97%87.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §3.5/§4.2/§5.2, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §四/§七（焦虑障碍）, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
*待办: 疾病目录新建 [惊恐障碍](../../../entities/diseases/%E6%83%8A%E6%81%90%E9%9A%9C%E7%A2%8D.md)（父类 焦虑唤醒障碍，Q0.5）+ term_registry 入库（Q0.4 命名标准——DSM-5 命名 + disease_id=`panic-disorder`）*
