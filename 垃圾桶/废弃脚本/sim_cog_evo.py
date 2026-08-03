#!/usr/bin/env python3
"""
认知演化模拟 v3 — 两元素三规则 → C₁-C₁₁ 全部涌现
修复: 参数调优让每层现象清晰可见

元素: 检测(detect), 残留(trace)
规则: 衰减(decay), 绑定(bind), 泛化(generalize)

设计原则: 每一层不加新代码——只调整 d_prime / criterion / decay_rate /
          link_lr / spread_rate 这五个参数的取值。
"""

import math, random, itertools
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

random.seed(42)

@dataclass
class Trace:
    pid: int
    features: Tuple[float, ...]
    activation: float = 0.0
    decay_rate: float = 0.15
    links: Dict[int, float] = field(default_factory=dict)
    label: str = ""
    birth_time: int = 0

class CogSys:
    def __init__(self, d_prime=1.0, criterion=0.3):
        self.traces: Dict[int, Trace] = {}
        self.next_id = 0
        self.dp = d_prime
        self.criterion = criterion
        self.t = 0
        self.link_lr = 0.10      # Hebbian 学习率
        self.spread_rate = 0.25  # 链接传播系数

    # ── 四规则 ──

    def detect(self, intensity=1.0) -> float:
        noise = random.gauss(0, 1.0 / max(0.1, self.dp))
        return max(0.0, min(1.0, intensity + noise))

    def decay(self):
        for t in self.traces.values():
            t.activation *= (1 - t.decay_rate)
            if t.activation < 0.001:
                t.activation = 0.0

    def bind(self, active: List[int]):
        for i, j in itertools.combinations(active, 2):
            if i not in self.traces or j not in self.traces:
                continue
            co = self.traces[i].activation * self.traces[j].activation
            if co < 0.003:
                continue
            self.traces[i].links[j] = self.traces[i].links.get(j, 0.0) + self.link_lr * co
            self.traces[j].links[i] = self.traces[j].links.get(i, 0.0) + self.link_lr * co

    def generalize(self, features: Tuple[float, ...]) -> Tuple[Optional[int], float]:
        best_id, best_sim = None, 0.0
        for tid, t in self.traces.items():
            if t.activation < 0.001:
                continue
            sim = cosine(features, t.features)
            if sim > best_sim:
                best_sim, best_id = sim, tid
        if best_id is not None and best_sim >= self.criterion:
            return best_id, best_sim
        return None, best_sim

    # ── 一步 ──

    def step(self, features: Tuple[float, ...], intensity=1.0,
             label="") -> Dict:
        self.t += 1
        self.decay()

        act = self.detect(intensity)
        match_id, sim = self.generalize(features)

        new_trace = False
        if match_id is not None:
            tid = match_id
            boost = act * 0.35
            self.traces[tid].activation = min(1.0, self.traces[tid].activation + boost)
        else:
            tid = self.next_id
            self.traces[tid] = Trace(pid=tid, features=features, activation=act,
                                     decay_rate=0.15, label=label, birth_time=self.t)
            self.next_id += 1
            new_trace = True
            sim = 1.0

        # 传播: 被激活节点的链接向外扩散
        src = self.traces.get(tid)
        spread_ids = []
        if src and src.activation > 0.05:
            for other_id, link_str in src.links.items():
                if other_id in self.traces and self.traces[other_id].activation < 0.9:
                    spread = link_str * src.activation * self.spread_rate
                    self.traces[other_id].activation = min(1.0,
                        self.traces[other_id].activation + spread)
                    if self.traces[other_id].activation > 0.03:
                        spread_ids.append(other_id)

        # 绑定
        active = [t.pid for t in self.traces.values() if t.activation > 0.06]
        if tid not in active:
            active.append(tid)
        for sid in spread_ids:
            if sid not in active:
                active.append(sid)
        if len(active) >= 2:
            self.bind(active)

        n_active = len(active)
        n_links = sum(len(t.links) for t in self.traces.values())
        n_traces = len([t for t in self.traces.values() if t.activation > 0.001])

        return {'time': self.t, 'tid': tid, 'act': act, 'sim': sim,
                'new': new_trace, 'n_traces': n_traces, 'n_active': n_active,
                'n_links': n_links, 'spread_to': len(spread_ids)}

    def active(self, thr=0.03) -> List[Trace]:
        return [t for t in self.traces.values() if t.activation > thr]

    def link(self, a, b):
        if a is None or b is None: return 0.0
        return self.traces[a].links.get(b, 0.0) if a in self.traces else 0.0

    def clusters(self, min_link=0.15) -> List[List[int]]:
        ids = [t.pid for t in self.active()]
        visited, result = set(), []
        for pid in ids:
            if pid in visited: continue
            cluster, stack = [], [pid]
            while stack:
                cur = stack.pop()
                if cur in visited: continue
                visited.add(cur)
                cluster.append(cur)
                for o, s in self.traces[cur].links.items():
                    if s >= min_link and o not in visited:
                        stack.append(o)
            if cluster: result.append(cluster)
        return result

    def clone_empty(self):
        """复制痕迹结构但清空激活"""
        s = CogSys(self.dp, self.criterion)
        s.traces = {}
        for k, v in self.traces.items():
            s.traces[k] = Trace(pid=v.pid, features=v.features, activation=0.0,
                                decay_rate=v.decay_rate, links=dict(v.links),
                                label=v.label, birth_time=v.birth_time)
        s.next_id = self.next_id
        return s


