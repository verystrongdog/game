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
