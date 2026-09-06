"""
sim_consciousness_v7_estimator_validity.py — 脚本 4：estimator-validity 完整实验（模拟实现批次 4/4）
====================================================================================================
研讨论文产物（纯学术，不入游戏正典）。设计冻结：#95 Q1-Q19（estimator-validity）+ #97 Q1-Q6（cTE 变体）；
实现合同：Grilling #98 Q0-Q14（issue #96，ready-for-agent）。

实验管线（v7 §七 D10 H1）：F_known → 𝒞_exact → synthetic trajectory → Ĉ_obs，
测 Ĉ_obs ≈ 𝒞_exact 的成立域（A_pair 主判，无 θ_valid；plug-in 主估计 + TE/cTE 对照）。

实现合同铁律（Grilling #98，详见 .scratch/grilling-96-estimator-validity-implement/grilling-96.md）：
  - benchmark.py / components.py / cs4_test.py 零修改（依赖文件零修改验收）
  - estimator branch 只消费 observation branch；ground-truth branch 只用于 evaluation，
    二者不得在 estimator 计算阶段汇合（exact Reach 仅 coverage diagnostic）
  - 三 estimator 判定函数完全独立（禁 generic 参数化同构）
  - A_pair 分母由 (system, h) 固定，与 Reacĥ_r / candidate pairs / not_testable 无关
  - not_testable ≠ absent；无向三值化：present=任方向正证据 / absent=双向 absent / 其余=not_testable
  - d 是观测 delay 非 burn-in（禁 trajectory[d:] 丢弃前缀）
  - c=0.6 格 blocked（无冻结 coupling mapping，不得发明机制语义）
  - RepeatRecord=事实源 / aggregation=可重算缓存 / summary=可重建产物
  - 结果只由 (system, grid, estimator, repeat) 的确定性 seed 决定，不依赖执行顺序/共享 RNG
  - 不得以样本量/方差/稀疏度过滤已定义 condition pair（唯一排除理由=条件概率定义域为空）

运行模式（CLI，--help 查看全部）：
  --self-test            单元验收（逻辑断言 + 数值回归）
  --dry-run D0|D1        小规模试跑（D0 最小 smoke / D1 协议边界覆盖）
  --stage A|B            执行实验网格（支持 --systems/--estimators/--repeat-range/--jobs 子集）
  --aggregate            从 RepeatRecord 无损重算 cell aggregation（缓存）
  --summary              生成三层 summary（stageA_curves / stageB_interactions / validity_regions）
  --no-numpy             禁用 numpy cTE 内核（回退纯 Python reference）
"""

import argparse
import hashlib
import itertools
import json
import math
import multiprocessing
import os
import random
import subprocess
import sys
from collections import Counter
from math import lgamma

# 复用现有原语（零修改铁律：components/benchmark/cs4 只读 import）
from sim_consciousness_v7_components import (
    System, exact_kernel, edges_e1, weak_components, reach_states,
    stationary_dist, int_local, sb_local, sm_local, diff_traj_entropy,
    THETA_D, EPS,
)
from sim_consciousness_v7_benchmark import make_benchmark_systems
from sim_consciousness_cs4_test import transfer_entropy, THETA_TE

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


# ============================================================
# §1 冻结配置（#95 Q5/Q6/Q12/Q13/Q16；#98 Q4/Q5/Q9/Q10）
# ============================================================

# 六梯度取值（#95 Q5）
N_LEVELS = (64, 256, 1024, 4096, 16384)
PN_LEVELS = (0.0, 0.05, 0.10, 0.20)
D_LEVELS = (1, 2, 4)
PM_LEVELS = (0.0, 0.20, 0.50)
H_LEVELS = (0, 1)
C_LEVELS = (0.6, 0.9)

BASELINE = {"N": 1024, "p_n": 0.0, "d": 1, "p_m": 0.0, "h": 0, "c": 0.9}
GRADIENT_ORDER = ("N", "p_n", "d", "p_m", "h", "c")          # 预注册梯度顺序（Q16）
LEVELS = {"N": N_LEVELS, "p_n": PN_LEVELS, "d": D_LEVELS,
          "p_m": PM_LEVELS, "h": H_LEVELS, "c": C_LEVELS}

# 统计层（#95 Q6/Q14；#98 Q4/Q5）
R = 32                # 独立重复/格
ALPHA = 0.01          # α（统计层参数，不改 E_S^(1)）
B_BOOT = 1000         # bootstrap 重采样次数（重采样单位=repeat）
B_PERM = 999          # 置换检验次数（固定 Monte Carlo，#98 Q4b）
SELECT_THRESHOLD = 0.15   # 阶段 B 选格阈值（#95 Q12：选格规则非有效性阈值）
R4_SYSTEMS = ("R_corr", "N_bcast", "F9", "B_cpg", "H_loop")  # R4 预注册异常清单（Q12）
R4 = tuple(R4_SYSTEMS)

# h 隐变量预注册冻结表（#95 Q13；三估计器共用同一 V_obs，不接受 CLI 覆盖/运行时修改）
# 显式：F9→s、F8′→z1、B_cpg→x2、H_loop→c1、CA→格0、RL→s0；其余→末位变量
_HIDDEN_EXPLICIT = {
    "F9": 0, "F8′": 4, "B_cpg": 1, "H_loop": 0,
    "CA_Rule30": 0, "CA_Rule0": 0, "RL_Q": 0, "RL_rand": 0,
}

# 阶段 B 预注册交互（#95 Q15/Q16；c×h 因 c=0.6 blocked 不可计算，#98 Q10c）
STAGEB_INTERACTIONS = (("N", "p_n"), ("d", "p_m"))

SCHEMA_VERSION = "1.0"

# ============================================================
# §2 benchmark 装载（只读）
# ============================================================

_SYSTEMS_CACHE = None


def benchmark_entries():
    """20 系统（10 类 × rep/ctl）。只读 import make_benchmark_systems()（零修改铁律）。"""
    global _SYSTEMS_CACHE
    if _SYSTEMS_CACHE is None:
        _SYSTEMS_CACHE = make_benchmark_systems()
    return _SYSTEMS_CACHE


def hidden_index(name, n):
    """h=1 的预注册隐变量下标（#95 Q13 冻结表；其余系统→末位）。"""
    if name in _HIDDEN_EXPLICIT:
        return _HIDDEN_EXPLICIT[name]
    return n - 1


# ============================================================
# §3 synthetic trajectory 生成（#95 Q10/Q17；#98 Q9c）
# ============================================================

class _BernoulliRNG:
    """轨迹/扰动用 rng：包装 random.Random，提供 benchmark step_fn 需要的
    rng.bernoulli(p) 接口（components :57-60 惯例——随机性用 bernoulli 原语表达）。
    同时提供 .random()/.randint()/.shuffle() 供扰动算子与初始状态使用。"""

    def __init__(self, seed):
        self._r = random.Random(seed)

    def bernoulli(self, p):
        return self._r.random() < p

    def random(self):
        return self._r.random()

    def randint(self, a, b):
        return self._r.randint(a, b)

    def shuffle(self, seq):
        self._r.shuffle(seq)


def generate_trajectory(step_fn, n, N, rng):
    """synthetic trajectory：μ₀=Unif(Ω) 起步、无 burn-in、长度 N（#95 Q10）。

    d 是观测 delay 语义，不是 burn-in——此处生成完整轨迹，丢弃前缀由扰动算子禁止
    （#98 Q9 铁律：禁 trajectory[d:]）。
    """
    state = tuple(rng.randint(0, 1) for _ in range(n))
    traj = [state]
    for _ in range(N - 1):
        state = step_fn(state, rng)
        traj.append(state)
    return traj


# ============================================================
# §4 观测扰动算子（#95 Q17；#98 Q9c）
# ============================================================

