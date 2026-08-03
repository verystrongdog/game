#!/usr/bin/env python3
"""冲突战蒙特卡洛模拟 v4 — 双方卡牌对战, JSON 数据驱动

v4 新特性:
  - 从 data/*.json 加载卡池（15情绪卡 + 25认知卡 + 21行为卡 + 7驱动参数 + 态度矩阵）
  - 双方交替回合, 态度碰撞 (D轴差 → 胜者造成 SAN 伤害)
  - 手牌/牌库系统 (牌库46张, 手牌上限13, 每回合抽至满)
  - AP 系统 (每回合6AP, 行为卡消耗AP, 认知/情绪卡 AP=0)
  - 意志力追踪 (初始5点, 硬解锁消耗)
  - 卡牌组合检测 (完整态度/酝酿/冲动/执行)
  - 驱动惯性 (τ_rise/τ_decay 平滑)

用法:
  python3 sim_battle_v4.py                  # 默认: 蒙特卡洛 N=500
  python3 sim_battle_v4.py --mc N=1000      # 1000场蒙特卡洛
  python3 sim_battle_v4.py --verbose        # 单场详细回合日志
  python3 sim_battle_v4.py --random         # 随机选牌模式 (对照基线)
  python3 sim_battle_v4.py --smoke          # 冒烟测试 (5×100场)
"""

import json, math, random, statistics, sys
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

DATA_DIR = Path(__file__).parent / "data"

HAND_SIZE = 13
DRAW_PER_TURN = 6
BASE_AP = 6
MAX_WILLPOWER = 5
START_WILLPOWER = 5
START_SAN = 100
START_HP = 100
MAX_TURNS = 30
AP_PER_TURN = 6

# 7 驱动 ID 列表 (按 drives.json 顺序)
DRIVE_IDS = ['reflex', 'punish', 'reward', 'moral', 'culture', 'value', 'care']
DRIVE_NAMES = ['反射', '惩罚机制', '奖励机制', '道德驱动', '文化习俗', '价值驱动', '照护']
# 驱动 ID→短名 (与 attitudes.json id 格式一致)
DRIVE_SHORT_NAMES = {}

# C_control 表: 15情绪 × 7驱动 (来源: 意志力系统.md §二, v3 验证过)
# 格式: {emo_name: {drive_id: value or None}}
C_CONTROL_TABLE = {
    '快乐':  {'reflex': None, 'punish': None, 'reward': 0,   'moral': 0,   'culture': 1.2, 'value': 0,   'care': 1.4},
    '爱':    {'reflex': None, 'punish': None, 'reward': 0,   'moral': 0,   'culture': 0.4, 'value': 0,   'care': 1.4},
    '共情':  {'reflex': None, 'punish': 0.8,  'reward': 0,   'moral': 0,   'culture': 0.5, 'value': 2.5, 'care': 1.5},
    '平静':  {'reflex': None, 'punish': None, 'reward': 0,   'moral': 0,   'culture': 0.9, 'value': 2.7, 'care': 1.7},
    '希望':  {'reflex': None, 'punish': None, 'reward': 0,   'moral': 0,   'culture': 0.7, 'value': 0,   'care': 1.4},
    '敬畏':  {'reflex': None, 'punish': 0,    'reward': 2.0, 'moral': 1.5, 'culture': 0.4, 'value': 3.0, 'care': 2.0},
    '愤怒':  {'reflex': None, 'punish': 0,    'reward': 2.8, 'moral': 0,   'culture': 1.0, 'value': 0,   'care': 2.8},
    '恐惧':  {'reflex': 0,    'punish': 0,    'reward': 2.8, 'moral': 2.4, 'culture': 1.1, 'value': 3.8, 'care': 2.8},
    '焦虑':  {'reflex': 0,    'punish': 0,    'reward': 2.8, 'moral': 2.3, 'culture': 1.0, 'value': 3.8, 'care': 2.8},
    '厌恶':  {'reflex': 0,    'punish': 0,    'reward': 2.7, 'moral': 2.2, 'culture': 1.0, 'value': 3.7, 'care': 2.7},
    '恐怖':  {'reflex': None, 'punish': 0,    'reward': 2.8, 'moral': 0,   'culture': 1.1, 'value': 3.8, 'care': 2.8},
    '绝望':  {'reflex': 0,    'punish': 0,    'reward': 2.7, 'moral': 2.2, 'culture': 0.9, 'value': 3.7, 'care': 2.7},
    '内疚':  {'reflex': None, 'punish': 0,    'reward': 1.6, 'moral': 1.5, 'culture': 0.4, 'value': 2.6, 'care': 1.6},
    '悲痛':  {'reflex': None, 'punish': 0,    'reward': 2.4, 'moral': 2.0, 'culture': 0.8, 'value': 3.4, 'care': 2.4},
    '孤独':  {'reflex': None, 'punish': 0,    'reward': 2.4, 'moral': 1.9, 'culture': 0.7, 'value': 3.4, 'care': 2.4},
}

# 行为卡简化效果表 (card_id → numeric effect)
BEHAVIOR_EFFECTS = {
    # 反射驱动
    'flee':     {'type': 'buff_self', 'buff': 'dodge', 'duration': 1},
    'freeze':   {'type': 'buff_self', 'buff': 'freeze', 'duration': 1},
    'dodge':    {'type': 'buff_self', 'buff': 'dodge_counter', 'duration': 1},
    # 惩罚机制
    'withdraw': {'type': 'buff_self', 'buff': 'damage_reduce', 'value': 0.30, 'duration': 2},
    'concede':  {'type': 'remove_threat', 'ratio': 0.50},
    'restrain': {'type': 'willpower_recover', 'amount': 1},
    # 奖励机制
    'pursue':   {'type': 'buff_self', 'buff': 'anticipation', 'duration': 2},
    'persist':  {'type': 'buff_self', 'buff': 'tenacity', 'stacks': 2, 'max_stacks': 5},
    'probe':    {'type': 'reveal_enemy', 'count': 1},
    # 道德驱动
    'hold_fast':     {'type': 'san_restore', 'amount': 1},
    'uphold':        {'type': 'remove_debuff_ally', 'count': 1},
    'self_reproach': {'type': 'willpower_recover', 'amount': 2, 'requires': '内疚'},
    # 文化习俗
    'conform':  {'type': 'reduce_enemy_intent', 'ratio': 0.10},
    'follow':   {'type': 'copy_ally', 'ratio': 0.50},
    'ritual':   {'type': 'remove_debuff_self', 'count': 1, 'buff_stacks': 2},
    # 价值驱动
    'sacrifice':    {'type': 'san_damage', 'amount': 4, 'self_san': 2, 'self_hp_pct': 0.15},
    'breakthrough': {'type': 'san_damage', 'amount': 5, 'self_debuff': 'exhaustion'},
    'confront':     {'type': 'san_damage', 'amount': 3},
    # 照护
    'soothe':    {'type': 'calm_target', 'arousal_reduce': 0.3},
    'shield':    {'type': 'protect_ally', 'damage_reduce': 0.30},
    'body_block': {'type': 'protect_ally', 'damage_reduce': 0, 'absolute': True, 'self_debuff': 'heavy_wound'},
}

