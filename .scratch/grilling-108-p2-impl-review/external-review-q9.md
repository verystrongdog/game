# 外部 AI 评审 — Q9 moonlight_landing.json schema

> 来源: ChatGPT 分享页 t_6a944f6054888191bf9e026c91029fe3（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取 4 条消息。

---

## [168]

请说明为什么12个fid级落点不能直接与48个dk级活跃节点比较，fid→dk映射在校验中的作用及如何防止实现错误。

## [184]

请用简洁明了的语言总结引擎加载期执行的四项校验规则（supp互斥、归一化、support映射、非负及r>0），并说明每条规则的重要性。

## [189]

请详细解释为什么字段缺失时禁止静默补为"PLACEHOLDER"，以及这对数据加载和校准的影响为何重要。

## [197]

**Q9 定案：选 A — 参数形式 schema。**

我赞成 A，而且这里有一个地方建议在定案文字里**稍微收紧**：`PLACEHOLDER` 可以作为**明确的占位状态**存在，但不能再出现“字段缺失时自动补 `PLACEHOLDER`”这种静默默认。字段缺失和字段显式占位是两回事。

### 锁定 schema

核心结构：

```text id="6x3mqp"
moonlight_landing.json
├── schema
├── version
├── calibration_status
├── calibration_version
└── semantics[]
    ├── id
    ├── primary[4]
    ├── secondary[8]
    ├── r
    └── alpha_s
```

其中：

- `r = "PLACEHOLDER"` → 当前按占位规则使用 `r = 1`，因此得到 12 落点均匀分配；
- `r` 完成 #35 校准后改为数值；
- `alpha_s = "PLACEHOLDER"` 同样明确表示**尚未校准**，不伪装成正式数值；
- `calibration_status` / `calibration_version` 位于**文件顶层**；
- 不生成第二个 calibration 状态文件。

这里尤其要区分：

```text id="q2n8vs"
字段存在 + "PLACEHOLDER"  → 合法的未校准状态
字段缺失                  → ❌ schema/load error
```

这样才能延续 #106 的“禁止静默回退”原则。

### 为什么参数形式优于预计算数组

A 保留了：

> **主/辅落点 + `r` → `v_s^norm`**

这一唯一生成路径。

因此以后 #35 只需要校准 `r`，不用同时维护一套 12 个预计算权重，也避免：

```text id="m4v7dc"
r = 1.4
       ↓
公式算出来的 v^norm ≠
JSON 里另存的 12 个 weight
```

这种双源漂移。

### 四项加载期门禁锁死

引擎读取文件后直接验证：

1. **supp 互斥**：不同 semantics 的 support 不得重叠；
2. **归一化**：按 #101 Q4 公式重算后 `Σ v_s^norm = 1`；
3. **support ⊆ W_active**：先进行 **fid → dk** 映射，再验证落点属于 48 个活跃 dk 节点；
4. **非负 / `r > 0`**：保证生成权重合法。

这里你核实的 **48 个 W_active 是 dk 级，而 12 落点是 fid 级**，因此实现时不能直接比较字符串；必须经过既有 fid→dk 映射。这一点值得直接写进 task-plan，否则非常容易出现“12 个 fid 看起来都在图里，但校验集合实际上是 dk”的实现错误。

### 关于 `alpha_s`

本题只锁定它作为 schema 中的**显式校准参数/占位字段**存在；不在 Q9 重新定义 #101/#35 已有的数值语义。也就是说，不借 schema 题重新打开 α_s 的正式数值问题。

### Q9 正式记录

> **Q9（B3-⑨）：A。`moonlight_landing.json` 采用参数形式 schema：顶层包含 `schema`、`version`、`calibration_status`、`calibration_version`，`semantics[]` 包含 `id`、`primary[4]`、`secondary[8]`、`r`、`alpha_s`。**
>
> `r`/`alpha_s` 的未校准状态显式编码为字符串 `"PLACEHOLDER"`；`r="PLACEHOLDER"` 时按 `r=1` 的占位规则由 #101 Q4 公式计算均匀的 12 落点权重。**字段缺失不得静默补为 `PLACEHOLDER`。**
>
> `calibration_status` 为文件顶层校准状态，不另建校准状态文件；`calibration_version` 同样位于顶层并由后续 `moonState(D)` 读取。
>
> 引擎加载期执行 fail-fast 校验：support 互斥、按公式计算的权重归一化、support 经 fid→dk 映射后属于 48 个 `W_active` 端点集、以及 `r > 0`/权重非负。预计算 `v^norm` 不作为第二数据源。
>
> 正式 `r`/`alpha_s` 数值仍归 #35 校准，本题只锁 schema 与加载契约。

**Q9 闭合，选 A。**

---

If you want, I can:

- Explain the reason for forbidding silent placeholder fallback
- Summarize the four loading phase validations in simple terms
- Describe how fid-to-dk mapping avoids validation errors
