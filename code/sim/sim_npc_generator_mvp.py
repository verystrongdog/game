"""
#87 A′-Generator 最小可用实现（MVP）
====================================
目标：证明"从结构化输入自动得到一个合法、可追溯、能经过资格门的患者 artifact"。
第一版不实现文学叙事生成——产物是 gen.json + 机械版 trace + 资格门裁决。

流水线（每步可追溯）：
    Matrix(社会演化矩阵) → SoilSampler → EventGenerator → MemoryBuilder
    → Transformer(资格门) → ArtifactDeriver → gen.json → Q6 六轴统计

铁律（评审 t6a97b213/t6a97b2c2 确认）：
  1. MVP 不允许为让患者生成成功而修改资格门
  2. 每步有 trace（为什么这个出生年/事件/记忆/资格判定）
  3. R=100 固定 seed 分布测试，第一轮不优化——先记录系统实际产生什么

数据来源（引用即读取铁律）：
  - 社会演化矩阵: ../规格/素材/社会演化矩阵.md §八
  - 事件→候选集: design/rules/skill-tree/创伤记忆转化接口.md §3.2.1
  - 资格门五原子: 转化接口 §3.2.2 + 决策树 #113
"""

import random
import json
from dataclasses import dataclass, field, asdict

# ============================================================
# 数据层（从正典提取，MVP 内嵌为常量——后续可迁 JSON）
# ============================================================

# 社会演化矩阵 §八：出生年段 → 人生各阶段宏观事件（简化版）
# 每段给出 少年/青年/中年 的代表性宏观事件标签
ERA_MATRIX = [
    {"label": "1955-1965", "youth": ["文革", "上山下乡", "工农兵学员"], "young": ["恢复高考", "改革开放", "知青返城", "个体户"], "mid": ["国企改革", "下岗潮", "房改"]},
    {"label": "1965-1975", "youth": ["文革后期", "恢复高考", "改革开放"], "young": ["特区", "乡镇企业", "下海潮", "计划生育"], "mid": ["下岗潮", "打工潮", "1998医改房改"]},
    {"label": "1975-1985", "youth": ["改革开放", "义务教育法", "乡镇企业"], "young": ["打工潮", "高校扩招", "国企抓大放小"], "mid": ["房贷", "新农合", "金融风暴2008", "四万亿"]},
    {"label": "1985-1995", "youth": ["下岗潮家庭", "留守儿童", "扩招"], "young": ["大学扩招就业", "进城务工", "移动互联网"], "mid": ["房价", "精神卫生法2013", "内卷"]},
    {"label": "1995-2005", "youth": ["义务教育免费", "网络普及"], "young": ["大学普及化", "灵活就业", "心理健康话语"], "mid": []},
]

# 地域剖面（矩阵 §七 简化）：region → 社会特征标签
REGION_PROFILES = {
    "东北": ["单位制", "下岗潮重灾", "人口外流"],
    "长三角": ["乡镇企业", "民营", "外贸"],
    "珠三角": ["打工潮", "世界工厂", "移民"],
    "中西部": ["劳动力输出", "留守儿童", "农业"],
    "西部": ["贫困", "资源稀缺", "迷信习俗"],
}

