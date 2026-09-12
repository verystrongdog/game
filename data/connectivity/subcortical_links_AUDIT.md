# subcortical_links.json 对抗性审核报告

> 逐条验证 `data/connectivity/subcortical_links.json` 中 11 条皮下-皮下连接的文献引用。交叉引用 `reference/literature/疾病-脑区链路映射-文献数据源.md` 作为区域级佐证，PubMed 摘要为逐引用验证依据。

## 目录

1. [交叉引用总览](#一交叉引用总览)
2. [逐连接审核](#二逐连接审核)
3. [严重错误汇总](#三严重错误汇总)
4. [引用质量问题](#四引用质量问题)
5. [证据层级不匹配](#五证据层级不匹配)
6. [修正建议清单](#六修正建议清单)
7. [附录：已验证引用 PubMed ID 速查](#附录已验证引用-pubmed-id-速查)

---

## 一、交叉引用总览

**`subcortical_links.json` 与 `疾病-脑区链路映射-文献数据源.md` 的重叠度：几乎为零。**

| | subcortical_links.json | 文献数据源.md |
|---|---|---|
| 引用类型 | 单项 DTI/概率追踪研究 | 大规模 meta 分析、ENIGMA、RDoC 框架 |
| 引用数 | 14 条独立引用键 | 8 篇关键文献 |
| 重叠引用 | — | 仅 `RDoC_reward_valuation` 有概念重叠 |

唯一概念交叉点：JSON 中的 `RDoC_reward_valuation` 对应文献数据源 §四 的 RDoC 正性效价-奖赏评估域。

文献数据源 §八 自述：「疾病→具体链路映射 ⚠️ 文献在脑区/网络层，不在 364 链路层，**需设计师翻译**」。JSON 正是做了这个翻译——但翻译质量需要逐条审核。

文献数据源在**脑区/网络层面**确认了 JSON 涉及的绝大部分脑区对存在功能/结构关联（如杏仁核-海马、杏仁核-OFC、OFC-纹状体、壳核-丘脑在 Guo 2026、Opel 2020、RDoC v4 中均有覆盖），但这只能作为**区域级佐证**，不能替代束级 DTI 证据。

---

## 二、逐连接审核

### 连接 1：杏仁核 → 海马体 CA1

```json
"source_region": "杏仁核", "target_region": "海马体 CA1",
"pathway": "杏仁核→海马体(钩束+杏仁核背侧束)",
"fc_strength": 0.80,
"ref": "Zhou2015_MultipleSclerosis, Granger2020_NeuroImage, Clark2022_eLife, PMC6831033_amygdalofugal"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Zhou2015_MultipleSclerosis | 26229470 | ✅ | **部分支持**。Zhou F et al. (2015), *Neuropsychiatr Dis Treat*。DTI 概率追踪证实杏仁核↔海马结构连接。但：(1) 研究 MS 患者病理状态非健康人；(2) **未提及钩束或杏仁核背侧束**的具体束名。 |
| Granger2020_NeuroImage | — | ❌ | **期刊名错误**。Granger 未在 NeuroImage 发表 UF 论文。实际发表在 *J Neurosci* (2021, PMID 33328295) 和 *Neurobiol Learn Mem* (2021, PMID 33285317)。两篇均研究 UF 连接杏仁核→OFC/MTL，不直接涉及杏仁核→海马的结构连接。 |
| Clark2022_eLife | — | ⚠️ | Clark IA et al. (2022), *eLife* 11:e79303。研究了穹窿、UF、旁海马扣带束。**对穹窿和 UF 均未发现显著关联**——显著结果仅限于旁海马扣带束。阴性结果不应作为阳性连接证据。 |
| PMC6831033_amygdalofugal | 31689177 | 🔥 | **严重错误**。Folloni et al. (2019), *eLife*, PMC6831033。杏仁核被盖腹侧束（AmF）连接杏仁核→**前额叶**（腹侧纹状体/NAcc/OFC），**不连接海马**。海马仅作为对照束（穹窿）出现。这是事实性错误——将 AmF 张冠李戴为杏仁核→海马通路。 |

**综合判定：🔴 不通过。** 4 条引用中：1 条事实错误、1 条期刊名错误、1 条阴性结果、1 条仅部分支持。需全部重新审核。

---

### 连接 2：海马体 CA1 → 杏仁核

```json
"source_region": "海马体 CA1", "target_region": "杏仁核",
"pathway": "海马体→杏仁核(钩束双向连接)",
"fc_strength": 0.80,
"ref": "Zhou2015_MultipleSclerosis, Clark2022_eLife"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Zhou2015_MultipleSclerosis | 26229470 | ✅ | DTI 概率追踪不区分方向，双向连接推断合理。但同上，未命名钩束。 |
| Clark2022_eLife | — | ❌ | 同上，穹窿/UF 结果阴性，不应作为阳性证据。 |

**综合判定：🟡 勉强通过。** 仅 Zhou2015 一条有效引用。Clark2022 应移除。

---

### 连接 3：杏仁核 → OFC

```json
"source_region": "杏仁核", "target_region": "OFC",
"pathway": "杏仁核→OFC(钩束)",
"fc_strength": 0.85,
"ref": "Passamonti2012_PLoS_ONE, Lee2020_Anxiety, Trostl_social_phobia_UF"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Passamonti2012_PLoS_ONE | 23144970 | ✅ | Passamonti L et al. (2012), *PLoS ONE*。DTI + 虚拟解剖（virtual dissection），直接证实 UF（杏仁核↔OFC）在 conduct disorder 中 FA 异常。**直接 DTI 证据，可作为主引用。** |
| Lee2020_Anxiety | 32002922 | ⚠️ | Lee & Lee (2020), *Adv Exp Med Biol*。**综述**，非原始 DTI 研究。汇总了 UF-杏仁核-OFC 在焦虑中的 DTI 证据。作为次级引用合理，但不满足 JSON `_method` 声明的"DTI 原始研究"标准。 |
| Trostl_social_phobia_UF | — | ⚠️ | Tröstl J et al. (2011), *European Psychiatry* 26/S2:182, P01-182。**会议摘要**，非完整论文。n=14 社交恐惧症患者，UF 双侧 FA↓。样本量极小+会议摘要，证据等级低。 |

**综合判定：🟢 通过（需降级次级引用标注）。** Passamonti2012 为坚实的主引用。Lee2020 和 Trostl 应标注为次级/弱证据。

---

### 连接 4：OFC → 杏仁核

```json
"source_region": "OFC", "target_region": "杏仁核",
"pathway": "OFC→杏仁核(钩束,自上而下恐惧消退)",
"fc_strength": 0.85,
"ref": "Passamonti2012_PLoS_ONE, Granger2020_NeuroImage"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Passamonti2012_PLoS_ONE | 23144970 | ✅ | UF 是双向束，反向引用合理。 |
| Granger2020_NeuroImage | — | ❌ | 同上，期刊名错误。实际 Granger 论文（*J Neurosci* 2021, PMID 33328295）描述了 UF 双向连接杏仁核↔OFC，但引用键需修正。 |

**综合判定：🟢 通过（需修正引用名）。**

---

### 连接 5：杏仁核 → 伏隔核/NAcc

```json
"source_region": "杏仁核", "target_region": "伏隔核/NAcc",
"pathway": "杏仁核→NAcc(基底外侧杏仁核→腹侧纹状体)",
"fc_strength": 0.75,
"ref": "Baliki2013_JNeurosci_NAcc_parcellation"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Baliki2013_JNeurosci_NAcc_parcellation | 24107968 | ✅ | Baliki MN et al. (2013), *J Neurosci*。DTI 概率追踪，杏仁核（AMYG）明确列为 NAcc 结构连接靶点之一（Fig 3 connectivity fingerprints）。但注意：这不是论文主要发现（重点是 NAcc core/shell 功能分离），杏仁核连接是连通性指纹中的一个数据点。 |

**综合判定：🟢 通过。** 引用有效，但建议寻找以杏仁核→NAcc 为主要焦点的补充引用。

---

### 连接 6：伏隔核/NAcc → 杏仁核

```json
"source_region": "伏隔核/NAcc", "target_region": "杏仁核",
"pathway": "NAcc→杏仁核(腹侧纹状体→基底外侧杏仁核)",
"fc_strength": 0.70,
"ref": "Baliki2013_JNeurosci_NAcc_parcellation"
```

**同连接 5。** 🟢 通过。

> ℹ️ 双向 fc_strength 不对称（0.75 vs 0.70）需提供来源——是来自 Baliki 论文的具体数值还是设计师估算？需标注。

---

### 连接 7：伏隔核/NAcc → 丘脑 🔥

```json
"source_region": "伏隔核/NAcc", "target_region": "丘脑",
"pathway": "NAcc→丘脑(前丘脑辐射+accumbofrontal束)",
"fc_strength": 0.75,
"ref": "Olivo2018_FrontHumNeurosci, Elliott2023_HCP_reward"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Olivo2018_FrontHumNeurosci | 29520227 | 🔥 | Olivo G et al. (2018), *Front Hum Neurosci*。**严重曲解**。论文研究的"风险束"是**两个独立束**：前丘脑辐射（ATR，丘脑→额叶）和 accumbofrontal 束（NAcc→额叶）。两条束分别投射到额叶，**论文未证明 NAcc→丘脑的直接连接**。将两个独立束拼接成 NAcc→丘脑是不成立的。 |
| Elliott2023_HCP_reward | 38700259 | 🔥 | Elliott BL et al. (2024), *Hippocampus*。研究海马→VTA/vmPFC/腹侧纹状体的连接。**丘脑不在靶区列表中**。论文根本不涉及丘脑。 |

**综合判定：🔴 不通过——两条引用均不成立。** 这是全表最严重的引用失败。需寻找真正证明 NAcc-丘脑直接连接的 DTI 研究（如 NAcc→丘脑前核/背内侧核的束路追踪），或降级此连接为"待验证"。

---

### 连接 8：伏隔核/NAcc → 海马体 CA1

```json
"source_region": "伏隔核/NAcc", "target_region": "海马体 CA1",
"pathway": "NAcc→海马(奖赏-记忆回路)",
"fc_strength": 0.70,
"ref": "Elliott2023_HCP_reward_628subjects, Baliki2013_JNeurosci"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Elliott2023_HCP_reward_628subjects | 38700259 | ✅ | Elliott et al. (2024), *Hippocampus*。n=628 HCP，概率追踪。发现腹侧纹状体（含 NAcc）与海马长轴有同质化连接分布。**直接证据，大样本。** |
| Baliki2013_JNeurosci | 24107968 | ⚠️ | 同上，海马在 NAcc 连通性指纹中作为靶点之一。间接支持。 |

**综合判定：🟢 通过。** Elliott 为坚实的主引用。

> ℹ️ `Elliott2023_HCP_reward_628subjects` 和连接 7 中的 `Elliott2023_HCP_reward` 是**同一篇论文**，用了两个不同的引用键。需统一。

---

### 连接 9：海马体 CA1 → 丘脑

```json
"source_region": "海马体 CA1", "target_region": "丘脑",
"pathway": "海马→丘脑(穹窿→乳头体→丘脑前核)",
"fc_strength": 0.75,
"ref": "Elliott2023_HCP_reward, Clark2022_eLife_fornix"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| Elliott2023_HCP_reward | 38700259 | ❌ | 同上，丘脑不在靶区中。不支持此连接。 |
| Clark2022_eLife_fornix | — | ⚠️ | Clark et al. (2022) 描述了穹窿连接海马→前丘脑的解剖路径。但论文**对穹窿未发现显著结果**（显著限于旁海马扣带束）。穹窿→乳头体→丘脑前核是 Papez 回路的经典神经解剖学知识，不需要 Clark 2022 来证明。 |

**综合判定：🟡 勉强通过（需更换引用）。** Elliott 应移除。穹窿→丘脑前核的 Papez 回路应引用经典解剖学文献（如 Papez 1937, Aggleton & Brown 1999, 或人类 DTI 穹窿研究如 Concha et al. 2005），而非一篇对该束结果阴性的论文。

---

### 连接 10：OFC → 伏隔核/NAcc

```json
"source_region": "OFC", "target_region": "伏隔核/NAcc",
"pathway": "OFC→NAcc(眶额-纹状体奖赏回路)",
"fc_strength": 0.80,
"ref": "RDoC_reward_valuation, Haber2010_frontostriatal"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| RDoC_reward_valuation | — | ⚠️ | NIMH RDoC 框架 v4，非同行评审论文。在正性效价-奖赏评估域中列出了 OFC→腹侧纹状体。框架级引用，非 DTI 原始证据。 |
| Haber2010_frontostriatal | 19812543 | ✅ | Haber & Knutson (2010), *Neuropsychopharmacology*。高引综述（3000+），详细描述了 OFC→腹侧纹状体（含 NAcc）奖赏回路。但主要基于**灵长类示踪剂 + 人类 fMRI**，不是人类 DTI。 |

**综合判定：🟢 通过。** OFC→NAcc 是神经科学中极为成熟的连接，两条均为合理的权威引用。但应注意它们不满足 JSON `_method` 声明的"DTI/概率追踪"标准——这里用的是框架+综述级证据。如需完全合规，可补充一篇人类 DTI 研究（如 Bracht et al. 2009 或类似）。

---

### 连接 11：壳核 → 丘脑

```json
"source_region": "壳核", "target_region": "丘脑",
"pathway": "壳核→丘脑(纹状体-丘脑,基底节直接通路)",
"fc_strength": 0.85,
"ref": "CSTC_model_Alexander1986, Haber2010"
```

| 引用 | PMID | 存在? | 判定 |
|------|------|-------|------|
| CSTC_model_Alexander1986 | 3085570 | ✅ | Alexander, DeLong & Strick (1986), *Ann Rev Neurosci*。CSTC 环路的奠基性论文，明确描述了壳核→GPi→丘脑→皮层的平行回路。注意通路是**间接的**（经 GPi/SNr），JSON pathway 字段"基底节直接通路"正确标注了这一点。 |
| Haber2010 | 19812543 | ✅ | 补充了 CSTC 环路的当代理解。 |

**综合判定：🟢 通过。** 经典文献支撑充分。

---

## 三、严重错误汇总

以下引用存在**事实性错误**，必须修正：

| # | 连接 | 问题引用 | 问题描述 | 严重度 |
|---|------|---------|---------|:---:|
| 1 | 杏仁核→海马体 | `PMC6831033_amygdalofugal` | AmF 通路连接杏仁核→**前额叶**（腹侧纹状体/NAcc/OFC），不连接海马。论文中海马仅作为对照束出现。 | 🔴 严重 |
| 2 | NAcc→丘脑 | `Olivo2018_FrontHumNeurosci` | 论文研究的是两个独立束（ATR 丘脑→额叶 + accumbofrontal NAcc→额叶），不构成 NAcc→丘脑直接连接。将两条独立束拼接为 NAcc→丘脑是对论文的曲解。 | 🔴 严重 |
| 3 | NAcc→丘脑 | `Elliott2023_HCP_reward` | 丘脑不在该研究的靶区中（仅 VTA/vmPFC/腹侧纹状体）。 | 🔴 严重 |
| 4 | 海马→丘脑 | `Elliott2023_HCP_reward` | 同上。 | 🔴 严重 |
| 5 | 杏仁核→海马体 | `Granger2020_NeuroImage` | Granger 未在 NeuroImage 发表 UF 论文。实际发表于 *J Neurosci* (2021) 和 *Neurobiol Learn Mem* (2021)。且两篇均不直接支持杏仁核→海马连接。 | 🟠 中等 |
| 6 | 杏仁核→海马体 | `Clark2022_eLife` | 论文对 UF 和穹窿的统计结果均为**阴性**（无显著关联）。阴性结果不应作为阳性连接证据。 | 🟠 中等 |

---

## 四、引用质量问题

以下引用存在质量问题，建议降级或替换：

| # | 引用键 | 实际问题 | 建议 |
|---|--------|---------|------|
| 1 | `Trostl_social_phobia_UF` | 会议摘要（*European Psychiatry* 2011, P01-182），非完整同行评审论文，n=14 | 降级为辅助引用，或寻找正式发表的社交恐惧症 UF DTI 论文替代（如 Baur et al.） |
| 2 | `Lee2020_Anxiety` | 综述（*Adv Exp Med Biol*），非原始 DTI 研究 | 标注为综述级引用，补充原始研究 |
| 3 | `RDoC_reward_valuation` | NIMH 框架文档，非同行评审论文 | 标注为框架级引用 |
| 4 | `Clark2022_eLife` / `Clark2022_eLife_fornix` | 论文对 UF 和穹窿的结果为阴性，仅旁海马扣带束有显著结果 | 不应作为阳性连接证据使用；如仅作解剖学参考需标注"阴性结果" |
| 5 | `Elliott2023_HCP_reward` 和 `Elliott2023_HCP_reward_628subjects` | 同一篇论文（Elliott et al. 2024, *Hippocampus*, PMID 38700259）用了两个不同的引用键 | 统一为一个键，如 `Elliott2024_Hippocampus_HCP628` |

---

## 五、证据层级不匹配

JSON `_method` 声明标准：「每条连接需有至少一篇同行评审文献的 DTI/概率追踪证据」。

实际引用证据层级分布：

| 层级 | 引用 | 数量 |
|------|------|:---:|
| **DTI/概率追踪原始研究** | Passamonti2012, Baliki2013, Zhou2015, Elliott2023, Olivo2018 | 5 |
| **经典神经解剖学综述** | Alexander1986, Haber2010 | 2 |
| **综述/框架** | Lee2020 (综述), RDoC_reward_valuation (框架) | 2 |
| **会议摘要** | Trostl_social_phobia_UF | 1 |
| **阴性结果论文** | Clark2022_eLife | 1 |
| **不存在的引用** | Granger2020_NeuroImage | 1 |

**11 条连接中仅 5 条有真正的 DTI 原始研究支撑。** 6 条连接的引用包含综述、框架文档、会议摘要或错误引用。

---

## 六、修正建议清单

### 紧急（事实性错误）

- [ ] **连接 1（杏仁核→海马）**：移除 `PMC6831033_amygdalofugal`（AmF 不连海马）。寻找真正的杏仁核→海马束级 DTI 文献替代。`Clark2022_eLife` 也应移除（阴性结果）。
- [ ] **连接 7（NAcc→丘脑）**：移除 `Olivo2018_FrontHumNeurosci` 和 `Elliott2023_HCP_reward`。寻找真正证明 NAcc-丘脑直接连接的 DTI 研究，或降级此连接为「待验证」并标注 `_status: "unverified"`。
- [ ] **连接 9（海马→丘脑）**：移除 `Elliott2023_HCP_reward`。替换为真正的穹窿 DTI 文献（如 Concha et al. 2005 穹窿 DTI, PMID 15884013）或 Papez 回路经典文献。

### 高优先级（引用修正）

- [ ] **全局**：`Granger2020_NeuroImage` → 改为 `Granger2021_JNeurosci` (PMID 33328295) 或 `Granger2021_NeurobiolLearnMem` (PMID 33285317)，并确认引用它的连接是否确实被该论文支持
- [ ] **全局**：统一 Elliott 引用键——`Elliott2023_HCP_reward` 和 `Elliott2023_HCP_reward_628subjects` 合并为一个标准键
- [ ] **全局**：移除所有 `Clark2022_eLife` 作为阳性连接证据的使用（保留为解剖学参考时需标注阴性结果）

### 中优先级（质量提升）

- [ ] **连接 3-4**：`Trostl_social_phobia_UF` 标注 `_evidence_level: "conference_abstract"`，或替换为 Baur et al. 的正式发表论文
- [ ] **连接 3-4**：`Lee2020_Anxiety` 标注 `_evidence_level: "review"`
- [ ] **连接 10**：`RDoC_reward_valuation` 标注 `_evidence_level: "framework"`
- [ ] **连接 5-6**：`Baliki2013` 的 fc_strength 不对称（0.75 vs 0.70）来源需注明（来自论文数据 vs 设计师估算）

### 低优先级（增强）

- [ ] 所有引用添加 PMID/DOI 字段以便追溯
- [ ] 每条连接添加 `_evidence_level` 字段（值：`primary_dti` / `review` / `framework` / `classic` / `conference_abstract`）
- [ ] 连接 5-6：寻找以杏仁核→NAcc 为主要焦点的补充文献，替代以 NAcc parcellation 为焦点的 Baliki 2013
- [ ] 连接 10：补充一篇人类 DTI 原始研究（OFC→NAcc 的束路追踪），使证据层级满足 `_method` 声明
- [ ] 连接 1-2：fc_strength 0.80 的来源标注（哪篇文献的数据或何种转换公式）

---

## 附录：已验证引用 PubMed ID 速查

| JSON 引用键 | 实际文献 | PMID | 期刊 | 类型 |
|------------|---------|------|------|------|
| Zhou2015_MultipleSclerosis | Zhou F et al. (2015) | 26229470 | Neuropsychiatr Dis Treat | DTI 原始研究 |
| Granger2020_NeuroImage | ❌ 不存在。实际为 Granger SJ et al. (2021) | 33328295 | J Neurosci | HARDI 原始研究 |
| Granger2020_NeuroImage (备选) | Granger SJ et al. (2021) | 33285317 | Neurobiol Learn Mem | DTI+fMRI 原始研究 |
| Clark2022_eLife | Clark IA et al. (2022) | — | eLife 11:e79303 | DTI 原始研究（对 UF/穹窿阴性） |
| PMC6831033_amygdalofugal | Folloni D et al. (2019) | 31689177 | eLife | DTI 概率追踪 |
| Passamonti2012_PLoS_ONE | Passamonti L et al. (2012) | 23144970 | PLoS ONE | DTI 原始研究 |
| Lee2020_Anxiety | Lee KS & Lee SH (2020) | 32002922 | Adv Exp Med Biol | 综述 |
| Baliki2013_JNeurosci_NAcc_parcellation | Baliki MN et al. (2013) | 24107968 | J Neurosci | DTI 原始研究 |
| Olivo2018_FrontHumNeurosci | Olivo G et al. (2018) | 29520227 | Front Hum Neurosci | DTI 原始研究 |
| Elliott2023_HCP_reward | Elliott BL et al. (2024) | 38700259 | Hippocampus | DTI 概率追踪 |
| Haber2010_frontostriatal | Haber SN & Knutson B (2010) | 19812543 | Neuropsychopharmacology | 综述 |
| CSTC_model_Alexander1986 | Alexander GE et al. (1986) | 3085570 | Ann Rev Neurosci | 经典文献 |
| Trostl_social_phobia_UF | Tröstl J et al. (2011) | — | Eur Psychiatry 26/S2 (摘要) | 会议摘要 |
| RDoC_reward_valuation | NIMH RDoC Snapshot v4 (2018) | — | nimh.nih.gov | 框架文档 |

---

*创建: 2026-08-01 | 审核: 14 条引用中 5 条为 DTI 原始研究，3 条存在事实性错误*
*关联: [subcortical_links.json](subcortical_links.json), [疾病-脑区链路映射-文献数据源.md](../../reference/literature/%E7%96%BE%E7%97%85-%E8%84%91%E5%8C%BA%E9%93%BE%E8%B7%AF%E6%98%A0%E5%B0%84-%E6%96%87%E7%8C%AE%E6%95%B0%E6%8D%AE%E6%BA%90.md)*
