#!/usr/bin/env python3
"""生成 data/cognition_cards.json — 25 张认知卡的完整数据。

用法: python3 code/tools/gen_cognition_cards.py
来源: 卡牌系统/认知卡模板.md, data/drives.json
"""

import json
from pathlib import Path


def build_cognition_cards() -> list[dict]:
    """返回 25 张认知卡的完整数据。每张卡的参数根据模块特性和卡名语义设计。"""
    cards = []

    # ═══════════════════════════════════════════════════════════
    # 模块 1: 知觉与注意 (5 张) — CPM Relevance, 无前置
    # ═══════════════════════════════════════════════════════════

    cards.append({
        "id": "insight",
        "name": "洞见",
        "type": "认知",
        "module": "知觉与注意",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "揭示敌人一个隐藏属性。",
        "base_effect": "揭示敌方 1 个隐藏标签/属性。若敌方无隐藏属性，改为 d' 临时 +0.3（本回合）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.20,
            "criterion": 0.00,
            "depth_alpha": 0.30,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty"],
            "prerequisite_modules": [],
        },
        "effect": {
            "type": "揭示",
            "target": "敌方",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧/焦虑→注意窄化：d' 对威胁源 +0.3 但对非威胁源 -0.3。"
                "快乐→注意拓宽：criterion 临时 -0.1（更容易注意到细节）。"
            ),
            "boosts_behaviors": ["回避", "面对"],
            "combo_emotion": ["恐惧", "焦虑"],
            "gate_unlocks": [],
        },
        "design_note": (
            "第一关认知卡。成本最低、最先可用。效果温和但信息价值高。"
            "与凝神（唯心）形成对比——洞见是'看清除什么'，凝神是'选择不看什么'。"
        ),
    })

    cards.append({
        "id": "focus",
        "name": "凝神",
        "type": "认知",
        "module": "知觉与注意",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "忽略负面情绪的干扰，保持注意清晰。",
        "base_effect": "本回合忽略 1 种负面情绪卡的手牌压力效果。criterion 临时 +0.2（更保守，更不轻易被情绪牵着走）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.10,
            "criterion": 0.30,
            "depth_alpha": 0.40,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty", "Intrinsic Pleasantness"],
            "prerequisite_modules": [],
        },
        "effect": {
            "type": "窄化",
            "target": "自身",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "高 Arousal（|A| > 0.5）→ 凝神更难维持：α 被压低 0.15。"
                "平静→凝神效果翻倍：忽略 2 种情绪卡的手牌压力。"
            ),
            "boosts_behaviors": ["面对", "坚持", "观察"],
            "combo_emotion": ["平静", "希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "与洞见（唯物）形成对比——洞见向外看，凝神向内守。"
            "凝神是'主动不看的勇气'——不是不知道，是选择不被知道的东西左右。"
            "在月光下，凝神可能产生微弱的观察者效应——你选择不看的东西，真的会暂时褪色。"
        ),
    })

    cards.append({
        "id": "scrutinize",
        "name": "察微",
        "type": "认知",
        "module": "知觉与注意",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "发现环境中隐藏的线索或物件。",
        "base_effect": "揭示当前房间/场景中 1-2 个隐藏线索。若场景无隐藏线索，改为获得'细节关注'buff（下张认知卡 d' +0.2）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.30,
            "criterion": -0.10,
            "depth_alpha": 0.50,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty", "Goal Relevance"],
            "prerequisite_modules": [],
        },
        "effect": {
            "type": "揭示",
            "target": "环境",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "高 Arousal（|A| > 0.6）→ criterion 进一步降低至 -0.25（过度警觉→草木皆兵）。"
                "平静→ d' +0.1（不慌不忙地看，最清楚）。"
            ),
            "boosts_behaviors": ["搜索", "调查", "检查"],
            "combo_emotion": ["平静", "共情"],
            "gate_unlocks": [],
        },
        "design_note": (
            "察微是信息收集的基础卡——不直接造成伤害，但为后续认知操作提供素材。"
            "criterion -0.1 表示'我愿意看到更多东西'，但代价是可能误报（把噪音当信号）。"
        ),
    })

    cards.append({
        "id": "survey",
        "name": "纵观",
        "type": "认知",
        "module": "知觉与注意",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "拓宽注意范围，同时观察多个目标。",
        "base_effect": "本回合可同时查看所有敌方单位的 1 个属性（多敌方场景）或查看敌方当前状态 + 意图（单敌方场景）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.05,
            "criterion": -0.20,
            "depth_alpha": 0.20,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty"],
            "prerequisite_modules": [],
        },
        "effect": {
            "type": "拓宽",
            "target": "敌方",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧→注意窄化：纵观效果减半（仅能观察 1 个目标/1 个属性）。"
                "快乐→注意拓宽：纵观效果 +1 目标。"
                "愤怒→只对威胁源有效（对其他目标 d' -0.3）。"
            ),
            "boosts_behaviors": ["评估", "指挥", "协调"],
            "combo_emotion": ["快乐", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "纵观是'广度换深度'——d' 低但覆盖面广。"
            "与察微互补：察微看一个点，纵观看全局。两张 combo 可触发'全景图'效果。"
        ),
    })

    cards.append({
        "id": "alert",
        "name": "警觉",
        "type": "认知",
        "module": "知觉与注意",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "提前发现敌方的威胁意图。",
        "base_effect": "预览敌方下回合可能采取的行动类型（不一定是确定性的——月光下的概率分布）。若敌方无隐藏意图，改为本回合反射驱动 θ_play 降低 0.1。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.15,
            "criterion": -0.25,
            "depth_alpha": 0.25,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty", "Goal Relevance"],
            "prerequisite_modules": [],
        },
        "effect": {
            "type": "预览",
            "target": "敌方",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧→警觉被过度激活：criterion 进一步降低至 -0.4（草木皆兵——什么都像威胁）。"
                "焦虑→预览的不确定性被放大（概率分布展宽）。"
            ),
            "boosts_behaviors": ["准备", "防御", "逃跑"],
            "combo_emotion": ["恐惧", "焦虑"],
            "gate_unlocks": [],
        },
        "design_note": (
            "警觉是知觉与注意模块中唯一偏唯心的卡——因为'威胁'是需要被解释的，不是纯客观属性。"
            "criterion -0.25 表示'宁可误报不可漏报'——对威胁信号极度宽松，对安全信号保守。"
        ),
    })

    # ═══════════════════════════════════════════════════════════
    # 模块 2: 记忆 (5 张) — CPM Implications 辅助
    # ═══════════════════════════════════════════════════════════

    cards.append({
        "id": "reclaim",
        "name": "拾遗",
        "type": "认知",
        "module": "记忆",
        "tendency": "唯物",
        "time_orientation": "过去",
        "effect_description": "从弃牌堆回收一张卡牌加入手牌。",
        "base_effect": "从弃牌堆选择 1 张卡牌回到手牌。不可回收本回合刚消耗的卡。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.10,
            "criterion": 0.10,
            "depth_alpha": 0.40,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Discrepancy", "Outcome Probability"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "回收",
            "target": "卡牌",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "悲痛→回忆偏向负面：从弃牌堆回收时只能选情绪卡（'除了难过的事什么也想不起来'）。"
                "希望→可额外回收 1 张（'记得那些好的时候'）。"
            ),
            "boosts_behaviors": ["重新尝试", "坚持"],
            "combo_emotion": ["希望", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "拾遗是资源回收卡——让关键卡牌获得第二次使用机会。"
            "不可回收同回合刚消耗的卡（防止无限循环）。"
            "d' 低表示'记得不一定准'——回收的卡效果可能打 9 折（回忆不是原版）。"
        ),
    })

    cards.append({
        "id": "recall",
        "name": "追忆",
        "type": "认知",
        "module": "记忆",
        "tendency": "唯物",
        "time_orientation": "过去",
        "effect_description": "检索牌库中一张特定类型的卡加入手牌。",
        "base_effect": "查看牌库顶 5 张，选择其中 1 张加入手牌。其余按原顺序放回。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.20,
            "criterion": 0.05,
            "depth_alpha": 0.55,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Causal Attribution", "Goal Conductiveness"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "检索",
            "target": "卡牌",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "高 Arousal（|A| > 0.5）→ 检索范围缩减：只能看 3 张。"
                "平静→检索范围扩大：看 7 张。"
            ),
            "boosts_behaviors": ["计划", "准备", "选择"],
            "combo_emotion": ["平静", "希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "追忆是定向检索——比拾遗更主动但需要更深加工（α=0.55）。"
            "记忆检索受 Arousal 影响严重——太兴奋或太紧张都记不清。"
            "配合 CHC 长时记忆检索能力 (Glr) 可提升检索范围。"
        ),
    })

    cards.append({
        "id": "letgo",
        "name": "释怀",
        "type": "认知",
        "module": "记忆",
        "tendency": "唯心",
        "time_orientation": "过去",
        "effect_description": "移除手牌中一张负面情绪卡。",
        "base_effect": "从手牌中选择 1 张负面情绪卡（valence_group=negative），将其消耗（不产生打出效果，直接移出本场战斗）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.00,
            "criterion": -0.35,
            "depth_alpha": 0.60,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Adjustment", "Control"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "重构",
            "target": "自身",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "内疚→释怀难度增加：需额外满足 C_control ≥ 1.0（'我不配放下'）。"
                "平静→释怀效果增强：可额外移除 1 张中性情绪卡。"
                "爱→释怀负面情绪时可改为转化为 1 张 希望。"
            ),
            "boosts_behaviors": ["放下", "原谅", "前行"],
            "combo_emotion": ["平静", "爱", "希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "释怀是记忆模块的唯心路线核心卡——不是'忘掉'，是'重新摆放'。"
            "criterion -0.35 表示'我愿意相信我可以放下'——这本身就是一种信念。"
            "与拾遗（唯物）形成对比：拾遗是把过去拿回来，释怀是把过去放下去。"
        ),
    })

    cards.append({
        "id": "flashback",
        "name": "闪回",
        "type": "认知",
        "module": "记忆",
        "tendency": "唯物",
        "time_orientation": "过去",
        "effect_description": "重复结算上回合一张卡的效果。",
        "base_effect": "选择上回合（已结算的）1 张认知卡或行为卡，再次触发其效果（以当前状态为目标重新结算，不消耗原卡 AP）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.15,
            "criterion": -0.10,
            "depth_alpha": 0.45,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Causal Attribution"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "回收",
            "target": "卡牌",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧/PTSD→闪回不可控：有 30% 概率闪回到'不想回忆的事'（随机选择而非玩家选择）。"
                "悲痛→闪回效果 × 0.7（悲伤扭曲了记忆的清晰度）。"
            ),
            "boosts_behaviors": ["重复", "改进", "再来一次"],
            "combo_emotion": ["希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "闪回是双刃剑——记忆不会完美复现，每次闪回效果打 9 折（记忆衰减）。"
            "PTSD 患者（角色被动）的闪回可能不可控——这是病情在游戏机制中的体现。"
        ),
    })

    cards.append({
        "id": "etch",
        "name": "铭刻",
        "type": "认知",
        "module": "记忆",
        "tendency": "唯心",
        "time_orientation": "过去",
        "effect_description": "将当前一张卡的效果保留至下回合。",
        "base_effect": "选择当前手牌中 1 张卡的卡面效果，将其'铭刻'到下回合——该效果在下回合结束时自动触发（不占用手牌槽位，不额外消耗 AP）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.10,
            "criterion": -0.20,
            "depth_alpha": 0.70,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Adjustment", "Internal Standards"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "重构",
            "target": "自身",
            "duration": "至下回合结束",
        },
        "linkages": {
            "emotion_distortion": (
                "高 A（|A| > 0.6）→ 铭刻不稳定：下回合触发时有 20% 概率效果打折。"
                "希望→铭刻效果 +20%（'我相信这值得记住'）。"
            ),
            "boosts_behaviors": ["计划", "准备", "等待"],
            "combo_emotion": ["希望", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "铭刻是记忆模块的唯心路线——你主动选择把什么刻进自己。"
            "最高 α (0.70) 的记忆卡——深度审慎才能决定什么值得记住。"
            "与闪回（唯物）对比：闪回是记忆找上你，铭刻是你选择记忆。"
        ),
    })

    # ═══════════════════════════════════════════════════════════
    # 模块 3: 知识表征与分类 (5 张) — CPM Relevance + Normative
    # ═══════════════════════════════════════════════════════════

    cards.append({
        "id": "discern",
        "name": "甄别",
        "type": "认知",
        "module": "知识表征与分类",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "揭示对象的完整标签和属性。",
        "base_effect": "揭示敌方完整属性面板（所有标签、当前状态、活跃驱动）。持续 2 回合，期间该敌方无法隐藏任何属性。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.35,
            "criterion": 0.10,
            "depth_alpha": 0.50,
        },
        "cpm": {
            "step": "Relevance",
            "sec": ["Novelty", "Goal Relevance"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "归类",
            "target": "敌方",
            "duration": "2 回合",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧→分类偏向'威胁'：对威胁相关标签 d' +0.2，非威胁标签可能被忽略。"
                "愤怒→分类偏向'敌人/障碍'：D>0 但不一定准确。"
            ),
            "boosts_behaviors": ["针对", "利用弱点", "精准打击"],
            "combo_emotion": ["平静", "共情"],
            "gate_unlocks": ["惩罚机制 φ"],
        },
        "design_note": (
            "甄别是'严肃的归类'——d' 最高（0.35）的知识表征卡。"
            "完成知识表征 → 解锁惩罚机制 φ（你现在知道'这是什么威胁'了）。"
            "与定性（唯心）形成对比：甄别问'它是什么'，定性问'它可以叫什么'。"
        ),
    })

    cards.append({
        "id": "label",
        "name": "定性",
        "type": "认知",
        "module": "知识表征与分类",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "为对象添加或改写一个临时标签。",
        "base_effect": "为敌方或自身添加 1 个临时标签（3 回合）。标签类型取决于当前情绪状态和玩家选择。该标签影响对象的行为倾向和系统对其的反应。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": -0.05,
            "criterion": -0.35,
            "depth_alpha": 0.45,
        },
        "cpm": {
            "step": "Normative",
            "sec": ["Internal Standards", "External Standards"],
            "prerequisite_modules": ["知觉与注意"],
        },
        "effect": {
            "type": "归类",
            "target": "敌方",
            "duration": "3 回合",
        },
        "linkages": {
            "emotion_distortion": (
                "愤怒→标签偏向'敌人/威胁/障碍'。"
                "爱→标签偏向'可拯救/误入歧途/值得等待'。"
                "恐惧→标签偏向'怪物/不可名状/不可理解'。"
                "共情→标签更接近对象的自我认知。"
            ),
            "boosts_behaviors": ["说服", "安抚", "对峙", "理解"],
            "combo_emotion": ["共情", "愤怒", "爱"],
            "gate_unlocks": [],
        },
        "design_note": (
            "定性是月光下最具观察者效应的卡之一——你给的标签可能变成真的。"
            "d' 负值（-0.05）表示定性本身不提升准确性——它改变的是框架，不是信息质量。"
            "criterion -0.35 表示'我愿意相信这个标签'——这是信念驱动的操作。"
        ),
    })

    cards.append({
        "id": "attribute",
        "name": "归因",
        "type": "认知",
        "module": "知识表征与分类",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "判断敌方行为的真实动机，降低其行为的威胁评估。",
        "base_effect": "分析敌方当前行为意图，揭示其背后的驱动和情绪状态。若分析成功，该敌方本回合行为效果 -25%（'看穿了就不那么可怕了'）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.25,
            "criterion": 0.15,
            "depth_alpha": 0.55,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Causal Attribution", "Discrepancy"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "重评",
            "target": "敌方",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "愤怒→归因偏向敌意：倾向于将敌方行为归因为'恶意'，反而增加威胁评估。"
                "共情→归因更准确：d' +0.15（更能理解对方的动机）。"
                "恐惧→归因偏向最大威胁假设。"
            ),
            "boosts_behaviors": ["安抚", "谈判", "理解", "反制"],
            "combo_emotion": ["共情", "平静"],
            "gate_unlocks": ["奖励机制 φ"],
        },
        "design_note": (
            "归因在 CPM Step 2 (Implications) 中执行——'你这么做是因为什么？'"
            "归因的成功率取决于角色 CHC 晶体知识 (Gc) 和流体推理 (Gf)。"
            "错误的归因比不归因更危险——愤怒中的归因往往会激化冲突。"
        ),
    })

    cards.append({
        "id": "rectify",
        "name": "正名",
        "type": "认知",
        "module": "知识表征与分类",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "移除对象身上的虚假标签或幻象。",
        "base_effect": "移除敌方或环境中的 1 个虚假标签/幻象/观察者效应产物。若对象无虚假标签，改为移除自身 1 个由情绪扭曲造成的认知偏差（如注意窄化/确认偏向）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.40,
            "criterion": 0.30,
            "depth_alpha": 0.60,
        },
        "cpm": {
            "step": "Normative",
            "sec": ["Internal Standards", "External Standards"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "重评",
            "target": "敌方",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "高 D→正名效果增强（'我有足够的控制感去质疑眼前的假象'）。"
                "低 D（D < -0.3）→正名可能失败（'我连自己都不信'），有概率反而强化虚假标签。"
            ),
            "boosts_behaviors": ["揭露", "质疑", "挑战", "拒绝"],
            "combo_emotion": ["愤怒", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "正名是最'唯物'的知识表征卡——d'=0.40 + criterion=0.30 = 最精准最保守。"
            "在月光下，正名是消解观察者效应幻象的关键工具。"
            "D 轴是正名的生命线——控制感越低，越容易被假象牵着走。"
        ),
    })

    cards.append({
        "id": "analogy",
        "name": "类比",
        "type": "认知",
        "module": "知识表征与分类",
        "tendency": "唯心",
        "time_orientation": "过去",
        "effect_description": "将陌生的对象或情境匹配到已有经验图式。",
        "base_effect": "选择一个已揭示的敌方属性/标签，将其'类比'到已知图式，降低该属性的威胁评估或增强正面评估。类比成功 → 对该敌方的所有行为卡 cost_modifier 下降 0.2（持 2 回合）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.05,
            "criterion": -0.30,
            "depth_alpha": 0.50,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Causal Attribution", "Discrepancy"],
            "prerequisite_modules": ["知觉与注意", "记忆"],
        },
        "effect": {
            "type": "归类",
            "target": "敌方",
            "duration": "2 回合",
        },
        "linkages": {
            "emotion_distortion": (
                "恐惧→类比可能'过度匹配'：将新威胁错误类比为已知最恐怖的经验。"
                "共情→类比更准确：d' +0.15（更能抓住本质相似性）。"
            ),
            "boosts_behaviors": ["理解", "接纳", "适应"],
            "combo_emotion": ["共情", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "类比依赖记忆模块——需要检索过去的经验（前置模块含'记忆'）。"
            "criterion -0.30 表示'我愿意相信这个类比成立'——需要信念跳跃。"
            "类比是将不可名状变为可理解的第一步——'它就像……'"
        ),
    })

    # ═══════════════════════════════════════════════════════════
    # 模块 4: 表象与语言 (5 张) — CPM Coping + Normative
    # ═══════════════════════════════════════════════════════════

    cards.append({
        "id": "metaphor",
        "name": "隐喻",
        "type": "认知",
        "module": "表象与语言",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "重新框定对象的意义，改变其行为倾向。",
        "base_effect": "为敌方添加 1 个临时标签（3 回合），敌方 AI 行为受标签影响。标签类型取决于当前情绪状态和玩家选择。同时，该敌方对你造成的 SAN 伤害 -1（'它不再那么可怕了'或'它比你想象的危险'）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.00,
            "criterion": -0.30,
            "depth_alpha": 0.50,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Adjustment", "Internal Standards"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "命名",
            "target": "敌方",
            "duration": "3 回合",
        },
        "linkages": {
            "emotion_distortion": (
                "愤怒→标签偏向'敌人/威胁'：强化攻击意愿但增加威胁感知。"
                "爱→标签偏向'可拯救/误入歧途'：降低冲突意愿。"
                "恐惧→标签偏向'怪物/不可名状'：增加逃跑行为的推力。"
            ),
            "boosts_behaviors": ["对峙", "安抚", "说服", "威慑"],
            "combo_emotion": ["共情", "愤怒", "敬畏"],
            "gate_unlocks": [],
        },
        "design_note": (
            "隐喻是表象与语言模块的唯心核心——'给它起个名字，它就不一样了'。"
            "月光下，语言有创造现实的重量。隐喻的效果取决于标签是否被'相信'。"
            "d'=0.00——隐喻不提升准确性，它改变的是意义的框架。"
        ),
    })

    cards.append({
        "id": "depict",
        "name": "白描",
        "type": "认知",
        "module": "表象与语言",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "剥离对象的虚假表象和幻象，看清其本来面目。",
        "base_effect": "移除敌方或当前场景中所有由观察者效应/月光产生的幻象和虚假标签。每个被移除的幻象对敌方造成 1 点心灵震慑（'假象被剥去的那一刻，制造假象的人也会受伤'）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.35,
            "criterion": 0.25,
            "depth_alpha": 0.65,
        },
        "cpm": {
            "step": "Normative",
            "sec": ["External Standards", "Internal Standards"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "揭示",
            "target": "敌方",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "高 D→白描效果增强：d' +0.1（控制感让你更能区分真实和假象）。"
                "低 D（D < -0.3）→白描可能失效：你无法区分自己看到的什么是真的。"
                "恐惧→白描更难：d' 对威胁源 -0.15（恐惧让假象更有说服力）。"
            ),
            "boosts_behaviors": ["揭露", "质疑", "拒绝", "面对"],
            "combo_emotion": ["平静", "愤怒"],
            "gate_unlocks": [],
        },
        "design_note": (
            "白描是表象与语言模块的唯物路线——'只描述，不解释'。"
            "与隐喻（唯心）形成尖锐对比：隐喻靠命名创造意义，白描靠去除命名看清真相。"
            "最高 d' (0.35) 的表象与语言卡——不说多余的话，就不引入多余的幻象。"
        ),
    })

    cards.append({
        "id": "envision",
        "name": "构想",
        "type": "认知",
        "module": "表象与语言",
        "tendency": "唯心",
        "time_orientation": "未来",
        "effect_description": "在脑海中预演一个可能的未来场景。",
        "base_effect": "选择 1 个未来可能发生的事件（敌方可能的行为/环境可能的变化），获得该事件的详细预演。若该事件真的发生，己方在下回合获得'预先准备'buff（对该事件的首张响应卡 AP -1，效果 +20%）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.05,
            "criterion": -0.25,
            "depth_alpha": 0.60,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Control", "Adjustment"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类", "记忆"],
        },
        "effect": {
            "type": "预览",
            "target": "自身",
            "duration": "至下回合",
        },
        "linkages": {
            "emotion_distortion": (
                "焦虑→构想偏向最坏情景：有 40% 概率预演到灾难化版本（反而增加焦虑）。"
                "希望→构想偏向乐观版本：预演的正面可能性 +20%。"
                "绝望→构想失败：看不到任何正面未来分支。"
            ),
            "boosts_behaviors": ["准备", "计划", "等待", "预防"],
            "combo_emotion": ["希望", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "构想是表象与语言模块的未来导向卡——用表象'看到'还未发生的。"
            "月光下，构想有微弱的观察者效应——你预演的未来，有极小概率被拉近。"
            "焦虑中的构想是双刃剑——你看到的是准备还是自我实现的预言？"
        ),
    })

    cards.append({
        "id": "rephrase",
        "name": "转述",
        "type": "认知",
        "module": "表象与语言",
        "tendency": "唯物",
        "time_orientation": "现在",
        "effect_description": "改变事件的语言描述方式，缓和对情绪的冲击。",
        "base_effect": "选择一个当前生效的情绪效果（手牌压力/打出偏移/残留倾向），重新'描述'它。根据描述方式，该情绪效果的 PAD 偏移量在 ±20% 范围内调整（可选择缓和或放大）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.15,
            "criterion": 0.05,
            "depth_alpha": 0.55,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Adjustment"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "重评",
            "target": "自身",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "高 D→转述效果增强：调整范围扩大到 ±30%（高控制让你更擅长重新框定）。"
                "低 D→转述效果减弱：只能缩小（不能扩大）情绪效果（'我只能试着让它不那么糟'）。"
            ),
            "boosts_behaviors": ["安抚自己", "冷静", "重新评估"],
            "combo_emotion": ["平静", "希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "转述是认知行为疗法（CBT）核心技术在月光世界的映射——改变描述，改变感受。"
            "与隐喻（唯心）不同——转述是'换个说法'，隐喻是'给它一个全新的名字'。"
            "转述的唯物路线在于：它承认客观事实，但调整主观框架。"
        ),
    })

    cards.append({
        "id": "naming",
        "name": "命名",
        "type": "认知",
        "module": "表象与语言",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "在月光下赋予对象一个名字——这个名字可能变成真的。",
        "base_effect": "消耗 1 意志力。为对象创造并固化 1 个永久标签（本场战斗内永久）。该标签影响所有相关卡牌的效果结算。在月光浓度高的场景，标签可能触发观察者效应事件。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": -0.10,
            "criterion": -0.40,
            "depth_alpha": 0.75,
        },
        "cpm": {
            "step": "Normative",
            "sec": ["Internal Standards", "External Standards"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类", "表象与语言"],
        },
        "effect": {
            "type": "命名",
            "target": "敌方",
            "duration": "整场",
        },
        "linkages": {
            "emotion_distortion": (
                "敬畏→命名效果 × 1.5（在宏大存在面前，命名的重量更大）。"
                "绝望→命名可能反噬：有 30% 概率创造负面标签而非预期标签。"
            ),
            "boosts_behaviors": ["定义", "宣告", "创造", "固化"],
            "combo_emotion": ["敬畏", "爱", "愤怒"],
            "gate_unlocks": [],
        },
        "design_note": (
            "命名是认知卡中 α 最高（0.75）的卡——需要深度审慎和全部前置模块。"
            "唯一消耗意志力的认知卡——在月光下，命名是有代价的创造行为。"
            "d' 负值（-0.10）表示命名不是'发现真相'——它是'创造真相'。"
            "criterion -0.40 = 全游戏最宽松的判断偏向——你必须深深地相信这个名字。"
        ),
    })

    # ═══════════════════════════════════════════════════════════
    # 模块 5: 推理与决策 (5 张) — CPM Implications + Coping
    # ═══════════════════════════════════════════════════════════

    cards.append({
        "id": "predict",
        "name": "预判",
        "type": "认知",
        "module": "推理问题解决与决策",
        "tendency": "唯物",
        "time_orientation": "未来",
        "effect_description": "预览敌方下回合最可能采取的行为及其概率分布。",
        "base_effect": "显示敌方下回合可能的行为列表（按概率排序，最多 3 项）。预判准确度 = d' × (1 + β·w_Gf)，β=0.2。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.25,
            "criterion": 0.10,
            "depth_alpha": 0.55,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Outcome Probability", "Urgency"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "预览",
            "target": "敌方",
            "duration": "即时",
        },
        "linkages": {
            "emotion_distortion": (
                "焦虑→预判被灾难化扭曲：低概率的高威胁选项被放大显示（概率 +15% 虚增）。"
                "平静→预判准确度 +15%（最理性的预判状态）。"
                "恐惧→只看到威胁相关选项，忽略非威胁行为。"
            ),
            "boosts_behaviors": ["准备", "反制", "规避", "利用"],
            "combo_emotion": ["平静", "希望"],
            "gate_unlocks": ["奖励机制 φ"],
        },
        "design_note": (
            "预判是推理模块的唯物基础卡——基于现有信息计算概率，不添加信念成分。"
            "角色流体推理 (Gf) 直接影响预判准确度。"
            "与决意（唯心）形成对比：预判问'最可能发生什么'，决意问'我选择相信什么会发生'。"
        ),
    })

    cards.append({
        "id": "decide",
        "name": "决意",
        "type": "认知",
        "module": "推理问题解决与决策",
        "tendency": "唯心",
        "time_orientation": "未来",
        "effect_description": "从多个可能的未来分支中，选择相信其中一个并将其拉近。",
        "base_effect": "展示 2-3 个可能的未来分支（基于当前态势推演）。选择一个'相信'——该分支的发生概率 +20%（月光下，信念改变概率）。消耗 1 意志力。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.05,
            "criterion": -0.35,
            "depth_alpha": 0.70,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Control", "Adjustment"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类", "推理问题解决与决策"],
        },
        "effect": {
            "type": "推演",
            "target": "自身",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "希望对决意的加成最强：选择的正面分支额外 +10% 概率（'希望让信念有了锚点'）。"
                "绝望→决意无法使用（看不到任何值得相信的未来）。"
                "愤怒→决意偏向'击败敌人'的分支，忽略其他选项。"
            ),
            "boosts_behaviors": ["坚持", "突破", "冲刺", "相信"],
            "combo_emotion": ["希望", "愤怒", "爱"],
            "gate_unlocks": ["价值驱动 φ"],
        },
        "design_note": (
            "决意是推理模块的唯心路线核心卡——在月光下，足够深地相信一件事，会让它变得更可能。"
            "这是观察者效应在游戏机制中最直接的体现。"
            "消耗意志力 + 最高 α (0.70) = 这是最有分量的认知操作之一。"
        ),
    })

    cards.append({
        "id": "calculate",
        "name": "筹算",
        "type": "认知",
        "module": "推理问题解决与决策",
        "tendency": "唯物",
        "time_orientation": "未来",
        "effect_description": "优化行动方案，降低下张行为卡的 AP 消耗。",
        "base_effect": "本回合下一张打出的行为卡 AP 消耗 -1（最低降至 1）。若该行为卡为硬解锁状态，意志力成本 -1（最低降至 0）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.20,
            "criterion": 0.15,
            "depth_alpha": 0.55,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Control", "Power"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "推演",
            "target": "自身",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "高 Arousal→筹算被打断：AP 减免降低至 -0（太激动算不清）。"
                "平静→筹算效果 +1：可再降低 1 AP（'冷静是最好的计算器'）。"
            ),
            "boosts_behaviors": ["所有行为卡"],
            "combo_emotion": ["平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "筹算是推理模块最直接的实用卡——让行为更省力。"
            "但节省 AP ≠ 降低 C_control——如果行为卡需要硬解锁，意志力成本可以降低但不能消除。"
            "配合推演使用 → 连续筹算+推演 → 下回合打出成本极低的行为卡。"
        ),
    })

    cards.append({
        "id": "extend",
        "name": "推演",
        "type": "认知",
        "module": "推理问题解决与决策",
        "tendency": "唯物",
        "time_orientation": "未来",
        "effect_description": "延长一张效果卡牌的持续时间。",
        "base_effect": "选择当前场上 1 个有效果持续时间的状态/标签，将其剩余持续时间 +2 回合（不超过其原始持续时间的 2 倍）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.15,
            "criterion": 0.05,
            "depth_alpha": 0.60,
        },
        "cpm": {
            "step": "Implications",
            "sec": ["Outcome Probability", "Goal Conductiveness"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类"],
        },
        "effect": {
            "type": "推演",
            "target": "己方效果",
            "duration": "即时（延长目标）",
        },
        "linkages": {
            "emotion_distortion": (
                "高 Arousal→推演仓促：延长的回合效果打折（+2 回合但效果量 × 0.8）。"
                "希望→推演倾向延长正面效果。"
                "焦虑→推演倾向延长防御性效果（而非进攻性效果）。"
            ),
            "boosts_behaviors": ["维持", "等待", "巩固"],
            "combo_emotion": ["希望", "平静"],
            "gate_unlocks": [],
        },
        "design_note": (
            "推演是推理模块的'时间魔术'——把此刻的认知效果拉到未来。"
            "不能无限延长——上限为原始持续时间的 2 倍（防止永久 buff 堆叠）。"
            "与筹算配合可形成'准备-爆发'循环。"
        ),
    })

    cards.append({
        "id": "weigh",
        "name": "权衡",
        "type": "认知",
        "module": "推理问题解决与决策",
        "tendency": "唯心",
        "time_orientation": "现在",
        "effect_description": "比较两个选项的得失，放弃其中一个以强化另一个。",
        "base_effect": "从当前手牌中选择 2 张，比较并放弃 1 张（消耗该卡且不触发其效果），保留的 1 张获得'深思熟虑'加成：效果 +30%，AP 消耗 -0（不超过基础值）。消耗被放弃的卡进入弃牌堆（情绪卡直接消失）。",
        "ap_cost": 0,
        "cognitive_quality": {
            "d_prime": 0.10,
            "criterion": 0.20,
            "depth_alpha": 0.65,
        },
        "cpm": {
            "step": "Coping",
            "sec": ["Control", "Adjustment"],
            "prerequisite_modules": ["知觉与注意", "知识表征与分类", "推理问题解决与决策"],
        },
        "effect": {
            "type": "推演",
            "target": "卡牌",
            "duration": "本回合",
        },
        "linkages": {
            "emotion_distortion": (
                "焦虑→权衡困难：需要额外选择 1 张作为'安全备份'（不参与权衡，只是放着）。"
                "高 D→权衡更果断：放弃的卡不会进弃牌堆而直接移除本场（高控制感——'我不需要犹豫'）。"
                "希望→更可能保留正面效果的卡。"
            ),
            "boosts_behaviors": ["选择", "专注", "决断"],
            "combo_emotion": ["平静", "希望"],
            "gate_unlocks": [],
        },
        "design_note": (
            "权衡是推理模块的唯心路线——不是'哪个更可能'（唯物），而是'我选择重视哪个'（唯心）。"
            "criterion +0.20 = 比较保守——你在仔细掂量，不会轻易下结论。"
            "与决意形成推理唯心双卡：权衡是'选牌'，决意是'选未来'。"
        ),
    })

    return cards


