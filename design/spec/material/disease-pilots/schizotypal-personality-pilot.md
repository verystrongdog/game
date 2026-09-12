---
父类: 人格障碍（Q0.5 新建父类；P1 必加新病）
疾病ID: schizotypal-personality
CGI-S范围: 3-7
文献: "Howes & Kapur (2009) Nat Rev Neurosci aberrant salience/纹状体 DA 假说 | 分裂型特质纹状体(腹侧)功能异常 | Modinos et al. 精神病易感 ToM 神经关联: mPFC/TPJ 异常募集 | ENIGMA Schizotypy WG (2021): 亚临床 schizotypy mOFC/vmPFC 皮质厚度↑ 与精分模式正相关 r=.285 | SZ 谱系共享但亚临床"
创建: 2026-08-21
---

# 分裂型人格障碍 重映射试点

> 26 病重映射第二批（Grilling #88 Q0.6；**新增病**，Q0.2 P1 必加）。纯文献驱动，无旧文件。本文件把分裂型重映射为三体模型上的 **12 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"）。核心病理 = **认知扭曲**（纹状体多巴胺功能↑→异常突显，Howes & Kapur 2009）+ **社交疏离**（社会认知节点群异常——STS/TPJ/dmPFC 心智化网络）+ **古怪信念/知觉扭曲**（过度关联 + 源监控失败）。与精神分裂症共享 SZ 谱系模式但为**亚临床幅值**（正边上限 +0.3 / 负边上限 −0.3）。7 参数推导（DA_VTA +0.2 / bias_cognitive −0.15 / bias_limbic +0.15）与标签组合「社交钝化 + **[NEW]异常突显**」完全一致。输出格式照 [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §六 字段规范。

## 目录

