# 拖延症重映射试点

> 26 病重映射第二批试点（模板：[ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §六 字段规范）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **11 条病理边（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」）**。核心病理 = **dmPFC（节点 `superiorfrontal`，fid SuperiorFrontalMPFC）努力折扣信号异常（Le Bouc & Pessiglione 2022）+ dlPFC 灰质体积↓（解耦沉默）+ DMN 过度活跃压倒前额叶控制 + 岛叶努力感知异常**。跨诊断特征（CGI-S 1-3，轻症维度），可与其他疾病 NPC 叠加。档位过滤 B′：CGI-S 1-3 → **仅轻档 + 亚临床（1-2）可达，重档 = 3 仍为轻症量级**（中/重档值为上限参考）。7 参数推导与标签组合交叉验证：旧默认标签「反刍」仅捕获 NE 内转成分，回避型结构（bias 负向）超出 6 标签表达 → **参数直调方案**，建议 NPC AI §5.2 新增行。

## 目录

1. [文献锚点（4 篇核心 + 关键数据点）](#一文献锚点4-篇核心--关键数据点)
2. [50 实体病理边表（11 条，含三体边核验列）](#二50-实体病理边表11-条含三体边核验列)
3. [拖延症 → 7 参数映射建议（4 tone + 3 CSTC）](#三拖延症--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_008_L 等 → 新病理边）](#四旧链路对照表link_008_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Le Bouc & Pessiglione (2022)** *Nat Commun* | 努力决策 fMRI | **dmPFC 努力折扣信号预测拖延**——预期努力成本随时间急剧衰减（「以后做就不费力」认知偏差）；努力折扣 > 奖赏折扣 → e07（dmPFC→NAcc 估值环路过度耦合，节点 `superiorfrontal`） |
| 2 | **Amalia et al. (2024)** 系统综述（23 项研究, n=6,087） | 结构/网络综述 | **dlPFC 灰质体积↓**（→ e04 认知 gate 解耦）；**认知控制网络-DMN 连接 disrupted**（→ e02/e03 连接解耦）；DMN 过度活跃压倒前额叶控制信号（→ e11） |
| 3 | **文献数据源 §七 拖延症 特征**（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md)） | 特征汇总 | 跨诊断——低自控 + 高奖赏敏感性 + 反刍 + 无聊易感；**左侧 dlPFC 刺激→任务完成意愿↑（因果证据，干预性非病理偏侧）**；对应功能域：认知控制域（dlPFC↓ / dmPFC 努力折扣异常）、奖赏域（时间折扣偏误——远期奖赏价值↓）、内感受域（岛叶努力感知异常） |
| 4 | **NPC AI §4.2/§5.2 标签校准**（[NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md)） | 设计校准 | 旧默认标签「反刍」（NE−0.1 内转、bias_cognitive+0.15）；tone ±0.1~±0.2、bias ±0.15 幅值锚（→ §三 7 参数量级） |

**辅助锚（方向/范围补充）**：

- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——6 条旧链路的方向/量级（ENIGMA fc + 脑干强度估计）作为语义继承源，见 §四。
- **CGI-S 上限 3（跨诊断特征维度）**——拖延症本身不达临床严重度；作为特征维度可与 MDD/ADHD/OCD NPC 叠加（文献数据源 §七 拖延症「跨诊断特征」）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译；m 偏移量级沿用旧文件设计校准，**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（11 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像）。**dmPFC 对应节点 = `superiorfrontal`**（fid `SuperiorFrontalMPFC`/`SuperiorFrontal`，L5，social_cognition + motor_execution）。**11 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**。
>
> 边 ID 命名：`pro_e<NN>`。三档 m 偏移 = 轻/中/重；**档位过滤 B′（#88 待定项1 定案）：CGI-S 1-3 → 仅轻档 + 亚临床（1-2）可达，重档 = 3 仍为轻症量级**——中/重档值仅作上限参考（保留旧文件 0/−0.1/−0.1 形态）。
>
> **laterality_delta 全部 = 0**：Le Bouc/Amalia 无病理偏侧报告；左 dlPFC 刺激为干预证据（非病理偏侧，§6.5 规则 2 说明）。

### 2.1 认知控制域（4 条）——「dlPFC↓ + DMN-CCN 连接 disrupted」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **pro_e01** | caudalmiddlefrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3201 | 解耦沉默 | −0.1/−0.2/−0.2 | 0 | 旧 link_021_L（PMd→dlPFC 工作记忆环路解耦） | 行为覆盖①（认知控制域成员） |
| **pro_e02** ⭐新增 | rostralmiddlefrontal | precuneus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1694；**注**：三体图无 ACC→dlPFC 直连，link_008_L 语义转移至 FPN→DMN 抑制腿 | 解耦沉默 | −0.1/−0.2/−0.2 | 0 | 旧 link_008_L（ACC→dlPFC 解耦）语义转移；Amalia 2024 认知控制网络-DMN 连接 disrupted | 行为覆盖①（认知控制域成员） |
| **pro_e03** ⭐新增 | superiorfrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4047 | 解耦沉默 | 0/−0.1/−0.1 | 0 | Amalia 2024 dmPFC↔dlPFC（DMN-CCN）连接 disrupted | 行为覆盖①（认知控制域成员） |
| **pro_e04** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | 0/−0.1/−0.1 | 0 | dlPFC GMV↓（Amalia 2024）→ 认知 gate 启动困难；link_008_L 语义拆分承载 | 3.1 节 bias_cognitive 推导锚 |

### 2.2 奖赏域（3 条）——「时间折扣偏误：远期奖赏价值↓ + dmPFC 努力折扣」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **pro_e05** | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 结构异常 | 0/−0.1/−0.1 | 0 | 旧 link_336（VTA→NAcc DA，脑干强度估计 fc=0.9, Schultz 1997）——远期目标 DA 响应↓（§6.3 结构异常 b 类：广播腿选择性负偏移） | 行为覆盖②（远期目标激活−50% 成员） |
| **pro_e06** ⭐新增 | rostralmiddlefrontal | Accumbens-area | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−4（L5→L1）, edr=0.3593 | 解耦沉默 | 0/−0.1/−0.1 | 0 | dlPFC 对远期奖赏调控不足（延迟折扣率异常，文献数据源 §七 拖延症 奖赏域） | 行为覆盖②（远期目标激活−50% 成员） |
| **pro_e07** ⭐新增 | superiorfrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.1 | 0 | Le Bouc & Pessiglione 2022——dmPFC 努力折扣信号异常 → 奖赏-努力联合估值环路过度耦合（「以后做就不费力」估值偏差） | 3.1 节 bias_limbic 推导锚；行为覆盖②侧翼 |

### 2.3 内感受域（2 条）——「岛叶努力感知异常」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **pro_e08** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | 0/+0.1/+0.1 | 0 | 旧 link_155_L（ACC吻侧→前脑岛，任务相关不适→回避行为↑） | 行为覆盖③（内感受域成员） |
| **pro_e09** ⭐新增 | insula | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.1/+0.1 | 0 | 文献数据源 §七 拖延症「内感受域 岛叶努力感知异常」——岛叶将「开始工作」解读为不适信号 → 驱动回避 | 行为覆盖③（内感受域成员） |

### 2.4 行动门控/整合域（2 条）——「行动启动腿解耦 + DMN 反刍」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **pro_e10** | Putamen | Pallidum | cstc | ✅ 命中：somatic 环路 `go_direct`, striatal_gate→pallidal_output | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_363（壳核↔丘脑解耦）语义转移 → 行动启动腿解耦 = 开始行动难 | 3.1 节 bias_somatic 推导锚 |
| **pro_e11** ⭐新增 | precuneus | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=1, edr=0.242；**注**：图内无 PCC→dmPFC 直连，「PCC→mPFC 反刍」经 precuneus（PCC 邻接 DMN hub）承载 | 过度耦合 | 0/+0.1/+0.1 | 0 | 旧 link_131_L（PCC→mPFC 反刍/自我谴责，ENIGMA fc=9.76）语义转移；Amalia 2024 DMN 过度活跃 | 行为覆盖③（自我谴责循环侧翼） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 全部 0 = 无病理偏侧报告（§6.5 规则 2）。

---

## 三、拖延症 → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（ptsd-pilot §6.6 复制）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **−0.1** | 无 LC 边群命中 → 采纳旧默认标签「反刍」NE−0.1 | 内转——降低外部警觉（任务回避型注意撤出）；**修正项 vs 边推导 0（见 3.2）** |
| 2 | DA_VTA_baseline | **−0.1** | e05（VTA→Accumbens 结构异常 0/−0.1/−0.1） | VTA 出边群负偏移 → 远期奖赏 DA 响应↓（时间折扣偏误） |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 拖延不累及黑质纹状体运动启动 DA 通路（运动启动能力正常，问题在估值/启动意愿） |
| 4 | 5HT_baseline | **0** | 无 DR 边群命中 | 拖延无 5-HT 系统性证据（区别于 OCD/ADHD 的冲动维度） |
| 5 | bias_somatic | **−0.1** | e10（Putamen→Pallidum GO −0/−0.1/−0.1） | somatic 环路边群负偏移 → 躯体行动启动倾向↓（「开始行动」的 gate 开度不足） |
| 6 | bias_cognitive | **−0.1** | e04（dlPFC→Caudate −0/−0.1/−0.1） | cognitive 环路边群负偏移 → 认知/语言行动倾向↓（任务参与困难）；**修正项 vs 反刍标签 +0.15（见 3.2）** |
| 7 | bias_limbic | **+0.1** | e09（insula→Accumbens +0/+0.1/+0.1） | limbic 环路边群正偏移 → 不适驱动回避倾向↑（任务相关身体不适 → 情绪性回避） |

### 3.2 与标签组合交叉验证（敌我同构闭环）

旧文件默认标签「反刍」（NPC AI §4.2：NE−0.1 内转、bias_cognitive+0.15；多标签叠加取最大值）：

| 参数 | 标签组合结果（反刍） | 本文边推导结果 | 一致？ |
|------|--------------------|--------------|:---:|
| NE_baseline | −0.1（反刍 内转） | 0（无 LC 边）→ 采纳 −0.1 | ✅（采纳标签） |
| DA_VTA_baseline | 0 | −0.1（e05） | ⚠️ 边补充 |
| DA_SNc_baseline | 0 | 0 | ✅ |
| 5HT_baseline | 0 | 0 | ✅ |
| bias_somatic | 0 | −0.1（e10） | ⚠️ 边补充 |
| bias_cognitive | +0.15（反刍） | −0.1（e04） | ⚠️ 修正 |
| bias_limbic | 0 | +0.1（e09） | ⚠️ 边补充 |

**修正处置**：
- **bias_cognitive −0.1（vs 标签 +0.15）**：反刍标签的 bias_cognitive 面向抑郁型「内在思维活跃」；拖延型为**回避型**（认知行动倾向↓——任务参与困难），方向相反 → **参数直调取边推导 −0.1** `[NEW]`。
- **DA_VTA −0.1 / bias_somatic −0.1 / bias_limbic +0.1（边补充）**：反刍标签不触达 DA_VTA/bias_somatic/bias_limbic，边推导直接补充（远期奖赏↓、行动启动↓、回避倾向↑）——6 标签表达不了「回避型努力折扣」结构。

**结论**：拖延症病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（1 处方向修正 + 3 处边补充，均有机制依据）。**拖延症属 NPC AI §4.3 第 3 级粒度（参数直调）**，建议 §5.2 新增行。最终参数：**NE=0.2、DA_VTA=0.3、DA_SNc=0.5、5HT=0.5、bias_somatic=−0.1、bias_cognitive=−0.1、bias_limbic=+0.1**。作为跨诊断特征（CGI-S 1-3），可与 MDD/ADHD/OCD NPC 按特征叠加。

---

## 四、旧链路对照表（link_008_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_008_L | ACC→dlPFC | 解耦沉默 −0.1/−0.2/−0.2 | **pro_e02 + pro_e04**（dlPFC→precuneus / dlPFC→Caudate） | ⚠️ **语义拆分**——三体图无 ACC→dlPFC 直连；「dlPFC 控制不足」拆为 FPN→DMN 抑制腿 + 认知 gate 两承载 |
| link_021_L | PMd→dlPFC | 解耦沉默 −0.1/−0.2/−0.2 | **pro_e01** | ✅ 保留语义 |
| link_336 | VTA→NAcc | 结构异常 0/−0.1/−0.1 | **pro_e05** | ✅ 保留语义（结构异常 b 类：广播腿选择性负偏移） |
| link_155_L | ACC吻侧→前脑岛 | 过度耦合 0/+0.1/+0.1 | **pro_e08** | ✅ 保留语义 |
| link_363 | Putamen→Thalamus | 解耦沉默 0/−0.1/−0.1 | **pro_e10**（Putamen→Pallidum GO 腿） | ⚠️ **语义转移**——三体图无 Putamen→Thalamus 直连；「行动启动困难」由 somatic GO 腿解耦承载 |
| link_131_L | PCC→mPFC | 过度耦合 0/+0.1/+0.1 | **pro_e11**（precuneus→superiorfrontal） | ⚠️ **语义转移**——三体图无 PCC→dmPFC 直连；反刍经 precuneus（PCC 邻接 DMN hub）承载 |
| （旧表无） | dmPFC↔dlPFC 连接 disrupted（Amalia 2024） | — | **pro_e03** | ⭐ 新增 |
| （旧表无） | dlPFC→NAcc 远期奖赏调控不足（延迟折扣） | — | **pro_e06** | ⭐ 新增 |
| （旧表无） | dmPFC 努力折扣信号异常（Le Bouc & Pessiglione 2022） | — | **pro_e07** | ⭐ 新增——bias_limbic/估值机制锚 |
| （旧表无） | 岛叶努力感知异常 → limbic gate（文献对应功能域） | — | **pro_e09** | ⭐ 新增 |

**处置规则总结**：端点对存在 → 直接映射；不存在 → **语义转移/拆分优先**（link_008_L → e02+e04；link_363 → e10；link_131_L → e11），「病理新增」0 条（§6.4 从严）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 认知控制域 \|m\| > 0.2 → 每回合 10% 概率延迟 M1 声明到下一行动窗口（「等一下再做」） | ✅ 保留（阈值适配） | **认知控制域边群**（e01/e02/e03/e04）m_max ≥ 0.1 `[NEW 阈值适配 B′]` → 10% 延迟 M1 声明 | B′ 过滤后仅轻档可达（\|m\| ≤ 0.2），阈值降至轻档触发区间 |
| 奖赏域 m < 0 → 远期目标（link_336）激活 −50% | ✅ 保留 | **pro_e05 / pro_e06**（VTA→Accumbens 结构异常 + dlPFC→NAcc 解耦）m < 0 → 远期目标价值 −50% | 「奖赏域」在新格式 = 奖赏域病理边集 |
| 内感受域 m > 0 → 任务相关身体不适（疲劳/紧张）→ 回避行为↑ | ✅ 保留 | **pro_e08 / pro_e09**（rACC→insula + insula→Accumbens）m > 0 → 回避行为↑ | 「内感受域」在新格式 = 内感受域病理边集 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| （旧文件无非线性跳变条目） | — | — | **不新增**（新增从严，ptsd-pilot §6.4 原则）；候选跳变「bias_somatic 与 bias_cognitive 同时 < 0 → 任务完全冻结」留待 [待 #88 数值校准] 评估，本试点不落表 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_008_L, link_021_L | **pro_e01, pro_e02, pro_e04** |
| 2（关联） | link_336, link_155_L, link_131_L, link_363 | **pro_e03, pro_e05, pro_e06, pro_e07, pro_e08, pro_e09, pro_e10, pro_e11** |

> 核心 = dlPFC 控制不足（e01/e02/e04）；新增边全部落关联（跨诊断特征维度——掉落权重低、可叠加）。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6；拖延症仅轻档+亚临床可达（B′，CGI-S 1-3，重档=3 仍为轻症） | pathology_edges.json（schema §6.1） |
| 偏侧偏离量 | laterality_delta | 0（无病理偏侧报告，§6.5 规则 2） | pathology_edges.json |
| NE 基线偏离（拖延症） | ΔNE_baseline | −0.1（基线 0.3 → 0.2，采纳反刍标签） | §三 |
| DA_VTA 基线偏离（拖延症） | ΔDA_VTA_baseline | −0.1（基线 0.4 → 0.3）`[NEW 边补充]` | §三 |
| CSTC 偏置（拖延症） | bias_somatic / bias_cognitive / bias_limbic | −0.1 / −0.1 / +0.1（值域 [−0.3,+0.3]） | §三 |
| 拖延触发阈值 | m_th | 认知控制域 m_max ≥ 0.1 → 10% 延迟 M1 声明 `[NEW 阈值适配 B′]` | §五.1 |
| 远期目标衰减 | — | 奖赏域 m < 0 → 远期目标价值 −50% | §五.1 |
| 回避触发 | — | 内感受域 m > 0 → 回避行为↑ | §五.1 |
| 任务冻结候选阈值 | — | bias_somatic 与 bias_cognitive 同时 < 0（候选，待 #88 校准） | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [拖延症](../../../entities/diseases/%E6%8B%96%E5%BB%B6%E7%97%87.md), [注意缺陷多动障碍](../../../entities/diseases/%E6%B3%A8%E6%84%8F%E7%BC%BA%E9%99%B7%E5%A4%9A%E5%8A%A8%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§4.3/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../../data/connectivity/link_registry.json)（⚠️ 已废弃 2026-08-07）*
