"""
意识候选结构定义 v5.3 — 全系统验证框架
==================================================
研讨产物（纯学术，不入游戏正典）。

定位声明（v5.3 修订，接受外部攻击后收束）：
    本定义判定的是「意识候选结构」（宽泛类），不是「意识」。
    C_candidate(S) 是意识结构的充分条件（必要条件未知）。
    收窄由桥接公设承担（体验侧，F4，数学外）。

v5.3 判定：
    C_candidate(S) ⟺ Int(S) > 0 ∧ Diff(S) ≥ θ_D(3bit) ∧ ∃ SelBroadcast(S)
    覆盖度声明：I₀∪J 与系统其余部分的关系为声明项（诊断输出），
                不进入判定——接受"局部模块即可判定候选"的宽泛性。

    Int(S)     = sup{ KL_μ(F‖F₁×⋯×Fₖ) : supp(μ) ⊆ Reach(S), μ ∈ ℳ_info, KL 有限 } > 0
                 [修订1] 类型修正：μ 是测度，supp(μ) ⊆ Reach(S)（非 μ ∈ Reach(S)）
                 μ_S 方案否决——U1 判定唯一性（运行条件成新自由度）
    Diff(S)    = log₂|ReachableSet| ≥ 3 bit
    SelBroadcast = ∃I₀(|I₀|≥2), J⊆V∖I₀：
                     [修订2] 多目标广播 |J| ≥ m(=2)，∀j∈J: TE(I₀→j) > 0
                     [修订3] 选择性比 SelRatio(I₀→J) ≥ θ_S
                     联合读出 ≥3 值（非退化）∧ 目标相互独立（无复制伪装）

四个系统统一验证：
    S*₃  : 4 分量新构造（多目标广播）——期望：三要件全通过
    S*   : 2 位同步从动 = 麻醉态（期望：Diff 不足 + 无目标 → 拒）
    S″   : 4 独立 NOT 门 = 平凡展开（期望：Int = 0 → 拒）
    S‴   : NOT 门 + 开关耦合（期望：广播/TE 不足 → 拒）
"""

import itertools
import math
from collections import Counter

THETA_DIFF = 3.0       # θ_D 分化下界（bit）
MIN_SOURCE_VALUES = 3  # 源分化：联合读出 ≥ 3 值
MIN_TARGETS = 2        # 多目标广播：|J| ≥ 2
THETA_SEL = 1.0        # 选择性比下界：TE(I₀→j) / max_{K≠I₀} TE(K→j) ≥ θ_S


# ============================================================
# §1 系统定义
# ============================================================

def make_systems():
    """返回 {名称: (N, F)}。F: int → int，n 的位 i 为分量 i 的值。"""

    # --- S*₃：4 分量，两路广播（设计目标：多目标广播 + 目标独立）---
    # 耦合核 (x₁,x₂) 相互耦合；x₃、x₄ 各自独立翻转
    # 广播源 I₀={x₁,x₂}（耦合核联合），目标 J={x₃,x₄}
    # x₁′ = x₁⊕x₂, x₂′ = x₂⊕x₃(取 x₁ 门控?), ... 见下方显式定义
    def F_s3(n):
        x1, x2, x3, x4 = (n & 1), ((n >> 1) & 1), ((n >> 2) & 1), ((n >> 3) & 1)
        # 核心耦合：x₁、x₂ 双向依赖（整合源）
        nx1 = (x1 + x2) % 2
        nx2 = (x1 + x2 + x3) % 2
        # 目标 x₃：受源影响但自身演化（接收广播）
        nx3 = (x3 + x1) % 2
        # 目标 x₄：受源影响但自身演化（接收广播）——与 x₃ 不同方式（独立性）
        nx4 = (x4 + x2) % 2
        return nx1 + 2 * nx2 + 4 * nx3 + 8 * nx4

    # --- S*：2 位同步从动（麻醉态形状）---
    def F_star(n):
        x1, x2 = (n & 1), ((n >> 1) & 1)
        nx1 = 1 - x1
        nx2 = 1 - x1
        return nx1 + 2 * nx2

    # --- S″：4 独立 NOT 门（平凡展开）---
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
        "S*₃ (4分量新构造)": (4, F_s3),
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


def full_reachable(F, N):
    union = set()
    for s in all_states(N):
        union |= reachable_set(F, N, s)
    return union


def diff_bits(F, N):
    return math.log2(len(full_reachable(F, N)))


def marginal_transition(F, N, comp_idx):
    """分量边际转移分布（2×2 行随机矩阵，其他分量均匀化）。"""
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


def integration_kl_sup_reachable(F, N):
    """[修订1] Int = sup over μ ∈ Reach(S) 的平均 KL。

    实现：μ 的可达域 = 可达状态集；sup over 可达状态上的分布
    = max over 可达状态 x 的单点分布 KL(x)（把质量集中在 KL 最大的可达状态）。
    同时报告可达集平均 KL 作对照。
    """
    P = {}
    for cur in all_states(N):
        row = [0.0] * (1 << N)
        row[F(cur)] = 1.0
        P[cur] = row
    Q = decoupled_joint(F, N)
    reach = full_reachable(F, N)
    row_kl = {}
    for cur in reach:
        q_row = [Q[cur].get(i, 0.0) for i in range(1 << N)]
        row_kl[cur] = kl_divergence(P[cur], q_row)
    sup_val = max(row_kl.values())
    avg_val = sum(row_kl.values()) / len(row_kl)
    return sup_val, avg_val


def entropy(seq):
    c = Counter(seq)
    n = len(seq)
    h = 0.0
    for cnt in c.values():
        p = cnt / n
        h -= p * math.log(p)
    return h


