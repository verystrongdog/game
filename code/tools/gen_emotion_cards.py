#!/usr/bin/env python3
"""从 data/emotions.json + 情绪卡模板 生成 data/emotion_cards.json。

用法: python3 tools/gen_emotion_cards.py
来源: 卡牌系统/情绪卡模板.md, data/emotions.json
"""

import json
import sys
from pathlib import Path

KAPPA_BASE = 0.30  # PAD 偏移基础系数

# ── 每张情绪卡的创意内容 (flavor text) ──
# 格式: { 锚点ID: { play_desc, hand_desc, residual_tendency, residual_dir,
#                    trigger, count_formula, sources, rarity,
#                    boosts, conflicts, design_note } }

CREATIVE = {
    "fear": {
        "play_desc": "强烈恐惧爆发——心跳骤停，世界收窄为一条逃生通道。",
        "hand_desc": "轻度恐惧压力——你总觉得有什么在暗处。",
        "residual_tendency": "惊觉倾向 ↑",
        "residual_dir": "negative",
        "trigger": "角色认知到危险时自动塞入手牌（CPM Step 1 Novelty 检测到威胁信号）",
        "count": "1 + floor(恐慌程度 / 3)，恐慌程度 = 威胁强度 × (1 - D_current)",
        "sources": ["态度产", "NPC 塞", "环境产"],
        "rarity": "common",
        "boosts": ["逃跑", "僵住", "闪避", "回避"],
        "conflicts": ["追求", "坚持", "牺牲", "突破"],
        "design_note": (
            "恐惧卡的价值在于它在正确时机被'转化'而非单纯打出。"
            "拥有恐惧卡的人不一定输——知道如何面对恐惧的人可能反败为胜。"
            "恐惧 + 愤怒 D 轴互相抵消 → 行为'对峙'（想逃又想打，僵住了）。"
        ),
    },
    "anger": {
        "play_desc": "怒火喷涌——血液冲上头顶，所有选项收窄为一个：向前。",
        "hand_desc": "隐隐躁动——你比平时更容易被小事点燃。",
        "residual_tendency": "易怒倾向 ↑",
        "residual_dir": "negative",
        "trigger": "角色遭受不公/挫败/挑衅时自动塞入手牌",
        "count": "1 + floor(不公强度 / 3)，不公强度 = 期望落差 × (1 - D_current)",
        "sources": ["态度产", "NPC 塞", "环境产"],
        "rarity": "common",
        "boosts": ["对峙", "反击", "破坏", "质问"],
        "conflicts": ["安抚", "妥协", "回避", "退缩"],
        "design_note": (
            "愤怒是唯一主动靠近威胁源的情绪（P<0 但 D>0）。"
            "穿上铠甲的恐惧——愤怒掩盖了恐惧，但恐惧仍在铠甲下面。"
            "愤怒 + 恐惧 D 轴抵消 → 僵住状态。"
        ),
    },
    "guilt": {
        "play_desc": "内疚如潮水涌来——你无法停止回想那个瞬间，如果当初……",
        "hand_desc": "若有若无的不安——有什么事情还没了结。",
        "residual_tendency": "自责倾向 ↑",
        "residual_dir": "negative",
        "trigger": "角色违反自身道德标准时自动塞入手牌（CPM Normative 检测到行为与 Internal Standards 不符）",
        "count": "1 + floor(违反程度 / 2)，违反程度 = 行为与 Internal Standards 差距",
        "sources": ["态度产", "NPC 塞"],
        "rarity": "uncommon",
        "boosts": ["道歉", "弥补", "忏悔", "自省"],
        "conflicts": ["逃避", "否认", "推卸", "攻击"],
        "design_note": (
            "内疚是道德情绪的典型——内疚耦合直接短路激活道德驱动。"
            "一颗鞋子里的石头：不大，但每一步都疼。"
            "内疚 + 共情 → 修复行为驱动力极强。"
        ),
    },
    "anxiety": {
        "play_desc": "焦虑蔓延——所有可能性中最坏的那一个被无限放大。",
        "hand_desc": "隐约不安——对未来的模糊担忧，说不清但挥之不去。",
        "residual_tendency": "焦虑基线 ↑",
        "residual_dir": "negative",
        "trigger": "未来不确定性高 + 控制感低时自动塞入手牌（CPM Implications 检测到 Outcome Probability 低且 Discrepancy 高）",
        "count": "1 + floor(不确定度 / 3)，不确定度 = 后果离散度 × (1 - D_current - Control_signal)",
        "sources": ["态度产", "环境产", "NPC 塞"],
        "rarity": "common",
        "boosts": ["规避", "准备", "确认", "检查"],
        "conflicts": ["冒险", "放手", "信任", "乐观行动"],
        "design_note": (
            "焦虑 ≈ 恐惧的 PAD 坐标（最近邻居，距离 0.18），区别在于 D 稍高。"
            "焦虑没有恐惧的'具体对象'——它是对未来的恐惧。"
            "焦虑卡连续手牌压力累积 → 可能触发广泛性焦虑状态。"
        ),
    },
    "sorrow": {
        "play_desc": "悲痛袭来——看不见的伤口裂开，世界褪色。",
        "hand_desc": "沉重感——做什么都需要额外的力气。",
        "residual_tendency": "愉悦基线 ↓",
        "residual_dir": "negative",
        "trigger": "角色经历丧失/分离时自动塞入手牌",
        "count": "取决于丧失强度，1-3 张",
        "sources": ["态度产", "环境产", "NPC 塞", "共情传递"],
        "rarity": "uncommon",
        "boosts": ["哀悼", "独处", "回忆", "放下"],
        "conflicts": ["庆祝", "社交", "进取", "享乐"],
        "design_note": (
            "悲痛是唯一 -P-A-D（Octant 8）的情绪——所有驱动激活不足，'动不了'。"
            "悲痛的行为冻结是真实的生理反应——不是玩家'不想动'，是'动不了'。"
            "悲痛 + 共情 → 共享悲痛可降低强度（两个人扛）。"
        ),
    },
    "empathy": {
        "play_desc": "你感受到对方的感受——那情绪穿过你的边界，仿佛是你自己的。",
        "hand_desc": "共情开放状态——你比平时更容易接收他人的情绪信号。",
        "residual_tendency": "共情敏感度 ↑",
        "residual_dir": "neutral",
        "trigger": "角色注意到他人情绪表达时自动塞入手牌",
        "count": "1-2 张，取决于 Attachment_strength",
        "sources": ["态度产", "环境产", "共情传递"],
        "rarity": "uncommon",
        "boosts": ["倾听", "陪伴", "安抚", "理解"],
        "conflicts": ["漠视", "攻击", "利用", "欺骗"],
        "design_note": (
            "共情的推力接近零——它本身不给行为方向，传递的是被共情情绪的方向。"
            "可传递其他情绪——共情是你感受世界的窗口。"
            "共情需要知觉与注意(注意到他人) + 知识表征(归为需要帮助) → 照护门控条件。"
        ),
    },
    "joy": {
        "play_desc": "快乐绽放——一瞬间，世界变得明亮而广阔。",
        "hand_desc": "轻松愉悦——嘴角不自觉地上扬。",
        "residual_tendency": "愉悦基线 ↑",
        "residual_dir": "positive",
        "trigger": "角色达成目标/体验正面事件时自动塞入手牌",
        "count": "1-2 张，取决于事件正面程度",
        "sources": ["态度产", "环境产", "初始牌库"],
        "rarity": "common",
        "boosts": ["探索", "分享", "创造", "庆祝"],
        "conflicts": ["破坏", "回避", "退缩"],
        "design_note": (
            "快乐的注意拓宽 + 风险低估效果是双刃剑——发现更多，但错过威胁。"
            "快乐是治疗的目标象限之一——但不是唯一目标。真正的心理健康是完整的情绪谱系。"
            "快乐 + 认知卡 → 注意拓宽使 criterion 临时降低。"
        ),
    },
    "love": {
        "play_desc": "爱意涌动——你清楚为什么而站在这里。",
        "hand_desc": "温暖的情感觉知——有什么值得你留下。",
        "residual_tendency": "依恋安全感 ↑",
        "residual_dir": "positive",
        "trigger": "角色对依恋对象的存在/行为产生回应时自动塞入手牌",
        "count": "1 + floor(Attachment_strength / 2)",
        "sources": ["态度产", "NPC 塞", "初始牌库"],
        "rarity": "uncommon",
        "boosts": ["守护", "陪伴", "付出", "原谅"],
        "conflicts": ["背叛", "抛弃", "漠视"],
        "design_note": (
            "爱是唯一可主动选择对自身不利选项的正向情绪——愿意为对象承担损失。"
            "爱的低唤醒 + 中等控制 → '我知道我在乎什么'。"
            "爱 + 价值驱动 → 信念的终极燃料。C_control(爱+价值)=0——信念自然流动。"
        ),
    },
    "disgust": {
        "play_desc": "厌恶翻涌——这东西不应该存在于世界上。",
        "hand_desc": "隐约排斥——某种挥之不去的'不对劲'。",
        "residual_tendency": "排斥敏感度 ↑",
        "residual_dir": "negative",
        "trigger": "角色感知到污染/道德违规/存在性污染时自动塞入手牌",
        "count": "1-2 张，取决于污染强度",
        "sources": ["态度产", "环境产", "NPC 塞"],
        "rarity": "common",
        "boosts": ["清除", "远离", "净化", "拒绝"],
        "conflicts": ["接纳", "靠近", "理解", "包容"],
        "design_note": (
            "厌恶是'清除而非避开'——要消灭对象，不只是逃跑。"
            "厌恶 + 道德驱动 → 可能触发'替天行道'路径（价值驱动硬解锁成本降低）。"
            "厌恶 + 文化习俗 → 社会排斥行为的双重强化。"
        ),
    },
    "awe": {
        "play_desc": "敬畏降临——你被某种远超自身理解的存在压得说不出话。",
        "hand_desc": "渺小感——你的烦恼突然显得微不足道。",
        "residual_tendency": "超越体验开放性 ↑",
        "residual_dir": "positive",
        "trigger": "角色遭遇远超自身尺度的存在/现象时自动塞入手牌",
        "count": "1 张（稀有触发）",
        "sources": ["环境产", "态度产"],
        "rarity": "rare",
        "boosts": ["静默", "凝视", "接纳", "顿悟"],
        "conflicts": ["攻击", "喧哗", "漠视"],
        "design_note": (
            "敬畏是 NRC 中最稀有的情绪（仅 26 词）。"
            "P≈0 但 A>0 D<0——'我醒着，但我控制不了'。"
            "敬畏是通往顿悟/超越体验的窗口——月光下，敬畏可能触发观察者效应事件。"
        ),
    },
    "terror": {
        "play_desc": "恐怖撕裂心智——你见证的不可名状之物动摇了存在的根基。",
        "hand_desc": "战栗的余波——你的手还在抖。",
        "residual_tendency": "惊骇阈值 ↓",
        "residual_dir": "negative",
        "trigger": "角色直面不可名状之物/观察者效应现象时自动塞入手牌",
        "count": "1-3 张，取决于不可名状程度",
        "sources": ["环境产", "NPC 塞"],
        "rarity": "rare",
        "boosts": ["逃跑", "僵住", "尖叫", "崩溃"],
        "conflicts": ["面对", "理解", "靠近", "坚持"],
        "design_note": (
            "恐怖区别于恐惧——D 轴更高（-0.124 vs -0.414），控制感更多。"
            "恐惧是被追 → 恐怖是看见了不该看的东西。"
            "恐怖 + 观察者效应 → 月光下，你相信的恐怖是真的。"
        ),
    },
    "despair": {
        "play_desc": "绝望蔓延——没有出口。所有路径通向同一堵墙。",
        "hand_desc": "认知闭合——你不再寻找新的可能性。",
        "residual_tendency": "希望基线 ↓",
        "residual_dir": "negative",
        "trigger": "角色连续失败/丧失所有控制路径时自动塞入手牌（CPM Coping 检测到 Control=0 且 Power=0）",
        "count": "1-3 张",
        "sources": ["态度产", "环境产"],
        "rarity": "uncommon",
        "boosts": ["放弃", "屈服", "自毁", "冻结"],
        "conflicts": ["坚持", "尝试", "探索", "希望行动"],
        "design_note": (
            "绝望 = D 轴最低（-0.510）——彻底的失控。"
            "认知闭合是绝望的核心特征：不再搜索新信息。所有认知卡效果 × 0.5。"
            "绝望是游戏中最大的危机——不是因为伤害高，是因为你不再看到出路。"
        ),
    },
    "hope": {
        "play_desc": "希望浮现——你不知道会好起来，但你亲眼见过午夜之后的黎明。",
        "hand_desc": "安静的期待——不需要大声，不需要证据。",
        "residual_tendency": "希望基线 ↑",
        "residual_dir": "positive",
        "trigger": "角色成功克服困难/获得新信息揭示正面可能性时自动塞入手牌",
        "count": "1-2 张",
        "sources": ["态度产", "环境产"],
        "rarity": "uncommon",
        "boosts": ["坚持", "尝试", "相信", "等待"],
        "conflicts": ["放弃", "屈服", "自毁"],
        "design_note": (
            "希望是低唤醒 + 高控制（+P-A+D）——'我知道会好起来'。"
            "希望不需要证据——它本身就是对抗绝望的武器。"
            "希望 + 价值驱动 → 降低 θ_play（从 0.50 降至 0.35），让'坚持'变得更容易。"
        ),
    },
    "calm": {
        "play_desc": "平静安住——你不需要去任何地方，不需要变成任何人。",
        "hand_desc": "安宁的低语——呼吸变深了。",
        "residual_tendency": "宁静基线 ↑",
        "residual_dir": "positive",
        "trigger": "角色处于安全环境/完成冥想/成功处理情绪后自动塞入手牌",
        "count": "1 张",
        "sources": ["环境产", "态度产", "初始牌库"],
        "rarity": "uncommon",
        "boosts": ["冥想", "休息", "观察", "接纳"],
        "conflicts": ["冲动", "攻击", "冒险"],
        "design_note": (
            "平静是 +P-A-D——愉悦但低唤醒、低控制。'舒服地不动'。"
            "治疗目标象限——最低唤醒的安宁状态。"
            "平静 + 认知卡 → criterion 回归中性（抵消情绪偏向），是最佳认知状态。"
        ),
    },
    "loneliness": {
        "play_desc": "孤独如墙——你站在透明的屏障后面，世界在另一边继续。",
        "hand_desc": "若有若无的空洞——即使在人海中也不消散。",
        "residual_tendency": "社交回避 ↑",
        "residual_dir": "negative",
        "trigger": "角色长时间缺乏社交连接/Attachment 信号为零时自动塞入手牌",
        "count": "1 + floor(隔离回合数 / 5)",
        "sources": ["环境产", "态度产"],
        "rarity": "uncommon",
        "boosts": ["独处", "内省", "写作", "创造"],
        "conflicts": ["社交", "求助", "信任"],
        "design_note": (
            "孤独 ≠ 悲痛（丧失 vs 隔离）。孤独不一定痛苦——它可以催生深刻的创造。"
            "孤独 + 表象与语言 → d' 提升（少了社交噪音），但 criterion 偏向悲观。"
            "孤独是最难被'治愈'的情绪——因为它需要的不只是时间，而是真正被看见。"
        ),
    },
}


