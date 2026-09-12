#!/usr/bin/env python3
"""
gen_modulation_ceiling.py — 从文献数据推导链路调制上限

数据来源:
  - ENIGMA 结构连接矩阵 (68×68 cortical + 14×68 subcortical-cortical)
  - Hansen et al. (2024) Nature Neuroscience — 脑干-皮层 FC 层级
  - Kroell (2024) 14 功能网络
  - 白质纤维束解剖数据

输出:
  - data/connectivity/link_modulation_ceiling.json — 每条合法链路的调制参数
  - 技能树系统/链路调制上限参考表.md — 人类可读的参考文档

公式:
  modulation_ceiling = sc_norm × layer_weight × direction_factor
  其中:
    sc_norm = min(sc_value / sc_p95, 1.0) 归一化到 [0, 1]
    layer_weight = 0.5 + 0.1 × target_layer (L0→0.5, L5→1.0)
    direction_factor = 1.0 (feedforward 上行) or 0.7 (feedback 下行)

  actual_modulation = ceiling × myelination (myelination ∈ [0, 1])
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent

# === 1. 加载数据 ===

def load_brain_regions():
    """加载 70 条目（50 解剖实体），映射到 ENIGMA DK 标签"""
    with open(ROOT / 'data/brain_regions.json') as f:
        d = json.load(f)

    regions = {}
    for name, r in d['regions'].items():
        bfb = r.get('bfb_region') or ''
        level = r.get('level')
        category = r.get('category', '')

        # 映射 bfb_region → ENIGMA cortical label (左半球前缀 L_)
        enigma_ctx = None
        enigma_sctx = None

        if bfb and bfb != 'N/A':
            # Cortical DK regions
            ctx_map = {
                'bankssts': 'L_bankssts', 'caudalanteriorcingulate': 'L_caudalanteriorcingulate',
                'caudalmiddlefrontal': 'L_caudalmiddlefrontal', 'cuneus': 'L_cuneus',
                'entorhinal': 'L_entorhinal', 'fusiform': 'L_fusiform',
                'inferiorparietal': 'L_inferiorparietal', 'inferiortemporal': 'L_inferiortemporal',
                'isthmuscingulate': 'L_isthmuscingulate', 'lateraloccipital': 'L_lateraloccipital',
                'lateralorbitofrontal': 'L_lateralorbitofrontal', 'lingual': 'L_lingual',
                'medialorbitofrontal': 'L_medialorbitofrontal', 'middletemporal': 'L_middletemporal',
                'parahippocampal': 'L_parahippocampal', 'paracentral': 'L_paracentral',
                'parsopercularis': 'L_parsopercularis', 'parsorbitalis': 'L_parsorbitalis',
                'parstriangularis': 'L_parstriangularis', 'pericalcarine': 'L_pericalcarine',
                'postcentral': 'L_postcentral', 'posteriorcingulate': 'L_posteriorcingulate',
                'precentral': 'L_precentral', 'precuneus': 'L_precuneus',
                'rostralanteriorcingulate': 'L_rostralanteriorcingulate',
                'rostralmiddlefrontal': 'L_rostralmiddlefrontal', 'superiorfrontal': 'L_superiorfrontal',
                'superiorparietal': 'L_superiorparietal', 'superiortemporal': 'L_superiortemporal',
                'supramarginal': 'L_supramarginal', 'frontalpole': 'L_frontalpole',
                'temporalpole': 'L_temporalpole', 'transversetemporal': 'L_transversetemporal',
                'insula': 'L_insula',
            }
            enigma_ctx = ctx_map.get(bfb)

        # Subcortical mapping (bfb_region → ENIGMA subcortical label)
        sctx_map = {
            'Amygdala': 'Lamyg',
            'Hippocampus': 'Lhippo',
            'Accumbens-area': 'Laccumb',
            'Caudate': 'Lcaud',
            'Putamen': 'Lput',
            'Pallidum': 'Lpal',
            'Thalamus-Proper': 'Lthal',
        }
        enigma_sctx = sctx_map.get(bfb)

        regions[name] = {
            'name': name,
            'level': level,
            'category': category,
            'bfb_region': bfb,
            'enigma_ctx': enigma_ctx,
            'enigma_sctx': enigma_sctx,
        }
    return regions


def load_enigma_matrices():
    """加载 ENIGMA 结构连接矩阵 (68×68 cortical + 14×68 subcortical-cortical)"""
    ctx_matrix = np.load(ROOT / 'data/connectivity/enigma_sc_ctx_matrix.npy')
    sctx_matrix = np.load(ROOT / 'data/connectivity/enigma_sc_sctx_matrix.npy')

    ctx_labels = list(np.load(ROOT / 'data/connectivity/enigma_sc_ctx_labels.npy', allow_pickle=True))
    sctx_labels = list(np.load(ROOT / 'data/connectivity/enigma_sc_sctx_labels.npy', allow_pickle=True))

    return {
        'ctx_matrix': ctx_matrix,
        'sctx_matrix': sctx_matrix,
        'ctx_labels': ctx_labels,
        'sctx_labels': sctx_labels,
        'sc_p95': float(np.percentile(ctx_matrix[ctx_matrix > 0], 95)),
        'sc_max': float(ctx_matrix.max()),
    }


def load_hansen_brainstem():
    """Hansen 2024 脑干核团→皮层 FC 定性数据

    由于我们没有原始 FC 矩阵，使用基于 Hansen 社区分类的估计值。
    GREEN社区(中脑)=跨模态皮层, PINK社区=扣带皮层(情绪调节),
    YELLOW社区=单模态皮层(感觉运动), BLUE社区=外侧跨模态(工作记忆)

    返回每个脑干核团的皮层连接强度估计值 (0-1 归一化)
    """
    # 基于 Hansen 2024 Table 1 + Fig.5 的社区赋值
    # 强度估计: 全脑最强hub(蓝斑,PAG) 用高值, 较小核团用中低值
    hansen = {
        # GREEN 社区 — 内侧跨模态皮层（自传记忆、社会认知）
        'PAG': {'community': 'GREEN', 'fc_strength': 0.85, 'note': '全脑最强hub之一, 皮层-脑干FC最高'},
        'VTA': {'community': 'GREEN', 'fc_strength': 0.80, 'note': 'GREEN社区核心, DA源头'},
        '上丘': {'community': 'GREEN', 'fc_strength': 0.70, 'note': 'GREEN社区, 视觉-运动接口'},
        '黑质致密部': {'community': 'GREEN', 'fc_strength': 0.65, 'note': 'GREEN社区, DA运动启动'},
        '黑质致密部_R': {'community': 'GREEN', 'fc_strength': 0.65, 'note': '同黑质致密部(右侧)'},

        # PINK 社区 — 扣带皮层（情绪调节、唤醒）
        '中缝背核': {'community': 'PINK', 'fc_strength': 0.75, 'note': 'PINK社区核心, 5-HT源头, 扣带连接hub'},
        '蓝斑': {'community': 'PINK', 'fc_strength': 0.90, 'note': '全脑最强hub, NE源头, 全脑投射'},
        '蓝斑_R': {'community': 'PINK', 'fc_strength': 0.90, 'note': '同蓝斑(右侧)'},

        # YELLOW 社区 — 单模态皮层（感觉/运动）
        '中缝正中核': {'community': 'YELLOW', 'fc_strength': 0.50, 'note': 'YELLOW社区, 海马/隔区投射'},
        '脑桥网状核': {'community': 'YELLOW', 'fc_strength': 0.45, 'note': 'YELLOW社区, 自主神经'},

        # 通路和复合结构 — 使用其端点核团的平均值
        'VTA-NAcc': {'community': 'GREEN', 'fc_strength': 0.78, 'note': 'VTA→NAcc DA通路'},
        '杏仁核-PAG': {'community': 'GREEN', 'fc_strength': 0.72, 'note': '杏仁核→PAG恐惧通路'},
        '反射环路·PAG→杏仁核': {'community': 'GREEN', 'fc_strength': 0.80, 'note': '防御环路'},
        '反射环路·冻结反应': {'community': 'GREEN', 'fc_strength': 0.75, 'note': 'vlPAG通路'},
        '反射环路·快速闪避': {'community': 'GREEN', 'fc_strength': 0.75, 'note': 'dlPAG→运动通路'},

        # 无独立Hansen数据的结构
        '小脑皮层': {'community': 'N/A', 'fc_strength': 0.55, 'note': '小脑-丘脑-皮层环路, 非Hansen数据, 估计值'},
    }
    return hansen


def load_white_matter_tracts():
    """加载白质纤维束数据，提取端点脑区对"""
    with open(ROOT / 'data/connectivity/white_matter_tracts.json') as f:
        d = json.load(f)

    tract_pairs = {}  # (region_a, region_b) → tract_info

    for category in ['association_tracts', 'commissural_tracts', 'projection_tracts', 'cerebellar_tracts']:
        tracts = d.get(category, [])
        for tract in tracts:
            endpoints = set()
            if 'endpoints' in tract:
                for ep in tract['endpoints']:
                    endpoints.add(ep)
            if 'connects' in tract:
                for c in tract['connects']:
                    endpoints.add(c)
            # 记录所有端点对
            eps = list(endpoints)
            for i in range(len(eps)):
                for j in range(i+1, len(eps)):
                    pair = tuple(sorted([eps[i], eps[j]]))
                    if pair not in tract_pairs:
                        tract_pairs[pair] = []
                    tract_pairs[pair].append(tract.get('name', 'unknown'))

    return tract_pairs


# === 2. 计算调制上限 ===

def get_enigma_sc(region_a, region_b, regions, enigma_data):
    """查找两个脑区之间的 ENIGMA 结构连接强度"""
    ra = regions.get(region_a)
    rb = regions.get(region_b)
    if not ra or not rb:
        return None

    ctx_labels = enigma_data['ctx_labels']
    ctx_matrix = enigma_data['ctx_matrix']
    sctx_labels = enigma_data['sctx_labels']
    sctx_matrix = enigma_data['sctx_matrix']

    # 尝试 cortical-cortical 连接
    if ra['enigma_ctx'] and rb['enigma_ctx']:
        try:
            ia = ctx_labels.index(ra['enigma_ctx'])
            ib = ctx_labels.index(rb['enigma_ctx'])
            val = max(ctx_matrix[ia, ib], ctx_matrix[ib, ia])
            if val > 0:
                return {'value': float(val), 'source': 'ENIGMA_ctx', 'pair': f'{ra["enigma_ctx"]}↔{rb["enigma_ctx"]}'}
        except ValueError:
            pass

    # 尝试 subcortical-cortical (a=subcortical, b=cortical)
    for sub_r, ctx_r in [(ra, rb), (rb, ra)]:
        if sub_r['enigma_sctx'] and ctx_r['enigma_ctx']:
            try:
                isub = sctx_labels.index(sub_r['enigma_sctx'])
                ictx = ctx_labels.index(ctx_r['enigma_ctx'])
                val = sctx_matrix[isub, ictx]
                if val > 0:
                    return {'value': float(val), 'source': 'ENIGMA_sctx',
                            'pair': f'{sub_r["enigma_sctx"]}→{ctx_r["enigma_ctx"]}'}
            except ValueError:
                pass

    # 尝试 subcortical-subcortical (通过共同皮层连接代理——两个subcortical区域的间接连接)
    if ra['enigma_sctx'] and rb['enigma_sctx']:
        try:
            isub_a = sctx_labels.index(ra['enigma_sctx'])
            isub_b = sctx_labels.index(rb['enigma_sctx'])
            # 间接: 取两个 subcortical 到所有皮层的连接强度的空间相关性
            vec_a = sctx_matrix[isub_a, :]
            vec_b = sctx_matrix[isub_b, :]
            # 用它们共有的皮层连接强度之和
            shared = np.sum(np.minimum(vec_a, vec_b))
            if shared > 0:
                return {'value': float(shared), 'source': 'ENIGMA_sctx_indirect',
                        'pair': f'{ra["enigma_sctx"]}↔{rb["enigma_sctx"]}(via ctx)'}
        except ValueError:
            pass

    return None


def get_brainstem_strength(region_name, hansen_data):
    """获取脑干核团的连接强度估计"""
    if region_name in hansen_data:
        return hansen_data[region_name]['fc_strength']
    return None


NORMALIZATION_REF = {
    'ENIGMA_p95': None,  # 运行时填充
    'hansen_max': 0.90,  # 蓝斑 FC 强度
}


def normalize_sc(value, source):
    """将原始 SC 值归一化到 [0, 1]"""
    if source.startswith('ENIGMA'):
        return min(value / NORMALIZATION_REF['ENIGMA_p95'], 1.0)
    elif source.startswith('Hansen'):
        return min(value / NORMALIZATION_REF['hansen_max'], 1.0)
    elif source == 'tract_known':
        return 0.50  # 已知白质通路但无定量SC
    elif source == 'estimated':
        return 0.30  # 无直接数据, 基于功能相近性估计
    else:
        return 0.25  # fallback


def layer_weight(layer):
    """层级权重: 高层链路的调制天花板更高"""
    # L0=0.50, L1=0.60, L2=0.70, L3=0.80, L4=0.90, L5=1.00
    if layer is None:
        return 0.70
    return 0.50 + 0.10 * layer


# === 3. 定义合法链路 ===

# 所有 L0-L5 文档中定义的"技能/操作"本质上就是链路调制的具名形式。
# 每条操作对应一条或多条链路: 源脑区 → 目标脑区(对下层脑区的调制)
# 我们用"操作"名称作为链路标识符。

# L0 基底操作: 脑干核团 → 直接调制效果
L0_LINKS = [
    # (操作名, 源脑区, [目标脑区], 方向, 效果类型)
    ('应激反应_被动', 'PAG', ['M1'], 'feedforward', 'defense'),
    ('应激反应_被动', '杏仁核-PAG', ['PAG'], 'feedforward', 'defense'),
    ('警觉', '上丘', ['PAG'], 'feedforward', 'detection'),
    ('忍耐_被动', '中缝背核', [], 'modulation', 'san_shield'),
    ('忍耐_主动', '中缝背核', ['ACC'], 'feedback', 'panic_suppress'),
    ('激活', '蓝斑', [], 'broadcast', 'arousal'),
    ('趋向', 'VTA', ['NAcc壳'], 'feedforward', 'motivation'),
    ('熟练', '小脑皮层', ['壳核'], 'feedforward', 'automation'),
]

# L1 调制: 边缘系统 → L0 调制
L1_LINKS = [
    ('恐惧条件化', '杏仁核', ['PAG'], 'feedback', 'threshold_mod'),
    ('恐惧条件化_BNST', 'BNST', ['蓝斑'], 'feedback', 'anxiety'),
    ('回忆', '海马体 CA1', ['上丘'], 'feedback', 'detection_boost'),
    ('辨别', '海马体 CA3', ['杏仁核'], 'feedback', 'false_alarm_reduce'),
    ('识景', '海马旁回', ['PAG'], 'feedback', 'context_mod'),
    ('期待', ['伏隔核/NAcc', '腹侧纹状体'], ['VTA'], 'feedback', 'approach_boost'),
    ('失望', '缰核', ['VTA'], 'feedback', 'avoidance_boost'),
    ('满足', '隔区', ['中缝背核'], 'feedback', 'san_boost'),
    ('习惯化', ['壳核', '苍白球'], ['小脑皮层'], 'feedback', 'ap_reduce'),
]

# L2 调制: 旁边缘 → L0/L1 调制
L2_LINKS = [
    ('内感受', '前脑岛', ['杏仁核'], 'feedback', 'threshold_info'),
    ('共感', '前脑岛', ['ACC'], 'feedback', 'empathy'),
    ('冲突感知', ['ACC', 'ACC背侧'], ['杏仁核'], 'feedback', 'conflict_detect'),
    ('价值直觉', 'OFC', ['腹侧纹状体'], 'feedback', 'value_compare'),
    ('内省', ['后扣带', '峡部扣带'], [], 'internal', 'san_recover'),
    ('识人', ['颞极', 'ACC吻侧'], ['杏仁核'], 'feedback', 'social_read'),
]

# L3 操作: 感觉皮层 → L2/L0 信息供给
L3_LINKS = [
    ('注视', ['枕叶 V1', '枕顶联合', '楔叶'], ['上丘'], 'feedforward', 'info_gather'),
    ('聆听', 'A1', ['上丘'], 'feedforward', 'info_gather'),
    ('身体感知', ['S1', '旁中央小叶'], ['前脑岛'], 'feedforward', 'body_info'),
    ('执行动作', 'M1', [], 'feedforward', 'precision'),
]

# L4 操作: 高级单模态 → L3/L2/L1 分类
L4_LINKS = [
    ('识别', ['颞下回', '纺锤体回', '外侧枕叶', '舌回'], ['枕叶 V1', '杏仁核'], 'feedback', 'classify'),
    ('读意图', ['颞上沟岸', '颞中回'], ['上丘'], 'feedforward', 'intent_read'),
    ('比喻', '角回', ['dlPFC'], 'feedback', 'cross_domain'),
    ('想象', ['楔前叶', '顶内沟', '顶叶'], ['dlPFC'], 'feedback', 'simulate'),
]

# L5 操作: 跨模态 → L4/L3/L2/L1/L0 认知框架 + 原L6整合操作（2026-08-07 Grilling #25 L6删除后并入L5）
L5_LINKS = [
    ('计划', ['dlPFC', '额极', '额上回', '额中回尾部'], ['M1', '壳核'], 'feedback', 'plan'),
    ('命名', ['Broca区', 'Wernicke区', '弓状束', '颞上回'], ['纺锤体回'], 'feedback', 'naming'),
    ('换位', ['TPJ', '缘上回', 'mPFC'], ['颞上沟岸', 'ACC吻侧'], 'feedback', 'perspective'),
    ('决策', ['vmPFC', 'OFC'], ['壳核', '腹侧纹状体'], 'feedback', 'decide'),
    ('控制', ['dlPFC', '额顶网络', 'ACC背侧'], ['杏仁核', 'PAG'], 'feedback', 'suppress'),
    ('自省', ['mPFC', '额上回'], ['后扣带'], 'feedback', 'metacog'),
    # ── 原L6操作（#25 L6删除 → L5吸收）──
    ('叙事重构', ['前额叶极·DMN', 'DMN+OFC'], [], 'global', 'narrative'),
    ('全脑协调', ['前额叶极·FPN', '全脑整合'], [], 'global', 'coordinate'),
    ('裁决', ['前额叶极·SN'], [], 'global', 'arbitrate'),
]


# === 4. 主计算 ===

def compute_all_links():
    regions = load_brain_regions()
    enigma_data = load_enigma_matrices()
    hansen_data = load_hansen_brainstem()
    tract_pairs = load_white_matter_tracts()

    NORMALIZATION_REF['ENIGMA_p95'] = enigma_data['sc_p95']

    all_links = (L0_LINKS + L1_LINKS + L2_LINKS + L3_LINKS +
                 L4_LINKS + L5_LINKS)

    results = []

    for link in all_links:
        name = link[0]
        sources = link[1] if isinstance(link[1], list) else [link[1]]
        targets = link[2] if isinstance(link[2], list) else ([link[2]] if link[2] else [])
        direction = link[3]
        effect_type = link[4]

        # 确定源脑区的层级
        src_levels = [regions[s]['level'] for s in sources if s in regions]
        src_level = max(src_levels) if src_levels else None

        # 收集所有 (source, target) 对之间的 SC
        sc_values = []
        sc_sources = []

        for src in sources:
            for tgt in targets:
                sc = get_enigma_sc(src, tgt, regions, enigma_data)
                if sc:
                    sc_values.append(sc['value'])
                    sc_sources.append(f'ENIGMA:{sc["source"]}:{sc["pair"]}')
                else:
                    # 尝试脑干数据
                    bs_src = get_brainstem_strength(src, hansen_data)
                    bs_tgt = get_brainstem_strength(tgt, hansen_data)
                    if bs_src or bs_tgt:
                        bs_val = max(bs_src or 0, bs_tgt or 0)
                        sc_values.append(bs_val * 3.0)  # 缩放到 ENIGMA 尺度
                        sc_sources.append(f'Hansen2024:{src}↔{tgt}')
                    else:
                        # 检查白质纤维束
                        pair = tuple(sorted([src, tgt]))
                        if pair in tract_pairs:
                            sc_values.append(enigma_data['sc_p95'] * 0.4)  # 中等估计
                            sc_sources.append(f'tract_known:{tract_pairs[pair][0]}')
                        else:
                            sc_values.append(enigma_data['sc_p95'] * 0.15)  # 最低估计
                            sc_sources.append('estimated')

        if not sc_values:
            sc_values = [enigma_data['sc_p95'] * 0.10]
            sc_sources = ['fallback']

        avg_sc = np.mean(sc_values)
        max_sc = max(sc_values)

        # 归一化
        sources_unique = set(s.replace('ENIGMA:', '').split(':')[0] for s in sc_sources)

        # 确定主要数据来源类型
        if any('ENIGMA_ctx' in s for s in sc_sources):
            primary_source = 'ENIGMA_cortical'
        elif any('ENIGMA_sctx' in s for s in sc_sources):
            primary_source = 'ENIGMA_subcortical'
        elif any('Hansen' in s for s in sc_sources):
            primary_source = 'Hansen2024_brainstem'
        elif any('tract_known' in s for s in sc_sources):
            primary_source = 'white_matter_tract'
        else:
            primary_source = 'estimated'

        sc_norm = normalize_sc(avg_sc, primary_source)
        lw = layer_weight(src_level)
        dir_factor = 1.0 if direction == 'feedforward' else 0.7

        ceiling = round(sc_norm * lw * dir_factor, 3)

        # 计算髓鞘化范围
        # 髓鞘化 0.0 → 调制 = 0 (刚接触, 链路未髓鞘化)
        # 髓鞘化 0.3 → 调制 = ceiling × 0.3 (基础髓鞘化)
        # 髓鞘化 0.6 → 调制 = ceiling × 0.6 (中等髓鞘化)
        # 髓鞘化 1.0 → 调制 = ceiling (完全髓鞘化)

        results.append({
            'link_name': name,
            'effect_type': effect_type,
            'source_regions': sources,
            'target_regions': targets,
            'direction': direction,
            'source_layer': src_level,
            'modulation_ceiling': ceiling,
            'myelination_range': {
                'none (0.0)': 0.0,
                'light (0.3)': round(ceiling * 0.3, 3),
                'moderate (0.6)': round(ceiling * 0.6, 3),
                'full (1.0)': ceiling,
            },
            'data_source': primary_source,
            'raw_sc_mean': round(float(avg_sc), 3),
            'raw_sc_max': round(float(max_sc), 3),
            'sc_details': sc_sources,
        })

    return results, regions, enigma_data


# === 5. 按效果类型汇总调制系数 ===

EFFECT_TYPE_GROUPS = {
    'damage_physical': {
        'description': '物理伤害加成',
        'target_actions': ['物理攻击'],
        'links': ['期待', '价值直觉', '决策', '命名', '叙事重构B'],
    },
    'damage_mental': {
        'description': '精神伤害加成',
        'target_actions': ['精神攻击'],
        'links': ['激活', '期待', '决策', '命名'],
    },
    'defense_physical': {
        'description': '物理防御加成',
        'target_actions': ['防御'],
        'links': ['身体感知', '决策', '想象'],
    },
    'hit_rate': {
        'description': '命中率加成',
        'target_actions': ['物理攻击', '精神攻击'],
        'links': ['执行动作', '读意图'],
    },
    'dodge': {
        'description': '闪避率加成',
        'target_actions': ['防御'],
        'links': ['应激反应_被动', '警觉', '回忆', '读意图'],
    },
    'san_recovery': {
        'description': 'SAN 恢复',
        'target_actions': [],
        'links': ['满足', '内省', '叙事重构A'],
    },
    'threshold_mod': {
        'description': '触发阈值偏移',
        'target_actions': [],
        'links': ['恐惧条件化', '识景', '辨别', '自省'],
    },
    'ap_reduction': {
        'description': 'AP 消耗减免',
        'target_actions': [],
        'links': ['熟练', '习惯化', '期待', '比喻'],
    },
}


# === 6. 主函数 ===

def main():
    results, regions, enigma_data = compute_all_links()

    # 保存 JSON
    output_json = ROOT / 'data/connectivity/link_modulation_ceiling.json'

    # 添加元数据
    output_data = {
        '_metadata': {
            'description': '链路调制上限 — 从 ENIGMA SC + Hansen 2024 推导',
            'formula': 'modulation_ceiling = sc_norm × layer_weight × direction_factor',
            'sc_normalization': {
                'enigma_p95': round(NORMALIZATION_REF['ENIGMA_p95'], 3),
                'enigma_max': round(float(enigma_data['sc_max']), 3),
                'hansen_max': NORMALIZATION_REF['hansen_max'],
            },
            'layer_weights': {f'L{i}': round(0.50 + 0.10 * i, 2) for i in range(7)},
            'direction_factors': {'feedforward': 1.0, 'feedback': 0.7, 'broadcast': 1.0, 'modulation': 0.7, 'internal': 0.5, 'global': 1.0},
            'myelination_note': 'actual_modulation = ceiling × myelination (myelination ∈ [0,1])',
            'generated': '2026-07-27',
        },
        'links': results,
        'effect_type_groups': EFFECT_TYPE_GROUPS,
    }

    with open(output_json, 'w') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f'✓ 已生成 {output_json}')
    print(f'  共 {len(results)} 条链路')

    # 按层级统计
    from collections import Counter
    layer_counts = Counter(r['source_layer'] for r in results)
    for lvl in sorted(layer_counts.keys(), key=lambda x: x or 99):
        entries = [r for r in results if r['source_layer'] == lvl]
        avg_c = np.mean([r['modulation_ceiling'] for r in entries])
        print(f'  L{lvl}: {layer_counts[lvl]} 条, 平均 ceiling={avg_c:.3f}')

    # 按数据来源统计
    source_counts = Counter(r['data_source'] for r in results)
    for src, cnt in source_counts.most_common():
        entries = [r for r in results if r['data_source'] == src]
        avg_c = np.mean([r['modulation_ceiling'] for r in entries])
        print(f'  {src}: {cnt} 条, 平均 ceiling={avg_c:.3f}')

    # 生成 Markdown 参考表
    gen_markdown(results, output_json)

    return results


def gen_markdown(results, json_output):
    """生成人类可读的 Markdown 参考表"""
    lines = []
    lines.append('# 链路调制上限参考表')
    lines.append('')
    lines.append('> 每条链路的最大调制效果（modulation ceiling）由 ENIGMA 结构连接强度、Hansen 2024 脑干-皮层 FC、白质纤维束解剖数据推导而来。')
    lines.append('> ')
    lines.append('> **公式**: `调制上限 = SC_norm × 层级权重 × 方向因子`')
    lines.append('> ')
    lines.append('> **实际调制** = `调制上限 × 髓鞘化程度` (髓鞘化 ∈ [0, 1])')
    lines.append('')
    lines.append('## 参数速查')
    lines.append('')
    lines.append('| 参数 | 值 | 说明 |')
    lines.append('|------|-----|------|')
    lines.append(f'| ENIGMA SC p95 | {NORMALIZATION_REF["ENIGMA_p95"]:.2f} | 结构连接 95 百分位 (归一化分母) |')
    lines.append('| 层级权重 | L0=0.50, L1=0.60, ..., L5=1.00 | 高层链路的调制天花板更高 |')
    lines.append('| 方向因子 | 上行1.0, 下行0.7, 广播1.0, 全局1.0 | 下行调制更"费力" |')
    lines.append('| 髓鞘化缩放 | 0.0(无) → 1.0(满) | 线性缩放调制上限 |')
    lines.append('')

    # 按层级分组输出
    lines.append('## 链路调制上限表')
    lines.append('')
    lines.append('| 链路名称 | 层级 | 类型 | 方向 | ceiling | 髓鞘化0.3 | 髓鞘化0.6 | 髓鞘化1.0(满) | 数据来源 |')
    lines.append('|---------|------|------|------|---------|----------|----------|-------------|---------|')

    for r in sorted(results, key=lambda x: (x['source_layer'] or 0, x['link_name'])):
        mye = r['myelination_range']
        lines.append(
            f'| {r["link_name"]} | L{r["source_layer"]} | {r["effect_type"]} | {r["direction"]} | '
            f'{r["modulation_ceiling"]:.3f} | {mye["light (0.3)"]:.3f} | '
            f'{mye["moderate (0.6)"]:.3f} | {mye["full (1.0)"]:.3f} | '
            f'{r["data_source"]} |'
        )

    lines.append('')
    lines.append('## 效果类型汇总')
    lines.append('')
    lines.append('将 ceiling 值映射到游戏中的百分比加成:')
    lines.append('')
    lines.append('| 效果类别 | 关联链路 | 叠加方式 | 最大累计 |')
    lines.append('|---------|---------|---------|---------|')

    for group_name, group in EFFECT_TYPE_GROUPS.items():
        group_links = [r for r in results if r['link_name'] in group['links']]
        if group_links:
            max_sum = round(sum(r['modulation_ceiling'] for r in group_links), 3)
            capped = min(max_sum, 1.0)
            link_names = ', '.join(r['link_name'] for r in group_links)
            lines.append(f'| {group_name} ({group["description"]}) | {link_names} | 加性 | {capped:.0%} (raw: {max_sum:.0%}) |')

    lines.append('')
    lines.append('> **叠加规则**: 同效果类型内的链路调制**加性叠加**，上限 100%。')
    lines.append('> **髓鞘化缩放**: 每条链路的实际调制 = ceiling × 髓鞘化程度。髓鞘化 0.3 = 30% 效果, 0.6 = 60%, 1.0 = 满效果。')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('*生成: 2026-07-27 | 数据来源: ENIGMA Toolbox HCP SC, Hansen et al. (2024) Nat Neurosci, Kroell (2024)*')
    lines.append(f'*JSON: [link_modulation_ceiling.json](../data/connectivity/link_modulation_ceiling.json)*')

    output_md = ROOT / '技能树系统/链路调制上限参考表.md'
    with open(output_md, 'w') as f:
        f.write('\n'.join(lines))
    print(f'✓ 已生成 {output_md}')


if __name__ == '__main__':
    main()