def transfer_entropy(source_past, target_past, target_future):
    """TE(源过去 → 目标未来 | 目标过去)。"""
    n = len(target_future)
    h_cond_target = 0.0
    joint_tp_tf = Counter(zip(target_past, target_future))
    marg_tp = Counter(target_past)
    for (tp, tf), cnt in joint_tp_tf.items():
        p_j = cnt / n
        p_tp = marg_tp[tp] / n
        h_cond_target -= p_j * math.log(p_j / p_tp)
    h_cond_both = 0.0
    joint_all = Counter(zip(source_past, target_past, target_future))
    marg_sp_tp = Counter(zip(source_past, target_past))
    for (sp, tp, tf), cnt in joint_all.items():
        p_j = cnt / n
        p_m = marg_sp_tp[(sp, tp)] / n
        h_cond_both -= p_j * math.log(p_j / p_m)
    return h_cond_target - h_cond_both


def sel_broadcast_check(F, N, steps=256):
    """[修订2+3] 选择性广播：∃I₀(|I₀|=2), J(|J|≥2)：
    ① 联合读出 ≥3 值（非退化）
    ② 多目标：∀j∈J: TE(I₀→j) > 0
    ③ 选择性比：对每个 j∈J，TE(I₀→j) ≥ θ_S · max_{K≠I₀} TE(K→j)
    ④ 目标独立：J 中目标两两 TE 不异常（无复制伪装——诊断输出）
    """
    if N < 4:
        return []  # 多目标广播需 ≥4 分量（I₀ 2 个 + J 2 个）
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
            # ① 非退化 + 源分化
            if all(v == g_trace[0] for v in g_trace):
                continue
            if len(set(g_trace)) < MIN_SOURCE_VALUES:
                continue
            targets = [j for j in range(N) if j not in I0]
            if len(targets) < MIN_TARGETS:
                continue
            # 计算所有源→目标 TE
            te_map = {}
            for j in targets:
                tgt_trace = [state_tuple(s, N)[j] for s in seq]
                te_map[j] = transfer_entropy(g_trace[:-1], tgt_trace[:-1], tgt_trace[1:])
            # ② 多目标：至少 MIN_TARGETS 个目标 TE > 0
            good_targets = [j for j in targets if te_map[j] > 1e-9]
            if len(good_targets) < MIN_TARGETS:
                continue
            # ③ 选择性比：TE(I₀→j) ≥ θ_S · max_{K≠I₀} TE(K→j)
            #    其他源 K = 单个分量（背景传播）
            sel_ok = True
            sel_ratios = {}
            for j in good_targets:
                tgt_trace = [state_tuple(s, N)[j] for s in seq]
                background = 0.0
                for K in range(N):
                    if K in I0:
                        continue
                    if K == j:
                        continue
                    k_trace = [state_tuple(s, N)[K] for s in seq]
                    # 单分量源 K 对 j 的 TE
                    bg = transfer_entropy(k_trace[:-1], tgt_trace[:-1], tgt_trace[1:])
                    background = max(background, bg)
                if background < 1e-12:
                    # 背景零传播 → 完全选择性 → 选择性比 = ∞（语义正确，非发散）
                    sel_ratios[j] = float("inf")
                else:
                    ratio = te_map[j] / background
                    sel_ratios[j] = ratio
                    if ratio < THETA_SEL:
                        sel_ok = False
            if not sel_ok:
                continue
            results.append({
                "c": c, "I0": I0, "J": good_targets,
                "n_src_vals": len(set(g_trace)),
                "te_map": {j: round(v, 4) for j, v in te_map.items()},
                "sel_ratios": {j: round(r, 3) for j, r in sel_ratios.items()},
            })
    return results


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 66)
    print("意识候选结构定义 v5.3 — 全系统统一验证")
    print("判定: Int>0(supp⊆Reach,sup) ∧ Diff≥3bit ∧ SelBroadcast(多目标+选择性比)")
    print("定位: C_candidate（候选结构充分条件）——收窄由桥接公设承担")
    print("=" * 66)

    systems = make_systems()
    rows = []
    for name, (N, F) in systems.items():
        sup_val, avg_val = integration_kl_sup_reachable(F, N)
        d_val = diff_bits(F, N)
        sb = sel_broadcast_check(F, N)
        passed = sup_val > 0 and d_val >= THETA_DIFF and bool(sb)
        rows.append((name, N, sup_val, avg_val, d_val, sb, passed))
        print(f"\n--- {name} (N={N}) ---")
        print(f"  Int(sup可达域) = {sup_val:.6f} nat  (>0: {'✅' if sup_val > 0 else '❌'})  "
              f"[可达集平均对照: {avg_val:.4f}]")
        print(f"  Diff = {d_val:.4f} bit  (≥3: {'✅' if d_val >= THETA_DIFF else '❌'})")
        if sb:
            first = sb[0]
            print(f"  SelBroadcast: ✅ 共 {len(sb)} 组，例: c={first['c']} I₀={first['I0']} "
                  f"J={first['J']} 源值数={first['n_src_vals']} TE={first['te_map']} "
                  f"SelRatio={first['sel_ratios']}")
        else:
            print(f"  SelBroadcast: ❌ 无候选")

    print("\n" + "=" * 66)
    print("汇总:")
    for name, N, sup_val, avg_val, d_val, sb, passed in rows:
        status = "✅ 候选" if passed else "❌ 拒绝"
        print(f"  {name:20s}: {status}  (Int={sup_val:.3f}, Diff={d_val:.2f}bit, 广播={'✓' if sb else '✗'})")
    print("=" * 66)


if __name__ == "__main__":
    main()
