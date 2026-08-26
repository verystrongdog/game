"""
Layer 2 — Integration Int(S) 单位测试
==================================================
研讨产物（纯学术，不入游戏正典）。

框架 v1.7 系统：S = (B, V_all, {X_i}, Ω, P, μ₀, τ, T_obs)
本脚本实现 Int(S) 并跑三个单位测试（GPT 第八份建议 §15）：

  Π₂(B)     = { {B₁,B₂} : B₁∪B₂=B, 二分 partition }
  P_π^cut   = P(y'_B₁|y_B₁) · P(y'_B₂|y_B₂)    切断后的因子化核
  I_π(S)    = (1/m) Σ_t E_{μ_t}[ KL( P(·|Y_t) ‖ P_π^cut(·|Y_t) ) ]
  Int(S)    = min_{π∈Π₂(B)} I_π(S)

测试：
  A 完全独立：P = P_A·P_B            → Int = 0
  B 弱耦合：  P ≈ P_A·P_B            → Int ≈ 0 但 > 0
  C 真不可分解：无法被二分近似        → Int > 0 且明显高

简化（第一版）：元件二值（X_i = {0,1}），全活动（A_i ≡ 1，无活动变量），
确定性转移（P(y'|y) = δ_{F(y)}）。cut 的"块间解耦"用对块外当前状态
均匀平均实现。
"""

import itertools
import math
from collections import Counter

EPS = 1e-12


# ============================================================
# §1 框架 v1.7 最小实现（确定性特例）
# ============================================================

def all_states(n):
    """n 元件二值 → 全部状态 {0,…,2^n-1}。"""
    return list(range(1 << n))


def state_tuple(s, n):
    """状态整数 → 元件位元组。位 i = 元件 i。"""
    return tuple((s >> i) & 1 for i in range(n))


def state_index(t):
    """元件位元组 → 状态整数。"""
    return sum(t[i] << i for i in range(len(t)))


def block_of(s, n, block):
    """状态 s 在 block（元件子集）上的投影 → 块状态整数。"""
    t = state_tuple(s, n)
    return state_index(tuple(t[i] for i in sorted(block)))


def full_transition_matrix(F, n):
    """确定性 F → 行随机矩阵 P（P[y'][y] = 1 若 y'=F(y)）。"""
    P = {}
    for y in all_states(n):
        row = [0.0] * (1 << n)
        row[F(y)] = 1.0
        P[y] = row
    return P


def block_projection(P, n, block, other_blocks):
    """P(y'_block | y_block)：对块外当前状态均匀平均后，块未来的边际分布。

    P̂(y'_B | y_B) = (1/|Ω_Ḃ|) Σ_{y_Ḃ} Σ_{y'_Ḃ} P(y'_B, y'_Ḃ | y_B, y_Ḃ)
    其中 Ḃ = 系统内除 B 外的所有元件（other_blocks 的全部元件）。
    """
    block = set(block)
    others = set(range(n)) - block
    # 所有块外状态
    other_states = all_states(len(others))
    # 对每个 y_B，构造分布
    result = {}
    n_others = len(other_states)
    # 遍历所有 y_B（块状态空间的每个值）
    # 块状态空间大小 = 2^|block|
    for yb in all_states(len(block)):
        dist = [0.0] * (1 << len(block))
        # 对每个 y_Ḃ 均匀平均
        for yo in other_states:
            # 组装完整 y = (y_B, y_Ḃ)——注意位序：block 元件与 others 元件在原始状态中的位置
            full_t = [0] * n
            bl_sorted = sorted(block)
            # yb 的位 j 对应 bl_sorted[j]
            for j, idx in enumerate(bl_sorted):
                full_t[idx] = (yb >> j) & 1
            for j, idx in enumerate(sorted(others)):
                full_t[idx] = (yo >> j) & 1
            y = state_index(tuple(full_t))
            # 边际化 y'_Ḃ：P(y'_B | y) 对 y'_Ḃ 求和
            for yf in all_states(n):
                yf_t = state_tuple(yf, n)
                yf_b = state_index(tuple(yf_t[i] for i in bl_sorted))
                # P(yf | y) 是 delta（确定性）或一般概率
                p = P[y][yf]
                dist[yf_b] += p
        # 除以块外状态数（均匀平均）
        dist = [d / n_others for d in dist]
        result[yb] = dist
    return result


