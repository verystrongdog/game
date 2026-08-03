#!/usr/bin/env python3
"""构建 region_name_map.json — 89 脑区三层 ID 映射表 (D25/D13/D15)

功能: 为 89 脑区生成 functional_id（英文唯一主键）+ dk_name（解剖映射）+ zh_name（显示）
输入: data/brain_regions.json
输出: data/connectivity/region_name_map.json
校验: functional_id 全局唯一、89 全覆盖、is_design_node 标记
"""
import json
import sys

# ── 人工审核命名表 (zh_name → functional_id) ──
# DK 皮层区: DK 名 PascalCase + 消歧后缀
# 脑干核团: 文献标准名完整词
# 白质通路: Catani 图谱名或功能语义
# 抽象节点: 功能语义 + is_design_node
NAMING = {
    # ── 皮层 (DK 名 PascalCase) ──
    'A1': 'TransverseTemporal',
    'ACC': 'AnteriorCingulateCortex',
    'ACC吻侧': 'RostralAnteriorCingulateCortex',
    'ACC背侧': 'AnteriorCingulateCortexDorsal',
    'Broca区': 'ParsOpercularis',
    'DMN+OFC': 'MedialOrbitalPrefrontalDMN',
    'M1': 'Precentral',
    'OFC': 'LateralOrbitofrontal',
    'S1': 'Postcentral',
    'TPJ': 'SupramarginalTPJ',
    'Wernicke区': 'SuperiorTemporalWernicke',
    'dlPFC': 'RostralMiddleFrontalDLPFC',
    'mPFC': 'SuperiorFrontalMPFC',
    'vmPFC': 'MedialOrbitalPrefrontalVMPFC',
    '内嗅皮层': 'Entorhinal',
    '前脑岛': 'Insula',
    '前额叶极': 'FrontalPole',
    '前额叶极·DMN': 'FrontalPoleDMN',
    '前额叶极·FPN': 'FrontalPoleFPN',
    '前额叶极·SN': 'FrontalPoleSN',
    '后扣带': 'PosteriorCingulate',
    '外侧枕叶': 'LateralOccipital',
    '峡部扣带': 'IsthmusCingulate',
    '旁中央小叶': 'Paracentral',
    '枕叶 V1': 'Pericalcarine',
    '枕顶联合': 'LateralOccipitalOccipitoParietal',
    '楔前叶': 'Precuneus',
    '楔叶': 'Cuneus',
    '海马旁回': 'Parahippocampal',
    '纺锤体回': 'Fusiform',
    '缘上回': 'Supramarginal',
    '舌回': 'Lingual',
    '角回': 'InferiorParietalAngular',
    '顶内沟': 'SuperiorParietal',
    '顶叶': 'InferiorParietal',
    '额上回': 'SuperiorFrontal',
    '额中回尾部': 'CaudalMiddleFrontal',
    '额极': 'FrontalPoleExtreme',
    '颞上回': 'SuperiorTemporal',
    '颞上沟': 'SuperiorTemporalSulcus',
    '颞上沟岸': 'BanksSTS',
    '颞下回': 'InferiorTemporal',
    '颞中回': 'MiddleTemporal',
    '颞极': 'TemporalPole',
    # ── 皮层下 (DK 名) ──
    'BNST': 'BedNucleusStriaTerminalis',
    'NAcc壳': 'AccumbensShell',
    'NAcc核': 'AccumbensCore',
    '下丘脑': 'Hypothalamus',
    '丘脑': 'Thalamus',
    '丘脑枕': 'ThalamusPulvinar',
    '伏隔核/NAcc': 'NucleusAccumbens',
    '小脑皮层': 'CerebellumCortex',
    '尾状核': 'Caudate',
    '杏仁核': 'Amygdala',
    '杏仁核-海马': 'AmygdalaHippocampus',
    '海马体 CA1': 'HippocampusCA1',
    '海马体 CA3': 'HippocampusCA3',
    '纹状体基质': 'StriatumMatrix',
    '缰核': 'Habenula',
    '腹侧纹状体': 'VentralStriatum',
    '苍白球': 'Pallidum',
    '隔区': 'SeptalRegion',
    '壳核': 'Putamen',
    '基底节间接通路': 'BasalGangliaIndirectPathway',
    # ── 脑干核团 (文献标准名完整词) ──
    'PAG': 'PeriaqueductalGray',
    'VTA': 'VentralTegmentalArea',
    'VTA-NAcc': 'VentralTegmentalAreaNAccPathway',
    '上丘': 'SuperiorColliculus',
    '中缝正中核': 'MedianRapheNucleus',
    '中缝背核': 'DorsalRapheNucleus',
    '反射环路·PAG→杏仁核': 'ReflexPAGAmygdala',
    '反射环路·冻结反应': 'ReflexFreeze',
    '反射环路·快速闪避': 'ReflexEscape',
    '杏仁核-PAG': 'AmygdalaPAGPathway',
    '脑桥网状核': 'PontineReticularNucleus',
    '蓝斑': 'LocusCoeruleus',
    '蓝斑_R': 'LocusCoeruleusRight',
    '黑质致密部': 'SubstantiaNigraParsCompacta',
    '黑质致密部_R': 'SubstantiaNigraParsCompactaRight',
    # ── 白质通路 (Catani 图谱名或功能语义) ──
    'mPFC-杏仁核': 'MPFCAmygdalaPathway',
    'vmPFC-TPJ': 'VMPFCTPJPathway',
    '前额叶-海马': 'PrefrontalHippocampalPathway',
    '岛叶-ACC': 'InsulaCingulumPathway',
    '岛叶-ACC-VTA': 'InsulaACCVTAPathway',
    '岛叶-PFC-杏仁核': 'InsulaPFCAmygdalaPathway',
    '岛叶-vmPFC': 'InsulaVMPFCPathway',
    '弓状束': 'ArcuateFasciculus',
    # ── 设计抽象节点 ──
    '全脑整合': 'WholeBrainIntegration',
    '额顶网络': 'FrontoparietalControlNetwork',
}

