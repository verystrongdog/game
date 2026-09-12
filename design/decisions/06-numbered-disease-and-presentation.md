# 设计决策树 — 编号轮次 — 疾病与呈现

> 按编号记录的后期轮次：#35 校准 / #113-#116 疾病生成 / #119-#126 突破机制与 Unity 呈现。
>
> **本文是历史档案**：只追加、不改旧条目。设计文档 = 当前状态；这里 = 怎么走到这里的。
> 总索引见 [README](README.md)。

---

## Grilling #35 — 战斗输出权重校准 + 精神攻击节点集 + 事件上限 + 月光场校准轨（2026-09-03 开题，闭合）

> Issue: [#35](https://github.com/verystrongdog/game/issues/35)（2026-08-08 开题，2026-09-03 闭合）| 维度: 规则+管线 | 形态: 跨 14 个 grilling 推迟聚合的最大校准议题。**方法修正**：scope 以引擎消费点 + 活跃正典标注自上而下重导出（推迟链只作候选提示）——因引用链大量过时（4 类失效实例，见治理发现）。月光场 E1/E2 已由 #100/#102 独立闭合；E3-E7 循先例独立 issue。14 项决策，全部经用户逐题确认（含外部评审 12 份）。

### 决策（Q0-Q12 + B 组）

- **Q0（范围/形态）**：A 形态——战斗域校准决策组（T0 + A 组 + B 组），三结果制（定值/暂定值/继续阻塞）；月光场 E3-E7 独立 issue 挂 #35 伞下；手动 trace = 方向性反馈非统计证明（#71 工具完成后正式验证）。
- **Q1（T0 战斗长度）**：**诊断指标**，无 PASS/FAIL——历史区间 4-6/8-10/16-20（#10 无论证拍板值）= 历史设计目标非规范地位；因果方向纠正（T 是 HP/伤害涌现观测量非独立旋钮）；战斗长度目标理论重建（动力学下限/疲劳上限推导）= 后续议题；精英/Boss 门禁推迟（Stat 实例未就绪）。
- **Q2（精神攻击双轨）**：**完成迁移**——采纳 `运行时状态模型 §8.1` a(t) 派生轨（#32 范式既定意图，非两公式择一）；`核心机制 §4.3` 旧公式降级为迁移前实现/历史公式；受控暂态（规范世界=新轨 / 运行世界=旧轨，引擎 P 系列接入前继续 base 2）。
- **Q2a（节点集+scale_mental）**：`S_mental` = cognitive CSTC 环路 ∩ W活跃 **7 fid**（ParsOpercularis/RostralMiddleFrontalDLPFC/FrontalPole/FrontalPoleFPN/FrontalPoleExtreme/CaudalMiddleFrontal/AnteriorCingulateCortexDorsal，排除 Caudate——W 行=列=0）；聚合 = 简单 mean(a)；gate 不参与 base；**motivation 乘子删除**（动机经 DA_VTA→b_j→a(t) 内化，防双算——旧轨两通道归并新轨单通道）；**scale_mental ≈ 3 暂定**（静息 mean(a)≈0.6 → ≈2 SAN 量级）；引擎 PENDING_IMPLEMENTATION。
- **Q3（θ_mem）**：`S_mem` = {HippocampusCA1, HippocampusCA3, Parahippocampal, Entorhinal} 4 fid（MTL 功能语义集合，Entorhinal L4 纳入）；`P_success = σ(mean(a) − θ_mem)`；θ_mem = 50% 成功率阈值（**SDT 判据 c**，#90 锚定）；**0.5 暂定**（0.6 = 隐含"记忆默认应失败"设计假设，正典无此前提）；PENDING。
- **Q4（一回合事件上限）**：**不设 N_max**——行动经济自然上界 + 三层饱和保护（tone clip/m 跳过/σ 饱和）已覆盖；文档化不变量；引擎防御断言 >64 抛异常。
- **B1（暴击四参）**：B 档——**θ_crit=0.82 / k_crit=1.0 暂定**（静息 a_exec=0.80777 实测，原 θ_crit=0.6 致静息 15.4% 暴击结构性错位）；base_crit=0.05/cap=0.30/L4 +0.15 保留；**低于阈值保留负偏差**（静息 3.8%，惩罚语义——max 压平会截断恐慌/压制对暴击的动态影响）；P4d 后回归校准。
- **B2（Δ_skill）**：**0.1 暂定**；公式权威 = **#74 D3** `a_j ← clip(a_j + Δ_skill × mean(m of 组内边), 0, 1)`（#70 裸注入 = 历史版本，同日被 #74 精化）；term_registry 补 m 缩放；PENDING（P1c）。
- **B3（FleeSanRestore）**：**+10 暂定** + **时段级防护**（1 游戏时段内每角色仅首次成功逃跑获得——防"进战→逃跑→再进战"刷 SAN 循环，战斗不推进游戏日无天然时间成本）；Δm 跳过/无掉落/敌人未解决保留。
- **B4（s_neg）**：**1.25 暂定**（已锁区间 [1,1.5] 中点）；**引擎现役**（SituationSelector 消费，#109 实施完成）——非 PENDING，待 #71 扫参验证。
- **B5（T2 动力学群）**：4 察觉静息常量 = **已实测定值**（csharp-tone M1，E-3 迁移硬编码→CalibrationConfig + 正典逐 fid 表）；MaxRounds=50 **非校准项**（防死循环保护）；δ_scale=0.3 **暂定**（工程理由：防 tone 饱和）；M1SustainPenalty=−0.1 / PerceptionThreshold=0.15 **无依据占位**（机制有定义数值零依据——待 #71 从零校准而非复核）。
- **B6（PanicToneShift）**：A 档分工——**C1 δ = 恐慌跨越边沿脉冲（事件线）/ PanicToneShift = 恐慌期稳态偏移（状态线）NE+0.2/5HT−0.2 暂定**；归属边界写死（防第三条机制）：PanicToneShift 是状态条件不得再次实现跨越检测。
- **B7（响应窗口阈值）**：**T_L4=0.70 / T_L5=0.75 暂定**（相对静息带 [0.535,0.771] 定位，激活门控语义）；两个独立响应（读意图自动防御 vs 叙事重构 +25%）**不合并**——共享 a(t) 阈值门控形式但节点域/效果/触发全不同；**校准语义约定**：统一语义不统一参数（S 节点集/θ 相对静息位置/超阈值行为效果三要素）。
- **B8（医疗人员压抑计数触发）**：**继续阻塞 + 转实体域**——不设暂定值（无消费方无给值理由）；**双门槛原则**：战斗内发生 ≠ 战斗域参数，领域归属 + 消费方存在性决定纳入（否则装备/药物/空间参数都会被"战斗内生效"吸入 #35）。

### 治理发现（本 grilling 形成，随 #35 收尾保留）

1. 引用链过时四模式：公式被替换推迟项悬空（w_perception/w_execution）/ 快照未随修表更新（NpcHp=15 vs F-5 权威 20-30）/ 术语漂移同名异物（情境强度系数 → 实为 s_neg）/ 引用链内部矛盾（#88 vs #90 κ/θ_g）。
2. 精神攻击双轨根因四层：范式迁移分批执行无完成回路 / #33 按公式家族清扫漏网（motivation 家族）/ 引擎与设计意图零核对 / 注册表记录意图非状态 → **validate_params C5 三向一致性（正典↔注册表↔引擎）必要性的活反例**。
3. Δ_skill 不一致根因：决策演进（#70→#74 同日精化）vs 快照滞后（term_registry 停 #70 版）——历史层 ≠ 现状层。
4. C1/PanicToneShift 重复根因：两条独立设计线（#32 事件线 / #34·#76 NPC 线）各自实现同一"恐慌→NE↑5HT↓"效应、交叉点无人认领 → 归属边界写入。
5. 双门槛原则（B8）：参数纳入战斗域校准 = 领域归属（战斗域）∧ 消费方存在性；暂定值服务消费链而非填表。
6. 校准语义约定（B7）：激活门控阈值统一语义——S 节点集 / θ 相对静息分布位置 / 超阈值行为效果；**统一语义，不统一参数**。

### 受影响文件

- `../设计归档/grilling/grilling-35-calibration/决策记录.md`（新建——决策表 + 治理发现 + 推迟清单）
- `design/rules/核心机制.md`（§4.2 暴击参数 θ_crit 0.82/k_crit 1.0 + §4.3 迁移标注：新轨定案/旧轨=历史实现）
- `design/rules/skill-tree/operations/基础行动设计.md`（§二 精神攻击公式迁移 + §三 暴击参数 + §四 速查表）
- `design/rules/skill-tree/运行时状态模型.md`（§4.5 延迟注闭合 → #74 D3 / §5.5 事件不变量 / §8.1 S_mental·S_mem·scale_mental·θ_mem 定案 + w_perception/w_execution 废弃声明）
- `design/rules/回合战斗流程.md`（§8.3 FleeSanRestore +10 暂定 + 时段级防护）
- `design/rules/skill-tree/NPC AI 行为模型.md`（§9.1 恐慌双机制分工：C1 边沿/PanicToneShift 稳态）
- `design/entities/敌人与事件.md`（§十二 压抑计数触发 → 转实体域标注）
- `data/term_registry.json`（w_perception/w_execution 废弃 + scale_mental 迁移状态 + Δ_skill m 缩放）
- `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs`（ScaleMental 注释：设计值 ≈3 暂定 PENDING，运行值 1.0 不动）
- `design/decisions/`（本文）+ `design/framework/six-dimensions.md`（规则 +1）+ memory（`战斗输出权重校准-grilling-35.md`）

### 推迟

- T0 trace 执行（N≈5 观测，载体手动/自动化待定）→ 独立议题；战斗长度目标理论重建（动力学下限/疲劳上限）→ 后续
- 精英/Boss 战斗长度门禁 → 敌人 Stat 实例（实体队列）
- 月光场 E3-E7（E3→E4→E6→E5→E7）+ r/α_s + E_c/E_th 族数值 → #35 伞下独立 issue
- 医疗人员压抑计数阈值 N → 实体域（敌人 Stat + 战斗设计）
- 4 察觉静息常量 E-3 迁移 + 正典逐 fid 表 → #70 管线 P0
- scale_mental/θ_mem/暴击/Δ_skill/FleeSanRestore/T_L4/T_L5/PanicToneShift 引擎接入 → 对应 P 系列批次
- δ_scale/M1SustainPenalty/PerceptionThreshold 从零校准；s_neg 正式验证 → #71 工具
- 一致性治理 C5-C7 + 单一事实源 → #111 方向 1 独立议题

---

## Grilling #113 — 疾病资格层 Eligibility(d) 解耦（创伤负荷 ≠ 疾病资格）（2026-09-03 开题，闭合）

> Issue: [#113](https://github.com/verystrongdog/game/issues/113)（2026-09-01 开题，2026-09-03 闭合）| 维度: 规则 | 形态: 机制层架构修正 + 证据层首批核验 | 来源: #89 顾维扬草稿外部评审两份（t6a96e985 顾维扬草稿审查 / t6a96ecd6 资格层解耦）+ 用户逐轮外部 AI 评审 ×17 轮（t6a96f10e ~ t6a970c9a37），每轮经用户逐题确认。**本轮定案：创伤负荷聚合 L_agg(d) 被当作疾病资格是变量语义错误（非参数问题），引入独立资格层 Eligibility(d) 硬门。**

### 背景

#89 顾维扬草稿生成输出暴露资格层结构缺陷：**L_agg(d) 被当作疾病资格**——丧失事件聚合 → BD-II（L_agg=1.085，无轻躁狂史）、事件负荷 → 环性（1.575，无周期性）、经济剥夺 → SUD 幽灵候选（0.84，无物质使用史）。外审 t6a96ecd6 精确定义问题边界：`Pathological(x) ⇏ Disease(d)` 与 `L_agg(d) ⇏ Eligibility(d)`——本轮不审查已定案项（创伤=唯一触发路径 :3980 D1、双阈值病理化门），只审查资格层是否存在及其与档位的职责边界。外审提出七步执行顺序，本轮按其推进。

### 决策（Q1-Q2-12 + 回放）

- **Q1（资格层地位）**：**方案 A 前置硬门**——`Candidate(d) → Eligibility(d) → L_agg(d) → Severity(d)`；`Eligibility(d) ⊥ L_agg(d)`（概念职责分离：Eligibility 判"有没有资格成为 d"，L_agg 判"已经是 d 时负荷多大"）。**Q1a（呈现）**：A2「机制上移除，诊断上保留」——被挡候选保留诊断记录；`L_agg`/`Severity` 对被挡候选为 ⊥ 语义（机制层不定义，呈现层延迟）。
- **Q1 窄锁定（t6a96f531e7 收窄）**：只锁门位置 + 必要条件 `Eligibility(d)=0 ⟹ d 不参与疾病竞争`（主病选择 + L_agg 聚合 + Severity/档位）；证据来源/缺失语义/判定函数/输出形态全部后置。呈现层候选（⊥ 记法/eligibility_reason/L_agg_raw/通道命名）不污染机制裁决。
- **Q2 第一刀（证据域）**：**B——允许独立记忆外临床史/行为史证据域** `E_d^hist`；**边界**：H 为专门定义的资格证据域，非任意人物属性（防万能诊断器）。完整证据域 `E_d = E_d^mem ∪ E_d^hist`（记忆内表征域 + 记忆外临床史域），选 B 不丢弃记忆内通道。
- **Q2-2（受控枚举）**：`E_d^hist` 用**受控枚举**（非自由文本解析）——自由文本 → 解释层会引入 `Narrative interpretation ⇏ Clinical fact` 新漏洞。两层分离：证据原子（证据域 schema）≠ 疾病—证据映射（d→E_d）。新增映射需可追溯权威依据（资格语义锚）。**DSM 边界**：不把完整诊断标准塞进 Eligibility（SUD 的失控/耐受/戒断不自动全成独立门槛）。
- **Q2-3（产出方）**：**A——#87 A′-Generator 显式产出规范化声明字段**（如 `clinical_history.mania_history ∈ {true,false,absent}`）；转化接口只消费声明值、不现场解析叙事。Narrative → #87 人机协同/审阅 → H（规范化声明）→ Eligibility（纯机械）→ {0,1}。
- **Q2-4（原子拆分 + BD-II 多必要条件）**：**MANIA_HISTORY 与 HYPOMANIA_HISTORY 必须分离**（外审 t6a96fafc6 修正我的 BD-I→HYPOMANIA 错误——躁狂/轻躁狂是质的区分非阈值；BD-I 需躁狂史，BD-II 需轻躁狂史+抑郁史+从未躁狂）。**新增第 8 原子 DEPRESSIVE_EPISODE_HISTORY**：BD-II → {HYPOMANIA, DEPRESSIVE}；**铁律 `L_agg 不能充当 DEPRESSIVE_EPISODE_HISTORY`**（丧失事件给负荷 ≠ 发作史，防"抑郁代理"重演）。
- **Q2-5（判定结构）**：**签名原子制选 A 但修正**——`Signature_d ⊆ NecessaryEvidence_d`（可共享，非疾病独有事实）；"不要为了防止诊断器化，把真实的必要条件错误降格成非必要"。BD-II 多必要条件：`E_BDII = HYPOMANIA ∧ DEPRESSIVE ∧ ¬MANIA`。**签名原子撤销为分析概念**（非"一病一必要原子"架构约束），资格门 = "必要条件门"非"单签名检测器"。
- **Q2-6（三值语义）**：**C 显式缺失态 + 两层分离**——证据原子域 `X_e ∈ {1,0,MISSING}`（1=有证据支持/0=明确否定/MISSING=无足够资料）；资格状态域 `EligibilityStatus ∈ {ELIGIBLE, INELIGIBLE, UNDETERMINED}`。**MISSING ≠ FALSE；UNDETERMINED ≠ INELIGIBLE**。input_source ∈ {canonical, fallback} 只负责缺失输入工程处置（正式→FAIL/演示→fallback），**不得把 MISSING 改造成医学 TRUE/FALSE**（fallback ≠ 医学证据）。
- **Q2-7（三值组合规则）**：∃P_i=0 → INELIGIBLE；∃N_j=1 → INELIGIBLE；∃P_i=MISSING 或 ∃N_j=MISSING → UNDETERMINED；∀P_i=1∧∀N_j=0 → ELIGIBLE。**P5 防后门**：ELIGIBLE 仅准入（必要条件满足+排除未触发），不表示疾病诊断成立、不保证档位——Eligibility 与 Severity 永不合流。
- **Q2-8（归位原则）**：锁原则不锁公式——`P_i 必要 ⟺ d⟹P_i`、`N_j 排除 ⟺ N_j⟹¬d`（疾病级权威依据）。SUBSTANCE_USE_HISTORY = 必要正向候选；**SUD 失控/耐受/戒断三原子不提前归位**（t6a9705a1fb 否掉我的"历史∧任一失控指标"公式——未核验的临床组合规则不得提前硬编码，防"结构美感压过临床事实"）。
- **Q2-9（五步核验协议）**：①DSM/ICD 标准定位 ②检验 `d⟹X`（X 是否必要——**方向不可交换**，t6a970687b3 修正）③检验 `X⟹d`（是否充分）④原子间组合关系 ⑤原子级归位表+文献锚。纪律：**方法先锁，结果后锁**。
- **Q2-10（证据等级）**：**A + 精确化**——资格语义锚 = **独立证据层**（非第三级）：DSM/ICD 标准文本优先（资格语义）；临床/学术文献（组合/边界/解释）；流行病学/病因文献（创伤→病关联，**不得单独证明资格必要性**）。"有文献" ≠ "该文献证明了当前声称的逻辑命题"；DSM/ICD 是权威来源 ≠ Eligibility 是完整诊断器。
- **Q2-11（执行批次）**：**A′ 原子依赖优先 + 疾病级必要性独立核验**——共享原子（DEPRESSIVE）语义核验一次，但 `MDD⟹DEPRESSIVE` 与 `BD-II⟹DEPRESSIVE` 分别证明（**共享原子语义可复用，疾病级逻辑不可自动继承**）。执行顺序：DEPRESSIVE → SUBSTANCE_USE → MANIA → HYPOMANIA → CYCLIC →（SUD 三原子延迟）→ 汇总五病归位 → 形成 Eligibility 规则。
- **Q2-12（五基础原子核验闭合）**：DEPRESSIVE_EPISODE_HISTORY（MDD/BD-II 必要正向，三重禁止 L_agg/症状负荷/创伤事件替代，DSM 内部标准不渗漏入资格门）；SUBSTANCE_USE_HISTORY（SUD 必要正向候选，≠次数/剂量/损害，物质类别"暂不拆分"非"无需拆分"）；MANIA_HISTORY（BD-I 必要正向/BD-II 排除条件，躁狂严重程度=功能损害∨住院∨精神病性特征**非并列必备**）；HYPOMANIA_HISTORY（BD-II 必要正向，环性"轻躁狂样"亚阈值不适用，逻辑地位≠临床存在性）；CYCLIC_MOOD_HISTORY（环性必要正向候选，=#87 病程模式声明，≠时期计数，防资格门现场计算病程）。
- **#1（候选集语义）**：候选集主/卫标注 = 召回级语义，Eligibility = 资格级语义，**正交**；候选集不加资格标注，资格由各病归位表承担。
- **#2（兼容性）**：资格门仅作用于**新生成**；已落盘 NPC 不批量回溯重算；顾维扬草稿作为本轮回放验证对象。
- **过度设计刹车（t6a970c54ff）**：机制层 + 五基础原子 = 收敛点；SUD 三原子/剩余 ~19 病/新增原子/为未来消费者提前完成资格规则 → **全部停止**，记延迟项。**#113 后续批次 = "已确定方法、尚无当前消费者的延迟执行项"，非未完成的本轮设计。**
- **顾维扬回放（七步⑥⑦，裁决 HYPOMANIA=0）**：证据声明 {DEPRESSIVE=1, HYPOMANIA=0, MANIA=0, SUBSTANCE=0, CYCLIC=0} → BD-II INELIGIBLE（必要原子 HYPOMANIA 未由 #87 声明成立，**非叙事判断**）、环性 INELIGIBLE、SUD INELIGIBLE、MDD ELIGIBLE → 主病重算 **MDD 轻**（原草稿 BD-II 主病被资格门排除，对应外审选项 B"降为 MDD"）。2006-2007 材料缺明确异常心境/相对基线改变/完整发作持续性三样生成侧依据，且叙事给出"时代红利+创业成功+风险偏好"替代解释 → 不足以声明完整轻躁狂发作。

### 受影响文件

- `design/rules/skill-tree/创伤记忆转化接口.md`（新增 §3.2.2 资格层 + §3.2.3 主病选择顺延 + §3.3 档位前置条件 + §四 速查表 + 头部/文末更新）
- `design/decisions/`（本文）
- `design/framework/six-dimensions.md`（规则维度转化接口条目补充）
- `data/term_registry.json`（新术语：Eligibility(d) 疾病资格层/资格语义锚/资格证据原子/ELIGIBLE-INELIGIBLE-UNDETERMINED/G1-G4 全局不变量 等）
- `../设计归档/grilling/grilling-113-disease-eligibility/grilling-113-disease-eligibility.md`（决策记录）
- `.scratch/grilling-113-disease-eligibility/chatgpt_share_t6a96f10e~t6a970c9a37.html`（外审存档 ×17）
- `reference/灵感收件箱.md`（2026-09-01 两条灵感，含资格门活例标注）
- memory（`疾病资格层-grilling-113.md`）

### 推迟

- SUD 三原子（LOSS_OF_CONTROL/TOLERANCE/WITHDRAWAL）归位 + 组合规则 → #113 后续批次（方法=五步协议已定）
- 剩余 ~19 病逐病核验（24 病分类框架表：临床史病/表征病/混合三通道，标注初判/待核验）→ 后续批次，逐病开核验记录
- 物质类别拆分（SUD）→ 暂不拆分（G3：工程范围 ≠ 医学结论），触发条件：资格证据/NPC 素材/疾病空间要求区分时
- E_d^mem 阈值化（DID→D_seg、PTSD→F 的资格阈值）→ 表征病批次
- 前瞻性风险分层（"高危未发病"状态）→ 独立机制，不属 Eligibility（职责边界三条已锁）

**推迟项执行进展注记（2026-09-03，#89 病种扩容线推进）**：首批非心境谱病种核验已在 #89 侧启动，详见 [grilling-89 记录](../archive/grilling/grilling-89-npc-material/grilling-89-npc-material.md) #89-D19~D26：

- **PTSD（B 表征病初判）**：走 E_d^mem 路径核验——证据基础完成（`PTSD-F资格阈值-证据基础.md`）：F 语义锚定（SAM 碎片）+ **反样本证据否决"F 单条件资格"**（感官碎片非 PTSD 独有，综述 f5）→ 规则方向 = 事件类型 ∈ {威胁/暴力,性创伤} ∧ F≥θ_F ∧ 可能 N≤θ_N；θ_F/θ_N 数值待本批次
- **SSD（B 表征病初判 → 修正建议 A 临床史病）**：DSM-5 核验（`SSD资格核验-第1-2步.md`）——资格核心 = B 标准（症状+心理过度投入）= 临床史非记忆形态；e08/e09 创伤→躯体化是发病机制非资格 → **修正 #113 地图初判**，待本批次确认
- 工作文档均归档于 `../规格/素材`；数值/最终规则仍待本批次

## [Grilling] 记忆生成器理论可行性评审 (2026-09-06，D1-D6)

> Issue: [#117](https://github.com/verystrongdog/game/issues/117) | 维度: 规则（纯学术研讨，不入游戏正典——#93/#97 先例）| 轨道裁决: 不入 #116 决策流（2026-09-06 用户）| 输入: ChatGPT 分享 6a9cbc29-7af0-83e8-9cc6-57624d9e3f89（q_t 严格定义 + 记忆生成器/人生生成器理论，全文 `chatX_transcript.txt` 3526 行）| 状态: ✅ 已闭合（2026-09-06）| 前置: 无 | 阻塞: 无

评审对象 = 对话全部技术主张 + 自评表（:3403-:3421）。结论：**结构层可行、价值层撤回**——记忆生成器能写（限定版），从零生成一生不能（不只缺 G_W，规范上缺外部 U）。

- **D1（Q1）**：q_t「主体定义已站住」过强——站住的是「预测价值用条件互信息度量」这一选择；q_t 作为可计算量未完成，三处未封口：①C_t 构造缺失（良构公式 ≠ 定义；C_t⊇S_t → q_t≡0 坑只换标签未解决）②Ψ_H 未定 ③P 归属——闭环下未来含智能体自身行为，预测≠因果一刀的前提（未来独立于记忆使用）不成立
- **D2（Q2）**：预测价值路线在自主闭环中病态——高维条件互信息无一致估计器（样本单位 = 整条人生轨迹）+ 记忆改变未来 → P 漂移 → q_t* 非良定目标；事后审计量结论不迁移。需换决策论框架
- **D3（Q3）**：决策论重述 = A 方案——规范目标 = 决策价值（依赖外部给定 U/P_world/π，记忆系统不自洽）；工程落点 = 生物代理量（RPE/预测误差类 δ_t、显著性）近似决策价值；q_t 退役为受控环境审计量。推论：对话「V1 只吃事件输入」在价值部分被更根本否定（无 U/P 则「值得记」无定义）；δ_t 地位升格为记忆形成主代理
- **D4（Q4）**：结构层整体采纳（q̂ 摘除后成立）——R/G 双更新闭环、F_R 依赖 G 论证、K_R 随机核、三随机源分解、操作集、M_t 冗余判定、差异化机制全部保持；π_ψ 选操作准则 = V1 必答未决（对话未给）；ρ = V1 前置
- **D5（Q5）**：Ψ_H 随 q_t 退役（仅受控审计需定义，不再阻塞 V1）；ρ 升级 V1 前置必答（ρ 未定则 V1 图检验项 3/4 无意义）；K_R 变量集收缩为 {R, G, r, δ, s, ξ}
- **D6（Q6）**：自评表逐行裁决——价值部分系统性乐观（第 4 行 q_t「可靠候选」撤回、第 7 行「写 V1 可以」限定为 ρ 先行+代理量+无 q̂ 版），结构部分基本可靠（第 5/6/8/9 行成立）；最终回答：记忆生成器 = 能（限定版），从零生成一生 = 不能（缺外部 U + 结构缺口 ρ/π_ψ/f_θ）

**受影响文件**：
- `reference/记忆生成器理论-可行性评审-v1.md`（新建——评审产物）
- `design/decisions/`（本条目）
- `data/term_registry.json`（不修改——术语候选清单用户 D 裁决 2026-09-06：全部不入库；q̂ 冲突与术语区分注记仅存 reference/记忆生成器理论-可行性评审-v1.md §九）

**推迟清单**：ρ 边语义候选（结果/价值关联 + 时间邻近 + 语义相似）→ **见 [Grilling #118](https://github.com/verystrongdog/game/issues/118)**（ρ v0 = 时间邻近 ∨ 同类别同 v 方向，已实例化）；π_ψ 准则 / f_θ 表示 / s_t sim → 见 #118（Q6/Q7/Q8 已实例化 v0）；U 与 G_W → 「一生」级目标理论边界声明，与 意识结构侧 暂停轨同为学术前沿（恢复接续点见 memory 意识结构侧暂停注记）

*关联: [#116](https://github.com/verystrongdog/game/issues/116)（同源输入的 #116 决策流另行处理）, [chatX_transcript.txt](../../reference/session-archive/chatX_transcript.txt)*

## [Grilling] 人生经历生成器 V0 — 双通道轨迹律设计 (2026-09-06，Q1-Q10)

> Issue: [#118](https://github.com/verystrongdog/game/issues/118) | 维度: 规则（纯学术研讨，不入游戏正典——#93/#97/#117 先例）| 轨道: 不入 #116 决策流 | 前置: #117（D1-D6）+ 双通道对象层锁定（2026-09-06 会话）| 状态: ✅ 已闭合（2026-09-06）

目标：`G: (S₀, θ_ind) → P(τ)`，`τ = (S₀,E₁,S₁,…,E_T,S_T)`；R1 强式：固定 (S₀, θ_ind) 下 |supp P(τ)| ≥ 2。核心科学断言 H1：分歧主要在决策点累积、记忆调制放大分歧（效应量报告，不预设结论）。

- **Q1** 抽象时步（阶段结构显式延迟 V1/Phase-2）
- **Q2** 5 轴离散状态：S = (E 经济, R 关系, H 健康, D₁ 驱力-生存, D₂ 驱力-社会)，各 3 档；风险/机遇轴与能力轴声明扩展
- **Q3** 事件 E_t = (type ∈ 6 原型, s, ΔS ∈ {−1,0,+1}^5·s)，效应模式显式映射表
- **Q4** 动作 A_t ∈ {∅} ∪ {E,R,H × l∈{1,2}} ∪ {D₁/D₂ 消费}（短视消费即时满足、代价副作用表）；成功概率归世界通道
- **Q5** 双触发（重大事件 ∨ 驱力缺口 ≥ θ_D）→ 连续决策窗 k=3 步；窗口步事件照常（模式差异唯一语义 = A_t 可用）
- **Q6** π 两段式静态：驱力贪心 + ε 探索 + 记忆调制；无记忆组 vs 有记忆组对比；否决 RL（需标量回报 U = D3 外部依赖 + 长时程信用分配不可行 + 最优性杀死 R1）
- **Q7** 记忆对象 = 结果记录 schema：r_j = (id,t,c,s,ΔS,S_before,v∈{−1,0,+1},m)；v 为 RPE 语义；S_before 情境检索键
- **Q8** 记忆操作全包规则：δ（被动 s·‖ΔS‖ / 决策 |v|）门槛 → f_θ 确定性编码 → merge/create（ξ^R 边界 p_merge）→ m 衰减/遗忘 → ρ 连边（时间邻近 ∨ 同类别同 v 方向）→ 决策点检索调制
- **Q9** 双维初始 θ_ind = (S₀, ε_i, β_i) 总体先验；R1 强式检验；消融组（ξ^W=0/ξ^A=0/ξ^R=0/全关）归因分化来源
- **Q10** 检验：6 条件 × N=200；T 扫参 {200,1000,5000}；主度量 D̄ + ΔD_decision（决策点距离增量），辅事件序列相似度；门禁 G1 非退化 / G2 不坍缩 / G3 消融可归因（指标锁数值不锁）；H1 报告效应量

**受影响文件**：
- `reference/人生经历生成器-双通道-V0-设计.md`（新建——V0 规格，含参数速查表 §十一：全部 [NEW 待标定]，不在规格阶段拍数值）
- `design/decisions/`（本条目）

**推迟清单**：阶段结构（V1 第一扩展）/ 困境期连续窗口深化 / 短视消费纹理 / 风险机遇轴·能力轴 / 可信轨 M-B 定义 / 日历时间慢变量（与 #116 D(t) 交汇时另行裁决轨道）；模拟实现批次另开 issue（#94 sim 批次先例）

*关联: [#117](https://github.com/verystrongdog/game/issues/117), [#116](https://github.com/verystrongdog/game/issues/116), [V0 规格](../../reference/%E4%BA%BA%E7%94%9F%E7%BB%8F%E5%8E%86%E7%94%9F%E6%88%90%E5%99%A8-%E5%8F%8C%E9%80%9A%E9%81%93-V0-%E8%AE%BE%E8%AE%A1.md)*

## [Grilling] #114 生成器生态问题 — 两问题归宿 + 生产范式移交（2026-09-06 闭合）

> Issue: [#114](https://github.com/verystrongdog/game/issues/114) | 维度: 规则 | 前置: #89 MVP 证据链 + #113 资格层 | 状态: ✅ 已闭合（2026-09-06）| 归宿: 两问题在生产范式移交后各自消解/接管，详见 #116 平凡实例化裁定

### 决策

- **Q1（负荷×声明相关性，67.9% 无主病）——生产侧消解**：患者生产范式改为"病种优先目标实例化"后，声明 = 目标规格的满足证据，不再存在"负荷够但声明无发作史"的生成错配；该 MVP 观测降级为**自底向上抽样的证据**（非生产方式）。构成分解（R=1000 复跑）：未病理化 14.5%（合法健康）/ 候选不含五病 5.0%（扩池可解）/ 五病 UNDETERMINED 21.4%（MISSING 伪影）/ 五病 INELIGIBLE 27.0%
- **Q2（池结构偏差，MDD 45.5%）——配额设计接管 + 扩池 backlog**：生产侧病房构成 = 批次配额 slot（非涌现分布）；5 病资格池能力上限残留 → **配额表驱动核验批次**（目的 = 扩大可生成病种，证据中立逐批解锁 ~19 病，PTSD/SSD 在途样板）→ 见 #116 D6
- **无主病语义（待决 4）**：未病理化 = 合法健康（s=∅ 正典语义）；病理化无 ELIGIBLE = 自底向上抽样伪影，平凡实例化生产下不再出现

### 受影响文件

- `../设计归档/grilling/grilling-116-disease-gen-evolution/决策记录-平凡实例化.md`（新建——裁定全文）
- `design/events/NPC人生生成器设计.md`（§一 修订注 + 头部修订声明）
- `design/decisions/`（本条目 + #116 条目）
- `design/framework/six-dimensions.md`（规则 +1：患者生成范式行；事件 #87 行补注）
- memory（`患者生成范式-平凡实例化-grilling-116.md`）
- issue #114 关闭评论

### 推迟

- 随机性裁决草案（5 条，2026-09-06 会话提出）——用户未确认，悬置
- S2 记忆档案结构（独立表示层议题，未立项；#117 学术轨已覆盖部分理论边界）
- 靶内多样性工艺（自由维：人格/日常/细节/活判据）——下一实际议题
- ~19 病资格核验——证据中立，随配额表需求逐批

## [Grilling] #115 人群点模型研究（2026-09-06 闭合）

> Issue: [#115](https://github.com/verystrongdog/game/issues/115) | 维度: 管线（独立研究/学习模型，不进游戏机制）| 状态: ✅ 已闭合（2026-09-06）

未进入逐题讨论（工作文件仅至 Step 2）。会话探索（人=点/14 亿/人群涌现/轨迹）结论与 #116/#117 同源判定一致：全规模人群模拟与"从零生成一生"在游戏侧不可行（#117 学术边界：缺外部 U + G_W）。独立研究线暂缓启动，本 issue 闭合；探索内容存留于 `../设计归档/grilling/grilling-115-crowd-point-model`。

*关联: [#114](https://github.com/verystrongdog/game/issues/114), [#116](https://github.com/verystrongdog/game/issues/116), [#117](https://github.com/verystrongdog/game/issues/117)*

## [Grilling] #116 疾病生成模型演化化改造 — 暂停 + 平凡实例化范式裁定（2026-09-06）

> Issue: [#116](https://github.com/verystrongdog/game/issues/116) | 维度: 规则 + 管线 | 前置: #87 A′-Generator + #88 转化接口 + #113 资格层 + #89 素材生产 | 状态: 方向暂停 + 范式裁定（2026-09-06）| 输入: 本会话（#114 生态问题 grilling 长程探索：原型/轨迹/ABM/LLM 投影/随机分叉/记忆档案 全路径证伪或挂起）+ #117/#118 学术轨结论

### 决策

- **D1（Q1 保留，issue body 已定）**：病目录层（26 病 × 档位 × m 模板）作为下游契约不动；本次只裁"怎么得病"的引擎层
- **D2（暂停裁决）**：轨迹演化替代快照映射（U→E→X→M→S→A→E′）**暂停**，不做生成侧架构级替换。理由（用户裁定）：项目资源无法进一步倾斜到真实的病患模拟；#117 学术轨已给理论边界（从零生成一生 = 不能，缺外部 U + G_W）；#118 V0 规格为学术轨产物不入正典。**Q2（替换范围 A/B 分叉）悬置**
- **D3（生产范式 = 病种优先目标实例化，暂名"平凡实例化"）**：目标 slot =（病种 d × 六轴缺口 × 自由维约束）→ 起草实例化（d 的必要原子证据成立、排除原子由替代解释支撑）→ 资格回放门 → 定稿。配额/病房构成 = 批次设计输入，非涌现输出
- **D4（#87 核心立场边界声明，显式修订非静默）**：#87「生成器不定义正确人生、疾病从经历涌现」为生成器本体原则；在**患者生产层**暂不适用。涌现原则保留范围：自由维靶内多样性工艺、六轴多样性门禁、验证脚本（MVP 类）、未来范式升级预留
- **D5（两层隔离铁律）**：病种优先仅适用于**患者生成层**；疾病资格核验层（~19 病解锁）保持证据中立（DSM/ICD 五步协议、反样本、G1-G4），不得因"想要某病患者"放宽——生成层目标驱动合法化 ≠ 资格层目标驱动合法化
- **D6（病种库扩张 = 配额表驱动核验批次）**：目的 = **生成更多种类的病患**。病房构成配额表（病种 × 六轴缺口，设计目标）→ 配额需要但未核验的病种 → 列入证据核验批次（证据中立，PTSD/SSD 在途为 A/B 通道样板）→ 核验通过即加入可生成池。可生成病种上限由核验进度决定，不由生产范式决定

### 受影响文件

- `../设计归档/grilling/grilling-116-disease-gen-evolution/决策记录-平凡实例化.md`（新建——裁定全文）
- `design/events/NPC人生生成器设计.md`（头部修订声明 + §一 修订注）
- `design/decisions/`（本条目 + #114 条目）
- `design/framework/six-dimensions.md`（规则 +1：患者生成范式行；事件 #87 行补注）
- memory（`患者生成范式-平凡实例化-grilling-116.md`）
- issue #116 评论（决策同步）

### 推迟清单

- 轨迹演化模型（#116 原方向）——暂停；恢复条件：资源到位或出现可信 W 世界表示时另行裁决
- Q2（替换范围 A/B）——随方向暂停悬置
- 随机性裁决草案（5 条）——用户未确认，悬置
- S2 记忆档案（独立表示层议题，未立项）
- 靶内多样性工艺（自由维）——下一实际议题
- ~19 病资格核验——配额表驱动，证据中立逐批 → **✅ 已完成（2026-09-06 批次 1-2：24/24 经历型全部定案可生成；批次 1 性创伤通道 PTSD/DID/BPD，批次 2 全量 SSD/SZ谱/进食族/PDD/焦虑谱/ASPD/拖延/OCD；新增资格原子 21 个（term_registry 304 条）；通道规律 = 全落 E_d^hist 声明轨（单宽模式原子 + 复合条件判定留 #87 声明侧），PTSD 为唯一 E_d^mem 表征签名；详见 ../设计归档/grilling/grilling-116-disease-gen-evolution 批次 1-2）**

**闭合注记（2026-09-06）：** issue #116 已完成 Step 5 关闭——关闭总结评论（决策表 + 受影响文件 + 推迟清单）见 [issue #116](https://github.com/verystrongdog/game/issues/116#issuecomment-5557298206)。

*关联: [#114](https://github.com/verystrongdog/game/issues/114), [#115](https://github.com/verystrongdog/game/issues/115), [#117](https://github.com/verystrongdog/game/issues/117), [#118](https://github.com/verystrongdog/game/issues/118), [决策记录](../archive/grilling/grilling-116-disease-gen-evolution/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95-%E5%B9%B3%E5%87%A1%E5%AE%9E%E4%BE%8B%E5%8C%96.md), [NPC人生生成器设计](../events/NPC%E4%BA%BA%E7%94%9F%E7%94%9F%E6%88%90%E5%99%A8%E8%AE%BE%E8%AE%A1.md)*

## [Grilling] #119 — m（髓鞘化）语义层定案：物理基础与认知通道解耦（2026-09-06 开题，闭合）

> Issue: [#119](https://github.com/verystrongdog/game/issues/119) | 维度: 规则 | 形态: 语义层定案（用户质疑 → 事实核查 → 逐题 + 红队攻击收敛）| 状态: ✅ 已闭合（2026-09-06）| 前置: 三体模型 #26 / m 载体定案 #73 / 可塑性巩固 / 调制三因子 v2 | 阻塞解除: 关键突破触发条件（事件队列 #1）

用户质疑：髓鞘化是否已废弃神经链路系统的残留概念？其物理基础（轴突绝缘/传导加速）能否支撑技能成长使用体系？事实核查修正前提：废弃的是 364 pairwise 链路数据（#26）；髓鞘化 m 作为参数保留并已重锚到三体模型 CC+PP 888 边（#73 D1）。物理基础评估：活动依赖髓鞘可塑性（Fields 2015）支撑"使用即成长/不衰退/慢变量"；薄弱点在 m 双重身份（效率 vs 权重）、认知质变硬挂髓鞘。

### 决策

- **Q1（m 语义定位）= A′ 复合成熟度参数**：m := 三体连接功能成熟度（复合抽象参数，髓鞘化为科学锚标签，非逐轴突解剖建模）——整合髓鞘同步效率（Pajevic 2023：活动依赖/持久/慢）、突触权重（增强通道，Frey & Morris 1997）、自动化程度（使用/突破通道）三机制宏观投影。三类增长写入同一标量；三类读出保持原函数（强度 W∝m_mean / 效率 sigmoid(m) / 负反馈 f(m)）。**不变量：公式不得拆解 m 内部成分；出现成分区分需求（如"只快不强"）→ 触发分参（延迟项）**。逐公式核验：Δm 公式/调制 sigmoid/W 权重/阈值类（m≥0.5 涌现、m≥0.7 聚焦、增强上限 0.3）/0.8→1.0 突破——结构全不变，仅物理解释标签降级。
- **Q2（0.8→1.0 语义）= 自动化跃迁**：关键突破 = 受控→自动加工完成（双加工/ACT-R 技能习得锚：认知→联结→自动化）；m 阶段表本身即"受控→自动"轴（初学→熟练→专精→精通→完全自动化）。三型 = 三种自动化路径：去抑制 = 释放自动化（基底节去抑制）、主动抑制 = 控制自动化、悖论整合 = 整合自动化（L4-L5 认知类）。叙事节点 = 催化剂（游戏化压缩，不声称"顿悟直接长髓鞘"伪科学主张）。
- **Q3（调制关系）= 正交声明 + 术语修正**：天花板三因子（兴奋性 Momi / 传导速度 Hansen / 神经调质 Hansen，静态，决定 ceiling/优先级/专精）⊥ m（动态 sync 乘子，不进入 ceiling）。速查表"髓鞘化同步"行改标注 = m 效率读出（非第 4 天花板因子——原"三因子速查"标题与 4 行速查表的术语不一致由此修正）。
- **红队攻击（用户要求）3 漏洞全采纳**：
  - **P1（声明粒度）**：m 内写入 = {使用 Δm、增强+、突破}；**m 外状态 = {标记倍率位、聚焦倍率}**——Q1"整合三机制"原表述把标记位（#73 D4 独立位）误算入 m，修正声明粒度。
  - **P2（激活门控不变）**：m（含 1.0）只经强度/效率读出影响数值，**不改变激活条件**（情境自动激活/聚焦门控照旧）——防"完全自动化=自动施放"泄漏到 P1c/回合流程。
  - **P3（通道分界）**：日常理解（增强 ≤0.3）≠ 叙事质变（突破 0.8→1.0）——突破 = 存在性重组织（自我模型/世界观级事件，与创伤转化/意识外显世界观一致），非技能理解量；突破非均匀适用所有链路。
- **攻击未破**：离散档位表（m0.3/0.5/0.7/1.0 预计算）vs 连续 m（补"连续 m 为引擎口径"标注）；病理边 m 三档（#88）= 病态自动化回路，与成熟度自洽；自动化不衰退（双加工支持）。

### 受影响文件

- `data/term_registry.json`（髓鞘化条目：definition 复合成熟度声明 + deviation_reason + numerical_locations 补调制 v2）
- `design/rules/skill-tree/modulation/链路调制上限参考表-v2.md`（§调制因子速查术语修正 + 髓鞘化同步行 = m 效率读出 + 链路参数表示例档位标注）
- `design/rules/核心机制.md`（§1.3 语义注记块）
- `design/rules/skill-tree/脑功能层级模型.md`（§12.1 关键突破行 = 自动化跃迁语义）
- `design/rules/skill-tree/运行时状态模型.md`（§九 m 语义注记：内外状态分离/两类读出/门控不变）
- `design/decisions/`（本条）+ `design/framework/six-dimensions.md`（髓鞘化成长行注记）
- `../设计归档/grilling/grilling-119-m-semantics/决策记录.md`（决策记录）
- memory（`m-语义层-grilling-119.md`）

### 推迟清单

- 关键突破**触发规则**（哪些叙事节点触发/三型 × 链路类型绑定/m 涨幅）→ 下一个 grilling（原话题 #120 候选，事件维度）
- 三类写入（使用+巩固+突破）合流的数值平衡 → #35 校准轨
- 分参触发条件（m 成分区分需求）——无消费者，延迟
- 术语注册候选：「自动化跃迁」「复合成熟度」——grilling 结束用户裁决是否入库

*关联: [#73](https://github.com/verystrongdog/game/issues/73), [#26](https://github.com/verystrongdog/game/issues/26), [决策记录](../archive/grilling/grilling-119-m-semantics/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)*

## [Grilling] 角色发展轴 — "角色设定"演化载体的引用-组装式设计（2026-09-06 开题，闭合）

> Issue: [#121](https://github.com/verystrongdog/game/issues/121) | 维度: 实体 + 事件 | 形态: 新系统载体设计（#120 Q1 裁定衍生）| 状态: ✅ 已闭合（2026-09-06）| 前置: #120 边界收缩裁定（2026-09-06）/ #119 m 语义定案 / #90 记忆内容层 / #86 剧情正交与条件语法 / #88 创伤转化单向 / 面具装备 #20 | 阻塞解除: #120 关键突破触发规则（触发载体就绪，里程碑接口交付）

**起因**：#120 Q1 用户裁定——突破触发应与角色身心发展进程相关（非仅主线事件）；查证无现成载体 → 拆出 #121 专立"角色发展轴"。

### 决策

- **Q1（载体语义，U1-U3）**：被控角色有初始设定、行为遵循之；经历（选择/受伤/人际伤害类，剧情未写）改变设定；"会思考"= 呈现目标，需物理载体承接。载体 = 模板 × 实例（每可扮演角色 = 模板，受控实例随局演化；身份切换/解锁只影响同存实例数，不改载体结构——复核推迟至角色解锁事件立项）。
- **Q2（设定分解 S1-S6）**：S1 静态内核（不变）/ S2 经历事实（#90，输入源）/ S3 自我叙事内容（变，**只增不减追加式**，D-3b）/ S4 信念断言（变，修正=追加修正记录）/ S5 行为倾向（暂不变，代价待评估）/ S6 既有数值态（接口不装入）。**结构可增删**：设计期配置化 + 受控登记（D-3a）；成分槽运行期不增删；S3 不删减，遗忘仅限未设计的特殊经历机制。
- **Q3（终点语义）= 议题末端 × 无全局完成态（Q-b）**：每模板 **恰 1 条核心议题**（Q-a 方案一）；议题有末端 = "重新安放"形态（内容批次定义）；**无轴满/通关**；轴终态**不消费结局**（OUT-3 摘除，结局公式单独裁定）。否决 T1 无终点轴 / 纯 T3 结局映射。
- **Q4（主流 RPG 校准）**：本设计定位 = 身份涌现型（Disco Elysium 思想内阁 / Planescape: Torment 先例）× 累积态→结局映射（巫师 3 模式，§8.2 已预留）——骨架固定、设定做内容层过滤器；规则化后果（非逐分支手写）保证可扩展性。主流商业 RPG 不做深层自我态是成本信号非结构无效。
- **Q5（冗余性判断）**：结构非冗余——四条已承诺决策（#120 裁定 / U2 / 自问层 / 结局 §8.2）预设载体存在；真正问题是**做多厚**：选 L2（载体 + 每角色 1 议题薄轴 + 只喂 #120，不喂结局）。
- **Q6（初衷确认）**：初衷 = m 突破（0.8→1.0）触发载体（#119 推迟清单 → #120 → 本 topic），叠加 U1-U3 呈现可信度第二初衷。突破 = 排除法后唯一通道（叙事节点直触 ❌ #120 Q1 已否决 / 使用次数累积 ❌ #119 P3 / 对话 effect ❌ #86 正交）。
- **Q7（明悟研究锚）**：C1-C10 共性（前置积累/僵局打破/酝酿/外源催化剂/重构非新事实/Aha 伴随体验/**渐变-突变连续谱**/张力前提/不可强推/事后验证）——双形态实证常态支持"薄轴累积 + 突破跃迁"双层。
- **Q8（复用架构，D-5）**：载体 = 对既有系统的**引用与组装**（#90 / m 突破通道 / 可塑性巩固 §八 / 自问层 / 议题槽）——**无新存储层、无新核心机制**；交付物 = glue 契约 + 输入/输出端点。可行性与 #111 装配层架构立场一致。
- **Q9（双通道复用）**：顿悟 = m 突破通道原样（零改动）；渐悟 = 内容层 #90 记录演化（RC 再巩固 = 信念修正通道，"提取=写操作"）+ 巩固窗口增强通道（m ≤ 0.3 bootstrap）；S3/S4 装进 #90 不新建。m 0.3-0.8 区间任何事件写不了 m——理解类事件只能"入门"（≤0.3）或"跃迁"（≥0.8）。
- **Q10（#90 铁律与分离）**：m 三写入通道（使用 Δm/巩固增强/突破）不动；内容层记录角色 ≤ 事件触发器（同构 #86 条件查 m）；"状态机直写 m"（X2）正式否决、无需修订铁律。**D-6 三条采纳**。
- **Q11（范围纪律，D-7）**：#121 **不含 m 公式设计**——跃迁判定/阈值/涨幅/频率 → #120；数值平衡 → #35；本 topic 只留输入/输出接口。触点范围 = **仅突破通道**（薄版，载体不接巩固窗口）。
- **Q12（端点圈定）**：输入 {IN-1 经历, IN-2 自问, IN-3 线索拼合, IN-5 Boss 思潮}；输出 {OUT-1 里程碑事件 → #120, OUT-2 内容读出 → 呈现}；IN-6 面具/元机制摘除、OUT-3 结局输入摘除、OUT-4 角色解锁延迟、IN-4 创伤记忆处理反向 = **挂起为单独议题**。
- **Q13（里程碑最小定义，Q-c）**：里程碑 = 议题相关记录家族的聚合状态事件；达成条件组合（自问消解 ×N / 记录达 STABLE / Boss 改写……）由内容批次逐角色定义，不写死阈值；事件形状 = 广播 (id, 达成时刻, 源)。RESET 澄清：#90 RESET = 敌方侧语义，玩家议题记录不清零；Boss 触及 = **B1 改写**（RC 式，旧版本保留）。

### 受影响文件

- `design/entities/角色发展轴.md`（新建——正典文档，glue 契约 + IN/OUT 端点 + 议题/里程碑定义）
- `design/events/任务目标系统.md`（§2.3 接口角色注记 + §十一 延迟项更新）
- `design/decisions/`（本条目）
- `design/framework/six-dimensions.md`（实体 ✅ +1）
- `data/term_registry.json`（议题/里程碑/角色发展轴等入库）
- memory（`角色发展轴-grilling-121.md`）
- issue #121 关闭评论

### 推迟清单

- IN-4 创伤记忆处理反向通道（面对创伤→发展）——单独议题，与 #88 单向性一并裁决
- 自问层详细设计（UI/触发/消解/OUT-2 投影）——端点已定，详细设计另开
- 逐角色议题内容批次（14 模板 × 1 议题 + 末端形态 + 里程碑条件）
- #120 定案项：就绪门槛形式 / 三型 × 链路绑定表 / 涨幅频率 / 里程碑可浪费性
- OUT-3 结局输入 / OUT-4 角色解锁 / S5 行为倾向演化 / 轴呈现量化（随自问层）

*关联: [#120](https://github.com/verystrongdog/game/issues/120), [#119](https://github.com/verystrongdog/game/issues/119), [#90](https://github.com/verystrongdog/game/issues/90), [角色发展轴](../entities/%E8%A7%92%E8%89%B2%E5%8F%91%E5%B1%95%E8%BD%B4.md), [决策记录](../archive/grilling/grilling-121-role-development-axis/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)*

## [Grilling] #120 — 关键突破触发规则：里程碑→突破资格→休息执行（2026-09-06 开题，闭合）

> Issue: [#120](https://github.com/verystrongdog/game/issues/120) | 维度: 规则 + 事件 | 形态: 触发规则定案（含 Q1 方向裁定 → 拆出 #121 角色发展轴 → 回炉）| 状态: ✅ 已闭合（2026-09-06）| 前置: #119 m 语义层 + #121 角色发展轴 | 原挂账: 决策树 :579「关键突破 → 独立讨论」

### 沿革

Q1 用户裁定：突破触发应跟**角色本身身心发展进程**相关，非（仅）主线事件 → 查证无现成载体 → 拆出 #121 角色发展轴（先闭合）→ 本 issue 回炉定义里程碑→突破接口。

### 决策

- **Q-A（沉淀对象，两次修正）**：玩家从就绪**技能**（链路上下文组）中选择沉淀，非单条链路（呈现可读性）；共享边跨技能同步受益。修正沿革：先定"选链路" → 用户问链路/技能关系 → 修正为选技能。
- **Q-B（就绪门槛）**：组内**全部边** m≥0.8（瓶颈口径：技能流畅 = 最弱一环也熟）。配套可达性契约：**技能使用激活其上下文组内全部边**（Δm 可达，防最弱边卡死）——技能执行 P1c 输入契约。木桶效应两层分析：数值层求和（Σ ceiling×sync）无严格木桶；行为层自动化=必要环节全熟，木桶成立 → 全边门槛成立。
- **Q-C（三型）**：去抑制/主动抑制/悖论整合 = 突破**加成类型**（机制化推迟到技能系统批次）；型与技能域正交（型=突破方式，技能=突破对象，无锁域——用户问"为何锁域"后裁定伪绑定）。#119 三型文字保留为语义注记。
- **Q-D（突破窗口）**：里程碑 → 激活**突破资格**（暂存、累积不过期）→ 休息时段从就绪技能执行，无额外资源消耗，不浪费（否决即时+可流失 D1——与巩固窗口 §8.3 即时性解耦；顿悟非"此刻捕获"而可沉淀）。
- **词表（玩家语域修正）**：m 阶段正式名 = **笨拙/协调/精通/娴熟/本能**（用户亲定）；旧名（初学/熟练/专精/精通/完全自动化）降级为机制注记；1.0 机制语义 = 自动化加工完成（双加工锚保留）；突破事件内部名"自动化跃迁"保留，玩家可见 = 技能变"本能"。
- **术语语域原则（用户直觉）**：机制术语（工程/学术腔）与玩家侧呈现词分层——技能熟练度描述须是"角色对自身技能释放"的自然语域，非认知科学语言。

### 受影响文件

- `design/rules/skill-tree/关键突破.md`（新建——触发规则正典：触发链/就绪门槛/突破效果/玩家词表/范围边界）
- `design/rules/核心机制.md`（§1.3 阶段表换玩家词 + 词表注记 + 突破引用）
- `design/entities/角色发展轴.md`（§六 #120 消费端定案注记）
- `data/term_registry.json`（新术语：关键突破；髓鞘化条目补阶段词表注记）
- `design/decisions/`（本条）+ `design/framework/six-dimensions.md` + `design/framework/dimensions/事件.md`（关键突破空缺闭合）
- `../设计归档/grilling/grilling-120-breakthrough/决策记录.md` + memory（`关键突破触发-grilling-120.md`）
- issue #120 关闭总结评论

### 推迟清单

- 三型 = 突破加成类型（型特异性效果设计）→ 技能系统批次（#70 P 系列）
- 突破频率/娴熟进度体验/瓶颈口径数值 → #35 校准轨
- 逐角色里程碑达成条件（内容批次，#121 推迟项 3）
- 自问层详细设计（渐悟 UI/OUT-2 投影，#121 推迟项 2）
- IN-4 创伤记忆处理反向通道（单独议题）

*关联: [#119](https://github.com/verystrongdog/game/issues/119), [#121](https://github.com/verystrongdog/game/issues/121), [关键突破](../rules/skill-tree/%E5%85%B3%E9%94%AE%E7%AA%81%E7%A0%B4.md)*

## [Grilling] #122 — Unity 呈现沙盘：可控角色 + 指令→动作→UI 反馈最小闭环（2026-09-06 开题，闭合）

> Issue: [#122](https://github.com/verystrongdog/game/issues/122) | 维度: 呈现 + 管线 | 形态: 载体决策 + 工程交付 | 状态: ✅ 决策闭合，实施待本机验证 | 起因: 状态面板细部规格 grilling 被用户依赖顾虑拦截（无可控角色可调试前纸面 UI 不可行）

### 决策

- **D1（载体与范围）**：`code/unity/` 工程骨架 + 单场景白盒演示场——移动(WASD 自由，非战棋网格) + 基础行动(1=物攻/2=防御/3=精攻)；不含回合全量/网格/敌方AI/脑区3D。呈现验证载体，非正典实体模板。
- **D2（结算驱动）= 轻量手动回合沙盘**：每回合选 M1 动作 + Broca 动作 + [执行回合] → 玩家动作 → 陪练简单 AI → 冷却/防御按行动窗口口径（回合流程 §9）；不触碰引擎 TurnManager。简化注记：M1→Broca 固定顺序、射程 2.0/6.0m 演示常量、陪练 AI 非 NPC Affordance Competition。
- **D3（版本/目录）**：Unity 6 (6000.0.83f1)，目录 `code/unity/`（.gitignore 已预留）。
- **D4/D5（角色模型）**：暂无外部模型 → 白盒人形 + 程序化动作；`CharacterVisual` 为模型接入点（外部模型目标保留）。
- **D6（引擎消费）⏸ 挂起（Q6b）**：选定"附加 netstandard2.1 桥接项目"方向；实施时暴露兼容墙——netstandard2.1 缺 `ArgumentNullException.ThrowIfNull`（71 处/22 文件）、collection expressions(C#12)、records(IsExternalInit)。子集桥接（4 文件 + DamageCalculator.cs 1 处引擎改动）vs 全量引擎重构（71 处）待用户定案。当前 `WhiteboxSolver` 临时镜像 `CalibrationConfig.Default`（替换透明）。
- **D7（UI 集）**：uGUI——左下状态面板（HP/SAN 条+数值、防御/冷却/回合标签）+ 右下行动栏（1/2/3/执行/重置）+ 日志；陪练头顶精确数值标注为**调试显示**（非正典敌方模糊规则 §3.8）；无 AP 显示（正典不设 AP）。
- **验证环境裁决**：沙箱装 Unity 6000.0.83f1 成功但 **Personal 许可激活死锁**（无 Secret Service 钥匙串 → unity-cli OAuth 令牌无法落盘 → `license activate --personal` 强制已登录会话；无 root 无法装 gnome-keyring；deb 依赖链 libgcr-base 缺失）→ 验证环境 = 用户本机（Windows unity-cli 登录已验证 ✅）。
- **法律核查采纳**：2026-06-30 ToS §17.2 AI-agent 条款——本地 Editor+项目文件工作流属官方澄清范围外（不触发）；缓解措施：仅本地 Editor/用户账号/项目、官方 CLI、不触云端服务/不训练/不爬取。

### 受影响文件

- `code/unity/`（新工程：Assets/Scripts 8 文件 + Assets/Editor/SceneBuilder + Assets/Tests/PlayMode 冒烟测试 2 例 + Packages/manifest + ProjectSettings + README）
- `.gitignore`（code/unity/ 产物 + .unity-editor/.unity-home/.nuget-* 本地安装）
- `code/src/YouAreNotTheFish.Core.Unity/`（⏸ 桥接项目草稿，Q6b 定案后启用）
- `../设计归档/grilling/grilling-122-unity-slice/决策记录.md` + `design/framework/six-dimensions.md` + `design/decisions/`（本条）
- 本机验证：打开 `code/unity/` → YANTF→创建 Demo 场景 → Play / PlayMode 测试

### 推迟清单

- Q6b 桥接范围定案 → EngineSolver（DamageCalculator 直连）替换 WhiteboxSolver
- 状态面板细部规格 grilling（本沙盘为 UI 调试底子，回炉）
- 外部人形模型接入 → 见 [#123 动作库规格](#grilling-123--unity-沙盘角色动作集规格动作受控词表--动画来源--引用契约2026-09-07-开题闭合)（动作面已规格化，接入=下游消费者）；unity-brain-connect 神经演示（复用本工程阶段 0.1）

*关联: [#122 决策记录](../archive/grilling/grilling-122-unity-slice/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [code/unity/README.md](../../code/unity/README.md)*

## [Grilling] #123 — Unity 沙盘角色动作集规格：动作受控词表 + 动画来源 + 引用契约（2026-09-07 开题，闭合）

> Issue: [#123](https://github.com/verystrongdog/game/issues/123) | 维度: 呈现 + 管线 | 形态: 呈现资产规格（工程级，非正典实体模板）| 状态: ✅ 决策闭合，实施待进行（Batch 0-2）| 前置: #122 呈现沙盘载体 + KiWalkerLab Humanoid/Animator 路线验证 | 起因: 用户观察——AI 仅在"简单动作引用"上可信，复杂度上升可信度即崩；计划以现有骨架先做厚动作库供后续功能简单引用，兼作 Unity 学习路径

### 沿革

用户 Q1 反问"没仔细考虑过要用哪些动作" → 词表改**自上而下需求推导**（消费源：基础行动/移动/战斗反馈/回合扩展面/状态姿态/NPC 行为演示/对话言语/休息）；调查业界流行动作分桶惯例与"为何主流不用纯代码引用"；对照工程内三实例（白盒程序化 / KiWalkerLab 纯状态+CrossFade / SitCheck 手工）。

### 决策

- **Q1（词表结构与范围）**：分层二维判定（Q-a 消费端就绪 × Q-b 来源就绪）→ L1 落地（接动画）/ L2 登记（锁名+资产锚）/ 不入表（扩展协议快轨）。**12 词条**：L1=9 `{Idle,Walk,Run,Jump,PhysicalAttack,MentalAttack,Defend,HitReaction,Down}`；L2=3 `{Sit,Stand,Talk}`。不入表：逃跑/投降/借机（#122 D1 排除）、恐慌/警觉/冻结/随机行为（呈现形态未设计）、技能动画（P1 技能接入另立）。
- **Q1b（分类标签）**：词条带 `category ∈ {locomotion, combat, reaction, social, interaction, status}`（对齐业界分桶，可检索）。
- **Q2（内容形态）**：物攻=空手直拳；精攻主形态=**A 前指宣言**（B 言语压迫 / C 凝视威压 = 变体候选；变体字段入词表，本期每动作 1 clip）；防御=循环护前格挡；受击=单型通用（精神受击差异留反馈动画）；倒下=倒地停留末帧。
- **Q2b（来源矩阵）**：L1 缺口 5 动作 = Mixamo 优先 + 程序化兜底（白盒参数现成）；`source ∈ {KI引用, Mixamo引用, 程序化, 制作}`。
- **Q2c（工作流/命名/许可）**：Mixamo 批量 zip（每动画一 FBX）→ Humanoid 导入 `Assets/Animations/Mixamo/Combat/` → **资源名=词表 id**；许可逐词条记录（KI/Mixamo 免费，Mixamo 禁独立转售）。
- **Q2d（分工）**：Editor 内操作**全用户手动**（学习目标）；AI 只产代码/文档/测试；代码同步 = AI 提交 → 用户 pull。
- **Q3（引用契约）= 形态 A**：纯状态集 + 运行时 `CrossFade`（零参数零手动 transition；状态名=词表 id=代码字符串三面对一）；衔接 = C# 优先级 `Down > HitReaction > 一次性动作 > locomotion` + 计时回待机 + fade 参数；位移全走 CharacterController（无 RootMotion）。工程先例 = KiWalkerLab。**升级触发器写入规格**：① 连续速度/方向混合 ② 层分离 ③ 组合复杂度超 C# 可读 → locomotion 迁 B/混合（一次性动作可留 A）。
- **Q4（载体）**：新建 ActionLab 动作演示场（无回合逻辑）+ 可复用 `ActionPlayer` 组件；DemoSandbox 白盒换真人 = 下游消费者（用户裁定：新场景不值得独立讨论，压扁为默认）。
- **Q5（实施批次）**：Batch0 词表规格 + C# `ActionIds` 机器源（非 JSON，JSON 化=升级触发器之一）+ `ActionPlayer` + PlayMode 断言；Batch1 用户手动（Mixamo 导入 + 9 状态手摆 + 挂组件）；Batch2 手感调 fade + 测试绿 + 收尾。

### 受影响文件

- `design/presentation/动作库规格.md`（新建——词表 12 词条 + 元规则 + 契约 A + 来源矩阵 + 批次）
- `../设计归档/grilling/grilling-123-action-vocabulary/决策记录.md`（新建）
- `design/decisions/`（本条 + #122 推迟项注记「外部人形模型接入 → 见 #123」）
- `design/framework/six-dimensions.md`（呈现 ✅ +1；反馈动画空缺依赖更新）
- `code/unity/README.md` + `design/README.md`（入口链接）
- memory（`动作集-grilling-123.md`）

### 推迟清单

- ActionLab 实施（Batch 0-2，用户手动为主）→ 见 [#124 ActionLab 动作填充尝试](#grilling-124--actionlab-动作填充尝试载体锚定-mixamo-x-bot--执行形态2026-09-08-开题闭合)
- DemoSandbox 白盒换真人模型（消费者，反馈动画 grilling 期）
- 精攻变体 B/C 与受击多态填充（变体通道就绪）
- 词表 JSON 化（数据驱动需要时）
- 反馈动画方向 grilling（动作底子已备 ✅）

*关联: [#123 决策记录](../archive/grilling/grilling-123-action-vocabulary/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [design/presentation/动作库规格.md](../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [#122](https://github.com/verystrongdog/game/issues/122)*

## [Grilling] #124 — ActionLab 动作填充尝试：载体锚定 Mixamo X Bot + 执行形态（2026-09-08 开题，闭合）

> Issue: [#124](https://github.com/verystrongdog/game/issues/124) | 维度: 呈现 + 管线 | 形态: #123 推迟清单首项启动（实施执行层）| 状态: ✅ 决策闭合，Batch0 实施待交付 | 前置: #123 动作库规格（词表/契约 A/批次/防漂移）| 起因: 用户启动「尝试根据动作词表填充动作」；纠结 AI cli 直驱 Unity 的方便与复杂任务不可靠

### 沿革

上午 ChatGPT 会话总结（共享 `6a9f893d`）经攻击审查 → 无可采纳新机制/修改（用户裁定）；用户顾虑「成规模 AI 操作」→ 分域原则（AI 直驱安全 = 结果可读回自证 + 判据非人眼）+ 粒度闸门 + Jump 1 词条试点校准；载体问题逐文件二进制解析核验（X Bot/Y Bot 角色 + 5 条无蒙皮动画 + Taunt=Beta+嘲讽）；Q-B1..5 逐题定 Batch0 契约。

### 决策

- **Q0（执行形态）**：Batch0 代码先行（AI 零 Editor 操作）→ 用户 pull → 本机导入/生成/Play → Editor+pipeline 就绪后 Jump 1 词条 AI 直驱试点，实测定 Batch1 形态。
- **载体锚定（🔧 #123 闭合后修正）**：ActionLab 演示载体 = Mixamo **X Bot（默认）/ Y Bot（备用）**，替换 KI dummy；KiWalkerLab 保留对照。词表 12 条中 7 条来自 Mixamo → 载体锚 Mixamo 侧，retarget 面压到最小（仅 5 条 KI 通用动作），高风险接触动作全原生。`Taunt`/Beta 不入表不入载体。
- **Q-B1（机器源）**：`ActionIds` 12 词条常量 + `ActionCatalog` 只读元数据（id → {category, loop, priority, fade, clipFbxPath}），单一机器真相，不越「JSON 化=升级触发器」边界。
- **Q-B2（controller 生成）**：幂等 `ActionLabBuilder`（菜单触发，用户操作）；状态名=id 由构造成立；缺口状态先建、clip 留空 + 警告清单。
- **Q-B3（ActionPlayer 作用域）**：含 locomotion 通道（Move(speed)→Idle/Walk/Run）+ Play(id) 优先级覆盖；CC 位移 applyRootMotion=false；闭合目视清单 ① 与 X Bot retarget 验证。
- **Q-B4（L2 落点）**：ActionIds/Catalog = 12 词条全量（level 标注）；controller 仅 L1 9 态；Play(L2 id) → warning；L2→L1 待消费端就绪。
- **Q-B5（防漂移断言分档）**：按 clipFbxPath 资产存在性分档——存在→断言有 clip；不存在→断言状态存在且 clip 为空（显式待填）；随导入自动升级（Batch0 4/9 → 导入后 9/9）。
- **Q-m（来源实证映射）**：5 条 Mixamo clip 无蒙皮下载核验：Jab Cross→PhysicalAttack、Charge→MentalAttack（伸手指人=A 前指宣言）、Short Left Side Step→Defend（循环格挡）、Head Hit→HitReaction、Dying→Down；文件名≠语义以预览/Play 为准。

### 受影响文件

- `../设计归档/grilling/grilling-124-actionlab/决策记录.md`（新建——决策表/写入验证表/推迟清单）
- `design/presentation/动作库规格.md`（🔧 闭合后修正：载体 + 来源矩阵实证）
- `design/decisions/`（本条 + #123 推迟项「ActionLab 实施 → 见 #124」）
- `design/framework/six-dimensions.md`（呈现行 + footer）
- `code/unity/README.md`（§二·E ActionLab 实施手册）+ `design/README.md`（入口）
- GitHub：Issue #124 关闭总结；#123 🔧 闭合后修正评论
- memory（`动作集实施-grilling-124.md`）

### 推迟清单

- Jump 1 词条 AI 直驱试点（依赖用户本机 Editor + pipeline 就绪）
- Batch1 用户执行（X Bot 导入 + 5 clip 改名 + 菜单生成 + Play 目视验收）
- 物攻单次直拳语义 / HitReaction 通用性（Play 后判）
- L2（Sit/Stand/Talk）接线（消费端就绪时）
- Batch0 代码实施（ActionIds/ActionCatalog/ActionPlayer/ActionLabDriver/ActionLabBuilder/ActionLabSmokeTests + README §二·E）——同会话交付

*关联: [#124 决策记录](../archive/grilling/grilling-124-actionlab/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [design/presentation/动作库规格.md](../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [#123 决策记录](../archive/grilling/grilling-123-action-vocabulary/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [#124](https://github.com/verystrongdog/game/issues/124)*

---

## [Grilling] #126 — Unity 玫瑰花海场景：真实草原 DEM + 商业化密度株丛 + 小人穿行（2026-09-12 开题，闭合）

> Issue: [#126](https://github.com/verystrongdog/game/issues/126) | 维度: 呈现 + 管线 | 形态: 独立技术验证 lab（**不入正典**）| 状态: ✅ 决策闭合 + 代码落地 + **本机 Unity 实测通过** | 前置: #122 呈现沙盘骨架（`WalkerController` 复用）| 起因: 用户「我希望通过 unity 生成一片玫瑰花海，我能够控制一个小人在其中穿行」

### 沿革

全项目 `grep 玫瑰|花海|植被` 仅命中 `../规格/素材` 内书名《春姨和玫瑰花》→ 花海在既有设计文档中不存在，属新话题；决策树与 gh issue 查重均通过。Step 3 数学语言规范打断 3 次（「一片」量词缺失 / 「轻微」阈值模糊 / 「一块」「商业化种植密度」枚举未受控）→ **用户显式豁免 CLAUDE.md 该规范**（「本次实验我提供权限」）；豁免仅限本会话，**CLAUDE.md 文件本体未改动**。用户裁定交付边界 = 纯技术验证 lab。检索路径：先排除全球 DEM（30 m / 10 m 在 100 m 地块下样本不足）→ 锁定 USGS 3DEP 1 m lidar → 实检 4 个草原候选地全部有 1 m 覆盖 → 2 km 瓦片扫 1444 窗取最平。

### 决策

- **D1（地块数据源）**：USGS 3DEP **1 m lidar** DEM（Konza Prairie 高草草原，源产品 `KS_Statewide_2018_A18` / `S_Central_NE_NW_Kansas_Lidar`），公有领域。排除 SRTM/Copernicus GLO-30（30 m，100 m 内仅 3×3 样本）与 NED 1/3 arc-sec（≈10 m，仅 10×10 样本）。
- **D2（选取判据）**：2 km 瓦片内扫全部 101×101 px 窗口，`argmin relief`，约束 `relief ≤ 3.5 m ∧ std ≤ 0.7 m` —— 把「轻微起伏」换成可机械核验约束。
- **D3（地块实测）**：100×100 m，101×101 @ 1.0 m；relief **3.1075 m**，std 0.5665 m，最大 1 m 高差 **0.1145 m（6.53°）**；中心 39.095390°N / 96.578843°W。对照：瓦片中位高差 16.00 m、整瓦片 94.56 m。
- **D4（地面实现）**：程序化 Mesh（101×101 顶点）+ MeshCollider，**不启用 Unity Terrain 模块**（`manifest.json` 未列 `com.unity.modules.terrain`）。
- **D5（种植密度）**：**300 株/亩**，落于文献区间 [180, 330]（平阴县人民政府栽培技术 + 农博数据中心，两源互印；算术校验 `1/(行距×株距)` → 185–333 株/亩 自洽）。
- **D6（布置）**：六角错行 **s = 1.602 m**（行距 s√3/2，奇行偏移 s/2）→ **N = 4563**，实测 **304.2 株/亩**；三角格每株 6 最近邻距离恒 = s。
- **D7（覆盖率判据）**：三角格覆盖半径 = `s/√3` → 全覆盖充要条件 **`D ≥ 2s/√3 = 1.8498 m`**；取 D = 1.85 m → 覆盖率 1.0、冠层投影比 1.209 —— 把「整片区域完全覆盖」换成显式几何判据。
- **D8（株丛资产）**：程序化低模 5 茎 + 8 叶 + 5 花 × 6 瓣 = **106 tri**，零外部资产（同 `WalkerController.BuildBody` 口径）。
- **D9（渲染）**：**每株一个 GameObject**（MeshFilter + MeshRenderer 共享网格与材质，材质开 GPU Instancing 自动合批）；**株丛无碰撞体**（「穿行」语义）；阴影投射关闭；株丛对象运行时生成（不烘焙进场景）。🔧 **实测后修正**：原定 `Graphics.DrawMeshInstanced` 即时模式 —— 实测其绘制不进 `capture_game_view --source camera` 抓帧路径、也不出现在编辑器 Scene View，改用真实 GameObject。
- **D10（小人载体）**：**`WalkerController`**。事实排除另两者：`AnimatorWalker` 与 `ActionLabDriver` 的 locomotion clip 均指向 `Assets/Kevin Iglesias/...`（不在仓库）→ 走/跑态为空。
- **D11（场景生成）**：新 Editor builder + 菜单 `YANTF → 玫瑰实验 → 创建玫瑰花海场景` → `Assets/Scenes/RoseFieldLab.unity`（沿 `WalkerLabBuilder` 先例）。
- **D12（相机）**：第三人称跟随，`cameraOffset = (0, 3.0, −6.5)`，略高于 1.25 m 冠层。

### 本机实测（2026-09-12，Unity 6000.5.2f1 + Unity CLI `com.unity.pipeline`）

用 Unity CLI 直驱编辑器跑通全链路，取代「交付代码待用户验证」：编译 `failed:false / errors:[]` → 菜单生成场景（日志 **株数 4563 / 密度 304 株/亩 / 间距 1.602 m / 蓬径 1.85 m = 判据 1.850 m → 覆盖率 1.0 / 地块高差 3.1075 m**，与 D3/D5/D6/D7 预测逐项一致）→ PlayMode 测试 **玫瑰 4/4 通过**（全项目 16 项 14 过 2 败，败项为 ActionLab 既有）→ Play 截图回读 **红色像素 8.04% / 草地 68.4%**，运行时层级 `RoseField(玫瑰花海)/Roses` 下 4563 个 MeshRenderer。

**排查中发现两处根因（均已修复）**：① `Run In Background` 默认关闭 → 编辑器失焦时**玩家循环停止**（`Time.frameCount` 4 秒不动），场景照常渲染但 `Update` 不再执行，表观症状＝「玫瑰一株都不渲染」；builder 现显式设 `PlayerSettings.runInBackground = true`。② **即时模式绘制（`Graphics.DrawMesh*`）不进 `capture_game_view --source camera` 抓帧路径**，故改真实 GameObject 渲染（见 D9 🔧）。方法论提醒：截图验证必须先做帧新鲜度断言（本次用两次截图 md5 比对）—— 冻结帧会让整条排查链建立在错误前提上。

### 受影响文件

- `../设计归档/grilling/grilling-126-rosefield/决策记录.md`（新建——决策表/本机实测/写入验证表/校验结果/推迟清单）
- `design/presentation/地块数据-Konza草原.md`（新建——数据源/判据/实测/口径/复现命令）
- `design/presentation/玫瑰株丛密度.md`（新建——密度文献/布置/覆盖率判据推导）
- `code/unity/Assets/Resources/YANTF/konza_plot_101x101_r16.bytes`（新建——高度图 20 402 B）
- `code/unity/Assets/Scripts/HeightField.cs`、`RoseMeshFactory.cs`、`RoseFieldLab.cs`（新建）
- `code/unity/Assets/Shaders/RoseInstanced.shader`、`code/unity/Assets/Editor/RoseFieldLabBuilder.cs`、`code/unity/Assets/Tests/PlayMode/RoseFieldSmokeTests.cs`（新建）
- `code/unity/README.md`（§二·F 新增 + §三 结构树 + footer）
- `design/framework/six-dimensions.md`（呈现行 + 管线行 + footer）
- GitHub：Issue #126 关闭总结
- memory（`玫瑰花海实验-grilling-126.md`）

### 推迟清单

- 用户本机 Unity 验证（编译 / 菜单生成 / Play 目视 / 帧率）
- `Graphics.DrawMeshInstanced` 12 参重载与自定义 shader 编译为首验点 → 退路：`Graphics.RenderMeshInstanced` 或 `Shader.Find("Standard")`（`MakeRoseMaterial` 已内建 fallback）
- 花瓣/叶片背面偏暗（Lambert + Cull Off）→ 后续可换双面光照
- 遮蔽剔除 / LOD / 视锥分块（当前 4563 株全量提交）
- 花海入正典（若需要）→ 回空间维度 grilling（三层空间归属 + 月光分布接口）

*关联: [#126 决策记录](../archive/grilling/grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [地块数据-Konza草原](../presentation/%E5%9C%B0%E5%9D%97%E6%95%B0%E6%8D%AE-Konza%E8%8D%89%E5%8E%9F.md), [玫瑰株丛密度](../presentation/%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md), [code/unity/README](../../code/unity/README.md), [#126](https://github.com/verystrongdog/game/issues/126)*

---
*创建: 2026-09-12（由 design/decisions/ 拆分）| 更新: 2026-09-12*
*关联: [决策树总索引](README.md), [设计框架-六维状态](../framework/six-dimensions.md)*
