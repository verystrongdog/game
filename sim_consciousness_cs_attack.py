"""
Layer 2 — CS 合取攻击测试（F1-F6 + 同构复制）
==================================================
研讨产物（纯学术，不入游戏正典）。

GPT 第十一份：13 个单项测试 ≠ CS 已验证。攻击 CS = Int ∧ Diff ∧ SelBroadcast 合取。

F1-F6（负类测试集，要求 CS=0）：
  F1 计数器调制器（最危险）——计数器 + 多目标广播 + 反馈
  F2 纯随机强耦合——高熵 + 耦合 + 广播
  F3 大型前馈计算图——无反馈
  F4 通信总线——广播到多目标 + 反馈
  F5 重复模块网络——局部结构复制膨胀
  F6 工程控制器——传感器→控制器→执行器 + 门控

附加：同构复制测试 S′=S⊕S（无相互作用）→ CS(S′)=?

每个系统记录 (Int, Diff, SelBroadcast, CS)。

实现：随机 Markov 核模拟（框架允许 P 随机；SelBroadcast 必须在随机系统上测——
确定性周期系统 TE 无法区分传播强度，v2 教训）。
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
STEPS = 4000
SEED = 42


# ============================================================
# §1 通用组件（复用三测试脚本逻辑）
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
    n = len(target_future)
    h_cond_target = 0.0
    j1 = Counter(zip(target_past, target_future))
    m1 = Counter(target_past)
    for (tp, tf), c in j1.items():
        pj = c / n
        pm = m1[tp] / n
        h_cond_target -= pj * math.log(pj / pm)
    h_cond_both = 0.0
    j2 = Counter(zip(source_past, target_past, target_future))
    m2 = Counter(zip(source_past, target_past))
    for (sp, tp, tf), c in j2.items():
        pj = c / n
        pm = m2[(sp, tp)] / n
        h_cond_both -= pj * math.log(pj / pm)
    return h_cond_target - h_cond_both


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


def diff_score(traj, n):
    """Diff = H(O_t)，O = 全状态（身份观测）。"""
    seq = [sum(t[i] << i for i in range(n)) for t in traj]
    return entropy(seq)


def integration_kl_approx(traj, n, partition):
    """Int 近似（轨迹版）：E_μ[ KL(P(·|y) ‖ P_cut(·|y)) ]。

    简化：对轨迹上每个状态 y，计算当前一步转移与"cut 后因子化转移"的 KL，
    用经验条件概率估计。第一版：用确定性/经验转移的简化近似——
    用 互信息 I(Y_{t+1}; Y_t) 减去 cut 后的信息（近似）。
    """
    # 真实实现需要转移核估计；这里用"跨 partition 的互信息"作 Int 代理
    #（GPT 的单位测试已确认 min-over-partition KL 的判别力，此处用跨块互信息近似）
    B1, B2 = partition
    seq = [sum(t[i] << i for i in range(n)) for t in traj]
    # I(Y_{B1,t+1}; Y_{B2,t} | Y_{B1,t})：B2 对 B1 未来的影响（跨块耦合）
    # 简化代理：I(Y_{B1}; Y_{B2}) 联合熵 vs 独立熵（静态整合近似）
    o_b1 = comp_trace(traj, B1)
    o_b2 = comp_trace(traj, B2)
    mi = mutual_information(o_b1, o_b2)
    return mi


def integration_score(traj, n):
    """Int = max over 二分的跨块互信息（正：有整合）。"""
    best = 0.0
    best_pi = None
    for r in range(1, 1 << n):
        B1 = [i for i in range(n) if (r >> i) & 1]
        if not B1 or len(B1) == n:
            continue
        B2 = [i for i in range(n) if i not in B1]
        mi = integration_kl_approx(traj, n, (B1, B2))
        if mi > best:
            best = mi
            best_pi = (B1, B2)
    return best, best_pi


def sel_broadcast_score(traj, n):
    """SelBroadcast：存在 (I, J) 满足五组件 → 1/0。"""
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
            te_vals = {}
            te_ok = True
            for j in J:
                o_j = comp_trace(traj, [j])
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
                oa = comp_trace(traj, [a])
                ob = comp_trace(traj, [b])
                mi = mutual_information(oa, ob)
                if mi > THETA_F * max(entropy(oa), entropy(ob), EPS) and mi > EPS:
                    distinct_ok = False
                    break
            if not distinct_ok:
                continue
            # Selectivity（背景排除 I, J）
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
                if med < EPS:
                    ratio = float("inf")
                else:
                    ratio = te_main / med
                if ratio < 1.0:
                    sel_ok = False
                    break
            if not sel_ok:
                continue
            cov = len(set(I) | set(J)) / n
            if cov < THETA_C:
                continue
            return 1  # 找到一组即可
    return 0


# ============================================================
# §2 F1-F6 系统
# ============================================================

def make_f1():
    """F1 计数器调制器（最危险）：计数器 C(3bit) + 多目标广播 + 反馈。"""
    def step(state, rng):
        # 元件 0-2: 计数器 (3bit)；3,4: 目标 J；5: 反馈
        c = state[0] + 2 * state[1] + 4 * state[2]
        j1, j2, fb = state[3], state[4], state[5]
        nc = (c + 1 + fb) % 8          # 计数器 + 反馈调制
        nj1 = (c >> 0) & 1 if rng.random() < 0.8 else rng.randint(0, 1)  # 读计数器低位
        nj2 = (c >> 1) & 1 if rng.random() < 0.8 else rng.randint(0, 1)  # 读计数器次低位
        nfb = rng.randint(0, 1)        # 反馈噪声
        return ((nc >> 0) & 1, (nc >> 1) & 1, (nc >> 2) & 1, nj1, nj2, nfb)
    return simulate(6, step), 6


def make_f2():
    """F2 纯随机强耦合：A,B 耦合 + A,B→C,D + C,D→A,B + 大噪声。"""
    def step(state, rng):
        a, b, c, d = state
        na = (a ^ b) if rng.random() < 0.5 else rng.randint(0, 1)
        nb = (a ^ b) if rng.random() < 0.5 else rng.randint(0, 1)
        nc = a if rng.random() < 0.5 else rng.randint(0, 1)
        nd = b if rng.random() < 0.5 else rng.randint(0, 1)
        return (na, nb, nc, nd)
    return simulate(4, step), 4


def make_f3():
    """F3 纯前馈：I → A → B → C,D,E,F（无反馈）。"""
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


def make_f4():
    """F4 通信总线：Bus 复制给 J1..J3 + J 反馈 Bus。"""
    def step(state, rng):
        bus, j1, j2, j3 = state
        nbus = (bus ^ j1 ^ j2 ^ j3) if rng.random() < 0.5 else rng.randint(0, 1)
        nj1 = bus if rng.random() < 0.8 else rng.randint(0, 1)
        nj2 = bus if rng.random() < 0.8 else rng.randint(0, 1)
        nj3 = bus if rng.random() < 0.8 else rng.randint(0, 1)
        return (nbus, nj1, nj2, nj3)
    return simulate(4, step), 4


def make_f5():
    """F5 重复模块：M1(0,1) 与 M2(2,3) 完全相同模块，无互连。"""
    def step(state, rng):
        a1, b1, a2, b2 = state
        na1 = a1 if rng.random() < 0.5 else rng.randint(0, 1)
        nb1 = a1 if rng.random() < 0.5 else rng.randint(0, 1)
        na2 = a2 if rng.random() < 0.5 else rng.randint(0, 1)
        nb2 = a2 if rng.random() < 0.5 else rng.randint(0, 1)
        return (na1, nb1, na2, nb2)
    return simulate(4, step), 4


def make_f6():
    """F6 工程控制器：Sensor → Controller → Actuator ×2 + 门控 + 记忆。"""
    def step(state, rng):
        s, ctrl, act1, act2, gate, mem = state
        ns = rng.randint(0, 1)
        nctrl = s if rng.random() < 0.7 else (ctrl ^ mem) if rng.random() < 0.5 else rng.randint(0, 1)
        nact1 = ctrl if (rng.random() < 0.9 if gate == 1 else 0.2) else rng.randint(0, 1)
        nact2 = ctrl if (rng.random() < 0.9 if gate == 1 else 0.2) else rng.randint(0, 1)
        ngate = rng.randint(0, 1)
        nmem = ctrl
        return (ns, nctrl, nact1, nact2, ngate, nmem)
    return simulate(6, step), 6


# ============================================================
# §3 同构复制测试
# ============================================================

def make_copy_test():
    """同构复制：S（满足 CS 的系统，用 E2 广播结构）与 S′ = S ⊕ S（无互连）。"""
    def step1(state, rng):
        x0, x1, x2, x3 = state
        nx0 = rng.randint(0, 1)
        nx1 = rng.randint(0, 1)
        nx2 = x0 if rng.random() < 0.8 else rng.randint(0, 1)
        nx3 = x1 if rng.random() < 0.8 else rng.randint(0, 1)
        return (nx0, nx1, nx2, nx3)
    traj_s = simulate(4, step1)
    def step2(state, rng):
        a0, a1, a2, a3, b0, b1, b2, b3 = state
        # 两个独立副本，无互连
        na0 = rng.randint(0, 1)
        na1 = rng.randint(0, 1)
        na2 = a0 if rng.random() < 0.8 else rng.randint(0, 1)
        na3 = a1 if rng.random() < 0.8 else rng.randint(0, 1)
        nb0 = rng.randint(0, 1)
        nb1 = rng.randint(0, 1)
        nb2 = b0 if rng.random() < 0.8 else rng.randint(0, 1)
        nb3 = b1 if rng.random() < 0.8 else rng.randint(0, 1)
        return (na0, na1, na2, na3, nb0, nb1, nb2, nb3)
    traj_s2 = simulate(8, step2)
    return traj_s, traj_s2


# ============================================================
# §4 主流程
# ============================================================

def main():
    print("=" * 70)
    print("Layer 2 — CS 合取攻击测试（F1-F6 + 同构复制）")
    print("CS = Int ∧ Diff ≥ 3bit ∧ SelBroadcast")
    print("=" * 70)

    tests = [
        ("F1 计数器调制器", make_f1, "应拒绝(无意识)"),
        ("F2 纯随机强耦合", make_f2, "应拒绝"),
        ("F3 纯前馈图", make_f3, "应拒绝"),
        ("F4 通信总线", make_f4, "应拒绝"),
        ("F5 重复模块", make_f5, "应拒绝"),
        ("F6 工程控制器", make_f6, "应拒绝"),
    ]

    results = []
    for name, maker, expect in tests:
        traj, n = maker()
        diff = diff_score(traj, n)
        int_val, best_pi = integration_score(traj, n)
        sb = sel_broadcast_score(traj, n)
        cs = 1 if (int_val > 0 and diff >= 3 and sb == 1) else 0
        results.append((name, int_val, diff, sb, cs))
        print(f"\n--- {name} (N={n}) [{expect}] ---")
        print(f"  Int={int_val:.4f}(>0: {'✅' if int_val>0 else '❌'})  "
              f"Diff={diff:.3f}bit(≥3: {'✅' if diff>=3 else '❌'})  "
              f"SelBroadcast={'✅' if sb else '❌'}")
        print(f"  CS = {'✅ 通过（反例！）' if cs else '❌ 拒绝'}")

    print("\n" + "=" * 70)
    print("汇总:")
    for name, int_val, diff, sb, cs in results:
        verdict = "❌ 拒绝" if cs == 0 else "⚠️ **反例（CS=1）**"
        print(f"  {name:20s}: Int={int_val:.2f} Diff={diff:.2f} SB={sb} → {verdict}")
    print("=" * 70)

    # 同构复制测试
    print("\n" + "=" * 70)
    print("同构复制测试：S 与 S′ = S ⊕ S（无互连）")
    traj_s, traj_s2 = make_copy_test()
    diff_s = diff_score(traj_s, 4)
    int_s, _ = integration_score(traj_s, 4)
    sb_s = sel_broadcast_score(traj_s, 4)
    cs_s = 1 if (int_s > 0 and diff_s >= 3 and sb_s == 1) else 0
    diff_s2 = diff_score(traj_s2, 8)
    int_s2, _ = integration_score(traj_s2, 8)
    sb_s2 = sel_broadcast_score(traj_s2, 8)
    cs_s2 = 1 if (int_s2 > 0 and diff_s2 >= 3 and sb_s2 == 1) else 0
    print(f"  S :  Int={int_s:.3f} Diff={diff_s:.2f} SB={sb_s} → CS={cs_s}")
    print(f"  S′:  Int={int_s2:.3f} Diff={diff_s2:.2f} SB={sb_s2} → CS={cs_s2}")
    print(f"  解读: S={cs_s} → S′={cs_s2}（1=仍算候选 / 0=复制不膨胀 / 双实例=需要 C(S) 升级）")
    print("=" * 70)


if __name__ == "__main__":
    main()
