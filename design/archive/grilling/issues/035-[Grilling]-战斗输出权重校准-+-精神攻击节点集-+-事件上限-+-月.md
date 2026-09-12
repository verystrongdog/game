# #35 [Grilling] 战斗输出权重校准 + 精神攻击节点集 + 事件上限 + 月光场校准轨 E1-E7

> 状态：关闭 · 创建 2026-08-09 · 关闭 2026-09-01
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/35

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

校准 Grilling #32 运行时状态模型 §八 的四个未赋值权重参数 + 定义精神攻击 base damage 节点集 + 确认一回合事件数量上限。

**Scope 扩展（2026-08-29 Grilling #100 裁决：并入）**：月光场 CGL+AGC 数值校准实验轨 E1-E7（#38 Q7 / 时空结构数学框架 §11.6 定义）并入本 issue。E1 壳态保持性（P0 先行）协议已由 Grilling #100 完整锁定（见 #100 评论与决策树），E2-E7 按序执行。

## 六维定位

- **维度**: 规则（战斗结算数值——删除所有角色和地点后仍然成立）+ 管线（月光场模拟验证）
- **依赖**: Grilling #32 运行时状态模型 ✅ / #34 NPC Affordance Competition ✅ / #26 三体神经模型 ✅ / Grilling #38 月光场接口形态 ✅（§11.6 实验轨）/ Grilling #100 E1 协议 ✅
- **阻塞**: 战斗模拟可运行性（#24 代码就绪度——因缺少实现反馈而暂停）

## 当前状态

运行时状态模型 §八定义了四个输出映射公式但权重均未赋值：

| 输出 | 公式 | 权重 | 状态 |
|------|------|------|------|
| 察觉分 | mean(a of L3 sensory nodes) × w_perception | ❌ 未赋值 |
| 执行分 | a(Precentral) × w_execution | ❌ 未赋值 |
| 精神攻击基础伤害 | mean(a of cognitive nodes) × scale_mental | ❌ 未赋值 |
| 记忆检索成功率 | σ(mean(a of MTL nodes) − θ_mem) | ❌ 未赋值 |

附加：
- 精神攻击 base damage 节点集（当前仅标记 "cognitive only"）
- 一回合事件数量上限（δ_event 冲击叠加饱和约束）
- **月光场校准轨 E1-E7**（#38 Q7）：E1 壳态保持性（P0，协议见 #100）→ E2 月相调制标定 → E3 局部注入响应 → E4 群体事件驱动 → E6 q^base(λ) 标定 → E5 边权敏感性 → E7 g(SAN,state) 机制层实验

---

## 评论（2 条）

### verystrongdog · 2026-08-29

## E1 结果同步（2026-08-29 Grilling #100 闭合）

月光场校准轨 E1（壳态保持性）已按 #100 协议实现跑通：**PASS**——B 族+A1 壳态保持成立（占位参数域内，G_test=P₄，E_c=1/E_th=0.5/ε=0.1/d_max=1）。关键数值：吸引性 t*=0.085-0.102τ；ε_num=1.1e-7；ρ_RK4(状态)=15.852；求解器一致 1.3e-7。Phase 3 诊断全正常（regime 探针/双模态/敏感性）。

**E2 可开题**（月相调制标定：扫描 f_c(λ;θ_c)/f_th(λ;θ_th)）。本 issue scope = 战斗输出权重校准 + 月光场校准轨 E1-E7，继续。

### verystrongdog · 2026-09-01

## 🎯 Grilling #35 闭合总结（2026-09-03）

### 决策表

| # | 决策 | 结论 |
|---|------|------|
| Q0 | 范围形态 | A：战斗域校准决策组；E3-E7 独立 issue；三结果制（定值/暂定值/继续阻塞） |
| Q1 | T0 战斗长度 | 诊断指标，无 PASS/FAIL；历史区间=历史目标非规范；目标重建后续 |
| Q2 | 精神攻击双轨 | 完成迁移 a(t) 派生轨；§4.3 旧公式=迁移前实现；受控暂态 |
| Q2a | 节点集+scale_mental | S_mental 7 fid（cognitive∩W活跃）；motivation 乘子删除；scale_mental≈3 暂定；PENDING |
| Q3 | θ_mem | S_mem 4 fid（MTL）；0.5 暂定（SDT 判据 c）；PENDING |
| Q4 | 事件上限 | 不设 N_max；不变量+防御断言 >64 |
| B1 | 暴击四参 | θ_crit=0.82/k_crit=1.0 暂定（静息 a_exec=0.80777 实测错位纠正）；负偏差保留（静息 3.8%） |
| B2 | Δ_skill | 0.1 暂定；#74 D3 权威公式（×mean(m)） |
| B3 | FleeSanRestore | +10 暂定 + 时段级防护 |
| B4 | s_neg | 1.25 暂定（引擎现役，待 #71） |
| B5 | T2 动力学群 | 静息常量=实测定值 / MaxRounds=非校准 / δ_scale=暂定 / M1·感知阈值=无依据占位 |
| B6 | PanicToneShift | NE+0.2/5HT−0.2 暂定；C1=边沿脉冲/稳态偏移分工写死 |
| B7 | 响应窗口阈值 | T_L4=0.70 / T_L5=0.75 暂定；独立不合并；统一语义不统一参数 |
| B8 | 压抑计数 | 继续阻塞转实体域（双门槛原则） |

### 治理发现（6 项）

引用链过时四模式 / 双轨根因→C5 三向一致性活反例 / Δ_skill 快照滞后 / C1·PanicToneShift 设计线交叉 / 双门槛原则 / 校准语义约定

### 受影响文件

`.scratch/grilling-35-calibration/决策记录.md` + `验证表.md`（新建）· `docs/决策树.md`（#35 条目）· `docs/设计框架-六维状态.md`（规则 +1 → 39）· `规则/核心机制.md`（§4.2 暴击/§4.3 迁移）· `基础行动设计.md`（§二/§三/§四）· `运行时状态模型.md`（§4.5 闭合/§5.5 不变量/§8.1 定案）· `回合战斗流程.md`（§8.3）· `NPC AI 行为模型.md`（§9.1）· `敌人与事件.md`（:454）· `技能生成机制.md`（:34/:57 清扫）· `data/term_registry.json`（4 条目）· `CalibrationConfig.cs`（注释）· memory `战斗输出权重校准-grilling-35.md`

### 质量门禁

cross_refs 720/725 过（其余为既有问题）· validate_params 26 过（7 fail 全既有）· term_registry JSON 有效 · 引擎运行值零改动（测试绿）

### 推迟清单

T0 trace 执行 + 战斗长度目标重建 → 独立议题 / 精英·Boss 门禁 → Stat 实例 / 月光场 E3-E7 + r/α_s + E_c/E_th → 独立 issue / 压抑计数 N → 实体域 / 4 静息常量 E-3 迁移 → P0 / 各暂定参数引擎接入 → P 系列 / δ_scale·M1·感知阈值从零校准 + s_neg 验证 → #71 / C5-C7 治理 + 单一事实源 → #111 方向 1

---

**写入验证**：决策记录 + 验证表见 `.scratch/grilling-35-calibration/`（14 项决策逐条 ✅，3 项需人类复查见验证表 §⚠️）。

---
*导出: 2026-09-12 | 来源: GitHub issue*
