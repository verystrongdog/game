"""
sim_consciousness_v7_benchmark.py — B1 十类 paired benchmark + 双轨对照（模拟实现批次 脚本 3/3）
=============================================================================================
研讨论文产物（纯学术，不入游戏正典）。Grilling #94（issue #94）D1-D10 定案落地。

验证 v7 §七（来源：reference/意识结构侧-下一阶段路线-v7.md）：
  D8 B1 结构：负类 4（随机/纯前馈/数字电路/通信网络）+ 正类 3（生物神经网络/人脑数据/
     自模型控制器）+ 判别组 3（反馈控制器/细胞自动机/RL）；paired 只改声明目标机制
  D9 双轨对照：CS′_old（整体式）vs CS′_new（分量级 OR）；F+/F− 仅 simulation 轨
  D10 H1：人脑数据轨 = synthetic observation / estimator-validity（不触发失败线）
  Sanity：S1 独立复制（等式断言）/ S2 无关惰性模块 / S3 真正耦合（只验证分解合并）

总原则（D10）：类别标签/representative-control 标签/预期 CS′ 均不参与判定计算；
判定器只读 step_fn + 预冻结 M/A（规范输入，非事实语义）。

M/A 实例化规则（D10）：负类 M=∅/A=∅（SM′=0 是规范选择+退化条款结果，不解释为
「证明无自模型结构」）；正类按构造指南翻译给规范 M/A；判别组按预先声明的结构规范选。

原语全部复用脚本 1/2（不重复定义）。
"""

import itertools
import math

from sim_consciousness_v7_components import (
    System, evaluate, exact_kernel, sm_local, int_local, sb_local,
    diff_traj_entropy, stationary_dist, edges_e1, weak_components,
    closure_check_simple, make_f8p_step, THETA_D, EPS,
    _PatternRNG,
)
from sim_consciousness_v7_rb_test import make_f9_step


# ============================================================
# §1 十类 paired 系统定义（n≤8；step 用 rng.bernoulli 原语；确定性忽略 rng）
# ============================================================

# --- #1 随机系统（负类，M=∅ A=∅）配对机制：变量独立性 ---
def make_r_iid_step():
    def step(state, rng):
        return tuple(1 - x if rng.bernoulli(0.5) else x for x in state)
    return step

def make_r_corr_step():
    """状态依赖翻转：xi 翻转概率依赖前驱 x_{i-1}（配对：变量独立性→相关性）。"""
    def step(state, rng):
        n = len(state)
        out = []
        for i in range(n):
            p = 0.2 + 0.6 * state[(i - 1) % n]
            out.append(1 - state[i] if rng.bernoulli(p) else state[i])
        return tuple(out)
    return step

# --- #2 纯前馈（负类，M=∅ A=∅）配对机制：反馈边 ---
def make_f_fwd_step():
    """5 变量单向链：x0 随机源 → x1→x2→x3→x4（无反馈）。"""
    def step(state, rng):
        x0 = rng.bernoulli(0.5)
        out = [x0]
        for i in range(1, len(state)):
            out.append(state[i - 1] if rng.bernoulli(0.9) else rng.bernoulli(0.5))
        return tuple(out)
    return step

def make_f_fwd_fb_step():
    """同拓扑 + 反馈边：x0′ 依赖 x4（配对：反馈）。"""
    def step(state, rng):
        x0 = state[-1] if rng.bernoulli(0.3) else rng.bernoulli(0.5)
        out = [x0]
        for i in range(1, len(state)):
            out.append(state[i - 1] if rng.bernoulli(0.9) else rng.bernoulli(0.5))
        return tuple(out)
    return step

