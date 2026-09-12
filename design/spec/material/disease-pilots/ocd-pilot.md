# OCD 重映射试点

> 26 病重映射第二批试点（模板：[ptsd-pilot.md](../disease-pilots/ptsd-pilot.md) §六 字段规范）。本文件把旧 `link_NNN` 链路表（挂已废弃 link_registry.json）重映射为三体模型上的 **17 条病理边（全部命中 `tripartite_model.json` 现有边，0 条「病理新增」）**，每条含 `{source, target, 边类型, 病理类型, m偏移三档, laterality_delta, 文献依据, 行为覆盖/非线性跳变挂接}`。核心病理 = **CSTC 环路过度耦合无法终止**（认知环路走 Caudate：ACC→Caudate / dlPFC→Caudate；躯体环路走 Putamen：SNc→Putamen / superiorfrontal→Putamen GO + Putamen→Pallidum NO-GO 腿解耦）+ 奖赏-边缘环路劫持（OFC→Accumbens↑、海马 ALFF↑）+ DMN 背内侧↓。档位过滤 B′：CGI-S 3-7 → **三档全可用**。7 参数推导（4 tone + 3 CSTC bias）与 NPC AI §5.2 标签组合「敏化-威胁 + 抑制不足」交叉验证：5/7 一致，DA_SNc、bias_cognitive 两处由 CSTC 核心机制修正（参数直调，[NEW 数值校准层]）——敌我同构闭环成立。

## 目录

