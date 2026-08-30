# 外部 AI 评审 — Q11 门禁机制

> 来源: ChatGPT 分享页 t_6a945196b9688191b2b30f025f171a3f（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复。

---

Q11 我建议**选 A**，并且连带契约 3 明确裁决为：**s_env / SituationSelector 不挂 `CalibrationGate`**。

理由很简单：这里要防的是“**未校准月光数据进入正式 m_field 数值通道**”，而不是把所有 P2 新增数值都一股脑绑到 calibration。

### Q11 定案

**1. 门禁形态：A**

```text
CalibrationGate.EnsureCalibrated(status, version)
```

只挂在：

```text
moonState
   ↓
q̂ × g × R
   ↓
m_field 合成注入点  ← EnsureCalibrated
   ↓
s_total
```

正式消费时：

- `CALIBRATED` → 允许；
- `PLACEHOLDER` → fail-fast；
- calibration version 不满足要求 → fail-fast；
- 不允许静默回退。

这与 #106 的分层正好衔接：底层抛数据/引擎异常，Console 捕获后统一输出错误并 `exit 1`。

---

**2. Demo 例外必须是显式 opt-in**

锁定：

```text
AllowPlaceholderDemo = false   // 默认
```

只有 Console：

```text
--mfield-demo
```

才允许走 placeholder 路径。

而且不是“开了 demo 就什么都不说”，而是**每回合明确警告**：

> PLACEHOLDER 数据，仅原型测试

这样 placeholder 的存在不会伪装成正式校准结果。

---

**3. `s_env` 不挂门禁——这里明确裁决**

我赞成你的解释：

```text
s_total = s_event + s_env + m_field
                  ↑        ↑
             不需要       需要
          CalibrationGate
```

`α_env` 是环境空间基调，情境 prototype injection 是 SituationSelector 的情境通道；二者不消费 `moonlight_landing` 的 calibration artifact。

所以：

> **CalibrationGate 的适用范围是 moonlight → m_field 的正式消费边界，不是整个 `s_total` 汇合点。**

这也保持 #101 已锁定的三通道正交性，不会因为“都有数值”就把 `s_env` 错误地视为月光校准消费方。

---

**4. 三文件 schema major 校验**

Q11 一并锁死：

```text
alpha_patterns
env_tones
moonlight_landing
       ↓
schema major compatibility check
       ↓
major mismatch → fail-fast
minor mismatch → 允许兼容演进
```

字段缺失仍然是 load error，**不能通过补默认值绕过 schema 检查**。

---

**5. `MoonState.Query` 自检**

也采纳：

- `0 ≤ λ ≤ 1`
- `E_c > 0`
- `0 < E_th < E_c`
- 所有结果 finite
- NaN / ±Inf → 异常

这属于**运行时防御性不变量**，不与 #71 的 artifact 六项硬校验混为一谈。

### 最终锁定文本

> **Q11：选 A。** 采用显式 `CalibrationGate.EnsureCalibrated(status, version)`，并将其挂载于 **m_field 正式合成注入点**。未校准或版本不满足要求时 fail-fast，不得静默回退。
>
> P2 demo 例外采用显式 `CalibrationConfig.AllowPlaceholderDemo`，默认 `false`；仅 Console `--mfield-demo` 显式开启，placeholder 注入期间每回合输出醒目警告。
>
> `alpha_patterns`、`env_tones`、`moonlight_landing` 加载时统一校验 schema major；major 不匹配 fail-fast，minor 允许兼容演进。
>
> `MoonState.Query` 对 λ、E_c、E_th 及有限性执行运行时防御断言，违反即抛异常。
>
> **门禁范围明确限定为 moonlight calibration → m_field 的正式消费链路；`s_env`、α_env 与 SituationSelector 情境原型注入不挂 CalibrationGate。** 情境基线 `s_neg` 归 #35，不因其存在而成为 moonlight calibration 消费方。

**Q11 闭合。** A + “s_env 不挂门禁”。

---

If you want, I can:

- Explain the role of CalibrationGate in m_field injection and s_env exclusion
- Summarize key fail-fast conditions and Demo placeholder handling in Q11
- Outline how Q11 decision integrates with schema validation and runtime checks
