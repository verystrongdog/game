"""
Layer 2 — 四要件合取 CS' 测试（GPT 第十三份）
==================================================
研讨产物（纯学术，不入游戏正典）。

CS' = Int ∧ Diff ∧ SelBroadcast ∧ SM（候选结构判据，非意识定义）

记录完整向量 C(S) = (Int, Diff, SB, SM)。

测试序列：
  F1 计数控制器     (应: SM=1 → CS'=? 关键反例)
  F3 纯前馈         (应: SM=0 → CS'=0)
  F8 表征+因果使用   (应: 四维全正 → CS'=1)
  F9 伪自模型       (状态估计+反馈控制——SM 是否只是控制理论?)
  复制攻击 S vs S⊕S (哪一维因复制膨胀?)

判定：情况A(F1=0,F3=0,F8=1)→SM 提高区分力；情况B(F1=1)→四要件仍不够
"""

import itertools
import math
import random
from collections import Counter

EPS = 1e-12
THETA_TE = 0.01
THETA_SRC = 0.5
THETA_F = 0.5
THETA_C = 0.3
THETA_M = 0.3
STEPS = 4000
SEED = 42


# ============================================================
# §1 通用组件
# ============================================================

def entropy(seq):
    c = Counter(seq)
    n = len(seq)
    h = 0.0
    for cnt in c.values():
        p = cnt / n
        h -= p * math.log(p)
    return h


def mutual_information(seq_a, seq_b):
    pairs = list(zip(seq_a, seq_b))
    n = len(pairs)
    pa = Counter(seq_a)
    pb = Counter(seq_b)
    pab = Counter(pairs)
    mi = 0.0
    for (a, b), c in pab.items():
        p_ab = c / n
        p_a = pa[a] / n
        p_b = pb[b] / n
        mi += p_ab * math.log(p_ab / (p_a * p_b))
    return mi


def transfer_entropy(source_past, target_past, target_future):
    n = len(target_future)
    h1 = 0.0
    j1 = Counter(zip(target_past, target_future))
    m1 = Counter(target_past)
    for (tp, tf), c in j1.items():
        pj = c / n
        pm = m1[tp] / n
        h1 -= pj * math.log(pj / pm)
    h2 = 0.0
    j2 = Counter(zip(source_past, target_past, target_future))
    m2 = Counter(zip(source_past, target_past))
    for (sp, tp, tf), c in j2.items():
        pj = c / n
        pm = m2[(sp, tp)] / n
        h2 -= pj * math.log(pj / pm)
    return h1 - h2


def simulate(n_comp, step_fn, steps=STEPS, seed=SEED):
    rng = random.Random(seed)
    state = tuple(rng.randint(0, 1) for _ in range(n_comp))
    traj = [state]
    for _ in range(steps - 1):
        state = step_fn(state, rng)
        traj.append(state)
    return traj


def comp_trace(traj, comps):
    out = []
    for t in traj:
        val = 0
        for j, i in enumerate(sorted(comps)):
            val |= t[i] << j
        out.append(val)
    return out


# --- Diff ---
def diff_score(traj, n):
    seq = [sum(t[i] << i for i in range(n)) for t in traj]
    return entropy(seq)


# --- Int（跨块互信息近似）---
def integration_score(traj, n):
    best = 0.0
    for r in range(1, 1 << n):
        B1 = [i for i in range(n) if (r >> i) & 1]
        if not B1 or len(B1) == n:
            continue
        B2 = [i for i in range(n) if i not in B1]
        o1 = comp_trace(traj, B1)
        o2 = comp_trace(traj, B2)
        mi = mutual_information(o1, o2)
        best = max(best, mi)
    return best


