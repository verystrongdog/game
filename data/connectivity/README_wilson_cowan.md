# Wilson-Cowan (1972) Neural Population Dynamics

> 来源: riv20/wilson-cowan-1973 (GitHub) — Python 复现
> 论文: Wilson & Cowan (1972) Biophysical Journal 12, 1-24

## 核心方程

兴奋性(E)和抑制性(I)神经群体的耦合动力学：

```
μ · dE/dt = -E + (1 - r_E·E) · F_E · S_E(ρ_E·β_EE*E - ρ_I·β_IE*I + P)
μ · dI/dt = -I + (1 - r_I·I) · F_I · S_I(ρ_E·β_EI*E - ρ_I·β_II*I + Q)
```

### 参数含义

| 参数 | 含义 | 典型值 |
|------|------|--------|
| μ | 膜时间常数 | 10 ms |
| r_E, r_I | 绝对不应期 | 1 ms |
| F_E, F_I | 最大发放率 | 1 kHz |
| ρ | 连接密度 | 1 μm⁻¹ |
| P, Q | 外部输入 | 可变 |

### Sigmoid 响应函数

```
S(x) = 1/(1 + exp(-v·(x-θ))) - 1/(1 + exp(v·θ))
```

### 空间耦合核

```
β(x) = b · exp(-|x|/σ)
```

## 简化形式（空间均匀）

```
Tu · du/dt = -u + f(μ · (a·u - b·v + Su))
Tv · dv/dt = -v + f(μ · (c·u - d·v + Sv))
```

其中 u = E群体, v = I群体, f = sigmoid/tanh, a/b/c/d 为耦合强度。

## 关键动力学特性

1. **双稳态 (bistability)**：足够强的自兴奋 (a 大) + 侧抑制 (b 大) → 两个稳定不动点
2. **极限环振荡**：E-I 耦合在一定参数范围内产生持续振荡
3. **滞后 (hysteresis)**：刺激强度扫描方向不同 → 不同响应曲线

## 游戏应用要点

1. **每个 functional_id 的激活 a 可用 WC 简化形式**：τ·da/dt = -a + f(输入)
2. **E-I 平衡 = 节点的兴奋/抑制平衡**，决定节点是信号传递还是过滤
3. **双稳态 = 脑区的"锁存"行为**，可用于建模持续注意/工作记忆
4. **时间常数 τ 应按层级梯度变化**：L0 快 (~10ms), L5 慢 (~150ms)
