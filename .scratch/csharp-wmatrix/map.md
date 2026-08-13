# map: csharp-wmatrix

> csharp-engine step 3（plan §十一）——WMatrixBuilder：69×69 皮层-皮层连接权重 + τ[69]。Status: closed（2026-08-13）——工作issue 01 resolved，AC-1~12 全 ✅，62/62 测试全绿

## Notes

- 依赖 csharp-engine plan v1.1 §4.1（6 条）+ csharp-engine-types 交付的 WMatrix 契约（W/Tau/RowFids）
- 结转 #5（csharp-engine-types sign-off）：`W.RowFids == RegionIds` 行序对齐断言在本 feature 落地 → spec AC-2 ✅
- **数据实测已完成**（任务issue「数据实测」表）：48 参与 fids / 735 幸存边 / 1389 非零元 / 无孤立节点 / 唯一无对向边 pericalcarine→Amygdala / mirror 2 fids；归一化后 W 一般不对称（行和不同）
- **spec v1.0 已写**（`c861eb7`）：6 步构建算法 + 12 条 AC + 偏差声明 B1-B4（固化任务issue D1-D8，含 D8 方向契约：行=接收者）
- **v1.0 全量审计（3 专家）退回**：3 ❌（AC-11 计数 82 错、AC-8 τ 分布口径矛盾、B2 数字误挂并集口径）+ 4 ⚠️ + 6 info；公式与 B3 方向契约全过。report.md 已写
- **spec v1.1 已修正并提交**（`5924f11`）：AC-11 82→50、AC-8 改继承后 27/30/12、B2 改 Cerebellum-Cortex 幸存口径 CC 6+PP 12、AC-7 锚点 dk 名标识+绝对容差、Step 4.3 歧义名理由、B1 修正清单 5 处、段号 §4.3、哨兵统一标注
- **设计文档冲突待规格澄清**（任务issue D1/B1）：皮层动力学-通用层 §5.1「仅 cortical」vs 运行时状态模型 §4.2 排除清单——spec 按后者写；5 处文档修正延后至审计后
- **实现闭合**（`e27292e`）：WMatrixBuilder 6 步算法 + 12 测试，62/62 全绿。结转 #1（AC-7 Step 4.3 解析规则）实测拦截一次测试侧错误（dk 名 'transversetemporal' vs fid 'TransverseTemporal'）——正是它要防的错。builder 零 spec 偏差

## Decisions-so-far

- [任务issue 01](design/issues/01-wmatrix-spec.md) → 8 决策（D1-D8）+ 2 追问 → claimed（2026-08-13）
- v1.0 全量审计（3 专家）→ 退回修改（3 ❌ / 4 ⚠️ / 6 info）→ [report.md](design/audit/report.md)
- spec v1.1 修正 → Δ审计（2 专家）conditional 通过 + L1 修正 → [sign-off.md](design/audit/sign-off.md) 获批（2026-08-13）
- [工作issue 01](impl/issues/01-wmatrix-implementation.md) → 实现 + 证据式自审 → resolved（2026-08-13，GitHub #51）

## Fog

- ~~结转 #3：5 处设计文档修正~~ ✅ 已执行（2026-08-13）：皮层动力学 §5.1/§5.3 + 运行时状态模型 §4.1/§4.5/参数速查表全部修正，footer 日期更新，spec 变更日志 v1.1 🔧² 记录
- step 4 csharp-wc-dynamics（WcDynamics 消费本 feature 的 W/Tau/行序）——**下一步**
