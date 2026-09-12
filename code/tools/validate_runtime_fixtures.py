#!/usr/bin/env python3
"""validate_runtime_fixtures.py — 跨语言 fixture 的 **Python 侧 runner**（P4c）

owner 方案 §9.3 判据：「跨语言接受/拒绝集合一致」+「Python/C# 共用合法与非法 fixture」。

本脚本做两件事：

1. **schema 层**——按 §9.3 要求的「Schema 与语义检查分工」，对 8 个 runtime 文件
   施加**结构/枚举/长度/值域**规则（`RULES`），产出通过/拒绝。
2. **fixture 一致性**——读 `data/runtime-fixtures/index.json`，对每条 fixture
   跑结构校验，比对 `expect`。任何不一致即为跨语言接受集分叉的 Python 侧证据。

C# 侧的对应 runner 是 `code/src/YouAreNotTheFish.Core.Tests/Data/RuntimeFixtureTests.cs`，
两侧必须给出**逐条相同**的判定。

## 分工边界（为何不写完整 JSON Schema）

- **结构规则（本脚本 + C# 加载器）**：必填键、类型、枚举、数组长度、数值值域。
- **跨文件语义规则（C# 引擎加载器）**：如 moonlight 的 supp ⊆ W_active 需要
  tripartite 边端点集；`validate_params.py` / `validate_disease.py` 承担其余设计语义。
  这些**只有引擎能判**，Python 侧不重复实现——重复实现就是第二个真相源。

用法: python3 code/tools/validate_runtime_fixtures.py
退出码: 0 = 全部一致, 1 = 有不一致
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURES = 'data/runtime-fixtures'

# JSON 写 snake_case（小写），与 C# PascalCase 成员大小写不敏感对应
BRAIN_CATEGORIES = {'cortical', 'subcortical', 'brainstem'}
LEVELS = {'L0', 'L1', 'L2', 'L3', 'L4', 'L5'}


class Reject(Exception):
    """结构契约违规。消息里带 rule id，便于两侧比对归因。"""

    def __init__(self, rule, detail):
        super().__init__(f'{rule}: {detail}')
        self.rule = rule


def need(doc, key, rule):
    if not isinstance(doc, dict) or key not in doc:
        raise Reject(rule, f'缺根键 {key}')
    return doc[key]


def need_nonempty(doc, key, rule):
    v = need(doc, key, rule)
    if not v:
        raise Reject(rule, f'根键 {key} 为空')
    return v


def need_keys(obj, keys, rule, where):
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            raise Reject(rule, f'{where} 缺 {k}')


# ══════════════════════════════════════════════════════════════════
# 结构契约规则（与 C# 加载器一一对应）
#
# 顺序即优先级：**仅键匹配**先于**唯一性**，否则"键≠functional_id"的用例
# 会先撞上唯一性规则，归因就错了（2026-09-12 实测）。
# ══════════════════════════════════════════════════════════════════

def check_brain_regions(doc, ctx):
    regions = need_nonempty(doc, 'regions', 'BR-required-root')
    if not isinstance(regions, dict):
        raise Reject('BR-type-root', 'regions 不是字典')
    for key, r in regions.items():
        if not isinstance(r, dict):
            raise Reject('BR-type-nested', f'{key} 不是字典')
        # 键匹配先于唯一性：否则"键≠functional_id"的用例会先撞上唯一性规则，归因就错了
        if r.get('functional_id') != key:
            raise Reject('BR-key-match-functional-id',
                         f'{key} 的 functional_id={r.get("functional_id")!r}')
        # 枚举按 SnakeCaseEnumConverter 的语义比对：JSON 写 snake_case（小写），
        # 与 PascalCase 成员大小写不敏感地对应。不按 PascalCase 字面比。
        if str(r.get('category', '')).lower() not in BRAIN_CATEGORIES:
            raise Reject('BR-enum-category', f'{key} category={r.get("category")!r}')
        need_keys(r, ['function_profile'], 'BR-required-nested', key)
    ids = [r.get('functional_id') for r in regions.values()]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise Reject('BR-unique-functional-id', f'重复 functional_id {dup}')


def check_signal_types(doc, ctx):
    cats = need_nonempty(doc, '_categories', 'ST-required-root')
    if not isinstance(cats, dict):
        raise Reject('ST-type-root', '_categories 不是字典')
    for name, c in cats.items():
        need_keys(c, ['subtypes'], 'ST-required-nested', f'类目 {name}')


def check_tripartite_model(doc, ctx):
    nodes = need_nonempty(doc, 'graph_nodes', 'TP-required-root')
    profs = need_nonempty(doc, 'node_profiles', 'TP-required-root')
    if len(nodes) != len(profs):
        raise Reject('TP-node-profile-parity',
                     f'graph_nodes={len(nodes)} ≠ node_profiles={len(profs)}')
    for key in ('corticocortical', 'brainstem', 'cstc', 'privileged_pathways'):
        v = need(doc, key, 'TP-required-root')
        if not v:
            raise Reject('TP-length-edges', f'{key} 为空（该通信原语无任何边）')


def check_w_sensory(doc, ctx):
    rows = need_nonempty(doc, 'rows', 'WS-required-root')
    matrix = need(doc, 'matrix_2d', 'WS-required-root')
    modalities = need_nonempty(doc, 'modalities', 'WS-required-root')
    if not isinstance(matrix, list) or not matrix:
        raise Reject('WS-type-root', 'matrix_2d 不是非空列表')
    if len(modalities) != 8:
        raise Reject('WS-length-modalities', f'modalities={len(modalities)} ≠ 8')
    if len(matrix) != len(rows):
        raise Reject('WS-row-matrix-parity',
                     f'matrix_2d 行数={len(matrix)} ≠ rows 行数={len(rows)}')
    for i, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != len(modalities):
            raise Reject('WS-row-width',
                         f'第 {i} 行宽度={len(row) if isinstance(row, list) else "非列表"} '
                         f'≠ 模态数 {len(modalities)}')


def check_situation_primitives(doc, ctx):
    arch = need_nonempty(doc, 'situation_archetypes', 'SP-required-root')
    networks = {n.get('name') for n in ((doc.get('functional_networks') or {}).get('networks') or [])}
    if not isinstance(arch, list):
        raise Reject('SP-type-root', 'situation_archetypes 不是列表')
    for a in arch:
        need_keys(a, ['name', 'key_brain_regions'], 'SP-required-nested', f'原型 {a.get("name")}')
        for lv in a.get('levels_involved') or []:
            if lv not in LEVELS:
                raise Reject('SP-enum-level', f'{a.get("name")} levels_involved 含 {lv!r}')
        if networks:
            for n in a.get('primary_networks') or []:
                if n not in networks:
                    raise Reject('SP-network-registry',
                                 f'{a.get("name")} primary_networks 含未注册网络 {n!r}')


ALPHA_CONSUMED_ROWS = ['A1', 'A2', 'A4', 'A5', 'B1', 'B2', 'B4', 'C1', 'D1', 'D2']


def check_alpha_patterns(doc, ctx):
    if not str(need(doc, 'schema', 'AP-schema-name')).startswith('alpha_patterns'):
        raise Reject('AP-schema-name', f'schema={doc.get("schema")!r}')
    if need(doc, 'version', 'AP-schema-major') != 1:
        raise Reject('AP-schema-major', f'version={doc.get("version")!r}（期望 1）')
    events = need_nonempty(doc, 'events', 'AP-row-count')
    for row in ALPHA_CONSUMED_ROWS:
        if row not in events:
            raise Reject('AP-row-present', f'消费行 {row} 缺失')
    if len(events) < 14:
        raise Reject('AP-row-count', f'events={len(events)} < 14')
    for row in ALPHA_CONSUMED_ROWS:
        e = events[row]
        pat = e.get('pattern')
        if not isinstance(pat, list) or len(pat) != 8:
            raise Reject('AP-pattern-length',
                         f'{row} pattern 长度={len(pat) if isinstance(pat, list) else "非列表"} ≠ 8')
        for v in pat:
            if v not in (0, 1):
                raise Reject('AP-pattern-domain', f'{row} pattern 含 {v!r} ∉ {{0,1}}')
    for row, e in events.items():
        m = e.get('m_alpha')
        if m == 'm_delta':
            continue
        if isinstance(m, bool) or not isinstance(m, (int, float)):
            raise Reject('AP-malpha-type', f'{row} m_alpha={m!r} 既非数也非 "m_delta"')
        if not (0.0 <= float(m) <= 1.0):
            raise Reject('AP-malpha-range', f'{row} m_alpha={m!r} ∉ [0,1]')


def check_env_tones(doc, ctx):
    if not str(need(doc, 'schema', 'ET-schema-name')).startswith('env_tones'):
        raise Reject('ET-schema-name', f'schema={doc.get("schema")!r}')
    if need(doc, 'version', 'ET-schema-major') != 1:
        raise Reject('ET-schema-major', f'version={doc.get("version")!r}（期望 1）')
    envs = need_nonempty(doc, 'environments', 'ET-required-root')
    for name, e in envs.items():
        need_keys(e, ['display_name', 'alpha_env', 'situation'], 'ET-required-nested', f'环境 {name}')
        if not e.get('display_name'):
            raise Reject('ET-required-nested', f'环境 {name} display_name 为空')
        need_keys(e.get('situation'), ['primary'], 'ET-required-nested', f'环境 {name}')
        if not e['situation'].get('primary'):
            raise Reject('ET-required-nested', f'环境 {name} situation.primary 为空')
        ae = e.get('alpha_env')
        if not isinstance(ae, list) or len(ae) != 8:
            raise Reject('ET-length-alpha-env',
                         f'环境 {name} alpha_env 长度={len(ae) if isinstance(ae, list) else "非列表"} ≠ 8')
        for v in ae:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                raise Reject('ET-range-alpha-env', f'环境 {name} alpha_env 含 {v!r} ∉ [0,1]')


def check_moonlight_landing(doc, ctx):
    if not str(need(doc, 'schema', 'ML-schema-name')).startswith('moonlight_landing'):
        raise Reject('ML-schema-name', f'schema={doc.get("schema")!r}')
    if need(doc, 'version', 'ML-schema-major') != 1:
        raise Reject('ML-schema-major', f'version={doc.get("version")!r}（期望 1）')
    if doc.get('calibration_status') not in ('PLACEHOLDER', 'CALIBRATED'):
        raise Reject('ML-calibration-status', f'calibration_status={doc.get("calibration_status")!r}')
    sems = need_nonempty(doc, 'semantics', 'ML-required-root')
    for s in sems:
        need_keys(s, ['id', 'primary', 'secondary', 'r', 'alpha_s'], 'ML-required-nested',
                  f'语义 {s.get("id")}')
        if len(s.get('primary') or []) != 4:
            raise Reject('ML-required-nested',
                         f'{s.get("id")} primary 落点数={len(s.get("primary") or [])} ≠ 4')
        if len(s.get('secondary') or []) != 8:
            raise Reject('ML-required-nested',
                         f'{s.get("id")} secondary 落点数={len(s.get("secondary") or [])} ≠ 8')
        r = s.get('r')
        if r == 'PLACEHOLDER':
            rv = 1.0
        else:
            try:
                rv = float(r)
            except (TypeError, ValueError):
                raise Reject('ML-r-range', f'{s.get("id")} r 解析失败 {r!r}')
        if not (rv > 0.0):
            raise Reject('ML-r-range', f'{s.get("id")} r={rv} 非正')
    # supp 互斥：primary ∪ secondary 无重复（同一语义内）
    for s in sems:
        pts = list(s.get('primary') or []) + list(s.get('secondary') or [])
        if len(set(pts)) != len(pts):
            raise Reject('ML-supp-mutual-exclusion', f'{s.get("id")} 落点重叠')


RULES = {
    'brain_regions': check_brain_regions,
    'signal_types': check_signal_types,
    'tripartite_model': check_tripartite_model,
    'W_sensory': check_w_sensory,
    'situation_primitives': check_situation_primitives,
    'alpha_patterns': check_alpha_patterns,
    'env_tones': check_env_tones,
    'moonlight_landing': check_moonlight_landing,
}


def judge(logical_id, path, ctx):
    """返回 (accepted: bool, rule_or_None, detail)。"""
    doc = json.load(open(path, encoding='utf-8'))
    try:
        RULES[logical_id](doc, ctx)
        return True, None, ''
    except Reject as e:
        return False, e.rule, str(e)


def main():
    idx_path = os.path.join(ROOT, FIXTURES, 'index.json')
    if not os.path.exists(idx_path):
        print(f'❌ {FIXTURES}/index.json 不存在（先跑 build_runtime_data_fixtures.py）')
        return 1
    idx = json.load(open(idx_path, encoding='utf-8'))

    # 结构规则先跑一遍**真实数据文件**——规则过严会在这里暴露，
    # 而不是在 fixture 比对里表现为"合法数据被拒"（那是更晚、更难查的失败）。
    print('── 结构契约 vs 真实数据 ──')
    bad = 0
    for rel, lid in [('data/brain_regions.json', 'brain_regions'),
                     ('data/signal_types.json', 'signal_types'),
                     ('data/connectivity/tripartite_model.json', 'tripartite_model'),
                     ('data/connectivity/W_sensory.json', 'W_sensory'),
                     ('data/connectivity/situation_primitives.json', 'situation_primitives'),
                     ('data/connectivity/alpha_patterns.json', 'alpha_patterns'),
                     ('data/connectivity/env_tones.json', 'env_tones'),
                     ('data/connectivity/moonlight_landing.json', 'moonlight_landing')]:
        ok, rule, detail = judge(lid, os.path.join(ROOT, rel), {})
        print(f'  {"PASS" if ok else "FAIL"}  {lid:24} {rel}'
              + ('' if ok else f'  ← {detail}'))
        if not ok:
            bad += 1

    print('\n── fixture 判定 ──')
    mismatches = []
    n_ok = 0
    verdicts = []
    for e in idx['cases']:
        path = os.path.join(ROOT, e['file'])
        if not os.path.exists(path):
            mismatches.append((e['file'], 'fixture 文件缺失', e['expect'], 'missing'))
            continue
        accepted, rule, detail = judge(e['logical_id'], path, {})
        verdicts.append({
            'file': e['file'], 'logical_id': e['logical_id'], 'case': e['case'],
            'expect': e['expect'], 'accepted': accepted, 'detail': detail,
        })
        want = e['expect'] == 'accept'
        if accepted != want:
            mismatches.append((e['file'],
                               '应接受但被拒' if want else '应拒绝但被接受',
                               e['expect'], detail))
        else:
            n_ok += 1

    print(f'  {n_ok}/{len(idx["cases"])} 条判定与 index 一致')
    if mismatches:
        print(f'\n  ❌ {len(mismatches)} 条不一致：')
        for f, why, expect, detail in mismatches[:40]:
            print(f'     {f}\n        期望 {expect} · {why} · {detail}')

    # 导出判定供与 C# 侧**逐条比对**（路径由环境变量给出）。
    # 不设环境变量时只做自检、不落盘——默认跑校验器不应污染工作树。
    export = os.environ.get('DSH_FIXTURE_VERDICTS_PY')
    if export:
        json.dump({'_source': 'python', 'count': len(verdicts), 'verdicts': verdicts},
                  open(export, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'  ✓ 已导出 Python 判定 → {export}')

    total = len(idx['cases'])
    if bad or mismatches:
        print(f'\n❌ 结构失败 {bad} · fixture 不一致 {len(mismatches)}')
        return 1
    print(f'\n✅ schema 层与 fixture 全部一致'
          f'（8 个 runtime 文件结构契约通过 · {total} 条 fixture 判定正确）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
