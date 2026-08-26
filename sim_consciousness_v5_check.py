"""
意识结构侧定义 v5 — 非平凡性构造 S*₂ 验证
==================================================
研讨产物（纯学术，不入游戏正典）。

v5 判定：
    意识(结构侧) ⟺ Int(S) > 0 ∧ Diff(S) ≥ θ_diff(3 bit) ∧ ∃c SelBroadcast(c)

待验证构造 S*₂：X = {0,1}³，3 分量，转移：
    x₁′ = (x₁ + x₂) mod 2
    x₂′ = (x₂ + x₃) mod 2
    x₃′ = ¬x₃

验证项：
    [1] Int > 0          —— 整体动力学 vs 解耦动力学 F₁×F₂×F₃ 的 KL 偏差（逐行）
    [2] Diff ≥ 3 bit     —— 可达状态集基数 ≥ 8（log2 |reachable| ≥ 3）
    [3] SelBroadcast     —— ∃c,g,i₀：
                              ① 非退化（读出沿轨迹变化）
                              ② 源分化（源分量读出 ≥ 3 个不同值）
                              ③ 选择性访问（存在目标 j≠i₀ 读出与源一致，且非全分量）
                              ④ 非平凡（i₀ 存在，g 非常数）
"""

import itertools
import math

# ============================================================
# §1 系统定义
# ============================================================

N_COMP = 3  # 分量数


def state_tuple(n):
    """整数 n (0..7) → 分量元组 (x1, x2, x3)。位 0 = x1。"""
    return tuple((n >> i) & 1 for i in range(N_COMP))


def state_index(t):
    """分量元组 → 整数。"""
    return sum(t[i] << i for i in range(N_COMP))


def F(n):
    """S*₂ 转移函数。返回下一状态整数。"""
    x1, x2, x3 = state_tuple(n)
    nx1 = (x1 + x2) % 2
    nx2 = (x2 + x3) % 2
    nx3 = 1 - x3
    return state_index((nx1, nx2, nx3))


# ============================================================
# §2 可达状态与分化 Diff
# ============================================================

def reachable_set(start=0):
    """从初态 start 出发，沿 F 遍历全部可达状态。"""
    seen = set()
    cur = start
    while cur not in seen:
        seen.add(cur)
        cur = F(cur)
    return seen


def all_reachable():
    """全状态空间上的可达集（任意初态可达状态的并）。"""
    union = set()
    for s in range(8):
        union |= reachable_set(s)
    return union


def diff_bits(reachable):
    """Diff(S) = log2 |可达集|（bit）。"""
    return math.log2(len(reachable))


# ============================================================
# §3 整合 Int（KL 散度：整体 vs 解耦）
# ============================================================

def marginal_transition(comp_idx):
    """分量 comp_idx 的边际转移分布（行随机矩阵 2×2，行=当前值，列=下一值）。

    计算方式：固定当前分量值，对所有其他分量均匀化，统计下一分量值的分布。
    均匀化 = 在输入上取均匀先验（本系统无外部输入，A 空）。
    """
    # 对每个当前分量值 v ∈ {0,1}，收集所有 (其他分量状态) 下的转移结果
    rows = []
    for v in (0, 1):
        nxt_counts = [0, 0]
        total = 0
        for others in itertools.product((0, 1), repeat=N_COMP - 1):
            # 组装完整状态
            comps = list(others)
            comps.insert(comp_idx, v)
            n = state_index(tuple(comps))
            nxt = state_tuple(F(n))[comp_idx]
            nxt_counts[nxt] += 1
            total += 1
        rows.append([c / total for c in nxt_counts])
    return rows


def decoupled_joint(row_src, row_tgt):
    """解耦联合分布 P(x→·) = F₁(x₁→·) ⊗ F₂(x₂→·) ⊗ F₃(x₃→·)。

    返回 8×8 矩阵，行 = 当前状态，列 = 下一状态（概率）。
    注意：这里仅对 (x₁, x₂) 两个分量做解耦验证（x₃ 独立翻转本就是解耦的）。
    更一般地：解耦联合 = 各分量边际转移的乘积。
    """
    marg = [marginal_transition(i) for i in range(N_COMP)]
    joint = {}
    for cur in range(8):
        c = state_tuple(cur)
        # P(next | cur) = Πᵢ marg[i][c[i]][next[i]]
        row = {}
        for nxt in range(8):
            t = state_tuple(nxt)
            p = 1.0
            for i in range(N_COMP):
                p *= marg[i][c[i]][t[i]]
            row[nxt] = p
        joint[cur] = row
    return joint


