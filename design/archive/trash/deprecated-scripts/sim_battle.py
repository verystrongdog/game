#!/usr/bin/env python3
"""冲突战蒙特卡洛模拟 v3 — 不碰撞，只看数值链路"""
import random, math, statistics
from collections import defaultdict

# ═══════════════════════════════════
# DATA (only emotion cards have PAD)
# ═══════════════════════════════════
EMOTIONS = {
    '恐惧': [-0.854, 0.680, -0.414], '愤怒': [-0.666, 0.730, 0.314],
    '焦虑': [-0.708, 0.730, -0.316], '厌恶': [-0.896, 0.550, -0.366],
    '恐怖': [-0.770, 0.700, -0.124], '绝望': [-0.770, 0.588, -0.510],
    '内疚': [-0.584, 0.134, -0.588], '悲痛': [-0.896, -0.424, -0.672],
    '孤独': [-0.500, -0.548, -0.524], '快乐': [0.960, 0.648, 0.588],
    '爱':   [1.000, 0.038, 0.346],   '共情': [0.458, -0.302, 0.090],
    '平静': [0.600, -0.756, 0.114],  '希望': [0.854, -0.366, 0.478],
    '敬畏': [-0.062, 0.480, -0.400],
}

# Cognition cards: 5 modules, each advances a CPM step
COG_MODULES = ['知觉与注意','记忆','知识表征','表象与语言','推理与决策']
COGNITIONS = [{'name': m, 'module': i} for i, m in enumerate(COG_MODULES)]

# Behavior cards: belong to one of 7 drives
DRIVES = ['反射','惩罚','奖励','道德','文化','价值','照护']
BEHAVIORS = [
    {'name':'僵住','drive':0},{'name':'逃跑','drive':0},{'name':'回避','drive':1},
    {'name':'妥协','drive':1},{'name':'趋近','drive':2},{'name':'坚持','drive':2},
    {'name':'坚守','drive':3},{'name':'纠正','drive':3},{'name':'遵从','drive':4},
    {'name':'礼仪','drive':4},{'name':'牺牲','drive':5},{'name':'超越','drive':5},
    {'name':'安抚','drive':6},{'name':'保护','drive':6},
]

# ═══════════════════════════════════
# CORE PIPELINE (all from docs)
# ═══════════════════════════════════

def sigmoid(x): return 1/(1+math.exp(-x))

def compute_drive_activations(V, A, D):
    """行为系统-整合.md §3.1"""
    g = {}
    g['反射'] = sigmoid(2.0*max(0,A-0.3) + 1.5*max(0,0.5-D) - 0.5)
    g['惩罚'] = sigmoid(2.5*min(0,V) + 1.0*max(0,A-0.2) - 0.3)
    g['奖励'] = sigmoid(2.5*max(0,V) + 0.8*max(0,A-0.2) - 0.35)
    g['道德'] = sigmoid(2.0*max(0,D-0.1) + 1.0*(1-abs(A)) - 0.4)
    g['文化'] = sigmoid(1.5*(1-abs(D)) + 2.0*0.5 - 0.3)  # C_score placeholder=0.5
    g['价值'] = sigmoid(1.5*max(0,D-0.4) + 3.0*0 - 0.7)  # willpower=0 baseline
    g['照护'] = sigmoid(1.0*V + 0.5*D + 0.5*0 - 0.5)     # willpower placeholder
    return g

def compute_phi(cog_progress):
    """CPM φ 门控, 行为系统-整合.md §6.1"""
    # cog_progress: 0-4 (number of CPM steps completed)
    phi = {'反射': 1.0}
    phi['惩罚'] = 1.0 if cog_progress >= 1 else 0.3
    phi['奖励'] = 1.0 if cog_progress >= 2 else 0.2
    phi['道德'] = 1.0 if cog_progress >= 3 else 0.1
    phi['文化'] = 1.0 if cog_progress >= 1 else 0.4
    phi['价值'] = 1.0 if cog_progress >= 4 else 0.05
    phi['照护'] = 1.0 if cog_progress >= 1 else 0.3
    return phi

def play_thresholds():
    """行为卡可用阈值, 行为系统-整合.md §4.1"""
    return {'反射':0.15,'惩罚':0.20,'奖励':0.25,'道德':0.35,'文化':0.15,'价值':0.50,'照护':0.20}

