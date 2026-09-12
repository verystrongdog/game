#!/usr/bin/env python3
"""migrate_paths.py — 仓库重构 Phase 3：路径全面改英文

把设计文档目录改为英文骨架，产出 design/ · reference/ · code/ · data/ 四层结构。

用法：
    python3 tools/migrate_paths.py --dry-run   # 只打印计划，不动文件
    python3 tools/migrate_paths.py             # 执行

命名口径：**目录名改英文，文件名保留中文**（设计文档为中文，文件名承载语义）。
例外：框架索引与决策树片段（其文件名镜像新英文目录名）一并改英文。

来源: REFACTOR-PLAN.md §5.2 / §六 Phase 3
"""

import argparse
import os
import subprocess
import sys

# ── 顶层目录映射（git mv 整个目录，内容随之）────────────────────
TOP = [
    ("规则/",     "design/rules/"),
    ("实体/",     "design/entities/"),
    ("空间/",     "design/space/"),
    ("事件/",     "design/events/"),
    ("呈现/",     "design/presentation/"),
    ("管线/",     "design/pipeline/"),
    ("规格/",     "design/spec/"),
    ("设计归档/", "design/archive/"),
    ("垃圾桶/",   "design/archive/trash/"),
    ("参考/",     "reference/"),
    ("src/",      "code/src/"),
    ("unity/",    "code/unity/"),
    ("sim/",      "code/sim/"),
    ("tools/",    "code/tools/"),
]

# ── 嵌套中文目录映射（路径用【原始】形式书写；执行时经顶层映射转换）──
NESTED = [
    ("规则/技能树系统/",                       "design/rules/skill-tree/"),
    ("规则/技能树系统/操作层/",                "design/rules/skill-tree/operations/"),
    ("规则/技能树系统/调制参数/",              "design/rules/skill-tree/modulation/"),
    ("规则/技能树系统/已废弃/",                "design/rules/skill-tree/deprecated/"),
    ("规则/技能树系统/参考文献/",              "design/rules/skill-tree/references/"),
    ("实体/疾病目录/",                         "design/entities/diseases/"),
    ("实体/疾病目录/_父类/",                   "design/entities/diseases/_parent-classes/"),
    ("空间/治疗中心建模/",                     "design/space/treatment-center-modeling/"),
    ("空间/治疗中心建模/references/raw/参考图/",
     "design/space/treatment-center-modeling/references/raw/reference-images/"),
    ("呈现/3D可视化/",                         "design/presentation/visualization-3d/"),
    ("规格/引擎/",                             "design/spec/engine/"),
    ("规格/素材/",                             "design/spec/material/"),
    ("规格/素材/病种试点/",                    "design/spec/material/disease-pilots/"),
    ("规格/素材/ref/一手叙事/",                "design/spec/material/ref/first-person-narratives/"),
    ("规格/数据源/",                           "design/spec/source-data/"),
    ("设计归档/grilling/方法论/",              "design/archive/grilling/methodology/"),
    ("设计归档/grilling/_根级/",               "design/archive/grilling/_root/"),
    ("设计归档/grilling/grilling-116-disease-gen-evolution/资格核验批次1-性创伤通道/",
     "design/archive/grilling/grilling-116-disease-gen-evolution/eligibility-batch1-sexual-trauma/"),
    ("设计归档/grilling/grilling-116-disease-gen-evolution/资格核验批次2-全量解锁/",
     "design/archive/grilling/grilling-116-disease-gen-evolution/eligibility-batch2-full-unlock/"),
    ("参考/废弃/",                             "reference/deprecated/"),
    ("参考/废弃/卡牌系统/",                    "reference/deprecated/card-system/"),
    ("参考/废弃/态度系统/",                    "reference/deprecated/attitude-system/"),
    ("参考/废弃/情绪系统/",                    "reference/deprecated/emotion-system/"),
    ("参考/废弃/月光场/",                      "reference/deprecated/moonlight-field/"),
    ("参考/废弃/行为系统/",                    "reference/deprecated/behavior-system/"),
    ("参考/废弃/认知系统/",                    "reference/deprecated/cognitive-system/"),
    ("参考/文献/",                             "reference/literature/"),
    ("参考/文献/参考文献/",                    "reference/literature/papers/"),
    ("参考/书籍/",                             "reference/books/"),
    ("参考/会话存档/",                         "reference/session-archive/"),
    ("docs/维度/",                             "design/framework/dimensions/"),
    ("docs/决策树/",                           "design/decisions/"),
    ("docs/agents/",                           "design/conventions/agents/"),
]

