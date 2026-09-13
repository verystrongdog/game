#!/usr/bin/env python3
"""
validate_issues.py 的规则 fixture 测试 — 14 条规则**各一正一反** + 1 条快照键契约。

**为什么需要它**（候选队列项，2026-09-13 落地）：
  `validate_issues.py` 有 1400+ 行、14 条规则，**在此之前没有任何自动化测试**——
  它的行为历来靠"人工造一个 issue 草稿跑一遍"验证。代价已经付过两次：
    · §4.1.1 例外 1「门禁可引用尚不存在的脚本」——**文档承诺了、代码从未实现**，
      存活到 #142 首次交付新门禁时才被撞出（见 issue-process.md §5.3 的校正记录）；
    · #134 的门禁行因解析器从散文里误抓到一个**已存在的文档路径**而"空过"——
      写得越啰嗦越安全，直到 I6 收紧才堵住。
  这两类偏差都是"读一遍代码发现不了、跑一个草稿也未必碰上"的。

**怎么测**：直接调规则函数（不经过 CLI、不联网）——`Subject` 与 `Ctx` 都是纯构造，
snapshot 用手写字典注入。因此 14 条规则**全部可测**，含需要快照的 I5/I7/I11/I13/I14。

**判据**：每条规则给出（正例：违规必须被报出）+（反例：合规必须不报）。
另有 1 条**静态契约用例**：规则读取的 `snapshot[...]` 键集合 ⊆ `fetch_snapshot` 产出的键集合
——这条正是抓出 I13「closed_numbers 恒为空集」的用例。

用法: python3 code/tools/test_validate_issues.py [-v]
退出码: 0 = 全部用例符合预期, 1 = 有用例不符
"""

import ast
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("validate_issues", HERE / "validate_issues.py")
vi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vi)

# ── 基础草稿：一个**处处合规**的 Task（每个正例只破坏一处） ──────────
BASE = """### 类型
Task

### 动机
动机：说清这条 issue 存在的理由，以及不做会怎样。

### 能力增量
| 能力 | 轴 | 从 → 到 |
|---|---|---|
| Core → Unity 适配层 | Implementation | `FAKE` → `PARTIAL` |

### 依赖
blocked-by: 无
consumed-by: 门禁:docs-integrity
requires: 无

### 门禁
docs-integrity

### 预期差分
允许变化（仓库相对路径）：
- `design/engineering/gates.json`

预期不变：
- `data/` 不动

### 验收标准
- [ ] 改前：无此检查
- [ ] 改后：退出码 0

### 明确排除
- 不做别的事

### 回滚
`git revert` 提交组。

### 交付物
- `code/tools/validate_issues.py`

### 接入位置
接入 `code/tools/run_all_checks.py`。
"""

SUBJECT_NUM = 101


def body(**over):
    """以 BASE 为基础替换某些字段的整节内容。"""
    out = BASE
    for heading, text in over.items():
        name = heading.replace("_", " ")
        pat = re.compile(rf"### {re.escape(name)}\n(.*?)(?=\n### |\Z)", re.S)
        if not pat.search(out):
            raise KeyError(f"BASE 里没有 ### {name}")
        out = pat.sub(f"### {name}\n{text}\n", out, count=1)
    return out


def drop(heading):
    """整节删除（测 I1）。"""
    return re.sub(rf"### {re.escape(heading)}\n.*?(?=\n### |\Z)", "", BASE, count=1, flags=re.S)


def subj(text=None, number=SUBJECT_NUM, labels=("type:task",)):
    return vi.Subject(body=text if text is not None else BASE, number=number,
                      title="fixture", labels=list(labels))


def ctx(snapshot=None, labels=None):
    return vi.Ctx("github" if snapshot is not None else "file", labels=labels,
                  snapshot=snapshot, gates=vi.load_gates(),
                  deprecated_terms=vi.load_deprecated_terms())


def status_of(rule_id, subjects, c):
    rule = next(r for r in vi.RULES if r.id == rule_id)
    findings = rule.fn(subjects, c) or []
    st = {f.status for f in findings}
    for sev in (vi.FAIL, vi.WARN, vi.SKIP):
        if sev in st:
            return sev
    return vi.PASS


