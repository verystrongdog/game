# ASPD（反社会型人格障碍）资格核验 — 证据收集

> **证据收集，非裁决。** 本文档只做五步核验协议的素材采集（①DSM/ICD 标准定位 ②必要性分析输入 ③反样本 ④资格原子候选材料 ⑤表征域材料），**不产出**：阈值数字、判定函数、最终资格规则、任何 ELIGIBLE/INELIGIBLE/UNDETERMINED 结论、原子命名归位结论。判定与定值全部留给用户裁决。
> 纪律约束（沿用 #113/#116）：G1-G4 全局不变量、反样本纪律、表征偏好 ≠ 资格阈值、症状计数不得充当资格原子、MISSING ≠ FALSE、禁止"创伤事件→原子"（转化接口 §3.2.2 :213）、患者层"目标实例化合法化"不得回灌资格层（[决策记录-平凡实例化](../决策记录-平凡实例化.md) D4 两层隔离铁律）。

| 项 | 值 |
|----|-----|
| Type | 资格核验批次 2（证据收集，子代理产出，待用户裁决） |
| 归属 | [#116](https://github.com/verystrongdog/game/issues/116) 配额表驱动核验批次（平凡实例化裁定 D6）+ [批次 2 总览](总览.md) G5 ASPD 行 |
| 前置 | #113 资格层（Eligibility(d)/原子三值/G1-G4）+ [批次 1 BPD 定案（BPD_PATTERN_HISTORY）](../资格核验批次1-性创伤通道/BPD-核验收尾.md) + 批次 1 模板 |
| 目标病 | 反社会型人格障碍（ASPD） |
| 项目通道 | **A 临床史主导**（[批次 2 总览](总览.md) G5 行工作地图初判；通道归属是核验产物而非输入——批次 1 BPD 曾由"C 混合"修正为"A 主导"，本文件不预设结论） |
| 父类 | 人格障碍（DSM-5 PD 通用标准 A-F 为父类语义锚） |
| 创伤易感事件类型 | [忽视/遗弃]（转化接口 §3.2.1 :136 候选集行；疾病目录 frontmatter 只读镜像） |
| 参考先例 | `BPD_PATTERN_HISTORY` = #87 单一模式存在性声明（转化接口 §3.2.2 :234；人格障碍 = 持久模式非发作史；≥X/Y 组合判定留 #87 声明侧、资格门不计数）；CYCLIC_MOOD_HISTORY 配方同构 |

## 目录

- [〇、项目内锚点一览（供对照，证据引用基准）](#〇项目内锚点一览供对照证据引用基准)
- [一、DSM-5 / ICD-11 定位](#一dsm-5-icd-11-定位)
- [二、必要性分析输入（d⟹X 方向材料，不作结论）](#二必要性分析输入dx-方向材料不作结论)
- [三、反样本收集（有反社会行为但不是 ASPD）](#三反样本收集有反社会行为但不是-aspd)
- [四、资格原子候选材料（BPD_PATTERN_HISTORY 先例同构问题）](#四资格原子候选材料bpd_pattern_history-先例同构问题)
- [五、表征域补充材料（E_d^mem 侧，"冷漠叙事化"）](#五表征域补充材料e_dmem-侧冷漠叙事化)
- [六、待核验清单与移交](#六待核验清单与移交)

---

## 〇、项目内锚点一览（供对照，证据引用基准）

以下为证据引用的项目内基准（均已 Read 确认，引用即读取铁律）：

| 锚点 | 项目内取值/语义 | 出处 |
|------|----------------|------|
| 资格层链路 | 候选召回 → Eligibility(d) ∈ {ELIGIBLE, INELIGIBLE, UNDETERMINED} → 仅 ELIGIBLE 进入主病选择/聚合 | 转化接口 §3.2.2 |
| 证据域 | E_d = E_d^mem（记忆内表征）∪ E_d^hist（记忆外临床史/行为史规范化声明） | 转化接口 §3.2.2 :170-175 |
| 证据原子三值 | X_e ∈ {1, 0, MISSING}；MISSING ≠ FALSE | 转化接口 §3.2.2 :183 |
| 归位原则 | P_i 是 d 的必要条件 ⟺ d⟹P_i；N_j 是 d 的排除条件 ⟺ N_j⟹¬d（方向不可交换） | 转化接口 §3.2.2 :199-201 |
| 禁止项 | 创伤事件 → 原子；症状计数 → 原子；DSM 内部症状/时长条件 → Eligibility 原子（归 #87 声明依据） | 转化接口 §3.2.2 :213 |
| ASPD 召回行 | 事件类型"忽视/遗弃"候选集 = {BPD 主, MDD, ASPD, 分裂情感 卫}，临床锚注"依恋损伤；早期剥夺→情感钝化"；§3.2.1 十类事件表当前**仅此一行**召回 ASPD | 转化接口 §3.2.1 :136 |
| 表征偏好表 ASPD | (N, F, D_seg) = (0.70, 0.30, 0.05)——"冷漠叙事化" | 转化接口 §3.2.3 :271 |
| BPD 定案签名（先例） | `BPD_PATTERN_HISTORY = 1`：#87 单一模式存在性声明（BPD 式持久人格模式存在性，≥5/9 组合判定留声明侧、资格门不现场数条款）；无硬排除原子（共病合法），PD 通用标准 E/F 排除 = 声明侧纪律 | 转化接口 §3.2.2 :234；term_registry `BPD_PATTERN_HISTORY` |
| BPD_PATTERN_HISTORY 注册表语义 | "人格障碍是持久模式非发作史——不能用症状计数或单域分原子（polythetic 下任何单域非必要）；单一宽模式声明 + 判定留声明侧是唯一不触发『症状计数→原子』禁止项的形态" | data/term_registry.json :3869-3879 |
| ASPD 疾病目录 | 父类人格障碍，疾病ID `aspd`，创伤易感事件类型 `[忽视/遗弃]`（镜像）；核心病理"自我社会域↓ 解耦沉默（共情缺失）+ 防御域↓（威胁反应低）+ 认知控制域↓（冲动控制失败）"；14 条病理边 aspd_e01-e14 全为**解耦沉默**（m 负偏移），CU traits→右侧杏仁核活动↓ 右偏 +0.2 | [实体/疾病目录/反社会型人格障碍.md](../../../实体/疾病目录/反社会型人格障碍.md) :6/:13/:19 |
| 父类（人格障碍） | 默认病理类型"解耦沉默 或 过度耦合"；子类含 ASPD/BPD/分裂型 | [实体/疾病目录/_父类/人格障碍.md](../../../实体/疾病目录/_父类/人格障碍.md) |
| 通道修正先例 | BPD 由工作地图"C 混合"修正为"A 临床史主导"（核验修正，同 SSD 先例）——通道归属由核验产出 | 转化接口 §3.2.2 :234 |

**引用约定**：DSM-5/DSM-5-TR 标准条文为中文工作整理（非官方译本），关键英文短语保留原文；逐字准确性存疑处一律标 [需核验]。文献只给"支持/反对某命题的材料"，不因"有文献"即认定命题成立（G2：病因关联文献不得单独证明资格必要性）。DSM-5（APA, 2013）与 DSM-5-TR（APA, 2022）条文差异处单列标注。

---

## 一、DSM-5 / ICD-11 定位

### 1.1 DSM-5 Section II — ASPD（301.7）：门槛结构与 A-D 标准

**来源**：DSM-5（APA, 2013）/ DSM-5-TR（APA, 2022），Section II 人格障碍章，301.7 Antisocial Personality Disorder（ICD-10-CM 映射 F60.2）。（免费权威镜像：NCBI StatPearls [Torrico & Hany, ASPD](https://www.ncbi.nlm.nih.gov/books/NBK546673/) 逐字转引 DSM-5-TR 标准；[MSD Manual Professional, ASPD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd)；[WikiDoc ASPD](https://www.wikidoc.org/index.php/Antisocial_personality_disorder)）

**门槛结构**（依镜像转述 DSM-5-TR 原文要点）：核心特征（essential feature）= "一种对他人权利的**漠视与侵犯**的普遍模式（pervasive pattern of disregard for and violation of the rights of others），始于童年或早期青少年并延续至成年"；门槛为 A（普遍模式，**15 岁以来**，**7 条中 ≥3 条**，polythetic）+ B（年龄 ≥18）+ C（**15 岁前品行障碍史**）+ D（反社会行为**非仅**发生于精神分裂症或双相障碍病程中）。逐条如下：

| # | 标准主题（中文整理） | DSM-5 关键语义 | 项目关注点 |
|:-:|--------------------|-----------------|-----------|
| 1 | 不遵守社会规范中的守法行为——反复实施可被逮捕的行为 | Failure to conform to social norms with respect to lawful behaviors, as indicated by repeatedly performing acts that are grounds for arrest | 违法条款（任务点名）——**"可被逮捕行为"是行为事件条款，非自我报告态度** |
| 2 | 欺骗性——反复说谎、使用化名、为个人利益或快乐行骗 | Deceitfulness, as indicated by repeated lying, use of aliases, or conning others for personal profit or pleasure | 欺骗条款（任务点名）——"为个人利益/快乐"动机成分 |
| 3 | 冲动性或不能事先计划 | Impulsivity or failure to plan ahead | 冲动条款（任务点名）——与 BPD Criterion 4 表面重叠（§三.4） |
| 4 | 易激惹与攻击性——反复斗殴或袭击 | Irritability and aggressiveness, as indicated by repeated physical fights or assaults | 攻击条款（任务点名）——与 IED/双相躁狂易激惹需鉴别（§三.2） |
| 5 | 鲁莽地漠视自己或他人安全 | Reckless disregard for the safety of self or others | 鲁莽条款（任务点名）——"自损"是漠视安全而非 BPD 式情绪驱动自伤 |
| 6 | 一贯不负责任——反复不能维持稳定工作行为或履行财务义务 | Consistent irresponsibility, as indicated by repeated failure to sustain consistent work behavior or honor financial obligations | 不负责任条款（任务点名） |
| 7 | 缺乏悔意——对伤害、虐待或偷窃他人**无动于衷或加以合理化** | Lack of remorse, as indicated by being indifferent to or rationalizing having hurt, mistreated, or stolen from another | 无悔意条款（任务点名）——7 条中唯一带"内部态度/情绪"语义的条款；polythetic 单条非必要（§二.2） |

> **结构事实 1（供 §二/§四 引用）**：ASPD 的 A 标准是 **polythetic（≥3/7）**——不存在"任一单条行为条款对每个患者必然成立"。与 BPD（≥5/9）同构的计数结构，但 ASPD 另有 B/C/D 三个**非 polythetic 独立条款**（年龄/品行障碍史/病程排除）。
> **结构事实 2**：A 标准的 7 条全部是**指向他人的行为条款**（违法/欺骗/攻击/鲁莽/不负责任），只有第 7 条近似"态度"（无动于衷/合理化）；DSM-5 ASPD 是**行为性定义**——"冷漠/共情缺失"不是 A 标准门槛内容（见 §五，"冷漠"的 DSM 落点）。

### 1.2 品行障碍史（Criterion C）与"成人反社会行为"Z 码——独立条款地位

**来源**：同上（NCBI StatPearls / MSD Manual；DSM-5 标准文本二手转述）。

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| C1 | DSM-5 Criterion C 原文语义："**There is evidence of conduct disorder with onset before age 15 years.**"——必备独立条款，非 A 标准内部项 | DSM-5-TR 转引（StatPearls/Mirror）；DSM-5 原文逐字 [需核验] | Criterion C 与 Criterion A 时间窗不同：A = "since age 15"，C = "before age 15" |
| C2 | Criterion B："The individual is at least age 18 years." | 同上 | 年龄硬条款（§四.3 候选原子材料） |
| C3 | "Adults who do not have evidence of conduct disorder in childhood but otherwise meet the criteria for ASPD can be diagnosed with **adult antisocial behavior**"——该编码**非正式精神障碍诊断**（ICD-9 V 码 / ICD-10 Z 码，具体码号 [需核验]） | StatPearls 转述（[NCBI NBK546673](https://www.ncbi.nlm.nih.gov/books/NBK546673/)） | DSM 为"无 CD 史的成人反社会行为"单设了**非障碍编码**——材料指向"CD 史"在 DSM 分类学上是 ASPD 的强必备语义（§二.1） |
| C4 | MSD：诊断要求转述 "patients must have evidence that a conduct disorder has been present before age 15 years" + "ASPD is diagnosed only in people ≥ 18 years" | [MSD Manual Professional, ASPD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd) | 与 C1/C2 一致 |

> **注记**：品行障碍（CD）本身是儿童/青少年期诊断（DSM-5 行为障碍章；CD 要求年龄 <18 且"若 ≥18 岁则未达到 ASPD 标准"——CD 与 ASPD 的诊断边界在 18 岁衔接，见 §三.3）；"品行障碍史（15 岁前）"是**作为 ASPD 的历史前件被回溯引用**，不是当前 CD 诊断。

### 1.3 DSM-5 人格障碍通用标准（父类语义锚）

**来源**：DSM-5 Section II 人格障碍章开篇 General diagnostic criteria for a personality disorder（[NCBI StatPearls PD 概述转引](https://www.ncbi.nlm.nih.gov/books/NBK546673/)；BPD 证据收集 §1.2 同源）。

| 标准 | 内容（中文整理） | 项目相关语义 |
|:-:|----------------|-------------|
| A | 持久的内在体验和行为模式显著偏离个体文化期望，体现在 ≥2 域：①认知 ②情感 ③**人际功能** ④**冲动控制** | "模式 + 偏离"载体；ASPD 的偏离主要落在③（对他人权利的漠视/剥削）与④ |
| B | 该持久模式是僵化、不可变通的，并在广泛的个人与社会情境中**渗透/普遍**（pervasive） | 跨情境声明要件——§三 环境性反社会行为的区分锚 |
| C | 导致临床上显著的痛苦或社会、职业等重要功能损害 | 损害性要件（ASPD 的"痛苦"常在他方而非本人——材料注记） |
| D | 该模式稳定且持续时间长，起病可追溯至青少年期或成年早期 | 早发 + 慢性要件；ASPD 模式起病可追溯至**青少年期（15 岁前后）**且有 CD 前史 |
| E | 该模式不能更好地被其他精神障碍所解释 | 排除他因要件（§三 反样本语义） |
| F | 该模式不是物质或躯体疾病（如头部外伤）的生理效应所致 | 排除物质/躯体要件（§三.4 器质性人格改变） |

### 1.4 DSM-5-TR 注记与 DSM-5 Section III（替代模型）提示

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| T1 | DSM-5-TR 未改动 ASPD 的 A/B/C 标准与 ≥3/7 门槛（[需核验逐字对照]）；**Criterion D 措辞**：DSM-5-TR 转引为 "not exclusively during the course of **schizophrenia or bipolar disorder**"，DSM-IV-TR 旧版为 "schizophrenia or a **manic episode**"；DSM-5(2013) 究竟用哪个措辞 [需核验] | StatPearls（DSM-5-TR）；WikiDoc（DSM-5）；DSM-IV-TR 历史对照 | "双相期间"范围表述差异——语义锚版本选择是裁决输入 |
| T2 | DSM-5 Section III（AMPD 替代模型，供进一步研究）对 ASPD 的定义走"人格功能损害 + 病理性特质"路线，其特质组合含 **manipulativeness/deceitfulness/callousness/hostility/irresponsibility/impulsivity/risk taking**（数量门槛与逐字 [需核验]）——"callousness（冷酷）"只在替代模型作为特质之一出现，不在 Section II 门槛内 | DSM-5 Section III [需核验] | 与 §五（"冷漠"表征的 DSM 落点）直接相关 |

### 1.5 ICD-11 定位

**来源**：ICD-11（WHO, 2019 发布 / 2022 生效 / 现行 2024 版），MMS 代码与 CDDG 临床描述（逐字 [需核验]；在线浏览器 https://icd.who.int/browse/2024-01/mms/zh 或 icd.who.int/browse/2024-01/mms/en）。

| 项 | ICD-11 定位 | 备注 |
|----|------------|------|
| 人格障碍本体 | 6D10 Personality disorder，按严重度分型：6D10.0 轻度 / 6D10.1 中度 / 6D10.2 重度（[代码编号 [需核验]]） | 维度化严重度 + 特质域限定语，取代 ICD-10 类别式 F60.x |
| ASPD 对应 | **无独立"反社会型/非社交型人格障碍"类别或 pattern 限定语**——对应物 = 6D10 人格障碍（严重度）**+ 6D11.2 dissociality（社交紊乱）特质域限定语** | 与 DSM-5 独立类别逻辑不同；ICD-10 F60.2 dissocial personality disorder 的迁移映射 = 6D10.x + 6D11.2（映射表 [需核验]） |
| 特质域限定语 | 6D11.0 negative affectivity / .1 detachment / **.2 dissociality** / .3 disinhibition / .4 anankastia / .5 borderline pattern（ICD-11 唯二保留的"pattern"之一是 borderline pattern；**无 dissocial pattern**） | 编号与"限定语仅用于中/重度"问题 [需核验] |
| 品行障碍史要求 | ICD-11 CDDG **不要求** DSM-5 Criterion C 式的"15 岁前品行障碍史"（[需核验]）——dissociality 是特质域描述；品行障碍（儿童/青少年）在 ICD-11 是独立类别 conduct-dissocial disorder（6C91 系，[需核验编号]） | 两分类系统对"CD 史是否必要"立场不同——资格语义锚选择的重要材料（§四.4） |
| 人格障碍通用要求 | CDDG：自我/人际功能问题 + 模式**长期持续**（"present over an extended period"；是否逐字含 "≥2 年" [需核验]）+ 通常首见于童年/青少年并延续至成年 + 非其他障碍/物质/躯体直接效应所致（[需核验]） | 与 DSM-5 通用标准 D/F 对应 |

**ICD-11 6D11.2 dissociality 内容要点**（依 CDDG 转述，逐字 [需核验]）：漠视社会义务与惯例以及他人权利与感受；自我价值感膨胀（inflated sense of self-worth）；**冷酷（callousness）**、缺乏共情；操纵性与欺骗性；把他人当作工具；敌意、攻击性、鲁莽、漠视自身与他人安全；行为可包括反复违法与违反社会规范。

> **两种分类逻辑的结构差异（材料，供 §四 使用）**：DSM-5 = 独立疾病类别，门槛 = A（≥3/7 polythetic，15 岁以来）∧ B（≥18）∧ C（CD 史 <15）∧ D（非仅 SZ/双相期间）∧ PD 通用标准；ICD-11 = 严重度维度 + dissociality 特质域限定语（描述性、无计数门槛、**无 CD 史要求**）。资格层以哪个为"语义锚"、两锚冲突（尤其 CD 史是否必备）如何处理，属用户裁决项，本文件不表态。

### 1.6 任务点名特征 → 条款映射表

| 任务点名特征 | DSM-5 条款 | ICD-11 dissociality 元素 |
|------------|-----------|--------------------------|
| 违法/反复被捕行为 | A-1 | 反复违法（作为行为表现） |
| 欺骗/行骗 | A-2 | 操纵性、欺骗性 |
| 冲动 | A-3 | —（冲动更多落 disinhibition 域；两域可叠加 [需核验]） |
| 易激惹攻击 | A-4 | 敌意、攻击性 |
| 鲁莽不顾安全 | A-5 | 鲁莽、漠视自身/他人安全 |
| 一贯不负责任 | A-6 | 漠视社会义务 |
| 缺乏悔意 | A-7 | 冷酷、缺乏共情、无悔意（作域描述） |
| 品行障碍史（15 岁前） | **Criterion C（独立必备条款）** | 无对应必备条款（CD 为独立儿童类别） |
| 年龄 ≥18 | Criterion B | 人格障碍本体为成人持续性模式（[需核验措辞]） |
| 非仅精神分裂症/双相期间 | Criterion D | 排除他病所致（CDDG 通用要求） |

---

## 二、必要性分析输入（d⟹X 方向材料，不作结论）

> 归位原则方向：`P_i 是 d 的必要条件 ⟺ d⟹X`。本节只收集"支持/反对 ASPD⟹X"的材料。**方向不可交换**：即便材料支持 d⟹X，也不等于 X⟹d（充分性见 §三 反样本）。

### 2.1 命题 A：ASPD ⟹ 品行障碍史（15 岁前）？

**支持材料（A⟹方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| A1 | DSM-5 Criterion C 为独立必备条款："There is evidence of conduct disorder with onset **before age 15 years**"——非 A 标准内部 polythetic 项，无门槛组合可以绕开它 | DSM-5/DSM-5-TR（§1.1/§1.2 C1） | 与 BPD 的差别：BPD 无此类单列史实条款 |
| A2 | MSD/StatPearls 临床转述一致：诊断须有 15 岁前 CD 证据（"evidence of conduct disorder must be present"） | [MSD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd)；[StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) | 教科书层一致，非 DSM 原文 |
| A3 | DSM 为"无 CD 史但成人反社会行为"设置**非障碍 Z 码**（adult antisocial behavior）——即 DSM 分类学把"无 CD 史的反社会成人"移出 ASPD 类别 | StatPearls（§1.2 C3） | 支持"CD 史是 ASPD 的必备前置"的分类学语义 |

**反对/限定材料（¬A 或 A 弱化方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| A4 | **ICD-11 无 CD 史要求**：dissociality 特质域 + 严重度即可描述，不引用品行障碍前史条款 | ICD-11 CDDG（§1.5，逐字 [需核验]） | 两锚冲突点；"CD 史必要"是 DSM-5 分类决策而非跨系统共有的医学事实 |
| A5 | 流行病学：多数 CD 儿童**不**发展成 ASPD（StatPearls 引：约 25% 女孩 / 40% 男孩 CD 最终发展成 ASPD [数值 [需核验]]）——CD 史是 ASPD 的必要**分类条件**，但不构成充分/高概率条件；从 CD 到 ASPD 有大量流失 | [StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) | G4：逻辑地位（分类必备）≠ 临床发生概率 |
| A6 | 临床可操作性批评：成人对 15 岁前行为史的报告常不可靠，需旁证（collateral）——"无档案化 CD 史"可能反映信息缺失而非事实否定 | StatPearls（评估段：collateral information） | MISSING ≠ FALSE 的项目语义在临床有对应物 |
| A7 | 品行障碍史是 DSM-5 **Criterion**（历史前件条款）而非核心定义（essential feature = 漠视/侵犯他人权利的普遍模式，落在 Criterion A）——若做"资格原子"须区分：核心定义承载"模式存在性"，Criterion C 承载"15 岁前发展史" | DSM-5（§1.1） | 任务点名的材料分界：CD 史 ≠ ASPD 的定义核心 |

### 2.2 命题 B：ASPD ⟹ 缺乏悔意模式？

**支持材料（B⟹方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| B1 | DSM/教科书典型描述：ASPD 个体"rarely experience remorse / remorse for actions is lacking"、常合理化伤害行为 | [StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/)；[MSD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd) | 典型呈现（typical presentation）描述，非门槛 |
| B2 | 任务点名的方向材料（DSM 文本收集）：7 条中第 7 条 = "being indifferent to or **rationalizing** having hurt, mistreated, or stolen from another"——DSM 把"合理化"也计入无悔意，语义比"完全无内疚"宽 | DSM-5/DSM-5-TR A-7（§1.1） | — |

**反对/限定材料（¬B 或 B 弱化方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| B3 | A 标准 polythetic ≥3/7——形式上存在不含第 7 条的合法达标组合（如 1+2+4、1+3+5+6 等）；**第 7 条对每例非必要** | DSM-5（§1.1 结构事实 1） | 任务点名的核心形式反例（同 BPD 文件 B4 同构论证） |
| B4 | 实证结构：多数符合 psychopathy（PCL-R）者也符合 DSM ASPD，**反之不然**——ASPD 是行为性定义，仅部分 ASPD 个体具 psychopathy 式情感/人际缺损（缺乏共情、情感肤浅、冷漠） | Hare & Neumann 2008（*Annu Rev Clin Psychol* 4:217-246）；[StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) | "无悔意/冷漠"更接近 psychopathy/CU 特质，非 DSM ASPD 全样本属性 |
| B5 | "缺乏悔意"在 DSM-5 Section III（AMPD）才作为 callousness 等特质进入（§1.4 T2）——主流 Section II 门槛不要求 | DSM-5 Section III [需核验] | 语义锚版本裁决输入 |
| B6 | 无法悔意 ≠ 反社会行为证据：悔意是**内部状态**，DSM 第 7 条以行为指标（无动于衷/合理化）判定——声明侧可操作性材料 | DSM-5 A-7 措辞 | 若做原子，"无悔意模式"须是 #87 声明的行为化表述（§四/§五） |

### 2.3 命题 C：ASPD ⟹ 违法/反社会行为史？

**支持材料（C⟹方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| C1 | essential feature = "对他人权利的**漠视与侵犯**的普遍模式"——"侵犯他人权利的行为史"在定义层面被点名（行为性定义） | DSM-5（§1.1） | "反社会行为史（广义模式）"是 ASPD 定义成分 |
| C2 | Criterion A 全部 7 条均为行为条款（违法/欺骗/攻击/鲁莽/不负责任），且 A 前缀限定"occurring **since age 15**"——15 岁后的反社会行为史是 A 标准的载体 | DSM-5（§1.1） | — |
| C3 | Criterion C 的品行障碍史（<15）本身含反复侵犯权利/规范的行为（CD 15 条含违法性行为）——ASPD⟹（<15 行为史）经 C 成立 | DSM-5 CD 标准（§1.2 注；CD 15 条逐字 [需核验]） | "15 岁前已有反社会行为史"随 Criterion C 必备 |

**反对/限定材料（¬C 或 C 弱化方向）**：

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| C4 | A-1（"可被逮捕的行为"）只是 7 条之一——**具体违法记录/被捕史**非每例必要（≥3/7 组合可不含 A-1，如 3+4+7）；"违法史"若窄化为"被捕/定罪记录"则非必要 | DSM-5（§1.1） | 与 §三.1（SUD 犯罪、孤立违法）反样本呼应 |
| C5 | G4 提醒：反社会行为史跨诊断普遍（SUD、双相躁狂、IED、创伤后、环境性、器质性均可）——"有反社会行为史"不指向 ASPD 唯一（详见 §三 全部行） | §三 | 逻辑地位 ≠ 临床独有性 |
| C6 | "违法/犯罪"受法律与执法环境调制（可逮捕行为的判定随司法环境变）——DSM 用"grounds for arrest"而非"被定罪"正是为避开执法偏倚 [需核验原文意图]；行为条款须以行为本身而非法律后果为声明对象 | DSM-5 A-1 措辞（§1.1） | 声明侧措辞材料 |

> 综合材料（供裁决参考，非结论）：A（CD 史 15 岁前）在 DSM-5 是**单列必备条款**（分类学强必要，且配"无则 Z 码"处理）；B（无悔意模式）与 C（狭义违法史）在 DSM 内部只能锚到 polythetic A 标准的部分条款，均存在"达标组合可不含该条款"的形式反例。因此若走资格原子，A 与 B/C 的语义地位不同——CD 史可独立声明（DEPRESSIVE_EPISODE_HISTORY 式史原子候选），"无悔意/违法"只能作为**模式声明内部的行为域成分**（BPD_PATTERN_HISTORY 思路），见 §四。

---

## 三、反样本收集（有反社会行为但不是 ASPD）

> 反样本纪律（沿用 PTSD-F 前车之鉴 + BPD 文件）：任何资格规则候选必须能在不误放下列样本的前提下成立。每行给出"表面相似特征 / 为什么不是 ASPD / DSM 锚 / 拦截要点"材料。

### 3.1 违法/欺骗行为组

| 反样本 | 表面相似（ASPD 类） | 为什么不是 ASPD（区分锚） | 来源 | 对"违法/欺骗史类资格成分"的拦截要点 |
|--------|-------------------|------------------------|------|------------------------------|
| SUD（物质使用障碍） | 为获物质而盗窃/欺骗/违法、不负责任、冲动（与 A-1/2/3/6 表面重叠） | SUD = 物质使用模式（失控/损害等）；DSM-5 ASPD 鉴别要求查**清醒期行为**：反社会行为仅见于物质相关状态 → 归 SUD/物质所致，非 ASPD；**但 ASPD 可与 SUD 共病**（清醒期模式仍在） | [MSD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd)（sobriety 鉴别）；StatPearls 鉴别段 | "物质相关违法史"单独不得放行 ASPD（项目 SUBSTANCE_USE_HISTORY 原子先例——SUD 轨道分流）；需"清醒期仍持续"的持久模式成分 |
| 孤立/情境性违法行为 | 一次或偶发违法、受罚后不再犯 | 与长期反社会特质不一致（"isolated acts of misbehavior"与持久模式不符）；无跨情境渗透性 | [StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) 鉴别段 | 单次/偶发事件 ≠ 模式声明（§2.3 C4） |
| 成人反社会行为（无 CD 史） | 成年后持续违法/欺骗，满足部分 A 条款 | DSM 明确：无 15 岁前 CD 证据 → **adult antisocial behavior（Z 码，非障碍）**，不得诊 ASPD | StatPearls（§1.2 C3） | **CD 史成分缺失 = 拦截点**——支持 CONDUCT_DISORDER_HISTORY 类原子材料（§四.3） |
| 环境性反社会行为（团伙/战区/贫困街区） | 在特定环境中长期参与帮派暴力/盗窃/勒索（行为面与 A 条款重叠） | PD 通用标准 A 要求模式"显著偏离**个体自身文化**的期望"；DSM-5 注记反社会行为须在**社会文化语境**中评估（在某语境适应/规范的生存行为 ≠ 人格偏离）[逐字 [需核验]]；CDDG 特质域评定亦须考虑文化规范 [需核验] | DSM-5 PD 通用标准 A；ASPD 文化相关段 [需核验]；转化接口 §3.2.1 :145 环境语义注记 | 团伙成员/环境适应样本须由声明侧"文化/情境语境"区分——环境存在性不是资格证据（:145） |
| 心理病态（psychopathy，非 DSM 诊断） | 冷酷、操纵、无悔意（与 A-2/7 及"冷漠叙事化"表征高度相似） | psychopathy（PCL-R，Hare）含情感/人际核心（缺乏共情、夸大、情感肤浅），**不是 DSM-5 诊断类别**；多数 psychopath 符合 ASPD 但反之不然——ASPD 门槛不含共情/情感条款 | Hare & Neumann 2008；[StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) | "冷酷无共情"作为资格成分会与 psychopathy 构念混淆——§五 表征域核心材料 |

### 3.2 冲动 / 攻击 / 去抑制组

| 反样本 | 表面相似（ASPD 类） | 为什么不是 ASPD（区分锚） | 来源 | 拦截要点 |
|--------|-------------------|------------------------|------|---------|
| ADHD | 冲动、易激惹、违纪/违法冲动行为、不负责任表象 | ADHD = 神经发育性（症状须 12 岁前、跨情境注意/多动/冲动缺陷）；ADHD 冲动非"为个人利益侵犯他人权利"结构；无欺骗/剥削模式、无 CD 史要求；项目已判 ADHD 发育性、不参与创伤转化 | DSM-5 ADHD 标准（转化接口 §3.2.1 :124）；Storebø & Simonsen 2016 综述（MSD 引，ADHD+CD 早于 10 岁 ↑ASPD 风险——**风险因素 ≠ 诊断**） | 发育性轨道不入 ASPD 资格门；ADHD+CD 高风险样本仍须按 ASPD 自身门槛核验 |
| IED（间歇性暴怒障碍） | 冲动性攻击爆发（与 A-4 表面重叠） | IED = 冲动性攻击**爆发**（语言/躯体，反应与诱因明显不成比例、非预谋），无 CD 史、无欺骗/剥削/不负责任的普遍模式；DSM-5 IED 鉴别要求排除 ASPD/BPD/CD/ADHD/BD 语境下的攻击 [逐字 [需核验]]（StatPearls 转述 "IED cannot be diagnosed as comorbid with ASPD" [需核验]） | [StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK546673/) 鉴别段；DSM-5 IED [需核验] | 纯攻击性冲动样本（无普遍剥削模式 + 无 CD 史）不得放行 |
| 双相 I/II 躁狂/轻躁狂期 | 冲动、鲁莽、易激惹攻击、违法（躁狂期行为与 A 条款重叠） | DSM-5 **Criterion D**：反社会行为**仅**发生于精神分裂症/双相病程 → 不得诊 ASPD；躁狂 = 发作性（睡眠需求减、夸大等）≠ 慢性模式；双相轨道已有 MANIA/HYPOMANIA 发作史原子 | DSM-5 Criterion D（§1.1）；转化接口 §3.2.2 :207-209 先例原子 | "躁狂期反社会"由发作史原子分流至双相轨道；Criterion D 是 ASPD 特有的病程排除条款（与 BPD 无对应条款不同，§四.4） |
| 精神分裂症（含偏执型/未分化） | 攻击、怪异反社会行为 | Criterion D 同上：仅发作期反社会 → 排除；分裂情感/偏执型 SZ 有自己的事件类型轨道（§3.2.1 威胁/暴力、社会伤害行） | DSM-5 Criterion D；转化接口 §3.2.1 | 需区分"共病共存"（SZ + ASPD 各自独立成立）与"仅病程中"（排除）——判定粒度留声明侧/裁决 |
| 创伤后去抑制/应激性攻击 | 创伤暴露后出现攻击、鲁莽、反社会样行为 | PTSD（DSM-5）：易激惹攻击/鲁莽自毁是**创伤后警觉/反应簇**条款，是状态性/症状性；cPTSD（ICD-11）亦为创伤特异性模式，无 ASPD 的欺骗/剥削/CD 史结构；PD 通用标准 D（持久稳定模式）区分"应激后新发/状态性"与"自青少年起持久模式" | DSM-5 PTSD Criterion E（易激惹与愤怒爆发、鲁莽或自毁行为）；ICD-11 6B41 cPTSD [需核验]；PD 通用标准 D | 创伤事件 → 资格禁止（:213）：创伤后的反社会样行为须经"持久模式 + CD 史"声明核验，创伤本身不得充当资格证据（§五.4 展开） |
| BPD 冲动攻击/鲁莽自损 | 冲动、愤怒爆发、物质滥用、危险驾驶（与 A-3/4/5 表面重叠） | BPD 的冲动/攻击是**情绪失调驱动、指向自身/关系**（自伤自杀条款、被弃恐惧、身份紊乱）；ASPD 是**对他人**的剥削/冷漠（无自伤自杀条款、无被弃恐惧）；DSM-5 鉴别：BPD 操纵为**获取照料**，ASPD 操纵为**利益/权力/物质** [逐字 [需核验]]；**两病共病常见**（Bateman & Fonagy 2008；[共病率 [需核验]]） | DSM-5 ASPD 鉴别段 [需核验]；MSD；Bateman & Fonagy 2008 *J Clin Psychol* 64(2):181-194 | BPD_PATTERN_HISTORY=1 与 ASPD 候选**可并行共病**（非互斥）；BPD 冲动攻击 ≠ ASPD 剥削模式——§四 原子须在模式层分离 |

### 3.3 儿童/青少年组（年龄窗反样本）

| 反样本 | 表面相似（ASPD 类） | 为什么不是 ASPD（区分锚） | 来源 | 拦截要点 |
|--------|-------------------|------------------------|------|---------|
| 品行障碍（CD，<18） | 15 岁前即有反复侵犯权利/规范行为——与 ASPD 的 Criterion C 前史同款 | CD 是 **<18 岁**诊断；DSM-5 CD 诊断要求含"若 ≥18 岁则须未达 ASPD 标准"（CD↔ASPD 在 18 岁边界互斥衔接 [逐字 [需核验]]）；<18 岁不得诊 ASPD（Criterion B） | DSM-5 CD/ASPD 标准（§1.2 注） | 年龄 <18 样本 = CD 轨道，不得放行 ASPD；≥18 且有 CD 史者才进入 ASPD 候选 |
| 青少年期局限型反社会（adolescence-limited） | 青少年期违法/反社会行为（A 条款表象） | Moffitt 双轨迹：**adolescence-limited**（青春期常见、多数成年消退，非人格障碍）vs **life-course-persistent**（早发 CD + 持续 → ASPD 风险）；多数青少年反社会者成年后消退——模式不持久 → PD 通用标准 D 不满足 | Moffitt 1993（*Psychol Rev* 100:674-701，双轨迹理论）；[数值 [需核验]] | 青少年期单段行为史不得作 ASPD 证据——需"15 岁前 CD + 15 岁后持续"两段连续模式（§2.1 A7/§四.3） |
| ADHD × CD 早发组合 | 童年多动冲动 + 行为问题（CD 高风险样本） | ADHD+CD 早于 10 岁 ↑ 成年 ASPD 风险（Storebø & Simonsen 2016）——**风险因素**；是否成病仍须过 ASPD 门槛（成年 A + B + C） | MSD 病因段（引 Storebø & Simonsen 2016） | 风险关联文献不得单独证明资格（G2） |

### 3.4 人格障碍间 & 器质性鉴别组

| 反样本 | 门槛概要 | 表面相似（ASPD 类） | 区分锚（为什么不是 ASPD） | 来源 |
|--------|---------|-------------------|--------------------------|------|
| BPD | ≥5/9（情绪不稳/冲动/自伤/被弃恐惧/身份紊乱等），无 CD 史要求 | 冲动、愤怒、物质滥用、操纵 | 动机方向相反（照料 vs 利益）；自伤自杀条款 ASPD 无；CD 史 ASPD 必备 BPD 无；共病合法 | DSM-5 鉴别段 [需核验]；MSD；转化接口 :234 BPD 签名 |
| NPD（自恋型） | ≥5/9（夸大/特权/缺乏共情等） | 剥削、缺乏共情、操纵 | NPD 一般**较少攻击与欺骗**（MSD 鉴别）；无 A-1 违法条款倾向、无 CD 史要求；夸大自我 vs ASPD 对他人权利的普遍漠视 | [MSD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd)；DSM-5 [需核验] |
| 器质性人格改变（Personality change due to another medical condition；ICD-10 F07.0） | DSM-5 器质性人格改变（310.1/F07.0）含冲动、去抑制、攻击等类型；由脑损伤/疾病直接所致 | 外伤/卒中/颞叶病变/额颞叶退行后出现冲动攻击、冷酷、反社会样行为（"acquired sociopathy"） | PD 通用标准 F：非躯体疾病生理效应所致 → 排除；器质变化有明确起病点（病程改变 vs 终生模式）；无 CD 史 | DSM-5 PD 通用标准 F；Personality change due to another medical condition [需核验]；Leppla et al. 2021（StatPearls 引） | 
| 分裂情感/SZ 谱伴攻击 | 精神病性期攻击/冲动 | Criterion D 排除"仅病程中"反社会；分裂情感为 SZ 谱轨道（§3.2.1 忽视/遗弃行召回**分裂情感 卫**——与 ASPD 同候选集内） | DSM-5 Criterion D；转化接口 §3.2.1 :136 | 候选集内分流：忽视/遗弃同时召回 {BPD, MDD, ASPD, 分裂情感 卫}——同一事件的多个候选由各自资格原子区分（分裂情感无 CD 史结构） |

### 3.5 反样本 → 证据域拦截方向汇总（材料层，非规则）

| 反样本组 | 若 ASPD 资格由"X"承载，会误放的风险 | 材料提示的分离方向 |
|---------|----------------------------------|-------------------|
| 违法/欺骗组（SUD/孤立违法/Z 码/psychopathy/环境性） | 仅凭"违法/欺骗史"或"冷酷呈现"放行 | 需"持久普遍模式"（跨情境、清醒期仍在）+ 文化语境声明侧区分；无 CD 史 → Z 码分流 |
| 冲动/攻击组（ADHD/IED/躁狂/SZ/创伤后/BPD） | 仅凭"冲动攻击/去抑制"放行 | 发作史原子分流（MANIA/HYPOMANIA）、发育性不入、Criterion D 病程排除、BPD 轨道共病并行 |
| 儿童/青少年组（CD/adolescence-limited） | 用 15 岁前 CD 前史直接放行成人 ASPD | 年龄窗（≥18）+ "两段连续"模式声明（CD <15 ∧ A 模式 ≥15） |
| PD 间与器质（NPD/BPD/器质人格改变） | 模式间混淆或器质误入 | 动机方向/CD 史/起病点（通用标准 D/F）区分 |

> 通用鉴别材料（DSM-5 PD 章引言，同 BPD 文件）：人格障碍各类型共享通用标准 A-F，PD 间鉴别靠**模式内容差异**（对谁/何种动机/何域偏离）；ASPD 对 BPD/NPD 的关键差异在**动机方向（利益/权力 vs 照料 vs 夸大）**与 **CD 史要求**。

---

## 四、资格原子候选材料（BPD_PATTERN_HISTORY 先例同构问题）

### 4.1 先例语义回放（引用即读取铁律）

| 项 | 内容 | 出处 |
|----|------|------|
| 原子 | BPD_PATTERN_HISTORY | 转化接口 §3.2.2 :234；term_registry.json :3869-3879 |
| 语义 | "已声明的 BPD 式持久人格模式存在性（多域跨情境模式：人际两极化/情绪反应性不稳/冲动自损/身份紊乱/空虚等，由 #87 按 DSM-5 PD 通用标准 A-F + BPD 模式域判定后声明）；≠ 症状计数——≥5/9 组合判定留在声明侧，资格门不现场数条款" | 同上 |
| 配方要点 | ①人格障碍 = 持久模式非发作史（polythetic 下分域原子必然退化为资格门计数 → 触发 :213 禁止项）②单一宽模式声明 ③判定（≥5/9 组合、排除他病 E/F）留声明侧 ④共病合法无硬排除原子 | term_registry deviation_reason；BPD 收尾裁决 #2/#4 |

### 4.2 ASPD 与 BPD 先例的同构点 / 差异点（材料，供裁决）

| 维度 | 同构点（支持走 BPD 单模式声明路线） | 差异点（ASPD 特有，需裁决如何处理） |
|------|----------------------------------|-----------------------------------|
| 门槛结构 | Criterion A = polythetic ≥3/7——单条/单域非个体必要，分条原子 = 资格门计数（:213 禁止） | **B/C/D 是非 polythetic 独立条款**：B 年龄 ≥18、C CD 史 <15、D 非仅 SZ/双相期间——BPD 无对应物 |
| 障碍本体 | 人格障碍 = 持久模式（通用标准 A-D）；模式声明形态（CYCLIC 配方）适配 | ASPD 模式时间窗分两段：Criterion A"since age 15" + Criterion C"CD before age 15"——单字段模式声明能否承载两段语义（含 15 岁边界判定）是设计问题 |
| 记忆签名 | 无（BPD 核验结论同构适用：表征偏好不是资格证据；§五） | ASPD 病理边 aspd_e01-e14 全解耦沉默（冷酷/低威胁反应）——"冷漠"在呈现侧有机制故事，但同属非记忆形态（§五） |
| 排除条款 | BPD 定案：无硬排除原子，PD E/F = 声明侧纪律 | ASPD 有 Criterion D（非仅 SZ/双相期间）——D 是资格层排除候选还是声明侧纪律，无直接先例（BPD 无此条款）；MANIA_HISTORY 作为 BD 轨道分流先例可参考 |

### 4.3 CONDUCT_DISORDER_HISTORY 独立原子候选材料（"是否需独立品行障碍史原子"）

| # | 材料 | 来源 | 方向 |
|:-:|------|------|:---:|
| D1 | Criterion C 是**独立必备条款**（非 polythetic 项），语义 = 一个**离散的、可独立声明的历史事实**（15 岁前品行障碍存在性）——与"≥3/7 成人模式"证据来源、时间窗、判定方式都不同（§2.1/§1.2） | DSM-5（§1.1/§1.2） | 支持独立声明原子（同 DEPRESSIVE_EPISODE_HISTORY"史存在性"先例形态，转化接口 :207） |
| D2 | 先例：DEPRESSIVE_EPISODE_HISTORY/SUBSTANCE_USE_HISTORY/MANIA_HISTORY 均为"离散史实存在性"原子（E_d^hist #87 声明），非模式宽原子——CD 史在结构上与它们同类 | 转化接口 §3.2.2 :207-209 | 支持独立原子 |
| D3 | 反样本价值：3.1 行 Z 码（成人反社会行为无 CD 史）、3.3 行 adolescence-limited（青少年反社会）都靠"CD 史成分缺失/不成立"拦截——独立原子让"CD=0 或 MISSING"成为可核验的否定/悬置位 | §三.1/§三.3；StatPearls（Z 码） | 支持独立原子（防"无 CD 史样本"被宽模式声明吞并） |
| D4 | 反对独立原子方向的材料：BPD_PATTERN_HISTORY 先例把"持久模式 + 判定"压成单一声明，主张资格门不拆 DSM 条款；若拆出 CD 原子，是否会在资格门形成"两原子 + 组合"的半计数结构（触发 :213 禁止项风险）——但注意 Criterion C 不是"A 标准内部计数项"，是独立条款，形式上有别于"症状计数" | term_registry BPD deviation_reason；转化接口 :213 | 反对/谨慎方向（形式区分留给裁决） |
| D5 | SSD 先例：时长/年龄窗类条件做成**声明侧原子**合法（SYMPTOM_DURATION_6M——"≥6 月判定留 #87 声明侧"，CYCLIC 配方）——"onset before age 15"同为年龄窗判定，可同构 | [SSD-收尾-裁决点.md](SSD-收尾-裁决点.md) :27/:35 | 支持：若做原子，15 岁边界判定留声明侧 |
| D6 | ICD-11 侧：无 CD 史要求（§1.5）——若资格语义锚选 ICD-11，CD 史原子将无锚可依；选 DSM-5 则有 Criterion C | ICD-11 CDDG [需核验] | 语义锚选择裁决输入 |

> 候选原子命名归位（如 ASPD_PATTERN_HISTORY / CONDUCT_DISORDER_HISTORY / 年龄 ≥18 的处理方式）全部留给裁决，本文件只提供上列 DSM/先例材料。

### 4.4 排除/分流条款材料（Criterion D + 通用标准 E/F）

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| E1 | Criterion D："antisocial behavior **not exclusively** during the course of schizophrenia or bipolar disorder"——排除范围是"仅在病程中"；**非"不得共病"**（SZ/双相与 ASPD 可独立共病，只要模式在发作外也存在） | DSM-5-TR Criterion D（§1.4 T1） | "仅"字的语义粒度是声明侧/裁决的关键 |
| E2 | PD 通用标准 E/F（不能更好地被其他障碍解释 / 非物质或躯体所致）——BPD 定案先例把这些归 **#87 声明侧纪律**（替代解释规则），不进资格门 | 转化接口 :234；BPD 收尾 #4 | ASPD 是否沿用（E/F 同款）+ Criterion D 单独处理方式 = 裁决 |
| E3 | 共病事实材料：ASPD×SUD 高度共病（MSD 转述 ECA：大多数 ASPD 患者有 SUD，约一半 SUD 患者符合 ASPD [数值 [需核验]]）；ASPD×BPD 共病在 NESARC 全国样本中显著（共现者 SUD/司法接触更重——[Personality and Mental Health, pmh.1491](https://onlinelibrary.wiley.com/doi/full/10.1002/pmh.1491)，作者/年份/率值 [需核验]）；Bateman & Fonagy 2008 述共病临床常见 | [MSD](https://www.msdmanuals.com/professional/psychiatric-disorders/personality-disorders/antisocial-personality-disorder-aspd)；Wiley pmh.1491；Bateman & Fonagy 2008 *J Clin Psychol* 64(2):181-194 | 硬排除原子会大量误杀共病样本——材料提示"分流而非排除"方向（BPD 先例同） |
| E4 | 与 BPD 不同：BPD 门槛内无 D 式病程排除条款，其"共病合法无硬排除"结论不能自动继承到 ASPD 的 Criterion D——D 若做成排除原子需论证"N_j⟹¬ASPD"（仅病程中反社会 ⟹ 非 ASPD，方向成立 [材料层]）；若归声明侧则语义 = "声明已排除仅病程中反社会" | 转化接口 :199-201（归位原则）；DSM-5 Criterion D | 归位裁决输入 |

### 4.5 工程可行性项目内材料

E_d^hist 来源 = #87 A′-Generator **规范化声明字段**（转化接口 §3.2.2 :175：转化接口不解析叙事）；故"模式声明"与"史实声明"型原子在工程上均为 A′ 产出的事实性声明字段（1/0/MISSING）。"15 岁边界""≥3/7 组合""CD 史存在性"等 DSM 内部判定按 :213 禁止项与 CYCLIC/SSD 配方**留 #87 声明侧**（资格门不现场计算年龄窗/条款数）。哪些事实值得做成 A′ 字段、合并成几个原子 = 用户裁决（本文件只提供 §4.2-§4.4 的 DSM 侧候选材料与两方向论据）。

---

## 五、表征域补充材料（E_d^mem 侧，"冷漠叙事化"）

### 5.1 项目内现有锚（已 Read 确认）

| 锚 | 内容 | 出处 |
|----|------|------|
| 表征偏好 | ASPD (N, F, D_seg) = (0.70, 0.30, 0.05)——"冷漠叙事化" | 转化接口 §3.2.3 :271 |
| 邻域对照 | 高 N 邻域：环性 (0.70)、SUD (0.65)、GAD (0.75)、OCD (0.80)、MDD (0.90)、PDD (0.95)；低 F 邻域（叙事完整侧）与 MDD/PDD/GAD 同侧 | 转化接口 §3.2.3 :253-275 |
| 病理边 | aspd_e01-e14 全部为**解耦沉默**（m 负偏移）——冷酷共情缺失（vmPFC/ACC/mPFC 信号发不出）、防御域低威胁反应（杏仁核→PAG）、TPJ 换位思考失败、dlPFC 冲动控制失败 | [实体/疾病目录/反社会型人格障碍.md](../../../实体/疾病目录/反社会型人格障碍.md) :19-36；Dugré et al. 2020/Dugré & Potvin 2021（文献锚） |
| BPD 收尾纪律 | BPD 核验修正结论：E_d^mem 仅作**起草侧参考，不进资格门**（无记忆签名/OGM 方向；高 F 与 PTSD 混淆反样本） | [BPD-核验收尾.md](../资格核验批次1-性创伤通道/BPD-核验收尾.md) #1 |

### 5.2 外部文献材料（表征/冷漠的临床-神经研究）

| # | 材料 | 来源 | 方向 |
|:-:|------|------|:---:|
| R1 | ASPD 自传记忆研究：监狱患者自我定义记忆（self-defining memory）提取任务中，ASPD 组情绪调节/心理化缺损相关；ASPD 组检索自传记忆时**面部情绪反应减弱**（冷漠的检索时呈现面） | Gandolphe 团队系列（[PLOS ONE 2022, self-defining memory 面部反应](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268818)；[PubMed 29548510 罪犯自传记忆特异性](https://pubmed.ncbi.nlm.nih.gov/29548510/)；[HAL 2024 论文预览](https://theses.hal.science/tel-04767352v1/preview/2024ULILH028.pdf)；作者/细节 [需核验]） | 表征/呈现侧材料（检索时情感呈现差异），非资格证据 |
| R2 | 共情分离材料：ASPD/psychopathy 存在**认知共情（理解他人心理）保留、情感共情（对他人痛苦的情绪反应）缺损**的证据（meta/综述篇目与效应量 [需核验]） | 综述检索中（详见 V10） | "共情缺失"是临床/神经心理学特征（功能域），非记忆形态 |
| R3 | 项目机制锚一致：aspd_eNN 全部解耦沉默 = "信号发不出"（冷酷共情缺失 + 低威胁反应），与"冷漠叙事化"呈现的机制故事同源；但机制层 ≠ 资格证据（G1：资格门只消费 #87 规范化声明） | 疾病目录 ASPD :19；转化接口 :178-179 | 起草侧机制材料 |

### 5.3 命题 E：纯表征（N=0.70"冷漠叙事化"）能否资格化？——支持面材料

| # | 材料 | 来源 |
|:-:|------|------|
| E1 | ASPD 存在可辨识的呈现/检索侧特征（冷漠叙事化、提取时低情绪反应，R1），E_d^mem/呈现层可作**起草侧参考**或主病选择的表征输入（§3.2.3 偏好表用途——**偏好 ≠ 资格阈值**，批次纪律） | R1；转化接口 §3.2.3 |
| E2 | 项目机制故事支持"叙事平静/冷"与低情绪唤起相关（aspd_eNN 解耦沉默；防御域低威胁反应）——若以呈现侧线索观之，冷漠叙事与"情绪风暴"（BPD）方向相反 | 疾病目录 ASPD :13/:19 |
| E3 | F=0.30 与 PTSD/DID 高 F 相距远——低碎片化使 ASPD 不会与 F 门（PTSD/DID）混淆（对照区分度验证 §3.2.3 :277 方法） | 转化接口 §3.2.3 :271/:277 |

### 5.4 命题 E 反对/限定面材料（纯表征资格化的反对材料——任务点名收集）

| # | 材料 | 来源 | 备注 |
|:-:|------|------|------|
| E4 | DSM-5/ICD-11 的 ASPD/dissociality 诊断特征**全部为临床史/行为模式级**（违法/欺骗/攻击/鲁莽/不负责任 + CD 史），**无一条**基于"记忆形态/叙事风格/区隔化"；(N,F,D_seg) 不出现在任何 ASPD 标准中 | DSM-5（§1.1/§1.2）；ICD-11 CDDG（§1.5） | 纯表征门缺少 DSM 语义锚（G2），同 BPD 文件 C4 论证 |
| E5 | "冷漠/共情缺失"在 DSM 的落点：(a) A-7 无悔意（polythetic 单条，且以行为指标判定）；(b) CD 的 **with limited prosocial emotions（CU）specifier（<18 岁、限儿童/青少年）**；(c) Section III AMPD callousness 特质（替代模型）——**均不是记忆形态，且无一为 Section II 门槛必备** | DSM-5 A-7（§1.1）；CD CU specifier [需核验]；§1.4 T2 | "冷漠"的临床史/行为属性而非记忆属性 |
| E6 | 高 N（叙事完整）指向**叙事化谱系**而非 ASPD：ASPD N=0.70 与环性同值，且低于 GAD/OCD/MDD/PDD（0.75-0.95）——纯高 N 样本会与抑郁谱（MDD 反刍叙事、PDD 慢性叙事）混淆；"完整叙述创伤"是多数非碎片化障碍的共有形态 | 转化接口 §3.2.3 :253-275 | 纯 N 门无 ASPD 特异性（同 BPD 文件 C8 高 F 混淆反样本的镜像论证） |
| E7 | "叙事冷漠"可来自**状态性/非人格障碍因素**：抑郁期情感钝化、SZ 阴性症状、解离性麻木（PTSD/DID 叙述可平板）、SUD、文化性情感表达规范——须与"持久冷漠模式"区分（PD 通用标准 D），区分在声明侧 | DSM-5 各障碍文本（状态性）；PD 通用标准 D | 表征域无法区分状态/特质（记忆形态不携带病程语义） |
| E8 | 反样本直接威胁：psychopathy 式"冷酷叙事"是最接近"冷漠叙事化"的非 ASPD 构念（§3.1 行）——若纯表征可资格化，冷酷叙事样本（可能无 CD 史、无 A 行为模式）将误放 | §3.1；Hare & Neumann 2008 | 表征信号无法承载 CD 史/年龄/病程排除 |
| E9 | 结构性纪律：批次纪律 = 表征偏好 ≠ 资格阈值；BPD 收尾 = E_d^mem 仅作起草侧参考不进资格门；ASPD 无记忆形态锚 → A 通道（临床史主导）为工作地图初判（[批次 2 总览](总览.md) G5 行）；"纯表征能否资格化"若为"是"需回应上述全部反样本——本文件只收材料 | 批次 1 总览 §三.4；BPD 收尾 #1；批次 2 总览 | 不表态 |

### 5.5 归位初判材料表（特征 → 证据域侧）

| ASPD 特征（§1.6 映射） | 是否有 E_d^mem 侧证据材料 | 是否主要在 E_d^hist 侧 | 材料提示 |
|----------------------|--------------------------|----------------------|---------|
| 违法/欺骗/攻击/鲁莽/不负责任（A-1~6 行为史） | ❌ | ✅ 主要是 | 行为史模式声明候选（§四.2） |
| 无悔意/冷漠（A-7） | ⚠️ 呈现侧线索（R1/E7），非资格证据 | ✅ 模式级 | "冷漠"近邻 = CU specifier/psychopathy（E5）——临床史/行为化声明 |
| 品行障碍史（15 岁前） | ❌ | ✅ 独立史实 | CONDUCT_DISORDER_HISTORY 类原子候选（§4.3） |
| 年龄 ≥18 | ❌ | ✅（实例化/声明侧） | Criterion B（§1.2 C2） |
| 非仅 SZ/双相期间（D） | ❌ | ✅（排除/声明侧） | Criterion D 归位裁决输入（§4.4） |
| 冷漠叙事化表征 (N=0.70) | ✅ 呈现侧有故事（R1/R3） | 否 | 起草侧参考/主病选择输入，非资格门（§5.3/5.4） |

---

## 六、待核验清单与移交

### 6.1 [需核验] 汇总（写作时未能核对原文/文献的项）

| # | 项 | 类型 | 建议核验源 |
|:-:|----|------|-----------|
| V1 | DSM-5(2013) vs DSM-5-TR Criterion D 措辞（"schizophrenia or a manic episode" vs "schizophrenia or bipolar disorder"） | 原文核对 | DSM-5 印刷版 / APA 官方 |
| V2 | ICD-11 代码结构（6D10.0/.1/.2、6D11.0-6D11.5）与 6D11.2 dissociality CDDG 逐字 | 原文核对 | WHO ICD-11 MMS/CDDG（icd.who.int） |
| V3 | ICD-11 是否含"人格障碍须持续 ≥2 年/首见童年青少年"逐字；无 CD 史要求的逐字确认 | 原文核对 | WHO CDDG |
| V4 | DSM-5/TR ASPD 与 CD 标准逐字英文与中文译本（本文为中文工作整理）；CD 15 条 4 组、CD↔ASPD 18 岁互斥衔接条款、CU specifier 逐字 | 原文核对 | DSM-5 印刷版/授权译本 |
| V5 | DSM-5 Section III AMPD ASPD 特质组合（含 callousness）与数量门槛 | 原文核对 | DSM-5 Section III |
| V6 | adult antisocial behavior Z 码具体码号（V71.01？/Z72.81？） | 编码核对 | DSM-5 附录/ICD-10-CM |
| V7 | CD→ASPD 比例数值（StatPearls 25% 女孩/40% 男孩）与 Moffitt 双轨迹比例 | 数值/著录 | 原文/系统性综述 |
| V8 | 共病率数值（ASPD×SUD 约半数、ASPD×BPD 率值；NESARC 共现样本 pmh.1491 作者/年份） | 数值 | ECA/NESARC 原文（Grant 2004、Compton 2005、Regier 1990）；[pmh.1491](https://onlinelibrary.wiley.com/doi/full/10.1002/pmh.1491) |
| V9 | psychopathy–ASPD 重叠率数值（监狱样本中 ASPD 符合 PCL-R 比例） | 数值 | Coid & Ullrich 2010 等 |
| V10 | ASPD/psychopathy 认知/情感共情分离的 meta 篇目与效应量 | 文献著录 | 综述/meta 检索（2026-09-06 核验中） |
| V11 | R1 自传记忆/面部反应研究作者、样本、结果细节 | 文献细节 | PLOS ONE 2022 / PubMed 29548510 原文 |
| V12 | DSM-5 ASPD 文化相关诊断段逐字（团伙/语境评估）；BPD 鉴别段"照料 vs 利益"逐字；IED 共病表述核验 | 原文核对 | DSM-5 各障碍 Differential/Culture 节 |
| V13 | 项目内对照：Dugré 2020/Dugré & Potvin 2021 与疾病目录 frontmatter 著录一致性 | 勘误 | pathology_edges.json 文献字段 |
| V14 | ICD-11 conduct-dissocial disorder 编号（6C91 系） | 原文核对 | WHO ICD-11 MMS |

### 6.2 移交说明

- 本文件为**证据收集层**产物：§一（定位）、§二（必要性输入）、§三（反样本）、§四（原子候选材料）、§五（表征域材料）全部为素材，供用户裁决：资格语义锚选择（DSM-5 版次 vs ICD-11）、通道归属确认、原子形态（单宽模式声明 / 独立 CONDUCT_DISORDER_HISTORY / 两段合并 / Criterion D 归位）、组合方式与（后续批次的）数值。
- 特别提示裁决的材料要点（非结论）：①ASPD 的 Criterion C（CD 史 <15）是**非 polythetic 独立必备条款**，与 BPD 先例（单模式声明即可）在结构上不同（§2.1/§4.2/§4.3）；②Criterion D 病程排除是 BPD 无对应物的新条款（§4.4）；③"冷漠叙事化"（N=0.70）的表征侧材料全为呈现/机制层（§5.2-5.4），无 DSM 记忆形态锚（§5.4 E4-E9）。
- 移交的下一动作（由用户/主代理裁决后执行）：五步核验的"结果层"（原子命名与归位表、组合结构、判定函数、数值）与 Step 4 写入（转化接口 §3.2.2 批次 2 签名表 ASPD 行、term_registry 入库、归位表汇总）——**均不在本文件范围**。
- 本批次并行产出：见 [批次 2 总览](总览.md)（G1-G6 各证据收集子代理运行中）。

---

*创建: 2026-09-06 | 状态: 证据收集完成（待用户裁决）*
*关联: [批次 2 总览](总览.md), [批次 1 BPD 证据收集](../资格核验批次1-性创伤通道/BPD-核验-证据收集.md), [批次 1 BPD 收尾](../资格核验批次1-性创伤通道/BPD-核验收尾.md), [转化接口 §3.2.2](../../../规则/技能树系统/创伤记忆转化接口.md), [反社会型人格障碍疾病目录](../../../实体/疾病目录/反社会型人格障碍.md), [决策记录-平凡实例化](../决策记录-平凡实例化.md)*
