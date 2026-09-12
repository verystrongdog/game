# Grilling #75 P2 情境系统进引擎 — 实施任务计划（Grilling #108 执行契约版）

> Grilling #75 (GitHub #75) 结论：情境系统进引擎——α_patterns 数据化 + 27 原型选择器 + s_env/m_field 三通道 + 情境只读状态接口。4 项共识：design/events/持续场分离 / 映射表+SAN 调制+节点注入 / 三通道并入 s 数组 / 隐式涌现+只读接口。
> **Grilling #108（2026-09-02 实施前审查）**：在 #75/#104 锁定决策约束下，将 15 个实施层开放点（Q1-Q15）定案为**执行契约**——开发者拿到本文档后无需再问设计问题即可实施 #105。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [数据文件](#三数据文件)
4. [情境选择器](#四情境选择器)
5. [三通道输入落点](#五三通道输入落点)
6. [情境只读状态接口](#六情境只读状态接口)
7. [任务分解](#七任务分解)
8. [文件清单](#八文件清单)
9. [数据契约与校验](#九数据契约与校验)
10. [验收标准](#十验收标准)
11. [推迟清单](#十一推迟清单)

---

## 一、背景与动机

#69 确立 s(t) 三通道语义（s_事件/s_env/m_field）与 D9（α pattern 数据化），但实施未落地：EventProcessor 仍硬编码 6 元素 α pattern（`EventProcessor.cs:123` `new[] {1,0,1,0,0,0}`）；situation_primitives.json（27 原型）已加载但 demo 未消费（引擎数据关系规格 §六 接缝 🔶）；W_sensory 仍 69×6。P2 落地情境系统，为 P3 NPC 全量提供情境输入。

## 二、决策清单

### 顶层设计决策（#75，2026-08-16，已锁定）

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | design/events/持续场分离：`alpha_patterns.json` 只放 14 战斗事件（#69 schema 原样，8 模态）；`env_tones.json` 独立放环境基调 α_env（空间类型 → 8 模态强度） | 数据 |
| D2 | 情境选择器 = 空间→原型映射表（`typical_game_scenario` 辅助建表）+ 低 SAN 概率偏移（恐慌→诡异/负面原型）+ **key_brain_regions 直接节点注入**（心理情境非感官，不走 W_sensory）+ 刷新时机 = 空间切换 + SAN 阈值跨越（C1） | 算法 |
| D3 | 三通道并入 s 数组：`s_total[69] = s_事件 + s_env + m_field`——`WcDynamics.Step` 签名零改动；正典文档层写 `h = ΣW·a + b + s_total` | 落点 |
| D4 | 情境 salience = 隐式涌现（原型注入 → a(t) → salience 自然反映，不查表）+ **只读情境状态接口**（当前原型 id + 强度，供 P3/UI/叙事） | 接口 |

### 实施决策（#104，2026-09-02，已锁定）

| 编号 | 决策 |
|------|------|
| Q1 | m_field 实现深度：结构实现 + PLACEHOLDER 分级 + 门禁（非占位全 0） |
| Q2 | 排期：独立实施 issue #105、串行惯例、无冲突协调机制 |
| Q3 | 开启时机：待 #91 关闭后实施（已解除，2026-08-30） |
| Q4 | 实施边界：moonlight_landing.json + moonState(D) 契约骨架 + PLACEHOLDER 消费路径 + 正式消费门禁 + 显式 demo 例外；不含 #35 数值生产与 #71 artifact 校验 |
| Q6 | env_tones demo 3 环境（病房/走廊/护士站，示例集非上限）；key_brain_regions fid 直用 + 27 原型全量校验器（不建 dk→fid 映射表） |

### 执行契约（Grilling #108，2026-09-02，Q1-Q15 定案）

| # | 定案（一句契约） |
|---|-----------------|
| Q1 | `alpha_patterns.json` 建立 `row_id → pattern[8]` 契约；行 id ↔ 派生分支绑定留代码（Emit 持有 A1/A2/A4/A5/B1/B2/B4/C1/D1/D2）；`m_alpha` 二态（有限数字 [0,1] ∪ `"m_delta"`）；消费行缺失 / pattern 长度≠8 / 类型非法 / 数值越界 / 非 `"m_delta"` 字符串 → 加载期抛 `JsonException`；14 行完整保留、引擎仅映射消费 10 行（A3/A6/A7 保留不消费）；字段缺失 ≠ 占位 |
| Q2 | W_sensory 扩列锚点：嗅觉 = {LateralOrbitofrontal, Amygdala}、热觉 = {Postcentral, Insula}；允许节点模态数 > 2（Postcentral 成 3 模态）；原 6 列逐位不变；元字段同步 |
| Q3 | `env_tones.json` 环境键 = 英文 slug id + `display_name` 中文；demo = ward/corridor/nurse_station；`alpha_env` 恰好 8 值 ∈ [0,1]，违规 fail-fast；运行时缺失环境键 → 抛异常；`CombatState.CurrentEnvironment` = string；Console `--env <id>` 注入 |
| Q4 | 情境 = 战斗/遭遇级**全局单一**（SituationState 单一挂 CombatState）；s_env（含原型注入）空间级、所有参与者同值注入；SAN 调制 = **存在性条件**（任意参与者 SAN<30%，含敌方）；刷新路径 = 空间切换 ∪ 任意 C1 |
| Q5 | env_map 折叠进 `env_tones.json`（每环境键含 `situation.primary` 引用原型 `name`）；**删除 alternates 字段**（未定义语义，不建第二套候选池）；加新环境 = 加一个键，零 schema 变更 |
| Q6 | 诡异/负面组 G = {原型：`negative_valence ≥ t_neg(=0.2)` 且 `valence = negative`}，构造期计算（当前 17 成员）；t_neg 是规则参数非硬编码名单；G 与 primary **不互斥**；p_panic=0.5 语义：恐慌真 → P(G 均匀随机)=0.5 / P(primary)=0.5，假 → 确定性 primary；组内均匀随机，注入 RNG |
| Q7 | 强度双档阶梯：恐慌假 → `strength = 1.0`；恐慌真 → `strength = s_neg ∈ [1,1.5]`（数值 [NEW] 归 #35）；只作用于原型 fid 注入、**不缩放 α_env**（正交）；重选时定值、情境内恒定 |
| Q8 | C1 重选 = 事件流驱动（TurnManager 事件窗口检测 `StatusChangeEvent(Panic, Entered=true)` → `Select(env, panic, rng)`）；**下一回合 Phase 1 生效**（本回合按旧情境结算）；恐慌消退（Entered=false）不重选；初始情境在 `CombatState.Create` 确定；SituationSelector 无状态纯函数 |
| Q9 | `moonlight_landing.json` 参数形式 schema：顶层 `schema`/`version`/`calibration_status`/`calibration_version` + `semantics[]`（id/primary[4]/secondary[8]/r/alpha_s）；r/α_s = 字符串 `"PLACEHOLDER"`（r=PLACEHOLDER → 按 r=1 均匀）；**字段缺失 ≠ PLACEHOLDER（load error）**；四项校验引擎加载期 fail-fast（supp 互斥 / 公式重算 Σv=1 / **fid→dk 映射后 ⊆ 48 W_active 端点** / 非负 + r>0） |
| Q10 | `MoonState` 静态纯函数 + `Query(int day)` → `MoonStateResult(Phase=λ(D), Shell={E_c(λ),E_th(λ)}, QhatBaseline[69], CalibrationStatus, Version)`；E_c/E_th 按 #102 E2 形式结构实现（常量挂 CalibrationConfig 为 PLACEHOLDER）；**N=69 为占位契约**（graph identity 闭合后升级）；D 推进与 MOON_PHASE_CHANGED 广播**不实现**（demo 固定 D） |
| Q11 | `CalibrationGate.EnsureCalibrated(status, version)` 挂载于 **m_field 合成注入点**（PLACEHOLDER/version 不匹配 → fail-fast，接 #106 分层）；**s_env / α_env / 情境原型注入不挂门禁**（三通道正交）；demo 例外 = `CalibrationConfig.AllowPlaceholderDemo`（默认 false）+ Console `--mfield-demo` + 每回合醒目警告；三数据文件 schema major 加载期统一校验；MoonState.Query 运行时自检（0≤λ≤1/E_c>0/0<E_th<E_c/有限） |
| Q12 | 三通道 **Phase 1 注入点合成**：`s_total_i = SPending_i + s_env + m_field_i`；SPending 保持事件累加语义不变；`s_env[69]` 存 CombatState（情境刷新重算，Q8 下一回合生效）；`m_field_i[j] = QhatBaseline[j] × g(SAN_i) × R[j]`，**g ≡ 1.0 占位**（E7/#35 定正式形式）、q̂ 无空间差异（延迟）；WcDynamics.Step 签名零改动 |
| Q13 | fid 一致性校验器**两层防线**：① `code/tools/validate_situation_fids.py` 管线侧（名称 ∈ region_name_map.regions 且 name == functional_id；37 去重名 100% 命中报告；失败 exit 非零；新增原型自动纳入；不建 dk→fid 映射表）② SituationSelector 构造时引擎侧全量断言 fid ∈ 已知集（未知 → 加载期异常）；不要求 ⊆ W_sensory/W_active（情境 fid 与 moonlight 落点校验分离） |
| Q14 | Console 新增 `--demo-situation` 非交互 trace 模式（`--env`/`--day`/`--rounds`/`--seed`/`--mfield-demo`）；输出：初始环境/情境/strength + 每回合 λ(D) + WC a(t) 摘要 + 首回合 s_env 注入前后对比 + mfield-demo 时 PLACEHOLDER 警告；`CombatState.Create(environment)` 默认 ward，非法 id → CliUsageException → exit 1；不污染 RunBattle；同 seed 同输出 |
| Q15 | 测试矩阵 G1-G9（引擎 C# 复用 BadJson 模式 / Console 进程级复用 InvalidArgs_Exit1 / fid 校验器管线侧 python + 引擎断言）；现有 309 测试全绿 = P2 回归门槛；**p_panic 用契约断言**（恐慌假 → 必 primary；恐慌真 → 必 ∈ {G ∪ primary}；同 seed 同选择），不做频率统计（无样本量正典） |

## 三、数据文件

### 3.1 `data/connectivity/alpha_patterns.json`（新建，#69 D9 落地 + Q1 契约）

```json
{
  "schema": "alpha_patterns", "version": 1,
  "modalities": ["visual","auditory","somatosensory","pain","social_cognition","language_cognition","olfactory","thermoreception"],
  "events": {
    "A1": {"trigger": "物理攻击命中", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A2": {"trigger": "被格挡/闪避", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A3": {"trigger": "物理暴击", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A4": {"trigger": "精神攻击执行", "pattern": [0,0,0,0,1,1,0,0], "m_alpha": 1.0},
    "A5": {"trigger": "防御成功", "pattern": [0,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "A6": {"trigger": "技能使用成功", "pattern": [0,0,0,0,0,0,0,0], "m_alpha": 0.0},
    "A7": {"trigger": "逃跑", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": 1.0},
    "B1": {"trigger": "被物理击中", "pattern": [1,0,1,1,0,0,0,0], "m_alpha": "m_delta"},
    "B2": {"trigger": "闪避/格挡", "pattern": [1,0,1,0,0,0,0,0], "m_alpha": "m_delta"},
    "B3": {"trigger": "被暴击", "pattern": [1,0,1,1,0,0,0,0], "m_alpha": "m_delta"},
    "B4": {"trigger": "被精神攻击", "pattern": [0,0,0,1,1,1,0,0], "m_alpha": "m_delta"},
    "C1": {"trigger": "SAN<30%", "pattern": [0,0,0,1,0,0,0,0], "m_alpha": 1.0},
    "D1": {"trigger": "队友倒下", "pattern": [1,1,0,0,1,0,0,0], "m_alpha": 1.0},
    "D2": {"trigger": "敌人倒下", "pattern": [1,1,0,0,1,0,0,0], "m_alpha": 1.0}
  }
}
```

- pattern 前 6 位 = 现有硬编码值原样迁移；末 2 位（嗅觉/热觉）战斗事件补 0
- **Q1 契约**：`m_alpha ∈ {有限数字 [0,1]} ∪ {"m_delta"}`——数字 = 常量（A 类 = 1.0），`"m_delta"` = 用该分支现有算法计算 m（B/C/D 类，`"m"` 旧写法已废弃，统一 `"m_delta"`，#69 为权威 schema）
- **行 id ↔ 派生分支绑定留代码**（EventProcessor Emit 调用点持有 A1/A2/A4/A5/B1/B2/B4/C1/D1/D2），JSON 只做 `row_id → pattern[8]`，不描述触发分支
- **14 行完整保留**（数据层完整性）；引擎仅映射消费 **10 行**；A3/A6/A7 保留但不消费（偏差 B1 不落地；未来落地 = 映射表 + 派生分支双改）
- **加载期 fail-fast（抛 `JsonException`，接 #106 分层 → Console exit 1）**：消费行缺失 / pattern 长度 ≠ 8 / m_alpha 类型非法 / 数值越界 / 非 `"m_delta"` 字符串。**数据表不是可选配置；一旦进入引擎加载路径就必须满足 schema**——不静默补零/截断/自动修复

### 3.2 `data/connectivity/env_tones.json`（新建，环境基调 + env_map 折叠 + Q3/Q5 契约）

```json
{
  "schema": "env_tones", "version": 1,
  "modalities": ["visual","auditory","somatosensory","pain","social_cognition","language_cognition","olfactory","thermoreception"],
  "environments": {
    "ward": {
      "display_name": "病房",
      "alpha_env": [0.3, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2],
      "situation": {"primary": "<情境原型 name，如 social_confrontation>"}
    },
    "corridor": {
      "display_name": "走廊",
      "alpha_env": [0.4, 0.3, 0.1, 0.0, 0.1, 0.0, 0.2, 0.1],
      "situation": {"primary": "<情境原型 name>"}
    },
    "nurse_station": {
      "display_name": "护士站",
      "alpha_env": [0.6, 0.4, 0.1, 0.0, 0.3, 0.2, 0.3, 0.2],
      "situation": {"primary": "<情境原型 name>"}
    }
  }
}
```

- **Q3 契约**：环境键 = **英文 slug id** + `display_name` 中文显示名（数据键承担机器接口、显示名承担人类可读语义——同 Q1 原则）；demo 固定 ward/corridor/nurse_station，**示例集非固定上限**（#104 Q6），扩展 = 加键零 schema 变更
- **Q5 契约**：**env_map 折叠进本文件**——`situation.primary` 引用已有情境原型的 `name`（不复制情境内容）；**无 alternates 字段**（已删除——无锁定消费者语义，恐慌偏移统一走全局 G 组，不建环境本地候选池）
- **fail-fast**：`alpha_env` 必须恰好 8 值且 ∈ [0,1]（长度/范围违规 → 加载期抛异常）；运行时请求不存在的环境 id → 抛异常（禁止回退零向量）；schema major 不匹配 → fail-fast
- `typical_game_scenario`（27 段自由叙事文本）与 environment id **不建立自动耦合**；primary 映射由人工依叙事建表
- 初始表值 = 示例值 [NEW]（demo 用）；完整环境表值归空间内容填充（#75 推迟清单原样）

### 3.3 W_sensory 扩列 69×8（T1 + Q2 契约）

`W_sensory.json` 追加 olfactory/thermoreception 两列（#69 D4' 已定；原 6 列数据逐位不变）——**Q2 锚点 fid 集（实测均在 69 canonical 内）**：

| 新模态 | 锚点 fid | 依据 |
|--------|---------|------|
| olfactory（嗅觉） | `LateralOrbitofrontal`, `Amygdala` | #69 解剖锚「梨状皮层/OFC」——梨状皮层不在 69 fid 集，映射到 OFC 主投射（LateralOrbitofrontal）+ 气味-情绪联结（Amygdala）；二者现均 0 模态，无干扰 |
| thermoreception（热觉） | `Postcentral`, `Insula` | #69 解剖锚「躯体感觉皮层温度区」= Postcentral（S1）+ Insula（内感受温度） |

- **允许节点模态数 > 2**：Postcentral 由 somatosensory+pain 变 3 模态（体感+痛+温，生理成立）——W_sensory ∈ {0,1}^(69×8) 无模态数上限，「12+ 双模态」是现状描述非约束
- 原 6 列逐位不变（迁移防错位断言）；`modality_nodes` / `cortical_nodes_with_sensory_input` / `cortical_nodes_without_sensory_input` / `metadata` 元字段同步更新（引擎不读，数据完整性）
- `EventProcessor.Emit` 的 `k < 6` 硬编码随 Q1 改 pattern 长度驱动（`for k < pattern.Length`）；`WsensoryMatrix.cs` 动态读列零改动

### 3.4 `data/connectivity/moonlight_landing.json`（新建，#101 R 落点数据 + Q9 契约）

```json
{
  "schema": "moonlight_landing", "version": 1,
  "calibration_status": "PLACEHOLDER",
  "calibration_version": 0,
  "semantics": [
    {
      "id": "s_core",
      "primary": ["Amygdala","HippocampusCA1","HippocampusCA3","Parahippocampal"],
      "secondary": ["AnteriorCingulateCortex","RostralAnteriorCingulateCortex","AnteriorCingulateCortexDorsal","Insula","LateralOrbitofrontal","PosteriorCingulate","IsthmusCingulate","TemporalPole"],
      "r": "PLACEHOLDER",
      "alpha_s": "PLACEHOLDER"
    }
  ]
}
```

- **Q9 契约**：参数形式 schema——引擎按 #101 Q4 公式由 r + 主辅分组计算 `v_s^norm`（`r/(4r+8)` 主 / `1/(4r+8)` 辅；r=PLACEHOLDER → 按 r=1 均匀分配 12 落点）；**预计算 v^norm 数组不作第二数据源**（防双源漂移，r 是 #35 唯一校准杠杆）
- **字段缺失 ≠ PLACEHOLDER**：字段存在 + `"PLACEHOLDER"` = 合法未校准态；字段缺失 = schema/load error（延续 #106 禁止静默回退）
- **四项校验（引擎加载期 fail-fast）**：① supp 互斥（语义间 fid 不重叠，当前 1 语义恒真，防未来扩展）② 归一化（按公式重算 Σv^norm = 1）③ supp ⊆ W_active——**先 fid→dk 映射**再验证 ∈ 48 dk 级端点集（三体模型 1049 边去重端点；实测 12/12 命中；HippocampusCA1/CA3 同 dk `Hippocampus`、ACC 双 fid 同 dk `caudalanteriorcingulate`）④ 非负 + r > 0
- **文件存在 ≠ 已校准**（#104 Q1）；正式 r/α_s 数值 → #35

## 四、情境选择器

```
SituationSelector.Select(environment, panic, rng) → (archetypeId, strength)   // 无状态纯函数（Q8）
```

1. **候选池（Q5）**：`env_tones.json` 的 `situation.primary`（原型 name 引用）——正常情境的确定性选择
2. **SAN 调制（Q4/Q6）**：`panic` = **存在性布尔**（任意参与者 SAN < 30%，含敌方）；恐慌为真时：
   - `P(选择 G 中均匀随机一个) = p_panic = 0.5`
   - `P(选择 situation.primary) = 1 − p_panic = 0.5`
   - 恐慌为假 → 确定性选择 primary
3. **诡异/负面组 G（Q6，构造期计算，不复制进 env_tones）**：
   ```
   G = {原型 : rdoc_profile.negative_valence ≥ t_neg(=0.2) ∧ appraisal_profile.valence = negative}
   ```
   - 当前 27 原型实测 **G = 17 成员**（social_confrontation…witnessing_trauma）；t_neg=0.2 是规则参数 [NEW]，内容填充可调阈值/加排除规则精化，不改 selector 架构
   - **G 与 primary 不互斥**（primary ∈ G 合法，两概率路径可同结果，不加去重/排除逻辑）
   - 校验器断言 G 非空（G ⊆ 27 由构造恒真）；组内均匀随机，注入 RNG（同 seed 同选择，#75 D9）
4. **强度（Q7）**：`strength = 1.0`（panic 假）| `s_neg ∈ [1,1.5]`（panic 真，具体数值 [NEW] 归 #35）——**只作用于原型 fid 节点注入**，与 α_env 正交（不缩放 α_env）；重选时定值、情境生命周期内恒定
5. **刷新时机（Q8）**：
   - 触发：空间切换（战斗外，上层驱动；P2 demo = 创建时指定）∪ **任意参与者 C1 事件**（`StatusChangeEvent(Panic, Entered=true)`，TurnManager 事件窗口检测 → 调用 Select）
   - **生效时点 = 下一回合 Phase 1**（本回合按旧情境完成结算；不窗口内中途换情境）
   - **恐慌消退（Entered=false）不触发重选**（C1 只有进入行；情境保持至下一次空间切换或下一次 C1）
   - 初始情境在 `CombatState.Create` 确定（environment.primary + 初始存在性恐慌判定）

**神经落点（直接节点注入，Q4）**：

```
选中原型 → s_env_j += strength × 1[j ∈ 原型 key_brain_regions（fid 直用，无翻译）]
s_env_j = (W_sensory × α_env)_j + Σ_原型注入          // 全局同值（空间级），Q4
```

- **fid 一致性校验（Q13 两层防线）**：① `code/tools/validate_situation_fids.py`（断言名称 ∈ `region_name_map.regions` 且 `name == functional_id`；37 去重名 100% 命中为验收门槛；失败 exit 非零；未来新增原型自动防回归；**不建立 dk→fid 翻译映射表**——翻译需求 = 0）② SituationSelector 构造时引擎侧全量断言 fid ∈ 已知集（未知 → 加载期异常，禁止静默零注入）
- 情境 fid **不要求 ⊆ W_sensory/W_active**（心理情境非感官；该约束只属于 moonlight_landing，不混用）

## 五、三通道输入落点

```
s_total[69] = s_事件（EventProcessor，读 alpha_patterns.json）
            + s_env（环境基调: W_sensory × α_env + 情境原型节点注入，空间级稳定）
            + m_field（月光场: 结构实现 + PLACEHOLDER 分级 + 门禁，Grilling #104 Q1/Q4）

h_j = Σ W·a + b_j + s_total_j        （文档层公式；引擎 WcDynamics.Step 签名不变）
```

### 合成时序（Q12：Phase 1 注入点合成）

```
Phase 4:  EventProcessor → SPending[69]（事件累加，现有机制语义不变）
          s_env[69] ← CombatState 稳定态（情境刷新时重算）
Phase 1:  MoonState.Query(D) → q̂；SAN_i → g(SAN_i)；R（moonlight_landing v^norm）→ m_field_i
          s_total_i = SPending_i + s_env + m_field_i
          → WcDynamics.Step(a, b, s_total_i, w)
```

- **SPending 保持事件累加**（现有 accumulate-then-inject-then-clear 语义零改动）；`s_env[69]` 存 CombatState（Q8 重选后**下一回合 Phase 1 生效**）；`m_field` 每回合每参与者重算（依赖当前 SAN）
- **g ≡ 1.0 占位**（`CalibrationConfig.MFieldGain` [NEW]；E7/#35 定正式形式，不改三通道架构）；**q̂ = `MoonState.Query(D).QhatBaseline`**，无空间差异 q̂_{x_i}（延迟）
- **WcDynamics.Step 签名零改动**——唯一核心引擎改动 = Phase 1 注入前三通道合成

### m_field 通道（Q9-Q11）

> ⚠️ **已更新（2026-09-02 #101/#103 + Grilling #104 + Grilling #108 Q9-Q12）**：原「m_field 占位全 0，MFieldStrength=0 [NEW]」已废弃——#101 闭合 R 落点结构、#103 定 moonState(D)/calibration_status 分级、#108 锁 schema/骨架/门禁/合成时序。

```
m_field_vec⁽ⁱ⁾(t) = q̂_{x_i(t)}(t) · g(SAN_i, state_i) · R_i
R_i = Σ_s α_s · v_s^norm   （12 落点 = L1∪L2∩W活跃；主辅两档 r=m/a 参数化；非负/稀疏）
```

1. **数据层**：`moonlight_landing.json`（Q9 schema，见 §3.4）——12 落点 fid + 主辅两档 + r/α_s 显式 PLACEHOLDER；四项校验引擎加载期 fail-fast
2. **引擎层**：`MoonState.Query(int day)` 契约骨架（Q10）——λ(D)=(1−cos(2πD/29.5))/2 解析 + calibration_status/version 读取 + E_c/E_th 结构实现 + QhatBaseline[69] 占位
3. **门禁层**（Q11）：`CalibrationGate.EnsureCalibrated(status, version)` 挂 **m_field 合成注入点**；PLACEHOLDER/版本不匹配 → fail-fast（Data/Engine 层抛 → Console 转 stderr + exit 1，接 #106 分层）；**s_env / α_env / 情境原型注入不挂门禁**（不消费 moonlight calibration，三通道正交）
4. **demo 例外**（Q11/Q14）：`CalibrationConfig.AllowPlaceholderDemo`（默认 false）+ Console `--mfield-demo` 显式开启 → 占位 m_field 注入 + 每回合醒目警告「PLACEHOLDER 数据，仅原型测试」；默认（无 flag）战斗以 `s_total = s_事件 + s_env` 正常运行，m_field 消费 fail-fast
5. **边界**：正式 q̂/E_c/E_th 数值生产 → #35；#103 artifact 6 项硬校验（validate_calibration.py）→ #71；**R 落点校验（P2）≠ artifact 硬校验（#71）**

## 六、情境只读状态接口

```csharp
// Entity/CombatState.cs
public SituationState Situation { get; }   // 只读——当前情境原型 id + 强度 + 环境 id（全局单一，Q4）
public sealed record SituationState(string ArchetypeId, float Strength, string EnvironmentId);
```

- 消费方：P3 NPC 行为偏置参考（非 salience 乘子）、UI 情境标签、叙事、玩家观察
- 战斗内刷新：空间切换（战斗外）+ C1 事件（战斗内重选，**下一回合生效**，Q8）
- 引擎加载期对 key_brain_regions 全量 fid 断言（Q13 第二层防线）在 SituationSelector 构造时执行

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | W_sensory.json 扩列 69×8（嗅觉 {LateralOrbitofrontal,Amygdala} / 热觉 {Postcentral,Insula}，原 6 列不变，Q2）+ 元字段同步 | 数据 | `W_sensory.json` | D1 |
| T2 | alpha_patterns.json（14 事件 8 模态，m_alpha 二态 `"m_delta"`，Q1）+ EventProcessor 去硬编码（读 JSON，绑定留代码，加载期 fail-fast JsonException） | 数据+代码 | `alpha_patterns.json` + `EventProcessor.cs` | T1 |
| T3 | env_tones.json（ward/corridor/nurse_station + display_name + situation.primary，无 alternates，Q3/Q5） | 数据 | `env_tones.json` | D1 |
| T4 | **fid 一致性校验器两层防线**（Q13）：`code/tools/validate_situation_fids.py`（37 名 100% 命中/失败非零退出/新原型自动纳入）+ SituationSelector 引擎侧加载断言 | 代码 | 校验脚本 + 验证报告 + 引擎断言 | T3 |
| T5 | SituationSelector（Select 纯函数：env_map=env_tones.primary + G 构造期计算(Q6) + p_panic 概率 + 强度双档(Q7)）+ `CurrentEnvironment` 传入 CombatState | 代码 | `Engine/SituationSelector.cs` + `CombatState.Situation` + `CombatState.Create(environment)` | T4 |
| T6 | 三通道合成（Q12）+ m_field 通道（moonlight_landing.json(Q9) + MoonState.cs(Q10) + CalibrationGate(Q11)）+ 只读 SituationState | 代码 | `MoonState.cs` + `CalibrationGate.cs` + `CombatState` 扩展 + `CalibrationConfig`（AllowPlaceholderDemo/MFieldGain/SituationPanicShift/s_neg [NEW]） | T2/T5 |
| T7 | Console `--demo-situation` 模式（Q14）+ 测试矩阵 G1-G9（Q15）+ 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T5/T6 |

## 八、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/connectivity/W_sensory.json` | 改写（+2 模态列，Q2 锚点） | 数据 |
| `data/connectivity/alpha_patterns.json` | 新建（Q1 契约） | 数据 |
| `data/connectivity/env_tones.json` | 新建（Q3/Q5 契约） | 数据 |
| `data/connectivity/moonlight_landing.json` | **新建（Q9 schema，r/α_s PLACEHOLDER）** | 数据 |
| `code/src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` | 改写（读 JSON 去硬编码，Q1 fail-fast） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/SituationSelector.cs` | 新建（Q4-Q8） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/MoonState.cs` | **新建（Q10 契约骨架）** | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/CalibrationGate.cs` | **新建（Q11 门禁）** | 代码 |
| `code/src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（Situation + s_env[69] 存储 + Create(environment)） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+AllowPlaceholderDemo/MFieldGain/SituationPanicShift/s_neg/t_neg [NEW]） | 代码 |
| `code/tools/validate_situation_fids.py` | **新建（Q13 管线校验器）** | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增（G1-G9 矩阵，Q15） | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写（`--demo-situation` + `--mfield-demo` + `--env`，Q14） | 代码 |
| `design/decisions/` / `design/framework/six-dimensions.md` / `design/README.md` / memory | 追加（Grilling #108） | 文档 |

## 九、数据契约与校验

### 不变量

- `alpha_patterns.json` pattern 前 6 位 = 现有硬编码逐位一致（迁移防错位）；14 行完整、消费 10 行（Q1）
- `W_sensory` 69×8 行序 = canonical 69（C1 约束延续）；原 6 列数据逐位不变（Q2）
- `env_tones.json` 模态列表与 alpha_patterns 一致（8 模态）；环境键 = 英文 slug + display_name；无 alternates（Q3/Q5）
- `moonlight_landing.json`：12 落点 + 主辅两档 + r/α_s PLACEHOLDER；字段缺失 ≠ 占位（Q9）
- 情境注入：s_total ∈ 合理范围（W·a+b+s 输入范围由 sigmoid 自然饱和）
- 确定性：SituationSelector 用注入 RNG，同种子同选择（#75 D9 / Q6）
- 三通道正交：s_env 不挂 CalibrationGate、与 m_field 无交互项（Q11 / #101 Q3）

### 校验（含 Q15 测试矩阵 G1-G9）

| 组 | 校验 | 形态 |
|----|------|------|
| G1 | 数据契约 fail-fast：alpha_patterns（14 行/长度 8/二态 m_alpha/消费行缺失→JsonException/畸形）；env_tones（3 键/schema major/α_env 长度与范围/缺失→抛）；moonlight_landing（12 落点/四项校验/r>0/PLACEHOLDER/缺失≠占位） | C#（复用 `Loader_BadJsonThrowsJsonException` 模式） |
| G2 | 迁移回归：W_sensory 原 6 列逐位不变（数据断言）；**现有 309 测试全绿 = P2 回归门槛** | C# + python |
| G3 | EventProcessor：现有派生测试 JSON 驱动后逐位一致转绿 + A1 行消费正例 | C# |
| G4 | SituationSelector：env→primary；非恐慌→primary 确定性；恐慌→G（**固定 seed 快照断言**，含 primary∈G 重合路径）；G=17 构造断言；C1 重选→下一回合生效 | C# |
| G5 | MoonState：λ(D) 表值（D=0→0 / D=14.75→1 连续 / D=15 离散近满月）；纯函数同入同出；运行时断言（0≤λ≤1/E_c>0/0<E_th<E_c/有限） | C# |
| G6 | 门禁：EnsureCalibrated(PLACEHOLDER)→抛 / CALIBRATED→过 / version 不匹配→抛 / AllowPlaceholderDemo→放行+警告 | C# |
| G7 | 三通道合成：s_total=SPending+s_env+m_field；s_env 重选后更新（下一回合生效）；m_field 随 SAN 每回合变；Step 签名不变（既有测试证明） | C# |
| G8 | fid 校验器：37 名 100% 命中 / 失败非零退出 / 新增原型自动纳入 | python（管线侧）+ C#（引擎加载断言） |
| G9 | Console：--demo-situation 输出集（初始情境/λ(D)/a(t) 摘要/注入对比）；--mfield-demo 警告；非法 env→exit 1；同 seed 快照同输出 | 进程级（复用 `InvalidArgs_Exit1` 模式，锁 stderr） |

**p_panic 测试契约（Q15）**：恐慌假 → 必选 primary；恐慌真 → 必 ∈ {G ∪ primary}；同 seed + 同输入 → 同选择。**不做频率统计断言**（p_panic=0.5 是行为契约；无预注册样本量，不制造「跑 n 次接近 50%」的验收）。

### 管线侧校验

| 校验 | 命令 |
|------|------|
| α pattern 迁移比对 | 迁移前后 6 位逐位比对（脚本） |
| W_sensory 形状 | 69×8 断言（validate 工具扩展） |
| **fid 一致性校验（Q13）** | `code/tools/validate_situation_fids.py`：27 原型 key_brain_regions 名称 ∈ region_name_map.regions 且 name == functional_id（100% 命中，失败不静默降级） |
| **R 落点校验（Q9）** | 引擎加载期四项校验：supp 互斥/归一化/supp⊆W_active（fid→dk）/非负+r>0——归 P2；#103 artifact 6 项硬校验归 #71，**不混淆** |
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests`（309 + G1-G9 全绿） |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十、验收标准

- [ ] W_sensory 69×8（原 6 列逐位不变；嗅觉 {LateralOrbitofrontal,Amygdala} / 热觉 {Postcentral,Insula}，Q2）
- [ ] alpha_patterns.json 14 事件（前 6 位与现有一致；m_alpha 二态 `"m_delta"`，Q1）；EventProcessor 无硬编码 α pattern，全部读 JSON；消费行缺失/畸形 → JsonException fail-fast
- [ ] env_tones.json（ward/corridor/nurse_station + display_name + situation.primary，无 alternates，Q3/Q5）；SituationSelector 空间映射 + SAN 调制 + 刷新生效（全局单一，Q4；下一回合生效，Q8）
- [ ] **fid 一致性校验器两层防线（Q13）**：27 原型全量通过（名称 ∈ region_name_map.regions 且 name == functional_id）；无 dk→fid 映射表；引擎侧加载断言
- [ ] moonlight_landing.json（Q9）：12 落点 + 主辅两档 + 四项校验通过；r/α_s 显式 PLACEHOLDER；字段缺失 ≠ 占位
- [ ] moonState(D) 契约骨架（Q10）：λ(D) 解析 + calibration_status/version 读取 + E_c/E_th 结构实现 + QhatBaseline[69]；PLACEHOLDER 门禁 fail-fast（Q11）
- [ ] s_total = s_事件 + s_env + m_field（Phase 1 注入点合成，Q12）；SituationState 只读接口可用；Step 签名不变
- [ ] Console `--demo-situation`（Q14）：指定环境 → 情境显示 + λ(D) + a(t) 注入前后对比；`--mfield-demo` 显式 PLACEHOLDER 标记；非法 env → exit 1
- [ ] 测试 G1-G9 全绿 + 现有 309 回归全绿（Q15）；决策树 #108 / 六维状态 / 项目总览 / memory 落位

## 十一、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| ~~m_field 参数集与节点落点~~ | ~~#38 开放中~~ | ✅ **已解除（2026-09-02 #101 闭合 + #104 Q1 + #108 Q9-Q12）**——结构/PLACEHOLDER/schema/骨架/门禁/时序全部定案；正式数值归 #35 |
| env_tones 全环境表值 + situation.primary 全表 | 空间内容未全设计 | 空间 grilling/内容填充（demo 3 环境为示例集；primary 依 typical_game_scenario 人工建表） |
| G 组精化（调 t_neg / 加排除规则） | 内容填充期需求 | 内容填充（t_neg=0.2 为规则参数；不新建字段/不改 selector 架构） |
| s_neg 具体数值（∈[1,1.5]）+ g(SAN) 正式形式 + r/α_s + q̂/E_c/E_th 数值 | 无正典值 | #35 数值校准（E7 定 g 形式；#35 只改 CalibrationConfig 值，不动架构） |
| q̂ 空间差异 q̂_{x_i} | 空间落点未闭合 | graph/spatial 校准（延迟实现） |
| D 推进机制 + MOON_PHASE_CHANGED 广播 | 游戏循环层，无 P2 消费者 | 游戏循环实施（#103 Q1/Q5 契约已定） |
| 白天无月光渗透过渡态 | 空间遭遇规则延迟项 | 独立话题 |
| #103 calibration artifact 6 项硬校验（validate_calibration.py） | #103 推迟清单 | #71 数值平衡工具或独立（**非 P2 范围**，Q4 边界写死） |

---

*创建: 2026-08-16 | 更新: 2026-09-02 (Grilling #104：m_field 段落对齐 #101/#103——结构实现+PLACEHOLDER+门禁；T4 改 fid 一致性校验器；env_tones demo 3 环境集锁定；推迟清单 m_field 项解除) | 更新: 2026-09-02 (Grilling #108 实施前审查：Q1-Q15 执行契约注入——m_alpha 二态/m_delta、W_sensory 锚点、env_tones slug+primary 删 alternates、全局情境+G 组+p_panic+强度双档+C1 下一回合、moonlight_landing schema+MoonState+门禁+注入点合成、fid 校验两层防线、--demo-situation、G1-G9 矩阵)*
*关联: [Grilling #69 task-plan](../grilling-69-external-stimulus/task-plan.md), [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [Grilling #104 实施 issue](https://github.com/verystrongdog/game/issues/105), [Grilling #108 实施前审查 issue](https://github.com/verystrongdog/game/issues/108), [运行时状态模型](../../../rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [situation_primitives.json](../../../../data/connectivity/situation_primitives.json), [核心机制](../../../rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