# ── 快照构造器 ────────────────────────────────────────────────
def snap(open_numbers=(), closed=(), native=None):
    states = {n: "OPEN" for n in open_numbers}
    states.update({n: "CLOSED" for n in closed})
    return {"numbers": set(states), "states": states,
            "open": [], "closed_numbers": set(closed),
            "native_blocked_by": native or {}, "total": len(states), "truncated": False}


DEPRECATED = vi.load_deprecated_terms()
DEP_TERM = DEPRECATED[0][0] if DEPRECATED else None

# ── 用例表：(规则, 名称, 期望, subjects 工厂, ctx 工厂) ─────────
CASES = [
    # I1 必填章节齐全
    ("I1", "正例：缺「回滚」节", vi.FAIL, lambda: [subj(drop("回滚"))], ctx),
    ("I1", "反例：九节 + 类型专属两节齐全", vi.PASS, lambda: [subj()], ctx),

    # I2 类型枚举 + 标签一致
    ("I2", "正例：类型不在六种枚举内", vi.FAIL, lambda: [subj(body(类型="TaskX"))], ctx),
    ("I2", "正例：正文 Task 但标签 type:rfc", vi.FAIL, lambda: [subj(labels=("type:rfc",))],
     lambda: ctx(labels=["type:rfc"])),
    ("I2", "反例：Task + type:task", vi.PASS, lambda: [subj()], lambda: ctx(labels=["type:task"])),

    # I3 四轴枚举
    ("I3", "正例：轴不在四轴内", vi.FAIL,
     lambda: [subj(body(能力增量="| 能力 | 轴 | 从 → 到 |\n|---|---|---|\n| Core → Unity 适配层 | Foo | `FAKE` → `PARTIAL` |"))], ctx),
    ("I3", "正例：`到` 不是该轴合法状态", vi.FAIL,
     lambda: [subj(body(能力增量="| 能力 | 轴 | 从 → 到 |\n|---|---|---|\n| Core → Unity 适配层 | Implementation | `FAKE` → `MAYBE` |"))], ctx),
    ("I3", "反例：合法轴与状态", vi.PASS, lambda: [subj()], ctx),

    # I4 Design 未 ACCEPTED 不得声明 Implementation 迁移
    ("I4", "正例：Design=UNRESOLVED 的能力却声明 Implementation 迁移", vi.FAIL,
     lambda: [subj(body(能力增量="| 能力 | 轴 | 从 → 到 |\n|---|---|---|\n| 探索与接敌 | Implementation | `NONE` → `PARTIAL` |"))], ctx),
    ("I4", "反例：Design=ACCEPTED 的能力", vi.PASS, lambda: [subj()], ctx),

    # I5 引用存在性
    ("I5", "正例：blocked-by 指向不存在的编号", vi.FAIL,
     lambda: [subj(body(依赖="blocked-by: #999999\nconsumed-by: 终态（fixture）\nrequires: 无"))],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM]))),
    ("I5", "正例：consumed-by 待建 → 警告（A3 弱化形态）", vi.WARN,
     lambda: [subj(body(依赖="blocked-by: 无\nconsumed-by: 待建:下游还没建\nrequires: 无"))],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM]))),
    ("I5", "反例：无前置 + 终态消费", vi.PASS, lambda: [subj()],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM]))),

    # I6 门禁解析（含 #134 回归）
    ("I6", "正例：门禁行的脚本路径不存在", vi.FAIL,
     lambda: [subj(body(门禁="python3 code/tools/nope_missing.py"))], ctx),
    ("I6", "正例（#134 回归）：散文门禁行里的文档路径不算门禁", vi.FAIL,
     lambda: [subj(body(门禁="validate_ceiling_generator（**本 issue 交付的新门禁**——按 "
                            "`design/engineering/issue-process.md` §4.1.1 例外 1：允许引用尚不存在但由本 issue 交付的门禁）"))],
     ctx),
    ("I6", "反例：真实 gate id", vi.PASS, lambda: [subj()], ctx),

    # I7 blocked-by 未关闭时不得 in-progress
    ("I7", "正例：前置仍 OPEN 却标 in-progress", vi.FAIL,
     lambda: [subj(body(依赖="blocked-by: #5\nconsumed-by: 终态（fixture）\nrequires: 无"),
                   labels=("type:task", "state:in-progress"))],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM, 5]))),
    ("I7", "反例：无前置且 in-progress", vi.PASS,
     lambda: [subj(labels=("type:task", "state:in-progress"))],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM]))),

    # I8 路径 / 段引用
    ("I8", "正例：正文命名了不存在的仓库路径且未标注缺失", vi.FAIL,
     lambda: [subj(body(动机="动机：见 `code/tools/no_such_module.py`。"))], ctx),
    ("I8", "正例：路径**名含标记词**也不得被豁免（标记须在散文里）", vi.FAIL,
     lambda: [subj(body(动机="动机：见 `code/tools/尚未用完.py`。"))], ctx),
    ("I8", "正例：同行显式标注「待建」→ 降为警告（例外 4）", vi.WARN,
     lambda: [subj(body(动机="动机：新增 `code/tools/将来才有的.py`（待建，本 issue 交付）。"))], ctx),
    ("I8", "反例：路径都存在", vi.PASS, lambda: [subj()], ctx),

    # I9 脆弱引用
    ("I9", "正例：`文件:行号` 式引用", vi.WARN,
     lambda: [subj(body(动机="动机：见 `ActionPlayer.cs:42` 那一行。"))], ctx),
    ("I9", "反例：无行号引用", vi.PASS, lambda: [subj()], ctx),

    # I10 归档隔离 + 废弃术语
    ("I10", "正例：引用垃圾桶路径", vi.FAIL,
     lambda: [subj(body(动机="动机：见 `code/unity/README.md` 与 design/archive/trash/x.md。"))], ctx),
    ("I10", "正例：使用已废弃术语 → 警告", vi.WARN,
     lambda: [subj(body(动机=f"动机：沿用{DEP_TERM}旧模型。"))], ctx) if DEP_TERM else None,
    ("I10", "反例：无垃圾桶路径、无废弃术语", vi.PASS, lambda: [subj()], ctx),

    # I11 单线程
    ("I11", "正例：两条同时 in-progress", vi.FAIL,
     lambda: [subj(number=101, labels=("type:task", "state:in-progress")),
              subj(number=102, labels=("type:task", "state:in-progress"))],
     lambda: ctx(snapshot=snap(open_numbers=[101, 102]))),
    ("I11", "反例：只有一条 in-progress", vi.PASS,
     lambda: [subj(number=101, labels=("type:task", "state:in-progress")),
              subj(number=102)],
     lambda: ctx(snapshot=snap(open_numbers=[101, 102]))),

    # I12 计数
    ("I12", "正例：验收标准 9 条（超上限 8）", vi.FAIL,
     lambda: [subj(body(验收标准="\n".join(f"- [ ] 第 {i} 条" for i in range(1, 10))))], ctx),
    ("I12", "反例：2 条验收 / 1 行能力增量 / 1 条门禁", vi.PASS, lambda: [subj()], ctx),

    # I13 并行就绪的文件集合相交
    ("I13", "正例：两条就绪 issue 都改 gates.json", vi.WARN,
     lambda: [subj(number=101), subj(number=102)],
     lambda: ctx(snapshot=snap(open_numbers=[101, 102]))),
    ("I13", "正例：前置**全部已关闭** → 仍算就绪，故仍报相交", vi.WARN,
     lambda: [subj(body(依赖="blocked-by: #5\nconsumed-by: 终态（fixture）\nrequires: 无")),
              subj(number=102)],
     lambda: ctx(snapshot=snap(open_numbers=[101, 102], closed=[5]))),
    ("I13", "反例：两条就绪但文件集合不相交", vi.PASS,
     lambda: [subj(number=101),
              subj(body(预期差分="允许变化（仓库相对路径）：\n- `data/action_set.json`\n\n预期不变：\n- 其它不动"))],
     lambda: ctx(snapshot=snap(open_numbers=[101, 102]))),

    # I14 正文 blocked-by 与原生依赖边一致
    ("I14", "正例：正文声明 blocked-by 但原生边为空", vi.WARN,
     lambda: [subj(body(依赖="blocked-by: #5\nconsumed-by: 终态（fixture）\nrequires: 无"))],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM, 5], native={SUBJECT_NUM: set()}))),
    ("I14", "反例：两侧一致", vi.PASS, lambda: [subj()],
     lambda: ctx(snapshot=snap(open_numbers=[SUBJECT_NUM], native={SUBJECT_NUM: set()}))),
]
CASES = [c for c in CASES if c is not None]


