# 外部 AI 评审 — Q15 测试矩阵 + B1-B5 闭合

> 来源: ChatGPT 分享页 t_6a945571aa48819195bf6ba458bc0518（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取 3 条消息。

---

## [184]

请详细阐述如何验证panic选择机制中的概率语义与确定性RNG契约的符合性，解释验证方法和可能的陷阱。

## [189]

请继续详细描述如何将Q1–Q15的最终决策统一写入决策树、六维状态及相应的task-plan/spec中，包括具体方法和注意事项。

## [197]

确认 **Q15 = 采纳**。✅

而且这一题的核心边界我赞成锁死：**`p_panic = 0.5` 是行为契约，不在 #108 用频率统计去证明概率值。** 没有预注册样本量和统计检验设计，就不应该临时制造一个“跑 1000 次，接近 50% 就算通过”的验收标准。

### Q15 最终锁定

**G1–G9 全部纳入测试矩阵：**

- **G1** 数据契约 fail-fast：三类 JSON 的 schema、字段、长度、范围、PLACEHOLDER、缺失字段等。
- **G2** 迁移回归：W_sensory 原 6 列逐位保持；现有 **309 测试全绿**作为 P2 回归门槛。
- **G3** EventProcessor：JSON 驱动后现有派生行为逐位一致，并锁 A1 正例。
- **G4** SituationSelector：环境映射、panic/非-panic、固定 seed、G 构造、primary∈G、C1 下一回合生效。
- **G5** MoonState：λ 边界/连续性、纯函数性、运行时防御断言。
- **G6** CalibrationGate：PLACEHOLDER / CALIBRATED / version mismatch / demo override。
- **G7** 三通道合成：  
  `s_total = SPending + s_env + m_field`
  以及刷新、生效时序、SAN 驱动和 `Step` 签名不变。
- **G8** fid 校验：管线 37 名 100% 命中 + 非零失败 + 新原型自动纳入；引擎侧再次 fail-fast。
- **G9** Console：`--demo-situation` 输出契约、PLACEHOLDER 警告、非法 env、同 seed 可复现。

### `p_panic` 测试契约

锁定为：

```text
panic = false → 必须选择 primary

panic = true → 必须选择 G 或 primary

同 seed + 同输入 → 选择结果必须一致
```

不做：

```text
重复运行 n 次 → 统计约 50%
```

因为这里验收的是**选择机制是否符合已锁定的概率语义与确定性 RNG 契约**，不是 #108 的校准实验。

### B1–B5 状态

因此现在可以正式认为：

**B1 数据层：闭合**  
**B2 SituationSelector：闭合**  
**B3 m_field 通道：闭合**  
**B4 fid 校验器：闭合**  
**B5 Console + 测试：闭合**

也就是说，#108 的 **15 个实施层开放点 Q1–Q15 已全部定案**。

下一步进入 **Step 4：把 Q1–Q15 的最终决策统一写入决策树、六维状态和 #108 task-plan/spec 的相应位置**。这里要特别遵守你前面已经锁定的纪律：**现在才正式落盘，不提前把半成品决策写进规范。**

---

If you want, I can:

- 继续详细描述Q15决策树落盘步骤
- 阐述如何验证panic选择机制的契约一致性
- 介绍如何维护测试矩阵G1–G9的长效闭合性
