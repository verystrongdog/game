"""
sim_consciousness_v7_components.py — v7 分量分解 + 完整 CS′_local(C)（模拟实现批次 脚本 1/3）
=============================================================================================
研讨论文产物（纯学术，不入游戏正典）。Grilling #94（issue #94）D1-D6 定案落地。

验证 v7 定义（来源：参考/意识结构侧-下一阶段路线-v7.md）：
  §四 Reach R1（正概率、μ₀ 锚定、无界时域、含瞬态）
  §三 E_S^(1) 一阶结构依赖边 + 弱连通分量 𝒞（非强连通）
  §五 Diff(C) 轨迹分布熵 + Capacity 诊断量（不参与判定）
  §二 分量级判定 CS′(S) = ⋁_{C∈𝒞(S)} CS′_local(C) + Replication Invariance
  §六 SM′ = RB_I ∧ RB_A（R-B 内部因果穿透 + AgencyUse，exact do-kernel 实测）

判定链（Grilling #94 D3）：
  CS′_local(C) = Int_local(C) > 0 ∧ Diff(C) ≥ θ_D(3bit) ∧ SB_local(C) ∧ SM_local(C)
  SM_local(C)  = RB_I(C) ∧ RB_A(C)
  CS′(S)       = ⋁_{C∈𝒞(S)} CS′_local(C)

验收（issue #94）：
  ① Replication Invariance 用完整判据断言（禁止 Diff-only 代理验收）：CS′(S⊕S)=CS′(S)，
     0→0 半边（F8⊕F8）+ 1→1 半边（F8′ 及 F8′⊕R 惰性模块）
  ② v5.3 full_reachable=Ω 退化不再出现（Diff 用轨迹熵，非容量）
  ③ 分层验收输出：分量分解 → 分量指标 → Local CS′ → System CS′ → Replication

实现微调（交付说明）：exact_kernel 要求 step 函数的随机性用 rng.bernoulli(p) 原语表达
（rng.random()<p / rng.randint(0,1) 的语义等价机械改写，动力学零改动）——黑盒 random()
无法让核提取器获知阈值 p，通用精确枚举要求随机结构显式。
"""

import itertools
import math

# 复用现有 sim 常量（Grilling #94 D4：从既有来源读取，不复制魔法数字）
from sim_consciousness_cs4_test import (          # cs4 阈值常量 :26-30
    THETA_TE, THETA_SRC, THETA_F, THETA_C,
)
from sim_consciousness_v5_check import (          # v5.3 四系统 + 广播阈值 :36-39
    make_systems, MIN_SOURCE_VALUES, MIN_TARGETS, THETA_SEL,
)

# ============================================================
# §0 数值冻结表（Grilling #94 D4，来源见注释）
# ============================================================

THETA_D = 3.0            # θ_D 分化阈值 3 bit（v7 参数速查表，分量级保留）
T_DIFF = 64              # Diff 观察窗口（v7 参数表「T_obs 派生」；D4 实例化 T=64）
N_MAX_EXACT = 8          # n≤8 exact 轨（v7 §七；超出显式报错，不降级采样）
EPS = 1e-12              # 浮点容差（精确核比较）
MIX_MAX_ITER = 5000      # 稳态幂迭代上界（混合时间通常 < 数百步；超限走时间平均回退）


# ============================================================
# §1 系统定义（唯一权威源；D2：P(y′|y) 必须由 step_fn 唯一派生）
# ============================================================

class System:
    """统一装载格式（Grilling #94 D2）：(name, n, step_fn, M_set, A_set)。

    step_fn(state, rng) 中随机性用 rng.bernoulli(p) 表达；确定性系统忽略 rng。
    M_set/A_set：候选自模型变量 / 外显动作变量（脚本 2/3 直接读取）。
    """

    def __init__(self, name, n, step_fn, M_set, A_set, kernel_builder=None):
        self.name = name
        self.n = n
        self.step_fn = step_fn
        self.M_set = frozenset(M_set)
        self.A_set = frozenset(A_set)
        # 可选：预构建核（返回 (P, states)），优先于 step_fn（如直和系统用张量积，
        # 利用复制稳定性核因式分解 P_{S⊕R}=P_S⊗P_R——D3 推论①，避免 2^20 重放）
        self.kernel_builder = kernel_builder


def make_f8_step():
    """F8 表征+因果使用——step 载体（bernoulli 改写自 cs4 :241-249，语义等价）。

    原：nm1 = y1 if rng.random()<0.9 else rng.randint(0,1) 等（cs4 :241-249）。
    V={y1,y2,m1,m2}，M={2,3}，A={0,1}（cs4 :283-287）→ I=∅ → RB_I 恒假（v7 §六）。
    """
    def step(state, rng):
        y1, y2, m1, m2 = state
        nm1 = y1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nm2 = y2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        if rng.bernoulli(0.6):
            ny1 = y1 ^ m1
        else:
            ny1 = (y1 ^ y2) if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        if rng.bernoulli(0.6):
            ny2 = y2 ^ m2
        else:
            ny2 = y1 if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        return (ny1, ny2, nm1, nm2)
    return step


