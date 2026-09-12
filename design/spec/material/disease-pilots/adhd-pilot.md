# ADHD 重映射试点

> 26 病重映射第二批试点（模板：[ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §六 字段规范）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **18 条病理边（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」）**。核心病理 = **dlPFC/ACC 发育性解耦（非受损而是成熟延迟）+ DMN 干扰（FPN→DMN 抑制腿失连 + DMN 核心过度活跃）+ NE 调节失灵（波动非方向性）+ 延迟折扣率↑**。ENIGMA 效应量小（d < 0.25）→ 全表 m 量级偏小。档位过滤 B′：CGI-S 3-6 → **轻/中档可用、无重档**（重档值并入中档）。7 参数推导与标签组合交叉验证：§5.2 无 ADHD 行，设计建议「抑制不足 + 敏化-奖励」近似，发育性解耦 + NE 波动超出 6 标签表达 → **参数直调方案（NPC AI §4.3 第 3 级粒度）**，建议 §5.2 新增行。

## 目录

1. [文献锚点（4 篇核心 + 关键数据点）](#一文献锚点4-篇核心--关键数据点)
2. [50 实体病理边表（18 条，含三体边核验列）](#二50-实体病理边表18-条含三体边核验列)
3. [ADHD → 7 参数映射建议（4 tone + 3 CSTC）](#三adhd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_008_L 等 → 新病理边）](#四旧链路对照表link_008_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **ENIGMA ADHD mega-analysis**（[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 ADHD） | 结构 mega | **岛叶 + 内嗅皮层 + 颞中回表面积↓（d=−0.07~−0.24）**；杏仁核体积↓；额顶网络表面积↓（d=−0.08~−0.13，外化障碍特异）→ e11/e13/e14 结构锚 + e03 |
| 2 | **Norman et al. (2016)** *Biol Psychiatry*（dlPFC 成熟延迟） | 纵向影像 | 认知控制任务中 dlPFC **低激活——发育延迟而非受损** → 解耦沉默为主病理类型（e04/e05/e06） |
| 3 | **DMN 干扰假说**（Sonuga-Barke & Castellanos 2007；文献数据源 §七 ADHD「DMN 干扰——任务中 DMN 抑制不足」） | 功能假说 | 任务负激活缺失 → FPN→DMN 抑制腿失连（e01）+ DMN 核心过度活跃（e17）+ DMN-FPN 反相关不足（e03） |
| 4 | **延迟折扣率↑**（文献数据源 §七 ADHD「奖赏」） | 奖赏机制 | 腹侧纹状体对**即时奖赏过度敏感**（→ e15）+ dlPFC 对**延迟奖赏调控不足**（→ e16） |

**辅助锚（方向/范围补充）**：

- **ENIGMA 结构共享因子（文献数据源 §3.1）**——ADHD/ASD 模式**独立**于 MDD/BD/SCZ/OCD → ADHD 边集独立设计，不共享他病结构因子。
- **Soubrié (1986) 低 5HT→去抑制**（NPC AI §4.2「抑制不足」标签文献锚）——ADHD 冲动维度 → e18（DR→rACC 5-HT 腿）。
- **反应抑制（SSRT 延长）**——ADHD 冲动核心机制 → e10（STN→Pallidum STOP 超直接腿发育不足）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——9 条旧链路的方向/量级作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译；m 偏移量级沿用旧文件设计校准（ENIGMA d<0.25 → 全表量级偏小），**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（18 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**18 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**。
>
> 边 ID 命名：`adhd_e<NN>`。三档 m 偏移 = 轻/中/重；**档位过滤 B′（#88 待定项1 定案）：CGI-S 3-6 → 上限未达 7，无重档**——重档值并入中档（表中第 3 值 = 中档值，运行时 m 封顶中档）。
>
> **laterality_delta 全部 = 0**：ENIGMA mega 未报告稳健偏侧（双侧一致、d 值小），按 §6.5 规则 2 默认 0。

### 2.1 认知控制域（5 条）——「dlPFC/ACC 发育性解耦」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e01** ⭐新增 | rostralmiddlefrontal | precuneus | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.1694；**注**：图内无 ACC→dlPFC 直连，link_008_L（认知控制域）语义转移至 FPN→DMN 抑制腿 | 解耦沉默 | −0.1/−0.2/−0.2 | 0 | 旧 link_008_L（ACC→dlPFC 解耦）；DMN 干扰假说（dlPFC 无法压制 DMN） | 非线性跳变① + 行为覆盖③（DMN 入侵成员） |
| **adhd_e02** | caudalmiddlefrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3201 | 解耦沉默 | −0.1/−0.2/−0.2 | 0 | 旧 link_021_L（PMd→dlPFC 工作记忆环路解耦） | 非线性跳变①（工作记忆容量成员） |
| **adhd_e03** | medialorbitofrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4287 | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_082_L（vmPFC→dlPFC，DMN-FPN 反相关不足） | 行为覆盖③（DMN 入侵成员） |
| **adhd_e04** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | 0/−0.1/−0.1 | 0 | dlPFC/ACC 解耦的 CSTC 表达（ACC 冲突监测→尾状核策略 gate 发育不足）；Norman 2016 成熟延迟 | 3.1 节 bias_cognitive 推导锚 |
| **adhd_e05** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | 0/−0.1/−0.1 | 0 | dlPFC→纹状体认知 gate 发育不足 → 工作记忆容量↓（Norman 2016） | 非线性跳变①（激活点−2 结构基础） |

### 2.2 唤醒域（3 条）——「蓝斑 NE 调节失灵（波动非方向性）」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e06** | LocusCoeruleus | rostralmiddlefrontal | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_328（蓝斑→dlPFC NE，Hansen fc=0.75）——NE 过低期（认知资源不足） | 行为覆盖②（NE 低值期成员） |
| **adhd_e07** | LocusCoeruleus | pericalcarine | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_331（蓝斑→V1 NE，Hansen fc=0.6）——NE 过高期（感觉信噪比↑→注意力分散） | 行为覆盖①（NE 高值期成员） |
| **adhd_e08** | LocusCoeruleus | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=1, edr=0.4612 | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_332 波动拆分（蓝斑→杏仁核 NE，Hansen fc=0.7）冲动腿 | 行为覆盖①（情绪冲动期成员） |

### 2.3 行动门控域（2 条）——「行动门控资源↓ + 反应抑制失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e09** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_344（黑质→壳核 DA 解耦，行动门控资源↓） | 3.1 节 DA_SNc 推导锚 |
| **adhd_e10** ⭐新增 | SubthalamicNucleus | Pallidum | cstc | ✅ 命中：global 环路 `stop_hyperdirect`, stn→pallidal_output（Nambu 2015） | 解耦沉默 | 0/−0.1/−0.1 | 0 | 反应抑制缺陷（SSRT 延长）——STOP 超直接腿发育不足 → 冲动无法被急停 | 行为覆盖①（冲动打断侧翼） |

### 2.4 内感受/识别域（2 条）——ENIGMA 岛叶 + 模式识别↓

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e11** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_155_L（ACC吻侧→前脑岛）+ **ENIGMA 岛叶表面积↓** | 行为覆盖③（内感受整合↓） |
| **adhd_e12** | fusiform | inferiortemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.222 | 解耦沉默 | 0/−0.1/−0.1 | 0 | 旧 link_030_L（纺锤体回→颞下回，模式识别↓→细节遗漏） | 行为覆盖①（感觉分散侧翼） |

### 2.5 结构域（2 条）——ENIGMA 表面积↓（结构基础落边）

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e13** ⭐新增 | entorhinal | Hippocampus | privileged_pathway | ✅ 命中：`perforant_path`, dir=feedback, level_diff=−3, edr=0.6071 | 解耦沉默 | 0/−0.1/−0.1 | 0 | ENIGMA 内嗅皮层表面积↓（d=−0.07~−0.24）→ 记忆编码输入腿↓ | 行为覆盖③（记忆整合侧翼） |
| **adhd_e14** ⭐新增 | middletemporal | insula | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−2, edr=0.4421 | 解耦沉默 | 0/−0.1/−0.1 | 0 | ENIGMA 颞中回表面积↓（d=−0.07~−0.24）→ 突显整合腿↓ | 行为覆盖①（突显整合侧翼） |

### 2.6 奖赏域（2 条）——「延迟折扣率↑」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e15** ⭐新增 | VentralTegmentalArea | Accumbens-area | brainstem | ✅ 命中：`VTA_DA` targeted_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 腹侧纹状体对即时奖赏过度敏感（文献数据源 §七 ADHD 奖赏） | 3.1 节 DA_VTA 推导锚 |
| **adhd_e16** ⭐新增 | rostralmiddlefrontal | Accumbens-area | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−4（L5→L1）, edr=0.3593 | 解耦沉默 | 0/−0.1/−0.1 | 0 | dlPFC 对延迟奖赏调控不足（文献数据源 §七 ADHD 奖赏） | 行为覆盖③（冲动决策侧翼） |

### 2.7 整合域（2 条）——「DMN 干扰」内容源 + 冲动控制调制

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **adhd_e17** ⭐新增 | posteriorcingulate | precuneus | privileged_pathway | ✅ 命中：`dmn_core`, dir=feedforward, level_diff=2, edr=0.4926 | 过度耦合 | +0.1/+0.2/+0.2 | 0 | DMN 核心过度活跃 → 白日梦内容生成（DMN 干扰假说；DMN 内部 rs-FC 增强） | 行为覆盖③（白日梦替代行动的内容源） |
| **adhd_e18** ⭐新增 | DorsalRapheNucleus | rostralanteriorcingulate | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.1 | 0 | 5-HT 对 ACC 冲动控制调制不足（Soubrié 1986；ADHD 冲动维度）[设计层：标签→tone 反向锚定] | 3.1 节 5HT tone 推导锚 |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 全部 0 = ENIGMA mega 无稳健偏侧报告（§6.5 规则 2）。

---

## 三、ADHD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（ptsd-pilot §6.6 复制）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0（波动↑）** | e06（LC→dlPFC −）、e07（LC→V1 +）、e08（LC→Amygdala +） | LC 出边群 2+/1− 且幅值相抵 → **基线不变、方差↑**（调节失灵而非方向性异常）；波动效应挂行为覆盖①/② |
| 2 | DA_VTA_baseline | **+0.15** | e15（VTA→Accumbens +0/+0.1/+0.2） | VTA 出边群正偏移 → 即时奖赏超敏（延迟折扣率↑） |
| 3 | DA_SNc_baseline | **−0.1** | e09（SNc→Putamen 0/−0.1/−0.1） | SNc 出边群负偏移 → 行动门控资源↓；**修正项 vs 标签 0（见 3.2）** |
| 4 | 5HT_baseline | **−0.2** | e18（DR→rACC 0/−0.1/−0.1 解耦沉默） | DR 出边群负向 → 冲动控制调制不足（Soubrié 1986）；幅值由「抑制不足」标签 −0.2 锚定 |
| 5 | bias_somatic | **+0.15** | 无 somatic 环路边群命中 → 取标签「抑制不足」 | 冲动躯体行动倾向（多动/冲动）；标签锚 +0.15 |
| 6 | bias_cognitive | **−0.15** | e04（ACC→Caudate −）、e05（dlPFC→Caudate −） | cognitive 环路边群 2/2 负偏移 → 认知/语言行动倾向↓（任务参与/启动困难、注意力不集中）；**修正项 vs 标签 0（见 3.2）** |
| 7 | bias_limbic | **+0.15** | 无 limbic 环路边群命中 → 取标签「敏化-奖励」 | 奖赏驱动行动倾向↑（即时奖赏追逐）；标签锚 +0.15 |

### 3.2 与标签组合交叉验证（敌我同构闭环）

> **§5.2 无 ADHD 行**。设计层建议 2 标签近似：「抑制不足」（冲动）+「敏化-奖励」（即时奖赏超敏）——多标签叠加取最大值，clamp 值域：

| 参数 | 标签组合结果（建议） | 本文边推导结果 | 一致？ |
|------|--------------------|--------------|:---:|
| NE_baseline | 0 | 0（波动↑） | ✅ |
| DA_VTA_baseline | +0.2（敏化-奖励） | +0.15（e15） | ✅（幅值校准层） |
| DA_SNc_baseline | 0 | −0.1（e09） | ⚠️ 修正 |
| 5HT_baseline | −0.2（双标签） | −0.2（e18） | ✅ |
| bias_somatic | +0.15（抑制不足） | 0（边群无命中）→ 取标签 | ✅（取标签） |
| bias_cognitive | 0 | −0.15（e04/e05） | ⚠️ 修正 |
| bias_limbic | +0.15（敏化-奖励） | 0（边群无命中）→ 取标签 | ✅（取标签） |

**修正处置**：
- **DA_SNc −0.1**：行动门控资源↓（壳核腿）为 ADHD 结构特征（文献数据源「行动门控域 壳核/尾状核↓」），6 标签不触达 DA_SNc → 参数直调修正 −0.1 `[NEW 数值校准层]`。
- **bias_cognitive −0.15**：发育性解耦 → 认知行动倾向↓，6 标签无负 bias_cognitive 对应（社交钝化方向同但语义为社交域，不适用）→ 参数直调修正 −0.15 `[NEW]`。

**结论**：ADHD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（2 处修正有机制依据）。**ADHD 属 NPC AI §4.3 第 3 级粒度（参数直调）**——发育性解耦 + NE 波动超出 6 标签表达。最终参数：**NE=0.3（波动）、DA_VTA=0.55、DA_SNc=0.4、5HT=0.3、bias_somatic=+0.15、bias_cognitive=−0.15、bias_limbic=+0.15**。**建议 NPC AI §5.2 新增 ADHD 行（参数直调清单）**。

---

## 四、旧链路对照表（link_008_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_008_L | ACC→dlPFC | 解耦沉默 −0.1/−0.2/−0.3 | **adhd_e01**（dlPFC→precuneus FPN→DMN 抑制腿） | ⚠️ **语义转移**——三体图无 ACC→dlPFC 直连；认知控制域解耦 + DMN 干扰合并承载 |
| link_021_L | PMd→dlPFC | 解耦沉默 −0.1/−0.2/−0.3 | **adhd_e02** | ✅ 保留语义 |
| link_082_L | vmPFC→dlPFC | 解耦沉默 0/−0.1/−0.2 | **adhd_e03** | ✅ 保留语义 |
| link_328 | LocusCoeruleus→dlPFC | 解耦沉默 0/−0.1/−0.2 | **adhd_e06** | ✅ 保留语义（NE 低值期腿） |
| link_331 | LocusCoeruleus→V1 | 过度耦合 0/+0.1/+0.2 | **adhd_e07** | ✅ 保留语义（NE 高值期腿） |
| link_332 | LocusCoeruleus→Amygdala | 过度耦合+解耦沉默（双向波动） | **adhd_e08** | ⚠️ **波动拆分**——正偏移腿（冲动期）→ e08；负偏移腿（认知不足期）并入 e06（LC→dlPFC 解耦）；波动动力学保留于行为覆盖①/② |
| link_344 | SubstantiaNigraParsCompacta→Putamen | 解耦沉默 0/−0.1/−0.2 | **adhd_e09** | ✅ 保留语义 |
| link_155_L | ACC吻侧→前脑岛 | 解耦沉默 0/−0.1/−0.2 | **adhd_e11** | ✅ 保留语义 + **并吞 ENIGMA 岛叶表面积↓** |
| link_030_L | fusiform→inferiortemporal | 解耦沉默 0/−0.1/−0.1 | **adhd_e12** | ✅ 保留语义 |
| （旧表无） | FPN→DMN 抑制腿失连（DMN 干扰核心） | — | **adhd_e01** | ⭐ 新增（并吞 link_008_L） |
| （旧表无） | ACC/dlPFC→尾状核 gate 发育不足（成熟延迟 CSTC 表达） | — | **adhd_e04 / adhd_e05** | ⭐ 新增 |
| （旧表无） | STN→Pallidum STOP 腿发育不足（SSRT 延长） | — | **adhd_e10** | ⭐ 新增 |
| （旧表无） | 内嗅皮层→海马 输入腿↓（ENIGMA） | — | **adhd_e13** | ⭐ 新增 |
| （旧表无） | 颞中回→岛叶 突显腿↓（ENIGMA） | — | **adhd_e14** | ⭐ 新增 |
| （旧表无） | VTA→腹侧纹状体 即时奖赏超敏 | — | **adhd_e15** | ⭐ 新增——DA_VTA 机制锚 |
| （旧表无） | dlPFC→NAcc 延迟奖赏调控不足 | — | **adhd_e16** | ⭐ 新增 |
| （旧表无） | PCC↔precuneus DMN 核心过度活跃 | — | **adhd_e17** | ⭐ 新增——DMN 干扰内容源 |
| （旧表无） | DR→rACC 5-HT 冲动调制腿不足 | — | **adhd_e18** | ⭐ 新增——5HT tone 锚 |

**处置规则总结**：端点对存在 → 直接映射；不存在 → **语义转移优先**（link_008_L → e01；link_332 波动拆分），「病理新增」0 条（§6.4 从严）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 唤醒域 净方向 > 0（NE 过高期）→ 感觉域随机激活 1 条链路；L4-L5 技能命中 −20% | ✅ 保留 | **adhd_e07 / adhd_e08**（NE 高值期边，m 取高值段）+ **adhd_e14**（突显整合腿↓侧翼） | 波动动力学保留：净方向由 LC 出边群瞬时和判定 |
| 唤醒域 净方向 < 0（NE 过低期）→ L3-L5 技能需要额外 1 激活点 | ✅ 保留 | **adhd_e06**（LC→dlPFC 解耦，NE 低值期） | 认知资源不足期 |
| 认知控制域 \|m\| > 0.2 → DMN 入侵：每回合 10% 概率跳过 M1 声明（白日梦替代行动） | ✅ 保留 | **认知控制域边群**（e01/e04/e05）m_max > 0.2 + **adhd_e17**（DMN 内容源） | 「认知控制域」在新格式 = 认知控制域病理边集；白日梦内容由 e17 提供 |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 认知控制域 m_max < −0.3 → dlPFC 工作记忆容量 −2（实际激活点 −2）；作用域 link_008_L + link_021_L | ✅ 保留（改作用域） | **认知控制域边群**（e01/e02/e04/e05）m_max < −0.3 → 激活点 −2 | 注：B′ 无重档（CGI-S 3-6）→ m_max < −0.3 需轻/中档叠加场景触发；e05 为工作记忆容量的 CSTC 结构基础 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_008_L, link_021_L, link_328, link_332 | **adhd_e01, adhd_e02, adhd_e06, adhd_e08** |
| 2（关联） | link_331, link_344, link_155_L, link_082_L | **adhd_e03, adhd_e07, adhd_e09, adhd_e11, adhd_e13, adhd_e14, adhd_e15, adhd_e16, adhd_e17** |
| 1（边缘） | link_030_L | **adhd_e05, adhd_e10, adhd_e12, adhd_e18** |

> 核心 = 认知控制域解耦（e01/e02）+ NE 波动两腿（e06/e08）；新增边中 e04/e15/e16/e17 落关联（机制锚）、e10/e18 落边缘。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6；ADHD 无重档（B′，CGI-S 3-6，重档并入中档） | pathology_edges.json（schema §6.1） |
| 偏侧偏离量 | laterality_delta | 0（ENIGMA 无稳健偏侧，§6.5 规则 2） | pathology_edges.json |
| NE 基线偏离（ADHD） | ΔNE_baseline | 0（波动↑，基线 0.3 不变） | §三 |
| DA_VTA 基线偏离（ADHD） | ΔDA_VTA_baseline | +0.15（基线 0.4 → 0.55） | §三 |
| DA_SNc 基线偏离（ADHD） | ΔDA_SNc_baseline | −0.1（基线 0.5 → 0.4）`[NEW 修正项]` | §三 |
| 5HT 基线偏离（ADHD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（ADHD） | bias_somatic / bias_cognitive / bias_limbic | +0.15 / −0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| NE 波动高值期阈值 | — | LC 出边群瞬时和 > 0 → 感觉分散（e07/e08） | §五.1 |
| NE 波动低值期阈值 | — | LC 出边群瞬时和 < 0 → 额外 1 激活点（e06） | §五.1 |
| DMN 入侵阈值 | m_th | 认知控制域 m_max > 0.2 → 10% 跳过 M1 声明 | §五.1 |
| 工作记忆容量跳变 | m_th | 认知控制域 m_max < −0.3 → 激活点 −2 | §五.2 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [注意缺陷多动障碍](../../../entities/diseases/%E6%B3%A8%E6%84%8F%E7%BC%BA%E9%99%B7%E5%A4%9A%E5%8A%A8%E9%9A%9C%E7%A2%8D.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§4.3/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §3.1/§七, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../../data/connectivity/link_registry.json)（⚠️ 已废弃 2026-08-07）*
