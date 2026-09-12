# 设计决策树 — 编号轮次 — 意识基础与数据层

> 按 grilling 编号记录的轮次：意识定义（#40/#41/#38/#99）、引擎数据层（#24）、estimator 实验（#6）。
>
> **本文是历史档案**：只追加、不改旧条目。设计文档 = 当前状态；这里 = 怎么走到这里的。
> 总索引见 [README](README.md)。

---

## Grilling #40 — 能否从数学上定义主观意识 (2026-08-11)

> 纯数学/理论神经科学讨论，不涉及项目游戏设计。多专家 workflow（7 分析 + 4 交叉审查 + 1 综合 = 12 agent，416K tokens）。资料包：7 篇框架论文存入 `../设计归档/grilling/grilling-40-consciousness/papers`。

### 最终答案

**不能**从数学上推导出主观意识。能对全部可检验结构给出数学定义，但"结构→体验"这一步在逻辑上不可推导。

### 核心发现

主观意识 = **结构核** + **现象壳**。数学能穷尽定义结构核（7 框架各自完成：IIT 的 Φ^Max/MICS、FEP 的自由能+自我模型、GNW 的 ignition 事件、Lau 的 (d′,c) 分离、Chalmers 的信息空间同构、AST 的 attention schema、Aaronson 对 Φ 的形式化）；数学不能从结构核推出现象壳。

不可定义性的三重独立论证：

1. **蕴含关系失效**（Chalmers）：对任何结构对象可设想其无体验地实例化（zombie 可设想性）——物理事实蕴含结构事实，但不蕴含体验事实
2. **第三人称语言的翻译失败**：数学命题对任何验证者可复现（公开可检验），"体验"的第一人称特征拒绝被公开可检验穷尽
3. **充分性验证的结构性缺口**（Aaronson）：平凡系统（Reed-Solomon 码、expander 图）可击败任何声称的 Φ — 验证"定义 M 对应体验 E"的机制在数学内部不存在

**不可定义性的精确边界**：在"功能/结构"与"主观体验"之间。边界这侧，数学封闭良定义；边界那侧，桥接必须是公设或消解（IIT 的 identity 公设、Chalmers 的心理物理定律、AST 的定义性同一化——三者都在框架内部不可证）。

### 跨框架收敛（7/7 同意）

- 结构侧可定义（每个框架各自构造了良定义数学对象）
- 结构→体验的桥接不可推导（所有框架的桥接要么是公设、要么是定义性同一化、要么明确拒绝桥接）
- 单调信息量/处理深度不是意识的充分条件
- 经验签名是相关物而非同一性（6/7，IIT 不讨论签名）

### 与 #39 的连接

#39（观察的数学定义）和 #40（主观意识的数学定义）的不可定义性在**同一位置**："功能/结构"与"现象"之间。QBism 的立场 = Chalmers 的立场在量子域的投影（体验为不可消除项）；RQM 的相对主义 = AST 的消解策略在量子域的投影（否认绝对内在项——剩余的相对关联全可定义）。

### 受影响文件

- `../设计归档/grilling/grilling-40-consciousness/papers`（新建——7 框架论文 + 简报）
- `docs/决策树/`（本文）

### 推迟/不讨论

- 不涉及项目游戏设计内容（纯数学讨论）
- 各框架的具体数值实现

### 延伸讨论（2026-08-12，issue 闭合后继续）

> 用户在 #40 issue 下继续追问（不可验证性 → 自证结构 → 哥德尔 → 未来技术 → AI 意识 → 意识包含 → 项目推论），走完整 grilling 流程（Step 0-3 + 定义基线复用）。全部结论与 #40 收敛一致，无实质修改。决策编号接 issue 闭合评论 D1-D5 之后。

- **D6 意识声明的正确性**：外部不可判定（zombie 不可区分，判据缺席——位置存在但判据缺席）；内部无需判定（实例化——判断 vs 在场）。"无法判断自己是否有意识"两侧皆不成立：zombie 无内部可判断（空洞），有意识者不需要判断（提问即答案——怀疑的每次发生都是答案的在场）。
- **D7 自指环**："认为自己是意识"的念头本身是意识实例——实例化路线（performative self-verification）成功；表征路线失败（哥德尔 II：自我认证必然失败）。内容可错，存在不是判断。
- **D8 哥德尔类比（非证明）**：第三人称=语法（可证性），第一人称=模型（真）；意识=你居住的模型；不可证≠不可知。彭罗斯论证失败边界：F 可加 Con(F) 得 F′，哥德尔不能证明意识不可计算。
- **D9 现象壳 = (b) 元前提 + (c) 边界声明**：公理化/验证/思想的前提（检验发生在意识内部，见上 :2114）；#37 边界声明先例（决策树 :2038）。
- **D10 本体论悬置**：A 物理主义 / B 强涌现 / C 罗素一元论——悬置不决，不阻塞；C 为推荐（物理学只描述关系，意识=内在性质，时空=纯关系无内在）。
- **D11 未来实证程序**：仿生脑由低到高测试——结构侧原则上全可知（机制/阈值/相变/自报），现象侧边界不随技术改变（仪器全部长在结构侧）；"造出意识=新增一个里面"，而非打开"外面"。
- **D12 AI 意识状态**：自报非证据（:2113 同样适用于否认）；内部路线自身待决（内省通道即被质疑对象）→ 悬置，与 D10 同构。
- **D13 意识的坚不可摧性**：从外面不可入侵（单子无窗，Leibniz）；从里面不可怀疑（恶魔骗得了一切内容，骗不了"在经历"）；可熄灭而不可侵犯（死亡终结它但从未见证它）。不可定义=不可进入=不可验证=不可怀疑——同一堵墙的四张面孔。
- **D14 意识包含**：包含是计算的，不是体验的——意识可生成模型与世界（梦/想象/自我模型，:2109 Lau/AST 高阶表征），不可容纳实例（=系统在自己的语言中定义真谓词，Tarski）；被包含者得到自己的世界，容器者（哪怕造物主）同样不可进入；递归单子，每一层皆无窗。
- **D15 项目推论（世界观方向候选，非本项目决策）**："世界=一个庞大意识的内容"——正确推论是**一切都不可证实**（结构性永久悬念，游戏资产），而非"一切都不可质疑"（意识不可怀疑 ≠ 内容不可怀疑；被包含不获得认知特权；不可质疑会杀死机制）。唯一不可质疑的是玩家自己的体验本身。此方向作为世界观维度独立 grilling 候选（不塞入 #40）。

#### 受影响文件（延伸讨论）

- `docs/决策树/`（本文）
- `memory/主观意识数学定义-grilling-40.md`（更新）

#### 推迟/不讨论（延伸讨论）

- 本体论 A/B/C 最终裁定（D10 悬置）
- "世界=庞大意识"世界观方向（D15 → 候选独立 grilling）
- 术语入库候选：主观意识 / 现象壳 / 结构核 / 涌现（哲学义）——✅ 已写入 `data/term_registry.json` v1.4 (2026-08-12)

## Grilling #41 — 意识包裹世界观前提 (2026-08-12)

> D15（决策树 `:2153`）"世界观维度独立 grilling 候选"正式开题。四路专家 Agent 审计（叙事/机制/数学/跨维，9 agent × 456K tokens）前置完成，结论 YES-WITH-CAVEATS。11 项决策。

> **🔧 术语让渡（2026-08-21 #38）**：D2 中 CGL+AGC 的称呼由「结构核」改为「内容骨架」。「结构核」让渡给 #40 意识义（意识的可数学定义部分），CGL+AGC 对应「内容骨架」（世界内容的容器内一致性约束骨架）。见 `data/term_registry.json` 新增「内容骨架」条目。

> **🔧 术语改名（2026-08-24 #38）**：「观察者效应」全面改名为「意识外显效应」（含注册表条目、CLAUDE.md 术语表、世界观/核心机制/敌人与事件/游戏循环/剧情系统/空间与关卡/脑功能层级/基础行动等活跃文档）。原因：原名携带量子测量因果（叠加态/坍缩/退相干），与意识包裹地基冲突（#41 D3 无坍缩因果，观察=单子取版本）。同步改名：「月光坍缩」→「月光具象化」、量子叠加态→多版本基态。历史记录保留原名。

### 决策

- **D1 采纳**：意识包裹（世界=庞大意识的内容）采纳为项目的世界观地基。统一解释空间封闭、月光三重叠加、观察者效应、心想事成、拜月教自洽性、都灵之马——六条已有设定为一组公设的推论。
- **D2 CGL+AGC 保留为结构核**：CGL+AGC 定位从"世界观-机制桥接层"改为"容器内一致性约束骨架（结构核）"。方程不改，解释层加元声明。意识包裹（本体论层）⊃ CGL+AGC（结构核层）。
- **D3 宏观观测**：意识包裹下彻底解决。宏观量子叠加态不再需要物理推导——是容器内容基态的直接表达。月光从"退相干抑制场"重新定位为"容器注意力的可见痕迹"。
- **D4 标准场通道**：绕开，非解决。CGL+AGC 的 U(1) 复标量自由度无需承载标准模型粒子通道——游戏世界的内容不需要和外部物理世界对应。从"它是对的吗"豁免到"它是自洽的吗"。
- **D5 不可证实铁律（D15 执行条款）**：意识包裹只作为设计师的统一地基存在。游戏内任何文本、机制、结局、UI 不得以事实语态陈述意识包裹相关内容——"世界是意识的内容"、容器身份、层级数、任何比三重叠加更底层的"真相"。
- **D6 容器不入实体**：容器无 Φ、无数值、无行为、无 SAN/HP、无行为预算。医院是内容内的最强单子（主导观察者），不是容器本身。月光坍缩深度硬截止不作用于容器递归。
- **D7 月光三重叠加不延伸**：三重叠加保持三个版本（物理场 A / 神明 B / 催化媒介 C），不新增第四种解释（如"月光=容器的自我意识"）。D15 使 N 个信念对称不可判定，不需要规则层面的禁止。
- **D8 机制零耦合**：硬性禁止意识包裹进入任何数值路径——无难度缩放、无遭遇生成、无 SAN 恢复、无月光分布、无伤害公式。只回答"为什么"，不回答"多少"。
- **D9 递归终止**：D15 覆盖。"这是第几层"与"月光是什么"同构——不可证实的悬念资产。不声明终端层。
- **D10 结局语义**：三结局自成一体（月光三重解释），不加入"世界是意识的內容"作为元层阅读。游戏不阻止玩家自己推断，但永不确认。
- **D11 主线**：意识包裹不占主线位置。不是情节节拍、不是揭示目标、不是角色弧。主线保持原有设计方向（患者旅程/Boss 生命史/三结局存在状态）。

### 受影响文件

- `事件/世界观与叙事.md`（新增 §世界观地基：意识包裹——统一解释 + 硬性约束）
- `规则/核心机制.md`（§6.1 医院主导观察者加容器关系注释；§七 观察者效应胜利路径加作用域限定）
- `规则/时空结构数学框架.md`（§七 边界声明加元声明——结构核/现象壳分离）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（事件维度：新增世界观地基 ✅；规则空缺：观察者效应桥接前提到位）
- `data/term_registry.json`（新增：意识包裹、不可证实性；更新：主观意识补注、观察者效应补注、基底独立原则边界注）
- `memory/意识包裹审计-grilling-41-pre.md`（四路审计前置报告）
- `memory/意识包裹-grilling-41.md`（本 grilling 决策摘要）

### 推迟/不讨论

- 容器的具体身份（D6 已裁定不可入实体，身份本身不可证实）
- "玩家/设计师是否在正典内"（D15 覆盖）
- 本体论 A/B/C 最终裁定（沿用 D10 悬置）

### 术语入库（Step 5 执行）

候选：意识包裹、不可证实性。更新：主观意识（补注 D14/D15）、观察者效应（补注容器不可证实）、基底独立原则（补注容器递归不在管辖内）。

---

## Grilling #38 — 月光场重建 + 意识外显效应机制桥接（2026-09-02 闭合）