# 认知卡简化效果表
COGNITION_EFFECTS = {
    # 知觉与注意
    'insight':    {'type': 'reveal_enemy', 'count': 1},
    'focus':      {'type': 'ignore_hand_pressure', 'count': 1},
    'scrutinize': {'type': 'reveal_environment', 'count': 1},
    'survey':     {'type': 'broaden_attention', 'count': 1},
    'alert':      {'type': 'preview_enemy_intent', 'count': 1},
    # 记忆
    'reclaim':  {'type': 'recover_from_discard', 'count': 1},
    'recall':   {'type': 'search_deck', 'count': 5},
    'letgo':    {'type': 'remove_negative_emotion', 'count': 1},
    'flashback': {'type': 'replay_last_card', 'count': 1},
    'etch':     {'type': 'preserve_card', 'count': 1},
    # 知识表征与分类
    'discern':  {'type': 'reveal_enemy_full', 'duration': 2},
    'label':    {'type': 'add_tag', 'duration': 3},
    'attribute': {'type': 'reduce_enemy_effect', 'ratio': 0.25},
    'rectify':  {'type': 'remove_false_tag', 'count': 1},
    'analogy':  {'type': 'reduce_cost_modifier', 'value': 0.2, 'duration': 2},
    # 表象与语言
    'metaphor':  {'type': 'add_tag', 'duration': 3, 'san_damage_reduce': 1},
    'depict':    {'type': 'remove_illusions', 'count': 99},
    'envision':  {'type': 'preview_future', 'count': 1},
    'rephrase':  {'type': 'adjust_emotion_effect', 'ratio': 0.20},
    'naming':    {'type': 'permanent_tag', 'cost_willpower': 1},
    # 推理问题解决与决策
    'predict':  {'type': 'preview_enemy_actions', 'count': 3},
    'decide':   {'type': 'boost_branch', 'prob_boost': 0.20, 'cost_willpower': 1},
    'calculate': {'type': 'reduce_next_ap', 'amount': 1},
    'extend':   {'type': 'extend_duration', 'turns': 2},
    'weigh':    {'type': 'enhance_card', 'ratio': 0.30},
}

# 认知卡 CPM 参与 (card_id → {cpm_step, prerequisite_modules})
# 从 cognition_cards.json 提取
COG_CPM_MAP = {}
COG_MODULE_MAP = {}

# ═══════════════════════════════════════════════════════════
# COMBATANT DATA CLASS (Step 3)
# ═══════════════════════════════════════════════════════════

@dataclass
class Combatant:
    name: str
    san: float = START_SAN
    hp: float = START_HP
    max_san: float = START_SAN
    max_hp: float = START_HP
    willpower: int = START_WILLPOWER
    ap: int = AP_PER_TURN
    emo_pad: tuple = (0.0, 0.0, 0.0)  # (V, A, D)
    emo_name: str = '平静'
    cog_progress: int = 0
    deck: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    discard: list = field(default_factory=list)
    drive_activation: dict = field(default_factory=dict)
    inertia: dict = field(default_factory=dict)
    buffs: list = field(default_factory=list)
    turns_without_cog: int = 0   # 连续未打认知卡回合数
    last_attitude: dict = field(default_factory=dict)  # 上回合形成的态度 (用于碰撞)
    anticipation_bonus: bool = False  # 酝酿加成标记
    emotion_suppressed: bool = False  # 执行-情感压制标记
    last_combo_type: str = None  # 本回合打出的组合类型

# ═══════════════════════════════════════════════════════════
# MATH UTILS
# ═══════════════════════════════════════════════════════════

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def pad_magnitude(V: float, A: float, D: float) -> float:
    return math.sqrt(V*V + A*A + D*D)

def clamp_pad(val: float) -> float:
    return max(-1.0, min(1.0, val))

# ═══════════════════════════════════════════════════════════
# DATA LOADING (Step 1)
# ═══════════════════════════════════════════════════════════

def load_json(name: str) -> dict:
    with open(DATA_DIR / name, encoding='utf-8') as f:
        return json.load(f)

def load_game_data():
    """加载所有 JSON 数据, 构建查找表."""
    print("加载数据...", end=" ", flush=True)

    emotions_data = load_json('emotions.json')
    drives_data = load_json('drives.json')
    emotion_cards_data = load_json('emotion_cards.json')
    cognition_cards_data = load_json('cognition_cards.json')
    behavior_cards_data = load_json('behavior_cards.json')
    attitudes_data = load_json('attitudes.json')

    # ── 情绪 PAD 查找: {中文名: (V, A, D)} ──
    emo_pad = {}
    emo_id_to_name = {}
    for e in emotions_data['emotions']:
        p = e['pad']
        emo_pad[e['name']] = (p['V'], p['A'], p['D'])
        emo_id_to_name[e['id']] = e['name']

    # ── 驱动参数 ──
    drive_params = {}
    for d in drives_data['drives']:
        dp = {
            'name': d['name'],
            'theta_play': d['theta_play'],
            'theta_force': d.get('theta_force'),
            'beta': d['cost_sensitivity_beta'],
            'gamma': d['effect_gain_gamma'],
            'phi_value': d['cognitive_gate_phi']['value'],
            'phi_fallback': d['cognitive_gate_phi'].get('fallback', 0.3),
            'phi_condition': d['cognitive_gate_phi'].get('condition', ''),
            'drive_pole': (d['drive_pole']['valence'], d['drive_pole']['intensity'], d['drive_pole']['autonomy']),
            'rise_half_life': d['inertia']['rise_half_life'],
            'decay_half_life': d['inertia']['decay_half_life'] if isinstance(d['inertia']['decay_half_life'], (int, float)) else 1.0,
        }
        drive_params[d['id']] = dp

    # ── 认知门控时间线 (cog_progress → 可用驱动) ──
    gating_timeline = drives_data.get('cognitive_gating_timeline', {})
    # 简化: 从 drives 各自的 phi_condition 推导 phi 值
    # phi_reflex = 1.0 always (无前置)
    # phi_punish/culture = 1.0 if cog>=1 else fallback
    # phi_reward = 1.0 if cog>=2 else fallback
    # phi_moral = 1.0 if cog>=3 else fallback
    # phi_value = 1.0 if cog>=4 else fallback
    # phi_care = 1.0 if cog>=1 else fallback (from drives.json: 知觉与注意 + 知识表征)

    # ── 卡牌查找表 ──
    card_lookup = {}  # card_id → card_data

    for card in emotion_cards_data['cards']:
        card_lookup[card['id']] = card
    for card in cognition_cards_data['cards']:
        card_lookup[card['id']] = card
        # 填充 CPM map
        COG_CPM_MAP[card['id']] = {
            'step': card['cpm']['step'],
            'prereqs': card['cpm'].get('prerequisite_modules', []),
        }
        COG_MODULE_MAP[card['id']] = card['module']
    for card in behavior_cards_data['cards']:
        card_lookup[card['id']] = card

    # ── 态度矩阵: {emo_name: {drive_id: state}} ──
    attitude_matrix = attitudes_data.get('summary_matrix', {})

    # ── 态度查找索引: {(emo_name, drive_name): attitude_entry} ──
    # drive_name 使用中文驱动名 (如 '反射', '惩罚机制'), 与 attitude.id 格式 '情绪+驱动' 一致
    attitude_index = {}
    for att in attitudes_data.get('attitudes', []):
        key = (att['emotion'], att['id'].split('+')[1])
        attitude_index[key] = att

    # ── 行为卡驱动映射: {card_id: drive_id} ──
    beh_drive_map = {}
    drive_beh_map = defaultdict(list)  # {drive_id: [card_ids]}
    for card in behavior_cards_data['cards']:
        beh_drive_map[card['id']] = card['drive_id']
        drive_beh_map[card['drive_id']].append(card['id'])

    # ── 驱动 ID→中文名 映射 (全名) ──
    drive_id_to_name = {d['id']: d['name'] for d in drives_data['drives']}

    # 更新模块级 DRIVE_SHORT_NAMES (get_drive_name_for_card 使用)
    DRIVE_SHORT_NAMES.update({
        'reflex': '反射', 'punish': '惩罚', 'reward': '奖励',
        'moral': '道德', 'culture': '文化', 'value': '价值', 'care': '照护',
    })

    print("✓")
    print(f"  情绪: {len(emotions_data['emotions'])} 锚点, {len(emotion_cards_data['cards'])} 情绪卡")
    print(f"  认知: {len(cognition_cards_data['cards'])} 认知卡")
    print(f"  行为: {len(behavior_cards_data['cards'])} 行为卡")
    print(f"  驱动: {len(drives_data['drives'])} 驱动")
    print(f"  态度矩阵: {len(attitude_matrix)} 情绪 × 7 驱动, {len(attitude_index)} 条目已索引")

    return {
        'emo_pad': emo_pad,
        'emo_id_to_name': emo_id_to_name,
        'drive_params': drive_params,
        'card_lookup': card_lookup,
        'attitude_matrix': attitude_matrix,
        'attitude_index': attitude_index,
        'beh_drive_map': beh_drive_map,
        'drive_beh_map': drive_beh_map,
        'drive_id_to_name': drive_id_to_name,
        'emotion_cards': emotion_cards_data['cards'],
        'cognition_cards': cognition_cards_data['cards'],
        'behavior_cards': behavior_cards_data['cards'],
    }

