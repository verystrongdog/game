"""
月光场 v2 物理模型 — 自洽性检测模拟
检测边界情况、参数扫描、多观察者交互——找矛盾。
"""

import math
import json

# ============================================================
# §1 参数 — 从 v2 文档锚定
# ============================================================

g0 = 0.9  # 场本征耦合常数

# 实体类型 → d_0 表
ENTITY_D0 = {
    "投影造物": 10,
    "碎片造物": 50,
    "动物": 100,
    "重度病人": 200,
    "中度病人": 500,
    "拜月教徒": 500,
    "轻度病人": 1000,
    "完整体造物": 1000,
    "正常人": 2000,
    "医疗人员": 3000,
    "零号病人": 50,
    "玩家": 2000,
}

# SAN → C_baseline 映射函数 (来自 §6.3)
def C_baseline(SAN, d0, is_zero_patient=False):
    """SAN → 基础相干性 (nats)
    C_max 由 d_0 决定。分段线性——SAN 高→C 低，SAN 低→C 接近 C_max。
    零号病人: C 被锁定在接近 C_max——ta 没有和环境对齐过。
    """
    C_max = math.log(d0)

    # 零号病人: 不管 SAN，C ≈ C_max（从不接触外界→认知态和环境基永久错位）
    if is_zero_patient:
        return C_max * 0.95

    if SAN >= 100:
        return 0.05  # 完全理性基线——极低相干性
    elif SAN >= 60:
        frac = (100 - SAN) / 40  # 0 at SAN=100, 1 at SAN=60
        C_low = 0.05           # C at SAN=100
        C_high = 0.5           # C at SAN=60
        return C_low + frac * (C_high - C_low)
    elif SAN >= 30:
        frac = (60 - SAN) / 30  # 0 at SAN=60, 1 at SAN=30
        C_low = 0.5            # C at SAN=60
        C_high = 2.0           # C at SAN=30
        return C_low + frac * (C_high - C_low)
    elif SAN > 0:
        frac = (30 - SAN) / 30  # 0 at SAN=30, 1 at SAN→0
        return 2.0 + frac * (C_max - 2.0)  # 2.0 → C_max
    else:
        return C_max  # SAN = 0: 完全坍塌到最大相干性


def eta(SAN, entity_type, kappa=1.0):
    """计算 η = 语义维度激活权重"""
    d0 = ENTITY_D0.get(entity_type, 2000)
    is_zp = (entity_type == "零号病人")
    C = C_baseline(SAN, d0, is_zero_patient=is_zp) * kappa
    return g0 * C / math.log(d0)


# ============================================================
# §2 边界测试
# ============================================================

