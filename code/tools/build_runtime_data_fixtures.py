#!/usr/bin/env python3
"""build_runtime_data_fixtures.py — 生成**跨语言共用**的 runtime 数据契约 fixture

owner 方案 §9.3 要求「Python/C# 共用合法与非法 fixture」「跨语言接受/拒绝集合一致」。
本脚本是那条判据的实现基础：它从**真实数据文件**出发，逐个施加**单一**变更，
产出 `data/runtime-fixtures/` 下的合法/非法 fixture 与索引。

## 为什么是"单点变异"而不是手写 JSON

手写 fixture 会与真实数据脱节（真实数据加了字段，fixture 不知道）。
单点变异保证：每个非法 fixture 与合法版本的差异**恰好一处**，
因此"该被拒绝"的归因是确定的——不会出现"它失败了，但不知道因为哪条规则"。

## 目录结构

```
data/runtime-fixtures/
  index.json                         每条的 file / case / expect / rule / mutation
  <logical_id>/
    valid.json                       真实文件的副本（必须被接受）
    <rule>-<case>.json               单点变异（必须被拒绝）
```

`file` 字段建议 C# 侧用"干净检出"的路径（仅 moonlight 需要跨文件，见下）。

用法:
    python3 code/tools/build_runtime_data_fixtures.py --refresh   # 重建 fixture
    python3 code/tools/build_runtime_data_fixtures.py --check     # 校验索引与磁盘一致
"""

import argparse
import copy
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = 'data/runtime-fixtures'

# (相对路径, logical_id)
SOURCES = [
    ('data/brain_regions.json', 'brain_regions'),
    ('data/signal_types.json', 'signal_types'),
    ('data/connectivity/tripartite_model.json', 'tripartite_model'),
    ('data/connectivity/W_sensory.json', 'W_sensory'),
    ('data/connectivity/situation_primitives.json', 'situation_primitives'),
    ('data/connectivity/alpha_patterns.json', 'alpha_patterns'),
    ('data/connectivity/env_tones.json', 'env_tones'),
    ('data/connectivity/moonlight_landing.json', 'moonlight_landing'),
]

# moonlight_landing 的加载器签名是 (path, brainRegions, tripartite)，跨文件依赖。
# 索引里显式声明依赖，两侧 runner 据此构造参数——不靠"哪个文件在第几层"猜。
DEPENDS_ON = {'moonlight_landing': ['brain_regions', 'tripartite_model']}




# ══════════════════════════════════════════════════════════════════
# 每个 runtime 文件的契约规则 + 对应的单点变异
# ══════════════════════════════════════════════════════════════════

CASES = []


def case(logical_id, rule, mutation, note):
    """登记一条非法 fixture。mutation(doc) 原地改 doc。"""
    CASES.append({'logical_id': logical_id, 'rule': rule,
                  'mutation': mutation, 'note': note})


def _first_key(d):
    return next(iter(d))


# ── brain_regions：结构性结构 + 引用完整性 ──
case('brain_regions', 'BR-required-root', lambda d: d.pop('regions'),
     '缺 regions 根键 → 加载器必须拒绝（不能当成"零脑区"静默通过）')
case('brain_regions', 'BR-required-root', lambda d: d.update(regions={}),
     'regions 为空 → 0 个脑区，行序锚全部失效')
case('brain_regions', 'BR-unique-functional-id',
     lambda d: d['regions'][list(d['regions'].keys())[1]].update(
         functional_id=d['regions'][list(d['regions'].keys())[0]]['functional_id']),
     'functional_id 重复（两个条目同 id）→ 主键不再唯一')
case('brain_regions', 'BR-enum-category',
     lambda d: d['regions'][_first_key(d['regions'])].update(category='NotACategory'),
     'category 非法枚举值')
case('brain_regions', 'BR-key-match-functional-id',
     lambda d: d['regions'][_first_key(d['regions'])].update(functional_id='NoSuchRegion'),
     '字典键 ≠ functional_id → 两套主键分叉')
case('brain_regions', 'BR-required-nested',
     lambda d: d['regions'][_first_key(d['regions'])].pop('function_profile'),
     '缺 function_profile → 该脑区无功能剖面')