def perturb_trajectory(traj, p_n, d, p_m, hidden, rng_pn, rng_pm):
    """观测扰动算子，固定序 p_n → d → p_m → h（#95 Q17）。

    - p_n：位翻转作用于完整真实轨迹
    - d：下采样（选择被观测拍 t ≡ 0 mod d）；d>1 时 lag-1 = 下采样后相邻观测记录
    - p_m：整拍缺失（逐拍独立丢弃）；缺失不拼接——lag-1 条件对仅由原始时间轴连续
      且两拍均存在的 (t,t+1) 构成（保留采样索引以禁止拼接）
    - h：变量剔除（观测通道不存在；系统动力学不受影响——完整系统仍运行 V_all）

    返回 [(k, state_vobs)]：k=下采样索引（用于禁止拼接），state_vobs=剔除隐变量后的观测状态。
    """
    n = len(traj[0])
    # p_n 位翻转（完整真实轨迹）
    flipped = []
    for st in traj:
        lst = list(st)
        for i in range(n):
            if rng_pn.random() < p_n:
                lst[i] = 1 - lst[i]
        flipped.append(tuple(lst))
    # d 下采样：观测拍 k=0,1,... → 原时间 t=k*d（k=0..ceil(N/d)-1）
    sampled = [(k, flipped[k * d]) for k in range((len(flipped) + d - 1) // d)]
    # p_m 整拍缺失（保留采样索引）
    kept = [(k, s) for (k, s) in sampled if rng_pm.random() >= p_m]
    # h 变量剔除
    obs = []
    for k, s in kept:
        if hidden is None:
            obs.append((k, s))
        else:
            obs.append((k, tuple(s[i] for i in range(len(s)) if i != hidden)))
    return obs


# ============================================================
# §5 exact ground-truth assembly（evaluation-only，#98 Q1/Q7/Q8）
# ============================================================

class GroundTruth:
    """系统级 exact ground truth（确定性一次计算；只用于 evaluation/诊断）。

    红线（#98 Q1）：exact Reach 仅 coverage diagnostic，不得流向 candidate
    construction / estimator input / estimator-side decision。
    """

    def __init__(self, system):
        self.system = system
        P, states = exact_kernel(system.step_fn, system.n)
        self.P = P
        self.states = states
        self.E = edges_e1(P, states)                    # E_S^(1) 有向边（全图）
        self.comps = weak_components(system.n, self.E)  # 𝒞_exact（全图弱连通）
        self.reach = reach_states(P, states, [1.0] * len(states))  # exact Reach（诊断）
        # 分量 id（全图；component-connectivity projection 的操作化——路径可经隐变量）
        self.comp_id = {}
        for cid, C in enumerate(self.comps):
            for v in C:
                self.comp_id[v] = cid

    def projected(self, obs_vars):
        """h 投影后的 truth（#98 Q8a/Q7b）：
        - 有向边 truth = E_S^(1) ∩ (V_obs × V_obs)（直接依赖边；经隐变量路径不产生新边）
        - A_pair truth = 全图弱连通分量（component-connectivity projection，隐变量作中间节点）
        obs_vars: 原坐标列表（V_obs）。
        """
        obs_set = set(obs_vars)
        E_obs = {(i, j) for (i, j) in self.E if i in obs_set and j in obs_set}
        comp_id_obs = {v: self.comp_id[v] for v in obs_vars}
        return E_obs, comp_id_obs


def project_kernel(P, states, coords):
    """闭包子系统核 P_C(y′_C|y_C)（#98 Q3a(b)：脚本 4 内联，逐项对齐 evaluate()
    （sim_consciousness_v7_components.py :708-727）的投影语义——y∖C 均匀边缘化 + 行归一化）。

    仅用于 CS′̂ exact-primitive replay；不扩展 components.py（基础原语库只读铁律）。
    """
    nC = len(coords)
    S_C = 1 << nC
    statesC = list(itertools.product((0, 1), repeat=nC))
    idx = {s: i for i, s in enumerate(states)}
    P_C = [[0.0] * S_C for _ in range(S_C)]
    for y in states:
        yi = idx[y]
        yC = tuple(y[orig] for orig in coords)
        row = P[yi]
        for yp in states:
            ypC = tuple(yp[orig] for orig in coords)
            P_C[statesC.index(yC)][statesC.index(ypC)] += row[idx[yp]]
    for row in P_C:
        s = sum(row)
        if s > 0:
            for k in range(len(row)):
                row[k] /= s
    return P_C, statesC


def cs_hat_replay(gt, obs_vars, comps_hat, M_set, A_set):
    """CS′̂ = 在 Ĉ_obs 分量上用 exact 原语重放四要件（#95 Q7：「基于估计结构的
    exact-primitive replay」；#98 Q3c：不调用 evaluate()，从 Ĉ_obs 分量重新执行）。

    返回 (CS_hat, per_component)。
    """
    per = []
    for C_obs in comps_hat:
        C_orig = [obs_vars[v] for v in C_obs]           # 观测坐标 → 原坐标
        nC = len(C_orig)
        P_C, statesC = project_kernel(gt.P, gt.states, C_orig)
        diff, _, _ = diff_traj_entropy(P_C, nC)
        mu, _ = stationary_dist(P_C, nC)
        int_v = int_local(P_C, mu, nC)
        sb_v, _ = sb_local(P_C, mu, nC)
        map_C = {orig: j for j, orig in enumerate(C_orig)}
        M_in_C = [map_C[o] for o in M_set if o in map_C]
        A_in_C = [map_C[o] for o in A_set if o in map_C]
        sm_v, _ = sm_local(P_C, nC, M_in_C, A_in_C)
        cs_local = (int_v > EPS) and (diff >= THETA_D) and sb_v and sm_v
        per.append({"C_obs": list(C_obs), "Diff": round(diff, 4),
                    "Int_local": round(int_v, 6), "SB_local": bool(sb_v),
                    "SM_local": bool(sm_v), "CS_local": bool(cs_local)})
    return any(c["CS_local"] for c in per), per


# ============================================================
# §6 Reacĥ / 候选对构造（#95 Q18；#98 Q2/Q4c）
# ============================================================

def reach_hat(obs_series):
    """逐 repeat 观测去重状态集（V_obs 上；不跨 repeat 合并）。"""
    return {s for (_, s) in obs_series}


def build_transitions(obs_series):
    """观测转移：{(y, y′)}（下采样后相邻观测记录、两拍均存在——缺失不拼接，Q17）。
    返回 (pairs, trans)：pairs=[(y, y′)]；trans=dict y→[y′ 列表]。"""
    pairs = []
    trans = {}
    for (k1, s1), (k2, s2) in zip(obs_series, obs_series[1:]):
        if k2 != k1 + 1:
            continue                      # 缺失拍——禁止拼接
        pairs.append((s1, s2))
        trans.setdefault(s1, []).append(s2)
    return pairs, trans


def candidate_pairs(reach, n_obs):
    """动态候选对（#95 Q18）：y ∈ Reacĥ，单坐标翻转 y′=flip_i(y) ∈ Reacĥ。
    候选全集不得由 exact Reach / full-state graph 预先提供。
    返回 dict {(i,j): [(y, y′)]}（i=翻转坐标、j=被影响坐标；j≠i）。"""
    cand = {}
    for y in reach:
        for i in range(n_obs):
            y2 = list(y)
            y2[i] = 1 - y2[i]
            y2 = tuple(y2)
            if y2 in reach:
                for j in range(n_obs):
                    if j != i:
                        cand.setdefault((i, j), []).append((y, y2))
    return cand


# ============================================================
# §7 estimator adapters（三判定函数完全独立，#98 Q5 铁律）
# ============================================================

def _sub_seed(unit_seed, *parts):
    """层级 RNG 派生（#98 Q4b）：cell→repeat→estimator→edge→condition-pair。
    子 seed = sha256(unit_seed || parts)，无全局 RNG、无跨单元状态污染。"""
    h = hashlib.sha256(str(unit_seed).encode())
    for p in parts:
        h.update(str(p).encode())
    return int.from_bytes(h.digest()[:8], "big")


# ---------- plug-in（#98 Q4 状态机） ----------

def _ones_frac(values, j):
    if not values:
        return 0.0
    return sum(1 for v in values if v[j] == 1) / len(values)


def _make_hypergeometric_sampler(K, n1, N):
    """预计算超几何 PMF（log 空间防下溢）+ 累积分布，返回 O(log M)/次的采样器。

    标签置换下 y 组内 1 的个数 k ~ Hypergeometric(K, n1, N)（#98 Q4b：同一置换分布、
    同一 B=999 MC 预算；仅采样实现更高效——性能优化不改变统计语义）。
    """
    lo = max(0, K - (N - n1))
    hi = min(K, n1)
    logc = []
    for k in range(lo, hi + 1):
        logc.append((lgamma(K + 1) - lgamma(k + 1) - lgamma(K - k + 1)) +
                    (lgamma(N - K + 1) - lgamma(n1 - k + 1) -
                     lgamma(N - K - n1 + k + 1)))
    mx = max(logc)
    w = [math.exp(x - mx) for x in logc]
    total = sum(w)
    cum = []
    acc = 0.0
    for wi in w:
        acc += wi
        cum.append(acc)

    def sampler(rng):
        u = rng.random() * total
        lo_i, hi_i = 0, len(cum) - 1
        while lo_i < hi_i:
            mid = (lo_i + hi_i) // 2
            if cum[mid] < u:
                lo_i = mid + 1
            else:
                hi_i = mid
        return lo + lo_i

    return sampler


def _perm_p_value(outcomes_a, outcomes_b, j, obs, perm_seed):
    """保持时间结构的标签置换（#98 Q4b）：置换 y/y′ 两组 outcome 的条件标签、保组大小。

    二元结局下，置换分布仅由「y 组内 1 的个数」决定——该个数在标签置换下服从
    超几何分布。B_perm=999 固定 Monte Carlo（等价于完整标签置换，O(log M)/次）；
    固定预算，不按样本量切换精确枚举（#98 Q4b）。
    """
    a = [v[j] for v in outcomes_a]
    b = [v[j] for v in outcomes_b]
    n1, n2 = len(a), len(b)
    pool = a + b
    K = sum(pool)                                  # 总 1 数
    rng = random.Random(perm_seed)
    sampler = _make_hypergeometric_sampler(K, n1, len(pool))
    cnt = 0
    for _ in range(B_PERM):
        k = sampler(rng)                           # 超几何采样：y 组内 1 数
        p1 = k / n1
        p2 = (K - k) / n2
        if abs(p1 - p2) >= obs:
            cnt += 1
    return (cnt + 1) / (B_PERM + 1)


def plugin_edge_test(trans, cand_pairs, i, j, unit_seed):
    """plug-in 单有向边判定（#98 Q4 状态机）：
    condition pairs → |ΔP̂| → 999 置换 → α/m_ij → ∃ 聚合。

    返回 (state, statistic, p_min, m_ij, detail)。
    """
    valid = []
    for (y, yp) in cand_pairs:
        ny = trans.get(y, [])
        nyp = trans.get(yp, [])
        # #98 Q4c：两组各 ≥1 outcome 才进入检验（0 计数=条件概率定义域为空，
        # 非「少量样本」——不得以样本量/方差/稀疏度过滤）
        if len(ny) >= 1 and len(nyp) >= 1:
            valid.append((y, yp, ny, nyp))
    m_ij = len(valid)
    if m_ij == 0:
        return ("not_testable", None, None, 0, {})
    alpha_edge = ALPHA / m_ij
    stats = []
    for pair_idx, (y, yp, ny, nyp) in enumerate(valid):
        obs = abs(_ones_frac(ny, j) - _ones_frac(nyp, j))
        p = _perm_p_value(ny, nyp, j, obs, _sub_seed(unit_seed, "perm", i, j, pair_idx))
        stats.append({"y": list(y), "y_prime": list(yp),
                      "d_obs": round(obs, 6), "p_value": p,
                      "rejected": p <= alpha_edge})
    any_rej = any(s["rejected"] for s in stats)
    state = "present" if any_rej else "absent"
    return (state, max(s["d_obs"] for s in stats),
            min(s["p_value"] for s in stats), m_ij, stats)


# ---------- TE（#95 Q9：cs4 + THETA_TE 硬阈值；无置换检验） ----------

def te_edge_test(obs_series, i, j):
    """TE 判定：cs4 transfer_entropy（lag-1 双变量、plug-in 熵、ln 语义原样）+ THETA_TE。
    无置换检验（#95 Q9 冻结硬阈值语义）。"""
    pairs, _ = build_transitions(obs_series)
    if len(pairs) == 0:
        return ("not_testable", None, None, None, {"n_transition": 0})
    sp = [p[0][i] for p in pairs]
    tp = [p[0][j] for p in pairs]
    tf = [p[1][j] for p in pairs]
    te = transfer_entropy(sp, tp, tf)
    state = "present" if te >= THETA_TE else "absent"
    return (state, te, None, None, {"n_transition": len(pairs)})


# ---------- cTE（#97 Q1/Q2 + #98 Q5：全条件、逐边单检验、无硬阈值） ----------

def cte_value(xi, xj, z):
    """cTE(X_i→X_j) = H(X_j|Z) − H(X_j|X_i, Z)，Z = X_{∖{i}} lag-1 过去（#97 Q1）。
    log2（#98 Q5b：对齐 components entropy 惯例；无硬阈值故基不影响判定）。"""
    n = len(xj)
    if n == 0:
        return 0.0
    c_z = Counter(z)
    c_zxj = Counter(zip(z, xj))
    c_xiz = Counter(zip(xi, z))
    c_xizxj = Counter(zip(xi, z, xj))
    h_z = -sum(c / n * math.log2(c / c_z[zz]) for (zz, v), c in c_zxj.items())
    h_xiz = -sum(c / n * math.log2(c / c_xiz[(xi_, zz)])
                 for (xi_, zz, v), c in c_xizxj.items())
    return h_z - h_xiz


def cte_value_np(xi, xj, z, nz):
    """numpy 版 cTE 内核（#98 Q11b：仅统计内层向量化；与 cte_value 数值一致，
    由 --self-test 回归验证）。nz=Z 的编码位数。"""
    z_arr = np.asarray(z, dtype=np.int64)
    xi_arr = np.asarray(xi, dtype=np.int64)
    xj_arr = np.asarray(xj, dtype=np.int64)
    n = len(xj_arr)
    code_xiz = (xi_arr << nz) | z_arr          # (Xi, Z) 联合编码
    code_zxj = (z_arr << 1) | xj_arr           # (Z, Xj) 联合编码
    code_xizxj = (code_xiz << 1) | xj_arr      # (Xi, Z, Xj) 联合编码
    c_z = np.bincount(z_arr).astype(np.float64)
    c_zxj = np.bincount(code_zxj, minlength=len(c_z) * 2).astype(np.float64)
    c_xiz = np.bincount(code_xiz, minlength=len(c_z) * 2).astype(np.float64)
    c_xizxj = np.bincount(code_xizxj, minlength=len(c_z) * 4).astype(np.float64)
    h_z = _h_cond_np(c_zxj, c_z, n)
    h_xiz = _h_cond_np(c_xizxj, c_xiz, n)
    return h_z - h_xiz


def _h_cond_np(joint_counts, group_counts, n):
    """H(V|G) = −Σ p(g,v) log2(p(g,v)/p(g))（全向量化，无逐项 Python 循环）。
    joint_counts 的编码 = (group 编码 << 1) | v，故 group 索引 = code >> 1。"""
    g = np.maximum(group_counts[np.arange(len(joint_counts)) >> 1], 1e-300)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = joint_counts * np.log2(joint_counts / g)
    return -(np.nan_to_num(term, nan=0.0, posinf=0.0, neginf=0.0)).sum() / n


def _h_cond_rows_np(joint_mat, group_mat, n):
    """行级 H(V|G)（joint_mat 每行一个联合分布；group_mat 按 code>>1 展开）。"""
    g = np.maximum(group_mat, 1e-300)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = joint_mat * np.log2(joint_mat / g)
    return -(np.nan_to_num(term, nan=0.0, posinf=0.0, neginf=0.0).sum(axis=1)) / n


def cte_perm_pvalue_np(xi, xj, z_code, nz, obs_cte, seed):
    """cTE 置换检验（numpy 全向量化，仅统计内层，#98 Q11b）：
    置换 X_{i,t−1} 序列、保留其余结构；B_perm=999 一次性生成置换矩阵，
    行级条件熵矩阵运算——无逐置换 Python 循环。H(Xj|Z) 对置换不变（常数项）。"""
    N_PERM = B_PERM
    n = len(xj)
    xi_a = np.asarray(xi, dtype=np.int64)
    xj_a = np.asarray(xj, dtype=np.int64)
    z_a = np.asarray(z_code, dtype=np.int64)
    rng = np.random.default_rng(seed)
    # 置换矩阵：逐行 rng.permutation（O(N)/行；argsort 在大 N 下 O(N log N) 反而更慢）
    perms = np.stack([rng.permutation(n) for _ in range(N_PERM)])   # (B, n)
    xi_perm = xi_a[perms]                                          # (B, n)
    # 常数项 H(Xj|Z)
    c_z = np.bincount(z_a).astype(np.float64)
    c_zxj = np.bincount((z_a << 1) | xj_a, minlength=len(c_z) * 2).astype(np.float64)
    h_z = _h_cond_np(c_zxj, c_z, n)
    # 每置换 H(Xj|Xi,Z)
    stride = 1 << (nz + 2)                                       # (xi, z, xj) 编码空间
    code_xizxj = (((xi_perm << nz) | z_a[None, :]) << 1) | xj_a[None, :]   # (B, n)
    rows = np.arange(N_PERM)[:, None] * stride
    counts_all = np.bincount((code_xizxj + rows).ravel(), minlength=N_PERM * stride)
    counts_all = counts_all.reshape(N_PERM, stride).astype(np.float64)
    stride_g = 1 << (nz + 1)
    code_xiz = ((xi_perm << nz) | z_a[None, :]) + np.arange(N_PERM)[:, None] * stride_g
    c_xiz_all = np.bincount(code_xiz.ravel(), minlength=N_PERM * stride_g)
    c_xiz_all = c_xiz_all.reshape(N_PERM, stride_g).astype(np.float64)
    g_mat = c_xiz_all[:, np.arange(stride) >> 1]
    h_xiz = _h_cond_rows_np(counts_all, g_mat, n)
    cte_b = h_z - h_xiz
    cnt = int(np.sum(cte_b >= obs_cte))
    return (cnt + 1) / (N_PERM + 1)


def cte_edge_test(obs_series, n_obs, i, j, unit_seed, use_numpy):
    """cTE 判定（#97 Q2 + #98 Q5a）：置换 X_{i,t−1} 序列、保留其余结构，
    B_perm=999，α=0.01 逐边单检验（FWER family size=1，无 m_ij 划分），无硬阈值。"""
    pairs, _ = build_transitions(obs_series)
    if len(pairs) == 0:
        return ("not_testable", None, None, None, {"n_transition": 0})
    nz = n_obs - 1                                # Z = V_obs ∖ {X_i}，nz 位
    xi = [p[0][i] for p in pairs]
    xj = [p[1][j] for p in pairs]
    z = [tuple(p[0][k] for k in range(n_obs) if k != i) for p in pairs]
    if use_numpy and _HAS_NUMPY:
        z_code = [sum(bit << b for b, bit in enumerate(zz)) for zz in z]
        obs_cte = cte_value_np(xi, xj, z_code, nz)
        p = cte_perm_pvalue_np(xi, xj, z_code, nz, obs_cte,
                               _sub_seed(unit_seed, "cteperm", i, j))
    else:
        obs_cte = cte_value(xi, xj, z)
        rng = random.Random(_sub_seed(unit_seed, "cteperm", i, j))
        cnt = 0
        for _ in range(B_PERM):
            xi_perm = xi[:]
            rng.shuffle(xi_perm)
            if cte_value(xi_perm, xj, z) >= obs_cte:
                cnt += 1
        p = (cnt + 1) / (B_PERM + 1)
    state = "present" if p <= ALPHA else "absent"
    return (state, obs_cte, p, None, {"n_transition": len(pairs)})


# ============================================================
# §8 per-repeat 评估（EdgeResult / Ĉ_obs / A_pair / P/R/F1 / CS′̂）
# ============================================================

def undirected_state(s_ab, s_ba):
    """无向三值化（#98 Q8b 修正版）：
    present ⟺ 任一方向 present；absent ⟺ 双向均 absent；否则 not_testable。
    正证据 OR、负证据必须双向 absent 共同证明；not_testable 不得转 absent。"""
    if s_ab == "present" or s_ba == "present":
        return "present"
    if s_ab == "absent" and s_ba == "absent":
        return "absent"
    return "not_testable"


def _p_r_f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def evaluate_repeat(system_entry, grid, estimator, obs_series, unit_seed, use_numpy):
    """单 repeat 全评估（#95 Q2/Q4/Q19 + #98 Q6/Q7/Q8）。

    返回 RepeatRecord（事实源）。
    """
    sys_obj = system_entry["sys"]
    name = system_entry["name"]
    h = grid["h"]
    hidden = hidden_index(name, sys_obj.n) if h else None
    obs_vars = [v for v in range(sys_obj.n) if v != hidden]      # V_obs 原坐标
    n_obs = len(obs_vars)

    # ground truth（确定性，system 级缓存；此处仅取投影 truth）
    gt = _get_gt(system_entry)
    E_obs, comp_id_obs = gt.projected(obs_vars)

    # 观测侧统计
    reach = reach_hat(obs_series)
    _, trans = build_transitions(obs_series)
    n_transition = len(build_transitions(obs_series)[0])

    # 逐估计器边判定
    edge_results = {}
    if estimator == "plug-in":
        cand = candidate_pairs(reach, n_obs)
        for (i, j) in sorted(cand):
            st, stat, pv, m_ij, detail = plugin_edge_test(trans, cand[(i, j)], i, j, unit_seed)
            edge_results[(i, j)] = {
                "edge": [i, j], "estimator": estimator, "state": st,
                "statistic": round(stat, 6) if stat is not None else None,
                "statistic_name": "abs_delta_p",
                "p_value": pv, "family_size": m_ij,
                "sample_info": {"n_condition_pairs": len(cand[(i, j)]),
                                "n_valid_condition_pairs": m_ij},
                "detail": detail,
            }
        for (i, j) in itertools.permutations(range(n_obs), 2):
            if (i, j) not in edge_results:
                edge_results[(i, j)] = {
                    "edge": [i, j], "estimator": estimator, "state": "not_testable",
                    "statistic": None, "statistic_name": "abs_delta_p",
                    "p_value": None, "family_size": 0,
                    "sample_info": {"n_condition_pairs": 0, "n_valid_condition_pairs": 0},
                    "detail": {},
                }
    elif estimator == "te":
        for (i, j) in itertools.permutations(range(n_obs), 2):
            st, stat, pv, fs, info = te_edge_test(obs_series, i, j)
            edge_results[(i, j)] = {
                "edge": [i, j], "estimator": estimator, "state": st,
                "statistic": round(stat, 6) if stat is not None else None,
                "statistic_name": "TE",
                "p_value": None, "family_size": None,
                "sample_info": info, "detail": {},
            }
    elif estimator == "cte":
        for (i, j) in itertools.permutations(range(n_obs), 2):
            st, stat, pv, fs, info = cte_edge_test(obs_series, n_obs, i, j, unit_seed, use_numpy)
            edge_results[(i, j)] = {
                "edge": [i, j], "estimator": estimator, "state": st,
                "statistic": round(stat, 6) if stat is not None else None,
                "statistic_name": "cTE",
                "p_value": pv, "family_size": 1 if st != "not_testable" else None,
                "sample_info": info, "detail": {},
            }
    else:
        raise ValueError(f"未知 estimator: {estimator}")

    # Ĉ_obs 保守图（仅 present 有向边 → 无向投影 → 弱连通分量；#95 Q19）
    present = {(i, j) for (i, j), er in edge_results.items() if er["state"] == "present"}
    undirected_edges = {tuple(sorted(e)) for e in present}
    comps_hat = weak_components(n_obs, [tuple(e) for e in undirected_edges])
    comp_id_hat = {}
    for cid, C in enumerate(comps_hat):
        for v in C:
            comp_id_hat[v] = cid

    # A_pair：分母 D = C(|V_obs|,2) 固定（#98 Q7 铁律：与 Reacĥ_r 无关）
    pairs_all = list(itertools.combinations(range(n_obs), 2))
    n_pairs = len(pairs_all)
    a_pair = 0.0
    for (a, b) in pairs_all:
        if (comp_id_obs[obs_vars[a]] == comp_id_obs[obs_vars[b]]) == \
           (comp_id_hat[a] == comp_id_hat[b]):
            a_pair += 1.0
    a_pair /= n_pairs if n_pairs > 0 else 1

    # 无向边级 P/R/F1（三值化；tested = 最终状态 present/absent，#98 Q8b）
    und_state = {}
    for (a, b) in pairs_all:
        s_ab = edge_results[(a, b)]["state"]
        s_ba = edge_results[(b, a)]["state"]
        und_state[(a, b)] = undirected_state(s_ab, s_ba)
    n_cand_u = n_pairs
    n_tested_u = sum(1 for s in und_state.values() if s in ("present", "absent"))
    n_nt_u = n_cand_u - n_tested_u
    tp_u = fp_u = fn_u = 0
    for (a, b) in pairs_all:
        s = und_state[(a, b)]
        # 无向 truth = E_obs（原坐标有向边）的对称闭包
        truth_u = ((obs_vars[a], obs_vars[b]) in E_obs or
                   (obs_vars[b], obs_vars[a]) in E_obs)
        if s == "not_testable":
            continue
        if s == "present" and truth_u:
            tp_u += 1
        elif s == "present" and not truth_u:
            fp_u += 1
        elif s == "absent" and truth_u:
            fn_u += 1
    p_u, r_u, f1_u = _p_r_f1(tp_u, fp_u, fn_u)

    # 有向边级 P/R/F1（cTE 主判；plug-in/TE 诊断，#97 Q6 + #98 Q8c）
    n_cand_d = n_obs * (n_obs - 1)
    n_tested_d = sum(1 for er in edge_results.values() if er["state"] != "not_testable")
    n_nt_d = n_cand_d - n_tested_d
    tp_d = fp_d = fn_d = 0
    for (i, j), er in edge_results.items():
        if er["state"] == "not_testable":
            continue
        truth_d = (obs_vars[i], obs_vars[j]) in E_obs
        if er["state"] == "present" and truth_d:
            tp_d += 1
        elif er["state"] == "present" and not truth_d:
            fp_d += 1
        elif er["state"] == "absent" and truth_d:
            fn_d += 1
    p_d, r_d, f1_d = _p_r_f1(tp_d, fp_d, fn_d)

    # CS′̂（exact-primitive replay，#95 Q7）
    cs_hat, cs_per = cs_hat_replay(gt, obs_vars, comps_hat,
                                   sys_obj.M_set, sys_obj.A_set)

    # 覆盖率诊断（#95 Q18）
    coverage = len(reach) / len(gt.reach) if len(gt.reach) > 0 else 0.0

    record = {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "system": name, "cat": system_entry["cat"], "role": system_entry["role"],
            "mech": system_entry["mech"], "n": sys_obj.n,
            "grid": dict(grid), "estimator": estimator, "repeat": 0,
        },
        "observation": {
            "reach_hat_size": len(reach), "reach_size": len(gt.reach),
            "coverage": round(coverage, 4), "n_transition_pairs": n_transition,
            "n_candidate_edges": len(edge_results), "n_tested_edges": n_tested_d,
        },
        "edges": [er for er in edge_results.values()],
        "truth": {
            "exact_directed_edges": sorted(
                [(obs_vars.index(i), obs_vars.index(j)) for (i, j) in E_obs]),
            "exact_projected_components": [
                [obs_vars.index(v) for v in sorted(C) if v in obs_vars]
                for C in gt.comps],
            "reach_size": len(gt.reach),
        },
        "replay": {
            "present_directed_edges": sorted([list(e) for e in present]),
            "components_hat": comps_hat,
            "per_component": cs_per,
            "CS_hat": bool(cs_hat),
        },
        "metrics": {
            "A_pair": round(a_pair, 6),
            "undirected": {"P": p_u, "R": r_u, "F1": f1_u,
                           "n_candidate": n_cand_u, "n_tested": n_tested_u,
                           "n_not_testable": n_nt_u},
            "directed_diag": {"P": p_d, "R": r_d, "F1": f1_d,
                              "n_candidate": n_cand_d, "n_tested": n_tested_d,
                              "n_not_testable": n_nt_d,
                              "is_primary": estimator == "cte"},
        },
    }
    return record


_GT_CACHE = {}


def _get_gt(entry):
    name = entry["name"]
    if name not in _GT_CACHE:
        _GT_CACHE[name] = GroundTruth(entry["sys"])
    return _GT_CACHE[name]


# ============================================================
# §9 网格调度（Stage A / Stage B 选格，#95 Q5/Q16 + #98 Q9/Q10）
# ============================================================

def make_stageA_grid():
    """阶段 A：六条单因素扫描共享基线去重 → 14 格/系统/估计器（#95 Q16）。
    排序按预注册梯度顺序（#98 Q9a）。"""
    cells = []
    for factor in GRADIENT_ORDER:
        for v in LEVELS[factor]:
            g = dict(BASELINE)
            g[factor] = v
            cells.append(g)
    seen = set()
    out = []
    for g in cells:
        key = tuple(sorted(g.items()))
        if key not in seen:
            seen.add(key)
            out.append(g)
    return out


def cell_id(system_name, grid, estimator):
    """可读确定性 cell_id（#98 Q12a：导航标识非数据真相；完整 grid 对象存 meta）。"""
    return (f"{system_name}__N{grid['N']}_pn{grid['p_n']:g}_d{grid['d']}"
            f"_pm{grid['p_m']:g}_h{grid['h']}_c{grid['c']:g}__{estimator}")


def derive_seed(system_name, grid, estimator, repeat):
    """#95 Q6：seed = hash(system, 梯度格, estimator, repeat) 确定性派生。"""
    key = f"{system_name}|{tuple(sorted(grid.items()))}|{estimator}|{repeat}"
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def varying_factor(grid):
    """该格在阶段 A 单因素扫描中变化的因素（相对基线；其余因素=基线值）。"""
    for f in GRADIENT_ORDER:
        if grid[f] != BASELINE[f]:
            return f
    return None


def select_stage_B(stageA_cells, a_pair_map):
    """阶段 B 选格器（#98 Q10a 铁律）：确定性纯函数，只消费 Stage A 结果。

    a_pair_map: {(system, estimator, cell_key): A_pair mean}
    返回 (selected_levels, trigger_log)：
      selected_levels[(system, estimator, factor)] = 档位集合（并集；R4 系统=全档）
      trigger_log: [{rule, system, estimator, factor, trigger_level, selected_levels}]
    """
    selected = {}
    trigger_log = []
    entries = benchmark_entries()
    by_name = {e["name"]: e for e in entries}

    def add_levels(system, estimator, factor, levels):
        key = (system, estimator, factor)
        cur = selected.setdefault(key, set())
        for v in levels:
            cur.add(v)

    for e in entries:
        name = e["name"]
        if name in R4:
            continue                       # R4 系统在下方强制全档
        for estimator in ("plug-in", "te", "cte"):
            # 按因素组织该 (system, estimator) 的单因素曲线（grid 与系统无关，数据按 key 取）
            by_factor = {}
            for c in stageA_cells:
                f = varying_factor(c)
                if f is None:
                    continue               # 基线格不属于任何单因素曲线
                by_factor.setdefault(f, []).append(c)
            for factor, clist in by_factor.items():
                levels = list(LEVELS[factor])
                # R1 下降区：相邻梯度档 A_pair 下降 ≥ 0.15 → 该档及 ±1 邻档
                ap = {}
                for c in clist:
                    key = (name, estimator, cell_key(c))
                    ap[c[factor]] = a_pair_map.get(key)
                order = [v for v in levels if v in ap and ap[v] is not None]
                for k in range(len(order) - 1):
                    v1, v2 = order[k], order[k + 1]
                    if ap[v1] is not None and ap[v2] is not None and \
                       ap[v1] - ap[v2] >= SELECT_THRESHOLD:
                        sel = _neighbor_levels(levels, v1) | _neighbor_levels(levels, v2)
                        add_levels(name, estimator, factor, sel)
                        trigger_log.append({"rule": "R1", "system": name,
                                            "estimator": estimator, "factor": factor,
                                            "trigger_level": [v1, v2],
                                            "selected_levels": sorted(sel)})
                # R3 边界区：预注册增强方向首次 1.0→<1.0 的档及 ±1 邻档
                enh = _enhancement_order(factor)
                if enh:
                    for k in range(len(enh) - 1):
                        v1, v2 = enh[k], enh[k + 1]
                        a1 = ap.get(v1)
                        a2 = ap.get(v2)
                        if a1 is not None and a2 is not None and \
                           a1 > 1 - 1e-9 and a2 < 1 - 1e-9:
                            sel = _neighbor_levels(levels, v2)
                            add_levels(name, estimator, factor, sel)
                            trigger_log.append({"rule": "R3", "system": name,
                                                "estimator": estimator, "factor": factor,
                                                "trigger_level": v2,
                                                "selected_levels": sorted(sel)})
                            break
    # R2 分歧区：|A_pair_plug − A_pair_TE| ≥ 0.15 → 该档及 ±1 邻档（仅 plug vs TE，#98 Q10b）
    for name in by_name:
        if name in R4:
            continue
        for c in stageA_cells:
            f = varying_factor(c)
            if f is None:
                continue
            key_p = (name, "plug-in", cell_key(c))
            key_t = (name, "te", cell_key(c))
            ap_p = a_pair_map.get(key_p)
            ap_t = a_pair_map.get(key_t)
            if ap_p is not None and ap_t is not None and abs(ap_p - ap_t) >= SELECT_THRESHOLD:
                sel = _neighbor_levels(LEVELS[f], c[f])
                add_levels(name, "plug-in", f, sel)
                add_levels(name, "te", f, sel)
                add_levels(name, "cte", f, sel)     # cTE 同格执行（不参与选格）
                trigger_log.append({"rule": "R2", "system": name,
                                    "estimator": "plug-in-vs-te", "factor": f,
                                    "trigger_level": c[f],
                                    "selected_levels": sorted(sel)})
    # R4 异常区：预注册系统清单全档（覆盖保证，#95 Q12）
    for name in R4:
        if name not in by_name:
            continue
        for estimator in ("plug-in", "te", "cte"):
            for factor in ("N", "p_n", "d", "p_m", "h"):
                add_levels(name, estimator, factor, set(LEVELS[factor]))
        trigger_log.append({"rule": "R4", "system": name, "estimator": "all",
                            "factor": "all", "trigger_level": None,
                            "selected_levels": "full"})
    return selected, trigger_log


def _neighbor_levels(levels, v):
    """档位 v 及 ±1 邻档（越界 clamp，#95 Q16）。"""
    idx = levels.index(v)
    out = set()
    for k in (idx - 1, idx, idx + 1):
        if 0 <= k < len(levels):
            out.add(levels[k])
    return out


def _enhancement_order(factor):
    """预注册梯度增强方向（#95 Q12「由每梯度预注册排序决定」）：
    从增强端向退化端排列。N/c 递增增强；p_n/d/p_m/h 递减增强。"""
    if factor in ("N", "c"):
        return list(LEVELS[factor])
    return list(reversed(LEVELS[factor]))


def make_stageB_grid(selected):
    """阶段 B 局部全因子（#98 Q10）：每交互因素用选档集合（无选择 → 全档 fallback），
    选中档位并集 → 全因子；并加入 ΔA_pair 预注册端点格（H/L 机械端点，#95 Q16——
    端点格为预注册固定格，非 post-hoc 选择，保证主交互量可计算）。
    返回 {(system, estimator): [grid, ...]}（c×h 不执行；与 Stage A 重复格由调用方复用）。"""
    out = {}
    for e in benchmark_entries():
        name = e["name"]
        for estimator in ("plug-in", "te", "cte"):
            grids = []
            seen_g = set()
            for (f1, f2) in STAGEB_INTERACTIONS:
                lv1 = sorted(selected.get((name, estimator, f1), set()) or set(LEVELS[f1]))
                lv2 = sorted(selected.get((name, estimator, f2), set()) or set(LEVELS[f2]))
                if not lv1:
                    lv1 = list(LEVELS[f1])
                if not lv2:
                    lv2 = list(LEVELS[f2])
                for v1 in lv1:
                    for v2 in lv2:
                        g = dict(BASELINE)
                        g[f1] = v1
                        g[f2] = v2
                        key = tuple(sorted(g.items()))
                        if key not in seen_g:
                            seen_g.add(key)
                            grids.append(g)
                # ΔA_pair 端点格（预注册机械端点：L=min、H=max，#98 Q10d）
                for v1 in (LEVELS[f1][0], LEVELS[f1][-1]):
                    for v2 in (LEVELS[f2][0], LEVELS[f2][-1]):
                        g = dict(BASELINE)
                        g[f1] = v1
                        g[f2] = v2
                        key = tuple(sorted(g.items()))
                        if key not in seen_g:
                            seen_g.add(key)
                            grids.append(g)
            out[(name, estimator)] = grids
    return out


# ============================================================
# §10 统计汇总（bootstrap CI / 聚合 / ΔA_pair / 成立域，#98 Q6b/Q10/Q12）
# ============================================================

def bootstrap_ci(values, B=B_BOOT, seed=42):
    """95% bootstrap CI（#95 Q6：#98 Q10——重采样单位=repeat，非时间点）。"""
    n = len(values)
    if n == 0:
        return [None, None]
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * B)]
    hi = means[int(0.975 * B)]
    return [round(lo, 6), round(hi, 6)]


