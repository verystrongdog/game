#!/usr/bin/env python3
"""build_data_manifest.py — 生成 data/manifest.json（P4c 数据契约）

从**证据**推导每个受控数据文件的四轴属性，而非手工填写：

| 轴 | 取值 | 判据（全部来自实测） |
|---|---|---|
| origin | authored / generated / external | 有生成器**写出**该路径 → generated；外部图集目录或已知外部来源 → external；其余 authored |
| role | runtime / generator-input / reference / evidence | `GameDataLoader.LoadAll` 加载 → runtime；被 `code/tools` 活跃**生成器脚本**读取 → generator-input；被设计文档或校验器引用 → reference；仅被归档文档引用 → evidence |
| lifecycle | active / deprecated / archived | 有 runtime 消费 / 活跃生成器读取 / 活跃文档引用 → active；仅废弃子系统或归档文档引用 → deprecated；**三条引用面全空** → archived |
| shipping | true / false | 仅 role=runtime |

## 判定顺序（先到先得，避免"深层引用覆盖表层"）

```
runtime          ← GameDataLoader.LoadAll 实测文件名
LEGACY 名单      ← 已废弃子系统的残留数据（人工登记，见下）
活跃文档引用     ← 活跃 .md 提到该文件名
活跃生成器读取   ← code/tools 生成器脚本中的路径字面量
外部来源         ← 外部图集目录 / 已知外部数据集
校验器读取       ← 只被 validate_*/清单工具读取的数据表 = 校验基准，非生成链输入
归档文档引用     ← 仅 design/archive、design/decisions 等提到
archived         ← 以上全无 = 真实孤儿
```

## 为什么 lifecycle 不再只看"设计文档引用数"

2026-09-12 实测发现的误分类：`data/connectivity/enigma_sc_ctx_matrix.npy` 等
5 个文件被标为 `archived`（零设计文档引用），**但它们是
`code/tools/gen_modulation_ceiling.py` 实际读取的输入**。只按文档引用判定，
会把"活着的生成链输入"判成"可清理的孤儿"——正是 owner 方案 §9.3
「先 inventory 后移动，不得靠默认值掩盖未知」要防的事。

现在 `archived` 的含义收紧为：**文档、代码、生成链三条引用面全空**。

> ⚠️ `--check` 刻意**不重新推导属性**。属性是**声明式契约**：任何新增 `.md`
> 提到某数据文件名都会改变 `refs` 计数（2026-09-12 实测：新增一份证据文档立即
> 改变了两个数据文件的 `active_docs`）。若 `--check` 比对推导值，则写任何文档
> 都要重生成 manifest——契约不可用。属性更新是人工动作：`--refresh`。

用法:
    python3 code/tools/build_data_manifest.py            # 生成（已存在则拒绝覆盖）
    python3 code/tools/build_data_manifest.py --refresh  # 从证据重新推导并覆盖（人工动作）
    python3 code/tools/build_data_manifest.py --check    # 契约校验：文件集与磁盘一致 + 属性合法
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


# ══════════════════════════════════════════════════════════════════
# 引用面扫描（文档 / 代码 / 写出）
# ══════════════════════════════════════════════════════════════════

# 这些前缀下的 .md 完全不参与引用统计（备份、过程工作区、外部资料、issue 存档）
DOC_DENY_PREFIX = ('.refactor-backup/', '.scratch/', 'reference/',
                   'design/archive/grilling/issues/')
# 这些前缀下的 .md 引用算"已废弃"档
DEPRECATED_DOC_PREFIX = ('design/archive', 'reference/deprecated', 'design/decisions')

DATA_FILE_RE = re.compile(r'data/[A-Za-z0-9_./\-]+\.(?:json|npy|csv)')


def tracked_files_under(prefix):
    """受控文件列表。

    `prefix=''`（或 `'.'`）表示全部：`git ls-files ''` 会报
    "empty string is not a valid pathspec" 并**返回 0 个文件而不报错**——
    2026-09-12 实测踩到：doc_refs 因此静默变成"零引用"，把 13 个文件误分类。
    故此处显式把空路径换成 '.'。
    """
    args = ['git', '-c', 'core.quotePath=false', 'ls-files']
    if prefix and prefix != '.':
        args.append(prefix)
    out = subprocess.run(args, capture_output=True, text=True, cwd=ROOT).stdout
    return [f for f in out.split('\n') if f]


def tracked_data_files():
    """受控数据文件（data/ 下的 json/npy/csv），排除 manifest 自身。

    排除自身是必需的：manifest 是**派生清单**，不是被盘点对象。
    若纳入，两次生成之间文件数会因清单自身出现而漂移（2026-09-12 实测 bug 1）。
    """
    return sorted(f for f in tracked_files_under('data/')
                  if f.endswith(('.json', '.npy', '.csv')) and f != MANIFEST)


def doc_refs(name):
    """按**文件名**统计 .md 引用，分活跃 / 废弃两档。

    只统计 **.md**——lifecycle 回答的是"还有人把它当依据吗"。
    为何不含代码与 JSON：任何提到某数据文件名的工具/清单都会抬高它的计数，
    于是"新增一个校验器"就会改变某个数据文件的 lifecycle（2026-09-12 实测 bug 3）。
    代码侧的消费由 role / consumed_by 表达，不混进 refs。

    ★ 两处与旧实现的差别（2026-09-12）：

    ① **只扫描 `git ls-files` 的受控 .md**。旧实现用 `grep -rl .` 扫工作区，
       于是 `.refactor-backup/` 与 `.scratch/` 里的副本会抬高计数（靠事后前缀过滤
       补救，而该过滤曾因先剥 `./` 而永不成立——实测 bug 2）。
    ② **`data/README.md` 计入活跃文档**。它是数据层自己的索引，是"这个文件还有人管"
       最直接的证据。旧实现把整个 `data/` 排除在外，导致「只有数据层 README 记着它」
       的文件被判成零引用孤儿——实测把 `data/connectivity/enigma_all_connections.csv`
       误伤成 archived。
    """
    files = []
    for p in tracked_files_under(''):
        if not p.endswith('.md') or p.startswith(DOC_DENY_PREFIX):
            continue
        try:
            t = open(os.path.join(ROOT, p), encoding='utf-8').read()
        except Exception:
            continue
        if name in t:
            files.append(p)
    active = [x for x in files if not x.startswith(DEPRECATED_DOC_PREFIX)]
    deprecated = [x for x in files if x.startswith(DEPRECATED_DOC_PREFIX)]
    return active, deprecated


# 写出语义：脚本把内容落到某个 data/ 路径上。
#
# 三个正则覆盖实测出现的三种写法：
#   ① 调用式：json.dump(obj, open(p,'w')) / p.write_text(...) / np.save(p, arr)
#   ② 分离式：p = ROOT / 'data/x.json' … json.dump(obj, f) —— 路径与写调用不同行
#   ③ 模式式：p = … ; open(p, 'w')
# 这不是完整数据流分析，但结论只用于 origin 轴（误判代价低，可人工 --refresh 纠正）。
WRITE_CALL_RE = re.compile(
    r'(?:json\.dump\w*|write_text|writelines|np\.save\w*|savetxt|to_csv|savefig)\s*\([^)]*?'
    r'(data/[A-Za-z0-9_./\-]+\.(?:json|npy|csv))', re.S)
WRITE_NEAR_RE = re.compile(
    r'(data/[A-Za-z0-9_./\-]+\.(?:json|npy|csv))[\s\S]{0,120}?'
    r'(?:json\.dump\w*|write_text|np\.save\w*|savetxt|to_csv)')
WRITE_MODE_RE = re.compile(
    r'open\(\s*[^)]*?(data/[A-Za-z0-9_./\-]+\.(?:json|npy|csv))[^)]*?[\'"][wa]')

# 生成器脚本命名前缀。`validate_` 开头的不是生成器——它是校验器，
# 读数据是为了比对，不是把它当输入加工。
GENERATOR_PREFIX = re.compile(
    r'(gen_|build_|rebuild_|generate_|expand_|refine_|normalize_|migrate_|'
    r'fix_|rename_|map_|add_|merge_|sync_)')


def active_generator_scripts():
    """`code/tools/` 下的活跃生成器脚本路径集合（排除校验器与清单工具）。"""
    out = set()
    for p in tracked_files_under('code/tools/'):
        b = os.path.basename(p)
        if not b.endswith('.py') or b.startswith('validate_'):
            continue
        if GENERATOR_PREFIX.match(b):
            out.add(p)
    return out


def scan_code():
    """一次扫描活跃代码，返回 (refs, writers, gens)。

    refs    {data 相对路径: [引用它的活跃代码文件]}
    writers {data 相对路径: [**写出**它的活跃代码文件]}
    gens    {data 相对路径: [其中属于活跃生成器脚本的]}

    ★ 只扫 `code/`（受控）。归档与垃圾桶里的工具不算活跃消费——它们引用某个
    数据文件，恰恰说明该文件是历史残留，而非仍在生成链上。
    """
    gen_scripts = active_generator_scripts()
    refs = collections.defaultdict(list)
    writers = collections.defaultdict(list)
    gens = collections.defaultdict(list)
    for p in [x for x in tracked_files_under('code/') if x.endswith(('.py', '.cs', '.sh'))]:
        try:
            t = open(os.path.join(ROOT, p), encoding='utf-8').read()
        except Exception:
            continue
        for m in set(DATA_FILE_RE.findall(t)):
            refs[m].append(p)
            if p in gen_scripts:
                gens[m].append(p)
        writes = set(WRITE_CALL_RE.findall(t))
        writes |= set(WRITE_NEAR_RE.findall(t))
        writes |= set(WRITE_MODE_RE.findall(t))
        for m in writes:
            writers[m].append(p)
    return refs, writers, gens


# ══════════════════════════════════════════════════════════════════
# 声明式事实表（人工登记，不推导）
# ══════════════════════════════════════════════════════════════════

# 引擎 runtime allowlist：GameDataLoader.LoadAll 实际加载者（双向校验见 validate_data_manifest.py）
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

EXTERNAL_PREFIX = ('data/connectivity/cab-np/',
                   'data/connectivity/hansen2024/', 'data/connectivity/yeo2011/')
EXTERNAL_EXTRA = {'data/connectivity/kroell14_networks.json',
                  'data/connectivity/enigma_sc_summary.json',
                  'data/hospital_ref/manifest.json'}

# 已废弃子系统（2026-07-26 态度/7驱动 · D20 卡牌 · 旧链路体系）的残留数据。
# 这些文件要么只被归档文档/工具引用，要么完全无引用——它们**不是**"还没分类"，
# 而是已裁定的历史残留，故显式登记而非依赖引用计数推导。
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

NOTE = {
    'data/connectivity/moonlight_landing.json': 'calibration_status = PLACEHOLDER（version 0），数值待标定。',
    'data/connectivity/link_modulation_ceiling_v2.json': '参考（旧链路体系）。当前调制正典见 design/rules/skill-tree/modulation/。',
    'data/term_registry.json': '设计期参考，非运行时数据。status 字段是术语唯一权威状态。',
    'data/hospital_ref/manifest.json': '医院建模参考的 provenance 记录（来源 PDF 路径为 Windows 绝对路径，跨机不可复现）。',
}

# 契约 fixture 目录：这些文件**是被 runner 按索引批量消费的**。
# 它们自身的文件名不会出现在任何文档或代码里——逐个登记路径字面量不可能，
# 也不是它们的用途。位置 + index.json 就是它们的注册方式。
#
# ★ 这是**位置即注册**的显式声明。若不写这一条，45 条非法 fixture 会被判成
#   "零引用孤儿 → archived"，而它们恰恰是数据契约里最不能删的东西
#   （删掉就等于删掉跨语言判据）。把规则写在明处，好过让分类看起来"干净"。
FIXTURE_PREFIX = 'data/runtime-fixtures/'

OWNER = {
    'runtime': '引擎组（code/src 消费方）',
    'generator-input': '工具组（code/tools 生成链）',
    'reference': '设计组（design/ 引用方）',
    'evidence': '归档（无活跃消费方）',
}


# ══════════════════════════════════════════════════════════════════
# 推导
# ══════════════════════════════════════════════════════════════════

def build():
    code_refs, code_writers, code_gens = scan_code()
    entries = {}
    for f in tracked_data_files():
        n = os.path.basename(f)
        active, deprecated = doc_refs(n)
        code_c = sorted(code_refs.get(f, []))
        writers = sorted(code_writers.get(f, []))
        gens = sorted(code_gens.get(f, []))
        # origin=generated 只认**写出证据**，不认"文件里出现过这个名字"——
        # 读入也算出现，那样每个输入都会被标成 generated（2026-09-12 定案）。
        generated = bool(writers)
        ext = f.startswith(EXTERNAL_PREFIX) or f in EXTERNAL_EXTRA

        if f in RUNTIME:
            origin = 'generated' if generated else 'authored'
            role, life, ship = 'runtime', 'active', True
        elif f.startswith(FIXTURE_PREFIX):
            origin, role, life, ship = 'authored', 'evidence', 'active', False
        elif f in LEGACY:
            origin = 'generated' if generated else 'authored'
            role, life, ship = 'reference', 'deprecated', False
        elif active:
            origin = 'external' if ext else ('generated' if generated else 'authored')
            role, life, ship = 'reference', 'active', False
        elif gens:
            origin = 'external' if ext else ('generated' if generated else 'authored')
            role, life, ship = 'generator-input', 'active', False
        elif ext:
            origin, role, life, ship = 'external', 'reference', 'active', False
        elif code_c:
            # 只被校验器/清单工具读取的数据表：它是校验基准，不是生成链输入
            origin = 'generated' if generated else 'authored'
            role, life, ship = 'reference', 'active', False
        elif deprecated:
            origin, role, life, ship = 'authored', 'evidence', 'deprecated', False
        else:
            # 文档、活跃代码、归档代码三条引用面全空 → 真实孤儿
            origin, role, life, ship = 'authored', 'evidence', 'archived', False

        e = {
            'logical_id': re.sub(r'\.(json|npy|csv)$', '', n),
            'origin': origin, 'lifecycle': life, 'role': role, 'shipping': ship,
            'owner': OWNER.get(role, '未指定'),
            'consumed_by': code_c,
            'generators': writers,
            'runtime_consumers': RUNTIME_CONSUMERS.get(f, []),
            'provenance': ('external（见 data/connectivity/sources.md 或子目录 README）'
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
            '四轴正交：一个文件可以是 external + active + generator-input + shipping=false',
            'runtime allowlist = GameDataLoader.LoadAll 实际加载的 8 个文件；运行时只允许消费 role=runtime 的文件',
            'shipping=true 仅限 role=runtime（进入运行时路径者）',
            'origin=generated 只认生成器**写出**证据（json.dump / write_text / np.save 等）',
            'lifecycle=archived 的判据是**三条引用面全空**（活跃文档 / 活跃代码 / 活跃工具链），'
            '不是"零设计文档引用"——后者会把活着的生成链输入误判为孤儿（2026-09-12 实测）',
            '`--check` 校验文件集与属性合法性，**不重新推导属性**（refs 计数会随任意新增 .md 漂移）；'
            '属性更新是人工动作 `--refresh`',
        ],
        '_stats': {
            'total': len(entries),
            'runtime': sum(1 for v in entries.values() if v['role'] == 'runtime'),
            'generator_input': sum(1 for v in entries.values() if v['role'] == 'generator-input'),
            'shipping_true': sum(1 for v in entries.values() if v['shipping']),
            'deprecated': sum(1 for v in entries.values() if v['lifecycle'] == 'deprecated'),
            'archived': sum(1 for v in entries.values() if v['lifecycle'] == 'archived'),
            'by_lifecycle_role': {f'{k[0]}/{k[1]}': n for k, n in sorted(c.items())},
        },
        'files': entries,
    }


# ══════════════════════════════════════════════════════════════════
# 命令行
# ══════════════════════════════════════════════════════════════════

VALID_ORIGIN = ('authored', 'generated', 'external')
VALID_LIFECYCLE = ('active', 'deprecated', 'archived')
VALID_ROLE = ('runtime', 'generator-input', 'reference', 'evidence')


def check(path):
    """契约校验：文件集与磁盘一致（无遗漏 / 无幽灵）+ 属性合法。不重新推导。"""
    if not os.path.exists(path):
        print(f'❌ {MANIFEST} 不存在')
        return 1
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
        if v.get('origin') not in VALID_ORIGIN:
            errs.append(f'{f}: origin 非法 {v.get("origin")!r}')
        if v.get('lifecycle') not in VALID_LIFECYCLE:
            errs.append(f'{f}: lifecycle 非法 {v.get("lifecycle")!r}')
        if v.get('role') not in VALID_ROLE:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='校验契约：文件集与磁盘一致 + 属性合法（不重新推导属性）')
    ap.add_argument('--refresh', action='store_true',
                    help='重新从证据推导属性并覆盖 manifest（当分类需要更新时的人工动作）')
    args = ap.parse_args()
    path = os.path.join(ROOT, MANIFEST)

    if args.check:
        return check(path)

    if not args.refresh and os.path.exists(path):
        print(f'{MANIFEST} 已存在；属性更新请显式用 --refresh（避免误覆盖已审定的分类）')
        return 0

    m = build()
    json.dump(m, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'✓ 已生成 {MANIFEST}')
    print(json.dumps(m['_stats'], ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
