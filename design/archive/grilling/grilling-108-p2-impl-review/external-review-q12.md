# 外部 AI 评审 — Q12 s_total 合成时序

> 来源: ChatGPT 分享页 t_6a9452165b9081919859cb9c0c9d91c2（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复。

---

Q12 定案：**选 A——Phase 1 注入点合成。**

这个方案和前面 Q8/Q11 的时序、门禁边界能完整接上，而且最大优点是**不改变现有 `SPending` 的语义**。

### 锁定的合成链

```text
Phase 4
  │
  ├─ EventProcessor → SPending[69]
  │
  └─ s_env[69] ← 当前情境/环境稳定态
                  │
Phase 1            │
  │                │
  ├─ MoonState → q̂
  ├─ SAN_i → g(SAN_i)
  ├─ R → m_field_i
  │
  ▼
s_total_i = SPending_i + s_env + m_field_i
  │
  ▼
WcDynamics.Step(...)
```

因此：

- `SPending` **继续只承担事件累加**；
- `s_env[69]` 作为 CombatState 的稳定态缓存，design/space/情境刷新时重算；
- Q8 的情境重选在下一回合 Phase 1 才体现；
- `m_field` 每回合重新计算，因为它依赖参与者的 SAN；
- `WcDynamics.Step` **签名不改**。

### 两个重要边界

**① `g` 当前只锁形式，不锁正式数值。**

P2：

```text
g(SAN) ≡ 1.0
```

作为 `CalibrationConfig` 中的 placeholder。

以后 #35 / E7 提供正式 `g(SAN)`，不需要重做三通道架构。

**② q̂ 当前取 `MoonState.Query(D).QhatBaseline`。**

也就是说 P2 暂时：

```text
q̂_j = QhatBaseline[j]
```

不实现：

```text
q̂_{x_i,j}
```

这种空间位置差异，留到后续 graph/spatial calibration。

### 门禁也保持局部化

默认正式路径：

```text
PLACEHOLDER
    ↓
m_field 正式消费
    ↓
CalibrationGate
    ↓
fail-fast
```

但：

```text
s_total = s_event + s_env
```

**完全可以在没有 m_field 的情况下正常运行。**

只有显式 `--mfield-demo` 才允许：

```text
PLACEHOLDER m_field
    ↓
注入
    ↓
每回合醒目警告
```

这与 Q11 的“门禁只挂 m_field 消费点”完全一致。

### Q12 正式定案

> **Q12：选 A。** 三通道在 Phase 1 注入点合成：
>
> `s_total_i = SPending_i + s_env + m_field_i`
>
> 其中 `SPending` 保持现有事件累加语义不变；`s_env[69]` 存储于 `CombatState`，由环境 α_env 与情境原型注入构成，在情境/空间刷新时重算，并按 Q8 于下一回合 Phase 1 生效。
>
> `m_field_i[j] = QhatBaseline[j] × g(SAN_i) × R[j]`，P2 中 `g ≡ 1.0` 作为 `CalibrationConfig` placeholder；q̂ 暂取 `MoonState.Query(D).QhatBaseline`，空间差异 q̂_{x_i} 延迟实现。
>
> 未启用 `--mfield-demo` 时，正式消费 placeholder m_field → `CalibrationGate` fail-fast；启用 demo 时允许占位注入并逐回合警告。
>
> **WcDynamics.Step 签名保持不变；唯一核心引擎改动为 Phase 1 注入前增加三通道合成。**

**Q12 闭合，选 A。**

---

If you want, I can:

- Explain how Phase 1 injection affects the system in simple terms
- Outline next development steps for implementing full g(SAN) and spatial q̂
- Describe risks and safety checks for enabling --mfield-demo mode