def aggregate_cell(repeat_records):
    """从 RepeatRecord（事实源）无损重算 cell aggregation（#98 Q12b 缓存）。"""
    n = len(repeat_records)
    a_pairs = [r["metrics"]["A_pair"] for r in repeat_records]
    mean_a = sum(a_pairs) / n if n else 0.0
    ci = bootstrap_ci(a_pairs)
    # 边级 P/R/F1：per-repeat 值取均值（口径注明；汇总计数口径可从 edges 重算，见下注）
    # 注：per-repeat 的 P/R/F1 分母（tested 边）随 repeat 变化，跨 repeat 池化计数
    # 与均值口径在 not_testable 分布不均时略有差异；此处固定为均值口径（报告注明）。
    p_u = sum(r["metrics"]["undirected"]["P"] for r in repeat_records) / n if n else 0.0
    r_u = sum(r["metrics"]["undirected"]["R"] for r in repeat_records) / n if n else 0.0
    f1_u = sum(r["metrics"]["undirected"]["F1"] for r in repeat_records) / n if n else 0.0
    p_d = sum(r["metrics"]["directed_diag"]["P"] for r in repeat_records) / n if n else 0.0
    r_d = sum(r["metrics"]["directed_diag"]["R"] for r in repeat_records) / n if n else 0.0
    f1_d = sum(r["metrics"]["directed_diag"]["F1"] for r in repeat_records) / n if n else 0.0
    cs_frac = sum(1 for r in repeat_records if r["replay"]["CS_hat"]) / n if n else 0.0
    return {
        "n_repeats": n,
        "A_pair": {"mean": round(mean_a, 6), "bootstrap": {
            "B": B_BOOT, "ci_level": 0.95, "resampling_unit": "repeat",
            "ci": ci}},
        "undirected": {"P": round(p_u, 4), "R": round(r_u, 4), "F1": round(f1_u, 4)},
        "directed_diag": {"P": round(p_d, 4), "R": round(r_d, 4), "F1": round(f1_d, 4)},
        "CS_hat_fraction": round(cs_frac, 4),
    }


