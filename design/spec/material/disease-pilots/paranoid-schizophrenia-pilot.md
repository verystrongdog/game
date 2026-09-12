---
父类: 奖赏系统障碍
疾病ID: paranoid-schizophrenia
CGI-S范围: 3-7
文献: ENIGMA SZ (Van Erp 2016) 海马d=-0.4, 杏仁核d=-0.3, 丘脑d=-0.3, 侧脑室d=+0.3 | PANSS (Fountoulakis 2019) 五域可卷入 | Guo et al. (2026) ALFF↑纹状体/IFG/ACC-mPFC, ↓中央前后回 | Fan&Tan (2022) DMN-FPN反相关消失 trait marker | Schijven et al. (2023) rACC反转d=-0.083/MTG左薄d=-0.074 | Okada et al. (2016) 苍白球左偏 | Gutman et al. (2022) 海马/杏仁核/丘脑偏侧夸大
---

# 偏执型精神分裂症 — 脑部重映射试点

> Grilling #88 试点批次（PTSD 试点之后 3 病之一）。把旧 `link_NNN` 链路表重映射为三体模型上的 **21 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **阳性症状主导的「内在点燃」**：语言网络偏侧异常（左 MTG/STG/Broca 左薄，Δ≠0）承载幻觉 + 岛叶-ACC 显著网络过度激活 + ACC↔rACC 认知控制锁定 + DMN-FPN 反相关消失（整合域）+ VTA→NAcc 奖赏解耦。**SZ 是唯一达到大样本稳健偏侧证据的疾病**（ENIGMA 偏侧化文献数据源 §九a），故本文件为三病共用的 laterality_delta 使用基线：幅度取 ±0.05~±0.1 微调级（§九c：±5-10% 量级偏移），不作主机制。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §4.2 标签组合「敏化-威胁 + 反刍」在 5/7 参数上直接一致，DA_VTA/DA_SNc 两参数为标签未覆盖的**边证据直调**（奖赏域解耦是精分核心病理，标签界面无对应项，走 §4.3 粒度2 参数直调）。

## 目录

