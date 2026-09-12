#!/usr/bin/env python3
"""
gen_modulation_ceiling_v2.py — 三因子链路调制模型

数据来源:
  A. Momi et al. (2025) Nature Communications — 皮层兴奋性梯度
     36名患者, 颅内电刺激(iES)+EEG. 高阶网络(DMN/FPN/SN)诱发电位
     显著强于低阶网络(视觉/感觉运动), 由递归反馈强度驱动.
     → 调制天花板(excitability): L5>L4>L3>L2>L1>L0

  B. TMS-fMRI 有效连接 — 因果调制强度直接测量
     单脉冲TMS+同步fMRI: 刺激A→记录B的BOLD%信号变化.
     → 链路优先级(conduction_speed): 粗纤维(快) vs 细纤维(慢)

  C. Hansen et al. (2024) Nature Neuroscience — 脑干神经调质社区
     58脑干核团, 5大社区, 9种递质系统.
     → 调制类型增益(neuromodulator_gain): DA=动机放大,
        NE=精度提升, 5-HT=过滤/防御

  D. Pajevic et al. (2023) eLife — 髓鞘化同步模型
     少突胶质细胞在10-40ms窗口内调制传导延迟.
     → 髓鞘化曲线: 不是线性缩放, 而是改变信号同步精度

三因子公式:
  modulation_ceiling = excitability × neuromodulator_gain
  link_priority = conduction_speed (决定同回合内链路的结算顺序)
  actual_modulation = ceiling × myelination_sync(myelination_level)
    where myelination_sync(m) = 1 / (1 + e^(-8×(m-0.4)))
    (sigmoid: 髓鞘化前30%几乎无效果, 40-60%快速增长, 80%+接近满效果)

输出:
  - data/connectivity/link_modulation_ceiling_v2.json
  - design/rules/skill-tree/modulation/链路调制上限参考表-v2.md（⚠️ 本脚本的 MD 输出尚未随 Phase 3 路径改名更新）
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent.parent

# ═══════════════════════════════════════════════════
# A. Momi 2025 兴奋性梯度 — modulation ceiling
# ═══════════════════════════════════════════════════

# Momi et al. (2025) Fig.2-4:
#   - iES刺激高阶网络 → 诱发电位 ~3× 强于低阶网络
#   - 递归(recurrent)成分: 低阶~20%, 高阶~70%
#   - 三个时间簇: ~40ms(前馈), ~80ms(局部递归), ~370ms(长程递归)
#   - 高阶网络的晚期成分(370ms)是最显著的层级区分器
#
# 兴奋性赋值: 基于网络层级位置的相对兴奋性
#   值 = 前馈基线(0.25) + 递归贡献(0-0.75) × 层级位置

MOMI_EXCITABILITY = {
    # L0 脑干: 几乎无递归加工, 纯前馈
    'brainstem': 0.25,     # 纯前馈, 最快最强制但无放大

    # L1 边缘系统: 少量递归(杏仁核-海马-皮层环路)
    'limbic': 0.40,        # 有情绪→皮层反馈但在演化上以快速通路为主

    # L2 旁边缘: 中等递归(岛叶/ACC是突显网络的一部分)
    'paralimbic': 0.55,    # 内感受+冲突监测涉及持续性递归

    # L3 初级感觉运动: 前馈为主但有次级区的递归
    'primary_sensory': 0.30,    # V1/A1/S1/M1 纯前馈
    'secondary_sensory': 0.45,  # 枕顶联合/楔叶/旁中央小叶 — 已有模式级的递归

    # L4 高级单模态: 中等偏高, 模式识别需要迭代加工
    'unimodal': 0.60,

    # L5 跨模态: 高递归 — Momi发现FPN/DMN刺激后诱发电位最强
    'transmodal': 0.85,    # dlPFC/TPJ/Broca — 最依赖递归整合

    # L5 跨模态（原L6整合并入）: 最高递归
    'integration': 0.95,   # DMN/FPN/SN交汇 — 全脑递归

    # 白质通路(连接本身不是灰质节点, 使用端点中值)
    'white_matter': 0.50,

    # 皮下结构 — 使用相邻层级值
    'subcortical_limbic': 0.40,  # 杏仁核/海马/NAcc
    'subcortical_motor': 0.30,   # 壳核/苍白球/尾状核
    'subcortical_relay': 0.30,   # 丘脑
}


def momi_excitability(category, level, region_name=''):
    """Momi 2025 兴奋性: 该脑区在层级中的递归放大潜力 [0, 1]"""
    if category == 'brainstem':
        return MOMI_EXCITABILITY['brainstem']
    elif category == 'cortical':
        if level == 3:
            # 区分初级 vs 次级感觉区
            primary = {'枕叶 V1', 'A1', 'S1', 'M1'}
            if region_name in primary:
                return MOMI_EXCITABILITY['primary_sensory']
            else:
                return MOMI_EXCITABILITY['secondary_sensory']
        elif level == 4:
            return MOMI_EXCITABILITY['unimodal']
        elif level == 5:
            return MOMI_EXCITABILITY['transmodal']
        elif level == 6:
            return MOMI_EXCITABILITY['integration']
        elif level == 2:
            return MOMI_EXCITABILITY['paralimbic']
        elif level == 1:
            return MOMI_EXCITABILITY['limbic']
        else:
            return MOMI_EXCITABILITY['unimodal']  # fallback
    elif category == 'subcortical':
        if level == 1:
            # 区分动机/情绪皮下 vs 运动皮下
            return MOMI_EXCITABILITY['subcortical_limbic']
        else:
            return MOMI_EXCITABILITY['subcortical_motor']
    elif category == 'white_matter':
        return MOMI_EXCITABILITY['white_matter']
    else:
        return 0.35  # fallback


# ═══════════════════════════════════════════════════
# B. TMS-fMRI 传导速度 — link resolution priority
# ═══════════════════════════════════════════════════

# 传导延迟 (ms) 基于:
#   - 演化保守度 (脑干反射最快, 前额叶最慢)
#   - 纤维束直径 (粗=快, 细=慢)
#   - Hansen 2024 时间层级: 脑干→皮层每层+20-50ms
#
# 游戏中的含义: priority = 结算顺序
#   priority 1 (最快) → priority 6 (最慢)
#   同一 priority 内, 防御方先结算

CONDUCTION_SPEED = {
    # (category, level) → (latency_ms, priority)
    ('brainstem', 0):       (15, 1),   # PAG/上丘: ~10-30ms
    ('brainstem', None):    (20, 1),
    ('subcortical', 1):     (40, 2),   # 杏仁核/海马: ~20-80ms
    ('subcortical', None):  (50, 2),
    ('cortical', 2):        (60, 3),   # 旁边缘: ~50-120ms
    ('cortical', 3):        (45, 2),   # 初级感觉: ~30-80ms (前馈快)
    ('cortical', 4):        (100, 4),  # 高级单模态: ~80-150ms
    ('cortical', 5):        (200, 5),  # 跨模态: ~150-300ms
    ('cortical', 6):        (350, 6),  # 整合: ~300ms+ (Momi的第三峰)
    ('white_matter', None): (100, 4),
    ('cortical', None):     (150, 4),  # fallback
    ('subcortical', None):  (80, 3),
}


def conduction_priority(category, level):
    """TMS-fMRI 传导速度 → 链路结算优先级 (1最快, 6最慢)"""
    key = (category, level)
    if key in CONDUCTION_SPEED:
        return CONDUCTION_SPEED[key][1]
    # fallback by category
    cat_key = (category, None)
    if cat_key in CONDUCTION_SPEED:
        return CONDUCTION_SPEED[cat_key][1]
    return 4


# ═══════════════════════════════════════════════════
# C. 脑干社区 → 神经调质增益 — effect type specialization
# ═══════════════════════════════════════════════════

# 社区划分与递质归属的**文献依据**：Hansen JY, et al. (2024).
#   *Integrating brainstem and cortical functional architectures.*
#   Nature Neuroscience 27(12):2500-2511. doi:10.1038/s41593-024-01787-0
#   GREEN:  DA (VTA/SN/PAG)      → 动机突显, 趋近/回避方向
#   PINK:   NE (LC) + 5-HT (DRN) → 唤醒/精度/过滤
#   YELLOW: 多种递质              → 感觉运动中继
#   ⚠️ 复合/通路结构（VTA-NAcc、杏仁核-PAG、反射环路·*）**论文不覆盖**，
#      其社区取自端点核团，属本仓推导。
#   BLUE:   DA + ?               → 工作记忆/认知控制
#
# ★ 但下面的**增益系数是估计值，不是论文数据**。
#   本仓没有读过 `data/connectivity/hansen2024/` 下的任何文件
#   （那 5 个数据文件当前零受控消费者），这些 1.0–1.5 的倍数是照上述
#   递质-功能对应关系**人工设定的**。
#   变量名、文档字符串、产出 JSON 的 `_metadata` 三处都必须体现这一点，
#   否则"从 Nature Neuroscience 推导"会被误读成"从该数据集算出来"。
#
# 增益类型的**设计意图**（这部分是本仓的设计，不是文献）：
#   DA → damage (动机放大: "你想要, 所以你打得更用力")
#   NE → precision/hit_rate (信噪比提升: "你看得更清楚")
#   5-HT → defense/SAN (感觉门控: "不重要的事被过滤掉了")
#   ACh → info_gather (注意力: "你注意到更多细节")

BRAINSTEM_COMMUNITY_GAIN_ESTIMATE = {
    # 脑干核团 → (社区, 增益类型, 增益系数)
    'PAG':      ('GREEN', 'defense', 1.3),
    'VTA':      ('GREEN', 'motivation', 1.5),
    '上丘':      ('GREEN', 'detection', 1.2),
    '中缝背核':   ('PINK', 'defense', 1.4),
    # ★ 2026-09-12 勘误：原写 YELLOW，与论文不符——论文 Table 1 把它列在 GREEN
    #   （与 PAG / VTA / 上丘同组）。依据 references/Hansen2024_脑干皮层功能层级_数据.md §五。
    '中缝正中核':  ('GREEN', 'defense', 1.1),
    '蓝斑':      ('PINK', 'force', 1.5),        # NE → 脊髓: 交感放大, 运动神经元增益
    '蓝斑_R':    ('PINK', 'force', 1.5),
    '黑质致密部':  ('GREEN', 'force', 1.4),      # DA → 背侧纹状体: 运动 vigor
    '黑质致密部_R': ('GREEN', 'force', 1.4),
    '脑桥网状核':  ('YELLOW', 'force', 1.2),     # 网状脊髓易化: 基础肌张力
    '小脑皮层':    ('N/A', 'force', 1.3),         # 内部模型: 力量预测校准；论文不覆盖


    # 复合/通路结构
    'VTA-NAcc':  ('GREEN', 'motivation', 1.5),
    '杏仁核-PAG': ('GREEN', 'defense', 1.4),
    '反射环路·PAG→杏仁核': ('GREEN', 'defense', 1.3),
    '反射环路·冻结反应': ('GREEN', 'defense', 1.2),
    '反射环路·快速闪避': ('GREEN', 'defense', 1.3),
}


# 非脑干区域的神经调质增益: 基于其已知的递质受体密度
# 皮层/皮下区域的增益类型由其功能角色决定
NON_BRAINSTEM_GAIN = {
    # === 运动输出系统 → force ===
    # M1 第5层 Betz 细胞 → 皮质脊髓束: 运动单位募集
    'M1': ('force', 1.5),
    # 壳核(CSTC感觉运动环路): 习惯化动作执行, 力量输出自动化
    '壳核': ('force', 1.3),
    '基底节间接通路': ('force', 1.1),
    # 苍白球: 基底节输出端, 门控运动——释放=可以动, 抑制=不能动
    '苍白球': ('force', 1.3),
    # 黑质致密部 → 背侧纹状体: DA 直接调制运动 vigor
    '黑质致密部': ('force', 1.4),
    '黑质致密部_R': ('force', 1.4),
    # 小脑皮层: 力量预测校准, 内部模型
    '小脑皮层': ('force', 1.3),
    # 脑桥网状核: 网状脊髓易化——基础肌张力/爆发力
    '脑桥网状核': ('force', 1.2),

    # === 动机/奖赏系统 → motivation (DA, "想要") ===
    'NAcc壳': ('motivation', 1.4),
    'NAcc核': ('motivation', 1.4),
    '伏隔核/NAcc': ('motivation', 1.4),
    '腹侧纹状体': ('motivation', 1.3),
    'VTA': ('motivation', 1.5),
    'VTA-NAcc': ('motivation', 1.5),

    # === 价值/决策系统 → motivation ===
    'OFC': ('motivation', 1.2),
    'vmPFC': ('motivation', 1.3),
    'DMN+OFC': ('motivation', 1.3),

    # === 恐惧/防御系统 → defense ===
    '杏仁核': ('defense', 1.5),
    '杏仁核-海马': ('defense', 1.4),
    'BNST': ('defense', 1.3),
    'PAG': ('defense', 1.3),

    # === 记忆/辨别 → precision ===
    '海马体 CA1': ('precision', 1.3),
    '海马体 CA3': ('precision', 1.3),

    # === 5-HT 防御/过滤 ===
    '中缝背核': ('defense', 1.4),
    '中缝正中核': ('defense', 1.1),
    '隔区': ('defense', 1.2),

    # === 执行控制 → precision (NE 在 PFC 的强投射) ===
    'dlPFC': ('precision', 1.5),
    'ACC': ('precision', 1.3),
    'ACC背侧': ('precision', 1.3),
    '额顶网络': ('precision', 1.4),
    '额极': ('precision', 1.3),
    '额上回': ('precision', 1.2),
    '额中回尾部': ('precision', 1.2),

    # === 语言 → 命名可以让动机/伤害直接兑现 ===
    'Broca区': ('motivation', 1.3),
    'Wernicke区': ('info', 1.2),

    # === 社会认知 → info ===
    'TPJ': ('info', 1.3),
    'mPFC': ('info', 1.2),
}


def neuromodulator_gain(region_name, category, level):
    """Hansen 2024 → 神经调质增益系数 + 增益类型"""
    # 先查脑干核团
    if region_name in BRAINSTEM_COMMUNITY_GAIN_ESTIMATE:
        comm, gain_type, coeff = BRAINSTEM_COMMUNITY_GAIN_ESTIMATE[region_name]
        return gain_type, coeff

    # 再查已知的皮层/皮下增益
    if region_name in NON_BRAINSTEM_GAIN:
        gain_type, coeff = NON_BRAINSTEM_GAIN[region_name]
        return gain_type, coeff

    # 默认: 基于层级推断
    if level is None:
        return 'neutral', 1.0
    elif level <= 1:
        return 'defense', 1.1
    elif level == 3 and category == 'cortical':
        # L3 皮层: M1→force, 其他感觉→info
        return 'info', 1.0
    elif level <= 3:
        return 'info', 1.0
    elif level <= 5:
        return 'precision', 1.2
    else:
        return 'neutral', 1.3  # L5: 全局（原L6整合层）, 无特定偏向但系数高


# ═══════════════════════════════════════════════════
# D. 髓鞘化同步模型 (Pajevic 2023)
# ═══════════════════════════════════════════════════

def myelination_sync(myelination):
    """
    髓鞘化同步函数: 不是线性缩放, 而是 sigmoid.
    前30%髓鞘化: 效果很小 (信号仍然不同步, 无法有效整合)
    40-60%: 快速增长 (信号开始同步到达, 下游能有效整合)
    80%+: 接近满效果 (信号精确同步)

    Pajevic 2023: 10-40ms 窗口内的少突胶质细胞响应决定了同步精度.
    初始(低髓鞘化)时传导延迟>40ms → 信号异步 → 下游无法整合.
    髓鞘化增长→传导延迟进入10-40ms窗口→信号同步→调制效果剧增.
    """
    # shift=0.4: 髓鞘化40%时达到sigmoid中点
    # steepness=8: 从20%到60%快速过渡
    return 1.0 / (1.0 + np.exp(-8.0 * (myelination - 0.4)))


# ═══════════════════════════════════════════════════
# 加载脑区数据
# ═══════════════════════════════════════════════════

def load_brain_regions():
    with open(ROOT / 'data/brain_regions.json') as f:
        d = json.load(f)

    regions = {}
    for name, r in d['regions'].items():
        regions[name] = {
            'name': name,
            'level': r.get('level'),
            'category': r.get('category', ''),
            'bfb_region': r.get('bfb_region') or '',
            'lobe': r.get('lobe', ''),
        }
    return regions


# ═══════════════════════════════════════════════════
# 链路定义 (同 v1)
# ═══════════════════════════════════════════════════

L0_LINKS = [
    ('应激反应·被动逃逸', ['PAG'], ['M1'], 'defense'),
    ('应激反应·冻结', ['反射环路·冻结反应'], ['M1'], 'defense'),
    ('应激反应·闪避', ['反射环路·快速闪避'], ['M1'], 'defense'),
    ('警觉', ['上丘'], [], 'detection'),
    ('忍耐·被动SAN盾', ['中缝背核'], [], 'defense'),
    ('忍耐·主动压制恐慌', ['中缝背核'], [], 'defense'),
    ('激活·蓝斑唤醒', ['蓝斑'], [], 'force'),          # NE → 脊髓: 交感放大
    ('趋向·动机方向', ['VTA'], ['NAcc壳'], 'motivation'),  # DA 动机突显
    ('熟练·自动化', ['小脑皮层'], ['壳核'], 'force'),     # 小脑内部模型: 力量校准
]

L1_LINKS = [
    ('恐惧条件化', ['杏仁核'], ['PAG'], 'defense'),
    ('恐惧·BNST焦虑', ['BNST'], ['蓝斑'], 'defense'),
    ('回忆·模式完成', ['海马体 CA1'], [], 'info'),
    ('辨别·模式分离', ['海马体 CA3'], [], 'precision'),
    ('识景·场景识别', ['海马旁回'], [], 'info'),
    ('期待·奖赏预期', ['伏隔核/NAcc', '腹侧纹状体'], ['VTA'], 'motivation'),
    ('失望·惩罚预期', ['缰核'], ['VTA'], 'defense'),
    ('满足·奖励终止', ['隔区'], ['中缝背核'], 'defense'),
    ('习惯化·CSTC捷径', ['壳核', '苍白球'], ['小脑皮层'], 'force'),  # CSTC感觉运动环路
]

L2_LINKS = [
    ('内感受·身体读取', ['前脑岛'], [], 'info'),
    ('共感·他人身体映射', ['前脑岛'], [], 'info'),
    ('冲突感知·异常检测', ['ACC', 'ACC背侧'], [], 'precision'),
    ('价值直觉·快速比较', ['OFC'], [], 'motivation'),  # OFC → 腹侧纹状体价值比较
    ('内省·SAN恢复', ['后扣带', '峡部扣带'], [], 'defense'),
    ('识人·社会读取', ['颞极', 'ACC吻侧'], [], 'info'),
]

L3_LINKS = [
    ('注视·视觉聚焦', ['枕叶 V1', '枕顶联合', '楔叶'], ['上丘'], 'info'),
    ('聆听·听觉聚焦', ['A1'], ['上丘'], 'info'),
    ('身体感知·体感精度', ['S1', '旁中央小叶'], ['前脑岛'], 'info'),
    ('执行动作·运动精度', ['M1'], [], 'precision'),
]

L4_LINKS = [
    ('识别·物体分类', ['颞下回', '纺锤体回', '外侧枕叶', '舌回'], [], 'info'),
    ('读意图·生物运动', ['颞上沟岸', '颞中回'], [], 'precision'),
    ('比喻·跨域映射', ['角回'], [], 'info'),
    ('想象·心理模拟', ['楔前叶', '顶内沟', '顶叶'], [], 'precision'),
]

L5_LINKS = [
    ('计划·多步序列', ['dlPFC', '额极', '额上回', '额中回尾部'], [], 'precision'),
    ('命名·语言固化', ['Broca区', 'Wernicke区', '弓状束', '颞上回'], [], 'motivation'),  # 命名强化动机
    ('换位·视角转换', ['TPJ', '缘上回', 'mPFC'], [], 'info'),
    ('决策·价值确认', ['vmPFC', 'OFC'], [], 'motivation'),  # 价值整合→动机确认
    ('控制·主动压制', ['dlPFC', '额顶网络', 'ACC背侧'], ['杏仁核', 'PAG'], 'precision'),
    ('自省·元认知', ['mPFC', '额上回'], ['后扣带'], 'defense'),
]

L6_LINKS = [
    ('叙事重构A·我不是受害者', ['前额叶极·DMN', 'DMN+OFC'], [], 'defense'),
    ('叙事重构B·我为他人而战', ['前额叶极·DMN', 'DMN+OFC'], [], 'motivation'),  # 叙事驱动的动机激增
    ('叙事重构C·我可以改变', ['前额叶极·DMN', 'DMN+OFC'], [], 'precision'),
    ('全脑协调·突破容量', ['前额叶极·FPN', '全脑整合'], [], 'precision'),
    ('裁决·网络切换', ['前额叶极·SN'], [], 'precision'),
]


# ═══════════════════════════════════════════════════
# 三因子计算
# ═══════════════════════════════════════════════════

def compute_link_params(link_name, source_names, gain_type_override, regions):
    """
    对每条链路计算三个因子:
      excitability: 调制天花板 [0, 1]
      priority: 结算优先级 [1-6]
      gain_type: 增益类型 (damage/precision/defense/info/automation)
      gain_coeff: 增益系数 [1.0-2.0]
    """
    # 收集所有源脑区的参数
    excitabilities = []
    priorities = []
    gain_types = []
    gain_coeffs = []

    for src_name in source_names:
        r = regions.get(src_name)
        if not r:
            continue
        cat = r['category']
        lvl = r['level']

        # Factor A: excitability
        exc = momi_excitability(cat, lvl, src_name)
        excitabilities.append(exc)

        # Factor B: priority
        pri = conduction_priority(cat, lvl)
        priorities.append(pri)

        # Factor C: neuromodulator gain
        gt, gc = neuromodulator_gain(src_name, cat, lvl)
        gain_types.append(gt)
        gain_coeffs.append(gc)

    # 聚合 (取中位数避免单个极端值主导)
    avg_exc = float(np.median(excitabilities)) if excitabilities else 0.35
    avg_pri = int(np.median(priorities)) if priorities else 4
    avg_gc = float(np.median(gain_coeffs)) if gain_coeffs else 1.0

    # gain_type: 最多出现的类型, 或被override
    if gain_type_override:
        primary_gain = gain_type_override
    elif gain_types:
        from collections import Counter
        primary_gain = Counter(gain_types).most_common(1)[0][0]
    else:
        primary_gain = 'neutral'

    # 调制天花板 = excitability × gain_coeff
    #   excitability: "这个脑区的递归加工能放大信号多少"
    #   gain_coeff: "神经调质将这个放大导向了哪种效果类型"
    ceiling = round(avg_exc * avg_gc, 3)
    ceiling = min(ceiling, 1.0)  # cap at 100%

    return {
        'excitability': round(avg_exc, 3),
        'priority': avg_pri,
        'gain_type': primary_gain,
        'gain_coeff': round(avg_gc, 3),
        'ceiling': ceiling,
        # 髓鞘化各阶段的实际调制值
        'myelination_curve': {
            'm0.1': round(ceiling * myelination_sync(0.1), 4),
            'm0.3': round(ceiling * myelination_sync(0.3), 4),
            'm0.5': round(ceiling * myelination_sync(0.5), 4),
            'm0.7': round(ceiling * myelination_sync(0.7), 4),
            'm0.9': round(ceiling * myelination_sync(0.9), 4),
            'm1.0': round(ceiling * myelination_sync(1.0), 4),
        }
    }


# ═══════════════════════════════════════════════════
# 效果类型 → 战斗公式映射
# ═══════════════════════════════════════════════════

GAIN_TYPE_MECHANICS = {
    'force': {
        'description': '运动输出放大 — 力量/爆发力',
        'formula': 'base_physical × (1 + min(Σ ceiling_i × sync(myelination_i), cap_force))',
        'affects': ['物理攻击.HP伤害', '打击力度'],
        'narrative': 'M1/皮质脊髓束/小脑/脑桥网状核 → "你的身体能做到什么程度"',
        'cap': 0.50,  # 身体有物理极限
        'stability': '高 (肌肉记忆不会今天会明天忘)',
    },
    'motivation': {
        'description': '动机驱动放大 — DA/NAcc/VTA 系统的"想要"转化为行动强度',
        'formula': 'base_physical × (1 + min(Σ ceiling_i × sync(myelination_i), cap_motivation))',
        'affects': ['物理攻击.HP伤害', '精神攻击.SAN伤害'],
        'narrative': 'VTA/NAcc/vmPFC → "你想做到什么程度"',
        'cap': 1.00,  # 动机可以让你突破身体极限(但伴随伤害风险)
        'stability': '低 (情境敏感: 打恨的人 vs 打路人, 力度不同)',
    },
    'precision': {
        'description': '精度/命中提升',
        'formula': 'base_hit_rate + Σ ceiling_i × sync(myelination_i) × 15%, capped at +50%',
        'affects': ['物理攻击.命中率', '精神攻击.命中率', '信息揭示精度'],
        'narrative': 'NE/蓝斑系统 — "你看得更清楚，做得更准"',
        'cap': 0.50,
        'stability': '中 (NE tonic/phasic 波动)',
    },
    'defense': {
        'description': '防御/SAN减免',
        'formula': 'incoming_damage × (1 - min(Σ ceiling_i × sync(myelination_i), 0.5))',
        'affects': ['受到物理伤害', '受到精神伤害', 'SAN消耗减免'],
        'narrative': '5-HT/中缝核系统 — "不重要的事被过滤掉了"',
        'cap': 0.50,
        'stability': '高 (被动护盾, 不消耗激活点)',
    },
    'info': {
        'description': '信息揭示数量/质量',
        'formula': '基础揭示1个属性 + floor(Σ ceiling_i × sync(myelination_i) × 3) 额外属性',
        'affects': ['敌方属性揭示数', '意图预测精度'],
        'narrative': 'ACh/皮层系统 — "你注意到更多细节"',
        'cap': 3,  # 额外属性数
        'stability': '高',
    },
    'automation': {
        'description': 'AP消耗减免',
        'formula': '技能AP = max(1, base_AP - floor(Σ ceiling_i × sync(myelination_i) × 3))',
        'affects': ['连续使用AP消耗', '冷却时间'],
        'narrative': '小脑/壳核CSTC环路 — "身体替你做了"',
        'cap': 'AP最低减至1',
        'stability': '高',
    },
    'neutral': {
        'description': '通用调制',
        'formula': 'base × (1 + Σ ceiling_i × sync(myelination_i) × 0.5), capped at +50%',
        'affects': ['所有效果'],
        'narrative': '通用增益',
        'cap': 0.50,
        'stability': '中',
    },
    'detection': {
        'description': '威胁检测',
        'formula': '威胁检测距离 + floor(Σ ceiling_i × sync(myelination_i) × 3)',
        'affects': ['检测范围', '警觉标记获取'],
        'narrative': '上丘 → "你感觉到有东西不对劲"',
        'cap': 3,
        'stability': '高',
    },
}


# ═══════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════

def main():
    regions = load_brain_regions()

    all_links = (L0_LINKS + L1_LINKS + L2_LINKS + L3_LINKS +
                 L4_LINKS + L5_LINKS + L6_LINKS)

    results = []
    for link in all_links:
        name = link[0]
        sources = link[1]
        gain_type = link[3] if len(link) > 3 else None

        params = compute_link_params(name, sources, gain_type, regions)

        # 确定源脑区的层级
        src_levels = []
        for s in sources:
            if s in regions and regions[s]['level'] is not None:
                src_levels.append(regions[s]['level'])
        src_level = max(src_levels) if src_levels else None

        results.append({
            'link_name': name,
            'source_regions': sources,
            'source_layer': src_level,
            'gain_type': params['gain_type'],
            'excitability': params['excitability'],
            'gain_coeff': params['gain_coeff'],
            'modulation_ceiling': params['ceiling'],
            'link_priority': params['priority'],
            'myelination_curve': params['myelination_curve'],
            'gain_mechanic': GAIN_TYPE_MECHANICS.get(params['gain_type'], GAIN_TYPE_MECHANICS['neutral']),
        })

    # 统计
    from collections import Counter
    print('=== 三因子模型 — 链路调制参数 ===')
    print(f'共 {len(results)} 条链路\n')

    print('按层级:')
    layer_ceils = defaultdict(list)
    for r in results:
        layer_ceils[r['source_layer']].append(r['modulation_ceiling'])
    for lvl in sorted(layer_ceils.keys(), key=lambda x: x or 99):
        ceils = layer_ceils[lvl]
        print(f'  L{lvl}: {len(ceils)} 条, ceiling mean={np.mean(ceils):.3f}, range=[{min(ceils):.3f}, {max(ceils):.3f}]')

    print('\n按增益类型:')
    gain_ceils = defaultdict(list)
    for r in results:
        gain_ceils[r['gain_type']].append(r['modulation_ceiling'])
    for gt in sorted(gain_ceils.keys()):
        ceils = gain_ceils[gt]
        print(f'  {gt}: {len(ceils)} 条, ceiling mean={np.mean(ceils):.3f}')

    print('\n按优先级:')
    pri_ceils = defaultdict(list)
    for r in results:
        pri_ceils[r['link_priority']].append(r['modulation_ceiling'])
    for pri in sorted(pri_ceils.keys()):
        ceils = pri_ceils[pri]
        links = [r['link_name'] for r in results if r['link_priority'] == pri]
        print(f'  priority {pri}: {len(ceils)} 条, ceiling mean={np.mean(ceils):.3f} — {links[:4]}...')

    # 保存 JSON
    output_json = ROOT / 'data/connectivity/link_modulation_ceiling_v2.json'
    output_data = {
        '_metadata': {
            'description': '三因子链路调制模型 — Momi2025 excitability × 脑干调质增益（估计）× Pajevic2023 myelination sync',
            'version': '2.0',
            'generated': '2026-07-27',
            'formula': 'ceiling = excitability × gain_coeff; actual = ceiling × sigmoid(myelination, shift=0.4, steep=8)',
            'factors': {
                'excitability': 'Momi et al. (2025) Nat Commun — cortical hierarchy of evoked response strength',
                'conduction_priority': 'TMS-fMRI effective connectivity + Hansen 2024 时间层级（文献依据）— link resolution order',
                'neuromodulator_gain': '脑干社区 → 效果类型专精。**增益系数为本仓人工估计**；'
                                   '社区划分与递质归属依 Hansen et al. (2024) Nat Neurosci '
                                   '（该数据集未被本脚本读取）',
                'myelination_sync': 'Pajevic et al. (2023) eLife — oligodendrocyte-mediated conduction delay synchronization',
            },
            'gain_type_mechanics': GAIN_TYPE_MECHANICS,
            'priority_rules': {
                1: '脑干反射 — 最先结算, 闪避/恐慌/基础防御',
                2: '边缘系统/初级感觉 — 情绪触发/感官输入',
                3: '旁边缘 — 突显检测/注意力分配',
                4: '高级单模态/白质通路 — 模式识别/分类',
                5: '跨模态皮层 — 认知框架/计划/语言',
                6: '全脑整合 — 最后结算, 叙事重构/裁决(改变全局规则)',
            },
        },
        'links': results,
    }

    with open(output_json, 'w') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f'\n✓ JSON → {output_json}')

    # 生成 MD
    gen_markdown(results)
    return results


def gen_markdown(results):
    lines = []
    lines.append('# 链路调制上限参考表 v2 — 三因子模型')
    lines.append('')
    lines.append('> **核心变更**: 不再使用 SC/FC 相关性。改用 Momi 2025 皮层兴奋性梯度 + 脑干调质增益（系数为本仓估计，社区划分依 Hansen 2024）+ Pajevic 2023 髓鞘化同步模型。')
    lines.append('>')
    lines.append('> **公式**: `调制天花板 = 兴奋性 × 增益系数`；`实际调制 = 天花板 × sigmoid髓鞘化(shift=0.4)`')
    lines.append('')
    lines.append('## 三因子速查')
    lines.append('')
    lines.append('| 因子 | 文献 | 测量内容 | 游戏映射 |')
    lines.append('|------|------|---------|---------|')
    lines.append('| **兴奋性** | Momi et al. (2025) *Nature Comms* | 颅内电刺激诱发电位强度 — 高阶网络~3×低阶网络 | 调制天花板: L5>L4>L3>L2>L1>L0 |')
    lines.append('| **传导速度** | TMS-fMRI 有效连接 + Hansen 2024 时间层级 | 刺激→下游响应延迟 (ms) | 结算优先级: 脑干(1) → 边缘(2) → 旁边缘(3) → 单模态(4) → 跨模态(5) |')
    lines.append('| **神经调质增益** | 社区划分依 Hansen et al. (2024) *Nature Neurosci*；**系数为本仓估计** | 5大社区 × 9种递质系统 | 效果类型专精: DA=伤害, NE=精度, 5-HT=防御, ACh=信息 |')
    lines.append('| **髓鞘化同步** | Pajevic et al. (2023) *eLife* | 少突胶质细胞 10-40ms 窗口传导同步 | 前30%几乎无效, 40-60%快速增长, 80%+满效(sigmoid) |')
    lines.append('')
    lines.append('## 增益类型 → 战斗公式')
    lines.append('')
    lines.append('| 增益类型 | 神经基础 | 影响效果 | 叠加上限 |')
    lines.append('|---------|---------|---------|---------|')
    lines.append('| **force** | M1/皮质脊髓束/小脑/脑桥网状核/蓝斑→脊髓 | 物理伤害(身体能力) | +50% |')
    lines.append('| **motivation** | VTA/NAcc/vmPFC DA系统 | 物理伤害(动机驱动) + 精神伤害 | +100% |')
    lines.append('| **precision** | NE/蓝斑→皮层系统 | 命中率 + 信息揭示精度 | +50% |')
    lines.append('| **defense** | 5-HT/中缝核系统 | 伤害减免 + SAN消耗减免 | -50% |')
    lines.append('| **info** | ACh/皮层系统 | 信息揭示数量 + 意图预测精度 | +3 额外属性 |')
    lines.append('| **automation** | 小脑/CSTC环路 | AP消耗减免 + 冷却减免 | AP最低减至1 |')
    lines.append('')
    lines.append('### 物理伤害双通道公式')
    lines.append('')
    lines.append('```')
    lines.append('物理攻击伤害 = base × (1 + force_mod + motivation_mod)')
    lines.append('')
    lines.append('force_mod = min(Σ force链路.ceiling × sync(myelination), 0.50)')
    lines.append('  → "你的身体能做到什么程度"')
    lines.append('  → 稳定, 可靠, 不受情境影响')
    lines.append('')
    lines.append('motivation_mod = min(Σ motivation链路.ceiling × sync(myelination), 1.00)')
    lines.append('  → "你想做到什么程度"')
    lines.append('  → 情境敏感: 对恐惧标记敌人+额外动机, 对友方-动机')
    lines.append('  → 高 motivation_mod 时: 伤害+但自身SAN消耗+ (用力过猛)')
    lines.append('```')
    lines.append('')
    lines.append('## 链路详细参数')
    lines.append('')
    lines.append('| 链路名称 | L | 增益类型 | 优先级 | exc | gain | ceiling | m0.3 | m0.5 | m0.7 | m1.0 |')
    lines.append('|---------|---|---------|--------|-----|------|---------|------|------|------|------|')

    for r in sorted(results, key=lambda x: (x['source_layer'] or 0, x['link_priority'], x['link_name'])):
        mc = r['myelination_curve']
        lines.append(
            f'| {r["link_name"]} | L{r["source_layer"]} | {r["gain_type"]} | {r["link_priority"]} | '
            f'{r["excitability"]:.3f} | {r["gain_coeff"]:.3f} | {r["modulation_ceiling"]:.3f} | '
            f'{mc["m0.3"]:.3f} | {mc["m0.5"]:.3f} | {mc["m0.7"]:.3f} | {mc["m1.0"]:.3f} |'
        )

    lines.append('')
    lines.append('> **髓鞘化解释 (sigmoid, shift=0.4, steep=8):**')
    lines.append('> - m0.1-m0.3: 刚学会——信号不同步, 几乎无调制效果')
    lines.append('> - m0.4-m0.6: 熟练——信号开始同步到达, 调制效果快速提升')
    lines.append('> - m0.7-m0.9: 精通——信号精确同步, 调制效果接近天花板')
    lines.append('> - m1.0: 完全髓鞘化——调制效果达到此链路的最大潜力')
    lines.append('')
    lines.append('## 结算顺序 (Priority Rules)')
    lines.append('')
    lines.append('同一回合内, 低 priority 的链路先结算:')
    lines.append('')
    lines.append('| Priority | 层级 | 典型链路 | 先结算什么 |')
    lines.append('|----------|------|---------|----------|')
    lines.append('| 1 | L0 脑干 | 应激反应, 警觉, 忍耐 | 闪避判定, 恐慌触发, SAN护盾 |')
    lines.append('| 2 | L1 边缘 + L3 感觉 | 恐惧条件化, 期待, 注视 | 情绪调制, 感官信息获取 |')
    lines.append('| 3 | L2 旁边缘 | 冲突感知, 内感受, 识人 | 异常检测, 阈值显示 |')
    lines.append('| 4 | L4 单模态 | 识别, 读意图, 想象 | 分类标签, 意图预测 |')
    lines.append('| 5 | L5 跨模态 | 计划, 命名, 控制, 决策, 叙事重构, 全脑协调, 裁决 | 认知框架, 伤害计算, 全局规则改变 |')
    lines.append('')
    lines.append('> **设计含义**: 身体反应(闪避/恐慌)永远比理性决策(计划/命名)先发生。你想压制恐惧→先用 L5 控制, 但 L0 的恐惧已经在 priority=1 时执行了——你得预判。')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('*生成: 2026-07-27 | 三因子模型 v2.0*')
    lines.append('*文献: Momi et al. (2025) Nat Commun, Hansen et al. (2024) Nat Neurosci（社区划分）, Pajevic et al. (2023) eLife；增益系数为本仓估计*')
    lines.append('*JSON: [link_modulation_ceiling_v2.json](../../data/connectivity/link_modulation_ceiling_v2.json)*')

    # ⚠️ 2026-09-12 记录：路径仍是 Phase 3 改名前的「技能树系统/」，该目录已不存在，
    #   故本脚本跑到 MD 生成一步必抛 FileNotFoundError（JSON 已先写出）。
    #   现行正典是 design/rules/skill-tree/modulation/链路调制上限参考表-v2.md。
    output_md = ROOT / '技能树系统/链路调制上限参考表-v2.md'
    with open(output_md, 'w') as f:
        f.write('\n'.join(lines))
    print(f'✓  MD → {output_md}')


if __name__ == '__main__':
    main()
