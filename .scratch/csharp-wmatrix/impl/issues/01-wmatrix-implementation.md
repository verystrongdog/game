# 工作issue 01: WMatrixBuilder 实现

> Status: claimed | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅ (2026-08-13)

## 问题（这件事要解决什么）

spec v1.1 已批准的 WMatrixBuilder（6 步构建算法）落地为可编译 C#：69×69 归一化权重矩阵 W + τ[69] 时间常数 + RowFids 行序。这是 WC 引擎 Layer 1 的输入——没有它，step 4（WcDynamics）无法编译、运行时状态模型 §四 Layer 1 无法落地。

## 目标

按 spec@v1.1 §二-§六 实现 `WMatrixBuilder.Build` 及 12 条 AC 的全部测试，`dotnet build` 0 错误 + 测试全绿。

## 指标

- AC-1 ~ AC-12 全部 ✅（含门禁 build/test）
- Build XML doc 含职责/输入/输出/异常/来源（spec §三 + plan「设计两次」约束）
- 2 项 sign-off 结转在本 feature 范围内回填验证（#1 AC-7 解析规则 / #2 AC-11 计数推导）

## 范围

引用 spec@v1.1 章节：§二 构建算法（Step 1-6）、§三 接口定义、§四 枚举与常量、§五 交叉引用约束 C1-C9。覆盖 AC-1~AC-12。

不覆盖：WcDynamics（step 4）、脑干 b_j 广播（step 5）、运行时 m/focus 接口（B4 注释预留）、5 处设计文档修正（sign-off 结转 #3，feature 闭合后执行）。

## 文件所有权声明

本 issue 独占修改（grep 已确认无其他进行中 work issue 冲突；src/YouAreNotTheFish.Core/Engine/ 目录存在且为空）：

- `src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/WMatrixBuilderTests.cs` — 新建

不碰 csproj（Engine/ 与 Engine tests/ 目录随文件自动纳入，无新依赖）。

## 完成标准

spec@v1.1 §六 AC-1 ~ AC-12 逐条对照（见「代码自审」段）。

## 实现

（见 commits）

## 代码自审（证据式）

### 门禁证据
- [ ] `dotnet build` 零错误
- [ ] `dotnet test` 全绿（含通过数/总数）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | W 69×69 / Tau 69 / RowFids 69 | | |
| AC-2 | RowFids == RegionIds；与 GraphNodes fids 双射 | | |
| AC-3 | 21 排除 fid 行列全 0 | | |
| AC-4 | 非零元 == 1389 | | |
| AC-5 | 48 行 ∈(0,1)；21 行 == 0 | | |
| AC-6 | 735 幸存对块等值；CC∩PP 重叠 0 | | |
| AC-7 | 5 锚点值（绝对容差 1e-5） | | |
| AC-8 | τ 分布 27/30/12 + 2 mirror 点名 | | |
| AC-9 | 双 Build 逐元相等 | | |
| AC-10 | 不可解析端点 → InvalidDataException | | |
| AC-11 | 69 对角 0 + 同 dk 非对角 50 格 0 | | |
| AC-12 | 21 排除 fid Tau > 0 | | |

### spec §七 自检清单
（逐项打勾）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | AC-7 锚点测试按 Step 4.3 解析规则展开（graph_nodes 键优先 → fid→dk 兜底；'Pericalcarine' 是 fid 名而 dk 键为小写 'pericalcarine'） | |
| 2 | AC-11 计数 50 由 graph_nodes 全量推导（Σ n(n−1)，不硬编码） | |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|

## Comments