def cut_kernel(P, n, B1, B2):
    """P_cut(y'|y) = P̂(y'_B₁|y_B₁) · P̂(y'_B₂|y_B₂)。

    B1 ∪ B2 = 全系统（本脚本系统内全部元件参与）。
    """
    proj1 = block_projection(P, n, B1, [B2])
    proj2 = block_projection(P, n, B2, [B1])
    Pcut = {}
    bl1 = sorted(B1)
    bl2 = sorted(B2)
    for y in all_states(n):
        y_t = state_tuple(y, n)
        yb1 = state_index(tuple(y_t[i] for i in bl1))
        yb2 = state_index(tuple(y_t[i] for i in bl2))
        row = [0.0] * (1 << n)
        for yf in all_states(n):
            yf_t = state_tuple(yf, n)
            yf_b1 = state_index(tuple(yf_t[i] for i in bl1))
            yf_b2 = state_index(tuple(yf_t[i] for i in bl2))
            row[yf] = proj1[yb1][yf_b1] * proj2[yb2][yf_b2]
        Pcut[y] = row
    return Pcut


def kl_row(P_row, Q_row):
    """KL(P_row ‖ Q_row)，P_row 是概率向量。"""
    total = 0.0
    for p, q in zip(P_row, Q_row):
        if p > EPS:
            total += p * math.log(p / max(q, EPS))
    return total


def integration_min(P, n, mu=None):
    """Int(S) = min_{π∈Π₂} I_π，I_π = E_μ[ KL(P(·|y) ‖ P_cut(·|y)) ]。

    简化：μ = 均匀分布（第一版；时间平均后续再加）。
    """
    if mu is None:
        mu = {y: 1.0 / (1 << n) for y in all_states(n)}
    best = float("inf")
    best_pi = None
    # 所有二分：B1 为 {0..n-1} 的非空真子集（去重：B1 与补集同）
    for r in range(1, 1 << n):
        B1 = [i for i in range(n) if (r >> i) & 1]
        if not B1 or len(B1) == n:
            continue
        if B1[0] > (B1[0] ^ (n - 1)):  # 去重（仅取一半）
            continue
        B2 = [i for i in range(n) if i not in B1]
        Pcut = cut_kernel(P, n, B1, B2)
        I_pi = 0.0
        for y in all_states(n):
            I_pi += mu[y] * kl_row(P[y], Pcut[y])
        if I_pi < best:
            best = I_pi
            best_pi = (B1, B2)
    return best, best_pi


# ============================================================
# §2 三个测试系统
# ============================================================

def make_test_a():
    """测试 A：完全独立——4 个独立翻转（每元件自翻转）。"""
    def F(y):
        return ((1 << 4) - 1) ^ y  # 逐位取反
    return F