def make_f8p_step():
    """F8′ 表征+因果使用+内部穿透（Grilling #94 D5 + D6 修正）。

    state = (y1,y2,m1,m2,z1,z2)，n=6；M={2,3}，A={0,1}，I={4,5}。
    D6（闭合后修正，2026-08-27）：A 通道由 XOR 型改为**直接依赖型**
    （ny1=m1 if 0.6——边际 do 检验可见），否则 RB_A 对 XOR 型 M→A 失效
    （P(A|do(M=m)) 在另一输入均匀化后不随 m 变，实测 0.5 vs 0.5）。
    新增 z1′=m1、z2′=m2（强度 0.9）→ M→I；z 不得反向影响 M/A
    （新增机制只能是 M→I，禁止 M→I→A）。判定器零改动（脚本 2 不修改判定器）。
    """
    def step(state, rng):
        y1, y2, m1, m2, z1, z2 = state
        nm1 = y1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        nm2 = y2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)
        # D6：M→A 直接依赖（边际 do 可见）；F8 保留 XOR 作自然负例
        ny1 = m1 if rng.bernoulli(0.6) else (y1 ^ y2) if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        ny2 = m2 if rng.bernoulli(0.6) else y1 if rng.bernoulli(0.5) else rng.bernoulli(0.5)
        nz1 = m1 if rng.bernoulli(0.9) else rng.bernoulli(0.5)   # M→I（D5）
        nz2 = m2 if rng.bernoulli(0.9) else rng.bernoulli(0.5)   # M→I（D5）
        return (ny1, ny2, nm1, nm2, nz1, nz2)
    return step


def _det_wrap(F):
    """v5.3 确定性系统（int→int，v5_check :46-89）包装为 step(state, rng)（忽略 rng）。"""
    def step(state, rng):
        x = sum(state[i] << i for i in range(len(state)))
        x2 = F(x)
        return tuple((x2 >> i) & 1 for i in range(len(state)))
    return step


def make_f8_copy_kernel():
    """F8⊕F8 的核 = 张量积 P_S⊗P_S（复制稳定性：E_{S⊕S}=E_S∪E_S、核因式分解，
    v7 §三 D3 推论①）。比 8 变量逐位重放（~7M 次 step）快 3 个量级，且数学精确。
    主流程附抽查断言：直和 step 直接枚举的核行与张量积行一致。
    """
    P8, s8 = exact_kernel(make_f8_step(), 4)
    S = 256
    P = [[0.0] * S for _ in range(S)]
    for a in range(16):
        for b in range(16):
            for ap in range(16):
                for bp in range(16):
                    P[a * 16 + b][ap * 16 + bp] = P8[a][ap] * P8[b][bp]
    states = list(itertools.product((0, 1), repeat=8))
    return P, states


def make_systems_v7():
    """脚本 1 被测系统清单（M/A 分配来源：cs4 :283-287；D5；v5.3 无 M/A）。"""
    sys_list = []
    # F8（0→0 半边 + SM 退化展示；M/A 分配 cs4 :283-287）
    sys_list.append(System("F8", 4, make_f8_step(), [2, 3], [0, 1]))
    # F8⊕F8（同构复制，n=8；核 = 张量积——复制稳定性数学实现；直和语义同
    # cs4 复制攻击段 :315-323）
    sys_list.append(System("F8⊕F8", 8,
                           lambda s, rng: make_f8_step()(s[0:4], rng) + make_f8_step()(s[4:8], rng),
                           [2, 3, 6, 7], [0, 1, 4, 5],
                           kernel_builder=make_f8_copy_kernel))
    # F8′（1→1 正例；D5）
    sys_list.append(System("F8′", 6, make_f8p_step(), [2, 3], [0, 1]))
    # F8′⊕R_const（加独立惰性模块不稀释；n=7；R={6} 常数 0，CS′(R)=0）
    sys_list.append(System("F8′⊕R", 7,
                           lambda s, rng: make_f8p_step()(s[0:6], rng) + (0,),
                           [2, 3], [0, 1]))
    # v5.3 四系统（无 M/A → SM 退化条款 CS′=0；承担分量/熵/退化修复展示）
    for name, (n, F) in make_systems().items():
        sys_list.append(System(f"v5.3:{name}", n, _det_wrap(F), [], []))
    return sys_list


# ============================================================
# §2 exact_kernel —— 从 step_fn 唯一派生精确核 P(y′|y)（D2）
# ============================================================

class _PatternRNG:
    """模式 rng：按预置出向量依次返回 bernoulli 结果，并记录 (阈值 p, 出位)。

    越界（出向量用尽）抛 OverflowError → 调用方视为实现缺陷（K 上界探测失败）。
    """

    def __init__(self, outcomes):
        self._out = outcomes
        self._i = 0
        self.consumed = []   # [(p, bit), ...] 实际消费的随机位及阈值

    def bernoulli(self, p):
        if self._i >= len(self._out):
            raise OverflowError("pattern exhausted")
        bit = self._out[self._i]
        self._i += 1
        self.consumed.append((p, bit))
        return bit