1. [文献锚点](#一文献锚点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [分裂型 → 7 参数映射建议（4 tone + 3 CSTC）](#三分裂型--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照（新增病：不适用）](#四旧链路对照新增病不适用)
5. [行为覆盖/非线性跳变保留清单（认知扭曲/古怪信念机制）](#五行为覆盖非线性跳变保留清单认知扭曲古怪信念机制)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Howes & Kapur (2009)** *Nat Rev Neurosci* | 理论+证据综述 | **纹状体多巴胺功能↑ → 异常突显（aberrant salience）**：无关刺激被赋予意义 → 认知扭曲/古怪信念 → spt_e01/e02/e03（VTA 出边群过度耦合，核心） |
| 2 | **分裂型特质纹状体功能研究**（腹侧纹状体功能障碍与症状表达） | 任务态影像 | 分裂型人格特质与早期精神病的**腹侧纹状体功能障碍**共享 → spt_e02（VTA→NAcc）幅值支持 |
| 3 | **Modinos et al.**（精神病易感 ToM 神经关联）+ **Fu & Yao**（临床/遗传风险组社会认知 fMRI meta） | 心智化影像 | 精神分裂谱系风险组 **mPFC/TPJ 异常募集**（心智化网络低激活）→ spt_e06/e09（STS-dmPFC、TPJ 边） |
| 4 | **ENIGMA Schizotypy WG (2021)** *Mol Psychiatry* | 结构影像 | 亚临床 schizotypy **mOFC/vmPFC 皮质厚度↑ 与精分模式正相关（r=.285）**——共享 SZ 谱系模式但亚临床 → 全病幅值上限设计依据（§二 引言） |

**辅助锚（方向/范围补充）**：

- **源监控缺陷**（SZ 谱系共享）——内部/外部归因失败 → 内部思维被误判为外部实体 → spt_e05（ACC→海马 监控-记忆回路解耦，思维造物主题锚）。
- **知觉扭曲/幻觉样体验**（分裂型知觉异常）——丘脑感觉门控 → spt_e12（丘脑→STS 感觉突显过度）。
- **NPC AI §4.2 标签**——「社交钝化」（bias_cognitive −0.15）为社交疏离的标签锚；`[NEW]异常突显` 为本次建议新增标签（§三.2 提案，待 NPC AI §4.2 扩展入库）。
- **世界观层接壤**（[世界观与叙事](../../../events/%E4%B8%96%E7%95%8C%E8%A7%82%E4%B8%8E%E5%8F%99%E4%BA%8B.md) 拜月教/思维造物主题）：NPC AI §5.3 边界——链路决定"容易产生认知扭曲"，具体信念内容（思维造物/神谕解读）在叙事层，本文件只落机制。
- **偏侧说明**：无稳健偏侧证据 → 全部 **Δ = 0**（ENIGMA Schizotypy mOFC 效应为双侧合并报告）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；分裂型无旧文件，全部 m 量级为本次设计校准 `[NEW]`——**亚临床幅值约束：正边上限 +0.3、负边上限 −0.3**（不达临床 SZ 的 ±0.6，体现谱系连续，NPC AI §5.2 p-factor 连续谱）。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**12 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（分裂型 = `schizotypal-personality`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围` 过滤——B′ 定案**；范围 3-7 → 三档全可用）。
>
> **端点名对照速查**：VTA=`VentralTegmentalArea`（L0）｜尾状核=`Caudate`（L1，cognitive/ somatic 环路 striatal_gate）｜腹侧纹状体=`Accumbens-area`（L1）｜杏仁核=`Amygdala`（L1）｜dlPFC=`rostralmiddlefrontal`（L5）｜dACC=`caudalanteriorcingulate`（L2，fid AnteriorCingulateCortexDorsal）｜海马=`Hippocampus`（L1）｜STS=`superiortemporal`（L4，fid SuperiorTemporalSulcus）｜dmPFC=`superiorfrontal`（L5，fid SuperiorFrontalMPFC）｜颞极=`temporalpole`（L2）｜TPJ/角回=`inferiorparietal`（L4，fid InferiorParietalAngular）｜楔前叶=`precuneus`（L4）｜STS 后段=`bankssts`（L4，fid BanksSTS）｜丘脑=`Thalamus-Proper`（L1）。

### 2.1 纹状体多巴胺域（6 条）——「异常突显 → 认知扭曲」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizotypal-personality_e01** ⭐新增 | VentralTegmentalArea | Caudate | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | **过度耦合** | +0.1/+0.2/+0.3 | 0 | Howes & Kapur 2009 纹状体 DA↑→异常突显（核心） | §五.1 行为覆盖① + 3.1 节 DA_VTA 推导锚 |
| **schizotypal-personality_e02** ⭐新增 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 过度耦合 | +0.1/+0.2/+0.3 | 0 | 分裂型腹侧纹状体功能障碍；Howes & Kapur 2009 | 3.1 节 bias_limbic 推导锚 + 行为覆盖① |
| **schizotypal-personality_e03** ⭐新增 | VentralTegmentalArea | Amygdala | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | 过度耦合 | 0/+0.1/+0.2 | 0 | DA 突显→情绪（猜疑/敌意归因的情绪燃料） | 行为覆盖①（猜疑侧翼） |
| **schizotypal-personality_e04** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | SZ 谱系 dlPFC 认知控制↓（亚临床）——逻辑松脱/推理侧认知扭曲 | 行为覆盖①（推理侧） |
| **schizotypal-personality_e05** ⭐新增 | caudalanteriorcingulate | Hippocampus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3543 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | SZ 谱系源监控缺陷（内部/外部归因失败） | §五.2 跳变②（思维造物主题锚） |
| **schizotypal-personality_e12** ⭐新增 | Thalamus-Proper | superiortemporal | privileged_pathway | ✅ 命中：`thalamocortical_relay`, dir=feedforward, level_diff=+3 | 过度耦合 | 0/+0.1/+0.2 | 0 | 知觉扭曲/幻觉样体验（丘脑感觉门控过度——无关感觉侵入意识） | §五.2 跳变③（拜月教异象解读锚） |

### 2.2 社会认知网络域（6 条）——「社交疏离 + 过度关联」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **schizotypal-personality_e06** ⭐新增 | superiortemporal | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.232 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | Modinos 精神病易感 ToM：STS-dmPFC 心智化网络异常（核心） | 行为覆盖②（社交疏离核心） |
| **schizotypal-personality_e07** ⭐新增 | superiortemporal | bankssts | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4911 | 解耦沉默 | 0/−0.1/−0.2 | 0 | STS 社会信号解码↓（社交线索读取不足） | 行为覆盖② |
| **schizotypal-personality_e08** ⭐新增 | temporalpole | superiortemporal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+2 | 解耦沉默 | 0/−0.1/−0.2 | 0 | 社会语义知识接入↓（社交疏离） | 行为覆盖② |
| **schizotypal-personality_e09** ⭐新增 | inferiorparietal | superiortemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.1772 | 解耦沉默 | 0/−0.1/−0.2 | 0 | Modinos/TPJ 心智化↓（换位思考不足） | 行为覆盖② |
| **schizotypal-personality_e10** ⭐新增 | precuneus | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.242 | **过度耦合** | +0.1/+0.2/+0.3 | 0 | 过度关联（magical thinking）——自我-世界边界模糊，无关事件被自我关联 | §五.2 跳变①（古怪信念固化核心） |
| **schizotypal-personality_e11** ⭐新增 | superiortemporal | precuneus | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.2574 | 解耦沉默 | 0/−0.1/−0.2 | 0 | 社会-自我整合不足（社交疏离的自我侧） | 行为覆盖② |

**图例**：⭐新增 = 新增病全部边为文献驱动新增（均命中现有三体边，非"病理新增"）；Δ 全 0 = 无稳健偏侧证据（§6.5.2）。方向注记：纹状体 DA 域正偏移（过度耦合=信号过强）与社会认知域负偏移（解耦沉默=信号发不出）并存——对应分裂型"认知扭曲（阳性样）+ 社交疏离（阴性样）"的双面表现（PANSS 五因子正/阴性因子，文献数据源 §五）。

---

## 三、分裂型 → 7 参数映射建议（4 tone + 3 CSTC）

> 规则照 ptsd-pilot.md §6.6：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0** | 无 LC 边群命中 | 分裂型无系统性唤醒偏移（区别于 PTSD/GAD） |
| 2 | DA_VTA_baseline | **+0.2** | e01/e02/e03（VTA 出边群 3/3 命中且 m 随严重度升高） | 纹状体 DA↑ = 异常突显（Howes & Kapur 2009）→ 认知扭曲（核心） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 分裂型 DA↑ 在 VTA/腹侧纹状体层，非 SNc 运动启动层 |
| 4 | 5HT_baseline | **0** | 无 DR 边群命中 | 分裂型无稳健 5-HT 偏移（区别于 SZ 阴性 5-HT↑、ASPD/BPD 5-HT↓） |
| 5 | bias_somatic | **0** | 无 somatic 环路边群命中 | 分裂型无躯体行动倾向偏移 |
| 6 | bias_cognitive | **−0.15** | 社会认知边群（e06-e09/e11 解耦） | 社交钝化——社交信号 gate 偏置低（社交疏离） |
| 7 | bias_limbic | **+0.15** | e02/e03（VTA→NAcc/Amygdala 突显→情绪） | 异常突显→情绪性突显增强（古怪信念的情感燃料） |

### 3.2 标签组合建议 + 交叉验证（敌我同构闭环）

**新增病标签建议：`社交钝化` + `[NEW]异常突显`**——社交钝化（现有标签，§4.2 #6）覆盖社交疏离；`异常突显` 为本次建议**新增标签**（NPC AI §4.2 扩展提案，待入库）：

| 标签 | 游戏表现 | → tone 效果 | → CSTC 偏置 | 文献依据 |
|------|---------|------------|-------------|---------|
| **异常突显** [NEW 建议] | 把无关刺激赋予意义（认知扭曲/魔法思维/猜疑） | DA_VTA_baseline +0.2 | bias_limbic +0.15 | Howes & Kapur (2009): aberrant salience——DA 对突显线索过度赋义 |

| 参数 | 标签组合结果（社交钝化 + 异常突显） | 本文边推导结果 | 一致？ |
|------|----------------------------------|--------------|:---:|
| NE_baseline | 0 | 0 | ✅ |
| DA_VTA_baseline | +0.2（异常突显） | +0.2 | ✅ |
| DA_SNc_baseline | 0 | 0 | ✅ |
| 5HT_baseline | 0 | 0 | ✅ |
| bias_somatic | 0 | 0 | ✅ |
| bias_cognitive | −0.15（社交钝化） | −0.15 | ✅ |
| bias_limbic | +0.15（异常突显） | +0.15 | ✅ |

**备选（不推荐）**：`社交钝化` + `敏化-奖励`——DA_VTA +0.2 / bias_limbic +0.15 两项命中，但**敏化-奖励附带 5HT −0.2 与边推导 0 冲突**（分裂型无 5-HT 偏移文献支持）→ 建议以新增标签 `异常突显` 替代，保持三方自洽。

**结论**：分裂型病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。分裂型 NPC 最终参数：DA_VTA=0.6、bias_cognitive=−0.15、bias_limbic=+0.15（其余基线）。三病参数对照：ASPD（5HT 0.3 / somatic +0.15 / cognitive −0.15）vs BPD（NE 0.5 / 5HT 0.3 / somatic +0.15 / limbic +0.15）vs 分裂型（DA_VTA 0.6 / cognitive −0.15 / limbic +0.15）——tone 面互不重叠，机制可区分。

---

## 四、旧链路对照（新增病：不适用）

> 分裂型为 **Q0.2 P1 新增病，无旧文件、无旧 link_NNN 对应**——本节按模板缺省。语义继承记录如下（供跨病一致性核验）：

| 语义源 | 继承内容 | 落点 |
|--------|---------|------|
| 疾病目录「精神分裂症」§七 对应功能域（奖赏域 VTA→NAcc / 社会认知域） | 纹状体 DA↑ + 社会脑异常，SZ 谱系共享 | **spt_e01/e02/e03 + e06-e11**——继承谱系模式但**亚临床幅值**（±0.3 上限 vs 临床 SZ ±0.6 意图） |
| ENIGMA Schizotypy WG (2021) | 亚临床 schizotypy 与精分形态学模式正相关（r=.285） | 全病幅值上限的设计依据（谱系连续，非独立模式） |
| NPC AI §4.2 标签「社交钝化」（SZ 阴性同款） | 社会认知 gate 偏置 −0.15 | spt 社交边群解耦的标签锚 |

---

## 五、行为覆盖/非线性跳变保留清单（认知扭曲/古怪信念机制）

> 新增病无旧「行为覆盖」表——本节为分裂型机制（**认知扭曲/古怪信念**）的新设计挂接，格式照 PTSD §五。世界观层接壤：以下机制只决定"容易产生认知扭曲"，具体信念内容（思维造物/神谕解读）由[世界观与叙事](../../../events/%E4%B8%96%E7%95%8C%E8%A7%82%E4%B8%8E%E5%8F%99%E4%BA%8B.md) 拜月教/思维造物主题提供（NPC AI §5.3 边界）。

### 5.1 行为覆盖

| 条目 | 新挂接 | 说明 |
|--------|--------|------|
| 认知扭曲（异常突显注入） | **e01/e02** m 正偏移 | 情境匹配时 20% 概率注入 1 条"异常关联"——把无关线索与当前情境强关联（NPC 对同一情境产生非玩家预期的解释） |
| 社交疏离（信号解码不足） | 社会认知边群 **e06-e09/e11** \|m\| > 0.2 | 社交信号 salience −50%（不理解社交线索——对协调/劝诱/共情技能响应减弱） |

### 5.2 非线性跳变（认知扭曲/古怪信念机制核心）

| m阈值 | 作用域 | 效果 |
|------|---------|------|
| **e10 m > 0.4** | schizotypal-personality_e10 | **古怪信念固化**：过度关联锁定——NPC 对特定线索产生固定解释，该信念相关 SAN 攻击免疫 1 种（信念不可动摇） |
| **e05 \|m\| > 0.3** | schizotypal-personality_e05 | **源监控失败**：内部思维 20% 概率被误判为外部实体——**思维造物产生机制锚**（认知扭曲 → "思维造物"感知，接世界观层） |
| **e12 m > 0.3** | schizotypal-personality_e12 | **知觉扭曲**：每回合 10% 概率把环境噪声解读为"异象"（亚临床幻觉样体验——拜月教主题锚） |

### 5.3 组件掉落池（新增病建议）

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **schizotypal-personality_e01, e05, e10** |
| 2（关联） | **schizotypal-personality_e02, e03, e06, e12** |
| 1（边缘） | **schizotypal-personality_e04, e07, e08, e09, e11** |

> 核心 3 条 = 异常突显核心（e01）+ 思维造物锚（e05）+ 古怪信念核心（e10）；权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.3（亚临床上限），m ∈ [0,1] 钳制 | pathology_edges.json（ptsd-pilot.md §6.1） |
| 偏侧偏离量 | laterality_delta | 全 0（无稳健偏侧证据，§6.5.2） | pathology_edges.json（§6.5） |
| DA_VTA 基线偏离（分裂型） | ΔDA_VTA_baseline | +0.2（基线 0.4 → 0.6） | §三 |
| CSTC 偏置（分裂型） | bias_cognitive / bias_limbic | −0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| 异常关联注入概率 | p_aberrant | 0.2（e01/e02 正偏移时，情境匹配每回合） | §五.1 |
| 社交信号减损 | r_social | 0.5（社会认知边群 \|m\| > 0.2 时） | §五.1 |
| 源监控失败概率 | p_source | 0.2（e05 \|m\| > 0.3 时内部思维误判为外部） | §五.2 |
| 知觉扭曲概率 | p_percept | 0.1（e12 m > 0.3 时环境噪声→异象，每回合） | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [反社会型人格障碍](../disease-pilots/aspd-pilot.md), [边缘型人格障碍](../disease-pilots/borderline-personality-pilot.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4/§5.2/§5.3, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md), [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §五/§七, [世界观与叙事](../../../events/%E4%B8%96%E7%95%8C%E8%A7%82%E4%B8%8E%E5%8F%99%E4%BA%8B.md), [角色与面具](../../../entities/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json)*
