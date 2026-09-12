# PTSD 重映射试点 — 输出模板

> 26 病重映射的**第一个试点**（Grilling #88 Q0.6 执行建议：PTSD 先行钉模板）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **13 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = 防御域跨层短路（杏仁核→PAG 劫持 L0 防御）+ 抑制不足（vmPFC→杏仁核 解耦 / LC→dlPFC 结构受损）+ 记忆域闪回（ACC→海马旁 跨层短路）+ 唤醒域 NE 超敏。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §4.2 标签组合「敏化-威胁 + 抑制不足」完全一致——敌我同构闭环成立。**输出格式（§六）将被复制到其余 25 病。**

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（新格式试点行，含三体边核验列）](#二50-实体病理边表新格式试点行含三体边核验列)
3. [PTSD → 7 参数映射建议（4 tone + 3 CSTC）](#三ptsd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_312 等 → 新病理边）](#四旧链路对照表link_312-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [输出模板说明（供 25 病复制的字段规范）](#六输出模板说明供-25-病复制的字段规范)
7. [参数速查表](#七参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者，跨诊断 ALFF meta） | 静息态 ALFF meta | PTSD 特异性偏离 = **ALFF↑ 左侧杏仁核 + 海马**（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §2.3）→ 防御域/记忆域边的**方向 + 左偏 Δ**（e01/e02/e07/e08/e13） |
| 2 | **Opel et al. (2020)** *Biol Psychiatry* 88(9):678-686（ENIGMA 二次分析） | 结构 meta | PTSD 灰质模式与 SZ/BD/MDD/OCD **均无显著相关**——独立结构模式 → PTSD 边集独立设计（不共享他病结构因子）；慢性应激→前额叶萎缩 → e10 结构异常 |
| 3 | **Koch et al. (2016)** *Depress Anxiety*（PMID [26918313](https://pubmed.ncbi.nlm.nih.gov/26918313/)） | 静息态 meta | PTSD 静息态：**杏仁核/岛叶活动↑ + vmPFC 活动↓** → 确认「vmPFC→杏仁核 抑制 ↓」连接方向（NPC AI §5.2 第二支柱）→ e03 解耦沉默 + e05 内感受唤醒 |
| 4 | **RDoC v4（NIMH）** | 回路矩阵 | 急性威胁回路：杏仁核→vmPFC/dmPFC/ACC + **dPAG** → 防御域边集（e01/e02/e03）的回路级锚；唤醒/调节域：蓝斑 NE → e04/e05/e10 |

**辅助锚（方向/范围补充）**：

- **Cao et al. (2025)** *Mol Psychiatry*（杏仁核 FC meta，96 研究, 8,730 人）——杏仁核亚区连接跨诊断异常 → 杏仁核相关边群（e04/e09/e11/e13）的覆盖范围。
- **Shin & Liberzon (2010)**——PTSD 杏仁核过度反应 + NE 高唤醒（NPC AI §4.2 标签「敏化-威胁」文献锚）。
- **左右脑偏侧化-文献数据源.md §八**——ENIGMA PTSD：胼胝体（连接两海马节段）微结构完整性↓ → **海马间跨半球连接异常** → 记忆域边（e06/e08）左偏 Δ 的来源；Gordon (2010)：PTSD 无显著 EEG alpha 偏侧 → 偏侧仅作装饰层、不作核心机制（#92 原则）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——9 条旧链路的方向/量级/通路描述（LeDoux 2000 / Paxinos 2004 / 本仓脑干强度估计 / Craig 2009）作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（新格式试点行，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`——机制引用镜像 = 校验报错，偏侧化架构 §五）。**13 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**——PTSD 无正常图中不存在的连接；「病理新增」边类型规范见 §六.4。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（PTSD = `ptsd`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围` 过滤——2026-08-21 #88 待定项1 定案 B′**：范围下限 >3 无轻档、上限 <6 无重档；量级沿用旧文件设计校准）。

### 2.1 防御域（4 条）——「杏仁核→PAG 跨层短路」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ptsd_e01** ⭐新增 | Amygdala | PeriaqueductalGray | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedback, level_diff=−1（L1→L0） | **跨层短路** | +0.2/+0.4/+0.6 | **−0.3** | NPC AI §5.2（杏仁核→PAG↑）；RDoC 急性威胁 dPAG；Shin & Liberzon 2010 | 非线性跳变①（m>0.5 跨层短路锁定） |
| **ptsd_e02** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | +0.2/+0.3/+0.5 | **−0.3** | 旧 link_312（PAG→杏仁核中央核，LeDoux 2000 / Paxinos 2004）；RDoC dPAG | 非线性跳变①（作用域成员） |
| **ptsd_e09** | SuperiorColliculus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | +0.1/+0.3/+0.5 | −0.2 | 旧 link_317（上丘→杏仁核经丘脑枕快速通路，Paxinos 2004） | 行为覆盖①（威胁超敏侧翼） |
| **ptsd_e13** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | −0.2 | Guo 2026 共享纹状体 ALFF↑（§2.1）；CSTC limbic 门控被威胁信号劫持 | 3.1 节 bias_limbic 推导锚 |

### 2.2 唤醒域（3 条）——「蓝斑 NE 超敏」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ptsd_e04** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合 | 0/+0.2/+0.4 | 0 | 旧 link_332（蓝斑→杏仁核 NE，脑干强度估计）；RDoC 唤醒域 | 3.1 节 NE tone 推导锚 |
| **ptsd_e05** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_326（蓝斑→前脑岛 NE，脑干强度估计 fc=0.85（PINK 最强 hub））+ **吞并 link_315 语义**（见 §四） | 行为覆盖①（内感受过度警觉） |
| **ptsd_e10** | LocusCoeruleus | rostralmiddlefrontal | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | **结构异常** | −0.1/−0.2/−0.3 | 0 | 旧 link_328（蓝斑→dlPFC NE，脑干强度估计）；慢性应激→前额叶萎缩（思路链） | 行为覆盖③ + 非线性跳变③（dlPFC 压制失效） |

### 2.3 记忆域（3 条）——「海马旁回闪回」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ptsd_e06** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939；**注**：dk 节点 L2，但含 L5 fid（FrontalPoleSN，脑功能层级模型 §L5）→ L5 叙事监控↔L1 记忆提取直连 = 跨层短路语义 | **跨层短路** | +0.2/+0.4/+0.6 | **−0.3**（旧 link_003_L 即为 L 半球） | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89 L）；Guo 2026 左偏 | 行为覆盖② + 非线性跳变②（闪回） |
| **ptsd_e07** ⭐新增 | Amygdala | parahippocampal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3496 | 过度耦合 | +0.1/+0.2/+0.3 | −0.3 | Guo 2026（左杏仁核+海马 ALFF↑）；情景记忆被恐惧条件化劫持（思路链） | 行为覆盖①（情境匹配×2 记忆端） |
| **ptsd_e08** | DorsalRapheNucleus | Hippocampus | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | 过度耦合 | +0.1/+0.2/+0.3 | −0.2 | 旧 link_319（中缝背核→海马 5-HT，脑干强度估计 fc=0.75）；左海马 ALFF↑ Guo 2026 | 3.1 节 5HT tone 推导锚；创伤记忆固化 |

### 2.4 抑制/调制域（3 条）——「vmPFC→杏仁核抑制 ↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ptsd_e03** ⭐新增 | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | −0.2/−0.4/−0.6 | 0 | NPC AI §5.2（vmPFC→杏仁核抑制↓）；Koch 2016（PMID:26918313）；Shin & Liberzon 2010 | 行为覆盖③（L5 压制效力−50% 的结构基础） |
| **ptsd_e11** | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged 孪生边存在） | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_320（中缝背核→杏仁核 5-HT，脑干强度估计 fc=0.7） | 3.1 节 5HT tone 推导锚 |
| **ptsd_e12** ⭐新增 | Amygdala | lateralorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3391 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 文献数据源 §七 PTSD（↓BLA-OFC 恐惧加工） | 恐惧加工缺陷（回避行为支持） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ 负 = 左偏（Guo 2026 左杏仁核/海马 ALFF↑ + ENIGMA PTSD 左偏），0 = 无偏侧证据（脑干核团双侧合并，Gordon 2010 无显著 alpha 偏侧）。

---

## 三、PTSD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（供 25 病复制）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e04（LC→Amygdala 0/+0.2/+0.4）、e05（LC→insula）、e10（LC→rostralmiddlefrontal） | LC 出边群 3/3 命中且 m 随严重度升高 → 蓝斑 NE 广播全局上调 = 过度警觉（RDoC 唤醒域） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | PTSD 不主要累及奖赏回路（结构模式独立，Opel 2020） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e08（DR→Hippocampus）、e11（DR→Amygdala）过度耦合 | 中缝核 5-HT 传递异常聚焦于威胁/记忆回路 → 全局 5HT 基线↓（低 5HT = 去抑制，Soubrié 1986） |
| 5 | bias_somatic | **+0.15** | e01（Amygdala→PAG 跨层短路）、e03（vmPFC→Amygdala 解耦）、e10（LC→dlPFC 结构受损） | L0 防御反射被劫持 + 自上而下压制失效 → 躯体防御行动（逃跑/战斗）gate 无法关闭 |
| 6 | bias_cognitive | **0** | 无 cognitive 环路（Caudate）边群命中 | dlPFC 受损在脑干广播层（e10）非 CSTC cognitive gate 偏置；vmPFC 边属 prefrontal_limbic 特权通路 |
| 7 | bias_limbic | **+0.15** | e13（Amygdala→Accumbens-area CSTC limbic GO）、e01/e02（防御边群） | 边缘环路 gate 被威胁信号劫持 → 情绪/本能行动倾向↑ |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」+「抑制不足」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| 5HT_baseline | −0.2（双标签） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | 0 | 0 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：PTSD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。PTSD NPC 最终参数：NE=0.5、5HT=0.3、bias_somatic=+0.15、bias_limbic=+0.15（其余基线）。

---

## 四、旧链路对照表（link_312 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_312 | PAG→Amygdala | 过度耦合 +0.2/+0.3/+0.5 | **ptsd_e02**（PeriaqueductalGray→Amygdala） | ✅ 保留语义（端点/类型/量级不变） |
| link_317 | SuperiorColliculus→Amygdala | 过度耦合 +0.1/+0.3/+0.5 | **ptsd_e09** | ✅ 保留语义 |
| link_315 | PAG→Insula（经丘脑中继） | 跨层短路 0/+0.2/+0.3 | **无直连边**（三体图无 PAG→insula，旧链路 registry 数据为经丘脑中继） | ⚠️ **废弃直连**；语义转移至 e05（LC→insula NE 内感受唤醒）+ e01 作用域；「跨层短路锁定」跳变挂 e01（见 §五） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 0/+0.2/+0.4 | **ptsd_e04** | ✅ 保留语义 |
| link_320 | DorsalRapheNucleus→Amygdala | 过度耦合 0/+0.2/+0.3 | **ptsd_e11** | ✅ 保留语义（5-HT 广播表达） |
| link_326 | LocusCoeruleus→Insula | 过度耦合 0/+0.2/+0.3 | **ptsd_e05** | ✅ 保留语义（并吞 link_315） |
| link_003_L | ACC(L)→parahippocampal | 跨层短路 +0.2/+0.4/+0.6 | **ptsd_e06**（caudalanteriorcingulate→parahippocampal） | ✅ 保留语义 + **偏侧显式化**（Δ=−0.3 落病理边，原 L 后缀入字段） |
| link_319 | DorsalRapheNucleus→HippocampusCA1 | 过度耦合 +0.1/+0.2/+0.3 | **ptsd_e08** | ✅ 保留语义（fid 合并：HippocampusCA1 → 节点 Hippocampus） |
| link_328 | LocusCoeruleus→RostralMiddleFrontalDLPFC | 结构异常 −0.1/−0.2/−0.3 | **ptsd_e10** | ✅ 保留语义（fid 合并：DLPFC → 节点 rostralmiddlefrontal） |
| （旧表无） | 杏仁核→PAG 跨层短路（思路链仅叙事层） | — | **ptsd_e01** | ⭐ 新增——核心机制落数据 |
| （旧表无） | vmPFC→杏仁核 抑制↓（NPC AI §5.2） | — | **ptsd_e03** | ⭐ 新增——核心机制落数据 |
| （旧表无） | BLA-OFC 恐惧加工↓（文献 §七 PTSD） | — | **ptsd_e12** | ⭐ 新增 |
| （旧表无） | 杏仁核→腹侧纹状体 威胁→门控劫持（Guo 2026 共享纹状体 ALFF↑ + CSTC limbic） | — | **ptsd_e13** | ⭐ 新增——bias_limbic 机制锚 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_315 → e05），「病理新增」从严（须文献支持新连接存在，见 §六.4）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 记忆域 m_max > 0.5 → 情境匹配权重 ×2 | ✅ 保留（改挂接） | **记忆域边群**（e06/e07/e08，m_max 取三条最大值） | 创伤相关刺激触发全网络激活；「记忆域」在新格式 = 记忆域病理边集 |
| link_003_L m > 0.4 → 闪回触发：10% 概率跳过当前行动窗口 | ✅ 保留 | **ptsd_e06** m > 0.4 | 同义替换（ACC→海马旁 跨层短路） |
| link_328 \|m\| > 0.3 → L5 控制·主动 对 L0-L2 防御链路压制效力 −50% | ✅ 保留（强化） | **ptsd_e10** \|m\| > 0.3 + **ptsd_e03**（结构基础） | 慢性应激→LC→dlPFC 受损；e03 vmPFC→杏仁核 解耦使压制失效从「效力减半」升级为「结构失效」 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_312 m > 0.5 → 跨层短路锁定（防御域不受 L0 以上抑制，SAN −2/回合），作用域 link_312+link_315 | ✅ 保留（改作用域） | **ptsd_e01** m > 0.5，作用域 = **防御域边群**（e01/e02/e13） | link_315 已废弃并入 → 作用域收敛为防御域病理边集 |
| link_003_L m > 0.5 → 闪回频率↑（每回合 20% 随机激活一条防御域链路） | ✅ 保留 | **ptsd_e06** m > 0.5 | 同义替换 |
| 认知控制域 \|m\| > 0.3 → dlPFC 自上而下控制压制 L1-L2 失效 | ✅ 保留 | **ptsd_e10** \|m\| > 0.3 | 同义替换（慢性应激→前额叶萎缩，Opel 2020 佐证） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_312, link_317, link_003_L, link_332 | **ptsd_e01, ptsd_e03, ptsd_e04, ptsd_e06** |
| 2（关联） | link_315, link_320, link_326, link_319 | **ptsd_e02, ptsd_e05, ptsd_e07, ptsd_e09, ptsd_e08, ptsd_e11, ptsd_e13** |
| 1（边缘） | link_328 | **ptsd_e10, ptsd_e12** |

> 核心 4 条 = 跨层短路核心（e01）+ 抑制不足核心（e03）+ 唤醒核心（e04）+ 闪回核心（e06）；新增边中 e12/e13 落关联/边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、输出模板说明（供 25 病复制的字段规范）

> 本节即**26 病复制模板**。其余 25 病按此字段规范产出，格式与本节完全一致。

### 6.1 病理边字段规范（pathology_edges.json 行 schema，✅ 已定稿 2026-08-21 #88 待定项2 + 遗留项1）

> **定稿决策（#88 待定项2 + 遗留项1）**：① 文件位置 `data/connectivity/pathology_edges.json`（与 tripartite_model.json 同层）；② **平铺数组**结构（`edges: [...]`，不按病分组），检索/校验经 `edge_id` 前缀；③ `edge_id = <disease_id>_e<NN>` 作**全局主键**（唯一性由 frontmatter 疾病ID 保证）；④ 顶层 `_schema_version: "1.1"`（v1.1 新增相位键）。
>
> **m_offset 双形态（v1.1，2026-08-21 遗留项1 定案）**：
> - **普通病**：`[轻, 中, 重]` 三值数组（`null` 占位 = 无此档，B′ 档位过滤）
> - **双向振荡（仅 bipolar-I/bipolar-II）**：`{"mania": [三档], "depression": [三档]}` 相位键——躁狂极/抑郁极各自三档；结算按当前心境相位 S ∈ {躁狂相, 抑郁相} 取对应极。**相位键出现 ⇔ disease_id ∈ {bipolar-I, bipolar-II}**（校验器强制约束）
> - **双向振荡 = 状态机机制，非第 5 病理类型**：底层病理类型仍按 §6.3 四类判定（躁狂极取过度耦合语义、抑郁极取解耦沉默语义），相位键表达"随相位在两类间切换"
> - **轻量时变（环性等）**：无相位键，用 hooks 挂接"边 m 时变 ±0.05"或行为循环状态机（L1/L2 层级，不进 m_offset）

```json
{
  "_description": "病理边注册表 — 26 病 → 三体模型病理边（Grilling #88）",
  "_schema_version": "1.0",
  "edges": [
    {
      "edge_id": "ptsd_e01",
      "source": "Amygdala",
      "target": "PeriaqueductalGray",
      "edge_type": "privileged_pathway",
      "tripartite_verified": "brainstem_subcortical; dir=feedback; level_diff=-1",
      "pathology_type": "跨层短路",
      "m_offset": [0.2, 0.4, 0.6],
      "laterality_delta": -0.3,
      "literature": "NPC AI §5.2; RDoC dPAG; Shin & Liberzon 2010",
      "hooks": "非线跳①"
    }
  ]
}
```

### 6.2 端点名对照速查（文献名 → 游戏节点名）

| 文献名 | 游戏节点（dk_name） | 层级 |
|--------|-------------------|:---:|
| vmPFC / mPFC 腹内侧 | `medialorbitofrontal`（fid MedialOrbitalPrefrontalVMPFC） | L5 |
| dlPFC / 背外侧前额叶 | `rostralmiddlefrontal` | L5 |
| OFC / 眶额皮层 | `lateralorbitofrontal` | L2 |
| ACC（背侧/吻侧） | `caudalanteriorcingulate` / `rostralanteriorcingulate` | L2（前者含 L5 fid） |
| 前脑岛 | `insula` | L2 |
| 杏仁核 | `Amygdala` | L1 |
| 海马 | `Hippocampus`（fid CA1/CA3 合并） | L1 |
| 海马旁回 | `parahippocampal` | L1 |
| 伏隔核/腹侧纹状体 | `Accumbens-area` | L1 |
| 蓝斑 | `LocusCoeruleus`（禁 LC_R） | L0 |
| 中缝背核 | `DorsalRapheNucleus` | L0 |
| PAG / 导水管周围灰质 | `PeriaqueductalGray` | L0 |
| 上丘 | `SuperiorColliculus` | L0 |

### 6.3 四类病理类型 → 三体模型判定规则（旧「四规则」重定义）

| 病理类型 | 三体判定规则（机械可核验） | 旧语义对应 | PTSD 实例 |
|---------|--------------------------|-----------|----------|
| **跨层短路** | 边 m 正偏移 + 满足其一：(a) 边类型 ∈ {privileged_pathway, brainstem} 且端点含 L0 或 L5（特权/广播直达反射或叙事）；(b) CC 边端点含 L5 fid（如 caudalanteriorcingulate/FrontalPoleSN）且对端为 L1-L2 记忆/情绪节点。语义：信号绕过 L2-L4 中间调制 | 旧「层级相邻被破」 | e01（L1→L0）、e06（L5-fid→L1） |
| **过度耦合** | 合法边（CC 双向互惠 / privileged / brainstem 广播）m 正偏移，闭环无法终止（不衰减） | 旧「双向不对称」 | e02/e04/e05/e07/e08/e09/e11/e13 |
| **解耦沉默** | 合法边 m 负偏移（信号发不出） | 旧「协同激活被断」 | e03（−0.2/−0.4/−0.6）、e12 |
| **结构异常** | (a) 边类型 = `病理新增`（端点组合不在 1049 边集合）；(b) brainstem 广播边**选择性** m 负偏移（投射腿结构受损，非全局 tone 变化） | 旧「结构存在被破」 | e10（LC→dlPFC 腿受损） |

### 6.4 「病理新增」边类型规范

- 触发条件：source/target 组合在 tripartite_model.json 四列表（cstc 47 + corticocortical 776 + brainstem 114 + privileged_pathways 112）**均未命中**。
- 处置优先级：**语义转移优先**（找同功能域/同调质现有边承载，如 PTSD link_315 PAG→insula → e05 LC→insula）；确需保留直连才标 `病理新增`（须有文献支持该连接在疾病中出现）。
- 校验：`validate_disease.py` 后续按本规则升级（查四列表命中；命中即用原 type，未命中报 `病理新增` 提示人工复核）。

### 6.5 laterality_delta 赋值规则

1. 文献「左/右」→ 负/正（左→−、右→+，偏侧化架构 §四.1）。
2. 无偏侧证据 → 0（Gordon 2010：PTSD 无显著 alpha 偏侧；脑干核团双侧合并主变体 = 0）。
3. **跨半球异常（如 PTSD 胼胝体/海马间）→ 落到相关病理边 Δ，不新增 L↔R 边**（合并节点图无 L↔R 边，#92 定案：跨半球载体 = 17 条自连的偏侧系数）。
4. 幅度：效应量 |d| < 0.1 不做（#92 成本原则）；PTSD 试点取 0.2~0.3（Guo 2026 左杏仁核/海马 ALFF↑ 为疾病特异性偏离）。

### 6.6 7 参数推导规则（供 25 病复制）

1. **tone 从脑干广播边群推导**：LC 出边群 → NE_baseline；DR 出边群 → 5HT_baseline；VTA 出边群 → DA_VTA_baseline；SNc 出边群 → DA_SNc_baseline。边群 m 正偏移 → tone ↑，负偏移 → tone ↓，混合 → 按主导方向。
2. **bias 从 CSTC 环路边推导**：somatic 环路（Putamen）边群 → bias_somatic；cognitive 环路（Caudate）边群 → bias_cognitive；limbic 环路（Accumbens-area）边群 → bias_limbic。
3. **量级沿用 NPC AI §4.2 标签校准**（tone ±0.1~±0.2、bias ±0.15），方向有文献、幅值待数值校准。
4. **强制交叉验证**：推导结果必须与 NPC AI §4.2 标签组合一致（§3.2 式验证表），不一致 → 回查病理边集或标签选择。

### 6.7 输出文件清单

1. 本模板（ptsd-pilot.md）→ 复制为 25 份疾病试点。
2. 疾病目录 md 迁移：旧 `## 链路配置` 表 → 新病理边引用（§二/§四 格式）。
3. `pathology_edges.json`（待 #88 创建，schema 以本模板 §6.1 定稿；落点见偏侧化架构 §九.1）。
4. NPC 7 参数表：26 病 → 7 参数偏离值入库（NPC AI 行为模型 §5.2 扩展）。

---

## 七、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6，m ∈ [0,1] 钳制 | pathology_edges.json（§6.1） |
| 偏侧偏离量 | laterality_delta | 0（默认），∈ [−1,+1] | pathology_edges.json（§6.5） |
| NE 基线偏离（PTSD） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（PTSD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（PTSD） | bias_somatic / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 跨层短路锁定阈值 | m_th | 0.5（e01，SAN −2/回合） | §五.2 |
| 闪回触发阈值 | m_th | 0.4（10% 跳过行动窗口）/ 0.5（每回合 20%） | §五.1/§五.2 |
| 标签派生阈值 | t | 0.5 [NEW 初值可调] | 偏侧化架构 §六.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [创伤后应激障碍](../../../entities/diseases/%E5%88%9B%E4%BC%A4%E5%90%8E%E5%BA%94%E6%BF%80%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §十八, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [左右脑偏侧化-文献数据源](../../../../reference/literature/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八, [角色与面具](../../../entities/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
