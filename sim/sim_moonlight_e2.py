#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim_moonlight_e2.py — E2 月相调制标定模拟实验（Grilling #102 协议 Q1-Q9 锁定版）

验证命题（#38 Q7 / 时空结构数学框架 §11.6 + §11.6 E2 协议块）：
    移动壳问题——λ(t) 驱动下 E_c(λ)/E_th(λ) 移动，场须绝热跟随。
    公式链：λ(t) → E_c(λ(t)), E_th(λ(t)) → E(t), q_i(t), q̂_i(t)。
    E1 验证固定月相下的壳动力学；E2 中 E_c 本身在动（分享页「裁决随机性供给」）。

────────────────────────────────────────────────────────────────────────
【协议强制声明】（Grilling #102 锁定，勿删勿改）
1. G_test 沿用 P₄（与 E1 同图——P2a 深绝热回退对照干净；最终医院图 G_H
   由 #1 闭合后替换；K(t)=K₀ 固定，C8）。
2. λ(t) 波形（Q1）：λ(t) = (1−cos(Ωt+π/2))/2，λ∈[0,1]，Ω=2π/T_moon，
   T_moon=29.5d（拍频周期）；λ(0)=0.5（弦月，Q6）；确定性（C7）。
3. 慢调制协议（Q2）：ε_adiab ≡ τ_char/T_mod，T_mod=T_moon/2π；
   扫描 T_moon/τ_char ∈ {10, 10², 10³, 10⁴}（ε_adiab ∈ {0.63, 6.3e-2, 6.3e-3, 6.3e-4}）。
   游戏日↔模拟单位映射推迟接口层（本脚本只产约束 ε_adiab*）。
4. 跟踪判据（Q3）：四硬门禁 P1 不脱壳（min_t[E−E_th(λ)]>0）/ P2a 深绝热回退
   （最深档 max|r−1|≤δ_r=0.05 继承 E1）/ P3 吸引性（p₀=±10% 于 λ(0)=0.5）/
   P4 数值分离（ε_num≤0.1×max|r−1|_moving 最深档）+ 两诊断 P2b 收敛标度 /
   滞后 Δφ。时间窗：T_settle=1·T_moon，分析窗 = 第 2~3 月相周期 [2·T_moon, 4·T_moon]。
5. 职责分离（Q4）：本脚本只标定 f_c(λ;θ_c)/f_th(λ;θ_th)；q^base(λ) 占位 =
   E_c(λ)/N（均匀壳态每节点能量，Σq̂=r 语义自洽）只验证响应链连通性，形状留 E6。
6. 形状族（Q5）：线性端点族 E_c(λ)=E_c,min+ΔE_c·λ（ΔE_c>0）、
   E_th(λ)=E_th,min+ΔE_th·λ（ΔE_th∈{−0.25,0,+0.25} 三方向——「满月易激活」
   假设兼容方向由扫描检验）；相对 gap 约束 gap(λ)≥0.1·E_c(λ) ∀λ；
   ρ_c=E_c,max/E_c,min∈{4/3, 1.5, 2.0}（4/3=旧参考 0.675→0.900 幅度比对照点）；
   基线 E_c,min=1.0 / E_th,min=0.5（继承 E1 占位）。
7. 数值协议（Q6）：标准 RK4 固定步长 + stage 求值扩展至 λ——d 与 λ 均在
   k2/k3/k4 中间态求值（冻结-λ 降阶同理 E1 修正 6）；dt₀=π/(100√λ_max)；
   每案例双跑（moving 主跑 + λ 冻结控制组 λ≡λ(0)，即 E1 式静态壳），
   绝热偏差 = moving − frozen；占位参数 ε=0.1/d_max=1/w=1 沿用（E2 不标定）。
   热循环提供 numba JIT 路径（G_test=P₄ 时启用；同一 RK4 离散，性能工具非
   方案变更）与纯 Python 回退路径，均与 E1 numpy 路径为同一标准 RK4 离散，
   启动时做一致性校验（|Δz| 阈值 1e-10）。
8. 验收合成（Q7）：E2 PASS ⇔ ① 深绝热区 {10³,10⁴}：P1∧P2a∧P3∧P4 全过
   ∧ ② 过渡区 {10²}：P1 过 ∧ ③ P4 最深档成立 ∧ ④ 破坏点定位入诊断
   （不判 FAIL——快档脱壳是合法发现）。输出成立区间下界 ε_adiab*
   （= P1 首次失败档的前一档）——接口层「1 游戏日」映射硬约束。
9. no-tuning：数值参数调整（dt 细化序列，仅预注册流程）≠ 模型参数调整
   （E_c,min/E_c,max/E_th,min/ΔE_th/ε/d_max/w 禁止修改以求通过）。
10. 失败三层分类（E2 版）：实现层（数值 bug）/ 协议层（判据/网格/形状族
    假设，换族重扫）/ 结构层（B 族+A1 移动壳不成立 → 回 §11.2 检查，不写「证伪」）。
────────────────────────────────────────────────────────────────────────

【输出格式】
每案例：ε_adiab、r(t) 统计（min/max/末值）、P1 gap、P2a（最深档）、
P3 t*、冻结控制 max|r−1|、绝热偏差、Δφ、逐判据 PASS/FAIL；末尾汇总表 +
最终裁决（PASS/FAIL/实现层/协议层/结构层）+ ε_adiab*。结果同时以 JSON 块
打印（机器可读）。

【参数来源】
- 协议参数：Grilling #102 Q1-Q9（2026-08-30 用户经确认的裁决）
- 结构锁定：时空结构数学框架 §三/§四/§11.1-11.6 + E2 协议块
- 复用：sim_moonlight_e1.py（G_test P₄ / energy / rhs / single_mode_ic /
  标准 RK4 stage-d 语义）
