# 重度抑郁症（MDD）重映射试点

> Grilling #88 26 病重映射的第二份试点（抑郁症谱系先行，与 PTSD 试点同格式）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **15 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」），每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = 奖赏域 VTA→NAcc 解耦沉默（快感缺失）+ 反刍域 DMN 核心过度耦合（后扣带-楔前叶）+ 认知控制域 dlPFC 门控解耦 + 内感受域 NE/岛叶耦合异常。**偏侧：全边 laterality_delta = 0**（de Kovel et al. 2019 ENIGMA：MDD 无结构偏侧改变；旧 `_L` 后缀链路全部入 0 处置，见 §四）。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §5.2「过度抑制 + 反刍（+ 快感缺失变体 敏化-奖励负）」标签组合交叉验证成立——敌我同构闭环成立。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（15 条，含三体边核验列）](#二50-实体病理边表15-条含三体边核验列)
3. [MDD → 7 参数映射建议（4 tone + 3 CSTC）](#三mdd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **ENIGMA MDD（Schmaal et al. 2016）** *Mol Psychiatry* 21(6):806-812（MDD WG，10 队列） | 结构 meta | 亚皮层体积：**海马↓（复发型）**、杏仁核↓（早发型）、丘脑↓（自杀史）；MDD 效应量 < SCZ（Cheon 2022 梯度 SZ>BD>MDD）→ 奖赏/记忆域边的结构锚（e01/e04/e14/e15 量级克制） |
| 2 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者，跨诊断 ALFF meta） | 静息态 ALFF meta | MDD 特异性偏离 = **ALFF↑ IFG/岛叶/ACC-mPFC/顶下小叶/额中回，ALFF↓ 小脑/距状裂**（[疾病-脑区链路映射-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §2.3）→ 内感受/反刍域边的方向（e05/e06/e10/e13）；岛叶 ALFF↑ 为六病共享（§2.1）→ e11/e12 内感受承载 |
| 3 | **RDoC v4（NIMH）** | 回路矩阵 | 正性效价（奖赏评估/预期/学习）：OFC、腹侧纹状体、VTA/SN、外侧缰核 → MDD；负性效价（丧失）：DMN、海马、OFC、奖赏回路 → MDD（文献数据源 §四.1）→ 奖赏域边集（e01-e04）+ DMN 反刍边集（e05-e07）的回路级锚 |
| 4 | **de Kovel et al. (2019)** *Am J Psychiatry*（ENIGMA MDD WG 二次分析） | 偏侧 null | **MDD 脑结构偏侧无显著改变（大样本 null）**——见 [ENIGMA偏侧化-精神疾病大样本meta-文献数据源.md](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) → **全边 laterality_delta = 0，不引入偏侧机制**（§6.5 规则 2） |

**辅助锚（方向/范围补充）**：

- **Hamilton et al. (2015)**——抑郁 DMN 过度连接（NPC AI §4.2「反刍」标签的文献依据）→ e05/e06 DMN 过度耦合。
- **Ma et al. (2019)**——DMN-FPN 反相关减弱为 MDD trait marker → e07（mOFC↔dlPFC 边界边）「边界崩溃」语义转移源。
- **文献数据源 §七 MDD**——核心回路「↓NAcc-丘脑, ↓NAcc-海马; VTA→NAcc 解耦」+ 对应功能域「奖赏域/自我社会域/行动门控域(苍白球↓)/认知控制域」→ e09（Pallidum→Thalamus）新增依据。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——11 条旧链路的方向/量级/通路描述（Schultz 1997 / Paxinos 2004 / Hansen 2024 / ENIGMA）作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；m 偏移量级沿用旧文件设计校准值，**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（15 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**15 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**——MDD 无正常图中不存在的连接。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（MDD = `mdd`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围: 3-7` 过滤——B′ 定案：下限 3 非 >3 → 轻档可用，上限 7 非 <6 → 重档可用，三档全**；量级沿用旧文件设计校准）。

### 2.1 奖赏域（4 条）——「VTA→NAcc 解耦沉默」快感缺失核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **mdd_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **解耦沉默** | −0.1/−0.3/−0.5 | 0 | 旧 link_336（VTA→NAcc 中脑边缘 DA，Schultz 1997 fc=0.9）；文献数据源 §七 MDD「VTA→NAcc 解耦」；RDoC 正性效价 | 行为覆盖①（趋近·主动 不可用）+ 非线性跳变①（作用域核心） |
| **mdd_e02** | VentralTegmentalArea | superiorfrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_338（VTA→mPFC DA，Hansen 2024 fc=0.6）；VTA→mPFC 奖赏价值整合通路解耦（思路链） | 非线性跳变①（作用域成员） |
| **mdd_e03** ⭐新增 | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（privileged 孪生边 `prefrontal_limbic` feedback, level_diff=−4） | 解耦沉默 | 0/−0.1/−0.3 | 0 | RDoC 正性效价（奖赏评估/预期）：OFC→腹侧纹状体；MDD 奖赏评估减弱（文献数据源 §四.1） | 3.1 节 bias_limbic 推导锚（负向） |
| **mdd_e04** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.3 | 0 | 旧 link_344（黑质→壳核 DA，Paxinos 2004 fc=0.85）；精神运动迟滞（DSM-5 精神运动性激越/迟滞） | 非线性跳变①（作用域成员，物理攻击 −20% 运动端） |

### 2.2 反刍域（3 条）——「DMN 核心过度耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **mdd_e05** ⭐核心 | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=+2 | **过度耦合** | +0.1/+0.3/+0.4 | 0 | 旧 link_131_L（PCC→mPFC，ENIGMA 9.76）**语义转移**（PCC→mPFC 无直连 → DMN 核心过度耦合）；Hamilton 2015 DMN over-connectivity；Guo 2026 MDD ALFF↑ ACC/mPFC 共享模式 | 行为覆盖② + 非线性跳变②（反刍占用） |
| **mdd_e06** ⭐新增 | precuneus | medialorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2083 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | link_131_L 语义的第二腿（DMN→MPFC 自我参照）；Hamilton 2015（DMN 过度连接→反刍）；Guo 2026 顶下小叶 ALFF↑（IPL 属 DMN，并入反刍边群） | 行为覆盖② + 非线性跳变②（作用域成员） |
| **mdd_e07** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默（旧「边界崩溃」） | −0.1/−0.2/−0.3 | 0 | 旧 link_082_L（mOFC→dlPFC，ENIGMA 7.79）；Ma 2019 DMN-FPN 反相关减弱 trait marker | 非线性跳变③（SN 切换延迟） |

### 2.3 认知控制域（2 条）——「dlPFC 自上而下控制↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **mdd_e08** | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | 旧 link_008_L（ACC→dlPFC，ENIGMA 5.23 情绪调节网络）**语义转移**（ACC→dlPFC 无直连 → dlPFC 认知门控解耦）；文献数据源 §七 MDD 认知控制域 dlPFC↓ | 3.1 节 bias_cognitive 推导锚（反刍门控） |
| **mdd_e09** ⭐新增 | Pallidum | Thalamus-Proper | cstc | ✅ 命中：somatic 环路 `disinhibition`, pallidal_output→thalamic_relay（cognitive/limbic 孪生行存在） | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 文献数据源 §七 MDD 行动门控域（苍白球↓）；ENIGMA MDD 苍白球↓（右,自杀史亚组） | 行为覆盖①（物理攻击 −20% 的结构基础）；3.1 节 bias_somatic 推导锚 |

### 2.4 内感受/唤醒域（4 条）——「NE→岛叶/ACC 耦合 + 岛叶 ALFF↑」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **mdd_e10** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | **过度耦合** | +0.1/+0.2/+0.3 | 0 | 旧 link_155_L（rACC→insula，ENIGMA 6.29 共情网络）；Guo 2026 岛叶/ACC ALFF↑ | 行为覆盖②（内感受耦合） |
| **mdd_e11** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_326（蓝斑→前脑岛 NE，Hansen PINK 最强 hub fc=0.85）；Guo 2026 共享岛叶 ALFF↑ | 3.1 节 NE tone 推导锚（内感受超敏） |
| **mdd_e12** | LocusCoeruleus | caudalanteriorcingulate | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_327（蓝斑→ACC NE，Hansen 2024 Fig5 fc=0.85）；Guo 2026 ACC/mPFC ALFF↑ | 3.1 节 NE tone 推导锚（作用域成员） |
| **mdd_e13** ⭐新增 | caudalanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3951 | 过度耦合 | 0/+0.1/+0.2 | 0 | Guo 2026 MDD 特异性 ACC/mPFC + 岛叶 ALFF↑（§2.3）；情绪-内感受耦合（躯体化症状支持） | 行为覆盖②（作用域成员） |

### 2.5 记忆/5HT 域（2 条）——「海马 5-HT 传递 + 记忆提取」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **mdd_e14** | DorsalRapheNucleus | Hippocampus | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | 过度耦合（旧「结构异常」） | 0/+0.1/+0.2 | 0 | 旧 link_319（中缝背核→海马 5-HT，Hansen PINK fc=0.75）；ENIGMA MDD 海马↓（复发型）——5-HT 传递聚焦于记忆回路 | 3.1 节 5HT tone 推导锚；负性记忆提取支持 |
| **mdd_e15** | caudalanteriorcingulate | parahippocampal | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.2939 | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_003_L（ACC→海马旁回，ENIGMA 4.89）；Guo 2026 共享 ACC ALFF↑ | 行为覆盖②（作用域成员，负性记忆提取） |

**图例**：⭐核心/⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 全 0 = MDD 无偏侧证据（de Kovel 2019 ENIGMA null，§6.5 规则 2；旧 `_L` 后缀为旧 ENIGMA 单侧数据点，新模型统一入 0，见 §四）。

---

## 三、MDD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD §三）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。MDD 默认标签 = 「反刍 + 过度抑制」（疾病文件），快感缺失核心（e01）对应 §5.2 快感缺失变体「过度抑制 + 敏化-奖励(负)」——双变体合并见 §3.2。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0**（严重度依赖 ↑，见注） | e11（LC→insula 0/+0.2/+0.3）、e12（LC→ACC 0/+0.1/+0.2） | LC 出边群 2/2 命中且 m 正偏移但**轻档均为 0** → tone 基线不变；内感受超敏随严重度上升（Guo 共享岛叶 ALFF↑），重档时 NE 上漂 +0.1~+0.2（内感受警觉，与 PTSD 方向同但幅度低——MDD 反刍内转抵消外部警觉） |
| 2 | DA_VTA_baseline | **−0.2** | e01（VTA→NAcc −0.1/−0.3/−0.5 解耦）、e02（VTA→mPFC 0/−0.1/−0.3 解耦） | VTA 出边群 2/2 命中且负偏移主导 → DA_VTA↓ = 快感缺失/奖赏预测误差消失（Schultz 1997 通路解耦） |
| 3 | DA_SNc_baseline | **−0.1** | e04（SNc→Putamen 0/−0.1/−0.3 解耦） | SNc 出边群命中且负偏移 → DA_SNc↓ = 运动启动↓（精神运动迟滞） |
| 4 | 5HT_baseline | **+0.2** | e14（DR→Hippocampus 0/+0.1/+0.2 过度耦合） | 中缝核 5-HT 传递聚焦于记忆回路过度 → 全局 5HT 基线↑（过度抑制：Crockett 2009 5HT↑ 行为抑制） |
| 5 | bias_somatic | **−0.15** | e09（Pallidum→Thalamus somatic disinhibition 解耦）、e04（SNc→Putamen） | 躯体 CSTC 环路 gate 关闭偏弱 + 苍白球↓ → 物理行动倾向↓（不动/迟滞） |
| 6 | bias_cognitive | **+0.15** | e08（dlPFC→Caudate cognitive go_direct 解耦） | cognitive 环路边命中（解耦 = 自上而下控制失效）+ 反刍标签 → 认知行动倾向↑（反刍占用：关不掉的内在加工） |
| 7 | bias_limbic | **0**（快感缺失变体 −0.15） | e03（mOFC→NAcc limbic go_direct 解耦） | limbic 环路边命中但为负向（奖赏趋近↓）→ 默认 0；快感缺失变体按 §5.2 敏化-奖励(负) 取 −0.15 |

> **注（NE 严重度依赖）**：tone 为基线值，随严重度档位由边群 m 上漂承载（轻档 m=0 → NE 基线 0；中/重档 LC 边 m>0 → 内感受警觉上浮）。此设计使轻症 MDD 与正常人 NE 基线一致、重档才显化内感受超敏。

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2/§5.2：MDD = 「过度抑制 + 反刍」双标签（默认）+ 快感缺失变体「过度抑制 + 敏化-奖励(负)」（§5.2 双变体；多标签叠加取最大值，clamp 值域）：

| 参数 | 默认标签组合（反刍+过度抑制） | 快感缺失变体（+敏化-奖励负） | 本文边推导结果 | 一致？ |
|------|------------|------------|--------------|:---:|
| NE_baseline | 0（反刍 −0.1 vs 过度抑制 0，取 max → 0） | 0 | 0（轻档） | ✅ |
| DA_VTA_baseline | 0 | **−0.2** | −0.2（e01 主导） | ✅（快感缺失变体；⚠️ 默认标签未覆盖 → 建议疾病文件标签扩展为三标签，见下） |
| DA_SNc_baseline | 0 | 0 | −0.1（e04） | ⚠️ 幅值差 0.1——精神运动迟滞由 e04 承载，建议标签侧补「运动输出↓」校准或接受 0.1 幅值差（待数值校准） |
| 5HT_baseline | +0.2 | +0.2 | +0.2（e14） | ✅ |
| bias_somatic | −0.15 | −0.15 | −0.15（e09） | ✅ |
| bias_cognitive | +0.15 | 0 | +0.15（e08 命中+反刍） | ✅（默认标签） |
| bias_limbic | 0 | −0.15 | 0/−0.15（e03 负向） | ✅（双变体各取） |

**标签扩展建议（§6.6 规则 4「不一致 → 回查标签选择」的产出）**：MDD 疾病文件默认标签建议由「反刍, 过度抑制」扩展为「**反刍, 过度抑制, 敏化-奖励(负)**」三标签（NPC AI §5.2 快感缺失+反刍双变体合并，≤3 标签上限内），使 DA_VTA −0.2 与 bias_limbic −0.15 获得标签支撑——否则快感缺失核心（e01）在 7 参数层无对应。

**结论**：MDD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（2 处 ⚠️ 为幅值/标签扩展校准项，非方向冲突）。MDD NPC 最终参数：DA_VTA=0.2、DA_SNc=0.4、5HT=0.7、bias_somatic=−0.15、bias_cognitive=+0.15（NE=0.3、bias_limbic=0 基线；快感缺失变体 DA_VTA=0.2、bias_limbic=−0.15）。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 解耦沉默 −0.1/−0.3/−0.5 | **mdd_e01**（VentralTegmentalArea→Accumbens-area） | ✅ 保留语义（端点 fid 合并：NucleusAccumbens → 节点 Accumbens-area；类型/量级不变） |
| link_344 | SNc→Putamen | 解耦沉默 0/−0.1/−0.3 | **mdd_e04**（SubstantiaNigraParsCompacta→Putamen） | ✅ 保留语义 |
| link_338 | VTA→SuperiorFrontalMPFC | 解耦沉默 0/−0.1/−0.3 | **mdd_e02**（VentralTegmentalArea→superiorfrontal） | ✅ 保留语义 |
| link_155_L | rACC→Insula | 过度耦合 +0.1/+0.2/+0.3 | **mdd_e10**（rostralanteriorcingulate→insula） | ✅ 保留语义 + **偏侧显式化**（原 _L 后缀废弃 → Δ=0，de Kovel 2019 null） |
| link_326 | LocusCoeruleus→Insula | 过度耦合 0/+0.2/+0.3 | **mdd_e11**（LocusCoeruleus→insula） | ✅ 保留语义 |
| link_131_L | PosteriorCingulate→SuperiorFrontalMPFC | 过度耦合 +0.1/+0.3/+0.4 | **mdd_e05**（posteriorcingulate→precuneus）+ **mdd_e06**（precuneus→medialorbitofrontal） | ⚠️ **废弃直连**（三体图无 PCC→mPFC 边）；语义转移至 DMN 核心边（PCC↔precuneus dmn_core）+ DMN→MPFC 腿（precuneus→mOFC），量级拆分 |
| link_008_L | ACC→RostralMiddleFrontalDLPFC | 解耦沉默 −0.1/−0.2/−0.3 | **mdd_e08**（rostralmiddlefrontal→Caudate） | ⚠️ **废弃直连**（三体图无 ACC→dlPFC 边）；语义转移至 dlPFC 认知 CSTC 门控（自上而下控制失效的机制表达） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 边界崩溃 −0.1/−0.2/−0.3 | **mdd_e07**（medialorbitofrontal→rostralmiddlefrontal） | ✅ 保留语义 + **类型重校准**：旧「边界崩溃」→ 新四类「解耦沉默」（DMN-FPN 界面边 m 负偏移 = 边界维持信号失效，§6.3）；原 _L 废弃 → Δ=0 |
| link_327 | LocusCoeruleus→ACC | 过度耦合 0/+0.1/+0.2 | **mdd_e12**（LocusCoeruleus→caudalanteriorcingulate） | ✅ 保留语义 |
| link_319 | DorsalRapheNucleus→HippocampusCA1 | 结构异常 0/+0.1/+0.2 | **mdd_e14**（DorsalRapheNucleus→Hippocampus） | ✅ 保留量级 + **类型重校准**：旧「结构异常」（新 §6.3 仅限病理新增边/脑干广播腿选择性负偏移）→ 正偏移广播边 = 「过度耦合」（fid 合并：HippocampusCA1 → 节点 Hippocampus） |
| link_003_L | ACC→Parahippocampal | 过度耦合 0/+0.1/+0.2 | **mdd_e15**（caudalanteriorcingulate→parahippocampal） | ✅ 保留语义 + 偏侧显式化（_L 废弃 → Δ=0） |
| （旧表无） | OFC→腹侧纹状体 奖赏评估解耦（RDoC 正性效价） | — | **mdd_e03** | ⭐ 新增——bias_limbic 机制锚 |
| （旧表无） | DMN→MPFC 自我参照腿（Hamilton 2015） | — | **mdd_e06** | ⭐ 新增——反刍第二腿 |
| （旧表无） | 苍白球→丘脑 行动门控↓（文献数据源 §七 MDD） | — | **mdd_e09** | ⭐ 新增——bias_somatic 机制锚 |
| （旧表无） | ACC↔岛叶 情绪-内感受耦合（Guo 2026 MDD 特异性 ALFF↑） | — | **mdd_e13** | ⭐ 新增 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在（link_131_L / link_008_L）→ **语义转移优先**（DMN 核心边 / 认知 CSTC 门控）；「病理新增」从严——0 条（全部命中现有边）。类型重校准 2 处（082_L 边界崩溃→解耦沉默；319 结构异常→过度耦合），符号/量级随 §6.3 规则修正，均不改变旧行为覆盖挂接语义。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| SAN < 40 → 奖赏域 link_336 m 再次 −0.1（叠加） | ✅ 保留 | **mdd_e01** | 同义替换（VTA→NAcc） |
| 自我社会域 m_max > 0.5 → 后扣带内省→每回合 SAN −1（反刍消耗） | ✅ 保留（改挂接） | **反刍域边群**（e05/e06，m_max 取两条最大值） | 「自我社会域」在新格式 = 反刍域病理边集；后扣带锚 = e05 |
| link_336 \|m\| > 0.4 → 趋近·主动 不可用 | ✅ 保留 | **mdd_e01** \|m\| > 0.4 | 同义替换 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 \|m\| > 0.4（link_336, link_344）→ 趋近·主动 不可用；物理攻击 −20% 伤害 | ✅ 保留 | **mdd_e01 / mdd_e04** \|m\| > 0.4，作用域 = 奖赏域边群（e01-e04） | 运动端结构基础 = e09（Pallidum 门控解耦） |
| 自我社会域 m_max > 0.5（link_131_L）→ 每回合 10% 概率跳过行动窗口（反刍占用） | ✅ 保留 | **mdd_e05/e06** m_max > 0.5 | 同义替换（DMN 核心/自我参照腿） |
| 整合域 \|m\| > 0.2（link_082_L）→ SN 在 DMN/FPN 间切换延迟 1 回合 | ✅ 保留 | **mdd_e07** \|m\| > 0.2 | 同义替换（mOFC↔dlPFC 边界边） |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_155_L, link_131_L, link_008_L, link_082_L | **mdd_e01, mdd_e10, mdd_e05, mdd_e08, mdd_e07** |
| 2（关联） | link_344, link_338, link_326, link_327 | **mdd_e04, mdd_e02, mdd_e11, mdd_e12, mdd_e03, mdd_e06, mdd_e09** |
| 1（边缘） | link_319, link_003_L | **mdd_e14, mdd_e15, mdd_e13** |

> 核心 5 条 = 快感缺失核心（e01）+ 内感受核心（e10）+ 反刍核心（e05）+ 认知控制核心（e08）+ 整合边界（e07）；新增边 e03/e06/e09 落关联、e13 落边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（MDD） | m_offset | 15 条，三档全（CGI-S 3-7），\|m\| ≤ 0.6，m ∈ [0,1] 钳制 | §二（pathology_edges.json §6.1） |
| 偏侧偏离量（MDD） | laterality_delta | **全边 0**（de Kovel 2019 null，§6.5 规则 2） | §二 |
| NE 基线偏离（MDD） | ΔNE_baseline | 0（基线 0.3；重档经 LC 边群上漂 +0.1~+0.2） | §三 |
| DA_VTA 基线偏离（MDD） | ΔDA_VTA_baseline | −0.2（基线 0.4 → 0.2；快感缺失核心） | §三 |
| DA_SNc 基线偏离（MDD） | ΔDA_SNc_baseline | −0.1（基线 0.5 → 0.4；精神运动迟滞） | §三 |
| 5HT 基线偏离（MDD） | Δ5HT_baseline | +0.2（基线 0.5 → 0.7；过度抑制） | §三 |
| CSTC 偏置（MDD） | bias_somatic / bias_cognitive / bias_limbic | −0.15 / +0.15 / 0（快感缺失变体 −0.15；值域 [−0.3,+0.3]） | §三 |
| 趋近·主动禁用阈值 | m_th | 0.4（e01，SAN<40 叠加 −0.1） | §五.1 |
| 反刍 SAN 消耗阈值 | m_th | 0.5（e05/e06 m_max，SAN −1/回合） | §五.1 |
| 物理攻击衰减 | — | \|m\| > 0.4 → −20% 伤害（e01/e04） | §五.2 |
| SN 切换延迟阈值 | m_th | 0.2（e07，延迟 1 回合） | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [重度抑郁症](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E9%87%8D%E5%BA%A6%E6%8A%91%E9%83%81%E7%97%87.md), [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [偏侧化架构](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §二/§三/§四/§七, [ENIGMA偏侧化-精神疾病大样本meta-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/ENIGMA%E5%81%8F%E4%BE%A7%E5%8C%96-%E7%B2%BE%E7%A5%9E%E7%96%BE%E7%97%85%E5%A4%A7%E6%A0%B7%E6%9C%ACmeta-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md), [tripartite_model.json](../../../data/connectivity/tripartite_model.json)*
