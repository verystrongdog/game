#!/usr/bin/env python3
"""
从演化出的 CTRNN 权重中提取认知公式

思路: 演化后的权重矩阵不是黑箱——每个认知功能对应权重空间中
可识别的结构模式。提取这些模式 = 得到认知能力的数学公式。
"""

import math, sys
import sim_evo_ctrnn_l3 as l3

random = l3.random
random.seed(3)

def sig(x): return 1.0/(1.0+math.exp(-x))

# ═══════════════════════ 加载最佳脑 ═══════════════════════

print("演化中...")
best, pop, history = l3.evolve(pop_size=40, generations=100, mut_step=0.05, n_neurons=14)
b = best.brain

print(f"\n{'='*60}")
print(f"  公式提取 — 从权重矩阵反推认知结构")
print(f"{'='*60}")

# ═══════════════════════ 基础参数 ═══════════════════════

taus = sorted(b.tau)
print(f"\n  τ 分布: {[f'{t:.1f}' for t in taus]}")
print(f"  τ 分离度: {max(taus)-min(taus):.1f}")

# 按 τ 分组
fast = [i for i in range(b.N) if b.tau[i] < 2.5]    # τ < 2.5: 反射
mid  = [i for i in range(b.N) if 2.5 <= b.tau[i] < 7.0]  # 中等
slow = [i for i in range(b.N) if b.tau[i] >= 7.0]   # τ >= 7: 记忆

print(f"  快神经元(τ<2.5): {len(fast)}个 — 反射通道")
print(f"  中神经元(2.5≤τ<7): {len(mid)}个 — 加工通道")
print(f"  慢神经元(τ≥7): {len(slow)}个 — 记忆通道")

# ═══════════════════════ C₂ 辨别公式 ═══════════════════════

print(f"\n{'─'*60}")
print(f"  C₂ 辨别: 感觉通道分化")
print(f"{'─'*60}")

snames = ['信号','食物','威胁','杠杆','时间']
channels = {}
for s in range(b.S):
    # 每种感觉的"专属神经元组"
    dedicated = sorted(range(b.N), key=lambda i: -abs(b.w_in[i][s]))
    top3 = dedicated[:3]
    channels[s] = top3
    print(f"  {snames[s]}: 主响应神经元 = {[f'N{i}(τ={b.tau[i]:.1f},w={b.w_in[i][s]:+.1f})' for i in top3]}")

# 公式: 每种感觉 s 在神经元群上的投射
print(f"\n  → 辨别公式:")
print(f"     h_s[i] = w_in[i][s] · sensory[s]")
print(f"     每个感觉通道 s 激活不同的神经元子集")
print(f"     通道 A ≠ 通道 B ⇔ corr(w_in[:][A], w_in[:][B]) 低")

# 计算通道间的权重相关性
for s1 in range(b.S):
    for s2 in range(s1+1, b.S):
        w1 = [b.w_in[i][s1] for i in range(b.N)]
        w2 = [b.w_in[i][s2] for i in range(b.N)]
        corr = sum(a*b for a,b in zip(w1,w2)) / (math.sqrt(sum(a*a for a in w1))*math.sqrt(sum(b*b for b in w2))+1e-9)
        if abs(corr) < 0.5:
            print(f"     ✓ {snames[s1]} ⊥ {snames[s2]}: corr={corr:.2f} (正交=通道独立)")

# ═══════════════════════ C₃ 记忆公式 ═══════════════════════

print(f"\n{'─'*60}")
print(f"  C₃ 记忆: 慢神经元的主动维持")
print(f"{'─'*60}")

# 分析最慢神经元的自反馈
slowest = max(range(b.N), key=lambda i: b.tau[i])
w_self = b.w[slowest][slowest]
print(f"  最慢神经元 N{slowest} (τ={b.tau[slowest]:.1f}):")
print(f"     自反馈权重 w[{slowest}][{slowest}] = {w_self:+.2f}")

# 遍历所有慢神经元，看自反馈符号
print(f"\n  慢神经元(τ≥7)自反馈分析:")
for i in slow:
    w_self_i = b.w[i][i]
    sign = "正反馈→主动维持" if w_self_i > 0 else "负反馈→自稳"
    print(f"     N{i} (τ={b.tau[i]:.1f}): w_self={w_self_i:+.2f} → {sign}")

# 公式
print(f"\n  → 记忆公式 (单个慢神经元):")
print(f"     τ_s · dy_s/dt = -y_s + w_self · σ(y_s + θ_s) + I_s(t)")
print(f"     当 w_self > 0 且 τ_s 大:")
print(f"       - 信号 I_s 触发激活")
print(f"       - 自反馈 w_self·σ(y_s) 维持激活")
print(f"       - 大 τ_s 使衰减极慢")
print(f"     结果: y_s(t) ≈ y_s(0) + ∫₀ᵗ (I_s(τ)/τ_s) dτ  (近似积分器)")

# ═══════════════════════ C₄ 关联公式 ═══════════════════════

print(f"\n{'─'*60}")
print(f"  C₄ 关联: 信号→慢神经元→运动输出的延迟桥接")
print(f"{'─'*60}")

# 找信号→慢神经元→运动输出的通路
print(f"  信号→慢神经元→运动 通路分析:")
for i in slow:
    w_sig = b.w_in[i][0]  # 信号输入权重
    w_out0 = b.w_out[0][i]  # 转向输出
    w_out1 = b.w_out[1][i]  # 速度输出
    if abs(w_sig) > 2.0:
        print(f"    信号 → N{i}(τ={b.tau[i]:.1f}) [w={w_sig:+.1f}]")
        print(f"      → 转向={w_out0:+.2f}, 速度={w_out1:+.2f}")

