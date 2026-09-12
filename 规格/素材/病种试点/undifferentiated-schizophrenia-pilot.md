---
父类: 奖赏系统障碍
疾病ID: undifferentiated-schizophrenia
CGI-S范围: 3-7
文献: Lutz et al. (2020) BSNIP P-SZ vs NP-SZ: smaller hippocampus/amygdala in NP-SZ | Bagcioglu et al. (2014) CC prefrontal region (CC1) smaller in undifferentiated | less severe than paranoid | ENIGMA SZ (Van Erp 2016) | Guo et al. (2026) | PANSS (Fountoulakis 2019) | Schijven et al. (2023) / Okada et al. (2016) / Gutman et al. (2022) 偏侧
---

# 未分化型精神分裂症 — 脑部重映射试点

> Grilling #88 试点批次（PTSD 试点之后 3 病之一）。把旧 `link_NNN` 链路表重映射为三体模型上的 **16 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。与偏执型共享精分谱系模式（奖赏解耦 + 整合域反相关消失 + ACC-mPFC 过度激活），但**效应量 ≈ 偏执型 ×0.7-0.8**（海马 d≈−0.3 vs −0.4，BSNIP），且**阴性症状 + 认知缺陷更突出**：语言社会域以**解耦沉默**为主（Broca↔Wernicke / vmPFC↔Wernicke / 中脑皮层 DA 腿 m 负偏移），胼胝体前额段 CC1↓（Bagcioglu 2014）承载语言-社会整合缺损；防御/记忆域结构损害更重（BSNIP：NP-SZ 海马+杏仁核 < P-SZ）。**偏侧 Δ 与偏执型同源但幅度收敛**（微调级 −0.05/+0.05），阳性边（听觉语言环路）幅度缩小。7 参数推导与 NPC AI §4.2 标签组合「敏化-威胁 + 社交钝化」在 5/7 参数直接一致，DA_VTA/DA_SNc 为标签外边证据直调。

## 目录