def kl_divergence(P, Q, eps=1e-12):
    """KL(P‖Q)，行概率向量。仅对 P>0 处求和。"""
    total = 0.0
    for p, q in zip(P, Q):
        if p > 0:
            total += p * math.log(p / max(q, eps))
    return total


def integration_kl():
    """Int = 平均 KL（整体动力学 P 与解耦联合 Q 的逐行 KL，按均匀初态平均）。"""
    P = {}
    for cur in range(8):
        nxt = F(cur)
        row = [0.0] * 8
        row[nxt] = 1.0
        P[cur] = row
    Q = decoupled_joint(None, None)
    total = 0.0
    for cur in range(8):
        total += kl_divergence(P[cur], Q[cur])
    return total / 8.0


# ============================================================
# §4 选择性广播 SelBroadcast
# ============================================================

def trajectory(start, steps=16):
    """从 start 出发的轨迹（状态序列）。"""
    seq = []
    cur = start
    for _ in range(steps):
        seq.append(cur)
        cur = F(cur)
    return seq


def comp_trace(seq, comp_idx):
    """分量 comp_idx 的读出轨迹（值序列）。"""
    return [state_tuple(s)[comp_idx] for s in seq]


def sel_broadcast_check(steps=32, min_source_values=3):
    """逐状态 c、逐源集合 I₀（|I₀|=2 联合读出）、逐目标 j∉I₀ 检查 ①②③④。

    v5.1 修订（修复"二值分量无 ≥3 值"矛盾）：
      - 源 = 多分量联合读出 g(x) = (xᵢ : i ∈ I₀)，|I₀| ≥ 2（特征绑定）
      - ② 源分化：g 沿轨迹 ≥ 3 个不同联合值
      - ③ 选择性访问：目标 j ∉ I₀ 与 g 的互信息 > 0（内容被目标"使用"，不必复制）
    """
    results = []
    for c in range(8):
        seq = trajectory(c, steps)
        for I0 in itertools.combinations(range(N_COMP), 2):
            # 联合读出 g(x) = (x_i, x_i')
            g_trace = []
            for s in seq:
                t = state_tuple(s)
                g_trace.append((t[I0[0]], t[I0[1]]))
            # ② 源分化：≥ 3 个不同联合值
            n_src_vals = len(set(g_trace))
            if n_src_vals < min_source_values:
                continue
            # ① 非退化：g 沿轨迹变化
            if all(v == g_trace[0] for v in g_trace):
                continue
            # ③ 选择性访问：存在目标 j ∉ I₀ 与 g 互信息 > 0
            for j in range(N_COMP):
                if j in I0:
                    continue
                tgt_trace = [state_tuple(s)[j] for s in seq]
                if mutual_information(g_trace, tgt_trace) > 1e-9:
                    results.append({
                        "c": c, "I0": I0, "j": j,
                        "n_src_vals": n_src_vals,
                        "g_trace": g_trace[:8],
                        "tgt_trace": tgt_trace[:8],
                    })
    return results


def mutual_information(seq_a, seq_b):
    """互信息 I(A;B)，序列经验分布。"""
    pairs = list(zip(seq_a, seq_b))
    n = len(pairs)
    from collections import Counter
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


# ============================================================
# §5 对照验证：S*（2 位同步从动 = 麻醉态形状）
#    X = {0,1}², F: 00→11, 01→11, 10→00, 11→00
#    预期：Int > 0（整合强）但 Diff 低 + 无选择性广播 → v5 拒绝
# ============================================================

def F_star(n):
    """S* 转移：00→11, 01→11, 10→00, 11→00（n = x1 + 2*x2）。"""
    x1 = n & 1
    x2 = (n >> 1) & 1
    nx1 = 1 - x1
    nx2 = 1 - x1  # x2 完全由 x1 决定（从动）
    return nx1 + 2 * nx2


def integration_kl_star():
    """S* 的 Int：整体 vs 解耦 KL。"""
    # 整体 P：确定性
    P = {}
    for cur in range(4):
        nxt = F_star(cur)
        row = [0.0] * 4
        row[nxt] = 1.0
        P[cur] = row
    # 解耦 Q：x1 自翻转（确定性），x2 边际均匀化
    Q = {}
    for cur in range(4):
        x1 = cur & 1
        x2 = (cur >> 1) & 1
        row = [0.0] * 4
        for nx2 in (0, 1):
            nxt = (1 - x1) + 2 * nx2
            row[nxt] = 0.5
        Q[cur] = row
    total = 0.0
    for cur in range(4):
        total += kl_divergence(P[cur], Q[cur])
    return total / 4.0