# ═══════════════════════════════════════════════════════════
# CORE PIPELINE (Step 2) — 从 v3 移植, 参数化
# ═══════════════════════════════════════════════════════════

def compute_drive_activations(V: float, A: float, D: float, drive_params: dict, C_score: float=0.5) -> dict:
    """PAD → 7 驱动原始激活 g_raw (sigmoid).
    公式来源: drives.json activation.sigmoid, 与 v3 一致.
    """
    g = {}
    # reflex: σ(2.0·max(0,A-0.3) + 1.5·max(0,0.5-D) - 0.5)
    g['reflex'] = sigmoid(2.0 * max(0, A - 0.3) + 1.5 * max(0, 0.5 - D) - 0.5)
    # punish: σ(2.5·min(0,V) + 1.0·max(0,A-0.2) - 0.3)
    g['punish'] = sigmoid(2.5 * min(0, V) + 1.0 * max(0, A - 0.2) - 0.3)
    # reward: σ(2.5·max(0,V) + 0.8·max(0,A-0.2) - 0.35)
    g['reward'] = sigmoid(2.5 * max(0, V) + 0.8 * max(0, A - 0.2) - 0.35)
    # moral: σ(2.0·max(0,D-0.1) + 1.0·(1-|A|) - 0.4)
    g['moral']  = sigmoid(2.0 * max(0, D - 0.1) + 1.0 * (1 - abs(A)) - 0.4)
    # culture: σ(1.5·(1-|D|) + 2.0·C_score - 0.3) — C_score 门控
    g['culture'] = sigmoid(1.5 * (1 - abs(D)) + 2.0 * C_score - 0.3)
    # value: σ(1.5·max(0,D-0.4) + 3.0·Override_signal - 0.7), Override=willpower_rel/5
    g['value'] = sigmoid(1.5 * max(0, D - 0.4) + 3.0 * 0 - 0.7)  # willpower baseline=0
    # care: σ(2.5·Vuln_signal + 1.5·Attach_strength - 0.3), placeholder for both=0.5
    g['care'] = sigmoid(2.5 * 0.5 + 1.5 * 0.5 - 0.3)  # placeholder values

    return g

def compute_phi(cog_progress: int, drive_params: dict) -> dict:
    """CPM φ 门控. 来源: drives.json cognitive_gate_phi.
    cog_progress: 0-4 (完成的 CPM 步数)
    映射关系:
      reflex: φ=1.0 always
      punish, culture: φ=1.0 if cog>=1 else fallback
      reward: φ=1.0 if cog>=2 else fallback
      moral: φ=1.0 if cog>=3 else fallback
      value: φ=1.0 if cog>=4 else fallback
      care: φ=1.0 if cog>=1 else fallback
    """
    dp = drive_params
    phi = {'reflex': 1.0}  # 短路通道

    phi['punish']  = dp['punish']['phi_value'] if cog_progress >= 1 else dp['punish']['phi_fallback']
    phi['culture'] = dp['culture']['phi_value'] if cog_progress >= 1 else dp['culture']['phi_fallback']
    phi['care']    = dp['care']['phi_value'] if cog_progress >= 1 else dp['care'].get('phi_fallback', 0.3)

    phi['reward'] = dp['reward']['phi_value'] if cog_progress >= 2 else dp['reward']['phi_fallback']
    phi['moral']  = dp['moral']['phi_value'] if cog_progress >= 3 else dp['moral']['phi_fallback']
    phi['value']  = dp['value']['phi_value'] if cog_progress >= 4 else dp['value']['phi_fallback']

    return phi

def compute_drive_inertia(g_raw: dict, inertia_prev: dict, drive_params: dict) -> dict:
    """驱动惯性平滑: α_i(t) = α_i(t-1) + λ·(g_i - α_i(t-1)).
    λ = 1 - exp(-1/τ), τ = rise_half_life 或 decay_half_life.
    """
    alpha = {}
    for did in DRIVE_IDS:
        prev = inertia_prev.get(did, 0.0)
        g = g_raw.get(did, 0.0)
        dp = drive_params[did]

        if g > prev:
            tau = dp['rise_half_life']
        else:
            tau = dp['decay_half_life']

        # λ = 1 - exp(-0.693/tau) ≈ 1 - 0.5^(1/tau)
        lam = 1.0 - math.exp(-0.693147 / max(0.1, tau))
        alpha[did] = prev + lam * (g - prev)

    return alpha

def compute_behavior_beta_gamma(drive_params: dict):
    """成本调制 β 和 效果调制 γ. 来源: drives.json."""
    beta = {did: drive_params[did]['beta'] for did in DRIVE_IDS}
    gamma = {did: drive_params[did]['gamma'] for did in DRIVE_IDS}
    return beta, gamma

def get_c_control(emo_name: str, drive_id: str) -> Optional[float]:
    """查 C_control 表. None 表示该情绪下该驱动不可用."""
    row = C_CONTROL_TABLE.get(emo_name, {})
    return row.get(drive_id)

def compute_evc(benefit: float, c_ctrl: float, effort_discount: float=0.5) -> dict:
    """EVC 计算. 来源: 意志力系统.md.
    返回: {evc, epsilon, theta_init, hard_ok}
    """
    epsilon = random.uniform(-0.3, 0.3)  # Logistic 近似
    evc = benefit - c_ctrl - effort_discount + epsilon
    theta_init = 1.0
    return {
        'evc': evc,
        'epsilon': epsilon,
        'theta_init': theta_init,
        'hard_ok': evc > theta_init,
    }

def get_attitude_state(emo_name: str, drive_id: str, attitude_matrix: dict) -> str:
    """从态度矩阵获取 emotion×drive 的状态: natural | forced | situational | invalid."""
    row = attitude_matrix.get(emo_name, {})
    return row.get(drive_id, 'invalid')

# ═══════════════════════════════════════════════════════════
# COMBATANT INITIALIZATION (Step 3)
# ═══════════════════════════════════════════════════════════

def create_combatant(name: str, data: dict) -> Combatant:
    """初始化战斗方: 洗牌库, 抽初始手牌."""
    c = Combatant(name=name)

    # 牌库: 全部 25 认知卡 + 21 行为卡 = 46 张
    deck_ids = [card['id'] for card in data['cognition_cards']]
    deck_ids += [card['id'] for card in data['behavior_cards']]
    random.shuffle(deck_ids)
    c.deck = deck_ids
    c.discard = []

    # 初始手牌: 从牌库抽 6 张 + 2 张随机情绪卡
    c.hand = []
    draw_from_deck(c, 6)
    # 随机初始情绪 (从所有情绪卡中随机选取, 模拟不同开局情绪状态)
    emo_cards = data['emotion_cards']
    # 初始情绪偏向: 70% 中性/负面, 30% 正面 (战斗通常从紧张状态开始)
    neg_emos = [ec for ec in emo_cards if ec.get('valence_group') in ('negative', 'mixed')]
    pos_emos = [ec for ec in emo_cards if ec.get('valence_group') == 'positive']
    for _ in range(2):
        if random.random() < 0.7 and neg_emos:
            ec = random.choice(neg_emos)
        else:
            ec = random.choice(emo_cards)
        c.hand.append(ec['id'])
    # 初始 PAD: 随机选取一个情绪锚点
    init_emo = random.choice(list(data['emo_pad'].keys()))
    c.emo_name = init_emo
    c.emo_pad = data['emo_pad'][init_emo]

    # 初始化惯性
    c.inertia = {did: 0.0 for did in DRIVE_IDS}
    c.drive_activation = {did: 0.0 for did in DRIVE_IDS}

    return c

def draw_from_deck(c: Combatant, n: int):
    """从牌库抽 n 张到手中. 牌库空时从弃牌堆洗入."""
    drawn = 0
    while drawn < n:
        if not c.deck:
            if not c.discard:
                break  # 无牌可抽
            # 洗入弃牌堆
            c.deck = c.discard[:]
            random.shuffle(c.deck)
            c.discard = []
        c.hand.append(c.deck.pop())
        drawn += 1

