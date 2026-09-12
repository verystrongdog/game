# 双相障碍 II 型（BD-II）重映射试点

> Grilling #88 重映射第三份试点（照 PTSD 模板字段规范复制，疾病 ID `bipolar-II`，CGI-S 3-6 两档制——**B′ 档位过滤后无重档**）。本文件把旧 `link_336/344/332/131_L/008_L/082_L/155_L` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **14 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」）。核心病理 = **奖赏域轻度双向振荡（轻躁狂↑/抑郁↓，抑郁主导）+ 自我社会域↑（轻躁狂期自我膨胀↔抑郁期反刍共享 mPFC 通路）+ 唤醒域 LC 振荡 + 内感受域异常（相位翻转触发器）**；结构效应量 < BD-I（ENIGMA BD-II 海马 d=−0.134 < BD-I −0.203，丘脑无显著）。**BD-I/BD-II 区分**：I 型三档全 + 躁狂极 ≥ 抑郁极 + 3 bias 全相位翻转（完全翻转型）；II 型两档（无重档）+ 抑郁极 > 躁狂极 + 仅 tone 四参数与 bias_limbic 相位翻转（温和型，bias_somatic/cognitive 维持标签静态）——II 型更贴近 NPC AI §5.2 标签基线，无完全精神病性躁狂。laterality：唯一偏侧证据 = Haznedar 2005 环性心境谱系「左侧前额叶（趋近相关）活动不对称↑（与 BD-II 共享）」→ 落 e06 左偏 Δ=−0.2，其余 0。**输出格式（§六 字段规范）与 PTSD 试点完全一致；「双向振荡」类型与 `m_offset` 相位分列为双相家族扩展，待 #88 定稿。**

## 目录

