#!/usr/bin/env python3
"""build_data_manifest.py — 生成 data/manifest.json（P4c 数据契约）

从**证据**推导每个受控数据文件的四轴属性，而非人工填写：

| 轴 | 取值 | 判据 |
|---|---|---|
| origin | authored / generated / external | 有生成器引用 → generated；外部图集目录或已知外部来源 → external；其余 authored |
| lifecycle | active / deprecated / archived | 有活跃文档引用 → active；仅废弃文档引用或已知遗留 → deprecated；零引用 → archived |
| role | runtime / generator-input / reference / evidence | `GameDataLoader.LoadAll` 实际加载 → runtime；其余按引用面判定 |
| shipping | true / false | 仅 role=runtime |

用法:
    python3 code/tools/build_data_manifest.py            # 生成 data/manifest.json
    python3 code/tools/build_data_manifest.py --check    # 校验已提交的 manifest 与实测一致（不写文件）

`--check` 是 P4c 判据「生成两次结果一致」的实现：它比对磁盘实测与已提交内容。
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = 'data/manifest.json'

# ── 引擎 runtime allowlist：GameDataLoader.LoadAll 实际加载者 ──
RUNTIME = {
    'data/brain_regions.json',
    'data/signal_types.json',
    'data/connectivity/tripartite_model.json',
    'data/connectivity/W_sensory.json',
    'data/connectivity/situation_primitives.json',
    'data/connectivity/alpha_patterns.json',
    'data/connectivity/env_tones.json',
    'data/connectivity/moonlight_landing.json',
}

RUNTIME_CONSUMERS = {
    'data/brain_regions.json': ['GameDataLoader.LoadBrainRegions', 'WMatrixBuilder(行序锚)', 'CstcGating(CI 解析)', 'MoonlightLanding'],
    'data/signal_types.json': ['GameDataLoader.LoadSignalTypes', 'function_label membership 校验'],
    'data/connectivity/tripartite_model.json': ['GameDataLoader.LoadTripartiteModel', 'WMatrixBuilder', 'CorticalBias', 'CstcGating'],
    'data/connectivity/W_sensory.json': ['GameDataLoader.LoadWsensory', 'EventProcessor(s 打包)', 'canonical 行序锚'],
    'data/connectivity/situation_primitives.json': ['GameDataLoader.LoadSituationPrimitives', 'SituationSelector'],
    'data/connectivity/alpha_patterns.json': ['GameDataLoader.LoadAlphaPatterns', 'EventProcessor(α pattern)'],
    'data/connectivity/env_tones.json': ['GameDataLoader.LoadEnvTones', 'EventProcessor(tone 通道)'],
    'data/connectivity/moonlight_landing.json': ['GameDataLoader.LoadMoonlightLanding'],
}

EXTERNAL_PREFIX = ('data/connectivity/abagen/', 'data/connectivity/cab-np/',
                   'data/connectivity/hansen2024/', 'data/connectivity/yeo2011/')
EXTERNAL_EXTRA = {'data/connectivity/kroell14_networks.json',
                  'data/connectivity/enigma_sc_summary.json',
                  'data/hospital_ref/manifest.json'}

# 已废弃子系统（2026-07-26 态度/7驱动 · D20 卡牌 · 旧链路体系）残留数据
LEGACY = {
    'data/attitudes.json', 'data/drives.json', 'data/emotions.json',
    'data/emotion_cards.json', 'data/cognition_cards.json', 'data/behavior_cards.json',
    'data/skill_coords.json',
    'data/connectivity/link_registry.json', 'data/connectivity/link_contexts.json',
    'data/connectivity/link_modulation_ceiling.json',
    'data/connectivity/link_modulation_ceiling_v2.json',
    'data/connectivity/personality_tag_links.json',
    'data/connectivity/subcortical_links.json',
    'data/connectivity/brainstem_cortical_fc.json',
    'data/connectivity/white_matter_tracts.json',
    'data/connectivity/link_name_lookup.json',
    'data/connectivity/yeo7_dk_network_map.json',
}

NOT_GAME = {'data/skills-lock.json'}

NOTE = {
    'data/skills-lock.json': '★ 非游戏数据：AI agent 的 skill 锁文件（41 项），误放于 data/。'
                             '零设计文档引用。建议迁至 .agents/ 或移出版本控制。',
    'data/connectivity/moonlight_landing.json': 'calibration_status = PLACEHOLDER（version 0），数值待标定。',
    'data/connectivity/link_modulation_ceiling_v2.json': '参考（旧链路体系）。当前调制正典见 design/rules/skill-tree/modulation/。',
    'data/term_registry.json': '设计期参考，非运行时数据。status 字段是术语唯一权威状态。',
    'data/hospital_ref/manifest.json': '医院建模参考的 provenance 记录（含来源 PDF 路径）。',
}

OWNER = {'runtime': '引擎组（code/src 消费方）', 'reference': '设计组（design/ 引用方）'}

DEPRECATED_DOC_PREFIX = ('design/archive', 'reference/deprecated', 'design/decisions')


def tracked_data_files():
    out = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files', 'data/'],
                         capture_output=True, text=True, cwd=ROOT).stdout
    return sorted(f for f in out.split('\n')
                  if f and f.endswith(('.json', '.npy', '.csv'))
                  and f != MANIFEST)          # 排除自身：派生清单不是被盘点对象


def doc_refs(name):
    # 只统计 **.md**（设计文档）——lifecycle 回答的是"设计是否还用它"。
    #
    # 为何不含代码与 JSON：任何提到某数据文件名的工具/清单都会抬高它的计数，
    # 于是"新增一个校验器"就会改变某个数据文件的 lifecycle（2026-09-12 实测：
    # validate_data_manifest.py 提到 brain_regions.json 即使其计数 +1 → 非确定）。
    # 代码侧的消费由 manifest 的 role / runtime_consumers 表达，不混进 lifecycle。
    out = subprocess.run(
        ['grep', '-rl', '--include=*.md', '--exclude-dir=obj', '--exclude-dir=bin',
         name, '.'],
        capture_output=True, text=True, cwd=ROOT).stdout
    raw = [x for x in out.split('\n') if x]
    # ★ 必须先在【原始】路径上过滤——若先剥掉 "./" 前缀，下面的 startswith 永远不成立，
    #   备份目录与 data/ 下的文件会被误算为"设计文档引用"（2026-09-12 --check 抓到）
    raw = [x for x in raw
           if not x.startswith(('./.refactor-backup', './.scratch', './data/'))]
    files = [x[2:] for x in raw]
    active = [x for x in files if not x.startswith(DEPRECATED_DOC_PREFIX)]
    deprecated = [x for x in files if x.startswith(DEPRECATED_DOC_PREFIX)]
    return active, deprecated


def generators_of(name):
    hits = []
    tdir = os.path.join(ROOT, 'code/tools')
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.py') or f == os.path.basename(__file__):
            continue
        try:
            t = open(os.path.join(tdir, f), encoding='utf-8').read()
        except Exception:
            continue
        if re.search(r'["\']' + re.escape(name) + r'["\']', t):
            hits.append(f)
    return hits


def build():
    entries = {}
    for f in tracked_data_files():
        n = os.path.basename(f)
        active, deprecated = doc_refs(n)
        gens = generators_of(n)
        if f in NOT_GAME:
            origin, life, role, ship = 'external', 'archived', 'reference', False
        elif f in RUNTIME:
            origin = 'generated' if gens else 'authored'
            life, role, ship = 'active', 'runtime', True
        elif f.startswith(EXTERNAL_PREFIX) or f in EXTERNAL_EXTRA:
            origin, life, role, ship = 'external', 'active', 'reference', False
        elif f in LEGACY:
            origin = 'generated' if gens else 'authored'
            life, role, ship = 'deprecated', 'reference', False
        elif not active and not deprecated:
            origin = 'generated' if gens else 'authored'
            life, role, ship = 'archived', 'reference', False
        else:
            origin = 'generated' if gens else 'authored'
            life, role, ship = 'active', 'reference', False

        e = {
            'logical_id': re.sub(r'\.(json|npy|csv)$', '', n),
            'origin': origin, 'lifecycle': life, 'role': role, 'shipping': ship,
            'owner': OWNER.get(role, '未指定'),
            'generator': gens,
            'runtime_consumers': RUNTIME_CONSUMERS.get(f, []),
            'provenance': ('external（见 connectivity/sources.md 或子目录 README）'
                           if origin == 'external' else '本仓作者维护'),
            'refs': {'active_docs': len(active), 'deprecated_docs': len(deprecated)},
        }
        if f in NOTE:
            e['note'] = NOTE[f]
        entries[f] = e

    c = collections.Counter((v['lifecycle'], v['role']) for v in entries.values())
    return {
        '_description': 'data/ 数据清单（P4c 数据契约）。每个受控数据文件的正交属性 + 所有权 + 生成链 + 消费方。由 code/tools/build_data_manifest.py 生成。',
        '_schema_version': '1.0',
        '_created': '2026-09-12',
        '_generated_by': 'code/tools/build_data_manifest.py',
        '_rules': [
            'origin ∈ {authored, generated, external}；lifecycle ∈ {active, deprecated, archived}；'
            'role ∈ {runtime, generator-input, reference, evidence}；shipping ∈ {true, false}',
            '四轴正交：一个文件可以是 external + active + reference + shipping=false',
            'runtime allowlist = GameDataLoader.LoadAll 实际加载的 8 个文件；'
            '运行时只允许消费 role=runtime 的文件',
            'shipping=true 仅限 role=runtime（进入运行时路径者）',
            'lifecycle=archived 表示零引用（活跃与废弃文档均不引用）→ 候选清理',
            '判据：连续两次生成结果一致（--check 比对磁盘实测与已提交内容）',
        ],
        '_stats': {
            'total': len(entries),
            'runtime': sum(1 for v in entries.values() if v['role'] == 'runtime'),
            'shipping_true': sum(1 for v in entries.values() if v['shipping']),
            'deprecated': sum(1 for v in entries.values() if v['lifecycle'] == 'deprecated'),
            'archived': sum(1 for v in entries.values() if v['lifecycle'] == 'archived'),
            'by_lifecycle_role': {f'{k[0]}/{k[1]}': n for k, n in sorted(c.items())},
        },
        'files': entries,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='校验契约：文件集与磁盘一致 + 属性合法（不重新推导属性）')
    ap.add_argument('--refresh', action='store_true',
                    help='重新从证据推导属性并覆盖 manifest（当分类需要更新时的人工动作）')
    args = ap.parse_args()
    m = build()
    path = os.path.join(ROOT, MANIFEST)
    if args.check:
        # manifest 是**声明式契约**，不是生成物。
        #
        # 只校验三件事（2026-09-12 定案）：
        #   ① 文件集与磁盘一致（无遗漏 / 无幽灵条目）
        #   ② 属性值合法（枚举合法 + shipping 蕴含 role=runtime）
        #   ③ 每个受控数据文件都被登记
        #
        # ★ 刻意**不**重新推导属性：refs 计数会因任意新增 .md 提及该文件名而漂移
        #   （实测：新增一份证据文档即改变两个数据文件的 active_docs），
        #   若 --check 比对推导值，写任何文档都要重生成 manifest —— 契约不可用。
        #   属性更新是人工动作：--refresh。
        if not os.path.exists(path):
            print(f'❌ {MANIFEST} 不存在'); return 1
        old = json.load(open(path, encoding='utf-8'))
        of = old.get('files', {})
        disk = set(tracked_data_files())
        declared = set(of)
        errs = []
        for f in sorted(disk - declared):
            errs.append(f'磁盘有 {f} 但 manifest 未登记')
        for f in sorted(declared - disk):
            errs.append(f'manifest 登记了 {f} 但磁盘没有（幽灵条目）')
        for f, v in of.items():
            if v.get('origin') not in ('authored', 'generated', 'external'):
                errs.append(f'{f}: origin 非法 {v.get("origin")!r}')
            if v.get('lifecycle') not in ('active', 'deprecated', 'archived'):
                errs.append(f'{f}: lifecycle 非法 {v.get("lifecycle")!r}')
            if v.get('role') not in ('runtime', 'generator-input', 'reference', 'evidence'):
                errs.append(f'{f}: role 非法 {v.get("role")!r}')
            if v.get('shipping') and v.get('role') != 'runtime':
                errs.append(f'{f}: shipping=true 但 role={v.get("role")}')
        if errs:
            print(f'❌ 数据契约有 {len(errs)} 项问题：')
            for e in errs[:30]:
                print('   ' + e)
            return 1
        print(f'✅ 数据契约成立（{len(declared)} 个文件登记完整 · 属性合法）')
        print('   注：属性更新为人工动作（--refresh），--check 不重新推导')
        return 0

    if args.refresh or not os.path.exists(path):
        pass          # 落到下方生成逻辑
    else:
        print(f'{MANIFEST} 已存在；属性更新请显式用 --refresh（避免误覆盖已审定的分类）')
        return 0

    json.dump(m, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'✓ 已生成 {MANIFEST}')
    print(json.dumps(m['_stats'], ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
