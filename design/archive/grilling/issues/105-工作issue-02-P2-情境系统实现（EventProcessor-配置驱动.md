# #105 工作issue 02: P2 情境系统实现（EventProcessor 配置驱动 + 27 原型选择器 + 三通道 + m_field 落点）

> 状态：关闭 · 创建 2026-08-30 · 关闭 2026-08-30
> 标签：维度:管线, implementation
> 原始：https://github.com/verystrongdog/game/issues/105

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 状态：排队中

> ⚠️ **排队**：按项目 implementation 串行惯例（grilling #104 Q3），本 issue 现在创建登记，**待 #91（csharp-console 实现）关闭后开始实施**。开始前基于当时最新 HEAD 增量（#104 Q2 A'）。

## 来源

Grilling [#104](https://github.com/verystrongdog/game/issues/104)（P2 情境系统实施）+ #75 方案（2026-08-16）+ #101 R 落点（2026-09-02）+ #103 接口层契约。阻塞解除：m_field_vec[69] 占位全 0 → #101 闭合。

## 决策摘要（Q1-Q4+Q6 已锁定）

| # | 决策 | 内容 |
|---|------|------|
| Q1 | m_field 实现深度 | **结构实现 + PLACEHOLDER 分级 + 门禁**（非占位全 0） |
| Q2 | 排期 | 独立 issue、进入队列、遵循串行惯例、最新 HEAD 增量、无冲突协调机制 |
| Q3 | 开启时机 | 现在创建，待 #91 关闭后实施 |
| Q4 | 实施边界 | 含 moonlight_landing.json + moonState(D) 契约骨架 + m_field PLACEHOLDER 消费路径 + 正式消费门禁 + 显式 demo 例外；**不含** #35 数值生产与 #71 artifact 校验 |
| Q6 | env_tones + key_brain_regions | demo = 病房/走廊/护士站 3 环境示例集（可扩展，非上限）；key_brain_regions **fid 直用** + 27 原型全量校验器（无 dk→fid 映射表） |

## 实施范围

1. **数据**：
   - `W_sensory.json` 扩列 69×8（嗅觉/热觉，原 6 列不变）
   - `alpha_patterns.json`（14 战斗事件 8 模态，#69 D9；前 6 位与现有硬编码逐位一致）
   - `env_tones.json`（**demo 3 环境：病房/走廊/护士站**——示例集非固定上限，扩展走空间内容填充，#75 推迟清单原样）
   - `moonlight_landing.json`（**新建**：12 落点 R = S_core = L1∪L2∩W活跃，主辅两档 r=m/a 参数化，r/α_s 显式 PLACEHOLDER，四项校验 supp 互斥/归一化/supp⊆W_active/非负——#101 Q2/Q8；**文件存在 ≠ 已校准**）
2. **代码**：
   - EventProcessor.cs 去硬编码（读 alpha_patterns.json）
   - SituationSelector.cs（空间→原型映射 + SAN 恐慌偏移 p_panic=0.5 + key_brain_regions **fid 直用直接节点注入** + 刷新时机=空间切换+C1）
   - `moonState(D)` 契约骨架（λ(D)=(1−cos(2πD/29.5))/2 解析函数 + calibration_status/version 消费——#103 Q4/Q5/Q6）
   - m_field 合成（q̂×g×R → s_total 加法，三通道 s_total = s_事件+s_env+m_field）
   - CombatState.Situation 只读接口；CalibrationConfig 新增常量（SituationPanicShift/MFieldStrength 等 [NEW]）
3. **校验器（T4 任务性质变更）**：27 原型 key_brain_regions **fid 一致性校验器**（断言：名称 ∈ `region_name_map.regions` 且 `name == functional_id`；27 原型全量、100% 命中为验收门槛；未来新增原型自动防回归；映射失败 → **校验失败，不静默降级**）。**不建立 dk→fid 翻译映射表**（当前 37 个去重名已 100% 是 fid，翻译需求 = 0）
4. **门禁**：PLACEHOLDER 下正式情境基线/SAN×月光消费 fail-fast（#103 Q6）；demo 走显式标记的原型测试路径
5. **测试+Console**：SituationSelector/moonState/m_field 合成/门禁/校验器测试；Console demo 接线（指定环境→情境显示+s 注入后 a(t) 变化可见，显式 PLACEHOLDER 标记）

## 边界（不包含）

- 正式 q̂/E_c/E_th 数值生产 → #35
- #103 calibration artifact 6 项硬校验（validate_calibration.py）→ #71
- env_tones 全环境表值 → 空间内容填充；情境强度系数 → #35；白天月光渗透 → 独立话题
- **R 落点校验（#101，P2 负责）≠ artifact 6 项硬校验（#103，归 #71）**——两类校验边界写死，防范围混淆

## 验收标准

- [ ] W_sensory 69×8（原 6 列逐位不变）；alpha_patterns 14 事件前 6 位与现有一致
- [ ] EventProcessor 无硬编码 α pattern，全部读 JSON
- [ ] env_tones schema + 病房/走廊/护士站 3 demo 环境；SituationSelector 空间映射 + SAN 调制 + 刷新生效
- [ ] **fid 一致性校验器**：27 原型全量通过（名称 ∈ region_name_map.regions 且 name == functional_id）；无映射表
- [ ] moonlight_landing.json：12 落点 + 主辅两档 + 四项校验（supp 互斥/归一化/supp⊆W_active/非负）通过；r/α_s 显式 PLACEHOLDER
- [ ] moonState(D) 契约骨架：λ(D) 解析 + calibration_status/version 消费 + PLACEHOLDER 门禁 fail-fast
- [ ] s_total = s_事件 + s_env + m_field；SituationState 只读接口可用
- [ ] Console demo 指定环境 → 情境显示 + s 注入后 a(t) 变化可见（显式 PLACEHOLDER 标记）
- [ ] 测试绿；决策树 #104 / 六维状态 / memory 落位

---

## 评论（1 条）

### verystrongdog · 2026-08-30

## ✅ 实施完成（2026-09-03）— 验收 8 项全过

### 验收标准逐项核验

- [x] **W_sensory 69×8**：原 6 列逐位不变（git 历史比对 True）；嗅觉 {LateralOrbitofrontal, Amygdala} / 热觉 {Postcentral, Insula}（Q2 锚点实测 4/4）
- [x] **alpha_patterns 14 事件**：前 6 位与现有硬编码 ALL MATCH（10 消费行脚本断言）；m_alpha 二态 `"m_delta"`；EventProcessor 无硬编码全读 JSON；消费行缺失/畸形 → JsonException fail-fast（G1 测试 5 类）
- [x] **env_tones 3 demo 环境**：ward/corridor/nurse_station + display_name + situation.primary（无 alternates）；SituationSelector 空间映射 + SAN 调制（存在性恐慌）+ 刷新生效（C1 事件流 → 下一回合 Phase 1，G4 测试锁定）
- [x] **fid 一致性校验器两层防线**：`tools/validate_situation_fids.py` 37/37 命中（名称 ∈ region_name_map.regions 且 name==functional_id，无 dk→fid 映射表）+ SituationSelector 构造断言（未知 fid → InvalidDataException）
- [x] **moonlight_landing.json**：12 落点（primary 4 + secondary 8）+ 四项校验（supp 互斥/归一化/supp⊆W_active fid→dk/非负+r>0）通过；r/α_s 显式 PLACEHOLDER；字段缺失 ≠ 占位（G1 测试）
- [x] **moonState(D) 契约骨架**：λ(D)=(1−cos(2πD/29.5))/2 解析 + calibration_status/version 消费 + E_c/E_th 线性端点族占位 + QhatBaseline[69]；PLACEHOLDER 门禁 fail-fast（G5/G6 测试）
- [x] **s_total = s_事件 + s_env + m_field**：Phase 1 注入点合成（Q12）；SituationState 只读接口可用；WcDynamics.Step 签名零改动（G7 测试）
- [x] **Console --demo-situation**：指定环境 → 情境显示 + λ(D) + a(t) 注入前后对比；--mfield-demo PLACEHOLDER 警告；非法 env → CliUsageException exit 1；同 seed 同输出（G9 进程级测试）

### 测试与校验

- **346/346 全绿**（309 回归 + 37 新增 G1-G9）
- fid 校验器 37/37；cross_refs 701 有效
- 机械实现 6 项详见 `.scratch/grilling-105-p2-impl/实现说明.md`

### 延迟（非缺口）

#35 正式数值 / #71 artifact 6 项硬校验 / env_tones 全环境表值 + G 组精化（空间内容填充）/ q̂ 空间差异 / D 推进 + MOON_PHASE_CHANGED 广播 / #107 fail-fast（串行队列）

### 实施轨迹

Grilling #109（实施执行层）→ T1-T7 七批 6 commit（b7153eb → 21cc39c，feat/p2-situation 分支，待合回 main）

---
*导出: 2026-09-12 | 来源: GitHub issue*
