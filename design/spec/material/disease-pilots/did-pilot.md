# DID 重映射试点

> 解离性身份障碍（DID）重映射试点（Grilling #88 Q0.6 第二批）。旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **14 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **整合域 DMN 叙事重构解耦沉默**（DMN 叙事链断开，非"边界崩溃"而是"区隔化"——与偏执型精分方向相反）+ **记忆域区隔化**（海马旁回不同身份状态间信息不流通，对接记忆内容层 #90 COMPARTMENTALIZED）+ **dmPFC↑ 过度监控**（过度激活试图维持控制但失败）。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §4.2 标签组合「敏化-威胁 + 反刍」一致。**档位过滤：CGI-S 4-7 无轻档（m 三档首元素恒 0）；laterality_delta 全部默认 0（无稳健偏侧证据，旧 `_L` 后缀 = ENIGMA 数据采集侧非疾病偏侧，遵循 #92 原则）。**

## 目录

1. [文献锚点（3 篇核心 + 关键数据点）](#一文献锚点3-篇核心--关键数据点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [DID → 7 参数映射建议（4 tone + 3 CSTC）](#三did--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_082_L 等 → 新病理边）](#四旧链路对照表link_082_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（3 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Lotfinia et al. (2020)** *J Psychiatr Res*（系统综述, 33 MRI 研究） | 结构系统综述 | 额叶（额上回/中央前回/扣带回）+ 颞叶（颞下/中/上回 + 梭状回）灰质体积↓；岛叶+杏仁核异常；**白质完整性↓ 跨几乎所有脑叶，含杏仁核-海马连接**（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 DID）→ 记忆域边（e04-e07）+ 整合域边（e01-e03）的结构基础 |
| 2 | **Reinders et al. (2019)** *Br J Psychiatry*（最大 DID 结构样本） | 结构影像 | 额颞广泛灰质体积↓；**身份状态切换→尾状核功能网络改变；ANP（表观正常人格）对情绪面孔全脑活动↓；EP（情绪人格）海马旁回右侧过度激活** → e09/e11（尾状核）+ e07（ANP 面孔加工↓）+ e06（EP 海马旁↑） |
| 3 | **2022 系统综述（13 静息态研究）** | 静息态综述 | **前额叶（尤其 dmPFC）过度激活 + DMN 区 hyperactivation**（文献数据源 §七 DID）→ e08（dmPFC 过度监控）+ e01-e03（DMN 叙事重构↓）的方向/范围锚 |

**辅助锚（方向/范围补充）**：

- **NPC AI §4.2 标签**——「敏化-威胁 + 反刍」为 DID 默认标签（旧文件）：NE/5HT/bias_limbic/bias_cognitive 通道锚（e11-e14），验证见 §三。
- **记忆内容层（../../../设计归档/grilling/grilling-90-memory-storage/grilling-90.md）**——#90 生命周期八状态含 **COMPARTMENTALIZED**（区隔化）状态：DID 记忆区隔化 = 内容层记忆被标记 COMPARTMENTALIZED（身份状态间不共享），机制层载体 = e05（parahippocampal→Hippocampus 解耦沉默）→ 内容层对接（§五）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——7 条旧链路的方向/量级/通路描述（ENIGMA 强度）作为语义继承源，见 §四。
- **ENIGMA 偏侧化数据源**——DID 无稳健偏侧证据（任务裁定）：旧 `_L` 后缀 = ENIGMA 数据采集侧（单侧 ROI），非疾病侧向证据 → laterality_delta 全 0（#92 原则：无稳健偏侧 → 默认 0）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`——机制引用镜像 = 校验报错，偏侧化架构 §五）。**14 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（DID = `did`）。三档 m 偏移 = 轻/中/重（**档位过滤 B′：CGI-S 4-7 范围下限 >3 → 无轻档，轻档恒 0**；量级沿用旧文件设计校准）。laterality_delta 全 0（§6.5 规则 2：无偏侧证据；旧 `_L` = 数据采集侧）。
>
> **端点名对照速查（文献名 → 游戏节点）**：dmPFC/mPFC 背内侧 = `superiorfrontal`（fid SuperiorFrontalMPFC, L5）；vmPFC/DMN 腹内侧 = `medialorbitofrontal`（fid MedialOrbitalPrefrontalDMN/VMPFC, L5）；dlPFC = `rostralmiddlefrontal`（L5）；ACC = `caudalanteriorcingulate`（L2，含 L5-fid FrontalPoleSN）；颞极 = `temporalpole`（L2）；后扣带 = `posteriorcingulate`（L2）；楔前叶 = `precuneus`（L4）；角回 = `inferiorparietal`（L4）；海马 = `Hippocampus`（L1）；海马旁回 = `parahippocampal`（L1）；杏仁核 = `Amygdala`（L1）；尾状核 = `Caudate`（L1）；伏隔核/腹侧纹状体 = `Accumbens-area`（L1）；蓝斑 = `LocusCoeruleus`（L0）；中缝背核 = `DorsalRapheNucleus`（L0）；梭状回 = `fusiform`（L4）。

### 2.1 整合域（3 条）——「DMN 叙事重构↓ 解耦沉默」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e01** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287（L5↔L5） | **解耦沉默** | 0/−0.3/−0.5 | 0 | 旧 link_082_L（mOFC→DLPFC 自传体记忆）；Lotfinia 2020 额叶 GMV↓ | 行为覆盖①（整合域 m_max） |
| **did_e02** ⭐新增 | medialorbitofrontal | inferiorparietal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1867（DMN mPFC↔角回 叙事核心） | **解耦沉默** | 0/−0.2/−0.4 | 0 | 旧 link_134 语义转移（PCC→mOFC 自传体记忆 → DMN mPFC↔AG 叙事整合）；Reinders 2019 额颞 GMV↓ | 行为覆盖① + 非线性跳变①（整合域完全解耦） |
| **did_e03** ⭐新增 | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2, edr=0.4926（PCC↔precuneus DMN core-to-core） | **解耦沉默** | 0/−0.2/−0.4 | 0 | DMN 核心断开（后扣带内省中心失联）；Lotfinia 2020 扣带回 GMV↓ | 行为覆盖③（后扣带内省不可用） |

### 2.2 记忆域（4 条）——「区隔化 + 创伤记忆侵入」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e04** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939；**注**：dk 节点 L2，但含 L5-fid（FrontalPoleSN，脑功能层级模型 §L5） | **解耦沉默** | 0/−0.2/−0.4 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89）；Lotfinia 2020 白质完整性↓ | 行为覆盖②（记忆区隔化） |
| **did_e05** ⭐新增 | parahippocampal | Hippocampus | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3773（海马旁回→海马 记忆写入闸门） | **解耦沉默** | 0/−0.2/−0.4 | 0 | 记忆区隔化的写入闸门断开（区隔化内容层载体 → #90 COMPARTMENTALIZED 对接）；Lotfinia 2020 杏仁核-海马白质↓ | 行为覆盖② + #90 内容层挂接 |
| **did_e06** | Hippocampus | Amygdala | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.6506（海马 CA1↔杏仁核 双向） | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_354（HC→Amygdala，Zhou 2015）；Lotfinia 2020 杏仁核-海马连接白质异常；EP 海马旁过度激活（Reinders 2019） | 非线性跳变②（创伤记忆侵入特定人格状态） |
| **did_e07** ⭐新增 | Amygdala | parahippocampal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3496（杏仁核→海马旁 情绪化情景记忆） | 过度耦合 | 0/+0.1/+0.2 | 0 | 创伤情绪→情景记忆绑定（EP 状态创伤记忆侵入特定身份）；Reinders 2019 EP 海马旁↑ | 行为覆盖②（情境匹配×记忆端） |

### 2.3 自我社会域（2 条）——「自我参照不稳定 + ANP 面孔加工↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e08** ⭐新增 | superiorfrontal | caudalanteriorcingulate | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−3（dmPFC→dACC 监控反馈，dACC↔mPFC salience-SN interface） | **过度耦合** | 0/+0.2/+0.3 | 0 | 旧 link_008_L 语义转移（ACC→dlPFC 情绪调节 结构异常 → dmPFC 过度监控）+ **dmPFC 静息态过度激活**（2022 综述 13 研究） | 非线性跳变③（过度监控：L5 压制效力结构性失效） |
| **did_e09** | caudalanteriorcingulate | superiorfrontal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+3（dACC→mPFC） | **解耦沉默** | 0/−0.2/−0.4 | 0 | 旧 link_009_L（ACC→mPFC 情绪面孔加工，ENIGMA 10.27）；Reinders 2019 ANP 对情绪面孔全脑活动↓ | 行为覆盖②（身份切换时情绪加工断开） |

### 2.4 自我参照/社会标签（1 条）——「颞极自我参照不稳定」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e10** ⭐新增 | caudalanteriorcingulate | temporalpole | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3287（ACC↔颞极 自我参照/识人） | **解耦沉默** | 0/−0.1/−0.3 | 0 | 旧 link_086_L 语义转移（mOFC→颞极 ToM 自我参照 → ACC↔颞极）；Lotfinia 2020 颞叶 GMV↓（颞极识人功能不稳定） | 行为覆盖③（"我是谁"无法回答） |

### 2.5 认知控制域（1 条）——「尾状核功能网络改变」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e11** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.2 | 0 | Reinders 2019 身份状态切换→尾状核功能网络改变；CSTC cognitive 门控被身份切换信号劫持 | 3.1 节 bias_cognitive 推导锚 |

### 2.6 唤醒/奖赏域（3 条）——「敏化-威胁 + 反刍 标签通道」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **did_e12** ⭐新增 | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.2 | 0 | NPC AI §4.2 敏化-威胁（bias_limbic 锚）；EP 状态威胁→趋避门控劫持 | 3.1 节 bias_limbic 推导锚 |
| **did_e13** ⭐新增 | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1（LC→杏仁核 NE） | 过度耦合 | 0/+0.1/+0.2 | 0 | NPC AI §4.2 敏化-威胁 NE 通道；DID EP 状态高唤醒/威胁监控 | 3.1 节 NE tone 推导锚 |
| **did_e14** ⭐新增 | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged 孪生边存在：Lowry 2008 DR→amygdala 5-HT） | 过度耦合 | 0/+0.1/+0.2 | 0 | NPC AI §4.2 敏化-威胁 + 反刍（5HT 聚焦异常→全局↓）；DID 冲动/情绪去抑制 | 3.1 节 5HT tone 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ 全 0 = 无稳健偏侧证据（旧 `_L` 后缀 = ENIGMA 数据采集侧，非疾病偏侧，#92 原则）。

---

## 三、DID → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（§6.6）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e13（LC→Amygdala 过度耦合） | LC 出边命中且 m 随严重度升高 → 蓝斑 NE 广播全局上调（敏化-威胁标签：EP 状态高唤醒/威胁监控） |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | DID 不主要累及奖赏回路（结构模式独立，Opel 2020 四病共享因子不含 DID） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e14（DR→Amygdala 过度耦合） | 中缝核 5-HT 传递异常聚焦于威胁/记忆回路 → 全局 5HT 基线↓（低 5HT = 去抑制，Soubrié 1986；敏化-威胁+反刍双标签） |
| 5 | bias_somatic | **0** | 无 somatic 环路（Putamen）边群命中 | DID 无躯体防御/运动环路病理 |
| 6 | bias_cognitive | **+0.15** | e11（rMF→Caudate cognitive GO 过度耦合）、e08（dmPFC→ACC 过度监控） | 认知环路 gate 被身份切换/过度监控信号劫持 → 语言/认知行动倾向↑（反刍标签：过度监控"关不掉"） |
| 7 | bias_limbic | **+0.15** | e12（Amygdala→Accumbens-area limbic GO）、e06/e07（创伤记忆侵入） | 边缘环路 gate 被创伤/情绪信号劫持 → 情绪/本能行动倾向↑（敏化-威胁标签） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-威胁」+「反刍」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁，max 反刍 −0.1） | +0.2 | ✅ |
| 5HT_baseline | −0.2（敏化-威胁） | −0.2 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | +0.15（反刍） | +0.15 | ✅ |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**结论**：DID 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。DID NPC 最终参数：NE=0.5、5HT=0.3、bias_cognitive=+0.15、bias_limbic=+0.15（其余基线）。

---

## 四、旧链路对照表（link_082_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 解耦沉默 0/−0.3/−0.5 | **did_e01**（medialorbitofrontal→rostralmiddlefrontal） | ✅ 保留语义（端点/类型/量级不变） |
| link_134 | PosteriorCingulate→MedialOrbitalPrefrontalDMN | 解耦沉默 0/−0.2/−0.4 | **did_e02**（medialorbitofrontal→inferiorparietal） | ⚠️ **端点转移**（三体图无 PCC→mOFC 直连，语义移至 DMN 叙事核心 mPFC↔角回）+ 新增 did_e03（PCC→precuneus）承载 PCC 端语义 |
| link_003_L | AnteriorCingulateCortex→Parahippocampal | 解耦沉默 0/−0.2/−0.4 | **did_e04**（caudalanteriorcingulate→parahippocampal） | ✅ 保留语义（偏侧后缀移除：`_L` = 数据采集侧非疾病偏侧） |
| link_354 | HippocampusCA1→Amygdala | 跨层短路 0/+0.2/+0.3 | **did_e06**（Hippocampus→Amygdala） | ✅ 保留语义（**类型重分类**：CC 边 L1↔L1 无 L0/L5 端点，不满足 §6.3 跨层短路判定 → 过度耦合；fid 合并 HippocampusCA1→Hippocampus） |
| link_009_L | AnteriorCingulateCortex→SuperiorFrontalMPFC | 解耦沉默 0/−0.2/−0.4 | **did_e09**（caudalanteriorcingulate→superiorfrontal） | ✅ 保留语义 |
| link_086_L | MedialOrbitalPrefrontalDMN→TemporalPole | 解耦沉默 0/−0.1/−0.3 | **did_e10**（caudalanteriorcingulate→temporalpole） | ⚠️ **端点转移**（三体图无 mOFC→TP 直连 → ACC↔颞极 自我参照） |
| link_008_L | AnteriorCingulateCortex→RostralMiddleFrontalDLPFC | 结构异常 0/+0.2/+0.3 | **did_e08**（superiorfrontal→caudalanteriorcingulate） | ⚠️ **语义转移**（三体图无 ACC→rMF 直连 → dmPFC→dACC 过度监控，方向反转承载 dmPFC 过度激活，类型 结构异常→过度耦合） |
| （旧表无） | 海马旁回→海马 区隔化闸门（思路链仅叙事层） | — | **did_e05** | ⭐ 新增——#90 内容层对接（COMPARTMENTALIZED） |
| （旧表无） | 杏仁核→海马旁回 创伤情绪侵入（思路链 CA1↔杏仁核↑） | — | **did_e07** | ⭐ 新增 |
| （旧表无） | 尾状核功能网络改变（Reinders 2019 任务态） | — | **did_e11** | ⭐ 新增——bias_cognitive 机制锚 |
| （旧表无） | 杏仁核→腹侧纹状体 威胁→门控劫持（敏化-威胁） | — | **did_e12** | ⭐ 新增——bias_limbic 机制锚 |
| （旧表无） | LC→杏仁核 NE / DR→杏仁核 5HT（标签通道） | — | **did_e13 / did_e14** | ⭐ 新增——tone 推导锚 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_134 → e02+e03、link_086_L → e10、link_008_L → e08），「病理新增」从严（本表 0 条病理新增，全部命中现有三体边）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 整合域 \|m\| > 0.3 → 身份切换（每 10 回合人格状态切换，随机另一套行为表，持续 2 回合） | ✅ 保留（改挂接） | **整合域边群**（e01/e02/e03，m_max 取三条最大值） | 身份切换 = DMN 叙事重构断开的涌现结果；「整合域」在新格式 = 整合域病理边集 |
| 记忆域 \|m\| > 0.3 → 海马旁回区隔化（前 3 回合激活链路切换后遗忘，不可同情境复用） | ✅ 保留（强化 + #90 对接） | **记忆域边群**（e04/e05/e06/e07）| e05（PHG→HC 写入闸门）为区隔化内容层载体：内容层记忆标记 COMPARTMENTALIZED（#90 生命周期八状态），机制层 = 本边群 |
| 自我社会域 \|m\| > 0.3 → 后扣带内省 不可用（"我是谁"无法回答） | ✅ 保留 | **did_e03**（PCC→precuneus）+ **did_e10**（ACC↔颞极） | 后扣带内省断开 + 颞极识人功能不稳定 双载体 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 整合域 m_max < −0.5 → 整合域完全解耦（DMN/FPN/SN 三网络独立运行无协调）；SAN=0 时触发随机行为，DID 在 SAN>0 即可局部触发 | ✅ 保留（改挂接） | **did_e01/e02/e03**（整合域边群，m_max 取最大值） | 区隔化非线性锁定：与偏执型精分"边界崩溃"方向相反（墙太厚 vs 墙倒塌） |
| （新增）创伤记忆侵入：记忆域 m_max > 0.4 → 10% 概率跳过当前行动窗口（闪回式侵入） | ⭐ 新增 [NEW] | **did_e06**（HC→Amygdala）m > 0.4 | 与 PTSD e06 闪回同构但触发源 = 身份状态绑定记忆（EP 专属创伤记忆） |
| （新增）过度监控锁定：\|did_e08\| > 0.3 → L5 控制·主动 对 L0-L2 压制效力 −50%（dmPFC 过度激活的"控制失败"） | ⭐ 新增 [NEW] | **did_e08**（dmPFC→dACC）| 与 PTSD e10 压制失效同构；DID 方向 = 过度监控而非结构受损 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 1（核心） | link_082_L, link_003_L, link_009_L | **did_e01, did_e04, did_e08, did_e09** |
| 1（关联） | link_134, link_354, link_086_L, link_008_L | **did_e02, did_e03, did_e05, did_e06, did_e07, did_e10, did_e11, did_e12** |
| 1（边缘） | — | **did_e13, did_e14**（标签通道边，非核心机制） |

> 核心 = 整合域叙事重构（e01）+ 记忆区隔化（e04）+ dmPFC 过度监控（e08）+ ANP 面孔加工↓（e09）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 中/重两档可用（轻档恒 0，CGI-S 4-7 无轻档），\|m\| ≤ 0.6 | did-pilot.md §二 / pathology_edges.json |
| 偏侧偏离量 | laterality_delta | 全 0（无稳健偏侧证据；旧 `_L` = 数据采集侧） | pathology_edges.json（§6.5 规则 2） |
| NE 基线偏离（DID） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（DID） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（DID） | bias_cognitive / bias_limbic | +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 身份切换触发阈值 | m_th | 0.3（整合域边群，每 10 回合切换，持续 2 回合） | §五.1 |
| 区隔化触发阈值 | m_th | 0.3（记忆域边群，切换后前 3 回合记忆不可复用） | §五.1 |
| 整合域完全解耦阈值 | m_th | 0.5（SAN>0 可局部触发） | §五.2 |
| 创伤侵入触发阈值 | m_th | 0.4（10% 跳过行动窗口）[NEW 初值可调] | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [grilling-90 记忆内容层](../../../archive/grilling/grilling-90-memory-storage/grilling-90.md), [解离性身份障碍](../../../entities/diseases/%E8%A7%A3%E7%A6%BB%E6%80%A7%E8%BA%AB%E4%BB%BD%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §十八, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [左右脑偏侧化-文献数据源](../../../../reference/literature/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八, [角色与面具](../../../entities/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
