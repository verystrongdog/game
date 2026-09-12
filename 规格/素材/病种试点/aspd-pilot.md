---
父类: 人格障碍（Q0.5 新建父类；原 社会认知障碍 迁出）
疾病ID: aspd
CGI-S范围: 3-7
文献: "Dugré et al. (2020) fMRI meta 83 studies (1,328 CP/ASPD): 急性威胁 dACC/SMA/前岛叶/dlPFC 低激活, 社会认知 壳核/楔前叶/mPFC 异常 | Dugré & Potvin (2021) 18 seed-based rs-fMRI meta: 杏仁核-vmPFC 连接↓ 与反社会严重度负相关, vmPFC/dmPFC/后扣带-楔前叶 连接 disrupted | CU traits→右侧杏仁核活动↓（meta-regression）"
创建: 2026-08-21
---

# 反社会型人格障碍（ASPD）重映射试点

> 26 病重映射第二批（Grilling #88 Q0.6；父类迁移：社会认知障碍 → **人格障碍**，Q0.5 定案）。本文件把旧 `link_NNN` 链路表重映射为三体模型上的 **14 条病理边**（全部命中 `tripartite_model.json` 现有边，0 条"病理新增"）。核心病理 = **冷酷-共情缺失**（vmPFC→杏仁核 解耦沉默 + dmPFC/ACC 共情回路静默）+ **威胁反应低**（杏仁核→PAG 解耦沉默，与 PTSD 同对反向）+ **冲动控制失败**（dlPFC→认知 gate 解耦 + 5-HT 抑制不足）。7 参数推导（5HT −0.2 + bias_somatic +0.15 + bias_cognitive −0.15）与 NPC AI §4.2 标签组合「社交钝化 + 抑制不足」完全一致——敌我同构闭环成立。输出格式照 [ptsd-pilot.md](ptsd-pilot.md) §六 字段规范。

## 目录

