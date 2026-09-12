"""
sim_consciousness_v7_rb_test.py — R-B 内部因果穿透判别三角（模拟实现批次 脚本 2/3）
=============================================================================================
研讨论文产物（纯学术，不入游戏正典）。Grilling #94（issue #94）D1-D7 定案落地。

验证 v7 §六（来源：reference/意识结构侧-下一阶段路线-v7.md）：
  SM′ = SelfRep ∧ SelfUse ∧ AgencyUse = RB_I ∧ RB_A（D3/D5/D6 冻结的判定器）
  RB_I（SelfRep，R-B 内部因果穿透）= ∃m≠m′, k∈I: P_F(X′_k|do(M=m)) ≠ P_F(X′_k|do(M=m′))
  RB_A（SelfUse∧AgencyUse 合一）= 同上 k∈A，Δ_A(M)>0 结构性条件（边际 do 检验）

判别三角（v7 §六最小判别集——L2 理论的核心承诺，Grilling #94 D7）：
  F1  计数控制器（死端投影） : Y∖M→M ✓ | M→I ✗ | M→A ✗ | SM′=0
  F9  伪自模型（状态估计器） : Y∖M→M ✓ | M→I ✗ | M→A ✓ | SM′=0
  F8′ 表征+因果使用          : Y∖M→M ✓ | M→I ✓ | M→A ✓ | SM′=1

断言（实测不符 → 触发 Step 6 闭合后修正）：
  SM_local(F1)=0 ∧ SM_local(F9)=0 ∧ SM_local(F8′)=1

原语全部复用脚本 1（不重复定义）；F1/F9 step 为 cs4 的 bernoulli 语义等价改写
（来源：sim_consciousness_cs4_test.py make_f1 :215-224 / make_f9 :252-269）。
Y∖M→M 表征形成为诊断列（E_S^(1) 边 (i∈A∪I)→(j∈M) 检验），不进 SM′。
"""

from sim_consciousness_v7_components import (
    System, evaluate, exact_kernel, sm_local, edges_e1, THETA_D, EPS,
    make_f8p_step,
)

# ============================================================
# §1 F1 / F9 系统定义（bernoulli 语义等价改写，来源 cs4）
# ============================================================

def make_f1_step():
    """F1 计数控制器（cs4 make_f1 :215-224 的 bernoulli 等价改写）。

    state=(c0,c1,c2,j1,j2,fb)，n=6；M={j1,j2}={3,4}，A=Y={c0,c1,c2}={0,1,2}，
    I={fb}={5}（Grilling #94 D7）。
    判别三角预期：Y∖M→M ✓（j1/j2 读出 c）、M→A ✗（c′=(c+1+fb)%8 不依赖 M）、
    M→I ✗（fb′=randint 不依赖 M）→ SM′=0。
    """
    def step(state, rng):
        c0, c1, c2, j1, j2, fb = state
        c = c0 + 2 * c1 + 4 * c2
        nc = (c + 1 + fb) % 8
        nj1 = ((c >> 0) & 1) if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        nj2 = ((c >> 1) & 1) if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        nfb = rng.bernoulli(0.5)
        return ((nc >> 0) & 1, (nc >> 1) & 1, (nc >> 2) & 1, nj1, nj2, nfb)
    return step


def make_f9_step():
    """F9 伪自模型（cs4 make_f9 :252-269 的 bernoulli 等价改写）。

    state=(s,m1,m2,a1,a2)，n=5；M={m1,m2}={1,2}，A={a1,a2}={3,4}，I={s}={0}
    （Grilling #94 D7；sensor 入 I）。
    判别三角预期：Y∖M→M ✓（m1′=s 0.85）、M→A ✓（a1′=m1 0.8）、
    M→I ✗（s′=randint 不依赖 M）→ SM′=0（状态估计+反馈控制的精确结构画像）。
    """
    def step(state, rng):
        s, m1, m2, a1, a2 = state
        ns = rng.bernoulli(0.5)
        nm1 = s if rng.bernoulli(0.85) else rng.bernoulli(0.5)
        nm2 = a1 if rng.bernoulli(0.85) else rng.bernoulli(0.5)
        na1 = m1 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        na2 = m2 if rng.bernoulli(0.8) else rng.bernoulli(0.5)
        return (ns, nm1, nm2, na1, na2)
    return step


