#!/usr/bin/env python3
"""
validate_trash_isolation.py 的注册表驱动分支测试 —— **三档执法策略各一正一反**（#159）。

**为什么需要它**：
  `validate_trash_isolation.py` 的废弃术语检查 2026-09-15 起有两个来源——**硬编码表 7 条正则**
  （检查 2）与**注册表驱动的逐术语执法策略**（检查 4）。后者是本条新增的，判定分散在
  "注册表字段 × 三档档位 × 行内豁免 × 整节豁免 × 引用式豁免"这几处，靠人读一遍代码看不出对错，
  而它的失效形态是**静默**的：档位接错了，扫描档可能一条都不报（门禁看起来全绿）。
  所以每档都要有（正例：该报的必须报）+（反例：不该报的必须不报）。

**判据**（对应 #159 的验收标准）：
  · `扫描` 档：活跃文档里的残留必须报出；引用式（行内代码 / 引号）、`⚠️ 已废弃` 行内与整节豁免下不报
  · `只登记` 档：**0 报告**（该串另有合法用法——盲目扫 `status` 实测会喷 77/32 条假阳性）
  · `关闭` 档：**0 报告**，但命中要进 `hits`（现存量要打印出来，欠账得在明处）
  · 缺字段 / 非法取值 ⇒ 按缺省 `扫描` 处理（fail-closed），并记进 hygiene
  · 检查 2 的硬编码模式**逐条不变**（这条测试把它的判定钉住，防后续改动顺手改坏）

**怎么测**：直接调函数、不联网、不起子进程；fixture 文档写在 `tempfile` 里，
**绝不写工作树**（[构建与测试 §四](../engineering/build-and-test.md) 的「工作树」判据）。

用法: python3 code/tools/test_validate_trash_isolation.py [-v]
退出码: 0 = 全部用例符合预期, 1 = 有用例不符
"""

import importlib.util
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
SPEC = importlib.util.spec_from_file_location(
    "validate_trash_isolation", HERE / "validate_trash_isolation.py")
vti = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vti)

SCAN = vti.ENFORCEMENT_SCAN
REG = vti.ENFORCEMENT_REGISTER
OFF = vti.ENFORCEMENT_OFF


def spec(*items):
    """(术语, 档位) 列表 → loading 后的 terms 形状（依赖注入，不读真注册表）。"""
    return {name: {"enforcement": tier, "replacement": "（fixture 替代：新模型）"}
            for name, tier in items}


def scan(files, term_spec):
    """把 {文件名: 文本} 写进临时目录，跑注册表驱动扫描 → (errors, hits)。"""
    with tempfile.TemporaryDirectory() as d:
        md_files = []
        for name, text in files.items():
            p = pathlib.Path(d) / name
            p.write_text(text, encoding="utf-8")
            md_files.append((name, p))
        return vti.scan_registry_terms(md_files, term_spec)


def hardcoded(text):
    """只跑检查 2（硬编码表）——防回归用。"""
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "fixture.md"
        p.write_text(text, encoding="utf-8")
        return vti.check_terms([("fixture.md", p)])


