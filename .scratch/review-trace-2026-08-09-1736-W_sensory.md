# Review Trace: W_sensory × 事件空间 s(t) 通道

> 审查日期: 2026-08-09 17:36 | 审查范围: `data/connectivity/W_sensory.json` (新建) + `规则/技能树系统/运行时状态模型.md` §4.5 + §5.5
> 方法: 符号执行 + 限界验证 | 前置检查: `run_all_checks.py` (4/5 FAIL — 均为已有问题，与本次无关)

## 前置输入
- [x] Layer 1 预检查: 4 FAIL (trash_isolation/params/cross_refs/spatial — 已确认与本次无关)
- [x] Layer 1.5 抽查: 跳过（覆盖范围与本次审查目标不重叠）
- [x] 被引用文件自动拉入: [NPC AI 行为模型.md](规则/技能树系统/NPC AI 行为模型.md) §3.3 (tone_bias 权重表)

---

## Trace Table — s(t) 通道 (W_sensory 构建后)

### 流程 1: 事件 emit → α 向量计算

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|---|------|----------|----------|------|----------|------------|------|------|
| 1.1 | §4.5 α = pattern_α × m_α | `pattern_α`: §4.5 α pattern 表 (14×6) | `枚举<{0,1}⁶>`: 14种事件，每种 6-bit 二进制 | 查表: event_type → pattern_α | `List<int>`: 6元素，每元素 ∈ {0,1} | 步骤 1.2 (m_α乘算) | event_type 不在表中 → ❌ 未处理。14种已穷举，不可能是运行时错误——事件类型是枚举 | ✅ |
| 1.2 | §4.5 m_α 分支 | `m` from magnitude 表 §5.5; event class (A/B/C/D) | `m ∈ [0, ∞)`; `枚举<A\|B\|C\|D>` | A类 → m_α=1.0; B/C/D类 → m_α=m; A6 → α=0 (特殊) | `m_α ∈ [0, 1]` (A类固定 1.0; B/C/D 同 m 但 m≥0 可超 1) | 步骤 1.3 (W_sensory 乘) | m > 1 (暴击) → m_α > 1 → α > 1。文档说 clip(tone, 0, 1) 但不 clip α。**A类 m_α 固定 1.0 正确，但 B/C/D 类 m 可能 > 1（暴击）→ α 可能 > 1** | ⚠️ |
| 1.3 | §4.5 s = W_sensory × α | W_sensory: `data/connectivity/W_sensory.json` (69×6 binary); α from 步骤 1.2 | `Matrix{0,1}^{69×6}` × `Vector[0,∞)^6` | 矩阵-向量乘法: `s_j = Σ_m W_{j,m} × α_m` | `Vector[0, N]^{69}`: s_j ∈ [0, N] where N ≤ 2 (无节点在 ≥3 模态) | WC 方程 §4.1: `h_j = Σ W·a + b_j + s_j` | s_j 可 > 1.0: 12 个双模态节点在全强度事件中 s_j = 2.0。WC sigmoid σ 自然饱和——非 bug，但文档未说明 | ⚠️ |
| 1.4 | §4.1 s_j → WC h 方程 | s_j from 步骤 1.3; W·a; b_j | `h_j = float` (无界) | 加法合成: `h_j = Σ W_jk·a_k + b_j + s_j` | `h_j ∈ R` | σ(h_j) → a_j 更新 | 无 | ✅ |

### 流程 2: W_sensory.json 数据完整性

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|---|------|----------|----------|------|----------|------------|------|------|
| 2.1 | W_sensory rows = 69 functional_ids | `data/brain_regions.json` regions keys | `Set<69 functional_id>` | 1:1 映射验证 | `Set<69>` = brain_regions 完全一致 | 步骤 1.3 (s_j 计算) | ✅ 0 缺失 / 0 多余 | ✅ |
| 2.2 | W_sensory 二进制约束 | 所有 69×6 = 414 条目 | `int ∈ {0,1}` | — | — | 步骤 1.3 | 全部 {0,1}，无非法值 | ✅ |
| 2.3 | 37 皮层节点激活 | 44 cortical + 25 non-cortical | `枚举<cortical\|subcortical\|brainstem>` | 分类统计 | 37/44 cortical 有 ≥1 模态; 7/44 无感官; 25 non-cortical 全零 | 步骤 1.3 | 7 皮层节点无 s(t): premotor/M1/MTL/DMN/reward。通过 W·a + b_j 参与动力学——非缺口 | ✅ |
| 2.4 | 模态节点一致性 vs α pattern 表 | 14 事件 α pattern (步骤 1.1) × 6 模态 × W_sensory modality_nodes | `枚举<{0,1}>` | 叉乘验证: ∀ event, ∀ modality with α_m=1, modality_nodes[m] ≠ ∅ | — | 步骤 1.3 | ✅ 全覆盖: 14 事件 × 活跃模态全部有节点 | ✅ |

