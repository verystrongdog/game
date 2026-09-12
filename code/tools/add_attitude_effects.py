#!/usr/bin/env python3
"""为 attitudes.json 中 90 个态度条目添加 game_effect 字段。

效果从 B(t) 参数化推导，不手写 90 个效果。特殊条目手工覆盖。

效果分类 (5 类):
  strike  — 冲击型: intensity>0.5, 对敌造成 SAN 伤害
  defend  — 防御型: valence<-0.3, 自身获得闪避/护盾/减伤
  bolster — 增益型: valence>0.3, 自身回复 SAN/意志力/抽牌
  control — 控制型: autonomy>0.3, 揭示/标签/规则修改
  freeze  — 冻结型: intensity<0.3, 效果微弱

自伤规则:
  natural      → 无自伤
  forced       → SAN磨损=C_control×0.5, WP消耗=floor(C_control)
  situational  → 文化不损, 照护轻微自损 (0.3 SAN)

伤害缩放:
  DAMAGE_SCALE = 8.0 (使态度效果与现有碰撞伤害量级相近)
"""

import json, math
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DAMAGE_SCALE = 8.0

# ── C_control 表 (来自 sim_battle_v4.py) ──
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

# ── 驱动 ID 映射 ──
DRIVE_NAME_TO_ID = {
    '反射': 'reflex', '惩罚': 'punish', '奖励': 'reward',
    '道德': 'moral', '文化': 'culture', '价值': 'value', '照护': 'care',
}


def classify_effect(b, state, emotion, drive_name):
    """从 B(t) 和 state 分类效果类型。"""
    v, i, a = b['valence'], b['intensity'], b['autonomy']

    # 冻结型: 极低强度
    if i < 0.3:
        return 'freeze'

    # 冲击型: 高强度
    if i > 0.5 and abs(v) > 0.1:
        return 'strike'

    # 防御型: 负 valence
    if v < -0.3:
        return 'defend'

    # 增益型: 正 valence
    if v > 0.3:
        return 'bolster'

    # 控制型: 高 autonomy
    if a > 0.3:
        return 'control'

    # 默认
    if i > 0.5:
        return 'strike'
    elif v < 0:
        return 'defend'
    else:
        return 'bolster'


def compute_effect(att, drive_name):
    """从态度数据计算 game_effect。"""
    b = att['behavior_output']
    state = att['state']
    emotion = att['emotion']
    drive_id = DRIVE_NAME_TO_ID.get(drive_name, '')

    etype = classify_effect(b, state, emotion, drive_name)
    v, i, a = b['valence'], b['intensity'], b['autonomy']

    # ── 主效果量级 ──
    base_power = abs(v) * i * DAMAGE_SCALE

    # autonomy 调整: 高主动→高效果, 被动→低效果
    autonomy_bonus = 1.0 + max(0, a) * 0.5

    # ── C_control ──
    c_ctrl_row = C_CONTROL_TABLE.get(emotion, {})
    c_ctrl = c_ctrl_row.get(drive_id)
    if c_ctrl is None:
        c_ctrl = 0.0

    # ── 自伤 ──
    self_cost = {'san_wear': 0.0, 'wp_cost': 0, 'hp_cost_pct': 0.0}
    if state == 'forced':
        self_cost['san_wear'] = round(c_ctrl * 0.5, 1)
        self_cost['wp_cost'] = int(math.floor(c_ctrl))
    elif state == 'situational':
        if drive_name == '照护':
            self_cost['san_wear'] = 0.3  # 轻微自损
        # 文化不损

    # ── 构建效果 ──
    effect = {
        'effect_type': etype,
        'target': 'enemy' if etype == 'strike' else ('self' if etype in ('defend', 'bolster') else 'enemy'),
        'primary': {},
        'secondary': {},
        'self_cost': self_cost,
        'special': None,
        'flavor': '',
    }

    if etype == 'strike':
        amount = max(1, round(base_power * autonomy_bonus))
        effect['primary'] = {'stat': 'san_damage', 'amount': amount, 'scale_with': 'intensity'}
        effect['flavor'] = f'心灵震慑 {amount} 点'
    elif etype == 'defend':
        effect['target'] = 'self'
        # 防御量与 intensity 成正比
        defense_pct = min(0.5, i * 0.5)
        effect['primary'] = {'stat': 'damage_reduce', 'amount': round(defense_pct, 2), 'duration': 2}
        effect['flavor'] = f'减伤 {defense_pct:.0%} (2回合)'
    elif etype == 'bolster':
        effect['target'] = 'self'
        if v > 0.5:
            effect['primary'] = {'stat': 'san_restore', 'amount': max(1, round(i * 2))}
            effect['flavor'] = f'回复 SAN {effect["primary"]["amount"]} 点'
        elif a > 0.2:
            effect['primary'] = {'stat': 'willpower', 'amount': 1}
            effect['flavor'] = '意志力 +1'
        else:
            effect['primary'] = {'stat': 'draw', 'amount': 1}
            effect['flavor'] = '抽牌 +1'
    elif etype == 'control':
        effect['primary'] = {'stat': 'reveal_or_tag', 'amount': 1}
        effect['flavor'] = '揭示/标签 1 个属性'
    elif etype == 'freeze':
        effect['target'] = 'self'
        effect['primary'] = {'stat': 'none', 'amount': 0}
        effect['flavor'] = '态度冻结——行为输出过低，无实质效果'

    return effect


