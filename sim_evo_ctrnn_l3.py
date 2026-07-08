#!/usr/bin/env python3
"""
CTRNN 认知演化 — 第三层 C₇ 情景记忆 (潮汐版)

C₇ 压力: 同一位置, 同一信号, 但在不同时间含义相反
  - 涨潮(上午): 信号 → 食物
  - 退潮(下午): 同一信号 → 威胁
  - agent 无法靠空间回避——食物就在那, 必须学时间上下文
"""

import math, random, sys
from collections import defaultdict

random.seed(3)

def sig(x): return 1.0/(1.0+math.exp(-x))

# ═══════════════════════ CTRNN ═══════════════════════

class CTRNN:
    def __init__(self, n=12, n_sens=5, n_mot=2):
        self.N, self.S, self.M = n, n_sens, n_mot
        self.y = [0.0]*n
        self.tau  = [random.uniform(0.5, 12.0) for _ in range(n)]
        self.bias = [random.uniform(-3.0, 3.0) for _ in range(n)]
        self.w    = [[random.uniform(-10.0, 10.0) for _ in range(n)] for _ in range(n)]
        self.w_in = [[random.uniform(-8.0, 8.0) for _ in range(n_sens)] for _ in range(n)]
        self.w_out= [[random.uniform(-6.0, 6.0) for _ in range(n)] for _ in range(n_mot)]

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

    def clone(self):
        c = CTRNN.__new__(CTRNN)
        c.N,c.S,c.M = self.N,self.S,self.M
        c.y = [0.0]*self.N
        c.tau = list(self.tau); c.bias = list(self.bias)
        c.w = [list(r) for r in self.w]
        c.w_in = [list(r) for r in self.w_in]
        c.w_out = [list(r) for r in self.w_out]
        return c

    def mutate(self, step=0.06):
        p = 0.2
        for i in range(self.N):
            if random.random()<p: self.tau[i]=max(0.1,self.tau[i]+random.gauss(0,step*1.5))
            if random.random()<p: self.bias[i]+=random.gauss(0,step)
            for j in range(self.N):
                if random.random()<p: self.w[i][j]+=random.gauss(0,step*2)
            for s in range(self.S):
                if random.random()<p: self.w_in[i][s]+=random.gauss(0,step*1.5)
        for m in range(self.M):
            for i in range(self.N):
                if random.random()<p: self.w_out[m][i]+=random.gauss(0,step)


# ═══════════════════════ 环境 v3 (潮汐) ═══════════════════════

