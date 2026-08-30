# 外部 AI 评审 — Q1（B1-①）alpha_patterns 契约

> 来源: ChatGPT 分享页 t_6a943190ad488191af49887a9acd5ae3（标题「确定JsonRequired方案」，发布 2026-08-30T13:35:12Z）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复（唯一可访问消息）。

---

**Q1（B1-①）定案：采纳你提出的四点契约，不做修改。**

这套边界很干净，尤其要把**“数据表完整性”**和**“引擎当前消费范围”**分开，否则以后很容易把 A3/A6/A7 的“不消费”误解成“数据不存在”。

### 锁定契约

**1. 行 ID ↔ 派生分支绑定：留在代码。**

`EventProcessor` 的 Emit 调用点明确持有：

`A1 / A2 / A4 / A5 / B1 / B2 / B4 / C1 / D1 / D2`

JSON 负责：

> `row_id → pattern[8]`

而不负责描述“这个 row_id 在什么事件/视角分支下触发”。

这样事件派生逻辑仍是代码的固有语义，数据层只是参数表。

---

**2. `m_alpha` 采用二态编码。**

允许：

```text
数字 [0,1]       → 常量值
"m_delta"        → 使用该分支已有算法计算 m
```

因此：

- A 类 → `1.0`
- B/C/D 类 → `"m_delta"`

这里建议再锁一个边界：**数字必须是有限数值且位于 `[0,1]`**，不能接受 `NaN`、`Infinity` 或越界值。

---

**3. 缺失/畸形数据必须 fail-fast。**

以下均属于加载错误：

- 消费行缺失；
- `pattern` 长度 ≠ 8；
- `m_alpha` 类型非法；
- 数值型 `m_alpha` 越界；
- `"m_delta"` 之外的字符串。

原则就是：

> **数据表不是可选配置；一旦进入引擎加载路径，就必须满足 schema。**

不要静默补零、截断或自动修复。

---

**4. 14 行数据完整保留，但引擎只映射 10 行。**

锁定：

```text
alpha_patterns.json
├── 14 rows：数据层完整集合
│
└── EventProcessor
    └── 10 rows：当前实际消费集合
```

A3/A6/A7 **保留在数据文件中，不要求当前 EventProcessor 消费**。

这尤其重要，因为它保持了 #69 的数据层完整性，同时不把尚未落地的分支硬塞进当前 P2 实现。

### Q1 正式记录

> **Q1（B1-①）：采纳。**
>
> `alpha_patterns.json` 建立 `row_id → pattern[8]` 数据契约；row ID 与 EventProcessor 派生分支的绑定由代码持有，不进入 JSON。
>
> `m_alpha` 允许两种编码：有限数字 `[0,1]`（常量）或 `"m_delta"`（调用现有分支算法计算 m）。当前 A 类使用 `1.0`，B/C/D 类使用 `"m_delta"`。
>
> 消费行缺失、pattern 长度错误或字段值类型/范围非法均在加载期 fail-fast，禁止静默置零、截断或自动修复。
>
> JSON 保留完整 14 行；EventProcessor 当前仅映射实际消费的 10 行（A1/A2/A4/A5/B1/B2/B4/C1/D1/D2），A3/A6/A7 保留但不消费。

**Q1 可以闭合。**

---

If you want, I can:

- Explain how fail-fast behavior improves data integrity in this contract
- Describe how numeric m_alpha values are limited and why
- Detail why the JSON keeps 14 rows but EventProcessor consumes only 10