# ── signal_types：受控词表 ──
case('signal_types', 'ST-required-root', lambda d: d.pop('_categories'),
     '缺 _categories 根键')
case('signal_types', 'ST-required-root', lambda d: d.update(_categories={}),
     '_categories 为空 → 词表失效（membership 校验失去基准）')
case('signal_types', 'ST-required-nested',
     lambda d: d['_categories'][_first_key(d['_categories'])].pop('subtypes'),
     '缺 subtypes')

# ── tripartite_model：三体图 ──
case('tripartite_model', 'TP-required-root', lambda d: d.pop('graph_nodes'),
     '缺 graph_nodes 根键')
case('tripartite_model', 'TP-required-root', lambda d: d.update(graph_nodes={}),
     'graph_nodes 为空 → 51 节点图坍塌，W 矩阵无行序锚')
case('tripartite_model', 'TP-length-edges', lambda d: d.update(corticocortical=[]),
     'corticocortical 为空 → 776 条皮层-皮层边丢失')
case('tripartite_model', 'TP-length-edges', lambda d: d.update(cstc=[]),
     'cstc 为空 → 47 条 CSTC 环路边丢失')
case('tripartite_model', 'TP-node-profile-parity',
     lambda d: d['node_profiles'].pop(_first_key(d['node_profiles'])),
     'node_profiles 与 graph_nodes 数量不等 → 剖面与图节点失配')

# ── W_sensory：69×8 矩阵 ──
case('W_sensory', 'WS-required-root', lambda d: d.pop('rows'),
     '缺 rows 根键')
case('W_sensory', 'WS-row-matrix-parity', lambda d: d.update(matrix_2d=d['matrix_2d'][:5]),
     'matrix_2d 行数 ≠ rows 行数 → 行序锚错位')
case('W_sensory', 'WS-row-width', lambda d: d['matrix_2d'].__setitem__(
     0, d['matrix_2d'][0][:3]),
     '矩阵某行宽度 ≠ 模态数（8）')
case('W_sensory', 'WS-length-modalities', lambda d: d.update(modalities=d['modalities'][:4]),
     'modalities 少于 8 → 感官模态列数不符')

# ── situation_primitives：27 原型 ──
case('situation_primitives', 'SP-required-root', lambda d: d.pop('situation_archetypes'),
     '缺 situation_archetypes 根键')
case('situation_primitives', 'SP-required-root', lambda d: d.update(situation_archetypes=[]),
     'situation_archetypes 为空 → 情境选择无候选')
case('situation_primitives', 'SP-required-nested',
     lambda d: d['situation_archetypes'][0].pop('key_brain_regions'),
     '原型缺 key_brain_regions')
case('situation_primitives', 'SP-enum-level',
     lambda d: d['situation_archetypes'][0].update(levels_involved=['L9']),
     'levels_involved 含 L0–L5 之外的值')
case('situation_primitives', 'SP-network-registry',
     lambda d: d['situation_archetypes'][0].update(primary_networks=['No Such Network']),
     'primary_networks 不在 functional_networks 注册表内')

# ── alpha_patterns：schema/version/pattern 长度/值域/消费行 ──
case('alpha_patterns', 'AP-schema-name', lambda d: d.update(schema='wrong_schema'),
     'schema 名不匹配（须以 alpha_patterns 开头）')
case('alpha_patterns', 'AP-schema-major', lambda d: d.update(version=2),
     'schema major 不匹配（期望 1）')
case('alpha_patterns', 'AP-row-present', lambda d: d['events'].pop('A1'),
     '消费行 A1 缺失（10 个消费行不可缺）')
case('alpha_patterns', 'AP-pattern-length',
     lambda d: d['events']['A1'].update(pattern=[1, 0, 1, 0, 0, 0, 0]),
     'pattern 长度 ≠ 8')
case('alpha_patterns', 'AP-pattern-domain',
     lambda d: d['events']['A1'].update(pattern=[2, 0, 1, 0, 0, 0, 0, 0]),
     'pattern 值 ∉ {0,1}')
case('alpha_patterns', 'AP-malpha-type',
     lambda d: d['events']['A1'].update(m_alpha='bogus'),
     'm_alpha 既非有限数也非 "m_delta"')
