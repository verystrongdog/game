#!/usr/bin/env python3
"""validate_data_manifest.py — data/manifest.json 契约校验（P4c）

检查三件事（对应 owner 方案 §9.3 的解决判据）：

  D1 manifest 与磁盘实测一致（等价于 `build_data_manifest.py --check`）
  D2 **runtime allowlist**：代码里实际加载的数据文件，必须都在 manifest 中标为
     role=runtime；反过来，标为 runtime 的文件必须真被代码加载
  D3 正交属性合法：即使 shipping=true 的文件必须 role=runtime；
     lifecycle=archived 的文件不得被 runtime 消费

用法: python3 code/tools/validate_data_manifest.py
退出码: 0 = 通过, 1 = 有违规
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, 'data/manifest.json')
LOADER = os.path.join(ROOT, 'code/src/YouAreNotTheFish.Core/Data/GameDataLoader.cs')

VALID_ORIGIN = {'authored', 'generated', 'external'}
VALID_LIFECYCLE = {'active', 'deprecated', 'archived'}
VALID_ROLE = {'runtime', 'generator-input', 'reference', 'evidence'}


def loaded_by_engine():
    """从 GameDataLoader.LoadAll 提取实际加载的数据文件（仓库相对路径）。"""
    src = open(LOADER, encoding='utf-8').read()
    i = src.find('LoadAll')
    body = src[i:] if i >= 0 else ''
    names = set(re.findall(r'"([A-Za-z_0-9]+\.json)"', body))
    out = set()
    for n in names:
        if n in ('brain_regions.json', 'signal_types.json'):
            out.add('data/' + n)
        else:
            out.add('data/connectivity/' + n)
    return out


def main():
    errors = []

    # ── D1 manifest 与磁盘一致 ──
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'code/tools/build_data_manifest.py'),
                        '--check'], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        errors.append('D1 manifest 与磁盘实测不一致：\n' + (r.stdout + r.stderr).strip()[:800])

    m = json.load(open(MANIFEST, encoding='utf-8'))
    files = m.get('files', {})

    # ── D3 属性合法 ──
    for f, v in files.items():
        if v.get('origin') not in VALID_ORIGIN:
            errors.append(f'D3 {f}: origin 非法 {v.get("origin")!r}')
        if v.get('lifecycle') not in VALID_LIFECYCLE:
            errors.append(f'D3 {f}: lifecycle 非法 {v.get("lifecycle")!r}')
        if v.get('role') not in VALID_ROLE:
            errors.append(f'D3 {f}: role 非法 {v.get("role")!r}')
        if v.get('shipping') and v.get('role') != 'runtime':
            errors.append(f'D3 {f}: shipping=true 但 role={v.get("role")} —— 只有 runtime 才发货')

    # ── D2 runtime allowlist 双向一致 ──
    engine = loaded_by_engine()
    declared = {f for f, v in files.items() if v.get('role') == 'runtime'}
    for f in sorted(engine - declared):
        errors.append(f'D2 引擎加载了 {f}，但 manifest 未标 role=runtime')
    for f in sorted(declared - engine):
        errors.append(f'D2 manifest 标 {f} 为 runtime，但引擎并未加载它')

    # ── D2' runtime 不得消费 archived ──
    for f, v in files.items():
        if v.get('lifecycle') == 'archived' and v.get('runtime_consumers'):
            errors.append(f"D3 {f}: lifecycle=archived 却有 runtime_consumers")

    print(f'manifest: {len(files)} 个文件 · runtime {len(declared)} 个 · 引擎实测 {len(engine)} 个')
    if errors:
        print()
        for e in errors:
            print('  ❌ ' + e)
        print(f'\n❌ {len(errors)} 项违规')
        return 1
    print('\n✅ 数据契约校验通过（D1 一致性 / D2 runtime allowlist / D3 属性正交）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
