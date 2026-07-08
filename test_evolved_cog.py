#!/usr/bin/env python3
"""
用演化出的 CTRNN 做受控行为测试

提取 sim_evo_ctrnn 中最佳 agent 的脑参数，
在隔离的测试场景中逐项验证:
  C₂ 辨别 — 能否区分信号/食物/威胁
  C₃ 记忆 — 信号消失后行为是否仍受其影响
  C₄ 关联前兆 — 信号后是否预判食物位置
"""

import math, random, sys, copy
from collections import defaultdict

random.seed(5)

# ═══════════════════════ 复用 CTRNN ═══════════════════════

def sig(x): return 1.0/(1.0+math.exp(-x))

class CTRNN:
    def __init__(self, n=4, n_sens=3, n_mot=2):
        self.N, self.S, self.M = n, n_sens, n_mot
        self.y = [0.0]*n
        self.tau  = [1.0]*n
        self.bias = [0.0]*n
        self.w    = [[0.0]*n for _ in range(n)]
        self.w_in = [[0.0]*n_sens for _ in range(n)]
        self.w_out= [[0.0]*n for _ in range(n_mot)]

    def step(self, sensory, dt=0.1):
        inp = [0.0]*self.N
        for i in range(self.N):
            rec = sum(self.w[j][i]*sig(self.y[j]+self.bias[j]) for j in range(self.N))
            sen = sum(self.w_in[i][s]*sensory[s] for s in range(self.S))
            inp[i] = rec + sen
        for i in range(self.N):
            dy = (-self.y[i] + inp[i]) / max(0.1, self.tau[i])
            self.y[i] += dy*dt
            self.y[i] = max(-15, min(15, self.y[i]))
        return [sum(self.w_out[m][i]*sig(self.y[i]+self.bias[i]) for i in range(self.N))
                for m in range(self.M)]


class Agent:
    def __init__(self, brain):
        self.brain = brain
        self.x = 100.0; self.y = 100.0
        self.angle = 0.0

    def reset(self, x=100, y=100, angle=0):
        self.x, self.y = x, y
        self.angle = angle
        self.brain.y = [0.0]*self.brain.N

    def sense_and_act(self, sig_val, food_val, threat_val):
        motor = self.brain.step([sig_val, food_val, threat_val])
        turn = max(-1, min(1, motor[0]))
        speed = max(0, min(2.5, sig(motor[1])*2.5))
        return turn, speed

    def move(self, turn, speed):
        self.angle += turn*0.8
        self.x += math.cos(self.angle)*speed
        self.y += math.sin(self.angle)*speed


# ═══════════════════════ 加载演化出的脑 ═══════════════════════

def load_best_brain():
    """重新跑一次短演化，拿到最佳脑参数"""
    import sim_evo_ctrnn as evo
    best, pop, hist = evo.evolve(pop_size=40, generations=80, mut_step=0.12)
    if best is None:
        print("演化失败，使用随机脑")
        return CTRNN()
    print(f"加载最佳脑: 适应度={best.fitness:.0f}, τ={[f'{t:.1f}' for t in best.brain.tau]}")
    return best.brain


# ═══════════════════════ 测试场景 ═══════════════════════

def run_trial(agent, signal_seq, food_seq, threat_seq, steps):
    """给 agent 喂一系列 (sig, food, threat) 输入，记录行为"""
    agent.reset()
    log = []
    for t in range(steps):
        turn, speed = agent.sense_and_act(
            signal_seq[t] if t < len(signal_seq) else 0.0,
            food_seq[t] if t < len(food_seq) else 0.0,
            threat_seq[t] if t < len(threat_seq) else 0.0,
        )
        agent.move(turn, speed)
        log.append({
            't': t, 'turn': turn, 'speed': speed,
            'x': agent.x, 'y': agent.y, 'angle': agent.angle,
            'y0': agent.brain.y[0], 'y1': agent.brain.y[1],
            'y2': agent.brain.y[2], 'y3': agent.brain.y[3],
        })
    return log


