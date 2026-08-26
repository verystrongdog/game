"""
意识结构侧定义 v5 — 全系统验证框架
==================================================
研讨产物（纯学术，不入游戏正典）。

v5 判定：
    意识(结构侧) ⟺ Int(S) > 0 ∧ Diff(S) ≥ θ_diff(3 bit) ∧ ∃c SelBroadcast(c)

四个系统统一验证：
    S*₂  : 新构造（期望：三要件全通过 → 意识）
    S*   : 2 位同步从动 = 麻醉态形状（期望：被拒——Diff 不足 + 无广播目标）
    S″   : 4 独立 NOT 门 = 平凡展开（期望：被拒——Int = 0）
    S‴   : NOT 门 + 开关耦合（期望：待定——v5 新广播语义下重验）

每个系统只需提供：分量数 N、转移函数 F(n)。
"""

import itertools
import math
from collections import Counter

THETA_DIFF = 3.0  # 分化下界 θ_diff（bit）
MIN_SOURCE_VALUES = 3  # 源分化下界（联合读出不同值数）
MAX_STATES = 16  # 支持最多 4 分量（0..15）


# ============================================================
# §1 系统定义
# ============================================================

def make_systems():
    """返回 {名称: (N, F)}。F: int → int，n 的位 i 为分量 i 的值。"""

    # --- S*₂：3 分量耦合（x₁′=(x₁+x₂)mod2, x₂′=(x₂+x₃)mod2, x₃′=¬x₃）---
    def F_s2(n):
        x1, x2, x3 = (n & 1), ((n >> 1) & 1), ((n >> 2) & 1)
        nx1 = (x1 + x2) % 2
        nx2 = (x2 + x3) % 2
        nx3 = 1 - x3
        return nx1 + 2 * nx2 + 4 * nx3

    # --- S*：2 位同步从动（x₁′=¬x₁, x₂′=¬x₁）---
    def F_star(n):
        x1, x2 = (n & 1), ((n >> 1) & 1)
        nx1 = 1 - x1
        nx2 = 1 - x1
        return nx1 + 2 * nx2

    # --- S″：4 独立 NOT 门（逐位取反）---
    def F_doubleprime(n):
        return ((1 << 4) - 1) ^ n

    # --- S‴：x₁′=¬x₁, x₂′=¬x₂, x₃′=¬x₃ 若 x₁=0 否则 x₃, x₄′=¬x₄ ---
    def F_tripleprime(n):
        x1, x2, x3, x4 = (n & 1), ((n >> 1) & 1), ((n >> 2) & 1), ((n >> 3) & 1)
        nx1 = 1 - x1
        nx2 = 1 - x2
        nx3 = (1 - x3) if x1 == 0 else x3
        nx4 = 1 - x4
        return nx1 + 2 * nx2 + 4 * nx3 + 8 * nx4

    return {
        "S*₂ (新构造)": (3, F_s2),
        "S* (麻醉态)": (2, F_star),
        "S″ (平凡展开)": (4, F_doubleprime),
        "S‴ (开关耦合)": (4, F_tripleprime),
    }


# ============================================================
# §2 通用组件
# ============================================================

def state_tuple(n, N):
    return tuple((n >> i) & 1 for i in range(N))


def all_states(N):
    return list(range(1 << N))


def reachable_set(F, N, start):
    seen = set()
    cur = start
    while cur not in seen:
        seen.add(cur)
        cur = F(cur)
    return seen


def diff_bits(F, N):
    """Diff = log2 |全可达集|（任意初态可达状态的并）。"""
    union = set()
    for s in all_states(N):
        union |= reachable_set(F, N, s)
    return math.log2(len(union))


def marginal_transition(F, N, comp_idx):
    """分量 comp_idx 的边际转移分布（2×2 行随机矩阵，输入均匀化）。"""
    rows = []
    for v in (0, 1):
        nxt_counts = [0, 0]
        for others in itertools.product((0, 1), repeat=N - 1):
            comps = list(others)
            comps.insert(comp_idx, v)
            n = sum(comps[i] << i for i in range(N))
            nxt = state_tuple(F(n), N)[comp_idx]
            nxt_counts[nxt] += 1
        total = sum(nxt_counts)
        rows.append([c / total for c in nxt_counts])
    return rows


def decoupled_joint(F, N):
    """解耦联合 Q：行=当前状态，列=下一状态概率 = Πᵢ 分量边际。"""
    marg = [marginal_transition(F, N, i) for i in range(N)]
    joint = {}
    for cur in all_states(N):
        c = state_tuple(cur, N)
        row = {}
        for nxt in all_states(N):
            t = state_tuple(nxt, N)
            p = 1.0
            for i in range(N):
                p *= marg[i][c[i]][t[i]]
            row[nxt] = p
        joint[cur] = row
    return joint


def kl_divergence(P, Q, eps=1e-12):
    total = 0.0
    for p, q in zip(P, Q):
        if p > 0:
            total += p * math.log(p / max(q, eps))
    return total


def integration_kl(F, N):
    """Int = 平均 KL（整体 P vs 解耦 Q，均匀初态）。"""
    P = {}
    for cur in all_states(N):
        row = [0.0] * (1 << N)
        row[F(cur)] = 1.0
        P[cur] = row
    Q = decoupled_joint(F, N)
    total = 0.0
    for cur in all_states(N):
        q_row = [Q[cur].get(i, 0.0) for i in range(1 << N)]
        total += kl_divergence(P[cur], q_row)
    return total / (1 << N)