# 关键: 找到信号敏感且速度输出为正的慢神经元
for i in slow:
    if abs(b.w_in[i][0]) > 2.0 and b.w_out[1][i] > 0.5:
        print(f"\n  → 关联通路: 信号 → N{i}(τ={b.tau[i]:.1f}) → 速度+{b.w_out[1][i]:.1f}")
        print(f"     物理含义: 信号激活慢神经元 → 慢神经元持续激活 → 持续趋近行为")
        print(f"     即使信号消失, 慢神经元激活仍在 → 行为持续")

print(f"\n  → 关联公式:")
print(f"     dy_slow/dt = (-y_slow + w_sig·sensory[sig] + ...)/τ_slow")
print(f"     speed = σ(Σ w_out[1][i] · σ(y_i + θ_i))")
print(f"     当 τ_slow 大: y_slow(t) ≈ 信号的历史积分")
print(f"     → speed 在信号消失后仍维持 → '信号预测食物'的行为表现")

# ═══════════════════════ C₅ 后果学习公式 ═══════════════════════

print(f"\n{'─'*60}")
print(f"  C₅ 后果学习: 杠杆传感器→食物预期的绑定")
print(f"{'─'*60}")

# 杠杆传感器 (index 3) 驱动哪些神经元
lever_neurons = [(i, b.w_in[i][3]) for i in range(b.N) if abs(b.w_in[i][3]) > 2.0]
print(f"  杠杆响应神经元:")
for i, w in sorted(lever_neurons, key=lambda x: -abs(x[1])):
    w_food = b.w_in[i][1]
    w_speed = b.w_out[1][i]
    print(f"    N{i}(τ={b.tau[i]:.1f}): lever_w={w:+.1f} food_w={w_food:+.1f} →speed={w_speed:+.1f}")

print(f"\n  → 后果公式:")
print(f"     h_lever[i] = w_in[i][lever] · lever_sense")
print(f"     h_food[i]  = w_in[i][food] · food_sense")
print(f"     当 lever_sense 和 food_sense 反复共现:")
print(f"       → 演化使 w_out 将 lever 响应神经元连接到正速度输出")
print(f"       → agent 学会'去杠杆处 → 有食物'")

# ═══════════════════════ C₇ 情景记忆公式 ═══════════════════════

print(f"\n{'─'*60}")
print(f"  C₇ 情景记忆: 信号×时间的交互门控")
print(f"{'─'*60}")

# 关键: 找同时有信号权重和时间权重的神经元
sig_time = [(i, b.w_in[i][0], b.w_in[i][4])
            for i in range(b.N)
            if abs(b.w_in[i][0]) > 1.5 and abs(b.w_in[i][4]) > 1.5]

print(f"  信号×时间 交互神经元 ({len(sig_time)}个):")
for i, sw, tw in sorted(sig_time, key=lambda x: -abs(x[1]*x[2])):
    tau_i = b.tau[i]
    w_speed = b.w_out[1][i]
    same_sign = (sw > 0) == (tw > 0)
    gate_type = "AND(同号→增强)" if same_sign else "XOR(异号→门控)"
    print(f"    N{i}(τ={tau_i:.1f}): sig={sw:+.1f} time={tw:+.1f} {gate_type} →speed={w_speed:+.1f}")

# 分析门控逻辑
print(f"\n  → 情景记忆公式:")
print(f"     对每个交互神经元 i:")
print(f"       h_i = w_in[i][sig]·signal + w_in[i][time]·time_context")
print(f"     在 σ(h_i + θ_i) 中:")
print(f"       - 同号(sig,time): h_i 在涨潮时被放大 → 强趋近")
print(f"       - 异号(sig,time): h_i 在退潮时被抵消 → 抑制趋近")
print(f"     结果: 同一信号, 不同时间 → 不同行为输出")

# 具体算一个例子
if sig_time:
    ex = sig_time[0]
    i, sw, tw = ex
    print(f"\n  具体例子 (N{i}):")
    print(f"    涨潮(time=0): h_i = {sw:+.1f}·sig + {tw:+.1f}·0 = {sw:+.1f}·sig")
    print(f"    退潮(time=1): h_i = {sw:+.1f}·sig + {tw:+.1f}·1 = {sw:+.1f}·sig{tw:+.1f}")
    if (sw > 0) != (tw > 0):
        print(f"    → 退潮时信号效应被削弱: 异号门控实现情景敏感")

# ═══════════════════════ 统一公式 ═══════════════════════

print(f"\n{'='*60}")
print(f"  统一认知动力系统")
print(f"{'='*60}")

print(f"""
  单神经元动力学:
    τᵢ · ẏᵢ = -yᵢ + Σⱼ wⱼᵢ · σ(yⱼ + θⱼ) + Σₛ w_in[i][s] · Sₛ

  运动输出:
    Mₘ = Σᵢ w_out[m][i] · σ(yᵢ + θᵢ)

  参数 → 认知功能 映射:
    τᵢ < 2.5                  → 反射通道 (快速响应, 无记忆)
    2.5 ≤ τᵢ < 7              → 加工通道 (中等时程)
    τᵢ ≥ 7                    → 记忆通道 (慢积分, 持久激活)
    w_self > 0 且 τ 大        → 主动维持 (工作记忆)
    w_in[:][A] ⊥ w_in[:][B]   → 辨别 (通道独立)
    w[slow][motor] · w_in[slow][sig] ≠ 0  → 关联 (信号→运动延迟桥接)
    w_in[i][sig]·w_in[i][ctx] ≠ 0 → 情景门控 (上下文调制信号响应)

  游戏设计不用演化——直接用这些规则设定 NPC 的 τ/w 参数:
    NPC 的认知风格 = {τ_distribution, w_in_sparsity, w_self_sign}
""")

print("=" * 60)
print("提取完毕")