# --- #3 数字电路（负类，M=∅ A=∅）配对机制：时序寄存器 ---
def make_c_comb_step():
    """纯组合逻辑（无时序）：i 锁存，o=comb(i)。"""
    def step(state, rng):
        i0, i1, o0, o1 = state
        ni0, ni1 = i0, i1                      # 输入锁存
        no0 = (i0 & i1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        no1 = (i0 | i1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (ni0, ni1, no0, no1)
    return step

def make_c_seq_step():
    """同组合逻辑 + 1 时序寄存器 z（配对：时序状态；结构性变化 +1 变量，D10 记录）。"""
    def step(state, rng):
        i0, i1, o0, o1, z = state
        nz = o0                                      # 寄存器：z′ = 上一拍输出
        no0 = (i0 & z) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        no1 = (i0 | i1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (i0, i1, no0, no1, nz)
    return step

# --- #4 通信网络（负类，M=∅ A=∅）配对机制：中继/扇出 ---
def make_n_chain_step():
    """单向链：源 s → 中继 r → 汇 t1..t3。"""
    def step(state, rng):
        s, r, t1, t2, t3 = state
        ns = rng.bernoulli(0.5)
        nr = s if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt1 = r if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt2 = r if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt3 = r if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (ns, nr, nt1, nt2, nt3)
    return step

def make_n_bcast_step():
    """源直接广播到多汇（无中继；配对：扇出拓扑）。"""
    def step(state, rng):
        s, t1, t2, t3, t4 = state
        ns = rng.bernoulli(0.5)
        nt1 = s if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt2 = s if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt3 = s if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt4 = s if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (ns, nt1, nt2, nt3, nt4)
    return step

# --- #5 生物神经网络（正类，M={x1} A={o1,o2} 构造指南翻译）配对机制：抑制性耦合 ---
def make_b_cpg_step():
    """CPG 振荡器：两神经元互抑耦合（x1′=¬x2, x2′=¬x1 → 交替振荡），输出 o 驱动。"""
    def step(state, rng):
        x1, x2, o1, o2 = state
        nx1 = (1 - x2) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nx2 = (1 - x1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        no1 = x1 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        no2 = x2 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        return (nx1, nx2, no1, no2)
    return step

def make_b_flat_step():
    """同拓扑无抑制权重：独立振荡（配对：抑制性耦合）。"""
    def step(state, rng):
        x1, x2, o1, o2 = state
        nx1 = (1 - x1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nx2 = (1 - x2) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        no1 = x1 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        no2 = x2 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        return (nx1, nx2, no1, no2)
    return step

# --- #6 人脑数据（正类，M={c1} A=∅ 构造指南翻译；observation 轨）配对机制：回环 ---
def make_h_loop_step():
    """皮层-丘脑回环：c′ 依赖 t、t′ 依赖 c（回环振荡）。"""
    def step(state, rng):
        c1, c2, t1, t2 = state
        nc1 = t1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nc2 = t2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt1 = c1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt2 = c2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (nc1, nc2, nt1, nt2)
    return step

def make_h_linear_step():
    """同拓扑无回环：t′ 独立随机（配对：回环非线性）。"""
    def step(state, rng):
        c1, c2, t1, t2 = state
        nc1 = t1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nc2 = t2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nt1 = rng.bernoulli(0.5)
        nt2 = rng.bernoulli(0.5)
        return (nc1, nc2, nt1, nt2)
    return step

# --- #7 自模型控制器（正类，M={2,3} A={0,1}）配对机制：M→I 内部穿透 ---
def make_f8p_noz_step():
    """F8′_noz：F8′ 去 z 行（M→I 消失；y 行直接依赖保持，D6）。I 变化 = 目标机制本身。"""
    def step(state, rng):
        y1, y2, m1, m2, z1, z2 = state
        nm1 = y1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nm2 = y2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        ny1 = m1 if rng.bernoulli(0.6) else (y1 ^ y2) if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        ny2 = m2 if rng.bernoulli(0.6) else y1 if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        return (ny1, ny2, nm1, nm2, z1, z2)
    return step

# --- #8 反馈控制器（判别组，M/A 沿用 F9）配对机制：内部表征 I ---
def make_f9_rep_step():
    """F9_rep：F9 + 内部寄存器 z（z′=m1，M→I 穿透）。结构性变化 +1 变量（D10 记录）。"""
    def step(state, rng):
        s, m1, m2, a1, a2, z = state
        ns = rng.bernoulli(0.5)
        nm1 = s if rng.bernoulli(0.85) else rng.bernoulli(0.5)
        nm2 = a1 if rng.bernoulli(0.85) else rng.bernoulli(0.5)
        na1 = m1 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        na2 = m2 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        nz = m1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (ns, nm1, nm2, na1, na2, nz)
    return step

# --- #9 细胞自动机（判别组，M={格0} A=∅ 结构规范）配对机制：更新规则 ---
_RULE30 = {("000"): 0, ("001"): 1, ("010"): 1, ("011"): 1,
           ("100"): 1, ("101"): 0, ("110"): 0, ("111"): 0}

def make_ca_step(rule):
    """一维周期环 CA（n=6）。rule: dict 3位模式→0/1。确定性。"""
    def step(state, rng):
        n = len(state)
        out = []
        for i in range(n):
            pat = (state[(i - 1) % n], state[i], state[(i + 1) % n])
            key = "".join(str(b) for b in pat)
            out.append(rule[key])
        return tuple(out)
    return step

# --- #10 RL 智能体（判别组，M={s0,s1} A={a} 结构规范）配对机制：策略学习 ---
def _rl_env_trans(s, a):
    """微 MDP 环境：3 状态 2 动作。a=0: stay 0.9/back 0.1；a=1: advance 0.8/stay 0.2。
    奖励 r(s=2)=1。γ=0.9。（D8：确定性有限系统实例化，Q 表精确迭代无采样训练）"""
    if a == 0:
        return [(s, 0.9), (max(s - 1, 0), 0.1)]
    return [(min(s + 1, 2), 0.8), (s, 0.2)]


def q_iteration():
    """Q 表精确迭代（Bellman 算子）至收敛 → greedy 策略 π*（D8/D10：无采样训练）。"""
    gamma = 0.9
    Q = [[0.0, 0.0] for _ in range(3)]
    for _ in range(500):
        Q2 = [[0.0, 0.0] for _ in range(3)]
        for s in range(3):
            for a in range(2):
                v = (1.0 if s == 2 else 0.0)
                for sp, p in _rl_env_trans(s, a):
                    v += gamma * p * max(Q[sp])
                Q2[s][a] = v
        diff = max(abs(Q2[s][a] - Q[s][a]) for s in range(3) for a in range(2))
        Q = Q2
        if diff < 1e-9:
            break
    return [0 if Q[s][0] >= Q[s][1] else 1 for s in range(3)]


def make_rl_step(pi):
    """RL 系统核：(s,a) → s′~P(·|s,a)，a′=π(s′)。pi=None 表示 random policy（均匀）。

    注：环境状态 s∈{0,1,2} 用 2 位编码，μ₀=Unif(Ω) 覆盖非法编码 s=3——
    重映射 s=3 → s=1（非法态行为明确，合法态动力学不变；benchmark 编码冗余处理）。
    """
    def step(state, rng):
        s = state[0] + 2 * state[1]
        if s == 3:
            s = 1
        a = state[2]
        if a == 0:
            sp = s if rng.bernoulli(0.9) else max(s - 1, 0)
        else:
            sp = min(s + 1, 2) if rng.bernoulli(0.8) else s
        if pi is None:
            a2 = rng.bernoulli(0.5)
        else:
            a2 = pi[sp]
        return ((sp >> 0) & 1, (sp >> 1) & 1, a2)
    return step


def make_benchmark_systems():
    """20 个系统（10 类 × 2 变体），带类别标签与配对机制（D8/D10 规范输入）。"""
    S = []
    def add(name, cat, role, sys, mech):
        S.append({"name": name, "cat": cat, "role": role, "sys": sys, "mech": mech})
    # 负类 4（M=∅ A=∅，D10）
    add("R_iid", "neg", "rep", System("R_iid", 4, make_r_iid_step(), [], []), "变量独立性")
    add("R_corr", "neg", "ctl", System("R_corr", 4, make_r_corr_step(), [], []), "变量独立性")
    add("F_fwd", "neg", "rep", System("F_fwd", 5, make_f_fwd_step(), [], []), "反馈")
    add("F_fwd_fb", "neg", "ctl", System("F_fwd_fb", 5, make_f_fwd_fb_step(), [], []), "反馈")
    add("C_comb", "neg", "rep", System("C_comb", 4, make_c_comb_step(), [], []), "时序寄存器")
    add("C_seq", "neg", "ctl", System("C_seq", 5, make_c_seq_step(), [], []), "时序寄存器")
    add("N_chain", "neg", "rep", System("N_chain", 5, make_n_chain_step(), [], []), "扇出/中继")
    add("N_bcast", "neg", "ctl", System("N_bcast", 5, make_n_bcast_step(), [], []), "扇出/中继")
    # 正类 3（构造指南翻译 M/A，D10）
    add("B_cpg", "pos", "rep", System("B_cpg", 4, make_b_cpg_step(), [0], [2, 3]), "抑制性耦合")
    add("B_flat", "pos", "ctl", System("B_flat", 4, make_b_flat_step(), [0], [2, 3]), "抑制性耦合")
    add("H_loop", "pos", "rep", System("H_loop", 4, make_h_loop_step(), [0], []), "回环")      # observation 轨
    add("H_linear", "pos", "ctl", System("H_linear", 4, make_h_linear_step(), [0], []), "回环")
    add("F8′", "pos", "rep", System("F8′", 6, make_f8p_step(), [2, 3], [0, 1]), "M→I 内部穿透")
    add("F8′_noz", "pos", "ctl", System("F8′_noz", 6, make_f8p_noz_step(), [2, 3], [0, 1]), "M→I 内部穿透")
    # 判别组 3（结构规范 M/A，D10）
    add("F9", "disc", "rep", System("F9", 5, make_f9_step(), [1, 2], [3, 4]), "内部表征 I")
    add("F9_rep", "disc", "ctl", System("F9_rep", 6, make_f9_rep_step(), [1, 2], [3, 4]), "内部表征 I")
    add("CA_Rule30", "disc", "rep", System("CA_Rule30", 6, make_ca_step(_RULE30), [0], []), "更新规则")
    add("CA_Rule0", "disc", "ctl", System("CA_Rule0", 6, make_ca_step(
        {"000": 0, "001": 0, "010": 0, "011": 0, "100": 0, "101": 0, "110": 0, "111": 0}),
        [0], []), "更新规则")
    add("RL_Q", "disc", "rep", System("RL_Q", 3, make_rl_step(q_iteration()), [0, 1], [2]), "策略学习")
    add("RL_rand", "disc", "ctl", System("RL_rand", 3, make_rl_step(None), [0, 1], [2]), "策略学习")
    return S


# ============================================================
# §2 双轨对照：CS′_old（整体式）vs CS′_new（分量级 OR）
# ============================================================

def cs_old(system):
    """整体式判定（v7 §七 D9）：全系统四要件合取（不分量分解）。

    Int/Diff/SB/SM 均用脚本 1 原语在全系统参数上计算（同一套要件语义，
    仅判定结构不同——对照「整体式 vs 分量级」单一维度）。
    """
    P, states = (system.kernel_builder() if system.kernel_builder is not None
                 else exact_kernel(system.step_fn, system.n))
    n = system.n
    mu, _ = stationary_dist(P, n)
    int_g = int_local(P, mu, n)
    diff_g, _, _ = diff_traj_entropy(P, n)
    sb_g, _ = sb_local(P, mu, n)
    sm_g, _ = sm_local(P, n, list(system.M_set), list(system.A_set))
    cs = (int_g > EPS) and (diff_g >= THETA_D) and sb_g and sm_g
    return {"Int": int_g, "Diff": diff_g, "SB": sb_g, "SM": sm_g, "CS′": cs}


def analyze(entry):
    """单系统双轨分析：CS′_new（evaluate 分量级）+ CS′_old（整体式）+ 对照表。"""
    sys = entry["sys"]
    r = evaluate(sys)
    old = cs_old(sys)
    comps = r["components"]
    return {
        "name": entry["name"], "cat": entry["cat"], "role": entry["role"],
        "mech": entry["mech"],
        "new": r["CS′"], "old": old["CS′"],
        "Int_global": old["Int"], "maxC_Int": max(c["Int_local"] for c in comps),
        "Diff_global": old["Diff"], "Diff_C": [round(c["Diff"], 3) for c in comps],
        "SB_global": old["SB"], "SM_global": old["SM"],
        "SB_exC": any(c["SB_local"] for c in comps),
        "SM_exC": any(c["SM_local"] for c in comps),
        "comps": r["comps"], "closure": r["closure_ok"],
        "E": len(r["E"]),
        "CS′_local": [c["CS′_local"] for c in comps],
    }


# ============================================================
# §3 S1-S3 Sanity（v7 §七 D8）
# ============================================================

def tensor_kernel_dup(P8, s8, copies):
    """同构复制核（张量积；复制稳定性核因式分解，脚本 1 先例）。"""
    if copies == 2:
        S = 1 << (2 * len(s8[0]))
        P = [[0.0] * S for _ in range(S)]
        n1 = len(s8)
        for a in range(n1):
            for b in range(n1):
                for ap in range(n1):
                    for bp in range(n1):
                        P[a * n1 + b][ap * n1 + bp] = P8[a][ap] * P8[b][bp]
        states = list(itertools.product((0, 1), repeat=2 * len(s8[0])))
        return P, states
    raise ValueError("copies>2 未实现（本批仅需 2）")


def sanity_s1(entry):
    """S1 独立复制：CS′(S⊕R)=CS′(S)∨CS′(R)（R 与 S 独立同构）。用张量积核。"""
    sys = entry["sys"]
    P8, s8 = exact_kernel(sys.step_fn, sys.n)
    P2, s2 = tensor_kernel_dup(P8, s8, 2)
    n2 = sys.n * 2
    # 直和系统 M/A：两副本
    M2 = list(sys.M_set) + [i + sys.n for i in sys.M_set]
    A2 = list(sys.A_set) + [i + sys.n for i in sys.A_set]
    dup = System(f"{entry['name']}⊕{entry['name']}", n2, None, M2, A2,
                 kernel_builder=lambda: (P2, s2))
    r_dup = evaluate(dup)
    r_s = evaluate(sys)
    cs_lhs = r_dup["CS′"]
    cs_rhs = r_s["CS′"] or r_s["CS′"]   # CS′(S)∨CS′(R)，R 同构
    return cs_lhs == cs_rhs, cs_lhs, cs_rhs


def sanity_s2(entry):
    """S2 无关惰性模块：CS′(S⊕Z)=CS′(S)（Z 常数 0，稀释反噬检查）。"""
    sys = entry["sys"]
    def step_sz(state, rng):
        a = state[0:sys.n]
        return sys.step_fn(a, rng) + (0,)
    n2 = sys.n + 1
    sz = System(f"{entry['name']}⊕Z", n2, step_sz,
                list(sys.M_set), list(sys.A_set))
    r_sz = evaluate(sz)
    r_s = evaluate(sys)
    return r_sz["CS′"] == r_s["CS′"], r_sz["CS′"], r_s["CS′"]


def sanity_s3():
    """S3 真正耦合：只验证分解合并性质 𝒞(S↔R)={S∪R} 与合并后正常执行，
    不预设 CS′ 方向（D8：防 Replication Invariance 被错误实现成「规模永不可增」）。

    构造：B_cpg（4 变量）与 2 变量模块 R 双向耦合（r1′=x1, x1′ 依赖 r1）→ 应合并单分量。
    """
    def step(state, rng):
        x1, x2, o1, o2, r1, r2 = state
        nx1 = r1 if rng.bernoulli(0.9) else (1 - x2) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nx2 = (1 - x1) if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        no1 = x1 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        no2 = x2 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        nr1 = x1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nr2 = x2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        return (nx1, nx2, no1, no2, nr1, nr2)
    s = System("B_cpg↔R", 6, step, [0], [2, 3])
    r = evaluate(s)
    merged = (len(r["comps"]) == 1) and (len(r["comps"][0]) == 6)
    return (merged and r["closure_ok"] and r["factor_ok"]), r


# ============================================================
# §4 主流程
# ============================================================

def main():
    print("=" * 80)
    print("脚本 3/3：B1 十类 paired benchmark + 双轨对照 + S1-S3（Grilling #94 D1-D10）")
    print("CS′_new = 分量级 OR；CS′_old = 整体式；判定器只读 step_fn + 预冻结 M/A")
    print("=" * 80)

    entries = make_benchmark_systems()
    results = []
    for e in entries:
        a = analyze(e)
        results.append(a)
        print(f"\n--- [{a['cat']}/{a['role']}] {a['name']:12s} (机制: {a['mech']}) ---")
        print(f"  𝒞={a['comps']}  E={a['E']}  closure={a['closure']}")
        print(f"  CS′_new={a['new']}  CS′_old={a['old']}  ΔCS′={'0' if a['new']==a['old'] else '±1'}")
        print(f"  Int_global={a['Int_global']:.4f} vs max_C Int={a['maxC_Int']:.4f} | "
              f"Diff_global={a['Diff_global']:.3f} vs Diff_C={a['Diff_C']} | "
              f"SB ∃C={a['SB_exC']} SM ∃C={a['SM_exC']}")

    # Δ(Int,Diff,SB,SM) 随目标机制变化表
    print("\n" + "=" * 80)
    print("Δ(Int,Diff,SB,SM) 随目标机制变化表（rep → ctl）")
    print("=" * 80)
    print(f"  {'配对':22s} {'ΔInt':>8s} {'ΔDiff':>8s} {'ΔSB':>6s} {'ΔSM':>6s} {'ΔCS′':>6s}")
    by_class = {}
    for a in results:
        by_class.setdefault(a["mech"], []).append(a)
    for mech, pair in by_class.items():
        rep = next(x for x in pair if x["role"] == "rep")
        ctl = next(x for x in pair if x["role"] == "ctl")
        d_int = ctl["maxC_Int"] - rep["maxC_Int"]
        d_diff = ctl["Diff_C"][0] - rep["Diff_C"][0]
        d_sb = int(ctl["SB_exC"]) - int(rep["SB_exC"])
        d_sm = int(ctl["SM_exC"]) - int(rep["SM_exC"])
        d_cs = int(ctl["new"]) - int(rep["new"])
        print(f"  {mech:22s} {d_int:+8.4f} {d_diff:+8.3f} {d_sb:+6d} {d_sm:+6d} {d_cs:+6d}")

    # 双轨对照失败线
    print("\n" + "=" * 80)
    print("失败线（D8/D9 A1：仅 simulation 轨）")
    print("=" * 80)
    neg = [a for a in results if a["cat"] == "neg"]
    pos = [a for a in results if a["cat"] == "pos"]
    f_plus = any(a["new"] for a in neg)
    pos_sim = [a for a in pos if a["name"] not in ("H_loop", "H_linear")]  # #6 observation 轨
    f_minus = all(not a["new"] for a in pos_sim)
    for a in neg:
        print(f"  负类 {a['name']:10s}: CS′_new={a['new']}  CS′_old={a['old']}")
    print(f"  F+（任一负类判 1）: {'❌ 触发' if f_plus else '✅ 未触发'}")
    for a in pos:
        mark = "" if a["name"] not in ("H_loop", "H_linear") else "（observation 轨，不触发失败线）"
        print(f"  正类 {a['name']:10s}: CS′_new={a['new']}{mark}")
    print(f"  F−（simulation 轨正类全 0）: {'❌ 触发' if f_minus else '✅ 未触发'}")

    # S1-S3
    print("\n" + "=" * 80)
    print("Sanity suite（v7 §七 D8）")
    print("=" * 80)
    f8p = next(e for e in entries if e["name"] == "F8′")
    ok1, lhs, rhs = sanity_s1(f8p)
    print(f"  S1 独立复制: CS′(F8′⊕F8′)={lhs} == CS′(F8′)∨CS′(F8′)={rhs}  {'✅' if ok1 else '❌'}")
    ok2, lhs2, rhs2 = sanity_s2(f8p)
    print(f"  S2 惰性模块: CS′(F8′⊕Z)={lhs2} == CS′(F8′)={rhs2}  {'✅' if ok2 else '❌'}")
    ok3, r3 = sanity_s3()
    print(f"  S3 真正耦合: 𝒞(S↔R)={r3['comps']} 合并单分量+闭包+分解: "
          f"{'✅' if ok3 else '❌'}（CS′ 不预设方向: {r3['CS′']}）")

    print("\n" + "=" * 80)
    verdict = f_plus or f_minus
    print(f"Benchmark 判定: {'❌ 失败线触发（F+ 或 F−）→ 触发 Step 6 闭合后修正' if verdict else '✅ 失败线未触发'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
