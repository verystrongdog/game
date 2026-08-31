# term_registry 候补候选清单

> 本文件是 `data/term_registry.json` `_pending_candidates` 字段指向的候补清单——已出现但未达入库标准（P3 级/单文档/待裁决）的术语登记处。达标准则后由对应 grilling 逐批移入主表。

## 待裁决/推迟项（Grilling #111 登记，2026-09-03）

以下术语在 Grilling #111（项目总体插件化）讨论中出现，**未采纳或未定案**，登记为候选/推迟态：

| 术语 | 状态 | 说明 |
|------|------|------|
| `降级协议` | ⚠️ 否决（非项目能力） | 通用运行时降级协议 **不采纳**（#111 Q2 定案：否决 Ready/Degraded/Unavailable 三态作为通用模块协议）。**「有这个术语」≠「项目采用这个机制」**。若未来具体数据产品出现局部降级/状态语义，需独立裁决后另行入库 |
| `单一事实源` | ⏸️ 推迟（未裁决） | #111 方向 1（知识新鲜度治本 = 单一事实源 + 生成视图 + 历史/现状分层）**本轮不裁决、不实施、不宣称完成**。涉及：CalibrationConfig.cs 手写常量、term_registry numerical_locations、生成视图、#35 触发点 1 治本方案。后续独立议题裁决 |
| 语义层兜底（非结构化知识防过时） | ⏸️ 推迟 | #111 issue 问题 8，纳入方向 1 后续议题；现状维持引用即读取 + 一致性清扫 |
| #70 路线图模块化重构 | ⏸️ 推迟 | #111 issue 问题 7：P0-P6 批次不因 #111 重构；模块化按「新子系统建 Module、既有 seam 纯审查」渐进融入 |

## 既有 P3 级候补（#111 之前已登记）

> 约 20 条 P3 级 + 单文档术语（历史登记），逐批入库。已完成入库批次：Grilling #26-27（CSTC/EDR/CTC/三体神经模型/function_profile/cstc_loop/cstc_role/signal_type/gameplay_domain/STN/脑干广播/皮层-皮层连接/功能剖面/基底节门控，14 条）。

---
*创建: 2026-09-03 | 更新: 2026-09-03*
*关联: [data/term_registry.json](term_registry.json), [docs/决策树.md](../docs/决策树.md) Grilling #111*