"""

import json
import math
import sys
import time

import numpy as np

from sim_moonlight_e1 import (
    N, S, TAU_CHAR, DT0, rk4_step, single_mode_ic,
)

# ────────────────────────────────────────────────────────────────────
# 一、协议参数（预注册冻结区）
# ────────────────────────────────────────────────────────────────────

# --- 占位参数（Q6：沿用 E1，E2 不标定——职责分离）---
EPS = 0.1        # 门控锐度
D_MAX = 1.0      # 最大阻尼/增益幅度

# --- 形状族网格（Q5）---
EC_MIN = 1.0                # 基线端点（继承 E1 占位 E_c=1）
ETH_MIN = 0.5               # 基线端点（继承 E1 占位 E_th=0.5）
RHO_C_VALUES = (4.0 / 3.0, 1.5, 2.0)     # 壳调制深度比（4/3 = 旧参考幅度比对照点）
DETH_VALUES = (-0.25, 0.0, +0.25)        # ΔE_th 三方向（满月易激活假设检验）
GAP_REL = 0.1               # 相对 gap 约束：gap(λ) ≥ 0.1·E_c(λ)（P3 ±10% 扰动可行性）

# --- 慢调制扫描（Q2）---
TAU_RATIOS = (10, 10 ** 2, 10 ** 3, 10 ** 4)   # T_moon/τ_char
LEVEL_DEEP = 2              # 深绝热区起始下标（10³, 10⁴；门禁 P1∧P3∧P4，P2a 仅最深档）
LEVEL_P1_MIN = 1            # 过渡区下标（10²；门禁 P1）；快档 {10} 为诊断（不入 PASS）

# --- 跟踪判据（Q3）---
DELTA_R = 0.05              # P2a 深绝热回退界（继承 E1 δ_r）
P0 = 0.10                   # P3 吸引性扰动 ±10%
N_CYCLES_SETTLE = 1         # 瞬态窗 = 1·T_moon
N_CYCLES_ANALYZE = (2, 4)   # 分析窗 = 第 2~3 周期 [2·T_moon, 4·T_moon]
EPS_NUM_CAP = 0.005         # ε_num 协议门槛（E1 Phase 1 原样）
P4_FACTOR = 0.1             # P4：ε_num ≤ 0.1×max|r−1|_moving（最深档）
P3_MARGIN = 1.2             # P3 包络裕度：|r−1| ≤ 1.2×env_max 视为回到包络

# --- 数值协议（Q6）---
SAMPLE_EVERY = 100          # 粗采样：Δt_s = 100·dt0（与 E1 对齐）
HORIZON_BENCH = 1000        # d≡0 基准时域（×τ_char，E1 Phase 1 同款）
CONSISTENCY_STEPS = 500     # 纯 Python vs numpy 路径一致性校验步数
T_MOON_DUMMY = TAU_CHAR     # 一致性校验占位（dEc=dEth=0 时 T_moon 不参与计算）

# ────────────────────────────────────────────────────────────────────
# 二、核心数学（结构锁定，勿改——§三/§四/§11）
# ────────────────────────────────────────────────────────────────────

S_ROWS = [tuple(float(x) for x in row) for row in S]   # 纯 Python 热循环用


def lam_of_t(t, T_moon):
    """λ(t) = (1−cos(Ωt+π/2))/2 = (1+sin(Ωt))/2，λ(0)=0.5（弦月，Q1/Q6）。"""
    return 0.5 * (1.0 + math.sin(2.0 * math.pi * t / T_moon))


def Ec_of_lam(lam, case):
    """E_c(λ) = E_c,min + ΔE_c·λ，ΔE_c = (ρ_c−1)·E_c,min > 0（Q5）。"""
    return case["Ec_min"] + case["dEc"] * lam


def Eth_of_lam(lam, case):
    """E_th(λ) = E_th,min + ΔE_th·λ（ΔE_th 三方向，Q5）。"""
    return case["Eth_min"] + case["dEth"] * lam


def gap_of_lam(lam, case):
    """gap(λ) = E_c(λ) − E_th(λ)（P1 的静态前提；协议要求 ≥ 0.1·E_c(λ)）。"""
    return Ec_of_lam(lam, case) - Eth_of_lam(lam, case)


# --- 纯 Python 热循环（性能；与 numpy 路径同一标准 RK4 离散）---

def energy_py(z):
    """E = ½‖φ̇‖² + ½⟨φ, Sφ⟩（z = 16 元列表 [x;y;u;v]）。"""
    K = 0.0
    for i in range(N):
        u = z[2 * N + i]
        v = z[3 * N + i]
        K += u * u + v * v
    V = 0.0
    for i in range(N):
        xi = z[i]
        yi = z[N + i]
        row = S_ROWS[i]
        sx = 0.0
        sy = 0.0
        for j in range(N):
            w = row[j]
            sx += w * z[j]
            sy += w * z[N + j]
        V += xi * sx + yi * sy
    return 0.5 * (K + V)


def rhs_py(z, d):
    """M φ̈ + d M φ̇ + S φ = F(t)，M=I，F≡0。"""
    out = [0.0] * (4 * N)
    for i in range(N):
        out[i] = z[2 * N + i]                  # ẋ = u
        out[N + i] = z[3 * N + i]              # ẏ = v
        row = S_ROWS[i]
        sx = 0.0
        sy = 0.0
        for j in range(N):
            w = row[j]
            sx += w * z[j]
            sy += w * z[N + j]
        out[2 * N + i] = -d * z[2 * N + i] - sx
        out[3 * N + i] = -d * z[3 * N + i] - sy
    return out


def damping_py(E, lam, case):
    """d(E, λ) = d_max·h((E_c(λ)−E)/ε, xth(λ))——全局标量 AGC，λ 时变。"""
    Ec = case["Ec_min"] + case["dEc"] * lam
    Eth = case["Eth_min"] + case["dEth"] * lam
    x = (Ec - E) / EPS
    xth = (Ec - Eth) / EPS
    return D_MAX * math.tanh(x) * math.tanh(x - xth)


def _F_py(zs, tt, T_moon, case, lam_frozen):
    if lam_frozen is not None:
        lam_v = lam_frozen
    else:
        lam_v = 0.5 * (1.0 + math.sin(2.0 * math.pi * tt / T_moon))
    return rhs_py(zs, damping_py(energy_py(zs), lam_v, case))


def rk4_step_py(z, dt, t, T_moon, case, lam_frozen):
    """标准固定步长 RK4：d 与 λ 均在 k2/k3/k4 中间态求值（Q6）。

    修正（E1 修正 6 同款教训）：冻结-λ 步进对真实（变 λ）动力学降阶——
    λ 是解析函数，中间态直接代值 t+dt/2 精确。"""
    k1 = _F_py(z, t, T_moon, case, lam_frozen)
    z2 = [zi + 0.5 * dt * k for zi, k in zip(z, k1)]
    k2 = _F_py(z2, t + 0.5 * dt, T_moon, case, lam_frozen)
    z3 = [zi + 0.5 * dt * k for zi, k in zip(z, k2)]
    k3 = _F_py(z3, t + 0.5 * dt, T_moon, case, lam_frozen)
    z4 = [zi + dt * k for zi, k in zip(z, k3)]
    k4 = _F_py(z4, t + dt, T_moon, case, lam_frozen)
    return [zi + (dt / 6.0) * (k1i + 2.0 * k2i + 2.0 * k3i + k4i)
            for zi, k1i, k2i, k3i, k4i in zip(z, k1, k2, k3, k4)]


# --- numba JIT 热路径（性能；与 numpy/纯 Python 路径同一标准 RK4 离散）---
# G_test 锁定 P₄（协议声明 1）时启用；S 形状变化（未来 G_H 替换）自动回退
# 到纯 Python 路径（一致性校验保证两路径数学等价）。

try:
    from numba import njit
    HAVE_NUMBA = True
except ImportError:
    HAVE_NUMBA = False

_P4_MAT = np.array([[1.0, -1.0, 0.0, 0.0],
                    [-1.0, 2.0, -1.0, 0.0],
                    [0.0, -1.0, 2.0, -1.0],
                    [0.0, 0.0, -1.0, 1.0]])
USE_NUMBA = bool(HAVE_NUMBA and N == 4 and np.allclose(S, _P4_MAT))

if USE_NUMBA:
    @njit(cache=True)
    def _energy_nb(z):
        """E = ½‖φ̇‖² + ½⟨φ, Sφ⟩（P₄ 展开，z = 16 元 float64 数组）。"""
        u0 = z[8]; u1 = z[9]; u2 = z[10]; u3 = z[11]
        v0 = z[12]; v1 = z[13]; v2 = z[14]; v3 = z[15]
        K = u0 * u0 + u1 * u1 + u2 * u2 + u3 * u3 + \
            v0 * v0 + v1 * v1 + v2 * v2 + v3 * v3
        x0 = z[0]; x1 = z[1]; x2 = z[2]; x3 = z[3]
        y0 = z[4]; y1 = z[5]; y2 = z[6]; y3 = z[7]
        sx0 = x0 - x1
        sx1 = -x0 + 2.0 * x1 - x2
        sx2 = -x1 + 2.0 * x2 - x3
        sx3 = -x2 + x3
        sy0 = y0 - y1
        sy1 = -y0 + 2.0 * y1 - y2
        sy2 = -y1 + 2.0 * y2 - y3
        sy3 = -y2 + y3
        V = x0 * sx0 + x1 * sx1 + x2 * sx2 + x3 * sx3 + \
            y0 * sy0 + y1 * sy1 + y2 * sy2 + y3 * sy3
        return 0.5 * (K + V)

    @njit(cache=True)
    def _stage_nb(z, tt, T_moon, Ec_min, dEc, Eth_min, dEth,
                  eps, d_max, moving, lam_frozen):
        """F(z, t)：d 与 λ 在中间态求值（Q6）。moving=1 → λ(t)；0 → λ≡lam_frozen。"""
        if moving:
            lam_v = 0.5 * (1.0 + math.sin(2.0 * math.pi * tt / T_moon))
        else:
            lam_v = lam_frozen
        u0 = z[8]; u1 = z[9]; u2 = z[10]; u3 = z[11]
        v0 = z[12]; v1 = z[13]; v2 = z[14]; v3 = z[15]
        x0 = z[0]; x1 = z[1]; x2 = z[2]; x3 = z[3]
        y0 = z[4]; y1 = z[5]; y2 = z[6]; y3 = z[7]
        K = u0 * u0 + u1 * u1 + u2 * u2 + u3 * u3 + \
            v0 * v0 + v1 * v1 + v2 * v2 + v3 * v3
        sx0 = x0 - x1
        sx1 = -x0 + 2.0 * x1 - x2
        sx2 = -x1 + 2.0 * x2 - x3
        sx3 = -x2 + x3
        sy0 = y0 - y1
        sy1 = -y0 + 2.0 * y1 - y2
        sy2 = -y1 + 2.0 * y2 - y3
        sy3 = -y2 + y3
        V = x0 * sx0 + x1 * sx1 + x2 * sx2 + x3 * sx3 + \
            y0 * sy0 + y1 * sy1 + y2 * sy2 + y3 * sy3
        E = 0.5 * (K + V)
        Ec = Ec_min + dEc * lam_v
        Eth = Eth_min + dEth * lam_v
        xg = (Ec - E) / eps
        xth = (Ec - Eth) / eps
        d = d_max * math.tanh(xg) * math.tanh(xg - xth)
        out = np.empty(16)
        out[0] = u0; out[1] = u1; out[2] = u2; out[3] = u3
        out[4] = v0; out[5] = v1; out[6] = v2; out[7] = v3
        out[8] = -d * u0 - sx0; out[9] = -d * u1 - sx1
        out[10] = -d * u2 - sx2; out[11] = -d * u3 - sx3
        out[12] = -d * v0 - sy0; out[13] = -d * v1 - sy1
        out[14] = -d * v2 - sy2; out[15] = -d * v3 - sy3
        return out

    @njit(cache=True)
    def _rk4_step_nb(z, dt, t, T_moon, Ec_min, dEc, Eth_min, dEth,
                     eps, d_max, moving, lam_frozen):
        k1 = _stage_nb(z, t, T_moon, Ec_min, dEc, Eth_min, dEth,
                       eps, d_max, moving, lam_frozen)
        k2 = _stage_nb(z + 0.5 * dt * k1, t + 0.5 * dt, T_moon, Ec_min, dEc,
                       Eth_min, dEth, eps, d_max, moving, lam_frozen)
        k3 = _stage_nb(z + 0.5 * dt * k2, t + 0.5 * dt, T_moon, Ec_min, dEc,
                       Eth_min, dEth, eps, d_max, moving, lam_frozen)
        k4 = _stage_nb(z + dt * k3, t + dt, T_moon, Ec_min, dEc,
                       Eth_min, dEth, eps, d_max, moving, lam_frozen)
        return z + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    @njit(cache=True)
    def _integrate_nb(z0, dt, n_steps, sps, T_moon, Ec_min, dEc, Eth_min, dEth,
                      eps, d_max, moving, lam_frozen, track_gap, return_states):
        """与 _run_e2_py 完全同语义的 numba 积分器（对齐采样 Δt_s=100·dt0）。"""
        n_samp = n_steps // sps + 1
        t_grid = np.empty(n_samp)
        E_trace = np.empty(n_samp)
        lam_trace = np.empty(n_samp)
        r_trace = np.empty(n_samp)
        Z_trace = np.empty((n_samp, 16)) if return_states else np.empty((0, 16))
        z = z0.copy()
        t = 0.0
        if moving:
            lam0 = 0.5
        else:
            lam0 = lam_frozen
        E = _energy_nb(z)
        t_grid[0] = 0.0
        E_trace[0] = E
        lam_trace[0] = lam0
        r_trace[0] = E / (Ec_min + dEc * lam0)
        if return_states:
            Z_trace[0] = z.copy()
        min_gap = 1e300
        k = 1
        for i in range(1, n_steps + 1):
            if track_gap:
                if moving:
                    lam_v = 0.5 * (1.0 + math.sin(2.0 * math.pi * t / T_moon))
                else:
                    lam_v = lam0
                g = E - (Eth_min + dEth * lam_v)
                if g < min_gap:
                    min_gap = g
            z = _rk4_step_nb(z, dt, t, T_moon, Ec_min, dEc, Eth_min, dEth,
                             eps, d_max, moving, lam_frozen)
            t += dt
            E = _energy_nb(z)
            if i % sps == 0:
                if moving:
                    lam_v = 0.5 * (1.0 + math.sin(2.0 * math.pi * t / T_moon))
                else:
                    lam_v = lam0
                t_grid[k] = t
                E_trace[k] = E
                lam_trace[k] = lam_v
                r_trace[k] = E / (Ec_min + dEc * lam_v)
                if return_states:
                    Z_trace[k] = z.copy()
                k += 1
        return t_grid, E_trace, lam_trace, r_trace, min_gap, Z_trace


def _run_e2_py(z0, dt, T_total, T_moon, case, lam_frozen=None,
               return_states=False, track_min_gap=True):
    """纯 Python 路径：固定步长 RK4，采样网格恒 Δt_s=100·dt0（与 E1 对齐约定）。

    返回 dict：t_grid / r_trace / E_trace / lam_trace / min_gap（全时域）/
    states（可选，采样网格上的 z）。z0 为 numpy 数组（E1 single_mode_ic 输出）。"""
    z = [float(v) for v in z0]
    n = int(round(T_total / dt))
    sps = max(1, int(round(SAMPLE_EVERY * DT0 / dt)))
    n_samp = n // sps + 1
    t = 0.0
    lam0 = lam_frozen if lam_frozen is not None else lam_of_t(0.0, T_moon)
    Ec0 = case["Ec_min"] + case["dEc"] * lam0

    t_grid = np.empty(n_samp)
    E_trace = np.empty(n_samp)
    lam_trace = np.empty(n_samp)
    r_trace = np.empty(n_samp)
    Z_trace = np.empty((n_samp, 4 * N)) if return_states else None

    E = energy_py(z)
    t_grid[0] = 0.0
    E_trace[0] = E
    lam_trace[0] = lam0
    r_trace[0] = E / Ec0
    if return_states:
        Z_trace[0] = np.array(z)
    min_gap = float("inf")
    k = 1
    for i in range(1, n + 1):
        if track_min_gap:
            lam_v = lam0 if lam_frozen is not None else lam_of_t(t, T_moon)
            g = E - (case["Eth_min"] + case["dEth"] * lam_v)
            if g < min_gap:
                min_gap = g
        z = rk4_step_py(z, dt, t, T_moon, case, lam_frozen)
        t += dt
        E = energy_py(z)
        if i % sps == 0:
            lam_v = lam0 if lam_frozen is not None else lam_of_t(t, T_moon)
            t_grid[k] = t
            E_trace[k] = E
            lam_trace[k] = lam_v
            r_trace[k] = E / (case["Ec_min"] + case["dEc"] * lam_v)
            if return_states:
                Z_trace[k] = np.array(z)
            k += 1
    return {"t": t_grid, "r": r_trace, "E": E_trace, "lam": lam_trace,
            "min_gap": min_gap, "Z": Z_trace}


def run_e2(z0, dt, T_total, T_moon, case, lam_frozen=None,
           return_states=False, track_min_gap=True):
    """积分入口：numba JIT 路径（G_test=P₄ 且 numba 可用）或纯 Python 路径。

    两路径为同一标准 RK4 离散（Q6），语义等价——由 consistency_check 门禁验证。"""
    if USE_NUMBA:
        n_steps = int(round(T_total / dt))
        sps = max(1, int(round(SAMPLE_EVERY * DT0 / dt)))
        moving = 1 if lam_frozen is None else 0
        lf = 0.5 if lam_frozen is None else float(lam_frozen)
        t_grid, E_trace, lam_trace, r_trace, min_gap, Z_trace = _integrate_nb(
            np.ascontiguousarray(z0, dtype=np.float64), dt, n_steps, sps,
            T_moon, case["Ec_min"], case["dEc"], case["Eth_min"], case["dEth"],
            EPS, D_MAX, moving, lf, int(track_min_gap), int(return_states))
        return {"t": t_grid, "r": r_trace, "E": E_trace, "lam": lam_trace,
                "min_gap": min_gap, "Z": Z_trace if return_states else None}
    return _run_e2_py(z0, dt, T_total, T_moon, case, lam_frozen,
                      return_states, track_min_gap)


def consistency_check():
    """活动积分路径（numba 或纯 Python）vs E1 numpy 路径的一致性校验（实现层门禁）。

    同一标准 RK4 离散、同一 dt、同一参数（λ 冻结 0 时 case 参数 ≡ E1 的
    E_c=1/E_th=0.5，dEc=dEth=0 恒等）、同一 IC（E1 同款 single_mode_ic(1.0)），
    |Δz| 阈值 1e-10（浮点求和顺序差异量级）。"""
    z0 = single_mode_ic(1.0)          # E1 同款 IC（E_c=1）
    z_np = np.array(z0)
    if USE_NUMBA:
        z_e2 = np.array(z0)
        for i in range(CONSISTENCY_STEPS):
            z_np = rk4_step(z_np, DT0)               # E1 numpy 路径（E1 常量）
            z_e2 = _rk4_step_nb(z_e2, DT0, i * DT0, T_MOON_DUMMY,
                                1.0, 0.0, 0.5, 0.0, EPS, D_MAX, 0, 0.0)
        return float(np.max(np.abs(z_np - z_e2)))
    z_py = [float(v) for v in z0]
    case = {"Ec_min": 1.0, "dEc": 0.0, "Eth_min": 0.5, "dEth": 0.0}
    t = 0.0
    for _ in range(CONSISTENCY_STEPS):
        z_np = rk4_step(z_np, DT0)               # E1 numpy 路径（E1 常量）
        z_py = rk4_step_py(z_py, DT0, t, T_MOON_DUMMY, case, 0.0)
        t += DT0
    return float(np.max(np.abs(z_np - np.asarray(z_py))))


# ────────────────────────────────────────────────────────────────────
# 三、协议执行
# ────────────────────────────────────────────────────────────────────

def make_cases():
    """9 形状案例 = 3 种 ρ_c × 3 种 ΔE_th（Q5）。gap 约束验证。"""
    cases = []
    for rho in RHO_C_VALUES:
        dEc = (rho - 1.0) * EC_MIN
        for dEth in DETH_VALUES:
            case = {"rho": rho, "dEth": dEth,
                    "Ec_min": EC_MIN, "dEc": dEc,
                    "Eth_min": ETH_MIN,
                    "label": "rho=%.4g,dEth=%+.2f" % (rho, dEth)}
            # gap 约束：线性族 gap 最差在端点（Q5）
            for lam_t in (0.0, 1.0):
                assert gap_of_lam(lam_t, case) >= GAP_REL * Ec_of_lam(lam_t, case), \
                    "gap 约束破坏: %s @ λ=%g" % (case["label"], lam_t)
            cases.append(case)
    return cases


def ic_at_phase(T_moon, case, p0=0.0):
    """A1 单模态壳上旋转 IC（Q6）：E0 = E_c(λ(0))·(1+p0)，λ(0)=0.5。"""
    lam0 = lam_of_t(0.0, T_moon)          # = 0.5
    E0 = Ec_of_lam(lam0, case) * (1.0 + p0)
    return single_mode_ic(E0), lam0


def bench_eps_num(case, T_moon):
    """d≡0、λ 冻结基准（Q6/P4）：max|r−1| 于 dt0/dt0/2/dt0/4（E1 Phase 1 同款）。

    ε_num 为能量漂移观测量（E1 修正 2：能量观测量在保守振子上为 6 阶，
    收敛比 ≈ 32-64 而非状态误差的 [14.4,17.6]——本基准只做漂移量级门禁，
    阶检验继承 E1 对同一积分器的状态误差验证）。"""
    z0, lam0 = ic_at_phase(T_moon, case)
    T_horizon = HORIZON_BENCH * TAU_CHAR
    out = {}
    for dt in (DT0, DT0 / 2.0, DT0 / 4.0):
        res = run_e2(z0, dt, T_horizon, T_moon, case, lam_frozen=lam0,
                     track_min_gap=False)
        out["dt=%g" % dt] = float(np.max(np.abs(res["r"] - 1.0)))
    return out


def eps_num_at(dt, bench):
    """取 d≡0 冻结基准在给定 dt 的 ε_num（细化序列门禁用）。"""
    return bench["dt=%g" % dt]


def run_case_level(case, T_moon, tau_ratio, need_perturb, dt=DT0):
    """单案例单绝热档：moving + 冻结控制 + （可选）P3 扰动。返回判据字典。

    dt 为数值细化参数（预注册序列 dt0 → dt0/2 → dt0/4，仅 P4 分辨率门禁触发）。
    """
    lam0 = 0.5
    z0, _ = ic_at_phase(T_moon, case)
    T_settle = N_CYCLES_SETTLE * T_moon
    T_lo = N_CYCLES_ANALYZE[0] * T_moon
    T_hi = N_CYCLES_ANALYZE[1] * T_moon
    T_total = T_hi

    # --- moving 主跑 ---
    m = run_e2(z0, dt, T_total, T_moon, case, lam_frozen=None)
    # --- 冻结控制组（λ≡λ(0)，E1 式静态壳）---
    f = run_e2(z0, dt, T_total, T_moon, case, lam_frozen=lam0)

    mask = (m["t"] >= T_lo) & (m["t"] < T_hi)
    r_a = m["r"][mask]
    E_a = m["E"][mask]
    r_frozen_a = f["r"][mask]

    max_dev = float(np.max(np.abs(r_a - 1.0)))             # moving max|r−1|
    max_dev_frozen = float(np.max(np.abs(r_frozen_a - 1.0)))  # 数值地板
    adiab_dev = max_dev - max_dev_frozen                   # 绝热偏差（诊断）

    # P1 不脱壳：min(E−E_th(λ)) > 0（m.min_gap 为全时域——含瞬态，更严）
    p1_gap = float(m["min_gap"])
    p1 = p1_gap > 0.0

    # Δφ 诊断：E 包络峰值相位 vs 最近满月相位（满月 = λ=1 在 t=T_moon/4+k·T_moon）
    if len(E_a) > 4 * SAMPLE_EVERY:
        win = max(1, int(0.5 * TAU_CHAR / (SAMPLE_EVERY * DT0)))
        if win > 1:
            kk = np.ones(win) / win
            Es = np.convolve(E_a, kk, mode="same")
        else:
            Es = E_a
        t_peak_E = float(m["t"][mask][int(np.argmax(Es))])
    else:
        t_peak_E = float(m["t"][mask][int(np.argmax(E_a))])
    k_nearest = int(round(t_peak_E / T_moon - 0.25))
    t_peak_Ec = T_moon * (0.25 + k_nearest)     # 最近满月相位
    dphi = t_peak_E - t_peak_Ec                 # >0 = 响应滞后（诊断）

    # 周期锁定（诊断）：max |r(t+T_moon)−r(t)| over t ∈ [2T_moon, 3T_moon]
    # r(t+T_moon) 用 np.interp 在采样网格上精确求值（T_moon 非 Δt_s 整数倍）
    t3 = m["t"]
    r3 = m["r"]
    mask_c = (t3 >= 2 * T_moon) & (t3 < 3 * T_moon)
    t_c = t3[mask_c]
    r_c = r3[mask_c]
    if len(t_c) > 4:
        r_shifted = np.interp(t_c + T_moon, t3, r3)
        cycle_lock = float(np.max(np.abs(r_c - r_shifted)))
    else:
        cycle_lock = float("nan")

    # P3 吸引性：±10% 扰动，t* = 首次进入包络（之后一直保持）≤ T_settle
    p3 = None
    p3_tstar = None
    if need_perturb:
        env_max = max_dev
        margin = P3_MARGIN * env_max if env_max > 0 else DELTA_R
        tstar_list = []
        for sgn in (+1.0, -1.0):
            z_p, _ = ic_at_phase(T_moon, case, p0=sgn * P0)
            mp = run_e2(z_p, dt, T_settle, T_moon, case, lam_frozen=None)
            rp = mp["r"]
            tp = mp["t"]
            inside = np.abs(rp - 1.0) <= margin
            last_out = np.nonzero(~inside)[0]
            if len(last_out) == 0:
                tstar = float(tp[0])
            elif last_out[-1] + 1 < len(tp):
                tstar = float(tp[last_out[-1] + 1])
            else:
                tstar = None
            tstar_list.append(tstar)
        valid = [ts for ts in tstar_list if ts is not None]
        p3_tstar = max(valid) if valid else None
        p3 = (p3_tstar is not None) and (p3_tstar <= T_settle)

    return {"case": case["label"], "tau_ratio": tau_ratio,
            "eps_adiab": TAU_CHAR / (T_moon / (2.0 * np.pi)),
            "max_dev": max_dev, "max_dev_frozen": max_dev_frozen,
            "adiab_dev": adiab_dev, "p1_gap": p1_gap, "p1": p1,
            "dphi": dphi, "cycle_lock": cycle_lock,
            "p2a": None, "p3": p3, "p3_tstar": p3_tstar}


def qhat_stats(Z, t_grid, lam_trace, case, T_lo, T_hi):
    """q̂ 占位连通性诊断（Q4）：q̂_i = q_i/(E_c(λ)/N)，均匀壳上应 ≈1。

    q_i = ½‖φ̇_i‖² + ¼Σ_j w_ij|φ_i−φ_j|²（§11.4 正定局部能量密度，P₄ w=1）。
    验证响应链 λ → q_i → q̂ 端到端连通（占位基线，数值形状留 E6）。"""
    mask = (t_grid >= T_lo) & (t_grid < T_hi)
    Zw = Z[mask]
    lam_w = lam_trace[mask]
    n = Zw.shape[0]
    out = []
    for i in range(N):
        u = Zw[:, 2 * N + i]
        v = Zw[:, 3 * N + i]
        phi2 = u * u + v * v
        nb = np.zeros(n)
        for j in (i - 1, i + 1):
            if 0 <= j < N:
                dx = Zw[:, i] - Zw[:, j]
                dy = Zw[:, N + i] - Zw[:, N + j]
                nb += dx * dx + dy * dy
        qi = 0.5 * phi2 + 0.25 * nb
        base = (case["Ec_min"] + case["dEc"] * lam_w) / N
        qhat = qi / base
        out.append({"node": i, "qhat_min": float(qhat.min()),
                    "qhat_max": float(qhat.max()),
                    "qhat_mean": float(qhat.mean())})
    return out


def main():
    t_start = time.time()
    cases = make_cases()

    # 实现层一致性校验（Q6 声明 7：纯 Python 热循环 vs E1 numpy 路径）
    ck = consistency_check()
    print("E2 月相调制标定 — Grilling #102 协议（Q1-Q9 锁定）")
    print("G_test=P₄ | τ_char=%.4f | dt0=%.5f | 案例数=%d | 一致性校验 |Δz|max=%.2e (阈值 1e-12)"
          % (TAU_CHAR, DT0, len(cases), ck))
    if ck > 1e-12:
        print("!! 实现层失败：纯 Python 热循环与 E1 numpy 路径不一致")
        sys.exit(2)
    print("扫描：ρ_c=%s × ΔE_th=%s × T_moon/τ_char=%s" %
          (tuple(round(r, 4) for r in RHO_C_VALUES),
           tuple(DETH_VALUES), tuple(TAU_RATIOS)))

    # ── d≡0 冻结基准（P4）──
    bench = bench_eps_num(cases[0], TAU_RATIOS[-1] * TAU_CHAR)
    eps_num_dt0 = eps_num_at(DT0, bench)
    eps_num_dt0h = eps_num_at(DT0 / 2.0, bench)
    eps_num_dt0q = eps_num_at(DT0 / 4.0, bench)
    print("\n[P4 基准] d≡0, λ 冻结, 时域=%d·τ_char" % HORIZON_BENCH)
    print("  ε_num(dt0)=%.3e  ε_num(dt0/2)=%.3e  ε_num(dt0/4)=%.3e  门槛 ≤%.3f" %
          (eps_num_dt0, eps_num_dt0h, eps_num_dt0q, EPS_NUM_CAP))
    p4_bench_ok = eps_num_dt0 <= EPS_NUM_CAP

    # ── 主网格：9 案例 × 4 档 ──
    rows = []
    total = len(cases) * len(TAU_RATIOS)
    for ci, case in enumerate(cases):
        for li, tr in enumerate(TAU_RATIOS):
            T_moon = tr * TAU_CHAR
            need_perturb = li >= LEVEL_DEEP          # P3 于深绝热区 {10³,10⁴}
            dt_use = DT0
            rec = run_case_level(case, T_moon, tr, need_perturb, dt=dt_use)
            # P4 数值分离（深绝热区全过；细化仅最深档）：
            # ε_num(dt) ≤ 0.1×max|r−1|(dt)。深绝热档物理偏差 O(ε_adiab) 趋近
            # dt₀ 数值地板 → 预注册细化序列 dt₀ → dt₀/2 → dt₀/4（E1 修正同款
            # 唯一合法细化，no-tuning 允许）。
            if li >= LEVEL_DEEP:
                p4 = eps_num_dt0 <= P4_FACTOR * rec["max_dev"]
                if not p4 and li == len(TAU_RATIOS) - 1:
                    for dt_ref in (DT0 / 2.0, DT0 / 4.0):
                        rec = run_case_level(case, T_moon, tr, need_perturb, dt=dt_ref)
                        p4 = eps_num_at(dt_ref, bench) <= P4_FACTOR * rec["max_dev"]
                        if p4:
                            dt_use = dt_ref
                            break
            else:
                p4 = None
            p1 = rec["p1"]
            p2a = (rec["max_dev"] <= DELTA_R) if li == len(TAU_RATIOS) - 1 else None
            rec["p2a"] = p2a
            rec["p4"] = p4
            rec["dt_use"] = dt_use
            if li >= LEVEL_DEEP:          # 深绝热区 {10³,10⁴}：P1∧P3[∧P2a]∧P4
                if li == len(TAU_RATIOS) - 1:
                    gate_pass = bool(p1 and p2a and rec["p3"] and p4)
                else:
                    gate_pass = bool(p1 and rec["p3"] and p4)
                verdict = "PASS" if gate_pass else "FAIL"
            elif li >= LEVEL_P1_MIN:      # 过渡区 {10²}：P1
                gate_pass = bool(p1)
                verdict = "PASS" if gate_pass else "FAIL"
            else:                         # 快档 {10}：诊断（不入 PASS）
                verdict = "DIAG"
            rec["verdict"] = verdict
            rows.append(rec)
            print("[%02d/%02d] %-22s T_moon/τ=%-5d ε_adiab=%.2e  max|r−1|=%.4e "
                  "frozen=%.2e  gap=%.4e  P1=%s P2a=%s P3=%s P4=%s Δφ=%.3f dt=%s → %s"
                  % (ci * len(TAU_RATIOS) + li + 1, total,
                     rec["case"], tr, rec["eps_adiab"], rec["max_dev"],
                     rec["max_dev_frozen"], rec["p1_gap"],
                     "✓" if p1 else "✗",
                     ("✓" if p2a else "✗") if p2a is not None else "–",
                     ("✓" if rec["p3"] else "✗") if rec["p3"] is not None else "–",
                     ("✓" if p4 else "✗") if p4 is not None else "–",
                     rec["dphi"], ("dt0" if dt_use == DT0 else "dt0/%d" % int(round(DT0 / dt_use))),
                     verdict))
            sys.stdout.flush()

    # ── 验收合成（Q7）──
    deep_levels = TAU_RATIOS[LEVEL_DEEP:]
    trans_level = TAU_RATIOS[LEVEL_P1_MIN]
    deep_ok = all(r["verdict"] == "PASS" for r in rows
                  if r["tau_ratio"] in deep_levels)
    trans_ok = all(r["verdict"] == "PASS" for r in rows
                   if r["tau_ratio"] == trans_level)
    p4_deep = all(r["p4"] for r in rows if r["tau_ratio"] == TAU_RATIOS[-1])

    # ── q̂ 占位连通性诊断（Q4）：参考案例最深档 ──
    ref = cases[0]
    T_moon_ref = TAU_RATIOS[-1] * TAU_CHAR
    z0r, _ = ic_at_phase(T_moon_ref, ref)
    mr = run_e2(z0r, DT0, 4 * T_moon_ref, T_moon_ref, ref,
                lam_frozen=None, return_states=True)
    qhat = qhat_stats(mr["Z"], mr["t"], mr["lam"], ref,
                      2 * T_moon_ref, 4 * T_moon_ref)
    print("\n[q̂ 占位连通性诊断] 参考案例 %s @ T_moon/τ=10⁴（均匀壳上 q̂≈1 为正常月光强度）"
          % ref["label"])
    for row in qhat:
        print("  节点 %d: q̂ ∈ [%.4f, %.4f], mean=%.4f" %
              (row["node"], row["qhat_min"], row["qhat_max"], row["qhat_mean"]))
    sys.stdout.flush()
    # 破坏点定位：P1 首次失败的档位（从慢到快），ε_adiab* = 前一档对应值；
    # 扫描域内无失败 → 下界未解析（跟随在全部档位成立）
    levels_sorted = sorted(TAU_RATIOS)
    eps_adiab_star = None
    for tr in levels_sorted:
        fail = any(not r["p1"] for r in rows if r["tau_ratio"] == tr)
        if fail:
            idx = levels_sorted.index(tr)
            if idx > 0:
                T_moon_prev = levels_sorted[idx - 1] * TAU_CHAR
                eps_adiab_star = TAU_CHAR / (T_moon_prev / (2.0 * np.pi))
            break
    if eps_adiab_star is None:
        # 扫描下界（快档 ε_adiab = 2π/10）作为「未达破坏」的上界报告
        eps_adiab_star_edge = TAU_CHAR / (levels_sorted[0] * TAU_CHAR / (2.0 * np.pi))

    final_ok = deep_ok and trans_ok and p4_deep
    if not p4_bench_ok:
        verdict = "实现层失败（ε_num 基准超限）"
    elif not final_ok:
        verdict = "FAIL（深绝热区或过渡区未全过；协议层/结构层区分见诊断）"
    else:
        verdict = "PASS"

    print("\n" + "=" * 72)
    print("E2 最终裁决")
    print("  深绝热区 {10³,10⁴}: %s" % ("全过" if deep_ok else "未全过"))
    print("  过渡区 {10²}:      %s" % ("全过" if trans_ok else "未全过"))
    print("  P4 数值分离:       %s" % ("成立" if p4_deep else "不成立"))
    if eps_adiab_star is None:
        print("  ε_adiab*（成立区间下界）: ≤ %.2e（扫描域内未达破坏——跟随在"
              "T_moon/τ_char ≥ 10 全部档位成立，下界未解析）" % eps_adiab_star_edge)
    else:
        print("  ε_adiab*（成立区间下界）: %.2e" % eps_adiab_star)
    print("  → E2 结论: %s" % verdict)
    print("  注：PASS = 线性族+ΔE_th 方向族在深绝热区绝热跟随成立；ε_adiab* 为接口层"
          "「1 游戏日」映射硬约束（E2 只产约束不决定换算）。失败分类与后续处置见 #102")
    print("=" * 72)
    print("耗时 %.1f s" % (time.time() - t_start))

    summary = {
        "protocol": "Grilling #102 Q1-Q9",
        "G_test": "P4", "N": N,
        "tau_char": float(TAU_CHAR), "dt0": float(DT0),
        "scan": {"rho_c": list(RHO_C_VALUES), "dEth": list(DETH_VALUES),
                 "tau_ratios": list(TAU_RATIOS)},
        "placeholder_params": {"E_c,min": EC_MIN, "E_th,min": ETH_MIN,
                               "eps": EPS, "d_max": D_MAX},
        "consistency": float(ck),
        "p4_bench": {"eps_num_dt0": eps_num_dt0,
                     "eps_num_dt0h": eps_num_dt0h, "cap": EPS_NUM_CAP},
        "results": rows,
        "composition": {"deep_ok": deep_ok, "trans_ok": trans_ok,
                        "p4_deep": p4_deep,
                        "eps_adiab_star": eps_adiab_star,
                        "eps_adiab_star_edge": (
                            eps_adiab_star_edge if eps_adiab_star is None else None)},
        "final_verdict": verdict,
    }
    print("\nJSON:")
    print(json.dumps(summary, ensure_ascii=False, indent=2,
                     default=lambda o: float(o) if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