def build_emotion_cards(emotions_json_path: str) -> list[dict]:
    """从 emotions.json 构建情绪卡列表。"""
    with open(emotions_json_path, "r", encoding="utf-8") as f:
        src = json.load(f)

    emotions = src["emotions"]  # list of dict
    cards = []

    for emo in emotions:
        eid = emo["id"]
        name = emo["name"]
        pad = emo["pad"]
        thrust = emo["behavior_thrust"]
        activates = emo["activates_drives"]
        intensity = thrust.get("intensity", "moderate")

        # PAD 偏移 = κ_base × PAD_card
        dV = round(KAPPA_BASE * pad["V"], 3)
        dA = round(KAPPA_BASE * pad["A"], 3)
        dD = round(KAPPA_BASE * pad["D"], 3)

        # 手牌压力 ≈ 打出偏移的 1/5
        hpV = round(dV / 5, 3)
        hpA = round(dA / 5, 3)
        hpD = round(dD / 5, 3)

        # 残留量: 低强度=0.01, 中强度=0.02, 高强度=0.03
        residual_amount_map = {"low": 0.01, "moderate": 0.02, "high": 0.03}
        residual_amount = residual_amount_map.get(intensity, 0.02)

        # 压力累积上限: 高强度=5, 中强度=4, 低强度=3
        max_accum_map = {"low": 3, "moderate": 4, "high": 5}
        max_accum = max_accum_map.get(intensity, 4)

        # 获取创意内容
        cr = CREATIVE.get(eid, {})
        play_desc = cr.get("play_desc", f"{name}情绪爆发。")
        hand_desc = cr.get("hand_desc", f"{name}的轻微压力。")
        residual_tendency = cr.get("residual_tendency", f"{name}倾向 ↑")
        residual_dir = cr.get("residual_dir", "neutral")
        trigger = cr.get("trigger", f"角色遭遇与{name}相关的刺激时自动塞入手牌")
        count_formula = cr.get("count", "1 张")
        sources = cr.get("sources", ["态度产"])
        rarity = cr.get("rarity", "common")
        boosts = cr.get("boosts", [])
        conflicts = cr.get("conflicts", [])
        design_note = cr.get("design_note", "")

        # 共情特殊：传递情绪列表
        transfer = []
        if eid == "empathy":
            # 共情可传递所有情绪（除自身）
            transfer = [e["name"] for e in emotions if e["id"] != "empathy"]

        card = {
            "id": eid,
            "name": name,
            "type": "情绪",
            "valence_group": emo.get("valence_group", "mixed"),
            "octant": emo.get("octant", ""),
            "pad": {
                "V": pad["V"],
                "A": pad["A"],
                "D": pad["D"],
            },
            "ap_cost": 0,
            "tags": ["暂时性卡牌（战终消失）"],
            # ── 打出效果 ──
            "play_effect": {
                "pad_offset": {"dV": dV, "dA": dA, "dD": dD},
                "description": play_desc,
                "behavior_thrust": {
                    "direction": thrust["direction"],
                    "intensity": intensity,
                    "autonomy": thrust.get("autonomy", "passive"),
                },
            },
            # ── 留在手牌 ──
            "hand_pressure": {
                "pad": {"dV": hpV, "dA": hpA, "dD": hpD},
                "description": hand_desc,
                "accumulates": True,
                "max_accumulation": max_accum,
            },
            # ── 战末残留 ──
            "residual": {
                "tendency": residual_tendency,
                "amount": residual_amount,
                "direction": residual_dir,
            },
            # ── 获得条件 ──
            "acquisition": {
                "sources": sources,
                "natural_trigger": trigger,
                "count": count_formula,
                "rarity": rarity,
            },
            # ── 联动 ──
            "linkages": {
                "activates_drives": activates,
                "boosts_behaviors": boosts,
                "conflicts_with_behaviors": conflicts,
                "transfer_emotions": transfer,
                "mood_coupled": True,
            },
            "design_note": design_note,
        }
        cards.append(card)

    return cards


