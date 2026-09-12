# Grilling #26 三体神经模型 — 实施任务计划

> Grilling #26 (GitHub #27) 结论：废弃 364 链路 pairwise 有向模型，替换为三体神经模型（CSTC 环路 + 皮层-皮层连接 + 脑干广播）。主轮 12 决策 + review-plan 追加 4 决策 = 16 项设计决策。

## 目录

1. [决策清单](#一决策清单)
2. [signal_type 受控词表](#二signal_type-受控词表)
3. [功能剖面草案 — 首批 15 实体](#三功能剖面草案--首批-15-实体)
4. [任务分解](#四任务分解)
5. [文件清单](#五文件清单)
6. [验收标准](#六验收标准)
7. [依赖与阻塞](#七依赖与阻塞)

---

## 一、决策清单

| 编号 | 决策 | 类型 | 来源 |
|------|------|------|------|
| D1 | 采用三体神经模型（CSTC 环路 + 皮层-皮层 + 脑干广播），替代 364 链路 pairwise 有向模型 | 架构 | 主轮 |
| D2 | CSTC 环路 3 类：躯体（M1/S1→Putamen）、认知（dlPFC→Caudate）、边缘（vmPFC/Amygdala→NAcc），边缘=调节器非动作通道 | 设计 | 主轮 |
| D3 | 每个 CSTC 环路内含 GO（D1 直接）/ NO-GO（D2 间接）/ STOP（STN 超直接）三通路 | 设计 | 主轮 |
| D4 | 皮层-皮层连接遵循 EDR（距离指数衰减）+ 层级规则（\|Δlevel\|≤1）+ 双向互惠（Markov 2013） | 设计 | 主轮 |
| D5 | 脑干广播 3 系统：LC→NE（全皮层）、中缝→5-HT（全皮层）、VTA/SNc→DA（纹状体+PFC） | 设计 | 主轮 |
| D6 | 新增 STN（底丘脑核）到解剖实体，删除 BasalGangliaIndirectPathway 和 AmygdalaHippocampus | 数据 | 主轮 |
| D7 | 图以 dk_name 为节点（50+STN=51），functional_id 为节点的通信模式标签，连接在 dk_name 之间 | 架构 | 追加 G2 |
| D8 | 功能剖面以 functional_id 为粒度写入，镜像变体（LC/LC_R, SNc/SNc_R）用 mirror_of 引用共享 | 数据 | 追加 G2 |
| D9 | function_profile 增加 cstc_loop 字段（somatic/cognitive/limbic/none），脚本按同环路匹配角色节点生成 CSTC 连接 | 设计 | 追加 G3 |
| D10 | signal_type 受控词表：4 大类 × 4-6 子类 = 19 个受控枚举，写入 data/signal_types.json | 数据 | 追加 G1 |
| D11 | EDR 放宽至 p ≥ 0.10（覆盖几乎所有解剖可行的皮层对），功能筛选交给 function_label 层的 output_types ∩ input_types 交集 | 设计 | 追加 G6 |
| D12 | 图节点模型：皮层-皮层=信息传递，CSTC=门控决策，脑干广播=全局状态调制——三种通信原语不平压为 pairwise 边 | 架构 | 主轮 |
| D13 | gameplay_domain 受控词表 12 项 | 设计 | 主轮 |
| D14 | Kroell 14 网络从硬编码 dict 迁移到 JSON 数据文件 | 数据 | 主轮 |
| D15 | 旧 364 链路脚本 + 数据文件 → 垃圾桶（9 个文件） | 清理 | 主轮 |
| D16 | 全程垃圾隔离：grep 所有引用并更新 | 清理 | 主轮 |

---

## 二、signal_type 受控词表

> 所有 function_profile 的 input_types/output_types 必须从此词表取值。`data/signal_types.json` 管理完整定义。底层锚点：excitation/gating 来自突触传递二分（Albin et al. 1989），modulation 来自神经调质分类（Marder 2012），plasticity 来自 LTP/LTD（Bear & Malenka 1994）。

### 4 大类 × 19 个子类

| 大类 | 子类 | 含义 | 解剖载体示例 |
|------|------|------|------------|
| **excitation** | motor_command | 运动指令 | M1, 旁中央小叶 |
| | sensory_feature | 感觉特征 | V1, A1, S1 |
| | cognitive_goal | 认知目标/策略 | dlPFC, ACC |
| | emotional_salience | 情绪突显/威胁标记 | Amygdala, Insula |
| | memory_trace | 记忆痕迹（已编码信息） | Hippocampus, Entorhinal |
| | social_intention | 社会意图/心理化 | TPJ, vmPFC, Broca |
| **modulation** | arousal_NE | 唤醒/警觉调制（NE） | LC |
| | reward_DA | 奖赏预测误差（DA→NAcc/PFC） | VTA |
| | motor_DA | 运动启动/活力调制（DA→Putamen/Caudate） | SNc |
| | mood_5HT | 情绪/冲动调制（5-HT） | 中缝背核, 中缝正中核 |
| | pain_opioid | 疼痛抑制/镇痛 | PAG |
| **gating** | go_direct | GO 信号：D1 直接通路去抑制 | Putamen, Caudate, NAcc (D1 MSNs) |
| | nogo_indirect | NO-GO 信号：D2 间接通路维持抑制 | Putamen, Caudate, NAcc (D2 MSNs) |
| | stop_hyperdirect | STOP 信号：STN 超直接紧急刹车 | STN |
| | disinhibition_thalamic | 丘脑去抑制释放（苍白球输出） | Pallidum→Thalamus |
| **plasticity** | ltp_consolidation | 长时程增强/髓鞘化巩固 | Hippocampus (CA1), 广泛皮层 |
| | ltd_depression | 长时程抑制/突触减弱 | 小脑皮层, 广泛皮层 |
| | context_code | 情境编码/模式分离 | Hippocampus (CA3/CA1), Entorhinal |

---

## 三、功能剖面草案 — 首批 15 实体

> 每个功能剖面 10 个字段。**以 functional_id 为粒度**——同 dk_name 的多个 functional_id 各自独立剖面。镜像变体（LC/LC_R, SNc/SNc_R）用 `mirror_of` 引用。input_types/output_types 全部使用 §二 受控词表。

### 3.1 M1 — Precentral (L3)

| 字段 | 值 |
|------|-----|
| primary_function | Voluntary motor command execution; final cortical output for skeletal movement |
| input_types | [excitation/sensory_feature, gating/go_direct, gating/stop_hyperdirect] |
| output_types | [excitation/motor_command] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | gamma |
| cstc_loop | somatic |
| cstc_role | cortical_input |
| hierarchy_direction | feedforward |
| gameplay_domain | motor_execution |

**来源**：Mesulam 1998 (L3 primary motor); Alexander, DeLong & Strick 1986 (motor CSTC)

### 3.2 S1 — Postcentral (L3)

| 字段 | 值 |
|------|-----|
| primary_function | Somatosensory processing: touch, proprioception, pain, temperature |
| input_types | [gating/disinhibition_thalamic] |
| output_types | [excitation/sensory_feature, modulation/pain_opioid] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | gamma |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | feedforward |
| gameplay_domain | sensory_perception |

**来源**：Mesulam 1998 (L3 primary sensory)

### 3.3 V1 — Pericalcarine (L3)

| 字段 | 值 |
|------|-----|
| primary_function | Primary visual processing: edge detection, orientation, spatial frequency |
| input_types | [gating/disinhibition_thalamic] |
| output_types | [excitation/sensory_feature] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | gamma |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | feedforward |
| gameplay_domain | sensory_perception |

**来源**：Mesulam 1998 (L3 primary visual); Felleman & Van Essen 1991

### 3.4 A1 — TransverseTemporal (L3)

| 字段 | 值 |
|------|-----|
| primary_function | Primary auditory processing: frequency, pitch, sound localization |
| input_types | [gating/disinhibition_thalamic] |
| output_types | [excitation/sensory_feature] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | gamma |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | feedforward |
| gameplay_domain | sensory_perception |

**来源**：Mesulam 1998 (L3 primary auditory)

### 3.5 Amygdala — Amygdala (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Emotional salience detection and fear conditioning; subcortical shortcut (~50ms) + cortical route |
| input_types | [excitation/sensory_feature, excitation/emotional_salience, plasticity/context_code] |
| output_types | [excitation/emotional_salience, plasticity/ltp_consolidation] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | theta |
| cstc_loop | limbic |
| cstc_role | cortical_input |
| hierarchy_direction | both |
| gameplay_domain | threat_defense |

**来源**：LeDoux 2000; McGaugh 2004; Haber 2016
**注**：Amygdala 在 limbic CSTC 中同时承担两种角色——(a) 作为 cortical_input 参与环路闭合（Amygdala→NAcc→Pallidum→Thalamus→Amygdala），传递情绪突显信号给纹状体门控；(b) 通过 subcortical shortcut（Amygdala→PAG/LC/下丘脑，~50ms）作为独立调节器，不经 CSTC 环路的快速防御响应。前者符合 D2 的环路建模，后者是 amygdala 特有的并行通路

### 3.6 HippocampusCA1 — Hippocampus (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Episodic memory consolidation and pattern completion; NMDA-dependent LTP for long-term storage |
| input_types | [plasticity/context_code, excitation/emotional_salience, modulation/arousal_NE] |
| output_types | [excitation/memory_trace, plasticity/ltp_consolidation] |
| timescale | medium |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | theta |
| cstc_loop | limbic |
| cstc_role | cortical_input |
| hierarchy_direction | both |
| gameplay_domain | memory_consolidation |

**来源**：Buzsáki 2002; O'Keefe & Nadel 1978

### 3.7 HippocampusCA3 — Hippocampus (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Pattern separation and rapid encoding; auto-associative network for novel context detection |
| input_types | [excitation/sensory_feature, excitation/cognitive_goal] |
| output_types | [plasticity/context_code, excitation/memory_trace] |
| timescale | medium |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | theta |
| cstc_loop | limbic |
| cstc_role | cortical_input |
| hierarchy_direction | both |
| gameplay_domain | memory_consolidation |

**来源**：Buzsáki 2002; Rolls 2013 (CA3 auto-association)

### 3.8 NAccShell — Accumbens-area (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Emotional reward processing; limbic striatal gate for affective value → approach motivation |
| input_types | [modulation/reward_DA, excitation/emotional_salience, modulation/motor_DA] |
| output_types | [gating/go_direct, gating/nogo_indirect] |
| timescale | medium |
| neurotransmitter_dominant | GABA |
| oscillatory_band | theta |
| cstc_loop | limbic |
| cstc_role | striatal_gate |
| hierarchy_direction | both |
| gameplay_domain | reward_learning |

**来源**：Haber 2016; Berridge & Robinson 1998 (incentive salience)

### 3.9 NAccCore — Accumbens-area (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Motor interface for reward-driven action; translates limbic motivation to motor output via VP→MD→ACC |
| input_types | [modulation/reward_DA, modulation/motor_DA, excitation/emotional_salience] |
| output_types | [gating/go_direct, gating/nogo_indirect] |
| timescale | medium |
| neurotransmitter_dominant | GABA |
| oscillatory_band | theta |
| cstc_loop | limbic |
| cstc_role | striatal_gate |
| hierarchy_direction | both |
| gameplay_domain | reward_learning |

**来源**：Haber 2016 (NAcc core→VP→MD pathway); Humphries & Prescott 2010

### 3.10 VTA — VentralTegmentalArea (brainstem, L0)

| 字段 | 值 |
|------|-----|
| primary_function | Dopamine prediction error broadcast: reward/aversion signal to NAcc, Caudate, Putamen, PFC |
| input_types | [excitation/emotional_salience, excitation/sensory_feature] |
| output_types | [modulation/reward_DA, plasticity/ltp_consolidation] |
| timescale | fast |
| neurotransmitter_dominant | dopamine |
| oscillatory_band | theta |
| cstc_loop | none |
| cstc_role | modulator |
| hierarchy_direction | feedforward |
| gameplay_domain | reward_learning |

**来源**：Schultz et al. 1997; Hansen et al. 2024; Haber 2016

### 3.11 SNc — SubstantiaNigraParsCompacta (brainstem, L0)

| 字段 | 值 |
|------|-----|
| primary_function | Nigrostriatal dopamine for action initiation, vigor, and habit reinforcement; D1/D2 modulation |
| input_types | [excitation/motor_command, gating/nogo_indirect] |
| output_types | [modulation/motor_DA, plasticity/ltd_depression] |
| timescale | medium |
| neurotransmitter_dominant | dopamine |
| oscillatory_band | beta |
| cstc_loop | none |
| cstc_role | modulator |
| hierarchy_direction | feedforward |
| gameplay_domain | motor_execution |

**来源**：Hansen et al. 2024; Graybiel & Grafton 2015; Alexander 1986

> **SNc_R**: `mirror_of: "SubstantiaNigraParsCompacta"`，左右镜像变体共享剖面。

### 3.12 LC — LocusCoeruleus (brainstem, L0)

| 字段 | 值 |
|------|-----|
| primary_function | Norepinephrine-mediated global arousal and attention; diffuse NE broadcast to entire neocortex |
| input_types | [excitation/cognitive_goal, excitation/emotional_salience] |
| output_types | [modulation/arousal_NE] |
| timescale | slow |
| neurotransmitter_dominant | norepinephrine |
| oscillatory_band | theta |
| cstc_loop | none |
| cstc_role | modulator |
| hierarchy_direction | feedforward |
| gameplay_domain | arousal_modulation |

**来源**：Foote & Morrison 1987; Aston-Jones & Cohen 2005; Hansen et al. 2024

> **LC_R**: `mirror_of: "LocusCoeruleus"`，左右镜像变体共享剖面。

### 3.13 PAG — PeriaqueductalGray (brainstem, L0)

| 字段 | 值 |
|------|-----|
| primary_function | Defensive behavior coordination: freeze/flight/fight + descending pain modulation |
| input_types | [excitation/emotional_salience, excitation/cognitive_goal] |
| output_types | [modulation/pain_opioid, excitation/motor_command] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | theta |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | feedforward |
| gameplay_domain | threat_defense |

**来源**：Bandler & Shipley 1994; Hansen et al. 2024; Pessoa 2024

### 3.14 Putamen — Putamen (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Sensorimotor action selection and habit execution; somatic CSTC gate for motor programs |
| input_types | [excitation/motor_command, modulation/motor_DA, gating/disinhibition_thalamic] |
| output_types | [gating/go_direct, gating/nogo_indirect] |
| timescale | medium |
| neurotransmitter_dominant | GABA |
| oscillatory_band | beta |
| cstc_loop | somatic |
| cstc_role | striatal_gate |
| hierarchy_direction | both |
| gameplay_domain | motor_execution |

**来源**：Alexander et al. 1986; Graybiel & Grafton 2015; Baladron et al. 2020

### 3.15 Caudate — Caudate (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Cognitive action selection and goal-directed behavior; cognitive CSTC gate for prefrontal decisions |
| input_types | [excitation/cognitive_goal, modulation/motor_DA, gating/disinhibition_thalamic] |
| output_types | [gating/go_direct, gating/nogo_indirect] |
| timescale | medium |
| neurotransmitter_dominant | GABA |
| oscillatory_band | theta |
| cstc_loop | cognitive |
| cstc_role | striatal_gate |
| hierarchy_direction | both |
| gameplay_domain | cognitive_control |

**来源**：Alexander et al. 1986; Haber 2016; Peng et al. 2024

### 3.16 StriatumMatrix — Caudate (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Automated habit execution and chunked action sequences; striosome/matrix compartment for skill automaticity |
| input_types | [excitation/motor_command, modulation/motor_DA, gating/go_direct] |
| output_types | [excitation/motor_command, plasticity/ltd_depression] |
| timescale | medium |
| neurotransmitter_dominant | GABA |
| oscillatory_band | beta |
| cstc_loop | somatic |
| cstc_role | striatal_gate |
| hierarchy_direction | both |
| gameplay_domain | habit_learning |

**来源**：Graybiel & Grafton 2015 (striosome→habits, matrix→goal-directed)

### 3.17 Pallidum — Pallidum (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Basal ganglia output gate: tonic thalamic inhibition; striatal GABA disinhibits → GO release |
| input_types | [gating/go_direct, gating/nogo_indirect, gating/stop_hyperdirect] |
| output_types | [gating/disinhibition_thalamic] |
| timescale | fast |
| neurotransmitter_dominant | GABA |
| oscillatory_band | beta |
| cstc_loop | none |
| cstc_role | pallidal_output |
| hierarchy_direction | both |
| gameplay_domain | action_gating |

**来源**：Alexander et al. 1986; Nambu 2015; Albin, Young & Penney 1989

### 3.18 Thalamus — Thalamus-Proper (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Sensory-motor relay and CSTC loop closure; thalamocortical gating via VA/VL (motor) and MD (prefrontal) |
| input_types | [gating/disinhibition_thalamic, excitation/sensory_feature, modulation/arousal_NE, modulation/mood_5HT] |
| output_types | [gating/disinhibition_thalamic] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | alpha |
| cstc_loop | none |
| cstc_role | thalamic_relay |
| hierarchy_direction | both |
| gameplay_domain | thalamic_relay |

**来源**：Jones 2007; Saalmann & Kastner 2012; Pessoa 2024

### 3.19 ThalamusPulvinar — Thalamus-Proper (L1)

| 字段 | 值 |
|------|-----|
| primary_function | Visual attention routing; dynamically gates cortico-cortical visual information flow based on attentional demand |
| input_types | [excitation/sensory_feature, excitation/cognitive_goal] |
| output_types | [gating/disinhibition_thalamic] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | alpha |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | both |
| gameplay_domain | thalamic_relay |

**来源**：Saalmann & Kastner 2012 (pulvinar attention routing); Jones 2007

### 3.20 STN — SubthalamicNucleus (brainstem, L0) [NEW]

| 字段 | 值 |
|------|-----|
| primary_function | Hyperdirect emergency brake: cortex→STN→GPi fast excitation, globally suppresses all ongoing action |
| input_types | [excitation/motor_command, excitation/cognitive_goal, excitation/emotional_salience] |
| output_types | [gating/stop_hyperdirect] |
| timescale | fast |
| neurotransmitter_dominant | glutamate |
| oscillatory_band | beta |
| cstc_loop | none |
| cstc_role | none |
| hierarchy_direction | feedforward |
| gameplay_domain | action_gating |

**来源**：Nambu 2015 (hyperdirect pathway); Paxinos & Mai 2004 (STN anatomy)
**注**：STN 服务所有 3 条 CSTC 环路的 STOP 通路。不参与 cstc_loop 分组——作为全局急停信号，STN→Pallidum 连接在 build_tripartite_model.py 中独立生成。

---

## 四、任务分解

### Phase 1: 数据层（data/）

#### Task 1.1 — 创建 signal_type 受控词表
- **产出**：`data/signal_types.json`
- **内容**：4 大类 × 19 子类，每子类含 `id` / `category` / `definition` / `anatomical_carriers`
- **来源**：§二
- **预计**：~100 行 JSON

#### Task 1.2 — 新增 STN 实体
- **产出**：`data/brain_regions.json` 新增 `SubthalamicNucleus` functional_id 条目
- **内容**：MNI 坐标（文献值 Paxinos & Mai 2004）、game_xyz、dk_name=None、category=brainstem、level=0、function_profile
- **预计**：~25 行 JSON

#### Task 1.3 — 删除 2 个功能聚合体
- **产出**：从 `brain_regions.json` 删除 `BasalGangliaIndirectPathway` 和 `AmygdalaHippocampus`
- **处理**：
  - BasalGangliaIndirectPathway → 功能由 Pallidum (GO/NO-GO 输出) + STN (STOP) 承接
  - AmygdalaHippocampus → 功能由 Amygdala (情绪突显) × Hippocampus (记忆巩固) 组合承接
- **预计**：删除 2 条目，functional_id 总数 70→68（+STN = 69）

#### Task 1.4 — 写入首批 20 个功能剖面
- **产出**：`brain_regions.json` 中目标 functional_id 条目增加 `function_profile` 字段
- **涵盖**：§三 3.1-3.20（15 解剖实体 → 20 个 functional_id 剖面 + 2 个 mirror_of 引用）
- **粒度**：functional_id 级写入；LC_R 和 SNc_R 用 `mirror_of` 引用共享
- **格式**：
  ```json
  "function_profile": {
      "primary_function": "...",
      "input_types": ["excitation/motor_command", "gating/go_direct", ...],
      "output_types": ["excitation/motor_command", ...],
      "timescale": "fast|medium|slow",
      "neurotransmitter_dominant": "glutamate|GABA|dopamine|norepinephrine|serotonin",
      "oscillatory_band": "gamma|beta|alpha|theta|delta",
      "cstc_loop": "somatic|cognitive|limbic|none",
      "cstc_role": "cortical_input|striatal_gate|pallidal_output|thalamic_relay|modulator|none",
      "hierarchy_direction": "feedforward|feedback|both",
      "gameplay_domain": "..."
  }
  ```
- **预计**：20 剖面 × ~15 行 JSON 共 ~300 行

#### Task 1.5 — Kroell 14 网络 → JSON
- **产出**：`data/connectivity/kroell14_networks.json`
- **内容**：14 网络名 + 每网络的脑区列表（用 dk_name）+ 网络间关系（重叠/拮抗）
- **来源**：迁移 `tools/build_link_legitimacy_matrix.py` L242-316 硬编码数据 + `data/connectivity/kroell14_networks.md`
- **预计**：~200 行 JSON

#### Task 1.6 — 术语注册表入库
- **产出**：`data/term_registry.json` 新增术语
- **候选**：CSTC / EDR (指数距离衰减) / CTC (Coherence through Communication) / 三体神经模型 / 功能剖面 / function_profile / gameplay_domain / STN / 脑干广播 / 皮层-皮层连接 / signal_type / cstc_loop / cstc_role / Tripartite
- **预计**：~150 行 JSON

### Phase 2: 脚本层（tools/）

#### Task 2.1 — 写 `build_tripartite_model.py`
- **产出**：新脚本，替代 `build_link_legitimacy_matrix.py`
- **功能**：
  1. 读取 `brain_regions.json`（含 function_profile）+ `signal_types.json`
  2. 生成 CSTC 环路：按 `cstc_loop` 分组 → 每环路内按 `cstc_role` 匹配 4 站 → 每连接标注 `pathway`（GO=直接/NO-GO=间接/STOP=超直接）
  3. 生成皮层-皮层连接：EDR (p ≥ 0.10) + |Δlevel| ≤ 1 + 双向互惠 + 排除 d=0
  4. 生成脑干广播：LC→{category=cortical}+{level=1}; 中缝→{category=cortical}; VTA/SNc→{dk_name IN ["Putamen","Caudate","Accumbens-area","rostralmiddlefrontal","superiorfrontal","medialorbitofrontal","frontalpole","caudalmiddlefrontal","lateralorbitofrontal","parsopercularis"]}
  5. 输出 `data/connectivity/tripartite_model.json`（3 段：cstc / corticocortical / brainstem）
- **代码规则（v2 修订版）**：
  - R1: CSTC 闭合—cortex→striatum→pallidum→thalamus→cortex。cortical_input 与 striatal_gate 按 `cstc_loop` 同组配对（躯体/认知/边缘各自独立）。`cstc_role=pallidal_output` 和 `cstc_role=thalamic_relay` 的节点 `cstc_loop=none`——作为通配，匹配所有环路的 striatal_gate→pallidal 和 pallidal→thalamic 连接。thalamic_relay→cortical_input 的闭合连接按 `cstc_loop` 回传同环路皮层
  - R4: 皮层-皮层 EDR 天花板：p ≥ 0.10，λ=0.015, c=0.85（Molnár et al. 2024）
  - R5: 皮层-皮层仅连接 |Δlevel| ≤ 1 的相邻层级
  - R6: 皮层-皮层双向互惠（Markov et al. 2013）
  - R7: 脑干广播 3 系统投放射程——DK_TARGETS 为硬编码 dk_name 列表（10 项：Putamen/Caudate/Accumbens-area + 7 prefrontal）。脚本启动时自检：硬编码 dk_name 若不在brain_regions.json 中 → WARN（不中断——部分缺失仍可生成剩余广播），便于新增/重命名 dk_name 时发现遗漏
  - R8: STN→Pallidum 超直接 STOP — 全局急停，不按环路分组
  - R9: 无 dk_name 的条目不参与皮层-皮层连接（脑干核团）
  - R10: dk_name 为图节点，functional_id 为通信模式标签。同一 dk_name 下多个 functional_id → 该图节点的 input_types/output_types/gameplay_domain 取所有 profile 的并集，各自保留独立语义（不做合并消歧）。并集后的 gameplay_domain 可为多值列表（如 Caudate 节点同时标记 [cognitive_control, habit_learning]），function_label 交集计算时分别匹配
- **预计**：~400 行 Python

#### Task 2.2 — 写 `build_function_labels.py`
- **产出**：新脚本，从 function_profile 组合推导连接功能
- **功能**：
  1. 读取 `tripartite_model.json` 中的连接
  2. 对每条连接 source→target：取 source.function_profile.output_types ∩ target.function_profile.input_types（使用 signal_types.json 受控词表做精确匹配）
  3. 交集项 → `function_label`（如 "V1→Fusiform: 传递 sensory_feature 供形状识别"）
  4. 派生 gameplay 标签：source.gameplay_domain + target.gameplay_domain → 连接级 gameplay 域列表
  5. 交集为空 → 标记 `role: "silent"`（连接存在但无功能语义，不进入游戏系统）
  6. 输出连接级 `function_label` 和 `gameplay_labels` 追加回 tripartite_model.json
- **预计**：~250 行 Python

#### Task 2.3 — 旧脚本迁移至垃圾桶
- **产出**：9 个文件移动到 `垃圾桶/`
- **清单**：同原计划 §四 删除/迁移文件
- **预计**：`git mv` 9 个文件

### Phase 3: 文档层（docs/）

#### Task 3.1 — 更新 `脑功能层级模型.md`
- **产出**：新增 §二十（三体神经模型），§十五 四规则标注废弃
- **内容**：同原计划 + signal_type 词表引用 + cstc_loop 字段说明 + EDR 筛选层说明（天花板+功能标签+gameplay 三层渐降）
- **预计**：~250 行

#### Task 3.2 — 更新决策树和六维状态
- 同原计划

#### Task 3.3 — 一致性清扫
- **grep 关键词**：`364链路` `pairwise` `link_legitimacy` `legitimacy_matrix` `link_registry` `Kroell` `ENIGMA` `ENIGMA_SUBCORTICAL_MAP` `_BRAINSTEM_TARGET_LEVEL` `四规则` `is_design_node`
- 同原计划

### Phase 4: 验证

#### Task 4.1 — 运行三体模型生成
- `python3 tools/build_tripartite_model.py` → 无报错
- 输出 `data/connectivity/tripartite_model.json` 包含 3 段

#### Task 4.2 — 运行功能标签生成
- `python3 tools/build_function_labels.py` → 无报错
- 每条连接均有 `function_label` + `gameplay_labels`

#### Task 4.3 — 交叉引用校验
- `grep` 所有活跃文档中不应出现已删除文件路径
- `brain_regions.json` functional_id 总数 69（68 + STN）

---

## 五、文件清单

### 新建文件
| 文件 | 类型 | Phase |
|------|------|-------|
| `data/signal_types.json` | 数据 | 1 |
| `data/connectivity/kroell14_networks.json` | 数据 | 1 |
| `tools/build_tripartite_model.py` | 脚本 | 2 |
| `tools/build_function_labels.py` | 脚本 | 2 |
| `data/connectivity/tripartite_model.json` | 生成物 | 4 |

### 修改文件
| 文件 | 修改内容 | Phase |
|------|---------|-------|
| `data/brain_regions.json` | +STN, +20 function_profile, +2 mirror_of, -2 聚合体 | 1 |
| `data/term_registry.json` | +~14 术语 | 1 |
| `规则/技能树系统/脑功能层级模型.md` | +§二十 三体模型, §十五 标废弃 | 3 |
| `docs/决策树.md` | +Grilling #26 记录 | 3 |
| `docs/设计框架-六维状态.md` | 规则+管线维度更新 | 3 |

### 删除/迁移文件（→ 垃圾桶/）
| 文件 | 替代 |
|------|------|
| `tools/build_link_legitimacy_matrix.py` | build_tripartite_model.py |
| `tools/build_link_registry.py` | 三体模型内置 ID |
| `tools/rebuild_link_registry.py` | 同上 |
| `tools/classify_link_roles.py` | build_function_labels.py |
| `tools/build_link_contexts.py` | function_profile 派生 |
| `tools/validate_link_data.py` | 新校验脚本 |
| `tools/gen_skill_reference.py` | 不再适用 |
| `data/connectivity/link_legitimacy_matrix.json` | tripartite_model.json |
| `data/connectivity/link_behavior_roles.json` | tripartite_model.json 内置 role |

---

## 六、验收标准

1. **词表完整**：signal_types.json 有 4 大类 × 19 子类，全部有 definition
2. **STN 就位**：SubthalamicNucleus 有 MNI 坐标 + function_profile
3. **剖面覆盖**：20 个 functional_id（+2 mirror_of）= 覆盖全部首批 15 解剖实体
4. **cstc_loop 完整**：所有 basal_ganglia 和 cortical input 剖面有 cstc_loop 值，能正确分组
5. **三体模型输出**：tripartite_model.json 包含 cstc（按 cstc_loop 分组的环路连接）、corticocortical（EDR p≥0.10 + 层级 + 双向）、brainstem（3 系统广播）三段
6. **功能标签输出**：每条连接有 function_label，交集为空的有 role:silent 标记
7. **旧文件隔离**：9 个废弃文件在垃圾桶中，活跃文档无引用
8. **一致性**：grep 关键词无活跃引用残留
9. **脚本可运行**：两个新脚本 python3 调用无异常

---

## 七、依赖与阻塞

- **依赖 Grilling #25**（解剖基座重构）：50 实体 + L0-L5 层级架构已就位 ✅
- **依赖 Grilling #22**（月光场数值校准）：η 空间参数已锚定 ✅
- **阻塞**：无。三体模型实现后，下游可进行——NPC AI 预烘焙管线更新、技能树 3D 可视化更新、战斗结算链路引用更新

---

*创建: 2026-08-07 | 更新: 2026-08-07 (v2: review-plan 追加 4 决策 + signal_type 词表 + 剖面粒度调整 + cstc_loop 字段)*
*关联: Grilling #26 (GitHub #27), [脑功能层级模型.md](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md), [决策树.md](../../../docs/%E5%86%B3%E7%AD%96%E6%A0%91.md), [signal_types.json](../../../data/signal_types.json)*
