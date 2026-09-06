"""
资格签名校验器 — 24 经历型资格门可执行化（回放门 + 反样本测试）

正典依据：规则/技能树系统/创伤记忆转化接口.md §3.2.1（事件→候选集）+
§3.2.2（批次 1-2 资格签名表，2026-09-06 定案：24/24 经历型全量）。

用途：
  1. 回放门：给定结构化患者输入（事件类型 + 记忆表征 F/N/D_seg + #87 临床史声明）
     → 判定 24 病 Eligibility ∈ {ELIGIBLE, INELIGIBLE, UNDETERMINED}
  2. 反样本测试：构造边界样本验证签名不误放

签名形态（三型，详见转化接口 §3.2.2 批次签名表）：
  - 声明型 A：必要正向原子 AND（1）+ 排除原子（任一 =1 → INELIGIBLE）
  - 表征型 M：PTSD = ∃m: 事件类型∈{威胁/暴力,性创伤} ∧ F≥0.80 ∧ N≤0.40
  - 混合型 C：DID = IDENTITY_STATE_HISTORY=1 ∧ ∃m: D_seg≥0.85
  - 延迟项：[NEW 初值可调] θ_F/θ_N/θ_Dseg（边界样本测试后校准）

用法：
  python3 tools/validate_eligibility.py --self-test   # 反样本自测
  python3 tools/validate_eligibility.py patient.json  # 回放单患者
"""

import json
import sys

# ============================================================
# 数据层：转化接口 §3.2.1 事件→候选集（召回）+ §3.2.2 签名表
# ============================================================

# 事件类型 → 候选病（§3.2.1 全表；含新增行）
EVENT_CANDIDATES = {
    "威胁/暴力": ["PTSD", "惊恐", "特定恐惧", "偏执型SZ"],
    "丧失/哀悼": ["MDD", "PDD", "BD-I", "BD-II", "环性"],
    "性创伤": ["PTSD", "DID", "BPD", "BN", "AN", "BED"],
    "社会伤害": ["BPD", "社交焦虑", "分裂型", "BN", "BED", "未分化SZ"],
    "忽视/遗弃": ["BPD", "MDD", "ASPD", "分裂情感"],
    "生理/疾病": ["躯体症状", "惊恐", "MDD"],
    "经济/剥夺": ["SUD", "MDD", "拖延", "环性"],
    "慢性冲突/高压": ["GAD", "MDD", "OCD", "SUD", "偏执型SZ"],
    "控制剥夺/完美主义": ["AN", "OCD"],
    "公开羞辱/失败": ["社交焦虑", "BN", "BED", "未分化SZ"],
}

# 病 → 候选类型名（中文，规范化：躯体症状=SSD 名、环性=持续性心境）
DISPLAY = {
    "躯体症状": "躯体症状(SSD)", "环性": "环性(持续性心境)",
}

# 病 → 必要正向原子 AND + 排除原子（声明型 A）
# atom 语义：#87 规范化声明 ∈ {1, 0, MISSING}；MISSING → UNDETERMINED
NECESSARY = {
    "MDD": ["DEPRESSIVE_EPISODE_HISTORY"],
    "SUD": ["SUBSTANCE_USE_HISTORY"],
    "BD-I": ["MANIA_HISTORY"],
    "BD-II": ["HYPOMANIA_HISTORY", "DEPRESSIVE_EPISODE_HISTORY"],
    "环性": ["CYCLIC_MOOD_HISTORY"],
    "BPD": ["BPD_PATTERN_HISTORY"],
    "躯体症状": ["SOMATIC_SYMPTOM_HISTORY", "SYMPTOM_PSYCHOLOGICAL_OVERINVESTMENT",
                 "SYMPTOM_DURATION_6M"],
    "偏执型SZ": ["SZ_POSITIVE_COURSE_HISTORY"],
    "未分化SZ": ["SZ_POSITIVE_COURSE_HISTORY"],
    "分裂型": ["STPD_PATTERN_HISTORY"],
    "分裂情感": ["SZAFFECTIVE_COURSE_HISTORY"],
    "AN": ["LOW_WEIGHT_PATTERN", "WEIGHT_GAIN_PREVENTION", "BODY_IMAGE_DISTURBANCE"],
    "BN": ["BINGE_HISTORY", "COMPENSATORY_BEHAVIOR_HISTORY", "BODY_IMAGE_DISTURBANCE"],
    "BED": ["BINGE_HISTORY", "BED_DISTRESS_PATTERN"],
    "PDD": ["PDD_PERSISTENT_DEPRESSION_PATTERN"],
    "惊恐": ["PANIC_PATTERN_HISTORY"],
    "特定恐惧": ["SPECIFIC_PHOBIA_PATTERN_HISTORY"],
    "社交焦虑": ["SOCIAL_ANXIETY_PATTERN_HISTORY"],
    "GAD": ["GAD_WORRY_PATTERN_HISTORY"],
    "ASPD": ["ASPD_PATTERN_HISTORY", "CONDUCT_DISORDER_HISTORY"],
    "拖延": ["PROCRASTINATION_PATTERN_HISTORY"],
    "OCD": ["OCD_PATTERN_HISTORY"],
}
# 排除原子（任一 =1 → INELIGIBLE）
EXCLUDE = {
    "MDD": ["MANIA_HISTORY", "HYPOMANIA_HISTORY"],
    "BD-II": ["MANIA_HISTORY"],
    "PDD": ["MANIA_HISTORY", "HYPOMANIA_HISTORY", "CYCLIC_MOOD_HISTORY"],
}
# 混合型 C：DID = IDENTITY_STATE_HISTORY=1 ∧ ∃ 相关记忆 D_seg ≥ θ_Dseg
MIXED_DID = {"atom": "IDENTITY_STATE_HISTORY", "θ_Dseg": 0.85}
# 表征型 M：PTSD（唯一）——∃m: 事件∈{威胁/暴力,性创伤} ∧ F≥θ_F ∧ N≤θ_N
PTSD_EVENTS = {"威胁/暴力", "性创伤"}
THETA_F, THETA_N = 0.80, 0.40