def exact_kernel(step_fn, n, max_depth=64):
    """精确 P(y′|y)（D2）。逐位扩展枚举：维护「已消费位串」前沿，逐位分叉，
    越界（位不足）的前缀继续扩展；完成的路径按 (y′, 消费位串) 去重累加。

    路径概率 = ∏(p 若位=1 否则 1−p)；相同 (y′, 消费位串) = 同一路径事件 → 合并
    （未消费尾位不得造成重复计数——条件消费语义）。确定性系统（零消费）退化为 δ 核。
    复杂度 = O(实际路径数 × 2)，与单步调用数上界无关（避免 2^K 全枚举）。
    """
    if n > N_MAX_EXACT:
        raise ValueError(f"n={n} 超出 exact 轨上界 n≤{N_MAX_EXACT}（v7 §七）；显式报错，不降级采样")
    states = list(itertools.product((0, 1), repeat=n))
    S = len(states)
    idx = {s: i for i, s in enumerate(states)}
    P = [[0.0] * S for _ in range(S)]
    for yi, y in enumerate(states):
        seen_paths = set()
        frontier = {()}
        depth = 0
        while frontier:
            if depth > max_depth:
                raise ValueError(f"路径深度超限 {max_depth}（exact 轨保护）")
            nxt = set()
            for bits in frontier:
                for tail in (0, 1):
                    full = bits + (tail,)
                    rng = _PatternRNG(full)
                    try:
                        y2 = step_fn(y, rng)
                    except OverflowError:
                        consumed = tuple(b for _, b in rng.consumed)
                        if consumed not in seen_paths:
                            nxt.add(consumed)
                        continue
                    consumed = tuple(b for _, b in rng.consumed)
                    if consumed in seen_paths:
                        continue
                    seen_paths.add(consumed)
                    prob = 1.0
                    for p, b in rng.consumed:
                        prob *= p if b == 1 else (1.0 - p)
                    P[yi][idx[y2]] += prob
            frontier = nxt
            depth += 1
    return P, states


# ============================================================
# §3 Reach R1 / E_S^(1) 边 / 弱连通分量 𝒞 / 闭包断言
# ============================================================

def reach_states(P, states, mu0_supp):
    """Reach R1（v7 §四）：∃y₀∈supp(μ₀), ∃t∈ℕ₀, P(Y_t=y|Y_0=y₀)>0。

    实现：从 supp(μ₀) 出发沿正概率边做图可达（t=0 含 supp 本身）。
    benchmark μ₀=Unif(Ω)（v7 §五）→ supp=Ω → Reach=Ω（t=0 平凡成立）。
    """
    n = len(states)
    supp = [i for i in range(n) if mu0_supp[i] > 0]
    reach = set(supp)
    frontier = list(supp)
    while frontier:
        i = frontier.pop()
        row = P[i]
        for j in range(n):
            if row[j] > 0 and j not in reach:
                reach.add(j)
                frontier.append(j)
    return reach


def edges_e1(P, states):
    """E_S^(1) 一阶结构依赖边（v7 §三）：
    (i,j) ∈ E ⟺ ∃y,y′∈Reach: y_{-i}=y′_{-i} ∧ y_i≠y′_i ∧ P_F(X′_j|y)≠P_F(X′_j|y′)。

    实现：预计算目标边际表 marg[j][y][v] = P(X′_j=v|y)，Reach 内枚举单坐标翻转对。
    """
    n = len(states[0])
    S = len(states)
    reach = reach_states(P, states, [1.0] * S)
    # marg[j][yi][0/1]
    marg = [[[0.0, 0.0] for _ in range(S)] for _ in range(n)]
    for yi in range(S):
        row = P[yi]
        for j in range(n):
            for k in range(S):
                marg[j][yi][states[k][j]] += row[k]
    E = set()
    for y_idx in reach:
        y = states[y_idx]
        for i in range(n):
            y2 = list(y)
            y2[i] = 1 - y2[i]
            y2 = tuple(y2)
            y2_idx = states.index(y2)
            if y2_idx not in reach:
                continue
            for j in range(n):
                if abs(marg[j][y_idx][0] - marg[j][y2_idx][0]) > EPS:
                    E.add((i, j))
    return E


def weak_components(n, E):
    """弱连通分量 𝒞(S)（v7 §三：CC(G_S^u)，非强连通）。union-find。"""
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for i, j in E:
        union(i, j)
    comps = {}
    for v in range(n):
        comps.setdefault(find(v), []).append(v)
    return [sorted(c) for c in comps.values()]


