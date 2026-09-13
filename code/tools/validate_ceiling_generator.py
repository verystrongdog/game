#!/usr/bin/env python3
"""validate_ceiling_generator.py — 生成链解耦的机械判据（#134）

**判据：跑一次「只写 MD」的生成器，数据契约的字节必须一个不动。**

为什么需要它（#134 的动机，实跑过的读数）：`gen_modulation_ceiling.py` 曾在跑到 MD
一步时必抛 `FileNotFoundError`（落点还是重构前的 `技能树系统/`，目录早已不存在），
而产出 JSON 早已先写出——于是"修一个输出路径"被绑定"改 836 个数值"，这条生成链
**无法被安全地触碰**。解耦（`--md-only` + 非受控默认落点）之后它才可以，本校验器
把这个性质钉成每次自动发现的判据，而不是留在散文里。

三步：
  1. 记录 `data/connectivity/link_modulation_ceiling.json` 与 `..._v2.json` 的 SHA256
  2. 跑 `gen_modulation_ceiling.py --md-only --md-out <临时目录>/链路调制上限参考表.md`
     ——MD 刻意写到仓库外的临时目录：**校验器不许写工作树**
     （判据见 design/engineering/build-and-test.md §四）
  3. 复查两个 SHA256，并断言 MD 真的写出了内容

顺带钉住 `design/rules/skill-tree/deprecated/链路调制上限参考表.md` 的字节：
那是 2026-07-27 的历史快照（与 v1 JSON 的 `_metadata.provenance_note` 同一份快照纪律），
**任何写入路径都不许落到它头上**——这条护栏是 2026-09-13 owner 决定的一部分
（v1 已被 v2 取代；刷新那份快照等于把"当时的表"改成"今天的表"）。

来源: design/engineering/build-and-test.md §2.1 · issue #134
用法: python3 code/tools/validate_ceiling_generator.py [--verbose]
退出码: 0 = 解耦成立, 1 = 有 JSON 被改写 / MD 没写出来 / 历史快照被动过
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GENERATOR = ROOT / "code/tools/gen_modulation_ceiling.py"

# 被守护的数据契约（生成器的产出；#134 的核心判据）
GUARDED = [
    ROOT / "data/connectivity/link_modulation_ceiling.json",
    ROOT / "data/connectivity/link_modulation_ceiling_v2.json",
]

# 历史快照：不许被任何写入路径覆盖（2026-09-13 owner 决定）
FROZEN = ROOT / "design/rules/skill-tree/deprecated/链路调制上限参考表.md"

MD_NAME = "链路调制上限参考表.md"


def sha256(path):
    """文件不存在时返回 None（缺失本身由别的校验器报，这里不重复报）。"""
    if not path.is_file():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    verbose = "--verbose" in sys.argv

    print("=" * 60)
    print("生成链解耦校验（#134）— 只写 MD 不得改写数据契约")
    print("=" * 60)

    before = {p: sha256(p) for p in GUARDED}
    frozen_before = sha256(FROZEN)

    tmpdir = Path(tempfile.mkdtemp(prefix="ceiling-gen-"))
    md_out = tmpdir / MD_NAME
    errors = []
    try:
        cmd = [sys.executable, str(GENERATOR), "--md-only", "--md-out", str(md_out)]
        print(f"  运行: {' '.join(cmd[:2])} --md-only --md-out <tmp>/{MD_NAME}")
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if verbose:
            print(r.stdout.rstrip())
        if r.returncode != 0:
            errors.append(f"生成器 --md-only 退出码 {r.returncode}（应 0）\n{r.stdout}{r.stderr}")
        if not md_out.is_file():
            errors.append(f"MD 未写出：{md_out}（--md-only 也必须能产出参考表）")
        elif md_out.stat().st_size == 0:
            errors.append(f"MD 写出来是空文件：{md_out}")

        after = {p: sha256(p) for p in GUARDED}
        for p in GUARDED:
            if before[p] != after[p]:
                errors.append(
                    f"数据契约被改写：{p.relative_to(ROOT)}\n"
                    f"    before {before[p]}\n    after  {after[p]}")
        frozen_after = sha256(FROZEN)
        if frozen_before != frozen_after:
            errors.append(
                f"历史快照被动过：{FROZEN.relative_to(ROOT)}\n"
                f"    before {frozen_before}\n    after  {frozen_after}")

        md_lines = len(md_out.read_text(encoding="utf-8").splitlines()) if md_out.is_file() else 0
        print(f"  数据契约 {len(GUARDED)} 个 · 历史快照 1 个 · MD 输出 {md_lines} 行")
        for p in GUARDED:
            print(f"    {p.relative_to(ROOT)}  {after[p][:16]}… {'不变' if after[p] == before[p] else '❌ 变了'}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if errors:
        print()
        for e in errors:
            print(f"❌ {e}")
        print(f"\n{'=' * 60}\n❌ {len(errors)} 处违规（解耦不成立）\n{'=' * 60}")
        return 1

    print("\n✅ 解耦成立：只写 MD 不改数据契约；历史快照未被触碰")
    return 0


if __name__ == "__main__":
    sys.exit(main())