# ── 单文件映射（同样用【原始】路径书写）────────────────────────
FILES = [
    ("项目总览.md",                      "design/README.md"),
    ("docs/设计框架-六维状态.md",        "design/framework/six-dimensions.md"),
    ("docs/写作与引用规范.md",           "design/conventions/writing-and-references.md"),
    # 框架维度索引（文件名镜像新英文目录名，一并改）
    ("docs/维度/规则.md", "design/framework/dimensions/rules.md"),
    ("docs/维度/实体.md", "design/framework/dimensions/entities.md"),
    ("docs/维度/空间.md", "design/framework/dimensions/space.md"),
    ("docs/维度/事件.md", "design/framework/dimensions/events.md"),
    ("docs/维度/呈现.md", "design/framework/dimensions/presentation.md"),
    ("docs/维度/管线.md", "design/framework/dimensions/pipeline.md"),
    # 决策树片段
    ("docs/决策树/01-被否决的方向.md",              "design/decisions/01-rejected-directions.md"),
    ("docs/决策树/02-话题轮次-2026-07至08-01.md",   "design/decisions/02-topics-2026-07-to-08-01.md"),
    ("docs/决策树/03-话题轮次-2026-08-01至08-11.md","design/decisions/03-topics-2026-08-01-to-08-11.md"),
    ("docs/决策树/04-编号轮次-意识基础与数据层.md", "design/decisions/04-numbered-consciousness-and-data-layer.md"),
    ("docs/决策树/05-编号轮次-引擎实施.md",         "design/decisions/05-numbered-engine-implementation.md"),
    ("docs/决策树/06-编号轮次-疾病与呈现.md",       "design/decisions/06-numbered-disease-and-presentation.md"),
]

# 新顶层目录（承载文件，不参与 git mv）
PLACEHOLDERS = ["design", "reference", "code"]


def run(cmd, dry):
    if dry:
        return 0, ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stderr.strip()


def post(path):
    """把【原始】路径转换成顶层目录移动之后的路径。"""
    for old, new in TOP:
        if path == old:
            return new
        if path.startswith(old):
            return new + path[len(old):]
    return path


def move_dir(old, new, dry, log):
    old, new = old.rstrip("/"), new.rstrip("/")
    cur = old if dry else post(old)          # dry-run 用原始路径检查，执行时用移动后路径
    if not os.path.isdir(cur):
        log.append(("MISSING", old, new, ""))
        return
    if os.path.exists(new):
        log.append(("SKIP-EXISTS", old, new, ""))
        return
    if not dry:
        os.makedirs(os.path.dirname(new) or ".", exist_ok=True)
    rc, err = run(["git", "mv", cur, new], dry)
    log.append(("OK" if rc == 0 else "FAIL", old, new, err[:90]))


def move_file(old, new, dry, log):
    cur = old if dry else post(old)
    if not os.path.isfile(cur):
        log.append(("MISSING", old, new, ""))
        return
    if not dry:
        os.makedirs(os.path.dirname(new) or ".", exist_ok=True)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", cur],
                             capture_output=True).returncode == 0
    cmd = ["git", "mv", cur, new] if tracked else ["mv", cur, new]
    rc, err = run(cmd, dry)
    log.append(("OK" if rc == 0 else "FAIL", old, new, err[:90]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run
    log = []

    print(f"{'[DRY-RUN] ' if dry else ''}Phase 3 路径改英文\n")
    print("── 1. 顶层目录 ──")
    for old, new in TOP:
        move_dir(old, new, dry, log)
    print("── 2. 嵌套中文目录 ──")
    for old, new in NESTED:
        move_dir(old, new, dry, log)
    print("── 3. 单文件 ──")
    for old, new in FILES:
        move_file(old, new, dry, log)

    ok = sum(1 for x in log if x[0] == "OK")
    print(f"\n{'计划' if dry else '执行'} {len(log)} 项：成功 {ok} · "
          f"失败 {sum(1 for x in log if x[0]=='FAIL')} · 跳过 {sum(1 for x in log if x[0].startswith('SKIP'))}")
    for st, o, n, e in log:
        if st != "OK":
            print(f"  {st:<12} {o} → {n}  {e}")
    # docs/ 应已空
    if os.path.isdir("docs"):
        rest = [os.path.join(dp, f) for dp, _, fs in os.walk("docs") for f in fs]
        print(f"\ndocs/ 残留文件 {len(rest)}")
        for r in rest[:8]:
            print(f"  {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
