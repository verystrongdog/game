# map: csharp-wmatrix

> csharp-engine step 3（plan §十一）——WMatrixBuilder：69×69 皮层-皮层连接权重 + τ[69]。Status: spec v1.0 已写（2026-08-13），待 workflow 审计

## Notes

- 依赖 csharp-engine plan v1.1 §4.1（6 条）+ csharp-engine-types 交付的 WMatrix 契约（W/Tau/RowFids）
- 结转 #5（csharp-engine-types sign-off）：`W.RowFids == RegionIds` 行序对齐断言在本 feature 落地 → spec AC-2
- **数据实测已完成**（任务issue「数据实测」表）：48 参与 fids / 735 幸存边 / 1389 非零元 / 无孤立节点 / 唯一无对向边 pericalcarine→Amygdala / mirror 2 fids；归一化后 W 一般不对称（行和不同）
- **spec v1.0 已写**（`40fd511` 后）：6 步构建算法 + 13 条 AC + 偏差声明 B1-B4（固化任务issue D1-D8，含 D8 方向契约：行=接收者）
- **设计文档冲突待规格澄清**（任务issue D1/B1）：皮层动力学-通用层 §5.1「仅 cortical」vs 运行时状态模型 §4.2 排除清单——spec 按后者写；文档修正延后至审计后

## Decisions-so-far

- [任务issue 01](design/issues/01-wmatrix-spec.md) → 7 决策（D1-D7）+ 2 追问 → claimed（2026-08-13）

## Fog

- D1 文档修正待 spec 审计后执行（皮层动力学-通用层 §5.1 措辞，L1 级）
- 审计未做（spec v1.0 已写毕）