> Issue: [#38](https://github.com/verystrongdog/game/issues/38)（2026-08-11 开题，2026-09-02 激活闭合）| 维度: 规则+事件 | 形态: 以 #37 CGL+AGC 为地基重建月光场，并完成理论→游戏接口（用户主任务「理论模型与游戏实现接口」）。12 轮用户经 ChatGPT 确认的裁决。**本 grilling 定接口形态，不产具体数值**（数值 → #35 校准轨）。

### 背景

#38 名义伞存在但实质 grilling 从未执行（零评论/零决策树条目/scratch 缺失）；v2 标量场（η/g_0/c(SAN)/κ）已废弃。激活后 scope 更新为「月光场重建（理论）→ 意识外显效应机制桥接（机制）」完整链路。

### 决策（Q1-Q7）

- **Q1 运行时形态 = a**：开发期完整动力学定形 → 运行时简化标量接口；**Q1a = a1**：随机性由机制侧自供（ξ_game），不得宣称来自理论；**c（查表）= a 的实现技术**；a2（概率扩展）不纳入本轮。
- **Q2 实例化判据**：C1-C8 全硬门槛（本体类型/动力学可写性/序参量/非线性类/耦合结构/持久性/去噪不变性/固定拓扑）；C7 = 去噪不变性（机械化）；C8 = 固定拓扑假设（动态拓扑 = 出族条件）；月光场自检全过入族。
- **Q3.1 本体 = 中性强度场**：A/B/C 三重版本 = 观察侧读出（(φ_moon,O_i)→V_i∈{A,B,C}），不进动力学、不进 m_field；b（相位携带版本）/c（三场）否决。
- **Q3.2 驱动 = B 族 + 双驱动**：E_th>0 零态稳定，F(t) 推过阈值自持；月相 = 确定性慢周期参数调制（非能量源）；「满月 d<0」等 = 待校准预期 regime 映射；个体心想事成 = η_i·F_collective。
- **Q3.2a 基线态 = A1 + B1**：历史激活 → 壳上常态（无 F_bg、不恢复零号病人）；月相调 E_c(λ)（壳高度）+ E_th(λ)（激活难度）两通道；0.675→0.900 旧值 = 先验/验收参考，非理论输入。
- **Q3.3 构造 = (d) 均匀基线 + 局部源调制**：晶格 = 医院空间图 G_H；局部性来自 F 的空间分布，非"月亮照射模态"。
- **Q3.4 算子**：M=I、S=L(G)（边权 w_ij 待校准，不附加世界观解释）、F = F_collective·1 + F_local；**锁定：局部增强 ≠ 局部 AGC**（E(φ) 全局、d(φ) 全局决定）；G_H = (ii) 分层图（G_0/G_1/G_2，E_c/E_th 各层共享）。
- **Q3.5 场结构 = (a) 单全局场**：三层 = 同一场的三个空间区域（单复场 + 单一全局 AGC 保家族边界）；**主导观察者 = (i) 不进主链**（走情境基线 + 观察侧两通道）；C8：G(t)=constant，空间切换由上层空间系统改可达性语义。
- **Q4 投影 = a′**：q_i = ½|φ̇_i|² + ¼Σw_ij|φ_i−φ_j|²（正定局部能量密度，Σq_i=E(φ)）；r = E/E_c(λ) 全局诊断；q̂_i = q_i/q_i^base(λ) 接口归一化；三层分离 φ→q_i→q̂_i→m_field。
- **Q5 接口 = A(a)+B(i)**：m_field_vec⁽ⁱ⁾ = q̂_{x_i(t)}·g(SAN,state)·R_i（q̂ 理论投影 / g 机制层调制方向不定死 / R_i∈ℝ^69 神经落点留独立 grilling → **已闭合 [#101](https://github.com/verystrongdog/game/issues/101)，2026-09-02**）；**单向接口 m_field_vec ↛ φ_moon**。
- **Q6 参数分层**：「结构锁定项 vs 待校准项」（结构选择≠数学唯一推出）；F_local = 事件触发注入 + 动力学自然恢复（不设 τ_local）。
- **Q7 实验轨**（→ #35）：E1→E2→E3→E4→E6→E5→E7；E1 壳态保持性 P0 先行（失败回退 Q3.2 检查 B 族+A1）；E2 对照 0.675→0.900 为先验参考非硬拟合；E7 g 为机制层实验。
  - **→ 见 [Grilling #100](#grilling-100--e1-壳态保持性模拟实验协议2026-08-29-闭合)**：E1 协议已量化并实现跑通（PASS，2026-08-29）。
  - **→ 见 [Grilling #102](#grilling-102--e2-月相调制标定移动壳慢调制协议2026-08-30-开题协议锁定)**：E2 月相调制标定协议已锁定（2026-08-30）。

### 结构锁定 vs 待校准（摘要）

- **结构锁定**：方程骨架、M=I、B 族、单全局场+联合图、F 双通道、正定投影、r/q̂ 形态、m_field=q̂·g·R、A/B/C 观察侧
- **待校准**（→ #35）：f_c(λ;θ_c)、f_th(λ;θ_th)、w_ij、d_max、ε、F_collective、F_local、初始条件、q^base(λ)、g(SAN,state)
- **待验证假设**：A1 历史激活、满月峰值、满月易激活——不升级为理论事实
- **推迟**：R_i 神经落点（functional_id 映射）→ **已闭合 [#101](https://github.com/verystrongdog/game/issues/101)（2026-09-02）**；「相信被打败」胜利路径（5.1 另一半，暂缓待 E1 结果后）；空间层间连接拓扑细节

### 受影响文件

- `规则/时空结构数学框架.md`（新增 §十一 月光场实例化——主产物）
- `规则/核心机制.md`（§6.3 月光调制口径更新）
- `规则/技能树系统/运行时状态模型.md`（§4.5 m_field 接口注）
- `data/term_registry.json`（月光/m_field 更新；新增：理论投影、实例化判据、去噪不变性）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（5.1 状态更新）
- `../设计归档/grilling/grilling-38-moonlight-field`（README + 本 grilling 记录）
- `memory/月光场机制桥接-grilling-38.md`

---

## Grilling #99 — #41 决策自洽性复核（2026-09-02）

> Issue: [#99](https://github.com/verystrongdog/game/issues/99) | 维度: 事件+规则 | 形态: 闭合后复核（不重新开题）。对照最新设定（#38 改名/内容骨架术语让渡）预检 #41 D1-D11 的执行缝隙，发现 5 项（F1-F5），裁决 2 项，推迟 3 项。意识结构侧 #93-97 确认不涉 #41（决策树 `:3126` 前置声明「#41（意识包裹，不涉）」；纯学术轨不入游戏正典）。

### 决策

- **F1（D5 边界 — 玩家向正典去容器级表述）**：`事件/世界观与叙事.md` §月光本质 A-version 移除「容器注意力的可见痕迹」——玩家向正典（月光三重叠加）不再含容器级表述；容器注意力解释（#41 D3）移入 §世界观地基·统一解释，标注「设计层读解——不入游戏文本」。
- **F2（D5/D9 边界 — 消除"更深真相存在"暗示）**：`事件/游戏循环.md` §9.2「月光知道答案，但它不告诉你」→「答案是否存在，本身就是一个谜」——悬念保留、零断言，与不可证实性（无客观层可裁决）及三重叠加兼容。

### 推迟/未决

- **F3 都灵之马措辞**：「容器边界职能的人格化」（世界观 :146）+「容器/容器代理」（核心机制 §七）与 D6 一致性——未裁决，维持现状。候选方案：核心机制删「容器代理」措辞改「无敌叙事 NPC（无敌由叙事固定，与容器无涉）」+ 世界观 :146 加设计层注。
- **F4 术语残留（#38 改名清扫缺口）**：`项目总览.md`「三重叠加态」已顺手修正 ✅；待处理：term_registry 月光条目「坍缩表观」v2 残留、`参考/灵感收件箱.md`、`参考/文献/精神类药物参考-消耗品设计数据源.md` 的旧名（观察者效应）。建议随 CGL+AGC 定稿（5.1 桥接）一并清扫。
- **F5 5.1 桥接开题前 D8 边界确认**：机制桥接文本不得引用意识包裹/容器——待新任务「理论模型↔游戏实现接口」承接。

### 受影响文件

- `事件/世界观与叙事.md`（:29 移除容器表述；§世界观地基 加设计层注）
- `事件/游戏循环.md`（§9.2 改写）
- `项目总览.md`（:74 术语修正）
- `docs/决策树/`（本文）
- `memory/意识包裹复核-grilling-99.md`（本 grilling 决策摘要）

---

## Grilling #24 恢复 — 引擎数据层重描述（2026-08-14）

> Issue: [#24](https://github.com/verystrongdog/game/issues/24)（恢复）| 维度: 管线+规则 | 前置: csharp-engine step 1-12 全部交付（294/294 绿）

### 话题

用户发起：引擎代码在信息不完整时强行编写 → 从已确定的正典数据（解剖/物理背景/战斗逻辑）重新描述数据关系，兼学 C#。盘点三阶段（3 subagent 并行 + 主代理交叉验证）证明引擎与正典**结构性偏差≈0**——偏差集中在文档同步滞后 + 3 个待裁决语义点 + [NEW] 待校准常量。

### 决策

- **D1（话题形态）**：先盘点后决定（用户选 C）——产出《引擎数据层偏差清单》（`../设计归档/grilling/grilling-24-engine-data-relations`）
- **D2（偏差基准）**：正典文档 + data/ JSON 为正确基准（A+B 裁定）；正典内部冲突按决策树最新裁决
- **D3（盘点后范围）**：文档同步 + 重描述数据关系文档（用户选 B）——引擎代码仅 E-1 一处语义修正
- **D4（E-1 物理 motivation 下界）**：`clamp(motivationMod, −1, MotivationCap)`——原实现下界 0（负值归零）。正典仅定义上界 +100%，下界无裁决；统一 [−1,1] 与精神攻击（不 clamp）及 flow 层 producer（csharp-flow spec §5.1 clamp(tone_bias,−1,1)）口径一致——沮丧（低动机）时物理出力下降。落地：DamageCalculator.cs:52 + AC-4 锚点 4.0→2.0 + csharp-damage spec B7 + 核心机制 §4.2
- **D5（D-1 region_name_map 口径）**：70→69——删 #26 D6 已废弃聚合体（AmygdalaHippocampus/BasalGangliaIndirectPathway）+ 补 SubthalamicNucleus，与 brain_regions.json 键集完全一致（python3 验证）
- **D6（C-1 plan step 表同步）**：step 8-12 由"待开始"更新为"✅ 已交付"（git 证实 26 提交 294/294 绿）；变更日志加 v1.2 行
- **D7（数据关系规格形态）**：A 数据流图 + B 模块接口表合一（用户选 C）——《引擎数据关系规格.md》落位 `规则/技能树系统/`（正式正典），ASCII 图，含 §六 Unity 接缝
- **D8（附带清扫）**：核心机制 §2.1 Euler 残留→解析解、§十一 tone baseline [0.1,2.0]→[0,1]、脑功能层级模型 §十八 70→69（L5 7→8 dk 补 caudalanteriorcingulate、L1 16→14 删 2 聚合体、L0 11→12 补 STN）、data/README 重写为引擎 5 文件、CombatEvents.cs:87 HpDamage 注释更正、data-layer spec v1.3（收录 GameData/LoadAll）、engine-types spec 值域表体修正

### 受影响文件

- `规则/技能树系统/引擎数据关系规格.md`（新建——正式正典）
- `../设计归档/grilling/grilling-24-engine-data-relations/引擎数据层偏差清单.md`（新建——盘点产物）
- `src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs`（E-1 motivation 下界 −1）
- `src/YouAreNotTheFish.Core.Tests/Engine/DamageCalculatorTests.cs`（AC-4 锚点 4.0→2.0）
- `src/YouAreNotTheFish.Core/Types/CombatEvents.cs`（T-1 HpDamage 注释）
- `data/connectivity/region_name_map.json`（D-1：69 对齐）
- `data/README.md`（C-2：重写索引）
- `规则/核心机制.md`（§2.1 解析解、§4.2 motivation 下界、§十一 tone baseline）
- `规则/技能树系统/脑功能层级模型.md`（§十八 70→69 + L5/L1/L0 清单）
- `../规格/引擎/csharp-engine-roadmap.md`（C-1 step 表 + T-4/T-5）
- `../规格/引擎/csharp-damage.md`（B7 + AC-4 + §3.1）
- `../规格/引擎/csharp-data-layer.md`（v1.3：GameData/LoadAll + D-5）
- `../规格/引擎/csharp-engine-types.md`（T-2/T-3 值域表体）
- `docs/设计框架-六维状态.md`（管线维度更新）
- `data/term_registry.json`（motivation_mod 定义补下界）

### 延迟

- 建议修剩余项（E-2 14 事件闭环、E-3 静息常量去硬编码、E-4 NpcSalience 正式化、E-5 [NEW] 校准）→ 数值校准/技能系统 grilling → **已承接：[Grilling] 引擎补全路线图 (2026-08-16)**——E-2 拆入 P1c/P4a/P4d、E-3→P0 校准、E-4→P3、E-5→#35 并行轨
- 纯文档问题剩余（决策树 D10 "19 子类"笔误、audit 字段数笔误等 8 项）→ 随文档维护顺带修正

---

## [Grilling] 外界刺激来源定义 — 环境基调 + 月光场 + 模态扩展 (2026-08-16)

> Issue: [#69](https://github.com/verystrongdog/game/issues/69) | 维度: 规则+管线 | 11 项主轮决策 + 2 项修正 = 13 项共识

### 话题

内部动力学（WC 皮层动力学 69 fid + 脑干广播 4 tone + CSTC 门控）已锚定，但「外界刺激」仅有机制骨架 `s = W_sensory × α`，来源覆盖仅 14 个战斗对抗事件。非战斗/环境/世界刺激未定义。本次定义 s(t) 的外界来源分类学。

### 决策

- **D1 — 四来源域分类**：外界刺激按来源域分层——战斗对抗 / 环境·世界 / 社会·叙事 / 内感受·生理。战斗域已有 14 α，其余三域需补齐。

- **D2 — s(t) 双形态**：`s_j = s_事件_j + s_env_j`。事件脉冲（一次性）+ 持续场。

- **D3 — 环境基调 s_env**：持续场命名 = **环境基调**。s_env = 当前空间/场景的真实物理存在（气味/温度/光线），经 `W_sensory × α_env` 展开，环境内恒定。**修正**: 环境基调是独立物理存在，月光场调制它（非来源）。

- **D4 — 扩展模态集合**：不限于现有 6 模态。W_sensory 从 `{0,1}^(69×6)` → `{0,1}^(69×8)`。**修正**: 新增确认 2 个模态（嗅觉+热觉）。

- **D5 — 环境域新模态**：嗅觉 olfactory + 热觉 thermoreception。空间扭曲不单立模态，并入月光场通道。

- **D6 — 月光场通道 m_field**：月光 = 神经可接收刺激（非仅视觉），独立第三输入通道，承载观察者效应/幻觉/空间扭曲。不进感官模态。

- **D7 — 刷新时序**：持续场/月光场在「空间切换 + 月相/昼夜」节点刷新，环境内恒定。事件脉冲仍在战斗/事件点一次性注入。

- **D8 — 社会叙事域零新模态**：NPC 对话/线索/观察读出/Boss 命名复用语言认知+社会认知。任务目标「持续压力」= 内部认知态，排除出 scope（后续 grilling）。

- **D9 — α pattern 数据化**：α pattern 从 EventProcessor.cs 硬编码迁出到 `data/connectivity/alpha_patterns.json`，配置驱动。此后新增模态/事件/刺激源只改 JSON，不动引擎核心代码。（管线侧）

- **D10 — 内感受域零新模态**：内感受已被现有「痛觉」模态覆盖（Insula/ACC 已在 modality_nodes.pain）。药效/依赖/戒断 = 链路调制状态机制（非外界刺激）。心跳/疲劳归躯体+痛觉。

- **D11 — 战斗衔接**：战斗进行中 s_env + m_field 照常作用，事件脉冲叠加其上。战斗 = 环境基调 + 月光场 + 战斗对抗事件，三通道并置。

### 影响与后续

- 数据侧：`W_sensory.json` 扩列至 69×8；新建 `alpha_patterns.json`。C# `WsensoryMatrix.cs` 按需零改动（动态读列），`EventProcessor.cs` 改为配置驱动（去硬编码 α pattern）。
- 文档侧：`运行时状态模型.md` §4.5 扩展、`皮层动力学-通用层.md` §六 同步。
- 完整实施计划见 [../设计归档/grilling/grilling-69-external-stimulus/task-plan.md](../../%E8%AE%BE%E8%AE%A1%E5%BD%92%E6%A1%A3/grilling/grilling-69-external-stimulus/task-plan.md)（已通过四维质检）。

### 延迟

- 任务目标/承诺「持续压力」= 内部认知态 → 独立 grilling 内部认知激励
- 幻觉/精神异常走 m_field 的节点级落点（月光激活哪些 functional_id）→ 观察者效应机制节点映射 grilling → **已闭合 [#101](https://github.com/verystrongdog/game/issues/101)（2026-09-02，R_i 神经落点；幻觉调制为未来新语义候选，走 Q2 互斥分区）**
- m_field 强度 → 战斗难度调制(η) 具体比例 → 与月光场重建(#38/#35)联动（v2 η 已废弃，新参数集待定）

### 受影响文件

- `../设计归档/grilling/grilling-69-external-stimulus/task-plan.md`（新建，已质检）
- `../设计归档/grilling/task-check-2026-08-16-1910-grilling-69-task-plan.md`（质检报告）
- `data/term_registry.json`（本次同步更新：s(t) 定义 6→8 模态 + 新增 5 术语）
- `docs/设计框架-六维状态.md`（规则维度更新）

---

## [Grilling] 引擎补全路线图 — 缺口盘点与依赖排期 (2026-08-16)

> Issue: [#70](https://github.com/verystrongdog/game/issues/70) | 维度: 规则+管线 | 前置: csharp-engine step 1-12 全部交付（294/294 绿）+ Grilling #24 引擎数据层重描述

### 话题

承接 #24 延迟项（E-2/3/4/5），以 294/294 引擎核心为基线，盘点逻辑引擎全部缺口、排依赖序、产出分 feature 任务计划（全量路线图）。

### 决策

- **D1（范围）**：全量路线图——①引擎内 E-2/3/4/5 + 接口 stub ②结构性系统（技能/情境/NPC/战斗扩展/实体）③管线（平衡工具/Unity/测试）全部盘点排期
- **D2（依赖序）**：按依赖链顺序——①技能接口裁决 → ②LinkState+m 进引擎 → ③情境系统 → ④NPC Affordance 全量 → ⑤战斗扩展+实体系统；⑥校准全程并行
- **D3（skill.cortical_nodes 激活机制）**：C 混合注入+传播——核心节点直接注入 Δ_skill [NEW]（`a_j ← clip(a_j + Δ_skill, 0, 1)`）+ W·a 网络自然传播。闭合运行时状态模型 §4.5 延迟项。依据：A6 α=0「技能走 WC 内部通路」语义 + 物理技能公式「固定值 + a(Precentral)×w_execution」混合形态
- **D4（E-2/3/4 处置）**：按归属并入对应批次，不设独立 fixup 批——E-4→P3（NpcSalience 正式化）、E-2 拆入（A3/B3 暴击→P4d、A6 技能→P1c、A7 逃跑→P4a）、E-3 静息常量→P0 校准、响应窗口 stub→P4c
- **D5（校准策略）**：并行校准轨——数值平衡工具 + #35（战斗输出权重校准，已开放）独立推进；结构批用参数化占位值经 CalibrationConfig 回填
- **D6（批次粒度）**：拆细——P1 拆 3 子批（数据重建/LinkState+m/技能执行）、P4 拆 5 子批（逃跑投降/互转/响应窗口/暴击/空间），每子批独立 feature issue
- **D7（里程碑）**：每批 RED→GREEN + 总里程碑 = Console 完整战斗 demo（多敌方+技能+情境+NPC 全量+装备/消耗品+校准值），与 step 12 Smoke 一脉相承；Unity 属呈现维度（P6）不作引擎完成标准
- **D8（数据链断裂修复）**：三体技能上下文重建——link_contexts 重生于 tripartite（旧 364 链路数据已废弃）+ 8 行为角色分类器 + 60 候选池验证

### 盘点发现（引用即读取）

- **F-1 数据链断裂**：`link_contexts.json`（364 条）+ `link_registry.json`（⚠️ 已废弃标注）均基于旧 pairwise 364 链路 → 「60 候选池」实测数据失效，需在三体连接上重建
- **F-2 8 行为角色缺失**：tripartite 边 role 字段 = active/silent/modulating（脑干广播权重），8 行为角色（attack_physical 等）分类不在三体数据中，需新分类器
- **F-3 暴击机制规则空缺**：全规则库仅「L4 揭示弱点→暴击率↑」效果方向，无暴击率基线/倍率/触发判定正典 → A3/B3 事件无法落地根因
- **F-4 响应窗口 stub**：IResponseResolver 为 Noop，L1 期待/L3 精准/L5 叙事重构仅接口

### 受影响文件

- `../设计归档/grilling/grilling-70-engine-roadmap/task-plan.md`（新建——主产物，P0-P6 批次表 + 依赖图 + 里程碑）
- `docs/决策树/`（本文）；#24 延迟项 E-2/3/4/5 加注「→ 见 #70」
- `docs/设计框架-六维状态.md`（管线维度队列更新）
- `data/term_registry.json`（候选：Δ_skill [NEW]，待用户确认）
- `memory/grill-engine-roadmap-70.md`（决策摘要）
- 关联开放 issue：**#35**（并行校准轨）、#23（代码框架校验管线）、#38（m_field 依赖）

### 推迟

- 任务目标「持续压力」内部认知态（#69 延迟）→ 独立 grilling
- m_field 节点级落点 → #38 月光场重建后 → **已闭合 [#101](https://github.com/verystrongdog/game/issues/101)（2026-09-02）**
- 观察者效应机制桥接 → 独立 grilling（六维状态规则空缺）
- 14 角色→组件映射表 → P5-3 前置，逐角色开 issue

---

## [Grilling] 数值平衡工具方案 — 蒙特卡洛模拟 + 参数校准 (2026-08-16)

> Issue: [#71](https://github.com/verystrongdog/game/issues/71) | 维度: 管线+规则 | 前置: csharp-engine 294/294 ✅ + CalibrationConfig 实例化 ✅ + 核心机制 §十 ✅ | 承接: #70 路线图 P0 并行校准轨

### 话题

设计数值平衡工具（蒙特卡洛战斗模拟 + 参数校准），作为 E-5 校准常量群与 #35 校准 grilling 的执行载体，为 P1-P5 参数化占位值提供回填路径。

### 决策

- **D1（工具形态）**：C# 批量模拟器 + Python 分析壳——C# 驱动引擎真实代码路径（确定性 IRng 注入），Python 只做聚合/图表/报告，零公式复刻（旧 sim_battle.py 复刻路线已废弃）
- **D2（校准优先级）**：T0 战斗长度（杂兵 4-6/精英 8-10/Boss 16-20 回合，门禁）→ T1 #35 权重组（scale_mental/θ_mem/精神攻击节点集）→ T2 E-5 动力学群（δ_scale/M1 惩罚/感知阈值/4 静息常量）→ T3 Δm 成长曲线
- **D3（指标集）**：五组全含——战斗结算/动力学健康（tone 饱和率·gate 分布，防 step 6 惰性复发）/SAN 行为（阈值跨越）/速度/成长（Δm）
- **D4（工程形态）**：独立 `YouAreNotTheFish.Balance` 控制台工程；CLI `--battles/--seed/--scan <p>:<min>:<max>:<steps>/--scenario/--out`；输出 `data/calibration/`（raw+reports 分离）
- **D5（场景模板）**：demo 模板 + 敌人与事件 §4.1 权威表全敌人类型（取中值）覆盖三档；**顺带修 F-5 旧值表**
- **D6（任务划分）**：T1-T8；校准决策归 #35 grilling（工具只报指标，不自动改 CalibrationConfig）

### 接口发现

- ✅ CalibrationConfig 已是 instance record + static Default（sign-off 结转 #4 蒙特卡洛参数 sweep 预谋），经 CombatContext 注入 → 参数扫描零引擎改动
- ⚠️ E-3 前置：4 静息常量硬编码 SpeedScoreCalculator.cs:21-30 → T1 迁入 CalibrationConfig
- ⚠️ m_default 读 static Default（WMatrixBuilder.cs:63）→ 需 m 扫描时小改签名
- ⚠️ T3 Δm 不在引擎（属 P1b LinkState）→ 本次 Python 公式验证（validate_dm_curve.py），引擎内验证延后

### 一致性发现 F-5

敌人 HP 基线三处不一致：敌人与事件 §4.1 正文=新值（轻度 20-30 等，#10 上调已写入）vs 敌人与事件 §十二 速查=旧值（12-18 等）vs 核心机制 §10.1=旧值；医疗人员同文件 §5.2(25-40) vs §十二(15-25) 自相矛盾 → T7 修表

### 受影响文件

- `../设计归档/grilling/grilling-71-balance-tool/task-plan.md`（新建——主产物：架构/CLI/指标/任务 T1-T8/验收）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列：P0 数值平衡工具方案 ✅）
- `规则/核心机制.md`（§10.1 F-5 修表）+ `实体/敌人与事件.md`（§十二 F-5 修表）
- `memory/数值平衡工具-grilling-71.md`（决策摘要）
- 关联：#35（校准 grilling 消费工具）、#70（P0 并行校准轨）、#23（validate 脚本体系，不重复）

### 推迟

- 暴击参数校准 → P4d 补规则后（#70）
- Δm 引擎内验证 → P1b LinkState 后
- m_field/月光场校准 → #38 后
- 敌人 Stat 实例细化（Boss） → 实体维度队列

---

## [Grilling] P1a 技能上下文三体重建（数据层） (2026-08-16)

> Issue: [#72](https://github.com/verystrongdog/game/issues/72) | 维度: 规则+管线 | 前置: #70 D8/F-1/F-2 发现 + tripartite 888 边 + kroell14 14 网络 | 承接: #70 路线图 P1a

### 话题

把技能生成的上下文基础从已废弃旧 pairwise 364 链路（link_contexts.json，F-1）重建到三体模型连接上——产出 link_contexts_tripartite.json 结构 + 8 行为角色分类规则 + 候选池验证方案。

### 决策

- **D1（边集）**：CC + PP 信息传递边（888 条）——brainstem/CSTC 是调制/门控原语，由 tone/gate 系统独立承载（NPC AI §3.3 + 运行时 §6.5），不入技能内容池
- **D2（网络归属）**：gameplay_labels 桥接——`networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅}`（kroell14），零新映射表；覆盖盲区：thalamic_relay 不在任何网络 domains（预期 uncovered 边 ≤30）
- **D3（角色分类）**：12 gameplay_domain → 8 role 权重映射表（domain_role_map.json，初始值可调，signal_type 辅助修正待评估）；主角色=argmax、副角色=次高分>0.25
- **D4（候选池规模）**：实测值不设约束（60 是旧 364 数据快照非设计目标）；重建报告给新规模
- **D5（Schema）**：双视图——contexts 主视图（context→edges，技能生成直消费）+ edge_contexts 反视图（edge→contexts，组件/药物复用）+ _rules 算法声明 + stats（uncovered 报告）

### 数据发现

- kroell14_networks.json 每网络含 gameplay_domains（机器可读）→ 桥接可行
- tripartite 边全量含 gameplay_labels（12 domain）→ 映射表有全量输入
- **F-6 新发现**：`hansen_communities.json` 被 kroell14 _usage 引用（"50 网络集合含混合+边缘"）但文件不存在 → 推迟清单，独立数据补齐话题

### 受影响文件

- `../设计归档/grilling/grilling-72-p1a-skill-context/task-plan.md`（新建——主产物：schema/映射表/任务 T1-T5/验证）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列 P1a ✅ 方案已定）
- `data/connectivity/domain_role_map.json`（T1 落地）+ `link_contexts_tripartite.json`（T2 产出）
- `tools/build_contexts_tripartite.py`（T2）+ `rebuild-report.md`（T3）
- `规则/技能树系统/技能生成机制.md`（§二 60 候选池注更新）
- `memory/技能上下文三体重建-grilling-72.md`

### 推迟

- Hansen 社区/50 网络集合 → hansen_communities.json 补齐（独立话题）
- signal_type 辅助修正启用 → T3 冲突边分析后定
- 映射表权重校准 → #35
- 组件分类/药物调制复用 → P5-3/P5-2 批次

### 实施完成（2026-09-01，Grilling #112）

- `domain_role_map.json` / `build_contexts_tripartite.py` / `link_contexts_tripartite.json` / `rebuild-report.md` 全部落地（commit 5de8968 + 9eed1c9）
- 实测结果：888 边 → 71 contexts → **71 候选技能**（uncovered 0）；flee/disrupt 零主角色 = KNOWN DESIGN LIMITATION（权重归 #35 校准）
- 契约定案（外审 t_6a966/t_6a96a/t_6a96a926）：edge_contexts.source/target = dk_name（fid 反查归 P1c）；产物 = 非 Module 强契约数据产物（schema/version + 消费门禁）；六维验收表 6 条实判
- **T4 推迟**：function_label 实测 49%（#92 重生成覆盖 build_function_labels.py 产物，git 66d1dd2/30108af）——signal_type 辅助修正输入不足；上游修复项单列
- 技能对接链声明：P1a→P1b→P1c→技能系统 grilling→#35→呈现层，P1a 为第 1 段，对接完成 ≠ 技能可玩

---

## [Grilling] P1b LinkState + m 成长进引擎 (2026-08-16)

> Issue: [#73](https://github.com/verystrongdog/game/issues/73) | 维度: 规则+管线 | 前置: csharp-engine 294/294 ✅ + P1a 角色分类 | 承接: #70 路线图 P1b

### 话题

把髓鞘化 m 从 demo 常量（m_mean ≡ MDefault=0.3，WMatrixBuilder B4 偏差）升级为三体边级 LinkState——数据结构 + m_mean 入 W + Δm 战后结算 + 可塑性巩固接口 + 聚焦接口。

### 决策

- **D1（m 载体）**：CC + PP 边（888 条，与 P1a 边集一致）；brainstem/CSTC 权重由 role/常量表定（运行时 §5.6/§6.3），无使用频率语义
- **D2（m 初始值）**：核心机制 §10.3 层级表中值，边层级 = max(source.L, target.L)；角色疾病偏移后置
- **D3（Δm 激活）**：P1a 角色分类驱动基础行动——物理攻击(M1)→attack_physical 边 n+1、精神攻击(Broca)→attack_mental 边 n+1、防御→defend 边 n+1；**g(n) = 单场战斗内激活次数**；P1c 后扩展技能使用边
- **D4（可塑性巩固）**：引擎数据 + 结算接口（LinkState.Marked + TryConsolidate(edgeId, Mark|Boost, strength) + 校验：不可重复/m≤0.3/强度映射 0.03-0.07/0.07-0.12/0.12-0.20）；UI/强度计算归上层
- **D5（聚焦）**：`Build(GameData, LinkState, FocusSet)` 独立参数（构建层状态），聚焦边 ×2.0；原单参重载保留

### 引擎现状核查

- `WMatrixBuilder.Build(GameData)` 单参数，m_mean = `CalibrationConfig.Default.MDefault`（static，B4 偏差注释明确 demo 无 LinkState）
- `LinkGrowthEvent` 存在但 EventProcessor no-op；`CombatState` 无 link_states；WMatrix 每场战斗构建一次（TurnManager ctor:54 + CombatState.Create:84）

### 受影响文件

- `../设计归档/grilling/grilling-73-p1b-linkstate/task-plan.md`（新建——主产物：数据结构/初始化/Δm 规则/接口/T1-T6/验收）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列 P1b ✅ 方案已定）
- 实施后：`Entity/LinkState.cs` / `Types/FocusSet.cs` / `Engine/MyleinGrowth.cs`（新建）+ `WMatrixBuilder.cs` / `TurnManager.cs` / `CombatState.cs` / Console / Tests（改写）
- `memory/髓鞘化成长引擎-grilling-73.md`

### 推迟

- 技能使用激活边 → P1c；角色疾病标签 m 偏移 → 角色批次；事件强度计算 → 数值平衡工具；NPC 静态 m 模板 → P3

---

## [Grilling] P1c 技能执行引擎 — 混合注入 + 效果结算 + A6 (2026-08-16)

> Issue: [#74](https://github.com/verystrongdog/game/issues/74) | 维度: 规则+管线 | 前置: #70 D3（混合注入裁决）+ P1a 候选池 + P1b LinkState | 承接: #70 路线图 P1c

### 话题

落地技能执行引擎：SkillDefinition 数据 + Δ_skill 混合注入 + skill_base_effect × gate_bonus 结算 + A6 事件闭环。

### 决策

- **D1（cortical_nodes）**：组内边端点 functional_id 去重集合（P1a 双视图供给），数据驱动零手工；命名属构建层/UI 后置
- **D2（base 节点集）**：组内节点 a(t) 均值（公式形态按 role：乘 scale_mental / 加 w_execution / σ−θ_mem）——"调链路改技能数值" D3 意图，技能有身份
- **D3（注入）**：结算前注入 + Δ_skill × mean(m of 组内边)；Δ_skill 初始 0.1 [NEW] 待 #35 校准；聚焦经 W ×2.0 已反映，注入不乘 focus（防双算）
- **D4（A6）**：立即闭环——技能使用成功 emit；δ = sign(tone_bias[role]) 代码常量（NPC AI §3.3 推导，与 Gurney 权重表同惯例）；m=1.0；α=0
- **D5（执行集成）**：通道全表（attack_physical/defend/approach/flee→M1；attack_mental/disrupt/support→Broca；perceive→无通道响应型预留）+ 4 类效果（物理/精神/防御/记忆检索）；flee/approach/disrupt/perceive 接口预留。**记忆检索效果 → 见 #90**（P_success 引擎层公式 + 内容层 P_trigger 勾起，2026-08-20 对接）

### 引擎现状核查

- CombatAction = M1/Broca 双通道 ActionSlot（PhysicalAttack/MentalAttack/Defend）——Skill 动作扩展 ActionKind.Skill + skillId

### 受影响文件

- `../设计归档/grilling/grilling-74-p1c-skill-execution/task-plan.md`（新建——主产物：数据结构/通道映射/结算流程/A6/T1-T6/验收）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列 P1c ✅ 方案已定）
- 实施后：SkillDefinition.cs / SkillCatalog.cs / SkillResolver.cs（新建）+ CombatAction/Enums/ActionResolver/CalibrationConfig/Console/Tests（改写）
- `memory/技能执行引擎-grilling-74.md`

### 推迟

- 技能命名 → 技能系统 grilling；flee/approach/disrupt 效果 → P4a/P3；perceive 执行 → P4c；base_fixed/w_execution/k_defend 数值 → #35；support 细分 → support 技能 grilling

---

## [Grilling] P2 情境系统进引擎 — 选择器 + 三通道 + salience (2026-08-16)

> Issue: [#75](https://github.com/verystrongdog/game/issues/75) | 维度: 规则+管线 | 前置: #69 三通道语义/D9 + situation_primitives 27 原型 + EventProcessor 硬编码现状 | 承接: #70 路线图 P2 | **实施: → 见 [#104](https://github.com/verystrongdog/game/issues/104)（2026-09-02 实施启动，issue [#105](https://github.com/verystrongdog/game/issues/105)）**

### 话题

情境系统进引擎：α_patterns 数据化（#69 D9 落地）+ 27 原型选择器 + s_env/m_field 三通道 + 情境只读状态接口（供 P3）。

### 决策

- **D1（数据边界）**：事件/持续场分离——alpha_patterns.json 只放 14 战斗事件（#69 schema 原样，8 模态）；env_tones.json 独立放环境基调 α_env（空间类型→8 模态强度）
- **D2（情境选择器）**：空间→原型映射表（typical_game_scenario 辅助）+ 低 SAN 概率偏移（恐慌→诡异/负面原型，p_panic=0.5 [NEW]）+ key_brain_regions **直接节点注入**（心理情境非感官，不走 W_sensory）+ 刷新时机 = 空间切换 + C1 事件
- **D3（三通道落点）**：并入 s 数组——s_total = s_事件 + s_env + m_field；WcDynamics.Step 签名零改动。**🔧 修正 (2026-09-02 #104 Q1)**：原「m_field 占位全 0，MFieldStrength=0 [NEW]，节点落点 #38 后填」已更新——#101 闭合 R 落点结构、#103 定 moonState(D)/calibration_status 分级，m_field 按**结构实现 + PLACEHOLDER 分级 + 门禁**（见 #104 条目）
- **D4（情境 salience）**：隐式涌现（原型注入→a(t)→salience 自然反映，不查表——正典原则 4）+ 只读情境状态接口（SituationState: 原型 id+强度+环境 id，供 P3/UI/叙事）

### 数据现状核查

- EventProcessor.cs:123 硬编码 new[]{1,0,1,0,0,0}（6 模态定长）；situation_primitives 27 原型（key_brain_regions 实测 37 去重名已全为 fid——#104 Q6 修正，混合说法已过时）；W_sensory 仍 69×6

### 受影响文件

- `../设计归档/grilling/grilling-75-p2-situation/task-plan.md`（新建——主产物：schema/选择器/落点/T1-T7/验收）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列 P2 ✅ 方案已定）
- 实施后：W_sensory.json（69×8）+ alpha_patterns.json + env_tones.json（数据）+ EventProcessor/SituationSelector/CombatState/CalibrationConfig/Console/Tests（代码）
- `memory/情境系统引擎-grilling-75.md`

### 推迟

- m_field 参数集/节点落点 → #38 → **已闭合 #101 + #104 Q1（结构实现 + PLACEHOLDER，正式数值归 #35）**；env_tones 全环境表值 → 空间内容（demo 3 环境集已锁定 #104 Q6）；SAN 偏移分组表标注 → 内容填充；情境强度系数 → #35；白天月光渗透 → 独立话题

---

## [Grilling] P3 NPC Affordance 全量 — 7 参数化 + salience 正式化 (2026-08-16)

> Issue: [#76](https://github.com/verystrongdog/game/issues/76) | 维度: 规则+管线 | 前置: NPC AI 正典 §三/§四 + P1a/P1b/P1c/P2 | 承接: #70 路线图 P3（E-4 闭合）

### 话题

NpcSalience 从 demo 占位升级为正式 Affordance Competition：7 参数化性格 + 6 标签映射 + 技能候选集 + T_SAN + 目标选择框架。

### 决策

- **D1（7 参数落点）**：personality_tags.json（6 标签→7 参数映射，§4.2 表）+ NpcPersonality record + per-participant baseline（ToneUpdater 衰减目标 = baseline，替换 demo 硬编码）
- **D2（候选集）**：3 基础行动（demo 节点集正式化：物理=Precentral+SD1 代理/精神=dlPFC+Broca+ACC/防御=Insula+Amygdala）+ 已浮现技能（NPC 静态 LinkState ∩ 涌现条件）；杂兵（m=0.3）→ 基础行动，Boss → 可浮现
- **D3（选择规则）**：Boss argmax / 杂兵 Softmax + T_SAN（0/+0.10/+0.30/∞）+ SAN=0 均匀随机 + 恐慌配置占位（PanicToneShift [NEW] NE+0.2/5HT−0.2）+ 目标选择框架（四节点群全量留 P4e）
- **D4（E-4 闭合）**：demo 占位全删（3 行动节点/FirstEnemy/硬编码 baseline/tone_bias）；RoleToneWeights 代码常量（8×4）与 A6 sign **同源派生**；Console 双模板（杂兵 Softmax/Boss argmax）对比

### 引擎现状核查

- NpcSalience.cs：PhysicalNodes/MentalNodes/DefendNodes 硬编码 + FirstEnemy + BaselineNe 等常量 + 内联 tone_bias 权重（plan §4.8 [NEW]）

### 受影响文件

- `../设计归档/grilling/grilling-76-p3-npc-affordance/task-plan.md`（新建——主产物：数据结构/候选集/选择规则/E-4 清单/T1-T7/验收）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线队列 P3 ✅ 方案已定）
- 实施后：NpcPersonality.cs / RoleToneWeights.cs / personality_tags.json（新建）+ NpcSalience.cs 重写 + ParticipantState/ToneUpdater/CandidateSetBuilder/Console/Tests（改写）
- `memory/NPC全量引擎-grilling-76.md`

### 推迟

- 目标 salience 四节点群 → P4e；恐慌配置数值 → #35；NPC 持久髓鞘化/跨战斗记忆 → Boss 批次；多标签叠加样例 → 敌人 Stat 批次

---

## [Grilling] P4d 暴击机制补全 — 规则空缺 F-3 (2026-08-16)

> Issue: [#77](https://github.com/verystrongdog/game/issues/77) | 维度: 规则 | 前置: F-3 发现（#70）+ 基础行动设计 + 运行时 §5.5 A3/B3 pattern | 承接: #70 路线图 P4d

### 话题

补全暴击机制规则空缺——全规则库仅「L4 识别揭示物理弱点→暴击率↑」方向，无基线/倍率/触发正典。A3/B3 事件 pattern 已定义但无触发源。

### 决策

- **D1（触发机制）**：物理暴击 = a(t) 执行强度驱动——`crit_rate = clip(base_crit + k_crit × (a_exec − θ_crit), 0, cap)`，a_exec = mean(a(Precentral), a_SD1_somatic)（速度执行分同源）；**精神无随机暴击**（用户裁定：永远命中+随机=双重随机粗糙）
- **D2（效果）**：物理暴击 ×1.5（基础→gate×防御→×1.5→量化）；判定通过 emit A3+B3（E-2 闭环）；精神增强 = 确定性弱点状态
- **D3（L4 识别）**：主动观察动作（占 1 动作不占 M1/Broca，bypass gate）+ 弱点状态：物理→crit+15%、精神→SAN×1.5、持续 2 回合 [NEW] 重复识别刷新
- **D4（数值与落点）**：初始值全 [NEW] 待 #35（base_crit 0.05/θ_crit 0.6/k_crit 0.5/cap 0.30）；引擎落点 = DamageCalculator/EventProcessor A3B3/StatusKind 弱点/识别技能（P1c 扩展）；正典 3 处写入

### 用户质疑与修正

- 「精神直接暴击太粗糙」→ 精神攻击改为**无随机暴击 + 确定性弱点机制**（物理概率 vs 精神机制，不同质）
- 「事件接线是什么」→ 澄清：A3/B3 是 §5.5 定义的 δ/α 事件（暴击者 DA↑、被暴击者 NE↑5HT↓），接线 = 暴击判定通过后引擎发射，影响后续回合动力学

### 受影响文件

- `../设计归档/grilling/grilling-77-p4d-crit/task-plan.md`（新建——主产物）
- `规则/技能树系统/操作层/基础行动设计.md`（§二 暴击段 + §三 L4 细化）
- `规则/核心机制.md`（§4.2 暴击公式 + §十一 速查）
- `规则/技能树系统/运行时状态模型.md`（§5.5 A3/B3 触发源注）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（规则空缺 F-3 闭合）
- `memory/暴击机制-grilling-77.md`

### 推迟

- 暴击参数校准 → #35；弱点状态 UI → 状态面板 grilling；NPC 侧暴击可读性 → 战斗界面 grilling

---

## [Grilling] P4a 逃跑/投降进引擎 — A7 闭环 (2026-08-16)

> Issue: [#78](https://github.com/verystrongdog/game/issues/78) | 维度: 规则+管线 | 前置: 回合战斗流程 §8.2/§8.3 正典 + IsOver 现状 | 承接: #70 路线图 P4a

### 话题

逃跑/投降规则落地引擎：CombatAction 扩展 + 退出战斗逻辑 + A7 事件闭环 + 战斗结束条件扩展 + 补 [NEW] 数值。

### 决策

- **D1（逃跑成功率）**：默认成功（正典无成功率规则）；L5 控制压制回避 = 接口预留；软边界自动逃跑 P4e 接入
- **D2（逃跑惩罚）**：FleeSanRestore [NEW] = +10（待 #35）+ Δm 结算跳过 + A7 事件闭环（δ (1,−1,0,0) + α 视觉+躯体，E-2）
- **D3（投降判定）**：简化——敌方类型 ∈ {医疗人员, 拜月教徒} 且 SAN ≥ 30%（理性残余阈值 [NEW] 与恐慌对齐）；demo 默认接受（拒绝查表 [NEW] 待 P3 性格 + 叙事）；接受 → 投降方败北（非死亡无尸体）
- **D4（结束条件）**：ExitStatus 四态（None/Fled/Surrendered/Defeated）+ ActionKind.Flee（M1）/Surrender（Broca）+ IsOver 扩展（任一方全员 ExitStatus ≠ None → 结束）；退出者保留状态快照

### 受影响文件

- `../设计归档/grilling/grilling-78-p4a-flee-surrender/task-plan.md`（新建——主产物）
- `规则/回合战斗流程.md`（§8.2 投降行 + §8.3 逃跑规则补 [NEW]，✅ 已写入）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P4a ✅）
- 实施后：Enums/CombatAction/ParticipantState（ExitStatus）+ ActionResolver（逃跑投降）+ EventProcessor（A7）+ TurnManager（IsOver）+ CalibrationConfig（+2 [NEW]）
- `memory/逃跑投降引擎-grilling-78.md`

### 推迟

- L5 控制压制回避 → L5 技能批次；软边界自动逃跑 → P4e；投降拒绝查表 → P3 后 + 对话系统；逃跑成功率（如需）→ 数值校准讨论

---

## [Grilling] P4b HP↔SAN 互转进引擎 — 兑换逻辑 + 上限追踪 (2026-08-16)

> Issue: [#79](https://github.com/verystrongdog/game/issues/79) | 维度: 规则+管线 | 前置: 核心机制 §5.3 正典（数值完整） | 承接: #70 路线图 P4b

### 话题

HP↔SAN 互转落地引擎：兑换动作 + 分段公式 + 单次/单场上限追踪。少数无 [NEW] 参数的批次（正典值全用）。

### 决策

- **D1（动作）**：ConvertHpToSan（自残）+ ConvertSanToHp（吃怪物肉）两独立动作 + 花费量 payload；均占 M1 通道（与物理攻击互斥）；无冷却
- **D2（公式）**：正典字面——HP→SAN `min(spent,10)×2 + max(spent−10,0)×1`（round1）；SAN→HP `min(spent,10)/2 + max(spent−10,0)/3`（floor1 + cap 8.0——"换最多 8 HP"字面）；单次上限 15/20
- **D3（边界）**：花费后 HP ≥ 1 / SAN ≥ 1（不能自残致死/主动进随机行为）；单场上限 per-participant 累计（30/15），超限拒绝
- **D4（事件）**：互转不产生 δ/s 事件（正典未定义，避免发明）；Console demo 命令 + 额度显示

### 受影响文件

- `../设计归档/grilling/grilling-79-p4b-hp-san-convert/task-plan.md`（新建——主产物）
- `规则/核心机制.md`（§5.3 边界注）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P4b ✅）
- 实施后：Enums/CombatAction（+2 动作）+ CombatState（累计字段）+ ActionResolver（兑换结算）+ Console/Tests
- `memory/HP-SAN互转引擎-grilling-79.md`

### 推迟

- 互转 δ/s 事件（自残痛觉）→ 事件系统扩展批次；药物/装备交互 → P5；互转 UI → 战斗界面

---

## [Grilling] P4e 空间系统进引擎 — 战棋网格 + 多敌方 (2026-08-16)

> Issue: [#80](https://github.com/verystrongdog/game/issues/80) | 维度: 规则+管线 | 前置: 回合战斗流程 §十 27 项决策 + 引擎多参与者现状 | 承接: #70 路线图 P4e（P4 最后一大批）

### 话题

空间系统（§十）落地引擎：网格 + 移动 + 射程/视线 + 控制区/借机/夹击 + 友伤/AOE + 多敌方。

### 决策

- **D1（空间模型）**：battlefields.json（尺寸+障碍物+初始站位）+ Position(x,y,z 整米) + 双距离（移动=网格对角 1.5 / 射程控制区=欧几里得）
- **D2（移动）**：CombatAction.Movement 同窗口 + 配额 `12×clamp(1+k_move×(执行分−0.5), 0.8, 1.2)` [NEW] + 穿越校验 + 软边界→P4a 逃跑
- **D3（射程视线）**：目标合法性校验（距离≤射程；全高拒绝含精神；半高/生物命中修正）+ SkillDefinition.Range [NEW]
- **D4（交互层）**：控制区 1.5m + 自动借机（占未用通道）+ 夹击（−25%/−50%+察觉−2/135°+20%）+ 友伤分级 + AOE 结算器（SkillDefinition.Aoe 接口预留）——**全部纯 C# 逻辑判定**
- **D5（demo 范围）**：多敌方（现有排序满足，5v3）+ 部署预设 + P3 目标框架激活（攻最近）；隐藏/伏击接口预留

### 用户架构澄清（关键）

「位置/视野涉及引擎渲染的部分只用 C# 模拟可行么」→ **可行且正确**：位置/视线/掩体的**判定**是规则层几何算法（DDA 线段-格采样/距离/向量夹角），非渲染；Unity 只渲染结果 + 输入。数据流：battlefields.json（数据）→ 引擎几何判定（纯函数，确定性）→ 数字结果 → Unity 显示。符合引擎纯 .NET 库架构（csharp-engine plan §一）。

### 受影响文件

- `../设计归档/grilling/grilling-80-p4e-space/task-plan.md`（新建——主产物，T1-T9）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P4e ✅——P4 全部方案闭合）
- 实施后：battlefields.json + Position/BattlefieldMath/ZoneAttack/Flanking/AoeResolver（新建）+ SkillDefinition(+Range/Aoe) + CombatAction(+Movement) + CombatState(+Positions) + ActionResolver + NpcSalience（攻最近）+ Console/Tests
- `memory/空间系统引擎-grilling-80.md`

### 推迟

- 隐藏/伏击 → 遭遇设计批次；AOE 链路赋予 → P1 实施后；目标四节点群 → NPC 精细化；高度/坠落验证 → 关卡数据；环境交互（§10.13）→ 环境交互 grilling；空间参数 → #35

---

## [Grilling] P4c 响应窗口进引擎 — L4 读意图 + 忍耐主动 + 叙事重构 (2026-08-16)

> Issue: [#81](https://github.com/verystrongdog/game/issues/81) | 维度: 规则+管线 | 前置: 回合战斗流程 §六 + IResponseResolver 接口（Noop stub） | 承接: #70 路线图 P4c

### 话题

响应窗口落地引擎——IResponseResolver 从 Noop 实现为正式响应解析器（L4 读意图 / 忍耐·主动 / L5 叙事重构 B），闭合响应窗口 stub。P4 最后子批。

### 决策

- **D1（范围）**：三响应全实现（L4/忍耐主动/叙事重构 B）；L0 回避保持 DamageCalculator 现状 ✅
- **D2（L4 读意图）**：a(t) 动力学驱动——社会认知节点（mPFC/TPJ/STS）`mean(a) > 阈值 [NEW]` → 响应可用；效果 = 自动防御（当回合无冷却，核心机制 §4.4）；仅物理攻击声明生效
- **D3（忍耐·主动）**：响应自动触发（CD=0 + Broca 未用 → 被精神攻击声明自动使用）：SAN 减免翻倍（−2 最低 1）+ Broca 占用 + CD2；UI 留呈现层
- **D4（叙事重构 B + 防御主动澄清）**：同队受伤害 + L5 节点 a(t) 超阈值 → NarrativeBoost（下窗口攻击 +25%）；**"防御主动"判为 #70 表述残留**（正典无此名词），不发明；L5 控制留 L5 技能批次

### 受影响文件

- `../设计归档/grilling/grilling-81-p4c-response-window/task-plan.md`（新建——主产物）
- `规则/回合战斗流程.md`（§6.2 补注，✅ 已写入）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P4c ✅——**P4 全部闭合**）
- 实施后：ResponseResolver（替换 Noop）+ SocialCognitionNodes + DamageCalculator（忍耐/NarrativeBoost）+ StatusKind.NarrativeBoost + CombatState + CalibrationConfig(+2 [NEW]) + Console/Tests
- `memory/响应窗口引擎-grilling-81.md`

### 推迟

- 响应选择 UI → 战斗界面；L5 控制（防御借 M1）→ L5 技能批次；NPC 响应策略 → NPC 精细化；阈值 → #35

---

## [Grilling] P5-1 武器与护甲进引擎 — 装备槽 + 数值集成 (2026-08-16)

> Issue: [#82](https://github.com/verystrongdog/game/issues/82) | 维度: 规则+管线 | 前置: 武器与装备.md 正典 + DamageCalculator weaponBonus 参数 | 承接: #70 路线图 P5-1

### 话题

武器/护甲系统落地引擎：装备数据结构 + 槽位 + 数值集成 + 效果分级实现。

### 决策

- **D1（数据结构）**：equipment.json（11+25+12 全量）+ 槽位校验（主手/副手/饰品×5/精神防护——§4.1）+ 构建层→战斗快照
- **D2（效果范围）**：数值类全实现（weapon_bonus/hit_mod/减伤累加/阈值偏移/equipment_SAN/HP/防御替换）+ 4 简单状态（流血 DoT/暴击+10%/反伤/命中 debuff）；复杂效果接口预留
- **D3（精神武器）**：数据 + m 阈值校验（P1b LinkState）+ 占 M1 + 冷却 + 12 件效果接口预留（demo no-op）
- **D4（装备流程）**：EquipmentSet 构建层→CombatState 快照（同 LinkState 模式）+ DamageCalculator 全接入 + Console demo

### 受影响文件

- `../设计归档/grilling/grilling-82-p5-1-equipment/task-plan.md`（新建——主产物，T1-T7）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P5-1 ✅）
- 实施后：equipment.json + Equipment/EquipmentSet/StatusEffects/MentalWeaponResolver（新建）+ DamageCalculator/Enums/CombatState/Console/Tests
- `memory/武器护甲引擎-grilling-82.md`

### 推迟

- 复杂效果（AOE 切换/破门/免疫/移动力）→ 状态系统扩展批次；武器链路解锁 → P1b 后；精神武器 12 效果 → 状态系统扩展；稀有/Boss 效果 → Boss 批次；装备数值 → #35

---

## [Grilling] P5-2 消耗品进引擎 — 药物链路调制 + 风险模型 (2026-08-16)

> Issue: [#83](https://github.com/verystrongdog/game/issues/83) | 维度: 规则+管线 | 前置: 消耗品系统.md 正典 + P1b LinkState + P1a 上下文 | 承接: #70 路线图 P5-2

### 话题

消耗品系统（17 药物）落地引擎：drugs.json + 调制生效 + 使用流程 + 风险模型。

### 决策

- **D1（药物映射）**：drugs.json 17 药 + 上下文级调制目标（P1a 衔接——§3.15 域表 → gameplay_domain → P1a 上下文桥接；**§3.15 缺口填充**）；首批 3-4 药完整映射 + 其余按域批量
- **D2（调制生效）**：`EffectiveM[edgeId] = clamp(LinkState.M + Σ偏移, 0, 1)`（拮抗天花板 Σ ≤ 1.4/冲突取绝对值最大——决策树 #4）+ W 脏标记下回合重算 + 钳制 ↕ = 区间锁定
- **D3（使用）**：`ActionKind.UseItem`（M1 通道——杂项动作，同环境交互 §10.13）+ 每回合 1 种 + 同域叠加后药降级（§八）
- **D4（风险）**：过量战斗内（单场 ≥2 窄治疗窗 → 调制翻倍+负面）+ 依赖/戒断/耐药跨战斗计数器接口预留（N/K/M [NEW] 待 #35）+ 禁止组合（致死阻止/危险警告标志）

### 正典缺口确认

- §3.15 "具体药物-链路映射表待内容填充"——P5-2 以 P1a 上下文为调制目标填充首批（上下文级比链路级可操作；13 功能域已废弃 D28）

### 受影响文件

- `../设计归档/grilling/grilling-83-p5-2-consumables/task-plan.md`（新建——主产物，T1-T7）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P5-2 ✅）
- 实施后：drugs.json + Drug/EffectiveM/DrugPersistentState + WMatrixBuilder（EffectiveM 消费）+ ActionResolver（UseItem）+ Enums/CombatState/Console/Tests
- `memory/消耗品引擎-grilling-83.md`

### 推迟

- 药物映射全量精调 → 内容填充；N/K/M 数值 → #35；非战斗使用（SSRI/尼古丁）→ 休息系统批次；敌人用药 → NPC 精细化；涌现效果细节 → 状态系统扩展

---

## [Grilling] P5-3 面具组件进引擎 — 病理链路调制 + 同角色加成 (2026-08-16)

> Issue: [#84](https://github.com/verystrongdog/game/issues/84) | 维度: 规则+管线 | 前置: 角色与面具 §8 + P1a 上下文 + P1b/P5-2 EffectiveM | 承接: #70 路线图 P5-3

### 话题

面具组件系统引擎机制先行落地——组件内容（components.json/病理边）等 14 角色映射表批次（§8.12）。

### 决策

- **D1（处理方式）**：机制先行 + 内容推迟——MaskSet/调制/加成/重叠互斥机制本批落地；组件内容随 14 角色映射表批次（§8.8.2：病理链路只能从已定义疾病推导，不能拍脑袋造——用户裁定）；demo 用 1-2 占位组件 [NEW] 验证机制
- **D2（调制）**：共享 P5-2 `EffectiveM` 表——`clamp(LinkState.M + Σ药物 + Σ组件, 0, 1)`（拮抗限额 ≤1.4 共享，冲突取绝对值最大）
- **D3（同角色加成）**：按 primary_role 分组（§8.9.1 修正——13 功能域废弃）→ 组件偏移 × (1+bonus)（15/25/30/35%）；专属被动接口预留；网络仅展示
- **D4（操作/重叠/互斥）**：MaskSet 5 槽构建层（编辑/锁死/替换/多面具=皮肤）+ 疾病重叠判定（edge ∈ 疾病边 → 无效）+ 拮抗互斥接口预留

### 受影响文件

- `../设计归档/grilling/grilling-84-p5-3-mask-components/task-plan.md`（新建——主产物，T1-T6）
- `docs/决策树/`（本文）+ `docs/设计框架-六维状态.md`（P5-3 ✅——**P5 全部闭合，P1-P5 设计讨论完成**）
- 实施后：MaskComponent/MaskSet/MaskBonus/MaskOverlap/AntagonisticPairs + CombatState（EffectiveM 扩展）+ Console/Tests
- `memory/面具组件引擎-grilling-84.md`

### 推迟

- components.json/pathology_edges.json 全量 → 14 角色映射表批次；拮抗对列表 → 逐角色拆解；专属被动 → 同上；病理链路代价 → 映射表+状态系统

---

## [Grilling] 对话数学语言规范固化 (2026-08-16，6 项决策)

> Issue: [#85](https://github.com/verystrongdog/game/issues/85) | 维度: 管线（元过程/质量保障） | 前置: 无（元话题） | 关联: [数学语言书写规范](../agents/math-language-writing.md) §七、CLAUDE.md §对话数学语言规范

### 话题

将「对话中规范用户语言习惯、强制数学语言表达需求」固化为项目规则。用户提出：语言是思维的边界，描述习惯影响思维方式；越是严谨的数学描述，AI 越不容易偏差。

### 决策

- **D1（触发范围）**：全程，无场景豁免——grilling、新设计、代码/文档需求、参数修改、C# 教学、闲聊中出现的可量化语义一律严谨。语言相对论立场：描述习惯训练思维方式
- **D2（标准锚定）**：数学专业论文的表述规范——符号先定义后使用/量词显式/条件完整/阈值区间分布精确/枚举受控/断言可机械核验；叙事（意图/动机/情绪）可保留
- **D3（执行强度）**：AI 打断 → 用户亲自重述 → AI 验证达标后继续。AI 不代写（代写剥夺思维训练本体）
- **D4（打断形式）**：固定句式指出具体模糊点（引用触发词+所在句子）+ 触发词类型提示（阈值模糊/枚举未受控/量词缺失/符号未定义，仅分类不代写）；**零容忍**，初犯同样打断
- **D5（写入位置）**：分层固化——①CLAUDE.md 新增「对话数学语言规范」条目（只增不删）②`docs/agents/math-language-writing.md` 新增 §七 对话交互规范（人类输入方向），与已有 AI 产出方向合并为单一权威文档 ③`data/term_registry.json` 入库「数学语言」「模糊量词」 ④决策树 + issue #85
- **D6（自我更新）**：对话规范受自己约束（自指）——发现未覆盖的模糊形态 → AI 指出"此为规范未覆盖项" → 记入待修订清单，grilling 结束或积累 5 条后单独讨论修订；修订只增不删

### 受影响文件

- `CLAUDE.md`（新增 §对话数学语言规范）
- `docs/agents/math-language-writing.md`（新增 §七 对话交互规范 + 目录/尾部更新）
- `data/term_registry.json`（入库「数学语言」「模糊量词」，144→146）
- `docs/决策树/`（本文）
- `docs/设计框架-六维状态.md`（管线维度状态更新）
- `memory/对话数学语言规范-grilling-85.md`

### 推迟

- 规范未覆盖模糊形态的修订清单 → 积累 5 条后单独讨论

---

## [Grilling] 故事主线框架 — 剧情系统设计 (2026-08-16，D 系列 4 项 + S 系列 8 项 + M 系列 5 项)

> Issue: [#86](https://github.com/verystrongdog/game/issues/86) | 维度: 事件+管线 | 前置: 世界观 ✅ / 游戏循环 ✅ / 任务目标系统 ✅ / Boss 框架 ✅ / 空间关卡 ✅ | 阻塞: 关键突破触发 / 多结局条件 / 素材库生产

### 话题

用户感悟：物理背景设计充分，但"有主观意识的个体如何与环境交互""剧情完整设计""选择如何影响个体变化"未细化。狗咬函数式思考法（条件-分支-状态机）应用到叙事层。经调研成熟 RPG（Bethesda 状态机任务/巫师 3 对话树/极乐迪斯科感官球+白文本/CRPG 3万变量全局状态）后定案。

### 决策 — 主线结构（D 系列）

- **D1（结构层）**：不新增叙事结构层——结构性主线 × 叙事性主线交汇即完整骨架。"幕/章节/节拍"为索引占位词，无设计定义；D11 已否决情节节拍式理解。本话题聚焦内容填充
- **D2（命名修正）**：「脊柱线/理解线」废弃 → 「结构性主线/叙事性主线」（旧名出处：决策树 :635 + 任务目标系统 §6.1；用户不记得命名过）
- **D3（剧情代码本体）**：模式 2 对话分支树统一载体——NPC/环境（感官球式）/内心（自问）三类节点同构
- **D4（内容量）**：≈ 300-350k 字 [EST]，AI 起草 + 人工审定

### 决策 — 对话树结构（S 系列）

- **S1（图形态）**：DAG + 有界回跳。类型 A（语境汇合）天然支持；类型 B（重复询问）状态差驱动——Q/R/f 无变化重复原话、有变化新回应
- **S2（节点字段）**：`{id, type, speaker, tags, entry_conditions, text, options[], passive_checks[]}` + 选项 `{text, condition, effect, next}`
- **S2+（演化策略）**：增 = WARNING 自由（JSON 超集，JsonSerializer 忽略未知属性）；删 = ERROR 护栏；新字段登记注册表
- **S3（会话语义）**：⟨entry, pointer, active, ended⟩；中途离开不回滚状态（连续世界一致性）
- **S4（节点-世界绑定）**：状态谓词 C'（查询 L/φ/T），交互时实时求值——非静态表（极乐迪斯科是静态城镇，本项目是月光驱动动态世界）。时段粒度 = 三时段
- **S5（三类节点）**：完全同构（仅 type 不同）；speaker 受控词表 speaker_entities.json
- **S6（多参与方）**：顺序化一对一会话序列（by_order/by_choice/by_condition）；规则 = 数据值 + 策略表 + fallback(by_order)——新增规则不破坏已有数据
- **S7（任务衔接）**：效果 = 任务接口调用；效果注册表 + PENDING 降级；task_contract.json 契约快照。路径 B：回报/放弃流程留待任务系统自身 grilling，接口前瞻
- **S8（呈现层）**：分层存储——text 客观层（D15 纯净）+ perceptions 受控类别层（6 类枚举：玩家_低SAN/玩家_高SAN/虔信者/理性者/完整体造物/default）

### 决策 — 素材库管线（M 系列）

- **M1（人机协同）**：用户构建角色背景（人脑综合：哪些经历塑造性格）+ AI 检索现实资料（事实收集）+ AI 派生工程化视图
- **M2（双轨存储）**：`实体/角色背景/<角色>.md`（纯文本原文，AI 不改写）+ `<角色>.gen.json`（AI 派生，schema 可拓展）；双向链接
- **M3（批次）**：自下而上——P1 普通 NPC 生态 → P2 重要 NPC → P3 14 角色核心层 → P4 Boss 生命史。顺序同构引擎管线（脑区数据 → 连接 → 涌现）
- **M4（起点切片）**：住院楼 1F 生态（玩家醒来楼层）；规模编写时定
- **M5（模板策略）**：不构建生态位模板——按具体情境逐 NPC 构建；素材驱动（先积累素材池，够大后挑选构建）

### 受影响文件

- `事件/剧情系统设计.md`（新建——主产物，全文 7 章）
- `事件/任务目标系统.md`（§6.1 命名修正：脊柱线/理解线 → 结构性主线/叙事性主线）
- `docs/维度/事件.md`（索引 + 待设计项更新）
- `docs/设计框架-六维状态.md`（事件 ✅ +2 → 9；空缺表故事主线/对话序列闭合）
- `docs/决策树/`（本文）
- `data/term_registry.json`（新术语入库：结构性主线/叙事性主线/对话树/剧情系统三元组/生态/切片/双轨存储等）
- `项目总览.md`（事件索引同步）
- `memory/剧情系统设计-grilling-86.md`

### 推迟

- 结局触发条件公式 → 数值校准 grilling
- 回报/放弃流程规格 → 任务系统自身 grilling（路径 B）
- validate_story.py / StoryEngine 实现 → 引擎 P 系列批次
- 素材库内容生产 → 后续逐 NPC（用户构建 + AI 检索）
- NPC 候选名单 → 素材积累足够后挑选（M5）

---

## [Grilling] 记忆内容层物理储存设计 (2026-08-20，D1-D8)

> Issue: [#90](https://github.com/verystrongdog/game/issues/90) | 维度: 规则+管线 | 前置: #87 创伤记忆语义（D6-D9）✅ | 阻塞: #88 转化规则（量化合成依赖本 issue schema）

### 话题

记忆内容层物理储存 = 运行时基础设施（从 #87-D10 拆出）：「一条记忆」的数据结构/存储位置/写入管线/检索接口/生命周期。现状核查：#91 动力学变量无记忆实体、m 是链路强度非内容、唯一先例 = 敌人跨战斗记忆（敌人与事件 §4.6）。数学基础 = 两份新建文献综述（[记忆储存机制-文献综述](../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E8%AE%B0%E5%BF%86%E5%82%A8%E5%AD%98%E6%9C%BA%E5%88%B6-%E6%96%87%E7%8C%AE%E7%BB%BC%E8%BF%B0.md)、[记忆数学模型-文献综述](../../%E5%8F%82%E8%80%83/%E6%96%87%E7%8C%AE/%E8%AE%B0%E5%BF%86%E6%95%B0%E5%AD%A6%E6%A8%A1%E5%9E%8B-%E6%96%87%E7%8C%AE%E7%BB%BC%E8%BF%B0.md)，2026-08-20 各 16/18 篇）+ 数学建模工作稿（六阶段状态机 E/C/S/R/RC/F）。

### 决策

- **D1（勾起函数）**：`P_trigger,j = σ(κ·s_j³ − θ_g)`，n 固定 3（Minerva 2 激活结构特征，非自由参数；更高次幂向硬阈值退化杀死阈下触发）；κ/θ_g [NEW] 待 #35。否决：线性+σ（判别弱）、硬阈值（阈下触发清零）、聚合回声 σ(κ·I−θ_g)（不能逐条定位）
- **D2（再巩固范围）**：提取=写操作应用于**全部记忆类型** + 改写幅度烈度分级（A+）：创伤大幅/普通轻微；`T_re ≤ 6h×τ_scale`；测试效应 `P_acc += δ_test` 全类型；未稳定化 → WEAKENED
- **D3（容量 + 黑箱语义）**：`cost_j = α/a_j`，`Σ_j cost_j ≤ Cap_max`（方案 B 去神经化，纯游戏参数）；`a_j = |T_j|/D`。**黑箱**：不建 CA3 回返网络、不引 DG（DK 无亚区分割，CA1/CA3 共享 1 OBJ）、内容层公式零解剖数据依赖。否决：Treves-Rolls `C_slot/(a·ln(1/a))`（语义漂移风险，复刻 #25 教训）、Hopfield 0.138N（N 映射无意义）。**海马内部环路建模 = 推迟单开 issue**
- **D4（存储位置）**：构建层持久（`MemoryRecord[]`，与 m 同层慢变量）+ 战斗层快照（`battle_active_memories` 只存 id+激活强度，战斗结束并入构建层）；否决战斗层单层（每战重建放不下跨战生命周期）/档案单层（每回合读写不现实）
- **D5（写入管线）**：四来源 `source ∈ {event, generated, script, observation}` + 双通道（预生成直写构建层、战斗事件经战斗层快照批量并入）。**可塑性巩固不是记忆创建来源**（三层分离：创建=自动/窗口=TryConsolidate 不触碰记录/强化=内容层机制；事件强度与烈度 A 共享输入独立公式）
- **D6（检索 s）**：`s_j = w₁·(P·T_j)/N + w₂·(c_R·c_E,j)`，w₁+w₂=1（内容+情境加权）；触发源分离（外部知觉→内容项、内部情绪→情境项，对接 #87-D7 双触发源）；情境向量 = 时间+地点+情绪+在场人物 [NEW]；消费方分家：P_trigger 供创伤/情境触发、P_success（θ_mem）供记忆类技能
- **D7（生命周期）**：八状态状态机（NEW/CONSOLIDATING/STABLE/RECONSOLIDATING/WEAKENED/FORGOTTEN/COMPARTMENTALIZED/RESET）+ 三条铁律（遗忘不作用于 m、提取=写操作、同一状态机覆盖全部类型）。**敌人跨战斗记忆并入统一幂律**（`P_acc(t)=P_acc(0)·t^(−b)`，Boss 差异 = b 参数化；「完整/50%/遗忘」降级为叙事化采样点；击败清零 = RESET；四件套 = behavioral payload）
- **D8（schema 定案）**：`type ∈ {behavioral, narrative, generic}`——**trauma 不作为 type**（创伤=烈度属性 I_mem 高，剂量-反应累积后无需改 type）；判定=写入管线结构可核验（behavioral⟺四件套/narrative⟺Conway 三层/generic⟺payload=∅ 正面定义）；`entities` 保留（关系索引，DID 共享矩阵 :1294/触发源在场人物/NPC 社交检索）；`index` 二进制 `{0,1}ᵈ`（强度由 I_mem 承载防双源）；事件快照字段 + A_trauma 阈值 = #88 定义

### 受影响文件

- `规则/技能树系统/记忆内容层.md`（新建——正典，schema + 六阶段 + 生命周期 + 接口）
- `../设计归档/grilling/grilling-90-memory-storage/数学建模-记忆过程.md`（新建——六阶段数学推导工作稿）
- `../设计归档/grilling/grilling-90-memory-storage/grilling-90.md`（issue 工作文件，D1-D8 决策记录）
- `参考/文献/记忆储存机制-文献综述.md`（新建——16 篇）
- `参考/文献/记忆数学模型-文献综述.md`（新建——18 篇）
- `docs/设计框架-六维状态.md`（规则/管线 ✅ 同步）
- `data/term_registry.json`（新术语入库候选：记忆内容层/可提取性/勾起/再巩固/区隔化等）
- `memory/记忆内容层-grilling-90.md`（新建）

### 相关决策树条目对接

- :2492 P1c D5「记忆检索效果」接口预留 → **→ 见本条目**（P_success 引擎层公式对接，内容层 P_trigger 提供勾起）
- :1374 跨战斗记忆「记模式不记回合」→ 本条目 D7（并入统一幂律 + behavioral payload）
- :1294 DID Alter 记忆共享矩阵 → 本条目 D8 entities 字段
- :527 脑功能层级「遗忘作用于记忆/访问层，不作用于 m」→ 本条目 D7 三条铁律 1
- :1955/:2040 战斗输出权重校准（θ_mem）→ 本条目 P_success（θ_mem 解释为 SDT 判据 c，数值仍归 #35）

### 推迟

- 海马内部环路建模（CA3 回返网络/DG 亚区）→ 单开 issue，不阻塞本条目
- 事件快照字段清单 + A_trauma 判定阈值 → #88 转化规则
- κ/θ_g/w₁/w₂/α/Cap_max/b/τ_scale 等数值 → #35 数值校准
- 健忘症角色解搁置 → 依赖本 schema 引擎实现（P 批次）
- 记忆引擎实现（MemoryRecord 数据结构/检索/生命周期）→ 引擎 P 系列批次（P1c 记忆检索效果对接）

---

## [Grilling] 三体模型左右偏侧化缺失 (2026-08-20，D1-D10)

> Issue: [#92](https://github.com/verystrongdog/game/issues/92) | 维度: 规则+管线 | 状态: ✅ 已完成 (2026-08-20) | 从 #88 Q0.1 拆出

### 话题

正常人类大脑存在稳健的左右功能差异（Kong 2018 ENIGMA 17,141 人：语言区左偏最强；Karolis 2019 四功能轴：语言→左、情绪→右），但三体模型（51 节点 L+R 合并）完全无法表达——#26 重构静默丢弃 #20 D10（决策树 :1414「DK 左右边独立，偏侧异常值得作为游戏机制」）的偏侧能力，无任何决策记录讨论此取舍（`脑功能层级模型.md` §二十 grep `左右/偏侧/半球/镜像` 零命中）。SZ 是唯一偏侧稳健的精神疾病（Schijven 2023 / Okada 2016 / Gutman 2022，效应量全部 |d|<0.1 极小）——合并节点无法表达"左"的异常。

### 决策

- **D1（Q1）— 节点级元数据（方案 B″）**：51 节点图不动，节点附加偏侧元数据，**显式声明不进战斗结算**。C″ 全拆 68 节点被否决（推翻 #26 D7，776 皮层-皮层边按偏侧重算，成本与 |d|<0.1 收益不成比例）。
- **D2（Q2）— SZ 单侧异常 = 元数据微调**：节点元数据记录健康基线；SZ 敌人/面具的节点取值偏离基线（rACC 反转、MTG 增大、苍白球左偏），仅展示/叙事锚点，不进结算。
- **D3（Q2b）— 可见性 A + 入库**：偏侧标签仅玩家自角色可见（黑箱原则，决策树 :51 + #88 Q0.4）；敌方/面具偏侧偏离如实入库（数据保真）。
- **D4（Q3）— β 单一连续系数**：`lateralization ∈ [−1,+1]`（负=左偏、正=右偏、0=双侧），Karolis 2019 偏侧系数原样实现；否决 α 双字段（方向枚举 + strength，信息冗余）。
- **D5（Q3b）— P1 解剖实体级**：一合并节点一系数，写 tripartite graph_nodes + brain_regions 对应实体。Kong 2018 偏侧定义在 DK 区域级；SZ 偏离区（MTG/rACC/苍白球）全单 functional_id。
- **D6（Q4）— M1 + 前向规则**：镜像（LC_R/SNc_R）复制主变体完整 10 字段剖面 + mirror_of 溯源；新镜像默认显示层、机制引用镜像 = 校验报错；偏侧字段不适用镜像。现状核验：仅 2 镜像、0 出边 0 端点；STN/上丘等双侧结构无镜像（非模式）。
- **D7（Q5）— Y′ 端点 + Δ**：pathology_edges.json 端点 = 50 实体名，附机器可读 `laterality_delta ∈ [−1,+1]`（默认 0）。X（DK 偏侧名 + 合并规则）否决：L_/R_ 名最终也须换算成 Δ，多包一层命名再做一次翻译。Y（偏侧仅注释）否决：与 D3 入库冲突。
- **D8（Q6）— Q0.1 以「B + Δ」定案**：#88 重映射锚点 = 50 实体名 + laterality_delta，双轨废止。依赖：#92 先闭合，#88 端点规格解除阻塞。
- **D9（Q7+Q8）— 显示层派生规则**：标签阈值 t=0.5 [NEW 初值可调]（|combined| ≥ t → 左/右偏标签，否则双侧，显示层专用零结算）；叠加 = baseline + ΣΔ 线性求和（不落盘），显示层 clamp [−1,+1]。
- **D10（Q9+Q10）— 正交声明 + Δ 随病理边**：mni_xyz = 解剖代表位置，与偏侧系数正交（坐标混杂是合并语义正常结果，不修正；3D 偏侧呈现留给呈现维度）；laterality_delta 随 pathology_edges.json 病理边走，受 [角色与面具.md §8.8.2](../../实体/角色与面具.md) 文献铁律约束（D2 方案 2 偏侧进 frontmatter 否决：与 #88 疾病文件扩展议题纠缠）。

### 受影响文件

- `规则/技能树系统/偏侧化架构.md`（新建——正典，字段规格/叠加规则/镜像处置/正交声明/参数速查表）
- `规则/技能树系统/脑功能层级模型.md`（§二十 新增 20.11 偏侧小节）
- `data/connectivity/tripartite_model.json`（graph_nodes 49 节点 + lateralization: 0.0，镜像 2 节点除外）
- `data/brain_regions.json`（58 个带 dk_name 条目 + lateralization；LC_R/SNc_R 镜像展开 10 字段 + mirror_of）
- `data/term_registry.json`（5 术语入库：偏侧化/laterality_delta/镜像实体/LC_R/SNc_R）
- `docs/设计框架-六维状态.md`（规则+管线状态同步）
- `memory/偏侧化架构-grilling-92.md`（新建）

### 相关决策树条目对接

- :1414 #20 D10「DK 左右边独立，偏侧异常值得作为游戏机制」→ 本条目 D1-D3 恢复并落地（可见但非机制）
- :1845 #26 D7 图节点模型（L+R 合并）→ 本条目 D1 补缺失记录（合并保留 + 元数据承载偏侧）
- :1847 #26 D8 mirror_of → 本条目 D6（展开 + 前向规则）
- :2817 #88 components/pathology_edges 全量 → 本条目 D7（Y′ 端点规格），内容填充回 #88

### 推迟

- 3D 偏侧呈现设计（标签/标注/高亮）→ 呈现维度（D10-A）
- t 值调参 → [NEW 初值可调]，后续验证
- 健康基线全量数值表（文献效应量 → [−1,+1] 换算）→ 内容批次（#88 或单独任务）
- pathology_edges.json 文件创建 + 每条 Δ 具体取值 → #88（26 病扩种批次）
- 偏侧化建议初值（语言区 −0.7 等 [NEW 待文献复核]）→ 内容批次

---

## [Grilling] 病因-疾病-神经系统模型关系 — 疾病脑部重映射 (2026-08-21，Q0-Q0.6 + 遗留项 1-5)

> Issue: [#88](https://github.com/verystrongdog/game/issues/88) | 维度: 规则+实体+管线 | 状态: ✅ 执行完成（2026-08-21） | 前置: #87 创伤记忆语义 ✅ + #90 记忆内容层 schema ✅ + #92 偏侧化架构 ✅

### 话题

创伤记忆→病理链路 m 偏移的转化接口（#87 拆出）在重映射前置讨论中扩展为**疾病→脑区映射全面重设计**：旧 link_NNN 系统（挂已废弃 link_registry.json）不适配三体模型（#26），疾病文件处于"文字半迁移、数据悬空"状态。

### 决策（Q0 系列）

- **Q0 前提核查**：4 类病理链路诞生于旧 364 链路时代（:128-140 破旧四规则）；#26 三体模型后 §8.8.1 文字改口但疾病数据未迁移；validate_disease.py 仍查废弃注册表 → 必须重映射
- **Q0.3 分类学锚定**：称呼层 DSM-5 + 表现层 **PANSS 五因子**（修正敌人与事件 §2.2 误标"ICD-11 症状域"，真实来源 PANSS，Fountoulakis 2019）+ 机制层解剖域三体边；**ICD-11 完全退出**（:1041 佐证）
- **Q0.4 命名标准（D 方案）**：DSM-5 诊断名正式称呼 + 疾病ID 唯一主键 + 解剖域标签；26 病入库 term_registry；黑箱原则（:51）
- **Q0.2 目录规模**：19 → **26 种**（+7：BPD/分裂型人格/躯体症状/惊恐/社交焦虑/恶劣心境 PDD/暴食 BED）
- **Q0.5 父类**：新建「人格障碍」（ASPD/BPD/分裂型，ASPD 自社会认知迁移）+「躯体症状」；8 父类
- **Q0.1 锚点**：#92-D8 定案：50 实体名 + laterality_delta ∈ [−1,+1]
- **Q0.6 范围**：玩家侧病理边 + 敌人侧 7 参数映射，双通道重映射（NPC AI §5.2 缺口补齐）

### 决策（待定项 1-5）

- **待定项1（双向振荡）**：m_offset 相位键 `{mania, depression}` 仅限 bipolar-I/II（14 条）；双向振荡 = 状态机机制非第 5 病理类型（底层按四类判定）；环性轻量时变走 hooks；schema v1.1
- **待定项2（schema）**：pathology_edges.json 平铺数组 + edge_id `<disease_id>_e<NN>` 全局主键 + `_schema_version`
- **待定项3（病理类型）**：§8.8 旧四规则 → 三体判定规则（机械可核验）；4 类型入库 term_registry
- **待定项4（迁移）**：19 旧病 link_NNN → pathology_edges 引用（精简格式）；边 ID 前缀统一为 disease_id（8 病 99 条重命名）
- **待定项5（校验器）**：validate_disease.py v2（查 pathology_edges + 相位键约束 + 前缀断言 + 父类主导类型校验）

### 产出

- `data/connectivity/pathology_edges.json`：**348 条病理边 / 26 病**，全部命中三体模型 1049 边（0 病理新增），35 条 Δ 非零（SZ 左语言网络/rACC/苍白球等），142 条⭐新增
- 26 病 pilot（`.scratch/grilling-88-etiology-disease-neural/*-pilot.md`）：文献锚点+病理边+7 参数映射+旧链路对照+行为覆盖
- 26 疾病文件（19 迁移 + 7 新）+ 8 父类；validate_disease.py v2 全量 0 ERROR 0 WARNING
- 7 参数映射规则（敌我同构闭环）：每病 tone+CSTC 与 NPC AI §5.2 标签验证；3 条 [NEW] 裁决规则（状态分离/域特异/标签缺口）

### 相关决策树条目对接

- :128-140 病理链路（破四规则）→ 本条目 Q0 前提 + 待定项3（三体判定规则替换）
- :1041 5 ICD-11 症状域降级 → Q0.3（PANSS 五因子落实）
- :2957 #92 偏侧化 → Q0.1 锚点（50 实体 + laterality_delta）
- :2817 #84 components/pathology_edges 全量 → 本条目（pathology_edges.json 已建，内容批次对接）

### 推迟

- 转化接口本体（E1-E3：事件快照字段/A_trauma 阈值/病因字段）→ 后续批次（#88 收尾遗留）
- [NEW] 幅值（+0.6 等）+ CGI-S 三档数值校准 → #35
- 7 新病组件掉落池再平衡 → 组件批次（14 角色映射表）
- 敌人 Stat 管线接入 pathology_edges → 敌人批次
- 14 角色疾病文件 frontmatter 父类路径 bug 修复（旧文件 `../_父类/`）→ 随角色批次

---

## [Grilling] 创伤记忆转化接口 — 数值敲定 (2026-08-21，D1-D6)

> 承接: #88（转化接口本体，原话题恢复）| 维度: 规则 | 前置: #88 重映射 ✅ + #90 schema ✅ | 状态: 结构锁定 + 数值 [NEW 初值可调]

### 话题

#88 关闭时推迟的转化接口本体（创伤记忆→疾病档位）恢复设计。用户澄清：①g 心智成熟系数 = 不成熟度（值域 ∈[0,1]，公式 `L=ΣΔI×g` 零改动）②创伤记忆无档位（连续量），档位是疾病层离散属性 ③数值本讨论敲定（不推 #35——#35 是战斗域，不同参数域）。

### 决策

- **D1（致病立场）**：C 定案——创伤 = 累积到阈值；无创伤+无器质+非发育 = 健康；未达单次阈值经剂量-反应累积突破。否决素质/遗传维度。
- **D2（g 不成熟度）**：g = 不成熟度 ∈ [0,1]（成熟者 g→0 → 负荷低；不成熟者 g→1 → 负荷高）；公式 `L = ΣΔI×g` 保持 #90 §3.2 原样。否决"g=成熟度需改公式 (1−g)"。
- **D3（双阈值）**：`病理化 ⟺ (I_max ≥ A_trauma_I) ∨ (L ≥ A_trauma_L)`——单次毁灭性或长期累积任一达标。A_trauma_I=0.7 [NEW]、A_trauma_L=1.0 [NEW]。
- **D4（双维档位）**：`s = clamp(g(L) + h(I_max), ∅, 重)`——L 定基础档（θ_L1=1.0/θ_L2=2.0/θ_L3=3.5 [NEW]），I_max 急性加成（θ_I=0.9 → +1 档 [NEW]）。L 定性、I 定量。
- **D5（演变）**：档位状态机 s(t) ∈ {∅,轻,中,重}——升档（L 增长跨阈值/I_max 更新）、降档（#90 ΔI_int<0 治疗）、RESET→∅；P_acc 衰减不降档（遗忘不作用于 m 铁律）。与 :1042 m 固定值调和（演变=档位状态切换，m 在模板值间跳变）。
- **D6（映射范围）**：疾病选择 = **M:N 候选集模型**——事件类型 → 候选疾病集 C(Rᵢ)（1→N，如性创伤→{PTSD,DID,BPD}）+ N/F/R 选主病 + 卫星病聚合达标成型；疾病层档位 = 指向该病的**聚合负荷**（N→1）。映射范围 = 全 **25** 经历型（26−ASD，#87"18 种"为扩种前数字）。事件类型开放枚举（增=未映射态+兜底，删=ERROR 护栏）。候选集映射表 [NEW 待逐类型填充]。

### 数值修正通道

结构（D1-D6）已锁定；数值（k/A_trauma/θ_L/θ_I）标 [NEW 初值可调]——模拟验证/设计评审后走校准批次或 Step 6 闭合后修正。

### 受影响文件

- `规则/技能树系统/创伤记忆转化接口.md`（新建——正典）
- `规则/技能树系统/记忆内容层.md`（A_trauma 移交标注 → 已定义）
- `docs/决策树/`（本文）
- `data/term_registry.json`（候选：不成熟度/转化接口）

### 推迟

- 事件类型枚举 + 父类/子类映射表 → 逐病内容批次
- k 人物脆弱性调制 → 后置
- 阈值验证 → 模拟批次

---

## [Grilling] 创伤记忆转化接口 — 本体完成（#88 原始问题 1-5 收尾，2026-08-21，D7-D12）

> 承接: #88 关闭时推迟的转化接口本体 | 维度: 规则 | 前置: 转化接口结构（D1-D6）✅ | 状态: ✅ 完成（#88 全部原始问题闭合）

### 决策（#88 原始问题 1-5 逐项）

- **D7（M:N 候选集）**：1 创伤→多病、N 创伤→1 病均临床存在 → 记忆层候选集 C(Rᵢ) + 疾病层聚合负荷。卫星病独立聚合阈值 ≥1.5。
- **D8（ADHD 移出）**：ADHD → 发育性（遗传度 ~74%，Faraone & Larsson 2019，与 ASD 同性质走 W_npc 直调）；经历型 25→24（26−ASD−ADHD）。
- **D9（立场 B）**：创伤 = 充分条件之一；无创伤 NPC 走素质-应激兜底 [NEW 待 #87 生成功能]。
- **D10（映射表）**：10 事件类型 → 候选集（24 经历型全覆盖）；SZ 谱创伤路径（Varese 2012 总体 OR 2.78, 95% CI 2.34-3.31；🔧 2026-09-06 勘误：原引 2.87 为性虐待亚组 CI 上界）、双相谱全覆盖、进食谱（BN/BED 共享）、新增控制剥夺/公开羞辱。
- **D11（主病选择）**：(N, F, D_seg) 三维偏好表 + 软边界匹配（argmax 负欧氏距离）；D_seg 对接 #90 COMPARTMENTALIZED，分离 PTSD(0.10)/DID(0.95)。
- **D12（收尾 3 项）**：①病因字段 = frontmatter `创伤易感事件类型` 只读镜像（24 病，唯一真相源=映射表）②分级文献铁律（病理边严格 §8.8.2 + 病因映射流行病学锚）③事件快照字段清单（#87→#88 交接契约 9 字段：event_type/A/N/F/D_seg/t_anchor/entities/g/k）。

### 受影响文件

- `规则/技能树系统/创伤记忆转化接口.md`（正典，§3.0-§3.2.2 完整）
- 24 经历型疾病文件（frontmatter `创伤易感事件类型`）
- `实体/疾病目录/注意缺陷多动障碍.md`（发育性声明）
- `docs/决策树/`（本文）

### 推迟

- 素质-应激兜底规则 → #87 生成功能
- 阈值模拟验证 → 校准批次
- 偏好表 (N,F,D_seg) 文献复核 → 内容批次
- 转化接口模拟脚本 → 可选（验证转化逻辑）

---

## [Grilling] 意识结构侧下一阶段路线 — 检验框架（可证伪化/Replication Invariance/跨系统 benchmark）(2026-08-27，Q1-Q6)

> Issue: [#93](https://github.com/verystrongdog/game/issues/93) | 维度: 规则（纯学术研讨，不入游戏正典——#40 先例）| 状态: ✅ 执行完成（2026-08-27）| 前置: v6 定稿（Layer0-2）+ #40（结构核/现象壳）+ #41（意识包裹，不涉）| 输入: ChatGPT 分享链接 ×11（链接 1 = 路线图本体，链接 2-11 = 用户逐题裁决）

### 话题

v6 定稿已知开放问题 #1（Diff 复制膨胀：S⊕S 使 Diff 2.70→5.33，CS′ 0→1）与 #2（F1/F9 边界反例）的下一阶段路线。ChatGPT 路线图主张：**不加第五指标，转向检验框架能走多远**。5 条线（L1 可证伪化 / L2 主体性攻击 / L3 跨系统 benchmark / L4 Layer 3 弱问题 / L5 T_CS 构造）逐题裁决。

### 决策（Q1-Q6，逐条对照写入）

- **Q1 总基线（D1）**：检验优先、不加第五指标。依据：v6 诚实结论 #2 已站队；加指标撞 #40 三重不可定义性论证（:2131）；F1/F9 误通过本质属 Layer 3 桥接 H 位置
- **Q2 判据结构级不变性（D2）**：CS′(S) = ⋁_{C∈𝒞(S)} CS′_local(C)；𝒞(S⊕R)=𝒞(S)∪𝒞(R)；Replication Invariance（复制不新增候选结构 + 无关模块不稀释）；B（稀释反噬）/C（问题混淆）/D（宽泛说法）否决；θ_D 不动
- **Q2.1 分量边（D3）**：E_S^(1) 单坐标结构依赖边（∃y,y′∈Reach: y₋ᵢ=y′₋ᵢ ∧ yᵢ≠y′ᵢ ∧ P_F(X′ⱼ|y)≠P_F(X′ⱼ|y′)）；分量=弱连通分量（非强连通）；规范定义=A（Layer 0/1 完整 F）、观测估计=D（Layer 3 TE/cTE，Ĉ_obs≠𝒞）；三性质（复制稳定性/单调性/同构不变性）为推论；冗余副本不产生边
- **Q2.2 Reach（D4）**：R1 = 正概率、μ₀ 锚定、无界时域、含瞬态；R2/R3/R4 否决（R3 实测退化：v5_check :104-121 full_reachable=Ω → Diff=N，判定为实现错误）；S1 采纳（一阶边边界，高阶 E^(k) 留 anomaly-triggered）；S2 采纳收紧（规范基本核，时间尺度不得动态选择）；限离散域
- **Q2.3 Diff 域（D5）**：Diff(C) = (1/(T+1))Σ_t H((π_C)_*μ_t) 轨迹分布熵；Capacity=log₂|Reach(C)| 降为诊断量；D-A/D-C 否决；μ₀=Unif(Ω) 为实验控制非理论公设；理论定义与有限样本估计分离
- **Q3 benchmark（D8）**：B1 结构——正类=prior-positive（桥接公设预期）、负类=anti-complexity controls、判别组={反馈控制器,CA,RL}；F+（负对照判 1）/F−（正类全判 0）双失败线；判别组无失败线；双轨对照（CS′_old vs CS′_new + 全要件表）；Sanity S1/S2（等式断言）+S3（只验证分解合并，不预设 CS′ 方向）；B2/B3 否决
- **Q3.1 执行协议（D9）**：A1——F+/F− 仅 simulation 轨（规范定义可精确计算才判理论失败）；观察轨报告估计值+不确定度+estimator validity；骨架锁定≠参数冻结
- **Q3.2 实例化（D10）**：H1——人脑轨 = synthetic observation / estimator-validity benchmark（F_known→𝒞_exact→synthetic→Ĉ_obs，严禁"合成≡人脑"）；paired/mechanism-matched control（F_open↔F_closed、Rule0↔Rule30/110、random↔Q-learning、F9↔F8′）；n≤8 为 v1 计算预算（非理论定义域）
- **Q4 SM 重建（D6）**：SM′=SelfRep∧SelfUse∧AgencyUse；语义四元组降为构造指南（违反跨基底）；AgencyUse 作用于外显动作变量 A（Δ_A(M)>0 结构性候选，统计阈值留统计层）；自反结构保留但不单独充分
- **Q4.1 SelfRep（D7）**：R-B 内部因果穿透——V=M⊍A⊍I，∃m≠m′,k∈I: P_F(X′_k|do(M=m))≠P_F(X′_k|do(M=m′))；A=∅ 退化条款（封闭系统 I=V∖M）；R-B 为必要条件非充分；R-C（预测性）降为辅助指标；判别三角 F1（缺 M→I,M→A）/F9（缺 M→I）/F8′（三者满足）
- **Q5 L4 定位（D11）**：L4=收束/边界层非指标搜索层；收紧表述"当前框架未推出结构同构⟹现象同一，相反主张需额外桥接公设"；L4 无失败线；B（指标完备性）= anomaly-triggered route
- **Q6 L5 定位（D12）**：T_CS 构造超出当前框架定义域（哥德尔中性 v5.3 性质 3；#40 D7 表征路线失败 :2153；#40 D8 类比非定理 :2154）；记推迟清单非否决

### 受影响文件

- `参考/意识结构侧-下一阶段路线-v7.md`（新建——v7 定稿，Q1-Q6 全量决策 + v6 开放问题对照表 + 参数速查表）
- `参考/意识结构侧-Layer0-2定稿-v6.md`（开放问题 #1/#2/#3/#5/#6 加注「→ 见 v7」+ 头部衔接声明 + 关联更新）
- `docs/决策树/`（本文）
- `data/term_registry.json`（候选入库，待用户确认——见 issue 关闭评论）

### 相关决策树条目对接

- :2113-2125 #40（结构核/现象壳、不可定义性三重论证）→ 本条目 Q1 依据 + Q5/Q6 收束
- :2153 #40 D7（自指环：表征路线失败）→ Q6 依据
- :2154 #40 D8（哥德尔类比非证明）→ Q6 依据
- v6 定稿「已知开放问题」→ 本条目 Q2-Q4.1 全部对应处理（见 v7 §十对照表）

### 推迟

- **模拟实现批次**：分量分解（E_S^(1)/Reach/𝒞）+ Diff(C) 轨迹熵 + R-B do 测试（F1/F8′/F9 判别三角实测）+ benchmark 参数化（10 类 paired 系统，n≤8 exact 轨 + scaled observation 轨）——脚本实现时逐项验证 → **已完成，见 [#94 模拟实现批次](https://github.com/verystrongdog/game/issues/94)**（sim_consciousness_v7_* 三脚本，2026-08-27）
- **T_CS 构造**（哥德尔中性外，非当前定义域；#40 D7/D8 衔接）
- 高阶依赖 E^(k)/超图（anomaly-triggered，Q5 D11 条件触发）→ **见 #97 分拣（维持原状态）**
- 连续状态空间 Reach 定义（Q2.2 定义域外）→ **见 #97 分拣（维持原状态）**
- 任务化 μ₀ 实验轨（Q2.3 D5，robustness/任务条件）→ **见 #97 分拣（维持原状态）**
- SelfRep 充分定义（R-B 仅为必要条件，v7 §六）→ **见 #97 分拣（维持，另开 grilling）**

## [Grilling] 模拟实现批次 — v7 定义落地为可机检 sim（分量分解/Diff轨迹熵/R-B判别三角/benchmark）(2026-08-27)

> Issue: [#94](https://github.com/verystrongdog/game/issues/94) | 维度: 规则（纯学术研讨，不入游戏正典——#40/#93 先例）| 状态: ✅ 执行完成（2026-08-27）| 前置: v7 定稿 ✅（Grilling #93）| 输入: 用户批次草案 + ChatGPT 分享 ×7（t_6a8f1aef…/t_6a8f1ba3…/t_6a8f1c74…/t_6a8f1ce6…/t_6a8f1df3…/t_6a8f2198…/t_6a8f23e1…）

### 话题

决策树 :3163 #93 推迟清单首位的「模拟实现批次」——把 v7 定稿的数学定义落成可机检 sim 脚本，逐项实测验证。按依赖顺序拆 3 脚本：分量分解（脚本 1）→ R-B 判别三角（脚本 2）→ B1 benchmark（脚本 3）。

### 决策（本批 D1-D7 + v7 D8/D9/D10 落地确认）

- **D1 范围**：脚本 1 = 完整 `CS′_local(C)`（四要件局部化），Replication Invariance 用完整判据断言（禁 Diff-only 代理验收——Int/SB/SM 局部化在 S⊕S 下漂移会制造假阳性）；验收分层输出（分量分解 → 分量指标 → Local CS′ → System CS′ → Replication）
- **D2 核精确化**：`exact_kernel(step_fn, n)` 唯一派生 P(y′|y)——逐位扩展枚举 + 按实际消费位串去重（条件消费语义，未消费尾位不重复计数）；禁为 F1/F8/F9 手工维护第二套核定义；统一接口 `System=(name,n,step_fn,M_set,A_set)`；n≤8 exact 轨显式报错不降级采样；step 随机性用 `rng.bernoulli(p)` 原语（`random()<p` 语义等价改写——黑盒 random() 无法让核提取器获知阈值）
- **D3 四要件局部化**：`CS′_local(C)=Int_local>0 ∧ Diff(C)≥θ_D ∧ SB_local ∧ SM_local`；`SM′=RB_I∧RB_A`（do 条件均匀权重 w(y|M=m)=1/|{y:y_M=m}|，不跟随 μ_t）；退化条款入原语（M∩C=∅→0；A∩C=∅→仅 RB_I）；分量闭包断言（无跨分量边 ⟹ 核因式分解 ⟹ 每分量动力学封闭）；Int 的 P_π^cut = IIT cut 核（块输入截断+均匀边缘化，v5_check :124-137 先例——非「y′ 联合独立化」，后者对独立噪声系统恒 0）；SB 用稳态精确 TE（非轨迹估计——D2 exact 轨）
- **D4 Diff 参数**：T=64 固定（混合判定否决——ε 成为塞进 Diff 的隐藏时间尺度自由度）；熵底 log2；数值冻结表（θ_D=3bit、SB 阈值复用 cs4 :26-30/v5_check :36-39 从来源读取、Int μ=稳态幂迭代、μ₀=Unif(Ω)）；H(μ_t^C) 序列 + 稳态熵 H_C(∞) 仅诊断（D4 写死防替代）
- **D5 F8′ 构造**：F8 + (z1,z2) 内部寄存器（n=6，M={m1,m2} A={y1,y2} I={z1,z2}）；z′=m 强度 0.9；z 不得反向影响 M/A（禁 M→I→A）；F8 原有动力学零改动；1 个 z 即足 RB_I，2 个维持与 (m1,m2) 配对；RB 必须 do-kernel 实测（非构造直接赋值）
- **D6 闭合后修正（2026-08-27）**：F8′ A 通道 XOR→直接依赖（`ny1=m1 if 0.6`）——实测发现 v7 §六 AgencyUse 的边际 do 比较对 XOR 型 M→A 数学上不可见（`P(y1′|do(m1=0))=P(y1′|do(m1=1))=0.5`，单步/多步干预皆然）；判定器零改动；F8 保留 XOR 作自然负例（「存在结构上的 M→A XOR 依赖 ≠ 边际 AgencyUse do 检验可见」——暴露 v7 RB_A 检测边界而非缺陷）；(b) 条件化 do 否决（打开条件变量选择/多条件/条件分布/可比性一整套定义自由度）；(c) 接受 RB_A=False 否决（F8′ 失去正例功能）
- **D7 脚本 2 装载**：F1 M={j1,j2} A=Y={c0,c1,c2} I={fb}；F9 M={m1,m2} A={a1,a2} I={s}（sensor 入 I）；判别三角断言对象 = SM′（F1=0/F9=0/F8′=1）；Y∖M→M 表征形成为诊断列（E 边 (i∈A∪I)→(j∈M) 检验）不进 SM′
- **v7 D8 落地确认（D8′）**：B1 十类 = 负 4 + 正 3 + 判别 3，每类 rep + 预期负控制，paired 只改声明目标机制；「预期负控制」= 实验预期非验收定义（不得为满足预期修改系统/判定器，意外成立记录为实验反例）；paired 原则上保持 V/M/A/I 不变（目标机制本身致 I 变化 = 结构性变化显式记录）
- **v7 D9 落地确认**：#6 人脑数据 synthetic observation 轨（报告估计值+不确定度+estimator validity），不触发 exact failure line；F+ = ∃负类判 1、F− = ∀simulation 轨正类判 0（单个正类 0 不失败）；判别组无失败线
- **v7 D10 落地确认（D10′）**：M/A = benchmark 规范输入（非从系统推断的事实语义，防「研究者怎么选都可以」自由度）；负类 M=∅/A=∅（SM′=0 是规范选择+退化条款结果，不解释成「证明无自模型结构」）；正类构造指南翻译；判别组结构规范（CA M={格0}/A=∅，RL M={状态}/A={动作}）；类别标签/预期结果不参与判定计算

### 实测结论（sim_consciousness_v7_components.py / rb_test.py / benchmark.py）

- **脚本 1**：Replication Invariance 双边 ✅（0→0：CS′(F8⊕F8)=CS′(F8)=0，分量 1→2 复制稳定性 + 张量积核与直和枚举抽查一致；1→1：CS′(F8′)=1、CS′(F8′⊕R)=1 加惰性模块不稀释）；v5.3 full_reachable=Ω 退化修复 ✅（S″ 逐分量 1bit、S‴ 分量 [[0,2],[1],[3]]、S* 1.015bit 全拒——旧容量误判消失）；闭包/因式分解断言全 ✓
- **脚本 2**：判别三角 F1=0/F9=0/F8′=1 全过——v6 边界反例（F1 旧记录 CS′=1）被 SM′ 排除 ✅，F9（状态估计+反馈控制）同样被排除
- **脚本 3**：失败线未触发（F+：负类 8 系统全 0——F_fwd Diff_global=5.0 等高 Diff 系统也因 SM 退化被拒；F−：B_cpg=1、F8′=1，H_loop=0 为 observation 轨失败观测——分量分解显示为两个 2-回环逐分量 Diff=2bit<θ_D）；判别组 F9_rep=1（反馈控制器+内部表征=1 画边界）；S1 复制等式/S2 惰性模块/S3 耦合合并单分量全 ✅；Δ(Int,Diff,SB,SM) 表显示 SM′ 对目标机制敏感（抑制性耦合/M→I ΔCS′=−1、内部表征 ΔCS′=+1）

### 受影响文件

- `sim_consciousness_v7_components.py` / `sim_consciousness_v7_rb_test.py` / `sim_consciousness_v7_benchmark.py`（新建——模拟实现批次三脚本）
- `docs/决策树/`（本文 + #93 推迟项标注「→ 见 #94」）
- `../设计归档/grilling/grilling-94-sim-batch/grilling-94.md`（本批决策日志 D1-D7 + D8′/D10′ + 实测记录）
- `参考/意识结构侧-下一阶段路线-v7.md`（衔接：#93 推迟项 → #94 完成；v7 定义未被修改——D6 为构造修正非定义修正）

### 推迟

- 脚本 3 observation 轨深化（#6 estimator-validity 完整实验：样本量/噪声/时间分辨率/观测缺失梯度）→ **已完成设计，见 [#95](https://github.com/verystrongdog/game/issues/95)**（Q1-Q19；脚本 4 实现见 [#96](https://github.com/verystrongdog/game/issues/96)，cTE 并入见 [#97](https://github.com/verystrongdog/game/issues/97)）
- scaled observation 轨（n≫8 采样估计轨，D 条款）→ **见 #97 分拣（维持阻塞）**
- SelfRep 充分定义（R-B 仅为必要条件，v7 §六，保留）→ **见 #97 分拣（维持，另开 grilling）**
- 高阶依赖 E^(k)/超图（anomaly-triggered，v7 Q5 D11，保留）→ **见 #97 分拣（维持原状态）**
- 任务化 μ₀ 实验轨（v7 §五，保留）→ **见 #97 分拣（维持原状态）**
- 连续状态空间 Reach（v7 §四定义域外，保留）→ **见 #97 分拣（维持原状态）**

---

---
*创建: 2026-09-12（由 docs/决策树/ 拆分）| 更新: 2026-09-12*
*关联: [决策树总索引](README.md), [设计框架-六维状态](../设计框架-六维状态.md)*
