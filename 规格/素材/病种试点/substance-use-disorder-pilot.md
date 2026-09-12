# 物质使用障碍（SUD）重映射试点

> 26 病重映射第 2 份试点（照 [PTSD 试点](ptsd-pilot.md) §六 字段规范复制）。本文件把旧 `link_336/344/343/008_L/328/363/155_L/003_L` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **13 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **奖赏域双相状态**（VTA→NAcc 急性↑/戒断↓，net 解耦沉默）+ **习惯化壳核**（Putamen→Thalamus 过度耦合）+ **认知控制域↓**（认知 CSTC 环路 dlPFC→Caudate 解耦，替代不存在的 ACC→dlPFC 直连）。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §4.2/§5.2 标签组合「敏化-奖励 + 抑制不足」交叉验证：DA_VTA 因「急性敏化 vs 戒断耗竭」双相经**状态分离裁决**取敏化侧（Robinson & Berridge 1993 激励敏化——wanting 高而 liking 低），bias_cognitive −0.15 为**标签缺口裁决**（6 标签无"认知↓"标签，补 NPC AI 行为模型缺口）。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（新格式试点行，含三体边核验列）](#二50-实体病理边表新格式试点行含三体边核验列)
3. [SUD → 7 参数映射建议（4 tone + 3 CSTC）](#三sud--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Navarri et al. (2022)** *Hum Brain Mapp*（ENIGMA AUD/CUD） | 结构 mega | AUD: 丘脑↓/海马↓/杏仁核↓/NAcc↓（效应量 ≥ 精分）、皮质厚度↓ 梭状回/颞下回/额上回/ACC；CUD: 杏仁核↓/NAcc↓/海马↓/**mOFC↓** → 奖赏域结构性耗竭（NAcc↓ → e01；杏仁核↓ → e11）+ 认知域额叶变薄（e08 结构异常）的形态学锚；**海马/丘脑↓** 为奖赏-习惯环结构性背景（不设独立海马/丘脑病理边——SUD 无 PTSD 式情景闪回，丘脑经 e04 壳核-丘脑习惯环承载） |
| 2 | **Dugré et al. (2023)** *Addict Biol*（96 研究） | 功能连接 meta | **vmPFC-腹侧纹状体 超连接** + **dlPFC-ACC/岛叶 低连接** + CSTC 环路 disrupted → e05 过度耦合（bias_limbic 锚）+ e06/e07/e09 解耦（认知/内感受域↓）方向锚 |
| 3 | **Klugah-Brown et al. (2023)** *Neurosci Biobehav Rev*（99 fMRI 研究） | 跨物质 meta | 所有物质共享：**背侧纹状体+前额叶**回路异常（奖赏/突显/习惯/执行控制）→ 壳核习惯化（e04）+ 纹状体-前额叶边群（e05/e06/e07/e13）覆盖范围锚 |
| 4 | **Robinson & Berridge (1993)** 激励敏化理论 | 理论 | 药物线索 → DA 系统**敏化**（wanting 超敏）→ NPC 侧 DA_VTA +0.2 的敏化侧锚；戒断/慢性期 DA 耗竭 → 病理边 net 负方向锚（**状态分离裁决**的文献基础） |

**辅助锚（方向/范围补充）**：

- **Everitt & Robbins (2005)**——奖赏从腹侧纹状体（目标导向）→ 背侧纹状体（习惯）迁移 → e04 壳核习惯化 + e13 precentral→Putamen 动作自动化的环路级锚。
- **Koob & Le Moal（负强化/"dark side"）**——戒断期负性情绪状态经**杏仁核-纹状体**回路驱动渴求 → e11（Amygdala→Accumbens-area）戒断期跳变作用域锚。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——8 条旧链路的方向/量级/通路描述（Schultz1997 / Paxinos2004 / Hansen2024 / Alexander1986_CSTC / ENIGMA 连接强度）作为语义继承源，见 §四。
- **NPC AI §4.2**——标签「敏化-奖励」（DA_VTA +0.2, 5HT −0.2, bias_limbic +0.15）与「抑制不足」（5HT −0.2, bias_somatic +0.15）；§5.2「躁狂」行 = 同标签组合先例（VTA→NAcc ↑, dlPFC 抑制 ↓）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准（link_336 等），新增数值标记 `[NEW]`。SUD 的「急性↑/戒断↓」双相状态由**边 net 方向（戒断耗竭侧）+ 行为覆盖跳变（中毒期侧）**双通道表达（§5.1）。

---

## 二、50 实体病理边表（新格式试点行，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**13 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。旧 `link_008_L`（ACC→dlPFC）在 tripartite 图中**无直连边**（rostralmiddlefrontal↔caudalanteriorcingulate 不在 1049 集合内）→ 按 §六.4 **语义转移优先**：认知控制域↓由认知 CSTC 环路（dlPFC→Caudate / ACC→Caudate）承载。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（SUD = `substance-use-disorder`，主键前缀 `sud`）。三档 m 偏移 = 轻/中/重（frontmatter `CGI-S范围: 3-7` → 档位过滤 B′ 三档全）。laterality_delta 全部 0：ENIGMA AUD/CUD 与 Klugah-Brown 均未报告稳健偏侧效应（旧 `_L` 后缀为 ENIGMA 单半球数据点，非偏侧证据——按 #92 合并双侧节点，不设 Δ）。

### 2.1 奖赏域（4 条）——「VTA→NAcc 急性↑/戒断↓」双相核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（中脑边缘 DA 通路） | **解耦沉默**（net 戒断侧；急性期过度耦合见挂接） | −0.1/−0.3/−0.5 | 0 | 旧 link_336（VTA→NAcc，fc=0.9，Schultz1997）；ENIGMA NAcc↓（Navarri 2022）；Robinson & Berridge 1993 | 行为覆盖①②（中毒/戒断双相跳变） |
| **sud_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast（黑质纹状体 DA 通路） | 解耦沉默 | 0/−0.2/−0.3 | 0 | 旧 link_344（SNc→壳核，fc=0.85，Paxinos2004） | 行为覆盖①（戒断期作用域） |
| **sud_e03** | SubstantiaNigraParsCompacta | Caudate | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | 旧 link_343（SNc→尾状核，fc=0.9，Paxinos2004） | 行为覆盖①（戒断期作用域） |
| **sud_e05** ⭐新增 | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（privileged `prefrontal_limbic` L5→L1 孪生存在） | **过度耦合** | +0.2/+0.3/+0.4 | 0 | Dugré 2023（vmPFC-腹侧纹状体 超连接）；Klugah-Brown 2023 纹状体-前额叶 | 3.1 节 bias_limbic 推导锚 |

### 2.2 习惯化/行动门控域（2 条）——「壳核习惯锁定」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e04** | Putamen | Thalamus-Proper | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.603 | **过度耦合** | +0.1/+0.3/+0.4 | 0 | 旧 link_363（壳核→丘脑，CSTC 直接通路，Alexander1986；Haber2010）；Everitt & Robbins 2005 习惯化 | 非线性跳变①（习惯锁定） |
| **sud_e13** ⭐新增 | precentral | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Everitt & Robbins 2005（动作自动化）；Klugah-Brown 2023 背侧纹状体习惯回路 | 3.1 节 bias_somatic 推导锚；非线性跳变①（M1 强制熟练） |

### 2.3 认知控制域（2 条）——「dlPFC↓ 冲动控制失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e06** ⭐转移 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | −0.1/−0.3/−0.5 | 0 | 旧 link_008_L（ACC→dlPFC 解耦）**语义转移**（直连不在三体图，cognitive 环路承载）；Dugré 2023 dlPFC-ACC 低连接 | 行为覆盖③ + 非线性跳变②（dlPFC 压制失效） |
| **sud_e07** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=feedback, level_diff=−1, edr=0.5807 存在） | 解耦沉默 | 0/−0.2/−0.3 | 0 | Dugré 2023（dlPFC-ACC 低连接，ACC 侧语义）；ENIGMA AUD 皮质厚度↓ ACC（Navarri 2022） | 行为覆盖③（认知压制−50% 作用域） |

### 2.4 唤醒/结构域（1 条）——「LC→dlPFC 结构受损」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e08** | LocusCoeruleus | rostralmiddlefrontal | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | **结构异常** | 0/−0.2/−0.3 | 0 | 旧 link_328（LC→dlPFC NE，fc=0.75，Hansen2024）；ENIGMA AUD 额上回/额叶皮质变薄（Navarri 2022） | 行为覆盖③ + 非线性跳变②（结构基础） |

### 2.5 内感受域（1 条）——「岛叶解耦」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e09** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.4246 | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_155_L（ACC吻侧→前脑岛）；Dugré 2023 dlPFC-岛叶低连接（内感受侧语义） | 行为覆盖④（内感受错误归因） |

### 2.6 记忆/情绪域（2 条）——「物质情境记忆 + 戒断期负性情绪」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e10** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：CC, dir=feedback, level_diff=−1, edr=0.2939 | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89）；物质相关情境记忆线索化 | 行为覆盖①（物质线索侧翼） |
| **sud_e11** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=lateral, edr=0.5893 存在） | 过度耦合 | 0/+0.1/+0.2 | 0 | ENIGMA AUD/CUD 杏仁核↓（Navarri 2022，结构）；Koob & Le Moal 戒断期负性情绪→渴求（"dark side" 杏仁核-纹状体回路） | 非线性跳变③（戒断期渴求） |

### 2.7 调制域（1 条）——「5HT 广播↓ → 冲动去抑制」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **sud_e12** ⭐新增 | DorsalRapheNucleus | caudalanteriorcingulate | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | Soubrié (1986) 低 5HT=去抑制；SUD 冲动性-5-HT 功能低下文献群 | 3.1 节 5HT tone 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；⭐转移 = 旧链路直连在三体图不存在，按 §六.4 语义转移至同功能域现有边；Δ = 0（无稳健偏侧证据：ENIGMA AUD/CUD 未报告偏侧效应；旧 `_L` 后缀为 ENIGMA 单半球数据点，按 #92 合并双侧节点）。

---

## 三、SUD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD 模板 §六.6）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。SUD 的**状态分离裁决**（[NEW]，见 3.3）：双相状态疾病（急性↑/戒断↓）的 NPC 参数取**行为表型侧**（敏化），病理边 m 取**慢性耗竭侧**（戒断），两者经行为覆盖跳变衔接。

### 3.1 从病理边推导

| # | 参数 | 偏离值（边推导） | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0** | e08（LC→dlPFC 结构异常） | LC 出边群唯一命中为**结构异常**（投射腿受损，§6.3 规则(b) 非全局 tone 变化）→ 不驱动 NE tone |
| 2 | DA_VTA_baseline | **−0.2**（耗竭侧） | e01（VTA→NAcc 解耦 net） | VTA 出边群净负（戒断耗竭）→ 按 §6.6 规则 1 推导为 −0.2；**但 NPC 参数取敏化侧 +0.2**（状态分离裁决，3.2/3.3） |
| 3 | DA_SNc_baseline | **−0.1**（耗竭侧） | e02（SNc→Putamen）、e03（SNc→Caudate） | SNc 出边群双负（0/−0.2/−0.3 + 0/−0.1/−0.2）→ 边推导 −0.1；NPC 参数取 0（状态分离裁决） |
| 4 | 5HT_baseline | **−0.2** | e12（DR→ACC 解耦） | 中缝核 5-HT 广播↓ → 冲动去抑制（Soubrié 1986）；与「抑制不足」标签同向 |
| 5 | bias_somatic | **+0.15** | e13（precentral→Putamen somatic GO 过度耦合） | 习惯化动作执行 gate 无法关闭 → 躯体行动倾向↑ |
| 6 | bias_cognitive | **−0.15** [NEW 标签缺口] | e06（dlPFC→Caudate）、e07（ACC→Caudate）解耦 | 认知 CSTC 环路双负 → 语言/认知行动 salience↓ → 冲动物理行动主导 |
| 7 | bias_limbic | **+0.15** | e05（mOFC→NAcc limbic GO 过度耦合）、e11（Amygdala→NAcc） | 边缘环路 gate 被奖赏线索劫持 → 情绪/本能趋近倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-奖励」+「抑制不足」双标签（多标签叠加取最大值，clamp 值域；§5.2「躁狂」行同组合先例）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0 | 0（e08 结构异常不驱动 tone） | ✅ |
| DA_VTA_baseline | +0.2（敏化-奖励） | −0.2（e01 戒断耗竭侧） | ⚠️ **状态分离裁决**：NPC 取 +0.2（敏化侧——线索 wanting 超敏，Robinson & Berridge 1993）；病理边 net 取 −（戒断耗竭）；经行为覆盖①跳变衔接 |
| DA_SNc_baseline | 0 | −0.1（e02/e03 戒断侧） | ⚠️ **状态分离裁决**：NPC 取 0（标签侧） |
| 5HT_baseline | −0.2（双标签） | −0.2（e12 解耦） | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15（e13 过度耦合） | ✅ |
| bias_cognitive | 0 | −0.15（e06/e07 解耦） | ⚠️ **标签缺口裁决**：6 标签无"认知↓"标签 → 采纳边推导 −0.15（[NEW]，补 NPC AI 缺口） |
| bias_limbic | +0.15（敏化-奖励） | +0.15（e05/e11 过度耦合） | ✅ |

**结论**：SUD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合经**状态分离裁决 + 标签缺口裁决**自洽。SUD NPC 最终参数：**NE=0.3、DA_VTA=0.6、DA_SNc=0.5、5HT=0.3、bias_somatic=+0.15、bias_cognitive=−0.15、bias_limbic=+0.15**。设计语义：成瘾 NPC = 线索敏化（DA↑）+ 冲动去抑制（5HT↓）+ 认知压制弱（bias_cognitive−）——"wanting 高、压制弱"的敌我同构闭环。

### 3.3 双相状态裁决规则（[NEW]，写入 §六.6 供 25 病复制）

> 触发条件：疾病的脑干广播边群出现**方向相反的相位状态**（SUD 急性↑/戒断↓；BN 暴食↑/清除↓；BED 暴食↑/内疚↓），或文献明确「敏化-耗竭」双相（Robinson & Berridge）。
> 裁决：① NPC 7 参数 = **行为表型侧**（与 §4.2 标签组合一致）；② 病理边 m_offset = **慢性/基线侧**（戒断耗竭）；③ 两通道经 行为覆盖/非线性跳变 衔接（急性期额外 +Δ、戒断期净方向翻转）；④ 验证表对冲突行标注 ⚠️ 状态分离裁决，不再视为规则 4 违规。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NAcc | 过度耦合+解耦沉默 −0.1/−0.3/−0.5 | **sud_e01**（VentralTegmentalArea→Accumbens-area） | ✅ 保留语义（量级不变；双相类型显式化为 net 解耦 + 急性跳变挂接） |
| link_344 | SNc→Putamen | 过度耦合+解耦沉默 0/−0.2/−0.3 | **sud_e02** | ✅ 保留语义（同 link_336 显式化） |
| link_343 | SNc→Caudate | 过度耦合+解耦沉默 0/−0.1/−0.2 | **sud_e03** | ✅ 保留语义（同上） |
| link_363 | Putamen→Thalamus | 过度耦合 +0.1/+0.3/+0.4 | **sud_e04**（Putamen→Thalamus-Proper） | ✅ 保留语义（端点/类型/量级不变） |
| link_008_L | ACC(L)→dlPFC | 解耦沉默 −0.1/−0.3/−0.5 | **sud_e06**（rostralmiddlefrontal→Caudate） | ⚠️ **语义转移**：ACC→dlPFC 直连不在三体图（rostralmiddlefrontal↔caudalanteriorcingulate 无 CC 边）→ 认知控制域↓ 由认知 CSTC 环路（dlPFC→Caudate）承载；量级沿用 |
| link_328 | LocusCoeruleus→RostralMiddleFrontalDLPFC | 解耦沉默 0/−0.2/−0.3 | **sud_e08** | ✅ 保留语义（fid 合并：DLPFC → rostralmiddlefrontal；类型修正为结构异常——LC 投射腿受损，§6.3 规则(b)） |
| link_155_L | ACC吻侧(L)→前脑岛 | 解耦沉默 0/−0.1/−0.3 | **sud_e09** | ✅ 保留语义 + **L 后缀取消**（ENIGMA 单半球数据点非偏侧证据，#92 合并双侧，Δ=0） |
| link_003_L | ACC(L)→海马旁回 | 过度耦合 0/+0.2/+0.3 | **sud_e10** | ✅ 保留语义 + L 后缀取消（Δ=0） |
| （旧表无） | vmPFC-腹侧纹状体 超连接（文献 §七 SUD） | — | **sud_e05** | ⭐ 新增——bias_limbic 机制锚（Dugré 2023） |
| （旧表无） | dlPFC-ACC 低连接（文献 §七 SUD） | — | **sud_e07** | ⭐ 新增——ACC 侧认知环路解耦 |
| （旧表无） | 戒断期负性情绪→渴求（杏仁核-纹状体，ENIGMA 杏仁核↓ + Koob） | — | **sud_e11** | ⭐ 新增——戒断期跳变作用域锚 |
| （旧表无） | 5HT 广播↓→冲动（Soubrié 1986） | — | **sud_e12** | ⭐ 新增——5HT tone 推导锚 |
| （旧表无） | 动作自动化（背侧纹状体习惯，Everitt & Robbins 2005） | — | **sud_e13** | ⭐ 新增——bias_somatic 推导锚 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_008_L → cognitive 环路），「病理新增」从严（本文件 0 条）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 净方向 > 0（中毒期）：物质相关刺激→link_336 额外 +0.1；其他奖赏刺激→衰减 50% | ✅ 保留（改挂接） | **sud_e01** 急性期跳变（+0.1，作用域=奖赏域边群 e01/e02/e03）+ 其他奖赏衰减 50% | 中毒期 = 急性过度耦合侧；与 3.3 状态分离裁决衔接 |
| 奖赏域 净方向 < 0（戒断期）：缰核→VTA 活跃（经杏仁核↔NAcc 回路）——趋近不可用；SAN −2/回合 | ✅ 保留（改挂接） | **sud_e01** 戒断期净方向翻转 + **sud_e11**（杏仁核-纹状体负性情绪渴求）+ SAN −2/回合 | 缰核非 tripartite 节点（无 L↔R/无缰核）→ 语义由 e01 净负 + e11 作用域承载 |
| 认知控制域 \|m\| > 0.4 → L5 控制·主动 对 L1 冲动压制效力 −50% | ✅ 保留 | **sud_e06/sud_e07** \|m\| > 0.4（取两者 m_max）+ **sud_e08**（结构基础） | 同 PTSD e10 结构逻辑：慢性应激→dlPFC 受损 |
| （新增）内感受错误归因 [NEW] | ⭐ 新增 | **sud_e09** \|m\| > 0.3 | 岛叶解耦 → 渴求/戒断身体信号被错误归因（误读为生理需求/正常信号），旧思路链"内感受域↓"落数据 |
| （新增）**耐药 [NEW]** | ⭐ 新增 | **sud_e01** 急性期 +Δ 随使用次数递减（每 3 次使用后 +Δ 减半：+0.1→+0.05→+0.03）；戒断期 m 下探幅度加深 | 耐药 = 奖赏峰值递减 → 驱动剂量升级行为（行为学：需更多物质达同等效应） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_363 m > 0.4 → 习惯锁定——M1 通道强制"熟练"（自动化行为），无法选择新动作类型 | ✅ 保留 | **sud_e04** m > 0.4，作用域 = e04 + e13 | 壳核习惯化锁定（Everitt & Robbins 2005） |
| 认知控制域 m_max < −0.4 → dlPFC 压制完全失效——所有 L1-L2 行为由标签+情境直接驱动 | ✅ 保留 | **sud_e06** m < −0.4（作用域含 e07） | dlPFC 压制完全失效（冲动直接驱动） |
| （新增）戒断期渴求跳变 [NEW] | ⭐ 新增 | **sud_e11** m > 0（戒断期激活）→ 物质相关趋近不可压制（冲动强制）| 戒断期负性情绪→杏仁核-纹状体渴求（Koob 负强化） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_008_L, link_363, link_328 | **sud_e01, sud_e06, sud_e04, sud_e08** |
| 2（关联） | link_344, link_343, link_155_L, link_003_L | **sud_e02, sud_e03, sud_e09, sud_e10, sud_e05, sud_e07, sud_e11** |
| 1（边缘） | — | **sud_e12, sud_e13** |

> 核心 4 条 = 奖赏双相核心（e01）+ 认知控制↓核心（e06）+ 习惯化核心（e04）+ 结构受损核心（e08）；新增边 e05/e07/e11 落关联权重，e12/e13 落边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6（SUD max=0.5） | §二 |
| 偏侧偏离量 | laterality_delta | 0（无稳健偏侧证据） | §二 |
| NE 基线偏离（SUD） | ΔNE_baseline | 0（基线 0.3） | §三 |
| DA_VTA 基线偏离（SUD） | ΔDA_VTA_baseline | +0.2（敏化侧，状态分离裁决；基线 0.4 → 0.6） | §三 |
| DA_SNc 基线偏离（SUD） | ΔDA_SNc_baseline | 0（标签侧；边推导 −0.1 弃用） | §三 |
| 5HT 基线偏离（SUD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（SUD） | bias_somatic / bias_cognitive / bias_limbic | +0.15 / −0.15 [NEW] / +0.15（值域 [−0.3,+0.3]） | §三 |
| 习惯锁定阈值 | m_th | 0.4（sud_e04，M1 强制熟练） | §五.2 |
| dlPFC 压制失效阈值 | m_th | −0.4（sud_e06，\|m\|） | §五.2 |
| 耐药衰减 | r | +Δ 每 3 次使用减半 [NEW 初值可调] | §五.1 |
| 戒断期 SAN 惩罚 | ΔSAN | −2/回合 | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [PTSD 重映射试点](ptsd-pilot.md), [物质使用障碍](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E7%89%A9%E8%B4%A8%E4%BD%BF%E7%94%A8%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [脑功能层级模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md), [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [tripartite_model.json](../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../data/connectivity/link_registry.json)（⚠️ 已废弃）*
