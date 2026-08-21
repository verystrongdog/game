# 广泛性焦虑障碍（GAD）重映射试点

> Grilling #88 试点批——GAD（disease_id=`gad`，CGI-S 3-6）。旧 7 条链路（link_312 等，挂已废弃 link_registry.json）重映射为三体模型上的 **12 条病理边**（12 条全部命中 `tripartite_model.json` 现有边，0 条"病理新增"；其中 4 条 ⭐新增边均命中现有边；2 条旧链路无直连 → 语义转移）。核心病理 = **泛化持续**（vs PTSD 跨层短路、特定恐惧刺激特异、惊恐发作性突发）：防御域 PAG→杏仁核 上行放大（日常刺激被解读为威胁）+ 唤醒域蓝斑持续警觉（"关不掉的担忧引擎"，BNST 无三体节点 → 语义由 LC 广播边群承载）+ 内感受域前脑岛过敏 + DMN 内连接增强（Pierce & Black 2023 持续性担忧的神经基础）+ 前额叶调控轻度减弱（< PTSD 严重度）。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §4.2 标签「敏化-威胁」完全一致。**B′ 档位过滤（#88 待定项1 定案）：CGI-S 3-6 无重档 → 全部边仅轻/中两档（|m| ≤ 0.3）；laterality_delta 全部 0（无稳健偏侧证据）。**

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [GAD → 7 参数映射建议（4 tone + 3 CSTC）](#三gad--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_312 等 → 新病理边）](#四旧链路对照表link_312-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Pierce & Black (2023)** *J Affect Disord Rep* | ALE meta（30 研究） | **DMN 内部连接↑ 与焦虑严重度正相关** → DMN 内连接边群（gad_e07~e10）——持续性担忧的神经基础 |
| 2 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者） | 跨诊断 ALFF meta | 焦虑障碍 ALFF↑ = **双侧岛叶（尤其前岛叶）+ ACC/mPFC + 杏仁核 + 纹状体**（[疾病-脑区链路映射-文献数据源.md](../../参考/文献/疾病-脑区链路映射-文献数据源.md) §2.1 共享模式）→ 内感受/防御/行动门控边群方向（gad_e06/e12） |
| 3 | **2023 MKDA meta**（*Eur Psychiatry*） | 额边缘模型 meta | **前额叶-边缘系统过度耦合 + 前额叶对杏仁核自上而下调控减弱** → 认知控制轻度减弱（gad_e11 解耦，< PTSD 严重度） |
| 4 | **RDoC v4（NIMH）** | 回路矩阵 | 急性威胁回路：杏仁核→vmPFC/dmPFC/ACC + **dPAG**（→ gad_e01 防御锚）；**唤醒/调节域：蓝斑 NE**（→ gad_e02/e03 唤醒锚） |

**辅助锚（方向/范围补充）**：

- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——7 条旧链路（link_312/332/320/326/155_L/008_L/131_L）的方向/量级作为语义继承源，见 §四。
- **BNST 无三体节点**——旧文件「蓝斑↑↑ BNST 持续警觉」（[广泛性焦虑障碍.md](../../实体/疾病目录/广泛性焦虑障碍.md) 思路链）中 BNST 的持续警觉语义由 **LC 广播边群（gad_e02/e03）承载**（语义转移，见 §四处置规则）。
- **左右脑偏侧化-文献数据源**——GAD 无稳健左右偏侧证据（Guo 2026 焦虑障碍仅落在共享模式，无 PTSD 式特异性左偏）→ **全部边 laterality_delta = 0**（§6.5 规则 2）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，**全部数值有来源，新增数值标记 `[NEW]`**；重档量级（旧值第三档）因 B′ 档位过滤（CGI-S 3-6 无重档）整体淘汰。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点）；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`。**12 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**——GAD 无正常图中不存在的连接。
>
> 边 ID 命名：`gad_e<NN>`。**B′ 档位过滤：CGI-S 3-6 → 无重档，m 仅轻/中两档**（旧文件第三档量级如 link_332 的 +0.5 整体淘汰）；量级沿用旧文件轻/中档设计校准。**laterality_delta 全部 0**——GAD 无稳健偏侧证据（§6.5 规则 2）。「病理新增」边类型规范见 [ptsd-pilot.md](ptsd-pilot.md) §6.4。

### 2.1 防御域（1 条）——「威胁解读上行放大」（非跨层短路）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e01** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1（L0→L1） | 过度耦合 | +0.1/+0.2 | 0 | 旧 link_312（PAG→杏仁核，LeDoux 2000 / Paxinos 2004）；RDoC 急性威胁 dPAG；[广泛性焦虑障碍.md](../../实体/疾病目录/广泛性焦虑障碍.md) 防御域↑（日常刺激被解读为威胁） | 行为覆盖①（泛化威胁解读） |

> **方向说明**：旧文件核心病理写作「杏仁核→PAG↑」，但 GAD 的防御域 = **威胁解读上行放大**（L0→L1 正向耦合），非 PTSD/惊恐式的 L1→L0 下行反射劫持（跨层短路保留给 PTSD 与惊恐发作）——四病机制区分的第一道分界。

### 2.2 唤醒域（2 条）——「蓝斑持续警觉」（BNST 语义转移）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e02** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | +0.1/+0.3 | 0 | 旧 link_332（蓝斑→杏仁核 NE，Hansen 2024 fc=0.7）；RDoC 唤醒域；[GAD 思路链](../../实体/疾病目录/广泛性焦虑障碍.md) 蓝斑 NE 持续激活 | 非线性跳变①（持续警觉锁定） |
| **gad_e03** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | +0.1/+0.2 | 0 | 旧 link_326（蓝斑→前脑岛 NE，Hansen PINK fc=0.85） | 行为覆盖①（内感受过度警觉） |

> BNST（终纹床核）无三体节点：旧文件「BNST 维持长时间警觉」语义由 LC 广播边群（gad_e02/e03）承载——持续警觉 = LC 全局 NE 上调，不新增节点（§四处置规则：语义转移优先）。

### 2.3 内感受域（2 条）——「前脑岛内感受过敏」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e05** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | +0.1/+0.2 | 0 | 旧 link_155_L（rACC→前脑岛，ENIGMA 6.29 L） | 行为覆盖②（假阳性威胁检测） |
| **gad_e06** ⭐新增 | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 过度耦合 | 0/+0.1 | 0 | Guo 2026 岛叶 ALFF↑（共享模式）；[GAD 思路链](../../实体/疾病目录/广泛性焦虑障碍.md) 心跳/呼吸/肌肉紧张被过度解读为危险信号 | 行为覆盖②（内感受→威胁闭环） |

### 2.4 调制域（1 条）——「5-HT 传递聚焦威胁回路」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e04** | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | 过度耦合 | 0/+0.2 | 0 | 旧 link_320（中缝背核→杏仁核 5-HT，Hansen PINK fc=0.7） | 3.1 节 5HT tone 推导锚 |

### 2.5 DMN 内连接域（4 条）——「持续性担忧引擎」（Pierce & Black 2023）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e07** | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2（L2→L4） | 过度耦合 | 0/+0.1 | 0 | 旧 link_131_L 语义转移（PCC→mPFC 自传体记忆，ENIGMA 9.76 L——无直连，见 §四）；Pierce & Black 2023 DMN 内连接↑ | 行为覆盖③（担忧持续） |
| **gad_e08** ⭐新增 | isthmuscingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2（L2→L4） | 过度耦合 | 0/+0.1 | 0 | Pierce & Black 2023（DMN 内连接↑与焦虑严重度正相关） | 行为覆盖③ |
| **gad_e09** ⭐新增 | precuneus | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.242 | 过度耦合 | 0/+0.1 | 0 | Pierce & Black 2023；DMN mPFC 腿（自传体/担忧） | 行为覆盖③ + 非线性跳变②（担忧反刍） |
| **gad_e10** ⭐新增 | posteriorcingulate | isthmuscingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5177 | 过度耦合 | 0/+0.1 | 0 | Pierce & Black 2023（DMN 核心 hub 强连接） | 行为覆盖③ |

### 2.6 抑制/调控域（2 条）——「前额叶调控轻度减弱」（< PTSD）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **gad_e11** | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | −0.1/−0.2 | 0 | 旧 link_008_L 语义转移（ACC→dlPFC 情绪调节，ENIGMA 5.23 L——无直连，见 §四）；2023 MKDA meta 前额叶对杏仁核调控减弱；[GAD 思路链](../../实体/疾病目录/广泛性焦虑障碍.md) 认知控制↓（< PTSD 严重度） | 行为覆盖④（L5 压制 −30%） |
| **gad_e12** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1 | 0 | Guo 2026 共享纹状体 ALFF↑（§2.1）；CSTC limbic 门控被持续威胁信号偏置 | 3.1 节 bias_limbic 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ = 0 = 无偏侧证据（GAD 无稳健左右偏侧，§6.5 规则 2）；「轻/中」两档 = B′ 档位过滤（CGI-S 3-6 无重档）。

---

## 三、GAD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（复制自 [ptsd-pilot.md](ptsd-pilot.md) §6.6）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（[NPC AI 行为模型.md](../../规则/技能树系统/NPC%20AI%20行为模型.md) §4.1）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e02（LC→Amygdala +0.1/+0.3）、e03（LC→insula +0.1/+0.2） | LC 出边群 2/2 命中正偏移且 m 随严重度升高 → 蓝斑 NE 广播全局上调 = 持续警觉（RDoC 唤醒域；"关不掉的担忧引擎"） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | GAD 不主要累及奖赏回路（担忧/警觉为轴，非奖赏轴） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e04（DR→Amygdala 0/+0.2 过度耦合） | 中缝核 5-HT 传递异常聚焦于威胁回路 → 全局 5HT 基线↓（低 5HT = 去抑制，Soubrié 1986；同 PTSD 推导链） |
| 5 | bias_somatic | **0** | 无 somatic 环路（Putamen）边群命中 | GAD 无运动启动异常——担忧是认知/情绪性的（vs 惊恐的运动输出超驱动） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）边群命中 | 前额叶调控减弱在特权通路层（e11 属 prefrontal_limbic），非 CSTC cognitive gate（同 PTSD 判定） |
| 7 | bias_limbic | **+0.15** | e12（Amygdala→Accumbens-area CSTC limbic GO）、e01（防御边群） | 边缘环路 gate 被持续威胁信号偏置 → 焦虑性回避/情绪行动倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」单标签（GAD 默认标签，[广泛性焦虑障碍.md](../../实体/疾病目录/广泛性焦虑障碍.md) 默认标签）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：GAD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。GAD NPC 最终参数：NE=0.5、5HT=0.3、bias_limbic=+0.15（其余基线）。**与 PTSD 的 7 参数差异 = bias_somatic（0 vs +0.15，PTSD 双标签含抑制不足）**；机制差异全在边层（GAD 无跨层短路/闪回记忆/LC→dlPFC 结构受损）。

---

## 四、旧链路对照表（link_312 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_312 | PAG→Amygdala | 过度耦合 +0.1/+0.2/+0.4 | **gad_e01**（PeriaqueductalGray→Amygdala） | ✅ 保留语义（端点/类型不变；重档 +0.4 按 B′ 过滤 → 轻/中 +0.1/+0.2） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 +0.1/+0.3/+0.5 | **gad_e02** | ✅ 保留语义（重档 +0.5 过滤 → +0.1/+0.3） |
| link_326 | LocusCoeruleus→Insula | 过度耦合 +0.1/+0.2/+0.3 | **gad_e03** | ✅ 保留语义（重档 +0.3 过滤 → +0.1/+0.2） |
| link_320 | DorsalRapheNucleus→Amygdala | 过度耦合 0/+0.2/+0.3 | **gad_e04** | ✅ 保留语义（重档 +0.3 过滤 → 0/+0.2） |
| link_155_L | RostralACC(L)→Insula | 过度耦合 +0.1/+0.2/+0.3 | **gad_e05**（rostralanteriorcingulate→insula） | ✅ 保留语义 + **偏侧显式化**（无偏侧证据 → Δ=0，原 L 后缀入字段不保留） |
| link_008_L | ACC(L)→dlPFC | 结构异常 0/−0.1/−0.2 | **无直连边**（CC 图无 caudalanteriorcingulate→rostralmiddlefrontal） | ⚠️ **废弃直连**；语义转移至 **gad_e11**（medialorbitofrontal→Amygdala 解耦 −0.1/−0.2，前额叶对杏仁核调控减弱——2023 MKDA meta 佐证） |
| link_131_L | PosteriorCingulate(L)→mPFC | 过度耦合 0/+0.1/+0.2 | **无直连边**（CC 图无 posteriorcingulate→superiorfrontal） | ⚠️ **废弃直连**；语义转移至 DMN 边群 **gad_e07**（PCC→precuneus dmn_core）+ **gad_e09**（precuneus→superiorfrontal，mPFC 腿补全） |
| （旧表无） | 杏仁核→前脑岛 内感受（思路链仅叙事层） | — | **gad_e06** | ⭐ 新增——Guo 2026 岛叶 ALFF↑ |
| （旧表无） | isthmuscingulate→precuneus（DMN hub 腿） | — | **gad_e08** | ⭐ 新增——Pierce & Black 2023 |
| （旧表无） | posteriorcingulate→isthmuscingulate（DMN 核心 hub） | — | **gad_e10** | ⭐ 新增——Pierce & Black 2023 |
| （旧表无） | 杏仁核→腹侧纹状体 威胁→门控偏置 | — | **gad_e12** | ⭐ 新增——bias_limbic 机制锚 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_008_L → e11、link_131_L → e07/e09），「病理新增」从严（须文献支持新连接存在，见 [ptsd-pilot.md](ptsd-pilot.md) §6.4）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接，阈值按档位重标定）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 唤醒域 m_max > 0.4 → 每回合额外激活一条唤醒域链路（持续性警觉），不可主动关闭 | ✅ 保留（阈值重标定 `[NEW]`） | **唤醒域边群**（gad_e02/gad_e03，m_max 取两档中档值，≥ 0.3 触发） | 旧阈值 0.4 落在重档（B′ 过滤后不存在）；重标定为**中档 0.3 触发**——GAD 泛化持续 = 持续警觉是常态而非重度特征 |
| 内感受域 m_max > 0.3 → 身体信号→威胁解读，每回合 5% 概率错误激活防御域链路（假阳性威胁检测） | ✅ 保留（阈值重标定 `[NEW]`） | **内感受域边群**（gad_e05/gad_e06，≥ 0.2 触发） | 旧阈值 0.3 落在重档；重标定为**中档 0.2 触发**（假阳性威胁检测 = GAD 泛化解读的核心玩法表达） |
| 认知控制域 \|m\| > 0.2 → L5 控制·主动 对 L1-L2 焦虑压制效力 −30% | ✅ 保留 | **gad_e11** \|m\| ≥ 0.2（中档 −0.2） | 同义替换（vmPFC→杏仁核 解耦，< PTSD 的结构性失效） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_332 m > 0.5 → 持续警觉锁定——唤醒域链路不可被任何自上而下机制抑制，SAN −1/回合 | ✅ 保留（阈值按档位重标定 `[NEW]`） | **gad_e02** m ≥ 0.3（中档）→ 持续警觉锁定，SAN −1/回合 | 旧阈值 0.5 落在重档（B′ 过滤后不存在）；重标定为中档 0.3——GAD 的"无法关掉的担忧引擎"在 3-6 范围即成立 |
| （旧表无） | — | **DMN 内连接边群**（gad_e07~e10）m_max ≥ 0.1（中档）→ 担忧反刍：每回合 20% 概率强制进入 DMN 内连接域激活（行动窗口跳过 10%） | ⭐ 新增——Pierce & Black 2023 担忧的神经基础落行为层（DMN 边群中档 m_max=0.1，阈值按可达性标定 `[NEW]`） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_332, link_312, link_326, link_155_L | **gad_e01, gad_e02, gad_e03, gad_e05** |
| 2（关联） | link_320, link_008_L, link_131_L | **gad_e04, gad_e07, gad_e08, gad_e09, gad_e10, gad_e11, gad_e12** |
| 1（边缘） | — | **gad_e06** |

> 核心 4 条 = 防御上行放大（e01）+ 唤醒持续警觉（e02/e03）+ 内感受过敏（e05）；DMN 担忧边群落关联权重（GAD 特色但非核心机制）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（GAD） | m_offset | **轻/中两档**（B′ 过滤无重档），m ∈ {0, +0.1, +0.2, +0.3, −0.1, −0.2}，\|m\| ≤ 0.3 | §二 |
| 偏侧偏离量（GAD） | laterality_delta | 0（全部边——无偏侧证据） | §二 |
| NE 基线偏离（GAD） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（GAD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（GAD） | bias_limbic | +0.15（值域 [−0.3,+0.3]） | §三 |
| 持续警觉锁定阈值 | m_th | 0.3（唤醒域边群，SAN −1/回合） | §五.2 |
| 假阳性威胁检测概率 | p_fp | 5%/回合（内感受边群 m ≥ 0.2 时） | §五.1 |
| 担忧反刍触发概率 | p_rum | 20%/回合（DMN 边群 m_max ≥ 0.1，行动窗口跳过 10%） | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [ptsd-pilot.md](ptsd-pilot.md), [广泛性焦虑障碍](../../实体/疾病目录/广泛性焦虑障碍.md), [NPC AI 行为模型](../../规则/技能树系统/NPC%20AI%20行为模型.md) §4.2/§5.2, [脑功能层级模型](../../规则/技能树系统/脑功能层级模型.md) §二十, [疾病-脑区链路映射-文献数据源](../../参考/文献/疾病-脑区链路映射-文献数据源.md) §七（焦虑障碍/GAD）, [tripartite_model.json](../../data/connectivity/tripartite_model.json), [link_registry.json](../../data/connectivity/link_registry.json)（⚠️ 已废弃）*