def draw_phase(c: Combatant, data: dict, emotion_pool: list):
    """回合开始: 先抽情绪卡, 再从牌库补齐手牌. 重置 AP."""
    # ── 先抽情绪卡 (确保情绪卡不会被牌库卡挤掉) ──
    if emotion_pool:
        for _ in range(2):
            emo_card = random.choice(emotion_pool)
            if len(c.hand) < HAND_SIZE:
                c.hand.append(emo_card['id'])

    # ── 再从牌库补至手牌上限 ──
    needed = HAND_SIZE - len(c.hand)
    if needed > 0:
        draw_from_deck(c, min(needed, DRAW_PER_TURN))

    # 重置 AP
    c.ap = AP_PER_TURN

# ═══════════════════════════════════════════════════════════
# CARD UTILS (Step 3-4)
# ═══════════════════════════════════════════════════════════

def card_type(card_id: str, data: dict) -> str:
    """返回卡牌类型: '情绪' | '认知' | '行为'."""
    card = data['card_lookup'].get(card_id)
    return card['type'] if card else '未知'

def is_cognition(card_id: str, data: dict) -> bool:
    return card_type(card_id, data) == '认知'

def is_emotion(card_id: str, data: dict) -> bool:
    return card_type(card_id, data) == '情绪'

def is_behavior(card_id: str, data: dict) -> bool:
    return card_type(card_id, data) == '行为'

def card_drive(card_id: str, data: dict) -> Optional[str]:
    """返回行为卡的驱动 ID."""
    return data['beh_drive_map'].get(card_id)

def card_ap_cost(card_id: str, data: dict) -> int:
    """返回卡牌 AP 消耗 (认知/情绪=0, 行为=base_ap)."""
    card = data['card_lookup'].get(card_id, {})
    return card.get('base_ap', card.get('ap_cost', 0))

def card_name(card_id: str, data: dict) -> str:
    card = data['card_lookup'].get(card_id, {})
    return card.get('name', card_id)

# ═══════════════════════════════════════════════════════════
# ATTITUDE LOOKUP
# ═══════════════════════════════════════════════════════════

def lookup_attitude(emo_name: str, drive_name: str, data: dict) -> dict:
    """从态度索引查找条目. drive_name 为中文驱动名 (如 '反射', '价值驱动').
    返回: attitude_entry dict or None.
    """
    return data['attitude_index'].get((emo_name, drive_name))

def get_drive_name_for_card(card_id: str, data: dict) -> str:
    """获取行为卡对应的驱动短名 (与 attitudes.json 中 '情绪+驱动' 格式一致)."""
    drive_id = data['beh_drive_map'].get(card_id)
    if drive_id:
        return DRIVE_SHORT_NAMES.get(drive_id, '')
    return ''

# ═══════════════════════════════════════════════════════════
# COMBO DETECTION (Step 3)
# ═══════════════════════════════════════════════════════════

def check_combo(played_cards: list, data: dict, actor=None) -> dict:
    """检测卡牌组合类型并查找对应态度条目.
    优先级: 完整态度 > 酝酿 > 冲动 > 执行
    返回: {type, emo_mult, beh_mult, wp_bonus, attitude_entry, attitude_name, ...}
    """
    has_cog = any(is_cognition(cid, data) for cid in played_cards)
    has_emo = any(is_emotion(cid, data) for cid in played_cards)
    has_beh = any(is_behavior(cid, data) for cid in played_cards)

    # 找出具体的卡牌ID
    emo_card = next((cid for cid in played_cards if is_emotion(cid, data)), None)
    beh_card = next((cid for cid in played_cards if is_behavior(cid, data)), None)

    result = {'type': None, 'emo_mult': 1.0, 'beh_mult': 1.0, 'wp_bonus': 0,
              'attitude_entry': None, 'attitude_name': None}

    if has_cog and has_emo and has_beh:
        result['type'] = '完整态度'
        # 查找态度: emotion from card name, drive from behavior card
        if emo_card and beh_card:
            emo_name = card_name(emo_card, data)
            drive_name = get_drive_name_for_card(beh_card, data)
            att = lookup_attitude(emo_name, drive_name, data)
            if att:
                result['attitude_entry'] = att
                result['attitude_name'] = att.get('narrative_name', att['id'])

    elif has_cog and has_emo and not has_beh:
        result['type'] = '酝酿'
        result['wp_bonus'] = 0  # 酝酿不回复意志力

    elif has_emo and has_beh and not has_cog:
        result['type'] = '冲动'
        result['emo_mult'] = 1.5
        result['beh_mult'] = 1.2
        # 冲动也能产生态度: emotion + behavior → attitude
        if emo_card and beh_card:
            emo_name = card_name(emo_card, data)
            drive_name = get_drive_name_for_card(beh_card, data)
            att = lookup_attitude(emo_name, drive_name, data)
            if att:
                result['attitude_entry'] = att
                result['attitude_name'] = att.get('narrative_name', att['id'])

    elif has_cog and has_beh and not has_emo:
        result['type'] = '执行'
        result['wp_bonus'] = 1
        # 执行用当前情绪状态查态度 (没有打出情绪卡)
        if beh_card and actor:
            drive_name = get_drive_name_for_card(beh_card, data)
            att = lookup_attitude(actor.emo_name, drive_name, data)
            if att:
                result['attitude_entry'] = att
                result['attitude_name'] = att.get('narrative_name', att['id'])

    return result

# ═══════════════════════════════════════════════════════════
# AI CARD SELECTION (Step 3)
# ═══════════════════════════════════════════════════════════

def ai_select_cards(c: Combatant, data: dict, drive_params: dict, random_mode: bool=False) -> list:
    """AI 选牌: 贪心启发式或随机.
    返回: [card_ids] 本回合要打出的卡牌列表.
    """
    if random_mode:
        return ai_select_random(c, data)

    hand = c.hand[:]
    available_ap = c.ap
    selected = []

    # 分类手牌
    emo_cards = [cid for cid in hand if is_emotion(cid, data)]
    cog_cards = [cid for cid in hand if is_cognition(cid, data)]
    beh_cards = [cid for cid in hand if is_behavior(cid, data)]

    # ── 1. 优先打出情绪卡 (AP=0, 免费) ──
    if emo_cards:
        selected.append(emo_cards[0])
        hand.remove(emo_cards[0])

    # ── 2. 优先打出认知卡 (AP=0, 推进 CPM) ──
    if cog_cards:
        selected.append(cog_cards[0])
        hand.remove(cog_cards[0])

    # ── 3. 评估可用的行为卡 ──
    if beh_cards:
        # 计算当前驱动激活 (不打情绪卡时的 PAD)
        V, A, D = c.emo_pad
        g_raw = compute_drive_activations(V, A, D, drive_params)
        phi = compute_phi(c.cog_progress, drive_params)
        g_eff = {did: g_raw[did] * phi[did] for did in DRIVE_IDS}

        # 检查恐慌强制: g_reflex > theta_force
        theta_force = drive_params['reflex'].get('theta_force')
        if theta_force and g_eff['reflex'] > theta_force:
            # 必须打出反射卡
            reflex_cards = [cid for cid in beh_cards if card_drive(cid, data) == 'reflex']
            if reflex_cards:
                selected.append(reflex_cards[0])
                hand.remove(reflex_cards[0])
                return selected
            else:
                # 没有反射卡在手, 自动僵住 (freeze 自动加入)
                selected.append('freeze')
                return selected

        # 按 g_eff 排序驱动
        ranked_drives = sorted(DRIVE_IDS, key=lambda d: g_eff[d], reverse=True)

        for did in ranked_drives:
            if available_ap <= 0:
                break
            drive_cards = [cid for cid in beh_cards if card_drive(cid, data) == did]
            if not drive_cards:
                continue

            theta = drive_params[did]['theta_play']
            if g_eff[did] >= theta:
                # 自然可用
                best = min(drive_cards, key=lambda cid: card_ap_cost(cid, data))
            else:
                # 需要硬解锁 — 检查是否有足够意志力
                c_ctrl = get_c_control(c.emo_name, did)
                if c_ctrl is None or c.willpower < math.floor(c_ctrl):
                    continue  # 不可用
                best = min(drive_cards, key=lambda cid: card_ap_cost(cid, data))

            cost = card_ap_cost(best, data)
            if cost <= available_ap:
                selected.append(best)
                hand.remove(best)
                available_ap -= cost
                break  # 每回合只打一张行为卡

    return selected