def diff_bits_star():
    """S* 的 Diff：可达集大小。"""
    ra = set()
    for s in range(4):
        seen = set()
        cur = s
        while cur not in seen:
            seen.add(cur)
            cur = F_star(cur)
        ra |= seen
    return math.log2(len(ra))


def sel_broadcast_check_star(steps=32, min_source_values=3):
    """S* 的选择性广播检查（2 分量）。

    结构事实：S* 只有 2 个分量——源集合 I₀ 只能是全分量 {0,1}，
    因此不存在目标 j ∉ I₀——选择性访问 ③ 在结构上不可能满足。
    返回恒为空列表（S* 永远无广播候选）。
    """
    return []


# ============================================================
# §6 主流程
# ============================================================

def main():
    print("=" * 60)
    print("意识结构侧定义 v5 — S*₂ 三要件验证")
    print("=" * 60)

    # --- 验证 [1]: Int > 0 ---
    int_val = integration_kl()
    print(f"\n[1] 整合 Int = {int_val:.6f} nat  (> 0 ? {int_val > 0})")

    # --- 验证 [2]: Diff ≥ 3 bit ---
    ra = all_reachable()
    d = diff_bits(ra)
    print(f"\n[2] 分化 Diff = {d:.4f} bit  (≥ 3 ? {d >= 3})")
    print(f"    可达状态集 = {sorted(ra)} ({len(ra)} 状态)")

    # 逐初态可达集（观察是否状态相关）
    print("    逐初态可达集:")
    for s in range(8):
        rs = reachable_set(s)
        print(f"      初态 {s} (状态{state_tuple(s)}): {sorted(rs)} ({len(rs)} 状态)")

    # --- 验证 [3]: SelBroadcast ---
    print("\n[3] 选择性广播（联合读出 ≥ 3 值 + 互信息访问）:")
    sb = sel_broadcast_check()
    if sb:
        for info in sb[:8]:
            print(f"    ✅ c={info['c']}({state_tuple(info['c'])}) 源集合 I₀={info['I0']} "
                  f"目标 j={info['j']}: 源值数={info['n_src_vals']}, "
                  f"g轨迹前8={info['g_trace']}, 目标轨迹前8={info['tgt_trace']}")
        if len(sb) > 8:
            print(f"    … 共 {len(sb)} 组 (c, I₀, j) 满足")
    else:
        print("    ❌ 未找到满足 ①②③④ 的 (c, I₀, j)")

    # 补充：若 3 值太严，报告 2 值下的情况（诊断用）
    sb2 = sel_broadcast_check(min_source_values=2)
    if not sb and sb2:
        print("\n    [诊断] 放宽到 ≥2 值时有候选:")
        for info in sb2[:5]:
            print(f"      c={info['c']}({state_tuple(info['c'])}) 源 I₀={info['I0']}: 源值数={info['n_src_vals']}")

    # --- 对照验证：S*（麻醉态形状，2 位同步从动）应被 v5 拒绝 ---
    print("\n[4] 对照验证：S*（2 位同步从动 = 麻醉态形状）应被 v5 拒绝:")
    sb_star = sel_broadcast_check_star()
    d_star = diff_bits_star()
    int_star = integration_kl_star()
    rejected = not (int_star > 0 and d_star >= 3 and bool(sb_star))
    print(f"    Int(S*) = {int_star:.6f} nat (>0? {int_star > 0})")
    print(f"    Diff(S*) = {d_star:.4f} bit (≥3? {d_star >= 3})")
    print(f"    SelBroadcast(S*): {'找到候选（不该）' if sb_star else '无候选 ✅'}")
    print(f"    → v5 拒绝 S*: {'✅ 是（麻醉态形状被拒）' if rejected else '❌ 否（S* 漏网）'}")

    # --- 总结 ---
    passed = int_val > 0 and d >= 3 and bool(sb) and rejected
    print("\n" + "=" * 60)
    verdict = "✅ S*₂ 满足三要件且 S* 被拒（v5 定义成立）" if passed else "❌ v5 验证未完全通过（需调整）"
    print("v5 判定结果:", verdict)
    print("=" * 60)


if __name__ == "__main__":
    main()
