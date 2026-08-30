# 外部 AI 评审 — Q6 诡异/负面分组规则 + p_panic 语义

> 来源: ChatGPT 分享页 t_6a94432e93188191886ce00ed41f687f（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复。

---

**Q6 定案：A + 采纳你给出的 `p_panic` 语义。**

这题我认为可以直接锁死，不需要为了“诡异”二字再提前制造 27 条人工标注。

### 1. 分组规则：选 A

锁定：

```text
G = {
    prototype |
    negative_valence >= 0.2
    AND
    appraisal_profile.valence == negative
}
```

并且：

- **构造期计算**，不把 G 再复制一份到 `env_tones.json`；
- `t_neg = 0.2` 是本批规则参数，而不是 27 条硬编码成员名单；
- 当前 G 明确属于**可运行的近似组**，不是声称它等价于心理学意义上的“uncanny”；
- 后续内容填充阶段可以通过调整阈值或增加排除规则精化，不需要因此修改 P2 的 selector 架构；
- G 必须非空且所有成员都来自现有 27 个 prototype，由校验器断言。

这样既满足 #75 “本批提供分组规则、标注随内容填充”，又没有偷偷把内容生产提前塞进实施阶段。

### 2. `p_panic`：按你给出的概率契约锁定

存在性恐慌条件为真、发生重选时：

```text
P(选择 G 中随机 prototype) = 0.5
P(选择 environment.primary) = 0.5
```

也就是：

```text
p_panic = 0.5
```

恐慌条件为假：

```text
situation = environment.primary
```

而 G 内部：

> **均匀随机选择，不引入额外权重。**

随机源继续采用注入 RNG，因此同一 seed + 同一输入 → 同一选择。

### 3. 一个我建议同时锁死的小边界

**G 不需要排除 `primary`。**

也就是说，如果某个环境的 `situation.primary` 恰好也属于 G，那么它仍然是合法的 G 成员，不额外增加一条“G 与 primary 必须不相交”的隐含规则。

这样最符合目前的最小契约：**G 是按原型属性构造的全局集合，primary 是环境映射，两者没有被定义为互斥集合。**

此时一次 panic 重选虽然理论上可能两条路径都得到同一个 prototype，但这是当前规则的自然结果，不应偷偷引入第三套去重/排除逻辑。

### Q6 正式记录

> **Q6（B2-⑥）：A；`p_panic` 语义确认。**
>
> 诡异/负面候选组 `G` 由 27 个情境原型在 `SituationSelector` 构造期计算：
>
> `negative_valence >= 0.2 AND appraisal_profile.valence == negative`。
>
> `G` 不复制进 `env_tones.json`；当前规则产生的是可运行的近似组，后续可在内容填充阶段通过阈值调整/排除规则精化。校验器断言 `G` 非空且所有成员属于 27 个已注册 prototype。
>
> 存在性恐慌条件为真且发生重选时，以 `p_panic = 0.5` 决定：50% 选择 `G` 中均匀随机的一个 prototype，50% 选择当前环境 `situation.primary`；恐慌条件为假时确定性选择 `primary`。组内选择使用注入 RNG，保证同 seed 同选择。
>
> `G` 与 `primary` 不要求互斥；若 `primary ∈ G`，允许两条概率路径最终产生相同 prototype，不增加额外排除逻辑。

**Q6 闭合。**

这样 B2 现在已经把“正常环境指向谁”和“存在性恐慌怎么偏移”都变成了可直接实现的确定性契约。

---

If you want, I can:

- Expand on how to implement 'p_panic' logic in code
- Describe how to tune thresholds for refining group G during content filling
- Clarify consequences and edge cases of allowing primary to be in group G