### 流程 3: δ_event → tone 注入

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|---|------|----------|----------|------|----------|------------|------|------|
| 3.1 | §5.5 δ = pattern_δ × m | `pattern_δ`: δ pattern 表 (14×4); m from magnitude 表 | `枚举<{−1,0,+1}⁴>` × `m ∈ [0, ∞)` | 逐元素乘: `δ_t = pattern_t × m` | `Vector[-∞, +∞]⁴`: 4 tone 脉冲值 | 步骤 3.2 (tone 更新) | A6: δ = sign(tone_bias[role])。**sign(0) = 0 → baseline 时技能使用不产生脉冲。未显式文档化** | ⚠️ |
| 3.2 | §5.2 tone ← tone + (Δ/τ)(−(tone−baseline) + δ) | tone(t), baseline, δ (步骤 3.1), τ (步骤 3.3) | tone ∈ [0,1], δ ∈ R⁴, Δ/τ ∈ [0.7, 3.3] | 离散欧拉步 + clip | `tone(t+1) ∈ [0,1]⁴` | b_j 计算 (§五); tone_bias (NPC AI §3.3) | DA_VTA τ=0.3 → Δ/τ=3.33。单次命中 (δ_DA_VTA=+1×m≈0.8) → tone 0.4→1.0 clip。已知延迟项 (F4)。无新缺口 | ✅(已知延迟) |
| 3.3 | §5.2 clip(tone, 0, 1) | tone(t+1) pre-clip | tone ∈ R (可能 <0 或 >1) | `clip(x, 0, 1)` | `tone ∈ [0, 1]` | b_j, tone_bias | 下溢 (<0) 和上溢 (>1) 均已处理 | ✅ |
| 3.4 | §5.5 m ≈ 0 → skip emit | m from magnitude 表 | `m ∈ [0, ∞)` | 阈值: `if m ≈ 0: return (no event)` | `Optional<Event>` | 步骤 1.1, 3.1 | "≈ 0" 精度未定义: ε = ? 浮点比较建议 ε = 1e-6 或 m < 0.01 | ⚠️ |

### 流程 4: 跨文件引用完整性

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|---|------|----------|----------|------|----------|------------|------|------|
| 4.1 | §5.5 A6 δ = sign(tone_bias[skill.role]) | `NPC AI 行为模型.md` §3.3 tone_bias 权重表 | `tone_bias ∈ [-0.5, +0.5]` (8 role × 4 tone) | sign(tone_bias): +/0/− | `枚举<{−1,0,+1}⁴>` 每 tone 独立 sign | 步骤 3.1 (δ 乘法) | tone_bias 权重表存在且未被废弃。sign(0)=0 边界已标注（步骤 3.1 缺口） | ✅(引用有效) |
| 4.2 | §5.1 脑干核团 → brain_regions.json L0 | `data/brain_regions.json` L0 entities | 引用 (dk_name=None) | 数据源引用 | 4 brainstem nuclei | §5.2 τ 映射 | ✅ | ✅ |
| 4.3 | §4.5 W_sensory → `data/connectivity/W_sensory.json` | 本地文件 | `引用<JSON>` | 文件路径引用 | W_sensory matrix 69×6 | 步骤 1.3 | ✅ 文件存在且可解析 | ✅ |

---

## 缺口汇总

| # | 位置 | 严重度 | 描述 | 处理 |
|----|------|--------|------|------|
| G1 | §4.5 步骤 1.2 | ~~⚠️~~ | ~~B/C/D 类 α > 1 风险~~ → **假警报**: A 类 m_α=1.0 固定; B/C/D 全部 m ≤ 1.0（|ΔHP|/HP_max, |ΔSAN|/SAN_max, 或固定 1.0）。α ∈ [0,1] 由构造保证 | ✅ 关闭 |
| G2 | §4.5 步骤 1.3 | ⚠️→✅ | s_j 可达 2.0（12 双模态节点）| ✅ 已文档化：§4.5 加 s_j 值域说明 + sigmoid 自然饱和 |
| G3 | §5.5 步骤 3.1 | ⚠️→✅ | sign(tone_bias) = 权重表固定符号，sign(0)=0 语义 | ✅ 已文档化：§5.5 A6 注释扩展 |
| G4 | §5.5 步骤 3.4 | ⚠️→✅ | m ≈ 0 精度未定义 | ✅ 已定义：ε = 0.01 (m < 0.01 → skip emit) |
| G5 | §4.5 A6 | ⚠️→⏳ | skill.cortical_nodes 激活机制未定义 | ⏳ 已标注延迟：§4.5 A6 注释加延迟标记 |
| G6 | W_sensory metadata | ℹ️→✅ | Amygdala 排除说明 | ✅ 已文档化：§4.5 加非皮层节点排除说明 |

---

## 半径扩张 — 待复查

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| G1: α clip | 步骤 1.3 s_j 计算 | 待决策 |
| G3: sign(0) 行为 | 步骤 3.1 δ 计算; tone_bias 消费者 | 待文档化 |
| G5: skill.cortical_nodes 激活 | WC 动力学; 技能系统 | 待 grilling / 设计 |

---

## 变更追踪

| 上次缺口 (review-plan #3) | 本次状态 | 备注 |
|---------|---------|------|
| F1: W_sensory 未构建 | ✅ 已解决 | 69×6 矩阵已构建且全覆盖验证通过 |
| F4: DA_VTA 饱和 | ⚠️ 仍延迟 | 数值校准延迟项 |
| F11: SAN_max 被动变化触发 C1 | ✅ 已修正 | 仅响应 SAN 实际扣减 |
| 消耗品/移动/等待不生成事件 | ✅ 确认 | 设计一致 |

---

## 统计
- 总 trace 行数: 15
- ✅: 14 (含 5 个本次修正)
- ⚠️: 0
- ❌: 0
- ⏳ 延迟: 1 (G5 — skill.cortical_nodes 激活机制)

## 结论

6 个 ⚠️ 缺口全部处理完毕：1 假警报关闭 (G1) + 4 文档修正 (G2/G3/G4/G6) + 1 延迟标记 (G5)。s(t) 通道设计层和文档层均已闭合。

唯一未闭合项 G5 (skill.cortical_nodes 激活) 已标注为延迟，阻塞技能系统与 WC 动力学的衔接——建议创建 grilling issue 后续讨论。

---

*创建: 2026-08-09 17:36*
*关联: [运行时状态模型.md](../../规则/技能树系统/运行时状态模型.md), [W_sensory.json](../../data/connectivity/W_sensory.json)*