def baseline_random(steps):
    """随机游走基线"""
    agent = Agent(CTRNN())  # 全零权重 → 纯随机
    return run_trial(agent, [], [], [], steps)


# ═══════════════════════ 测试 1: C₂ 辨别 ═══════════════════════

def test_discrimination(brain):
    """三个纯信号分别测试，看行为是否分化"""
    print(f"\n{'='*60}")
    print(f"  测试 C₂: 辨别")
    print(f"{'='*60}")

    agent = Agent(brain)
    tests = {
        '纯信号 (sig=1, food=0, threat=0)': ([1.0]*30, [0.0]*30, [0.0]*30),
        '纯食物 (sig=0, food=1, threat=0)': ([0.0]*30, [1.0]*30, [0.0]*30),
        '纯威胁 (sig=0, food=0, threat=1)': ([0.0]*30, [0.0]*30, [1.0]*30),
        '混合 (sig=1, threat=1)':             ([1.0]*30, [0.0]*30, [1.0]*30),
    }

    results = {}
    for name, (sig_seq, food_seq, threat_seq) in tests.items():
        log = run_trial(agent, sig_seq, food_seq, threat_seq, 30)
        avg_speed = sum(r['speed'] for r in log[5:]) / 25  # 跳过前5步预热
        avg_turn = sum(abs(r['turn']) for r in log[5:]) / 25
        # net displacement
        dx = log[-1]['x'] - log[0]['x']
        dy = log[-1]['y'] - log[0]['y']
        dist = math.sqrt(dx**2 + dy**2)
        results[name] = {'speed': avg_speed, 'turn': avg_turn, 'dist': dist,
                         'final_y': [round(log[-1][f'y{i}'],2) for i in range(4)]}

    # 输出
    print(f"  {'场景':<30} {'均速':>6} {'转角':>6} {'位移':>7} {'最终神经元状态'}")
    print(f"  {'─'*30} {'─'*6} {'─'*6} {'─'*7} {'─'*30}")
    for name, r in results.items():
        print(f"  {name:<30} {r['speed']:5.2f} {r['turn']:5.2f} {r['dist']:6.1f}  {r['final_y']}")

    # C₂ 判定: 不同输入 → 不同行为输出
    speeds = [r['speed'] for r in results.values()]
    if max(speeds) - min(speeds) > 0.3:
        print(f"  ✓ 辨别成立: 不同输入产生不同行为 (速度差={max(speeds)-min(speeds):.2f})")
    else:
        print(f"  ✗ 辨别失败: 所有输入产生相似行为")

    # 威胁回避判定
    threat_speed = results['纯威胁 (sig=0, food=0, threat=1)']['speed']
    signal_speed = results['纯信号 (sig=1, food=0, threat=0)']['speed']
    if threat_speed < signal_speed * 0.7:
        print(f"  ✓ 威胁回避: 威胁时速度({threat_speed:.2f}) < 信号时({signal_speed:.2f})")
    elif threat_speed > signal_speed * 1.2:
        print(f"  ~ 威胁反而加速? 威胁速度({threat_speed:.2f}) > 信号速度({signal_speed:.2f})")

    return results


# ═══════════════════════ 测试 2: C₃ 记忆持久性 ═══════════════════════

