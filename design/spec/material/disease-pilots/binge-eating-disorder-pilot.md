# 暴食障碍（BED）重映射试点

> 26 病重映射第 5 份试点（照 [PTSD 试点](ptsd-pilot.md) §六 字段规范复制）。**BED 为新增病（Q0.2 P2 扩种，无旧疾病文件/旧链路）**——本文件纯文献驱动，全部 11 条病理边为 ⭐新增（均命中 `tripartite_model.json` 现有边，0 条"病理新增"，从严规则：新增病优先语义转移，禁凭空加边）。核心病理 = **奖赏超敏**（VTA→NAcc / mOFC→NAcc 过度耦合）+ **冲动控制↓**（认知 CSTC 环路 dlPFC→Caudate 解耦）+ **暴食发作回路**（insula→NAcc 触发 + Amygdala→NAcc 情绪性暴食 + Putamen 习惯化）。**BED ≈ BN 无清除行为**：共享奖赏超敏+冲动控制↓ 核心，但无清除期（§三.5 与 BN 对照）。7 参数推导与 NPC AI §4.2/§5.2 标签组合「敏化-奖励 + 抑制不足」交叉验证：DA_VTA/5HT/bias_somatic/bias_limbic 一致，DA_SNc +0.1 与 bias_cognitive −0.15 为**标签缺口裁决**（[NEW]）。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（新格式试点行，含三体边核验列）](#二50-实体病理边表新格式试点行含三体边核验列)
3. [BED → 7 参数映射建议（4 tone + 3 CSTC）](#三bed--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表](#四旧链路对照表)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Schag et al. (2013)** *Obes Rev* 14(6):477-495（PMID [23331770](https://pubmed.ncbi.nlm.nih.gov/23331770/)） | 系统综述 | BED = **食物相关冲动性**：奖赏超敏（奖赏线索→纹状体过度反应）+ 冲动控制↓ → e01/e02 奖赏超敏 + e03/e04 认知↓ 方向锚 |
| 2 | **Kessler et al. (2016)** *Neurosci Biobehav Rev* 63:223-238（PMID [26850211](https://pubmed.ncbi.nlm.nih.gov/26850211/)） | 综述 | BED 神经生物学基础：**纹状体奖赏**、**前额叶控制**、**岛叶内感受**、**背侧纹状体习惯** + 情绪失调 → 暴食发作回路（e05/e06/e07/e08/e09）的结构锚 |
| 3 | **Balodis et al. (2013)** *Int J Eat Disord* | 纵向 fMRI | 奖赏处理中 **fronto-striatal 招募↓** → 持续暴食（治疗抵抗预测）→ e03（dlPFC→Caudate 解耦）的额-纹状体失衡锚 |
| 4 | **Schulte et al. (2016)** 成瘾共享机制 | 综述 | BED 与成瘾障碍共享**奖赏超敏 + 冲动控制↓ + 习惯化**机制（"food addiction" 框架）→ 与 [SUD 试点](substance-use-disorder-pilot.md) 敌我同构对照（同核心边群 VTA→NAcc / dlPFC→Caudate / Putamen 习惯） |

**辅助锚（方向/范围补充）**：

- **暴食-清除循环差异**——BED 无清除行为（DSM-5 排除标准）：暴食期后无呕吐/过度运动 → 无 BN 的清除期 SAN −3 惩罚与清除习惯锁定（§三.5/§五.2）。
- **NPC AI §4.2**——标签「敏化-奖励」（DA_VTA +0.2, 5HT −0.2, bias_limbic +0.15）与「抑制不足」（5HT −0.2, bias_somatic +0.15）——与 [BN 试点](bulimia-nervosa-pilot.md) 同组合。
- **三体模型**——BED 全部边复用现有 1049 边集合（0 病理新增）：本文件为"新增病从严"示范（无旧链路可继承，逐边文献核验）。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八）；m 偏移量级为 **`[NEW]` 设计校准**（参照 PTSD e13 / SUD e05 同类 limbic GO 边幅值 0.1~0.4；无旧文件可沿用，全部数值标记 `[NEW]`）。laterality_delta 全部 0（Schag/Kessler/Balodis 均未报告稳健偏侧效应，§6.5 规则 2）。

---

## 二、50 实体病理边表（新格式试点行，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像）。**11 条全部命中三体模型现有边，0 条"病理新增"**（新增病从严：优先语义转移，禁凭空加边）。本表全部 ⭐新增（BED 无旧文件）。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（BED = `binge-eating-disorder`，主键前缀 `bed`）。三档 m 偏移 = 轻/中/重（frontmatter `CGI-S范围: 3-7` **建议值 [待 #88 定稿]** → 档位过滤 B′ 三档全）。

### 2.1 奖赏超敏域（3 条）——「纹状体奖赏回路超敏」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bed_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（中脑边缘 DA 通路） | **过度耦合** | +0.1/+0.3/+0.4 | 0 | Schag 2013（食物奖赏线索→纹状体过度反应）；Schulte 2016（与 SUD 共享奖赏回路） | 行为覆盖①（暴食期）+ 3.1 节 DA_VTA 推导锚 |
| **bed_e02** ⭐核心 | medialorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（privileged `prefrontal_limbic` L5→L1 孪生存在） | 过度耦合 | +0.2/+0.3/+0.4 | 0 | Schag 2013（奖赏价值评估超敏：OFC-腹侧纹状体）；Kessler 2016 | 行为覆盖①（食物线索评估）+ 3.1 节 bias_limbic 推导锚 |
| **bed_e08** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | Kessler 2016（背侧纹状体奖赏/习惯） | 3.1 节 DA_SNc 推导锚 |

### 2.2 暴食发作回路域（3 条）——「线索→内感受→趋近 触发链」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bed_e05** ⭐核心 | insula | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=feedback, level_diff=−1, edr=0.4172 存在） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Kessler 2016（岛叶食物线索反应→趋近）；Schulte 2016 | 非线性跳变①（暴食发作不可中断）+ 3.1 节 bias_limbic 推导锚 |
| **bed_e06** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | Kessler 2016（渴求时内感受警觉） | 行为覆盖①（渴求期侧翼） |
| **bed_e09** | Amygdala | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=lateral, edr=0.5893 存在） | 过度耦合 | 0/+0.1/+0.2 | 0 | Kessler 2016（情绪失调：负性情绪→进食趋近）；Schulte 2016（负强化） | 行为覆盖①（情绪性暴食触发） |

### 2.3 冲动控制域（2 条）——「认知控制↓ 抑制失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bed_e03** ⭐核心 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | Balodis 2013（fronto-striatal 招募↓→持续暴食）；Schag 2013（冲动控制↓） | 行为覆盖③（L5 压制完全失效）+ 3.1 节 bias_cognitive 推导锚 |
| **bed_e04** | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=feedback, level_diff=−1, edr=0.5807 存在） | 解耦沉默 | 0/−0.1/−0.2 | 0 | Kessler 2016（ACC 监控↓）；Schag 2013 | 行为覆盖③（作用域成员） |

### 2.4 习惯化/行动域（2 条）——「暴食习惯化（无清除）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bed_e07** | Putamen | Thalamus-Proper | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.603 | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Kessler 2016（背侧纹状体习惯化）；Schulte 2016（成瘾式习惯） | 非线性跳变②（暴食习惯锁定） |
| **bed_e11** | precentral | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Kessler 2016（进食动作执行习惯化）；Schag 2013（冲动→动作执行） | 3.1 节 bias_somatic 推导锚 |

### 2.5 调制域（1 条）——「5HT 广播↓ → 冲动」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bed_e10** | DorsalRapheNucleus | caudalanteriorcingulate | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | Schag 2013（冲动性）；Soubrié 1986（低 5HT=去抑制） | 3.1 节 5HT tone 推导锚 |

**图例**：全部 ⭐新增（BED 无旧文件）；均命中现有三体边，0 条"病理新增"（新增病从严示范）；Δ = 0（无稳健偏侧证据）。

---

## 三、BED → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD 模板 §六.6）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值（边推导） | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.1**（域特异，不取） | e06（LC→insula 过度耦合） | LC 出边群仅命中内感受域（insula）→ 域特异增益不驱动全局 tone（域特异裁决 [NEW]，同 BN §3.3）→ NPC 取标签侧 0 |
| 2 | DA_VTA_baseline | **+0.2** | e01（VTA→NAcc 过度耦合） | VTA 出边群正偏移 → 奖赏回路超敏（Schag 2013）——与「敏化-奖励」同向 |
| 3 | DA_SNc_baseline | **+0.1** | e08（SNc→Putamen 过度耦合） | SNc→壳核 DA↑（背侧纹状体奖赏/习惯，Kessler 2016）→ 标签缺口裁决 [NEW] |
| 4 | 5HT_baseline | **−0.2** | e10（DR→ACC 解耦） | 中缝核 5-HT 广播↓ → 冲动去抑制（Soubrié 1986；Schag 2013 冲动性）——与「抑制不足」同向 |
| 5 | bias_somatic | **+0.15** | e11（precentral→Putamen somatic GO 过度耦合） | 进食动作 gate 无法关闭 → 躯体行动倾向↑（冲动→动作执行） |
| 6 | bias_cognitive | **−0.15** [NEW 标签缺口] | e03（dlPFC→Caudate）、e04（ACC→Caudate）解耦 | 认知 CSTC 环路双负 → 语言/认知行动 salience↓ → 冲动行为主导（Balodis 2013） |
| 7 | bias_limbic | **+0.15** | e02（mOFC→NAcc）、e05（insula→NAcc）、e09（Amygdala→NAcc）过度耦合 | 边缘环路 gate 被食物线索+情绪劫持 → 情绪/本能趋近倾向↑（暴食发作）——与「敏化-奖励」同向 |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「敏化-奖励」+「抑制不足」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0 | +0.1（e06 LC→insula 域特异） | ⚠️ **域特异裁决**：LC 边集中于内感受域 → 不驱动全局 tone [NEW]；NPC 取 0 |
| DA_VTA_baseline | +0.2（敏化-奖励） | +0.2（e01 过度耦合） | ✅ |
| DA_SNc_baseline | 0 | +0.1（e08 过度耦合） | ⚠️ **标签缺口裁决**：采纳边推导 +0.1（背侧纹状体）[NEW] |
| 5HT_baseline | −0.2（双标签） | −0.2（e10 解耦） | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15（e11 过度耦合） | ✅ |
| bias_cognitive | 0 | −0.15（e03/e04 解耦） | ⚠️ **标签缺口裁决**：6 标签无"认知↓"标签 → 采纳边推导 −0.15（[NEW]，补 NPC AI 缺口） |
| bias_limbic | +0.15（敏化-奖励） | +0.15（e02/e05/e09 过度耦合） | ✅ |

**结论**：BED 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合经**域特异裁决 + 标签缺口裁决**自洽。BED NPC 最终参数：**NE=0.3、DA_VTA=0.6、DA_SNc=0.6、5HT=0.3、bias_somatic=+0.15、bias_cognitive=−0.15、bias_limbic=+0.15**。设计语义：BED NPC = 奖赏超敏（DA↑）+ 冲动去抑制（5HT↓）+ 认知压制弱（bias_cognitive−）——"食物线索即失控"的敌我同构闭环。

### 3.3 BED vs BN 对照（无清除行为差异）

| 维度 | BED | BN | 差异表达 |
|------|-----|----|---------|
| NPC 7 参数 | 与 BN **完全相同**（同一标签组合 + 同一奖赏/冲动核心） | 同左 | 无差异（敌我同构共享模板） |
| 奖赏边群 | 同（VTA→NAcc / SNc→Putamen 过度耦合） | 同 | 量级相近 |
| 习惯化 | 暴食进食习惯化（e07/e11 +0.1/+0.2/+0.3） | 清除习惯化（bn_e03 +0.1/+0.3/+0.4 更强） | BN 清除习惯 m 更重（呕吐/过度运动自动化） |
| 循环结构 | 渴求→暴食→内疚（**无清除期**） | 暴食→清除→内疚 | BED 无清除期 SAN −3 惩罚、无清除习惯锁定跳变（§五.2） |
| 认知控制 | 同（dlPFC→Caudate 解耦） | 同 | — |

> 设计结论：BED 与 BN 共享 NPC 参数模板（任务要求"BED = 类似 BN 但无清除行为"），**行为差异全部由行为覆盖/非线性跳变承载**（BED 暴食期更长、无清除泄压 → 内疚期更重）。7 参数层不区分两病——区分在循环结构层 [NEW 设计决策]。

---

## 四、旧链路对照表

> **本文件省略该节**：BED 为 Q0.2 P2 新增病（grilling-88.md Q0.2），无旧疾病文件、无旧链路配置（link_registry.json 无 BED 条目），无从对照。全部病理边为 ⭐新增且 0 条"病理新增"（新增病从严：逐边文献核验 + 语义转移优先），对照任务见 §二 表格。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（新增病，全为 [NEW] 设计）

| 条目 | 新挂接 | 说明 |
|------|--------|------|
| 暴食期：奖赏边群 净方向 > 0 → 趋近·主动 食物/奖赏目标 锁定 | **bed_e01/bed_e02** 净方向 > 0 | 暴食期 = 奖赏超敏边群激活（Schag 2013）；**无 BN 的物理攻击 −50% 限制**（BED 无清除动作干扰） |
| 内疚期：奖赏边群 净方向 < 0 → SAN −2/回合（无清除惩罚） | **bed_e01** 净方向 < 0 | 区别于 BN 的 SAN −3/回合（无清除泄压 → 内疚更持久但单回合惩罚更轻） |
| 冲动压制失效：认知控制域 \|m\| > 0.4 → L5 控制·主动 对 L1 冲动压制完全失效 | **bed_e03/bed_e04** \|m\| > 0.4 | 冲动控制↓（Balodis 2013） |
| 渴求期：食物线索出现 → e06/e02 激活（线索→内感受→评估） | **bed_e06/bed_e02** | 暴食发作回路触发前奏 |

### 5.2 非线性跳变（新增病，全为 [NEW] 设计）

| m阈值 | 作用域 | 效果 |
|------|---------|------|
| **bed_e05** m > 0.3 | bed_e05 + bed_e09 | **暴食发作不可中断**——insula→NAcc 触发链一旦启动，L5 压制完全失效（与 e03 解耦协同）——"失控进食"的机制表达 |
| **bed_e07** m > 0.4 | bed_e07 + bed_e11 | 暴食习惯锁定——进食动作自动化（成瘾式习惯，Schulte 2016） |
| **bed_e01** m > 0.4 | 奖赏边群 | 暴食期滞回（Borsboom 2017）——奖赏边群 m 累积超阈值后无法自我终止，必须经内疚期回落（无清除泄压 → 回落更慢） |

### 5.3 组件掉落池（新增病 → 新边权重）

| 权重 | 新病理边 |
|:---:|---------|
| 2（核心） | **bed_e01, bed_e02, bed_e03, bed_e05** |
| 2（关联） | **bed_e04, bed_e07, bed_e08, bed_e09** |
| 1（边缘） | **bed_e06, bed_e10, bed_e11** |

> 核心 4 条 = 奖赏超敏核心（e01）+ 线索评估核心（e02）+ 冲动控制↓核心（e03）+ 暴食发作核心（e05）；e06/e10/e11 落边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6（BED max=0.4），全部 [NEW] 校准 | §二 |
| 偏侧偏离量 | laterality_delta | 0（无稳健偏侧证据） | §二 |
| NE 基线偏离（BED） | ΔNE_baseline | 0（域特异裁决；基线 0.3） | §三 |
| DA_VTA 基线偏离（BED） | ΔDA_VTA_baseline | +0.2（基线 0.4 → 0.6） | §三 |
| DA_SNc 基线偏离（BED） | ΔDA_SNc_baseline | +0.1（标签缺口裁决；基线 0.5 → 0.6） | §三 |
| 5HT 基线偏离（BED） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（BED） | bias_somatic / bias_cognitive / bias_limbic | +0.15 / −0.15 [NEW] / +0.15 | §三 |
| 暴食发作不可中断阈值 | m_th | 0.3（bed_e05） | §五.2 |
| 暴食习惯锁定阈值 | m_th | 0.4（bed_e07） | §五.2 |
| 暴食期滞回阈值 | m_th | 0.4（bed_e01） | §五.2 |
| 认知压制失效阈值 | m_th | 0.4（bed_e03/bed_e04，\|m\|） | §五.1 |
| 内疚期 SAN 惩罚 | ΔSAN | −2/回合（无清除，区别于 BN −3） | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md)（Q0.2 P2 扩种）, [PTSD 重映射试点](ptsd-pilot.md), [神经性贪食症试点](bulimia-nervosa-pilot.md)（无清除对照）, [物质使用障碍试点](substance-use-disorder-pilot.md)（成瘾共享机制对照）, [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [tripartite_model.json](../../../data/connectivity/tripartite_model.json), [角色与面具](../../../%E5%AE%9E%E4%BD%93/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) §8.8*