1. [文献锚点（4 篇核心 + 偏侧 3 篇 + 关键数据点）](#一文献锚点4-篇核心--偏侧-3-篇--关键数据点)
2. [50 实体病理边表（21 条，含三体边核验列）](#二50-实体病理边表21-条含三体边核验列)
3. [7 参数映射建议（4 tone + 3 CSTC）](#三七参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）](#五行为覆盖非线性跳变保留清单panss-五因子挂接)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（4 篇核心 + 偏侧 3 篇 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **ENIGMA SZ — Van Erp et al. (2016)** *Biol Psychiatry*（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §3.2/§七 精神分裂症） | 结构 mega-meta | 海马 d=−0.4、杏仁核 d=−0.3、丘脑 d=−0.3、NAcc↓、苍白球↑、侧脑室 d=+0.3 → 记忆/防御/奖赏/行动门控域边的**结构锚 + 方向**（e07/e08/e10/e12/e20/e21） |
| 2 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者，跨诊断 ALFF meta，§2.1/§2.3） | 静息态 ALFF meta | **SZ 特异性**：ALFF↑ 纹状体/IFG/ACC-mPFC；ALFF↓ 中央前后回/旁中央小叶；共享：杏仁核/岛叶 ALFF↑ → 纹状体 gate 过度耦合（e18/e19）、ACC-mPFC 过度激活（e04/e13）、M1↔S1 解耦（e21）、杏仁核-海马耦合↑（e10） |
| 3 | **Fountoulakis et al. (2019)** *Int J Neuropsychopharmacol*（§五） | PANSS 五因子+四阶段分期 | 五因子（阴性/阳性/抑郁焦虑/兴奋敌意/神经认知）全可卷入；1 期阳性主导 → 4 期全卷入 → §五 行为覆盖/跳变的 **PANSS 因子挂接**（偏执型以阳性因子为行为主挂接） |
| 4 | **Fan & Tan (2022)** DMN-FPN 反相关消失（[文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 精神分裂症 整合域） | 静息态 trait marker | DMN-FPN **反相关消失** = 精分 trait marker → e05（mOFC↔dlPFC 解耦沉默，旧「边界崩溃」语义继承）+ §五 整合域跳变（L5 叙事重构不可用） |

**偏侧 3 篇（ENIGMA 偏侧化文献数据源，SZ 必须用非零 laterality_delta）：**

| # | 文献 | 关键数据点（→ 偏侧 Δ 用途） |
|---|------|--------------------------|
| 5 | **Schijven et al. (2023)** *PNAS*（5,080 SZ + 6,015 CTR，§三） | **rACC 厚度偏侧反转** d=−0.083（对照左偏→病例右偏，左皮层更薄驱动）→ e04/e13 Δ=−0.05；**MTG 左皮层薄** d=−0.074（右偏增大，幻听关联，Plaze 2018 佐证）→ e02 Δ=−0.1 |
| 6 | **Okada et al. (2016)** *Mol Psychiatry*（884 SZ + 1,680 CTR，§四） | **苍白球体积左偏**（SZ 特异，对照组无此偏侧）→ e20 Δ=−0.05；健康偏侧基线：海马/杏仁核右偏、丘脑左偏 → e03/e10/e11/e12 Δ 方向参照 |
| 7 | **Gutman et al. (2022)** *Hum Brain Mapp*（2,833 SZ + 3,929 CTR，§五） | **海马/杏仁核/丘脑偏侧夸大**（偏侧指数差 d=0.05~0.15）→ 皮层下边群 e03（丘脑 Δ=−0.05）、e10/e11/e12（海马/杏仁核 Δ=+0.05） |

**辅助锚（方向/范围补充）**：

- **Kong et al. (2018)** *PNAS*（17,141 健康人，§二）——语言区偏侧最强（额下回岛盖部/颞横回/颞上回左偏），为 SZ 左语言网络异常偏移的**正常偏侧参照系** → e01/e02/e16 语言边群 Δ 的基线锚；利手与皮层偏侧无显著关联 → 游戏可忽略利手混杂。
- **P50 听觉门控障碍**（SZ 最可复现的感觉门控发现）——丘脑听觉中继门控失败 → e03（Thalamus→transversetemporal 过度耦合）承载「感官过载」+ link_318 语义转移。
- **中脑皮层 DA 假说**（Davis et al. 1991 经典框架）——皮层 DA 功能低下 → 阴性/认知症状 → e06（VTA→rostralmiddlefrontal 结构异常）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——15 条旧链路的方向/量级/通路描述作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，偏离处标注 `[NEW]`。**偏侧豁免声明**：ENIGMA 偏侧化 §6.5 规则 4「|d|<0.1 不做」对 SZ 豁免——SZ 是唯一达到大样本稳健偏侧证据的疾病（§九a），幅度取微调级 ±0.05~±0.1（§九c 结论），不作主机制。

---

## 二、50 实体病理边表（21 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点）；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`。**21 条全部命中三体模型现有边**（cstc 47 + corticocortical 776 + brainstem 114 + privileged_pathways 112），0 条「病理新增」（§6.4 语义转移优先；本文件仅 link_318 一例语义转移，余为端点直配或 ⭐新增）。CGI-S 3-7 → 档位过滤 B′ 三档全可用。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（`paranoid-schizophrenia`）。三档 m 偏移 = 轻/中/重，|m| ≤ 0.6；laterality_delta 负=左偏、正=右偏（§6.5），SZ 偏侧幅度取微调级 ±0.05~±0.1。

### 2.1 语言/感觉域（4 条）——「内在点燃：幻觉 + 感官过载」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e01** | parsopercularis | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1723 | 解耦沉默 | 0/−0.2/−0.4 | **−0.05** | 旧 link_116_L（Broca↔Wernicke，旧「结构异常」→ §6.3 机械重分类）；Kong 2018 Broca/STG 左偏基线；Guo 2026 IFG ALFF↑ | 行为覆盖②（语言社会域 m_max 上限成员） |
| **paranoid-schizophrenia_e02** ⭐新增 | superiortemporal | middletemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5576 | 过度耦合 | +0.2/+0.4/+0.6 | **−0.1** | Schijven 2023（MTG 左薄 d=−0.074，幻听关联 Plaze 2018）；Kong 2018（STG/颞平面左偏最强）——**幻听核心边** | 行为覆盖②（语言社会域 m_max > 0.5 → Broca 紊乱）+ 跳变① |
| **paranoid-schizophrenia_e03** | Thalamus-Proper | transversetemporal | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+2（MGN→A1） | 过度耦合 | +0.2/+0.4/+0.6 | **−0.05** | link_318 **语义转移**（SC→Thalamus 无直连，见 §四）；P50 听觉门控失败（SZ 最可复现感觉门控发现）；Gutman 2022 丘脑偏侧夸大 | 行为覆盖① + 跳变①（感觉域 m_max = 0.6 重档） |
| **paranoid-schizophrenia_e21** ⭐新增 | precentral | postcentral | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.7590 | 解耦沉默 | 0/−0.1/−0.2 | 0 | Guo 2026（SZ 特异性 ALFF↓ 中央前后回）→ M1↔S1 感觉运动整合↓ | 阴性侧翼（动作迟缓） |

### 2.2 认知控制/整合域（3 条）——「ACC↔rACC 锁定 + DMN-FPN 反相关消失」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e04** | caudalanteriorcingulate | rostralanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5879（**端点含 caudalanteriorcingulate = 任务指定 rACC 反转 Δ 载体**） | 过度耦合 | +0.2/+0.4/+0.6 `[NEW 校准]` | **−0.05** | 旧 link_007_L（ACC↔rACC 闭环锁定）；Schijven 2023 **rACC 偏侧反转**（d=−0.083）；Guo 2026 ACC-mPFC ALFF↑（SZ 效应最强） | 跳变③（认知控制域 m_max = 0.6 → dlPFC 压制失效）+ bias_cognitive 锚 |
| **paranoid-schizophrenia_e05** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默 | −0.1/−0.2/−0.4 | 0 | 旧 link_082_L（旧「边界崩溃」→ §6.3 机械重分类）；Fan&Tan 2022 DMN-FPN 反相关消失 trait marker | 跳变②（整合域 \|m\| > 0.3 → SN 无法切换, L5 叙事重构不可用） |
| **paranoid-schizophrenia_e06** ⭐新增 | VentralTegmentalArea | rostralmiddlefrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **结构异常** | −0.1/−0.2/−0.3 | 0 | 中脑皮层 DA 腿选择性受损（Davis 1991 mesocortical hypodopaminergia；旧文件「已知链路缺口」VTA→vmPFC 同类投影）；§6.3 结构异常 subtype (b) | DA_VTA tone 推导锚（负项） |

### 2.3 奖赏域（2 条）——「VTA→NAcc 解耦沉默」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e07** | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 解耦沉默 | −0.2/−0.4/−0.6 | 0 | 旧 link_336（VTA→NAcc 中脑边缘 DA，Schultz 1997）；ENIGMA NAcc↓；RDoC 腹侧纹状体预测误差消失 | DA_VTA tone 推导锚（主项） |
| **paranoid-schizophrenia_e08** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.2/−0.4 | 0 | 旧 link_344（SNc→壳核 黑质纹状体 DA，Paxinos 2004） | DA_SNc tone 推导锚 |

### 2.4 防御/记忆域（4 条）——「海马/杏仁核结构↓ + 偏侧夸大」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e09** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939；**注**：dk 节点 L2，但含 L5 fid（FrontalPoleSN）→ L5 叙事监控↔L1 记忆提取直连 | **跨层短路** | 0/+0.2/+0.3 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89 L）；Guo 2026 ACC-mPFC ALFF↑（旧「过度耦合」→ §6.3 规则 b 机械重分类） | 妄想记忆绑定（叙事层） |
| **paranoid-schizophrenia_e10** ⭐新增 | Amygdala | Hippocampus | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.6506 | 过度耦合 | +0.1/+0.2/+0.3 | **+0.05** | Guo 2026 共享杏仁核 ALFF↑；Gutman 2022 海马/杏仁核偏侧夸大（右偏方向，Okada 2016 基线）→ 被害妄想记忆条件化 | 行为覆盖侧翼（威胁记忆） |
| **paranoid-schizophrenia_e11** | DorsalRapheNucleus | Hippocampus | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | 过度耦合 | 0/+0.1/+0.2 | **+0.05** | 旧 link_319（中缝背核→海马 5-HT，脑干强度估计 fc=0.75，旧「结构异常」→ 正 m 广播边机械重分类）；Gutman 2022 海马偏侧夸大 | 5HT tone 推导锚（聚焦腿） |
| **paranoid-schizophrenia_e12** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/0/+0.3 | **+0.05** | 旧 link_312（PAG→杏仁核中央核，LeDoux 2000 / Paxinos 2004）；Gutman 2022 杏仁核偏侧夸大 | 威胁超敏侧翼（重档才激活） |

### 2.5 内感受/唤醒域（3 条）——「岛叶-ACC 显著网络（SZ 最强）+ LC NE 广播」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e13** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | +0.2/+0.3/+0.5 | **−0.05** | 旧 link_155_L + link_160（rACC↔前脑岛，**L/R 合并**）；Guo 2026 岛叶 ALFF↑（跨六病共享，**精分效应最强**，旧思路链）；Schijven 2023 rACC 反转 | 行为覆盖侧翼（内感受警觉）+ bias_limbic 锚 |
| **paranoid-schizophrenia_e14** | LocusCoeruleus | caudalanteriorcingulate | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 旧 link_327（蓝斑→ACC NE，脑干强度估计 Fig5 对应社区） | NE tone 推导锚 + 行为覆盖① |
| **paranoid-schizophrenia_e15** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_326（蓝斑→前脑岛 NE，脑干强度估计 fc=0.85（PINK 最强 hub）） | NE tone 推导锚（次项） |

### 2.6 语言社会域/整合（2 条）——「ToM 网络 + 反刍自我参照」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e16** | medialorbitofrontal | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2822 | 过度耦合 | +0.1/+0.2/+0.4 | **−0.05** | 旧 link_084_L（vmPFC↔Wernicke，ToM 网络）；Guo 2026 共享 IFG/ACC-mPFC ALFF↑ | 行为覆盖②（语言社会域成员）+ 跳变①作用域 |
| **paranoid-schizophrenia_e17** | inferiorparietal | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2145 | 解耦沉默 | 0/−0.2/−0.3 | 0 | 旧 link_047_L（角回→mPFC，Reward 网络）；反刍自我参照整合↓ | 反刍标签支撑 |

### 2.7 行动门控域（3 条）——「纹状体 gate 过度耦合 + 苍白球左偏」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **paranoid-schizophrenia_e18** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Guo 2026（SZ 特异性 ALFF↑ 纹状体 + ACC-mPFC）→ 认知环路 gate 被 ACC 锁定信号劫持 | bias_cognitive 推导锚 |
| **paranoid-schizophrenia_e19** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Guo 2026 共享纹状体 ALFF↑ + 杏仁核 ALFF↑ → 边缘环路 gate 被威胁信号劫持 | bias_limbic 推导锚 |
| **paranoid-schizophrenia_e20** ⭐新增 | Pallidum | Thalamus-Proper | cstc | ✅ 命中：somatic 环路 `disinhibition`, pallidal_output→thalamic_relay | 过度耦合 | 0/+0.1/+0.2 | **−0.05** | ENIGMA SZ 苍白球↑；Okada 2016 **苍白球左偏（SZ 特异）**；Schijven 2023 苍白球年龄×诊断交互 d=0.081 | 结构修饰（节点 m 直调层，不升格 CSTC bias，见 §三.1 注） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 负 = 左偏、正 = 右偏（§6.5 规则 1）；SZ 偏侧幅度 ±0.05~±0.1 = ENIGMA 偏侧化 §九c 微调级（|d|<0.1 的豁免声明见 §一）；`[NEW 校准]` = 偏离旧文件数值（0.2/0.3/0.5 → 0.2/0.4/0.6，使旧「认知控制域 >0.6」跳变在 |m|≤0.6 上限下可达）。脑干核团双侧合并主变体（LC/DR/VTA/SNc）Δ=0。

---

## 三、7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD 试点 §6.6 复制）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（NPC AI §4.1）。**bias 推导细化**：bias 从 CSTC `striatal_gate` 级腿（cortical_input→striatal_gate / striatal_gate→pallidal_output）推导；pallidal_output→thalamic_relay（如 e20）为结构输出腿，落节点 m 直调层（§4.3 粒度3），不升格 gate 偏置。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e14（LC→ACC +0.1/+0.2/+0.3）、e15（LC→insula 0/+0.2/+0.3） | LC 出边群 2/2 命中且 m 随严重度升高 → 蓝斑 NE 广播全局上调（过度警觉，RDoC 唤醒域） |
| 2 | DA_VTA_baseline | **−0.1** | e07（VTA→NAcc −0.2/−0.4/−0.6）、e06（VTA→rostralmiddlefrontal −0.1/−0.2/−0.3） | VTA 出边群 2 条均负偏移：NAcc 腿 = 中脑边缘 DA 预测误差消失（RDoC），dlPFC 腿 = 中脑皮层 DA 功能低下 → DA_VTA ↓ |
| 3 | DA_SNc_baseline | **−0.1** | e08（SNc→Putamen 0/−0.2/−0.4） | SNc 出边群负偏移 → 运动启动基线↓（动作迟缓/阴性成分） |
| 4 | 5HT_baseline | **−0.2** | e11（DR→Hippocampus 0/+0.1/+0.2 过度耦合） | 中缝核 5-HT 传递异常**聚焦**记忆回路 → 全局基线↓（低 5HT = 去抑制，Soubrié 1986；PTSD 试点 e08/e11 同判例） |
| 5 | bias_somatic | **0** | 无 striatal_gate 级 somatic 环路边命中 | e20 为 pallidal_output 结构腿（节点 m 直调层），不达 bias 校准阈值（±0.15 起）；无「过度抑制」标签 |
| 6 | bias_cognitive | **+0.15** | e18（ACC→Caudate cognitive `go_direct` +0.1/+0.2/+0.3）、e04（ACC↔rACC 锁定环为 cognitive 环路 cortical_input 成员） | 认知环路 striatal_gate 正偏移 → 语言/认知行动 gate 偏置↑（反刍标签一致） |
| 7 | bias_limbic | **+0.15** | e19（Amygdala→Accumbens-area limbic `go_direct` +0.1/+0.2/+0.3）、e13（rACC↔insula）、e12（PAG→Amygdala） | 边缘环路 gate 被威胁/记忆信号劫持 → 情绪/本能行动倾向↑（敏化-威胁标签一致） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」+「反刍」双标签（多标签叠加取最大值，clamp 值域；标签未覆盖参数走 §4.3 粒度2 参数直调）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| DA_VTA_baseline | 0（标签未覆盖） | −0.1 | ⚠️ 标签外直调：奖赏域解耦（e07/e06）是精分核心病理，标签界面无对应项 → 参数直调（§4.3 粒度2），边证据独立成立 |
| DA_SNc_baseline | 0（标签未覆盖） | −0.1 | ⚠️ 标签外直调：同上（e08 黑质纹状体腿解耦） |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | +0.15（反刍） | +0.15 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：偏执型病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（5/7 标签直接覆盖；DA_VTA/DA_SNc 为有边证据的标签外直调——敌我同构下「标签是设计师简写、参数是底层真相」的合法扩展，NPC AI §4.2 末注）。**偏执型 NPC 最终参数：NE=0.5、DA_VTA=0.3、DA_SNc=0.4、5HT=0.3、bias_cognitive=+0.15、bias_limbic=+0.15（其余基线）**。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 解耦沉默 −0.2/−0.4/−0.6 | **paranoid-schizophrenia_e07**（VentralTegmentalArea→Accumbens-area） | ✅ 保留语义（fid 合并：NucleusAccumbens → 节点 Accumbens-area） |
| link_344 | SubstantiaNigraParsCompacta→Putamen | 解耦沉默 0/−0.2/−0.4 | **paranoid-schizophrenia_e08** | ✅ 保留语义 |
| link_007_L | ACC(L)→RostralAnteriorCingulateCortex | 过度耦合 +0.2/+0.3/+0.5 | **paranoid-schizophrenia_e04**（caudalanteriorcingulate↔rostralanteriorcingulate） | ⚠️ 量级校准 `[NEW]` 0.2/0.4/0.6（使认知控制跳变可达）+ **偏侧显式化**（rACC 反转 Δ=−0.05） |
| link_327 | LocusCoeruleus→AnteriorCingulateCortex | 过度耦合 +0.1/+0.2/+0.3 | **paranoid-schizophrenia_e14** | ✅ 保留语义 |
| link_155_L | RostralAnteriorCingulateCortex→Insula | 过度耦合 +0.2/+0.3/+0.5 | **paranoid-schizophrenia_e13**（rACC↔insula） | ✅ 保留语义（**与 link_160 合并**，L/R 后缀入 Δ=−0.05） |
| link_160 | RostralAnteriorCingulateCortex→Insula | 过度耦合 +0.2/+0.3/+0.5 | 并入 **paranoid-schizophrenia_e13** | ⚠️ 合并（三体图无 L/R 分边，同对端点合一） |
| link_326 | LocusCoeruleus→Insula | 过度耦合 0/+0.2/+0.3 | **paranoid-schizophrenia_e15** | ✅ 保留语义 |
| link_318 | SuperiorColliculus→Thalamus | 过度耦合 +0.1/+0.2/+0.4 | **无直连边**（三体图无 SC→Thalamus-Proper，旧链路 registry 数据为经丘脑枕中继） | ⚠️ **废弃直连**；语义转移至 **e03**（Thalamus-Proper→transversetemporal 丘脑听觉中继过度耦合 = P50 门控失败） |
| link_084_L | MedialOrbitalPrefrontalDMN→SuperiorTemporalWernicke | 过度耦合 +0.1/+0.2/+0.4 | **paranoid-schizophrenia_e16**（medialorbitofrontal↔superiortemporal） | ✅ 保留语义 + 偏侧显式化（Δ=−0.05） |
| link_116_L | ParsOpercularis→SuperiorTemporalWernicke | 结构异常 0/−0.2/−0.4 | **paranoid-schizophrenia_e01**（parsopercularis↔superiortemporal） | ⚠️ **类型重分类**：CC 合法边 m 负偏移 → 解耦沉默（§6.3）；偏侧显式化（Δ=−0.05） |
| link_047_L | InferiorParietalAngular→SuperiorFrontalMPFC | 解耦沉默 0/−0.2/−0.3 | **paranoid-schizophrenia_e17**（inferiorparietal↔superiorfrontal） | ✅ 保留语义（fid 合并） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 边界崩溃 −0.1/−0.2/−0.4 | **paranoid-schizophrenia_e05**（medialorbitofrontal↔rostralmiddlefrontal） | ⚠️ **类型重分类**：五分类→四分类，「边界崩溃」语义（DMN-FPN 反相关消失）转移至挂接/跳变（§五），类型按 §6.3 = 解耦沉默 |
| link_003_L | AnteriorCingulateCortex→Parahippocampal | 过度耦合 0/+0.2/+0.3 | **paranoid-schizophrenia_e09**（caudalanteriorcingulate↔parahippocampal） | ⚠️ **类型重分类**：CC 端点含 L5 fid（FrontalPoleSN）+ 对端 L1 → 跨层短路（§6.3 规则 b） |
| link_319 | DorsalRapheNucleus→HippocampusCA1 | 结构异常 0/+0.1/+0.2 | **paranoid-schizophrenia_e11**（DorsalRapheNucleus→Hippocampus） | ⚠️ **类型重分类**：brainstem 广播正 m → 过度耦合（PTSD e08 同判例）；fid 合并 |
| link_312 | PeriaqueductalGray→Amygdala | 过度耦合 0/0/+0.3 | **paranoid-schizophrenia_e12** | ✅ 保留语义 + 偏侧显式化（Δ=+0.05 杏仁核右偏夸大） |
| （旧表无） | STG↔MTG 听觉语言环路点燃（思路链「感觉域被内在信号点燃」） | — | **paranoid-schizophrenia_e02** | ⭐ 新增——幻听核心边（Schijven 2023 MTG 左薄） |
| （旧表无） | 中脑皮层 DA 腿受损（旧「已知链路缺口」VTA→vmPFC 同类） | — | **paranoid-schizophrenia_e06** | ⭐ 新增——结构异常（§6.3 subtype b） |
| （旧表无） | 杏仁核-海马 妄想记忆条件化（Guo 2026 杏仁核 ALFF↑ + Gutman 偏侧夸大） | — | **paranoid-schizophrenia_e10** | ⭐ 新增 |
| （旧表无） | ACC→尾状核 cognitive gate 被劫持（Guo 2026 纹状体+ACC ALFF↑） | — | **paranoid-schizophrenia_e18** | ⭐ 新增——bias_cognitive 机制锚 |
| （旧表无） | 杏仁核→NAcc limbic gate 被威胁劫持（Guo 2026 共享纹状体 ALFF↑） | — | **paranoid-schizophrenia_e19** | ⭐ 新增——bias_limbic 机制锚 |
| （旧表无） | 苍白球→丘脑 行动门控结构异常（ENIGMA 苍白球↑ + Okada 2016 左偏） | — | **paranoid-schizophrenia_e20** | ⭐ 新增——偏侧 Δ 载体 |
| （旧表无） | M1↔S1 感觉运动整合↓（Guo 2026 ALFF↓ 中央前后回） | — | **paranoid-schizophrenia_e21** | ⭐ 新增 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_318 → e03）；类型冲突 → **§6.3 机械重分类**（link_116_L/082_L/003_L/319 四例）；「病理新增」从严（本文件 0 条，新增边全部命中现有边）。

---

## 五、行为覆盖/非线性跳变保留清单（PANSS 五因子挂接）

> PANSS 五因子（Fountoulakis 2019 §5.1）：阴性 / 阳性 / 抑郁焦虑 / 兴奋敌意 / 神经认知。偏执型以**阳性 + 兴奋敌意**为主挂接（1 期阳性主导，§5.2 分期）。

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| SAN < 30 → L5 叙事重构不可用 | ✅ 保留 | **全局**（L5 叙事重构依赖的 L5 边群：e05/e04/e06 任一 \|m\| 重档） | 全因子（4 期全卷入，§5.2） | 同 PTSD 试点；病程晚期认知衰退主导 |
| 感觉域 m_max > 0.6 → 目标选择随机化 15% | ✅ 保留（阈值收敛） | **感觉域边群**（e03 m_max = 0.6 重档 + e21） | 神经认知（概念紊乱/注意缺陷） | 旧「>0.6」与 |m|≤0.6 上限收敛为「= 0.6 重档锁定」`[NEW]` |
| 语言社会域 m_max > 0.5 → Broca 区输出 5% 紊乱（随机替换为语言攻击） | ✅ 保留 | **语言域边群**（e02 m_max = 0.6 重档 > 0.5；e01/e16 成员） | 阳性（幻觉/不寻常思维内容） | 幻听核心（Schijven 2023 MTG 左薄 ↔ Plaze 2018 幻听） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | PANSS 因子 | 说明 |
|--------|:---:|--------|-----------|------|
| 感觉域 m_max > 0.6 → 强制激活不可被 L5 压制，SAN −2/回合（作用域 link_318, link_084_L） | ✅ 保留（改作用域） | **e03** m = 0.6（重档），作用域 = e03 + e16 | 阳性 + 兴奋敌意 | link_318 语义转移至 e03；link_084_L → e16 |
| 整合域 \|m\| > 0.3 → SN 无法在 DMN/FPN 间切换 → L5 叙事重构不可用（作用域 link_082_L） | ✅ 保留 | **e05** \|m\| = 0.4（重档）> 0.3 | 神经认知（抽象思维困难） | Fan&Tan 2022 DMN-FPN 反相关消失 trait marker |
| 认知控制域 m_max > 0.6 → dlPFC 自上而下控制压制 L1-L2 失效（作用域 link_007_L） | ✅ 保留（阈值收敛） | **e04** m = 0.6（重档；`[NEW 校准]` 0.2/0.4/0.6） | 兴奋/敌意（冲动控制差）+ 神经认知 | ACC↔rACC 锁定环；rACC 反转 Δ 同边承载 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 3（核心） | link_336, link_007_L, link_155_L, link_160, link_318, link_084_L, link_116_L, link_082_L | **e07, e04, e13, e03, e16, e01, e05**（+ e02 幻听核心，待 #88 组件批次再平衡） |
| 2（关联） | link_344, link_327, link_326, link_047_L, link_003_L, link_319 | **e08, e14, e15, e17, e09, e11**（+ e18, e19） |
| 1（边缘） | link_312 | **e12**（+ e06, e10, e20, e21） |

> 核心 7 条 = 奖赏解耦核心（e07）+ 认知锁定核心（e04）+ 显著网络核心（e13）+ 感官过载核心（e03）+ ToM 过度耦合（e16）+ 语言解耦（e01）+ 整合崩溃（e05）。新增边中 e02 落核心（幻听）、e18/e19 落关联（bias 锚）、e06/e10/e20/e21 落边缘。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6 | §二 |
| 偏侧偏离量 | laterality_delta | 0 默认；SZ 微调级 ±0.05~±0.1（10 条非零） | §二（ENIGMA 偏侧化 §九c） |
| NE 基线偏离 | ΔNE_baseline | +0.2（0.3 → 0.5） | §三 |
| DA_VTA 基线偏离 | ΔDA_VTA_baseline | −0.1（0.4 → 0.3，标签外直调） | §三 |
| DA_SNc 基线偏离 | ΔDA_SNc_baseline | −0.1（0.5 → 0.4，标签外直调） | §三 |
| 5HT 基线偏离 | Δ5HT_baseline | −0.2（0.5 → 0.3） | §三 |
| CSTC 偏置 | bias_cognitive / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 感觉域过载阈值 | m_th | 0.6（e03 重档，目标随机化 15%，SAN −2/回合） | §五 |
| 语言域紊乱阈值 | m_th | 0.5（e02 重档 >0.5，Broca 紊乱 5%） | §五 |
| 整合域跳变阈值 | m_th | 0.3（e05 \|m\| 重档 0.4，L5 叙事重构不可用） | §五 |
| 认知控制锁定阈值 | m_th | 0.6（e04 重档，dlPFC 压制失效） | §五 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [grilling-88.md](../disease-pilots/grilling-88.md), [偏执型精神分裂症](../../../entities/diseases/%E5%81%8F%E6%89%A7%E5%9E%8B%E7%B2%BE%E7%A5%9E%E5%88%86%E8%A3%82%E7%97%87.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [ENIGMA偏侧化-精神疾病大样本meta-文献数据源](../../../../reference/literature/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §三/§四/§五/§九, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
