# 外部 AI 评审 — Q8 刷新时机挂钩点

> 来源: ChatGPT 分享页 t_6a944c7d02c081918f852b9e668867ed（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复。

---

**Q8 定案：选 A — 事件流驱动 + 下一回合生效。**

这和现有 `C1` 的事件语义、`SPending` 的回合边界以及 #75 D2 的“空间切换 + C1 事件”刷新契约能够完整对齐。

### 锁定的时序

```text id="4r7q1m"
本回合
  │
  ├─ EventProcessor 检测到 C1 Entered
  │
  ├─ TurnManager 事件窗口触发 SituationSelector.Select(...)
  │
  ├─ 得到新 situation + strength
  │
  └─ 标记为下一回合使用
          │
          ▼
下一回合 Phase 1
  └─ 新 situation contribution 生效
```

核心原则是：

> **事件在本回合发生，本回合仍按旧情境完成结算；新情境从下一回合开始注入。**

这样不会出现一个事件窗口中途切换情境，导致同一回合前后部分使用不同情境的情况。

### 三条连带契约全部采纳

**① Panic 消退不触发重选。**

C1 只有 `Entered=true` 的 crossing 行，因此没有 `Exited` 重选路径。

所以：

```text id="r0t5cz"
panic Entered
    → 重选

panic Exited
    → 不重选
    → 当前 situation 保持
```

当前 situation 一直保持到**下一次空间切换或下一次 C1 Entered**。

---

**② 初始情境在 `CombatState.Create` 确定。**

创建 CombatState 时，根据：

```text id="w3x9ea"
environment.primary
        +
initial panic state
        ↓
初始 situation + strength
```

确定初始情境。

因此不会出现“CombatState 创建后先没有 situation，等第一回合才补”的隐式状态。

---

**③ 重选机制保持纯函数，触发机制放在 TurnManager。**

保持：

```text id="3g6x2p"
SituationSelector.Select(env, panic, rng)
```

负责**选择**。

TurnManager 负责**什么时候调用**。

这样 SituationSelector 不需要知道回合、事件窗口或 Phase 状态，也不需要被改造成状态机。

### Q8 正式记录

> **Q8（B2-⑧）：A。C1 情境重选采用事件流驱动：TurnManager 事件窗口检测 `StatusChangeEvent(Panic, Entered=true)` 后调用 `SituationSelector.Select(env, panic, rng)`。重选结果从下一回合开始生效；触发 C1 的本回合继续使用旧情境完成结算。**
>
> Panic 消退（`Entered=false`）不触发情境重选，当前情境保持至下一次空间切换或下一次 C1 Entered。CombatState.Create 时依据环境 primary 与初始存在性恐慌状态确定初始情境。SituationSelector 保持无状态选择函数，TurnManager 仅增加事件窗口 hook，不引入情境状态机。

**Q8 闭合。**

至此 **B2（SituationSelector）的 Q4–Q8 已经全部锁死**。其中 Q8 也把一个很容易在实现阶段产生歧义的问题——“C1 到底什么时候改变 `s_total`”——明确落到了**下一回合边界**。

---

If you want, I can:

- Explain how Q8 integrates with previous SituationSelector decisions Q4–Q7
- Describe a sample sequence illustrating the event flow and situation update timing
- Suggest potential implementation considerations or challenges for Q8 approach