def closure_check_simple(P, states, comps):
    """decomposition invariant（D3）：无跨分量边 ⟹ 核因式分解
    P_F(Y′|y) = ∏_C P_F(Y′_C|y_C)（每分量 C 动力学封闭）。
    ① 闭包：∀y,y′ 同 y_C ⟹ P(Y′_C|y) = P(Y′_C|y′)（分布以 9 位小数规范化比较）
    ② 因式分解：∀y,y′: P(y′|y) = ∏_C P_C(y′_C|y_C)。
    """
    idx = {s: i for i, s in enumerate(states)}
    S = len(states)
    closure_ok = True
    factor_ok = True
    # ① 每分量 C：按 y_C 分组收集分布，同组多于一个不同分布 → 闭包失败
    for C in comps:
        groups = {}
        for y in states:
            yC = tuple(y[k] for k in C)
            dist = {}
            for yp in states:
                ypC = tuple(yp[k] for k in C)
                dist[ypC] = dist.get(ypC, 0.0) + P[idx[y]][idx[yp]]
            key = tuple(sorted((k, round(v, 9)) for k, v in dist.items()))
            groups.setdefault(yC, set()).add(key)
        if any(len(ds) > 1 for ds in groups.values()):
            closure_ok = False
    # ② 因式分解（利用 ① 中闭包成立时的规范分布：取每 yC 组的任一分布）
    P_C_norm = {}
    for C in comps:
        dist_by_yC = {}
        for y in states:
            yC = tuple(y[k] for k in C)
            if yC in dist_by_yC:
                continue
            dist = {}
            for yp in states:
                ypC = tuple(yp[k] for k in C)
                dist[ypC] = dist.get(ypC, 0.0) + P[idx[y]][idx[yp]]
            dist_by_yC[yC] = dist
        P_C_norm[tuple(C)] = dist_by_yC
    for y in states:
        yi = idx[y]
        for yp in states:
            pi = idx[yp]
            lhs = P[yi][pi]
            rhs = 1.0
            for C in comps:
                yC = tuple(y[k] for k in C)
                ypC = tuple(yp[k] for k in C)
                rhs *= P_C_norm[tuple(C)][yC][ypC]
            if abs(lhs - rhs) > 1e-9:
                factor_ok = False
                break
        if not factor_ok:
            break
    return closure_ok, factor_ok


# ============================================================
# §4 Diff(C) 轨迹熵 + Capacity 诊断量（v7 §五；D4）
# ============================================================

def stationary_dist(P_C, n_C, max_iter=MIX_MAX_ITER, tol=1e-12):
    """稳态分布 μ_∞（幂迭代自 μ₀=Unif；不收敛时取末 1000 步时间平均并标注）。

    用于 Int_local 的 E_μ 与 SB_local 的精确 TE（D3/D4 冻结）。
    """
    S = 1 << n_C
    mu = [1.0 / S] * S
    for _ in range(max_iter):
        mu2 = [0.0] * S
        for i in range(S):
            if mu[i] > 0:
                row = P_C[i]
                for j in range(S):
                    mu2[j] += mu[i] * row[j]
        diff = max(abs(mu2[i] - mu[i]) for i in range(S))
        mu = mu2
        if diff < tol:
            return mu, True
    # 不收敛（如确定性多吸引子）→ 时间平均回退（末 1000 步）
    acc = [0.0] * S
    for _ in range(1000):
        mu2 = [0.0] * S
        for i in range(S):
            row = P_C[i]
            for j in range(S):
                mu2[j] += mu[i] * row[j]
        mu = mu2
        for j in range(S):
            acc[j] += mu[j]
    mu_avg = [a / 1000.0 for a in acc]
    return mu_avg, False


def h2(dist):
    """香农熵（log2，bit——θ_D 语义单位，v7 §五）。"""
    h = 0.0
    for p in dist:
        if p > EPS:
            h -= p * math.log2(p)
    return h


def diff_traj_entropy(P_C, n_C):
    """Diff(C) = (1/(T+1))Σ_{t=0}^{T} H(μ_t^C)，μ₀=Unif(Ω_C)（v7 §五 + D4）。

    返回 (diff, h_series, h_steady)；h_steady 仅诊断（稳态熵 H_C(∞)，不参与定义——
    Grilling #94 D4 写死防替代）。
    """
    S = 1 << n_C
    mu = [1.0 / S] * S
    series = [h2(mu)]
    for _ in range(T_DIFF):
        mu2 = [0.0] * S
        for i in range(S):
            if mu[i] > 0:
                row = P_C[i]
                for j in range(S):
                    mu2[j] += mu[i] * row[j]
        mu = mu2
        series.append(h2(mu))
    diff = sum(series) / (T_DIFF + 1)
    mu_st, _ = stationary_dist(P_C, n_C)
    return diff, series, h2(mu_st)


def capacity(P_C, n_C):
    """Capacity(C) = log₂|Reach(C)| 诊断量（v7 §五，不参与 CS′ 判定）。

    benchmark μ₀=Unif(Ω) 下 Reach(C)=全空间 → Capacity=|C| bit（诊断基线，
    Diff/Capacity 利用率可观察）。
    """
    states = list(itertools.product((0, 1), repeat=n_C))
    reach = reach_states(P_C, states, [1.0] * len(states))
    return math.log2(max(1, len(reach)))