def validate_cards(cards: list[dict]) -> list[str]:
    """验证认知卡数据，返回错误列表。"""
    errors = []

    # 有效模块列表和激活顺序
    module_order = [
        "知觉与注意",
        "记忆",
        "知识表征与分类",
        "表象与语言",
        "推理问题解决与决策",
    ]
    valid_modules = set(module_order)
    valid_tendencies = {"唯物", "唯心"}
    valid_types = {"揭示", "重评", "拓宽", "窄化", "重构", "预览", "回收", "命名", "归类", "推演", "检索"}
    valid_targets = {"自身", "敌方", "环境", "卡牌", "己方效果"}
    valid_durations = {"即时", "本回合", "2 回合", "3 回合", "整场", "至下回合", "至下回合结束", "即时（延长目标）"}
    valid_steps = {"Relevance", "Implications", "Coping", "Normative"}
    valid_secs = {
        "Novelty", "Intrinsic Pleasantness", "Goal Relevance",
        "Causal Attribution", "Outcome Probability", "Discrepancy",
        "Goal Conductiveness", "Urgency", "Control", "Power",
        "Adjustment", "Internal Standards", "External Standards",
    }

    # CPM 参与度矩阵（来自模板 §4.4）
    module_step_map = {
        "知觉与注意": ["Relevance"],
        "记忆": ["Relevance", "Implications", "Coping"],
        "知识表征与分类": ["Relevance", "Implications", "Normative"],
        "表象与语言": ["Coping", "Normative"],
        "推理问题解决与决策": ["Implications", "Coping"],
    }

    for i, card in enumerate(cards):
        cid = card["id"]
        name = card["name"]
        module = card["module"]
        prefix = f"[{name}] "

        # 1. 模块有效性
        if module not in valid_modules:
            errors.append(f"{prefix}模块 '{module}' 不在 5 模块中")

        # 2. 倾向有效性
        if card["tendency"] not in valid_tendencies:
            errors.append(f"{prefix}倾向 '{card['tendency']}' 无效")

        # 3. 数值范围
        cq = card["cognitive_quality"]
        for field, lo, hi in [("d_prime", -1.0, 1.0), ("criterion", -1.0, 1.0), ("depth_alpha", 0.0, 1.0)]:
            val = cq[field]
            if val < lo or val > hi:
                errors.append(f"{prefix}{field}={val} 超出 [{lo}, {hi}]")

        # 4. CPM 步骤与模块一致
        cpm_step = card["cpm"]["step"]
        if cpm_step not in valid_steps:
            errors.append(f"{prefix}CPM 步骤 '{cpm_step}' 无效")
        if module in module_step_map and cpm_step not in module_step_map[module]:
            errors.append(
                f"{prefix}模块 '{module}' 不在 CPM 步骤 '{cpm_step}' 的参与模块中"
            )

        # 5. 前置模块不违反激活顺序
        # 严格链: 知觉与注意 → 知识表征 → 推理 → 表象与语言（记忆不在链中，自由取用）
        strict_chain = [
            "知觉与注意",
            "知识表征与分类",
            "推理问题解决与决策",
            "表象与语言",
        ]
        prereqs = card["cpm"]["prerequisite_modules"]
        current_idx = strict_chain.index(module) if module in strict_chain else -1
        for pr in prereqs:
            if pr not in valid_modules:
                errors.append(f"{prefix}前置模块 '{pr}' 无效")
            elif pr in strict_chain and current_idx >= 0:
                pr_idx2 = strict_chain.index(pr)
                # 允许同一模块的前置（表示需先打出同模块低级卡），但不能是后续模块
                if pr_idx2 > current_idx:
                    errors.append(f"{prefix}前置模块 '{pr}' 是严格链中后续模块——不能跳过认知阶段")

        # 6. 不能跳过知觉直接推理
        if "推理问题解决与决策" in prereqs or module == "推理问题解决与决策":
            if "知觉与注意" not in prereqs:
                pass  # 推理不需要知觉作为直接前置，但需要通过知识表征

        # 7. 必填字段
        if not card["effect_description"].strip():
            errors.append(f"{prefix}效果描述为空")
        if not card["base_effect"].strip():
            errors.append(f"{prefix}基础效果为空")
        if not card["design_note"].strip():
            errors.append(f"{prefix}设计备忘为空")

        # 8. effect type
        if card["effect"]["type"] not in valid_types:
            errors.append(f"{prefix}效果类型 '{card['effect']['type']}' 无效")

        # 9. SEC 有效性
        for sec in card["cpm"]["sec"]:
            if sec not in valid_secs:
                errors.append(f"{prefix}SEC '{sec}' 无效")

    # 10. 卡名唯一
    names = [c["name"] for c in cards]
    if len(names) != len(set(names)):
        from collections import Counter
        dupes = [n for n, cnt in Counter(names).items() if cnt > 1]
        errors.append(f"重复卡名: {dupes}")

    # 11. 卡数量 = 25
    if len(cards) != 25:
        errors.append(f"卡总数 {len(cards)} ≠ 25")

    # 12. 每模块 5 张
    from collections import Counter
    module_counts = Counter(c["module"] for c in cards)
    for mod, cnt in module_counts.items():
        if cnt != 5:
            errors.append(f"模块 '{mod}' 有 {cnt} 张卡，应为 5 张")

    # 13. 每模块唯物/唯心比例合理（3:2 或 2:3）
    for mod in valid_modules:
        mod_cards = [c for c in cards if c["module"] == mod]
        materialist = sum(1 for c in mod_cards if c["tendency"] == "唯物")
        idealist = sum(1 for c in mod_cards if c["tendency"] == "唯心")
        if materialist + idealist != 5:
            continue
        if materialist not in (2, 3):
            errors.append(f"模块 '{mod}' 唯物:{materialist} 唯心:{idealist}（比例异常）")

    return errors


def main():
    root = Path(__file__).parent.parent.parent
    output_path = root / "data" / "cognition_cards.json"

    # 构建
    cards = build_cognition_cards()

    # 验证
    errors = validate_cards(cards)
    if errors:
        print("验证错误:")
        for e in errors:
            print(f"  ✗ {e}")
        # 不退出——警告但继续输出（方便迭代修复）

    # 输出
    output = {
        "_description": (
            "25 张认知卡的完整数据。每张卡归属 5 模块之一，以 C⁵ 复平面坐标 (d' + i·criterion) "
            "量化操作质量，以加工深度 α 决定 System 1/2 走向。字段规范见 卡牌系统/认知卡模板.md。"
        ),
        "_source": "卡牌系统/认知卡模板.md, data/drives.json",
        "_updated": "2026-07-10",
        "cards": cards,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成 {output_path}（{len(cards)} 张认知卡）")
    print(f"  JSON 大小: {output_path.stat().st_size:,} bytes")

    if errors:
        print(f"\n⚠ 验证发现 {len(errors)} 个问题:")
        for e in errors:
            print(f"  ✗ {e}")
        print("请检查并修复后再提交。")


if __name__ == "__main__":
    main()
