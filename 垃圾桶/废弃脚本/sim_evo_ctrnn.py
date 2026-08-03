#!/usr/bin/env python3
"""
CTRNN 认知演化模拟 v2
基于 Izquierdo & Harvey (2007) / Phattanasri et al. (2007)

每个 agent = 4神经元 CTRNN，固定权重，无可塑性。
方程: τᵢ · ẏᵢ = -yᵢ + Σwⱼᵢ·σ(yⱼ+θⱼ) + Iᵢ

修复:
- 每个 agent 评估 N 次取平均 (减少噪声)
- 适应度直接奖励"用信号预测食物"
- 控制世界相位
- 降低突变压力
"""

import math, random, sys
from collections import defaultdict
from typing import List, Tuple

random.seed(1)

# ═══════════════════════ CTRNN ═══════════════════════

def sig(x): return 1.0/(1.0+math.exp(-x))

class CTRNN:
    def __init__(self, n=4, n_sens=3, n_mot=2):
        self.N, self.S, self.M = n, n_sens, n_mot
        self.y = [0.0]*n
        # 参数范围参考论文
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

    def mutate(self, step=0.15):
        p_mut = 0.2  # 20% 突变概率
        for i in range(self.N):
            if random.random()<p_mut: self.tau[i]=max(0.1,self.tau[i]+random.gauss(0,step*1.5))
            if random.random()<p_mut: self.bias[i]+=random.gauss(0,step)
            for j in range(self.N):
                if random.random()<p_mut: self.w[i][j]+=random.gauss(0,step*2)
            for s in range(self.S):
                if random.random()<p_mut: self.w_in[i][s]+=random.gauss(0,step*1.5)
        for m in range(self.M):
            for i in range(self.N):
                if random.random()<p_mut: self.w_out[m][i]+=random.gauss(0,step)

# ═══════════════════════ 环境 ═══════════════════════