def ai_select_random(c: Combatant, data: dict) -> list:
    """随机选牌 (对照基线)."""
    hand = c.hand[:]
    if not hand:
        return []
    selected = []
    # 随机选 0-3 张不同类型的卡
    for _ in range(random.randint(0, min(3, len(hand)))):
        if not hand:
            break
        idx = random.randrange(len(hand))
        selected.append(hand.pop(idx))
    return selected

# ═══════════════════════════════════════════════════════════
# CARD EFFECT RESOLUTION (Step 4)
# ═══════════════════════════════════════════════════════════

def resolve_emotion_card(actor: Combatant, card_id: str, data: dict, combo: dict) -> dict:
    """打出情绪卡: 应用 PAD 偏移. 返回结算日志."""
    card = data['card_lookup'].get(card_id, {})
    po = card.get('play_effect', {}).get('pad_offset', {})
    dV = po.get('dV', 0) * combo['emo_mult']
    dA = po.get('dA', 0) * combo['emo_mult']
    dD = po.get('dD', 0) * combo['emo_mult']

    old_pad = actor.emo_pad
    V = clamp_pad(old_pad[0] + dV)
    A = clamp_pad(old_pad[1] + dA)
    D = clamp_pad(old_pad[2] + dD)
    actor.emo_pad = (V, A, D)
    actor.emo_name = card.get('name', actor.emo_name)

    return {
        'card': card_id,
        'type': '情绪',
        'name': card.get('name', '?'),
        'pad_old': old_pad,
        'pad_new': actor.emo_pad,
        'pad_delta': (dV, dA, dD),
    }

def resolve_cognition_card(actor: Combatant, card_id: str, data: dict, combo: dict) -> dict:
    """打出认知卡: 推进 CPM. 返回结算日志."""
    card = data['card_lookup'].get(card_id, {})
    old_cog = actor.cog_progress
    actor.cog_progress = min(4, actor.cog_progress + 1)
    actor.turns_without_cog = 0

    # 认知卡特殊效果 (简化版)
    cog_eff = COGNITION_EFFECTS.get(card_id, {})
    eff_desc = cog_eff.get('type', 'cpm_advance') if cog_eff else 'cpm_advance'

    return {
        'card': card_id,
        'type': '认知',
        'name': card.get('name', '?'),
        'module': COG_MODULE_MAP.get(card_id, '?'),
        'cog_old': old_cog,
        'cog_new': actor.cog_progress,
        'effect': eff_desc,
    }

def resolve_behavior_card(actor: Combatant, target: Combatant, card_id: str,
                          data: dict, drive_params: dict, combo: dict) -> dict:
    """打出行为卡: 完整驱动链 + 简化数值效果. 返回结算日志."""
    card = data['card_lookup'].get(card_id, {})
    drive_id = card_drive(card_id, data)
    if not drive_id:
        return {'card': card_id, 'type': '行为', 'error': '无法确定驱动'}

    V, A, D = actor.emo_pad

    # ── Layer 1: 驱动原始激活 ──
    g_raw = compute_drive_activations(V, A, D, drive_params)
    # ── Layer 2: 惯性平滑 ──
    actor.inertia = compute_drive_inertia(g_raw, actor.inertia, drive_params)
    g_smooth = actor.inertia
    # ── Layer 3: CPM 门控 ──
    phi = compute_phi(actor.cog_progress, drive_params)
    g_eff = {did: g_smooth[did] * phi[did] for did in DRIVE_IDS}
    actor.drive_activation = g_eff

    # ── Layer 4: 可用性检查 ──
    theta = drive_params[drive_id]['theta_play']
    nat_avail = g_eff[drive_id] >= theta
    need_hard = not nat_avail

    # ── Layer 5: C_control ──
    c_ctrl = get_c_control(actor.emo_name, drive_id)
    blocked = c_ctrl is None

    # ── Layer 6: EVC ──
    ap_premium = 0
    san_wear = 0.0
    wp_cost = 0
    evc_result = {'evc': 0, 'hard_ok': True}

    if need_hard and not blocked:
        benefit = (actor.san + actor.hp) / 200.0 * 2.0
        evc_result = compute_evc(benefit, c_ctrl)
        hard_ok = evc_result['hard_ok']
        if hard_ok:
            wp_cost = math.floor(c_ctrl)
            ap_premium = wp_cost
            san_wear = max(0.0, c_ctrl - 1.5)
        else:
            blocked = True  # EVC 未通过

    # ── Layer 7: 成本/效果调制 ──
    beta, gamma = compute_behavior_beta_gamma(drive_params)
    cost_mod = 1.0 + beta[drive_id] * (1.0 - g_eff[drive_id])
    eff_mod = 1.0 + gamma[drive_id] * max(0.0, g_eff[drive_id] - theta)

    # ── Layer 8: 行为输出混合 ──
    lam_raw = math.exp(-actor.cog_progress * 0.7)
    lam_drive = 1.0 - lam_raw
    drive_pole = drive_params[drive_id]['drive_pole']
    b_raw = (V, abs(A), D)
    b_mixed = (
        lam_raw * b_raw[0] + lam_drive * drive_pole[0],
        lam_raw * b_raw[1] + lam_drive * drive_pole[1],
        lam_raw * b_raw[2] + lam_drive * drive_pole[2],
    )

    # ── Layer 9: 卡牌简化数值效果 ──
    beh_eff = BEHAVIOR_EFFECTS.get(card_id, {})
    eff_type = beh_eff.get('type', 'none')
    result_desc = ''
    damage_dealt = 0

    if eff_type == 'san_damage':
        amount = beh_eff.get('amount', 0) * eff_mod * combo['beh_mult']
        damage_dealt = int(amount)
        apply_san_damage(target, amount)

        # 自身代价
        self_san = beh_eff.get('self_san', 0)
        self_hp_pct = beh_eff.get('self_hp_pct', 0)
        if self_san:
            apply_san_damage(actor, self_san)
        if self_hp_pct:
            actor.hp = max(0, actor.hp - actor.max_hp * self_hp_pct)

        result_desc = f'心灵震慑 {damage_dealt}'
    elif eff_type == 'calm_target':
        ared = beh_eff.get('arousal_reduce', 0.3) * eff_mod
        Vt, At, Dt = target.emo_pad
        target.emo_pad = (Vt, clamp_pad(At - ared), Dt)
        result_desc = f'降低目标唤醒 {ared:.2f}'
    elif eff_type == 'san_restore':
        amount = beh_eff.get('amount', 1)
        actor.san = min(actor.max_san, actor.san + amount)
        result_desc = f'回复 SAN {amount}'
    elif eff_type == 'willpower_recover':
        amount = beh_eff.get('amount', 1)
        actor.willpower = min(MAX_WILLPOWER, actor.willpower + amount)
        result_desc = f'回复意志力 {amount}'
    elif eff_type == 'buff_self':
        buff_name = beh_eff.get('buff', '?')
        duration = beh_eff.get('duration', 1)
        actor.buffs.append({'name': buff_name, 'remaining': duration})
        result_desc = f'获得 {buff_name}({duration}回合)'
    elif eff_type == 'damage_reduce':
        result_desc = '降低伤害'
    else:
        result_desc = eff_type

    # ── 消耗 AP 和意志力 ──
    base_ap = card.get('base_ap', 1)
    actual_ap = max(0, int(base_ap * cost_mod) + ap_premium)
    actor.ap -= actual_ap
    if wp_cost > 0:
        actor.willpower -= wp_cost

    # ── 应用 SAN 磨损 ──
    if san_wear > 0:
        apply_san_damage(actor, san_wear)

    return {
        'card': card_id,
        'type': '行为',
        'name': card.get('name', '?'),
        'drive': drive_id,
        'drive_name': drive_params[drive_id]['name'],
        'g_raw': g_raw[drive_id],
        'g_smooth': g_smooth[drive_id],
        'g_eff': g_eff[drive_id],
        'theta': theta,
        'nat_avail': nat_avail,
        'need_hard': need_hard,
        'blocked': blocked,
        'c_ctrl': c_ctrl,
        'evc': evc_result['evc'],
        'wp_cost': wp_cost,
        'san_wear': san_wear,
        'ap_cost': actual_ap,
        'cost_mod': cost_mod,
        'eff_mod': eff_mod,
        'b_mixed': b_mixed,
        'damage_dealt': damage_dealt,
        'result': result_desc,
    }