# ── 特殊条目手工覆盖 ──
SPECIAL_OVERRIDES = {
    "恐惧+价值": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 8, "scale_with": "intensity"},
        "secondary": {"stat": "willpower", "amount": 1},
        "self_cost": {"san_wear": 1.9, "wp_cost": 3, "hp_cost_pct": 0.0},
        "special": "逆流而上——全游戏最贵硬解锁(C=3.8)。恐惧中坚守价值: 巨额心灵震慑 + 回收1意志力。",
        "flavor": "心灵震慑 8 点 + 意志力 +1",
    },
    "愤怒+价值": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 6, "scale_with": "intensity"},
        "secondary": {"stat": "remove_defense", "amount": 1},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "奋起——C_control=0，愤怒时价值驱动免费用。无视敌方1个防御效果。",
        "flavor": "心灵震慑 6 点 + 驱散1个敌方防御",
    },
    "爱+价值": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 5, "scale_with": "intensity"},
        "secondary": {"stat": "protect_ally", "amount": 1},
        "self_cost": {"san_wear": 0.5, "wp_cost": 0, "hp_cost_pct": 0.10},
        "special": "献身——为所爱之人承受。自身HP-10%, 同时保护1个队友本回合不受伤害。C_control=0 (爱让价值驱动自然流动)。",
        "flavor": "心灵震慑 5 点 + 保护队友 + 自身HP-10%",
    },
    "悲痛+照护": {
        "effect_type": "defend",
        "target": "ally",
        "primary": {"stat": "shared_calm", "amount": 0.3, "scale_with": "intensity"},
        "secondary": {"stat": "san_restore", "amount": 1},
        "self_cost": {"san_wear": 0.3, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "共悲——两个人扛。降低双方|A| 0.3, 双方各回复1 SAN。悲痛中的照护不是救对方, 是陪对方。",
        "flavor": "双方唤醒-0.3 + 各回复SAN 1",
    },
    "敬畏+文化": {
        "effect_type": "bolster",
        "target": "self",
        "primary": {"stat": "ritual_boost", "amount": 2.0, "scale_with": "intensity"},
        "secondary": {"stat": "san_restore", "amount": 2},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "虔敬——仪式效果翻倍(×2.0)。在宏大存在面前, 文化脚本获得了额外的重量。",
        "flavor": "本场仪式效果翻倍 + 回复SAN 2",
    },
    "愤怒+道德": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 4, "scale_with": "intensity"},
        "secondary": {"stat": "moral_intimidate", "amount": 1},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "义愤——愤怒时道德驱动免费(C=0)。额外: 敌方下回合道德驱动φ推迟1回合。",
        "flavor": "心灵震慑 4 点 + 敌方道德驱动推迟",
    },
    "恐惧+反射": {
        "effect_type": "defend",
        "target": "self",
        "primary": {"stat": "dodge", "amount": 1, "duration": 1},
        "secondary": {"stat": "control_loss", "amount": 0.2},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "溃逃——获得闪避但D轴降低0.2。身体替你做了决定, 控制感流失。",
        "flavor": "闪避1回合 + D轴-0.2",
    },
    "绝望+价值": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 6, "scale_with": "hp_lost"},
        "secondary": {"stat": "ignore_defense", "amount": 1},
        "self_cost": {"san_wear": 1.0, "wp_cost": 2, "hp_cost_pct": 0.0},
        "special": "背水——己方已损失HP比例越高伤害越大。无视敌方常规防御。绝望中唯一的出路。",
        "flavor": "心灵震慑(随已损HP增长) + 无视防御",
    },
    "共情+照护": {
        "effect_type": "bolster",
        "target": "ally",
        "primary": {"stat": "calm_and_heal", "amount": 0.3, "scale_with": "intensity"},
        "secondary": {"stat": "san_restore", "amount": 2},
        "self_cost": {"san_wear": 0.3, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "抚慰——降低目标|A| 0.3 +回复SAN 2。共情先传递再照护: 你理解她的痛苦, 所以你的安抚是真实的。",
        "flavor": "目标唤醒-0.3 + 回复SAN 2",
    },
    "内疚+道德": {
        "effect_type": "bolster",
        "target": "self",
        "primary": {"stat": "willpower", "amount": 2},
        "secondary": {"stat": "moral_activation", "amount": 0.3},
        "self_cost": {"san_wear": 0.5, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "赎罪——意志力+2, 道德驱动激活度+0.3。内疚短路激活道德: 不需要规范性评估。",
        "flavor": "意志力+2 + 道德驱动激活+0.3",
    },
    "孤独+价值": {
        "effect_type": "control",
        "target": "self",
        "primary": {"stat": "self_redefinition", "amount": 1},
        "secondary": {"stat": "willpower", "amount": 1},
        "self_cost": {"san_wear": 0.8, "wp_cost": 1, "hp_cost_pct": 0.0},
        "special": "独行——重新定义自身1个标签(移除负面/添加新标签)。孤独让价值驱动不是因为有人在看, 而是因为自己相信。",
        "flavor": "重新定义自身1个标签 + 意志力+1",
    },
    "厌恶+价值": {
        "effect_type": "strike",
        "target": "enemy",
        "primary": {"stat": "san_damage", "amount": 5, "scale_with": "intensity"},
        "secondary": {"stat": "purge_illusion", "amount": 1},
        "self_cost": {"san_wear": 1.0, "wp_cost": 2, "hp_cost_pct": 0.0},
        "special": "净除——额外移除敌方1个观察者效应幻象。厌恶的'要清除而非避开'在价值驱动下获得正当性。",
        "flavor": "心灵震慑 5 点 + 移除敌方1个幻象",
    },
    # 爱系列: 低唤醒 ≠ 无效果, 爱是温柔持久的 buff
    "爱+奖励": {
        "effect_type": "bolster",
        "target": "self",
        "primary": {"stat": "persistent_heal", "amount": 1, "duration": 3},
        "secondary": {"stat": "willpower", "amount": 1},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "沉浸——持续3回合每回合回复1 SAN + 意志力+1。爱的奖励不是爆发, 是持续滋养。",
        "flavor": "持续3回合回复SAN 1/回合 + 意志力+1",
    },
    "爱+道德": {
        "effect_type": "bolster",
        "target": "ally",
        "primary": {"stat": "grant_tenacity", "amount": 2, "duration": 3},
        "secondary": {"stat": "san_restore", "amount": 1},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "忠诚——给队友'韧性'2层(持续3回合) + 回复1 SAN。爱中的道德: 不是因为应该, 是因为在乎。",
        "flavor": "队友韧性+2层(3回合) + 回复SAN 1",
    },
    "爱+文化": {
        "effect_type": "bolster",
        "target": "ally",
        "primary": {"stat": "bond_strengthen", "amount": 0.2},
        "secondary": {"stat": "draw", "amount": 1},
        "self_cost": {"san_wear": 0.0, "wp_cost": 0, "hp_cost_pct": 0.0},
        "special": "依礼——强化与目标的Attachment_strength +0.2 + 抽牌+1。文化赋予了爱的表达形式。",
        "flavor": "情感纽带+0.2 + 抽牌+1",
    },
}


def main():
    path = DATA_DIR / "attitudes.json"
    data = json.loads(path.read_text(encoding='utf-8'))

    # ── 为每个条目计算效果 ──
    for att in data["attitudes"]:
        att_id = att["id"]
        drive_name = att_id.split("+")[1]

        if att_id in SPECIAL_OVERRIDES:
            att["game_effect"] = SPECIAL_OVERRIDES[att_id]
        else:
            att["game_effect"] = compute_effect(att, drive_name)

    # ── 统计 ──
    type_counts = {}
    for att in data["attitudes"]:
        etype = att["game_effect"]["effect_type"]
        type_counts[etype] = type_counts.get(etype, 0) + 1
    print(f"效果分布: {type_counts}")
    print(f"特殊覆盖: {len(SPECIAL_OVERRIDES)} 条目")

    # ── 写入 ──
    backup_path = path.with_suffix(".json.bak2")
    path.rename(backup_path)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"✓ 写入 {path}")

    # ── 预览特殊条目 ──
    print("\n── 特殊条目效果预览 ──")
    for att in data["attitudes"]:
        if att["id"] in SPECIAL_OVERRIDES:
            eff = att["game_effect"]
            print(f"  {att['narrative_name']} ({att['id']}, {att['state']}): {eff['flavor']}")

    # ── 预览各类效果的代表条目 ──
    print("\n── 各类效果代表条目 ──")
    shown = set()
    for etype in ['strike', 'defend', 'bolster', 'control', 'freeze']:
        for att in data["attitudes"]:
            if att["game_effect"]["effect_type"] == etype and etype not in shown:
                eff = att["game_effect"]
                print(f"  [{etype}] {att['narrative_name']} ({att['id']}): {eff['flavor']} | 自伤: {eff['self_cost']}")
                shown.add(etype)
                break


if __name__ == '__main__':
    main()
