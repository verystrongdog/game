# 躯体症状障碍 重映射试点

> 躯体症状障碍（somatic symptom disorder, SSD）重映射试点（Grilling #88 Q0.6 第二批 + Q0.2 P1 新增病 + Q0.5 新父类「躯体症状」首个子类）。**纯文献驱动，无旧文件、无旧链路对照表（§四省略）**。三体模型上 **13 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **内感受域 insula→ACC 过度耦合（内感受过敏）**——前脑岛+ACC 内感受回路高激活（RDoC 内感受域），叠加唤醒域 NE 警觉↑ + 前额叶抑制不足。「创伤→躯体化」是 **#88 转化接口的天然案例**：创伤记忆（杏仁核/内嗅）经 entorhinal→insula 内脏学习绑定 + Amygdala→insula 威胁→内感受转化，将心理创伤表达为躯体症状。7 参数推导（4 tone + 3 CSTC bias）与自定标签组合「敏化-威胁 + 抑制不足」一致（§5.2 示例表无躯体症状——**标签组合为本试点自定并注明**）。**档位过滤：CGI-S 3-7 三档全可用；laterality_delta 全部默认 0（无稳健偏侧证据）。**

## 目录

1. [文献锚点（3 篇核心 + 关键数据点）](#一文献锚点3-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [躯体症状 → 7 参数映射建议（4 tone + 3 CSTC）](#三躯体症状--7-参数映射建议4-tone--3-cstc)
4. [行为覆盖/非线性跳变保留清单（新增病全新建）](#四行为覆盖非线性跳变保留清单新增病全新建)
5. [参数速查表](#五参数速查表)

---

## 一、文献锚点（3 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Boeckle et al. (2016)** *NeuroImage: Clinical*（躯体形式障碍神经影像 meta 分析, PMID [27182487](https://pubmed.ncbi.nlm.nih.gov/27182487/)） | 功能影像 meta | 躯体形式障碍**高激活：前扣带（ACC）、前脑岛、感觉运动区**；前额叶低激活 → 内感受域核心边（e01/e02/e03）+ 调控域抑制↓（e10）的方向/范围锚 |
| 2 | **RDoC v4（NIMH）** | 回路矩阵 | **内感受域（Interoception）**：前脑岛（初级内感受皮层）+ ACC 内感受过敏——躯体症状=内感受信号异常放大（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §四.2 岛叶跨 4 RDoC 域）；急性威胁回路杏仁核→ACC/岛叶 → e07/e08 焦虑放大锚 |
| 3 | **Boeckle et al. (2016)** *BMC Psychiatry*（转换障碍神经影像 meta 分析, PMID [27283002](https://pubmed.ncbi.nlm.nih.gov/27283002/)） | 功能影像 meta | 转换/躯体症状：**边缘系统（杏仁核/岛叶/ACC）高激活 + 感觉运动/前额叶低激活** → 转化接口边（e08）+ 体感放大边（e12）+ 抑制不足边（e10） |

**辅助锚（方向/范围补充）**：

- **Guo et al. (2026)** *Transl Psychiatry*——跨诊断共享：**双侧前脑岛 + ACC/mPFC ALFF↑**（文献数据源 §2.1，焦虑障碍包含于共享模式）→ 内感受域边群方向（e01-e03/e07）。
- **#88 转化接口（grilling-88.md Q0 系列）**——「创伤→躯体化」= 创伤记忆（#87 语义）→ 病理链路 m 偏移的转化接口天然案例：本试点 e08/e09（杏仁核/内嗅 → 前脑岛）即为该接口在躯体症状上的表达。
- **NPC AI §4.2 标签**——自定标签组合「敏化-威胁 + 抑制不足」（§5.2 示例表无躯体症状，自定并注明）：NE/5HT/bias_somatic/bias_limbic 通道锚（e04-e06/e11-e13），验证见 §三。
- **RDoC 唤醒/调节域**——蓝斑 NE → 前脑岛/ACC 警觉（唤醒域）→ e04/e05（LC 广播内感受警觉）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用 NPC AI §4.2 标签校准值（新增病无旧文件继承，量级取标签校准 ±0.1~±0.2 / bias ±0.15），**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`——机制引用镜像 = 校验报错，偏侧化架构 §五）。**13 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（躯体症状 = `somatic-symptom` → 前缀 `ssd`）。三档 m 偏移 = 轻/中/重（**档位过滤 B′：CGI-S 3-7 范围下限 ≤3 → 轻档可用**；量级沿用 NPC AI §4.2 标签校准）。laterality_delta 全 0（§6.5 规则 2：无偏侧证据）。
>
> **端点名对照速查（文献名 → 游戏节点）**：前脑岛 = `insula`（L2，内感受域）；ACC 背侧 = `caudalanteriorcingulate`（L2，含 L5-fid）；ACC 吻侧 = `rostralanteriorcingulate`（L2）；vmPFC = `medialorbitofrontal`（L5）；丘脑 = `Thalamus-Proper`（L1）；体感皮层 S1 = `postcentral`（L3）；运动皮层 M1 = `precentral`（L3）；杏仁核 = `Amygdala`（L1）；内嗅皮层 = `entorhinal`（L4）；伏隔核 = `Accumbens-area`（L1）；壳核 = `Putamen`（L1）；蓝斑 = `LocusCoeruleus`（L0）；中缝背核 = `DorsalRapheNucleus`（L0）。

### 2.1 内感受域（6 条）——「前脑岛→ACC 内感受过敏」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ssd_e01** ⭐核心 | insula | caudalanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3951（前脑岛↔dACC 内感受-显著网络） | **过度耦合** | +0.1/+0.2/+0.3 | 0 | Boeckle 2016（ACC+前岛叶高激活）；RDoC 内感受域；Guo 2026 岛叶+ACC ALFF↑ | 行为覆盖①（症状波动）+ 非线性跳变① |
| **ssd_e02** | insula | rostralanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246（前脑岛↔rACC 内感受-情绪） | 过度耦合 | 0/+0.1/+0.2 | 0 | Boeckle 2016（ACC 高激活）；RDoC 内感受域情绪分量 | 行为覆盖①（症状情绪化） |
| **ssd_e03** | Thalamus-Proper | insula | cstc | ✅ 命中：limbic 环路 `thalamocortical`, thalamic_relay→cortical_input（丘脑皮层闭合）+ 同对 CC 边 edr=0.5042 | 过度耦合 | 0/+0.1/+0.2 | 0 | 内脏/躯体感觉丘脑中继放大（伤害性信号→前脑岛）；Boeckle 2016 感觉运动高激活 | 行为覆盖①（内脏感觉增益） |
| **ssd_e04** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | RDoC 唤醒域：LC→前脑岛 NE 内感受警觉（旧 link_326 语义，Hansen PINK 最强 hub fc=0.85） | 3.1 节 NE tone 推导锚 |
| **ssd_e05** | LocusCoeruleus | caudalanteriorcingulate | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | RDoC 唤醒域：LC→ACC 持续警觉（躯体症状监控）；Guo 2026 ACC ALFF↑ | 3.1 节 NE tone 推导锚 |
| **ssd_e06** | DorsalRapheNucleus | insula | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 5-HT 内感受调制异常（焦虑共病 5HT 通路）；RDoC 唤醒/情绪调制 | 3.1 节 5HT tone 推导锚 |

### 2.2 转化接口域（3 条）——「创伤→躯体化」#88 天然案例

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ssd_e07** | insula | Amygdala | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3261（前脑岛→杏仁核 内感受→威胁评估） | 过度耦合 | 0/+0.1/+0.2 | 0 | 内感受过敏→威胁评估放大（焦虑放大环）；Boeckle 2016 杏仁核高激活 | 行为覆盖②（焦虑放大） |
| **ssd_e08** ⭐转化 | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261（杏仁核→前脑岛 威胁→内感受） | **过度耦合** | 0/+0.1/+0.2 | 0 | **#88 转化接口**：创伤威胁信号→内感受皮层表达（心理创伤→躯体症状的直接通路）；Boeckle 2016 边缘高激活 | 行为覆盖②（焦虑放大）+ 非线性跳变②（创伤触发躯体化） |
| **ssd_e09** ⭐转化 | entorhinal | insula | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−2, edr=0.3107（Insula↔EC — interoceptive↔contextual memory binding, visceral learning） | 过度耦合 | 0/+0.1/+0.2 | 0 | **内脏学习绑定**：创伤情景记忆（内嗅）→ 内感受（前脑岛）内脏反应记忆；Boeckle 2016 情景-内感受共激活 | 行为覆盖②（症状记忆勾起） |

### 2.3 调控域（1 条）——「前额叶抑制不足」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ssd_e10** | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−4（vmPFC→杏仁核 恐惧消退，Milad & Quirk 2012） | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | Boeckle 2016 前额叶低激活：vmPFC 对杏仁核抑制不足 → 焦虑/躯体化无法自上而下压制 | 非线性跳变③（压制失效→症状锁定） |

### 2.4 体感/行动域（3 条）——「感觉放大 + 躯体化表达」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ssd_e11** | rostralanteriorcingulate | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.2 | 0 | 症状→趋避/寻求行为 gate（回避-求医行为）；RDoC 正性效价×内感受交叉 | 3.1 节 bias_limbic 推导锚 |
| **ssd_e12** | Thalamus-Proper | postcentral | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+2（VPL/VPM→S1 一级躯体感觉中继） | 过度耦合 | 0/+0.1/+0.2 | 0 | 体感中继放大（疼痛/不适感增强）；Boeckle 2016 感觉运动区高激活 | 行为覆盖①（体感增益） |
| **ssd_e13** | Thalamus-Proper | precentral | cstc | ✅ 命中：somatic 环路 `thalamocortical`, thalamic_relay→cortical_input | 过度耦合 | 0/+0.1/+0.2 | 0 | 内感受→运动门控（躯体化行为表达）；somatic 环路被内感受信号偏置 | 3.1 节 bias_somatic 推导锚 |

**图例**：⭐核心/⭐转化 = 本试点核心机制边（e01 内感受过敏核心；e08/e09 转化接口）；Δ 全 0 = 无稳健偏侧证据。**躯体症状无旧链路**：全部 13 条为文献驱动新建，但均命中现有三体边（非"病理新增"）。

---

## 三、躯体症状 → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（§6.6）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。
>
> **标签组合自定声明**：躯体症状障碍为 Q0.2 新增病，NPC AI §5.2 示例表（6 病）无躯体症状——标签组合「敏化-威胁 + 抑制不足」为本试点自定（与 PTSD 共享敏化-威胁锚，叠加 5HT 去抑制 + 躯体行动偏置），待 #88 入库确认。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e04（LC→insula）、e05（LC→caudalanteriorcingulate）过度耦合 | LC 出边群 2/2 命中且 m 随严重度升高 → 蓝斑 NE 广播全局上调 = 内感受警觉+焦虑放大（RDoC 唤醒域） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | 躯体症状不主要累及奖赏回路 |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e06（DR→insula）过度耦合 | 中缝核 5-HT 传递异常聚焦于内感受回路 → 全局 5HT 基线↓（低 5HT = 去抑制，Soubrié 1986；抑制不足标签） |
| 5 | bias_somatic | **+0.15** | e13（Thalamus→precentral somatic 环路中继）、e12（体感放大） | 躯体化行动 gate 被内感受信号偏置 → 身体行动/症状表达倾向↑（抑制不足标签） |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）边群命中 | 躯体症状主要累及体感/边缘环路，非认知环路 |
| 7 | bias_limbic | **+0.15** | e11（rACC→Accumbens-area limbic GO）、e07/e08（内感受↔威胁） | 边缘环路 gate 被内感受/威胁信号劫持 → 情绪/本能行动倾向↑（敏化-威胁标签） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

自定标签「敏化-威胁」+「抑制不足」（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| 5HT_baseline | −0.2（双标签） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：躯体症状病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。躯体症状 NPC 最终参数：NE=0.5、5HT=0.3、bias_somatic=+0.15、bias_limbic=+0.15（其余基线）。

---

## 四、行为覆盖/非线性跳变保留清单（新增病全新建）

> 躯体症状为新增病（Q0.2），无旧文件行为覆盖表——本节全部为文献驱动新建，标注 `[NEW]`。

### 4.1 行为覆盖（症状波动/焦虑放大）

| 条目 | 新挂接 | 说明 |
|------|--------|------|
| 内感受域 m_max > 0.3 → **症状波动**：每回合 10% 概率触发一次症状事件（SAN −1，症状相关 debuff 强化）[NEW] | **内感受域边群**（e01/e02/e03/e12，m_max 取最大值） | 内感受过敏 → 症状随机波动（Boeckle 2016 症状网络密度≈严重度，Borsboom 2017） |
| 转化接口 m_max > 0.3 → **焦虑放大**：情境焦虑相关事件触发时，症状事件概率 ×2 [NEW] | **ssd_e07/e08**（内感受↔杏仁核 双向） | 内感受→威胁评估放大环（e07）+ 威胁→内感受转化（e08）闭合 |
| 内脏学习 m_max > 0.3 → **症状记忆勾起**：创伤情景（#87 生成）匹配时，对应躯体症状强制激活 [NEW] | **ssd_e09**（entorhinal→insula） | 创伤情景→内脏反应记忆绑定（visceral learning）——#88 转化接口的内容端 |

### 4.2 非线性跳变（症状锁定/压制失效）

| 条目 | 新挂接 | 说明 |
|------|--------|------|
| 内感受域 m_max > 0.5 → **症状锁定**：内感受域边群强制激活不可被 L5 控制压制，SAN −2/回合 [NEW] | **ssd_e01**（insula→dACC）m > 0.5，作用域 = 内感受域边群 | 内感受过敏锁定（与 PTSD 防御锁定 / ASD 感官锁定同构，Borsboom 2017 滞回） |
| 创伤触发躯体化：转化接口 m_max > 0.4 → 10% 概率跳过当前行动窗口（症状发作）[NEW] | **ssd_e08**（Amygdala→insula）m > 0.4 | 心理创伤直接表达为躯体发作——#88 转化接口 |
| 调控失效：\|ssd_e10\| > 0.3 → vmPFC 对杏仁核压制效力 −50%（症状无法被认知压制）[NEW] | **ssd_e10**（vmPFC→Amygdala 解耦）\|m\| > 0.3 | 前额叶低激活（Boeckle 2016）→ 抑制不足结构性失效 |

---

## 五、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档可用（CGI-S 3-7），\|m\| ≤ 0.6 | somatic-symptom-pilot.md §二 / pathology_edges.json |
| 偏侧偏离量 | laterality_delta | 全 0（无稳健偏侧证据） | pathology_edges.json（§6.5 规则 2） |
| NE 基线偏离（躯体症状） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（躯体症状） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（躯体症状） | bias_somatic / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 症状波动触发阈值 | m_th | 0.3（每回合 10% 概率症状事件，SAN −1）[NEW] | §四.1 |
| 焦虑放大触发阈值 | m_th | 0.3（症状事件概率 ×2）[NEW] | §四.1 |
| 症状锁定阈值 | m_th | 0.5（SAN −2/回合，不可压制）[NEW] | §四.2 |
| 症状发作跳过阈值 | m_th | 0.4（10% 跳过行动窗口）[NEW] | §四.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [躯体症状障碍](../../../entities/diseases/%E8%BA%AF%E4%BD%93%E7%97%87%E7%8A%B6%E9%9A%9C%E7%A2%8D.md)（Q0.2 新增待建）, [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §十八, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §二/§四, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