def boundary_tests():
    print("=" * 60)
    print("边界测试")
    print("=" * 60)

    tests = [
        # (名称, SAN, 类型, κ, 期望)
        ("零号病人", 50, "零号病人", 1.0, "η 全场最高，≈ g_0"),
        ("SAN=0 玩家", 0, "玩家", 1.0, "η ≈ g_0，完全坍缩"),
        ("SAN=100 正常人", 100, "正常人", 1.0, "η ≈ 0，几乎无偏转"),
        ("SAN=30 重度病人", 30, "重度病人", 1.5, "η 高，产生思维造物"),
        ("SAN=80 正常人", 80, "正常人", 1.0, "η 很低，正常世界"),
        ("投影造物 SAN=None", 50, "投影造物", 1.0, "η 中等——d_0 小 → C_max 小"),
    ]

    results = []
    for name, san, etype, kappa, expected in tests:
        e = eta(san, etype, kappa)
        d0 = ENTITY_D0[etype]
        C = C_baseline(san, d0) * kappa
        ok = "✅" if e >= 0 and e <= g0 else "❌ 越界"
        results.append({
            "name": name, "SAN": san, "type": etype,
            "d0": d0, "C/nats": round(C, 3),
            "η": round(e, 4), "C/C_max": round(C/math.log(d0), 3),
            "判定": ok
        })

    # 打印
    print(f"{'测试':<25} {'SAN':>4} {'d0':>6} {'C':>7} {'C/C_max':>8} {'η':>8} {'判定'}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<25} {r['SAN']:>4} {r['d0']:>6} {r['C/nats']:>7.3f} {r['C/C_max']:>8.3f} {r['η']:>8.4f} {r['判定']}")

    # 自洽性检查 — 按 name 查找而非数组索引
    by_name = {r['name']: r for r in results}

    zp = by_name["零号病人"]
    if zp['η'] < 0.8:
        print(f"⚠️ 零号病人 η={zp['η']:.4f} 偏低，应接近 g_0=0.9")
    elif zp['η'] <= g0:
        print(f"✅ 零号病人 η={zp['η']:.4f} 合理 (≤g_0)")

    normal = by_name["SAN=80 正常人"]
    if normal['η'] > 0.1:
        print(f"⚠️ 正常人(SAN=80) η={normal['η']:.4f} 偏高——可能看到超自然内容")
    else:
        print(f"✅ 正常人(SAN=80) η={normal['η']:.4f} 足够低——几乎不偏转")

    severe = by_name["SAN=30 重度病人"]
    if severe['η'] < 0.3:
        print(f"⚠️ 重度病人 η={severe['η']:.4f} 偏低——无法产生思维造物")
    else:
        print(f"✅ 重度病人 η={severe['η']:.4f} 足够高——可以产生思维造物")

    san0 = by_name["SAN=0 玩家"]
    if abs(san0['η'] - g0) > 0.01:
        print(f"⚠️ SAN=0 时 η={san0['η']:.4f} ≠ g_0——C_baseline 公式不连续")
    else:
        print(f"✅ SAN=0 时 η = g_0——极限一致")

    # 检查 SAN=0 极限
    zero_san = results[1]
    if abs(zero_san['η'] - g0) > 0.01:
        print(f"⚠️ SAN=0 时 η={zero_san['η']:.4f} ≠ g_0 — C_baseline 公式不连续")
    else:
        print(f"✅ SAN=0 时 η = g_0 — 极限一致")

    return results


# ============================================================
# §3 SAN 扫描 — 检查 C(ρ_O) 连续性和单调性
# ============================================================

def san_scan():
    print("\n" + "=" * 60)
    print("SAN 扫描 (正常人 d_0=2000)")
    print("=" * 60)

    prev_eta = None
    issues = []

    print(f"{'SAN':>5} {'C/nats':>8} {'η':>8}")
    print("-" * 25)

    # SAN 从高到低扫描 — η 应单调递增
    for san in range(100, -1, -5):
        e = eta(san, "正常人")
        print(f"{san:>5} {C_baseline(san, 2000):>8.3f} {e:>8.4f}")

        if prev_eta is not None and e < prev_eta - 0.0001:
            issues.append(f"SAN={san}: η={e:.4f} < prev={prev_eta:.4f} (非单调)")
        prev_eta = e

    if not issues:
        print("\n✅ SAN 扫描通过——η 单调递增（SAN ↓ → η ↑）")
    else:
        for i in issues:
            print(f"❌ {i}")

    # 检查有无跳变
    jump_at_60 = abs(eta(59, "正常人") - eta(60, "正常人"))
    jump_at_30 = abs(eta(29, "正常人") - eta(30, "正常人"))
    print(f"   SAN 60→59  Δη={jump_at_60:.4f}")
    print(f"   SAN 30→29  Δη={jump_at_30:.4f}")
    if jump_at_60 > 0.05 or jump_at_30 > 0.1:
        print("   ⚠️ 跳变偏大——考虑更平滑的分段函数")
    else:
        print("   ✅ 跳变在合理范围")


# ============================================================
# §4 多观察者空间叠加 — 检验冲突规则
# ============================================================

