# ASD 重映射试点

> 自闭症谱系障碍（ASD）重映射试点（Grilling #88 Q0.6 第二批）。旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **15 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **社会认知节点群异常**（社交脑：TPJ/STS/mPFC/颞极 连接路径异常）+ 识别域异常（面孔/生物运动）+ 感觉域过度耦合（感官过敏）+ 认知控制域过度耦合（僵化/刻板）。
>
> **⚠️ 发育性特殊处理（NPC AI §5.3 定案）**：ASD = **结构连接差异，非髓鞘化差异——需单独处理**。本试点全部病理边的 m 偏移语义 = **结构性连接差异（连接路径异常/替代回路/代偿/缺失标准连接），不是经历型髓鞘化偏移**：表达层以「结构异常」类型承载（m 负偏移 = 结构性低连接/缺失，m 正偏移 = 结构性过度连接），**不参与 tone/bias 推导的髓鞘化语义**——NPC AI §4.3 第 3 级"节点 m 直调"（W_npc 矩阵结构差异）即其实现路径。7 参数仅由标签「社交钝化」给出（§5.2 示例表 6 病无 ASD——**标签组合为本试点自定并注明**）。**档位过滤：CGI-S 3-7 三档全可用；laterality_delta 全部默认 0（无稳健偏侧证据，旧 `_L` 后缀 = ENIGMA 数据采集侧非疾病偏侧，遵循 #92 原则）。**

## 目录