VERIFIED = set(NECESSARY) | {"PTSD", "DID"}  # 24 经历型全部


# ============================================================
# 判定器
# ============================================================

def eligibility_for(patient: dict) -> dict:
    """patient: {events: [event_type...], memories: [{event_type,F,N,D_seg}...],
                 declarations: {atom: 1|0|"MISSING"}}"""
    events = set(patient.get("events", []))
    memories = patient.get("memories", [])
    decl = patient.get("declarations", {})
    recalled = set()
    for e in events:
        recalled |= set(EVENT_CANDIDATES.get(e, []))
    results = {}
    for d in sorted(VERIFIED):
        # 召回门（§3.2.1）：病须被事件召回
        if d not in recalled:
            results[d] = ("INELIGIBLE", "未召回（事件类型不含该病候选）")
            continue
        # PTSD：表征型 M
        if d == "PTSD":
            hit = [m for m in memories if m.get("event_type") in PTSD_EVENTS
                   and m.get("F", -1) is not None and m.get("N", -1) is not None]
            if any(m["F"] >= THETA_F and m["N"] <= THETA_N for m in hit):
                results[d] = ("ELIGIBLE", f"∃威胁/性创伤记忆 F≥{THETA_F}∧N≤{THETA_N}")
            elif hit and all(m["F"] < THETA_F or m["N"] > THETA_N for m in hit):
                results[d] = ("INELIGIBLE", "事件在但记忆已叙事化（F 低/N 高）")
            else:
                results[d] = ("UNDETERMINED", "威胁/性创伤记忆表征 MISSING")
            continue
        # DID：混合型 C
        if d == "DID":
            a = decl.get("IDENTITY_STATE_HISTORY")
            seg_ok = any(m.get("D_seg", 0) >= MIXED_DID["θ_Dseg"] for m in memories)
            if a == 1 and seg_ok:
                results[d] = ("ELIGIBLE", "IDENTITY_STATE_HISTORY=1 ∧ ∃D_seg≥0.85")
            elif a == 0 or (a == 1 and not seg_ok and all(m.get("D_seg") is not None for m in memories)):
                results[d] = ("INELIGIBLE", "身份声明=0 或 无区隔化记忆")
            else:
                results[d] = ("UNDETERMINED", "身份声明或区隔化 MISSING")
            continue
        # 声明型 A：必要原子 AND + 排除原子（#113 组合规则：硬证据优先于 MISSING）
        nec = NECESSARY.get(d, [])
        exc = EXCLUDE.get(d, [])
        # ① 必要原子显式 0 → INELIGIBLE（一票否决）
        for p in nec:
            if decl.get(p) == 0:
                results[d] = ("INELIGIBLE", f"必要原子 {p}=0")
                break
        else:
            # ② 排除原子显式 1 → INELIGIBLE（一票否决，优先于其他 MISSING）
            for n in exc:
                if decl.get(n) == 1:
                    results[d] = ("INELIGIBLE", f"排除原子 {n}=1")
                    break
            else:
                # ③ 必要原子 MISSING → UNDETERMINED
                miss_p = [p for p in nec if decl.get(p, "MISSING") == "MISSING"]
                if miss_p:
                    results[d] = ("UNDETERMINED", f"必要原子 {miss_p[0]}=MISSING")
                    continue
                # ④ 排除原子 MISSING → UNDETERMINED
                miss_n = [n for n in exc if decl.get(n, "MISSING") == "MISSING"]
                if miss_n:
                    results[d] = ("UNDETERMINED", f"排除原子 {miss_n[0]}=MISSING")
                    continue
                results[d] = ("ELIGIBLE", "全部必要原子=1 且排除原子=0")
        continue
    return results


# ============================================================
# 反样本自测（构造边界样本验证签名不误放）
# ============================================================

