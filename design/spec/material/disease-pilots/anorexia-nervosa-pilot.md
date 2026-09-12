# 神经性厌食症（AN）重映射试点

> 26 病重映射第 3 份试点（照 [PTSD 试点](../disease-pilots/ptsd-pilot.md) §六 字段规范复制）。本文件把旧 `link_155_L/160/326/336/338/008_L/007_L/147_L/343/331` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **11 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"）。核心病理 = **奖赏回路↓（解耦沉默）**（VTA→NAcc / VTA→mPFC）+ **认知控制↑（过度耦合）**（认知 CSTC 环路 dlPFC→Caudate，替代不存在的 ACC→dlPFC 直连）+ **内感受岛叶异常（混合方向）**（rACC→insula 解耦 + LC→insula 过度警觉）+ **自我参照↑**（楔前叶→mPFC）+ Datta 2025 组分3 苍白球。**AN 与 BN 为相反模式**：AN = 奖赏↓ 认知↑；BN = 奖赏↑ 认知↓（同边异号，§三.4 对照）。7 参数推导与 NPC AI §4.2/§5.2 标签组合「过度抑制 + 反刍」交叉验证：5HT/bias_cognitive/bias_somatic 一致，DA_VTA −0.2 与 DA_SNc +0.1 为**标签缺口裁决**（[NEW]，补 NPC AI 行为模型缺口）。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（新格式试点行，含三体边核验列）](#二50-实体病理边表新格式试点行含三体边核验列)
3. [AN → 7 参数映射建议（4 tone + 3 CSTC）](#三an--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_155_L 等 → 新病理边）](#四旧链路对照表link_155_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Datta et al. (2025)** fMRI meta | 三组分 meta | 组分1 楔前叶（视觉/体感）；组分2 屏状核/**岛叶后部**（味觉/自我参照）；组分3 **苍白球/mPFC/ACC**（奖赏/转换）→ 三域边集（e07 楔前叶、e03/e04 岛叶、e08 苍白球、e02/e05/e06 mPFC/ACC）的结构锚 |
| 2 | **Bronleigh et al. (2022)** *Psychiatry Res Neuroimaging* | ALE meta | **AN vs BN：AN 奖赏− 认知+（与 BN 完全相反）** → 奖赏域↓（e01/e02 解耦）+ 认知域↑（e05/e06 过度耦合）方向锚——本项目 AN/BN 相反模式的文献基础 |
| 3 | **Panarello et al. (2025)** | 纵向 fMRI | **岛叶功能障碍在体重恢复后仍持续**（trait marker）→ 内感受边（e03/e04）为稳定 trait，不随病程消退 |
| 4 | **Kaye et al. (2005)** 5-HT 综述 | 神经化学 | AN 5-HT 功能异常（5-HT 受体结合↑，trait 性）→ 过度抑制的 5HT +0.2 锚 + e11（DR→ACC 过度耦合） |

**辅助锚（方向/范围补充）**：

- **AN-OCD 强迫特征**（文献数据源 §七 OCD 对照）——强迫/僵化 → e09（SNc→Caudate 过度耦合，策略锁定）+ e08（苍白球 set-shift 僵硬）。
- **NPC AI §4.2**——标签「过度抑制」（5HT +0.2, bias_somatic −0.15）与「反刍」（NE −0.1, bias_cognitive +0.15）；§5.2「抑郁（快感缺失）」行 = 奖赏↓+认知↑先例（VTA→NAcc ↓, dlPFC 控制 ↑）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃）**——10 条旧链路的方向/量级（本仓脑干强度估计 / ENIGMA 连接强度）作为语义继承源，见 §四。
- **暴食-清除亚型（AN-BP）**——DSM-5 AN 含限制型与暴食-清除亚型；AN-BP 的循环跳变见 §五.2 [NEW]。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八）；m 偏移量级沿用旧文件设计校准，新增数值标记 `[NEW]`。AN 内感受域为**混合方向**（ACC-岛叶解耦 + LC-岛叶过度警觉，旧思路链"方向混合"）→ 两条独立边表达。

---

## 二、50 实体病理边表（新格式试点行，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像）。**11 条全部命中三体模型现有边，0 条"病理新增"**。旧 `link_008_L`（ACC→dlPFC）直连不在三体图 → **语义转移优先**：认知控制↑由认知 CSTC 环路（dlPFC→Caudate 过度耦合）承载；旧 link_155_L 与 link_160 同端点（rACC→insula）→ **并吞为单边**（取较重档 −0.1/−0.2/−0.4）。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（AN = `anorexia-nervosa`，主键前缀 `an`）。三档 m 偏移（frontmatter `CGI-S范围: 3-7` → 档位过滤 B′ 三档全）。laterality_delta 全部 0：Datta/Bronleigh/Panarello 均未报告稳健偏侧效应（旧 `_L` 后缀为 ENIGMA 单半球数据点，非偏侧证据——#92 合并双侧，Δ=0）。

### 2.1 奖赏域（2 条）——「奖赏回路↓ 解耦沉默」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **an_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（中脑边缘 DA 通路） | **解耦沉默** | −0.1/−0.3/−0.5 | 0 | 旧 link_336（VTA→NAcc，fc=0.9）；Bronleigh 2022 AN 奖赏− | 行为覆盖②（食物/奖赏趋近不可用） |
| **an_e02** | VentralTegmentalArea | superiorfrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（→mPFC 奖赏价值整合） | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_338（VTA→mPFC，fc=0.6，本仓脑干强度估计）；食物奖赏价值被认知抑制 | 3.1 节 DA_VTA 推导锚 |

### 2.2 内感受域（2 条）——「岛叶异常（混合方向）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **an_e03** ⭐核心 | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.4246 | **解耦沉默** | −0.1/−0.2/−0.4 | 0 | 旧 link_155_L + **并吞 link_160**（rACC→前脑岛，ENIGMA 6.29/3.66）；Panarello 2025 岛叶 trait | 行为覆盖① + 非线性跳变②（饥饿=控制成功） |
| **an_e04** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_326（LC→前脑岛 NE，fc=0.85，脑干强度估计·PINK 最强 hub）；身体信号被过度警觉放大 | 行为覆盖①（内感受过度警觉侧） |

### 2.3 认知控制域（2 条）——「认知控制↑ 过度耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **an_e05** ⭐转移 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **过度耦合** | +0.2/+0.3/+0.5 | 0 | 旧 link_008_L（ACC→dlPFC 过度耦合）**语义转移**（直连不在三体图）；Bronleigh 2022 AN 认知+ | 行为覆盖③ + 非线性跳变①（过度控制） |
| **an_e06** | caudalanteriorcingulate | rostralanteriorcingulate | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.5879 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 旧 link_007_L（ACC→ACC吻侧，ENIGMA 8.84）；认知-情绪监控过度（AN-OCD 强迫特征） | 行为覆盖③（作用域成员） |

### 2.4 自我参照/感觉域（3 条）——「楔前叶身体意象 + 苍白球 set-shift + 视觉警觉」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **an_e07** | precuneus | superiorfrontal | corticocortical | ✅ 命中：CC, dir=feedforward, level_diff=+1, edr=0.242 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 旧 link_147_L（楔前叶→mPFC，ENIGMA 9.97）；Datta 2025 组分1 楔前叶身体意象自我参照 | 行为覆盖①（身体意象偏差侧翼） |
| **an_e08** ⭐新增 | Pallidum | Thalamus-Proper | cstc | ✅ 命中：cognitive 环路 `disinhibition`, pallidal_output→thalamic_relay（somatic/limbic 孪生存在；CC 孪生 edr=0.6395 存在） | 过度耦合 | 0/+0.1/+0.2 | 0 | Datta 2025 组分3 苍白球（奖赏/转换）——set-shift 僵硬 | 3.1 节认知僵硬锚 |
| **an_e10** | LocusCoeruleus | pericalcarine | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_331（LC→V1 NE，fc=0.6，本仓脑干强度估计）；身体意象视觉监控警觉 | 行为覆盖①（视觉侧翼） |

### 2.5 行动门控/调制域（2 条）——「策略僵化 + 5HT↑ 过度抑制」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **an_e09** | SubstantiaNigraParsCompacta | Caudate | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast（黑质纹状体 DA 通路） | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_343（SNc→尾状核，fc=0.9，Paxinos2004）；AN-OCD 强迫特征 → 策略锁定 | 3.1 节 DA_SNc 推导锚 |
| **an_e11** ⭐新增 | DorsalRapheNucleus | caudalanteriorcingulate | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | Kaye 2005（AN 5-HT 功能↑/受体结合↑）；Crockett 2009（5HT 增强惩罚诱导行为抑制） | 3.1 节 5HT tone 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边）；⭐转移 = 旧链路直连不在三体图，按 §六.4 语义转移；Δ = 0（无稳健偏侧证据，旧 `_L` 后缀为 ENIGMA 单半球数据点，#92 合并双侧）。

---

## 三、AN → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD 模板 §六.6）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值（边推导） | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.1**（域特异，不取） | e04（LC→insula）、e10（LC→pericalcarine）过度耦合 | LC 出边群正偏移，但**集中于感觉/内感受域**（岛叶+V1）→ 域特异增益，不驱动全局 tone（§3.3 域特异裁决 [NEW]）→ NPC 取标签侧 −0.1 |
| 2 | DA_VTA_baseline | **−0.2** | e01（VTA→NAcc）、e02（VTA→mPFC）解耦 | VTA 出边群双负 → 奖赏回路↓（Bronleigh AN 奖赏−）；标签「过度抑制+反刍」无 DA↓ 标签 → 标签缺口裁决 [NEW] |
| 3 | DA_SNc_baseline | **+0.1** | e09（SNc→Caudate 过度耦合） | SNc→尾状核 DA↑ → 策略锁定/僵化（AN-OCD 强迫特征）→ 标签缺口裁决 [NEW] |
| 4 | 5HT_baseline | **+0.2** | e11（DR→ACC 过度耦合） | 中缝核 5-HT 广播↑ → 行为抑制/忍耐↑（Crockett 2009；Kaye 2005）——与「过度抑制」同向 |
| 5 | bias_somatic | **−0.15**（标签侧） | 无 somatic CSTC 边群命中 | 无边群佐证 → 以标签「过度抑制」−0.15 为准（规则 4：无矛盾） |
| 6 | bias_cognitive | **+0.15** | e05（dlPFC→Caudate cognitive GO 过度耦合）、e08（Pallidum→Thalamus cognitive disinhibition） | 认知 CSTC 环路过度激活 → 认知/语言行动倾向↑（反刍 + 过度控制）——与「反刍」同向 |
| 7 | bias_limbic | **0** | 无 limbic CSTC 边群命中 | AN 边缘环路无系统偏置（奖赏↓在脑干广播层表达） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「过度抑制」+「反刍」双标签（多标签叠加取最大值，clamp 值域；§5.2「抑郁（快感缺失）」行同向先例）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | −0.1（反刍：内转） | +0.1（e04/e10 LC 域特异正偏移） | ⚠️ **域特异裁决**：LC 边集中于内感受/感觉域 → 域特异增益不驱动全局 tone [NEW]；NPC 取 −0.1（反刍） |
| DA_VTA_baseline | 0 | −0.2（e01/e02 解耦） | ⚠️ **标签缺口裁决**：6 标签无"DA↓"标签（§5.2 已用「敏化-奖励(负)」表达但 §4.2 未定义映射）→ 采纳边推导 −0.2 [NEW] |
| DA_SNc_baseline | 0 | +0.1（e09 过度耦合） | ⚠️ **标签缺口裁决**：采纳边推导 +0.1（策略僵化）[NEW] |
| 5HT_baseline | +0.2（过度抑制） | +0.2（e11 过度耦合） | ✅ |
| bias_somatic | −0.15（过度抑制） | 0（无 somatic CSTC 边） | ✅（无边群命中，标签为准） |
| bias_cognitive | +0.15（反刍） | +0.15（e05/e08 过度耦合） | ✅ |
| bias_limbic | 0 | 0（无 limbic CSTC 边） | ✅ |

**结论**：AN 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合经**域特异裁决 + 标签缺口裁决**自洽。AN NPC 最终参数：**NE=0.2、DA_VTA=0.2、DA_SNc=0.6、5HT=0.7、bias_somatic=−0.15、bias_cognitive=+0.15、bias_limbic=0**。设计语义：AN NPC = 高 5HT（过度抑制）+ 低 DA（奖赏↓/无快感）+ 低 NE（内转反刍）+ 认知偏置↑——"静、僵、拒食"的敌我同构闭环。

### 3.3 域特异裁决规则（[NEW]，写入 §六.6 供 25 病复制）

> 触发条件：脑干广播边群的 m 偏移**集中于单一感觉/内感受域**（如 AN 的 LC→insula/pericalcarine），而非跨域发散（对照 PTSD 的 LC→Amygdala/insula/dlPFC 三域）。
> 裁决：域特异增益不驱动全局 tone 推导；全局 tone 以标签组合为锚。判断标准：出边群命中目标数 ≤ 2 且同属感觉/内感受域 → 域特异；≥ 3 域 → 全局。

### 3.4 AN vs BN 相反模式对照（任务硬性要求）

| 维度 | AN | BN | 表达边（同边异号） |
|------|----|----|------------------|
| 奖赏域 | ↓（解耦沉默） | ↑（过度耦合） | VTA→Accumbens-area（an_e01 解耦 vs bn_e01 过度耦合）；SNc→Caudate/Putamen（an_e09 过度耦合 vs bn_e02 过度耦合——注意 AN 的 + 为策略僵化侧） |
| 认知控制域 | ↑（过度耦合） | ↓（解耦沉默） | rostralmiddlefrontal→Caudate（an_e05 +0.2/+0.3/+0.5 vs bn_e06 −0.1/−0.2/−0.3） |
| 5HT | +0.2（过度抑制） | −0.2（抑制不足） | DR→ACC（an_e11 过度耦合 vs bn_e10 DR→insula 解耦） |

> 同一边（dlPFC→Caudate cognitive GO）在 AN 为过度耦合、在 BN 为解耦沉默——三体边复用 + 符号翻转即表达相反病理（Bronleigh 2022 原始结论）。

---

## 四、旧链路对照表（link_155_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_155_L | ACC吻侧(L)→前脑岛 | 解耦沉默 −0.1/−0.2/−0.4 | **an_e03**（rostralanteriorcingulate→insula） | ✅ 保留语义 + **并吞 link_160**（同端点 rACC→insula 无偏侧条目，取较重档）+ L 后缀取消（Δ=0） |
| link_160 | ACC吻侧→前脑岛 | 解耦沉默 −0.1/−0.2/−0.3 | （并入 an_e03） | ⚠️ 并吞——同端点对合并为单边 |
| link_326 | LocusCoeruleus→前脑岛 | 过度耦合 0/+0.1/+0.2 | **an_e04** | ✅ 保留语义（内感受过度警觉侧） |
| link_336 | VTA→NAcc | 解耦沉默 −0.1/−0.3/−0.5 | **an_e01** | ✅ 保留语义（量级不变） |
| link_338 | VTA→mPFC(额上回) | 解耦沉默 0/−0.1/−0.3 | **an_e02** | ✅ 保留语义（fid 合并：SuperiorFrontalMPFC → superiorfrontal） |
| link_008_L | ACC(L)→dlPFC | 过度耦合 +0.2/+0.3/+0.5 | **an_e05**（rostralmiddlefrontal→Caudate） | ⚠️ **语义转移**：直连不在三体图 → 认知控制↑ 由 cognitive CSTC 环路承载；量级沿用 |
| link_007_L | ACC(L)→ACC吻侧 | 过度耦合 +0.1/+0.2/+0.3 | **an_e06** | ✅ 保留语义 + L 后缀取消 |
| link_147_L | 楔前叶(L)→mPFC(额上回) | 过度耦合 +0.1/+0.2/+0.3 | **an_e07** | ✅ 保留语义 + L 后缀取消 |
| link_343 | SNc→尾状核 | 过度耦合 0/+0.2/+0.3 | **an_e09** | ✅ 保留语义（策略锁定/僵化） |
| link_331 | LocusCoeruleus→V1(pericalcarine) | 过度耦合 0/+0.1/+0.2 | **an_e10** | ✅ 保留语义 |
| （旧表无） | 苍白球 set-shift 僵硬（Datta 2025 组分3） | — | **an_e08** | ⭐ 新增——cognitive 环路 disinhibition |
| （旧表无） | 5HT 广播↑→过度抑制（Kaye 2005） | — | **an_e11** | ⭐ 新增——5HT tone 推导锚 |

**处置规则总结**：端点对存在 → 直接映射保留；同端点对重复（link_155_L/link_160）→ 并吞；直连不存在（link_008_L）→ **语义转移优先**；「病理新增」从严（本文件 0 条）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 内感受域 \|m\| > 0.3 → 前脑岛内感受→身体状态信号不可信——HP/SAN 实际值 UI 模糊 ±15% | ✅ 保留 | **an_e03/an_e04** \|m\| > 0.3（取两者 m_max） | 岛叶 trait（Panarello 2025） |
| 奖赏域 \|m\| > 0.4 → 趋近·主动 → 食物/奖赏相关目标不可用 | ✅ 保留 | **an_e01** \|m\| > 0.4 | 奖赏回路↓（Bronleigh AN 奖赏−） |
| 认知控制域 m_max > 0.5 → 忍耐·主动 +50% 但每回合 SAN −1（自我惩罚） | ✅ 保留 | **an_e05/an_e06** m_max > 0.5 | 认知控制↑ + 自我惩罚 |
| （新增）内感受-认知耦合 [NEW] | ⭐ 新增 | **an_e03**（内感受）+ **an_e05**（认知）联合 | 饥饿信号被认知控制"解释"为控制成功（见非线性跳变②）——内感受与认知两域耦合表达 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 认知控制域 m_max > 0.6 → dlPFC 对 L1-L2 控制异常——执着于身体而忽略情绪；L1 奖赏/情绪信号被抑制但 L2 内感受信号反而增强 | ✅ 保留 | **an_e05/an_e06** m_max > 0.6 | 过度控制失代偿前兆 |
| 内感受域 \|m\| > 0.3 → 内感受信号 inverted——饥饿被解读为"控制成功"。SAN 恢复减半（无法通过内省缓解） | ✅ 保留 | **an_e03** \|m\| > 0.3 | 饥饿=控制成功的认知倒置 |
| （新增）暴食-清除亚型循环（AN-BP）[NEW] | ⭐ 新增 | **an_e05** 失代偿跳变 + **an_e01** 短时翻转 + **an_e09**（清除动作执行） | AN-BP 亚型：过度抑制累积 SAN −1/回合 → 自我惩罚超阈值 → 失代偿（认知 gate 崩溃）→ 短暂暴食（e01 短时 +）→ 清除（e09 策略锁定）→ 回归过度抑制。核心区别于 BN：AN 的暴食-清除是**过度控制的周期性崩溃**，BN 是失控主导 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_155_L, link_160, link_336, link_008_L | **an_e01, an_e03, an_e05** |
| 2（关联） | link_338, link_007_L, link_147_L, link_343 | **an_e02, an_e06, an_e07, an_e09** |
| 1（边缘） | link_326, link_331 | **an_e04, an_e10, an_e08, an_e11** |

> 核心 3 条 = 奖赏↓核心（e01）+ 内感受 trait 核心（e03）+ 认知↑核心（e05）；新增边 e08/e11 落边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6（AN max=0.5） | §二 |
| 偏侧偏离量 | laterality_delta | 0（无稳健偏侧证据） | §二 |
| NE 基线偏离（AN） | ΔNE_baseline | −0.1（反刍，域特异裁决；基线 0.3 → 0.2） | §三 |
| DA_VTA 基线偏离（AN） | ΔDA_VTA_baseline | −0.2（标签缺口裁决；基线 0.4 → 0.2） | §三 |
| DA_SNc 基线偏离（AN） | ΔDA_SNc_baseline | +0.1（标签缺口裁决；基线 0.5 → 0.6） | §三 |
| 5HT 基线偏离（AN） | Δ5HT_baseline | +0.2（基线 0.5 → 0.7） | §三 |
| CSTC 偏置（AN） | bias_somatic / bias_cognitive / bias_limbic | −0.15 / +0.15 / 0 | §三 |
| 内感受模糊阈值 | m_th | 0.3（an_e03/an_e04，HP/SAN ±15%） | §五.1 |
| 奖赏趋近禁用阈值 | m_th | 0.4（an_e01） | §五.1 |
| 过度控制阈值 | m_th | 0.5（忍耐+50%, SAN −1）/ 0.6（执着身体） | §五.1/§五.2 |
| 内感受倒置阈值 | m_th | 0.3（an_e03，饥饿=控制成功） | §五.2 |
| 失代偿阈值（AN-BP） | m_th | 认知 m_max 超 0.6 持续 N 回合 [NEW 初值可调] | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [PTSD 重映射试点](../disease-pilots/ptsd-pilot.md), [神经性厌食症](../../../entities/diseases/%E7%A5%9E%E7%BB%8F%E6%80%A7%E5%8E%8C%E9%A3%9F%E7%97%87.md), [神经性贪食症](../../../entities/diseases/%E7%A5%9E%E7%BB%8F%E6%80%A7%E8%B4%AA%E9%A3%9F%E7%97%87.md)（相反模式对照）, [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§5.2, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../../data/connectivity/link_registry.json)（⚠️ 已废弃）*
