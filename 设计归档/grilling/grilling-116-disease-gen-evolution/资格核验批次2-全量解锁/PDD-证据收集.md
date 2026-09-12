# PDD（持续性抑郁障碍）资格核验 — 证据收集

> **证据收集，非裁决。** 本文档只做五步核验协议的素材采集（①DSM/ICD 标准定位 ②必要性分析输入 ③反样本 ④"病程模式声明"型原子候选材料 ⑤表征域材料），**不产出**：阈值数字、判定函数、最终资格规则、任何 ELIGIBLE/INELIGIBLE/UNDETERMINED 结论、任何原子归位定案。判定与定值全部留给用户裁决。
> 纪律约束（沿用 #113 + 批次 1）：G1-G4 全局不变量、反样本纪律、表征偏好 ≠ 资格阈值、症状计数不得充当资格原子、DSM 内部症状/时长条件归 #87 声明侧、MISSING ≠ FALSE、共享原子语义可复用但疾病级逻辑不可自动继承（Q2-11）。

| 项 | 值 |
|----|-----|
| Type | 资格核验批次 2（G4-PDD 族，证据收集层，子代理产出，待用户裁决） |
| 归属 | [#116](https://github.com/verystrongdog/game/issues/116) 配额表驱动核验批次（平凡实例化裁定 D6）——[批次 2 总览（全量解锁）](../资格核验批次2-全量解锁/总览.md) G4 行 |
| 前置 | #113 资格层（Eligibility(d)/原子三值/G1-G4）+ 批次 1（PTSD/DID/BPD 定案）+ 批次 2 先行项（SSD 收尾裁决 ✅） |
| 目标病 | 持续性抑郁障碍（PDD，原名 Dysthymia 心境恶劣） |
| 项目通道 | **A 临床史通道**（工作地图初判：E_d^hist 主导；[grilling-113 工作地图](../../grilling-113-disease-eligibility/grilling-113-disease-eligibility.md) :111 列 PDD（持续性抑郁）于 A 类） |
| 父类 | 奖赏系统障碍（`实体/疾病目录/持续性抑郁障碍.md` frontmatter） |
| 创伤易感事件类型 | [丧失/哀悼]（转化接口 §3.2.1 反向索引，只读镜像） |
| 召回候选集 | 丧失/哀悼 → {MDD 主, **PDD**, BD-I, BD-II, 环性}（转化接口 §3.2.1 映射表，:133） |
| 参考先例 | ① DEPRESSIVE_EPISODE_HISTORY = "当前或既往已声明的重性抑郁发作存在性"（MDD 必要正向、BD-II 必要正向，**分别核验**；转化接口 §3.2.2 :207）② CYCLIC_MOOD_HISTORY = "#87 病程模式声明（反复亚阈值心境波动病程模式存在性，≠ 时期计数）"（:211）③ SYMPTOM_DURATION_6M = "已声明的症状持续 ≥6 月事实（时长判定留声明侧）"（批次 2 先行 SSD ✅ 2026-09-06 照准） |
| 表征偏好 | PDD (N, F, D_seg) = (0.95, 0.10, 0.05)——"慢性叙事"（转化接口 §3.2.3 :275）；对照 MDD (0.90, 0.20, 0.05) |

## 目录

- [〇、项目内锚点一览（供对照，证据引用基准）](#〇项目内锚点一览供对照证据引用基准)
- [一、DSM-5 / ICD-11 定位](#一dsm-5-icd-11-定位)
- [二、必要性分析输入（d⟹X 方向材料，不作结论）](#二必要性分析输入dx-方向材料不作结论)
- [三、反样本收集（慢性低落但非 PDD）](#三反样本收集慢性低落但非-pdd)
- [四、"病程模式声明"型原子候选材料（PDD_PERSISTENT_DEPRESSION_PATTERN + DEPRESSIVE_EPISODE_HISTORY 关系）](#四病程模式声明型原子候选材料pdd_persistent_depression_pattern--depressive_episode_history-关系)
- [五、表征域材料（E_d^mem 侧，高 N 慢性叙事能否资格化）](#五表征域材料e_dmem-侧高-n-慢性叙事能否资格化)
- [六、待核验清单与移交](#六待核验清单与移交)

---

## 〇、项目内锚点一览（供对照，证据引用基准）

以下为证据引用的项目内基准（均已 Read 确认，引用即读取铁律）：

| 锚点 | 项目内取值/语义 | 出处 |
|------|----------------|------|
| 资格层链路 | 候选召回 → Eligibility(d) ∈ {ELIGIBLE, INELIGIBLE, UNDETERMINED} → 仅 ELIGIBLE 进入主病选择/聚合 | 转化接口 §3.2.2 |
| 证据域 | E_d = E_d^mem（记忆内表征）∪ E_d^hist（记忆外临床史声明；来源 = #87 A′-Generator 规范化声明字段） | 转化接口 §3.2.2 :170-175 |
| 证据原子三值 | X_e ∈ {1, 0, MISSING}；MISSING ≠ FALSE | 转化接口 §3.2.2 :183 |
| 归位原则 | P_i 必要 ⟺ d⟹P_i；N_j 排除 ⟺ N_j⟹¬d（方向不可交换） | 转化接口 §3.2.2 :199-201 |
| 禁止项 | L_agg→原子；创伤事件→原子；症状计数→原子；**DSM 内部症状/时长条件→Eligibility 原子**（归 #87 声明依据） | 转化接口 §3.2.2 :213 |
| 共享原子纪律 | 共享原子（DEPRESSIVE）语义核验一次，但 MDD⟹DEPRESSIVE 与 BD-II⟹DEPRESSIVE 分别证明（**共享原子语义可复用，疾病级逻辑不可自动继承**） | 决策树 :4094（Q2-11） |
| 工作地图 | A 临床史病（E_d^hist 主导）含 **PDD（持续性抑郁）**；B 表征病 / C 混合为其余通道（初判，待逐病核验） | [grilling-113 决策记录](../../grilling-113-disease-eligibility/grilling-113-disease-eligibility.md) :109-115 |
| 召回候选集 | 丧失/哀悼 → {MDD 主, PDD, BD-I, BD-II, 环性} | 转化接口 §3.2.1 :133 |
| 表征偏好 PDD | (0.95, 0.10, 0.05)——"慢性叙事"；MDD (0.90, 0.20, 0.05)——"反刍 VAM 主导" | 转化接口 §3.2.3 :274-275 |
| 表征三维分离先例 | PTSD vs DID 欧氏距离 ≈ 0.852（D_seg 主导，"三维分离生效"）——**区分度验证只在候选集内做相对比较，非资格阈值** | 转化接口 §3.2.3 :277 |
| PDD 机制层设计 | 慢性持续型：无急性跳变、持续消耗；CGI-S 3-6；重档（双重抑郁叠加 CGI 6）临时启用 MDD 跳变表 [待 #88 定案] | `实体/疾病目录/持续性抑郁障碍.md` :48；persistent-depressive-pilot §五 |
| 事件快照时间粒度 | t_anchor = 时间锚（3 时段 × 日 粒度），情境向量分量——**点时刻粒度，无"发作时长/病程"字段** | 转化接口 §3.0 :81；grilling-90 数学建模 :73 |
| L 语义 | L = ΣΔI×g 累积负荷（剂量-反应），不携带"症状已持续多久"信息 | 转化接口 §二/§三.1 |
| 病程声明先例 | CYCLIC_MOOD_HISTORY（环性）= 病程模式存在性声明，≠ 时期计数，"防资格门现场计算病程" | 转化接口 §3.2.2 :211 |
| 时长声明先例（批次 2） | SYMPTOM_DURATION_6M（SSD）：≥6 月时长判定留 #87 声明侧（CYCLIC 配方同构）——✅ 用户照准（2026-09-06） | `资格核验批次2-全量解锁/SSD-收尾-裁决点.md` |

**引用约定**：DSM-5 标准条文为中文工作整理（非官方译本），关键英文短语保留原文；逐字准确性存疑处一律标 [需核验]。文献只给"支持/反对某命题的材料"，不因"有文献"即认定命题成立（G2：病因/关联文献不得单独证明资格必要性）。

---

## 一、DSM-5 / ICD-11 定位

### 1.1 命名与谱系定位

| # | 材料 | 来源 |
|:-:|------|------|
| N1 | DSM-IV 称 **Dysthymic Disorder（心境恶劣）**，与 MDD 为并列抑郁类障碍；另有 MDD 病程修饰语 "chronic"（当前发作 ≥2 年持续） | DSM-IV-TR（APA 2000）[逐字 [需核验]] |
| N2 | **DSM-5 更名 = 持续性抑郁障碍 PDD，并"合并"两类慢性抑郁**：PDD 由 DSM-IV 的 Dysthymia **与 DSM-IV 的慢性 MDD（chronic major depressive disorder）合并而来**——DSM-5 原文以 "consolidation" 描述（逐字 [需核验]，学界转述一致：Malhi et al. 2018 评论亦以此为对象） | DSM-5（APA 2013）PDD 章引言；[Malhi et al. 2018, *Can J Psychiatry*（Persistent Depression: Should Such a DSM-5 Diagnostic Category Persist?, DOI 10.1177/0706743718814429）](https://sage.cnpereading.com/doi/10.1177/0706743718814429) |
| N3 | 合并的直接后果：DSM-5 语境下"MDD 慢性化（发作连续 ≥2 年）"不再单独编码为 MDD-chronic，而落 PDD 的 **"with persistent major depressive episode"** specifier 之下（DSM-5 是否保留 MDD chronic specifier、如何逐字表述 [需核验]——这是 §三 反样本 1 与 §四 材料 5 的关键事实） | DSM-5（APA 2013）PDD specifier 表；Malhi et al. 2018 |
| N4 | PDD 诊断码 300.4（F34.1）；ICD-10-CM 映射 F34.1（与 ICD-11 的 6A72 对应，见 §1.4） | DSM-5（APA 2013）编码系统；[theravive PDD 页](https://www.theravive.com/therapedia/persistent-depressive-disorder-(dysthymia)-dsm--5-300.4-(f34.1)) [编码 [需核验]] |
| N5 | DSM-5-TR（APA 2022）：PDD 的 A-H 八条标准未实质改动 [需核验逐字对照]；本章新增**延长哀伤障碍（PGD）**入 Section II（2020 年 APA 大会批准），用于 §三 反样本 6 | DSM-5-TR（APA 2022）；[APA PsychNews 2020 批准报道](https://psychnews.psychiatryonline.org/doi/10.1176/appi.pn.2020.12b18) |

> 结构事实（供 §二/§四 引用）：DSM-5 的 PDD **不是** DSM-IV Dysthymia 的纯改名——它在**分类学上吞并了慢性 MDD**。因此"PDD 与 MDD 慢性化是两病"在 DSM-5 内部**不再成立**（慢性 MDD ⊆ PDD 谱系），而 ICD-11 保留了三分（单次/复发性抑郁障碍 vs 心境恶劣，见 §1.4）——两锚对"慢性 MDD 归属"给出不同边界，属用户裁决材料。

### 1.2 DSM-5 Section II — PDD（300.4 / F34.1）：门槛结构与 A-H 条

**来源**：DSM-5（APA 2013）Section II 抑郁障碍章 300.4 Persistent Depressive Disorder (Dysthymia)。标准条文已核对的复述见 [Pearson/BASC-3 官方标准摘录 PDF](https://images.pearsonclinical.com/images/assets/basc-3/basc3resources/DSM5_DiagnosticCriteria_PersistentDepressiveDisorder.pdf)、[theravive 300.4 条目](https://www.theravive.com/therapedia/persistent-depressive-disorder-(dysthymia)-dsm--5-300.4-(f34.1))；逐字以 DSM-5 印刷版为准 [需核验]。

| # | 标准主题（中文整理） | DSM-5 关键语义 | 项目关注点 |
|:-:|--------------------|-----------------|-----------|
| A | **慢性低落心境** | Depressed mood for **most of the day, for more days than not**, … for **at least 2 years**（主观报告或他人观察皆可）| 时程门槛（2 年）+ 频度门槛（多数日子）；**儿童青少年：可为易激惹（irritable）且时长 ≥1 年**（A 条 Note） |
| B | **伴随症状 ≥2/6**（While depressed 状态下存在）：①食欲差或过食 ②失眠或嗜睡 ③低能量或疲劳 ④低自尊 ⑤注意力不集中或难做决定 ⑥无望感 | Presence, while depressed, of **two (or more)** of the following… | **任务点名的"躯体症状条目（食欲/睡眠/精力/注意/无望 ≥2）"实为 B 条 6 项中的 5 项（1/2/3/5/6）+ 缺第 4 项低自尊**——B 条是躯体（1/2/3）+ 认知（4/5）+ 动机/认知（6）混合，非纯躯体条目；≥2/6 为 polythetic 计数门槛 |
| C | **病程连续性**：2 年（儿童 1 年）内**无任何连续 >2 个月**的无症状期（A+B 症状全缺即计为"无"） | never been without the symptoms in Criteria A and B for more than 2 months at a time | 慢性模式的"无长缓解"要件——与环性/发作性障碍的区分文本之一 |
| D | **MDE 叠加允许**：2 年期间可符合 MDD 发作标准；若 MDE 标准**连续满足满 2 年**，该状态被 PDD 吸收为 specifier（"with persistent major depressive episode"）而非独立 MDD-chronic | Criteria for a major depressive disorder may be continuously present for 2 years（逐字 [需核验]） | **"双重抑郁"的 DSM-5 载体**；§二 命题 B 与 §四 原子关系的关键条款 |
| E | **从未躁狂/轻躁狂**，且**从未满足环性心境障碍标准** | There has never been a manic episode or a hypomanic episode, and criteria have never been met for cyclothymic disorder | **PDD 排除条件锚**：与 BD-I/BD-II/环性 互斥（候选集内三病同现时分离依据；§三 反样本 2/3） |
| F | 不能用持续性分裂情感障碍、精神分裂症、妄想障碍或其他精神病性障碍更好解释 | not better explained by a persistent schizoaffective disorder, schizophrenia, … | 精神病谱系替代解释排除 |
| G | 非物质（滥用药物/药物）或躯体疾病（如甲状腺功能减退）的生理效应所致 | not attributable to the physiological effects of a substance … or another medical condition (e.g., hypothyroidism) | 物质/躯体所致低落排除（§三 反样本 4） |
| H | 临床显著痛苦或社会/职业等功能损害 | clinically significant distress or impairment | 损害性要件（与 MDD C 标准同构） |

> 结构事实（供 §二/§四 引用）：与 BPD 的 ≥5/9 polythetic 不同，PDD 的"达标门槛"形态 = **A（必然时长特征）+ B（≥2/6 polythetic 伴随症状）+ C（连续性）+ D/E（排除与叠加界）+ H（损害）**。A 对每个 PDD 个体**必然成立**（无 A 即无 PDD）；B 条是唯一 polythetic 计数点，且被 :213 禁止项覆盖（"≥2/6 组合判定"属 DSM 内部条件 → 归 #87 声明依据，不进资格门）。

### 1.3 DSM-5 PDD specifier 体系（材料，防把 PDD 读成单一病程形态）

| Specifier（中文整理） | DSM-5 语义要点 | 与原子候选的关系材料 |
|----------------------|---------------|---------------------|
| With pure dysthymic syndrome | 最近 ≥2 年未满足过完整 MDE 标准（纯恶劣心境期） | "PDD 无 MDE 史"合法形态的锚（§二 命题 B 反对面） |
| With persistent major depressive episode | 完整 MDE 标准**连续满足整个前 2 年** | DSM-5 语境下"MDD 慢性化"的正式落点（N3） |
| With intermittent major depressive episodes, **with/without** current episode | 2 年内曾叠加完整 MDE（发作-缓解），当前有/无发作 | "双重抑郁"的发作-缓解叠加形态（§二 命题 B 支持面） |
| 其余（With anxious distress / mixed features / melancholic / atypical / psychotic features / peripartum onset，自 MDD specifier 引入）+ Early/Late onset（<21 岁 / ≥21 岁） | 与 MDD specifier 共享 | 表征/共病域裁决参考，非资格核心 |

> 注记：specifier 逐字定义 [需核验]（DSM-5 specifier 段）。注意 **"with mixed features"** 亦列于 PDD 可加 specifier 之中——"混合特征"为**亚阈值**（未达轻躁狂/躁狂发作标准）时可加，与 E 条（从未完整躁狂/轻躁狂）并存不矛盾——材料，供 §三 反样本 5 使用。

### 1.4 ICD-11 定位（任务核验点：ICD-11 是否保留 PDD？）

**来源**：ICD-11（WHO，2019 发布 / 2022 生效 / 现行版），MMS 代码 + CDDG 临床描述。

| 项 | ICD-11 定位 | 备注 |
|----|------------|------|
| 心境恶劣对应实体 | **6A72 Dysthymic disorder——保留**，位于 **Depressive disorders（抑郁障碍）组**内 | [mrcpsych ICD-11 6A72 标准页](https://www.mrcpsych.uk/2022/05/icd-11criteria-for-dysthymic.html?m=0)、[findacode MMS 6A72](https://www.findacode.com/icd-11/code-810797047.html)；代码编号 [需核验] |
| 命名 | ICD-11 **未采用** DSM-5 的 "Persistent Depressive Disorder（持续性抑郁障碍）"称呼，继续用 **Dysthymic disorder（心境恶劣）** | 任务猜测"ICD-11 把心境恶劣并入 6A72 持续性心境障碍?"——**材料回应：ICD-11 MMS 无"持续性心境障碍"类名，6A72 本体名即 Dysthymic disorder**（"持续性/慢性"为描述语非类名）[需核验] |
| 与 DSM-5 的核心结构差异 | ICD-11 抑郁障碍为三分：**6A70 单次发作抑郁障碍 / 6A71 复发性抑郁障碍 / 6A72 心境恶劣障碍**——**未像 DSM-5 那样把慢性 MDD 并入心境恶劣**；持续 ≥2 年未缓解的发作在 ICD-11 归 6A70/6A71 而非 6A72 [需核验逐字] | 反样本 1（MDD 慢性化）在两锚下归属不同的直接原因 |
| 6A72 内容要点（CDDG 转述，逐字 [需核验]） | 持续 ≥2 年、多数日子大部分时间的低落心境 + ≥2 项伴随症状（食欲/睡眠/能量/自尊/注意/无望，与 DSM-5 B 条同源）；2 年内无 >2 个月无症状期；未同时满足抑郁发作标准（叠加发作的处理规则 [需核验]——是否同 DSM-5 允许叠加，是 ICD-11 与 DSM-5 的差异点） | 与 §1.2 对照：A/B/C 同源，**D（叠加/合并）与 specifier 体系为 DSM-5 独有结构** |
| 环性对照 | ICD-11 6A62 Cyclothymic disorder（双相及相关障碍组） | §三 反样本 3 |

> 跨锚差异材料（供裁决）：DSM-5 = "合并主义"（慢性 MDD ∪ Dysthymia = PDD，单类 + specifier 细分）；ICD-11 = "分离主义"（发作性抑郁与慢性心境恶劣并列三类）。项目疾病目录同时收录 MDD 与 PDD 两个独立条目（机制层各自建模，见 `实体/疾病目录/`），与**哪一锚**对齐决定"慢性 MDD 样本归 MDD 还是 PDD"的边界——**本文件不表态，只留两侧材料**（§三 反样本 1 / §四 材料 5）。

### 1.5 任务点名特征 → 条款映射表

| 任务/项目点名特征 | DSM-5 条款 | ICD-11 元素 | 备注 |
|------------------|-----------|------------|------|
| 慢性低落 ≥2 年（儿童 ≥1 年可易激惹） | A 条（含 Note） | 6A72 核心时长特征 | 时程/频度双门槛 |
| 期间无 ≥2 个月无症状 | C 条 | 6A72 同款（"无 >2 个月无症状期"） | 慢性连续性 |
| 躯体条目（食欲/睡眠/精力/注意/无望 ≥2） | B 条 6 项中 5 项（1/2/3/5/6）| 6A72 伴随症状 | 任务清单缺 B 条第 4 项"低自尊"——材料修正 |
| 未达 MDD 发作门槛期间 / 曾达但病程持续（双重抑郁） | D 条 + specifier（pure dysthymic / persistent MDE / intermittent MDE） | [叠加发作规则 [需核验]] | §二 命题 B 核心 |
| 从未躁狂/轻躁狂（与 BD 排除） | E 条 | 6A72 与双相障碍鉴别 | 排除条件锚（§三 2） |
| 高 N 慢性叙事（表征偏好） | 无 DSM 条款对应（记忆形态非诊断特征） | 同左 | §五 |

---

## 二、必要性分析输入（d⟹X 方向材料，不作结论）

> 归位原则方向：`P_i 是 d 的必要条件 ⟺ d⟹P_i`。本节只收集"支持/反对 PDD⟹X"的材料。**方向不可交换**：材料支持 d⟹X ≠ X⟹d（充分性见 §三 反样本）。

### 2.1 命题 A：PDD ⟹ 慢性低落病程（≥2 年模式）？

**支持材料（A⟹方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| A1 | PDD 诊断门槛的第一条即 A 条"2 年以上多数日子大部分时间低落"——**病程 ≥2 年（儿童 ≥1 年）是 PDD 的定义性必要特征**，无 A 即无 PDD | DSM-5（APA 2013）300.4 A 条 | 与 MDD"发作 ≥2 周"的时程量级差 ≈×50（§三 1 用） |
| A2 | C 条补足"慢性"的连续性语义：2 年内无 >2 个月无症状期——PDD 的"慢性" = 持续存在 + 无长缓解，而非单纯"总时长够长" | DSM-5（APA 2013）300.4 C 条 | 模式声明须含"无长缓解"语义候选（§四） |
| A3 | 纵向自然病程研究：恶劣心境/双重抑郁 10 年随访显示慢性化与叠加发作的高发（恢复延迟、复发常见；具体率值写作时未核验原文，不列数字） | [Klein DN, Shankman SA & Rose S 2006, *Am J Psychiatry* 163(5):872-880（PMID 16648329）](https://pubmed.ncbi.nlm.nih.gov/16648329/) | 病程证据支撑"慢性模式是 PDD 的核心承载物"（非资格阈值） |
| A4 | 项目机制层已把 PDD 定为"慢性持续型（无急性跳变）"，与 MDD 的"急性阈值跳变"相区分——项目内对"PDD = 慢性"与 DSM 对齐 | `实体/疾病目录/持续性抑郁障碍.md` :48 | 项目内一致材料（非外部独立证据） |

**反对/限定材料（¬A 或 A 弱化方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| A5 | A 条时长门槛对**儿童青少年仅 1 年**且可仅"易激惹"——"≥2 年"非全年龄普适 | DSM-5（APA 2013）300.4 A 条 Note | 若做原子语义，时程量词须区分成人（≥2 年）与儿童（≥1 年）（项目 NPC 生命周期是否涉及未成年 [需核验]） |
| A6 | A 条的频度语义是"多数日子、一天中大部分时间"（most of the day, more days than not）——**非"每一天每一时刻"**；主观报告与观察皆可 | DSM-5（APA 2013）300.4 A 条 | 声明表述若用"持续低落"须匹配 DSM 的"多数日子"量词（数学语言规范提醒） |
| A7 | specifier 体系说明"慢性"形态有内部变体（pure dysthymic / persistent MDE / intermittent MDE）——"≥2 年慢性模式"之上还叠加发作性形态差异（§1.3） | DSM-5（APA 2013）300.4 specifier 段 | "PDD⟹慢性"为真，但"慢性模式 + 发作史"共存的样本同样合法（§四 材料 4/5） |
| A8 | 慢性低落（2 年）本身跨诊断：慢性化 MDD、BD 慢性抑郁相、环性波动等均可呈现长期低落样态（虽然都不满足 PDD 全门槛）——**慢性低落 ≠ PDD**（充分性侧，见 §三） | DSM-5（APA 2013）各障碍标准 | 形式逻辑：命题 A 只说 d⟹慢性，不断言慢性⟹d |

### 2.2 命题 B：PDD ⟹ 曾有 MDD 发作？（"双重抑郁"必要性检验）

**支持材料（B⟹方向——"PDD 常伴 MDE"的临床材料）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| B1 | **"Double depression"（双重抑郁）概念**：Keller & Shapiro 命名"急性抑郁发作叠加于慢性抑郁障碍之上"现象，并报告叠加者病程更差（更长/更难缓解的指数发作） | [Keller MB & Shapiro RW 1982, *Am J Psychiatry* 139(4):438-442](https://pubmed.ncbi.nlm.nih.gov/7065289/) | 术语源头文献；叠加为**常见形态**（常见性数字 [需核验]） |
| B2 | DSM-5 D 条 + specifier 明确承认：PDD 病程中**可以**（may）持续/间歇出现完整 MDE（intermittent / persistent MDE specifier）——双重抑郁是 PDD 的**合法子形态** | DSM-5（APA 2013）300.4 D 条 + specifier | 支持"PDD∧MDE"组合在 DSM 语义内非矛盾 |
| B3 | 纵向随访：恶劣心境样本中大部分个体在病程中叠加 MDE（double depression 常见；比例值 [需核验]） | Klein et al. 2006（AJP）；Klein DN 相关综述（篇目/数值 [需核验]） | 流行病学材料（G2：不得单独证明必要性） |
| B4 | 项目侧：PDD 重档（CGI 6）= "双重抑郁叠加"并临时启用 MDD 跳变表——项目机制层已有"叠加"概念预留 [待 #88 定案] | `实体/疾病目录/持续性抑郁障碍.md` :48；persistent-depressive-pilot §五.2 | 项目内"叠加形态"先例（非资格材料，机制层） |

**反对/限定材料（¬B 方向——"MDE 史非 PDD 必要"）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| B5 | **"With pure dysthymic syndrome" specifier = 近 2 年从未满足完整 MDE 标准**——DSM-5 承认终身可能从未发作的纯恶劣心境 PDD 合法存在 | DSM-5（APA 2013）300.4 specifier 段 | "曾有 MDE"非 PDD 必要（任务点名要收集的核心反对材料 ✓） |
| B6 | DSM-IV 时代的对应规则：纯 Dysthymia 诊断**要求前 2 年（儿童 1 年）内无 MDE**（更早既往发作仅在其起病前已完全缓解 ≥2 个月的前提下允许）；DSM-5 放宽为 specifier 体系——即便在最宽松的 DSM-5 语义下，"无 MDE 史"仍是合法 PDD | DSM-IV-TR（APA 2000）300.4 D 条（含 Note）；DSM-5（APA 2013）300.4 | 反向对照：纯心境恶劣是**基础形态**，叠加是**常见但非必然**变体 |
| B7 | 若"PDD⟹曾有 MDE"成立，则 B5 的 pure dysthymic syndrome specifier 与 B6 的纯 Dysthymia 类目均无对象——与 DSM 两代文本矛盾 | 形式逻辑推演（基于 B5/B6） | 直接反证 B 命题的形式材料 |
| B8 | 项目先例同构：BD-II 与 MDD 共享 DEPRESSIVE_EPISODE_HISTORY 必要正向是**分别核验**的（Q2-11）——PDD 是否以 DEPRESSIVE 原子为必要/组合成分，不得因"同谱系"自动继承 | 决策树 :4094（Q2-11） | 疾病级逻辑不可自动继承（任务纪律点） |

> 综合材料（供裁决参考，非结论）：命题 A（PDD⟹慢性病程模式）在 DSM-5 中有定义级支撑（A/C 条）；命题 B（PDD⟹曾有 MDE）**有强反对面**——MDE 史对 PDD 是"合法叠加形态"而非"每例必备"。"慢性模式声明"若做成原子，其必要正向语义落在 **A+C 的病程模式存在性**；DEPRESSIVE_EPISODE_HISTORY 对 PDD 的归位（必要/非必要/组合成员）属用户裁决（§四）。

---

## 三、反样本收集（慢性低落但非 PDD）

> 反样本纪律（沿用 PTSD-F 前车之鉴）：任何资格规则候选必须能在不误放下列样本的前提下成立。每行给出"表面相似特征 / 为什么不是 PDD / DSM 锚 / 拦截要点"材料。

### 3.1 发作性/慢性化抑郁 反样本

| 反样本 | 表面相似（PDD 类） | 为什么不是 PDD（区分锚） | 来源 | 对"慢性模式资格原子"的拦截要点 |
|--------|-------------------|------------------------|------|------------------------------|
| **MDD 发作-缓解型**（recurrent/episodic） | 低落、快感缺失、反刍——与 PDD 同谱系同标签（项目两病默认标签均为「反刍+过度抑制」） | MDD = **发作 ≥2 周**、发作-缓解时相结构，缓解期可完全无症状；PDD = **≥2 年多数日子低落、无 >2 个月无症状期**（A/C 条）；DSM-5 鉴别段以时程与缓解性区分 | DSM-5（APA 2013）MDD A 条 vs 300.4 A/C 条；`实体/疾病目录/重度抑郁症.md`（发作期建模） | 有 DEPRESSIVE_EPISODE_HISTORY（发作史声明）≠ 慢性模式；发作史原子不得充当 PDD 资格（§四 材料 4 反对面） |
| **MDD 慢性化（单一 MDE 连续 ≥2 年）** | 持续低落 ≥2 年——表面与 PDD A 条无差别 | **DSM-5：该形态已被 PDD 吸收**（= PDD "with persistent major depressive episode" specifier，N3）——在 DSM-5 语义下它不是"非 PDD 的慢性 MDD"；**ICD-11：仍归 6A70/6A71**（未吸收）——同一临床形态两锚归属不同 | DSM-5（APA 2013）N3；ICD-11（WHO）§1.4；Malhi et al. 2018（质疑合并合理性） | 跨锚差异属用户裁决区：项目若取 ICD-11 语义，"慢性化 MDD"是反样本；若取 DSM-5 语义则样本本身即 PDD 形态——**两锚材料并列，不表态** |
| **BD-I/II 抑郁相（含慢性抑郁相）** | 抑郁相呈现长期低落 | BD = 有（轻）躁狂史；PDD **E 条排除任何躁狂/轻躁狂史**；且 BD 为发作周期结构（抑郁相可缓解）；项目已有 MANIA_HISTORY / HYPOMANIA_HISTORY 原子先例 | DSM-5（APA 2013）300.4 E 条 + BD 标准；转化接口 §3.2.2 :209-210 | MANIA/HYPOMANIA 声明 = PDD 排除条件候选（§四 材料 3）；同候选集内 BD 与 PDD 的分离即靠此 |
| **环性心境障碍** | 长期心境不稳、抑郁样波动、低落时段（项目与 PDD 同属 丧失/哀悼 候选集） | 环性 = **亚阈值两相波动**（轻躁狂样 + 抑郁样时段），抑郁样时段不达 PDD 的持续低落语义；PDD **E 条显式排除"曾满足环性标准"**（两病互斥）；DSM-5 鉴别段：环性心境不稳 vs PDD 持续低落 [逐字 [需核验]] | DSM-5（APA 2013）300.4 E 条 + 环性标准；转化接口 :211 CYCLIC_MOOD_HISTORY；`实体/疾病目录/持续性心境障碍.md` | 项目 CYCLIC_MOOD_HISTORY（亚阈值波动病程声明）若 =1 → PDD 排除候选；"波动"≠"持续低落"是区分核心（PDD 原子语义须落在"持续/多数日子"而非"反复波动"——与 CYCLIC 镜像对称） |
| **BD "with mixed features" specifier 状态** | 抑郁样状态下有躁狂样表现（激越/易激惹/联想奔逸） | specifier 的混合特征是**亚阈值**（未达完整轻躁狂/躁狂）；一旦曾有完整（轻）躁狂/轻躁狂发作 → BD，PDD E 条排除；反之若从未有完整发作，混合特征可加于 MDD/PDD specifier（§1.3 注） | DSM-5（APA 2013）"with mixed features" specifier + 300.4 E 条 | 拦截靠"完整发作史"（MANIA/HYPOMANIA 原子三值），不靠症状样态——混合特征表现本身不区分 PDD/BD |

### 3.2 物质/躯体所致 与 哀伤 反样本

| 反样本 | 表面相似（PDD 类） | 为什么不是 PDD（区分锚） | 来源 | 拦截要点 |
|--------|-------------------|------------------------|------|---------|
| 物质/药物所致抑郁障碍（substance/medication-induced depressive disorder） | 长期低落、乏力、睡眠食欲紊乱 | PDD **G 条排除**"物质生理效应所致"；独立诊断 = substance-induced depressive disorder（可慢性，只要物质使用持续）；项目 SUD 轨道已有 SUBSTANCE_USE_HISTORY 原子（≠"物质所致低落"声明） | DSM-5（APA 2013）300.4 G 条 + 物质所致抑郁障碍 | 排除条件锚：物质所致低落须由 #87 替代解释声明拦截（声明侧纪律，同 BPD/SSD 批次） |
| 躯体疾病所致抑郁障碍（如甲状腺功能减退） | 低能量/低落/注意差——与 PDD B 条表面重叠 | PDD **G 条排除**"躯体疾病生理效应所致"；独立诊断 = depressive disorder due to another medical condition（病程随躯体病走） | DSM-5（APA 2013）300.4 G 条 + 躯体疾病所致抑郁障碍 | 同上：替代解释声明（生理/疾病事件类型候选集只召回 {躯体症状主, 惊恐, MDD}——**不含 PDD**，§3.2.1 映射表本身已拦截 [材料]） |
| **正常哀伤（bereavement/grief）** | 丧失后持续低落（触发 PDD 的事件类型即 丧失/哀悼） | DSM-5 MDD 鉴别段：哀伤以对逝者的**思念/缺憾**为核心、痛苦随情境波动（"waves"）、自尊通常保留；PDD 为**泛化持续低落**、无对象性思念结构；MDD/PDD 均要求症状达障碍门槛（PDD 另有 2 年病程）——**哀伤本身非障碍** | DSM-5（APA 2013）MDD 鉴别段（grief vs MDE）；DSM-5-TR（APA 2022） | 丧失事件召回 → PDD 需"病程模式声明"支撑；单纯丧失/哀伤叙事不得放行 PDD |
| **延长哀伤障碍 PGD**（DSM-5-TR 新增 2022；ICD-11 6B42） | 丧失后 ≥1 年持续低落、功能受损——与 PDD 的 2 年慢性低落表面重叠 | PGD = 针对**特定逝者**的持续性哀伤反应（思念/渴望/ preoccupation 为核心，成人 >12 个月、儿童青少年 >6 个月），**非泛化抑郁模式**；PDD 无对象性要件；两病可共病但资格语义分离 [逐字标准 [需核验]] | [DSM-5-TR PGD 标准（Prigerson et al. JAMA Psychiatry 2021 评述](https://jamanetwork.com/journals/jamapsychiatry/fullarticle/2788766)）；[World Psychiatry 2022 PGD 综述（DOI 10.1002/wps.21228）](https://onlinelibrary.wiley.com/doi/10.1002/wps.21228)；ICD-11 6B42 | 高危险反样本：**丧失/哀悼 事件类型召回 PDD 的最高频误放路径**——PGD 有独立障碍门槛与 12 个月规则；"哀伤持续 + 低落"样本须能分离（对象性哀伤 vs 泛化低落）|
| 人格障碍（BPD 慢性空虚/烦躁；分裂型等） | 慢性不快、空虚、无望感（与 PDD B 条第 4/6 项表面重叠） | BPD = 人格模式（人际/情绪/冲动/身份域），其烦躁为**应激反应性小时尺度**（批次 1 已核验）；PDD 无跨情境人格模式要件；DSM-5 鉴别：PDD 与人格障碍可共病、按主诉区分 | DSM-5（APA 2013）BPD Criterion 6 时程括号；[BPD 核验证据收集（批次 1）](../资格核验批次1-性创伤通道/BPD-核验-证据收集.md) | 慢性不快不指向 PDD 唯一（跨诊断）；候选集层面 BPD 由事件类型门（性创伤/社会伤害/忽视遗弃）召回，与 丧失/哀悼 召回不重叠 [材料] |

### 3.3 反样本 → 拦截方向汇总（材料层，非规则）

| 反样本组 | 若 PDD 资格由"X"承载，会误放的风险 | 材料提示的分离方向 |
|---------|----------------------------------|-------------------|
| 发作-缓解型 MDD | 仅凭"低落/反刍/有抑郁史"放行 | 需**病程模式声明**（2 年连续/无 >2 月缓解）而非单次发作史 |
| 慢性化 MDD（DSM-5 语境） | "MDD 慢性化"样本在 DSM-5 已是 PDD persistent-MDE 形态——是否/如何成为双 ELIGIBLE | 两锚（DSM-5 合并主义 vs ICD-11 分离主义）材料并列，裁决区 |
| BD-I/II（含混合特征） | 长期抑郁相样本凭低落放行 | MANIA/HYPOMANIA 声明排除（E 条）；完整发作史 vs 亚阈值混合特征分离 |
| 环性心境 | 长期心境波动样本凭低落放行 | CYCLIC 声明排除（E 条）；"反复波动" vs "持续低落"语义分离 |
| 物质/躯体所致 | 慢性低落凭表现放行 | G 条替代解释声明拦截（SUBSTANCE_USE / 躯体疾病所致 声明侧纪律） |
| 哀伤/PGD | **丧失/哀悼 召回下凭"长期低落"放行** | PGD 独立障碍 + 12 个月规则 + 对象性哀伤 vs 泛化低落分离（§3.2 末两行） |

---

## 四、"病程模式声明"型原子候选材料（PDD_PERSISTENT_DEPRESSION_PATTERN + DEPRESSIVE_EPISODE_HISTORY 关系）

### 4.1 先例语义回放（引用即读取铁律）

| 项 | 内容 | 出处 |
|----|------|------|
| 原子 1 | CYCLIC_MOOD_HISTORY = "已声明的反复亚阈值心境波动**病程模式存在性**（≠ 时期计数，防资格门现场计算病程）"；环性必要正向候选；配方要点：①模式存在性声明（#87 A′ 字段）②病程计算留声明侧 ③存在性而非计数/频率 | 转化接口 §3.2.2 :211；决策树 :4095（Q2-12） |
| 原子 2 | SYMPTOM_DURATION_6M（SSD）= "已声明的症状持续 ≥6 月事实（病程判定留声明侧）"——**时长型声明原子在批次 2 已获用户照准**（CYCLIC 配方同构） | `资格核验批次2-全量解锁/SSD-收尾-裁决点.md` 〇.3 + 第 4 步 |
| 原子 3 | DEPRESSIVE_EPISODE_HISTORY = "当前或既往已声明的重性抑郁发作存在性"；MDD 必要正向、BD-II 必要正向（**分别核验**） | 转化接口 §3.2.2 :207；决策树 :4094/4095 |
| 红线 | 禁止：L_agg→原子；创伤事件→原子；症状计数→原子；**DSM 内部症状/时长条件→Eligibility 原子**（归 #87 声明依据） | 转化接口 §3.2.2 :213 |

> PDD 若走同构原子，需回答的候选材料问题（仅收集，不裁决）：①"≥2 年持续低落病程"由 DSM 的 A+C 承载，其存在性声明如何与 CYCLIC/SSD 同构落到 #87 A′ 字段；②时长语义（2 年/儿童 1 年/无 >2 月缓解）全部留声明侧；③DEPRESSIVE_EPISODE_HISTORY 与新模式原子的组合关系（AND/OR/独立）如何由 DSM D 条 + specifier 支撑（§4.3）。

### 4.2 候选原子材料：PDD_PERSISTENT_DEPRESSION_PATTERN

| 项 | 内容 |
|----|------|
| 候选语义（任务提议，供裁决） | **PDD_PERSISTENT_DEPRESSION_PATTERN** = "已声明的 **≥2 年持续低落病程模式存在性**——病程判定留 #87 声明侧"（CYCLIC 配方同构） |
| DSM 素材支撑 | A 条（≥2 年多数日子低落，儿童 ≥1 年可易激惹）+ C 条（无 >2 个月无症状期）——慢性模式 = A+C 的声明承载；B 条（≥2/6 伴随条目）为 DSM 内部计数 → 归 #87 声明依据（:213 禁止项），不进资格门 |
| DSM 素材反对/限定 | ①"多数日子、一天大部分时间"非"每天每刻"（A5/A6）——声明语义量词须匹配；②儿童青少年 1 年门槛（A5）——若项目含未成年 NPC 需双时程；③模式声明与 specifier 的关系：pure dysthymic / persistent MDE / intermittent MDE 是模式内部的**形态变体**，模式声明本身是否须携带形态信息（如"叠加发作存在性"）属 #87 声明 schema 设计问题，本文件不表态 |
| 工程可行性的项目内材料 | E_d^hist 来源 = #87 A′-Generator 规范化声明字段（:175），转化接口不解析叙事；记忆层 t_anchor 为点时刻粒度（3 时段×日）、L 无病程语义（§〇）——**"≥2 年"无法由快照/L 现场计算，只能由 #87 声明**（CYCLIC :211 + SSD SYMPTOM_DURATION_6M 双先例直接适用） |

### 4.3 DEPRESSIVE_EPISODE_HISTORY 与 PDD 模式声明的关系材料（不裁决 AND/OR）

| # | 材料 | 方向 | 来源 |
|:-:|------|:---:|------|
| D1 | **非 AND（不要求发作史）**：pure dysthymic syndrome specifier 承认无完整 MDE 的 PDD（B5/B6）——DEPRESSIVE_EPISODE_HISTORY=0 与 PDD 并存合法；模式声明独立成立时 PDD 资格不应依赖发作史原子 | ¬AND | DSM-5（APA 2013）300.4 specifier 段 |
| D2 | **非 OR（发作史不替代模式）**：发作-缓解型 MDD 有 DEPRESSIVE_EPISODE_HISTORY=1 但无 ≥2 年连续模式（§3.1 反样本 1）——发作史存在性逻辑上**推不出**慢性模式；两原子语义域不同（发作存在性 vs 病程模式存在性） | ¬OR | DSM-5（APA 2013）MDD vs 300.4；形式推演 |
| D3 | **AND 共存合法（双重抑郁）**：D 条 + intermittent/persistent MDE specifier = 发作叠加于慢性背景之上——DEPRESSIVE=1 ∧ PDD 模式=1 的样本在 DSM 语义内为 PDD（+叠加发作） | 组合合法 | DSM-5（APA 2013）300.4 D 条 + specifier；Keller & Shapiro 1982；Klein et al. 2006 |
| D4 | **共享原子的疾病级分别核验**：DEPRESSIVE_EPISODE_HISTORY 已对 MDD/BD-II 分别证明归位；PDD 若复用须独立走五步（不能因"MDD 必要正向"自动继承） | 纪律 | 决策树 :4094（Q2-11） |
| D5 | **MDD 侧资格与 PDD 侧资格正交后的编码差异材料**：若样本满足"单一 MDE 连续 ≥2 年"（DSM-5 = PDD persistent-MDE specifier 形态，N3），在项目双病模型下它同时满足 DEPRESSIVE=1 与 PDD 模式=1 → MDD 与 PDD 双 ELIGIBLE（双病并存/叠加表达）；而 DSM-5 编码惯例倾向单记 PDD（chronic MDE 不单独记 MDD-chronic）——**"双 ELIGIBLE 是否即双诊断"与"项目是否模拟 DSM-5 的编码惯例（单记 PDD）"为呈现层/裁决区，非证据层可闭合**；ICD-11 语义下同一样本归 6A70/6A71 而非 6A72——两锚差异再次显现 | 边界材料 | DSM-5（APA 2013）；ICD-11（WHO）；Malhi et al. 2018 |
| D6 | 排除原子候选（模式声明的反向护栏）：MANIA_HISTORY / HYPOMANIA_HISTORY（E 条，从未躁狂/轻躁狂）与 CYCLIC_MOOD_HISTORY（E 条，从未满足环性标准）——若任一 =1 → PDD 排除候选（材料提示：E 条是 PDD 与同候选集 BD-I/BD-II/环性 分离的 DSM 直接锚；是否落为排除原子 N_j = 用户裁决） | 排除侧材料 | DSM-5（APA 2013）300.4 E 条 |

> 综合（供裁决，非结论）：DSM 素材指向 **"发作史原子对 PDD 既非必要（D1）也非充分（D2），但可合法共存（D3）"**——若做组合，方向更像"模式声明独立必要正向 + 发作史原子由 MDD 侧资格门自行消费 +（可选）E 条排除原子"，而非两原子的 AND/OR 合并。**此排列只是对 DSM 材料的归纳，不构成规则草案。**

---

## 五、表征域材料（E_d^mem 侧，高 N 慢性叙事能否资格化）

### 5.1 项目内现有锚（已 Read 确认）

| 锚 | 内容 | 出处 |
|----|------|------|
| 表征偏好 PDD | (N, F, D_seg) = (0.95, 0.10, 0.05)——"慢性叙事"（24 经历型表中 N 最高一行） | 转化接口 §3.2.3 :275 |
| 表征偏好 MDD | (0.90, 0.20, 0.05)——"反刍 VAM 主导" | 转化接口 §3.2.3 :274 |
| 通道初判 | PDD 列 **A 临床史病（E_d^hist 主导）**——工作地图不把 PDD 放在表征通道 | [grilling-113 工作地图](../../grilling-113-disease-eligibility/grilling-113-disease-eligibility.md) :111 |
| 三维分离先例 | PTSD vs DID 距离 ≈0.852 → "三维分离生效"；**偏好表为 [NEW 初值待文献复核]** | 转化接口 §3.2.3 :249/:277 |
| 表征理论锚 | N = 叙事化（VAM，Brewin 1996）；F = 碎片化（SAM；R 由 F 派生，Ehlers & Clark 2000）；D_seg = 区隔化（#90） | 转化接口 §3.2.3 |
| 批次 1 修正先例 | BPD 原判 C 混合 → 核验修正为 **A 临床史主导**（无典型记忆签名 + OGM 方向，同 SSD 先例）——表征域不足资格化的修正路线 | 转化接口 §3.2.2 :234 批次 1 表；BPD 核验证据收集 §五 |

### 5.2 命题 C：PDD 能否靠纯表征（高 N）资格化？——支持面材料

| # | 材料 | 来源 |
|:-:|------|------|
| C1 | PDD 表征偏好为全表最高 N（0.95，"慢性叙事"）——抑郁谱系记忆以 VAM 叙事化/反刍为主导形态，N 维度可作 A 混合通道的**组成成分**材料（非阈值） | 转化接口 §3.2.3 :275 |
| C2 | 记忆内容层：高 N 叙事承载"慢性叙事"的内容痕迹（长期自我贬抑/无望的连贯叙事），理论上可成为 #87 声明侧判"长期负面自我叙事"的素材 | 转化接口 §3.2.3；#90 记忆内容层 [对应段 [需核验]] |
| C3 | PDD 病程长（≥2 年）→ 相关记忆更可能已被叙事整合（时间距离长、多次复述）——高 N 与慢性病程有**时间性关联**的假设材料（关联性 ≠ 必要资格，G2） | 记忆巩固理论（VAM 整合，Brewin 1996）；[假设性材料] |

### 5.3 命题 C 反对/限定面材料（纯表征资格化的结构性障碍——验证材料）

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| C4 | DSM-5/ICD-11 的 PDD 诊断特征全部为**临床史/症状/病程级**（A-H 条，§1.2），**无一条**基于记忆表征形态（N/F/D_seg）——高 N 叙事不出现在任何 PDD 标准中（同 BPD 核验 C4 论证结构） | DSM-5（APA 2013）；ICD-11（WHO） | 纯表征门缺 DSM 语义锚（G2） |
| C5 | **PDD 与 MDD 在偏好空间几乎相邻**：PDD (0.95,0.10,0.05) vs MDD (0.90,0.20,0.05) 欧氏距离 ≈ √(0.0025+0.01+0) ≈ **0.112**——比 PTSD-vs-DID 的 0.852 小一个量级；且两病**同现于 丧失/哀悼 候选集**（主病选择用 sim）——表征域（尤其 N）无法分离 PDD 与 MDD（材料：偏好值为 [NEW 初值待文献复核]，其上的一切距离计算同为暂定材料，非资格阈值） | 转化接口 §3.2.3 :274-275/:277 数据 + 本项目内算术（材料层） | "高 N 慢性叙事 vs MDD 反刍"的表征差异（ΔN=0.05/ΔF=0.10）远小于临床差异（时程 ×50）——诊断信息主要不在表征 |
| C6 | DSM 区分 PDD 与 MDD 的语义落在**病程时程**（≥2 年 vs ≥2 周发作）与**缓解性**（C 条）——这些是 E_d^hist/声明侧事实，不是记忆形态差异；表征（N/F/D_seg）是快照级、无时间维（§〇 t_anchor/L 材料） | DSM-5（APA 2013）；转化接口 §3.0/§3.2.3 | 表征域信息不变量上无法承载 ≥2 年语义 |
| C7 | 记忆特异性文献：自传记忆**过度概括化（OGM）**为抑郁谱系共性（含慢性抑郁）——尚无 PDD 特异的记忆形态签名 [PDD/心境恶劣 OGM 专项研究篇目 [需核验]]；OGM 与"高 N 叙事完整"方向相反（泛化记忆 ≠ 叙事化），如用 OGM 作 PDD 表征反而指向低特异 | [Williams JMG et al. 2007, *Psychol Bull* 133(1):122-148（抑郁 OGM meta）](https://doi.org/10.1037/0033-2909.133.1.122)（PDD 特异性 [需核验]） | 表征域无 PDD 独有签名（材料） |
| C8 | 通道初判 + 批次 1 修正路线：PDD 属 **A 临床史通道**（工作地图），且 BPD（同为"情绪性障碍表象"）已在批次 1 从 C/B 修正到 A 主导——先例提示临床史/病程声明是此类"慢性情绪病"的资格载体，表征仅作成分 | grilling-113 工作地图 :111；转化接口 §3.2.2 :234；批次 1 证据收集 | 结构性提示，不裁决 |
| C9 | 高 N 慢性叙事的内容本身跨诊断：慢性逆境/人格特质/文化性长期低落叙事均可呈"慢性叙事"形态（无 DSM 障碍对应）——叙事形态不等于病理事实（Narrative ⇏ Clinical fact，Q2-2 同构警戒） | 决策树 :4085（Q2-2） | 表征声明须先经 #87 人机协同规范化才成 E_d^hist 事实（转化接口 :175） |

### 5.4 PDD 特征 → 证据域候选对应初判表（归位材料）

| PDD 特征 | 是否有 E_d^mem 侧证据材料 | 是否主要在 E_d^hist 侧 | 材料提示 |
|---------|--------------------------|----------------------|---------|
| ≥2 年慢性低落（A/C） | ❌（快照级表征无时间维） | ✅ | "病程模式声明"候选（§4.2） |
| ≥2/6 伴随症状（B，躯体+认知） | 部分（反刍/内感受相关，e04-e06/e10 机制层） | ✅（症状存在性归 #87 声明侧） | :213 禁止症状计数→原子 |
| 从未躁狂/轻躁狂/环性（E） | ❌ | ✅（MANIA/HYPOMANIA/CYCLIC 声明） | 排除原子候选（D6） |
| 双重抑郁叠加（D/specifier） | ❌ | ✅（DEPRESSIVE_EPISODE_HISTORY 共享消费） | §4.3 D1-D5 |
| 高 N 慢性叙事（表征偏好） | ✅（0.95，全表最高 N） | — | 表征域与 MDD 相邻不可分离（C5）——只宜作成分不作资格主载体 |

---

## 六、待核验清单与移交

### 6.1 [需核验] 汇总（写作时未能在本项目核对原文/文献的项）

| # | 项 | 类型 | 建议核验源 |
|:-:|----|------|-----------|
| V1 | DSM-5 PDD 标准 A-H 逐字英文与中文译本（本文为中文工作整理）；300.4/F34.1 编码 | 原文核对 | DSM-5（APA 2013）印刷版/授权译本（如 [Pearson BASC-3 摘录 PDF](https://images.pearsonclinical.com/images/assets/basc-3/basc3resources/DSM5_DiagnosticCriteria_PersistentDepressiveDisorder.pdf)） |
| V2 | DSM-5 PDD D 条逐字（MDE may be continuously present…）与"consolidation of chronic MDD and dysthymia"原文；MDD 是否保留 chronic specifier | 原文核对 | DSM-5（APA 2013）300.4 + MDD 章 |
| V3 | DSM-5 PDD specifier 四式（pure dysthymic / persistent MDE / intermittent with/without current episode）逐字定义；"with mixed features"是否可加于 PDD | 原文核对 | DSM-5（APA 2013）300.4 specifier 段 |
| V4 | ICD-11 6A72 名称与内容逐字（是否允许叠加发作、有无"未满足抑郁发作标准"条款）；6A70/6A71 是否吸收 ≥2 年发作；代码编号复核 | 原文核对 | WHO ICD-11 MMS/CDDG（icd.who.int）；[mrcpsych 6A72 页](https://www.mrcpsych.uk/2022/05/icd-11criteria-for-dysthymic.html?m=0) |
| V5 | Klein et al. 2006（AJP 163(5):872-880）恢复率/叠加率等数值；相关纵向随访数值（Klein 系列） | 数值 | AJP 原文（PMID 16648329）；相关综述 |
| V6 | 双重抑郁在恶劣心境样本中的比例/终身发生率（Keller & Shapiro 1982 及后续） | 数值 | 原文/系统性综述 |
| V7 | PDD 流行病学（12 个月/终身患病率、早发 vs 晚发占比） | 数值 | DSM-5 流行病学段 / NESARC 等 |
| V8 | Malhi et al. 2018（*Can J Psychiatry*, DOI 10.1177/0706743718814429）作者全名、卷期与论点细节（质疑 DSM-5 合并的依据） | 文献著录 | 原文 |
| V9 | DSM-5-TR：PDD 标准是否零改动；PGD 标准逐字（成人 12 个月/儿童青少年 6 个月）与 ICD-11 6B42 对照 | 原文核对 | DSM-5-TR（APA 2022）；WHO ICD-11 |
| V10 | PDD/心境恶劣的自传记忆研究（OGM 等）是否无特异签名（除 C7 Williams 2007 之外的专项篇目） | 文献著录 | PubMed 检索 |
| V11 | DSM-5 PDD 与环性/BD 的鉴别段逐字（§3.1 行引用处） | 原文核对 | DSM-5 Differential Diagnosis 节 |
| V12 | 项目侧：NPC 生命周期是否含未成年（决定"儿童 ≥1 年可易激惹"是否相关）；#90 记忆内容层是否有未来拟加的时长字段 | 项目核对 | NPC 生成器文档 / #90 文档 |
| V13 | 本批次输出目录说明：任务指定输出至 `资格核验批次2/`，批次 2 其余产出（总览/SSD）位于 `资格核验批次2-全量解锁/`——**目录命名待主代理合并时统一** | 项目组织 | 批次 2 总览 |

### 6.2 移交说明

- 本文件为**证据收集层**产物：§一（定位，含 ICD-11 保留问题初步核验）、§二（必要性输入）、§三（反样本）、§四（原子候选材料）、§五（表征域材料）全部为素材，供用户裁决：①PDD_PERSISTENT_DEPRESSION_PATTERN 是否做成原子及其语义量词（成人 ≥2 年/儿童 ≥1 年/无 >2 月缓解 如何承载）；②DEPRESSIVE_EPISODE_HISTORY 对 PDD 的归位（D1-D3 材料：非必要、非充分、可共存）；③E 条三排除原子（MANIA/HYPOMANIA/CYCLIC）是否落为 PDD 排除条件；④两锚（DSM-5 合并主义 vs ICD-11 分离主义）取哪一语义锚处理"慢性化 MDD"边界样本；⑤表征域只作成分还是完全 A 通道。
- 移交的下一动作（由用户/主代理裁决后执行）：五步核验"结果层"（必要/排除归位表、签名结构、数值、判定函数）与 Step 4 写入（转化接口 §3.2.2 签名表追加、term_registry 入库、归位表更新）——**均不在本文件范围**。
- 本批次并行产出：批次 2 各族证据收集（SSD 已裁决；G1 进食族 / G2 焦虑谱 / G3 SZ 谱 / G5 ASPD / G6 拖延 并行运行中，见 [批次 2 总览](../资格核验批次2-全量解锁/总览.md)）。

---

*创建: 2026-09-06 | 更新: 2026-09-06 | 状态: 证据收集完成（待用户裁决）*
*关联: [批次 2 总览](../资格核验批次2-全量解锁/总览.md), [批次 1 总览](../资格核验批次1-性创伤通道/总览.md), [SSD 收尾裁决点](../资格核验批次2-全量解锁/SSD-收尾-裁决点.md), [转化接口 §3.2.2/§3.2.3](../../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%88%9B%E4%BC%A4%E8%AE%B0%E5%BF%86%E8%BD%AC%E5%8C%96%E6%8E%A5%E5%8F%A3.md), [持续性抑郁障碍](../../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E6%8C%81%E7%BB%AD%E6%80%A7%E6%8A%91%E9%83%81%E9%9A%9C%E7%A2%8D.md), [重度抑郁症](../../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E9%87%8D%E5%BA%A6%E6%8A%91%E9%83%81%E7%97%87.md), [持续性心境障碍（环性）](../../../../%E5%AE%9E%E4%BD%93/%E7%96%BE%E7%97%85%E7%9B%AE%E5%BD%95/%E6%8C%81%E7%BB%AD%E6%80%A7%E5%BF%83%E5%A2%83%E9%9A%9C%E7%A2%8D.md), [grilling-113 决策记录](../../grilling-113-disease-eligibility/grilling-113-disease-eligibility.md), [决策树 #113 Q2-11/Q2-12](../../../../docs/%E5%86%B3%E7%AD%96%E6%A0%91.md)*
