# WMatrixBuilder — 实现规格

> W 矩阵（69×69 皮层-皮层连接权重 + τ[69] 时间常数）的构建器规格——WC 引擎 Layer 1 的输入，csharp-engine plan §十一 step 3。版本: v1.1

## 目录

- [一、范围与依赖](#一范围与依赖)
- [二、构建算法](#二构建算法)
- [三、接口定义](#三接口定义)
- [四、枚举与常量](#四枚举与常量)
- [五、交叉引用约束](#五交叉引用约束)
- [六、验收标准](#六验收标准)
- [七、本 spec 自检清单](#七本-spec-自检清单)
- [变更日志](#变更日志)
- [参数速查表](#参数速查表)

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `WMatrixBuilder.Build(GameData data) → WMatrix`：W[69,69] 归一化权重 / Tau[69] 时间常数 / RowFids[69] 行序（WMatrix 契约类型由 csharp-engine-types 已交付，本 feature 只实现构建） |
| 不覆盖 | WcDynamics（step 4）、脑干 b_j 广播计算（step 5）、运行时 m 值（demo 全 m_default）、focus 聚焦配置（demo 全 1.0）、LinkState/CombatContext |
| 前置依赖 | csharp-data-layer ✅（GameData / TripartiteModel / BrainRegionsData / WsensoryMatrix 及 JSON 加载）；csharp-engine-types ✅（WMatrix 契约 + CalibrationConfig.Default.MDefault） |
| 阻塞 | step 4 csharp-wc-dynamics（其输入 h_j = W·a + b + s 依赖本 feature 的 W/Tau/行序） |
| 输入数据 | `data/brain_regions.json`（Regions 69，function_profile.timescale）、`data/connectivity/tripartite_model.json`（graph_nodes 51 / corticocortical 776 / privileged_pathways 112）、`data/connectivity/W_sensory.json`（rows 69 键 = canonical 行序）——均经 GameDataLoader.LoadAll 加载 |

本规格的决策依据 = [任务issue 01](../../.scratch/csharp-wmatrix/design/issues/01-wmatrix-spec.md) D1-D8（其「数据实测」表为本 spec 全部计数与锚点的出处，2026-08-13 python 实测 JSON，非凭记忆）。

### 偏差声明（与设计文档的已知差异，实现必须照此执行）

| # | 偏差 | 依据 |
|----|------|------|
| B1 | [皮层动力学-通用层](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md) §5.3 备注「皮层-皮层 W 仅包含 ~34 个 dk_name（皮层节点）」与[运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §4.2 排除清单不一致——**按运行时状态模型 §4.2 执行**：W 活跃节点 = 48 fids（44 皮层 + Amygdala + Hippocampus×2 + Cerebellum-Cortex），排除 = CSTC 6 dk + brainstem（16 dk / 21 fids）。**延后文档修正清单（v1.1 审计补全）**：①皮层动力学-通用层 §5.1（「仅 category=cortical」措辞）、§5.3（「~34 dk_name」+「CC 独有 6 节点」清单含已排除 Pallidum）；②运行时状态模型 §4.1（方程作用域「category=cortical 且不在 CSTC 排除清单中」）、§4.5（「25 个 subcortical/brainstem 节点不参与 WC 皮层动力学」）、参数速查表（「CC 节点数（排除后）~34 dk」——实测 35）。全部延后至审计后执行（任务issue D1/Q1） |
| B2 | plan §4.1 第 3 条括注「brainstem dk_name=None 节点（PAG、上丘、脑桥网状核、小脑皮层）」中**「小脑皮层」归类有误**——实测 Cerebellum-Cortex category=subcortical 且不在 CSTC 清单，**不排除**，参与 W（幸存口径触边 CC 6 条 + PP 12 条；任务issue 表中「CC 40 + PP 51」为 {Amygdala, Hippocampus, Cerebellum-Cortex} 三 dk 并集口径——v1.1 修正）。plan 文档修正延后（任务issue D1） |
| B3 | **方向契约**：[皮层动力学-通用层](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md) §5.1 `W[fid_A][fid_B] = w(dk(fid_A), dk(fid_B))` 是 [源][目标] 序；[运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §4.1 方程 `h_j = Σ_k W_jk·a_k` 要求 [行=接收者][列=发送者]。两者互为转置——demo 归一化前权重对称时数值无差，但归一化后行和不同会分叉。**本 spec 以运行时方程方向为准**：W[行=接收者][列=发送者]（任务issue D8） |
| B4 | m_mean 推导（§5.3 的 link_registry 映射）不落地——demo 无 LinkState，全部 m_mean ≡ CalibrationConfig.Default.MDefault = 0.3；focus_multiplier ≡ 1.0（§5.2 取值范围 1.0/2.0 中的基础档）。Build 签名无 focus 参数，接口注释预留（任务issue D2） |

## 二、构建算法

Build 为纯函数，共 6 步。每一步的来源见右列（设计文档章节引用）。

### Step 1 — 行序契约

- canonical 行序 = `data.Wsensory.RegionIds`（69，源自 W_sensory.json `rows` 的键序，首键 AccumbensCore）。
- 构建 `fid → rowIndex` 字典；`W.RowFids` = RegionIds 拷贝（防御性拷贝，WMatrix 构造已克隆）。
- 来源：csharp-engine-types spec C1 + 结转 #5；本 feature 落地 `RowFids == RegionIds` 断言（AC-2）。

### Step 2 — fid→dk 映射

- 遍历 `data.Tripartite.GraphNodes`（51 键），收集 `functional_ids` → `fid→dk` 字典。
- 实测：69 个 fid 唯一、与 RegionIds 双向双射（C2）。非双射 = 数据错误（测试拦截，builder 不防御）。

### Step 3 — 排除集

```
EXCLUDED_DK = { dk : GraphNodes[dk].Category == Brainstem } ∪ CSTC_DK
CSTC_DK = { Pallidum, Thalamus-Proper, Putamen, Caudate, Accumbens-area, SubthalamicNucleus }
```

- 实测：16 dk（CSTC 6 + brainstem 11，SubthalamicNucleus 双归属只计一次）/ 21 fids（10 CSTC 皮下 + 11 脑干）。
- 排除 fid 的 W 行=列恒 0；**仍填充 Tau**（排除节点 h_j = b_j + s_j，仍由 WC 驱动——运行时状态模型 §4.2、§5.7）。
- 来源：运行时状态模型 §4.2（CSTC 6 名逐字 + 脑干行=列=0）；GraphNodes 的 Category 字段为 builder 唯一判定来源（brain_regions 的 dk_name=None 仅作文档表述，不入算法）。

### Step 4 — 边遍历与权重

对 `Corticocortical ∪ PrivilegedPathways`（776 + 112 条）逐条处理，边 (S, T, edr)：

1. S 或 T ∈ EXCLUDED_DK → **跳过**（实测跳过 CC 130 / PP 23 → 幸存 CC 646 + PP 89 = 735）。
2. S == T → 跳过（自连接 w(A,A)=0，皮层动力学-通用层 §5.2；实测数据 0 条自环，防御性规则）。
3. 端点解析（任务issue D4）：S/T 先按 dk_name 查 GraphNodes；未命中再按 functional_id 查 fid→dk 字典（视为单 fid）；两者都失败 → 抛 `InvalidDataException`（含边描述）。实测当前数据 100% 按 dk_name 解析；15 个 dk/fid 同名歧义名中，非排除 dk 全为单 fid（仅 Amygdala）——Caudate（2 fids）∈ CSTC 排除集，第 1 条排除检查先行，歧义解析永不触达它（v1.1 修正理由表述）。
4. 权重 `w = edr × m_mean × focus_multiplier`，其中 `m_mean = CalibrationConfig.Default.MDefault`（0.3f）、`focus_multiplier = 1.0f`（B4）。公式来源：皮层动力学-通用层 §5.2。
5. **fan-out 广播**：对 S 的每个 fid s、T 的每个 fid t：`W[rowIndex(t)][rowIndex(s)] += w`（行=接收者=target，B3）。同 dk 对内多个 fid 共享同一权重模式（plan §4.1 第 1 条）。
6. 累加（`+=`）为防御语义：实测 CC∩PP 幸存 dk 对重叠 = 0（无重复边对），当前数据下与赋值等价——测试锁定该不变量（AC-6 附注）。

实测产出：幸存 edr ∈ [0.103, 0.759] → 未归一化 w ∈ [0.0309, 0.2277]；fan-out 后非零元 1389。

### Step 5 — 行归一化

对全部 69 行（含排除行，无异常分支——任务issue Q2）：

```
sum_j = Σ_k W[j][k]
W[j][k] = W[j][k] / (sum_j + ε)，ε = 0.01
```

- 来源：皮层动力学-通用层 §5.4、运行时状态模型 §4.3。
- 性质（实测）：48 活跃行 sum = S_j/(S_j+ε) ∈ (0,1)；21 排除行 sum = 0。
- **归一化后 W 一般不对称**：同一双向对的 W[j][k] 与 W[k][j] 各自除以不同行和（实测 tt↔cac 归一化后 0.02819 vs 0.03621）——不是实现错误（任务issue 数据实测表已精确化此表述）。

### Step 6 — τ 数组

按 canonical 行序逐 fid：

1. `region = data.BrainRegions.Regions[fid]`；`ts = region.FunctionProfile.Timescale`（`Timescale?`）。
2. `ts == null` → 若 `FunctionProfile.MirrorOf` 非空，取镜像目标 region 的 Timescale（一层继承）；仍为 null → 按 medium 处理。
3. 映射：Fast→0.01f / Medium→0.05f / Slow→0.15f（皮层动力学-通用层 §4.4）。

实测：原始字段 fast 27 / medium 29 / slow 11 / mirror 2（LocusCoeruleusRight→LocusCoeruleus=slow、SubstantiaNigraParsCompactaRight→SubstantiaNigraParsCompacta=medium）；**继承后最终 Tau[69] 分布 = fast 27 / medium 30 / slow 12**（v1.1 修正，与 AC-8 一致）。**69 个 fid 全部有 τ > 0（含 21 排除 fid）**。

## 三、接口定义

新文件 `src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs`（Engine/ 目录已存在，内新建文件；plan §3.2 L2 Engine 层约定：纯函数、无副作用、RNG 注入——本 builder 无 RNG 依赖）：

```csharp
namespace YouAreNotTheFish.Core.Engine;

public static class WMatrixBuilder
{
    /// <summary>
    /// 构建 69×69 皮层-皮层连接权重矩阵 W 与时间常数数组 Tau。
    /// 职责：边筛选（排除清单）→ 权重（w = edr × m_mean × focus）→ fan-out 广播
    /// → 行归一化（ε=0.01）→ τ 查表（含 mirror 继承）。
    /// 输入：GameData（消费 Tripartite / BrainRegions / Wsensory 三部分）。
    /// 输出：WMatrix（W[69,69] / Tau[69] / RowFids[69]），RowFids 顺序 == Wsensory.RegionIds。
    /// 异常：data 为 null → ArgumentNullException；
    ///       边端点无法经 GraphNodes 或 functional_id 解析 → InvalidDataException。
    /// 来源：csharp-engine plan §4.1；皮层动力学-通用层 §5.1-5.5、§4.4；运行时状态模型 §4.1-4.2。
    /// </summary>
    public static WMatrix Build(GameData data);
}
```

- 纯函数：无 static 可变状态、无 RNG、同输入同输出（AC-9）。
- 契约类型 WMatrix 构造已做防御性拷贝（csharp-engine-types 已交付），builder 不复刻。
- 数学公式与本文 §二逐行一致；XML doc 先行（plan「设计两次」约束，本 feature 属 6 个数值核心模块之一）。

## 四、枚举与常量

| 常量 | 符号 | 值 | 来源 | 位置 |
|------|------|-----|------|------|
| CSTC 排除 dk 集 | CSTC_DK | 6 名（Pallidum / Thalamus-Proper / Putamen / Caudate / Accumbens-area / SubthalamicNucleus） | 运行时状态模型 §4.2 | builder 私有 static readonly string[] |
| 归一化兜底 | ε | 0.01f | 皮层动力学-通用层 §5.4 | builder 私有 const |
| 髓鞘化（demo） | m_mean | 0.3f（引用 CalibrationConfig.Default.MDefault） | plan §七 / B4 | 复用 CalibrationConfig，不新建 |
| focus 乘子（demo） | focus_multiplier | 1.0f | 皮层动力学-通用层 §5.2 基础档 / B4 | builder 私有 const（注释预留聚焦接口） |
| τ 映射 | τ_fast / τ_medium / τ_slow / τ_default | 0.01f / 0.05f / 0.15f / 0.05f | 皮层动力学-通用层 §4.4 | builder 私有 static |
| 矩阵尺寸 | N | 69 | W_sensory rows 键数（实测） | 不新建常量，取 RegionIds.Length |

不新增枚举类型（复用已交付的 BrainRegionCategory / Timescale / TripartiteEdge 等）。

## 五、交叉引用约束

| # | 约束 | 性质 | 验证方式 |
|----|------|------|---------|
| C1 | `W.RowFids` 序列 == `Wsensory.RegionIds` 序列（canonical 唯一行序，无第二行序引用） | 恒等式 | AC-2 |
| C2 | GraphNodes.functional_ids 与 RegionIds 双向双射（69 == 69） | 数据不变量 | AC-2 附注（数据层已有测试，本 feature 加 builder 视角断言） |
| C3 | 排除集 == 16 dk / 21 fids；排除 fid 的行与列全 0 | 规格定义 | AC-3 |
| C4 | 每条边端点可解析（dk 优先 → fid 兜底 → 抛 InvalidDataException）；当前数据 0 失败 | 完整性 | AC-10 |
| C5 | fan-out 广播：同一 dk 对内所有 fid 单元格等值；同 dk 内非对角 fid 对恒 0（自连接 0 + 无自环的推论，共 Σ_dk n(n−1) = 50 个） | 结构性 | AC-6 / AC-11 |
| C6 | 方向契约：W[行=接收者][列=发送者]，与 h_j = Σ_k W_jk·a_k 一致（B3） | 规格定义 | AC-7 锚点（W[Amygdala][Pericalcarine] ≠ 0 且 W[Pericalcarine][Amygdala] == 0 唯一锁定方向） |
| C7 | 归一化性质：48 活跃行 sum ∈ (0,1)；21 排除行 sum == 0 | 数值 | AC-5 |
| C8 | 非零元计数 == 1389（fan-out 后全量） | 数据不变量 | AC-4 |
| C9 | 69 个 fid 全部 Tau > 0（含 21 排除 fid）；2 个 mirror fid 继承镜像目标值 | 完整性 | AC-8 / AC-12 |

## 六、验收标准

| AC | 验收标准 | 测试方式 |
|----|---------|---------|
| AC-1 | Build 返回 WMatrix：W 尺寸 69×69、Tau 长度 69、RowFids 长度 69 | 构造断言 |
| AC-2 | RowFids 序列 == RegionIds（C1，结转 #5 落地）；RegionIds 与 GraphNodes fids 双射 | 序列相等断言 + 集合断言 |
| AC-3 | 21 个排除 fid 的行全 0 且列全 0（C3） | 全量扫描 |
| AC-4 | 非零元计数 == 1389（C8） | 全量计数 |
| AC-5 | 48 行 0 < sum < 1；21 行 sum == 0（C7） | 全量行和断言 |
| AC-6 | fan-out 广播：全部 735 幸存 dk 对，块内单元格等值（全量扫描）；数据层不变量「CC∩PP 幸存 dk 对重叠 = 0」同步锁定 | 全量块等值 + 数据对集断言 |
| AC-7 | 锚点值（2026-08-13 由数据文件独立计算所得，**绝对容差 1e-5**；float32 实测偏差 <2e-7，余量 ~100×；数据文件变更时同步更新——本组锚点兼作数据漂移哨兵）：<br>· W[接收=Amygdala][发送=Pericalcarine] ≈ 0.02277450（唯一非互惠边，方向契约哨兵）<br>· W[接收=Pericalcarine][发送=Amygdala] == 0<br>· W[接收 dk=caudalanteriorcingulate][发送 dk=transversetemporal] ≈ 0.03620595（3 fid 行等值）<br>· W[接收 dk=transversetemporal][发送 dk=caudalanteriorcingulate] ≈ 0.02819380（锁定归一化后不对称）<br>· W[接收 dk=Hippocampus][发送 dk=entorhinal] ≈ 0.07386513（PP 边锚点，2 fid 行等值） | 锚点以 **dk 名**标识（Amygdala/Pericalcarine 同时是 fid 名）：锚点标识符按 §二 Step 4.3 端点解析规则展开（graph_nodes 键优先 → fid→dk 兜底），dk→fids 经 GraphNodes.functional_ids 展开，对块内每个单元格断言；fid 索引经 RowFids 查得（v1.1 修正命名粒度；Δ审计后补解析规则引用） |
| AC-8 | τ 分布（**继承后最终 Tau[69]**）：27 个 fid == 0.01、30 == 0.05、12 == 0.15；LocusCoeruleusRight == 0.15、SubstantiaNigraParsCompactaRight == 0.05（mirror 继承；v1.1 修正——29/11 只对 67 个非 mirror 原始字段成立） | 计数 + 点名断言 |
| AC-9 | 确定性：同一 GameData 两次 Build 结果逐元相等 | 双调用逐元对拍 |
| AC-10 | 端点不可解析 → InvalidDataException（合成 GameData：构造伪 tripartite 边） | 异常断言 |
| AC-11 | 自连接与同 dk：69 对角线全 0；同 dk 内**非对角** fid 对共 Σ_dk n(n−1) = 50 个单元格全 0（C5 推论，计数由 graph_nodes 全量推导；v1.1 修正——82 口径含对角，与 69 对角断言重复计数） | 全量扫描 + 计数断言 |
| AC-12 | 21 个排除 fid 的 Tau 均 > 0（排除节点仍 WC 驱动，C9） | 全量断言 |

> 数据漂移哨兵：AC-3/4/5/6/7/8/11/12 的期望计数/锚点/分布均源自数据 JSON（AC-5 的行数分界 48/21 与 AC-12 的 21 亦含数据计数），数据文件变更时同步复核期望值——它们兼作数据回归测试。

## 七、本 spec 自检清单

工作issue 的「代码自审」段逐项引用本清单：

- [ ] **数学公式逐项对照**：w = edr × m_mean × focus / 行归一化 +ε / τ 映射 与 皮层动力学-通用层 §5.2/§5.4/§4.4、运行时状态模型 §4.1-4.2 逐字一致
- [ ] **数据断言全部实测**：本 spec 所有计数与锚点（735/1389/50/21/16/27-30-12/5 锚点值）出自 2026-08-13 python 实测 JSON，无凭记忆数字
- [ ] **行序契约唯一 canonical** = RegionIds；无 BrainRegionsData.Regions 序引用
- [ ] **方向契约明确**（行=接收者，B3）且方向哨兵锚点入 AC-7
- [ ] **边界值覆盖**：零行 / 唯一非互惠对 / mirror 继承 / 不可解析端点 / 自连接 / 同 dk 对 / 排除节点 τ
- [ ] **确定性**：无 RNG、无 static 可变状态
- [ ] **接口注释先行**（Build XML doc 含职责/输入/输出/异常/来源——plan「设计两次」约束）
- [ ] **偏差声明完整**：B1（节点集分界）/ B2（小脑皮层归类）/ B3（方向）/ B4（m/focus demo 常数）全部在实现中有对应注释
- [ ] **排除清单逐名一致**：CSTC_DK 6 名与运行时状态模型 §4.2 逐字对照（含 STN 双归属说明）

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿：6 步构建算法 + 12 条 AC + 偏差声明 B1-B4（任务issue D1-D8 固化） | 任务issue 01 | 全量审计（3 专家退回：AC-11 计数 82 错 / AC-8 分布口径矛盾 / B2 数字误挂） |
| v1.1 | 2026-08-13 | 审计修正：AC-11 82→50（Σ_dk n(n−1) 非对角口径）、AC-8 改继承后最终分布 27/30/12、B2 支撑数字改 Cerebellum-Cortex 幸存口径（CC 6 + PP 12）、AC-7 锚点改 dk 名标识 + 绝对容差声明、Step 4.3 歧义名理由修正（Caudate 2 fids）、B1 补完整修正清单（5 处）、Step 5 段号 §4.2→§4.3、数据漂移哨兵统一标注、§七/§三 同步 | v1.0 全量审计退回 | Δ审计（变更章节 + 半径扩张） |
| v1.1 🔧 | 2026-08-13 | Δ审计后 L1 修正（免重审，表述类）：AC-7 测试方式补 Step 4.3 端点解析规则引用、数据漂移哨兵扩展至 AC-3/5/12 | Δ审计 conditional（0 error / 2 warning） | 免重审 |
| v1.1 🔧² | 2026-08-13 | 结转 #3 执行：B1 延后修正清单 5 处设计文档修正完成（工作issue 01 闭合后——皮层动力学 §5.1「仅 cortical」措辞、§5.3「~34 dk_name」+ Pallidum 移出清单；运行时状态模型 §4.1 方程作用域、§4.5「不参与 WC」谓词、参数速查表 35 dk） | sign-off 结转 #3 | 免重审（L1 文档清理，非本 spec 内容变更） |
| v1.1 🔧³ | 2026-08-13 | 用户批准的方向公式索引序修正（B3 裁定的执行）：皮层动力学 §5.1 公式改为 `W[fid_j][fid_k] = w(dk(fid_k) → dk(fid_j))`（行=接收者）并标注原 [源][目标] 序；运行时状态模型 §4.3 补放置说明 `W[fid_B][fid_A] = w(A,B)` | 用户确认（本 spec B3 内容不变——方向裁定已由两轮审计 5 专家确认） | 免重审 |

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 权重公式 | w = edr × m_mean × focus_multiplier | — | §二 Step 4 |
| 髓鞘化（demo） | m_mean | 0.3 | CalibrationConfig.MDefault |
| focus 乘子（demo） | focus_multiplier | 1.0 | §二 Step 4（B4） |
| 归一化兜底 | ε | 0.01 | §二 Step 5 |
| 时间常数 | τ_fast / τ_medium / τ_slow / τ_default | 0.01 / 0.05 / 0.15 / 0.05 | §二 Step 6 |
| 矩阵尺寸 | N | 69 | §五 C1 |
| 排除集 | EXCLUDED_DK | 16 dk / 21 fids | §二 Step 3 |
| 幸存边 | — | 735（CC 646 + PP 89） | §二 Step 4 |
| 非零元 | — | 1389 | §五 C8 |
| 幸存 edr 范围 | — | [0.103, 0.759] | §二 Step 4 |

---
*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.1*
*关联: [任务issue 01](../../.scratch/csharp-wmatrix/design/issues/01-wmatrix-spec.md), [csharp-engine plan](../../csharp-engine/design/plan.md), [皮层动力学-通用层](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md), [运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [csharp-engine-types spec](../../csharp-engine-types/design/spec.md)*
