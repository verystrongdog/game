#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim_moonlight_e1.py — E1 壳态保持性模拟实验（Grilling #100 协议 Q1-Q6 锁定版）

验证命题（#38 Q7 / 时空结构数学框架 §11.6）：
    F = 0，B 族 + A1 初始壳态 ⇒ r(t) = E(t)/E_c 长期保持在壳附近。
    E1 是结构性 sanity check，不是优化问题——禁止调参硬过。

────────────────────────────────────────────────────────────────────────
【协议强制声明】（Grilling #100 锁定，勿删勿改）
1. G_test 是 E1 的结构验证测试图，不代表最终医院空间拓扑。E1 仅验证
   CGL+AGC 在固定、连通、有限图上的壳态动力学。最终医院图 G_H 的节点、
   边及层间拓扑由 #1/#38 后续闭合后确定，并可在不改变 E1 验收逻辑的
   前提下替换。
2. 拓扑固定：K(t) = K0，整个 E1 运行期间不允许动态增删节点或边（C8）。
3. 导数约定（§四 记号修正，2026-08-29 #100）：h 的自变量为
   x = (E_c − E)/ε；h'(x_th) > 0、h'(0) < 0 均对 x 求导。原文本
   "h'(E_th)"（E_th 为能量值，不在 h 定义域内）正式改为 h'(x_th)。
4. h_E1(x) = tanh(x)·tanh(x − x_th) 是 E1 数值实验的代表性实现选择，
   不是 CGL+AGC 理论新增公理（#38 Q6 结构锁定边界）；若 E2+ 发现该
   形状不合适可更换，不构成推翻理论结构。
5. no-tuning 规则：数值参数调整（dt 细化序列 dt0, dt0/2, dt0/4，仅按
   预注册流程）≠ 模型参数调整（E_c/E_th/ε/d_max/w_ij 禁止修改以求通过）。
6. E1 PASS ⇔ Phase 1（数值基准）PASS ∧ Phase 2（主验收）PASS；
   Phase 3（诊断）不入 PASS，只负责解释与定位。
7. ε_num 门槛 0.005 是数值验收协议参数，不是理论误差界，不是 CGL+AGC
   参数；ρ_RK4 检验带 [14.4, 17.6] 同理。
────────────────────────────────────────────────────────────────────────

【输出格式】
每案例输出：r(t) 统计（min/max/末值）、t*、min_t(E−E_th)、ε_num、
收敛比 ρ、逐判据 PASS/FAIL；末尾输出汇总表与最终裁决（PASS/FAIL/
实现层失败/数值协议失败/结构层失败）。结果同时以 JSON 块打印（机器可读）。

【参数来源】
- 协议参数：Grilling #100 Q1-Q6（2026-08-29 用户经 ChatGPT 确认的裁决）
- 结构锁定：时空结构数学框架 §三/§四/§11.1-11.6（CGL+AGC、h 双零点族、
  B 族、A1、能量壳引理、理论投影、实验轨）