def apply_san_damage(c: Combatant, amount: float):
    """SAN 护盾逻辑: SAN 先吸收, 溢出扣 HP."""
    if c.san >= amount:
        c.san -= amount
    else:
        overflow = amount - c.san
        c.san = 0.0
        c.hp = max(0.0, c.hp - overflow)

def apply_attitude_effect(actor: Combatant, target: Combatant, attitude_entry: dict,
                         combo_type: str) -> dict:
    """应用态度条目的 game_effect 到战斗双方.
    返回: effect_log dict.
    """
    if not attitude_entry:
        return {'applied': False, 'reason': '无态度条目'}

    ge = attitude_entry.get('game_effect', {})
    if not ge:
        return {'applied': False, 'reason': '态度条目无 game_effect'}

    etype = ge.get('effect_type', 'freeze')
    primary = ge.get('primary', {})
    secondary = ge.get('secondary', {})
    self_cost = ge.get('self_cost', {})
    effect_log = {'applied': True, 'type': etype, 'flavor': ge.get('flavor', ''),
                  'attitude_name': attitude_entry.get('narrative_name', attitude_entry['id'])}

    # ── 应用主效果 ──
    p_stat = primary.get('stat', '')
    p_amount = primary.get('amount', 0)

    if p_stat == 'san_damage':
        apply_san_damage(target, p_amount)
        effect_log['damage_dealt'] = p_amount
    elif p_stat == 'damage_reduce':
        actor.buffs.append({'name': 'damage_reduce', 'value': p_amount,
                           'remaining': primary.get('duration', 2)})
    elif p_stat == 'san_restore':
        actor.san = min(actor.max_san, actor.san + p_amount)
        effect_log['san_restored'] = p_amount
    elif p_stat == 'willpower':
        actor.willpower = min(MAX_WILLPOWER, actor.willpower + p_amount)
        effect_log['wp_restored'] = p_amount
    elif p_stat == 'draw':
        draw_from_deck(actor, p_amount)
        effect_log['cards_drawn'] = p_amount
    elif p_stat == 'dodge':
        actor.buffs.append({'name': 'dodge', 'remaining': primary.get('duration', 1)})
    elif p_stat == 'persistent_heal':
        actor.buffs.append({'name': 'persistent_heal', 'value': p_amount,
                           'remaining': primary.get('duration', 3)})
    elif p_stat == 'grant_tenacity':
        target.buffs.append({'name': 'tenacity', 'stacks': p_amount,
                            'remaining': primary.get('duration', 3)})

    # ── 应用次效果 ──
    s_stat = secondary.get('stat', '')
    s_amount = secondary.get('amount', 0)
    if s_stat == 'willpower':
        actor.willpower = min(MAX_WILLPOWER, actor.willpower + s_amount)
    elif s_stat == 'san_restore':
        actor.san = min(actor.max_san, actor.san + s_amount)

    # ── 应用自伤 ──
    if self_cost.get('san_wear', 0) > 0:
        apply_san_damage(actor, self_cost['san_wear'])
        effect_log['self_san_wear'] = self_cost['san_wear']
    if self_cost.get('wp_cost', 0) > 0:
        actor.willpower = max(0, actor.willpower - self_cost['wp_cost'])
        effect_log['self_wp_cost'] = self_cost['wp_cost']
    if self_cost.get('hp_cost_pct', 0) > 0:
        hp_loss = actor.max_hp * self_cost['hp_cost_pct']
        actor.hp = max(0, actor.hp - hp_loss)
        effect_log['self_hp_loss'] = hp_loss

    return effect_log


def resolve_attitude_collision(A: Combatant, B: Combatant, combo_A: dict=None, combo_B: dict=None) -> dict:
    """态度碰撞: 用 B(t) 三轴碰撞替代原始 PAD D 轴碰撞.

    B(t) = (valence, intensity, autonomy)
    - valence 方向差决定胜负
    - intensity 决定伤害量级
    - autonomy 差决定主动方额外优势

    特殊情况: 双方同向同主动 → 态度共振 (双方都获得 buff)
    """
    COLLISION_SCALE = 5.0

    # ── 获取双方 B(t) ──
    # 优先使用本回合打出的态度 (来自 combo), 否则用上回合存储的态度
    def get_bt(combatant, combo):
        if combo and combo.get('attitude_entry'):
            bo = combo['attitude_entry'].get('behavior_output', {})
            return (bo.get('valence', 0), bo.get('intensity', 0), bo.get('autonomy', 0))
        if combatant.last_attitude:
            bo = combatant.last_attitude.get('behavior_output', {})
            return (bo.get('valence', 0), bo.get('intensity', 0), bo.get('autonomy', 0))
        # fallback: 从 PAD 构造
        V, A, D = combatant.emo_pad
        return (V, abs(A), D)

    va, ia, aa = get_bt(A, combo_A)
    vb, ib, ab = get_bt(B, combo_B)

    valence_diff = va - vb
    intensity_sum = ia + ib
    autonomy_diff = aa - ab

    # 态度共振: 双方同向 (valence 符号相同且差值小)
    if (va >= 0 and vb >= 0) or (va < 0 and vb < 0):
        if abs(valence_diff) < 0.3:
            # 双方同向 → 共振: 各回复 SAN (基于 intensity)
            heal = intensity_sum * COLLISION_SCALE * 0.3
            A.san = min(A.max_san, A.san + heal)
            B.san = min(B.max_san, B.san + heal)
            return {'winner': None, 'resonance': True,
                    'bt_A': (va, ia, aa), 'bt_B': (vb, ib, ab),
                    'heal': heal,
                    'attitude_A': combo_A.get('attitude_name') if combo_A else None,
                    'attitude_B': combo_B.get('attitude_name') if combo_B else None}

    # 方向冲突
    damage_to_B = intensity_sum * (1.0 + abs(valence_diff)) * (1.0 + max(0, autonomy_diff)) * COLLISION_SCALE / 2
    damage_to_A = intensity_sum * (1.0 + abs(valence_diff)) * (1.0 + max(0, -autonomy_diff)) * COLLISION_SCALE / 2

    apply_san_damage(B, damage_to_B)
    apply_san_damage(A, damage_to_A)

    if damage_to_B > damage_to_A:
        winner = A.name
    elif damage_to_A > damage_to_B:
        winner = B.name
    else:
        winner = None

    return {'winner': winner, 'resonance': False,
            'bt_A': (va, ia, aa), 'bt_B': (vb, ib, ab),
            'damage_to_A': damage_to_A, 'damage_to_B': damage_to_B,
            'attitude_A': combo_A.get('attitude_name') if combo_A else None,
            'attitude_B': combo_B.get('attitude_name') if combo_B else None}

# ═══════════════════════════════════════════════════════════
# TURN RESOLUTION (Step 5)
# ═══════════════════════════════════════════════════════════

