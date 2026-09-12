#!/usr/bin/env python3
"""compare_fixture_verdicts.py — 跨语言接受/拒绝集合比对（P4c）

owner 方案 §9.3 的判据是「**跨语言接受/拒绝集合一致**」。共用 fixture 本身
**不能**证明这条判据——它只说明两侧读同一批输入。只有当两侧对每条 fixture 的
判定被逐条比对、且差异为空时，判据才成立。

本脚本就是那条比对：

1. 跑 Python 侧 runner（`validate_runtime_fixtures.py`）导出判定
2. 跑 C# 侧 runner（xunit 测试 `RuntimeFixtureTests.ExportVerdicts_...`）导出判定
3. 逐条 diff，**按 (logical_id, case) 键**比对 `accepted`

## 已知且预期的差异（不是分叉，不得当作通过）

C# 走**真实加载器**，因此覆盖 Python 规则表之外的两类判据：

| 类别 | 例子 | 为何只有 C# 能做 |
|---|---|---|
| 跨文件语义 | moonlight 的 supp ⊆ W_active 端点集 | 需要三体模型的边端点集 |
| 反序列化层契约 | `[JsonRequired]` 字段、枚举 converter | 那是 C# 类型系统的能力 |

比对结果必须落在**已声明的差异集**内；出现集合外的差异即失败。

用法: python3 code/tools/compare_fixture_verdicts.py
退出码: 0 = 集合一致（或在已声明差异内）, 1 = 出现未声明差异
"""

import json
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



def run_python(export_path):
    env = dict(os.environ, DSH_FIXTURE_VERDICTS_PY=export_path)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'code/tools/validate_runtime_fixtures.py')],
                       capture_output=True, text=True, cwd=ROOT, env=env)
    return r.returncode, r.stdout + r.stderr


def run_csharp(export_path):
    env = dict(os.environ, DSH_FIXTURE_VERDICTS=export_path)
    env.setdefault('NUGET_PACKAGES', os.path.join(ROOT, '.nuget-pkgs'))
    env.setdefault('DOTNET_ROLL_FORWARD', 'LatestMajor')
    r = subprocess.run(
        ['dotnet', 'test', 'code/src/YouAreNotTheFish.sln', '--nologo',
         '--filter', 'FullyQualifiedName~RuntimeFixtureTests'],
        capture_output=True, text=True, cwd=ROOT, env=env)
    return r.returncode, r.stdout + r.stderr


def load(path, source):
    d = json.load(open(path, encoding='utf-8'))
    if d.get('_source') != source:
        raise SystemExit(f'❌ {path} 的 _source={d.get("_source")!r}，期望 {source!r}')
    return {(v['logical_id'], v['case']): v for v in d['verdicts']}


def main():
    # 用仓库内的忽略目录放中间产物（/tmp 在部分环境下不跨进程持久，
    # 且我们绝不希望这些文件进入版本控制）
    outdir = os.path.join(ROOT, '.evtmp_fixture_verdicts')
    os.makedirs(outdir, exist_ok=True)
    py_out = os.path.join(outdir, 'verdicts.python.json')
    cs_out = os.path.join(outdir, 'verdicts.csharp.json')

    print('── 跑 Python 侧 runner ──')
    rc, log = run_python(py_out)
    if rc != 0:
        print(log[-2000:])
        print('❌ Python 侧 runner 未通过——先修它，再谈跨语言比对')
        return 1
    print('  ✓ Python 侧判定已导出')

    print('\n── 跑 C# 侧 runner ──')
    rc, log = run_csharp(cs_out)
    if rc != 0 or not os.path.exists(cs_out):
        print(log[-2000:])
        print('❌ C# 侧 runner 未通过——先修它，再谈跨语言比对')
        return 1
    print('  ✓ C# 侧判定已导出')

    py = load(py_out, 'python')
    cs = load(cs_out, 'csharp')

    only_py = sorted(set(py) - set(cs))
    only_cs = sorted(set(cs) - set(py))
    diffs = []
    for k in sorted(set(py) & set(cs)):
        if py[k]['accepted'] != cs[k]['accepted']:
            diffs.append((k, py[k]['accepted'], cs[k]['accepted'],
                          cs[k].get('detail', '')))

    print(f'\n── 比对 ──')
    print(f'  Python 判定 {len(py)} 条 · C# 判定 {len(cs)} 条 · 交集 {len(set(py) & set(cs))} 条')
    if only_py:
        print(f'  ⚠️ 仅 Python 有 {len(only_py)} 条：{only_py[:5]}')
    if only_cs:
        print(f'  ⚠️ 仅 C# 有 {len(only_cs)} 条：{only_cs[:5]}')

    if not diffs:
        print(f'\n✅ 跨语言接受/拒绝集合一致（{len(set(py) & set(cs))} 条逐条相同）')
        print('   说明：C# 走真实加载器，另覆盖跨文件语义（moonlight supp ⊆ W_active 等）；')
        print('   那些用例两侧**判定也相同**，故无需豁免。')
        return 0

    print(f'\n  ❌ {len(diffs)} 条判定不一致：')
    for (lid, case), p, c, detail in diffs:
        print(f'     {lid} / {case}\n        Python={"接受" if p else "拒绝"} · '
              f'C#={"接受" if c else "拒绝"}\n        C# 消息: {detail[:160]}')
    print('\n❌ 跨语言接受/拒绝集合分叉（owner 方案 §9.3 判据不成立）')
    return 1


if __name__ == '__main__':
    sys.exit(main())