class World:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.step = 0
        self.w, self.h = 200, 200

        # 潮汐周期: 300步涨潮(上午), 300步退潮(下午)
        self.cycle_len = 600
        self.tide_switch = 300

        # 三个食物源——涨潮时信号→食物, 退潮时信号→威胁
        # agent 必须靠近这些位置才能吃到食物
        # 这意味着退潮时它必须学会抑制趋近信号
        self.patches = [
            {'x':60,'y':60,'sig_r':35,'food_r':14,'val':50},
            {'x':140,'y':60,'sig_r':35,'food_r':14,'val':50},
            {'x':100,'y':140,'sig_r':40,'food_r':16,'val':55},
        ]

        # 每个 patch 独立的小周期 (信号出现→结果出现)
        for p in self.patches:
            p['cyc'] = random.randint(40, 55)
            p['phase_offset'] = random.randint(0, p['cyc']-1)

        # 杠杆
        self.lever = {'x':100,'y':100,'r':10.0}
        self.lever_cooldown = 0
        self.lever_food_timer = 0
        self.lever_food_val = 45.0
        self.lever_food_r = 15.0
        self.lever_food_x = 100
        self.lever_food_y = 100

        # 零星食物
        self.scatter_p = 0.003
        self.scatter_v = 6.0

    def tide(self):
        """0=涨潮(上午/安全), 1=退潮(下午/危险)"""
        return 0 if (self.step % self.cycle_len) < self.tide_switch else 1

    def tick(self, agent_x=None, agent_y=None):
        self.step += 1

        if self.lever_cooldown > 0:
            self.lever_cooldown -= 1
        if self.lever_food_timer > 0:
            self.lever_food_timer -= 1

        if agent_x is not None and agent_y is not None and self.lever_cooldown == 0:
            d = math.sqrt((agent_x-self.lever['x'])**2+(agent_y-self.lever['y'])**2)
            if d < self.lever['r']:
                self.lever_food_timer = 12
                self.lever_cooldown = 30
                self.lever_food_x = agent_x
                self.lever_food_y = agent_y

    def sense(self, x, y):
        tide = self.tide()
        is_flood = (tide == 0)

        sig_total = 0.0
        food_total = 0.0
        threat_total = 0.0

        for p in self.patches:
            ph = (self.step + p['phase_offset']) % p['cyc']

            # 信号期: 涨潮退潮都有信号——这是关键!
            sig_active = (ph < 20)
            # 结果期: 涨潮=食物, 退潮=威胁
            result_active = (22 <= ph < 32)

            d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)

            if sig_active and d < p['sig_r']:
                prog = ph / 20
                sig_total += (1-d/p['sig_r'])*(0.2+0.8*prog)

            if result_active and d < p['food_r']:
                intensity = (1-d/p['food_r'])
                if is_flood:
                    food_total += p['val']*intensity
                else:
                    threat_total += 2.0*intensity  # 强威胁——退潮时靠近会重伤

        sig_total = min(1.0, sig_total)

        # 杠杆食物 (任何时候都安全)
        if self.lever_food_timer > 0:
            d = math.sqrt((x-self.lever_food_x)**2+(y-self.lever_food_y)**2)
            if d < self.lever_food_r:
                food_total += self.lever_food_val*(1-d/self.lever_food_r)

        if self.rng.random() < self.scatter_p:
            food_total += self.scatter_v

        # 杠杆传感器
        d_lev = math.sqrt((x-self.lever['x'])**2+(y-self.lever['y'])**2)
        lever_sense = max(0, 1-d_lev/self.lever['r']) if d_lev < self.lever['r']*1.5 else 0.0

        # 时间传感器: 0=涨潮, 1=退潮
        time_sense = 0.0 if is_flood else 1.0

        return sig_total, min(1.0,food_total/50.0), min(1.0,threat_total), lever_sense, time_sense

    def actual_food(self, x, y):
        tide = self.tide()
        is_flood = (tide == 0)
        f = 0.0
        for p in self.patches:
            ph = (self.step + p['phase_offset']) % p['cyc']
            if 22 <= ph < 32 and is_flood:  # 只在涨潮时产出食物
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['food_r']:
                    f += p['val']*(1-d/p['food_r'])
        if self.lever_food_timer > 0:
            d = math.sqrt((x-self.lever_food_x)**2+(y-self.lever_food_y)**2)
            if d < self.lever_food_r:
                f += self.lever_food_val*(1-d/self.lever_food_r)
        return f


# ═══════════════════════ Agent ═══════════════════════

class Agent:
    def __init__(self, brain):
        self.brain = brain
        self.alive = True

    def reset(self, world):
        self.x = random.uniform(20, world.w-20)
        self.y = random.uniform(20, world.h-20)
        self.angle = random.uniform(0, 2*math.pi)
        self.energy = 60.0
        self.alive = True
        self.age = 0
        self.eaten = 0.0
        self.threat_hits = 0
        # C₇ 统计
        self.flood_approach = 0     # 涨潮(安全)时趋近信号次数
        self.ebb_avoid = 0          # 退潮(危险)时抑制趋近次数
        self.signal_opp_flood = 0   # 涨潮时的信号机会
        self.signal_opp_ebb = 0     # 退潮时的信号机会
        self.lever_activations = 0
        self.lever_food_eaten = 0.0
        self.brain.y = [0.0]*self.brain.N

    def update(self, world):
        if not self.alive: return
        self.age += 1

        sg, food, threat, lever, time_sense = world.sense(self.x, self.y)
        motor = self.brain.step([sg, food, threat, lever, time_sense])
        turn = max(-1, min(1, motor[0]))
        speed = max(0, min(2.5, sig(motor[1])*2.5))

        is_flood = (time_sense < 0.5)

        # C₇ 行为记录
        if sg > 0.1:
            if is_flood:
                self.signal_opp_flood += 1
                if speed > 0.5: self.flood_approach += 1  # 涨潮应该趋近
            else:
                self.signal_opp_ebb += 1
                if speed < 0.8: self.ebb_avoid += 1       # 退潮应该抑制

        # 杠杆
        if world.lever_food_timer == 11:
            d = math.sqrt((self.x-world.lever_food_x)**2+(self.y-world.lever_food_y)**2)
            if d < world.lever_food_r*2:
                self.lever_activations += 1

        # 代谢
        self.energy -= 0.12 + speed*0.2

        # 威胁
        if threat > 0.05:
            self.energy -= threat*2.5
            self.threat_hits += 1

        # 进食
        af = world.actual_food(self.x, self.y)
        if af > 0:
            self.energy += af
            self.eaten += af
            if world.lever_food_timer > 0:
                d = math.sqrt((self.x-world.lever_food_x)**2+(self.y-world.lever_food_y)**2)
                if d < world.lever_food_r:
                    self.lever_food_eaten += af

        # 移动
        self.angle += turn*0.8
        self.x = (self.x + math.cos(self.angle)*speed) % world.w
        self.y = (self.y + math.sin(self.angle)*speed) % world.h

        if self.energy <= 0: self.alive = False
        if self.age > 600: self.alive = False