1. [文献锚点（4 篇核心 + 关键数据点）](#一文献锚点4-篇核心--关键数据点)
2. [50 实体病理边表（17 条，含三体边核验列）](#二50-实体病理边表17-条含三体边核验列)
3. [OCD → 7 参数映射建议（4 tone + 3 CSTC）](#三ocd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_007_L 等 → 新病理边）](#四旧链路对照表link_007_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点（4 篇核心 + 关键数据点）

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **CSTC 皮质-纹状体-丘脑-皮质模型**（Alexander et al. 1986, PMID 3085570；[疾病-脑区链路映射-文献数据源.md](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §七 OCD「核心回路」） | 回路模型 | OCD = CSTC 闭环**过度耦合无法终止**；腹侧动机环路 OFC→NAcc→丘脑 → 认知/躯体/边缘三环路病边设计（e01/e04/e07/e12） |
| 2 | **文献数据源 §七 OCD 连接表** | 连接 meta 汇总 | **↑OFC-腹侧纹状体/NAcc**（→ e12）、**↑底丘脑核(STN)-壳核**（→ e16，STN 唯一出边 STOP 超直接）、**↓壳核-OFC/IFG/岛叶**（→ e08 NO-GO 腿解耦）、**↓DMN背内侧(PCC-dmPFC)**（→ e15 precuneus→dmPFC 解耦） |
| 3 | **Guo et al. (2026)** *Transl Psychiatry*（254 实验, 10,456 患者，跨诊断 ALFF meta） | 静息态 ALFF meta | OCD 特异性偏离 = **ALFF↑ 海马 / 左侧 IFG / ACC-mPFC；ALFF↓ 右侧岛叶 / 壳核**（文献数据源 §2.3）→ e02/e13/e14 方向锚 + 偏侧说明（§二 图例） |
| 4 | **NPC AI §4.2/§5.2 标签校准**（[NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md)） | 设计校准 | OCD = 敏化-威胁 + 抑制不足 → 纹状体-丘脑-皮层环路↑；tone ±0.1~±0.2、bias ±0.15 幅值锚（→ §三 7 参数量级） |

**辅助锚（方向/范围补充）**：

- **ENIGMA 结构共享因子（Opel et al. 2020，文献数据源 §3.1）**——OCD 与 MDD/BD/SCZ 结构异常高度相关（r=.443–.782）→ OCD 常伴反刍/情绪成分 → §三 bias_cognitive 修正的第 3 标签「反刍」设计依据（旧文件默认标签即含反刍）。
- **SSRI 一线治疗 OCD**（5-HT 系统参与）——DR→ACC 5-HT 腿负向偏移的机制锚（e17）；Soubrié (1986) 低 5HT→去抑制（NPC AI §4.2「抑制不足」标签文献锚）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——10 条旧链路的方向/量级（ENIGMA fc + Hansen 2024 + Paxinos 2004）作为语义继承源，见 §四。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八「需设计师翻译」）；m 偏移量级沿用旧文件设计校准，**全部数值有来源，新增数值标记 `[NEW]`**。

---

## 二、50 实体病理边表（17 条，含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**17 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条「病理新增」**——OCD 无正常图中不存在的连接。
>
> 边 ID 命名：`ocd_e<NN>`。三档 m 偏移 = 轻/中/重；**档位过滤 B′（#88 待定项1 定案）：CGI-S 3-7 → 三档全可用**（下限 3 不触发「无轻档」、上限 7 不触发「无重档」）。量级沿用旧文件设计校准。
>
> **laterality_delta 全部 = 0**：Guo 2026 提示左侧 IFG↑ / 右侧岛叶-壳核↓ 的偏侧，但 OCD 偏侧 meta 证据不一致（CSTC 环路研究多双侧对称），按 §6.5 规则 2「无稳健偏侧证据 → 默认 0」（偏侧仅装饰层，#92 原则）。

### 2.1 认知控制域（5 条）——「CSTC cognitive 环路过度耦合无法终止」核心

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e01** ⭐新增 | caudalanteriorcingulate | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.2/+0.4/+0.6 | 0 | CSTC 模型（ACC 冲突监测→尾状核策略 gate 无法关闭）；Guo 2026 ALFF↑ ACC-mPFC；link_008_L 语义拆分承载 | 非线性跳变②（CSTC 闭环锁定作用域成员） |
| **ocd_e02** | caudalanteriorcingulate | rostralanteriorcingulate | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.5879 | 过度耦合 | +0.2/+0.4/+0.6 | 0 | 旧 link_007_L（ACC→ACC吻侧闭环，ENIGMA fc=8.84） | 行为覆盖① + 非线性跳变②（闭环再入源） |
| **ocd_e03** | caudalmiddlefrontal | rostralmiddlefrontal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3201 | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_021_L（PMd→dlPFC 工作记忆环路） | 非线性跳变②（作用域成员） |
| **ocd_e04** ⭐新增 | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.3/+0.5 | 0 | 文献数据源 §七 OCD 对应功能域「认知控制域 dlPFC→纹状体过度耦合」；link_008_L 语义拆分承载 | 3.1 节 bias_cognitive 推导锚 |
| **ocd_e14** | caudalanteriorcingulate | superiorfrontal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=3（L2→L5）, edr=0.651 | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_009_L（ACC→mPFC，ENIGMA fc=10.27）；Guo 2026 ALFF↑ ACC-mPFC | 行为覆盖①（冲突监测侧翼） |

### 2.2 行动门控域（5 条）——「行动门控卡住」双机制

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e05** | SubstantiaNigraParsCompacta | Putamen | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 过度耦合 | +0.1/+0.3/+0.4 | 0 | 旧 link_344（黑质→壳核 DA，Hansen fc=0.85, Paxinos 2004） | 非线性跳变③（行动门控失效成员） |
| **ocd_e06** | SubstantiaNigraParsCompacta | Caudate | brainstem | ✅ 命中：`SNc_DA` targeted_broadcast | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_343（黑质→尾状核 DA，Hansen fc=0.9, Paxinos 2004） | 3.1 节 DA_SNc 推导锚 |
| **ocd_e07** ⭐新增 | superiorfrontal | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.3/+0.5 | 0 | 文献数据源 §七 OCD「行动门控域 壳核↑」→ somatic GO 腿翻译（SMA 参与强迫行为重复执行） | 3.1 节 bias_somatic 推导锚 |
| **ocd_e08** | Putamen | Pallidum | cstc | ✅ 命中：somatic 环路 `nogo_indirect`, striatal_gate→pallidal_output | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 旧 link_363（壳核↔丘脑解耦）语义转移 → NO-GO 腿解耦 = 动作无法被终止；文献数据源「↓壳核-OFC/IFG/岛叶」 | 非线性跳变③（行动门控失效成员） |
| **ocd_e16** ⭐新增 | SubthalamicNucleus | Pallidum | cstc | ✅ 命中：global 环路 `stop_hyperdirect`, stn→pallidal_output（Nambu 2015） | 过度耦合 | +0.1/+0.3/+0.5 | 0 | 文献数据源「↑底丘脑核(STN)-壳核」→ STN 唯一出边语义转移（STOP 过度活跃 → 行动切换受阻/僵化） | 行为覆盖①（行动切换成本×2 结构基础） |

### 2.3 内感受/唤醒域（3 条）——「不对劲」信号持续激活

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e09** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 过度耦合 | 0/+0.2/+0.3 | 0 | 旧 link_155_L（ACC吻侧→前脑岛 冲突不适，ENIGMA fc=6.29） | 行为覆盖②（内感受域 m_max 成员） |
| **ocd_e10** | LocusCoeruleus | caudalanteriorcingulate | brainstem | ✅ 命中：`LC_NE` diffuse_broadcast | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_327（蓝斑→ACC NE，Hansen fc=0.85） | 3.1 节 NE tone 推导锚；行为覆盖② |
| **ocd_e17** ⭐新增 | DorsalRapheNucleus | caudalanteriorcingulate | brainstem | ✅ 命中：`Raphe_5HT` diffuse_broadcast | 解耦沉默 | 0/−0.1/−0.2 | 0 | 5-HT 投射至冲突监测环路不足 → 抑制不足（SSRI 一线治疗 OCD；Soubrié 1986 低 5HT 去抑制）[设计层：标签→tone 反向锚定] | 3.1 节 5HT tone 推导锚 |

### 2.4 识别域（1 条）——模式识别过度

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e11** | fusiform | inferiortemporal | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.222 | 过度耦合 | 0/+0.1/+0.2 | 0 | 旧 link_030_L（纺锤体回→颞下回，ENIGMA fc=10.61）；对细节/对称/污染过度分类 | 行为覆盖③（模式识别假阳性） |

### 2.5 奖赏/边缘域（2 条）——「OFC→腹侧纹状体↑」+ 海马 ALFF↑

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e12** ⭐新增 | lateralorbitofrontal | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | +0.1/+0.3/+0.4 | 0 | 文献数据源 §七 OCD「↑OFC-腹侧纹状体/NAcc」；CSTC 腹侧动机环路 | 3.1 节 bias_limbic 推导锚 |
| **ocd_e13** ⭐新增 | Hippocampus | Accumbens-area | cstc | ✅ 命中：limbic 环路 `go_direct`, cortical_input→striatal_gate | 过度耦合 | 0/+0.2/+0.3 | 0 | Guo 2026 ALFF↑ 海马（§2.3）→ 侵入性记忆反复进入情绪-行动门控 | 行为覆盖②（情境匹配侧翼） |

### 2.6 DMN 域（1 条）——「DMN 背内侧↓」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **ocd_e15** ⭐新增 | precuneus | superiorfrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=1, edr=0.242；**注**：图内无 PCC→dmPFC 直连，「PCC-dmPFC 背内侧连接↓」经 precuneus（PCC 邻接 DMN hub）承载 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 文献数据源 §七 OCD「↓DMN背内侧(PCC-dmPFC)」 | 行为覆盖①（僵化侧翼） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非「病理新增」）；Δ 全部 0 = 无稳健偏侧证据（Guo 2026 左侧 IFG↑/右侧岛叶-壳核↓ 提示但不一致；CSTC 环路双侧对称报告为主，§6.5 规则 2）。

---

## 三、OCD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则（ptsd-pilot §6.6 复制）：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **+0.2** | e10（LC→ACC 0/+0.1/+0.2） | LC 出边群命中且正偏移 → 全局警觉↑（OCD 焦虑共病高）；幅值由标签「敏化-威胁」+0.2 锚定 |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | OCD 主要累及 SNc 纹状体 DA 通路（黑质纹状体），非 VTA 中脑边缘通路 |
| 3 | DA_SNc_baseline | **+0.15** | e05（SNc→Putamen +0.1/+0.3/+0.4）、e06（SNc→Caudate 0/+0.2/+0.3） | SNc 出边群 2/2 命中且正偏移 → 习惯/策略过度执行；**修正项 vs 标签 0（见 3.2）** |
| 4 | 5HT_baseline | **−0.2** | e17（DR→ACC 0/−0.1/−0.2 解耦沉默） | DR 出边群负向 → 5-HT 传递不足 = 去抑制（Soubrié 1986）；SSRI 治疗锚 |
| 5 | bias_somatic | **+0.15** | e07（SF→Putamen GO +0.5max）、e08（Putamen→Pallidum NO-GO −0.3max） | somatic 环路边群正负并存，GO 腿幅值主导 → 躯体行动门控「卡在开启」/冲动执行；与「抑制不足」标签一致 |
| 6 | bias_cognitive | **+0.15** | e01（ACC→Caudate +0.6max）、e04（dlPFC→Caudate +0.5max） | cognitive 环路边群 2/2 强正偏移 → 认知/语言行动倾向被锁死 = 强迫思维-强迫行为循环；**修正项 vs 标签 0（见 3.2）** |
| 7 | bias_limbic | **+0.15** | e12（OFC→Accumbens +）、e13（HC→Accumbens +） | limbic 环路边群被价值/记忆信号劫持 → 情绪/本能行动倾向↑；与「敏化-威胁」标签一致 |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §5.2「强迫症 = 敏化-威胁 + 抑制不足」双标签（多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | +0.2（敏化-威胁） | +0.2 | ✅ |
| DA_VTA_baseline | 0 | 0 | ✅ |
| DA_SNc_baseline | 0（6 标签均不触达 SNc） | +0.15（e05/e06） | ⚠️ 修正 |
| 5HT_baseline | −0.2（双标签） | −0.2 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | 0 | +0.15（e01/e04） | ⚠️ 修正 |
| bias_limbic | +0.15（敏化-威胁） | +0.15 | ✅ |

**修正处置**：
- **DA_SNc +0.15**：CSTC 行动门控「习惯/策略过度执行」是 OCD 核心机制（任务明确要求 Putamen/Caudate 相关），6 标签界面无 DA_SNc 触达 → **参数直调修正 +0.15** `[NEW 数值校准层]`。
- **bias_cognitive +0.15**：cognitive 环路过度耦合无法终止 = OCD 核心（§5.2「纹状体-丘脑-皮层环路↑」），双标签组合的 bias_cognitive=0 表达不足 → 两方案闭合：① 参数直调修正 +0.15；② 3 标签组合「敏化-威胁 + 抑制不足 + 反刍」（反刍标签 bias_cognitive +0.15；旧文件默认标签即含反刍；Opel 2020 共享形态学因子佐证 OCD-抑郁重叠）`[NEW 建议标签扩展]`。

**结论**：OCD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽（2 处修正有明确机制依据）。OCD NPC 最终参数：**NE=0.5、5HT=0.3、DA_VTA=0.4、DA_SNc=0.65、bias_somatic=+0.15、bias_cognitive=+0.15、bias_limbic=+0.15**。

---

## 四、旧链路对照表（link_007_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_007_L | ACC→ACC吻侧 | 过度耦合 +0.2/+0.4/+0.6 | **ocd_e02**（caudalanteriorcingulate→rostralanteriorcingulate） | ✅ 保留语义（端点/类型/量级不变） |
| link_008_L | ACC→dlPFC | 过度耦合 +0.1/+0.3/+0.5 | **ocd_e01 + ocd_e04**（ACC→Caudate / dlPFC→Caudate） | ⚠️ **语义拆分**——三体图无 ACC→dlPFC 直连；「认知控制→纹状体过度耦合」闭环由 CSTC cognitive 两腿承载 |
| link_021_L | PMd→dlPFC | 过度耦合 0/+0.2/+0.3 | **ocd_e03**（caudalmiddlefrontal→rostralmiddlefrontal） | ✅ 保留语义 |
| link_344 | SubstantiaNigraParsCompacta→Putamen | 过度耦合 +0.1/+0.3/+0.4 | **ocd_e05** | ✅ 保留语义 |
| link_343 | SubstantiaNigraParsCompacta→Caudate | 过度耦合 0/+0.2/+0.3 | **ocd_e06** | ✅ 保留语义 |
| link_363 | Putamen→Thalamus | 解耦沉默 −0.1/−0.2/−0.3 | **ocd_e08**（Putamen→Pallidum NO-GO 腿） | ⚠️ **语义转移**——三体图无 Putamen→Thalamus 直连（CSTC 经 Pallidum 中转）；「动作无法终止」由 NO-GO 腿解耦承载 |
| link_155_L | ACC吻侧→前脑岛 | 过度耦合 0/+0.2/+0.3 | **ocd_e09** | ✅ 保留语义（偏侧 L 后缀并入 Δ，Δ=0） |
| link_327 | LocusCoeruleus→ACC | 过度耦合 0/+0.1/+0.2 | **ocd_e10** | ✅ 保留语义 |
| link_030_L | fusiform→inferiortemporal | 过度耦合 0/+0.1/+0.2 | **ocd_e11** | ✅ 保留语义 |
| link_009_L | ACC→mPFC | 过度耦合 0/+0.2/+0.3 | **ocd_e14**（caudalanteriorcingulate→superiorfrontal） | ✅ 保留语义（特权通路承载） |
| （旧表无） | CSTC cognitive 环路过度耦合（思路链仅叙事层） | — | **ocd_e01 / ocd_e04** | ⭐ 新增——核心机制落数据 |
| （旧表无） | 强迫行为重复执行 = somatic GO 过度耦合（文献「行动门控域 壳核↑」） | — | **ocd_e07** | ⭐ 新增 |
| （旧表无） | OFC→腹侧纹状体↑（文献 §七 OCD） | — | **ocd_e12** | ⭐ 新增——bias_limbic 机制锚 |
| （旧表无） | 海马 ALFF↑（Guo 2026 §2.3）→ limbic 门控劫持 | — | **ocd_e13** | ⭐ 新增 |
| （旧表无） | DMN 背内侧↓（文献 §七 OCD） | — | **ocd_e15** | ⭐ 新增 |
| （旧表无） | STN-壳核↑（文献 §七 OCD）→ STN 唯一出边 STOP | — | **ocd_e16** | ⭐ 新增 |
| （旧表无） | DR→ACC 5-HT 腿不足（抑制不足 tone 锚） | — | **ocd_e17** | ⭐ 新增 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移/拆分优先**（link_363 → e08；link_008_L → e01+e04），「病理新增」0 条（§6.4 从严）。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_007_L m > 0.5 → 行动切换成本 ×2（上一回合动作不可更换，僵化） | ✅ 保留 | **ocd_e02** m > 0.5 + **ocd_e16**（STOP 过度 → 切换受阻的结构基础） | ACC→ACC吻侧闭环再入；STN STOP 过度使僵化从「代价」升级为「结构」 |
| 内感受域 m_max > 0.3 → ACC 冲突监测：每回合 5% 概率强制激活 ACC↔ACC吻侧（L）闭环再入 | ✅ 保留（去 L 后缀） | **内感受/唤醒域边群**（e09/e10/e17）m_max > 0.3 → 强制激活 **ocd_e02** | 「内感受域」在新格式 = 内感受/唤醒域病理边集 |
| 识别域 m_max > 0.2 → 纺锤体回识别 → 模式识别假阳性率 +10% | ✅ 保留 | **ocd_e11** m > 0.2 | 同义替换（fusiform→inferiortemporal） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| link_007_L m > 0.6 → CSTC 闭环锁定：认知控制→行动门控→感觉反馈→认知控制 环路无法终止，SAN −2/回合；作用域 link_007_L + link_008_L | ✅ 保留（改作用域） | **ocd_e02** m > 0.6，作用域 = **认知控制域边群**（e01/e02/e03/e04/e14） | link_008_L 已拆分并入 → 作用域收敛为认知控制域病理边集 |
| 行动门控域 壳核↑ + 壳核↔丘脑↓ 同时 → 行动门控失效：每回合 20% 概率重复上一回合动作；作用域 link_344 + link_363 | ✅ 保留（改作用域） | **ocd_e05**（SNc→Putamen↑）与 **ocd_e08**（Putamen→Pallidum NO-GO↓）同时成立 → 20% 重复动作 | link_363 语义转移至 e08；「壳核↔丘脑↓」= NO-GO 腿解耦 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_007_L, link_008_L, link_344, link_363 | **ocd_e01, ocd_e02, ocd_e04, ocd_e05, ocd_e08** |
| 2（关联） | link_021_L, link_343, link_155_L, link_009_L | **ocd_e03, ocd_e06, ocd_e09, ocd_e12, ocd_e13, ocd_e14, ocd_e16, ocd_e17** |
| 1（边缘） | link_327, link_030_L | **ocd_e07, ocd_e10, ocd_e11, ocd_e15** |

> 核心 = CSTC cognitive 环路（e01/e04）+ 闭环源（e02）+ 行动门控双机制（e05/e08）；新增边中 e12/e13（bias_limbic 锚）落关联、e15/e16 落关联/边缘。具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6；OCD 三档全可用（B′，CGI-S 3-7） | pathology_edges.json（schema §6.1） |
| 偏侧偏离量 | laterality_delta | 0（无稳健偏侧证据，§6.5 规则 2） | pathology_edges.json |
| NE 基线偏离（OCD） | ΔNE_baseline | +0.2（基线 0.3 → 0.5） | §三 |
| 5HT 基线偏离（OCD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| DA_SNc 基线偏离（OCD） | ΔDA_SNc_baseline | +0.15（基线 0.5 → 0.65）`[NEW 修正项]` | §三 |
| CSTC 偏置（OCD） | bias_somatic / bias_cognitive / bias_limbic | +0.15 / +0.15 / +0.15（值域 [−0.3,+0.3]） | §三 |
| CSTC 闭环锁定阈值 | m_th | 0.6（e02，SAN −2/回合，作用域认知控制域边群） | §五.2 |
| 行动切换成本阈值 | m_th | 0.5（e02） | §五.1 |
| 行动门控失效组合 | — | e05 与 e08 同时成立 → 20% 重复动作 | §五.2 |
| 模式识别假阳性阈值 | m_th | 0.2（e11，+10%） | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](../disease-pilots/grilling-88.md), [ptsd-pilot.md](../disease-pilots/ptsd-pilot.md), [强迫症](../../../entities/diseases/%E5%BC%BA%E8%BF%AB%E7%97%87.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) §4.2/§5.2, [偏侧化架构](../../../rules/skill-tree/%E5%81%8F%E4%BE%A7%E5%8C%96%E6%9E%B6%E6%9E%84.md) §四/§八, [脑功能层级模型](../../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) §二十, [疾病-脑区链路映射-文献数据源](../../../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §2.3/§七, [左右脑偏侧化-文献数据源](../../../../reference/literature/%E5%B7%A6%E5%8F%B3%E8%84%91%E5%81%8F%E4%BE%A7%E5%8C%96-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md) §八, [tripartite_model.json](../../../../data/connectivity/tripartite_model.json), [link_registry.json](../../../../data/connectivity/link_registry.json)（⚠️ 已废弃 2026-08-07）*