# is_design_node 清单（无解剖实体，校验时跳过空间断言）
DESIGN_NODES = {
    '反射环路·PAG→杏仁核', '反射环路·冻结反应', '反射环路·快速闪避',
    '全脑整合', '额顶网络', '杏仁核-PAG', 'VTA-NAcc',
}


def main():
    with open('data/brain_regions.json') as f:
        data = json.load(f)
    regions = data['regions']

    errors = []
    # 1. 覆盖检查
    missing = set(regions) - set(NAMING)
    extra = set(NAMING) - set(regions)
    if missing:
        errors.append(f"未命名脑区: {missing}")
    if extra:
        errors.append(f"命名表多余: {extra}")

    # 2. functional_id 唯一性
    from collections import Counter
    dup = {k: v for k, v in Counter(NAMING.values()).items() if v > 1}
    if dup:
        errors.append(f"functional_id 重复: {dup}")

    # 3. 生成输出
    name_map = {}
    for zh, fid in NAMING.items():
        r = regions[zh]
        entry = {
            'zh_name': zh,
            'functional_id': fid,
            'dk_name': r.get('bfb_region'),  # 一对多（无 bfb_region 的为 None）
            'category': r.get('category'),
            'level': r.get('level'),
            'is_design_node': zh in DESIGN_NODES,
        }
        # 左右脑干合并: 蓝斑_R → hemisphere R
        if zh.endswith('_R'):
            entry['hemisphere'] = 'R'
        name_map[fid] = entry

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)

    out = {
        '_description': '89 脑区三层 ID 映射表 (D25) — functional_id 唯一主键 / dk_name 解剖映射(一对多) / zh_name 显示层',
        '_rules': [
            'functional_id: 英文唯一主键 (D15 完整词拼接 + D25 消歧后缀)',
            'dk_name: DK 图谱解剖映射，多 functional_id 可共享一个 dk_name',
            'is_design_node: true = 无解剖实体（校验时跳过空间断言）',
        ],
        'regions': name_map,
    }
    with open('data/connectivity/region_name_map.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(name_map)} 脑区 → data/connectivity/region_name_map.json")
    print(f"   is_design_node: {sum(1 for e in name_map.values() if e['is_design_node'])}")


if __name__ == '__main__':
    main()