SELF_TESTS = [
    # (名称, patient, 期望: {病: 状态})
    ("PTSD 正样本（威胁事件+碎片记忆）",
     {"events": ["威胁/暴力"], "memories": [{"event_type": "威胁/暴力", "F": 0.95, "N": 0.15, "D_seg": 0.05}],
      "declarations": {}},
     {"PTSD": "ELIGIBLE"}),
    ("PTSD 反样本（威胁事件+叙事化记忆）",
     {"events": ["威胁/暴力"], "memories": [{"event_type": "威胁/暴力", "F": 0.4, "N": 0.8, "D_seg": 0.05}],
      "declarations": {}},
     {"PTSD": "INELIGIBLE"}),
    ("MDD 正样本（完整声明：显式排除 0）",
     {"events": ["丧失/哀悼"], "memories": [],
      "declarations": {"DEPRESSIVE_EPISODE_HISTORY": 1, "MANIA_HISTORY": 0, "HYPOMANIA_HISTORY": 0}},
     {"MDD": "ELIGIBLE"}),
    ("MDD 排除（躁狂史）",
     {"events": ["丧失/哀悼"], "memories": [], "declarations": {"DEPRESSIVE_EPISODE_HISTORY": 1, "MANIA_HISTORY": 1}},
     {"MDD": "INELIGIBLE"}),
    ("PDD 排除（环性史，硬否决优先于 MANIA MISSING）",
     {"events": ["丧失/哀悼"], "memories": [],
      "declarations": {"PDD_PERSISTENT_DEPRESSION_PATTERN": 1, "CYCLIC_MOOD_HISTORY": 1}},
     {"PDD": "INELIGIBLE"}),
    ("BPD 正样本",
     {"events": ["性创伤"], "memories": [], "declarations": {"BPD_PATTERN_HISTORY": 1}},
     {"BPD": "ELIGIBLE"}),
    ("BPD 声明否定",
     {"events": ["性创伤"], "memories": [], "declarations": {"BPD_PATTERN_HISTORY": 0}},
     {"BPD": "INELIGIBLE"}),
    ("SSD 三原子不齐",
     {"events": ["生理/疾病"], "memories": [],
      "declarations": {"SOMATIC_SYMPTOM_HISTORY": 1, "SYMPTOM_PSYCHOLOGICAL_OVERINVESTMENT": 0,
                       "SYMPTOM_DURATION_6M": 1}},
     {"躯体症状": "INELIGIBLE"}),
    ("DID 正样本",
     {"events": ["性创伤"], "memories": [{"event_type": "性创伤", "F": 0.9, "N": 0.1, "D_seg": 0.95}],
      "declarations": {"IDENTITY_STATE_HISTORY": 1}},
     {"DID": "ELIGIBLE"}),
    ("DID 有身份无区隔",
     {"events": ["性创伤"], "memories": [{"event_type": "性创伤", "F": 0.5, "N": 0.6, "D_seg": 0.1}],
      "declarations": {"IDENTITY_STATE_HISTORY": 1}},
     {"DID": "INELIGIBLE"}),
    ("GAD 担忧样本不误放 OCD（无召回）",
     {"events": ["慢性冲突/高压"], "memories": [],
      "declarations": {"GAD_WORRY_PATTERN_HISTORY": 1, "OCD_PATTERN_HISTORY": "MISSING"}},
     {"GAD": "ELIGIBLE", "OCD": "UNDETERMINED"}),
    ("ASPD 缺品行障碍史",
     {"events": ["忽视/遗弃"], "memories": [],
      "declarations": {"ASPD_PATTERN_HISTORY": 1, "CONDUCT_DISORDER_HISTORY": 0}},
     {"ASPD": "INELIGIBLE"}),
    ("未召回病（丧失事件不召回惊恐）",
     {"events": ["丧失/哀悼"], "memories": [], "declarations": {"PANIC_PATTERN_HISTORY": 1}},
     {"惊恐": "INELIGIBLE"}),
    ("拖延自锚正样本",
     {"events": ["经济/剥夺"], "memories": [], "declarations": {"PROCRASTINATION_PATTERN_HISTORY": 1}},
     {"拖延": "ELIGIBLE"}),
]


def run_self_test():
    passed, failed = 0, []
    for name, patient, expect in SELF_TESTS:
        res = eligibility_for(patient)
        ok = all(res.get(d, ("", ""))[0] == s for d, s in expect.items())
        if ok:
            passed += 1
        else:
            failed.append((name, {d: res.get(d, ("未召回", ""))[0] for d in expect}))
    print(f"=== 反样本自测：{passed}/{len(SELF_TESTS)} 通过 ===")
    for name, got in failed:
        print(f"  FAIL {name}: 期望 {dict(SELF_TESTS[[n for n,_,_ in SELF_TESTS].index(name)][2])} 实得 {got}")
    return not failed


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(0 if run_self_test() else 1)
    if len(sys.argv) > 1:
        patient = json.load(open(sys.argv[1], encoding="utf-8"))
        res = eligibility_for(patient)
        elig = {d: (s, r) for d, (s, r) in res.items() if s == "ELIGIBLE"}
        print("ELIGIBLE:", elig if elig else "(无——全部 INELIGIBLE/UNDETERMINED)")
        print("UNDETERMINED:", [d for d, (s, _) in res.items() if s == "UNDETERMINED"])
        return
    run_self_test()


if __name__ == "__main__":
    main()