def behavior_beta_gamma():
    """成本调制β 和 效果调制γ, §4.2 §4.3"""
    beta  = {'反射':0.5,'惩罚':1.0,'奖励':1.2,'道德':0.8,'文化':0.3,'价值':1.5,'照护':0.6}
    gamma = {'反射':0.2,'惩罚':0.5,'奖励':0.6,'道德':0.7,'文化':0.2,'价值':1.0,'照护':0.5}
    return beta, gamma

def c_control_table(emo_name, drive_idx):
    """查表: 意志力系统.md §二 C_control.
    情绪名 → 驱动 → C_control 值."""
    # 15 emotions × 7 drives, from the verified table
    table = {
        '快乐': [None, None, 0,   0,   1.2, 0,   1.4],
        '爱':   [None, None, 0,   0,   0.4, 0,   1.4],
        '共情': [None, 0.8,  0,   0,   0.5, 2.5, 1.5],
        '平静': [None, None, 0,   0,   0.9, 2.7, 1.7],
        '希望': [None, None, 0,   0,   0.7, 0,   1.4],
        '敬畏': [None, 0,    2.0, 1.5, 0.4, 3.0, 2.0],
        '愤怒': [None, 0,    2.8, 0,   1.0, 0,   2.8],
        '恐惧': [0,    0,    2.8, 2.4, 1.1, 3.8, 2.8],
        '焦虑': [0,    0,    2.8, 2.3, 1.0, 3.8, 2.8],
        '厌恶': [0,    0,    2.7, 2.2, 1.0, 3.7, 2.7],
        '恐怖': [None, 0,    2.8, 0,   1.1, 3.8, 2.8],
        '绝望': [0,    0,    2.7, 2.2, 0.9, 3.7, 2.7],
        '内疚': [None, 0,    1.6, 1.5, 0.4, 2.6, 1.6],
        '悲痛': [None, 0,    2.4, 2.0, 0.8, 3.4, 2.4],
        '孤独': [None, 0,    2.4, 1.9, 0.7, 3.4, 2.4],
    }
    return table.get(emo_name, [0]*7)[drive_idx]

# ═══════════════════════════════════
# ONE ROUND
# ═══════════════════════════════════

def step(combatant):
    """
    处理一个战斗方的单回合状态计算。
    输入: combatant 的当前状态 (san, hp, emo_pad, cog_progress, beh_drive)
    输出: 该回合所有中间变量
    """
    V, A, D = combatant['emo_pad']
    san, hp = combatant['san'], combatant['hp']
    cog = combatant['cog_progress']
    drive_idx = combatant['beh_drive']
    drive_name = DRIVES[drive_idx]

    # Layer 2: drive activations
    g = compute_drive_activations(V, A, D)

    # Layer 3: CPM gating
    phi = compute_phi(cog)
    g_eff = {d: g[d]*phi[d] for d in g}

    # Layer 4: behavior card availability
    theta = play_thresholds()
    nat_avail = g_eff[drive_name] >= theta[drive_name]
    need_hard_unlock = not nat_avail

    # Layer 5: C_control
    c_ctrl = c_control_table(combatant['emo_name'], drive_idx)
    if c_ctrl is None:
        # 此情绪下该驱动不可用 (反射在非高A低D时无意义等)
        return {'status': 'blocked', 'reason': '驱动×情绪不兼容'}

    # Layer 6: EVC
    effort_discount = 0.5  # default
    epsilon = random.uniform(-0.3, 0.3)  # Logistic approx
    benefit = (san + hp) / 200.0 * 2.0   # ∝ 健康状态, 归一化到 [0, 2]
    evc = benefit - c_ctrl - effort_discount + epsilon
    theta_init = 1.0
    hard_ok = evc > theta_init if need_hard_unlock else True

    # Layer 7: costs if hard unlocked
    ap_premium = math.floor(c_ctrl) if need_hard_unlock else 0
    san_wear = max(0, c_ctrl - 1.5) if need_hard_unlock else 0
    effect_discount = 1 - 0.15 * c_ctrl

    # Layer 8-9: behavior output
    beta, gamma_mod = behavior_beta_gamma()
    cost_mod = 1 + beta[drive_name] * (1 - g_eff[drive_name])
    eff_mod = 1 + gamma_mod[drive_name] * max(0, g_eff[drive_name] - theta[drive_name])

    # B_raw (Frijda action tendency)
    b_raw = (V, abs(A), D)

    # Layer 10: mixed behavior output
    lam_raw = math.exp(-cog * 0.7)
    lam_drive = 1 - lam_raw

    # B_drive direction from drive valence
    drive_valence = {'反射':-1,'惩罚':-1,'奖励':1,'道德':0,'文化':0,'价值':1,'照护':1}
    b_drive_val = drive_valence[drive_name]
    b_drive = (b_drive_val, abs(A) if A>0 else 0.3, D)

    b_mixed = (
        lam_raw * b_raw[0] + lam_drive * b_drive[0],
        lam_raw * b_raw[1] + lam_drive * b_drive[1],
        lam_raw * b_raw[2] + lam_drive * b_drive[2],
    )

    return {
        'status': 'ok',
        'V': V, 'A': A, 'D': D,
        'g': g, 'g_eff': g_eff,
        'nat_avail': nat_avail, 'need_hard': need_hard_unlock,
        'c_ctrl': c_ctrl, 'benefit': benefit, 'evc': evc,
        'theta_init': theta_init, 'hard_ok': hard_ok,
        'ap_premium': ap_premium, 'san_wear': san_wear, 'effect_discount': effect_discount,
        'cost_mod': cost_mod, 'eff_mod': eff_mod,
        'b_raw': b_raw, 'b_drive': b_drive, 'b_mixed': b_mixed,
        'lam_raw': lam_raw, 'lam_drive': lam_drive,
    }

