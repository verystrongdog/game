# Gurney-Prescott-Redgrave (2001) Basal Ganglia Action Selection Model

> 来源: ModelDBRepository/83560 (GitHub) — MATLAB 实现
> 论文: Gurney, Prescott & Redgrave (2001) Biological Cybernetics 84, 401-423

## 核心架构

每个动作通道有 5 个神经群体：
1. **SD1** (Striatum D1) — GO/直接通路
2. **SD2** (Striatum D2) — NO-GO/间接通路
3. **STN** (Subthalamic Nucleus) — STOP/超直接通路
4. **GPe** (Globus Pallidus external)
5. **GPi** (Globus Pallidus internal) — 输出门（tonic 抑制丘脑）

## 动力学方程

每个单元的激活 `a` 遵循一阶衰减：
```
τ · da/dt = -a + u      (τ = 1/k = 0.04, k=25)
```

离散形式（零阶保持法）：
```
a(t+dt) = (a(t) - u) · exp(-k·dt) + u
```

### 逐单元输入 u

| 单元 | 输入公式 |
|------|---------|
| SD1 | u = c · W_SEL · (1 + DA_sel) |
| SD2 | u = c · W_CONT · (1 - DA_cont) |
| STN | u = c · W_STN + O(GPe) · W_GPe_STN |
| GPe | u = ΣO(STN)·W_STN_GPe + O(SD2)·W_CONT_GPe + O(SD1)·W_SEL_GPe + (ΣO(GPe)-self)·W_GPe_GPe |
| GPi | u = ΣO(STN)·W_STN_GPi + O(GPe)·W_GPe_GPi + O(SD1)·W_SEL_GPi + (ΣO(GPi)-self)·W_GPi_GPi |

### 输出函数（分段线性 ramp）

```
output(a) = 0              if a < e
          = m · (a - e)    if e ≤ a ≤ 1/m + e
          = 1              if a > 1/m + e
```

### DA 调制（Humphries 2003）

- **D1 (GO)**: m = m_base + gain · DA → DA 升高增强 GO
- **D2 (NO-GO)**: m = m_base - gain · DA → DA 升高抑制 NO-GO

### 连接权重

```
W_SEL = 1       (皮层→SD1)
W_CONT = 1      (皮层→SD2)
W_STN = 1       (皮层→STN)
W_SEL_GPi = -1  (SD1→GPi, GO通路)
W_SEL_GPe = 0   (SD1→GPe, 默认无连接; 'g' 选项 -0.25)
W_CONT_GPe = -1 (SD2→GPe)
W_STN_GPi = 0.9 (STN→GPi, STOP)
W_STN_GPe = 0.9 (STN→GPe)
W_GPe_STN = -1  (GPe→STN)
W_GPe_GPi = -0.3 (GPe→GPi)
```

### 选择判定

GPi 输出 < θ → 该通道的 tonic 抑制被解除 → 行动被选中
- default: θ = 0 (软选择, 可多选)
- hard: 仅最低 GPi 的通道胜出
- gate: 选通比例 (θ - output)/θ

## 游戏应用要点

1. **salience c 对应链路/技能的"当前需求强度"**
2. **DA 水平对应脑干 VTA/SNc 广播的 DA tone**
3. **GPi 输出 = CSTC 门控结果** — 直接决定行动是否被释放
4. **STN 超直接通路比 GO/NO-GO 快** — 可以建模"紧急刹车"机制