def resolve_turn(actor: Combatant, target: Combatant, data: dict,
                 drive_params: dict, emotion_pool: list, turn: int,
                 random_mode: bool=False) -> dict:
    """一方的完整回合结算. 返回回合日志.
    v4.1: 接入态度系统 — 组合检测查态度条目, 应用 game_effect, 存储 last_attitude.
    """
    log = {'actor': actor.name, 'turn': turn, 'events': [], 'collision': None,
           'attitude_effect': None}

    # ── 抽牌阶段 ──
    draw_phase(actor, data, emotion_pool)
    log['hand_size'] = len(actor.hand)
    log['ap_start'] = actor.ap

    # ── AI 选牌 ──
    played = ai_select_cards(actor, data, drive_params, random_mode)
    log['played'] = played

    # ── 打出认知卡: CPM 衰减逻辑 ──
    has_cog = any(is_cognition(cid, data) for cid in played)

    # ── 组合检测 (含态度查找) ──
    combo = check_combo(played, data, actor)
    log['combo'] = combo
    actor.last_combo_type = combo.get('type')

    # ── 结算每张卡 ──
    for cid in played:
        # 从手牌移除
        if cid in actor.hand:
            actor.hand.remove(cid)

        if is_emotion(cid, data):
            event = resolve_emotion_card(actor, cid, data, combo)
            # 情绪卡打出后消耗 (移出本场)
        elif is_cognition(cid, data):
            event = resolve_cognition_card(actor, cid, data, combo)
            # 认知卡回牌库
            actor.discard.append(cid)
        elif is_behavior(cid, data):
            event = resolve_behavior_card(actor, target, cid, data, drive_params, combo)
            # 行为卡回牌库
            actor.discard.append(cid)
        else:
            event = {'card': cid, 'type': '未知', 'error': '未识别的卡牌'}
        log['events'].append(event)

    # ── 应用态度效果 ──
    if combo.get('attitude_entry'):
        att_eff = apply_attitude_effect(actor, target, combo['attitude_entry'], combo['type'])
        log['attitude_effect'] = att_eff
        # 存储为 last_attitude (用于下回合碰撞)
        actor.last_attitude = combo['attitude_entry']
    else:
        # 清除上回合态度 (本回合未形成态度)
        actor.last_attitude = {}

    # ── 组合特殊效果 ──
    combo_type = combo.get('type')
    if combo_type == '酝酿':
        actor.anticipation_bonus = True
        # 酝酿产情绪卡 (PAD 最近锚点)
        log['anticipation'] = True
    else:
        actor.anticipation_bonus = False

    if combo_type == '执行':
        actor.emotion_suppressed = True
    else:
        actor.emotion_suppressed = False

    # ── 意志力回收 ──
    wp_bonus = combo.get('wp_bonus', 0)
    if wp_bonus > 0:
        actor.willpower = min(MAX_WILLPOWER, actor.willpower + wp_bonus)
        log['wp_bonus'] = wp_bonus

    # ── 未打出认知卡: 累计 ──
    if not has_cog:
        actor.turns_without_cog += 1
        if actor.turns_without_cog >= 3:
            actor.cog_progress = max(0, actor.cog_progress - 1)
            actor.turns_without_cog = 0
            log['cog_decay'] = True

    # ── PAD 衰减 ──
    # 酝酿: 衰减减半 (§四 4.3)
    # 执行(情感压制): 下回合情绪偏移减半 (§六 6.3) — 标记已在上面设置
    decay_rate = 0.05 if combo_type == '酝酿' else 0.10
    V, A, D = actor.emo_pad
    actor.emo_pad = (V * (1 - decay_rate), A * (1 - decay_rate), D * (1 - decay_rate))

    # ── Buff 持续回合递减 + 持续效果结算 ──
    for b in actor.buffs:
        b['remaining'] -= 1
        # persistent_heal: 每回合自动回复 SAN
        if b.get('name') == 'persistent_heal':
            actor.san = min(actor.max_san, actor.san + b.get('value', 1))
    actor.buffs = [b for b in actor.buffs if b['remaining'] > 0]

    log['pad_end'] = actor.emo_pad
    log['cog_end'] = actor.cog_progress
    log['ap_end'] = actor.ap
    log['wp_end'] = actor.willpower
    log['san_end'] = actor.san
    log['hp_end'] = actor.hp

    return log

# ═══════════════════════════════════════════════════════════
# BATTLE SIMULATION (Step 5)
# ═══════════════════════════════════════════════════════════

def simulate_battle(data: dict, random_mode: bool=False, verbose: bool=False) -> dict:
    """单场战斗: 双方交替回合直到一方 HP≤0 或达到回合上限."""
    dp = data['drive_params']
    emotion_pool = data['emotion_cards']

    A = create_combatant('玩家', data)
    B = create_combatant('敌方', data)

    battle_log = []
    winner = None

    for turn in range(1, MAX_TURNS + 1):
        # A 的回合
        log_a = resolve_turn(A, B, data, dp, emotion_pool, turn, random_mode)
        # 态度碰撞 (传入 combo 以使用 B(t))
        combo_a = log_a.get('combo', {})
        combo_b = {'attitude_entry': B.last_attitude} if B.last_attitude else {}
        collision = resolve_attitude_collision(A, B, combo_a, combo_b)
        log_a['collision'] = collision
        battle_log.append(log_a)

        if verbose:
            print_turn_log(log_a)

        if B.hp <= 0:
            winner = '玩家'
            break

        # B 的回合
        log_b = resolve_turn(B, A, data, dp, emotion_pool, turn, random_mode)
        combo_b = log_b.get('combo', {})
        combo_a2 = {'attitude_entry': A.last_attitude} if A.last_attitude else {}
        collision = resolve_attitude_collision(B, A, combo_b, combo_a2)
        log_b['collision'] = collision
        battle_log.append(log_b)

        if verbose:
            print_turn_log(log_b)

        if A.hp <= 0:
            winner = '敌方'
            break

    if winner is None:
        # 判定: HP 高者胜
        winner = '玩家' if A.hp > B.hp else ('敌方' if B.hp > A.hp else '平局')

    return {
        'winner': winner,
        'turns': len(battle_log) // 2 + len(battle_log) % 2,
        'battle_log': battle_log,
        'A_final': {'san': A.san, 'hp': A.hp, 'wp': A.willpower, 'pad': A.emo_pad, 'cog': A.cog_progress},
        'B_final': {'san': B.san, 'hp': B.hp, 'wp': B.willpower, 'pad': B.emo_pad, 'cog': B.cog_progress},
    }

def print_turn_log(log: dict):
    """打印单回合日志 (v4.1: 含态度名称和效果)."""
    actor = log['actor']
    t = log['turn']
    combo = log['combo']
    combo_type = combo.get('type', '')
    att_name = combo.get('attitude_name', '')
    combo_str = f" [{combo_type}]" if combo_type else ""
    if att_name:
        combo_str += f" 「{att_name}」"
    print(f"\n── {actor} 第{t}回合{combo_str} (AP:{log['ap_start']}→{log['ap_end']}) ──")

    for ev in log['events']:
        if ev.get('type') == '情绪':
            old = ev['pad_old']
            new = ev['pad_new']
            print(f"  ~ {ev['name']}: PAD ({old[0]:+.2f},{old[1]:+.2f},{old[2]:+.2f}) → ({new[0]:+.2f},{new[1]:+.2f},{new[2]:+.2f})")
        elif ev.get('type') == '认知':
            print(f"  ◇ {ev['name']} [{ev.get('module','?')}]: CPM {ev['cog_old']}→{ev['cog_new']} | {ev.get('effect','')}")
        elif ev.get('type') == '行为':
            g = ev.get('g_eff', 0)
            th = ev.get('theta', 0)
            flag = ''
            if ev.get('blocked'):
                flag = ' ✗阻塞'
            elif ev.get('need_hard'):
                flag = f" ⚠硬解锁(C={ev.get('c_ctrl','?')}, WP-{ev.get('wp_cost',0)})"
            else:
                flag = f" ✓自然(g={g:.2f}>{th})"
            print(f"  ⚡ {ev['name']} [{ev.get('drive_name','?')}]{flag}: {ev.get('result','')} | AP-{ev.get('ap_cost',0)}")

    # ── 态度效果 ──
    att_eff = log.get('attitude_effect') or {}
    if att_eff.get('applied'):
        print(f"  ✦ 态度效果 [{att_eff.get('attitude_name','?')}]: {att_eff.get('flavor','')}")
        if att_eff.get('self_san_wear'):
            print(f"    自伤: SAN磨损-{att_eff['self_san_wear']:.1f}", end='')
        if att_eff.get('self_wp_cost'):
            print(f"  WP-{att_eff['self_wp_cost']}", end='')
        if att_eff.get('self_hp_loss'):
            print(f"  HP-{att_eff['self_hp_loss']:.0f}", end='')
        if any(k in att_eff for k in ('self_san_wear', 'self_wp_cost', 'self_hp_loss')):
            print()

    # ── 态度碰撞 ──
    col = log.get('collision', {})
    if col:
        if col.get('resonance'):
            name_a = col.get('attitude_A', '?')
            name_b = col.get('attitude_B', '?')
            print(f"  ⟷ 态度共振 「{name_a}」×「{name_b}」: 双方各回复 {col['heal']:.1f} SAN")
        else:
            name_a = col.get('attitude_A', '?')
            name_b = col.get('attitude_B', '?')
            if col.get('winner'):
                print(f"  ⟷ 态度碰撞 「{name_a}」vs「{name_b}」: {col['winner']} 胜")
            else:
                print(f"  ⟷ 态度碰撞 「{name_a}」vs「{name_b}」: 僵持")
            print(f"    B(t)_A=({col['bt_A'][0]:+.2f},{col['bt_A'][1]:+.2f},{col['bt_A'][2]:+.2f})  B(t)_B=({col['bt_B'][0]:+.2f},{col['bt_B'][1]:+.2f},{col['bt_B'][2]:+.2f})")
            print(f"    伤害: A←{col.get('damage_to_A', 0):.1f}  B←{col.get('damage_to_B', 0):.1f}")

    if log.get('cog_decay'):
        print(f"  ⚠ 连续3回合无认知卡, CPM 衰减")
    if log.get('wp_bonus'):
        print(f"  ✦ 执行组合: 意志力 +{log['wp_bonus']}")
    if log.get('anticipation'):
        print(f"  ✦ 酝酿: PAD衰减减半, 产情绪卡")

    print(f"  → SAN:{log['san_end']:.0f} HP:{log['hp_end']:.0f} WP:{log['wp_end']} CPM:{log['cog_end']} PAD:({log['pad_end'][0]:+.2f},{log['pad_end'][1]:+.2f},{log['pad_end'][2]:+.2f})")