# ── 用例表：(区域, 名称, 期望 errors, 期望 hits 总数, () → (errors, hits)) ──
# errors = 报出来的违规处数；hits = 三档合起来的命中处数（只登记/关闭档也要收，供现存量打印）
CASES = [
    # ── 扫描档：正例 / 反例 ──────────────────────────────
    ("扫描", "正例：活跃文档里出现扫描档术语 → 报出",
     1, 1, lambda: scan({"a.md": "这里还在按 测试术语 的旧写法描述。\n"}, spec(("测试术语", SCAN)))),
    ("扫描", "反例：同一文档、术语不在注册表里 → 0 报告（删条目即恢复）",
     0, 0, lambda: scan({"a.md": "这里还在按 测试术语 的旧写法描述。\n"}, spec())),
    ("扫描", "反例：只出现在行内代码里（引用/列举）→ 0 报告",
     0, 0, lambda: scan({"a.md": "把 `测试术语` 标为 deprecated 时要注意。\n"}, spec(("测试术语", SCAN)))),
    ("扫描", "反例：只出现在「」引号里（引用/列举）→ 0 报告",
     0, 0, lambda: scan({"a.md": "正文只是列举「测试术语」这个词。\n"}, spec(("测试术语", SCAN)))),
    ("扫描", "反例：行内有 ⚠️ 已废弃 记载 → 0 报告",
     0, 0, lambda: scan({"a.md": "测试术语（⚠️ 已废弃，2026-09-15）\n"}, spec(("测试术语", SCAN)))),
    ("扫描", "反例：行内明文否定（不设/不需要/替代）→ 0 报告",
     0, 0, lambda: scan({"a.md": "本仓不设测试术语。\n替代方案见新模型。\n"}, spec(("测试术语", SCAN)))),
    ("扫描", "反例：落在「⚠️ 已废弃」标题下的整节 → 0 报告",
     0, 0, lambda: scan({"a.md": "# 正文\n\n## 旧模型 ⚠️ 已废弃\n\n测试术语当年是这么算的。\n\n## 新模型\n\n没了。\n"},
                        spec(("测试术语", SCAN)))),
    ("扫描", "正例：⚠️ 已废弃节**之外**的同一术语仍报出（整节豁免不越界）",
     1, 1, lambda: scan({"a.md": "# 正文\n\n## 旧模型 ⚠️ 已废弃\n\n历史。\n\n## 新模型\n\n仍写 测试术语。\n"},
                        spec(("测试术语", SCAN)))),
    ("扫描", "正例：同一术语在两份文档各出现一次 → 报 2 处",
     2, 2, lambda: scan({"a.md": "测试术语残留。\n", "b.md": "又一个 测试术语。\n"},
                        spec(("测试术语", SCAN)))),
    ("扫描", "反例：ASCII 术语要求词边界（AP 不得命中 CAPTCHA/APP）",
     0, 0, lambda: scan({"a.md": "CAPTCHA 与 APP 都不是那个缩写。\n"}, spec(("AP", SCAN)))),
    ("扫描", "正例：ASCII 术语独立成词 → 报出",
     1, 1, lambda: scan({"a.md": "每回合 AP +1。\n"}, spec(("AP", SCAN)))),

    # ── 只登记档：0 报告（真注册表里 β / η / κ / CPM 就是这档） ──
    ("只登记", "正例：只登记档 + 活跃文档大量出现 → 0 报告",
     0, 3, lambda: scan({"a.md": "β(t) 是易感慢变量。\nβ 受体阻断剂。\n还有 β。\n"},
                        spec(("β", REG)))),
    ("只登记", "反例：同一文本改成扫描档 → 报出（差别只在档位）",
     1, 1, lambda: scan({"a.md": "β(t) 是易感慢变量。\n"}, spec(("β", SCAN)))),

    # ── 关闭档：0 报告，但命中要进 hits（现存量） ──────────────
    ("关闭", "正例：关闭档 + 活跃文档现有残留 → 0 报告，但 hits 收下 2 处",
     0, 2, lambda: scan({"a.md": "AP +1。\nAP 积攒上限 2。\n"}, spec(("AP", OFF)))),
    ("关闭", "反例：关闭档不产生任何 error（不得因为欠账把门禁判红）",
     0, 0, lambda: scan({"a.md": "干净文档。\n"}, spec(("AP", OFF)))),

    # ── 检查 2（硬编码表）钉住：逐条不变 ─────────────────────
    ("硬编码", "正例：37 个技能（旧计数）→ 报出",
     1, 0, lambda: (hardcoded("表里有 37 个技能。\n"), {})),
    ("硬编码", "正例：激活点预算 → 报出",
     1, 0, lambda: (hardcoded("恢复激活点预算。\n"), {})),
    ("硬编码", "正例：每回合…激活点（旧模型）→ 报出",
     1, 0, lambda: (hardcoded("每回合恢复激活点。\n"), {})),
    ("硬编码", "反例：当前口径（50 个操作 / 聚焦容量）→ 0 报告",
     0, 0, lambda: (hardcoded("当前 50 个操作；容量约束由聚焦容量提供。\n"), {})),
    ("硬编码", "反例：行内 ⚠️ 已废弃 记载 → 0 报告",
     0, 0, lambda: (hardcoded("激活点预算（⚠️ 已废弃）\n"), {})),
]


# ── 契约用例：(名称, () → (bool, 说明)) ──────────────────────
def contract_registry_tiers():
    """真注册表：全部 deprecated 条目带合法 `enforcement` 取值。"""
    terms, hygiene = vti.load_registry_terms()
    bad = list(hygiene["missing"]) + [n for n, _ in hygiene["invalid"]]
    if bad:
        return False, f"这些 deprecated 条目没写（或写错）enforcement: {' '.join(bad)}"
    tiers = {t: sum(1 for v in terms.values() if v["enforcement"] == t)
             for t in vti.ENFORCEMENT_TIERS}
    return True, (f"{len(terms)} 条 deprecated = " +
                  " · ".join(f"{t} {n}" for t, n in tiers.items()))


