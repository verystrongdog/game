# 外部 AI 评审 — Q10 moonState(D) C# 契约骨架

> 来源: ChatGPT 分享页 t_6a9450c4d4c0819184c13be8502a06f3（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取 4 条消息。

---

## [177]

请详细探讨schema_version与calibration_version分离设计的原因、带来的好处，以及如何配合Q11门禁处理实现顶层状态兼容性。

## [193]

请详细解释graph identity如何最终确定q̂的硬维度，以及为什么当前选择N=69作为占位契约，这对产品升级意味着什么？

## [198]

请详细说明为什么P2实现不包括D的推进机制和MOON_PHASE_CHANGED广播，它们对系统设计的影响，以及后续版本如何计划处理这些功能。

## [206]

**Q10 定案：选 A — 静态纯函数 + 单记录 + `N=69` 占位契约。**

这与 #103 的纯函数、无副作用契约以及 #104 的 q̂ 消费路径要求完全一致。B/C 都会破坏已经锁定的上层边界。

### 锁定 API

核心形态：

```csharp
static class MoonState
{
    public static MoonStateResult Query(int day);
}
```

返回结构包含：

```text id="2q6v8p"
Phase          → λ(D)
Shell          → E_c(λ), E_th(λ)
QhatBaseline   → double[69]
Status         → CalibrationStatus
Version        → major.minor
```

`Query` 必须是**纯函数**：

- 不推进 `D`
- 不修改全局状态
- 不广播事件
- 不依赖战斗/空间/时段状态
- 相同 `day` + 相同配置 → 相同结果

### `D` 的边界保持不变

P2 **只实现查询，不实现 D 的推进机制**。

也就是：

```text id="m6j1sd"
游戏循环
    │
    │ （未来：夜晚第 3 次休息）
    ▼
D ← D + 1
    │
    ▼
MoonState.Query(D)
```

本轮 demo 直接给定 `D`，用于展示 `λ(D)` 的变化。

同理，`MOON_PHASE_CHANGED` 虽然已经在 #103 定义，但当前没有消费者，因此 **P2 不实现广播**，避免凭空建立第二条状态路径。

### `E_c / E_th`

这里锁定的是**结构实现，不是校准数值**。

即：

```text id="k3f7ya"
λ(D)
  ↓
E_c(λ)
E_th(λ)
```

按照 #102 E2 已锁定的形式计算；其中新增常量放进 `CalibrationConfig`，当前仍为 `PLACEHOLDER`。

所以不会把 #35 的数值校准偷渡到 #105。

### q̂ 的 `N=69`

P2 暂时固定：

```text
QhatBaseline.Length == 69
```

这是**当前占位契约**，不是最终声称 graph identity 已经证明 `N=69`。

待 graph identity 正式闭合后，升级为：

```text
QhatBaseline.Length == N(graph_identity)
```

这个 distinction 很重要，否则以后 graph identity 落地时容易出现“为什么已经写死 69”的设计债。

### Q10 正式记录

> **Q10（B3-⑩）：A。采用 `static class MoonState` + `public static MoonStateResult Query(int day)` 的静态纯函数 API。返回 `Phase=λ(D)`、`Shell={E_c(λ), E_th(λ)}`、`QhatBaseline[69]`、`CalibrationStatus`、`Version`。**
>
> `Query` 无副作用，不推进 D、不修改全局状态、不广播事件；P2 不实现 D 的推进机制及 `MOON_PHASE_CHANGED` 广播。Demo 使用固定 D 调用 Query 展示月相变化。
>
> `E_c/E_th` 按 #102 E2 已锁定形式进行结构实现，相关常量置于 `CalibrationConfig`，当前值为 `PLACEHOLDER`；正式数值仍归校准轨。
>
> `QhatBaseline` 当前采用 `N=69` 占位契约；待 graph identity 闭合后升级为由 graph identity 确定的 N，并执行硬维度校验。
>
> `schema_version` 与 `calibration_version` 分离；本题仅锁定 MoonState 对顶层 calibration 状态/版本的读取，统一 schema major 兼容性校验归 Q11 门禁处理。

**Q10 闭合，选 A。**

---

If you want, I can:

- Expand on P2 implementation details for D advancement and broadcasting
- Clarify the relationship between graph identity and q̂ dimension N=69
- Discuss version separation strategy for schema_version and calibration_version