def test_memory(brain):
    """信号消失后，内部状态和行为持续多久"""
    print(f"\n{'='*60}")
    print(f"  测试 C₃: 记忆持久性")
    print(f"{'='*60}")

    agent = Agent(brain)
    agent.reset()

    # Phase 1: 给信号 20 步
    # Phase 2: 零输入 50 步
    sig_seq = [1.0]*20 + [0.0]*50
    food_seq = [0.0]*70
    threat_seq = [0.0]*70

    log = run_trial(agent, sig_seq, food_seq, threat_seq, 70)

    # 慢神经元轨迹
    tau_rank = sorted(range(brain.N), key=lambda i: brain.tau[i])
    slow_i = tau_rank[-1]
    fast_i = tau_rank[0]

    print(f"  最慢神经元 (#{slow_i}, τ={brain.tau[slow_i]:.1f}) 轨迹:")
    for t in [0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 69]:
        if t < len(log):
            print(f"    t={t:2d}: y[{slow_i}]={log[t][f'y{slow_i}']:+.3f}  "
                  f"speed={log[t]['speed']:.2f}")

    # 半衰期: 信号消失后多少步 y 衰减到峰值的一半
    peak_y = max(abs(r[f'y{slow_i}']) for r in log[15:25])  # 信号期间峰值
    half_life = None
    for r in log[20:]:
        if abs(r[f'y{slow_i}']) < peak_y * 0.5:
            half_life = r['t'] - 20
            break

    print(f"  峰值激活: {peak_y:.2f}")
    if half_life is not None:
        print(f"  半衰期: {half_life} 步 (信号消失后)")
        if half_life > 20:
            print(f"  ✓ 长记忆: 半衰期 > 20步 → 慢神经元有效承载了信号记忆")
        elif half_life > 10:
            print(f"  ~ 中等记忆: 半衰期 {half_life} 步")
        else:
            print(f"  ✗ 短记忆: 半衰期 {half_life} 步")
    else:
        print(f"  半衰期内未衰减到一半 → 记忆 >= 50步")

    # 行为持久性: 信号消失后速度是否仍受影响
    speed_during_signal = sum(r['speed'] for r in log[10:20])/10
    speed_after_signal = sum(r['speed'] for r in log[30:50])/20
    print(f"  信号期间均速: {speed_during_signal:.2f}")
    print(f"  信号消失后均速: {speed_after_signal:.2f}")
    if speed_after_signal > speed_during_signal * 0.4:
        print(f"  ✓ 行为持续: 信号消失后仍保持 {speed_after_signal/speed_during_signal:.0%} 速度")
    else:
        print(f"  ~ 信号消失后行为快速消退")

    return log


# ═══════════════════════ 测试 3: C₄ 关联预判 ═══════════════════════

def test_association(brain):
    """信号→食物 的时间关联: 信号消失后 agent 是否向食物源方向移动"""
    print(f"\n{'='*60}")
    print(f"  测试 C₄: 关联预判 (信号→食物)")
    print(f"{'='*60}")

    agent = Agent(brain)

    # 模拟自然场景: 信号在 (0,0) 处释放, 食物将在 (0,0) 处出现
    # agent 初始在 (50, 0) —— 在信号范围内但不是食物位置
    # 信号持续 15 步 → 消失 → 20 步后食物出现

    total_steps = 50
    sig_seq = [0.0]*total_steps
    food_seq = [0.0]*total_steps
    threat_seq = [0.0]*total_steps

    # Phase 1: 信号 (t=0..14)
    for t in range(15):
        d = math.sqrt((agent.x-0)**2 + (agent.y-0)**2) if t == 0 else 0
        # agent 初始在 (50,0)，距离信号源 50
        sig_seq[t] = 1.0  # 强信号

    # Phase 2: 无信号 (t=15..34) — 等待期
    # Phase 3: 食物出现 (t=35..49)
    for t in range(35, 50):
        food_seq[t] = 1.0

    agent.reset(x=50, y=0, angle=math.pi)  # 朝向信号源 (向左)
    log = run_trial(agent, sig_seq, food_seq, threat_seq, total_steps)

    # 分析:
    # - 信号期间 (0-14): agent 应该向信号源移动
    # - 等待期 (15-34): 慢神经元如果记得信号, agent 应该继续向信号源方向移动
    # - 食物期 (35-49): agent 应该在食物附近

    x_start = log[0]['x']
    x_signal_end = log[14]['x']   # 信号结束时位置
    x_wait_end = log[34]['x']     # 等待期结束时位置
    x_final = log[-1]['x']

    print(f"  位置变化:")
    print(f"    初始 x={x_start:.1f}")
    print(f"    信号结束 t=14: x={x_signal_end:.1f} (移动 {x_signal_end-x_start:+.1f})")
    print(f"    等待结束 t=34: x={x_wait_end:.1f} (移动 {x_wait_end-x_signal_end:+.1f})")
    print(f"    最终 t=49:     x={x_final:.1f}")

    # 关键指标: 等待期是否继续向信号源移动
    toward_signal_wait = x_wait_end - x_signal_end
    if toward_signal_wait < -2:  # 继续向信号源(x=0)移动
        print(f"  ✓ 关联记忆: 信号消失后继续向信号源移动 {toward_signal_wait:.1f} 单位")
        print(f"    → 慢神经元在信号消失后维持了'信号源方向'的信息")
    elif toward_signal_wait < 0:
        print(f"  ~ 弱关联: 向信号源微移 {toward_signal_wait:.1f} 单位")
    else:
        print(f"  ✗ 无关联: 信号消失后未向信号源移动")

    # 对比: 随机基线
    rand_log = baseline_random(total_steps)
    rand_x_end = rand_log[14]['x']
    rand_x_final = rand_log[-1]['x']
    print(f"  随机基线: t=14 x={rand_x_end:.1f}, t=49 x={rand_x_final:.1f}")

    return log