1. [文献锚点（4 篇核心 + 关键数据点）](#一文献锚点4-篇核心--关键数据点)
2. [50 实体病理边表（14 条，含三体边核验列）](#二50-实体病理边表14-条含三体边核验列)
3. [BD-II → 7 参数映射建议（4 tone + 3 CSTC，相位双套）](#三bd-ii--7-参数映射建议4-tone--3-cstc相位双套)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单（含状态切换机制）](#五行为覆盖非线性跳变保留清单含状态切换机制)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Hibar et al. (2016)** ENIGMA BD（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §3.2） | 结构 meta | **BD-II 效应量 < BD-I**：海马 d=−0.134（vs BD-I −0.203）、侧脑室 d=+0.096、**丘脑无显著** → BD-II 结构边更轻（e11 海马 d 取 BD-II 值；**不设丘脑边**——与 BD-I e12 的区分） |
| 2 | **Guo et al. (2026)** *Transl Psychiatry*（跨诊断 ALFF meta） | 静息态 ALFF meta | BD 特异性偏离共享：**ALFF↑ 双侧 IFG/ACC-mPFC/纹状体/尾状核 + ALFF↓ 楔前叶**（文献数据源 §2.3）→ e04（尾状核）/e10（楔前叶）方向锚，幅值 < BD-I（轻躁狂非精神病性） |
| 3 | **Haznedar et al. (2005)**（环性心境谱系模型；文献数据源 §七 持续性心境障碍） | 结构/功能 | **左侧前额叶（趋近相关）活动不对称↑（与 BD-II 共享）**；感觉运动网络内在活动↑与 cyclothymic temperament 正相关 → e06 左偏 laterality_delta=−0.2（BD-II 唯一偏侧特征，对照 BD-I 全 0） |
| 4 | **奖赏超敏模型 + 反刍**（Robinson & Berridge 1993；Hamilton et al. 2015 抑郁症 DMN 过度连接——NPC AI §4.2「反刍」；Damme 2022 mOFC/NAcc，BSD 谱系共享） | 理论 + 结构 | 轻躁狂极奖赏敏感性↑（e01/e06 正极）；抑郁相反刍 = mPFC 自我参照环路持续耦合（e07 过度耦合双相复用：轻躁狂自我膨胀 ↔ 抑郁反刍） |

**辅助锚（方向/范围补充）**：

- **NPC AI §5.2**（[NPC AI 行为模型.md](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md)）——「抑郁（反刍）= 反刍 + 过度抑制：默认网络 ↑, 运动输出 ↓」→ BD-II 抑郁相配置；§6.3 Boss 阶段切换 = 相位状态机落点。
- **MDD 行为覆盖继承**（旧 BD-II 文件「抑郁相同 MDD」）——趋近不可用、反刍 SAN −1 → §五.1 抑郁相行为规则。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——link_336/344/332/131_L/008_L/082_L/155_L 的方向/量级作为语义继承源，见 §四。
- **左右脑偏侧化-文献数据源.md §八**——除 Haznedar 2005 左前额叶趋近不对称（BD-II 共享）外无稳健偏侧证据 → 其余边 laterality_delta = 0（§6.5 规则 2；#92 原则偏侧仅装饰层）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八「需设计师翻译」）；m 偏移量级沿用旧文件设计校准值（抑郁极直接继承旧 link 值，躁狂极镜像但 **≤ 抑郁极幅值**——抑郁主导），**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（14 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**14 条全部命中三体模型现有边（1049 条），0 条「病理新增」**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（BD-II = `bipolarii`）。**档位过滤（B′）**：BD-II frontmatter `CGI-S范围` = 3-6 → 上限 6 不达重度（无完全精神病性躁狂）→ **无重档，m 偏移只取 轻/中 两档**（对照 BD-I 三档全）。
>
> **双向振荡（[NEW] 双相家族 schema 扩展，待 #88 定稿）**：同一边随心境相位 S ∈ {轻躁狂相, 抑郁相} 在「过度耦合（正极）/解耦沉默（负极）」间切换。表中 `±X/−Y` = **正极（轻躁狂）/负极（抑郁）**（按档位分列），结算时按当前相位取对应极（§五.3 相位状态机）；单一值 = 相位无关。laterality_delta：仅 e06 左偏（Haznedar 2005），其余 0。

### 2.1 奖赏域（5 条）——「轻度双向振荡，抑郁主导」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中)（正极/负极） | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bipolarii_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **双向振荡**（轻躁狂:过度耦合/抑郁:解耦沉默） | +0.1/−0.2, +0.2/−0.3 | 0 | 旧 link_336（VTA→NAcc，Schultz 1997）；NPC AI §5.2 躁狂（VTA→NAcc↑）；奖赏超敏模型；MDD 快感缺失 VTA→NAcc 解耦 | 行为覆盖①（轻躁狂/抑郁姿态）；3.1 DA_VTA 推导锚（主）；轻躁狂锁定作用域 |
| **bipolarii_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | **双向振荡** | 0/−0.1, +0.1/−0.2 | 0 | 旧 link_344（SNc→壳核，Paxinos 2004）；壳核 ALFF↑ Guo 2026（幅值<BD-I） | 行为覆盖①；3.1 DA_SNc 推导锚 |
| **bipolarii_e03** ⭐新增 | VentralTegmentalArea | superiorfrontal | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **双向振荡** | +0.1/−0.1, +0.2/−0.2 | 0 | 奖赏超敏模型（BSD 谱系共享，环性心境条目）；VTA→mPFC 目标驱动（对照 BD-I e03，幅值减半） | 行为覆盖①（目标驱动）；3.1 DA_VTA 推导锚（次） |
| **bipolarii_e06** ⭐新增 | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`，cortical_input→striatal_gate | **双向振荡** | +0.1/−0.2, +0.2/−0.3 | −0.2 | 奖赏超敏模型（Robinson & Berridge 1993）；Damme 2022（mOFC/NAcc）；**Haznedar 2005 左侧前额叶趋近不对称↑（BD-II 共享）** | 行为覆盖①（冲动趋近/快感缺失）；3.1 bias_limbic 推导锚（相位）；BD-II 唯一偏侧边 |
| **bipolarii_e15** ⭐新增 | superiorfrontal | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`，cortical_input→striatal_gate | **双向振荡** | 0/−0.1, +0.1/−0.2 | 0 | 壳核 ALFF↑ Guo 2026；抑郁期精神运动迟滞（运动输出↓，NPC AI §5.2 抑郁(反刍)）；轻躁狂活动轻度增多 | 行为覆盖①（物理攻击姿态）；3.1 bias_somatic 推导锚（抑郁极） |

### 2.2 自我社会域（2 条）——「mPFC 自我参照环路持续耦合 + 楔前叶↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bipolarii_e07** | medialorbitofrontal | superiorfrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4385 | 过度耦合（相位无关，两相复用） | 0/+0.2 | 0 | 旧 link_131_L（PCC→mPFC，ENIGMA 9.76 L，Autobiographical Memory 网络）；Hamilton 2015 反刍 DMN 过度连接 | 行为覆盖②（轻躁狂自我膨胀 ↔ 抑郁反刍 SAN −1）；自我社会域↑ |
| **bipolarii_e10** ⭐新增 | precuneus | medialorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2083 | 解耦沉默 | −0.1/−0.2 | 0 | Guo 2026 BD 特异性 ALFF↓ 楔前叶（幅值<BD-I）；DMN 自我参照外送减弱 | 自我参照处理异常（轻躁狂夸大→内省缺失） |

### 2.3 唤醒/内感受域（3 条）——「LC 振荡 + 5-HT 相位 + 内感受翻转触发器」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中)（正极/负极） | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bipolarii_e05** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 过度耦合（相位无关） | 0/+0.1 | 0 | 旧 link_332（蓝斑→杏仁核 NE，Hansen 2024）；蓝斑振荡（幅值<BD-I：轻躁狂非精神病性） | 3.1 NE 推导锚；轻躁狂相睡眠衰减（§五.1，相位行为） |
| **bipolarii_e13** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合（相位无关） | 0/+0.2 | 0 | 旧 link_155_L（rACC→岛叶，ENIGMA 6.29 L）；内感受域异常（轻躁狂体感增强/抑郁躯体关注） | 行为覆盖③（**相位翻转触发器：内感受域 m_max > 0.2**） |
| **bipolarii_e14** ⭐新增 | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 有孪生边） | **双向振荡**（5-HT 相位调制） | −0.1/+0.1, −0.2/+0.2 | 0 | NPC AI §4.2 敏化-奖励（5HT −0.2）↔ 过度抑制（5HT +0.2）；5HT 行为抑制假说（Soubrié 1986） | 3.1 5HT 推导锚（双向）；轻躁狂相去抑制/抑郁相过度抑制 |

### 2.4 认知控制/记忆域（4 条）——「dlPFC 轻度解耦 + 海马轻度结构」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中)（正极/负极） | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bipolarii_e04** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`，cortical_input→striatal_gate | **双向振荡** | 0/−0.1, +0.1/−0.2 | 0 | Guo 2026 BD 特异性 ALFF↑ 尾状核/ACC-mPFC（幅值<BD-I） | 3.1 bias_cognitive 旁证（BD-II 不翻 cognitive bias，见 §三）；抑郁相思维迟滞（行为层） |
| **bipolarii_e08** | caudalanteriorcingulate | frontalpole | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+3（L2→L5） | 解耦沉默 | 0/−0.1 | 0 | 旧 link_008_L（ACC→dlPFC，ENIGMA 5.23 L）；认知控制域↓轻度（效应量<BD-I） | 行为覆盖③（L5 压制减弱，轻度） |
| **bipolarii_e09** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默（旧「边界崩溃」语义转移） | 0/−0.1 | 0 | 旧 link_082_L（vmPFC→dlPFC，ENIGMA 7.79 L，DMN-FPN）；DMN-FPN 反相关减弱（极轻度，仅重度抑郁期显现，旧思路链） | 整合域边界崩溃（轻度） |
| **bipolarii_e11** ⭐新增 | medialorbitofrontal | Hippocampus | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1） | 解耦沉默（结构证据：ENIGMA 海马↓） | −0.1/−0.2 | 0 | ENIGMA BD-II 海马 d=−0.134（< BD-I −0.203，Hibar 2016） | 记忆整合受损（轻度）；锂盐治疗锚（共享 BD-I） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；`±X/−Y` = 正极（轻躁狂）/负极（抑郁）（按档位分列，结算按 §五.3 相位状态机取极）；单一值 = 相位无关；Δ=−0.2 仅 e06（Haznedar 2005 左前额叶趋近不对称——轻躁狂相趋近活动左偏，该边正极激活时体现；BD-II 唯一偏侧特征），其余 0。**BD-II 无重档（B′：CGI-S 3-6）**，全表 m 两档且 \|m\| ≤ 0.3（< BD-I 上限 0.6）。

---

## 三、BD-II → 7 参数映射建议（4 tone + 3 CSTC，相位双套）

> 规则（照 PTSD §6.6）：tone 从脑干广播边群推导、bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准；正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。
>
> **双向性表达（[NEW]）**：BD-II NPC 持有两套相位参数集 P(M)/P(D)（NPC AI §6.3 Boss 阶段切换落点）。**与 BD-I 的区分**：BD-II 为**温和型（无重档）**——tone 四参数 + bias_limbic 相位翻转；**bias_somatic / bias_cognitive 维持标签静态**（不随相位翻转；轻躁狂相 0 / 抑郁相 −0.15·+0.15 由相位附加标签给出，见 3.2）。± 号含义：轻躁狂相/抑郁相。

### 3.1 从病理边推导（相位双套）

| # | 参数 | 偏离值（轻躁狂相/抑郁相） | 推导边（命中） | 推导链 |
|---|------|------------------------|---------------|--------|
| 1 | DA_VTA_baseline | **+0.2 / −0.3** | e01（VTA→NAcc）、e03（VTA→mPFC） | VTA 出边群 2/2 命中且双向——轻躁狂极 +0.2（奖赏超敏，标签校准值）、抑郁极 −0.3（**抑郁主导**：BD-II 抑郁极幅值 > 正极，快感缺失更常见） |
| 2 | DA_SNc_baseline | **+0.1 / −0.1** | e02（SNc→Putamen） | SNc 出边群命中（壳核广播）→ 运动激活相位翻转，幅值 < BD-I（轻躁狂非精神病性） |
| 3 | 5HT_baseline | **−0.2 / +0.2** | e14（DR→Amygdala 双向） | 中缝核 5-HT 相位调制——轻躁狂极 m 负（去抑制，匹配「敏化-奖励」5HT −0.2）、抑郁极 m 正（过度抑制，5HT +0.2） |
| 4 | NE_baseline | **+0.1 / −0.1** | e05（LC→Amygdala 过度耦合）、标签「反刍」（NE −0.1 内转） | LC 边群正偏移（轻躁狂 +0.1：精力↑/睡眠需求↓）↔ 反刍标签内转（抑郁 −0.1：外部警觉降低）——**BD-II 两相 NE 异号**（对照 BD-I 两相均为正：激越性抑郁），体现 II 型抑郁相以反刍/迟滞为主 |
| 5 | bias_somatic | **0 / −0.15** | e15（SF→Putamen CSTC somatic 负极） | somatic 环路抑郁极负偏移 + 相位附加标签「过度抑制」（−0.15）→ 抑郁相精神运动迟滞；轻躁狂相 0（II 型不翻 somatic bias，幅值不足） |
| 6 | bias_cognitive | **+0.15（两相）** | 标签「反刍」（bias_cognitive +0.15，静态） | e04（ACC→Caudate 双向）幅值过小（≤0.2）不驱动 bias 翻转；**反刍 = 关不掉的内在思维**（Hamilton 2015）维持静态 +0.15——与 BD-I（bias_cognitive 相位翻转 +0.15/−0.15）形成区分 |
| 7 | bias_limbic | **+0.15 / −0.15** | e06（mOFC→NAcc CSTC limbic 双向） | limbic 环路奖赏门控相位翻转（轻躁狂冲动趋近 / 抑郁快感缺失）→ 与「敏化-奖励（+0.15）↔ 敏化-奖励(负)（−0.15）」对应（唯一相位翻转的 bias，核心机制） |

### 3.2 与标签组合交叉验证（敌我同构闭环，相位双套）

NPC AI §5.2：**躁狂 = 敏化-奖励 + 抑制不足**；**抑郁(反刍) = 反刍 + 过度抑制**（默认网络 ↑, 运动输出 ↓）。BD-II 默认标签 = **敏化-奖励 + 反刍**（旧文件 frontmatter）；抑郁相在标签基线上叠加「过度抑制 + 敏化-奖励(负)」为相位附加标签。多标签叠加取最大值，clamp 值域：

| 参数 | 轻躁狂相：标签组合（敏化-奖励+反刍） | 轻躁狂相：本文边推导 | 一致？ | 抑郁相：标签组合（反刍+过度抑制+敏化-奖励负） | 抑郁相：本文边推导 | 一致？ |
|------|--------------------------------|------------------|:---:|--------------------------------------------|------------------|:---:|
| DA_VTA | +0.2（敏化-奖励） | +0.2 | ✅ | −0.2（敏化-奖励负） | −0.3 | ⚙ 直调增强（抑郁主导） |
| DA_SNc | 0 | +0.1 | ⚙ 直调（壳核广播） | 0 | −0.1 | ⚙ 直调 |
| 5HT | −0.2（敏化-奖励） | −0.2 | ✅ | +0.2（过度抑制） | +0.2 | ✅ |
| NE | −0.1（反刍） | +0.1 | ⚙ **相位覆盖**（轻躁狂相反刍内转被精力↑覆盖；睡眠需求↓） | −0.1（反刍） | −0.1 | ✅ |
| bias_somatic | 0 | 0 | ✅ | −0.15（过度抑制） | −0.15 | ✅ |
| bias_cognitive | +0.15（反刍） | +0.15 | ✅ | +0.15（反刍） | +0.15 | ✅ |
| bias_limbic | +0.15（敏化-奖励） | +0.15 | ✅ | −0.15（敏化-奖励负） | −0.15 | ✅ |

**结论**：BD-II 轻躁狂相 5/7 与标签完全一致（DA_VTA/5HT/bias_somatic/bias_cognitive/bias_limbic），1 相位覆盖（NE）+ 1 直调（DA_SNc）；抑郁相 6/7 一致 + 1 直调增强（DA_VTA −0.3 抑郁主导）。**BD-II 比 BD-I 更贴近标签基线**（I 型 3/7 一致 + 4/7 直调）——温和型、无重档、以抑郁为主导的谱系定位。**NPC AI §5.2「躁狂」行 = 轻躁狂相配置、「抑郁(反刍)」行 = 抑郁相配置**——敌我同构闭环成立。

**BD-II NPC 最终参数（两套相位配置）**：

| 相位 | NE | DA_VTA | DA_SNc | 5HT | bias_somatic | bias_cognitive | bias_limbic |
|------|----|--------|--------|-----|--------------|----------------|-------------|
| 轻躁狂相 | 0.4 | 0.6 | 0.6 | 0.3 | 0 | +0.15 | +0.15 |
| 抑郁相 | 0.2 | 0.1 | 0.4 | 0.7 | −0.15 | +0.15 | −0.15 |

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NucleusAccumbens | 过度耦合+解耦沉默 −0.2/−0.3/−0.4 | **bipolarii_e01**（VTA→Accumbens-area） | ✅ 保留语义 + **双向显式化 + 去重档**（B′：CGI-S 3-6 无重档；旧重档 −0.4 废弃；负极继承 −0.2/−0.3，正极镜像 +0.1/+0.2） |
| link_344 | SNc→Putamen | 解耦沉默 0/−0.1/−0.2 | **bipolarii_e02** | ✅ 保留语义 + 双向显式化（正极镜像 0/+0.1） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合 0/+0.1/+0.2 | **bipolarii_e05** | ✅ 保留语义 + 去重档（0/+0.1） |
| link_131_L | PosteriorCingulate→SuperiorFrontalMPFC | 过度耦合 0/+0.2/+0.3 | **bipolarii_e07**（mOFC→superiorfrontal） | ⚠️ **语义转移**：三体图无 PCC→superiorfrontal 直连 → 转至 mPFC 内部自我参照环路（mOFC↔SF）；去重档（0/+0.2）；L 后缀按 §6.5 处置为 Δ=0 |
| link_008_L | ACC(L)→RostralMiddleFrontalDLPFC | 解耦沉默 0/−0.1/−0.2 | **bipolarii_e08**（ACC→frontalpole） | ⚠️ **语义转移**（同 BD-I：三体图无 ACC→dlPFC 直连 → ACC→frontalpole）+ 去重档（0/−0.1） |
| link_082_L | MedialOrbitalPrefrontalDMN→RostralMiddleFrontalDLPFC | 边界崩溃 0/−0.1/−0.1 | **bipolarii_e09**（mOFC→rostralmiddlefrontal） | ✅ 保留语义 + 类型重分类（边界崩溃 → 解耦沉默）+ 去重档（0/−0.1） |
| link_155_L | RostralACC→Insula | 过度耦合 0/+0.2/+0.3 | **bipolarii_e13**（rACC→insula） | ✅ 保留语义 + 去重档（0/+0.2） |
| （旧表无） | 尾状核 ALFF↑ / CSTC cognitive（Guo 2026，幅值<BD-I） | — | **bipolarii_e04** | ⭐ 新增 |
| （旧表无） | VTA→mPFC 目标驱动（奖赏超敏，BSD 谱系共享） | — | **bipolarii_e03** | ⭐ 新增（对照 BD-I e03 幅值减半） |
| （旧表无） | 奖赏门控双向（mOFC→NAcc CSTC limbic；**Haznedar 2005 左前额叶趋近不对称**） | — | **bipolarii_e06** | ⭐ 新增——bias_limbic 相位锚 + BD-II 唯一偏侧边（Δ=−0.2） |
| （旧表无） | 精神运动双向（抑郁迟滞主导） | — | **bipolarii_e15** | ⭐ 新增——bias_somatic 抑郁极锚 |
| （旧表无） | 中缝核 5-HT 相位调制 | — | **bipolarii_e14** | ⭐ 新增——5HT 双向 tone 锚 |
| （旧表无） | 楔前叶 ALFF↓（Guo 2026，幅值<BD-I） | — | **bipolarii_e10** | ⭐ 新增 |
| （旧表无） | 海马体积↓（ENIGMA BD-II d=−0.134） | — | **bipolarii_e11** | ⭐ 新增——结构层（无丘脑边：BD-II 丘脑无显著，对照 BD-I e12） |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_131_L → e07、link_008_L → e08）；旧类型与 §6.3 机械判定不符 → 重分类（link_082_L → 解耦沉默）；**B′ 档位过滤统一去重档**；「病理新增」从严（本次 0 条）。

---

## 五、行为覆盖/非线性跳变保留清单（含状态切换机制）

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 净方向 > 0（轻躁狂相）：物理攻击 +10%，睡眠恢复 SAN −30% | ✅ 保留 | **奖赏域双向边群正极**（e01/e02/e03/e06/e15，取正极 m） | 幅值 < BD-I（+10% vs +20%）：轻躁狂非精神病性 |
| 奖赏域 净方向 < 0（抑郁相）：同 MDD 行为覆盖（趋近不可用, 反刍 SAN −1） | ✅ 保留 | **奖赏域双向边群负极**（同上，取负极 m）+ **bipolarii_e07**（mPFC 反刍通路） | 反刍 SAN −1 挂 e07（mPFC 自我参照持续耦合 → 关不掉的内在思维） |
| 内感受域 m_max > 0.2：ACC 冲突监测↑——每 5 回合检查一次心境相位翻转 | ✅ 保留 | **bipolarii_e13**（rACC→insula）m_max > 0.2 | 相位翻转触发器（见 §五.3 相位状态机）；BD-II 翻转频率 < BD-I（5 回合 vs 3 回合） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 m > 0.4（link_336）：轻躁狂锁定——奖赏域强制 ↑，不可被 L5 压制。持续 2-4 回合后自动翻转为 ↓ | ✅ 保留 | **bipolarii_e01** m > 0.4 | **BD-II 特有硬约束**（BD-I 无锁定——振荡自由）：轻躁狂锁定 2-4 回合后强制翻转（BD-II 无完全精神病性躁狂，锁定期上限防升级为 I 型） |
| （BD-I 共享）奖赏域 \|m\| > 0.5 → SAN −2/回合 | ❌ 不保留 | — | BD-II 全表 \|m\| ≤ 0.3（无重档），阈值 0.5 不可达——振荡代价跳变对 BD-II 永不触发（区分设计：I 型振荡剧烈损耗 SAN，II 型温和） |
| （BD-I 共享）唤醒域 m_max > 0.4 → 睡眠恢复 SAN −50% | ❌ 不保留 | — | 旧 BD-II 文件**无此阈值跳变**（睡眠恢复 SAN −30% 为轻躁狂相**相位行为**，见 §5.1 行为覆盖①，非阈值触发）；且 BD-II 全表 \|m\| ≤ 0.3（无重档）使 m_max > 0.4 不可达——与「振荡代价」跳变同理不引入（区分设计：I 型阈值跳变 / II 型相位行为） |

### 5.3 相位状态机（状态切换机制——[NEW] 双相家族核心机制落点）

> 同 BD-I §五.3 机制（对照 bipolar-I-pilot）；以下列出 **BD-II 特有参数**：

| 要素 | 定义 | 来源 |
|------|------|------|
| 相位状态 | S ∈ {M（轻躁狂相）, D（抑郁相）} | BD-II frontmatter「轻躁狂不达精神病水平」 |
| 双向边取极规则 | 双向振荡边 e ∈ E_osc：m(e) = m_mania(e)（S=M）或 m_depression(e)（S=D） | §二 双向振荡定义 |
| 相位参数集 | 7 参数按 §三 相位表切换 P(M)/P(D)（NPC AI §6.3 Boss 阶段切换落点） | NPC AI §6.3 |
| 翻转触发器 | 内感受域 m_max > 0.2 → 每 5 回合检查一次相位翻转（ACC 冲突监测↑） | 旧行为覆盖（BD-II） |
| **轻躁狂锁定** | 奖赏域 m > 0.4 → 轻躁狂锁定（奖赏域强制取正极，不可被 L5 压制），持续 2-4 回合后**自动翻转为抑郁相** | 旧非线性跳变（BD-II） |
| 初始相位 | 剧本/遭遇指定，默认 D（BD-II 抑郁主导）[NEW 初值可调] | 设计校准 |

> **BD-I vs BD-II 相位状态机区分**：① 翻转触发器不同（BD-I 唤醒域 3 回合 20% / BD-II 内感受域 5 回合检查）；② BD-II 有「轻躁狂锁定」硬约束且锁定期强制回落（防升级为 I 型躁狂），BD-I 无锁定、振荡自由；③ BD-II 无「振荡代价」（|m|>0.5 不可达），BD-I 有（SAN −2/回合）。

### 5.4 组件掉落池（旧「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_155_L, link_131_L | **bipolarii_e01, bipolarii_e06, bipolarii_e07, bipolarii_e13** |
| 2（关联） | link_344, link_332, link_008_L, link_082_L | **bipolarii_e02, bipolarii_e03, bipolarii_e04, bipolarii_e05, bipolarii_e08, bipolarii_e09, bipolarii_e14, bipolarii_e15** |
| 1（边缘） | （旧无） | **bipolarii_e10, bipolarii_e11** |

> 核心 4 条 = 奖赏双向核心（e01）+ 奖赏门控（e06）+ 自我参照/反刍（e07）+ 内感受翻转触发器（e13）；新增边中 e10/e11 落边缘（自我参照/结构层）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移（双向振荡） | m_offset | 正极/负极分列，\|m\| ≤ 0.3（本表），**两档制**（CGI-S 3-6，B′ 无重档） | 病理边表 §二 |
| 偏侧偏离量 | laterality_delta | 仅 e06 = −0.2（Haznedar 2005 左前额叶趋近不对称），其余 0 | 病理边表 §二 |
| 相位状态 | S | S ∈ {M, D}；默认 D [NEW 初值可调] | §五.3 |
| 轻躁狂锁定阈值 | m_th | 0.4（e01，强制正极 2-4 回合后自动翻转） | §五.2/§五.3 |
| 相位翻转检查 | — | 内感受域 m_max > 0.2 → 每 5 回合检查一次 | §五.1/§五.3 |
| 轻躁狂相睡眠衰减 | — | 睡眠恢复 SAN −30%（轻躁狂相相位行为，非阈值跳变） | §五.1 |
| NE 基线偏离（轻躁狂/抑郁相） | ΔNE_baseline | +0.1 / −0.1（基线 0.3 → 0.4 / 0.2） | §三.1 |
| DA_VTA 基线偏离 | ΔDA_VTA | +0.2 / −0.3（基线 0.4 → 0.6 / 0.1） | §三.1 |
| DA_SNc 基线偏离 | ΔDA_SNc | +0.1 / −0.1（基线 0.5 → 0.6 / 0.4） | §三.1 |
| 5HT 基线偏离 | Δ5HT_baseline | −0.2 / +0.2（基线 0.5 → 0.3 / 0.7） | §三.1 |
| CSTC 偏置 | bias_somatic / bias_cognitive / bias_limbic | 0/−0.15 · +0.15 静态 · +0.15/−0.15（值域 [−0.3,+0.3]） | §三.1 |
| 反刍 SAN 损耗 | — | −1/回合（e07 mPFC 反刍通路） | §五.1 |
| 标签派生阈值 | t | 0.5 [NEW 初值可调] | 偏侧化架构 §六.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [bipolar-I-pilot.md](../disease-pilots/bipolar-I-pilot.md), [双相障碍II型](../../../entities/diseases/%E5%8F%8C%E7%9B%B8%E9%9A%9C%E7%A2%8DII%E5%9E%8B.md), [双相障碍I型](../../../entities/diseases/%E5%8F%8C%E7%9B%B8%E9%9A%9C%E7%A2%8DI%E5%9E%8B.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2/§6.3, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §十八, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §2.3/§3.2/§七, [角色与面具](../../../entities/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