# --- SelBroadcast ---
def sel_broadcast_score(traj, n):
    for r in range(1, 1 << n):
        I = [i for i in range(n) if (r >> i) & 1]
        if len(I) < 2:
            continue
        J_all = [i for i in range(n) if i not in I]
        if len(J_all) < 2:
            continue
        for rj in range(1, 1 << len(J_all)):
            J = [J_all[k] for k in range(len(J_all)) if (rj >> k) & 1]
            if len(J) < 2 or len(J) > 3:
                continue
            o_I = comp_trace(traj, I)
            if entropy(o_I) < THETA_SRC:
                continue
            te_ok = True
            te_vals = {}
            for j in J:
                o_j = comp_trace(traj, [j])
                te = transfer_entropy(o_I[:-1], o_j[:-1], o_j[1:])
                te_vals[j] = te
                if te < THETA_TE:
                    te_ok = False
                    break
            if not te_ok:
                continue
            distinct_ok = True
            for a, b in itertools.combinations(J, 2):
                oa = comp_trace(traj, [a])
                ob = comp_trace(traj, [b])
                mi = mutual_information(oa, ob)
                if mi > THETA_F * max(entropy(oa), entropy(ob), EPS) and mi > EPS:
                    distinct_ok = False
                    break
            if not distinct_ok:
                continue
            bg_pool = [i for i in range(n) if i not in J and i not in I]
            all_bg = list(itertools.combinations(bg_pool, len(I)))
            if len(all_bg) > 6:
                rng = random.Random(SEED)
                rng.shuffle(all_bg)
                all_bg = all_bg[:6]
            sel_ok = True
            for j in J:
                o_j = comp_trace(traj, [j])
                te_main = te_vals[j]
                bg_tes = []
                for K in all_bg:
                    o_k = comp_trace(traj, K)
                    bg = transfer_entropy(o_k[:-1], o_j[:-1], o_j[1:])
                    bg_tes.append(bg)
                med = sorted(bg_tes)[len(bg_tes) // 2] if bg_tes else 0.0
                ratio = float("inf") if med < EPS else te_main / med
                if ratio < 1.0:
                    sel_ok = False
                    break
            if not sel_ok:
                continue
            cov = len(set(I) | set(J)) / n
            if cov < THETA_C:
                continue
            return 1
    return 0


# --- SM ---
def sm_score(traj, n, M_comps, Y_comps):
    o_m = comp_trace(traj, M_comps)
    o_y = comp_trace(traj, Y_comps)
    h_y = entropy(o_y)
    if h_y < EPS:
        return 0.0
    mi_same = mutual_information(o_m, o_y)
    mi_lag = mutual_information(o_m[1:], o_y[:-1])
    mi_my = max(mi_same, mi_lag)
    selfrep = mi_my / h_y
    mi_use = mutual_information(o_m[:-1], o_y[1:])
    if (mi_my > 0.99 * h_y) and (entropy(o_m) > 0.99 * h_y):
        return 0.0  # 平凡复制
    if selfrep < THETA_M:
        return 0.0
    if mi_use < EPS:
        return 0.0
    return 1.0


# ============================================================
# §2 系统
# ============================================================

def make_f1():
    def step(state, rng):
        c = state[0] + 2 * state[1] + 4 * state[2]
        j1, j2, fb = state[3], state[4], state[5]
        nc = (c + 1 + fb) % 8
        nj1 = (c >> 0) & 1 if rng.random() < 0.8 else rng.randint(0, 1)
        nj2 = (c >> 1) & 1 if rng.random() < 0.8 else rng.randint(0, 1)
        nfb = rng.randint(0, 1)
        return ((nc >> 0) & 1, (nc >> 1) & 1, (nc >> 2) & 1, nj1, nj2, nfb)
    return simulate(6, step), 6


def make_f3():
    def step(state, rng):
        i0, a, b, c, d, e, f = state
        ni = rng.randint(0, 1)
        na = i0 if rng.random() < 0.8 else rng.randint(0, 1)
        nb = a if rng.random() < 0.8 else rng.randint(0, 1)
        nc = b if rng.random() < 0.8 else rng.randint(0, 1)
        nd = b if rng.random() < 0.8 else rng.randint(0, 1)
        ne = b if rng.random() < 0.8 else rng.randint(0, 1)
        nf = b if rng.random() < 0.8 else rng.randint(0, 1)
        return (ni, na, nb, nc, nd, ne, nf)
    return simulate(7, step), 7


def make_f8():
    def step(state, rng):
        y1, y2, m1, m2 = state
        nm1 = y1 if rng.random() < 0.9 else rng.randint(0, 1)
        nm2 = y2 if rng.random() < 0.9 else rng.randint(0, 1)
        ny1 = (y1 ^ m1) if rng.random() < 0.6 else (y1 ^ y2) if rng.random() < 0.5 else rng.randint(0, 1)
        ny2 = (y2 ^ m2) if rng.random() < 0.6 else y1 if rng.random() < 0.5 else rng.randint(0, 1)
        return (ny1, ny2, nm1, nm2)
    return simulate(4, step), 4


def make_f9():
    """F9 伪自模型：状态估计 + 反馈控制（SM 是否只是控制理论?）。

    Sensor(S) → Estimator(M=状态估计) → Actuator(A, 受 M 控制) → 反馈 Sensor。
    M 是"自身状态估计"——SM 判据若把 F9 判过，说明 SM≈state estimation。
    """
    def step(state, rng):
        s, m1, m2, a1, a2 = state
        # Sensor：环境输入 + 状态
        ns = rng.randint(0, 1)
        # Estimator M：估计自身状态（读 s 和 a）
        nm1 = s if rng.random() < 0.85 else rng.randint(0, 1)
        nm2 = a1 if rng.random() < 0.85 else rng.randint(0, 1)
        # Actuator：受 M 控制
        na1 = m1 if rng.random() < 0.8 else rng.randint(0, 1)
        na2 = m2 if rng.random() < 0.8 else rng.randint(0, 1)
        return (ns, nm1, nm2, na1, na2)
    return simulate(5, step), 5


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 72)
    print("Layer 2 — 四要件合取 CS' = Int ∧ Diff ∧ SB ∧ SM")
    print("完整向量 C(S) = (Int, Diff, SB, SM)")
    print("=" * 72)

    systems = [
        ("F1 计数控制器", make_f1, 6, [3, 4], [0, 1, 2]),
        ("F3 纯前馈", make_f3, 7, [1, 2], [0, 4, 5, 6]),
        ("F8 表征+因果使用", make_f8, 4, [2, 3], [0, 1]),
        ("F9 伪自模型(状态估计)", make_f9, 5, [1, 2], [0, 3, 4]),
    ]

    results = []
    for name, maker, n, M_c, Y_c in systems:
        traj = maker()[0]
        int_v = integration_score(traj, n)
        diff_v = diff_score(traj, n)
        sb_v = sel_broadcast_score(traj, n)
        sm_v = sm_score(traj, n, M_c, Y_c)
        cs4 = 1 if (int_v > 0 and diff_v >= 3 and sb_v == 1 and sm_v == 1) else 0
        results.append((name, int_v, diff_v, sb_v, sm_v, cs4))
        print(f"\n--- {name} (N={n}) ---")
        print(f"  C(S) = (Int={int_v:.3f}, Diff={diff_v:.2f}, SB={sb_v}, SM={sm_v})")
        print(f"  CS' = {'✅ 1' if cs4 else '❌ 0'}")

    print("\n" + "=" * 72)
    print("汇总:")
    for name, int_v, diff_v, sb_v, sm_v, cs4 in results:
        print(f"  {name:28s}: Int={int_v:.2f} Diff={diff_v:.2f} SB={sb_v} SM={sm_v} → CS'={cs4}")
    print("=" * 72)
    print("判定: F1=1→情况B(四要件仍不够)；F1=0∧F3=0∧F8=1→情况A(SM提高区分力)")
    print("=" * 72)

    # 复制攻击
    print("\n" + "=" * 72)
    print("复制攻击：S (F8) vs S⊕S")
    traj_s = make_f8()[0]
    n_s = 4
    def step_copy(state, rng):
        a0, a1, a2, a3, b0, b1, b2, b3 = state
        def inner(y1, y2, m1, m2):
            nm1 = y1 if rng.random() < 0.9 else rng.randint(0, 1)
            nm2 = y2 if rng.random() < 0.9 else rng.randint(0, 1)
            ny1 = (y1 ^ m1) if rng.random() < 0.6 else (y1 ^ y2) if rng.random() < 0.5 else rng.randint(0, 1)
            ny2 = (y2 ^ m2) if rng.random() < 0.6 else y1 if rng.random() < 0.5 else rng.randint(0, 1)
            return (ny1, ny2, nm1, nm2)
        return inner(a0, a1, a2, a3) + inner(b0, b1, b2, b3)
    traj_s2 = simulate(8, step_copy)
    for label, traj, n, M_c, Y_c in [
        ("S (F8)", traj_s, 4, [2, 3], [0, 1]),
        ("S⊕S", traj_s2, 8, [2, 3, 6, 7], [0, 1, 4, 5]),
    ]:
        int_v = integration_score(traj, n)
        diff_v = diff_score(traj, n)
        sb_v = sel_broadcast_score(traj, n)
        sm_v = sm_score(traj, n, M_c, Y_c)
        cs4 = 1 if (int_v > 0 and diff_v >= 3 and sb_v == 1 and sm_v == 1) else 0
        print(f"  {label:8s}: Int={int_v:.3f} Diff={diff_v:.2f} SB={sb_v} SM={sm_v} → CS'={cs4}")
    print("  定位膨胀维: 看 Diff 是否随复制涨（S→S⊕S）")
    print("=" * 72)


if __name__ == "__main__":
    main()
