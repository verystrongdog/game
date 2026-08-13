# 复核签字: SpeedScoreCalculator + TurnOrderBuilder spec

> 复核日期: 2026-08-13 | 复核人: （待签） | 已读范围: （全表 Trace Table / 仅结论——待声明） | spec版本: v1.1（含 L1 修正）

## 审计报告关键发现

**全量审计 v1.0**（12 agent：3 专家 → 去重 → 9 条 error/warning 对抗验证）：0 ❌ / 7 ⚠️ CONFIRMED / 2 REFUTED / 15 info。

**Δ审计 v1.1**（2 专家只重审变更章节 + 半径扩张）：0 ❌ / 0 ⚠️ / 3 info（全部 L1 免重审修正）→ 等效通过。

7 个 ⚠️ 概要：W1 执行分值域引用指针错误（数值正确）；W2 AC-14 隐含前提未声明；W3 gurney.Somatic 长度防御缺失；W4 ComputeScore null 防御缺失；W5 AC-1 漂移哨兵覆盖边界未声明；W6 3/4 回落常量未被单独钉住；W7 FromCalibration 无 AC 覆盖。

## 逐项处置

| # | 发现 | 处置 | 理由 |
|----|------|------|------|
| W1 | §二 2.1 引用指针错误 | 修正spec（v1.1 F1：引用→运行时状态模型 §三「SD1 [0,2]」+ 可达性论证 u_SD1 = c(1+DA) 无条件非负） | 验证者独立复算确认 [−0.1,1.5] 是正确硬值域；仅指针瑕疵 |
| W2 | AC-14 隐含前提 | 修正spec（v1.1 F2：完整输入组合 a(Precentral)=1.0 ∧ Somatic[0]=2.0 ∧ 未防御 + 合成状态说明） | AC 必须可直接可测 |
| W3 | gurney 长度防御 | 修正spec（v1.1 F3：Somatic.Length ≠ 5 → ArgumentException，镜像 CstcGating 先例；AC-12 补） | 未契约化的 IndexOutOfRangeException 不可接受 |
| W4 | ComputeScore null 防御 | 修正spec（v1.1 F4：ArgumentNullException；AC-12 补） | 契约防御完整性 |
| W5 | AC-1 哨兵边界 | 修正spec（v1.1 F5：三面哨兵边界声明——名删除→KeyNotFound、值漂移→AC-3/AC-8、行序重排→契约中性） | 行序重排在全消费者按名解析的 canonical 契约下确实中性；诚实声明覆盖边界优于硬编码行号（后者与 wmatrix 结转 #1「不裸写下标」矛盾） |
| W6 | 回落常量未钉住 | 修正spec（v1.1 F6：3 个新逐节点锚点 0.68274397/0.68290060/0.68319666，Δ审计独立 f32 复算逐位核对通过） | 4 常量逐节点单独可证伪 |
| W7 | FromCalibration 无覆盖 | 修正spec（v1.1 F7：新增 AC-15） | 静态工厂是公开契约面 |
| R1 | AC-1 无观测面 | 接受 refutation（不处置） | 验证者实读反驳：发现误引 spec 原文；AC-3/AC-5 行为锚点构成观测面（独立复算：行解析对调 → 0.6827439 ≠ 0.6937933 必被捕获） |
| R2 | 硬值域应为 [−0.85,1.5] | 接受 refutation（不处置；残留指针瑕疵并入 W1） | 验证者双重证伪：运行时状态模型 §三 :71 确有 SD1 [0,2] 解析界；a_SD1 无条件 ∈ [0,2] |
| I1-I12 | 12 条 info（混合形态/措辞/值域语境等） | 修正spec/设计文档（v1.1 L1 批 + 设计文档写回 cb68803/5387d98） | 见 report.md Trace Table 处置建议列 |
| I13-I15 | 3 条 info（B 落点核查/RED 覆盖/实测表引用复算） | 免处置（核查通过） | 正向核查项 |
| I-Δ1~3 | Δ审计 3 info（0.565 措辞/可达上界半开/B3 标注） | 修正spec（v1.1 L1 修正，免重审） | 措辞级，断言本身经复算成立 |

## ⚠️ 结转清单（需在工作issue实现时验证）

| # | 结转项 | 目标 work issue |
|----|--------|----------------|
| 1 | 锚点测试统一走行序解析（fid 名 → RowOf），不裸写下标——dk/fid 命名陷阱（wmatrix 结转 #1 传统；本 feature 5 个解析名：Pericalcarine/TransverseTemporal/Insula/AnteriorCingulateCortex/Precentral） | 工作issue 01 |
| 2 | gurney.Somatic 长度防御实现时对照 CstcGating 的防御写法（异常类型一致） | 工作issue 01 |
| 3 | AC-10 镜像 Fisher-Yates 必须独立实现（不得复制引擎代码）——镜像即证伪器 | 工作issue 01 |
| 4 | RNG 消费序契约：实现侧不得改动 §三 3.2 写死的 Fisher-Yates 方向与 NextInt 参数（m=1 不消费 rng） | 工作issue 01 |
| 5 | AC-2 断言不变式 = 「计算结果与 0.565f 字面量逐位相等」（十进制 0.565 非 f32 精确可表示） | 工作issue 01 |
| 6 | 4 察觉静息常量实现时附数据漂移注释（来源 = csharp-tone M1 实测值表；AC-3 锚点即哨兵） | 工作issue 01 |

## 结论

- [ ] **批准** —— spec v1.1（含 L1 修正）可以进入实现阶段（工作issue 01）
- [ ] 退回 —— 需要修改后重新审计

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [report.md](report.md), [spec.md](../spec.md)*