1. [文献锚点（核心 + 疾病特异性 + 偏侧）](#一文献锚点核心--疾病特异性--偏侧)
2. [50 实体病理边表（16 条，含三体边核验列）](#二50-实体病理边表16-条含三体边核验列)
3. [7 参数映射建议（4 tone + 3 CSTC）](#三七参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）](#五行为覆盖非线性跳变保留清单panss-五因子挂接)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（核心 + 疾病特异性 + 偏侧）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Lutz et al. (2020)** *Schizophr Res* BSNIP（[疾病-脑区链路映射-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 未分化） | 结构（P-SZ n=237 vs NP-SZ n=127） | **NP-SZ 海马 + 杏仁核体积 < P-SZ** → 防御/记忆域结构损害更重，边级翻译为耦合减弱（e12 解耦沉默）——与偏执型同对端点的过度耦合形成**亚型区分** |
| 2 | **Bagcioglu et al. (2014)** *S Afr J Psychiatr* | 结构（胼胝体） | **胼胝体前额叶段 CC1↓**（+ 顶颞枕段 CC5↓）→ 跨半球语言-社会整合缺损 → 语言社会域**解耦**为主（e06/e10）+ 偏侧 Δ 的语言网络载体 |
| 3 | **ENIGMA SZ — Van Erp et al. (2016)**（§3.2/§七） | 结构 mega-meta | 海马 d=−0.4、杏仁核 d=−0.3、丘脑 d=−0.3、NAcc↓（**未分化取 ×0.7-0.8：海马 d≈−0.3**）→ e01/e02/e12 幅度梯度依据 |
| 4 | **Guo et al. (2026)**（§2.1/§2.3）+ **Fountoulakis et al. (2019)** PANSS 五因子（§五）+ **Fan & Tan (2022)** DMN-FPN 反相关消失 | ALFF meta / PANSS / trait marker | SZ 特异性 ALFF↑ 纹状体/IFG/ACC-mPFC、↓中央前后回（e15/e03/e07/e16）；PANSS **阴性 + 认知缺陷 > 偏执型、阳性 ≅ 偏执型**（行为挂接以阴性因子为主）；DMN-FPN 反相关减弱（e07） |

**偏侧（ENIGMA 偏侧化文献数据源，SZ 必须用非零 laterality_delta）：**

| # | 文献 | 关键数据点（→ 偏侧 Δ 用途） |
|---|------|--------------------------|
| 5 | **Schijven et al. (2023)** *PNAS*（§三） | rACC 反转 d=−0.083 → e03/e04 Δ=−0.05；MTG 左薄 d=−0.074 → e09 Δ=−0.05 |
| 6 | **Okada et al. (2016)** *Mol Psychiatry*（§四） | 苍白球左偏（SZ 特异）→ e13 Δ=−0.05；海马/杏仁核右偏健康基线 → e12 Δ=+0.05 方向参照 |
| 7 | **Gutman et al. (2022)** *Hum Brain Mapp*（§五） | 海马/杏仁核/丘脑偏侧夸大 → e05（丘脑 Δ=−0.05）、e12（海马/杏仁核 Δ=+0.05） |

**辅助锚**：Kong et al. (2018) 语言区左偏基线（e06/e09/e10 的 Δ 参照系）；中脑皮层 DA 假说（Davis 1991，e11 结构异常）；旧链路注册表（link_registry.json ⚠️ 已废弃，8 条旧链路语义继承源，见 §四）。

> **转换规则声明**：同偏执型（§一）。**偏侧豁免声明**：§6.5 规则 4「|d|<0.1 不做」对 SZ 豁免（ENIGMA 偏侧化 §九a/c），幅度取微调级 ±0.05。未分化幅度收敛（结构更小效应）——阳性语言边（e09）幅度低于偏执型（0.2/0.4/0.6 → 0.1/0.2/0.3）。

---

## 二、50 实体病理边表（16 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name；禁触镜像。**16 条全部命中三体模型现有边，0 条「病理新增」**。CGI-S 3-7 → 档位过滤 B′ 三档全可用。边 ID 命名：`undifferentiated-schizophrenia_e<NN>`。

### 2.1 奖赏域（2 条）——「奖赏解耦，量级 ×0.7-0.8」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **undifferentiated-schizophrenia_e01** | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 解耦沉默 | −0.1/−0.3/−0.4 | 0 | 旧 link_336（VTA→NAcc，Schultz 1997）；ENIGMA NAcc↓（×0.7-0.8） | DA_VTA tone 推导锚 |
| **undifferentiated-schizophrenia_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_344（SNc→壳核，Paxinos 2004） | DA_SNc tone 推导锚 |

### 2.2 认知控制/整合域（3 条）——「认知锁定较弱 + 反相关减弱 + 中脑皮层 DA 腿受损（阴性核心）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **undifferentiated-schizophrenia_e03** | caudalanteriorcingulate | rostralanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5879 | 过度耦合 | +0.1/+0.2/+0.3 | **−0.05** | 旧 link_007_L（ACC↔rACC 锁定，幅度降）；Schijven 2023 rACC 反转 | 认知锁定（弱于偏执型） |
| **undifferentiated-schizophrenia_e07** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 旧 link_082_L（DMN-FPN 反相关减弱，非消失——未分化效应量小）；Fan&Tan 2022 | 跳变②（整合域 \|m\| > 0.3 → L5 叙事重构不可用，重档 0.3 达标） |
| **undifferentiated-schizophrenia_e11** ⭐新增 | VentralTegmentalArea | rostralmiddlefrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **结构异常** | −0.1/−0.3/−0.4 | 0 | 中脑皮层 DA 腿选择性受损（Davis 1991）；**阴性/认知症状核心载体（幅度 > 偏执型）**；§6.3 subtype (b) | DA_VTA tone 推导锚（负项）+ 行为覆盖（SAN<30 联动） |

### 2.3 语言/感觉域（5 条）——「语言社会域解耦为主（阴性）+ 阳性残留（听觉语言环路）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **undifferentiated-schizophrenia_e06** | parsopercularis | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1723 | 解耦沉默 | 0/−0.2/−0.3 | **−0.05** | 旧 link_116_L（Broca↔Wernicke，旧「结构异常」→ 解耦沉默重分类）；**语言社会域 m_max < −0.2 → Broca 紊乱**（重档 −0.3 达标） | 行为覆盖①（语言贫乏/紊乱）+ PANSS 阴性 |
| **undifferentiated-schizophrenia_e10** ⭐新增 | medialorbitofrontal | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2822 | 解耦沉默 | −0.1/−0.2/−0.3 | **−0.05** | 社交钝化：ToM 网络解耦（Green 2015 社会脑低激活；偏执型同对为过度耦合 → **亚型区分**）；Bagcioglu 2014 CC1↓ 跨半球语言整合 | bias_cognitive 推导锚（负项） |
| **undifferentiated-schizophrenia_e09** ⭐新增 | superiortemporal | middletemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5576 | 过度耦合 | +0.1/+0.2/+0.3 | **−0.05** | 阳性残留：听觉语言环路点燃（PANSS 阳性 ≅ 偏执型，但效应量 ×0.7）；Schijven 2023 MTG 左薄 | 语言域成员（幅度收窄） |
| **undifferentiated-schizophrenia_e05** | Thalamus-Proper | transversetemporal | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+2（MGN→A1） | 过度耦合 | +0.1/+0.3/+0.5 | **−0.05** | link_318 **语义转移**（SC→Thalamus 无直连）；P50 门控失败；Gutman 2022 丘脑偏侧夸大 | 跳变①（感觉域 m_max = 0.5 重档 > 0.4 → 感官过载） |
| **undifferentiated-schizophrenia_e16** ⭐新增 | precentral | postcentral | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.7590 | 解耦沉默 | 0/−0.2/−0.3 | 0 | Guo 2026 ALFF↓ 中央前后回（**阴性主导更强**）；动作迟缓 | 阴性侧翼（PANSS 阴性） |

### 2.4 防御/记忆域（3 条）——「结构损害更重 → 耦合减弱（与偏执型相反）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **undifferentiated-schizophrenia_e08** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939；含 L5 fid（FrontalPoleSN） | **跨层短路** | 0/+0.1/+0.2 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89 L）；§6.3 规则 b 机械重分类 | 记忆绑定（弱于偏执型） |
| **undifferentiated-schizophrenia_e12** ⭐新增 | Amygdala | Hippocampus | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.6506 | 解耦沉默 | 0/−0.1/−0.2 | **+0.05** | **BSNIP NP-SZ 海马+杏仁核 < P-SZ** → 结构缩小 → 记忆-情绪耦合减弱（与偏执型 e10 过度耦合形成亚型区分）；Gutman 2022 海马/杏仁核偏侧夸大（右偏） | 防御域侧翼（威胁反应钝化） |
| **undifferentiated-schizophrenia_e13** ⭐新增 | Pallidum | Thalamus-Proper | cstc | ✅ 命中：somatic 环路 `disinhibition`, pallidal_output→thalamic_relay | 过度耦合 | 0/+0.1/+0.2 | **−0.05** | ENIGMA SZ 苍白球↑（×0.7）；Okada 2016 苍白球左偏 | 结构修饰（节点 m 直调层） |

### 2.5 内感受/唤醒域（3 条）——「显著网络弱耦合 + NE 广播弱上调」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **undifferentiated-schizophrenia_e04** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | +0.1/+0.2/+0.3 | **−0.05** | 旧 link_155_L（rACC↔前脑岛）；Guo 2026 岛叶 ALFF↑（共享）；Schijven 2023 rACC 反转 | 内感受侧翼 |
| **undifferentiated-schizophrenia_e14** ⭐新增 | LocusCoeruleus | caudalanteriorcingulate | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | Guo 2026 共享 ACC/mPFC ALFF↑（×0.5 幅度）；敏化-威胁标签支撑 | NE tone 推导锚（小幅度） |
| **undifferentiated-schizophrenia_e15** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.2 | 0 | Guo 2026 共享纹状体 ALFF↑（×0.5）；敏化-威胁门控劫持 | bias_limbic 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有边）；Δ 负 = 左偏、正 = 右偏（§6.5）；幅度 ±0.05 = ENIGMA 偏侧化 §九c 微调级；未分化在**语言社会域**与偏执型方向相反（解耦 vs 过度耦合，阴性 vs 阳性亚型区分）、在**防御/记忆域**（e12）方向相反（结构损害翻译）。

---

## 三、7 参数映射建议（4 tone + 3 CSTC）

> 规则同偏执型（§6.6 复制）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e14（LC→ACC 0/+0.1/+0.2） | LC 出边群单条小幅度正偏移 → 蓝斑 NE 广播轻度上调（敏化-威胁标签主驱动，边证据为共享 ACC ALFF↑） |
| 2 | DA_VTA_baseline | **−0.1** | e01（VTA→NAcc −0.1/−0.3/−0.4）、e11（VTA→rostralmiddlefrontal −0.1/−0.3/−0.4） | VTA 出边群 2 条均负偏移（NAcc 腿 + 中脑皮层腿），**中脑皮层腿幅度 = 偏执型 1.33×**（阴性主导）→ DA_VTA ↓ |
| 3 | DA_SNc_baseline | **−0.05** | e02（SNc→Putamen 0/−0.1/−0.3） | SNc 出边群负偏移（幅度 < 偏执型）→ 运动启动基线微降 |
| 4 | 5HT_baseline | **−0.2** | 无 DR 边群命中 | 敏化-威胁标签主驱动（未分化 5-HT 异常非主载体，边证据缺位不阻碍 tone，PTSD 试点 e11 判例为聚焦腿才加边） |
| 5 | bias_somatic | **0** | 无 striatal_gate 级 somatic 环路边命中 | e13 为 pallidal_output 结构腿（节点 m 直调层） |
| 6 | bias_cognitive | **−0.15** | e06/e10（语言/ToM 网络解耦）、e11（中脑皮层 DA 腿） | 认知/社会环路 striatal_gate 侧低激活 → 语言/认知行动 gate 偏置↓（社交钝化标签一致：−0.15） |
| 7 | bias_limbic | **+0.15** | e15（Amygdala→Accumbens limbic `go_direct` 0/+0.1/+0.2）、e04（rACC↔insula） | 边缘环路 gate 轻度劫持（敏化-威胁标签主驱动） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」+「社交钝化」双标签（多标签叠加取最大值；标签未覆盖参数走 §4.3 粒度2 参数直调）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| DA_VTA_baseline | 0（标签未覆盖） | −0.1 | ⚠️ 标签外直调：奖赏/中脑皮层 DA 解耦（e01/e11）是精分核心病理 → 参数直调（§4.3 粒度2） |
| DA_SNc_baseline | 0（标签未覆盖） | −0.05 | ⚠️ 标签外直调：同上（e02） |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | −0.15（社交钝化） | −0.15 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：未分化型病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（5/7 标签直接覆盖；DA_VTA/DA_SNc 标签外直调同偏执型判例）。**未分化型 NPC 最终参数：NE=0.5、DA_VTA=0.3、DA_SNc=0.45、5HT=0.3、bias_cognitive=−0.15、bias_limbic=+0.15（其余基线）**。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 解耦沉默 −0.1/−0.3/−0.4 | **undifferentiated-schizophrenia_e01** | ✅ 保留语义（fid 合并） |
| link_344 | SubstantiaNigraParsCompacta→Putamen | 解耦沉默 0/−0.1/−0.3 | **undifferentiated-schizophrenia_e02** | ✅ 保留语义 |
| link_007_L | ACC(L)→RostralAnteriorCingulateCortex | 过度耦合 +0.1/+0.2/+0.3 | **undifferentiated-schizophrenia_e03** | ✅ 保留语义 + 偏侧显式化（rACC 反转 Δ=−0.05） |
| link_155_L | RostralAnteriorCingulateCortex→Insula | 过度耦合 +0.1/+0.2/+0.3 | **undifferentiated-schizophrenia_e04** | ✅ 保留语义 + 偏侧显式化（Δ=−0.05） |
| link_318 | SuperiorColliculus→Thalamus | 过度耦合 +0.1/+0.2/+0.3 | **无直连边**（三体图无 SC→Thalamus-Proper） | ⚠️ **废弃直连**；语义转移至 **e05**（Thalamus→transversetemporal 听觉中继，m 校准 0.1/0.3/0.5 使感官过载跳变 0.4 阈值可达） |
| link_116_L | ParsOpercularis→SuperiorTemporalWernicke | 结构异常 0/−0.1/−0.2 | **undifferentiated-schizophrenia_e06** | ⚠️ **类型重分类**（解耦沉默，§6.3）；量级微调 0/−0.2/−0.3 `[NEW]`（语言社会域 m_max < −0.2 行为覆盖可达）；偏侧显式化（Δ=−0.05） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 边界崩溃 −0.1/−0.2/−0.3 | **undifferentiated-schizophrenia_e07** | ⚠️ **类型重分类**（解耦沉默，§6.3；「边界崩溃」语义入挂接） |
| link_003_L | AnteriorCingulateCortex→Parahippocampal | 过度耦合 0/+0.1/+0.2 | **undifferentiated-schizophrenia_e08** | ⚠️ **类型重分类**（跨层短路，§6.3 规则 b：L5 fid 端点） |
| （旧表无） | vmPFC↔Wernicke ToM 解耦（社交钝化；偏执型同对为过度耦合） | — | **undifferentiated-schizophrenia_e10** | ⭐ 新增——亚型区分核心 |
| （旧表无） | STG↔MTG 听觉语言环路（阳性残留，×0.7） | — | **undifferentiated-schizophrenia_e09** | ⭐ 新增 |
| （旧表无） | 中脑皮层 DA 腿受损（阴性/认知核心，幅度 > 偏执型） | — | **undifferentiated-schizophrenia_e11** | ⭐ 新增——结构异常 |
| （旧表无） | 杏仁核-海马 耦合减弱（BSNIP NP-SZ 结构损害） | — | **undifferentiated-schizophrenia_e12** | ⭐ 新增——与偏执型 e10 反向 |
| （旧表无） | 苍白球→丘脑 结构异常（ENIGMA 苍白球↑ + Okada 左偏） | — | **undifferentiated-schizophrenia_e13** | ⭐ 新增 |
| （旧表无） | LC→ACC NE 轻度上调（共享 ACC ALFF↑ ×0.5） | — | **undifferentiated-schizophrenia_e14** | ⭐ 新增——NE tone 锚 |
| （旧表无） | 杏仁核→NAcc limbic gate 轻度劫持（共享纹状体 ALFF↑ ×0.5） | — | **undifferentiated-schizophrenia_e15** | ⭐ 新增——bias_limbic 锚 |
| （旧表无） | M1↔S1 感觉运动整合↓（ALFF↓ 中央前后回，阴性主导） | — | **undifferentiated-schizophrenia_e16** | ⭐ 新增 |

**处置规则总结**：同偏执型（直接映射保留 / 语义转移优先 / §6.3 机械重分类 / 「病理新增」从严 0 条）。

---

## 五、行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）

> PANSS 五因子（Fountoulakis 2019 §5.1）。未分化以**阴性 + 神经认知**为主挂接（文献数据源 §七 未分化：阴性+认知缺陷 > 偏执型）。

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| SAN < 30 → L5 叙事重构不可用 | ✅ 保留 | **全局**（e07/e11 \|m\| 重档联动） | 全因子 | 同偏执型 |
| 语言社会域 m_max < −0.2 → Broca 区输出 5% 紊乱（随机替换为语言攻击） | ✅ 保留 | **语言域边群**（e06 重档 −0.3 < −0.2；e10 重档 −0.3） | 阴性（语言贫乏）+ 神经认知 | 与偏执型「m_max > 0.5 正向紊乱」方向相反 = **亚型区分**（解耦型紊乱 vs 点燃型紊乱） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| 感觉域 m_max > 0.4 → 感官过载——目标选择随机化 10% | ✅ 保留 | **e05** m = 0.5（重档）> 0.4 | 神经认知（注意缺陷） | 阈值 0.4 由旧文件保留；e05 重档 0.5 达标 |
| （旧表无，自偏执型继承）整合域 \|m\| > 0.3 → SN 无法在 DMN/FPN 间切换 → L5 叙事重构不可用 | ✅ 新增（同谱系共享） | **e07** \|m\| = 0.3（重档） | 神经认知（抽象思维困难） | Fan&Tan 2022；未分化同偏执型共享整合域跳变 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_007_L, link_155_L, link_082_L | **e01, e03, e04, e07**（+ e11 阴性核心，待 #88 组件批次） |
| 2（关联） | link_344, link_318, link_116_L, link_003_L | **e02, e05, e06, e08**（+ e10, e15） |
| 1（边缘） | （旧表无，新增） | **e09, e12, e13, e14, e16** |

> 核心 4 条 = 奖赏解耦（e01）+ 认知锁定（e03）+ 显著网络（e04）+ 整合减弱（e07）；e11（中脑皮层 DA 腿，阴性核心）建议升核心。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6；整体 ≈ 偏执型 ×0.7-0.8 | §二 |
| 偏侧偏离量 | laterality_delta | 0 默认；SZ 微调级 ±0.05（8 条非零） | §二 |
| NE 基线偏离 | ΔNE_baseline | +0.2（0.3 → 0.5） | §三 |
| DA_VTA 基线偏离 | ΔDA_VTA_baseline | −0.1（0.4 → 0.3，标签外直调） | §三 |
| DA_SNc 基线偏离 | ΔDA_SNc_baseline | −0.05（0.5 → 0.45，标签外直调） | §三 |
| 5HT 基线偏离 | Δ5HT_baseline | −0.2（0.5 → 0.3） | §三 |
| CSTC 偏置 | bias_cognitive / bias_limbic | −0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 语言社会域解耦阈值 | m_th | −0.2（e06/e10 重档 −0.3，Broca 紊乱 5%） | §五 |
| 感官过载阈值 | m_th | 0.4（e05 重档 0.5，目标随机化 10%） | §五 |
| 整合域跳变阈值 | m_th | 0.3（e07 \|m\| 重档 0.3，L5 叙事重构不可用） | §五 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [ptsd-pilot.md](ptsd-pilot.md), [grilling-88.md](grilling-88.md), [未分化型精神分裂症](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E6%9C%AA%E5%88%86%E5%8C%96%E5%9E%8B%E7%B2%BE%E7%A5%9E%E5%88%86%E8%A3%82%E7%97%87.md), [偏执型精神分裂症](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E5%81%8F%E6%89%A7%E5%9E%8B%E7%B2%BE%E7%A5%9E%E5%88%86%E8%A3%82%E7%97%87.md), [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4/§5.2, [偏侧化架构](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四, [脑功能层级模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [ENIGMA偏侧化-精神疾病大样本meta-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §三/§四/§五/§九, [tripartite_model.json](../../../data/connectivity/tripartite_model.json)*
