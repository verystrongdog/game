Title: 看看这段聊天

URL Source: https://chatgpt.com/s/t_6a950e055ad48191af18928a592bacb5

Published Time: 2026-08-31T05:15:49.354Z

Markdown Content:
This is a copy of a shared ChatGPT chat. It won't be added to memory.

#### ChatGPT said:

我定 **(a) `YANTF_DATA_DIR` 环境变量**。

而且你这次对外审两处归因的纠正是成立的：**Q5 契约本身不需要修正**，现在是在 #107 实施层补齐它所依赖的可测试性入口，并强化防假阳性。

### Q4 定案：A — `YANTF_DATA_DIR`

理由按优先级：

1.   **完全保持 #107 的边界**

    *   不改 CLI。

    *   不改公开 spec / AC-12。

    *   不增加用户可见参数。

    *   不扩大产品 API。

2.   **生产行为零变化**

 推荐实现语义：

```
YANTF_DATA_DIR 已设置
    → 使用该目录
YANTF_DATA_DIR 未设置
    → 完全走现有 FindDataDir()
```

因此不是修改既有生产发现策略，而是增加一个**显式测试覆盖入口**。

3.   **特别适合当前 #107 的“小改动 + main 直改”形态**

CLI 方案虽然更漂亮，但它解决的是一个更大的产品问题：

> “用户是否应该能够显式指定 data directory？”

这不是 #107 要解决的问题。

`YANTF_DATA_DIR` 只解决：

> “Console 回归测试能否可靠控制输入数据？”

**刚好够用，不多做。**

4.   **Q5 的防假阳性断言保留**

Console fixture：

```
brain_regions.json       ← 真实合法
tripartite_model.json    ← 缺 role
```

然后：

```
YANTF_DATA_DIR=<fixture>
↓
Console
↓
tripartite_model.json
↓
[JsonRequired] 触发 JsonException
↓
stderr 含「数据校验失败」
stderr 不含「数据目录缺失」
exit 1
```

这里我也采纳你的修正：**Q5 用“缺 role”，而不是 `role: null`**。

这样三层职责非常干净：

| 层 | 测试输入 | 证明什么 |
| --- | --- | --- |
| #106 Q1 | `role: null` | converter 兜底路径确实抛 `JsonException` |
| #106 Q3 | `role: null` 等 | 引擎级非法输入行为 |
| #107 Console | **缺 `role`** | `[JsonRequired]` → Console fail-fast 端到端链路 | 

### 最终锁定

> **Q4：选择 (a) `YANTF_DATA_DIR`。**
> 
> 
> Console 回归通过环境变量显式注入临时 fixture；未设置环境变量时 `FindDataDir()` 行为完全保持不变。Q5 契约不修改，只在实施层增加可控输入边界，并增加“stderr 含 `数据校验失败` 且不含 `数据目录缺失`”的防假阳性断言。Console fixture 使用**缺失 `role`**，对应 #92 事故原貌。

这个方案比 `--data-dir` 更适合当前 #107：**把测试缺口补上，但不借机把测试后门升级成产品功能。**

* * *

If you want, I can:

*   继续详细说明如何使用YANTF_DATA_DIR进行测试的具体步骤

*   展开阐述#107实施层如何补齐可测试性入口的设计细节

*   说明Q5契约保持不变但新增防假阳性断言的技术意义及实现