def make_discrimination_systems():
    """判别三角三系统（F1/F9/F8′；M/A 分配见 D7）。"""
    return [
        System("F1 计数控制器", 6, make_f1_step(), [3, 4], [0, 1, 2]),
        System("F9 伪自模型", 5, make_f9_step(), [1, 2], [3, 4]),
        System("F8′ 表征+因果使用", 6, make_f8p_step(), [2, 3], [0, 1]),
    ]


def y_minus_m_to_m(E, n, M_set, A_set):
    """诊断列：Y∖M→M 表征形成 = ∃(i,j)∈E_S^(1): i∈A∪I, j∈M（E 边检验）。"""
    M = set(M_set)
    YminusM = set(range(n)) - M
    return any((i, j) in E for i in YminusM for j in M)


# ============================================================
# §2 判别三角实测
# ============================================================

def main():
    print("=" * 78)
    print("脚本 2/3：R-B 内部因果穿透判别三角（Grilling #94 D1-D7）")
    print("SM′ = RB_I ∧ RB_A（边际 do 检验，判定器冻结自脚本 1）")
    print("断言：SM_local(F1)=0 ∧ SM_local(F9)=0 ∧ SM_local(F8′)=1")
    print("=" * 78)

    rows = []
    for sys in make_discrimination_systems():
        r = evaluate(sys)
        # 判别三角列
        n = sys.n
        M_set, A_set = list(sys.M_set), list(sys.A_set)
        E = r["E"]
        ym_to_m = y_minus_m_to_m(E, n, M_set, A_set)
        I_set = set(range(n)) - set(M_set) - set(A_set)
        sm_local_val = any(c["SM_local"] for c in r["components"])
        cs_val = r["CS′"]
        # 逐个分量拿 RB_I/RB_A（从 SM_detail 解析，如 "RB_I=True, RB_A=True"）
        rb_parts = []
        for c in r["components"]:
            rb_parts.append((c["C"], c["SM_local"], c["SM_detail"]))
        rows.append((sys.name, ym_to_m, rb_parts, sm_local_val, cs_val))

        print(f"\n--- {sys.name} (n={n}, M={sorted(M_set)}, A={sorted(A_set)}, I={sorted(I_set)}) ---")
        print(f"  E_S^(1) = {len(E)} 条边；𝒞 = {r['comps']}；closure={r['closure_ok']} factor={r['factor_ok']}")
        for c in r["components"]:
            print(f"  C={c['C']}: Diff={c['Diff']:.3f}bit  Int={c['Int_local']:.4f}  "
                  f"SB={c['SB_local']}  SM={c['SM_local']}  [{c['SM_detail']}]  "
                  f"CS′_local={'✅1' if c['CS′_local'] else '❌0'}")
        print(f"  诊断列 Y∖M→M = {'✓' if ym_to_m else '✗'}；"
              f"SM′ = {'✅ 1' if sm_local_val else '❌ 0'}；CS′ = {'✅ 1' if cs_val else '❌ 0'}")

    print("\n" + "=" * 78)
    print("判别三角（v7 §六）：")
    print(f"  {'系统':24s} {'Y∖M→M':7s} {'M→I':7s} {'M→A':7s} {'SM′':5s} {'CS′':5s}")
    expected = {"F1 计数控制器": 0, "F9 伪自模型": 0, "F8′ 表征+因果使用": 1}
    ok = True
    for name, ym_to_m, rb_parts, sm_val, cs_val in rows:
        rb_i = any("RB_I=True" in d for _, _, d in rb_parts)
        rb_a = any("RB_A=True" in d for _, _, d in rb_parts)
        exp = expected[name]
        match = (sm_val == bool(exp))
        ok = ok and match
        print(f"  {name:24s} {'✓' if ym_to_m else '✗':7s} "
              f"{'✓' if rb_i else '✗':7s} {'✓' if rb_a else '✗':7s} "
              f"{'1' if sm_val else '0':5s} {'1' if cs_val else '0':5s}  "
              f"{'✅' if match else '❌ 断言不符'}")
    print("=" * 78)
    print(f"判别三角断言（F1=0 / F9=0 / F8′=1）: {'✅ 全部通过' if ok else '❌ 失败 → 触发 Step 6 闭合后修正'}")
    print("=" * 78)


if __name__ == "__main__":
    main()
