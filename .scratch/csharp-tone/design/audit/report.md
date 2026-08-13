# 审计报告: csharp-tone spec（ToneUpdater + CorticalBias）

> 审计日期: 2026-08-13 | 审计方法: workflow 多专家 agent（3 专家 + 逐发现对抗验证，9 agents / 0 错误）| spec版本: v1.0

## Trace Table

| # | 专家 | 检查范围 | 判定 | 详情 |
|----|------|---------|------|------|
| 1 | 数学公式与数值锚点 | 解析解公式逐字核对 / k_t 4 值 / AC-2~6 全部样例 / b_j 锚点 / clamp 集合 / M1 重建与迭代 | 1 ⚠️ | F1 引用失实（下）；**公式与全部数值锚点经独立复算通过**（含 1389 非零元重建、round 10 < 1e-5） |
| 2 | 接口契约与架构 | 签名 vs plan §4.3 / 异常契约 AC 化 / 偏差 B1-B4 完整性 / AC 可测性 / 范围边界 / 自检清单 | 2 ⚠️ | F1 契约缺口（下）；F2 clamp 集合语义（对抗验证 refuted） |
| 3 | 数据完整性与交叉引用 | 114 边计数 / role 分布 / Raphe 双源 / 可解析性 / 排除 fid / 零广播清单 / 行序衔接 / C# 字段名 / fid 名大小写 | 3 ⚠️ | F1/F2 fid 命名错误 + F3 引用失真（下）；计数与结构全部复算通过 |

## 缺口汇总（经对抗验证后的真实发现）

| # | 严重度 | 类别 | 位置 | 摘要 |
|----|--------|------|------|------|
| F1-math | ⚠️ | 引用失实 | spec §四 4.1 DeltaSeconds 备注 | 「回合时长默认 1.0 秒（运行时状态模型 §4.3）」段引用错误——§4.3 是「连接权重 W」；权威出处是皮层动力学-通用层 §4.3「Δ = 回合时长（默认 1.0 秒）」（wc-dynamics spec §四 已正确引用） |
| F1-contract | ⚠️ | 契约缺口 | spec §六 CorticalBias AC-9~15 | §三 声明的 3 条异常（null × 2 / target 未命中 / Role==Silent）无任何 AC 覆盖——按 spec 实现可省略全部防御检查而测试仍全绿。ToneUpdater 的异常已 AC 化（AC-7），CorticalBias 却无对应项；wc-dynamics AC-11 / wmatrix AC-10 均有先例 |
| F1-data | ⚠️ | 锚点失实（fid 命名错误） | spec §六 AC-11 | 「AccumbensCore/**Shell**/NucleusAccumbens/VentralStriatum」——数据中 fid 名为 **AccumbensShell**，无裸 Shell。按 fid 名解析的测试必挂（wmatrix 结转 #1 警示的同类陷阱） |
| F2-data | ⚠️ | 锚点失实（fid 命名错误） | spec §六 AC-12 + 任务issue 数据实测表 | 「**PAG**」不是数据 fid 名——实际 **PeriaqueductalGray**（§五 C2 解析路径必失败）；「Thalamus×2」应明确为 Thalamus + ThalamusPulvinar。任务issue 15 零清单行有同源错误 |
| F3-data | ⚠️ | 引用来源失真 | spec §六 AC-15 + 任务issue M1 预览行 | 任务issue 行「active 48 ∈ [0.3775, 0.7712]，mean 0.5931」为**全 69 节点口径**（0.3775=排除节点 σ(0)），真实 active 口径 = [0.535174, 0.771229]，mean 0.658196——spec AC-15 数字正确但标注「来自任务issue 预览」失真 |

## 被对抗验证推翻的发现

| # | 发现 | 推翻理由 |
|----|------|---------|
| F2-contract | AC-13 clamp 命中集合未限定「严格超界」语义（10 个 fid 恰为 b=2.0 会污染枚举） | AC-13 自带注释「pre-clamp 2.5 → 2.0」已限定「clamp 实际改变值」语义；「命中」= clamp 生效，边界 fid pre==post 不属命中。发现方算术正确（tone=1 时 13 fid ≥ 2.0：3 个 2.5 + 10 个恰 2.0），但 spec 缺陷不成立——残留 info 级：建议显式注明 10 个边界 fid 消除歧义 |

