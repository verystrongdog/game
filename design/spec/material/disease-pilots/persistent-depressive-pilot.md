# 持续性抑郁障碍（恶劣心境，PDD）重映射试点

> Grilling #88 26 病重映射的第四份试点（抑郁症谱系新增病，Grilling #88 Q0.2 P2 扩种）。**纯文献驱动，无旧 `link_NNN` 文件**——本文件为 PDD 首次定义三体病理边集。DSM-5 命名：**持续性抑郁障碍（恶劣心境）Persistent Depressive Disorder (Dysthymia)**——抑郁心境持续 ≥2 年、多数日子存在，未达 MDD 大发作强度（或双重抑郁叠加时达）。三体模型上重映射为 **11 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），核心病理 = 慢性快感缺失（VTA→NAcc 解耦）+ 慢性 DMN 反刍（后扣带-楔前叶过度耦合，Wang 2013 恶劣心境 DMN 特异性）+ 慢性低能量（NE 内感受腿减弱）。**档位：CGI-S 3-6（建议，B′ 机械判定三档全——上限 6 非 <6）**；**偏侧：全边 laterality_delta = 0**（MDD 谱系 de Kovel 2019 null）。**与 MDD 的区分：慢性持续型（无急性跳变，改为持续消耗）**。7 参数推导与 NPC AI §5.2「反刍 + 过度抑制」标签组合（本文建议）交叉验证成立。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（11 条，含三体边核验列）](#二50-实体病理边表11-条含三体边核验列)
3. [PDD → 7 参数映射建议（4 tone + 3 CSTC）](#三pdd--7-参数映射建议4-tone--3-cstc)
4. [新增病说明与边集来源（无旧链路对照）](#四新增病说明与边集来源无旧链路对照)
5. [行为覆盖/非线性跳变保留清单（慢性持续型）](#五行为覆盖非线性跳变保留清单慢性持续型)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Wang et al. (2013)**（PMID [23389382](https://pubmed.ncbi.nlm.nih.gov/23389382/)，随机对照试验） | 静息态 DMN | **恶劣心境患者 DMN 过度连接，抗抑郁药（SSRI）治疗后正常化**——PDD 反刍的疾病特异性证据 → e04（PCC→precuneus DMN 核心）、e05（precuneus→mOFC 自我参照腿）的方向锚 |
| 2 | **ENIGMA MDD（Schmaal et al. 2016）** *Mol Psychiatry* 21(6):806-812 | 结构 meta | PDD 属 MDD 谱系慢性型：**海马↓（复发/慢性病程）**；亚皮层体积效应量 SZ>BD>MDD 梯度 → e06（PCC→海马 负性自传记忆提取）、e11（5-HT→海马）的慢性结构锚（量级 < MDD） |
| 3 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者） | 静息态 ALFF meta | 抑郁谱系共享：**ALFF↑ 岛叶/ACC-mPFC**（[疾病-脑区链路映射-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §2.1/§2.3）→ e10（rACC→insula）内感受/情绪耦合边 |
| 4 | **RDoC v4（NIMH）** | 回路矩阵 | 正性效价（奖赏评估/学习）：OFC、腹侧纹状体、VTA/SN → MDD/双相；负性效价（丧失）：DMN、海马、OFC、奖赏回路 → MDD（文献数据源 §四.1）→ 奖赏域（e01/e02）+ 反刍域（e04-e06）回路级锚 |

**辅助锚（方向/范围补充）**：

- **DSM-5 持续性抑郁障碍诊断标准**——慢性（≥2 年）、低能量/疲劳、注意力不集中、无望感、睡眠/食欲紊乱 → 行为覆盖锚（§五）与低能量边（e03/e09）的临床依据。
- **de Kovel et al. (2019)** *Am J Psychiatry*（ENIGMA MDD WG）——MDD 谱系无结构偏侧改变 → 全边 laterality_delta = 0。
- **Hamilton et al. (2015)**——抑郁 DMN 过度连接（NPC AI §4.2「反刍」标签文献锚）→ e04/e05 补充。
- **NPC AI 行为模型 §5.2**——「抑郁（反刍）：反刍 + 过度抑制 → 默认网络↑, 运动输出↓」→ 本文件标签组合建议（§三.2）的模板依据。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译；m 偏移量级参照 MDD 试点（[mdd-pilot.md](mdd-pilot.md)）降档（慢性低强度 ≈ MDD × 0.6~0.7），**全部数值有来源，新增数值标记 `[NEW]`**。PDD 为新增病，无旧文件设计校准值可继承——所有 m 为首次定义。

---

## 二、50 实体病理边表（11 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**11 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（PDD = `persistent-depressive`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围: 3-6` 过滤——B′ 机械判定：下限 3 非 >3 → 轻档可用；上限 6 非 <6 → 重档可用，三档全**；重档对应双重抑郁叠加或严重慢性期）。**设计定位：慢性持续型——所有边 m 绝对值 ≤ 0.3，重档不设急性跳变（见 §五.2）**。

### 2.1 奖赏域（3 条）——「慢性快感缺失」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **persistent-depressive_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | RDoC 正性效价（VTA→腹侧纹状体）；文献数据源 §七 MDD「VTA→NAcc 解耦」（PDD 为谱系慢性型）；慢性快感缺失（DSM-5） | 行为覆盖①（趋近·主动 效力 −50%）；3.1 节 DA_VTA 推导锚 |
| **persistent-depressive_e02** | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（privileged 孪生边 `prefrontal_limbic` feedback, level_diff=−4） | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | RDoC 正性效价（奖赏评估/预期：OFC→腹侧纹状体）；MDD 谱系奖赏评估减弱 | 3.1 节 bias_limbic 推导锚（负向） |
| **persistent-depressive_e03** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | DSM-5 低能量/疲劳；ENIGMA MDD 运动启动相关亚皮层↓（谱系共享） | 行为覆盖①（低能量侧翼） |

### 2.2 反刍域（3 条）——「慢性 DMN 过度耦合」（PDD 特异性核心）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **persistent-depressive_e04** ⭐核心 | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2 | **过度耦合** | 0/+0.2/+0.3 | 0 | **Wang et al. 2013（PMID:23389382）恶劣心境 DMN 过度连接**；Hamilton 2015 反刍 DMN | 行为覆盖②（慢性反刍消耗）；3.1 节 bias_cognitive 推导锚 |
| **persistent-depressive_e05** | precuneus | medialorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2083 | 过度耦合 | 0/+0.1/+0.2 | 0 | Wang 2013 DMN 过度连接（自我参照腿）；DSM-5 低自尊/无望感（自我参照负性加工） | 行为覆盖②（作用域成员） |
| **persistent-depressive_e06** | posteriorcingulate | Hippocampus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.378 | 过度耦合 | 0/+0.1/+0.2 | 0 | ENIGMA MDD 海马↓（慢性病程）；负性自传记忆过度提取（DSM-5 无望感锚） | 行为覆盖②（作用域成员） |

### 2.3 认知控制域（2 条）——「慢性注意/执行减弱」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **persistent-depressive_e07** | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | 0/−0.1/−0.2 | 0 | DSM-5 注意力集中困难；MDD 谱系认知控制域 dlPFC↓（文献数据源 §七） | 3.1 节 bias_cognitive 推导锚（机制侧） |
| **persistent-depressive_e08** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默 | 0/−0.1/−0.2 | 0 | DMN-FPN 反相关减弱（Ma 2019，MDD 谱系 trait marker）；慢性执行功能下降 | 行为覆盖③（L5 控制效力 −30%） |

### 2.4 内感受/唤醒域（2 条）——「慢性低能量 + 情绪-内感受耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **persistent-depressive_e09** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | DSM-5 低能量/疲劳（NE 驱动减弱）；与 PTSD（LC→insula 超敏）方向相反——抑郁谱系内感受钝化 | 3.1 节 NE tone 推导锚（负向腿） |
| **persistent-depressive_e10** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | 0/+0.1/+0.2 | 0 | Guo 2026 共享岛叶/ACC ALFF↑；情绪-内感受耦合（躯体不适主诉） | 行为覆盖②（作用域成员） |

### 2.5 记忆/5HT 域（1 条）——「5-HT→海马慢性传递」（SSRI 靶点）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **persistent-depressive_e11** | DorsalRapheNucleus | Hippocampus | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | **过度耦合** | 0/+0.1/+0.2 | 0 | Wang 2013 抗抑郁药（5-HT 机制）使恶劣心境 DMN 正常化 → 5-HT 系统参与；ENIGMA 海马慢性受累 | 3.1 节 5HT tone 推导锚 |

**图例**：⭐核心 = 本疾病核心机制边；全部 11 条为新增（无旧链路，但均命中现有三体边，非「病理新增」）；Δ 全 0 = MDD 谱系无偏侧证据（de Kovel 2019 null，§6.5 规则 2）。

---

## 三、PDD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD §三）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。**PDD 标签组合建议 = 「反刍 + 过度抑制」**（NPC AI §5.2「抑郁（反刍）」行直接复用；与 MDD 默认标签相同——区分在机制强度与跳变形态，见 §五）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0**（重档 −0.1） | e09（LC→insula 0/−0.1/−0.2 解耦） | LC 出边群命中且负偏移（内感受腿减弱）但**轻档 m=0** → 基线不变；重档 NE↓（慢性低能量显化）——与 PTSD（NE↑ 超敏）方向相反，抑郁谱系特征 |
| 2 | DA_VTA_baseline | **−0.1** | e01（VTA→NAcc −0.1/−0.2/−0.3 解耦） | VTA 出边群负偏移 → DA_VTA↓（慢性快感缺失，量级 < MDD 的 −0.2） |
| 3 | DA_SNc_baseline | **0** | e03（SNc→Putamen 0/−0.1/−0.2 解耦） | SNc 出边群轻档 m=0 → 基线不变（低能量由 NE 腿承载，非运动启动 tone 偏移） |
| 4 | 5HT_baseline | **+0.2** | e11（DR→Hippocampus 0/+0.1/+0.2 过度耦合） | 中缝核 5-HT 传递聚焦于记忆回路（SSRI 靶点，Wang 2013）→ 全局 5HT 基线↑（过度抑制：Crockett 2009 5HT↑ 行为抑制） |
| 5 | bias_somatic | **−0.15** | 无 somatic CSTC 环路边命中（e03 为脑干边） | 过度抑制标签校准（−0.15）；机制侧无 somatic 环路边 → 标签派生 [NEW 标注] |
| 6 | bias_cognitive | **+0.15** | e07（dlPFC→Caudate cognitive go_direct 命中 0/−0.1）、e04（DMN 反刍核心） | cognitive 环路边命中（解耦 = 控制失效）+ 反刍标签 → 认知行动倾向↑（慢性反刍占用，关不掉） |
| 7 | bias_limbic | **0** | e02（mOFC→NAcc limbic go_direct 解耦） | limbic 环路边命中但为负向（趋近↓）→ 默认 0（慢性快感缺失不以冲动趋近为特征） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2/§5.2：PDD 建议标签 = 「反刍 + 过度抑制」（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0（反刍 −0.1 vs 过度抑制 0，取 max → 0） | 0（e09 轻档 0；重档 −0.1） | ✅ |
| DA_VTA_baseline | 0（标签未覆盖） | −0.1（e01） | ⚠️ 幅值差 0.1——慢性快感缺失建议标签侧补「敏化-奖励(负)」或接受 0.1 幅值差（待数值校准）；方向一致（均 ≤0） |
| DA_SNc_baseline | 0 | 0（e03 轻档 0） | ✅ |
| 5HT_baseline | +0.2（过度抑制） | +0.2（e11） | ✅ |
| bias_somatic | −0.15（过度抑制） | −0.15（标签校准，无 somatic 环路边） | ✅（校准项） |
| bias_cognitive | +0.15（反刍） | +0.15（e07 命中 + e04 反刍核心） | ✅ |
| bias_limbic | 0 | 0（e02 负向） | ✅ |

**结论**：PDD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（6/7 ✅，DA_VTA 为 0.1 幅值校准项——慢性快感缺失在标签层缺显式表达，同 MDD 情形）。PDD NPC 最终参数：DA_VTA=0.3、5HT=0.7、bias_somatic=−0.15、bias_cognitive=+0.15（NE=0.3、DA_SNc=0.5、bias_limbic=0 基线）。**与 MDD NPC（DA_VTA=0.2）的差异：DA_VTA 高 0.1（慢性低强度）+ 无重档跳变（§五.2）——同一标签组合，靠边集量级与跳变形态区分。**

---

## 四、新增病说明与边集来源（无旧链路对照）

**PDD 为 Grilling #88 Q0.2 扩种的新增病（P2 优先级）**，无旧 `link_NNN` 文件、无 link_registry 条目可对照——本节替代「旧链路对照表」：

| 说明项 | 内容 |
|--------|------|
| DSM-5 命名 | **持续性抑郁障碍（恶劣心境）Persistent Depressive Disorder (Dysthymia)**；父类建议：奖赏系统障碍（Q0.5：奖赏系统 8→9，+恶劣心境） |
| CGI-S 范围 | **3-6**（建议初值；B′ 三档全——上限 6 非 <6；重档 = 双重抑郁叠加或严重慢性期） |
| 默认标签建议 | **反刍 + 过度抑制**（NPC AI §5.2「抑郁（反刍）」行；与 MDD 同标签，机制区分靠量级 + 跳变形态） |
| 边集来源 | 全部 11 条由文献直接驱动（§一锚点），**无旧链路语义继承**；量级 = MDD 试点降档（≈ ×0.6~0.7，见 §一转换规则声明） |
| 与 MDD 的边集差异 | ① 无 LC→ACC NE 腿（PDD 唤醒域不设正耦合）；② LC→insula 方向为**解耦**（慢性低能量，非超敏）；③ 无 Pallidum 行动门控边（PDD 无显著运动门控损害）；④ 新增 PCC→海马（慢性负性自传记忆）；⑤ 无 DMN-FPN 边界负向边之外的整合边（慢性弱化而非崩溃，量级差） |
| 与环性心境的边集差异 | ① 无奖赏超敏腿（mOFC→NAcc 为解耦而非过度耦合——PDD 无 BSD 超敏）；② 无壳核-丘脑特异性（Haznedar 为环性专属）；③ 无 SMN 气质边；④ 反刍域量级更高（DMN 过度耦合 0/+0.2/+0.3 vs 环性 0/+0.1/—） |
| 校验警告 | 无（新增病首次定义，不触发「父类方向无链路」类旧警告） |

**谱系梯度核对**（三病同域边量级对比，保证谱系内一致性）：

| 同域边 | MDD | PDD | 环性心境 |
|--------|:---:|:---:|:---:|
| VTA→Accumbens-area 解耦 | −0.1/−0.3/−0.5 | −0.1/−0.2/−0.3 | −0.1/−0.2/— |
| PCC→precuneus 过度耦合 | +0.1/+0.3/+0.4 | 0/+0.2/+0.3 | 0/+0.1/— |
| rACC→insula 过度耦合 | +0.1/+0.2/+0.3 | 0/+0.1/+0.2 | 0/+0.1/— |
| dlPFC→Caudate 解耦 | −0.1/−0.2/−0.3 | 0/−0.1/−0.2 | 0/−0.1/— |

---

## 五、行为覆盖/非线性跳变保留清单（慢性持续型）

### 5.1 行为覆盖（PDD 首定义，无旧条目——照 MDD 模板格式新建）

| 条件 | 约束 | 挂接 | 说明 |
|------|------|--------|------|
| 奖赏域边群 m_max > 0.2（e01/e02/e03） | 趋近·主动 效力 −50%（非禁用——慢性低强度） | **奖赏域边群** | 与 MDD 的「|m|>0.4 完全禁用」区分：PDD 慢性弱化而非急性失效 |
| 反刍域边群 m_max > 0.3（e04/e05/e06） | 每回合 SAN −1（反刍消耗，**持续型**） | **反刍域边群** | 与 MDD 的「m_max>0.5 触发」区分：PDD 阈值更低、无跳变（持续消耗） |
| 认知控制域 e08 \|m\| > 0.2 | L5 控制·主动 对 L0-L2 压制效力 −30% | **persistent-depressive_e08** | 慢性执行弱化（vs MDD 边界崩溃的 SN 切换延迟） |
| 内感受域 e09 \|m\| > 0.2 | 感知通道·内感受 灵敏度 −30%（低能量钝化） | **persistent-depressive_e09** | 与 PTSD 的内感受过度警觉相反 |

### 5.2 非线性跳变

**无（设计决策）**——PDD 为**慢性持续型**疾病：无急性发作、无阈值跳变。与 MDD（趋近禁用/反刍跳窗/SN 切换延迟三重跳变）、环性（无跳变但含振荡）的区分：

| 谱系 | 跳变形态 | 机制表达 |
|------|---------|---------|
| MDD（3-7） | 急性阈值跳变（m_th 0.2~0.5） | 趋近禁用/物理 −20%/反刍跳窗/SN 延迟 |
| PDD（3-6） | **无跳变，持续消耗** | SAN 持续 −1/回合 + 效力衰减（−50%/−30%） |
| 环性（2-4） | 无跳变，振荡 | ±0.05 m 时变 + 动作随机化 5% |

> 若 PDD 进入重档（双重抑郁叠加，CGI 6），**建议**临时启用 MDD 跳变表（§五.2 mdd）——作为「双重抑郁」的叠加规则 [待 #88 定案]，本试点不预设。

### 5.3 组件掉落池（PDD 首定义）

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **persistent-depressive_e01, persistent-depressive_e04** |
| 2（关联） | persistent-depressive_e02, e03, e05, e06, e07, e10 |
| 1（边缘） | persistent-depressive_e08, e09, e11 |

> 核心 2 条 = 慢性快感缺失（e01）+ 慢性 DMN 反刍（e04，PDD 特异性 Wang 2013）；边缘含内感受钝化（e09）与 5-HT 记忆腿（e11）。权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（PDD） | m_offset | 11 条，三档全（CGI-S 3-6 建议，B′），\|m\| ≤ 0.3 | §二（pathology_edges.json §6.1） |
| 偏侧偏离量（PDD） | laterality_delta | **全边 0**（MDD 谱系 de Kovel 2019 null，§6.5 规则 2） | §二 |
| NE 基线偏离（PDD） | ΔNE_baseline | 0（基线 0.3；重档 −0.1 慢性低能量） | §三 |
| DA_VTA 基线偏离（PDD） | ΔDA_VTA_baseline | −0.1（基线 0.4 → 0.3；慢性快感缺失） | §三 |
| 5HT 基线偏离（PDD） | Δ5HT_baseline | +0.2（基线 0.5 → 0.7；过度抑制） | §三 |
| CSTC 偏置（PDD） | bias_somatic / bias_cognitive / bias_limbic | −0.15 / +0.15 / 0（值域 [−0.3,+0.3]） | §三 |
| 慢性反刍 SAN 消耗阈值 | m_th | 0.3（e04-e06 m_max，SAN −1/回合，持续型） | §五.1 |
| 趋近·主动效力衰减 | — | 奖赏域 m_max > 0.2 → −50%（非禁用） | §五.1 |
| L5 压制效力衰减 | — | e08 \|m\| > 0.2 → −30% | §五.1 |
| 双重抑郁叠加规则 | — | PDD 重档（CGI 6）→ 临时启用 MDD 跳变表 [待 #88] | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [mdd-pilot.md](mdd-pilot.md), [cyclothymia-pilot.md](cyclothymia-pilot.md), [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [偏侧化架构](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §二/§四/§七, [ENIGMA偏侧化-精神疾病大样本meta-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md), [tripartite_model.json](../../../data/connectivity/tripartite_model.json), [Wang et al. 2013（PMID 23389382）](https://pubmed.ncbi.nlm.nih.gov/23389382/)*