def apply_damage(combatant, result):
    """SAN 磨损直接扣 SAN (护盾), SAN 归零后扣 HP."""
    san_wear = result['san_wear']
    if san_wear > 0:
        if combatant['san'] >= san_wear:
            combatant['san'] -= san_wear
        else:
            overflow = san_wear - combatant['san']
            combatant['san'] = 0
            combatant['hp'] = max(0, combatant['hp'] - overflow)

# ═══════════════════════════════════
# SIMULATION
# ═══════════════════════════════════

def random_combatant(san=100, hp=100, cog=0):
    emo_name = random.choice(list(EMOTIONS.keys()))
    beh = random.choice(BEHAVIORS)
    return {
        'san': san, 'hp': hp, 'max_san': 100, 'max_hp': 100,
        'emo_name': emo_name,
        'emo_pad': EMOTIONS[emo_name],
        'cog_progress': cog,
        'beh_drive': beh['drive'],
        'beh_name': beh['name'],
    }

def analyze(N=5000):
    print(f"运行 {N} 回合 (每方独立结算, 不碰撞, SAN磨损=自伤)...")
    all_results = []
    death_rounds = []

    # Track distributions
    san_wear_vals = []
    evc_vals = []
    c_ctrl_vals = []
    hard_rate = 0
    blocked_rate = 0
    activation_rate = 0

    # Per-emotion analysis
    emo_stats = defaultdict(lambda: {'total':0,'blocked':0,'hard_needed':0,'hard_ok':0,'hard_fail':0,
                                      'avg_c':0,'avg_evc':0,'avg_san_wear':0})

    p = random_combatant()
    for r in range(N):
        # Each round: random new cards, cog progresses
        p['emo_name'] = random.choice(list(EMOTIONS.keys()))
        p['emo_pad'] = EMOTIONS[p['emo_name']]
        beh = random.choice(BEHAVIORS)
        p['beh_drive'] = beh['drive']
        p['beh_name'] = beh['name']

        # Occasionally advance cognition (simulating cognitive card being played)
        if random.random() < 0.5:
            p['cog_progress'] = min(4, p['cog_progress'] + 1)

        result = step(p)
        all_results.append(result)

        en = p['emo_name']
        emo_stats[en]['total'] += 1

        if result['status'] == 'blocked':
            blocked_rate += 1
            emo_stats[en]['blocked'] += 1
            continue

        activation_rate += 1
        c_ctrl_vals.append(result['c_ctrl'])
        evc_vals.append(result['evc'])
        emo_stats[en]['avg_c'] += result['c_ctrl']
        emo_stats[en]['avg_evc'] += result['evc']

        if result['need_hard']:
            hard_rate += 1
            emo_stats[en]['hard_needed'] += 1
            if result['hard_ok']:
                emo_stats[en]['hard_ok'] += 1
            else:
                emo_stats[en]['hard_fail'] += 1

        if result['san_wear'] > 0:
            san_wear_vals.append(result['san_wear'])
            emo_stats[en]['avg_san_wear'] += result['san_wear']

        apply_damage(p, result)

        if p['hp'] <= 0:
            death_rounds.append(r+1)
            p = random_combatant()  # reset

    # ═══════════════ OUTPUT ═══════════════════
    print(f"\n{'='*60}")
    print(f"系统链路数值分析 (N={N} 回合)")
    print(f"{'='*60}")

    print(f"\n── 1. 全局 ──")
    print(f"总可用回合: {activation_rate} ({activation_rate/N*100:.1f}%)")
    print(f"被阻塞 (驱动×情绪不兼容): {blocked_rate} ({blocked_rate/N*100:.1f}%)")
    print(f"需要硬解锁: {hard_rate} ({hard_rate/activation_rate*100:.1f}% of active)")
    print(f"SAN磨损回合: {len(san_wear_vals)} ({len(san_wear_vals)/activation_rate*100:.1f}% of active)")
    if death_rounds:
        print(f"HP归零次数: {len(death_rounds)}, 平均死亡回合: {statistics.mean(death_rounds):.1f}")

    print(f"\n── 2. C_control 分布 ──")
    print(f"均值: {statistics.mean(c_ctrl_vals):.2f}  中位: {statistics.median(c_ctrl_vals):.2f}")
    print(f"范围: {min(c_ctrl_vals):.1f} ~ {max(c_ctrl_vals):.1f}")
    # Histogram
    buckets = defaultdict(int)
    for v in c_ctrl_vals:
        b = f'{math.floor(v)}~{math.floor(v)+1}' if v < 4 else '4+'
        buckets[b] += 1
    for b in sorted(buckets.keys(), key=lambda x: float(x.split('~')[0])):
        print(f"  C ∈ [{b}): {buckets[b]:>5} ({buckets[b]/len(c_ctrl_vals)*100:>5.1f}%)")

    print(f"\n── 3. EVC 分布 ──")
    print(f"均值: {statistics.mean(evc_vals):.2f}  中位: {statistics.median(evc_vals):.2f}")
    evc_pass = sum(1 for v in evc_vals if v > 1.0)
    print(f"EVC > θ_initiation(1.0): {evc_pass} ({evc_pass/len(evc_vals)*100:.1f}%)")

    print(f"\n── 4. SAN 磨损分布 ──")
    if san_wear_vals:
        print(f"均值: {statistics.mean(san_wear_vals):.2f}  中位: {statistics.median(san_wear_vals):.2f}")
        print(f"范围: {min(san_wear_vals):.1f} ~ {max(san_wear_vals):.1f}")

    print(f"\n── 5. benefit 随健康衰减 ──")
    for hp_san in [(200,0), (150,0), (100,50), (50,50), (20,30), (10,10)]:
        b = (hp_san[0] + hp_san[1]) / 200.0 * 2.0
        print(f"  SAN+HP={sum(hp_san):>3} → benefit={b:.2f}")

    print(f"\n── 6. 15情绪 × 硬解锁需求 ──")
    print(f"{'情绪':<6} {'回合':<6} {'阻塞%':<8} {'需硬解锁%':<10} {'硬解锁通过%':<10} {'平均C':<8} {'平均EVC':<8}")
    for name in sorted(emo_stats.keys()):
        s = emo_stats[name]
        t = s['total']
        blk = s['blocked']/t*100
        hd = s['hard_needed']/t*100 if t>s['blocked'] else 0
        hok = s['hard_ok']/max(1,s['hard_needed'])*100
        ac = s['avg_c']/max(1,t-s['blocked'])
        ae = s['avg_evc']/max(1,t-s['blocked'])
        print(f"{name:<6} {t:<6} {blk:>5.1f}%  {hd:>7.1f}%   {hok:>7.1f}%    {ac:>5.2f}   {ae:>6.2f}")

    # ─── gaps ───
    print(f"\n── 7. 未解决问题 (待日后补救) ──")
    print("  ❓ benefit 公式: benefit = (SAN+HP)/200*2, 临时线性, 待卡牌体系建立后重定")
    print("  ❓ 态度碰撞: 未实现, 当前只有 SAN 磨损自伤, 双方不互动")
    print("  ❓ effort_discount 固定 0.5, ε 用 uniform(-0.3,0.3) 近似 Logistic")
    print("  ❓ θ_initiation 固定 1.0, helplessness 未参与计算")
    print("  ❓ C_score 固定 0.5 (文化情境分)")
    print("  ❓ 照护驱动 Vulnerability_signal / Attachment_strength 未接入")
    print("  ❓ 认知卡/行为卡的具体数据未定义 (PAD以外的自有属性)")
    print("  ❓ CPM 进度通过随机步进模拟, 实际应由认知卡驱动")
    print("  ❓ 所有行为卡被假设为硬解锁时都能打, 未区分行为卡的具体'效果'")

if __name__ == '__main__':
    analyze(5000)