1. [文献锚点](#一文献锚点)
2. [50 实体病理边表（含三体边核验列）](#二50-实体病理边表含三体边核验列)
3. [ASPD → 7 参数映射建议（4 tone + 3 CSTC）](#三aspd--7-参数映射建议4-tone--3-cstc)
4. [旧链路对照表（link_009_L 等 → 新病理边）](#四旧链路对照表link_009_l-等--新病理边)
5. [行为覆盖/非线性跳变保留清单](#五行为覆盖非线性跳变保留清单)
6. [参数速查表](#六参数速查表)

---

## 一、文献锚点

| # | 文献 | 类型 | 关键数据点（→ 病理边用途） |
|---|------|------|--------------------------|
| 1 | **Dugré et al. (2020)** *Neurosci Biobehav Rev*（83 研究, 1,328 反社会/ASPD fMRI meta） | 任务态 fMRI meta | 急性威胁：**dACC/SMA/前岛叶/dlPFC 低激活**；社会认知（共情）：**壳核/楔前叶/mPFC 异常**（[疾病-脑区链路映射-文献数据源.md](../../参考/文献/疾病-脑区链路映射-文献数据源.md) §七 ASPD）→ 防御域边群（e01-e04）+ 自我社会域边群（e05-e07）+ 壳核共情边（e13）+ SMA 边（e14） |
| 2 | **Dugré & Potvin (2021)** *Psychol Med*（18 seed-based rs-fMRI meta） | 静息态连接 meta | **杏仁核-vmPFC 连接↓ 与反社会严重度负相关**；vmPFC/dmPFC/后扣带-楔前叶 连接 disrupted → e05（vmPFC→杏仁核 解耦核心）+ e06/e07（楔前叶/dmPFC 解耦） |
| 3 | **Aoki (2013) / Rogers & De Brito (2016)**（VBM meta） | 结构 meta | 前岛叶+杏仁核+vlPFC+dmPFC+梭状回 灰质体积异常 → 结构侧支持 e03/e04/e07 的结构基础 |
| 4 | **CU traits meta-regression**（Dugré 2020 内嵌） | 连接-特质回归 | **冷酷无情特质 → 右侧杏仁核活动↓** → 防御域边（e01/e02/e03）laterality_delta **+0.2**（右偏） |

**辅助锚（方向/范围补充）**：

- **5-HT 冲动攻击假说**（Coccaro et al.；Soubrié 1986 行为抑制假说）——中枢 5-HT 功能↓ → 去抑制/冲动攻击 → e12（DR→杏仁核 5-HT 抑制传递↓）。
- **NPC AI §4.2 标签**——「社交钝化」（bias_cognitive −0.15）+「抑制不足」（5HT −0.2 + bias_somatic +0.15）为 ASPD 标签组合（旧文件默认标签，保留）。
- **旧链路注册表（link_registry.json，⚠️ 已废弃 2026-08-07）**——6 条旧链路（link_009_L/086_L/049_L/312/155_L/008_L）的方向/量级作为语义继承源，见 §四。
- **父类迁移注记**：Q0.5 定案 ASPD 归入新建「人格障碍」父类（与 BPD、分裂型并列），原「社会认知障碍」父类引用需在疾病目录迁移时更新。

> **转换规则声明**：文献给出脑区/网络层结论，三体边层映射为设计师翻译（文献数据源 §八"需设计师翻译"）；旧链路携带的 m 量级沿用旧文件设计校准值，新增边量级为本次设计校准 `[NEW]`。

---

## 二、50 实体病理边表（含三体边核验列）

> 端点名 = `tripartite_model.json` `graph_nodes` 的 dk_name（51 节点，含 STN；病理边禁触镜像 `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`）。**14 条全部命中三体模型现有边（1049 条 = 47 CSTC + 776 皮层-皮层 + 114 脑干 + 112 特权通路），0 条"病理新增"**。ASPD 无正常图中不存在的连接；「病理新增」边类型规范见 ptsd-pilot.md §六.4。
>
> 边 ID 命名：`<疾病ID>_e<NN>`（ASPD = `aspd`）。三档 m 偏移 = 轻/中/重（**档位可用性由 frontmatter `CGI-S范围` 过滤——2026-08-21 #88 待定项1 定案 B′**；ASPD 范围 3-7 → 三档全可用）。方向约定：**全部为解耦沉默（m 负偏移）**——ASPD 的病理本质是"信号发不出"（冷酷共情缺失 + 低威胁反应），与 PTSD/BPD 的"信号过强"形成镜像对照。
>
> **端点名对照速查**：vmPFC=`medialorbitofrontal`（L5，fid MedialOrbitalPrefrontalVMPFC）｜dmPFC=`superiorfrontal`（L5，fid SuperiorFrontalMPFC）｜dlPFC=`rostralmiddlefrontal`（L5）｜dACC=`caudalanteriorcingulate`（L2，fid AnteriorCingulateCortexDorsal）｜rACC=`rostralanteriorcingulate`（L2）｜前岛叶=`insula`（L2）｜杏仁核=`Amygdala`（L1）｜TPJ=`supramarginal`（L5，fid SupramarginalTPJ）｜壳核=`Putamen`（L1）｜楔前叶=`precuneus`（L4）｜SMA→`paracentral`（L3，设计师映射：DK 无独立 SMA 标签，SMA/pre-SMA 落旁中央小叶与额上回内侧）。

### 2.1 防御域（4 条）——「威胁反应低」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **aspd_e01** ⭐新增 | Amygdala | PeriaqueductalGray | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedback, level_diff=−1（L1→L0） | **解耦沉默** | −0.1/−0.2/−0.3 | **+0.2** | Dugré 2020 急性威胁杏仁核低激活；CU traits→右侧杏仁核活动↓ | 行为覆盖②（低恐惧）+ §五.2 跳变 |
| **aspd_e02** | PeriaqueductalGray | Amygdala | privileged_pathway | ✅ 命中：`brainstem_subcortical`, dir=feedforward, level_diff=+1 | 解耦沉默 | 0/−0.1/−0.3 | **+0.2** | 旧 link_312（ASPD 侧语义，方向修正见 §四）；PAG→杏仁核 防御表达静默 | 行为覆盖②（作用域成员） |
| **aspd_e03** ⭐新增 | Amygdala | insula | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.3261 | 解耦沉默 | −0.1/−0.2/−0.3 | **+0.2** | Dugré 2020 急性威胁前岛叶低激活；Aoki 2013 前岛叶灰质异常 | 行为覆盖②（威胁内感受不发） |
| **aspd_e04** ⭐新增 | caudalanteriorcingulate | Amygdala | corticocortical | ✅ 命中：dir=feedback, level_diff=−1, edr=0.3987 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | Dugré 2020 急性威胁 dACC 低激活 | 行为覆盖②（威胁评估信号发不出） |

### 2.2 自我社会域（4 条）——「共情缺失」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **aspd_e05** ⭐新增 | medialorbitofrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, **level_diff=−4**（L5→L1 真跨层） | **解耦沉默** | **−0.2/−0.4/−0.6** | 0 | Dugré & Potvin 2021 杏仁核-vmPFC 连接↓ 与反社会严重度负相关（核心） | 行为覆盖① + §五.2 跳变载体（共情核心） |
| **aspd_e06** | precuneus | medialorbitofrontal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.2083 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | Dugré 2020 社会认知楔前叶异常；Dugré & Potvin 2021 楔前叶连接 disrupted；旧 link_086_L 语义转移（见 §四） | 行为覆盖①（自我-他人参照断开） |
| **aspd_e07** ⭐新增 | superiorfrontal | Amygdala | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedback, level_diff=−4 | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | Dugré & Potvin 2021 dmPFC 连接 disrupted；Rogers & De Brito 2016 dmPFC 灰质异常 | 行为覆盖①（道德/共情评估静默） |
| **aspd_e08** | caudalanteriorcingulate | superiorfrontal | privileged_pathway | ✅ 命中：`prefrontal_limbic`, dir=feedforward, level_diff=+3 | 解耦沉默 | **−0.2/−0.3/−0.5** | 0 | 旧 link_009_L（dACC→dmPFC 社会评价链路，量级沿用） | §五.2 跳变载体（社会奖惩无效） |

### 2.3 语言社会域（2 条）——「TPJ 换位思考失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **aspd_e09** | inferiorparietal | supramarginal | corticocortical | ✅ 命中：dir=feedforward, level_diff=+1, edr=0.224（角回→TPJ） | 解耦沉默 | −0.1/−0.2/−0.3 | 0 | 旧 link_049_L（TPJ 换位思考）；Dugré 2020 社会认知网络异常 | 行为覆盖①（读意图不可用侧翼） |
| **aspd_e10** | rostralanteriorcingulate | insula | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.4246 | 解耦沉默 | 0/−0.1/−0.2 | 0 | 旧 link_155_L（rACC-前岛叶 共情内感受链路） | 行为覆盖①（共感不可用） |

### 2.4 认知控制域（4 条）——「冲动控制失败」

| 病理边ID | source | target | 边类型 | 三体核验（命中详情） | 病理类型 | m偏移(轻/中/重) | laterality_delta | 文献依据 | 挂接 |
|---|---|---|---|---|---|---|---|---|---|
| **aspd_e11** | rostralmiddlefrontal | Caudate | cstc | ✅ 命中：cognitive 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | **−0.1/−0.2/−0.4** | 0 | 旧 link_008_L 语义转移（ACC→dlPFC 无三体边，见 §四）；Dugré 2020 dlPFC 低激活 | 行为覆盖③（冲动控制） |
| **aspd_e12** ⭐新增 | DorsalRapheNucleus | Amygdala | brainstem | ✅ 命中：`Raphe_5HT` targeted_broadcast（privileged `brainstem_subcortical` 孪生边存在） | 解耦沉默 | 0/−0.1/−0.2 | 0 | 5-HT 冲动攻击假说（Coccaro et al.；Soubrié 1986）——低 5-HT → 去抑制 | 3.1 节 5HT tone 推导锚 |
| **aspd_e13** ⭐新增 | Putamen | Amygdala | corticocortical | ✅ 命中：dir=lateral, level_diff=0, edr=0.3395 | 解耦沉默 | 0/−0.1/−0.2 | 0 | Dugré 2020 社会认知壳核异常（共情躯体模拟回路断开） | 行为覆盖①（共情侧翼） |
| **aspd_e14** ⭐新增 | paracentral | Putamen | cstc | ✅ 命中：somatic 环路 `go_direct`, cortical_input→striatal_gate | 解耦沉默 | 0/−0.1/−0.2 | 0 | Dugré 2020 急性威胁 SMA 低激活（SMA→paracentral 设计师映射，见 §二 引言） | 行为覆盖②（防御运动准备不足） |

**图例**：⭐新增 = 旧链路表无对应、本次新增（均命中现有三体边，非"病理新增"）；Δ +0.2 = 右偏（CU traits 右侧杏仁核活动↓，§6.5 规则：右→+；仅防御域杏仁核出边承载），0 = 无偏侧证据（其余边双侧合并）。方向注释：与 PTSD 试点对比——同一对端点（Amygdala↔PeriaqueductalGray）在 PTSD 为**过度耦合/跨层短路**（威胁超敏）、在 ASPD 为**解耦沉默**（威胁迟钝），体现两病"信号强度相反"的镜像设计（文献数据源 §七：PTSD 杏仁核↑ / ASPD 杏仁核↓）。

---

## 三、ASPD → 7 参数映射建议（4 tone + 3 CSTC）

> 规则照 ptsd-pilot.md §6.6：**tone 从脑干广播边群推导，bias 从 CSTC 环路边推导**；量级沿用 NPC AI §4.2 标签校准（tone ±0.1~±0.2，bias ±0.15），方向有文献、幅值待数值校准。正常人基线：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5（运行时状态模型 §5.4）。

### 3.1 从病理边推导

| # | 参数 | 偏离值 | 推导边（命中） | 推导链 |
|---|------|--------|---------------|--------|
| 1 | NE_baseline | **0** | 无 LC 边群命中 | ASPD 非高唤醒疾病；低唤起理论（Raine）仅作叙事层，无三体边锚 |
| 2 | DA_VTA_baseline | **0** | 无 VTA 边群命中 | 奖赏敏感在壳核 CC 层（e13）表达，非 DA 广播层偏移 |
| 3 | DA_SNc_baseline | **0** | 无 SNc 边群命中 | 同上 |
| 4 | 5HT_baseline | **−0.2** | e12（DR→Amygdala 解耦沉默） | 中缝核 5-HT 抑制传递↓ → 去抑制/冲动攻击（Soubrié 1986；Coccaro et al.） |
| 5 | bias_somatic | **+0.15** | e05（vmPFC→杏仁核 解耦）、e11（dlPFC→Caudate 解耦）、e12（5HT↓） | 自上而下抑制失效边群 → 行动 gate 无法关闭 → 攻击冲动释放（与 PTSD 同链，方向相反——PTSD 是威胁劫持，ASPD 是抑制缺位） |
| 6 | bias_cognitive | **−0.15** | 社会认知边群（e05/e06/e07/e08/e09/e10 解耦） | 社交信号 gate 偏置低（社交钝化——不理解/不回应社交线索） |
| 7 | bias_limbic | **0** | 无 limbic 环路（Accumbens-area）边群正偏移 | 情绪反应低（冷酷）——非情绪驱动型病理，与 BPD（+0.15）形成对照 |

### 3.2 与标签组合交叉验证（敌我同构闭环）

NPC AI §4.2「社交钝化」+「抑制不足」双标签（旧文件默认标签保留；多标签叠加取最大值，clamp 值域）：

| 参数 | 标签组合结果 | 本文边推导结果 | 一致？ |
|------|------------|--------------|:---:|
| NE_baseline | 0 | 0 | ✅ |
| DA_VTA / DA_SNc | 0 | 0 | ✅ |
| 5HT_baseline | −0.2（抑制不足） | −0.2 | ✅ |
| bias_somatic | +0.15（抑制不足） | +0.15 | ✅ |
| bias_cognitive | −0.15（社交钝化） | −0.15 | ✅ |
| bias_limbic | 0 | 0 | ✅ |

**结论**：ASPD 病理边集 ⇔ 7 参数偏移 ⇔ 标签组合三方自洽。ASPD NPC 最终参数：5HT=0.3、bias_somatic=+0.15、bias_cognitive=−0.15（其余基线）。与 PTSD（NE +0.2 / bias_limbic +0.15）形成「威胁迟钝-冷酷 vs 威胁超敏-情绪化」的镜像对照。

---

## 四、旧链路对照表（link_009_L 等 → 新病理边）

| 旧链路 | 旧端点（link_registry，⚠️ 已废弃） | 旧类型/m | 新病理边 | 处置 |
|--------|--------------------------------|---------|---------|------|
| link_009_L | caudalanteriorcingulate→superiorfrontal（L2→L5） | 解耦沉默 −0.2/−0.3/−0.5 | **aspd_e08**（dACC→dmPFC） | ✅ 保留语义（特权通路命中；量级沿用） |
| link_086_L | medialorbitofrontal→temporalpole（L5→L2） | 解耦沉默 −0.1/−0.2/−0.3 | **aspd_e06**（precuneus→medialorbitofrontal） | ⚠️ **废弃直连**（三体图无 mOFC→temporalpole）；语义转移至 DMN 自我-他人参照边（楔前叶→vmPFC） |
| link_049_L | inferiorparietal→supramarginal（角回→TPJ） | 解耦沉默 −0.1/−0.2/−0.3 | **aspd_e09** | ✅ 保留语义（端点/类型/量级不变） |
| link_312 | PeriaqueductalGray→Amygdala（L0→L1） | 解耦沉默 0/−0.1/−0.3 | **aspd_e02** | ✅ 保留语义（PAG→杏仁核 方向）；叙事方向（杏仁核→PAG 防御反应低）落 ⭐aspd_e01 |
| link_155_L | rostralanteriorcingulate→insula | 解耦沉默 0/−0.1/−0.2 | **aspd_e10** | ✅ 保留语义（CC 命中） |
| link_008_L | caudalanteriorcingulate→rostralmiddlefrontal（dACC→dlPFC） | 解耦沉默 −0.1/−0.2/−0.4 | **aspd_e11**（rostralmiddlefrontal→Caudate） | ⚠️ **废弃直连**（三体图无 ACC→dlPFC 皮层边）；语义转移至 dlPFC→认知 gate（CSTC cognitive go_direct） |
| （旧表无） | vmPFC→杏仁核 连接↓（Dugré & Potvin 2021） | — | **aspd_e05** | ⭐ 新增——核心机制落数据 |
| （旧表无） | 杏仁核→PAG 防御反应低（CU traits 右杏仁核↓） | — | **aspd_e01** | ⭐ 新增——核心机制落数据 |
| （旧表无） | 急性威胁前岛叶/dACC/dlPFC 低激活（Dugré 2020） | — | **aspd_e03 / aspd_e04 / aspd_e11** | ⭐ 新增 |
| （旧表无） | 5-HT 冲动攻击（Coccaro/Soubrié） | — | **aspd_e12** | ⭐ 新增 |
| （旧表无） | 壳核共情异常 / SMA 低激活（Dugré 2020） | — | **aspd_e13 / aspd_e14** | ⭐ 新增 |

**处置规则总结**：端点对在三体图中存在 → 直接映射保留；不存在 → **语义转移优先**（link_086_L → e06、link_008_L → e11），「病理新增」从严（ASPD 0 条）。注意 link_312 为 PTSD/ASPD 共享旧链路：PTSD 侧取其 PAG→杏仁核 过度耦合（ptsd_e02），ASPD 侧取其 解耦沉默（aspd_e02）——同一旧链路在两侧语义不同，重映射后由**独立病理边 + 方向**承载，冲突消除。

---

## 五、行为覆盖/非线性跳变保留清单

### 5.1 行为覆盖（旧文件「行为覆盖」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 自我社会域 \|m\| > 0.3 → L4 读意图 不可用；L2 共感 不可用 | ✅ 保留（改挂接） | **自我社会域边群**（e05/e06/e07/e08，\|m_max\| 取群内最大值）+ e09/e13 | 共情缺失 = 读意图/共感技能禁用（理解侧，非表达侧） |
| 防御域 \|m\| > 0.2 → 敌方 SAN 攻击→自身 SAN 损失 −50% | ✅ 保留 | **防御域边群**（e01/e02/e03/e04，\|m_max\|） | 低共情→低情绪影响（威胁信号进不来） |
| 认知控制域 \|m\| > 0.3 → 冲动控制——M1/Broca 通道 15% 概率选攻击而非声明动作 | ✅ 保留 | **aspd_e11** \|m\| > 0.3（+e12 5HT↓ 佐证） | 同义替换（dlPFC→认知 gate 解耦） |

### 5.2 非线性跳变（旧文件「非线性跳变」表 → 新挂接）

| 旧条目 | 保留/调整 | 新挂接 | 说明 |
|--------|:---:|--------|------|
| 自我社会域 m_max < −0.4 → 社会奖惩完全无效 | ✅ 保留 | **aspd_e08** m < −0.4（重档 −0.5） | 同义替换（dACC→dmPFC 社会评价链路静默 → 敌方 Broca/社会信号对自身无 SAN/行为影响） |
| （旧表无） | ⭐ 新增 | **aspd_e01** m < −0.3 | 威胁刺激不触发恐惧反应（低恐惧——CU 特质重档），防御/逃跑 salience 归零 |

### 5.3 组件掉落池（旧文件「组件掉落池」→ 新边权重）

| 权重 | 旧链路 | 新病理边 |
|:---:|--------|---------|
| 2（核心） | link_009_L, link_086_L, link_312, link_008_L | **aspd_e08, aspd_e06, aspd_e01, aspd_e02, aspd_e11** |
| 2（关联） | link_049_L, link_155_L | **aspd_e09, aspd_e10, aspd_e03, aspd_e04, aspd_e05, aspd_e07, aspd_e12** |
| 1（边缘） | — | **aspd_e13, aspd_e14** |

> 核心 5 条 = 社会奖惩核心（e08）+ 自我参照断开（e06）+ 防御迟钝双向（e01/e02）+ 冲动控制（e11）；新增边中 e05（共情核心）暂落关联，具体权重再平衡 [待 #88 组件批次]。

---

## 六、参数速查表

| 参数 | 符号 | 默认值/约束 | 位置 |
|------|------|-----------|------|
| 病理边 m 偏移 | m_offset | 轻/中/重三档，\|m\| ≤ 0.6，m ∈ [0,1] 钳制（本文件全为负档） | pathology_edges.json（ptsd-pilot.md §6.1） |
| 偏侧偏离量 | laterality_delta | +0.2（e01/e02/e03，CU traits 右杏仁核↓），其余 0 | pathology_edges.json（§6.5） |
| 5HT 基线偏离（ASPD） | Δ5HT_baseline | −0.2（基线 0.5 → 0.3） | §三 |
| CSTC 偏置（ASPD） | bias_somatic / bias_cognitive | +0.15 / −0.15（值域 [−0.3,+0.3]） | §三 |
| 社会奖惩失效阈值 | m_th | −0.4（aspd_e08，社会奖惩完全无效） | §五.2 |
| 冲动概率 | p_impulse | 0.15（认知控制域 \|m\| > 0.3 时 M1/Broca 通道） | §五.1 |
| 防御域 SAN 减损 | r_san | 0.5（敌方 SAN 攻击→自身 SAN 损失 −50%） | §五.1 |

---

*创建: 2026-08-21 | 更新: 2026-08-21*
*关联: [grilling-88.md](grilling-88.md), [ptsd-pilot.md](ptsd-pilot.md), [反社会型人格障碍](../../实体/疾病目录/反社会型人格障碍.md), [NPC AI 行为模型](../../规则/技能树系统/NPC AI 行为模型.md) §4/§5.2, [偏侧化架构](../../规则/技能树系统/偏侧化架构.md) §四/§八, [脑功能层级模型](../../规则/技能树系统/脑功能层级模型.md), [疾病-脑区链路映射-文献数据源](../../参考/文献/疾病-脑区链路映射-文献数据源.md) §七, [角色与面具](../../实体/角色与面具.md) §8.8, [tripartite_model.json](../../data/connectivity/tripartite_model.json)*