# ============================================================
# §5 Int_local(C)（v6 Layer 1 精确实现；D3）
# ============================================================

def int_local(P_C, mu, n_C):
    """Int_local(C) = min_{π∈Π₂(C)} E_μ[KL(P_C(·|Y) ‖ P_π^cut(·|Y))]（v6 Layer 1）。

    P_π^cut(y′|y) = ∏_{B∈π} P̂_B(y′_B|y_B)——IIT「cut 核」语义：块 B 的转移只读
    自身输入 y_B（跨块输入被截断）；P̂_B 对 y∖B 做均匀边缘化
    （来源：v5_check :124-137 marginal_transition 的「其他分量均匀化」先例）。
    注意：非「y′ 联合独立化」∏_B P(y′_B|y)——那对独立噪声系统恒 KL=0，测不出整合。
    μ = 稳态分布（D3/D4 冻结）。二分 partition 模对称去重。n_C<2 → 0（无内部整合）。
    """
    if n_C < 2:
        return 0.0
    S = 1 << n_C
    states = list(itertools.product((0, 1), repeat=n_C))
    idx = {s: i for i, s in enumerate(states)}
    cut_cache = {}
    def cut_block(B, y_B):
        """P̂_B(y′_B|y_B) = 均匀边缘化 y∖B 的块转移（v5_check :124-137 风格）。"""
        key = (B, y_B)
        if key in cut_cache:
            return cut_cache[key]
        Bset = set(B)
        others = [i for i in range(n_C) if i not in Bset]
        dist = {}
        cnt = 0
        for comb in itertools.product((0, 1), repeat=len(others)):
            y = [0] * n_C
            for j, bval in enumerate(y_B):
                y[B[j]] = bval
            for k, oval in enumerate(comb):
                y[others[k]] = oval
            yi = idx[tuple(y)]
            for yp in states:
                keyp = tuple(yp[j] for j in B)
                dist[keyp] = dist.get(keyp, 0.0) + P_C[yi][idx[yp]]
            cnt += 1
        for k in dist:
            dist[k] /= cnt
        cut_cache[key] = dist
        return dist
    best = float("inf")
    for mask in range(1, (1 << n_C) - 1):
        B1 = tuple(i for i in range(n_C) if (mask >> i) & 1)
        B2 = tuple(i for i in range(n_C) if i not in B1)
        total = 0.0
        for yi, y in enumerate(states):
            d1 = cut_block(B1, tuple(y[j] for j in B1))
            d2 = cut_block(B2, tuple(y[j] for j in B2))
            kl = 0.0
            for pi, yp in enumerate(states):
                p = P_C[yi][pi]
                if p > EPS:
                    q = d1[tuple(yp[j] for j in B1)] * d2[tuple(yp[j] for j in B2)]
                    if q > EPS:
                        kl += p * math.log(p / q)
            total += mu[yi] * kl
        best = min(best, total)
    return best


# ============================================================
# §6 SB_local(C)（v6 Layer 1 定义，exact 轨：TE 从稳态联合分布精确计算；D2/D3）
# ============================================================

def _joint_steady(P_C, mu, n_C):
    """稳态联合分布 P(Y_t=y, Y_{t+1}=y′) = μ_∞(y)·P_C(y′|y)。"""
    S = 1 << n_C
    jt = {}
    for i in range(S):
        if mu[i] > 0:
            row = P_C[i]
            for j in range(S):
                v = mu[i] * row[j]
                if v > EPS:
                    jt[(i, j)] = v
    return jt


def te_exact(P_C, mu, n_C, src_idx, tgt_idx):
    """TE(I→j) = H(X′_j|X_j) − H(X′_j|X_j, X_I)（稳态联合精确计算）。

    I 可为多变量（src_idx 列表）。v6 Layer 1 InfoTransfer 定义的规范值（exact 轨，
    非有限样本轨迹估计）。
    """
    states = list(itertools.product((0, 1), repeat=n_C))
    jt = _joint_steady(P_C, mu, n_C)
    def cond_h(cond_fn):
        groups = {}
        for (i, j), v in jt.items():
            y, yp = states[i], states[j]
            key = cond_fn(y, yp)
            g = groups.setdefault(key, [0.0, 0.0])
            g[0] += v
            g[1] += v * yp[tgt_idx]
        h = 0.0
        for key, (tot, cnt1) in groups.items():
            p1 = cnt1 / tot
            if p1 > EPS:
                h -= tot * (p1 * math.log2(p1))
            if 1 - p1 > EPS:
                h -= tot * ((1 - p1) * math.log2(1 - p1))
        return h
    h_cond_j = cond_h(lambda y, yp: (y[tgt_idx],))
    h_cond_jI = cond_h(lambda y, yp: (y[tgt_idx],) + tuple(y[i] for i in src_idx))
    return h_cond_j - h_cond_jI