def contract_scan_tier_is_green():
    """真注册表 + 真活跃文档：`扫描` 档当前 0 命中（否则门禁当场红）。"""
    terms, _ = vti.load_registry_terms()
    md = [(str(p.relative_to(vti.ROOT)), p) for p in vti.collect_md_files()]
    errors, hits = vti.scan_registry_terms(md, terms)
    scanned = [n for n, v in terms.items() if v["enforcement"] == SCAN]
    if errors:
        return False, f"扫描档报出 {len(errors)} 处残留（应先清理或改档）: {errors[0][:120]}"
    if len(scanned) == 0:
        return False, "扫描档一条都没有——门禁空跑（WORKFLOW §5.1：零测试不是通过）"
    return True, f"扫描档 {len(scanned)} 条 · 活跃文档 {len(md)} 个 · 命中 0 处"


def contract_hardcoded_table_frozen():
    """检查 2 的硬编码表条数不变（#159 预期不变：原判定逐条不动）。

    条数 = **7**（#159 正文写的是「6 类」——表里 `37` 有两种写法，是同一类的两条正则；
    这里按表的实际条数钉住，免得"6"这个数被当成判据）。
    """
    n = len(vti.DEPRECATED_TERMS)
    return (n == 7), f"DEPRECATED_TERMS 有 {n} 条（期望 7：37×2 + 激活点预算 + 激活点模型 + 在线手动选择 + 手动激活 + 每回合激活点）"


def contract_enforcement_fail_closed():
    """缺字段 / 非法取值 ⇒ 按缺省 `扫描` 处理，并记进 hygiene。"""
    doc = {"terms": {
        "无档位": {"status": "deprecated", "deviation_reason": "fixture"},
        "错档位": {"status": "deprecated", "deviation_reason": "fixture", "enforcement": "scan"},
        "活跃的": {"status": "active", "enforcement": "扫描"},
    }}
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "term_registry.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        terms, hygiene = vti.load_registry_terms(p)

    problems = []
    if set(terms) != {"无档位", "错档位"}:
        problems.append(f"只应收集 deprecated 条目，实得 {sorted(terms)}")
    for name in ("无档位", "错档位"):
        if terms.get(name, {}).get("enforcement") != vti.ENFORCEMENT_DEFAULT:
            problems.append(f"{name} 未按缺省 {vti.ENFORCEMENT_DEFAULT} 处理")
    if hygiene["missing"] != ["无档位"]:
        problems.append(f"missing 记录不对: {hygiene['missing']}")
    if hygiene["invalid"] != [("错档位", "scan")]:
        problems.append(f"invalid 记录不对: {hygiene['invalid']}")
    if problems:
        return False, "；".join(problems)
    return True, "缺字段/非法取值都按缺省 扫描 处理，且都记进 hygiene"


CONTRACTS = [
    ("注册表契约：全部 deprecated 带合法 enforcement", contract_registry_tiers),
    ("注册表契约：扫描档在真活跃文档上 0 命中", contract_scan_tier_is_green),
    ("防回归：硬编码表条数不变（7 条）", contract_hardcoded_table_frozen),
    ("fail-closed：缺字段 / 非法取值 ⇒ 扫描 + hygiene", contract_enforcement_fail_closed),
]


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    n_cases = len(CASES) + len(CONTRACTS)
    print(f"validate_trash_isolation.py 注册表驱动分支 fixture —— {n_cases} 条用例\n")

    failures = []
    for area, name, want_err, want_hits, fn in CASES:
        try:
            errors, hits = fn()
            got_err, got_hits = len(errors), sum(len(v) for v in hits.values())
            ok = (got_err == want_err and got_hits == want_hits)
            detail = f"errors={got_err}/{want_err} hits={got_hits}/{want_hits}"
        except Exception as e:                      # 用例自身炸了也是失败，不得淡化成通过
            ok, detail = False, f"用例异常 {type(e).__name__}: {e}"
        print(f"  {'✅' if ok else '❌'} [{area}] {name}  —— {detail}")
        if not ok or verbose:
            if not ok:
                failures.append(f"[{area}] {name} ({detail})")

    print()
    for name, fn in CONTRACTS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"用例异常 {type(e).__name__}: {e}"
        print(f"  {'✅' if ok else '❌'} [契约] {name}  —— {detail}")
        if not ok:
            failures.append(f"[契约] {name} ({detail})")

    print("\n" + "=" * 60)
    if failures:
        print(f"❌ {len(failures)} 条用例不符：")
        for f in failures:
            print(f"   - {f}")
        sys.exit(1)
    print(f"✅ {n_cases} 条用例全部符合预期（三档 enforcement 各一正一反 + 硬编码防回归 + 契约 4 条）")
    sys.exit(0)


if __name__ == "__main__":
    main()