case('alpha_patterns', 'AP-malpha-range',
     lambda d: d['events']['A1'].update(m_alpha=7.0),
     'm_alpha 越界（须 ∈ [0,1] 或 "m_delta"）')
case('alpha_patterns', 'AP-row-count',
     lambda d: d.update(events={k: v for k, v in list(d['events'].items())[:5]}),
     'events 行数不足 14')

# ── env_tones：schema/version/alpha_env 长度与值域/必备字段 ──
case('env_tones', 'ET-schema-name', lambda d: d.update(schema='wrong_schema'),
     'schema 名不匹配（须以 env_tones 开头）')
case('env_tones', 'ET-schema-major', lambda d: d.update(version=2),
     'schema major 不匹配（期望 1）')
case('env_tones', 'ET-required-root', lambda d: d.update(environments={}),
     'environments 为空 → 无环境基调可回退，且禁止回退零向量')
case('env_tones', 'ET-required-nested',
     lambda d: d['environments'][_first_key(d['environments'])].pop('display_name'),
     '环境缺 display_name')
case('env_tones', 'ET-required-nested',
     lambda d: d['environments'][_first_key(d['environments'])]['situation'].pop('primary'),
     '环境缺 situation.primary')
case('env_tones', 'ET-length-alpha-env',
     lambda d: d['environments'][_first_key(d['environments'])].update(alpha_env=[0.3, 0.2]),
     'alpha_env 长度 ≠ 8')
case('env_tones', 'ET-range-alpha-env',
     lambda d: d['environments'][_first_key(d['environments'])].update(
         alpha_env=[3.0, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2]),
     'alpha_env 值 ∉ [0,1]')

# ── moonlight_landing：schema/version/归一化/supp 互斥/字段缺失 ──
case('moonlight_landing', 'ML-schema-name', lambda d: d.update(schema='wrong_schema'),
     'schema 名不匹配（须以 moonlight_landing 开头）')
case('moonlight_landing', 'ML-schema-major', lambda d: d.update(version=2),
     'schema major 不匹配（期望 1）')
case('moonlight_landing', 'ML-calibration-status',
     lambda d: d.update(calibration_status='MAYBE'),
     'calibration_status ∉ {PLACEHOLDER, CALIBRATED}')
case('moonlight_landing', 'ML-required-nested',
     lambda d: d['semantics'][0].pop('r'),
     '字段缺失 ≠ PLACEHOLDER（字段缺失必须 load error）')
case('moonlight_landing', 'ML-r-range',
     lambda d: d['semantics'][0].update(r=0.0),
     'r 非正（须为正数或 "PLACEHOLDER"）')
case('moonlight_landing', 'ML-supp-mutual-exclusion',
     lambda d: d['semantics'][0].update(
         secondary=d['semantics'][0]['secondary'][:7] + d['semantics'][0]['primary'][:1]),
     'supp 互斥违反（primary 与 secondary 落点重叠）')
case('moonlight_landing', 'ML-required-nested',
     lambda d: d['semantics'][0].update(primary=d['semantics'][0]['primary'][:3]),
     'primary 落点数 ≠ 4')


# ══════════════════════════════════════════════════════════════════

def slug(s):
    return s.lower().replace('-', '-').replace(' ', '-')