# ═══════════════════════ 演化 ═══════════════════════

def evaluate(agent, world, trials=3, steps_per=450):
    total_fit = 0.0
    for _ in range(trials):
        agent.reset(world)
        for _ in range(steps_per):
            if not agent.alive: break
            world.tick(agent.x, agent.y)
            agent.update(world)

        # C₇ 核心适应度:
        # 涨潮时趋近 = 好, 退潮时趋近 = 坏
        flood_rate = agent.flood_approach / max(1, agent.signal_opp_flood)
        ebb_rate = 1.0 - (agent.ebb_avoid / max(1, agent.signal_opp_ebb))
        # ebb_rate 低 = 退潮时趋近少 = 好
        context_score = flood_rate * 30 - ebb_rate * 40

        fit = (agent.eaten
               + context_score
               - agent.threat_hits*8.0
               + agent.lever_activations*20.0
               + agent.lever_food_eaten*1.5
               + agent.age*0.03)
        total_fit += max(0.1, fit)
    return total_fit / trials


def evolve(pop_size=60, generations=150, elite=8, mut_step=0.05, n_neurons=14):
    world = World()
    pop = [Agent(CTRNN(n=n_neurons, n_sens=5, n_mot=2)) for _ in range(pop_size)]
    history = []
    best_ever = None

    for gen in range(generations):
        for a in pop:
            a.fitness = evaluate(a, world, trials=3, steps_per=450)
        pop.sort(key=lambda a: a.fitness, reverse=True)
        alive = [a for a in pop if a.fitness > 1.0]

        if alive:
            best = alive[0]
            if best_ever is None or best.fitness > best_ever.fitness:
                best_ever = best

            per_max = [max(a.brain.tau) for a in alive[:15]]
            per_min = [min(a.brain.tau) for a in alive[:15]]
            avg_sep = sum(per_max[i]-per_min[i] for i in range(len(per_max)))/len(per_max)

            flood_r = best.flood_approach/max(1,best.signal_opp_flood)
            ebb_r = best.ebb_avoid/max(1,best.signal_opp_ebb)

            history.append({
                'gen':gen, 'n':len(alive),
                'avg_fit':sum(a.fitness for a in alive)/len(alive),
                'best_fit':best.fitness, 'tau_sep':avg_sep,
                'flood_rate':flood_r, 'ebb_rate':ebb_r,
                'threat_hits':best.threat_hits, 'best_eaten':best.eaten,
            })

            if gen%25==0 or gen==generations-1:
                b = best.brain
                print(f"代{gen:3d} 存活{len(alive):2d} "
                      f"适应度={best.fitness:6.0f} 吃={best.eaten:5.0f} "
                      f"涨潮趋近={flood_r:.2f} 退潮回避={ebb_r:.2f} "
                      f"威胁={best.threat_hits} τ分离={max(b.tau)-min(b.tau):.1f}")

        new_pop = [Agent(pop[i].brain.clone()) for i in range(elite)]
        while len(new_pop) < pop_size:
            pool = pop[:pop_size//2]
            parent = max(random.sample(pool, 3), key=lambda a: a.fitness)
            child = Agent(parent.brain.clone())
            child.brain.mutate(mut_step)
            new_pop.append(child)
        pop = new_pop

    for a in pop:
        a.fitness = evaluate(a, world, trials=3, steps_per=450)
    pop.sort(key=lambda a: a.fitness, reverse=True)
    return best_ever, pop, history


# ═══════════════════════ 分析 ═══════════════════════

def analyze(best, pop, history):
    if best is None:
        print("无存活。"); return

    b = best.brain
    flood_r = best.flood_approach/max(1,best.signal_opp_flood)
    ebb_r = best.ebb_avoid/max(1,best.signal_opp_ebb)

    print(f"\n{'='*60}")
    print(f"  涌现分析 ({b.N}神经元, 适应度={best.fitness:.0f})")
    print(f"{'='*60}")

    taus = sorted(b.tau)
    print(f"\n  1. τ: [{', '.join(f'{t:.1f}' for t in taus)}]  分离={max(taus)-min(taus):.1f}")

    snames = ['信号','食物','威胁','杠杆','时间']
    print(f"\n  2. 感觉权重:")
    for i in range(b.N):
        w = b.w_in[i]
        dom = snames[max(range(5), key=lambda j: abs(w[j]))]
        print(f"     N{i:2d} (τ={b.tau[i]:.1f}): "
              f"[{w[0]:+6.2f} {w[1]:+6.2f} {w[2]:+6.2f} {w[3]:+6.2f} {w[4]:+6.2f}] → {dom}")
    channels = set()
    for i in range(b.N):
        channels.add(max(range(5), key=lambda j: abs(b.w_in[i][j])))
    print(f"     通道分化: {len(channels)}/5")

    print(f"\n  3. C₇ 情景记忆 (潮汐):")
    print(f"     涨潮趋近率: {flood_r:.2f} (应该高——涨潮时信号→食物)")
    print(f"     退潮回避率: {ebb_r:.2f} (应该高——退潮时信号→威胁)")
    print(f"     威胁伤害: {best.threat_hits}")

    # 信号×时间 交互
    sig_time = [(i, b.w_in[i][0], b.w_in[i][4])
                for i in range(b.N)
                if abs(b.w_in[i][0]) > 2.0 and abs(b.w_in[i][4]) > 2.0]
    if sig_time:
        print(f"     信号×时间交互神经元: {len(sig_time)}个")
        for i,s,t in sig_time[:4]:
            print(f"       N{i}(τ={b.tau[i]:.1f}): sig={s:+.1f} time={t:+.1f}")

    # C₇ 判定
    print(f"\n  4. C₇ 判定:")
    if flood_r > 0.4 and ebb_r > 0.4:
        print(f"     ✓✓ 情景记忆: 涨潮趋近({flood_r:.0%}) + 退潮回避({ebb_r:.0%})")
        print(f"       agent 学会了同一信号在不同时间的含义相反")
    elif flood_r > 0.3 or ebb_r > 0.3:
        print(f"     ~ 部分情景敏感: 涨潮={flood_r:.0%} 退潮={ebb_r:.0%}")
    else:
        print(f"     ✗ 未显示情景敏感行为")

    # 种群中的最佳情景记忆者
    best_ctxt = max(pop, key=lambda a:
        (a.flood_approach/max(1,a.signal_opp_flood) +
         a.ebb_avoid/max(1,a.signal_opp_ebb) -
         a.threat_hits*0.5))
    bf = best_ctxt.flood_approach/max(1,best_ctxt.signal_opp_flood)
    be = best_ctxt.ebb_avoid/max(1,best_ctxt.signal_opp_ebb)
    print(f"     种群最佳情景记忆者: 涨潮={bf:.0%} 退潮={be:.0%} "
          f"威胁={best_ctxt.threat_hits} 适应度={best_ctxt.fitness:.0f}")

    print(f"\n  5. 涌现判断:")
    checks = [f'C₂ 辨别: {len(channels)}/5 通道']
    if flood_r > 0.4 and ebb_r > 0.4:
        checks.append(f'C₇ 情景记忆: 潮汐行为分化 (涨潮{flood_r:.0%}/退潮{ebb_r:.0%})')
    elif flood_r > 0.3 or ebb_r > 0.3:
        checks.append(f'C₇ 前兆: 部分潮汐敏感')
    if max(b.tau)-min(b.tau) > 6:
        checks.append('C₃ 记忆: τ多时间尺度')
    for c in checks: print(f"     ✓ {c}")
    print(f"{'='*60}")


if __name__ == '__main__':
    GENS = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    N = 14
    print(f"CTRNN 认知演化 L3 潮汐版 (C₇) — {GENS} 代")
    print(f"{N}神经元 5传感器 潮汐周期600步(涨潮300/退潮300)")
    print(f"涨潮: 信号→食物 | 退潮: 同一信号→威胁 | 同一位置!")
    best, pop, history = evolve(pop_size=60, generations=GENS, mut_step=0.05, n_neurons=N)
    analyze(best, pop, history)