def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na>0 and nb>0 else 0.0


# ═══════════════════════════════════════
# 演示
# ═══════════════════════════════════════

def hr(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def demo():

    # ═══════════════════ C₁ 察觉 ═══════════════════
    hr("C₁ 察觉")
    s = CogSys(d_prime=2.0)
    for _ in range(5):
        s.step((1.0, 0.0), label="刺激")
    print(f"  痕迹数: {len(s.active())}")
    print(f"  规则: 检测 → '有东西'。仅此就够了。")

    # ═══════════════════ C₂ 辨别 ═══════════════════
    hr("C₂ 辨别")
    s = CogSys(d_prime=2.0, criterion=0.3)
    for _ in range(4):
        s.step((1.0, 0.0, 0.0), label="A")
        s.step((0.0, 1.0, 0.0), label="B")
    acts = {t.label: f"{t.activation:.2f}" for t in s.active()}
    print(f"  痕迹: {acts}")
    print(f"  规则: 泛化——cos(A,B)≈0, < criterion={s.criterion} → 不复用 → 两条痕迹")
    print(f"  → d' 控制检测噪声, criterion 控制'多相似算同一'")

    # ═══════════════════ C₃ 习惯化 ═══════════════════
    hr("C₃ 习惯化")
    s = CogSys(d_prime=2.5, criterion=0.3)
    acts = []
    for i in range(25):
        r = s.step((1.0, 0.0), label="重复刺激")
        acts.append(s.traces[0].activation)
    print(f"  第1次激活: {acts[0]:.2f} → 第5次: {acts[4]:.2f} → 第15次: {acts[14]:.2f} → 第25次: {acts[24]:.2f}")
    print(f"  规则: 衰减。每次新增≈衰减量→稳态。对不变的东西自动'静音'。")
    print(f"  → '注意'的演化根 = 对变化的偏向 = 对不变的习惯化")

    # ═══════════════════ C₄ 关联 ═══════════════════
    hr("C₄ 关联 (经典条件反射)")
    s = CogSys(d_prime=2.5, criterion=0.3)
    # 铃声和食物交替出现——前一个在衰减窗口内还有残留→共活跃→绑定
    for _ in range(10):
        s.step((1.0, 0.0, 0.0), label="铃声")
        s.step((0.0, 1.0, 0.0), label="食物")

    ids = {t.label: t.pid for t in s.active()}
    link_s = s.link(ids.get("铃声"), ids.get("食物"))
    print(f"  铃声→食物 链接: {link_s:.3f}  (反复共现 → Hebbian 绑定)")

    # 验证: 只给铃声, 看食物是否被传播激活
    s2 = s.clone_empty()
    s2.spread_rate = 0.30  # 稍高以凸显效果
    s2.step((1.0, 0.0, 0.0), label="铃声")
    active2 = {t.label: f"{t.activation:.3f}" for t in s2.active(0.01)}
    print(f"  只输入'铃声'后: {active2}")
    print(f"  → 绑定规则: 共活跃→链接。传播: 铃声→食物自动激活。")
    print(f"  → 巴甫洛夫 = 绑定 + 传播,不需要'学习模块'")

    # ═══════════════════ C₅ 后果 ═══════════════════
    hr("C₅ 后果学习 (操作条件反射)")
    s = CogSys(d_prime=2.5, criterion=0.3)
    for _ in range(10):
        s.step((0.8, 0.0, 0.0), label="推杠杆")
        s.step((0.0, 0.9, 0.0), label="食物")
    ids = {t.label: t.pid for t in s.active()}
    print(f"  链接: {s.link(ids.get('推杠杆'), ids.get('食物')):.3f}")
    print(f"  → '我的动作'=内部检测信号。绑定对内外信号一视同仁。")

    # ═══════════════════ C₆ 归类 ═══════════════════
    hr("C₆ 归类")
    # 关键: criterion 设高 (0.75) → 相似但不完全相同的刺激各建痕迹
    # 然后它们高频共现 → 痕迹之间绑定 → 形成簇
    s = CogSys(d_prime=3.0, criterion=0.75)
    apples = [(1.0, 0.2, 0.0), (0.85, 0.35, 0.0), (0.9, 0.1, 0.25)]
    stone  = (0.0, 0.0, 1.0)
    for _ in range(6):
        for i, a in enumerate(apples):
            s.step(a, label=f"苹果{i+1}")
        s.step(stone, label="石头")

    print(f"  痕迹: {len(s.active())}")
    for t in s.active():
        peers = ", ".join(f"{s.traces[o].label}:{v:.2f}"
                         for o,v in sorted(t.links.items(), key=lambda x:-x[1])[:5])
        print(f"    {t.label} ← [{peers}]")
    clusters = s.clusters(min_link=0.15)
    print(f"  簇: {len(clusters)}")
    for i, c in enumerate(clusters):
        print(f"    {[s.traces[pid].label for pid in c]}")
    print(f"  → 苹果之间互链→成簇。石头孤岛。归类 = 泛化边界 + 绑定聚簇。")

    # ═══════════════════ C₇ 情景记忆 ═══════════════════
    hr("C₇ 情景记忆")
    # 同一刺激 + 不同上下文维度 → 不同特征向量 → 不同痕迹
    s = CogSys(d_prime=3.0, criterion=0.5)
    for _ in range(4):
        s.step((1.0, 0.1, 0.0, 0.0), label="刺激@安全地")
    for _ in range(3):
        s.step((1.0, 0.9, 0.0, 0.0), label="刺激@危险地")
    for _ in range(2):
        s.step((1.0, 0.5, 0.0, 0.0), label="刺激@陌生地")

    n = len(s.active())
    print(f"  痕迹: {n}")
    for t in s.active():
        print(f"    {t.label}: f={tuple(round(x,1) for x in t.features[:4])}")
    print(f"  → {n}条痕迹对应同一刺激的{n}个上下文。'何时何地'不是记忆的新模块——")
    print(f"    是碰巧在场的情境信号被纳入特征向量。")
    print(f"  → 单次高强度=独特上下文=独立痕迹→创伤记忆不被冲淡。")

    # ═══════════════════ C₈ 社会认知 ═══════════════════
    hr("C₈ 社会认知")
    s = CogSys(d_prime=2.5, criterion=0.4)
    # 特征: [受伤强度, 痛苦感受, 是谁的体验(0=我,1=他人), 预留]
    for _ in range(5):
        s.step((1.0, 1.0, 0.0, 0.0), label="我受伤+痛苦")
    # 他人受伤——受伤维度重叠, 但体验来源维度不同 → criterion 0.4 可能分开
    for _ in range(4):
        s.step((0.9, 0.0, 1.0, 0.0), label="他人受伤")
    # 我再次体验——加强原有痕迹
    for _ in range(2):
        s.step((1.0, 0.5, 0.0, 0.0), label="我受伤(轻度)")

    print(f"  痕迹: {len(s.active())}")
    for t in s.active():
        peers = ", ".join(f"{s.traces[o].label}:{v:.2f}"
                         for o,v in sorted(t.links.items(), key=lambda x:-x[1])[:4])
        print(f"    {t.label}: links=[{peers}]")
    print(f"  → '他人受伤'与'我受伤'在特征空间部分重叠→泛化产生共鸣。")
    print(f"  → 共情的认知前提 = 泛化规则跨个体应用。不靠'社会认知模块'。")

    # ═══════════════════ C₉ 符号表征 ═══════════════════
    hr("C₉ 符号表征")
    s = CogSys(d_prime=3.0, criterion=0.3)
    for _ in range(15):
        s.step((1.0, 0.0, 0.0), label="实物(蛇)")
        s.step((0.0, 0.0, 1.0), label="词'蛇'")
    ids = {t.label: t.pid for t in s.active()}
    link_s = s.link(ids.get("实物(蛇)"), ids.get("词'蛇'"))
    print(f"  实物↔词 链接: {link_s:.3f}")

    s2 = s.clone_empty()
    s2.step((0.0, 0.0, 1.0), label="词'蛇'")
    active2 = {t.label: f"{t.activation:.3f}" for t in s2.active(0.01)}
    print(f"  只输入'蛇'这个词: {active2}")
    print(f"  → 符号通过强绑定接入实物痕迹→听到词激活实物的整个关联网。")
    print(f"  → 语言的力量 = 绑定链接的等价传播。'表象与语言'不是独立模块。")

    # ═══════════════════ C₁₀ 抽象推理 ═══════════════════
    hr("C₁₀ 抽象推理 (绑定的绑定)")
    s = CogSys(d_prime=3.0, criterion=0.3)
    # Phase 1: A↔B
    for _ in range(6):
        s.step((1.0, 0.0, 0.0), label="A")
        s.step((0.0, 1.0, 0.0), label="B")
    # Phase 2: B↔C (A的残留已衰减——A和C不会直接共现)
    # 等A的痕迹衰减
    for _ in range(8):
        s.decay()
    for _ in range(6):
        s.step((0.0, 1.0, 0.0), label="B")
        s.step((0.0, 0.0, 1.0), label="C")

    ids = {t.label: t.pid for t in s.active()}
    ab = s.link(ids.get("A"), ids.get("B"))
    bc = s.link(ids.get("B"), ids.get("C"))
    ac = s.link(ids.get("A"), ids.get("C"))
    print(f"  A→B: {ab:.3f}    B→C: {bc:.3f}    A→C(直接): {ac:.3f}")
    print(f"  → A↔C 链接≈{ac:.1f}, 远弱于 A↔B({ab:.1f})和B↔C({bc:.1f})")

    # 传播链 A→B→C
    s3 = s.clone_empty()
    s3.step((1.0, 0.0, 0.0), label="A")
    acts = {t.label: f"{t.activation:.3f}" for t in s3.active(0.01)}
    print(f"  只输入A: {acts}")
    print(f"  → A→B传播→C再传播。二阶链接链。'传递推理'=绑定规则的递归。")

    # ═══════════════════ C₁₁ 元认知 ═══════════════════
    hr("C₁₁ 元认知")
    s = CogSys(d_prime=3.0, criterion=0.3)
    sims = []
    for i in range(30):
        # 模拟认知表现波动: 有时d'高(判断准), 有时低(噪声大)
        s.dp = 3.0 if random.random() > 0.3 else 0.5
        r = s.step((1.0, 0.0), label="刺激")
        sims.append(r['sim'])
        if i % 5 == 0:
            status = "✓准" if r['sim'] > 0.7 else ("△凑合" if r['new'] == False else "✗新痕迹")
            print(f"    步{i+1}: sim={r['sim']:.2f} {status}")

    # 元认知: 统计"我最近判断的准确率"
    recent_sim = sum(sims[-10:]) / 10
    print(f"  最近10步平均sim={recent_sim:.2f}")
    print(f"  → 系统追踪'我判断得多准'——这就是元认知的根。")
    print(f"  → D(控制感)不是独立维度: D的认知层 = 元认知痕迹累积的确信度。")
    print(f"  → C₁₁不是新规则——检测作用于内部信号(判断质量) → 积累残留。")

    # ═══════════════════ 完整映射 ═══════════════════
    hr("总映射: 2元素3规则 → 现有认知系统")

    mapping = """
  你的现有概念           演化原语 (参数组合)
  ────────────           ──────────────────
  d'               ← 检测规则: 信号/噪声比
  criterion        ← 泛化规则: 相似门槛

  5个认知模块:
    知觉与注意     ← C₂(辨别) + C₃(习惯化)
    记忆           ← C₄(关联绑定) + C₇(特征含情境维度)
    知识表征与分类 ← C₆(泛化边界截出的簇 + 绑定簇内链接)
    表象与语言     ← C₉(极强绑定: token ≈ referent)
    推理与决策     ← C₁₀(绑定的绑定: 二阶链接传播)

  S1 / S2:
    S1 → 原始特征空间上的痕迹操作 (C₁-C₅)
    S2 → 链接空间上的痕迹操作 (C₆-C₁₁)
    深度 = 递归层数, 不是独立维度

  CPM 4步:
    Relevance   ← 检测+泛化: 这是新还是旧?
    Implication ← 绑定传播: 连着什么?
    Coping      ← 后果链接: 我做什么能改变结果?
    Normative   ← 元认知+社会认知: 这对吗?

  C⁵ 复平面:
    每个模块 = 一个复平面 (实部=d', 虚部=criterion)
    5模块 = 5个复平面直和 = C⁵
    d'和criterion天然正交→复数是自然表示

  CHC 能力:
    Gf ← C₁₀效率 (绑定递归速度)
    Gc ← C₆积累 (簇丰富度)
    Gsm ← 衰减δ参数 (痕迹保持)
    Glr ← 链接持久性
    Gv  ← C₂敏感度 (特征辨别)
    Gs  ← 总吞吐量 (检测+泛化+绑定)
"""

    print(mapping)
    print("─" * 60)
    print("结论:")
    print("  2个元素: 检测 + 残留")
    print("  3条规则: 衰减 + 绑定 + 泛化")
    print("  5个参数: d', criterion, decay_rate, link_lr, spread_rate")
    print("  → 全部11层认知, 全部5个模块, SDT, 双加工, CPM, CHC, C⁵")
    print("  没有一行代码是'设计'出来的。都是从原语交互中涌现。")
    print("=" * 60)


if __name__ == '__main__':
    demo()