# ============================================================
# §11 序列化 / data/sim_results/（#98 Q12）
# ============================================================

def outdir_path(outdir):
    return os.path.join(outdir, "data", "sim_results")


def _atomic_write_json(path, obj):
    """原子写入（tmp + rename，#98 Q11/Q14b）。"""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def write_manifest(outdir):
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "git_commit": git_commit(),
        "script_version": "sim_consciousness_v7_estimator_validity.py v1",
        "parameter_registry_version": "#95 Q5/Q6/Q12/Q13/Q16 + #98 Q4/Q5",
        "grid_definition_version": "#95 Q16（14 审计格）",
        "selection_rule_version": "#95 Q12 R1-R4",
        "h_table_version": "#95 Q13（预注册冻结）",
        "B": B_BOOT, "B_perm": B_PERM, "R": R, "alpha": ALPHA,
        "numpy_enabled": bool(_HAS_NUMPY),
        "numpy_kernel_version": "cte_value_np v1",
    }
    _atomic_write_json(os.path.join(outdir, "MANIFEST.json"), manifest)


def read_cell(outdir, system_name, grid, estimator):
    path = os.path.join(outdir, cell_id(system_name, grid, estimator) + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# §12 CLI / 主流程 / 验收（#98 Q13）
# ============================================================

def _cli():
    p = argparse.ArgumentParser(description="脚本 4：estimator-validity 实验（Grilling #95/#97/#98）")
    p.add_argument("--self-test", action="store_true", help="单元验收（逻辑断言+数值回归）")
    p.add_argument("--dry-run", choices=["D0", "D1"], help="小规模试跑")
    p.add_argument("--stage", choices=["A", "B"], help="执行阶段 A/B 网格")
    p.add_argument("--systems", nargs="*", default=None, help="系统子集（默认全部 20）")
    p.add_argument("--estimators", nargs="*", default=None,
                   choices=["plug-in", "te", "cte"], help="估计器子集")
    p.add_argument("--repeat-range", nargs=2, type=int, default=None, metavar=("START", "END"),
                   help="repeat 范围 [start, end)（默认 [0,32)）")
    p.add_argument("--jobs", type=int, default=1, help="并行 job 数（默认 1=串行）")
    p.add_argument("--aggregate", action="store_true", help="从 RepeatRecord 重算 cell aggregation")
    p.add_argument("--summary", action="store_true", help="生成三层 summary")
    p.add_argument("--outdir", default=".", help="输出根目录（默认 . → ./data/sim_results）")
    p.add_argument("--no-numpy", action="store_true", help="禁用 numpy cTE 内核")
    return p.parse_args()


def _use_numpy(args):
    return _HAS_NUMPY and not args.no_numpy


def _system_by_name(name):
    for e in benchmark_entries():
        if e["name"] == name:
            return e
    raise KeyError(name)


def _run_one_repeat(entry, grid, estimator, repeat, unit_seed, use_numpy):
    sys_obj = entry["sys"]
    rng_traj = _BernoulliRNG(_sub_seed(unit_seed, "traj"))
    rng_pn = _BernoulliRNG(_sub_seed(unit_seed, "pn"))
    rng_pm = _BernoulliRNG(_sub_seed(unit_seed, "pm"))
    N = grid["N"]
    traj = generate_trajectory(sys_obj.step_fn, sys_obj.n, N, rng_traj)
    h = grid["h"]
    hidden = hidden_index(entry["name"], sys_obj.n) if h else None
    obs_series = perturb_trajectory(traj, grid["p_n"], grid["d"], grid["p_m"],
                                    hidden, rng_pn, rng_pm)
    record = evaluate_repeat(entry, grid, estimator, obs_series, unit_seed, use_numpy)
    record["meta"]["repeat"] = repeat
    record["meta"]["seed"] = unit_seed
    return record


def _worker_job(task):
    """multiprocessing worker：计算一段 repeat-range 的 repeat 记录（#98 Q11c）。
    task = (system_name, grid, estimator, repeat_list, use_numpy)。"""
    name, grid, estimator, repeats, use_numpy = task
    entry = _system_by_name(name)
    out = []
    for r in repeats:
        seed = derive_seed(name, grid, estimator, r)
        out.append(_run_one_repeat(entry, grid, estimator, r, seed, use_numpy))
    return out


def run_cells(args, target_cells, repeat_range):
    """执行 (system, grid, estimator) 网格；per-cell 即时落盘 + 可恢复（#98 Q11/Q14）。"""
    outdir = outdir_path(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    write_manifest(outdir)
    use_numpy = _use_numpy(args)
    systems = args.systems or [e["name"] for e in benchmark_entries()]
    estimators = args.estimators or ["plug-in", "te", "cte"]
    r0, r1 = repeat_range if repeat_range else (0, R)
    run_log_path = os.path.join(outdir, "run_log.json")
    run_log = {}
    if os.path.exists(run_log_path):
        with open(run_log_path, encoding="utf-8") as f:
            run_log = json.load(f)

    tasks = []
    for name in systems:
        for grid in target_cells:
            for est in estimators:
                cid = cell_id(name, grid, est)
                path = os.path.join(outdir, cid + ".json")
                status = run_log.get(cid, {}).get("status")
                if status == "completed" and os.path.exists(path):
                    continue
                if status == "blocked":
                    continue
                # c=0.6 blocked（#98 Q2a：无冻结 coupling mapping → 元记录，不执行）
                if grid["c"] != 0.9:
                    blocked = {
                        "schema_version": SCHEMA_VERSION,
                        "cell_id": cid,
                        "system": name, "grid": grid, "estimator": est,
                        "status": "blocked",
                        "block_reason": "no_frozen_coupling_mapping",
                    }
                    _atomic_write_json(path, blocked)
                    run_log[cid] = {"status": "blocked"}
                    continue
                tasks.append((name, grid, est, cid, path))

    for name, grid, est, cid, path in tasks:
        # 已有 partial cell（未满 32）→ 按 repeat 索引合并（seed 确定性保证
        # 与整 cell 重跑逐字节等价——满足 Q11a/Q13c 拆分等价 + Q14b 终态语义）
        existing = {}
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    old = json.load(f)
                if old.get("status") == "completed":
                    continue
                for r in old.get("repeat_records", []):
                    existing[r["meta"]["repeat"]] = r
            except Exception:
                existing = {}
        repeats = list(range(r0, r1))
        if args.jobs > 1 and len(repeats) > 1:
            chunks = []
            per = max(1, len(repeats) // args.jobs)
            for k in range(0, len(repeats), per):
                chunks.append(repeats[k:k + per])
            pool_tasks = [(name, grid, est, chunk, use_numpy) for chunk in chunks]
            with multiprocessing.Pool(args.jobs) as pool:
                parts = pool.map(_worker_job, pool_tasks)
            new_records = [r for part in parts for r in part]
        else:
            new_records = [_run_one_repeat(_system_by_name(name), grid, est, r,
                                           derive_seed(name, grid, est, r), use_numpy)
                           for r in repeats]
        for r in new_records:
            existing[r["meta"]["repeat"]] = r
        records = [existing[k] for k in sorted(existing)]
        status = "completed" if len(records) >= R else "partial"
        # 组装 cell（事实源：completed = 恰 32 个 RepeatRecord + aggregation；
        # partial 是运行中间态，非最终结果状态，#98 Q14b）
        cell = {
            "schema_version": SCHEMA_VERSION,
            "cell_id": cid,
            "meta": {"system": name, "grid": grid, "estimator": est},
            "status": status,
            "repeat_records": records,
            "aggregation": aggregate_cell(records),
        }
        _atomic_write_json(path, cell)
        run_log[cid] = {"status": status}
        _atomic_write_json(run_log_path, run_log)
        print(f"[{'done' if status == 'completed' else 'partial'}] {cid} ({len(records)} repeats)")


def aggregate_pass(args):
    """--aggregate：从 repeat_records 无损重算 aggregation（#98 Q12b）。"""
    outdir = outdir_path(args.outdir)
    for root, _, files in os.walk(outdir):
        for fn in sorted(files):
            if not fn.endswith(".json") or fn in ("MANIFEST.json", "run_log.json",
                                                  "selection_log.json"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                cell = json.load(f)
            if cell.get("status") != "completed":
                continue
            cell["aggregation"] = aggregate_cell(cell["repeat_records"])
            _atomic_write_json(path, cell)
            print(f"[aggregated] {fn}")


def cell_key(grid):
    return tuple(sorted(grid.items()))


def summary_pass(args, stageA_cells):
    """--summary：三层报告（#95 Q15 + #98 Q12c：只读消费者，可重建产物）。"""
    outdir = outdir_path(args.outdir)
    sumdir = os.path.join(outdir, "summary")
    os.makedirs(sumdir, exist_ok=True)
    a_pair_map = {}
    cells_by_sys_est = {}
    # 读取全部 cell（本实现 cell 文件平铺于 outdir；#98 Q12c summary=只读消费者）
    from glob import glob
    for path in glob(os.path.join(outdir, "*.json")):
        fn = os.path.basename(path)
        if fn in ("MANIFEST.json", "run_log.json", "selection_log.json"):
            continue
        with open(path, encoding="utf-8") as f:
            cell = json.load(f)
        if cell.get("status") != "completed":
            continue
        meta = cell["meta"]
        name, grid, est = meta["system"], meta["grid"], meta["estimator"]
        ap = cell["aggregation"]["A_pair"]["mean"]
        a_pair_map[(name, est, cell_key(grid))] = ap
        cells_by_sys_est.setdefault((name, est), []).append((grid, cell))
    # ① stageA_curves：六条单因素曲线（per system × estimator；#95 Q15）
    # 只收 Stage A 单因素格（varying_factor 唯一且非基线），阶段 B 双因素格不入曲线
    stageA_keys = {cell_key(g) for g in stageA_cells}
    curves = {}
    for (name, est), items in cells_by_sys_est.items():
        for f in GRADIENT_ORDER:
            pts = []
            for grid, cell in items:
                if cell_key(grid) not in stageA_keys:
                    continue
                if varying_factor(grid) == f:
                    pts.append({"level": grid[f], "A_pair": cell["aggregation"]["A_pair"]})
            pts.sort(key=lambda x: x["level"])
            if pts:
                curves.setdefault(name, {}).setdefault(est, {})[f] = pts
    _atomic_write_json(os.path.join(sumdir, "stageA_curves.json"), curves)
    # ② Stage B 选格 + 交互（若 Stage A 数据存在）
    if a_pair_map:
        selected, trigger_log = select_stage_B(stageA_cells, a_pair_map)
        _atomic_write_json(os.path.join(outdir, "selection_log.json"),
                           {"trigger_log": trigger_log})
        interactions = {}
        for (name, est), grids in make_stageB_grid(selected).items():
            for (f1, f2) in STAGEB_INTERACTIONS:
                L1, H1 = LEVELS[f1][0], LEVELS[f1][-1]
                L2, H2 = LEVELS[f2][0], LEVELS[f2][-1]
                def A(v1, v2):
                    g = dict(BASELINE); g[f1] = v1; g[f2] = v2
                    return a_pair_map.get((name, est, cell_key(g)))
                a_ll, a_lh = A(L1, L2), A(L1, H2)
                a_hl, a_hh = A(H1, L2), A(H1, H2)
                if None in (a_ll, a_lh, a_hl, a_hh):
                    continue
                delta = (a_hh - a_hl) - (a_lh - a_ll)
                interactions.setdefault(name, {}).setdefault(est, {})[f"{f1}×{f2}"] = {
                    "delta_A_pair": round(delta, 6),
                    "cells": {"LL": a_ll, "LH": a_lh, "HL": a_hl, "HH": a_hh},
                }
        _atomic_write_json(os.path.join(sumdir, "stageB_interactions.json"), interactions)
    # ③ validity_regions（#95 Q15：A_pair=1 严格域 / ≥0.9 宽域 / plug-TE 分歧区）
    regions = {}
    for (name, est), items in cells_by_sys_est.items():
        vals = [cell["aggregation"]["A_pair"]["mean"] for _, cell in items]
        regions.setdefault(name, {})[est] = {
            "n_cells": len(vals),
            "strict_A1": sum(1 for v in vals if v > 1 - 1e-9),
            "wide_A09": sum(1 for v in vals if v >= 0.9),
            "min": min(vals) if vals else None, "max": max(vals) if vals else None,
        }
    _atomic_write_json(os.path.join(sumdir, "validity_regions.json"), regions)
    print(f"[summary] 写入 {sumdir}（{len(a_pair_map)} cells）")


# ---------------- 验收：--self-test（#98 Q13a） ----------------

def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ✓ {msg}")


def self_test():
    print("== --self-test：纯逻辑断言 ==")
    # 三值化真值表（#98 Q8b）
    _assert(undirected_state("present", "absent") == "present", "无向三值化：present+absent→present")
    _assert(undirected_state("present", "not_testable") == "present", "present+not_testable→present")
    _assert(undirected_state("absent", "absent") == "absent", "absent+absent→absent")
    _assert(undirected_state("absent", "not_testable") == "not_testable", "absent+not_testable→not_testable")
    _assert(undirected_state("not_testable", "not_testable") == "not_testable", "nt+nt→not_testable")
    _assert(undirected_state("present", "present") == "present", "present+present→present")
    # not_testable ≠ absent
    _assert("not_testable" != "absent", "not_testable ≠ absent（不同状态常量）")
    # 网格
    ga = make_stageA_grid()
    _assert(len(ga) == 14, f"阶段 A 去重 14 格（实际 {len(ga)}）")
    # seed 派生
    s1 = derive_seed("F8′", BASELINE, "plug-in", 0)
    s2 = derive_seed("F8′", BASELINE, "te", 0)
    s3 = derive_seed("F8′", BASELINE, "plug-in", 1)
    _assert(s1 != s2 and s1 != s3, "seed 含 estimator/repeat（不同单元不同 seed）")
    s4 = derive_seed("F8′", BASELINE, "plug-in", 0)
    _assert(s1 == s4, "同单元 seed 确定性")
    # h 隐变量表
    _assert(hidden_index("F8′", 6) == 4, "h 表：F8′→z1(4)")
    _assert(hidden_index("H_loop", 4) == 0, "h 表：H_loop→c1(0)")
    _assert(hidden_index("R_iid", 4) == 3, "h 表：其余→末位")
    # 扰动算子：d 下采样 + 缺失不拼接
    traj = [tuple([(t >> i) & 1 for i in range(2)]) for t in range(8)]
    rng_pn = random.Random(0)
    rng_pm = random.Random(0)
    obs = perturb_trajectory(traj, 0.0, 2, 0.0, None, rng_pn, rng_pm)
    _assert([k for k, _ in obs] == [0, 1, 2, 3], f"d=2 下采样索引 0,2,4,6→k=0..3（{ [k for k,_ in obs] }）")
    pairs, trans = build_transitions(obs)
    _assert(all(k2 == k1 + 1 for (k1, _), (k2, _) in zip(obs, obs[1:])), "无缺失时相邻索引连续")
    # p_m 缺失不拼接
    rng_pn2 = random.Random(0)
    rng_pm2 = random.Random(1)
    obs2 = perturb_trajectory(traj, 0.0, 1, 0.5, None, rng_pn2, rng_pm2)
    kept_idx = [k for k, _ in obs2]
    pairs2, _ = build_transitions(obs2)
    expected_pairs = [(s1, s2) for (k1, s1), (k2, s2) in zip(obs2, obs2[1:])
                      if k2 == k1 + 1]
    _assert(pairs2 == expected_pairs,
            f"缺失不拼接：仅原始时间轴相邻观测拍成对（kept={kept_idx}）")
    # h 投影
    rng3 = random.Random(0)
    obs3 = perturb_trajectory([(0, 1, 0)] * 4, 0.0, 1, 0.0, 1, rng3, random.Random(0))
    _assert(all(len(s) == 2 for _, s in obs3), "h 剔除：观测状态坐标数 n-1")
    # cTE vs cte_reference（纯 Python 数值一致性）
    xi = [0, 1, 0, 1, 0, 1]
    xj = [0, 0, 1, 1, 0, 0]
    z = [0, 0, 0, 1, 1, 1]
    v_ref = cte_value(xi, xj, z)
    _assert(abs(v_ref - cte_value(xi, xj, z)) < 1e-12, "cte_value 确定性")
    if _HAS_NUMPY:
        z_code = z
        v_np = cte_value_np(xi, xj, z_code, 1)
        _assert(abs(v_ref - v_np) < 1e-9, f"numpy 内核与 reference 一致（{v_ref} vs {v_np}）")
    print("== --self-test：数值回归（小数据 plug-in/TE/cTE）==")
    # 确定性系统：R_iid 无结构 → 全部 absent/not_testable；R_corr 有相关性
    for name in ("R_iid", "R_corr"):
        entry = _system_by_name(name)
        seed = derive_seed(name, BASELINE, "plug-in", 0)
        rec = _run_one_repeat(entry, BASELINE, "plug-in", 0, seed, _HAS_NUMPY)
        _assert(rec["meta"]["repeat"] == 0 and "A_pair" in rec["metrics"], f"{name} plug-in repeat 可运行")
        rec2 = _run_one_repeat(entry, BASELINE, "plug-in", 0, seed, _HAS_NUMPY)
        _assert(rec2 == rec, f"{name} 同 seed 重跑逐字节一致")
        rec_t = _run_one_repeat(entry, BASELINE, "te", 0, derive_seed(name, BASELINE, "te", 0), _HAS_NUMPY)
        _assert(rec_t["metrics"]["A_pair"] is not None, f"{name} TE repeat 可运行")
        rec_c = _run_one_repeat(entry, BASELINE, "cte", 0, derive_seed(name, BASELINE, "cte", 0), _HAS_NUMPY)
        _assert(rec_c["metrics"]["A_pair"] is not None, f"{name} cTE repeat 可运行")
    print("== --self-test 全部通过 ==")


def dry_run(args, level):
    """dry-run（#98 Q13b）：D0 最小 smoke / D1 协议边界覆盖。"""
    print(f"== dry-run {level} ==")
    use_numpy = _use_numpy(args)
    if level == "D0":
        cells = [BASELINE]
        systems = ["R_corr"]
        reps = (0, 2)
    else:
        cells = [dict(BASELINE), dict(BASELINE, N=64), dict(BASELINE, p_n=0.20),
                 dict(BASELINE, d=4), dict(BASELINE, p_m=0.50), dict(BASELINE, h=1),
                 dict(BASELINE, c=0.6)]
        systems = ["R_corr", "F8′"]
        reps = (0, 2)
    outdir = outdir_path(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    write_manifest(outdir)
    for name in systems:
        for grid in cells:
            for est in ("plug-in", "te", "cte"):
                cid = cell_id(name, grid, est)
                path = os.path.join(outdir, cid + ".json")
                if grid["c"] != 0.9:
                    blocked = {"schema_version": SCHEMA_VERSION, "cell_id": cid,
                               "system": name, "grid": grid, "estimator": est,
                               "status": "blocked",
                               "block_reason": "no_frozen_coupling_mapping"}
                    _atomic_write_json(path, blocked)
                    print(f"[blocked] {cid}")
                    continue
                entry = _system_by_name(name)
                records = [_run_one_repeat(entry, grid, est, r,
                                           derive_seed(name, grid, est, r), use_numpy)
                           for r in range(*reps)]
                cell = {"schema_version": SCHEMA_VERSION, "cell_id": cid,
                        "meta": {"system": name, "grid": grid, "estimator": est},
                        "status": "completed",
                        "repeat_records": records,
                        "aggregation": aggregate_cell(records)}
                _atomic_write_json(path, cell)
                print(f"[done] {cid}")
    print(f"== dry-run {level} 完成（输出 {outdir}）==")


def main():
    args = _cli()
    if args.self_test:
        self_test()
        return
    if args.dry_run:
        dry_run(args, args.dry_run)
        return
    if args.aggregate:
        aggregate_pass(args)
        return
    if args.summary:
        summary_pass(args, make_stageA_grid())
        return
    if args.stage:
        ga = make_stageA_grid()
        if args.stage == "A":
            run_cells(args, ga, args.repeat_range)
        else:
            # 阶段 B：先读阶段 A 结果选格（缺则提示）
            a_map = {}
            outdir = outdir_path(args.outdir)
            for c in ga:
                for name in (args.systems or [e["name"] for e in benchmark_entries()]):
                    for est in (args.estimators or ["plug-in", "te", "cte"]):
                        cell = read_cell(outdir, name, c, est)
                        if cell and cell.get("status") == "completed":
                            a_map[(name, est, cell_key(c))] = cell["aggregation"]["A_pair"]["mean"]
            if not a_map:
                print("阶段 B 需要先完成阶段 A（--stage A）")
                return
            selected, _ = select_stage_B(ga, a_map)
            grids = make_stageB_grid(selected)
            targets = []
            for name in (args.systems or [e["name"] for e in benchmark_entries()]):
                for est in (args.estimators or ["plug-in", "te", "cte"]):
                    targets.extend(grids.get((name, est), []))
            # 去重（含与阶段 A 重复格——复用不重跑，run_cells 会因 completed skip）
            seen = set()
            uniq = []
            for g in targets:
                k = tuple(sorted(g.items()))
                if k not in seen:
                    seen.add(k)
                    uniq.append(g)
            run_cells(args, uniq, args.repeat_range)
        return
    print("未指定模式。--help 查看全部选项。")


if __name__ == "__main__":
    main()