def validate_cards(cards: list[dict], emotions_json_path: str) -> list[str]:
    """验证情绪卡数据，返回错误列表。"""
    errors = []

    with open(emotions_json_path, "r", encoding="utf-8") as f:
        src = json.load(f)
    src_emos = {e["id"]: e for e in src["emotions"]}

    for i, card in enumerate(cards):
        eid = card["id"]
        name = card["name"]
        prefix = f"[{name}] "

        # 1. PAD 坐标与 emotions.json 一致
        if eid in src_emos:
            src_pad = src_emos[eid]["pad"]
            for dim in ["V", "A", "D"]:
                if abs(card["pad"][dim] - src_pad[dim]) > 0.001:
                    errors.append(
                        f"{prefix}PAD.{dim} ({card['pad'][dim]}) 与 emotions.json ({src_pad[dim]}) 不一致"
                    )

        # 2. 打出 PAD 偏移 |Δ| ≤ 0.3
        po = card["play_effect"]["pad_offset"]
        for dim in ["dV", "dA", "dD"]:
            if abs(po[dim]) > 0.3 + 0.001:
                errors.append(f"{prefix}打出偏移 {dim}={po[dim]} 超出 ±0.3")

        # 3. 残留量 ∈ [0.01, 0.05]
        ra = card["residual"]["amount"]
        if ra < 0.009 or ra > 0.051:
            errors.append(f"{prefix}残留量 {ra} 不在 [0.01, 0.05] 范围内")

        # 4. 必填字段非空
        required_str_fields = [
            ("name", card["name"]),
            ("play_effect.description", card["play_effect"]["description"]),
            ("hand_pressure.description", card["hand_pressure"]["description"]),
            ("residual.tendency", card["residual"]["tendency"]),
            ("acquisition.natural_trigger", card["acquisition"]["natural_trigger"]),
            ("acquisition.count", card["acquisition"]["count"]),
            ("design_note", card["design_note"]),
        ]
        for fname, val in required_str_fields:
            if not val or not val.strip():
                errors.append(f"{prefix}必填字段 '{fname}' 为空")

        # 5. activates_drives 与 emotions.json 一致
        if eid in src_emos:
            src_ad = src_emos[eid].get("activates_drives", [])
            card_ad = card["linkages"]["activates_drives"]
            if sorted(src_ad) != sorted(card_ad):
                errors.append(
                    f"{prefix}activates_drives ({card_ad}) 与 emotions.json ({src_ad}) 不一致"
                )

        # 6. behavior_thrust 与 emotions.json 一致
        if eid in src_emos:
            src_bt = src_emos[eid]["behavior_thrust"]
            card_bt = card["play_effect"]["behavior_thrust"]
            if src_bt["direction"] != card_bt["direction"]:
                errors.append(
                    f"{prefix}行为推力方向 ({card_bt['direction']}) 与 emotions.json ({src_bt['direction']}) 不一致"
                )

    # 7. 卡数量 = 15
    if len(cards) != 15:
        errors.append(f"卡总数 {len(cards)} ≠ 15")

    return errors


def main():
    root = Path(__file__).parent.parent
    emotions_path = root / "data" / "emotions.json"
    output_path = root / "data" / "emotion_cards.json"

    if not emotions_path.exists():
        print(f"✗ 找不到 {emotions_path}")
        sys.exit(1)

    # 构建
    cards = build_emotion_cards(str(emotions_path))

    # 验证
    errors = validate_cards(cards, str(emotions_path))
    if errors:
        print("验证错误:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    # 输出
    output = {
        "_description": (
            "15 张情绪卡的完整数据。每张卡锚定一个基础情绪（来自 NRC VAD Lexicon），"
            "定义打出效果（PAD 爆发）、手牌压力（轻度 PAD 偏移）、战末残留（心境偏移）、"
            "获得条件和联动规则。字段规范见 卡牌系统/情绪卡模板.md。"
        ),
        "_source": "卡牌系统/情绪卡模板.md, data/emotions.json",
        "_updated": "2026-07-10",
        "cards": cards,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成 {output_path}（{len(cards)} 张情绪卡）")
    print(f"  JSON 大小: {output_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
