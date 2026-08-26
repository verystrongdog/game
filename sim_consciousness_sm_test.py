"""
Layer 2 — Self-Model SM(S) 测试（GPT 第十二份）
==================================================
研讨产物（纯学术，不入游戏正典）。

GPT 裁决：缺失维度 = Self-Modeling（非"自指"——避免循环），纯结构可计算定义。

  SM(S) = SelfRep(S) ∧ SelfUse(S)
    SelfRep:  I(M_t; Y_t) > θ_M        M 携带系统自身状态信息
    SelfUse:  CausalEffect(M_t → Y_{t+1}) > 0   M 因果作用于系统未来
  非平凡性:  M_t = f(Y_t)，f 非平凡粗粒化（非 M = Y 复制）

四系统测试：
  F1 计数控制器      → SM = 0
  F3 纯前馈          → SM = 0
  F7 纯表征不因果使用 → 低/拒绝
  F8 表征+因果使用    → 高/通过

工作方法（GPT 警告）：先独立测 SM，不直接写 CS = Int∧Diff∧SB∧SM。
"""

import itertools
import math
import random
from collections import Counter

EPS = 1e-12
THETA_M = 0.3        # SelfRep 阈值（I(M;Y) 上界比例）
STEPS = 6000
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


def causal_effect_trace(source_trace, target_next_trace):
    """CausalEffect(M → Y') 近似：I(M_t; Y_{t+1})（源 t 对目标 t+1 的信息）。

    用互信息作因果作用代理（第一版；干预验证后续）。
    """
    return mutual_information(source_trace[:-1], target_next_trace[1:])


def sm_score(traj, n, M_comps, Y_comps):
    """SM = SelfRep ∧ SelfUse。

    SelfRep:  max(I(M_t;Y_t), I(M_t;Y_{t-1})) / H(Y) > θ_M
              —— M 携带 Y 的信息（含跨时刻结构编码；滞后表征也算）
    SelfUse:  I(M_t; Y_{t+1}) > 0（M 因果作用于 Y 未来）
    非平凡性: M 与 Y 不完全相同（I < H(Y) 且 M 熵 > 0）
    """
    o_m = comp_trace(traj, M_comps)
    o_y = comp_trace(traj, Y_comps)
    h_y = entropy(o_y)
    if h_y < EPS:
        return 0.0, {"selfrep": 0.0, "selfuse": 0.0, "reason": "Y 无熵"}
    # SelfRep：同刻与错位取 max
    mi_same = mutual_information(o_m, o_y)
    mi_lag = mutual_information(o_m[1:], o_y[:-1])
    mi_my = max(mi_same, mi_lag)
    selfrep = mi_my / h_y if h_y > EPS else 0.0
    # SelfUse：M_t → Y_{t+1}
    mi_use = causal_effect_trace(o_m, o_y)
    # 非平凡性：M ≠ Y（若 I(M;Y) = H(Y) = H(M)，M 是 Y 的复制 → 平凡）
    trivial = (mi_my > 0.99 * h_y) and (entropy(o_m) > 0.99 * h_y)
    if trivial:
        return 0.0, {"selfrep": selfrep, "selfuse": mi_use, "reason": "平凡复制 M=Y"}
    if selfrep < THETA_M:
        return 0.0, {"selfrep": selfrep, "selfuse": mi_use, "reason": f"SelfRep={selfrep:.3f}<θ_M"}
    if mi_use < EPS:
        return 0.0, {"selfrep": selfrep, "selfuse": mi_use, "reason": "SelfUse=0（仅描述不作用）"}
    return 1.0, {"selfrep": selfrep, "selfuse": mi_use, "reason": "通过"}


# ============================================================
# §2 四系统
# ============================================================

def make_f1():
    """F1 计数控制器：计数器 C(3bit) → J 多目标 + 反馈。无自我模型。"""
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
    """F3 纯前馈：I → A → B → C,D,E,F。无反馈无自模型。"""
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


def make_f7():
    """F7 纯表征不因果使用：Y 有结构动力学，M 表征 Y（SelfRep 高）但 M 不作用 Y'。

    Y = 2 元件耦合振荡（有结构）；M = Y 的粗粒化（读取，不写回）。
    """
    def step(state, rng):
        y1, y2, m1, m2 = state
        # Y 有结构：耦合振荡（y1,y2 相互影响）
        ny1 = (y1 ^ y2) if rng.random() < 0.8 else rng.randint(0, 1)
        ny2 = y1 if rng.random() < 0.8 else rng.randint(0, 1)
        # M 读 Y（纯表征，粗粒化：m1 = y1, m2 = y1^y2——不同函数）
        nm1 = y1 if rng.random() < 0.9 else rng.randint(0, 1)
        nm2 = (y1 ^ y2) if rng.random() < 0.9 else rng.randint(0, 1)
        # M 不作用于 Y'（Y 独立于 M 演化）
        return (ny1, ny2, nm1, nm2)
    return simulate(4, step), 4


def make_f8():
    """F8 表征+因果使用：Y 有结构，M 表征 Y（滞后编码）且 M 影响 Y'（自模型闭环）。

    修正（时序错位问题）：M 编码 Y 的滞后状态（M_t = Y_{t-1} 的结构），
    且 Y' 受 M 影响——形成真正的"模型参与动力学"闭环。
    """
    def step(state, rng):
        y1, y2, m1, m2 = state
        # M 编码 Y 的滞后结构（m1 存 y1 上一拍，m2 存 y2 上一拍——模型=过去状态的压缩）
        nm1 = y1 if rng.random() < 0.9 else rng.randint(0, 1)
        nm2 = y2 if rng.random() < 0.9 else rng.randint(0, 1)
        # Y' 受 M 影响（M 因果作用：用模型修正 Y 的演化）
        ny1 = (y1 ^ m1) if rng.random() < 0.6 else (y1 ^ y2) if rng.random() < 0.5 else rng.randint(0, 1)
        ny2 = (y2 ^ m2) if rng.random() < 0.6 else y1 if rng.random() < 0.5 else rng.randint(0, 1)
        return (ny1, ny2, nm1, nm2)
    return simulate(4, step), 4


# ============================================================
# §3 主流程
# ============================================================

def main():
    print("=" * 70)
    print("Layer 2 — Self-Model SM(S) 测试（GPT 第十二份）")
    print("SM = SelfRep(I(M;Y)) ∧ SelfUse(M→Y')")
    print("=" * 70)

    tests = [
        ("F1 计数控制器", make_f1, 6, [3, 4], [0, 1, 2], "SM=0"),
        ("F3 纯前馈", make_f3, 7, [1, 2], [0, 4, 5, 6], "SM=0"),
        ("F7 纯表征不因果使用", make_f7, 4, [2, 3], [0, 1], "低/拒"),
        ("F8 表征+因果使用", make_f8, 4, [2, 3], [0, 1], "高/过"),
    ]

    for name, maker, n, M_comps, Y_comps, expect in tests:
        traj = maker()[0]
        score, detail = sm_score(traj, n, M_comps, Y_comps)
        print(f"\n--- {name} (N={n}) [{expect}] ---")
        print(f"  SM = {score}  M={M_comps} Y={Y_comps}")
        print(f"  SelfRep={detail['selfrep']:.3f} SelfUse={detail['selfuse']:.4f} → {detail['reason']}")

    print("\n" + "=" * 70)
    print("预期: F1=0 / F3=0 / F7 低或拒 / F8 通过")
    print("=" * 70)


if __name__ == "__main__":
    main()
