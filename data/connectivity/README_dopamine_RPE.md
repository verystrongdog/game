# Schultz, Dayan & Montague (1997) — Dopamine Reward Prediction Error

> 来源: Sabina085/td-error-dopamine (GitHub) — Python 复现
> 论文: Schultz, Dayan & Montague (1997) Science 275, 1593-1599

## 核心方程 — Temporal Difference (TD) Learning

### RPE (Reward Prediction Error) — 多巴胺信号

```
δ(t) = r(t) + γ · V(t+1) - V(t)
```

其中：
- δ(t): 奖赏预测误差（= phasic DA 发放）
- r(t): 实际奖赏（t 时刻）
- γ: 折扣因子 (0-1)
- V(t): 价值估计 = w^T · x(t)（特征权重 × 刺激特征）

### 权重更新

```
w ← w + α · δ · x
```

其中 α 为学习率。

### 关键实验结果（论文复现）

1. **学习前**: DA 神经元对奖赏本身发放（r 驱动）
2. **学习后**: DA 转移到 CS（条件刺激）发放——预测奖赏，奖赏本身不再驱动 DA
3. **奖赏省略**: CS 后无奖赏 → DA 在预期奖赏时刻 **降低到基线以下**（负 RPE）
4. **延迟奖赏**: DA 发放逐步从 CS 转移到更接近奖赏的时刻
5. **早到奖赏**: 提前的奖赏仍触发 DA（正 RPE）

### 游戏应用要点

1. **VTA/SNc → DA 广播 = δ(t)**：战利品掉落/技能成功 → 比预期好 → 正 RPE
2. **负 RPE = 惩罚/失望信号**：预期技能够到但 MISS → DA 下降 → 影响学习
3. **γ 折扣 = 时间偏好**：即时奖赏权重高、延迟奖赏权重低
4. **与 5-HT 的交互**：中缝 5-HT 可能编码时间折扣率（Doya 2002），DA/5-HT 平衡决定冲动性

## 项目中已下载的原始文献

- `Schultz-Dayan-Montague-1997-dopamine-RPE.pdf` — 原始论文（7页, 455KB）