def mi_exact(P_C, mu, n_C, idx_a, idx_b):
    """MI(X_a; X_b)（稳态联合，cs4 FunctionalDistinct 的精确版）。"""
    states = list(itertools.product((0, 1), repeat=n_C))
    jt = _joint_steady(P_C, mu, n_C)
    pa, pb, pab = {}, {}, {}
    for (i, j), v in jt.items():
        y = states[i]
        a, b = y[idx_a], y[idx_b]
        pa[a] = pa.get(a, 0.0) + v
        pb[b] = pb.get(b, 0.0) + v
        pab[(a, b)] = pab.get((a, b), 0.0) + v
    mi = 0.0
    for (a, b), v in pab.items():
        mi += v * math.log2(v / (pa[a] * pb[b]))
    return mi


def sb_local(P_C, mu, n_C):
    """SB_local(C)（v6 Layer 1 + cs4/v5_check 阈值）：∃I₀(|I₀|=2), J⊆C∖I₀(|J|≥2)：
    ①源分化 ≥ MIN_SOURCE_VALUES(3) ②∀j∈J: TE(I₀→j) ≥ THETA_TE(0.01)
    ③选择性比 TE(I₀→j) ≥ THETA_SEL(1.0)·max_{K≠I₀} TE(K→j)（v5_check :221）
    ④目标独立（两两 MI ≤ THETA_F·max(H)，防复制伪装，cs4 :151-158）
    ⑤覆盖度 |I₀∪J|/|C| ≥ THETA_C(0.3)。
    搜索域收窄为 C 内（闭包子系统 → 天然分量内）。"""
    if n_C < 4:
        return False, None
    states = list(itertools.product((0, 1), repeat=n_C))
    H_j = {}
    for j in range(n_C):
        p0 = sum(mu[i] for i in range(1 << n_C) if states[i][j] == 0)
        H_j[j] = h2([p0, 1 - p0])
    for I0 in itertools.combinations(range(n_C), 2):
        src_vals = set()
        for i in range(1 << n_C):
            if mu[i] > EPS:
                src_vals.add(tuple(states[i][k] for k in I0))
        if len(src_vals) < MIN_SOURCE_VALUES:
            continue
        targets = [j for j in range(n_C) if j not in I0]
        if len(targets) < MIN_TARGETS:
            continue
        te_map = {j: te_exact(P_C, mu, n_C, list(I0), j) for j in targets}
        good = [j for j in targets if te_map[j] >= THETA_TE]
        if len(good) < MIN_TARGETS:
            continue
        sel_ok = True
        for j in good:
            bg = 0.0
            for K in range(n_C):
                if K in I0 or K == j:
                    continue
                bg = max(bg, te_exact(P_C, mu, n_C, [K], j))
            if bg > EPS and te_map[j] / bg < THETA_SEL:
                sel_ok = False
        if not sel_ok:
            continue
        distinct_ok = True
        for a, b in itertools.combinations(good, 2):
            mi = mi_exact(P_C, mu, n_C, a, b)
            if mi > THETA_F * max(H_j[a], H_j[b]) and mi > EPS:
                distinct_ok = False
        if not distinct_ok:
            continue
        cov = len(set(I0) | set(good)) / n_C
        if cov < THETA_C:
            continue
        return True, {"I0": I0, "J": good,
                      "te_map": {j: round(v, 4) for j, v in te_map.items()}}
    return False, None


# ============================================================
# §7 SM_local(C) = RB_I ∧ RB_A（v7 §六；exact do-kernel 实测，D5）
# ============================================================

def do_dist(P, n, M_set, m_tuple, k):
    """P(X′_k | do(M=m))——单步硬干预 + 条件均匀权重（D3）：
    w(y|M=m) = 1/|{y∈Ω: y_M=m}|，不跟随 μ_t（跨基底，结构性 do 检验）。
    """
    S = 1 << n
    states = list(itertools.product((0, 1), repeat=n))
    M_idx = sorted(M_set)
    m_map = dict(zip(M_idx, m_tuple))
    tot = [0.0, 0.0]
    cnt = 0
    for yi, y in enumerate(states):
        if all(y[i] == m_map[i] for i in M_idx):
            cnt += 1
            row = P[yi]
            for j in range(S):
                tot[states[j][k]] += row[j]
    if cnt == 0:
        return [0.0, 0.0]
    return [tot[0] / cnt, tot[1] / cnt]


def rb_penetration(P, n, M_set, target_set):
    """R-B 内部因果穿透：∃m≠m′, ∃k∈target: P_F(X′_k|do(M=m)) ≠ P_F(X′_k|do(M=m′))。

    target_set = I（SelfRep）或 A（SelfUse∧AgencyUse 合一——v7 中两者均为 M→A
    do 检验；Δ_A(M)>0 结构性条件）。空 target → False（D3 退化条款）。
    """
    if not target_set or not M_set:
        return False
    m_vals = list(itertools.product((0, 1), repeat=len(M_set)))
    for m1 in m_vals:
        for m2 in m_vals:
            if m1 == m2:
                continue
            for k in target_set:
                d1 = do_dist(P, n, M_set, m1, k)
                d2 = do_dist(P, n, M_set, m2, k)
                if abs(d1[0] - d2[0]) > EPS or abs(d1[1] - d2[1]) > EPS:
                    return True
    return False


