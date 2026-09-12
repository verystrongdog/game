---
父类: 奖赏系统障碍
疾病ID: schizoaffective
CGI-S范围: 3-7
文献: Madre et al. (2016) GMV loss closer to SZ than BD | ENIGMA Schizotypy WG (2021) schizotypy→SZ cortical thickness pattern (r=.285) but not BD (r=.166) | ENIGMA SZ (Van Erp 2016) | Guo et al. (2026) | PANSS (Fountoulakis 2019) | Schijven et al. (2023) / Okada et al. (2016) / Gutman et al. (2022) 偏侧
---

# 分裂情感性障碍 — 脑部重映射试点

> Grilling #88 试点批次（PTSD 试点之后 3 病之一）。把旧 `link_NNN` 链路表重映射为三体模型上的 **15 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **精分认知控制异常（×0.8）+ BD 奖赏/唤醒双向振荡（×0.5）的混合**：灰质丧失更接近精分（Madre 2016），故 m 偏移以精分模式为主；但**唤醒域 LC→杏仁核 过度耦合**承载心境相位翻转（唤醒域 m_max > 0.3 → 每 5 回合 15% 翻转，同 BD-II 轻度振荡），**敏化-奖励标签使 DA_VTA 取 +0.2**（唯一 tone 上升的精分谱系病——VTA 出边群混合：NAcc 腿解耦 = 精分快感缺失，Amygdala 腿过度耦合 = BD 奖赏敏化）。偏侧 Δ 同谱系保留（微调级 ±0.05），强调混合心境而非语言偏侧。7 参数推导与 NPC AI §4.2 标签组合「敏化-威胁 + 敏化-奖励」在 6/7 参数直接一致（DA_SNc 一项标签外直调）。

## 目录

