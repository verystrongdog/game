# 持续性心境障碍（环性心境）重映射试点

> Grilling #88 26 病重映射的第三份试点（抑郁症谱系，与 PTSD 试点同格式）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **9 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），每条含 `{source, target, 边类型, 病理类型, m偏移(轻/中/重), laterality_delta, 文献依据, 行为覆盖挂接}`。核心病理 = 奖赏域双相振荡（VTA→NAcc 轻度解耦 × mOFC→NAcc 奖赏超敏交替）+ 行动门控域壳核-丘脑 relay 减弱（Haznedar 特异性）+ 轻度 DMN 反刍。**档位：CGI-S 2-4 → 无重档（B′ 过滤）**；**偏侧：全边 laterality_delta = 0**（无独立偏侧证据，Gordon 2010 MDD 右偏仅趋势、不作机制）。7 参数推导与 NPC AI §5.2「敏化-奖励 + 反刍」标签组合全部一致——敌我同构闭环成立。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（9 条，含三体边核验列）](#二50-实体病理边表9-条含三体边核验列)
3. [环性心境 → 7 参数映射建议（4 tone + 3 CSTC）](#三环性心境--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Haznedar et al. (2005)** *Biol Psychiatry*（16 环性 vs 36 HC） | 结构 | **壳核 + 丘脑体积↓（区别于 BD I/II 的特征）**；前额叶灰质↓（BA12+BA32，OFC/扣带前缘）（[疾病-脑区链路映射-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七环性心境）→ e05（Putamen→Thalamus relay 减弱）、e08（dlPFC 轻度↓）的结构锚 |
| 2 | **Damme et al. (2022)** *JCPP Advances* | 结构/功能 | **mOFC/NAcc 体积↑（BSD 谱系，male-specific d≈1.01）**——奖励超敏模型 → e07（mOFC→NAcc 过度耦合）⭐新增依据 |
| 3 | **文献数据源 §七 环性心境** | 汇总 | 奖赏敏感性↑（奖励超敏模型 BSD 谱系共享）；**SMN 内在活动↑ 与 cyclothymic temperament 正相关**；认知控制域 dlPFC↓ 轻度（效应量 < BD-I）→ e09（SMN）、e08（dlPFC）、e01/e07（奖赏域） |
| 4 | **RDoC v4（NIMH）** | 回路矩阵 | 正性效价（奖赏评估/预期/学习）：OFC、腹侧纹状体、VTA/SN → MDD/双相/成瘾（文献数据源 §四.1）→ 奖赏域边集（e01/e07）回路级锚 |

**辅助锚（方向/范围补充）**：

- **Gordon, Palmer & Cooper (2010)** *Clin EEG Neurosci*——六病同测 EEG alpha 偏侧：MDD 右偏仅趋势水平；[左右脑偏侧化-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八：**MDD 偏侧证据弱，谨慎不作核心机制** → 环性心境全边 laterality_delta = 0。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——6 条旧链路的方向/量级/通路描述（Hansen 2024 / Paxinos 2004 / ENIGMA / Alexander 1986 CSTC）作为语义继承源，见 §四。
- **MDD 试点（[mdd-pilot.md](mdd-pilot.md)）**——抑郁谱系共享边（VTA→NAcc 解耦、DMN 反刍）在此降档复用，保证谱系内量级梯度（MDD > 环性）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译；m 偏移量级沿用旧文件设计校准值（环性 = MDD × 0.5~0.7 梯度 + BD-II × 0.5 推导），**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（9 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**9 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（环性心境 = `cyclothymia`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围: 2-4` 过滤——B′ 定案：上限 4 < 6 → 无重档**，重档显示为「—」；轻档可用（下限 2 非 >3））。轻症设计：所有 m 绝对值 ≤ 0.2，不设重度跳变。

### 2.1 奖赏域（3 条）——「奖赏超敏 × 轻度解耦 振荡」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **解耦沉默** | −0.1/−0.2/— | 0 | 旧 link_336（VTA→NAcc，Schultz 1997 fc=0.9）降档（< MDD 的 −0.1/−0.3/−0.5）；奖赏域抑郁相 | 行为覆盖①（奖赏域振荡作用域） |
| **cyclothymia_e07** ⭐新增 | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（privileged 孪生边 `prefrontal_limbic` feedback, level_diff=−4） | **过度耦合** | 0/+0.1/— | 0 | Damme 2022 mOFC/NAcc 体积↑（d≈1.01, male）；奖励超敏模型 BSD 谱系共享（文献数据源 §七） | 行为覆盖①（奖赏域振荡作用域）；3.1 节 bias_limbic / DA_VTA 推导锚 |
| **cyclothymia_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/— | 0 | 旧 link_344（SNc→Putamen，Paxinos 2004 fc=0.85）降档；运动启动轻度不稳 | 行为覆盖②（动作随机化作用域） |

### 2.2 行动门控域（1 条）——「壳核-丘脑 relay 减弱」（环性特异性）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e05** ⭐核心 | Putamen | Thalamus-Proper | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.603（CSTC 基底节 relay 的 CC 表达） | 解耦沉默（旧「结构异常」） | −0.1/−0.2/— | 0 | 旧 link_363（壳核→丘脑，Alexander 1986 CSTC PMID:3085570）；Haznedar 2005 壳核+丘脑体积↓（环性区别于 BD I/II） | 行为覆盖②（动作选择随机化 5%）；bias 推导辅助 |

### 2.3 反刍域（2 条）——「轻度 DMN 过度耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e06** | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2 | **过度耦合** | 0/+0.1/— | 0 | 旧 link_131_L（PCC→mPFC，ENIGMA 9.76）语义转移 + 降档（PCC→mPFC 无直连 → DMN 核心边）；反刍倾向（标签） | 3.1 节 bias_cognitive 推导锚（反刍侧） |
| **cyclothymia_e04** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | 0/+0.1/— | 0 | 旧 link_155_L（rACC→insula，ENIGMA 6.29）降档；情绪-内感受轻度耦合（Guo 共享 ALFF↑ 轻症表达） | 行为覆盖①（作用域成员） |

### 2.4 唤醒域（1 条）——「蓝斑振荡（不达 BD/GAD）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e03** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | **过度耦合** | 0/+0.1/— | 0 | 旧 link_332（蓝斑→杏仁核 NE，Hansen 2024 fc=0.7）；唤醒域轻度↑（蓝斑不稳定，< GAD/BD，文献数据源 §七） | 3.1 节 NE tone 推导锚（振荡承载） |

### 2.5 认知控制域（1 条）——「dlPFC 轻度↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e08** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | 0/−0.1/— | 0 | Haznedar 2005 前额叶灰质↓（BA12+BA32）；文献数据源 §七 认知控制域 dlPFC↓ 轻度（< BD-I） | 3.1 节 bias_cognitive 推导锚（机制侧） |

### 2.6 感觉运动域（1 条）——「SMN 内在活动↑」（气质相关，装饰层）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **cyclothymia_e09** ⭐新增 | precentral | postcentral | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.759 | 过度耦合 | 0/+0.1/— | 0 | SMN 内在活动↑ 与 cyclothymic temperament 正相关（文献数据源 §七环性心境） | 组件掉落池边缘权重（气质 trait，非核心机制） |

**图例**：⭐核心/⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 全 0 = 无独立偏侧证据（Gordon 2010 仅趋势、MDD 偏侧弱 §八，§6.5 规则 2）。

---

## 三、环性心境 → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD §三）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。环性默认标签 = 「敏化-奖励 + 反刍」（疾病文件）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0** | e03（LC→Amygdala 0/+0.1 过度耦合） | LC 出边群命中但轻档 m=0 → tone 基线不变；**蓝斑振荡（每 5 回合 ±0.05 m 调整，旧行为覆盖①）由边 m 时变承载，非 tone 基线偏移**——「不稳定」≠「上调」 |
| 2 | DA_VTA_baseline | **+0.2** | e07（mOFC→NAcc 过度耦合 0/+0.1）、e01（VTA→NAcc 解耦 −0.1/−0.2） | VTA 出边群混合（e07 正 = 奖赏超敏腿，e01 负 = 抑郁相腿）；主导方向 = 奖赏敏感性↑（Damme d≈1.01 + 敏化-奖励标签）→ DA_VTA↑；e01 为振荡负相（每 5 回合回落） |
| 3 | DA_SNc_baseline | **0** | e02（SNc→Putamen 0/−0.1 解耦） | SNc 出边群轻档 m=0 → 基线不变（运动启动轻度不稳经 e05 relay 承载，非 tone 偏移） |
| 4 | 5HT_baseline | **−0.2** | 无 DR 出边群命中 | 纯标签校准（敏化-奖励：5HT −0.2，Robinson & Berridge 1993 敏化）——**无脑干 5HT 边群命中，[NEW] 标注：由标签派生，机制侧待补 DR 边或接受标签校准** |
| 5 | bias_somatic | **0** | 无 somatic CSTC 环路边群命中（e05 为 CC 边非 CSTC 环路边） | 躯体 gate 无结构性偏置（环性不以运动抑制/激发为特征） |
| 6 | bias_cognitive | **+0.15** | e08（dlPFC→Caudate cognitive go_direct 命中 0/−0.1） | cognitive 环路边命中（轻度解耦）+ 反刍标签 → 认知行动倾向↑（轻度反刍占用） |
| 7 | bias_limbic | **+0.15** | e07（mOFC→NAcc limbic go_direct 过度耦合 正） | limbic 环路边命中且 m 正偏移 → 情绪/本能行动倾向↑（冲动趋近） |

> **注（5HT 校准）**：环性心境 7 参数中唯一无脑干边群支撑的 tone。两选项：① 接受标签校准（−0.2，当前选择，文档标注）；② 增补 DR→Amygdala 边（5HT 情绪调制，0/+0.1 过度耦合）——但正偏移 DR 边与 −0.2 标签方向冲突，故不增补，维持「标签校准 + 待数值校准」。

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2/§5.2：环性心境 = 「敏化-奖励 + 反刍」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0（反刍 −0.1 vs 敏化-奖励 0，取 max → 0） | 0（e03 轻档 0，振荡时变） | ✅ |
| DA_VTA_baseline | +0.2（敏化-奖励） | +0.2（e07 主导） | ✅ |
| DA_SNc_baseline | 0 | 0（e02 轻档 0） | ✅ |
| 5HT_baseline | −0.2（敏化-奖励） | −0.2（标签校准，无 DR 边群） | ✅（校准项） |
| bias_somatic | 0 | 0（无 somatic 环路边） | ✅ |
| bias_cognitive | +0.15（反刍） | +0.15（e08 命中 + 反刍） | ✅ |
| bias_limbic | +0.15（敏化-奖励） | +0.15（e07 正偏移） | ✅ |

**结论**：环性心境病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（7/7 ✅，5HT 为标注校准项）。环性 NPC 最终参数：DA_VTA=0.6、5HT=0.3、bias_cognitive=+0.15、bias_limbic=+0.15（NE=0.3、DA_SNc=0.5、bias_somatic=0 基线）。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 解耦沉默 −0.1/−0.2/−0.2 | **cyclothymia_e01**（VentralTegmentalArea→Accumbens-area） | ✅ 保留语义（fid 合并；量级按 B′ 去重档 → −0.1/−0.2/—） |
| link_344 | SNc→Putamen | 解耦沉默 0/−0.1/−0.1 | **cyclothymia_e02**（SubstantiaNigraParsCompacta→Putamen） | ✅ 保留语义（去重档 → 0/−0.1/—） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 0/+0.1/+0.1 | **cyclothymia_e03**（LocusCoeruleus→Amygdala） | ✅ 保留语义（去重档 → 0/+0.1/—） |
| link_155_L | rACC→Insula | 过度耦合 0/+0.1/+0.1 | **cyclothymia_e04**（rostralanteriorcingulate→insula） | ✅ 保留语义 + 偏侧显式化（_L 废弃 → Δ=0） |
| link_363 | Putamen→Thalamus | 结构异常 −0.1/−0.2/−0.2 | **cyclothymia_e05**（Putamen→Thalamus-Proper） | ✅ 保留量级 + **类型重校准**：旧「结构异常」（体积数据，新 §6.3 仅限病理新增边/脑干广播腿负偏移）→ 体积↓ 的机制表达 = relay 信号减弱 = 「解耦沉默」（去重档 → −0.1/−0.2/—） |
| link_131_L | PosteriorCingulate→SuperiorFrontalMPFC | 过度耦合 0/+0.1/+0.1 | **cyclothymia_e06**（posteriorcingulate→precuneus） | ⚠️ **废弃直连**（三体图无 PCC→mPFC 边）；语义转移至 DMN 核心边 + 降档 |
| （旧表无） | mOFC→NAcc 奖赏超敏（Damme 2022 d≈1.01） | — | **cyclothymia_e07** | ⭐ 新增——bias_limbic / DA_VTA 机制锚 |
| （旧表无） | dlPFC→Caudate 认知门控轻度↓（Haznedar 2005 前额叶灰质↓） | — | **cyclothymia_e08** | ⭐ 新增——bias_cognitive 机制锚 |
| （旧表无） | M1↔S1 SMN 内在活动↑（cyclothymic temperament） | — | **cyclothymia_e09** | ⭐ 新增——气质 trait（边缘权重） |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在（link_131_L）→ **语义转移优先**；「病理新增」从严——0 条。类型重校准 1 处（link_363 结构异常→解耦沉默）。**已知校验警告保留**：旧文件「整合域无链路（CGI-S 上限 4，未达受累阈值）」——新格式同样无 DMN-FPN 边界边（mdd_e07 类）纳入，为设计决策（轻症不累及整合域）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 净方向（每 5 回合检查）→ 轻度振荡（±0.05 m 调整）——不足以切换行为覆盖 | ✅ 保留 | **奖赏域边群**（e01/e07，作用域） | 「奖赏域」在新格式 = 奖赏域病理边集；振荡 = e01（抑郁相负）与 e07（超敏正）的净方向时变 |
| 行动门控域 \|m\| > 0.2 → 动作选择随机化 5%——决策不稳定 | ✅ 保留（改挂接） | **cyclothymia_e05** \|m\| ≥ 0.2 | 同义替换（壳核-丘脑 relay 减弱 → 决策不稳定）；旧阈值「>0.2」与中档 |m|=0.2 在严格不等号下不可达——边界语义（≥ vs >）随旧文件继承，[待 #88 数值校准] 统一为 ≥ 0.2 |

### 5.2 非线性跳变

**无**（旧文件无「非线性跳变」表）。设计说明：环性心境 CGI-S 上限 4（无重档，B′），所有 m 偏移 ≤ 0.2，**不设重度跳变**——轻症以「振荡 + 随机化」表达不稳定性，而非 MDD/BD 的阈值跳变。跳变机制为 MDD（§五.2 mdd）与 BD 的专属设计。

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_363 | **cyclothymia_e01, cyclothymia_e05** |
| 2（关联） | link_344, link_332, link_155_L, link_131_L | **cyclothymia_e02, cyclothymia_e03, cyclothymia_e04, cyclothymia_e06, cyclothymia_e07, cyclothymia_e08** |
| 1（边缘） | （旧无） | **cyclothymia_e09** |

> 核心 2 条 = 奖赏域振荡核心（e01）+ 环性特异性壳核-丘脑（e05）；新增边 e07/e08 落关联、e09 落边缘（气质 trait）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（环性） | m_offset | 9 条，**无重档**（CGI-S 2-4，B′：上限 4 < 6），\|m\| ≤ 0.2 | §二（pathology_edges.json §6.1） |
| 偏侧偏离量（环性） | laterality_delta | **全边 0**（无独立偏侧证据，§6.5 规则 2） | §二 |
| NE 基线偏离（环性） | ΔNE_baseline | 0（振荡 ±0.05 由边 m 时变承载） | §三 |
| DA_VTA 基线偏离（环性） | ΔDA_VTA_baseline | +0.2（基线 0.4 → 0.6；奖赏超敏） | §三 |
| 5HT 基线偏离（环性） | Δ5HT_baseline | −0.2（标签校准，无 DR 边群 [NEW]） | §三 |
| CSTC 偏置（环性） | bias_cognitive / bias_limbic | +0.15 / +0.15（bias_somatic 0；值域 [−0.3,+0.3]） | §三 |
| 奖赏域振荡周期 | T_osc | 5 回合（±0.05 m 调整） | §五.1 |
| 动作随机化阈值 | m_th | 0.2（e05，随机化 5%） | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [持续性心境障碍](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E6%8C%81%E7%BB%AD%E6%80%A7%E5%BF%83%E5%A2%83%E9%9A%9C%E7%A2%8D.md), [mdd-pilot.md](mdd-pilot.md), [NPC AI 行为模型](../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [偏侧化架构](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §二/§三/§四/§七, [左右脑偏侧化-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八, [tripartite_model.json](../../../data/connectivity/tripartite_model.json)*