def sm_local(P, n, M_set, A_set):
    """SM_local(C) = RB_I ∧ RB_A（v7 §六 D6/D7 + D3/D5）。

    退化条款（D3，入原语）：M∩C=∅ → False；A∩C=∅ → 仅 RB_I
    （A=∅ 退化条款，v7 §六：封闭系统 I=V∖M）。
    """
    if not M_set:
        return False, "M∩C=∅"
    V = set(range(n))
    I_set = V - set(M_set) - set(A_set)
    rb_i = rb_penetration(P, n, list(M_set), list(I_set))
    if not A_set:
        return rb_i, f"RB_I={rb_i} (A∩C=∅)"
    rb_a = rb_penetration(P, n, list(M_set), list(A_set))
    return (rb_i and rb_a), f"RB_I={rb_i}, RB_A={rb_a}"


# ============================================================
# §8 CS′_local / CS′ / 分层验收
# ============================================================

def evaluate(system):
    """单系统全量评估，返回分层结果 dict（验收分层：D1）。"""
    if system.kernel_builder is not None:
        P, states = system.kernel_builder()
    else:
        P, states = exact_kernel(system.step_fn, system.n)
    n = system.n
    idx = {s: i for i, s in enumerate(states)}
    E = edges_e1(P, states)
    comps = weak_components(n, E)
    closure_ok, factor_ok = closure_check_simple(P, states, comps)

    layer_components = []
    for C in comps:
        nC = len(C)
        statesC = list(itertools.product((0, 1), repeat=nC))
        # 闭包子系统 C 的核 P_C（D3：每分量动力学封闭）。投影：P(Y′_C|Y_C)，
        # 对映射到同一 y_C 的 y 累加后**按行归一化**（y∖C 均匀边缘化，
        # 与 benchmark μ₀=Unif 精神一致；闭包断言保证归一化安全）。
        P_C = [[0.0] * (1 << nC) for _ in range(1 << nC)]
        for y in states:
            yi = idx[y]
            yC = tuple(y[orig] for orig in C)
            for yp in states:
                ypC = tuple(yp[orig] for orig in C)
                P_C[statesC.index(yC)][statesC.index(ypC)] += P[yi][idx[yp]]
        for row in P_C:
            s = sum(row)
            if s > 0:
                for k in range(len(row)):
                    row[k] /= s
        diff, h_series, h_steady = diff_traj_entropy(P_C, nC)
        cap = capacity(P_C, nC)
        mu, conv = stationary_dist(P_C, nC)
        int_v = int_local(P_C, mu, nC)
        sb_v, sb_detail = sb_local(P_C, mu, nC)
        M_in_C = [orig for orig in C if orig in system.M_set]
        A_in_C = [orig for orig in C if orig in system.A_set]
        map_C = {orig: j for j, orig in enumerate(C)}
        sm_v, sm_detail = sm_local(P_C, nC,
                                   [map_C[o] for o in M_in_C],
                                   [map_C[o] for o in A_in_C])
        cs_local = (int_v > EPS) and (diff >= THETA_D) and sb_v and sm_v
        layer_components.append({
            "C": C, "nC": nC, "Diff": diff, "h_steady": h_steady,
            "Capacity": cap, "util": diff / cap if cap > 0 else 0.0,
            "Int_local": int_v, "SB_local": sb_v, "SB_detail": sb_detail,
            "SM_local": sm_v, "SM_detail": sm_detail,
            "CS′_local": cs_local,
        })
    cs_sys = any(c["CS′_local"] for c in layer_components)
    return {
        "name": system.name, "n": n, "M": sorted(system.M_set), "A": sorted(system.A_set),
        "E": E, "comps": comps, "closure_ok": closure_ok, "factor_ok": factor_ok,
        "components": layer_components, "CS′": cs_sys,
    }


