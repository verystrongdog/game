#!/usr/bin/env python3
"""
Unity 资产身份校验 — `.meta` 成对性 / GUID 唯一性 / 引用可解析 / Rig 断言。

**纯 git + 文本解析，不需要 Unity Editor**：因此可进 `docs-integrity` CI job（而 `unity`
门禁在 CI 的 ubuntu runner 上是 `NOT_AVAILABLE`）。规格与来源见
`design/engineering/危险点表.md` §十；本文件是它的实现。

四条规则:
  A1 成对性      受控资产 ⇄ 同名 `.meta`（扫描面限 `code/unity/Assets/**`——
                 `ProjectSettings/`、`Packages/` 下的文件本来就没有 `.meta`，
                 不限域会产生 26 处假阳性）
  A2 GUID 唯一性 全部受控 `.meta` 的 `guid:` 无重复
  A3 引用可解析  受控场景/controller/asset 里的每个 `guid:` 引用，都能由某个受控
                 `.meta` 定义；**Unity 内置 guid 与已知缺口走允许清单**（外置 JSON）
  A4 Rig 断言    每个受控 `*.fbx.meta` 的 `animationType == 3`（枚举名 `Human`，
                 UI 上叫 Humanoid）且 `avatarSetup == 1`（`CreateFromThisModel`）——
                 **非人形用途的 FBX（静态模型/道具）走 `non_humanoid_ok` 豁免**：
                 规则要拦的是「本该驱动 Humanoid 载体却默认导成 Generic」，
                 而不是「一切 FBX 都必须 Humanoid」

**为什么不只是文档**：A3 报的悬空引用里，4 条是已经手工查出过一次的——当时用一次性
脚本核完就没了，结论只留在散文里（`code/unity/README.md` §二·H 残留缺口 ①/④）。
校验器的职责就是把这个变成每次自动发现。

允许清单: `validate_unity_assets_exceptions.json`（同目录）——**三段生命周期不同**：
  · `builtin_guids`   —— Unity 内置资源 guid，恒等成立
  · `non_humanoid_ok` —— 非人形用途的 FBX，长期豁免（带理由）
  · `known_dangling`  —— 已知缺口引用，**每条必须带理由与 issue 编号**；
    **该 issue 关闭后必须删除该条**，否则允许清单会从"例外登记"长成"永久豁免名单"

用法: python3 code/tools/validate_unity_assets.py [--verbose]
退出码: 0 = 全部通过, 1 = 有违规
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
EXCEPTIONS = Path(__file__).parent / "validate_unity_assets_exceptions.json"

UNITY_PREFIX = "code/unity/"
# A1 的扫描面：只有 Assets/ 下的资产在 Unity 里会拿到 .meta
PAIRING_ROOT = "code/unity/Assets/"
# A3 的扫描面：这些扩展名的文本资产里会写 guid 引用
REF_BEARING = (".unity", ".controller", ".asset", ".anim", ".prefab")

META_GUID = re.compile(r"^guid:\s*([0-9a-f]{32})\s*$", re.M)
ANY_GUID = re.compile(r"guid:\s*([0-9a-f]{32})")
ANIM_TYPE = re.compile(r"^\s*animationType:\s*(\d+)", re.M)
AVATAR_SETUP = re.compile(r"^\s*avatarSetup:\s*(\d+)", re.M)

HUMAN_ANIM_TYPE = 3          # ModelImporterAnimationType.Human（UI 上叫 Humanoid）
CREATE_FROM_THIS_MODEL = 1   # ModelImporterAvatarSetup.CreateFromThisModel


def tracked_files():
    """受控文件（git ls-files）——判据是「干净检出里有什么」，不是磁盘上有什么。"""
    out = subprocess.run(["git", "-c", "core.quotePath=false", "ls-files"],
                         capture_output=True, text=True, cwd=ROOT).stdout
    return [l for l in out.split("\n") if l]


def load_exceptions():
    if not EXCEPTIONS.exists():
        return {"builtin_guids": [], "known_dangling": []}
    data = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    return {
        "builtin_guids": {e["guid"]: e.get("reason", "") for e in data.get("builtin_guids", [])},
        "package_guids": {e["guid"]: e.get("reason", "") for e in data.get("package_guids", [])},
        "non_humanoid_ok": {e["asset"]: e.get("reason", "") for e in data.get("non_humanoid_ok", [])},
        "known_dangling": {e["guid"]: e for e in data.get("known_dangling", [])},
    }


def check_pairing(unity_files, tracked):
    """A1：Assets/ 下每个受控资产有同名 .meta；每个受控 .meta 有主体。"""
    assets = [f for f in unity_files
              if not f.endswith(".meta") and f.startswith(PAIRING_ROOT)]
    metas = [f for f in unity_files if f.endswith(".meta")]
    missing = [a for a in assets if a + ".meta" not in tracked]
    orphans = []
    for m in metas:
        subject = m[: -len(".meta")]
        if subject in tracked:
            continue
        # 目录 .meta：主体是目录——只要该目录下有受控内容就算成立
        if any(x.startswith(subject + "/") for x in unity_files):
            continue
        orphans.append(m)
    return missing, orphans


def check_guid_unique(unity_files):
    """A2：受控 .meta 的 guid 无重复。"""
    seen, dup = {}, []
    for m in unity_files:
        if not m.endswith(".meta"):
            continue
        g = META_GUID.search((ROOT / m).read_text(encoding="utf-8", errors="replace"))
        if not g:
            continue
        g = g.group(1)
        if g in seen:
            dup.append((g, seen[g], m))
        else:
            seen[g] = m
    return seen, dup


def check_refs(unity_files, defined_guids, exceptions):
    """A3：引用可解析——未被受控 .meta 定义、也不在允许清单里的 guid 即悬空。"""
    dangling, allowed_hits = {}, []
    for f in unity_files:
        if not f.endswith(REF_BEARING):
            continue
        for g in ANY_GUID.findall((ROOT / f).read_text(encoding="utf-8", errors="replace")):
            if g in defined_guids:
                continue
            if g in exceptions["builtin_guids"]:
                allowed_hits.append((g, f, "builtin"))
                continue
            if g in exceptions["package_guids"]:
                allowed_hits.append((g, f, "package"))
                continue
            if g in exceptions["known_dangling"]:
                allowed_hits.append((g, f, "known"))
                continue
            dangling.setdefault(g, []).append(f)
    return dangling, allowed_hits


def check_rig(unity_files, exceptions):
    """A4：受控 *.fbx.meta 必须是 Humanoid + CreateFromThisModel（非人形用途走豁免）。"""
    bad, total, exempted = [], 0, []
    for m in unity_files:
        if not m.endswith(".fbx.meta"):
            continue
        asset = m[: -len(".meta")]
        if asset in exceptions["non_humanoid_ok"]:
            exempted.append(asset)
            continue
        total += 1
        text = (ROOT / m).read_text(encoding="utf-8", errors="replace")
        at = ANIM_TYPE.search(text)
        asetup = AVATAR_SETUP.search(text)
        at_v = at.group(1) if at else None
        as_v = asetup.group(1) if asetup else None
        if at_v != str(HUMAN_ANIM_TYPE) or as_v != str(CREATE_FROM_THIS_MODEL):
            bad.append((m, at_v, as_v))
    return total, bad, exempted


def main():
    verbose = "--verbose" in sys.argv
    tracked = tracked_files()
    tracked_set = set(tracked)
    unity_files = [f for f in tracked if f.startswith(UNITY_PREFIX)]
    exceptions = load_exceptions()

    missing, orphans = check_pairing(unity_files, tracked_set)
    defined_guids, dup = check_guid_unique(unity_files)
    dangling, allowed_hits = check_refs(unity_files, defined_guids, exceptions)
    rig_total, rig_bad, rig_exempt = check_rig(unity_files, exceptions)

    errors = []
    for a in missing:
        errors.append(f"🔴 [A1] 受控资产缺 .meta: {a}")
    for m in orphans:
        errors.append(f"🔴 [A1] 孤儿 .meta（无主体）: {m}")
    for g, first, second in dup:
        errors.append(f"🔴 [A2] GUID 重复 {g}: {first} / {second}")
    for g, files in dangling.items():
        errors.append(f"🔴 [A3] 悬空 guid 引用 {g} ← {', '.join(files)}")
    for m, at_v, as_v in rig_bad:
        errors.append(f"🔴 [A4] Rig 非 Humanoid: {m}（animationType={at_v} "
                      f"avatarSetup={as_v}，应为 {HUMAN_ANIM_TYPE}/{CREATE_FROM_THIS_MODEL}）")

    print(f"受控 Unity 文件 {len(unity_files)}"
          f"（.meta {sum(1 for f in unity_files if f.endswith('.meta'))}）"
          f" · 定义 guid {len(defined_guids)}\n")
    print(f"  A1 成对性      缺 .meta {len(missing)} · 孤儿 .meta {len(orphans)}")
    print(f"  A2 GUID 唯一性 重复 {len(dup)}")
    print(f"  A3 引用可解析  悬空 {len(dangling)}"
          f" · 经允许清单放行 {len(allowed_hits)}"
          f"（builtin {sum(1 for _, _, k in allowed_hits if k == 'builtin')}"
          f" / package {sum(1 for _, _, k in allowed_hits if k == 'package')}"
          f" / known {sum(1 for _, _, k in allowed_hits if k == 'known')}）")
    print(f"  A4 Rig 断言    受控 FBX {rig_total} · 非 Humanoid {len(rig_bad)}"
          f" · 非人形豁免 {len(rig_exempt)}")
    if verbose and allowed_hits:
        print("\n  允许清单放行明细：")
        for g, f, kind in allowed_hits:
            entry = exceptions["builtin_guids"].get(g) if kind == "builtin" \
                else exceptions["package_guids"].get(g, "") if kind == "package" \
                else exceptions["known_dangling"].get(g, {}).get("reason", "")
            print(f"    [{kind}] {g} ← {f}\n           {entry}")

    if errors:
        print()
        for e in errors:
            print(e)
        print(f"\n{'=' * 60}\n❌ {len(errors)} 处违规\n{'=' * 60}")
        sys.exit(1)

    print("\n✅ 全部通过")
    sys.exit(0)


if __name__ == "__main__":
    main()