## 审计结论

- [ ] 通过（无阻塞项）
- [x] **有条件通过（0 ❌ / 5 ⚠️ / 1 refuted）**——公式推导、全部数值锚点、计数结构、行序契约经独立复算通过；5 项 ⚠️ 中 4 项属「按 spec 字面实现必失败 / 引用失实」类（fid 命名 × 2、契约缺口、段引用失实），1 项为同源数据表口径混淆
- [ ] 退回修改

**处置路径**（参照 wmatrix / wc-dynamics 先例）：全部 5 项 ⚠️ 修复 → spec 升版 v1.1（E1-E5 + F6 注释）→ **Δ审计**（只重审变更章节 + 半径扩张复查）→ 人类 sign-off。任务issue 数据实测表同源错误（PAG 缩写、M1 口径）一并修复（四航回顾教训：同源数字一次改齐）。

## 半径扩张

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| E1 §四 备注引用 | 无（纯引用修正） | — |
| E2 新增 AC-16 + §七 补契约防御 | §六 AC 编号序列、工作issue 完成标准引用 AC 编号 | ✅ Δ审计已复查（0 real） |
| E3 AC-11 Shell→AccumbensShell | 工作issue 测试 fid 解析 | ✅ Δ审计已复查（0 real） |
| E4 AC-12 PAG→PeriaqueductalGray / Thalamus×2 明确 | 任务issue 数据实测表 15 零清单行（同源数字） | ✅ Δ审计已复查（0 real） |
| E5 任务issue M1 预览行口径 + spec AC-15 注释 | map.md Notes 行 9 引用同源数字（active 口径同样误标）→ 一并修复 | 已修复 |
| F6 AC-13 边界注释 | 无（注释性） | — |

## Δ审计（spec v1.1）

> 审计日期: 2026-08-13 | 方法: workflow 2 专家（数学/数据 + 契约/交叉引用）+ 逐发现对抗验证（4 agents / 0 错误）| 范围: 仅 E1-E5/F6 变更章节 + 半径扩张

### Trace Table

| # | 专家 | 重审范围 | 判定 |
|----|------|---------|------|
| 1 | 数学/数据 | E1 亲读皮层动力学-通用层 §4.3 确认「Δ = 回合时长（默认 1.0 秒）」；E5 独立重建 W（1389 非零元）复算 active 48 ∈ [0.535174, 0.771229] mean 0.658196 + 加权一致性 (48×0.658196+14×0.3775407+3×0.5498340+4×0.5986877)/69 ≈ 0.59308 ✓；F6 边界 fid 计数 = 10（Accumbens-area 4 + rostralmiddlefrontal 3 + superiorfrontal 2 + lateralorbitofrontal 1）✓；半径扩张 grep 零残留 | ✅ 通过，0 发现 |
| 2 | 契约/交叉引用 | E2 AC-16 ↔ §三 3 异常一一对应 + 构造可行性（GameDataLoader.LoadAll 公开、GameData record `with`、TripartiteModel init List 可追加、EdgeRole.Silent 存在）；E3/E4 fid 名与 JSON 一致；变更日志/版本号/footer/map/issue 🔧 注一致；半径扩张 grep 零残留 | ✅ 通过，2 info（均 refuted） |

### 发现（2 info，均经对抗验证 refuted）

| # | 发现 | 推翻理由 |
|----|------|---------|
| INFO-1 | AC-16 位于 AC-15 之前（编号非单调） | 结构性放置正确（AC-16 属 CorticalBias 表、AC-15 属 M1 里程碑节，各自节内编号单调）；AC 编号是可追溯性标识非位置索引，唯一性成立；重编号会造成任务issue/报告/sign-off 真实引用漂移；项目无全局单调约定 |
| INFO-2 | §六 前言「数值锚点全部来自任务issue 数据实测表」可加「性质断言以 §三 契约为准」区分 | 前言明确限定「数值锚点」，AC-16 无数值锚点故声明空真满足；非缺陷，纯可选精确度建议 |

### Δ审计结论

- [x] **通过（0 ❌ / 0 ⚠️ / 2 info 均 refuted）**——E1-E5/F6 修复全部成立，独立复算通过，半径扩张零残留。
