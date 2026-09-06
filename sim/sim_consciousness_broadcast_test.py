"""
Layer 2 — Selective Broadcast SelBroadcast(S) 单位测试 v2（随机系统）
==================================================
研讨产物（纯学术，不入游戏正典）。

v1 教训（确定性周期系统不可行）：
  确定性振荡器对任何目标的 TE 都≈同值——无法区分"广播源"与"背景源"；
  且目标自预测（周期）时 TE(源→目标|目标过去) 天然趋零。
  → SelBroadcast 必须在随机系统上测试（框架允许：P 是随机 Markov kernel）。

GPT 第十份：SelBroadcast = Source ∧ MultiTarget ∧ InfoTransfer ∧ AntiConfounding ∧ Selectivity
  Source:        H(O_I) ≥ θ_src（源携带真信息）
  MultiTarget:   |J| ≥ 2
  InfoTransfer:  ∀j∈J: TE(I→j | j_past) ≥ θ_TE
  AntiConfounding: 条件化共同原因（TE ≠ 因果）
  Selectivity:   SelRatio = TE(I→J)/median(TE(K→J)) ≥ θ_S（背景源同大小）
  + FunctionalDistinct(J) ≥ θ_F（目标不可合并）
  + Coverage(I,J) ≥ θ_C

六测试（E1-E6）：
  E1 单目标      I→J₁                 应失败（|J|<2）
  E2 真双目标广播 I→J₁, I→J₂ 独立使用   应通过
  E3 复制中继    I→R→J₁,J₂            应失败或明显降低（FunctionalDistinct）
  E4 共同原因    C→I, C→J₁, C→J₂      应失败（AntiConfounding）
  E5 固定拓扑    I→J₁,J₂ 无门控        通过（无 Selectivity 惩罚）
  E6 状态依赖    Q 门控调制            应通过（有 Selectivity）

随机系统设计原则：
  源 I = 高熵随机过程（每步随机翻转）
  目标 J = 未来不可自预测 + 由 I 驱动（J_{t+1} = f(I_t) + 自身噪声）
  背景 K = 同大小但与 J 无关（TE ≈ 0）
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
STEPS = 4000  # 随机系统需要长轨迹
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


# ============================================================
# §2 测试系统（随机 Markov 核，返回模拟函数）
# ============================================================

def simulate_system(n_comp, step_fn, steps=STEPS, seed=SEED):
    """模拟随机系统。step_fn(state_tuple, rng) → next_state_tuple。"""
    rng = random.Random(seed)
    state = tuple(rng.randint(0, 1) for _ in range(n_comp))
    traj = [state]
    for _ in range(steps - 1):
        state = step_fn(state, rng)
        traj.append(state)
    return traj


def comp_trace_from_traj(traj, comps):
    out = []
    for t in traj:
        val = 0
        for j, i in enumerate(sorted(comps)):
            val |= t[i] << j
        out.append(val)
    return out


def make_e1():
    """E1 单目标：I={0,1} 高熵源 → J={2}。应失败（|J|<2）。"""
    def step(state, rng):
        x0, x1, x2 = state
        nx0 = rng.randint(0, 1)         # 源高熵
        nx1 = rng.randint(0, 1)
        nx2 = x0 if rng.random() < 0.8 else rng.randint(0, 1)  # 目标受 I 驱动
        return (nx0, nx1, nx2)
    return simulate_system(3, step), 3


def make_e2():
    """E2 真双目标广播：I={0,1} → J={2,3}，目标独立受驱动 + 背景 {4,5}。应通过。"""
    def step(state, rng):
        x0, x1, x2, x3, x4, x5 = state
        nx0 = rng.randint(0, 1)
        nx1 = rng.randint(0, 1)
        nx2 = x0 if rng.random() < 0.8 else rng.randint(0, 1)  # 目标2受x0驱动
        nx3 = x1 if rng.random() < 0.8 else rng.randint(0, 1)  # 目标3受x1驱动
        nx4 = rng.randint(0, 1)         # 背景源（与 J 无关）
        nx5 = rng.randint(0, 1)
        return (nx0, nx1, nx2, nx3, nx4, nx5)
    return simulate_system(6, step), 6


def make_e3():
    """E3 复制中继：I={0,1} → R={2} → J={3,4}（J 复制 R）。应失败（目标冗余）。"""
    def step(state, rng):
        x0, x1, x2, x3, x4 = state
        nx0 = rng.randint(0, 1)
        nx1 = rng.randint(0, 1)
        nx2 = x0 if rng.random() < 0.8 else rng.randint(0, 1)  # 中继
        nx3 = x2                                                 # 复制中继
        nx4 = x2                                                 # 复制中继
        return (nx0, nx1, nx2, nx3, nx4)
    return simulate_system(5, step), 5


def make_e4():
    """E4 共同原因：C={0} → I={1}, J={2,3}。应失败（AntiConfounding）。"""
    def step(state, rng):
        x0, x1, x2, x3 = state
        nx0 = rng.randint(0, 1)         # C 高熵
        nx1 = x0                         # I 跟随 C
        nx2 = x0                         # J₁ 跟随 C
        nx3 = x0                         # J₂ 跟随 C
        return (nx0, nx1, nx2, nx3)
    return simulate_system(4, step), 4


def make_e5():
    """E5 固定拓扑：I={0,1} → J={2,3} 固定广播 + 背景 {4,5}。应通过（固定广播算 Broadcast）。"""
    def step(state, rng):
        x0, x1, x2, x3, x4, x5 = state
        nx0 = rng.randint(0, 1)
        nx1 = rng.randint(0, 1)
        nx2 = x0 if rng.random() < 0.8 else rng.randint(0, 1)
        nx3 = x1 if rng.random() < 0.8 else rng.randint(0, 1)
        nx4 = rng.randint(0, 1)
        nx5 = rng.randint(0, 1)
        return (nx0, nx1, nx2, nx3, nx4, nx5)
    return simulate_system(6, step), 6


def make_e6():
    """E6 状态依赖广播：Q 门控。I={0,1} → J={2,3}，仅当 Q=1 时强驱动。应通过。"""
    def step(state, rng):
        x0, x1, x2, x3, x4 = state
        nx0 = rng.randint(0, 1)
        nx1 = rng.randint(0, 1)
        # Q = x4：Q=1 时强驱动，Q=0 时弱
        p = 0.9 if x4 == 1 else 0.2
        nx2 = x0 if rng.random() < p else rng.randint(0, 1)
        nx3 = x1 if rng.random() < p else rng.randint(0, 1)
        nx4 = rng.randint(0, 1)         # Q 高熵
        return (nx0, nx1, nx2, nx3, nx4)
    return simulate_system(5, step), 5


# ============================================================
# §3 SelBroadcast 判定（轨迹版本）
# ============================================================

def sel_broadcast_check_traj(traj, n_comp):
    """对轨迹检查 SelBroadcast 五组件。"""
    results = []
    for r in range(1, 1 << n_comp):
        I = [i for i in range(n_comp) if (r >> i) & 1]
        if len(I) < 2:
            continue
        J_all = [i for i in range(n_comp) if i not in I]
        if len(J_all) < 2:
            continue
        for rj in range(1, 1 << len(J_all)):
            J = [J_all[k] for k in range(len(J_all)) if (rj >> k) & 1]
            if len(J) < 2 or len(J) > 3:
                continue
            o_I = comp_trace_from_traj(traj, I)
            # Source
            h_src = entropy(o_I)
            if h_src < THETA_SRC:
                continue
            # InfoTransfer
            te_ok = True
            te_vals = {}
            for j in J:
                o_j = comp_trace_from_traj(traj, [j])
                te = transfer_entropy(o_I[:-1], o_j[:-1], o_j[1:])
                te_vals[j] = te
                if te < THETA_TE:
                    te_ok = False
                    break
            if not te_ok:
                continue
            # FunctionalDistinct
            distinct_ok = True
            for a, b in itertools.combinations(J, 2):
                oa = comp_trace_from_traj(traj, [a])
                ob = comp_trace_from_traj(traj, [b])
                mi = mutual_information(oa, ob)
                if mi > THETA_F * max(entropy(oa), entropy(ob), EPS) and mi > EPS:
                    distinct_ok = False
                    break
            if not distinct_ok:
                continue
            # Selectivity（背景源排除 I, J）
            sel_ok = True
            sel_ratios = {}
            bg_pool = [i for i in range(n_comp) if i not in J and i not in I]
            all_bg = list(itertools.combinations(bg_pool, len(I)))
            if len(all_bg) > 6:
                rng = random.Random(SEED)
                rng.shuffle(all_bg)
                all_bg = all_bg[:6]
            for j in J:
                o_j = comp_trace_from_traj(traj, [j])
                te_main = te_vals[j]
                bg_tes = []
                for K in all_bg:
                    o_k = comp_trace_from_traj(traj, K)
                    bg = transfer_entropy(o_k[:-1], o_j[:-1], o_j[1:])
                    bg_tes.append(bg)
                med = sorted(bg_tes)[len(bg_tes) // 2] if bg_tes else 0.0
                if med < EPS:
                    # 背景零传播 → 完全选择性（比值饱和为 ∞，语义正确）
                    ratio = float("inf")
                else:
                    ratio = te_main / med
                sel_ratios[j] = ratio
                if ratio < 1.0:
                    sel_ok = False
                    break
            if not sel_ok:
                continue
            # Coverage
            cov = len(set(I) | set(J)) / n_comp
            if cov < THETA_C:
                continue
            results.append({
                "I": I, "J": J, "h_src": h_src,
                "te": te_vals, "sel_ratios": sel_ratios, "coverage": cov,
            })
    return results


# ============================================================
# §4 主流程
# ============================================================

def main():
    print("=" * 66)
    print("Layer 2 — SelBroadcast 六攻击测试 v2（随机系统）")
    print("=" * 66)

    tests = [
        ("E1 单目标", make_e1),
        ("E2 真双目标广播", make_e2),
        ("E3 复制中继", make_e3),
        ("E4 共同原因", make_e4),
        ("E5 固定拓扑", make_e5),
        ("E6 状态依赖广播", make_e6),
    ]

    for name, maker in tests:
        traj, n = maker()
        sb = sel_broadcast_check_traj(traj, n)
        print(f"\n--- {name} (N={n}) ---")
        if sb:
            first = sb[0]
            sr = first['sel_ratios']
            sr_disp = {k: ("∞" if v == float("inf") else round(v, 1)) for k, v in sr.items()}
            print(f"  ✅ 通过: I={first['I']} J={first['J']} "
                  f"源熵={first['h_src']:.3f} TE={ {k: round(v,3) for k,v in first['te'].items()} } "
                  f"SelRatio={sr_disp} 覆盖={first['coverage']:.2f}")
            if len(sb) > 1:
                print(f"  （共 {len(sb)} 组候选）")
        else:
            print(f"  ❌ 未通过（无候选）")

    print("\n" + "=" * 66)
    print("预期: E1 失败 / E2 通过 / E3 失败或降 / E4 失败 / E5 通过 / E6 通过")
    print("=" * 66)


if __name__ == "__main__":
    main()