1. [文献锚点（核心 + 疾病特异性 + 偏侧）](#一文献锚点核心--疾病特异性--偏侧)
2. [50 实体病理边表（15 条，含三体边核验列）](#二50-实体病理边表15-条含三体边核验列)
3. [7 参数映射建议（4 tone + 3 CSTC）](#三七参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）](#五行为覆盖非线性跳变保留清单panss-五因子挂接)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（核心 + 疾病特异性 + 偏侧）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Madre et al. (2016)** *Acta Psychiatr Scand*（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 分裂情感性） | 结构系统综述 | **灰质体积丧失介于精分与双相之间，更接近精分** → m 偏移以精分模式为主（×0.8），BD 成分为叠加（×0.5） |
| 2 | **ENIGMA Schizotypy WG (2021)** *Mol Psychiatry* | 结构相关 | 亚临床 schizotypy→mOFC/vmPFC 皮质厚度↑ 与 **SZ 模式正相关 r=.285**、与 BD 不显著 r=.166 → e06（mOFC↔dlPFC）等精分 trait 边保留 |
| 3 | **ENIGMA SZ — Van Erp et al. (2016)**（§3.2/§七）+ **Guo et al. (2026)**（§2.1/§2.3）+ **Fan & Tan (2022)** | 结构/ALFF/trait marker | SZ 结构梯度（海马/杏仁核/丘脑↓、苍白球↑）与 ALFF 模式（纹状体/IFG/ACC-mPFC↑、中央前后回↓）→ e01/e02/e12/e09/e15 等精分模式边；DMN-FPN 反相关消失（e06） |
| 4 | **Fountoulakis et al. (2019)** PANSS 五因子（§五）+ BD 模式（[文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 双相） | PANSS / 汇总 | 五因子全可卷入（混合心境 = 抑郁/焦虑因子 + 兴奋/敌意因子交替主导）；BD 奖赏域双向、唤醒域振荡 → §五 心境相位翻转挂接 + 唤醒域边（e07） |

**偏侧（ENIGMA 偏侧化文献数据源，SZ 必须用非零 laterality_delta）：**

| # | 文献 | 关键数据点（→ 偏侧 Δ 用途） |
|---|------|--------------------------|
| 5 | **Schijven et al. (2023)** *PNAS*（§三） | rACC 反转 d=−0.083 → e03/e04 Δ=−0.05；MTG 左薄 d=−0.074 → e09 Δ=−0.05 |
| 6 | **Okada et al. (2016)** *Mol Psychiatry*（§四） | 苍白球左偏（SZ 特异）→ e12 Δ=−0.05；海马右偏健康基线 → e13 Δ=+0.05 方向参照 |
| 7 | **Gutman et al. (2022)** *Hum Brain Mapp*（§五） | 海马/杏仁核/丘脑偏侧夸大 → e05（丘脑 Δ=−0.05）、e13（海马 Δ=+0.05） |

**辅助锚**：Robinson & Berridge (1993) 奖赏敏化（incentive sensitization，NPC AI §4.2「敏化-奖励」文献锚）→ e10/e11 奖赏边；Kong et al. (2018) 语言区左偏基线（e09 Δ 参照系）；旧链路注册表（link_registry.json ⚠️ 已废弃，8 条旧链路语义继承源，见 §四）。

> **转换规则声明**：同偏执型（§一）。**偏侧豁免声明**：§6.5 规则 4「|d|<0.1 不做」对 SZ 豁免（ENIGMA 偏侧化 §九a/c），幅度取微调级 ±0.05。分裂情感偏侧非主特征（强调混合心境），故偏侧 Δ 仅 6 条且全部收敛至 ±0.05。

---

## 二、50 实体病理边表（15 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name；禁触镜像。**15 条全部命中三体模型现有边，0 条「病理新增」**。CGI-S 3-7 → 档位过滤 B′ 三档全可用。边 ID 命名：`schizoaffective_e<NN>`。

### 2.1 奖赏域（4 条）——「精分奖赏解耦（×0.8）+ BD 奖赏敏化（×0.5）双向叠加」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e01** | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 解耦沉默 | −0.1/−0.3/−0.5 | 0 | 旧 link_336（VTA→NAcc 精分奖赏解耦，×0.8 幅度、重档更深） | DA_VTA tone 推导锚（负项） |
| **schizoaffective_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_344（SNc→壳核） | DA_SNc tone 推导锚 |
| **schizoaffective_e10** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.2/+0.3 | 0 | **敏化-奖励**（Robinson & Berridge 1993）：BD 奖赏线索过度敏化（×0.5 振荡）；Guo 2026 共享纹状体 ALFF↑ | bias_limbic 推导锚 + 心境翻转挂接 |
| **schizoaffective_e11** ⭐新增 | VentralTegmentalArea | Amygdala | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | BD 奖赏-情绪 DA 通路敏化（RDoC 正性效价奖赏学习：VTA→杏仁核）；与 e01 构成 **VTA 出边群混合**（见 §三.1） | DA_VTA tone 推导锚（正项） |

### 2.2 认知控制/整合域（2 条）——「精分 trait 保留」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e03** | caudalanteriorcingulate | rostralanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5879 | 过度耦合 | +0.1/+0.3/+0.4 | **−0.05** | 旧 link_007_L（ACC↔rACC 锁定，精分认知异常 ×0.8）；Schijven 2023 rACC 反转 | 认知锁定（兴奋/敌意因子挂接） |
| **schizoaffective_e06** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默 | −0.1/−0.2/−0.4 | 0 | 旧 link_082_L（DMN-FPN 反相关消失 ≈ 精分）；ENIGMA Schizotypy 2021（mOFC 模式与 SZ 正相关 r=.285） | 跳变②（整合域 \|m\| > 0.3 → L5 叙事重构不可用，重档 0.4 达标） |

### 2.3 唤醒域（2 条）——「BD 心境振荡核心」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e07** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/+0.2/+0.4 `[NEW 校准]` | 0 | 旧 link_332（蓝斑→杏仁核 NE，脑干强度估计）；BD 唤醒域振荡（×0.5）；重档 0.4 > 0.3 触发心境翻转 | **行为覆盖①（心境相位翻转）** + NE tone 推导锚 |
| **schizoaffective_e14** ⭐新增 | VentralTegmentalArea | rostralmiddlefrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **结构异常** | −0.1/−0.2/−0.3 | 0 | 中脑皮层 DA 腿受损（精分共享模式 ×0.8，Davis 1991）；§6.3 subtype (b) | 认知缺陷侧翼 |

### 2.4 感觉/语言域（3 条）——「精分阳性残留（×0.8）+ 感官过载（×0.5）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e05** | Thalamus-Proper | transversetemporal | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+2（MGN→A1） | 过度耦合 | 0/+0.2/+0.3 | **−0.05** | link_318 **语义转移**（SC→Thalamus 无直连）；P50 门控失败（×0.5）；Gutman 2022 丘脑偏侧夸大 | 感觉侧翼 |
| **schizoaffective_e09** ⭐新增 | superiortemporal | middletemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5576 | 过度耦合 | 0/+0.1/+0.2 | **−0.05** | 幻觉残留（精分模式 ×0.8，幅度最小档）；Schijven 2023 MTG 左薄 | 语言域成员（幅度收窄） |
| **schizoaffective_e15** ⭐新增 | precentral | postcentral | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.7590 | 解耦沉默 | 0/−0.1/−0.2 | 0 | Guo 2026 ALFF↓ 中央前后回（×0.5） | 阴性侧翼 |

### 2.5 防御/记忆域（2 条）——「精分记忆绑定 + 5-HT 聚焦」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e08** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939；含 L5 fid（FrontalPoleSN） | **跨层短路** | 0/+0.1/+0.2 | 0 | 旧 link_003_L（ACC→海马旁回）；§6.3 规则 b 机械重分类 | 记忆绑定 |
| **schizoaffective_e13** ⭐新增 | DorsalRapheNucleus | Hippocampus | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged 孪生边存在） | 过度耦合 | 0/+0.1/+0.2 | **+0.05** | 5-HT 传递聚焦记忆/情绪回路（精分共享 link_319 语义）；Gutman 2022 海马偏侧夸大（右偏） | 5HT tone 推导锚 |

### 2.6 内感受域（1 条）——「岛叶-ACC 显著网络」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e04** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | +0.1/+0.2/+0.3 | **−0.05** | 旧 link_155_L（rACC↔前脑岛，精分共享）；Guo 2026 岛叶 ALFF↑；Schijven 2023 rACC 反转 | 内感受侧翼 |

### 2.7 行动门控域（1 条）——「苍白球结构异常」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizoaffective_e12** ⭐新增 | Pallidum | Thalamus-Proper | cstc | ✅ 命中：somatic 环路 `disinhibition`, pallidal_output→thalamic_relay | 过度耦合 | 0/+0.1/+0.2 | **−0.05** | ENIGMA SZ 苍白球↑（×0.8）；Okada 2016 苍白球左偏 | 结构修饰（节点 m 直调层） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有边）；Δ 负 = 左偏、正 = 右偏（§6.5）；幅度 ±0.05 = ENIGMA 偏侧化 §九c 微调级；`[NEW 校准]` = link_332 重档 0.3 → 0.4（使唤醒域 m_max > 0.3 心境翻转跳变可达）。

---

## 三、7 参数映射建议（4 tone + 3 CSTC）

> 规则同偏执型（§6.6 复制）：tone 从脑干广播边群推导（**混合方向按主导**），bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e07（LC→Amygdala 0/+0.2/+0.4 过度耦合） | LC 出边群单条命中且 m 随严重度升高 → 蓝斑 NE 上调 + **心境相位振荡由 e07 跳变承载**（tone 保持高位，振荡在行为层翻转） |
| 2 | DA_VTA_baseline | **+0.2** | e01（VTA→NAcc −0.1/−0.3/−0.5）、e11（VTA→Amygdala +0.1/+0.2/+0.3）、e14（VTA→dlPFC −0.1/−0.2/−0.3） | **VTA 出边群混合**：NAcc 腿解耦（精分快感缺失）+ Amygdala 腿过度耦合（BD 奖赏敏化）+ dlPFC 腿受损 → §6.6 规则 1「混合 → 按主导方向」，主导方向由敏化-奖励标签锚定 **+0.2**（唯一 tone 上升的精分谱系病） |
| 3 | DA_SNc_baseline | **−0.05** | e02（SNc→Putamen 0/−0.1/−0.3） | SNc 出边群负偏移 → 运动启动基线微降 |
| 4 | 5HT_baseline | **−0.2** | e13（DR→Hippocampus 0/+0.1/+0.2 过度耦合） | 中缝核 5-HT 传递异常聚焦记忆/情绪回路 → 全局基线↓（去抑制；PTSD/偏执型同判例）；双标签（敏化-威胁 + 敏化-奖励）一致 |
| 5 | bias_somatic | **0** | 无 striatal_gate 级 somatic 环路边命中 | e12 为 pallidal_output 结构腿（节点 m 直调层） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）striatal_gate 级边命中 | e06（mOFC↔dlPFC）属 CC 层；e14（VTA→dlPFC）属脑干广播层 → 认知 gate 无偏置（无 反刍/社交钝化 标签） |
| 7 | bias_limbic | **+0.15** | e10（Amygdala→Accumbens limbic `go_direct` 0/+0.2/+0.3）、e07（LC→Amygdala） | 边缘环路 gate 被奖赏/威胁信号双向劫持 → 情绪/本能行动倾向↑（双标签一致：+0.15） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」+「敏化-奖励」双标签（多标签叠加取最大值；标签未覆盖参数走 §4.3 粒度2 参数直调）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| DA_VTA_baseline | +0.2（敏化-奖励） | +0.2（VTA 出边群混合，主导方向） | ✅ |
| DA_SNc_baseline | 0（标签未覆盖） | −0.05 | ⚠️ 标签外直调：黑质纹状体腿解耦（e02，精分共享）→ 参数直调（§4.3 粒度2） |
| 5HT_baseline | −0.2（双标签） | −0.2 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（双标签） | +0.15 | ✅ |

**结论**：分裂情感性障碍病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（**6/7 标签直接覆盖**，DA_SNc 一项标签外直调）。**分裂情感 NPC 最终参数：NE=0.5、DA_VTA=0.6、DA_SNc=0.45、5HT=0.3、bias_limbic=+0.15（其余基线）**——DA_VTA 为 0.6 是精分谱系唯一奖赏敏化态（BD 混合特征），与偏执型（0.3）/未分化（0.3）形成参数级三病区分。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 解耦沉默 −0.1/−0.3/−0.5 | **schizoaffective_e01** | ✅ 保留语义（fid 合并） |
| link_344 | SubstantiaNigraParsCompacta→Putamen | 解耦沉默 0/−0.1/−0.3 | **schizoaffective_e02** | ✅ 保留语义 |
| link_007_L | ACC(L)→RostralAnteriorCingulateCortex | 过度耦合 +0.1/+0.3/+0.4 | **schizoaffective_e03** | ✅ 保留语义 + 偏侧显式化（rACC 反转 Δ=−0.05） |
| link_155_L | RostralAnteriorCingulateCortex→Insula | 过度耦合 +0.1/+0.2/+0.3 | **schizoaffective_e04** | ✅ 保留语义 + 偏侧显式化（Δ=−0.05） |
| link_318 | SuperiorColliculus→Thalamus | 过度耦合 0/+0.2/+0.3 | **无直连边**（三体图无 SC→Thalamus-Proper） | ⚠️ **废弃直连**；语义转移至 **e05**（Thalamus→transversetemporal 听觉中继） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 边界崩溃 −0.1/−0.2/−0.4 | **schizoaffective_e06** | ⚠️ **类型重分类**（解耦沉默，§6.3；「边界崩溃」语义入挂接） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 0/+0.2/+0.3 | **schizoaffective_e07** | ⚠️ 量级校准 `[NEW]` 0/+0.2/+0.4（唤醒域 m_max > 0.3 心境翻转跳变可达）；**心境振荡语义显式化** |
| link_003_L | AnteriorCingulateCortex→Parahippocampal | 过度耦合 0/+0.1/+0.2 | **schizoaffective_e08** | ⚠️ **类型重分类**（跨层短路，§6.3 规则 b） |
| （旧表无） | 杏仁核→NAcc limbic gate 奖赏敏化（敏化-奖励） | — | **schizoaffective_e10** | ⭐ 新增——bias_limbic 机制锚 + BD 奖赏敏化 |
| （旧表无） | VTA→杏仁核 奖赏-情绪 DA 敏化（RDoC 正性效价） | — | **schizoaffective_e11** | ⭐ 新增——DA_VTA +0.2 的正项锚 |
| （旧表无） | 苍白球→丘脑 结构异常（ENIGMA 苍白球↑ + Okada 左偏） | — | **schizoaffective_e12** | ⭐ 新增 |
| （旧表无） | 中缝背核→海马 5-HT 聚焦（link_319 语义继承） | — | **schizoaffective_e13** | ⭐ 新增——5HT tone 锚 |
| （旧表无） | 中脑皮层 DA 腿受损（精分共享 ×0.8） | — | **schizoaffective_e14** | ⭐ 新增——结构异常 |
| （旧表无） | M1↔S1 感觉运动整合↓（ALFF↓ 中央前后回 ×0.5） | — | **schizoaffective_e15** | ⭐ 新增 |

**处置规则总结**：同偏执型（直接映射保留 / 语义转移优先 / §6.3 机械重分类 / 「病理新增」从严 0 条）。旧 8 条链路全部覆盖（link_318 语义转移、link_082_L/003_L 类型重分类、link_332 量级校准）。

---

## 五、行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）

> PANSS 五因子（Fountoulakis 2019 §5.1）。分裂情感以**抑郁/焦虑 + 兴奋/敌意交替**（混合心境）为主挂接，叠加精分神经认知因子。

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| SAN < 30 → L5 叙事重构不可用 | ✅ 保留 | **全局**（e06/e14 \|m\| 重档联动） | 全因子 | 同偏执型 |
| 唤醒域 m_max > 0.3 → 心境相位每 5 回合检查一次翻转（概率 15%，同 BD-II 轻度振荡） | ✅ 保留 | **e07** m = 0.4（重档）> 0.3，作用域 = 唤醒域边群（e07 + e10 奖赏侧） | 抑郁/焦虑 + 兴奋/敌意（心境因子交替） | 旧 link_332 → e07；`[NEW 校准]` 重档 0.4 使阈值可达；BD 振荡 ×0.5 强度 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| 整合域 \|m\| > 0.3 → SN 无法在 DMN/FPN 间切换——L5 叙事重构不可用（作用域 link_082_L，同精分） | ✅ 保留 | **e06** \|m\| = 0.4（重档）> 0.3 | 神经认知（抽象思维困难） | Fan&Tan 2022；精分 trait 共享 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_007_L, link_155_L, link_082_L | **e01, e03, e04, e06**（+ e07 心境振荡核心、e10 奖赏敏化核心，待 #88 组件批次） |
| 2（关联） | link_344, link_318, link_332, link_003_L | **e02, e05, e07, e08**（+ e10, e11） |
| 1（边缘） | （旧表无，新增） | **e09, e12, e13, e14, e15** |

> 核心 4 条 = 奖赏解耦（e01）+ 认知锁定（e03）+ 显著网络（e04）+ 整合崩溃（e06）；e07（心境翻转）/e10（奖赏敏化）为分裂情感特有核心，建议与旧核心并列。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6；精分模式 ×0.8 + BD 振荡 ×0.5 | §二 |
| 偏侧偏离量 | laterality_delta | 0 默认；SZ 微调级 ±0.05（6 条非零） | §二 |
| NE 基线偏离 | ΔNE_baseline | +0.2（0.3 → 0.5） | §三 |
| DA_VTA 基线偏离 | ΔDA_VTA_baseline | **+0.2**（0.4 → 0.6，精分谱系唯一奖赏敏化态） | §三 |
| DA_SNc 基线偏离 | ΔDA_SNc_baseline | −0.05（0.5 → 0.45，标签外直调） | §三 |
| 5HT 基线偏离 | Δ5HT_baseline | −0.2（0.5 → 0.3） | §三 |
| CSTC 偏置 | bias_limbic | +0.15（值域 [−0.3,+0.3]；somatic/cognitive = 0） | §三 |
| 心境翻转阈值 | m_th | 0.3（e07 重档 0.4，每 5 回合 15% 相位翻转） | §五 |
| 整合域跳变阈值 | m_th | 0.3（e06 \|m\| 重档 0.4，L5 叙事重构不可用） | §五 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [grilling-88.md](../disease-pilots/grilling-88.md), [分裂情感性障碍](../../../entities/diseases/%E5%88%86%E8%A3%82%E6%83%85%E6%84%9F%E6%80%A7%E9%9A%9C%E7%A2%8D.md), [偏执型精神分裂症](../../../entities/diseases/%E5%81%8F%E6%89%A7%E5%9E%8B%E7%B2%BE%E7%A5%9E%E5%88%86%E8%A3%82%E7%97%87.md), [双相障碍I型](../../../entities/diseases/%E5%8F%8C%E7%9B%B8%E9%9A%9C%E7%A2%8DI%E5%9E%8B.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [ENIGMA偏侧化-精神疾病大样本meta-文献数据源](../../../../reference/literature/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §三/§四/§五/§九, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
