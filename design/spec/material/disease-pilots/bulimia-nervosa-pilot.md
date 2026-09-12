# 神经性贪食症（BN）重映射试点

> 26 病重映射第 4 份试点（照 [PTSD 试点](ptsd-pilot.md) §六 字段规范复制）。本文件把旧 `link_336/344/155_L/326/008_L/363` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **10 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"）。核心病理 = **奖赏↑（暴食期过度耦合）**（VTA→NAcc / SNc→Putamen）+ **认知控制↓（抑制失败）**（认知 CSTC 环路 dlPFC→Caudate 解耦，替代不存在的 ACC→dlPFC 直连）+ **内感受岛叶↑**（LC→insula 过度警觉）+ **清除习惯化**（Putamen→Thalamus + precentral→Putamen）。**BN 与 AN 为相反模式**：BN = 奖赏↑ 认知↓；AN = 奖赏↓ 认知↑（同边异号，§三.4 对照）。7 参数推导与 NPC AI §4.2/§5.2 标签组合「抑制不足 + 敏化-奖励」交叉验证：DA_VTA/5HT/bias_somatic/bias_limbic 一致，DA_SNc +0.1 与 bias_cognitive −0.15 为**标签缺口裁决**（[NEW]）。

## 目录

1. [文献锚点（2-4 篇核心 + 关键数据点）](#一文献锚点2-4-篇核心--关键数据点)
2. [50 实体病理边表（新格式试点行，含三体边核验列）](#二50-实体病理边表新格式试点行含三体边核验列)
3. [BN → 7 参数映射建议（4 tone + 3 CSTC）](#三bn--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_336 等 → 新病理边）](#四旧链路对照表link_336-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（2-4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Bronleigh et al. (2022)** *Psychiatry Res Neuroimaging*（14 fMRI, 470 人） | ALE meta | BN 食物刺激：**奖赏区（豆状核/壳核）↑ + 内感受区（岛叶）↑ + 认知控制区（前额叶+ACC）↓——与 AN 相反模式** → e01/e02/e09 奖赏↑ + e04/e05 内感受 + e06/e07 认知↓ 三域方向锚（本项目 AN/BN 相反模式的文献基础） |
| 2 | **Mattavelli et al. (2024)** *Cortex* | ALE meta | 冲动性：延迟折扣→纹状体+ACC+额上回；食物 No-go→中央前/后回+**背侧纹状体**激活↓——**皮质-纹状体平衡失调** → e07 ACC↓ + e08（precentral→Putamen 抑制失败→GO 通路无法关闭） |
| 3 | **Kaye et al. (2005)** 5-HT 综述 | 神经化学 | BN 5-HT 功能↓（冲动性、暴食-清除循环）→ e10（DR→insula 解耦）+ 5HT −0.2 锚 |
| 4 | **文献数据源 §七 BN** | 项目文献汇总 | 奖赏敏感性↑ + 冲动控制↓——暴食-清除循环；症状严重度与额纹状体低激活相关 → 循环结构（§五） |

**辅助锚（方向/范围补充）**：

- **豆状核→Putamen 映射**——Bronleigh 2022「奖赏区（豆状核）↑」：豆状核（lentiform）= 壳核（`Putamen`）+ 苍白球（`Pallidum`）；BN 奖赏超敏主载体取壳核侧（e01/e02/e09，纹状体 DA 通路），苍白球侧由 AN 的 Datta 2025 组分3 表达（set-shift，见 [AN 试点](anorexia-nervosa-pilot.md) an_e08）。
- **AN 对标方向翻转**（旧 BN 思路链）——同一父类下与 AN 方向相反的表达；AN 的 e01/e05/e06 同边异号对照见 §三.4。
- **NPC AI §4.2**——标签「抑制不足」（5HT −0.2, bias_somatic +0.15）与「敏化-奖励」（DA_VTA +0.2, 5HT −0.2, bias_limbic +0.15）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃）**——6 条旧链路的方向/量级（Schultz1997 / Paxinos2004 / Hansen2024 / Alexander1986_CSTC / ENIGMA）作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八）；m 偏移量级沿用旧文件设计校准，**旧 BN 文件的非单调 m（link_336: 0/+0.3/−0.1；link_344: 0/+0.2/0）修正为严重度单调**（相位入行为覆盖，见 §五）；新增数值标记 `[NEW]`。

---

## 二、50 实体病理边表（新格式试点行，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像）。**10 条全部命中三体模型现有边，0 条"病理新增"**。旧 `link_008_L`（ACC→dlPFC）直连不在三体图 → **语义转移优先**：认知控制↓由认知 CSTC 环路（dlPFC→Caudate）承载，旧 m（0/0/0 结构异常）修正为解耦沉默负偏移（任务要求 BN 认知↓ 显式化）。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（BN = `bulimia-nervosa`，主键前缀 `bn`）。三档 m 偏移（frontmatter `CGI-S范围: 3-7` → 档位过滤 B′ 三档全）。laterality_delta 全部 0：Bronleigh/Mattavelli 均未报告稳健偏侧效应（旧 `_L` 后缀为 ENIGMA 单半球数据点，非偏侧证据——#92 合并双侧，Δ=0）。

### 2.1 奖赏域（3 条）——「奖赏↑ 暴食期过度耦合」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bn_e01** ⭐核心 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast（中脑边缘 DA 通路） | **过度耦合** | +0.1/+0.3/+0.4 | 0 | 旧 link_336（VTA→NAcc，fc=0.9）**量级修正**（旧 0/+0.3/−0.1 非单调，相位入行为覆盖）；Bronleigh 2022 BN 奖赏+ | 行为覆盖①②（暴食期/清除后） |
| **bn_e02** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_344（SNc→壳核，fc=0.85）**量级修正**（旧 0/+0.2/0）；Bronleigh 2022 豆状核奖赏区↑ | 3.1 节 DA_SNc 推导锚 |
| **bn_e09** ⭐新增 | insula | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=feedback, level_diff=−1, edr=0.4172 存在） | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Bronleigh 2022（内感受岛叶↑ + 奖赏↑ 联合）；食物线索→趋近 = 暴食发作触发回路 | 行为覆盖①（暴食发作核心）+ 3.1 节 bias_limbic 推导锚 |

### 2.2 内感受域（2 条）——「岛叶混合：过度警觉 + 饱腹感解耦」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bn_e04** | LocusCoeruleus | insula | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_326（LC→前脑岛 NE，fc=0.85，Hansen2024 PINK 最强 hub）；Bronleigh 2022 内感受区↑ | 行为覆盖①（食物线索内感受警觉） |
| **bn_e05** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.4246 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 旧 link_155_L（ACC吻侧→前脑岛）；饱腹感信号不可靠 + 清除后身体信号被忽略 | 行为覆盖②（清除后内感受忽略） |

### 2.3 认知控制域（2 条）——「dlPFC↓ 抑制失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bn_e06** ⭐转移 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | **解耦沉默** | −0.1/−0.2/−0.3 | 0 | 旧 link_008_L（ACC→dlPFC 结构异常 0/0/0）**语义转移 + 量级修正**（任务要求 BN 认知↓ 显式化）；Bronleigh 2022 前额叶↓ | 行为覆盖③（L5 压制完全失效） |
| **bn_e07** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate（CC 孪生 dir=feedback, level_diff=−1, edr=0.5807 存在） | 解耦沉默 | 0/−0.1/−0.2 | 0 | Mattavelli 2024（食物 No-go ACC 低激活）；Bronleigh 2022 ACC↓ | 行为覆盖③（作用域成员） |

### 2.4 习惯化/行动门控域（2 条）——「清除行为自动化」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bn_e03** | Putamen | Thalamus-Proper | corticocortical | ✅ 命中：CC, dir=lateral, level_diff=0, edr=0.603 | 过度耦合 | +0.1/+0.3/+0.4 | 0 | 旧 link_363（壳核→丘脑，CSTC 直接通路，Alexander1986；Haber2010）；清除行为自动化（呕吐/过度运动） | 非线性跳变①（清除习惯锁定） |
| **bn_e08** ⭐新增 | precentral | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.2/+0.3 | 0 | Mattavelli 2024（食物 No-go 中央前回+背侧纹状体激活↓=抑制机制失效 → GO 通路无法关闭）；清除动作执行 | 3.1 节 bias_somatic 推导锚 + 非线性跳变① |

### 2.5 调制域（1 条）——「5HT 广播↓ → 冲动」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **bn_e10** ⭐新增 | DorsalRapheNucleus | insula | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | Kaye 2005（BN 5-HT 功能↓）；Soubrié 1986（低 5HT=去抑制）→ 暴食冲动 | 3.1 节 5HT tone 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边）；⭐转移 = 旧链路直连不在三体图，按 §六.4 语义转移；Δ = 0（无稳健偏侧证据）。

---

## 三、BN → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（照 PTSD 模板 §六.6）：tone 从脑干广播边群推导，bias 从 CSTC 环路边推导；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15）。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。

### 3.1 从病理边推导

| # | 参数 | 偏离值（边推导） | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.1**（域特异，不取） | e04（LC→insula 过度耦合） | LC 出边群仅命中内感受域（insula）→ 域特异增益不驱动全局 tone（§3.3 域特异裁决 [NEW]）→ NPC 取标签侧 0 |
| 2 | DA_VTA_baseline | **+0.2** | e01（VTA→NAcc 过度耦合） | VTA 出边群正偏移 → 奖赏回路↑（暴食期过度耦合）——与「敏化-奖励」同向 |
| 3 | DA_SNc_baseline | **+0.1** | e02（SNc→Putamen 过度耦合） | SNc→壳核 DA↑（豆状核奖赏区，Bronleigh）→ 标签缺口裁决 [NEW]（「敏化-奖励」未覆盖 DA_SNc） |
| 4 | 5HT_baseline | **−0.2** | e10（DR→insula 解耦） | 中缝核 5-HT 广播↓ → 冲动去抑制（Soubrié 1986；Kaye 2005 BN 5-HT↓）——与「抑制不足」同向 |
| 5 | bias_somatic | **+0.15** | e08（precentral→Putamen somatic GO 过度耦合） | 清除/进食动作 gate 无法关闭（Mattavelli 抑制失败）→ 躯体行动倾向↑ |
| 6 | bias_cognitive | **−0.15** [NEW 标签缺口] | e06（dlPFC→Caudate）、e07（ACC→Caudate）解耦 | 认知 CSTC 环路双负 → 语言/认知行动 salience↓ → 冲动行为主导（Bronleigh 前额叶↓） |
| 7 | bias_limbic | **+0.15** | e09（insula→NAcc limbic GO 过度耦合） | 边缘环路 gate 被食物线索劫持 → 情绪/本能趋近倾向↑（暴食发作）——与「敏化-奖励」同向 |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「抑制不足」+「敏化-奖励」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0 | +0.1（e04 LC→insula 域特异） | ⚠️ **域特异裁决**：LC 边集中于内感受域 → 不驱动全局 tone [NEW]；NPC 取 0 |
| DA_VTA_baseline | +0.2（敏化-奖励） | +0.2（e01 过度耦合） | ✅ |
| DA_SNc_baseline | 0 | +0.1（e02 过度耦合） | ⚠️ **标签缺口裁决**：采纳边推导 +0.1（豆状核奖赏区，Bronleigh）[NEW] |
| 5HT_baseline | −0.2（双标签） | −0.2（e10 解耦） | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15（e08 过度耦合） | ✅ |
| bias_cognitive | 0 | −0.15（e06/e07 解耦） | ⚠️ **标签缺口裁决**：6 标签无"认知↓"标签 → 采纳边推导 −0.15（[NEW]，补 NPC AI 缺口） |
| bias_limbic | +0.15（敏化-奖励） | +0.15（e09 过度耦合） | ✅ |

**结论**：BN 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合经**域特异裁决 + 标签缺口裁决**自洽。BN NPC 最终参数：**NE=0.3、DA_VTA=0.6、DA_SNc=0.6、5HT=0.3、bias_somatic=+0.15、bias_cognitive=−0.15、bias_limbic=+0.15**。设计语义：BN NPC = 奖赏超敏（DA↑）+ 冲动去抑制（5HT↓）+ 认知压制弱（bias_cognitive−）——"看到食物就失控"的敌我同构闭环。

### 3.3 域特异裁决规则（[NEW]，写入 §六.6 供 25 病复制）

> 触发条件：脑干广播边群的 m 偏移集中于单一感觉/内感受域（BN 的 LC→insula；AN 的 LC→insula/pericalcarine），而非跨域发散。
> 裁决：域特异增益不驱动全局 tone 推导；全局 tone 以标签组合为锚（判断标准见 [AN 试点](anorexia-nervosa-pilot.md) §3.3）。

### 3.4 BN vs AN 相反模式对照（任务硬性要求）

| 维度 | BN | AN | 表达边（同边异号） |
|------|----|----|------------------|
| 奖赏域 | ↑（过度耦合） | ↓（解耦沉默） | VTA→Accumbens-area（bn_e01 +0.1/+0.3/+0.4 vs an_e01 −0.1/−0.3/−0.5）；SNc→Putamen/Caudate（bn_e02 + vs an_e09 +——注意 AN 的 + 为策略僵化侧） |
| 认知控制域 | ↓（解耦沉默） | ↑（过度耦合） | rostralmiddlefrontal→Caudate（bn_e06 −0.1/−0.2/−0.3 vs an_e05 +0.2/+0.3/+0.5） |
| 5HT | −0.2（抑制不足） | +0.2（过度抑制） | DR 出边（bn_e10 解耦 vs an_e11 过度耦合） |

> 同一边（dlPFC→Caudate cognitive GO）在 BN 为解耦沉默、在 AN 为过度耦合——三体边复用 + 符号翻转即表达相反病理（Bronleigh 2022 原始结论）。BN 的清除行为 = AN 认知控制↑ 的**失控镜像**。

---

## 四、旧链路对照表（link_336 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_336 | VTA→NAcc | 过度耦合+解耦沉默 0/+0.3/−0.1 | **bn_e01**（VentralTegmentalArea→Accumbens-area） | ⚠️ **量级修正**：旧 m 非单调（0/+0.3/−0.1，相位编码入 m）→ 修正为严重度单调过度耦合 +0.1/+0.3/+0.4（BN 奖赏↑ 主导）；暴食/清除相位入行为覆盖①② |
| link_344 | SNc→Putamen | 过度耦合+解耦沉默 0/+0.2/0 | **bn_e02** | ⚠️ 量级修正（旧 0/+0.2/0 非单调 → 0/+0.2/+0.3） |
| link_363 | Putamen→Thalamus | 过度耦合 +0.1/+0.3/+0.4 | **bn_e03**（Putamen→Thalamus-Proper） | ✅ 保留语义（端点/类型/量级不变） |
| link_155_L | ACC吻侧(L)→前脑岛 | 解耦沉默 −0.1/−0.2/−0.3 | **bn_e05** | ✅ 保留语义 + L 后缀取消（Δ=0） |
| link_326 | LocusCoeruleus→前脑岛 | 过度耦合 0/+0.2/+0.3 | **bn_e04** | ✅ 保留语义 |
| link_008_L | ACC(L)→dlPFC | 结构异常 0/0/0 | **bn_e06**（rostralmiddlefrontal→Caudate） | ⚠️ **语义转移 + 量级修正**：直连不在三体图 → cognitive 环路承载；旧 0/0/0 结构异常（父类反模式抵消设计）修正为解耦沉默 −0.1/−0.2/−0.3（任务要求 BN 认知↓ 显式化；父类抵消改由暴食-清除循环行为覆盖表达） |
| （旧表无） | 食物线索→趋近 暴食发作（Bronleigh 内感受↑+奖赏↑） | — | **bn_e09** | ⭐ 新增——bias_limbic 机制锚 + 暴食发作核心 |
| （旧表无） | ACC↓ 皮质-纹状体失衡（Mattavelli 2024） | — | **bn_e07** | ⭐ 新增——认知环路 ACC 侧解耦 |
| （旧表无） | 清除动作自动化/抑制失败（Mattavelli 中央前回+背侧纹状体） | — | **bn_e08** | ⭐ 新增——bias_somatic 推导锚 |
| （旧表无） | 5HT 广播↓→冲动（Kaye 2005；Soubrié 1986） | — | **bn_e10** | ⭐ 新增——5HT tone 推导锚 |

**处置规则总结**：端点对存在 → 直接映射保留；直连不存在（link_008_L）→ **语义转移优先**；旧非单调 m（相位编码）→ 修正为严重度单调，相位入行为覆盖；「病理新增」从严（本文件 0 条）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 奖赏域 净方向 > 0（暴食期）：趋近·主动 → 食物/奖赏目标 锁定；物理攻击 −50% | ✅ 保留 | **bn_e01/bn_e09** 净方向 > 0（暴食期跳变） | 暴食期 = 奖赏边群过度耦合激活 |
| 奖赏域 净方向 < 0（清除后）：SAN −3/回合 + 忍耐·主动 不可用（内疚/自我厌恶） | ✅ 保留 | **bn_e01** 净方向 < 0（清除后跳变）+ **bn_e05**（内感受忽略） | 清除后 = 奖赏边群翻转 + 内感受解耦 |
| 认知控制域 \|m\| > 0.4 → L5 控制·主动 对 L1 冲动压制完全失效 | ✅ 保留 | **bn_e06/bn_e07** \|m\| > 0.4 | 认知↓ 显式化后（§四 量级修正）此覆盖可直接挂接 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_363 m > 0.4 → 习惯锁定——清除行为自动化（呕吐/过度运动）。该链路激活时 SAN −2/回合 | ✅ 保留 | **bn_e03** m > 0.4，作用域 = e03 + e08 | 清除行为习惯化锁定 |
| （新增）暴食-清除循环 阶段机 [NEW] | ⭐ 新增 | **bn_e01/bn_e09**（暴食期）+ **bn_e03/bn_e08**（清除期）+ **bn_e01 翻转/bn_e05**（内疚期） | 三阶段循环：①暴食期（奖赏边群 +，趋近锁定）→ ②清除期（习惯边群 +，SAN −2/回合）→ ③内疚期（奖赏边群翻转 −，SAN −3/回合 + 忍耐不可用）→ 回到 ①。阶段切换由 奖赏域净方向 过零触发（Borsboom 滞回：暴食期 m 累积 > 阈值后无法自我终止，必须经清除期泄压） |
| （新增）暴食发作不可中断 [NEW] | ⭐ 新增 | **bn_e09** m > 0.3 | 暴食发作一旦启动（insula→NAcc 触发）不可被 L5 压制（与 e06 解耦协同）——"失控进食"的机制表达 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_336, link_008_L, link_155_L, link_363 | **bn_e01, bn_e06, bn_e05, bn_e03** |
| 2（关联） | link_344, link_326 | **bn_e02, bn_e04, bn_e07, bn_e09** |
| 1（边缘） | — | **bn_e08, bn_e10** |

> 核心 4 条 = 奖赏↑核心（e01）+ 认知↓核心（e06）+ 内感受核心（e05）+ 清除习惯核心（e03）；新增边 e07/e09 落关联权重，e08/e10 落边缘权重。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6（BN max=0.4） | §二 |
| 偏侧偏离量 | laterality_delta | 0（无稳健偏侧证据） | §二 |
| NE 基线偏离（BN） | ΔNE_baseline | 0（域特异裁决；基线 0.3） | §三 |
| DA_VTA 基线偏离（BN） | ΔDA_VTA_baseline | +0.2（基线 0.4 → 0.6） | §三 |
| DA_SNc 基线偏离（BN） | ΔDA_SNc_baseline | +0.1（标签缺口裁决；基线 0.5 → 0.6） | §三 |
| 5HT 基线偏离（BN） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（BN） | bias_somatic / bias_cognitive / bias_limbic | +0.15 / −0.15 [NEW] / +0.15 | §三 |
| 清除习惯锁定阈值 | m_th | 0.4（bn_e03，SAN −2/回合） | §五.2 |
| 认知压制失效阈值 | m_th | 0.4（bn_e06/bn_e07，\|m\|） | §五.1 |
| 暴食发作触发阈值 | m_th | 0.3（bn_e09，不可中断） | §五.2 |
| 清除后 SAN 惩罚 | ΔSAN | −3/回合 | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [PTSD 重映射试点](ptsd-pilot.md), [神经性贪食症](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E7%A5%9E%E7%BB%8F%E6%80%A7%E8%B4%AA%E9%A3%9F%E7%97%87.md), [神经性厌食症](../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E7%A5%9E%E7%BB%8F%E6%80%A7%E5%8E%8C%E9%A3%9F%E7%97%87.md)（相反模式对照）, [NPC AI 行为模型](../../../规则/技能树系统/NPC AI 行为模型.md) §4.2/§5.2, [疾病-脑区链路映射-文献数据源](../../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七, [tripartite_model.json](../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../data/connectivity/link_registry.json)（⚠️ 已废弃）*