# ═══════════════════════ 测试 4: 习惯化 ═══════════════════════

def test_habituation(brain):
    """反复虚假信号 → 响应是否递减"""
    print(f"\n{'='*60}")
    print(f"  测试 C₃: 习惯化 (重复虚假信号)")
    print(f"{'='*60}")

    agent = Agent(brain)

    # 4 轮虚假信号: 每轮 15 步信号 + 15 步间隔
    total_steps = 4 * 30
    sig_seq = [0.0]*total_steps
    food_seq = [0.0]*total_steps
    threat_seq = [0.0]*total_steps

    for block in range(4):
        start = block * 30
        for t in range(start, start+15):
            sig_seq[t] = 1.0

    agent.reset()
    log = run_trial(agent, sig_seq, food_seq, threat_seq, total_steps)

    # 每轮信号期间的平均速度
    speeds = []
    for block in range(4):
        start = block * 30
        block_speeds = [r['speed'] for r in log[start:start+15]]
        speeds.append(sum(block_speeds)/len(block_speeds))

    print(f"  各轮信号期间均速:")
    for i, s in enumerate(speeds):
        change = "" if i == 0 else f"({s-speeds[i-1]:+.2f} vs上轮)"
        print(f"    第{i+1}轮: {s:.2f} {change}")

    if speeds[-1] < speeds[0] * 0.7:
        print(f"  ✓ 习惯化: 响应递减至 {speeds[-1]/speeds[0]:.0%}")
    elif speeds[-1] < speeds[0]:
        print(f"  ~ 弱习惯化: 响应微降")
    else:
        print(f"  ✗ 未习惯化: 响应不变或增加")

    return log


# ═══════════════════════ 主流程 ═══════════════════════

if __name__ == '__main__':
    print("加载演化后的脑参数...")
    brain = load_best_brain()

    # 打印脑结构
    print(f"\n  脑结构总览:")
    print(f"  {'神经元':<8} {'τ':<6} {'偏置':<6} {'信号':<7} {'食物':<7} {'威胁':<7}")
    for i in range(brain.N):
        print(f"  {i:<8} {brain.tau[i]:<6.1f} {brain.bias[i]:<+6.2f} "
              f"{brain.w_in[i][0]:<+7.2f} {brain.w_in[i][1]:<+7.2f} {brain.w_in[i][2]:<+7.2f}")

    # 逐一测试
    test_discrimination(brain)
    test_memory(brain)
    test_association(brain)
    test_habituation(brain)

    print(f"\n{'='*60}")
    print(f"  测试完成")
    print(f"{'='*60}")
