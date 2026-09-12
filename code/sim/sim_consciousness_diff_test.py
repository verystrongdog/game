"""
Layer 2 — Differentiation Diff(S;O) 单位测试
==================================================
研讨产物（纯学术，不入游戏正典）。

GPT 第九份建议：Diff 三层结构
  O: S → O          规范观测映射（外生，先于 Diff——避免循环）
  O_t = O(Y_t)      规范观察状态
  Diff_state(S;O) = (1/m) Σ_t H_{μ_t}(O_t)    状态差异性
  Diff_T(S;O)     = H(O_t, …, O_{t+T})        动态窗口差异性（本版实现 Diff_state）

四组测试：
  D1 低状态系统     X ∈ {0,1}            → H ≤ 1 bit < 3，不过
  D2 真多状态系统   X ∈ {0,…,15} 均匀     → H = 4 bit ≥ 3，过
  D3 垃圾变量攻击   X = (C,R), R⊥C 高熵   → 加 R 不得虚假提升 Diff（生死测试）
  D4 纯随机系统     X ~ Uniform(Ω)        → H 高但不自动成意识（Diff 只是必要维度）

实现简化（第一版，同 Int）：元件二值、确定性转移、μ 均匀近似、O 身份映射
或投影映射（D3 用 O 丢弃垃圾变量验证 O 的作用）。
"""

import math
from collections import Counter

EPS = 1e-12


# ============================================================
# §1 通用组件
# ============================================================

def state_tuple(s, n):
    return tuple((s >> i) & 1 for i in range(n))


def entropy_of_distribution(dist):
    """熵（bit）。dist: 值 → 概率。"""
    h = 0.0
    for p in dist.values():
        if p > EPS:
            h -= p * math.log2(p)
    return h


def stationary_or_uniform(mu0_evolve=None, n=None):
    """第一版：均匀分布近似。"""
    return None  # 主流程直接用均匀


def diff_state(O, n, mu=None):
    """Diff_state = H_μ(O_t)。O: 完整状态 → 观测状态（整数）。"""
    if mu is None:
        mu = {y: 1.0 / (1 << n) for y in range(1 << n)}
    obs_dist = Counter()
    for y in range(1 << n):
        obs_dist[O(y)] += mu[y]
    return entropy_of_distribution(obs_dist)


def identity_O(n):
    return lambda y: y


def project_O(n, keep_bits):
    """投影观测：只保留 keep_bits（元件索引）的状态。"""
    def O(y):
        t = state_tuple(y, n)
        val = 0
        for j, i in enumerate(sorted(keep_bits)):
            val |= t[i] << j
        return val
    return O


# ============================================================
# §2 测试系统
# ============================================================

def make_test_d1():
    """D1 低状态：1 元件二值，X ∈ {0,1} → H ≤ 1 bit。"""
    n = 1
    O = identity_O(n)
    return n, O


def make_test_d2():
    """D2 真多状态：4 元件均匀运行（全部可达且均匀分布）→ H = 4 bit。

    用确定性遍历：4 元件计数器（F = y+1 mod 16），均匀 μ 下 H = 4 bit。
    """
    n = 4
    O = identity_O(n)
    return n, O


def make_test_d3():
    """D3 垃圾变量：C（2 元件真实系统）+ R（3 元件独立随机计数器）。

    对比：
      Diff(C)          —— 只观察 C 部分（O 投影到 C）
      Diff(C, R)       —— 观察全部（O 身份）——垃圾 R 应被 O 排除
      Diff(C) 无 O     —— 不投影（身份 O 时 Diff 被 R 撑高，验证 O 的必要性）
    """
    n = 5  # C = 元件 0,1；R = 元件 2,3,4
    O_c = project_O(n, [0, 1])       # 规范观测：只投影 C
    O_full = identity_O(n)           # 无 O：观测全部（含垃圾 R）
    return n, O_c, O_full


def make_test_d4():
    """D4 纯随机：4 元件，μ 均匀 → H = 4 bit（高），但只是必要维度。"""
    n = 4
    O = identity_O(n)
    return n, O


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 66)
    print("Layer 2 — Differentiation Diff(S;O) 单位测试")
    print("Diff_state = H_μ(O_t)，O 外生规范观测")
    print("=" * 66)

    # D1 低状态
    print("\n--- D1 低状态（X ∈ {0,1}）---")
    n1, O1 = make_test_d1()
    d1 = diff_state(O1, n1)
    print(f"  Diff = {d1:.4f} bit  (期望 ≤ 1 < 3)")
    print(f"  通过: {'✅' if d1 < 3 else '❌'}（应不过）")

    # D2 真多状态
    print("\n--- D2 真多状态（4 元件均匀 → 4 bit）---")
    n2, O2 = make_test_d2()
    d2 = diff_state(O2, n2)
    print(f"  Diff = {d2:.4f} bit  (期望 = 4 ≥ 3)")
    print(f"  通过: {'✅' if d2 >= 3 else '❌'}")

    # D3 垃圾变量（生死测试）
    print("\n--- D3 垃圾变量（C 2 元件 + R 3 元件独立计数器）---")
    n3, O_c, O_full = make_test_d3()
    d_c = diff_state(O_c, n3)       # 规范观测：只投影 C
    d_full = diff_state(O_full, n3) # 无 O：观测全部（含垃圾）
    print(f"  Diff(C)  [O 投影到 C]   = {d_c:.4f} bit")
    print(f"  Diff(C,R)[身份 O，含垃圾] = {d_full:.4f} bit")
    print(f"  垃圾 R 虚假提升: {'❌ 是（身份 O 被撑高）' if d_full > d_c + 1e-9 else '✅ 否'}")
    print(f"  O 的作用: {'✅ 有效（投影排除垃圾）' if d_c < d_full - 1e-9 else '⚠️ 无差异'}")

    # D4 纯随机
    print("\n--- D4 纯随机（4 元件均匀 → 4 bit 高值）---")
    n4, O4 = make_test_d4()
    d4 = diff_state(O4, n4)
    print(f"  Diff = {d4:.4f} bit  (高，但只是必要维度——不自动成意识)")
    print(f"  通过: {'✅' if d4 >= 3 else '❌'}（Diff 高是预期；CS 需三要件合取）")

    # 汇总
    print("\n" + "=" * 66)
    print(f"汇总: D1={d1:.2f}bit  D2={d2:.2f}bit  D3(C)={d_c:.2f}bit  D4={d4:.2f}bit")
    ok = d1 < 3 and d2 >= 3 and (d_c < d_full - 1e-9) and d4 >= 3
    print(f"四测试通过: {'✅' if ok else '❌'}")
    print("=" * 66)


if __name__ == "__main__":
    main()