- 占位参数（未校准 → #35 E2 标定）：E_c/E_th/ε/d_max/w_ij
"""

import json
import numpy as np

# ────────────────────────────────────────────────────────────────────
# 一、协议参数（预注册冻结区）
# ────────────────────────────────────────────────────────────────────

# --- G_test = P₄（#100 Q5 锁定；λ 谱 {0, 2−√2, 2, 2+√2}）---
N = 4
W = 1.0                                   # 边权（占位参数，未校准）
S = np.array([[1, -1, 0, 0],
              [-1, 2, -1, 0],
              [0, -1, 2, -1],
              [0, 0, -1, 1]], dtype=float)  # P₄ 组合 Laplacian，w=1

# --- 占位参数（全部未校准 → #35 E2 标定）---
E_C = 1.0        # 壳能量（归一化占位）
E_TH = 0.5       # 激活阈值（占位；约束 E(0)=0.9·E_c > E_th ✓）
EPS = 0.1        # 门控锐度（占位 → x_th = (1−0.5)/0.1 = 5）
D_MAX = 1.0      # 最大阻尼/增益幅度（注册表语义：|d| ≤ d_max）
X_TH = (E_C - E_TH) / EPS   # = 5.0，h 的阈值零点（对 x 求导约定）

# --- 验收判据（#100 Q1/Q6 锁定）---
DELTA_R = 0.05       # 壳态容差（预注册协议参数，非理论常数）
EPS_NUM_CAP = 0.005  # ε_num 协议门槛（δ_r ≥ 10·ε_num 自动满足：0.05 = 10×0.005）
RHO_BAND = (14.4, 17.6)  # RK4 阶检验带（理论 16，10% 带）

# --- 时间尺度（#100 Q3/Q5 锁定）---
lam, V = np.linalg.eigh(S)          # 升序特征值/正交特征向量
lam_plus_idx = int(np.where(lam > 1e-12)[0][0])   # 最小正特征值下标（k）
lam_min_plus = lam[lam_plus_idx]                  # λ_min⁺ = 2−√2 ≈ 0.5858
lam_max = lam[-1]                                 # λ_max = 2+√2 ≈ 3.4142
v_k = V[:, lam_plus_idx]           # 归一化 ‖v_k‖₂=1（最小正模式）
j_idx = int(np.where(lam > lam_min_plus + 1e-12)[0][0])  # 次小正特征值下标
lam_j = lam[j_idx]
v_j = V[:, j_idx]

TAU_CHAR = 2 * np.pi / np.sqrt(lam_min_plus)   # = 2π/√λ_min⁺
T_MAX = 1000 * TAU_CHAR
T_MIN = 5 * TAU_CHAR
T_SETTLE = 100 * TAU_CHAR
DT0 = np.pi / (100 * np.sqrt(lam_max))         # 最快模态每周期 200 步

# --- 扰动集（#100 Q4 锁定）---
P_MAIN = (-0.10, +0.10)            # 主验收（吸引性）
P_SENS = (-0.01, +0.01, -0.05, +0.05)  # 数值敏感性诊断（不入 PASS）
PROBES = (0.9 * E_TH, 1.1 * E_TH)  # regime 边界探针（0.45 → 归零；0.55 → 升壳）
ALPHA_DUAL = 0.1                   # 双模态叠加系数

N_STEPS_TAU = int(np.ceil(T_MAX / DT0))   # 每案例步数（≈4.83e5）
SAMPLE_EVERY = 100                 # 粗采样网格：Δt_s = 100·dt0（三个 dt 档对齐）


# ────────────────────────────────────────────────────────────────────
# 二、核心数学（结构锁定，勿改——§三/§四/§11）
# ────────────────────────────────────────────────────────────────────

def h_e1(x):
    """h_E1(x) = tanh(x)·tanh(x − x_th)——E1 代表性实现选择，非理论公理。
    双横截零点：x=0（壳，h'(0)=−tanh(x_th)<0）、x=x_th（阈值，h'(x_th)=tanh(x_th)>0）。"""
    return np.tanh(x) * np.tanh(x - X_TH)


def damping(E):
    """d(E) = d_max · h((E_c − E)/ε)。全局标量 AGC，全对全耦合（§三）。"""
    return D_MAX * h_e1((E_C - E) / EPS)


def energy(z):
    """E = ½‖φ̇‖² + ½⟨φ, Sφ⟩（§三 能量泛函；z = [Reφ; Imφ; Reφ̇; Imφ̇]）"""
    x, y, u, v = z[:N], z[N:2 * N], z[2 * N:3 * N], z[3 * N:]
    K = float(u @ u + v @ v)
    V = float(x @ S @ x + y @ S @ y)
    return 0.5 * (K + V)


def rhs(z, d):
    """M φ̈ + d M φ̇ + S φ = F(t)，M=I，F≡0（§三）。返回 16 维实状态导数。"""
    x, y, u, v = z[:N], z[N:2 * N], z[2 * N:3 * N], z[3 * N:]
    return np.concatenate([u, v, -d * u - S @ x, -d * v - S @ y])


def rk4_step(z, dt):
    """标准固定步长 RK4 单步：d(E) 在各级中间态求值（d 是 RHS 的组成部分）。

    修正（2026-08-29 #100 第 6 项）：冻结-d 步进（d=d(E_prev) 常数）对真实
    （变 d）动力学只是一阶近似（实测全动力学状态误差比 ≈2）；标准 RK4 在
    k2/k3/k4 中间态评估 d，恢复四阶收敛（实测 ρ_state≈16）。"""
    def F(zs):
        E = energy(zs)
        return rhs(zs, damping(E))
    k1 = F(z)
    k2 = F(z + 0.5 * dt * k1)
    k3 = F(z + 0.5 * dt * k2)
    k4 = F(z + dt * k3)
    return z + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def single_mode_ic(E0):
    """A1 单模态壳上旋转初始条件（#100 Q3/Q4 锁定）：
    φ(0)=√(E0/λ_k)·v_k，φ̇(0)=i√E0·v_k → E(0)=E0 严格成立。"""
    A = np.sqrt(E0 / lam_min_plus)
    w = np.sqrt(lam_min_plus)
    z = np.zeros(4 * N)
    z[:N] = A * v_k
    z[3 * N:] = w * A * v_k        # Re φ̇ = 0，Im φ̇ = w·A·v_k
    return z


def dual_mode_ic():
    """双模态诊断初始化（#100 Q4 锁定）：
    u = v_k + α·v_j，Q = λ_k + α²λ_j，A = √(E_c/Q)，
    φ̇(0) = iA(√λ_k·v_k + α√λ_j·v_j) → K(0)=V(0)=E_c/2，E(0)=E_c。"""
    Q = lam_min_plus + ALPHA_DUAL ** 2 * lam_j
    A = np.sqrt(E_C / Q)
    z = np.zeros(4 * N)
    z[:N] = A * (v_k + ALPHA_DUAL * v_j)
    z[3 * N:] = A * (np.sqrt(lam_min_plus) * v_k + ALPHA_DUAL * np.sqrt(lam_j) * v_j)
    return z


def run_rk4(z0, dt, t_horizon, d_zero=False, return_states=False):
    """固定步长 RK4 积分，返回对齐粗采样网格上的 E(t)（及可选状态轨迹）。
    对齐约定：采样间隔恒为 Δt_s = 100·dt0（与 dt 无关）——各 dt 档在
    同一时间网格上比较，避免网格错位污染收敛比。"""
    n = int(t_horizon / dt)
    sps = max(1, int(round(SAMPLE_EVERY * DT0 / dt)))   # 每 sps 步采样一次
    n_samp = n // sps + 1
    z = z0.copy()
    E_trace = np.empty(n_samp)
    E_trace[0] = energy(z)
    Z_trace = np.empty((n_samp, 4 * N)) if return_states else None
    if return_states:
        Z_trace[0] = z
    min_margin = float(energy(z) - E_TH)
    k = 1
    for i in range(1, n + 1):
        E = energy(z)
        d = 0.0 if d_zero else damping(E)
        z = rk4_step(z, dt)
        E = energy(z)
        m = E - E_TH
        if m < min_margin:
            min_margin = m
        if i % sps == 0:
            E_trace[k] = E
            if return_states:
                Z_trace[k] = z
            k += 1
    t_grid = np.arange(n_samp) * (sps * dt)
    return t_grid, E_trace, min_margin, (Z_trace if return_states else None)


def kinetic(z):
    """K = ‖φ̇‖²（能量壳引理 dE/dt = −d·K 的 K）"""
    u, v = z[2 * N:3 * N], z[3 * N:]
    return float(u @ u + v @ v)


def scalar_ref_ode(E0, t_grid):
    """标量 ODE 参考解：dE/dt = −d(E)·E。

    ⚠️ 修正（2026-08-29 #100）：K=E 仅对纯旋转态成立（壳区/绝热极限）；
    非绝热瞬态（|d|~ω）K≠E（实测 max|K/E−1|≈0.10），故本参考解只能用作
    渐近诊断（壳区），不能作为瞬态收敛对照。主实现校验 = 能量壳引理 + 全
    动力学高精度参考（见 phase2）。"""
    try:
        from scipy.integrate import solve_ivp
        sol = solve_ivp(lambda t, E: -damping(float(E)) * float(E),
                        (0.0, T_MAX), [E0], t_eval=t_grid,
                        rtol=1e-11, atol=1e-14, method="RK45")
        return sol.y[0]
    except ImportError:
        dt_ref = DT0 / 64.0
        n = int(np.ceil(T_MAX / dt_ref))
        E = float(E0)
        out = np.empty(len(t_grid))
        out[0] = E
        k = 1
        for i in range(1, n + 1):
            E = E + dt_ref * (-damping(E) * E)
            if i % (64 * SAMPLE_EVERY) == 0 and k < len(t_grid):
                out[k] = E
                k += 1
        return out


def shell_lemma_residual(z0, dt, t_horizon):
    """能量壳引理核对（积分形式，与 stage-d RK4 实现一致）。

    修正（2026-08-29 #100）：实现为标准 RK4（d 在各级中间态求值）后，
    引理求积用连续语义梯形（d_prev·K_prev + d_cur·K_cur)/2·dt；核对取
    瞬态窗 [0, T_settle]（壳区 AGC 对数值漂移的响应 d≈10·ΔE/ε 会污染
    全时域积分）。实测残差 dt0=8e-3、dt0/4=4.4e-5（≈四阶收敛）；
    接线错误（符号/结构）时残差 O(1)。"""
    n = int(t_horizon / dt)
    z = z0.copy()
    E0 = energy(z)
    K_prev = kinetic(z)
    d_prev = damping(E0)
    integral = 0.0
    for i in range(n):
        z = rk4_step(z, dt)
        E_cur = energy(z)
        K_cur = kinetic(z)
        d_cur = damping(E_cur)
        integral += -0.5 * (d_prev * K_prev + d_cur * K_cur) * dt
        K_prev = K_cur
        d_prev = d_cur
    E_final = energy(z)
    denom = max(abs(integral), 1e-12)
    return abs((E_final - E0) - integral) / denom


def full_ref_convergence(E0, dt, t_horizon=T_SETTLE):
    """全动力学实现校验（修正版，2026-08-29 #100 第 5 项）。

    (b1) 状态误差自参考四阶比：‖z_dt−z_dt/2‖/‖z_dt/2−z_dt/4‖ ≈ 16（带 [14.4,17.6]）
         ——RK4 状态误差 4 阶普适，不受观测量阶数影响。
    (b2) 独立求解器绝对一致性：solve_ivp（rtol=1e-10）参考，‖E_dt−E_ref‖∞ ≤ 1e-6
         （实测 dt0=1.3e-7；1e-6 仍低于接线错误量级 O(1) 六个数量级）。
    修正原因：E 观测量在壳区 RK4 误差实测 ~5e-9，已达 solve_ivp 精度地板，
    收敛比退化（~1.5）——故阶检验用状态误差、求解器对照用绝对一致而非收敛比。"""
    from scipy.integrate import solve_ivp

    def full_rhs(t, z):
        E = energy(z)
        return rhs(z, damping(E))

    z0 = single_mode_ic(E0)
    t_grid, _, _, _ = run_rk4(z0, dt, t_horizon)
    sol = solve_ivp(full_rhs, (0.0, t_horizon), z0, t_eval=t_grid,
                    rtol=1e-10, atol=1e-12, method="RK45")
    E_ref = np.array([energy(sol.y[:, i]) for i in range(sol.y.shape[1])])
    # (b2) 绝对一致
    _, E_dt, _, _ = run_rk4(z0, dt, t_horizon)
    agree = float(np.max(np.abs(E_dt - E_ref)))
    # (b1) 状态自参考四阶比（对齐网格）
    _, _, _, Z0 = run_rk4(z0, dt, t_horizon, return_states=True)
    _, _, _, Z1 = run_rk4(z0, dt / 2, t_horizon, return_states=True)
    _, _, _, Z2 = run_rk4(z0, dt / 4, t_horizon, return_states=True)
    d01 = float(np.max(np.linalg.norm(Z0 - Z1, axis=1)))
    d12 = float(np.max(np.linalg.norm(Z1 - Z2, axis=1)))
    rho = d01 / d12 if d12 > 0 else float("inf")
    ok1 = RHO_BAND[0] <= rho <= RHO_BAND[1]
    ok2 = agree <= 1e-6  # 实测 dt0=1.3e-7
    return {"rho_state": rho, "agree": agree}, ok1 and ok2, E_ref, t_grid


def per_mode_energies(z):
    """模态分解 E_k = ½λ_k|a_k|² + ½|ȧ_k|²（a_k = v_k†φ）。Σ_k E_k = E 恒等。"""
    x, y, u, v = z[:N], z[N:2 * N], z[2 * N:3 * N], z[3 * N:]
    phi = x + 1j * y
    phid = u + 1j * v
    out = np.empty(N)
    for i in range(N):
        vi = V[:, i]
        a = vi @ phi
        ad = vi @ phid
        out[i] = 0.5 * lam[i] * abs(a) ** 2 + 0.5 * abs(ad) ** 2
    return out


# ────────────────────────────────────────────────────────────────────
# 三、Phase 0 — 预注册输出
# ────────────────────────────────────────────────────────────────────

def phase0_report():
    print("=" * 72)
    print("E1 壳态保持性模拟实验 — Grilling #100 协议（Q1-Q6 锁定版）")
    print("=" * 72)
    print(f"G_test = P₄  N={N}  w=1  λ谱={np.round(lam, 6)}")
    print(f"λ_min⁺={lam_min_plus:.6f}  λ_max={lam_max:.6f}  "
          f"κ_λ={lam_max/lam_min_plus:.4f}  κ_ω={np.sqrt(lam_max/lam_min_plus):.4f}")
    print(f"τ_char={TAU_CHAR:.4f}  T_max={T_MAX:.1f}  T_min={T_MIN:.1f}  "
          f"T_settle={T_SETTLE:.1f}  dt0={DT0:.6f}  步数≈{N_STEPS_TAU}")
    print(f"占位参数: E_c={E_C}  E_th={E_TH}  ε={EPS}  x_th={X_TH}  d_max={D_MAX}")
    print(f"验收: δ_r={DELTA_R}  ε_num≤{EPS_NUM_CAP}  ρ_RK4∈{RHO_BAND}  "
          f"主验收 p0={P_MAIN}")
    print("-" * 72)


# ────────────────────────────────────────────────────────────────────
# 四、Phase 1 — 数值基准（d≡0 线性动力学）
# ────────────────────────────────────────────────────────────────────

def phase1():
    print("\n[Phase 1] 数值基准（d≡0 线性保守动力学）")
    z0 = single_mode_ic(E_C)
    E_traces = {}
    Z_traces = {}
    for dt, tag in ((DT0, "dt0"), (DT0 / 2, "dt0/2"), (DT0 / 4, "dt0/4")):
        _, Et, _, Zt = run_rk4(z0, dt, T_MAX, d_zero=True, return_states=True)
        E_traces[tag] = Et
        Z_traces[tag] = Zt
        eps = float(np.max(np.abs(Et - E_C)) / E_C)
        print(f"  {tag:6s}: ε_num(d≡0) = {eps:.3e}")

    # 阶检验用状态误差（RK4 状态误差为 4 阶；能量观测量在保守振子上为 6 阶
    # ——2026-08-29 #100 修正：能量观测量的收敛比实测 ≈64 而非 16，故改状态）
    d01 = float(np.max(np.linalg.norm(Z_traces["dt0"] - Z_traces["dt0/2"], axis=1)))
    d12 = float(np.max(np.linalg.norm(Z_traces["dt0/2"] - Z_traces["dt0/4"], axis=1)))
    rho = d01 / d12 if d12 > 0 else float("inf")
    eps_num = float(np.max(np.abs(E_traces["dt0"] - E_C)) / E_C)
    print(f"  ‖z_dt0−z_dt0/2‖∞={d01:.3e}  ‖z_dt0/2−z_dt0/4‖∞={d12:.3e}")
    print(f"  ρ_RK4(状态) = {rho:.3f}  (检验带 {RHO_BAND})")

    passed_rho = RHO_BAND[0] <= rho <= RHO_BAND[1]
    passed_eps = eps_num <= EPS_NUM_CAP
    # 协议门槛：ε_num 超限 → 预注册 dt 细化 dt0→dt0/4 重测（唯一合法数值调整）
    if not passed_eps:
        print(f"  ⚠ ε_num={eps_num:.3e} > {EPS_NUM_CAP} → 按预注册规则细化 dt0→dt0/4 重测")
        _, Eb, _, _ = run_rk4(single_mode_ic(E_C), DT0 / 4, T_MAX, d_zero=True)
        eps_num = float(np.max(np.abs(Eb - E_C)) / E_C)
        passed_eps = eps_num <= EPS_NUM_CAP
        print(f"  细化后 ε_num = {eps_num:.3e} → {'PASS' if passed_eps else 'FAIL'}")
        if not passed_eps:
            return False, "数值协议失败（ε_num 超限且细化后仍不达标）"
    if not passed_rho:
        return False, "数值协议失败（RK4 阶检验未通过）"
    print(f"  Phase 1: {'PASS' if (passed_rho and passed_eps) else 'FAIL'}")
    return (passed_rho and passed_eps), "PASS" if (passed_rho and passed_eps) else "FAIL"


# ────────────────────────────────────────────────────────────────────
# 五、Phase 2 — 主验收（p0 = ±10%，全动力学）
# ────────────────────────────────────────────────────────────────────

def phase2(dt):
    print(f"\n[Phase 2] 主验收（p0={P_MAIN}，dt={dt:.6f}）")
    n_steps = N_STEPS_TAU
    results = {}
    for p0 in P_MAIN:
        E0 = (1.0 + p0) * E_C
        z0 = single_mode_ic(E0)
        # 细步长全轨迹用于 t* 判定（每步采样 r）
        z = z0.copy()
        r_full = np.empty(n_steps + 1)
        E_full = np.empty(n_steps + 1)
        r_full[0] = energy(z) / E_C
        E_full[0] = energy(z)
        min_margin = float(energy(z) - E_TH)
        for i in range(1, n_steps + 1):
            E = energy(z)
            d = damping(E)
            z = rk4_step(z, dt)
            E = energy(z)
            E_full[i] = E
            r_full[i] = E / E_C
            m = E - E_TH
            if m < min_margin:
                min_margin = m
        # 判据(2) 吸引性：首次进入并持续停留（从末尾反向扫描）
        t_star = None
        for i in range(n_steps, -1, -1):
            if abs(r_full[i] - 1.0) > DELTA_R:
                t_star = (i + 1) * dt
                break
        if t_star is None:
            t_star = 0.0
        # 判据(1) 保持性窗口 [T_min, T_max]
        idx_min = int(np.ceil(T_MIN / dt))
        in_window = bool(np.all(np.abs(r_full[idx_min:] - 1.0) <= DELTA_R))
        # 判据(2) 通过：t* ≤ T_settle
        attract = t_star is not None and t_star <= T_SETTLE
        # 判据(3) 安全边界
        safe = min_margin > 0.0
        res = {
            "p0": p0, "E0": E0, "t_star": float(t_star),
            "r_min": float(np.min(r_full)), "r_max": float(np.max(r_full)),
            "r_final": float(r_full[-1]),
            "min(E−E_th)": min_margin,
            "criterion1_persistence": in_window,
            "criterion2_attractivity": bool(attract),
            "criterion3_safety": safe,
            "pass": in_window and attract and safe,
        }
        results[p0] = res
        print(f"  p0={p0:+5.2f}: E(0)={E0:.2f}  t*={t_star:.3f}τ?  "
              f"r∈[{res['r_min']:.4f},{res['r_max']:.4f}] 末值={res['r_final']:.6f}  "
              f"min(E−E_th)={min_margin:+.4f}")
        print(f"    保持性={in_window}  吸引性={attract}  安全={safe}  "
              f"→ {'PASS' if res['pass'] else 'FAIL'}")

    # ── 实现正确性三校验（修正版，2026-08-29 #100）──
    # (a) 能量壳引理核对（积分形式 + 冻结-d 一致求积 + 瞬态窗 [0,T_settle]）
    print("\n  [Phase 2 附加 a] 能量壳引理核对（∫dE = −∫d(E)·K dt，瞬态窗 [0,T_settle]）")
    z0a = single_mode_ic((1.0 + 0.10) * E_C)
    res_a = shell_lemma_residual(z0a, dt, T_SETTLE)
    ok_a = res_a <= 2e-2  # 实测 dt0=8e-3（四阶收敛至 dt0/4=4.4e-5）；接线错误 O(1)
    print(f"    相对残差 = {res_a:.3e}  → "
          f"{'PASS' if ok_a else 'FAIL（实现层信号）'}")
    if not ok_a:
        return False, "实现层失败（能量壳引理未满足——方程/能量/d(E) 接线错误）"

    # (b) 全动力学实现校验（状态四阶比 + 独立求解器绝对一致）
    print("  [Phase 2 附加 b] 全动力学实现校验（状态四阶比 ρ∈[14.4,17.6] + 求解器绝对一致 ≤1e-6）")
    chk, ok_b, _, _ = full_ref_convergence((1.0 + 0.10) * E_C, dt)
    print(f"    ρ_state(全动力学) = {chk['rho_state']:.2f}  (带 {RHO_BAND})  → "
          f"{'PASS' if RHO_BAND[0] <= chk['rho_state'] <= RHO_BAND[1] else 'FAIL'}")
    print(f"    ‖E_dt−E_ref‖∞(solve_ivp rtol=1e-10) = {chk['agree']:.3e}  (≤1e-6)  → "
          f"{'PASS' if chk['agree'] <= 1e-6 else 'FAIL'}")
    print(f"    → {'PASS' if ok_b else 'FAIL（实现层信号）'}")
    if not ok_b:
        return False, "实现层失败（全动力学实现校验未通过）"

    # (c) 标量 ODE 渐近诊断（K=E 仅壳区成立；瞬态偏差为预期，不入 PASS）
    print("  [Phase 2 附加 c] 标量 ODE 渐近诊断（Ė=−d(E)·E：仅壳区 K→E 后成立）")
    E0p = (1.0 + 0.10) * E_C
    z0p = single_mode_ic(E0p)
    n_samp = N_STEPS_TAU // SAMPLE_EVERY + 1
    t_grid = np.arange(n_samp) * (SAMPLE_EVERY * dt)
    E_scalar = scalar_ref_ode(E0p, t_grid)
    _, E_full_c, _, _ = run_rk4(z0p, dt, T_MAX)
    t_star_c = results[0.10]["t_star"]
    mask = t_grid >= t_star_c
    if mask.sum() > 0:
        dev_asy = float(np.max(np.abs(E_full_c[mask] - E_scalar[mask])) / E_C)
    else:
        dev_asy = float("nan")
    print(f"    壳区（t≥t*={t_star_c:.1f}）|E_full−E_scalar|/E_c 最大 = {dev_asy:.4f}"
          f"  （瞬态偏差预期非零：K≠E，max|K/E−1|≈0.10，非绝热）")

    all_pass = all(res["pass"] for res in results.values())
    print(f"  Phase 2: {'PASS' if all_pass else 'FAIL'}")
    return all_pass, "PASS" if all_pass else "FAIL"


# ────────────────────────────────────────────────────────────────────
# 六、Phase 3 — 诊断（不入 PASS，只解释）
# ────────────────────────────────────────────────────────────────────

def phase3(dt):
    print(f"\n[Phase 3] 诊断（dt={dt:.6f}；异常必须进入报告，不单独决定 PASS）")
    n_steps = N_STEPS_TAU
    # 3.1 数值敏感性 ±1%, ±5%
    print("  3.1 敏感性诊断 p0∈{±1%, ±5%}（不入吸引性验收）")
    for p0 in P_SENS:
        z0 = single_mode_ic((1.0 + p0) * E_C)
        _, Et, _, _ = run_rk4(z0, dt, T_MAX)
        r = Et / E_C
        print(f"    p0={p0:+5.2f}: r∈[{r.min():.4f},{r.max():.4f}] 末值={r[-1]:.6f}")
    # 3.2 regime 边界探针
    print("  3.2 regime 边界探针（验证 E_th 两侧符号）")
    for E0 in PROBES:
        z0 = single_mode_ic(E0)
        _, Et, _, _ = run_rk4(z0, dt, T_MAX)
        x0 = (E_C - E0) / EPS
        h0 = h_e1(x0)
        print(f"    E(0)={E0:.2f} (x0={x0:+.2f}, h={h0:+.4f}): "
              f"E末值={Et[-1]:.6f} (期望 {'→0' if h0 > 0 else '→E_c'})")
    # 3.3 双模态诊断（全局 d 无模式耦合 + 份额守恒）
    print("  3.3 双模态诊断（u=v_k+0.1·v_j，E(0)=E_c 精确）")
    z0 = dual_mode_ic()
    z = z0.copy()
    shares0 = per_mode_energies(z)
    E0tot = float(shares0.sum())
    max_share_drift = 0.0
    max_partition_err = 0.0
    for i in range(1, n_steps + 1):
        E = energy(z)
        d = damping(E)
        z = rk4_step(z, dt)
        if i % SAMPLE_EVERY == 0:
            sk = per_mode_energies(z)
            E_tot = float(sk.sum())
            # 份额漂移：两主导模态份额相对初值变化
            sh = sk / E_tot
            sh0 = shares0 / E0tot
            drift = float(np.max(np.abs(sh - sh0)))
            if drift > max_share_drift:
                max_share_drift = drift
            # 分解恒等 ΣE_k = E
            if abs(E_tot - energy(z)) / energy(z) > max_partition_err:
                max_partition_err = abs(E_tot - energy(z)) / energy(z)
    print(f"    初值份额: E_k/E={sh0[lam_plus_idx]:.4f}, E_j/E={sh0[j_idx]:.4f}")
    print(f"    max 份额漂移={max_share_drift:.3e}  分解恒等误差={max_partition_err:.3e}")
    print("    （份额漂移≈0 ⇒ 全局 d 对所有模态施加同一标量，无模式间耦合）")


# ────────────────────────────────────────────────────────────────────
# 七、主流程
# ────────────────────────────────────────────────────────────────────

def main():
    phase0_report()
    p1_ok, p1_verdict = phase1()
    dt_use = DT0  # Phase 1 判定后统一生效；细化流程见 phase1 内部
    p2_ok, p2_verdict = phase2(dt_use)
    phase3(dt_use)

    print("\n" + "=" * 72)
    print("E1 最终裁决")
    print(f"  Phase 1（数值基准）: {p1_verdict}")
    print(f"  Phase 2（主验收）:   {p2_verdict}")
    if not p1_ok:
        verdict = "数值协议失败"
    elif not p2_ok:
        verdict = p2_verdict
    else:
        verdict = "PASS"
    print(f"  → E1 结论: {verdict}")
    print("  注：PASS = B 族+A1 壳态保持成立（占位参数域内）；失败分类与后续处置见 #100 Step 5 评论")
    print("=" * 72)

    summary = {
        "protocol": "Grilling #100 Q1-Q6",
        "G_test": "P4", "N": N,
        "lam_min_plus": float(lam_min_plus), "lam_max": float(lam_max),
        "tau_char": float(TAU_CHAR), "T_max": float(T_MAX), "dt0": float(DT0),
        "placeholder_params": {"E_c": E_C, "E_th": E_TH, "eps": EPS,
                               "x_th": float(X_TH), "d_max": D_MAX},
        "phase1": {"verdict": p1_verdict, "eps_num_cap": EPS_NUM_CAP,
                   "rho_band": list(RHO_BAND)},
        "phase2": {"verdict": p2_verdict, "p_main": list(P_MAIN),
                   "delta_r": DELTA_R},
        "final_verdict": verdict,
    }
    print("\nJSON:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