# ═══════════════════════════════════════════════════════════
# MONTE CARLO ANALYSIS (Step 5-6)
# ═══════════════════════════════════════════════════════════

def monte_carlo(N: int=500, random_mode: bool=False, verbose: bool=False):
    """运行 N 场蒙特卡洛模拟, 输出统计摘要."""
    mode_str = "随机模式" if random_mode else "AI模式"
    print(f"\n{'='*60}")
    print(f"冲突战蒙特卡洛模拟 v4 — {mode_str} (N={N})")
    print(f"{'='*60}")

    data = load_game_data()
    dp = data['drive_params']

    # ── 运行 ──
    results = []
    stats = {
        'wins': Counter(),
        'turns': [],
        'cards_played': Counter(),
        'combos': Counter(),
        'c_ctrl_vals': [],
        'san_wear_vals': [],
        'blocked_count': 0,
        'hard_unlock_count': 0,
        'total_beh_played': 0,
        'total_cog_played': 0,
        'total_emo_played': 0,
    }

    for i in range(N):
        result = simulate_battle(data, random_mode, verbose=(verbose and i == 0))
        results.append(result)

        stats['wins'][result['winner']] += 1
        stats['turns'].append(result['turns'])

        for log in result['battle_log']:
            for ev in log['events']:
                stats['cards_played'][ev.get('name', ev.get('card', '?'))] += 1
                if ev.get('type') == '情绪':
                    stats['total_emo_played'] += 1
                elif ev.get('type') == '认知':
                    stats['total_cog_played'] += 1
                elif ev.get('type') == '行为':
                    stats['total_beh_played'] += 1
                    if ev.get('blocked'):
                        stats['blocked_count'] += 1
                    if ev.get('need_hard'):
                        stats['hard_unlock_count'] += 1
                    if ev.get('c_ctrl') is not None:
                        stats['c_ctrl_vals'].append(ev['c_ctrl'])
                    if ev.get('san_wear', 0) > 0:
                        stats['san_wear_vals'].append(ev['san_wear'])
            if log.get('combo', {}).get('type'):
                stats['combos'][log['combo']['type']] += 1

        if (i + 1) % 100 == 0:
            print(f"  已运行 {i+1}/{N}...")

    # ── 输出 ──
    print(f"\n── 1. 全局 ──")
    print(f"总战斗场次: {N}")
    print(f"玩家胜率: {stats['wins'].get('玩家', 0)/N*100:.1f}%")
    print(f"敌方胜率: {stats['wins'].get('敌方', 0)/N*100:.1f}%")
    print(f"平局: {stats['wins'].get('平局', 0)/N*100:.1f}%")
    print(f"平均回合数: {statistics.mean(stats['turns']):.1f} (中位: {statistics.median(stats['turns']):.0f})")
    if stats['turns']:
        print(f"回合范围: {min(stats['turns'])} ~ {max(stats['turns'])}")

    print(f"\n── 2. 卡牌使用 ──")
    print(f"总打出: {stats['total_emo_played']} 情绪 + {stats['total_cog_played']} 认知 + {stats['total_beh_played']} 行为")
    print(f"行为卡阻塞: {stats['blocked_count']} ({stats['blocked_count']/max(1,stats['total_beh_played'])*100:.1f}%)")
    print(f"硬解锁: {stats['hard_unlock_count']} ({stats['hard_unlock_count']/max(1,stats['total_beh_played'])*100:.1f}%)")

    print(f"\n── 3. C_control 分布 ──")
    if stats['c_ctrl_vals']:
        print(f"均值: {statistics.mean(stats['c_ctrl_vals']):.2f}  中位: {statistics.median(stats['c_ctrl_vals']):.2f}")
        print(f"范围: {min(stats['c_ctrl_vals']):.1f} ~ {max(stats['c_ctrl_vals']):.1f}")

    print(f"\n── 4. SAN 磨损分布 ──")
    if stats['san_wear_vals']:
        print(f"均值: {statistics.mean(stats['san_wear_vals']):.2f}  中位: {statistics.median(stats['san_wear_vals']):.2f}")
        print(f"范围: {min(stats['san_wear_vals']):.1f} ~ {max(stats['san_wear_vals']):.1f}")

    print(f"\n── 5. 卡牌组合分布 ──")
    for combo_type in ['完整态度', '酝酿', '冲动', '执行']:
        c = stats['combos'].get(combo_type, 0)
        print(f"  {combo_type}: {c} ({c/max(1,sum(stats['combos'].values()))*100:.1f}%)")

    print(f"\n── 6. 最常用卡牌 Top-10 ──")
    for name, count in stats['cards_played'].most_common(10):
        print(f"  {name}: {count}")

    return results

def smoke_test():
    """冒烟测试: 5 批 × 100 场, 检查统计稳定性."""
    print("冒烟测试: 5 批 × 100 场")
    data = load_game_data()
    all_wins = []
    for batch in range(5):
        wins = Counter()
        for _ in range(100):
            result = simulate_battle(data)
            wins[result['winner']] += 1
        rate = wins.get('玩家', 0)
        all_wins.append(rate)
        print(f"  批次 {batch+1}: 玩家胜 {rate}%")
    print(f"  胜率范围: {min(all_wins)}-{max(all_wins)}%, 标准差: {statistics.stdev(all_wins):.1f}")

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    args = sys.argv[1:]
    verbose = '--verbose' in args or '-v' in args
    random_mode = '--random' in args or '-r' in args
    smoke = '--smoke' in args

    # 解析 --mc N=xxx or --mc N
    mc_n = 500
    for i, a in enumerate(args):
        if a == '--mc':
            if i + 1 < len(args):
                val = args[i + 1]
                # Handle N=xxx format
                if '=' in val:
                    mc_n = int(val.split('=')[1])
                else:
                    mc_n = int(val)
            break
        elif a.startswith('--mc='):
            mc_n = int(a.split('=')[1])
            break

    if smoke:
        smoke_test()
    elif verbose:
        # 单场详细模式
        data = load_game_data()
        print(f"\n{'='*60}")
        print("单场详细战斗日志 (verbose mode)")
        print(f"{'='*60}")
        result = simulate_battle(data, random_mode, verbose=True)
        print(f"\n{'='*60}")
        print(f"战斗结束: {result['winner']} 胜 ({result['turns']} 回合)")
        print(f"玩家: SAN={result['A_final']['san']:.0f} HP={result['A_final']['hp']:.0f} WP={result['A_final']['wp']} CPM={result['A_final']['cog']}")
        print(f"敌方: SAN={result['B_final']['san']:.0f} HP={result['B_final']['hp']:.0f} WP={result['B_final']['wp']} CPM={result['B_final']['cog']}")
    else:
        # 默认: 蒙特卡洛
        monte_carlo(N=mc_n, random_mode=random_mode)