def build():
    outdir = os.path.join(ROOT, OUT)
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    index = []
    for rel, lid in SOURCES:
        src = os.path.join(ROOT, rel)
        doc = json.load(open(src, encoding='utf-8'))
        d = os.path.join(outdir, lid)
        os.makedirs(d)
        json.dump(doc, open(os.path.join(d, 'valid.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        index.append({
            'file': f'{OUT}/{lid}/valid.json',
            'case': 'valid',
            'logical_id': lid,
            'expect': 'accept',
            'rule': None,
            'mutation': '真实文件的副本',
            'depends_on': DEPENDS_ON.get(lid, []),
        })

    seen = {}
    for c in CASES:
        lid = c['logical_id']
        src = next(r for r, l in SOURCES if l == lid)
        doc = json.load(open(os.path.join(ROOT, src), encoding='utf-8'))
        before = json.dumps(doc, ensure_ascii=False, sort_keys=True)
        c['mutation'](doc)
        after = json.dumps(doc, ensure_ascii=False, sort_keys=True)
        if before == after:
            print(f'❌ 变异未生效（该用例无效）：{lid} / {c["rule"]} — {c["note"]}')
            return 1
        # 同一 rule 可有多条用例（如"缺根键"对不同根键），用序号区分：
        # rule id 保持稳定（不因新增用例而改名），case 才带序号。
        n = seen.get(c['rule'], 0) + 1
        seen[c['rule']] = n
        name = f'{slug(c["rule"])}-{n}.json'
        d = os.path.join(outdir, lid)
        json.dump(doc, open(os.path.join(d, name), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        index.append({
            'file': f'{OUT}/{lid}/{name}',
            'case': os.path.splitext(name)[0],
            'logical_id': lid,
            'expect': 'reject',
            'rule': c['rule'],
            'mutation': c['note'],
            'depends_on': DEPENDS_ON.get(lid, []),
        })

    json.dump({
        '_description': 'runtime 数据契约的跨语言共用 fixture（P4c）。Python 与 C# 必须给出相同的接受/拒绝判定。',
        '_generated_by': 'code/tools/build_runtime_data_fixtures.py',
        '_rules': [
            '每个非法 fixture 与合法版本的差异**恰好一处**（单点变异）——拒绝归因必须确定',
            'expect=accept → 加载器必须成功；expect=reject → 加载器必须抛错',
            'Python 侧 runner：code/tools/validate_runtime_fixtures.py',
            'C# 侧 runner：code/src/YouAreNotTheFish.Core.Tests/Data/RuntimeFixtureTests.cs',
            '两侧判定不一致 = 跨语言接受/拒绝集合分叉（owner 方案 §9.3 判据）',
        ],
        'count': {'accept': sum(1 for e in index if e['expect'] == 'accept'),
                  'reject': sum(1 for e in index if e['expect'] == 'reject')},
        'cases': index,
    }, open(os.path.join(outdir, 'index.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=2)

    n_acc = sum(1 for e in index if e['expect'] == 'accept')
    n_rej = sum(1 for e in index if e['expect'] == 'reject')
    print(f'✓ 已生成 {OUT}/：{len(index)} 条（accept {n_acc} / reject {n_rej}）')
    by_lid = {}
    for e in index:
        by_lid.setdefault(e['logical_id'], [0, 0])[0 if e['expect'] == 'accept' else 1] += 1
    for lid, (a, r) in by_lid.items():
        print(f'   {lid:24} accept {a} · reject {r}')
    return 0


def check():
    idx_path = os.path.join(ROOT, OUT, 'index.json')
    if not os.path.exists(idx_path):
        print(f'❌ {OUT}/index.json 不存在'); return 1
    idx = json.load(open(idx_path, encoding='utf-8'))
    errs = []
    listed = set()
    for e in idx['cases']:
        p = os.path.join(ROOT, e['file'])
        listed.add(e['file'])
        if not os.path.exists(p):
            errs.append(f'索引登记了 {e["file"]} 但磁盘没有')
        if e['expect'] not in ('accept', 'reject'):
            errs.append(f'{e["file"]}: expect 非法 {e["expect"]!r}')
        if e['expect'] == 'reject' and not e.get('rule'):
            errs.append(f'{e["file"]}: reject 用例缺 rule')
    on_disk = set()
    for dirpath, _, files in os.walk(os.path.join(ROOT, OUT)):
        for f in files:
            if f.endswith('.json') and f != 'index.json':
                on_disk.add(os.path.relpath(os.path.join(dirpath, f), ROOT))
    for f in sorted(on_disk - listed):
        errs.append(f'磁盘有 {f} 但索引未登记')
    for f in sorted(listed - on_disk):
        errs.append(f'索引有 {f} 但磁盘没有（幽灵条目）')
    if errs:
        print(f'❌ fixture 契约有 {len(errs)} 项问题：')
        for e in errs[:20]:
            print('   ' + e)
        return 1
    print(f'✅ fixture 契约成立（{len(listed)} 条：accept {idx["count"]["accept"]} / reject {idx["count"]["reject"]}）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refresh', action='store_true', help='重建 fixture 与索引')
    ap.add_argument('--check', action='store_true', help='校验索引与磁盘一致')
    args = ap.parse_args()
    if args.check:
        return check()
    return build()


if __name__ == '__main__':
    sys.exit(main())