# 事件类型 → 候选疾病集（转化接口 §3.2.1）
# 格式: event_type: {candidates: [(disease, is_primary)], description_pool: [...
EVENT_TYPE_CANDIDATES = {
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

# 事件池：每个宏观事件标签 → 可映射的事件类型 + 烈度范围
# （MVP 简化：宏观事件 → 创伤事件类型概率映射，用事件类型直接采样烈度）
# 事件类型基础烈度范围 [NEW 初值，MVP 测试用]
EVENT_A_RANGE = {
    "威胁/暴力": (0.5, 0.95), "丧失/哀悼": (0.4, 0.9), "性创伤": (0.7, 1.0),
    "社会伤害": (0.3, 0.7), "忽视/遗弃": (0.3, 0.6), "生理/疾病": (0.4, 0.8),
    "经济/剥夺": (0.3, 0.7), "慢性冲突/高压": (0.3, 0.6),
    "控制剥夺/完美主义": (0.3, 0.6), "公开羞辱/失败": (0.3, 0.6),
}

# 五基础资格原子（决策树 #113 Q2-12 核验闭合）
# atom: {disease: role}  role: 'necessary'(必要正向) / 'exclude'(排除)
ATOMS = ["DEPRESSIVE_EPISODE_HISTORY", "SUBSTANCE_USE_HISTORY", "MANIA_HISTORY", "HYPOMANIA_HISTORY", "CYCLIC_MOOD_HISTORY"]
# 疾病 → 必要正向原子（已核验的五病；未核验疾病资格 = UNDETERMINED 处理）
DISEASE_NECESSARY_ATOMS = {
    "MDD": ["DEPRESSIVE_EPISODE_HISTORY"],
    "SUD": ["SUBSTANCE_USE_HISTORY"],
    "BD-I": ["MANIA_HISTORY"],
    "BD-II": ["HYPOMANIA_HISTORY", "DEPRESSIVE_EPISODE_HISTORY"],  # 需轻躁狂史+抑郁史
    "环性": ["CYCLIC_MOOD_HISTORY"],
}
DISEASE_EXCLUDE_ATOMS = {
    "BD-I": [],  # 需躁狂史；无排除（BD-I 排除=器质等，MVP 不展开）
    "BD-II": ["MANIA_HISTORY"],  # 从未躁狂
    "MDD": ["MANIA_HISTORY", "HYPOMANIA_HISTORY"],  # 排除双相谱（若躁狂史则非 MDD）
}
# 未核验资格疾病的处理：资格规则未定义 → 统一 UNDETERMINED（MVP 只完整支持五病 + 其他标记）
VERIFIED_DISEASES = set(DISEASE_NECESSARY_ATOMS.keys())  # 五病已核验

# ============================================================
# 阶段 1: SoilSampler —— 采样出生年段/地域
# ============================================================
@dataclass
class Soil:
    era_label: str
    birth_year: int
    region: str
    social_conditions: list
    trace: list = field(default_factory=list)

def soil_sampler(rng: random.Random) -> Soil:
    era = rng.choice(ERA_MATRIX)
    region = rng.choice(list(REGION_PROFILES.keys()))
    # 出生年：在该段内随机
    y0, y1 = map(int, era["label"].split("-"))
    birth_year = rng.randint(y0, y1)
    conditions = REGION_PROFILES[region] + era["youth"]
    return Soil(
        era_label=era["label"], birth_year=birth_year, region=region,
        social_conditions=conditions,
        trace=[f"Soil: era={era['label']} region={region} birth={birth_year}",
               f"Soil: conditions={conditions}"])

# ============================================================
# 阶段 2+3: EventGenerator + MemoryBuilder
# ============================================================
@dataclass
class TraumaMemory:
    event_type: str
    A: float
    N: float
    F: float
    D_seg: float
    g: float
    k: float
    delta_I: float
    t_anchor: str
    trace: list = field(default_factory=list)

@dataclass
class LifeEvents:
    memories: list
    trace: list = field(default_factory=list)

# 诱发类型表: 躁狂/轻躁狂史 → 事件序列须含的诱发类型（双相谱临床: 丧失/慢性 诱发）
MANIA_TRIGGER_TYPES = ["丧失/哀悼", "慢性冲突/高压"]

# 声明×事件一致性规则（#87 Q3 MVP 发现, 2026-09-03）:
# 临床史声明独立于事件采样(#113 Q2-3 选 A 正向); 但 EventGenerator 须保证:
#   若 MANIA=1 → 事件序列须含 ≥1 诱发类型(丧失/慢性), 否则 BD-I 无从落病
#   若 HYPOMANIA=1 → 同上(BD-II 需诱发)
# 实现: 事件生成时若声明需诱发且未含, 强制补一条诱发事件

def sample_clinical_history(rng: random.Random) -> dict:
    """临床史声明独立采样（先于事件生成，#113 Q2-3 正向：声明独立于事件）。
    MVP 测试参数（非正典定案）: 原子基准概率 [P(1), P(0), P(MISSING)]"""
    atom_base = {
        "DEPRESSIVE_EPISODE_HISTORY": (0.30, 0.55, 0.15),
        "SUBSTANCE_USE_HISTORY":      (0.15, 0.75, 0.10),
        "MANIA_HISTORY":              (0.10, 0.80, 0.10),
        "HYPOMANIA_HISTORY":          (0.12, 0.78, 0.10),
        "CYCLIC_MOOD_HISTORY":        (0.12, 0.78, 0.10),
    }
    ch = {}
    for atom in ATOMS:
        p1, p0, pm = atom_base[atom]
        r = rng.random()
        if r < p1: v = 1
        elif r < p1 + p0: v = 0
        else: v = "MISSING"
        ch[atom] = v
    return ch

def event_generator(soil: Soil, clinical_history: dict, rng: random.Random) -> LifeEvents:
    """按人生阶段生成 3-6 条创伤记忆。事件类型随机采样 + 声明×事件一致性约束。
    简化假设（MVP 测试用，非正典定案）。"""
    memories = []
    all_types = list(EVENT_TYPE_CANDIDATES.keys())
    # 声明一致性: 需要诱发的声明
    need_trigger = []
    if clinical_history.get("MANIA_HISTORY") == 1 or clinical_history.get("HYPOMANIA_HISTORY") == 1:
        need_trigger = MANIA_TRIGGER_TYPES  # 躁狂/轻躁狂史 → 需丧失/慢性诱发
    # 声明DEPRESSIVE=1 无需强制（MDD 候选面广，5 类事件均含 MDD）
    # 声明SUBSTANCE=1 需诱发? SUD 候选来自经济/慢性 → 不强制的 case 观察
    n_mem = rng.randint(3, 6)
    chosen_types = []
    for i in range(n_mem):
        etype = rng.choice(all_types)
        chosen_types.append(etype)
        a_lo, a_hi = EVENT_A_RANGE[etype]
        A = round(rng.uniform(a_lo, a_hi), 2)
        N = round(rng.uniform(0.1, 0.95), 2)
        F = round(rng.uniform(0.1, 0.95), 2)
        D_seg = round(0.95 if rng.random() < 0.05 else rng.uniform(0.0, 0.15), 2)
        g = round(rng.uniform(0.5, 0.9), 2)
        k = round(rng.uniform(0.7, 1.0), 2)
        delta_I = round(k * A, 2)
        stage_name = ["少年期", "青年期", "中年期"][i % 3]
        memories.append(TraumaMemory(
            event_type=etype, A=A, N=N, F=F, D_seg=D_seg, g=g, k=k, delta_I=delta_I,
            t_anchor=f"{stage_name}(第{i+1}条)",
            trace=[f"Event{i+1}: type={etype} A={A} (range {a_lo}-{a_hi})",
                   f"Event{i+1}: N={N} F={F} D_seg={D_seg} g={g} k={k} ΔI={delta_I}"]))
    # 一致性保证: 若需诱发且未含诱发类型 → 追加一条诱发事件
    if need_trigger and not any(t in need_trigger for t in chosen_types):
        etype = rng.choice(need_trigger)
        a_lo, a_hi = EVENT_A_RANGE[etype]
        A = round(rng.uniform(a_lo, a_hi), 2)
        N = round(rng.uniform(0.1, 0.95), 2)
        F = round(rng.uniform(0.1, 0.95), 2)
        D_seg = round(0.95 if rng.random() < 0.05 else rng.uniform(0.0, 0.15), 2)
        g = round(rng.uniform(0.5, 0.9), 2)
        k = round(rng.uniform(0.7, 1.0), 2)
        delta_I = round(k * A, 2)
        memories.append(TraumaMemory(
            event_type=etype, A=A, N=N, F=F, D_seg=D_seg, g=g, k=k, delta_I=delta_I,
            t_anchor=f"诱发补录(声明×事件一致性)",
            trace=[f"Event+诱发: type={etype} A={A} (声明 MANIA/HYPOMANIA=1 需诱发)",
                   f"Event+诱发: ΔI={delta_I}"]))
    return LifeEvents(memories=memories, trace=[f"Events: {len(memories)} 条记忆 (含一致性约束)"])
# ============================================================
# 阶段 4: Transformer —— 病理化 + 候选召回 + 资格门 + 聚合档位
# ============================================================
@dataclass
class EligibilityResult:
    disease: str
    status: str  # ELIGIBLE / INELIGIBLE / UNDETERMINED
    reason: str
    clinical_history: dict

@dataclass
class Transformation:
    pathological: bool
    L_total: float
    I_max: float
    candidates: list          # 召回的全部候选
    eligibility: list         # EligibilityResult 列表
    eligible: list            # ELIGIBLE 疾病列表
    disease_profile: dict     # 主病/档位
    clinical_history: dict    # 原子声明（MVP 由生成器采样产出）
    trace: list = field(default_factory=list)

def transformer(memories: list, clinical_history: dict, rng: random.Random) -> Transformation:
    """病理化(§3.1) → 候选召回(§3.2.1) → 资格门(§3.2.2, 消费传入的 clinical_history) → 聚合(§3.3)。"""
    trace = []
    # --- 1. 病理化: L = ΣΔI×g, I_max; 阈值 A_trauma_L=1.0, A_trauma_I=0.7 (β=1.0 简化)
    # ΔI = k×A（#88 输入约定）；L = Σ ΔI×g = Σ k×A×g（剂量-反应，§二）
    L_total = round(sum(m.delta_I * m.g for m in memories), 3)
    I_max = max(m.delta_I for m in memories)
    pathological = L_total >= 1.0 or I_max >= 0.7
    trace.append(f"病理化: L={L_total} (≥1.0? {L_total>=1.0}) I_max={I_max} (≥0.7? {I_max>=0.7}) → {'病理化' if pathological else 's=∅'}")

    # --- 2. 候选召回: 每条记忆事件类型 → 候选集
    candidates = []
    for m in memories:
        for d in EVENT_TYPE_CANDIDATES[m.event_type]:
            if d not in candidates:
                candidates.append(d)
    trace.append(f"候选召回: {candidates}")

    # --- 3. 资格门: 消费传入的 clinical_history（#113 Q2-3: 声明独立于事件, 由生成器产出）
    trace.append(f"临床史声明: {clinical_history}")

    # 资格判定
    eligibility = []
    for d in candidates:
        if d not in VERIFIED_DISEASES:
            # 未核验疾病: 资格规则未定义 → UNDETERMINED
            eligibility.append(EligibilityResult(d, "UNDETERMINED", f"{d} 资格原子未核验(#113延迟)", clinical_history))
            continue
        nec = DISEASE_NECESSARY_ATOMS.get(d, [])
        exc = DISEASE_EXCLUDE_ATOMS.get(d, [])
        # 组合规则（§3.2.2）: ∃P_i=0 → INELIGIBLE; ∃N_j=1 → INELIGIBLE; ∃MISSING → UNDETERMINED; 全过 → ELIGIBLE
        status, reason = "ELIGIBLE", ""
        for p in nec:
            v = clinical_history.get(p, "MISSING")
            if v == 0:
                status, reason = "INELIGIBLE", f"必要原子 {p}=0 一票否决"
                break
            if v == "MISSING":
                status, reason = "UNDETERMINED", f"必要原子 {p}=MISSING"
                break
        if status == "ELIGIBLE":
            for n in exc:
                v = clinical_history.get(n, "MISSING")
                if v == 1:
                    status, reason = "INELIGIBLE", f"排除原子 {n}=1 一票否决"
                    break
                if v == "MISSING":
                    status, reason = "UNDETERMINED", f"排除原子 {n}=MISSING"
                    break
        if status == "ELIGIBLE" and not reason:
            reason = "全部必要原子=1 且排除原子=0"
        eligibility.append(EligibilityResult(d, status, reason, clinical_history))

    eligible = [e for e in eligibility if e.status == "ELIGIBLE"]
    trace.append(f"资格裁决: {[(e.disease, e.status, e.reason) for e in eligibility]}")

    # --- 4. 主病选择 + 聚合（仅 ELIGIBLE）
    disease_profile = {"主病": None, "档位": "∅", "备注": ""}
    if not pathological:
        disease_profile["备注"] = "病理化未达标 → s=∅（健康/亚临床）"
    elif not eligible:
        disease_profile["备注"] = f"病理化达标但无 ELIGIBLE 候选（有 {len([e for e in eligibility if e.status=='UNDETERMINED'])} 个 UNDETERMINED）"
    else:
        # MVP 主病选择: 简化为 ELIGIBLE 中 L_agg 最高（完整 N/F/R sim 留后续）
        best = None
        for e in eligible:
            # L_agg = 指向该病的记忆 ΔI×g 之和（MVP 简化用全部记忆）
            L_agg = L_total
            if best is None or L_agg > best[1]:
                best = (e.disease, L_agg)
        # 档位（§3.3）
        L = best[1]
        if L < 1.0: level = "∅"
        elif L < 2.0: level = "轻"
        elif L < 3.5: level = "中"
        else: level = "重"
        disease_profile = {"主病": best[0], "档位": level, "L_agg": L, "备注": "MVP 主病=ELIGIBLE中L_agg最高(完整N/F/R sim后续)"}
        trace.append(f"主病: {best[0]} 档位: {level} (L_agg={L})")

    return Transformation(pathological, L_total, I_max, candidates, eligibility, eligible,
                          disease_profile, clinical_history, trace)

# ============================================================
# 阶段 5: ArtifactDeriver —— gen.json 输出
# ============================================================
def derive_artifact(soil, life_events, trans, rng) -> dict:
    """产出 gen.json + 完整 trace（可追溯）。"""
    # 取姓名池（MVP 简单生成，不追求文学）
    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡"]
    given_m = ["建国", "志强", "伟", "军", "明", "涛", "磊", "强", "平", "辉"]
    given_f = ["秀英", "桂芳", "小梅", "丽", "娟", "芳", "静", "萍", "霞", "燕"]
    gender = rng.choice(["男", "女"])
    name = rng.choice(surnames) + rng.choice(given_m if gender == "男" else given_f)
    admission_year = 2015 + rng.randint(0, 2)
    age = admission_year - soil.birth_year

    artifact = {
        "_metadata": {
            "role": name, "draft": "mvp-generated", "status": "生成器自动产出(测试)",
            "source": "sim_npc_generator_mvp.py (R=固定seed)",
            "input_source": "canonical",
            "gen_schema": "MVP 最小版",
        },
        "identity": {
            "name": name, "gender": gender, "birth_year": soil.birth_year,
            "birth_region": soil.region, "入院年龄": age, "入院年份": admission_year,
        },
        "soil": {"era": soil.era_label, "region": soil.region, "conditions": soil.social_conditions},
        "trauma_memories": [{
            "event_type": m.event_type, "A": m.A, "N": m.N, "F": m.F, "D_seg": m.D_seg,
            "delta_I": m.delta_I, "t_anchor": m.t_anchor,
        } for m in life_events.memories],
        "clinical_history": trans.clinical_history,
        "transformation": {
            "病理化": trans.pathological, "L_total": trans.L_total, "I_max": trans.I_max,
            "资格裁决": [{"disease": e.disease, "status": e.status, "reason": e.reason} for e in trans.eligibility],
            "disease_profile": trans.disease_profile,
        },
        "trace": soil.trace + life_events.trace + trans.trace,
    }
    return artifact

# ============================================================
# Q6 六轴统计（质量门禁——生成后诊断，不参与资格）
# ============================================================
def q6_axis(artifact: dict) -> dict:
    """六轴标注（MVP 从 artifact 提取简版）。"""
    dp = artifact["transformation"]["disease_profile"]
    has_disease = dp.get("主病") is not None
    # 轴3 叙事功能: MVP 无叙事 → 用疾病状态近似（真实需叙事层）
    # 轴1 入院方式: MVP 无入院叙事 → "未定义(MVP)"
    return {
        "轴3疾病状态": dp.get("主病", "无"), "档位": dp.get("档位", "∅"),
        "病理化": artifact["transformation"]["病理化"],
    }

# ============================================================
# 主流程: 单次生成 + 批量分布测试
# ============================================================
def generate_one(seed: int) -> dict:
    rng = random.Random(seed)
    soil = soil_sampler(rng)
    clinical_history = sample_clinical_history(rng)  # 声明先于事件 (#113 Q2-3 正向)
    events = event_generator(soil, clinical_history, rng)  # 事件服从声明一致性
    trans = transformer(events.memories, clinical_history, rng)
    art = derive_artifact(soil, events, trans, rng)
    art["_metadata"]["seed"] = seed
    return art

def run_batch(n=100, base_seed=42):
    """固定 seed 批量生成 → 分布统计。"""
    stats = {
        "疾病分布": {}, "资格状态": {"ELIGIBLE": 0, "INELIGIBLE": 0, "UNDETERMINED": 0, "无候选/未病理化": 0},
        "档位分布": {}, "病理化率": 0, "平均记忆数": 0, "UNDETERMINED_疾病": {},
    }
    artifacts = []
    for i in range(n):
        art = generate_one(base_seed + i)
        artifacts.append(art)
        t = art["transformation"]
        stats["平均记忆数"] += len(art["trauma_memories"])
        if t["病理化"]:
            stats["病理化率"] += 1
        dp = t["disease_profile"]
        if dp.get("主病"):
            stats["疾病分布"][dp["主病"]] = stats["疾病分布"].get(dp["主病"], 0) + 1
            stats["档位分布"][dp.get("档位")] = stats["档位分布"].get(dp.get("档位"), 0) + 1
        else:
            stats["疾病分布"]["无(未病理化/无资格)"] = stats["疾病分布"].get("无(未病理化/无资格)", 0) + 1
        # 资格状态
        eligibles = [e for e in t["资格裁决"] if e["status"] == "ELIGIBLE"]
        inelig = [e for e in t["资格裁决"] if e["status"] == "INELIGIBLE"]
        undet = [e for e in t["资格裁决"] if e["status"] == "UNDETERMINED"]
        if not t["资格裁决"]:
            stats["资格状态"]["无候选/未病理化"] += 1
        else:
            if eligibles: stats["资格状态"]["ELIGIBLE"] += 1
            if inelig: stats["资格状态"]["INELIGIBLE"] += 1
            if undet:
                stats["资格状态"]["UNDETERMINED"] += 1
                for e in undet:
                    stats["UNDETERMINED_疾病"][e["disease"]] = stats["UNDETERMINED_疾病"].get(e["disease"], 0) + 1
    stats["平均记忆数"] = round(stats["平均记忆数"] / n, 1)
    stats["病理化率"] = round(stats["病理化率"] / n, 3)
    return stats, artifacts

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    print(f"=== #87 A′-Generator MVP 批量测试 R={n} base_seed={seed} ===")
    stats, arts = run_batch(n, seed)
    print(f"\n病理化率: {stats['病理化率']:.0%}  平均记忆数: {stats['平均记忆数']}")
    print(f"\n=== 疾病分布 (主病) ===")
    for d, c in sorted(stats["疾病分布"].items(), key=lambda x: -x[1]):
        print(f"  {d:<24} {c:>4}  {c/n:.0%}")
    print(f"\n=== 档位分布 ===")
    for d, c in sorted(stats["档位分布"].items(), key=lambda x: -x[1]):
        print(f"  {str(d):<6} {c:>4}  {c/n:.0%}")
    print(f"\n=== 资格状态 (每患者至少一次) ===")
    for s, c in stats["资格状态"].items():
        print(f"  {s:<20} {c:>4}  {c/n:.0%}")
    print(f"\n=== UNDETERMINED 疾病频次 (未核验资格) ===")
    for d, c in sorted(stats["UNDETERMINED_疾病"].items(), key=lambda x: -x[1]):
        print(f"  {d:<20} {c:>4}")
    # 样例输出
    print("\n=== 样例患者 (seed 42) ===")
    sample = generate_one(seed)
    print(json.dumps(sample["identity"], ensure_ascii=False))
    print("临床史:", sample["clinical_history"])
    print("资格裁决:", [(e["disease"], e["status"], e["reason"][:30]) for e in sample["transformation"]["资格裁决"]])
    print("疾病档案:", sample["transformation"]["disease_profile"])
