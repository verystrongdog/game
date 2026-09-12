#!/usr/bin/env python3
"""从 data/attitudes.json 生成 卡牌系统/态度效果速查表.md"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUT_PATH = Path(__file__).parent.parent.parent / "卡牌系统" / "态度效果速查表.md"

data = json.loads((DATA_DIR / "attitudes.json").read_text(encoding='utf-8'))

# 驱动顺序
DRIVE_ORDER = ['反射', '惩罚', '奖励', '道德', '文化', '价值', '照护']
# 情绪顺序 (按 valence_group)
EMO_GROUPS = {
    '正面': ['快乐', '爱', '希望', '平静'],
    '混合/中性': ['共情', '敬畏'],
    '负面': ['愤怒', '恐惧', '焦虑', '厌恶', '恐怖', '绝望', '内疚', '悲痛', '孤独'],
}

# ── 按驱动分组 ──
by_drive = defaultdict(list)
for att in data['attitudes']:
    drive = att['id'].split('+')[1]
    by_drive[drive].append(att)

lines = []
lines.append('# 态度效果速查表')
lines.append('')
lines.append('> 90 个态度的完整游戏效果数据。参数化生成 + 15 个特殊条目手工覆盖。数据源：`data/attitudes.json`。')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 目录')
lines.append('')
lines.append('1. [效果分类规则](#一效果分类规则)')
lines.append('2. [态度效果总表（按驱动）](#二态度效果总表按驱动)')
lines.append('3. [特殊条目详解](#三特殊条目详解)')
lines.append('4. [两类组合效果表](#四两类组合效果表)')
lines.append('5. [B(t) 碰撞公式](#五bt-碰撞公式)')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 一、效果分类规则')
lines.append('')
lines.append('| 类型 | B(t) 条件 | 游戏效果 | 典型 B(t) |')
lines.append('|------|----------|---------|-----------|')
lines.append('| **strike** (冲击型) | intensity > 0.5 | 对敌 SAN 伤害 | v 远离 0, i 高, a 任意 |')
lines.append('| **defend** (防御型) | valence < -0.3 | 自身减伤/闪避 | v 负, i > 0.3 |')
lines.append('| **bolster** (增益型) | valence > 0.3 | 回复 SAN/意志力/抽牌 | v 正, i < 0.7 |')
lines.append('| **control** (控制型) | autonomy > 0.3 | 揭示/标签/规则修改 | a 高, i 中 |')
lines.append('| **freeze** (冻结型) | intensity < 0.3 | 效果微弱/无输出 | i 极低 |')
lines.append('')
lines.append('**自伤规则：**')
lines.append('- `natural` → 无自伤（身体自然流动）')
lines.append('- `forced` → SAN 磨损 = C_control × 0.5，WP 消耗 = floor(C_control)')
lines.append('- `situational` → 文化不损，照护轻微自损 (0.3 SAN)')
lines.append('')
lines.append('> **伤害缩放**：DAMAGE_SCALE = 8.0，使态度效果与碰撞伤害量级相近。')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 二、态度效果总表（按驱动）')
lines.append('')

for drive in DRIVE_ORDER:
    entries = sorted(by_drive[drive], key=lambda a: EMO_GROUPS.get('正面',[]).index(a['emotion']) if a['emotion'] in EMO_GROUPS.get('正面',[]) else 99)

    lines.append(f'### {drive}驱动')
    lines.append('')
    lines.append('| # | 态度 | 叙事名 | 状态 | 类型 | 主效果 | 自伤 |')
    lines.append('|---|------|--------|------|------|--------|------|')

    for i, att in enumerate(entries, 1):
        ge = att.get('game_effect', {})
        etype = ge.get('effect_type', '?')
        primary = ge.get('primary', {})
        p_stat = primary.get('stat', '')
        p_amt = primary.get('amount', 0)
        flavor = ge.get('flavor', '-')
        self_cost = ge.get('self_cost', {})
        cost_str = ''
        if self_cost.get('san_wear'):
            cost_str += f'SAN-{self_cost["san_wear"]:.1f} '
        if self_cost.get('wp_cost'):
            cost_str += f'WP-{self_cost["wp_cost"]} '
        if self_cost.get('hp_cost_pct'):
            cost_str += f'HP-{self_cost["hp_cost_pct"]*100:.0f}%'
        if not cost_str:
            cost_str = '-'

        # 标记特殊条目
        name_display = f'**{att["narrative_name"]}**' if ge.get('special') else att['narrative_name']

        lines.append(f'| {i} | {att["emotion"]}+{drive} | {name_display} | {att["state"]} | {etype} | {flavor} | {cost_str} |')

    lines.append('')

lines.append('---')
lines.append('')
lines.append('## 三、特殊条目详解')
lines.append('')

special_entries = [a for a in data['attitudes'] if a.get('game_effect', {}).get('special')]
for att in special_entries:
    ge = att['game_effect']
    lines.append(f'### {att["narrative_name"]} — {att["id"]}')
    lines.append('')
    lines.append(f'> {ge["special"]}')
    lines.append('')
    lines.append(f'- **状态**：{att["state"]}（{att.get("state_desc", "")}）')
    lines.append(f'- **B(t)**：valence={att["behavior_output"]["valence"]:+.2f}, intensity={att["behavior_output"]["intensity"]:.2f}, autonomy={att["behavior_output"]["autonomy"]:+.2f}')
    lines.append(f'- **主效果**：{ge["flavor"]}')
    if ge.get('secondary', {}).get('stat'):
        lines.append(f'- **次效果**：{ge["secondary"].get("stat")} {ge["secondary"].get("amount", "")}')
    lines.append(f'- **自伤**：SAN磨损={ge["self_cost"]["san_wear"]}, WP={ge["self_cost"]["wp_cost"]}, HP%={ge["self_cost"]["hp_cost_pct"]}')
    lines.append(f'- **效果类型**：{ge["effect_type"]}')
    lines.append('')

lines.append('---')
lines.append('')
lines.append('## 四、两类组合效果表')
lines.append('')
lines.append('### 酝酿（认知+情绪）')
lines.append('')
lines.append('| 要素 | 值 |')
lines.append('|------|-----|')
lines.append('| AP 消耗 | 0（认知 0 + 情绪 0） |')
lines.append('| PAD 偏移 | 情绪卡正常偏移 |')
lines.append('| 产情绪卡 | 1 张（当前 PAD 最近锚点） |')
lines.append('| PAD 衰减 | 减半（δ × 0.5）— 情绪保留更久 |')
lines.append('| 酝酿加成 | 标记，下回合完整态度行为卡效果 +10% |')
lines.append('| 风险 | 连续酝酿 → PAD 累积 → 可能暴走 |')
lines.append('| 态度查找 | 不查（无行为卡，无驱动） |')
lines.append('')
lines.append('### 冲动（情绪+行为）')
lines.append('')
lines.append('| 要素 | 值 |')
lines.append('|------|-----|')
lines.append('| AP 消耗 | 行为卡 AP 照常 |')
lines.append('| 情绪偏移 | ×1.5（无认知框架缓冲） |')
lines.append('| 行为效果 | ×1.2（情绪直接灌入） |')
lines.append('| 可用驱动 | 反射✅ 惩罚✅ 文化✅ 照护⚠️ 奖励❌ 道德❌ 价值❌ |')
lines.append('| 一致性检测 | 情绪推力方向 vs 行为 valence：一致=无惩罚，不一致=效果×0.7 + AP+1 + SAN磨损+1 |')
lines.append('| 态度查找 | ✅ 情绪+行为 → 查 attitudes.json |')
lines.append('')
lines.append('### 执行（认知+行为）')
lines.append('')
lines.append('| 要素 | 值 |')
lines.append('|------|-----|')
lines.append('| AP 消耗 | 行为卡 AP 照常（cost_modifier 中 α 被压至 0.3，文化/照护不压制） |')
lines.append('| 认知效果 | ×1.3（无情绪干扰） |')
lines.append('| 意志力 | +1（同回合首次执行；二次=0；三次+=0） |')
lines.append('| 情感压制 | 标记，下回合情绪卡 PAD 偏移 × 0.5 |')
lines.append('| 态度查找 | ✅ 当前情绪+行为 → 查 attitudes.json |')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 五、B(t) 碰撞公式')
lines.append('')
lines.append('### 完整态度碰撞')
lines.append('')
lines.append('```')
lines.append('va, ia, aa = B(t)_A  (valence, intensity, autonomy)')
lines.append('vb, ib, ab = B(t)_B')
lines.append('')
lines.append('valence_diff  = va - vb      # 方向冲突度')
lines.append('intensity_sum = ia + ib      # 强度叠加')
lines.append('autonomy_diff = aa - ab      # 主动方优势')
lines.append('')
lines.append('# 态度共振：双方同向且差值 < 0.3')
lines.append('if sign(va)==sign(vb) and |valence_diff| < 0.3:')
lines.append('    heal = intensity_sum × 5.0 × 0.3')
lines.append('    → 双方各回复 heal SAN')
lines.append('')
lines.append('# 方向冲突')
lines.append('damage_to_B = intensity_sum × (1+|valence_diff|) × (1+max(0,autonomy_diff)) × 2.5')
lines.append('damage_to_A = intensity_sum × (1+|valence_diff|) × (1+max(0,-autonomy_diff)) × 2.5')
lines.append('```')
lines.append('')
lines.append('### 两类组合碰撞')
lines.append('')
lines.append('两类组合（酝酿/冲动/执行）也参与碰撞。碰撞时取最近一次完整态度或两类组合的 B(t)。')
lines.append('若双方本回合均未形成态度，fallback 到原始 PAD 构造 B(t) = (V, |A|, D)。')
lines.append('')
lines.append('---')
lines.append('')
lines.append('*生成: 2026-07-10 | 数据源: data/attitudes.json*')
lines.append('*关联: [卡牌组合逻辑](%E5%8D%A1%E7%89%8C%E7%BB%84%E5%90%88%E9%80%BB%E8%BE%91.md), [态度系统](../态度系统/态度系统.md), [attitudes.json](../../data/attitudes.json)*')

OUT_PATH.write_text('\n'.join(lines), encoding='utf-8')
print(f'✓ 写入 {OUT_PATH}')
print(f'  总条目: {len(data["attitudes"])}')
print(f'  特殊条目: {len(special_entries)}')
