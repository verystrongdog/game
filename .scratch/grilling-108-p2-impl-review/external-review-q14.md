# 外部 AI 评审 — Q14 Console demo 形态

> 来源: ChatGPT 分享页 t_6a9454fed7dc819199ca5aa4c869cc84（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取 4 条消息。

---

## [165]

请给出关于剩余的 Q15 测试矩阵开放点的详细计划，包括测试目标、设计思路、参数选择及如何保证覆盖全面。

## [181]

请详细阐述为什么选择使用专属非交互 --demo-situation trace 模式而不是将演示逻辑直接集成到 RunBattle 中，有哪些风险和收益？

## [186]

请详细说明如何具体使用 --demo-situation 模式进行非交互战斗模拟，包括启动命令、参数配置示例，以及如何观察输出内容的变化。

## [194]

**Q14 定案：选 A。** ✅

我会采纳 **专属非交互 `--demo-situation` trace 模式**，而不是把展示逻辑塞进 `RunBattle`。

理由很明确：

- **直接对应 #105 验收目标**：情境、λ(D)、s 注入以及 `a(t)` 变化都能在一次确定性运行中观察。
- **不污染真实战斗入口**：`RunBattle` 继续保持现有交互语义，降低回归风险。
- **与 `RunResting` 的 trace 模式惯例一致**：非交互、可复现、适合自动化测试。
- **`--seed` 继续作为唯一 RNG 来源**，保证同 seed → 同选择 → 同输出。
- `--env`、`--day`、`--rounds`、`--mfield-demo` 的职责也清晰，不需要再创造另一套 demo 配置机制。

### Q14 最终锁定

```text
--demo-situation
  --env <id>          环境 ID，默认 ward
  --day <n>           固定游戏日 D
  --rounds <n>        trace 回合数
  --seed <n>          RNG seed
  --mfield-demo       显式允许 PLACEHOLDER m_field
```

并锁定：

1. `CombatState.Create(environment)` 增加环境参数；普通 Battle 默认 `ward`。
2. 非法环境 ID → `CliUsageException` → stderr + exit 1。
3. demo 输出：
   - 初始环境 / 情境原型 / strength；
   - 每回合 `λ(D)`；
   - WC `a(t)` 摘要；
   - 首回合展示 s_env 注入前后对比；
   - `--mfield-demo` 时明确输出 PLACEHOLDER 警告。
4. 不修改 `WcDynamics.Step` 签名。
5. 不把 demo 特殊逻辑反向污染正式 Battle 路径。
6. 同一 `--seed` 下输出必须确定性一致。

**因此 Q14 = A，闭合。**  
B5 还剩最后一个开放点：**Q15 测试矩阵**。

---

If you want, I can:

- Explain how the --demo-situation mode works in practice
- Describe the rationale behind separating demo logic from RunBattle
- Outline next steps to finalize Q15 测试矩阵