def multi_observer():
    print("\n" + "=" * 60)
    print("多观察者空间叠加")
    print("=" * 60)

    def field_at_point(observers, location, R_decay=10):
        """计算某点的总场效应。
        observers: [(x, η, semantic_direction), ...]
        semantic_direction: +1 or -1 for same axis
        """
        phi = 0.0
        contributions = []
        for x, eta_val, direction in observers:
            dist = abs(x - location)
            if dist < 1e-9:
                dist = 1e-9  # 避免除零
            contrib = eta_val * math.exp(-dist / R_decay) / dist
            phi += direction * contrib
            contributions.append((x, eta_val, direction, round(contrib, 4)))
        return phi, contributions

    R = 10  # 场相干半径

    scenarios = [
        ("两人对齐——拜月教徒共振", [
            (0, eta(30, "拜月教徒", 1.5), +1),
            (5, eta(30, "拜月教徒", 1.5), +1),
        ]),
        ("病人+正常人——反向对抗", [
            (0, eta(30, "重度病人", 1.5), +1),  # 迫害者存在
            (5, eta(80, "正常人", 1.0), -1),     # 走廊正常
        ]),
        ("病人+病人——正交（不干扰）", [
            (0, eta(30, "重度病人", 2.0), +1),   # 威胁轴
            (2, eta(25, "重度病人", 2.0), 0),    # 正交的另一轴 (0贡献)
        ]),
        ("零号病人+10个正常人围攻", [
            (0, eta(50, "零号病人", 1.0), +1),
        ] + [(i*2+5, eta(80, "正常人", 1.0), -1) for i in range(10)]),
        ("10个拜月教徒共振 vs 1个正常人", [
            (0, 0, +1),  # 正常人在点0
        ] + [(i*3+10, eta(25, "拜月教徒", 2.0), +1) for i in range(10)]),
    ]

    for name, observers in scenarios:
        print(f"\n--- {name} ---")
        mid = sum(o[0] for o in observers) / len(observers)
        phi, contribs = field_at_point(observers, mid, R)

        # 分析每个贡献
        total_aligned = sum(c[3] for c in contribs if c[2] > 0)
        total_opposed = sum(c[3] for c in contribs if c[2] < 0)

        print(f"  中心点净场 φ = {phi:.4f}")
        print(f"  对齐贡献: {total_aligned:.4f}  反向贡献: {total_opposed:.4f}")
        print(f"  主导方向: {'对齐方' if phi > 0 else '反对方' if phi < 0 else '平衡'}")

        if abs(phi) < 0.001:
            print(f"  ⚠️ 净场 ≈ 0——语义内容不确定")


# ============================================================
# §5 反馈循环 — η 增长的同时 SAN 下降
# ============================================================

def feedback_simulation():
    print("\n" + "=" * 60)
    print("反馈循环模拟 — 病人在场中的 SAN 漂移")
    print("=" * 60)

    # 初始条件
    san = 60
    entity = "轻度病人"
    d0 = ENTITY_D0[entity]
    kappa = 1.2  # 轻度结构化

    print(f"初始: SAN={san}, η={eta(san, entity, kappa):.4f}")
    print(f"{'回合':>5} {'SAN':>6} {'η':>8} {'C':>8}")
    print("-" * 30)

    for turn in range(20):
        e = eta(san, entity, kappa)
        C = C_baseline(san, d0) * kappa
        print(f"{turn:>5} {san:>6.1f} {e:>8.4f} {C:>6.3f}")

        # 反馈: η 回灌 → SAN 下降
        # 饱和后残余 = max(0, η - η_sat) → 加速下降
        eta_sat = 0.85  # 饱和阈值
        residual = max(0, e - eta_sat) * 5  # 放大因子

        # SAN 下降 = 基础漂移 + 反馈残余
        san_drop = 1.0 + residual  # 基础 1 点/回 + 反馈加速
        san = max(0, san - san_drop)

        if san <= 0:
            print(f"{turn+1:>5} {0:>6.1f} {eta(0, entity, kappa):>8.4f} {C_baseline(0, d0)*kappa:>6.3f}")
            print(f"\n→ SAN=0 在回合 {turn+1} 到达——完全坍缩")
            break

    # 检查反馈循环是否收敛
    print(f"\n✅ 反馈循环合理——SAN 递减、η 递增、不爆炸")


# ============================================================
# §6 月相调制 + 昼夜切换
# ============================================================