def main():
    print("=" * 78)
    print("脚本 1/3：v7 分量分解 + 完整 CS′_local(C)（Grilling #94 D1-D6）")
    print("CS′_local(C) = Int_local>0 ∧ Diff≥3bit ∧ SB_local ∧ SM_local(RB_I∧RB_A)")
    print("CS′(S) = ⋁ CS′_local(C)；Replication Invariance 用完整判据断言")
    print("=" * 78)

    systems = make_systems_v7()
    results = {}
    for sys in systems:
        print(f"\n--- {sys.name} (n={sys.n}, M={sorted(sys.M_set)}, A={sorted(sys.A_set)}) ---")
        r = evaluate(sys)
        results[sys.name] = r
        print(f"  E_S^(1) = {len(r['E'])} 条边；𝒞(S) = {r['comps']}")
        print(f"  closure(闭包)={'✓' if r['closure_ok'] else '✗'}  "
              f"factor(因式分解)={'✓' if r['factor_ok'] else '✗'}")
        for c in r["components"]:
            print(f"  C={c['C']}: Diff={c['Diff']:.3f}bit(≥3:{'✓' if c['Diff']>=THETA_D else '✗'}) "
                  f"Cap={c['Capacity']:.2f} 利用率={c['util']:.2f} "
                  f"H∞(诊断)={c['h_steady']:.3f}")
            print(f"          Int_local={c['Int_local']:.4f}(>0:{'✓' if c['Int_local']>EPS else '✗'}) "
                  f"SB_local={c['SB_local']} SM_local={c['SM_local']} [{c['SM_detail']}]")
            if c["SB_detail"]:
                print(f"          SB 例: I₀={c['SB_detail']['I0']} J={c['SB_detail']['J']} "
                      f"TE={c['SB_detail']['te_map']}")
            print(f"          CS′_local = {'✅ 1' if c['CS′_local'] else '❌ 0'}")
        print(f"  ⟹ CS′({sys.name}) = {'✅ 1' if r['CS′'] else '❌ 0'}")

    print("\n" + "=" * 78)
    print("验收 ① Replication Invariance（完整判据）")
    print("=" * 78)
    f8, f8s, f8p, f8pr = results["F8"], results["F8⊕F8"], results["F8′"], results["F8′⊕R"]
    ok_00 = (f8s["CS′"] == f8["CS′"] == 0)
    ok_11 = (f8p["CS′"] == 1) and (f8pr["CS′"] == 1)
    print(f"  [0→0] CS′(F8)={f8['CS′']} vs CS′(F8⊕F8)={f8s['CS′']}  "
          f"复制不新增候选: {'✅' if ok_00 else '❌'}")
    print(f"  [1→1] CS′(F8′)={f8p['CS′']} vs CS′(F8′⊕R)={f8pr['CS′']}  "
          f"加惰性模块不稀释: {'✅' if ok_11 else '❌'}")
    print(f"  复制稳定性: 𝒞(F8)={len(f8['comps'])} 分量 → 𝒞(F8⊕F8)={len(f8s['comps'])} 分量 "
          f"(期望 1→2)")

    # 张量积核 vs 直和 step 直接枚举的一致性抽查（复制稳定性核因式分解验证）
    print("  张量积核 vs 直和 step 枚举一致性抽查:")
    P8, s8 = exact_kernel(make_f8_step(), 4)
    Pt, st = make_f8_copy_kernel()
    n = 8
    idx_t = {s: i for i, s in enumerate(st)}
    rng_probe = _PatternRNG
    ok_tensor = True
    for y in [st[0], st[111], st[255]]:   # 抽查 3 个状态
        row_direct = [0.0] * 256
        # 用逐位扩展枚举直和 step 的行（小枚举，仅抽查）
        frontier = {()}
        seen = set()
        depth = 0
        while frontier and depth <= 40:
            nxt = set()
            for bits in frontier:
                for tail in (0, 1):
                    full = bits + (tail,)
                    rng = rng_probe(full)
                    try:
                        y2 = make_f8_step()(y[0:4], rng) + make_f8_step()(y[4:8], rng)
                    except OverflowError:
                        consumed = tuple(b for _, b in rng.consumed)
                        if consumed not in seen:
                            nxt.add(consumed)
                        continue
                    consumed = tuple(b for _, b in rng.consumed)
                    if consumed in seen:
                        continue
                    seen.add(consumed)
                    prob = 1.0
                    for p, b in rng.consumed:
                        prob *= p if b == 1 else (1.0 - p)
                    row_direct[idx_t[y2]] += prob
            frontier = nxt
            depth += 1
        if max(abs(row_direct[i] - Pt[idx_t[y]][i]) for i in range(256)) > 1e-9:
            ok_tensor = False
    print(f"  {f'✅ 一致（{3} 状态抽查）' if ok_tensor else '❌ 不一致'}")

    print("\n" + "=" * 78)
    print("验收 ② v5.3 full_reachable=Ω 退化不再出现（Diff 用轨迹熵，非容量）")
    print("=" * 78)
    for name, r in results.items():
        if name.startswith("v5.3:"):
            for c in r["components"]:
                print(f"  {name} C={c['C']}: Diff(C)={c['Diff']:.3f}bit "
                      f"(旧 full_reachable=Ω→Diff=N={c['nC']}bit 误判通过；新 Diff=轨迹熵)")

    print("\n" + "=" * 78)
    print("验收 ③ 汇总")
    print("=" * 78)
    for name, r in results.items():
        print(f"  {name:14s}: CS′={'✅ 1' if r['CS′'] else '❌ 0'}  𝒞={r['comps']}")
    print(f"\nReplication Invariance: {'✅ 成立（0→0 与 1→1 双边）' if ok_00 and ok_11 else '❌ 失败'}")
    print("=" * 78)


if __name__ == "__main__":
    main()