def mutual_information(seq_a, seq_b):
    pairs = list(zip(seq_a, seq_b))
    n = len(pairs)
    pa = Counter(seq_a)
    pb = Counter(seq_b)
    pab = Counter(pairs)
    mi = 0.0
    for (a, b), cnt in pab.items():
        p_ab = cnt / n
        p_a = pa[a] / n
        p_b = pb[b] / n
        mi += p_ab * math.log(p_ab / (p_a * p_b))
    return mi


def entropy(seq):
    """经验熵 H(seq)。"""
    c = Counter(seq)
    n = len(seq)
    h = 0.0
    for cnt in c.values():
        p = cnt / n
        h -= p * math.log(p)
    return h


def transfer_entropy(source_past, target_past, target_future):
    """转移熵 TE(源过去 → 目标未来 | 目标过去)
    TE = H(target_future | target_past) - H(target_future | target_past, source_past)
    > 0 ⟺ 源过去在控制目标自身过去后，仍提供关于目标未来的信息（定向因果）。
    """
    # 对齐三序列（同一时刻 t：source_past[t], target_past[t], target_future[t]）
    n = len(target_future)
    # H(target_future | target_past)
    h_cond_target = 0.0
    joint_tp_tf = Counter(zip(target_past, target_future))
    marg_tp = Counter(target_past)
    for (tp, tf), cnt in joint_tp_tf.items():
        p_j = cnt / n
        p_tp = marg_tp[tp] / n
        h_cond_target -= p_j * math.log(p_j / p_tp)
    # H(target_future | target_past, source_past)
    h_cond_both = 0.0
    joint_all = Counter(zip(source_past, target_past, target_future))
    marg_sp_tp = Counter(zip(source_past, target_past))
    for (sp, tp, tf), cnt in joint_all.items():
        p_j = cnt / n
        p_m = marg_sp_tp[(sp, tp)] / n
        h_cond_both -= p_j * math.log(p_j / p_m)
    return h_cond_target - h_cond_both


def sel_broadcast_check(F, N, steps=128):
    """选择性广播：∃c, I₀(|I₀|=2), j∉I₀：
    ① 非退化（联合读出沿轨迹变化）
    ② 源分化（联合读出 ≥ 3 个不同值）
    ③ 选择性访问 = 定向因果（TE(源过去 → 目标未来 | 目标过去) > 0）
    返回候选列表。N=2 时结构上无目标 → 恒空。
    """
    if N < 3:
        return []  # 无目标分量 j ∉ I₀
    results = []
    for c in all_states(N):
        seq = []
        cur = c
        for _ in range(steps):
            seq.append(cur)
            cur = F(cur)
        for I0 in itertools.combinations(range(N), 2):
            g_trace = []
            for s in seq:
                t = state_tuple(s, N)
                g_trace.append((t[I0[0]], t[I0[1]]))
            # ① 非退化
            if all(v == g_trace[0] for v in g_trace):
                continue
            # ② 源分化
            if len(set(g_trace)) < MIN_SOURCE_VALUES:
                continue
            # ③ 选择性访问：定向因果 TE > 0
            for j in range(N):
                if j in I0:
                    continue
                tgt_trace = [state_tuple(s, N)[j] for s in seq]
                # TE: 源过去 g[t] → 目标未来 tgt[t+1]，控制目标过去 tgt[t]
                te = transfer_entropy(
                    g_trace[:-1],       # 源过去
                    tgt_trace[:-1],     # 目标过去
                    tgt_trace[1:],      # 目标未来
                )
                if te > 1e-9:
                    results.append({
                        "c": c, "I0": I0, "j": j,
                        "n_src_vals": len(set(g_trace)),
                        "TE": te,
                    })
                    break  # 每个 (c, I₀) 找到一个目标即可
    return results


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 64)
    print("意识结构侧定义 v5 — 四系统统一验证")
    print("判定: Int > 0 ∧ Diff ≥ 3bit ∧ ∃SelBroadcast")
    print("=" * 64)

    systems = make_systems()
    rows = []
    for name, (N, F) in systems.items():
        int_val = integration_kl(F, N)
        d_val = diff_bits(F, N)
        sb = sel_broadcast_check(F, N)
        passed = int_val > 0 and d_val >= THETA_DIFF and bool(sb)
        rows.append((name, N, int_val, d_val, sb, passed))
        print(f"\n--- {name} (N={N}) ---")
        print(f"  Int  = {int_val:.6f} nat  (>0: {'✅' if int_val > 0 else '❌'})")
        print(f"  Diff = {d_val:.4f} bit  (≥3: {'✅' if d_val >= THETA_DIFF else '❌'})")
        if sb:
            first = sb[0]
            print(f"  SelBroadcast: ✅ 共 {len(sb)} 组候选，例: c={first['c']} "
                  f"I₀={first['I0']} j={first['j']} 源值数={first['n_src_vals']} "
                  f"TE={first['TE']:.4f}")
        else:
            print(f"  SelBroadcast: ❌ 无候选")

    print("\n" + "=" * 64)
    print("汇总:")
    for name, N, int_val, d_val, sb, passed in rows:
        status = "✅ 意识（结构侧）" if passed else "❌ 拒绝"
        print(f"  {name:16s}: {status}  (Int={int_val:.3f}, Diff={d_val:.2f}bit, "
              f"广播={'✓' if sb else '✗'})")
    print("=" * 64)


if __name__ == "__main__":
    main()