1. [文献锚点（3 篇核心 + 关键数据点）](#一文献锚点3-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [ASD → 7 参数映射建议（4 tone + 3 CSTC）](#三asd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_086_L 等 → 新病理边）](#四旧链路对照表link_086_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（3 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Opel et al. (2020)** *Biol Psychiatry* 88(9):678-686（ENIGMA 二次分析） | 结构 meta | **ADHD/ASD 结构模式独立于 MDD/BD/SCZ/OCD 共享因子**——ASD 边集独立设计，不共享四病结构因子；结构差异 = 连接方式不同（非"变弱"）（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §3.1）→ 全部社会认知边「结构异常」类型的独立模式依据 |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | **社会过程域 ToM（心理理论）：MPFC/TPJ/STS/楔前叶**；**affiliative（亲和）：VTA-NAcc-VP-杏仁核**（文献数据源 §4.1）→ 社交脑边群（e01-e05/e07/e09/e10/e15）的回路级锚 |
| 3 | **社交脑连接（social brain connectivity）** | 功能连接综述 | **TPJ/STS/mPFC/颞极** 四枢纽连接路径异常 = ASD 社会认知缺损核心 → 社交脑节点群边（e01-e05/e07）+ 识别域边（e08/e09） |

**辅助锚（方向/范围补充）**：

- **ENIGMA ASD 结构独立（Opel 2020）**——ASD 结构模式不与四病共享因子相关 → 本试点全部社会认知边独立设计，**类型统一标「结构异常」（发育性）**，区别于 PTSD（跨层短路）/MDD（解耦沉默）等经历型病理。
- **NPC AI §5.3**——"发育性障碍（ASD）= 结构连接差异，非髓鞘化差异——需单独处理"：m 偏移语义重定义为结构差异，见文首 ⚠️。
- **NPC AI §4.2 标签**——默认标签「社交钝化」（旧文件）：无 tone 偏移、bias_cognitive −0.15（§5.2 示例表 6 病无 ASD——自定并注明）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——10 条旧链路的方向/量级/通路描述（ENIGMA 强度）作为语义继承源，见 §四。
- **RDoC 唤醒域**——感觉域边（e13/e14）的感官过敏锚：丘脑枕→视觉联合皮层中继 + LC→V1 感觉信噪比（NPC AI §5.2 社交钝化之外的独立感觉通道）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，**全部数值有来源，新增数值标记 `[NEW]`**；结构异常边的 m 语义 = 结构性连接差异（§5.3 特殊处理），非髓鞘化偏移。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`——机制引用镜像 = 校验报错，偏侧化架构 §五）。**15 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（ASD = `asd`）。三档 m 偏移 = 轻/中/重（**档位过滤 B′：CGI-S 3-7 范围下限 ≤3 → 轻档可用**；量级沿用旧文件设计校准）。laterality_delta 全 0（§6.5 规则 2：无偏侧证据；旧 `_L` = 数据采集侧）。
>
> **⚠️ 结构异常边语义声明（NPC AI §5.3）**：`结构异常` 类型在本表 = **发育性结构连接差异**（m 负 = 连接路径缺失/低连接，如替代回路缺失；m 正 = 结构性过度连接），**不是经历型髓鞘化偏移**。表达层经 NPC AI §4.3 第 3 级"节点 m 直调"（W_npc 矩阵结构差异）实现，不参与 tone/bias 髓鞘化推导。
>
> **端点名对照速查（文献名 → 游戏节点）**：mPFC/dmPFC = `superiorfrontal`（fid SuperiorFrontalMPFC, L5）；vmPFC/DMN = `medialorbitofrontal`（L5）；dlPFC = `rostralmiddlefrontal`（L5）；额中回尾部 = `caudalmiddlefrontal`（L5）；TPJ = `supramarginal`（fid SupramarginalTPJ, L5）+ `inferiorparietal`（fid InferiorParietalAngular, L4）；STS = `superiortemporal`（fid SuperiorTemporalSulcus, L4）；pSTS = `bankssts`（fid BanksSTS, L4）；颞极 = `temporalpole`（L2）；Broca = `parsopercularis`（L5）；梭状回/FFA = `fusiform`（L4）；颞中回 = `middletemporal`（L4）；楔前叶 = `precuneus`（L4）；ACC = `caudalanteriorcingulate`（L2，含 L5-fid）；杏仁核 = `Amygdala`（L1）；丘脑枕 = `Thalamus-Proper`（L1）；V1 = `pericalcarine`（L3）；视觉联合皮层 = `cuneus`（L3）；蓝斑 = `LocusCoeruleus`（L0）；VTA = `VentralTegmentalArea`（L0）；伏隔核 = `Accumbens-area`（L1）。

### 2.1 自我社会域（5 条）——「社交脑 ToM 节点群」结构异常

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e01** ⭐核心 | superiorfrontal | supramarginal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.2181（mPFC↔TPJ ToM 主链） | **结构异常** | −0.2/−0.3/−0.4 | 0 | 旧 link_086_L 语义转移（mOFC→颞极 ToM → mPFC→TPJ 换位思考主链）；RDoC ToM MPFC/TPJ | 行为覆盖①（L4 读意图不可用）+ 非线性跳变②（社会线索完全过滤） |
| **asd_e02** | inferiorparietal | supramarginal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.224（角回→TPJ） | **结构异常** | −0.1/−0.2/−0.3 | 0 | 旧 link_049_L（IP→TPJ，ENIGMA 10.34）；RDoC ToM TPJ | 行为覆盖①（读意图） |
| **asd_e03** ⭐新增 | superiorfrontal | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.232（mPFC↔STS 社会线索） | **结构异常** | −0.1/−0.2/−0.3 | 0 | RDoC ToM MPFC/STS；社交脑 mPFC↔STS 连接异常 | 行为覆盖①（社会线索处理） |
| **asd_e04** ⭐新增 | superiortemporal | bankssts | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4911（STS↔pSTS 生物运动/目光） | **结构异常** | −0.1/−0.2/−0.3 | 0 | RDoC ToM STS；生物运动/目光加工异常（社交脑） | 行为覆盖①（目光/生物运动线索） |
| **asd_e05** | caudalanteriorcingulate | superiorfrontal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+3（dACC↔mPFC 社会显著） | **结构异常** | −0.1/−0.2/−0.3 | 0 | 旧 link_009_L（ACC→mPFC，ENIGMA 10.27）；社交脑 社会显著加工 | 行为覆盖②（社会显著过滤） |

### 2.2 语言社会域（2 条）——「Broca↔Wernicke + 颞极↔STG」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e06** | parsopercularis | superiortemporal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1723（Broca↔Wernicke 语言社会） | **结构异常** | −0.2/−0.3/−0.4 | 0 | 旧 link_116_L（Broca↔Wernicke 共情，ENIGMA 7.97）；语言社会功能异常 | 行为覆盖①（语言社会） |
| **asd_e07** ⭐新增 | temporalpole | superiortemporal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+2, edr=0.455（STG↔TP 腹侧语言/语义网络） | **结构异常** | −0.1/−0.2/−0.3 | 0 | RDoC ToM 颞极；社交脑 颞极↔STG 语义社会连接 | 行为覆盖①（语义/语言社会） |

### 2.3 识别域（2 条）——「面孔/生物运动识别」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e08** | fusiform | middletemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.6046（FFA→MTG 面孔/语义） | **结构异常** | −0.1/−0.2/−0.3 | 0 | 旧 link_032_L（梭状回→颞中回，ENIGMA 7.28）；面孔/生物运动识别异常 | 行为覆盖①（面孔识别） |
| **asd_e09** ⭐新增 | fusiform | Amygdala | privileged_pathway | ✅ 命中：`ventral_stream_emotion`, dir=feedback, level_diff=−3（FFA→杏仁核 面孔-情绪通路，Pessoa & Adolphs 2010） | **结构异常** | −0.1/−0.2/−0.3 | 0 | 面孔情绪识别缺损（社交脑）；ENIGMA ASD 结构独立模式 | 行为覆盖①（面孔情绪） |

### 2.4 自传体/自我参照域（2 条）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e10** ⭐新增 | precuneus | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.242（楔前叶→mPFC 自传体/自我参照） | **结构异常** | 0/−0.1/−0.2 | 0 | 旧 link_131_L 语义转移（PCC→mPFC 自传体记忆 → 楔前叶→mPFC 自我参照）；RDoC ToM 楔前叶 | 行为覆盖②（自我参照） |
| **asd_e11** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287（mOFC↔dlPFC 自传体） | **结构异常** | −0.1/−0.2/−0.3 | 0 | 旧 link_082_L（mOFC→dlPFC 自传体记忆，ENIGMA 7.79） | 行为覆盖② |

### 2.5 认知控制域（1 条）——「僵化/刻板」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e12** | caudalmiddlefrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3201（额中回尾部↔dlPFC 工作记忆） | **过度耦合**（结构性过度连接） | +0.1/+0.2/+0.3 | 0 | 旧 link_021_L（额中回尾部↔dlPFC，ENIGMA 10.45）；僵化/刻板/特殊兴趣（与 OCD 共享过度耦合特征但限于 routine） | 行为覆盖③（僵化） |

### 2.6 感觉域（2 条）——「感官过敏」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e13** | Thalamus-Proper | cuneus | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+2, edr=0.3163（Pulvinar→视觉联合皮层中继） | **过度耦合**（结构性过度连接） | +0.1/+0.2/+0.3 | 0 | 旧 link_318 语义转移（上丘→丘脑枕→皮层 感觉中继过度 → 丘脑枕→视觉联合皮层 relay 过度） | 行为覆盖④（感官过载）+ 非线性跳变①（感官过载锁定） |
| **asd_e14** | LocusCoeruleus | pericalcarine | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast（LC→V1 感觉信噪比） | **过度耦合**（结构性过度连接） | 0/+0.1/+0.2 | 0 | 旧 link_331（LC→V1 感觉信噪比异常，Hansen PINK fc=0.6）；RDoC 唤醒域 | 行为覆盖④（感官过载） |

### 2.7 社会奖赏域（1 条）——「affiliative 社交动机」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **asd_e15** ⭐新增 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（DA 奖赏预测误差） | **结构异常** | −0.1/−0.2/−0.3 | 0 | RDoC affiliative：VTA-NAcc-VP-杏仁核；社交奖赏/动机连接差异（社交动机↓） | 行为覆盖⑤（社交动机低） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ 全 0 = 无稳健偏侧证据（旧 `_L` 后缀 = ENIGMA 数据采集侧，非疾病偏侧，#92 原则）。**结构异常 = 发育性结构连接差异（§5.3 特殊处理），非髓鞘化偏移**；过度耦合（e12/e13/e14）同为结构性过度连接语义。

---

## 三、ASD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（§6.6）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。
>
> **⚠️ 特殊路径声明（NPC AI §5.3 + §6.6 例外）**：ASD 结构异常边**不参与 tone/bias 髓鞘化推导**（结构连接差异 ≠ 神经调质/门控偏置）——§6.6 规则 1/2 对 ASD 不适用，7 参数仅由标签「社交钝化」给定（敌我同构参数层），结构差异经 NPC AI §4.3 第 3 级"节点 m 直调"（W_npc 矩阵）单独表达。**标签组合自定声明**：§5.2 示例表（6 病）无 ASD——默认标签「社交钝化」（旧文件继承）为本试点自定确认，待 #88 入库。

### 3.1 从病理边推导（结构差异路径，非标准推导）

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0** | 无全局 LC tone 偏移（asd_e14 LC→pericalcarine 为选择性感觉腿结构性过度连接，非全局 NE 广播上调） | 社交钝化 标签无 tone 偏移（Green 2015 社会脑低激活≠全局警觉变化） |
| 2 | DA_VTA_baseline | **0** | asd_e15（VTA→NAcc）为结构性低连接（affiliative 腿），非全局 DA tone 变化 | 结构性差异不入全局 tone 推导（§5.3 特殊路径） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | — |
| 4 | 5HT_baseline | **0** | 无 DR 边群命中 | — |
| 5 | bias_somatic | **0** | 无 somatic 环路（Putamen）边群命中 | 感觉域结构性差异在 CC/特权层，非 CSTC somatic gate |
| 6 | bias_cognitive | **−0.15** | 无 cognitive 环路（Caudate）边群命中——**由标签「社交钝化」直接给定**（社会脑低激活→认知/语言行动倾向↓，Green 2015） | 标签主锚：ASD 7 参数以标签为准，结构差异另走 W_npc 直调 |
| 7 | bias_limbic | **0** | 无 limbic 环路边群命中 | — |

### 3.2 与标签组合交叉验证（敌我同构闭环）

自定标签「社交钝化」（单标签；§5.2 无 ASD 示例，自定并注明）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0（社交钝化无 tone 偏移） | 0 | ✅ |
| DA_VTA / DA_SNc / 5HT | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | −0.15（社交钝化） | −0.15（标签直接给定；结构边不入 CSTC 推导） | ✅ |
| bias_limbic | 0 | 0 | ✅ |

**结论**：ASD 病理边集（结构差异层）⇔ 7 参数偏移（标签层）经 §5.3 特殊路径解耦自洽——**结构差异走 W_npc 矩阵直调，7 参数仅由「社交钝化」标签给定**。ASD NPC 最终参数：NE=0.3、DA_VTA=0.4、DA_SNc=0.5、5HT=0.5（全基线）、bias_cognitive=−0.15（其余 bias 0）；结构差异 = 15 条病理边 m 直调。

---

## 四、旧链路对照表（link_086_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_086_L | MedialOrbitalPrefrontalDMN→TemporalPole | 结构异常 −0.2/−0.3/−0.4 | **asd_e01**（superiorfrontal→supramarginal） | ⚠️ **端点转移**（三体图无 mOFC→TP 直连；ToM 语义移至 mPFC→TPJ 换位思考主链）+ 新增 asd_e07（颞极↔STG）承载颞极端语义 |
| link_009_L | AnteriorCingulateCortex→SuperiorFrontalMPFC | 结构异常 −0.1/−0.2/−0.3 | **asd_e05**（caudalanteriorcingulate→superiorfrontal） | ✅ 保留语义（偏侧后缀移除：`_L` = 数据采集侧非疾病偏侧） |
| link_131_L | PosteriorCingulate→SuperiorFrontalMPFC | 结构异常 0/−0.1/−0.2 | **asd_e10**（precuneus→superiorfrontal） | ⚠️ **端点转移**（三体图无 PCC→SF 直连；自传体记忆→楔前叶→mPFC 自我参照） |
| link_116_L | ParsOpercularis→SuperiorTemporalWernicke | 结构异常 −0.2/−0.3/−0.4 | **asd_e06**（parsopercularis→superiortemporal） | ✅ 保留语义（fid 合并：Wernicke → 节点 superiortemporal） |
| link_049_L | InferiorParietalAngular→SupramarginalTPJ | 结构异常 −0.1/−0.2/−0.3 | **asd_e02**（inferiorparietal→supramarginal） | ✅ 保留语义 |
| link_318 | SuperiorColliculus→Thalamus | 过度耦合 +0.1/+0.2/+0.3 | **asd_e13**（Thalamus-Proper→cuneus） | ⚠️ **端点转移**（三体图无 SC→Thalamus 直连；感觉中继语义移至丘脑枕→视觉联合皮层 relay） |
| link_331 | LocusCoeruleus→Pericalcarine | 过度耦合 0/+0.1/+0.2 | **asd_e14**（LocusCoeruleus→pericalcarine） | ✅ 保留语义（LC→V1 感觉信噪比） |
| link_032_L | Fusiform→MiddleTemporal | 结构异常 −0.1/−0.2/−0.3 | **asd_e08**（fusiform→middletemporal） | ✅ 保留语义 |
| link_021_L | CaudalMiddleFrontal→RostralMiddleFrontalDLPFC | 过度耦合 +0.1/+0.2/+0.3 | **asd_e12**（caudalmiddlefrontal→rostralmiddlefrontal） | ✅ 保留语义（僵化/刻板） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 结构异常 −0.1/−0.2/−0.3 | **asd_e11**（medialorbitofrontal→rostralmiddlefrontal） | ✅ 保留语义（自传体记忆） |
| （旧表无） | mPFC↔STS 社会线索（RDoC ToM） | — | **asd_e03** | ⭐ 新增 |
| （旧表无） | STS↔pSTS 生物运动/目光（RDoC ToM） | — | **asd_e04** | ⭐ 新增 |
| （旧表无） | FFA→杏仁核 面孔情绪（Pessoa & Adolphs 2010） | — | **asd_e09** | ⭐ 新增 |
| （旧表无） | VTA→NAcc affiliative 社交奖赏（RDoC） | — | **asd_e15** | ⭐ 新增 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_086_L → e01+e07、link_131_L → e10、link_318 → e13），「病理新增」从严（本表 0 条病理新增，全部命中现有三体边）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_086_L \|m\| > 0.3 → L4 读意图·主动 不可用（无法从面部表情/动作推断意图） | ✅ 保留（改挂接） | **asd_e01/e02**（mPFC→TPJ + 角回→TPJ ToM 边群） | ToM 主链断开 → 读意图不可用；新增 e03/e04（STS 社会线索/生物运动）同域 |
| 感觉域 m_max > 0.3 → 感官过载（每回合 10% 概率额外激活一条感觉域链路，SAN −1） | ✅ 保留 | **感觉域边群**（asd_e13/e14，m_max 取两条最大值） | 感觉域在新格式 = 感觉域病理边集 |
| link_049_L \|m\| > 0.3 → L5 换位·主动 不可用（无法以他人视角看世界） | ✅ 保留 | **asd_e01**（mPFC→TPJ）| L5 换位 = TPJ ToM 主链的 L5 端 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 感觉域 m_max > 0.5 → 感官过载锁定（感觉域链路强制激活不可被 L5 控制压制，SAN −2/回合） | ✅ 保留 | **asd_e13** m > 0.5，作用域 = 感觉域边群（e13/e14） | 结构性过度连接锁定（与 PTSD 防御锁定 / 躯体症状症状锁定同构） |
| 自我社会域 m_max < −0.4 → 社会线索完全过滤（敌方 Broca 输出对自身不产生 SAN 影响，社交盲区） | ✅ 保留 | **asd_e01**（mPFC→TPJ）+ **asd_e03/e05**（STS 社会线索）m_max < −0.4 | 社交脑结构缺失 → 社交盲区（结构性，非压制失效） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 1（核心） | link_086_L, link_009_L, link_116_L, link_049_L | **asd_e01, asd_e05, asd_e06, asd_e02** |
| 1（关联） | link_131_L, link_318, link_021_L, link_082_L, link_032_L | **asd_e10, asd_e13, asd_e12, asd_e11, asd_e08** |
| 1（边缘） | link_331 | **asd_e14, asd_e03, asd_e04, asd_e07, asd_e09, asd_e15** |

> 核心 = ToM 主链（e01）+ 社会显著（e05）+ 语言社会（e06）+ TPJ 读意图（e02）；新增边落关联/边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档可用（CGI-S 3-7），\|m\| ≤ 0.6；语义 = 结构性连接差异（§5.3） | asd-pilot.md §二 / pathology_edges.json |
| 偏侧偏离量 | laterality_delta | 全 0（无稳健偏侧证据；旧 `_L` = 数据采集侧） | pathology_edges.json（§6.5 规则 2） |
| CSTC 偏置（ASD） | bias_cognitive | −0.15（社交钝化标签直接给定；结构差异另走 W_npc 直调） | §三 |
| 感官过载触发阈值 | m_th | 0.3（感觉域边群，10% 概率额外激活，SAN −1） | §五.1 |
| 感官过载锁定阈值 | m_th | 0.5（强制激活不可压制，SAN −2/回合） | §五.2 |
| 社会线索过滤阈值 | m_th | 0.4（自我社会域 m_max < −0.4，社交盲区） | §五.2 |
| 标签派生阈值 | t | 0.5 [NEW 初值可调] | 偏侧化架构 §六.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [自闭症谱系障碍](../../../entities/diseases/%E8%87%AA%E9%97%AD%E7%97%87%E8%B0%B1%E7%B3%BB%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2/§5.3, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §十八, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §三/§四/§七, [左右脑偏侧化-文献数据源](../../../../reference/literature/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八, [角色与面具](../../../entities/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