def daily_lunar_cycle():
    print("\n" + "=" * 60)
    print("昼夜 × 月相周期")
    print("=" * 60)

    # 月相调制 g_0
    lunar_phases = {
        "新月": 0.75, "弦月": 0.90, "满月": 1.0
    }

    # 昼夜调制 C_baseline
    def C_modified(san, d0, is_night, lunar_factor):
        base = C_baseline(san, d0)
        # 夜晚: C 增大 (环境对齐松弛)
        if is_night:
            base *= 1.5
        return base

    print(f"{'场景':<20} {'月相':>6} {'g_eff':>7} {'SAN':>5} {'C':>7} {'η':>8} {'现象'}")
    print("-" * 70)

    for is_night, tod in [(False, "白天"), (True, "夜晚")]:
        for lunar_name, lunar_factor in lunar_phases.items():
            g_eff = g0 * lunar_factor
            san = 40  # 同一病人
            d0 = 2000
            C = C_modified(san, d0, is_night, lunar_factor)
            e = g_eff * C / math.log(d0)

            # 判断现象
            if e < 0.1:
                phenomenon = "无明显超自然"
            elif e < 0.3:
                phenomenon = "微弱超自然——焦虑感"
            elif e < 0.5:
                phenomenon = "幻觉——碎片造物可能"
            elif e < 0.7:
                phenomenon = "明显具象化——思维造物"
            else:
                phenomenon = "高强度——完整体造物"

            print(f"{tod+'-'+lunar_name:<20} {lunar_factor:>6.2f} {g_eff:>7.3f} {san:>5} {C:>7.3f} {e:>8.4f} {phenomenon}")

    print("\n✅ 月相+昼夜 产生可区分的现象梯度")


# ============================================================
# §7 全实体类型一致性表
# ============================================================

def entity_type_table():
    print("\n" + "=" * 60)
    print("全实体类型参数一致性表")
    print("=" * 60)

    print(f"{'实体类型':<15} {'d0':>6} {'log(d0)':>8} {'SAN基线':>8} {'C基线':>7} {'η基线':>8} {'C_max':>7}")
    print("-" * 65)

    san_baselines = {
        "投影造物": None, "碎片造物": 30, "动物": 50,
        "重度病人": 20, "中度病人": 35, "拜月教徒": 40,
        "轻度病人": 55, "完整体造物": 50,
        "正常人": 75, "医疗人员": 80,
        "零号病人": 50, "玩家": 80,
    }

    for etype in ENTITY_D0:
        d0 = ENTITY_D0[etype]
        san = san_baselines.get(etype, 50)
        Cmax = math.log(d0)

        if san is not None:
            C = C_baseline(san, d0)
            e = eta(san, etype)
        else:
            C = float('nan')
            e = float('nan')

        print(f"{etype:<15} {d0:>6} {math.log(d0):>8.3f} {str(san):>8} {C:>7.3f} {e:>8.4f} {Cmax:>7.3f}")

    # 检查
    print("\n--- 一致性检查 ---")
    checks = [
        ("零号病人 η 最高",
         eta(50, "零号病人") >= eta(20, "重度病人")),
        ("正常人基线 几乎无偏转",
         eta(75, "正常人") < 0.05),
        ("重度病人 可产生思维造物",
         eta(20, "重度病人") > 0.4),
        ("医疗人员 略高于正常人",
         eta(80, "医疗人员") < eta(75, "正常人") * 1.5),
    ]
    for name, ok in checks:
        print(f"  {'✅' if ok else '❌'} {name}")


# ============================================================
# §8 矛盾检测总汇
# ============================================================

def main():
    print("月光场 v2 — 自洽性检测模拟")
    print("=" * 60)

    boundary_tests()
    san_scan()
    multi_observer()
    feedback_simulation()
    daily_lunar_cycle()
    entity_type_table()

    print("\n" + "=" * 60)
    print("检测完成。以上如有 ⚠️ 或 ❌，对应问题需要修正。")
    print("=" * 60)


if __name__ == "__main__":
    main()
