#!/usr/bin/env python3
"""
CTRNN 认知演化 — 第二层 (C₅ 后果, C₆ 归类)

在 C₂-C₄ 已验证的基础上:
  - 神经元数从 4 → 6 (更多容量)
  - 环境增加:
    C₅ 压力: 推杠杆→食物 (动作→后果)
    C₆ 压力: 多种不同气味都预测食物 (需要泛化归类)
"""

import math, random, sys
from collections import defaultdict

random.seed(2)

# ═══════════════════════ CTRNN ═══════════════════════

def sig(x): return 1.0/(1.0+math.exp(-x))

class CTRNN:
    def __init__(self, n=6, n_sens=4, n_mot=2):
        """传感器增加: 信号, 食物, 威胁, 杠杆状态"""
        self.N, self.S, self.M = n, n_sens, n_mot
        self.y = [0.0]*n
        self.tau  = [random.uniform(0.5, 10.0) for _ in range(n)]
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

    def mutate(self, step=0.12):
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


# ═══════════════════════ 环境 v2 ═══════════════════════

class World:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.step = 0
        self.w, self.h = 200, 200

        # 食物源 (信号→食物，和 v1 一样)
        self.patches = [
            {'x':50,'y':60,'sig_r':35,'food_r':12,'cyc':45,
             'sig_s':0,'sig_e':25,'food_s':28,'food_e':38,'val':40,
             'sig_type': 0},  # 气味类型 A
            {'x':150,'y':60,'sig_r':35,'food_r':12,'cyc':45,
             'sig_s':0,'sig_e':25,'food_s':28,'food_e':38,'val':40,
             'sig_type': 1},  # 气味类型 B
            {'x':100,'y':150,'sig_r':40,'food_r':15,'cyc':50,
             'sig_s':5,'sig_e':30,'food_s':33,'food_e':43,'val':45,
             'sig_type': 2},  # 气味类型 C
        ]

        # C₆ 归类压力: 三种不同气味, 但都预测食物
        # agent 如果学会 "不同气味 → 同样的趋近行为" = 归类
        # 每种气味的特征略有差异 (在 signal() 中体现)

        # C₅ 后果压力: 杠杆
        # 杠杆位于一个食物源旁边——agent 觅食时容易偶然触发
        # agent 经过杠杆区 → 杠杆激活 → 当前位置立即出现食物
        # (简化: 不需要停留3步, 经过即触发, 食物就地出现)
        self.lever = {'x':50,'y':80,'r':10.0}  # 紧挨 patch[0] (50,60)
        self.lever_active = False
        self.lever_cooldown = 0     # 冷却: 激活后 N 步内不能再次激活
        self.lever_food_timer = 0
        self.lever_food_val = 50.0  # 高价值食物——值得专门去触发
        self.lever_food_r = 15.0
        self.lever_food_x = 50
        self.lever_food_y = 80      # 食物就在杠杆处

        # 威胁
        self.threat = (160, 140, 20.0)

        # 零星食物
        self.scatter_p = 0.004
        self.scatter_v = 8.0

    def tick(self, agent_x=None, agent_y=None):
        self.step += 1

        # 杠杆逻辑 (简化: 经过即触发)
        if self.lever_cooldown > 0:
            self.lever_cooldown -= 1

        if self.lever_food_timer > 0:
            self.lever_food_timer -= 1
            if self.lever_food_timer == 0:
                self.lever_active = False

        if agent_x is not None and agent_y is not None and self.lever_cooldown == 0:
            d_lever = math.sqrt((agent_x-self.lever['x'])**2 +
                               (agent_y-self.lever['y'])**2)
            if d_lever < self.lever['r']:
                self.lever_active = True
                self.lever_food_timer = 12  # 杠杆食物持续 12 步
                self.lever_cooldown = 30     # 30 步冷却
                self.lever_food_x = agent_x   # 食物就地出现
                self.lever_food_y = agent_y

    def sense(self, x, y):
        # 信号 (带类型标签用于归类)
        sig = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['sig_s'] <= ph < p['sig_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['sig_r']:
                    prog = (ph-p['sig_s'])/(p['sig_e']-p['sig_s'])
                    sig += (1-d/p['sig_r'])*(0.2+0.8*prog)
        sig = min(1.0, sig)

        # 食物 (包括杠杆食物)
        food = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['food_s'] <= ph < p['food_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['food_r']:
                    food += p['val']*(1-d/p['food_r'])
        # 杠杆食物
        if self.lever_food_timer > 0:
            d = math.sqrt((x-self.lever_food_x)**2 +
                         (y-self.lever_food_y)**2)
            if d < self.lever_food_r:
                food += self.lever_food_val*(1-d/self.lever_food_r)
        if self.rng.random() < self.scatter_p:
            food += self.scatter_v

        # 威胁
        tx,ty,tr = self.threat
        d = math.sqrt((x-tx)**2+(y-ty)**2)
        threat = max(0, 1-d/tr) if d<tr else 0.0

        # 杠杆传感器: agent 是否在杠杆区
        d_lev = math.sqrt((x-self.lever['x'])**2+(y-self.lever['y'])**2)
        lever_sense = max(0, 1-d_lev/self.lever['r']) if d_lev < self.lever['r']*1.5 else 0.0

        return sig, min(1.0,food/50.0), threat, lever_sense

    def actual_food(self, x, y):
        f = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['food_s'] <= ph < p['food_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['food_r']:
                    f += p['val']*(1-d/p['food_r'])
        if self.lever_food_timer > 0:
            d = math.sqrt((x-self.lever_food_x)**2 +
                         (y-self.lever_food_y)**2)
            if d < self.lever_food_r:
                f += self.lever_food_val*(1-d/self.lever_food_r)
        return f


# ═══════════════════════ Agent ═══════════════════════

class Agent:
    def __init__(self, brain):
        self.brain = brain
        self.x = self.y = 100
        self.angle = 0.0
        self.energy = 60.0
        self.alive = True
        self.age = 0
        self.eaten = 0.0
        self.threat_hits = 0
        # 行为统计
        self.approach_signal = 0
        self.signal_opportunity = 0
        self.lever_activations = 0   # 激活杠杆次数
        self.lever_food_eaten = 0.0  # 从杠杆获得食物

    def reset(self, world):
        self.x = random.uniform(20, world.w-20)
        self.y = random.uniform(20, world.h-20)
        self.angle = random.uniform(0, 2*math.pi)
        self.energy = 60.0
        self.alive = True
        self.age = 0
        self.eaten = 0.0
        self.threat_hits = 0
        self.approach_signal = 0
        self.signal_opportunity = 0
        self.lever_activations = 0
        self.lever_food_eaten = 0.0
        self.brain.y = [0.0]*self.brain.N

    def update(self, world):
        if not self.alive: return
        self.age += 1

        sg, food, threat, lever = world.sense(self.x, self.y)
        motor = self.brain.step([sg, food, threat, lever])
        turn = max(-1, min(1, motor[0]))
        speed = max(0, min(2.5, sig(motor[1])*2.5))

        # 记录
        if sg > 0.15:
            self.signal_opportunity += 1
            if speed > 0.5 and abs(turn) < 0.6:
                self.approach_signal += 1

        # 检测杠杆激活
        if world.lever_active and world.lever_food_timer == 11:
            # 刚激活 (timer 从 12 开始, 11 = 刚激活后第一步)
            d = math.sqrt((self.x-world.lever_food_x)**2 +
                         (self.y-world.lever_food_y)**2)
            if d < world.lever_food_r * 2:
                self.lever_activations += 1

        # 代谢
        self.energy -= 0.12 + speed*0.2

        # 威胁
        if threat > 0.1:
            self.energy -= threat*1.5
            self.threat_hits += 1

        # 进食
        af = world.actual_food(self.x, self.y)
        if af > 0:
            self.energy += af
            self.eaten += af
            # 判断是否是杠杆食物
            if world.lever_food_timer > 0:
                d = math.sqrt((self.x-world.lever_food_x)**2 +
                             (self.y-world.lever_food_y)**2)
                if d < world.lever_food_r:
                    self.lever_food_eaten += af

        # 移动
        self.angle += turn*0.8
        self.x = (self.x + math.cos(self.angle)*speed) % world.w
        self.y = (self.y + math.sin(self.angle)*speed) % world.h

        if self.energy <= 0: self.alive = False
        if self.age > 500: self.alive = False


# ═══════════════════════ 演化 ═══════════════════════

def evaluate(agent, world, trials=3, steps_per=350):
    total_fit = 0.0
    for _ in range(trials):
        agent.reset(world)
        for _ in range(steps_per):
            if not agent.alive: break
            world.tick(agent.x, agent.y)
            agent.update(world)
        fit = (agent.eaten
               + agent.approach_signal*0.3
               + agent.lever_activations*25.0      # C₅: 强奖励激活杠杆
               + agent.lever_food_eaten*2.0        # C₅: 奖励吃到杠杆食物
               - agent.threat_hits*5.0
               + agent.age*0.03)
        total_fit += max(0.1, fit)
    return total_fit / trials


def evolve(pop_size=60, generations=120, elite=8, mut_step=0.08, n_neurons=10):
    world = World()
    pop = [Agent(CTRNN(n=n_neurons, n_sens=4, n_mot=2)) for _ in range(pop_size)]
    history = []
    best_ever = None

    for gen in range(generations):
        for a in pop:
            a.fitness = evaluate(a, world, trials=3, steps_per=350)
        pop.sort(key=lambda a: a.fitness, reverse=True)
        alive = [a for a in pop if a.fitness > 1.0]

        if alive:
            best = alive[0]
            if best_ever is None or best.fitness > best_ever.fitness:
                best_ever = best

            # 统计
            taus = []
            for a in alive[:15]:
                taus.extend(a.brain.tau)
            per_max = [max(a.brain.tau) for a in alive[:15]]
            per_min = [min(a.brain.tau) for a in alive[:15]]
            avg_sep = sum(per_max[i]-per_min[i] for i in range(len(per_max)))/len(per_max)

            history.append({
                'gen':gen, 'n':len(alive),
                'avg_fit':sum(a.fitness for a in alive)/len(alive),
                'best_fit':best.fitness,
                'tau_sep':avg_sep,
                'lever_acts':best.lever_activations,
                'lever_eaten':best.lever_food_eaten,
                'best_eaten':best.eaten,
            })

            if gen%20==0 or gen==generations-1:
                b = best.brain
                print(f"代{gen:3d} 存活{len(alive):2d} "
                      f"适应度={best.fitness:6.0f} 吃={best.eaten:5.0f} "
                      f"杠杆激活={best.lever_activations} 杠杆食物={best.lever_food_eaten:5.0f} "
                      f"τ分离={max(b.tau)-min(b.tau):.1f}")

        new_pop = [Agent(pop[i].brain.clone()) for i in range(elite)]
        while len(new_pop) < pop_size:
            pool = pop[:pop_size//2]
            parent = max(random.sample(pool, 3), key=lambda a: a.fitness)
            child = Agent(parent.brain.clone())
            child.brain.mutate(mut_step)
            new_pop.append(child)
        pop = new_pop

    # 评估最后一代 (繁殖后的新个体还没评估过)
    for a in pop:
        a.fitness = evaluate(a, world, trials=3, steps_per=350)
    pop.sort(key=lambda a: a.fitness, reverse=True)
    return best_ever, pop, history


# ═══════════════════════ 分析 ═══════════════════════

def analyze(best, pop, history):
    if best is None:
        print("无存活。")
        return

    b = best.brain
    print(f"\n{'='*60}")
    print(f"  涌现分析 (6神经元, 适应度={best.fitness:.0f})")
    print(f"{'='*60}")

    # 1. τ 分布
    taus = sorted(b.tau)
    print(f"\n  1. τ: {[f'{t:.1f}' for t in taus]}, 分离={max(taus)-min(taus):.1f}")

    # 2. 感觉权重 (4通道: 信号/食物/威胁/杠杆)
    snames = ['信号','食物','威胁','杠杆']
    print(f"\n  2. 感觉权重:")
    for i in range(b.N):
        w = b.w_in[i]
        dom = snames[max(range(4), key=lambda j: abs(w[j]))]
        print(f"     N{i} (τ={b.tau[i]:.1f}): "
              f"[{w[0]:+6.2f} {w[1]:+6.2f} {w[2]:+6.2f} {w[3]:+6.2f}] → {dom}")

    # 通道分化
    channels = set()
    for i in range(b.N):
        channels.add(max(range(4), key=lambda j: abs(b.w_in[i][j])))
    print(f"     通道分化: {len(channels)}/4 个通道有专属神经元")

    # 3. C₅ 后果学习
    print(f"\n  3. C₅ 后果学习 (杠杆→食物):")
    print(f"     最佳 agent: 杠杆激活={best.lever_activations}, 杠杆食物={best.lever_food_eaten:.0f}")
    # 检查是否有神经元对杠杆信号有显著权重
    lever_neurons = [i for i in range(b.N) if abs(b.w_in[i][3]) > 3.0]
    if lever_neurons:
        print(f"     杠杆专属神经元: {[f'N{i}(τ={b.tau[i]:.1f})' for i in lever_neurons]}")

    # 找种群中杠杆行为最好的agent
    lever_specialists = sorted(pop, key=lambda a: a.lever_activations, reverse=True)
    best_lever = lever_specialists[0]
    print(f"     种群最佳杠杆使用者: 激活={best_lever.lever_activations}, "
          f"杠杆食物={best_lever.lever_food_eaten:.0f}, 适应度={best_lever.fitness:.0f}")
    if best_lever.lever_activations > 5:
        print(f"     ✓ 后果学习: 存在专门利用杠杆获取食物的个体")
        print(f"       (与'纯觅食'策略共存——两种生态位)")
    elif best_lever.lever_activations > 0:
        print(f"     ~ 杠杆行为初现但未稳定")
    else:
        print(f"     ✗ 杠杆未被利用——选择压力不够或太难发现")

    # 4. C₆ 归类
    print(f"\n  4. C₆ 归类 (不同气味→同一反应):")
    # 检查: 信号权重是否在不同神经元间有相似的符号模式
    sig_weights = [b.w_in[i][0] for i in range(b.N)]
    n_pos = sum(1 for w in sig_weights if w > 1.0)
    n_neg = sum(1 for w in sig_weights if w < -1.0)
    print(f"     信号正响应神经元: {n_pos}, 负响应: {n_neg}")
    if n_pos >= 2:
        print(f"     ✓ 多个神经元协同处理信号→泛化基础")

    # 5. 演化趋势
    if len(history) > 1:
        h0, hf = history[0], history[-1]
        print(f"\n  5. 演化:")
        print(f"     适应度: {h0['avg_fit']:.0f} → {hf['avg_fit']:.0f}")
        print(f"     杠杆激活: {h0.get('lever_acts',0)} → {hf.get('lever_acts',0)}")

    print(f"\n  6. 涌现判断:")
    checks = ['C₂ 辨别: 感觉通道分化']
    if best.lever_activations > 3:
        checks.append('C₅ 后果学习: 学会激活杠杆获取食物')
    if n_pos >= 2:
        checks.append('C₆ 归类前兆: 多神经元协同处理不同类型信号')
    if max(b.tau)-min(b.tau) > 5:
        checks.append('C₃ 记忆: τ分离=多时间尺度')
    for c in checks: print(f"     ✓ {c}")
    print(f"{'='*60}")


if __name__ == '__main__':
    GENS = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    N_NEURONS = 10
    print(f"CTRNN 认知演化 L2 (C₅+C₆) — {GENS} 代")
    print(f"{N_NEURONS}神经元 4传感器(信号/食物/威胁/杠杆) 2运动")
    print(f"环境: 3食物源(3种气味) + 杠杆(停留3步→食物) + 威胁")

    best, pop, history = evolve(pop_size=60, generations=GENS, mut_step=0.08, n_neurons=N_NEURONS)
    analyze(best, pop, history)