def make_test_b(eps=0.05):
    """测试 B：弱耦合——x₁ 独立翻转；x₂ 以 1-eps 独立翻转、eps 跟随 x₁。
    其余 x₃, x₄ 独立翻转。注意这是随机系统（非确定性）。
    """
    # 返回完整 P 矩阵（随机）
    n = 4
    P = {}
    for y in all_states(n):
        x1, x2, x3, x4 = state_tuple(y, n)
        row = [0.0] * (1 << n)
        # x₁ 独立翻转
        nx1 = 1 - x1
        # x₂：1-eps 独立翻转，eps 跟随 x₁（=nx1）
        # x₃, x₄ 独立翻转
        for nx2 in (0, 1):
            for nx3 in (0, 1):
                for nx4 in (0, 1):
                    p = 1.0
                    # x1
                    p *= 1.0  # 确定
                    # x2 随机
                    if nx2 == (1 - x2):
                        p *= (1 - eps)
                    else:
                        p *= 0.0
                    if nx2 == (1 - x1):
                        p *= 0.0  # 跟随分支我们简化：只保留独立分支
                    # 简化：x2 以 1-eps 独立翻转（概率 (1-eps)），以 eps 保持（不翻）
                    # 重新写清楚：
                    pass
        # 上面太乱，重写
        row = [0.0] * (1 << n)
        # x1 独立翻转（确定）
        # x2 弱耦合：P(nx2=¬x2) = 1-eps；P(nx2=x2) = eps（小幅偏离独立）
        # 但"跟随 x1"的耦合会破坏独立性——改用：x2 受 x1 弱影响：
        #   P(nx2 = ¬x2 ⊕ (x1 与 x2 相同 ? 0 : 1))——太绕。
        # 简单方案：x2' = ¬x2 以 1-eps；x2' = x1 以 eps（弱耦合到 x1）
        for nx2 in (0, 1):
            for nx3 in (0, 1):
                for nx4 in (0, 1):
                    p = 1.0
                    p *= 1.0  # x1 确定翻转
                    # x2 弱耦合
                    if nx2 == (1 - x2):
                        p *= (1 - eps)
                    elif nx2 == x1:
                        p *= eps
                    else:
                        p *= 0.0
                    p *= 1.0  # x3, x4 确定翻转
                    nx3_ok = (nx3 == 1 - x3)
                    nx4_ok = (nx4 == 1 - x4)
                    if not (nx3_ok and nx4_ok):
                        p = 0.0
                    if p > 0:
                        nxt = nx1 + (nx2 << 1) + (nx3 << 2) + (nx4 << 3)
                        row[nxt] += p
        P[y] = row
    return P


def make_test_c():
    """测试 C：真不可分解——S*₃ 耦合核（4 元件，强耦合）。"""
    def F(y):
        x1, x2, x3, x4 = state_tuple(y, 4)
        nx1 = (x1 + x2) % 2
        nx2 = (x1 + x2 + x3) % 2
        nx3 = (x3 + x1) % 2
        nx4 = (x4 + x2) % 2
        return nx1 + (nx2 << 1) + (nx3 << 2) + (nx4 << 3)
    return F


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 66)
    print("Layer 2 — Integration Int(S) 单位测试（GPT 方案）")
    print("Int(S) = min_{π∈Π₂} E_μ[ KL(P(·|y) ‖ P_cut(·|y)) ]")
    print("=" * 66)

    n = 4

    # 测试 A：完全独立
    print("\n--- 测试 A：完全独立（4 独立翻转）---")
    FA = make_test_a()
    PA = full_transition_matrix(FA, n)
    intA, piA = integration_min(PA, n)
    print(f"  Int(A) = {intA:.6f}  (期望 0)  [最优二分: {piA}]")
    print(f"  通过: {'✅' if abs(intA) < 1e-9 else '❌'}")

    # 测试 B：弱耦合
    print("\n--- 测试 B：弱耦合（x₂ 以 ε 跟随 x₁）---")
    PB = make_test_b(eps=0.05)
    intB, piB = integration_min(PB, n)
    print(f"  Int(B) = {intB:.6f}  (期望 ≈0 但 >0)")
    print(f"  通过: {'✅' if intB > 1e-9 else '❌'}（>0 且小）")

    # 测试 C：真不可分解
    print("\n--- 测试 C：真不可分解（S*₃ 耦合核）---")
    FC = make_test_c()
    PC = full_transition_matrix(FC, n)
    intC, piC = integration_min(PC, n)
    print(f"  Int(C) = {intC:.6f}  (期望明显 >0)  [最优二分: {piC}]")
    print(f"  通过: {'✅' if intC > 0.5 else '❌'}（明显高）")

    # 汇总
    print("\n" + "=" * 66)
    print(f"汇总: A={intA:.4f}  B={intB:.4f}  C={intC:.4f}")
    ok = abs(intA) < 1e-9 and intB > 1e-9 and intC > 0.5
    print(f"三测试全部通过: {'✅' if ok else '❌'}")
    print("=" * 66)


if __name__ == "__main__":
    main()
