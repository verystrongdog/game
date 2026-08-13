# map: csharp-wmatrix

> csharp-engine step 3（plan §十一）——WMatrixBuilder：69×69 皮层-皮层连接权重 + τ[69]。Status: 任务issue 已建（2026-08-13），spec 写作中

## Notes

- 依赖 csharp-engine plan v1.1 §4.1（6 条）+ csharp-engine-types 交付的 WMatrix 契约（W/Tau/RowFids）
- 结转 #5（csharp-engine-types sign-off）：`W.RowFids == RegionIds` 行序对齐断言在本 feature 落地
- **数据实测已完成第一轮**（见任务issue「数据实测」表）：48 参与 fids / 735 幸存边 / 1389 非零元 / 无孤立节点 / 唯一无对向边 pericalcarine→Amygdala / mirror 2 fids
- **设计文档冲突待规格澄清**（任务issue D1）：皮层动力学-通用层 §5.1「仅 cortical」vs 运行时状态模型 §4.2 排除清单——按后者写 spec

## Decisions-so-far

- [任务issue 01](design/issues/01-wmatrix-spec.md) → 7 决策（D1-D7）+ 2 追问 → claimed（2026-08-13）

## Fog

- D1 文档修正待 spec 审计后执行（皮层动力学-通用层 §5.1 措辞，L1 级）
- 审计未做、spec 未写