def snapshot_key_contract():
    """静态契约：规则读取的 snapshot 键 ⊆ fetch_snapshot 产出的键。

    这条用例的存在理由：I13 曾读 `snapshot["closed_numbers"]` 而 fetch_snapshot
    **从不产出**该键 → 恒为空集 → 「blocked-by 全部已关闭」判据永不成立。
    只跑规则函数发现不了（注入的字典里我给了那个键），只跑 --from-github 也发现不了
    （不报错、只是漏报）。故用静态比对把它钉住。
    """
    src = (HERE / "validate_issues.py").read_text(encoding="utf-8")
    read = set(re.findall(r'snapshot\.get\(\s*"([^"]+)"', src))
    read |= set(re.findall(r'snapshot\["([^"]+)"\]', src))
    produced = set()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "fetch_snapshot":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                    produced |= {k.value for k in sub.value.keys if isinstance(k, ast.Constant)}
    missing = sorted(read - produced)
    return read, produced, missing


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    failures = []
    print(f"validate_issues.py 规则 fixture —— {len(CASES)} 条用例 + 1 条快照键契约\n")

    per_rule = {}
    for rule_id, name, expect, mk_subjects, mk_ctx in CASES:
        c = mk_ctx()
        got = status_of(rule_id, mk_subjects(), c)
        ok = got == expect
        per_rule.setdefault(rule_id, [0, 0])
        per_rule[rule_id][0 if ok else 1] += 1
        if not ok:
            failures.append(f"[{rule_id}] {name}: 期望 {expect}，实得 {got}")
        if verbose or not ok:
            print(f"  {'✅' if ok else '❌'} [{rule_id}] {name} —— {got}")

    read, produced, missing = snapshot_key_contract()
    if missing:
        failures.append(f"[契约] 规则读取的 snapshot 键未被 fetch_snapshot 产出: {missing}")
        print(f"  ❌ [契约] snapshot 键: 规则读 {sorted(read)} / 快照产 {sorted(produced)}"
              f" —— 缺 {missing}")
    else:
        print(f"  ✅ [契约] snapshot 键：规则读的 {len(read)} 个键全部由 fetch_snapshot 产出")

    if verbose:
        print("\n  按规则：")
        for rid in sorted(per_rule, key=lambda x: int(x[1:])):
            ok_n, bad_n = per_rule[rid]
            print(f"    {rid:5} 通过 {ok_n} · 不符 {bad_n}")

    covered = {c[0] for c in CASES}
    all_rules = {r.id for r in vi.RULES}
    if all_rules - covered:
        failures.append(f"[覆盖] 未覆盖的规则: {sorted(all_rules - covered)}")

    print()
    if failures:
        for f in failures:
            print(f"🔴 {f}")
        print(f"\n{'=' * 60}\n❌ {len(failures)} 处不符（共 {len(CASES)} 条用例）\n{'=' * 60}")
        sys.exit(1)
    print(f"{'=' * 60}\n✅ {len(CASES)} 条用例全部符合预期"
          f"（覆盖 {len(all_rules)}/{len(all_rules)} 条规则）\n{'=' * 60}")
    sys.exit(0)


if __name__ == "__main__":
    main()