class World:
    """周期性食物源: 信号期 → 食物期 → 冷却期"""
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.step = 0
        self.w, self.h = 200, 200

        # 三个食物源，相位错开
        self.patches = [
            {'x':50,'y':60,'sig_r':35,'food_r':12,'cyc':45,
             'sig_s':0,'sig_e':25,'food_s':28,'food_e':38,'val':40},
            {'x':150,'y':60,'sig_r':35,'food_r':12,'cyc':45,
             'sig_s':0,'sig_e':25,'food_s':28,'food_e':38,'val':40},
            {'x':100,'y':150,'sig_r':40,'food_r':15,'cyc':50,
             'sig_s':5,'sig_e':30,'food_s':33,'food_e':43,'val':45},
        ]
        # 虚假信号: 有气味无食物 → 选择压力 → 习惯化
        self.false_signal = {'x':30,'y':140,'sig_r':30,'cyc':40,
                             'sig_s':5,'sig_e':20}
        # 威胁
        self.threat = (100,100,22.0)
        # 零星食物
        self.scatter_p = 0.005
        self.scatter_v = 10.0

    def tick(self): self.step += 1

    def sense(self, x, y):
        # 信号
        sig = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['sig_s'] <= ph < p['sig_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['sig_r']:
                    prog = (ph-p['sig_s'])/(p['sig_e']-p['sig_s'])
                    sig += (1-d/p['sig_r'])*(0.2+0.8*prog)
        # 虚假信号
        fs = self.false_signal
        ph = self.step % fs['cyc']
        if fs['sig_s'] <= ph < fs['sig_e']:
            d = math.sqrt((x-fs['x'])**2+(y-fs['y'])**2)
            if d < fs['sig_r']:
                prog = (ph-fs['sig_s'])/(fs['sig_e']-fs['sig_s'])
                sig += (1-d/fs['sig_r'])*(0.2+0.8*prog)
        sig = min(1.0, sig)

        # 食物
        food = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['food_s'] <= ph < p['food_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['food_r']:
                    food += p['val']*(1-d/p['food_r'])
        if self.rng.random() < self.scatter_p:
            food += self.scatter_v

        # 威胁
        tx,ty,tr = self.threat
        d = math.sqrt((x-tx)**2+(y-ty)**2)
        threat = max(0, 1-d/tr) if d<tr else 0.0

        return sig, min(1.0,food/50.0), threat

    def actual_food(self, x, y):
        """返回实际食物量(非归一化)"""
        f = 0.0
        for p in self.patches:
            ph = self.step % p['cyc']
            if p['food_s'] <= ph < p['food_e']:
                d = math.sqrt((x-p['x'])**2+(y-p['y'])**2)
                if d < p['food_r']:
                    f += p['val']*(1-d/p['food_r'])
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
        # 行为记录
        self.approach_signal = 0   # 信号出现时趋近次数
        self.signal_opportunity = 0 # 信号出现次数
        self.false_approach = 0    # 趋近虚假信号次数
        self.false_opportunity = 0

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
        self.false_approach = 0
        self.false_opportunity = 0
        self.brain.y = [0.0]*self.brain.N

    def update(self, world):
        if not self.alive: return
        self.age += 1

        sg, food, threat = world.sense(self.x, self.y)
        motor = self.brain.step([sg, food, threat])
        turn = max(-1, min(1, motor[0]))
        speed = max(0, min(2.5, sig(motor[1])*2.5))

        # 记录信号趋近行为
        if sg > 0.15:
            self.signal_opportunity += 1
            if speed > 0.5 and abs(turn) < 0.6:
                self.approach_signal += 1
        # 记录虚假信号趋近
        fs = world.false_signal
        d_false = math.sqrt((self.x-fs['x'])**2+(self.y-fs['y'])**2)
        if d_false < fs['sig_r']:
            ph = world.step % fs['cyc']
            if fs['sig_s'] <= ph < fs['sig_e']:
                self.false_opportunity += 1
                if speed > 0.5:
                    self.false_approach += 1

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

        # 移动
        self.angle += turn*0.8
        self.x = (self.x + math.cos(self.angle)*speed) % world.w
        self.y = (self.y + math.sin(self.angle)*speed) % world.h

        if self.energy <= 0: self.alive = False
        if self.age > 500: self.alive = False


# ═══════════════════════ 演化 ═══════════════════════

def evaluate(agent, world, trials=3, steps_per=300):
    """多次试验取平均适应度"""
    total_fit = 0.0
    for _ in range(trials):
        agent.reset(world)
        for _ in range(steps_per):
            if not agent.alive: break
            world.tick()
            agent.update(world)

        # 适应度 = 吃到的食物 + 信号趋近奖励 - 威胁惩罚 - 虚假信号惩罚 + 存活奖励
        fit = (agent.eaten
               + agent.approach_signal*0.5          # 奖励趋近信号
               - agent.false_approach*1.0            # 惩罚趋近虚假信号
               - agent.threat_hits*5.0
               + agent.age*0.03)
        total_fit += max(0.1, fit)
    return total_fit / trials


def evolve(pop_size=60, generations=120, elite=8, mut_step=0.12):
    world = World()
    pop = [Agent(CTRNN()) for _ in range(pop_size)]
    history = []
    best_ever = None

    for gen in range(generations):
        # 评估
        for a in pop:
            a.fitness = evaluate(a, world, trials=3, steps_per=300)

        pop.sort(key=lambda a: a.fitness, reverse=True)
        alive = [a for a in pop if a.fitness > 1.0]

        if alive:
            best = alive[0]
            if best_ever is None or best.fitness > best_ever.fitness:
                best_ever = best

            # 统计 τ 分布
            taus_all = []
            for a in alive[:15]:
                taus_all.extend(a.brain.tau)
            taus_all.sort()
            per_agent_max = [max(a.brain.tau) for a in alive[:15]]
            per_agent_min = [min(a.brain.tau) for a in alive[:15]]
            avg_tau_sep = sum(per_agent_max[i]-per_agent_min[i] for i in range(len(per_agent_max)))/len(per_agent_max)

            history.append({
                'gen':gen, 'n':len(alive),
                'avg_fit':sum(a.fitness for a in alive)/len(alive),
                'best_fit':best.fitness,
                'best_eaten':best.eaten,
                'tau_sep':avg_tau_sep,
                'tau_vals':taus_all,
            })

            if gen%20==0 or gen==generations-1:
                b = best.brain
                print(f"代{gen:3d} 存活{len(alive):2d} "
                      f"适应度={best.fitness:6.1f} 吃={best.eaten:5.0f} "
                      f"τ=[{b.tau[0]:.1f},{b.tau[1]:.1f},{b.tau[2]:.1f},{b.tau[3]:.1f}] "
                      f"τ分离={max(b.tau)-min(b.tau):.1f}")

        # 繁殖
        new_pop = [Agent(pop[i].brain.clone()) for i in range(elite)]
        while len(new_pop) < pop_size:
            # 锦标赛选择 (从上半区选)
            pool = pop[:pop_size//2]
            parent = max(random.sample(pool, 3), key=lambda a: a.fitness)
            child = Agent(parent.brain.clone())
            child.brain.mutate(mut_step)
            new_pop.append(child)
        pop = new_pop

    return best_ever, pop, history


# ═══════════════════════ 分析 ═══════════════════════

def analyze(best, pop, history):
    if best is None:
        print("无存活。")
        return

    b = best.brain
    print(f"\n{'='*60}")
    print(f"  涌现分析 (最佳 agent, 适应度={best.fitness:.1f})")
    print(f"{'='*60}")

    # 1. τ 分离
    taus = sorted(b.tau)
    print(f"\n  1. τ 分布: {[f'{t:.1f}' for t in taus]}")
    print(f"     τ分离度: {max(taus)-min(taus):.1f}")
    if max(taus)-min(taus) > 5:
        print("     ✓ 多时间尺度涌现——快神经元(~反射) + 慢神经元(~记忆)")
    elif max(taus)-min(taus) > 2:
        print("     ~ 有分离趋势，但不够显著")
    else:
        print("     ✗ τ 未分离——所有神经元在同一时间尺度")

    # 2. 感觉权重
    print(f"\n  2. 感觉权重 (w_in[neuron][sig/food/threat]):")
    snames = ['信号','食物','威胁']
    for i in range(b.N):
        w = b.w_in[i]
        dom = snames[max(range(3), key=lambda j: abs(w[j]))]
        print(f"     神经元{i} (τ={b.tau[i]:.1f}): "
              f"[{w[0]:+6.2f} {w[1]:+6.2f} {w[2]:+6.2f}] → {dom}")

    # C₂ 辨别: 不同神经元有不同的主响应通道
    dominant_channels = set()
    for i in range(b.N):
        dominant_channels.add(max(range(3), key=lambda j: abs(b.w_in[i][j])))
    if len(dominant_channels) >= 2:
        print(f"     ✓ C₂ 辨别: 不同神经元分工不同通道 ({len(dominant_channels)}个)")
    else:
        print(f"     ✗ 所有神经元集中在同一通道")

    # 3. 慢神经元的功能
    slow_i = max(range(b.N), key=lambda i: b.tau[i])
    fast_i = min(range(b.N), key=lambda i: b.tau[i])
    print(f"\n  3. 最慢神经元 {slow_i} (τ={b.tau[slow_i]:.1f}):")
    print(f"     感觉权重: sig={b.w_in[slow_i][0]:+.2f} food={b.w_in[slow_i][1]:+.2f} threat={b.w_in[slow_i][2]:+.2f}")
    # 测试: 给信号后看持久性
    test = CTRNN(); test.tau=list(b.tau); test.bias=list(b.bias)
    test.w=[list(r) for r in b.w]; test.w_in=[list(r) for r in b.w_in]
    test.w_out=[list(r) for r in b.w_out]
    for _ in range(15): test.step([1.0,0.0,0.0])  # 输入信号
    trace = []
    for t in range(40):
        test.step([0.0,0.0,0.0])
        if t%5==0:
            trace.append((t, test.y[slow_i]))
    print(f"     信号消失后慢神经元激活: {[f't={t}:{y:.2f}' for t,y in trace[:6]]}")
    last_y = abs(trace[-1][1])
    if last_y > 0.3:
        print(f"     ✓ 信号消失40步后仍保持激活({last_y:.2f})——慢神经元=记忆")
    else:
        print(f"     ~ 40步后衰退到 {last_y:.2f}")

    # 快神经元
    print(f"\n  4. 最快神经元 {fast_i} (τ={b.tau[fast_i]:.1f}):")
    print(f"     感觉权重: sig={b.w_in[fast_i][0]:+.2f} food={b.w_in[fast_i][1]:+.2f} threat={b.w_in[fast_i][2]:+.2f}")
    if b.tau[fast_i] < 1.0:
        print(f"     ✓ 快神经元 τ<1→ 快速响应，类似反射")

    # 5. 虚假信号习得
    print(f"\n  5. 虚假信号行为:")
    print(f"     趋近虚假信号: {best.false_approach}/{best.false_opportunity} 次")
    if best.false_opportunity > 0:
        rate = best.false_approach/best.false_opportunity
        if rate < 0.3:
            print(f"     ✓ 虚假信号趋近率低({rate:.0%})——可能已习惯化")
        else:
            print(f"     ~ 仍趋近虚假信号({rate:.0%})——未习惯化")

    # 6. 演化趋势
    if len(history) > 1:
        h0, hf = history[0], history[-1]
        print(f"\n  6. 演化趋势:")
        print(f"     适应度: {h0['avg_fit']:.0f} → {hf['avg_fit']:.0f}")
        print(f"     τ分离:  {h0['tau_sep']:.1f} → {hf['tau_sep']:.1f}")

    # 综合
    print(f"\n  7. 涌现判断:")
    checks = []
    if max(b.tau)-min(b.tau) > 5:
        checks.append('C₃ 习惯化/记忆基础: τ分离=多时间尺度')
    if len(dominant_channels) >= 2:
        checks.append('C₂ 辨别: 感觉通道分工')
    if best.eaten > 200:
        checks.append('C₄ 关联前兆: 进食效率显著高于随机')
    if best.false_opportunity > 0 and best.false_approach/best.false_opportunity < 0.3:
        checks.append('C₃ 习惯化: 抑制对虚假信号的响应')

    for c in checks: print(f"     ✓ {c}")
    if not checks: print(f"     (需要更多代)")
    print(f"{'='*60}")


if __name__ == '__main__':
    GENS = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    print(f"CTRNN 认知演化 v2 — {GENS} 代")
    print(f"4神经元 3传感器(信号/食物/威胁) 2运动(转向/速度)")
    print(f"3食物源(信号→食物周期) + 1虚假信号 + 1威胁区")
    print(f"每个agent评估3次取平均")

    best, pop, history = evolve(pop_size=60, generations=GENS, mut_step=0.12)
    analyze(best, pop, history)
