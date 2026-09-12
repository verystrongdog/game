# Free Energy Principle & Active Inference: Consciousness as Self-Evidencing

> Friston, "A free energy principle for a particular physics" — arXiv:1906.10184, 2019
> Wiese & Friston, "The neural correlates of consciousness under the free energy principle" — Phil Mind Sci 2, 2021
> Parr, Pezzulo & Friston, "Active Inference: The Free Energy Principle in Mind, Brain, and Behavior" — MIT Press, 2022

## Core Claim

The Free Energy Principle (FEP) is NOT itself a theory of consciousness — it applies to ANY self-organizing system (including bacteria). However, it provides necessary constraints on what it means to BE (rather than merely simulate) a conscious system, and suggests that consciousness emerges from having a **generative self-model** engaged in an active inference loop.

## I. The Physics: Non-Equilibrium Steady State (NESS)

### 1.1 Langevin Dynamics
```
ẋ(τ) = f(x, τ) + ω
```
- x(τ): slowly-changing macroscopic state variables
- f: state-dependent flow (deterministic dynamics)
- ω: Gaussian noise, mean 0, covariance 2Γ (Γ = fluctuation amplitude)

### 1.2 Fokker-Planck Equation → NESS Density
```
ṗ(x, τ) = ∇·(Γ∇ − f) p(x, τ) = 0   (at NESS)
```
The NESS density defines **surprisal** (self-information):
```
𝔍(x) = −ln p(x)
```

### 1.3 Flow Decomposition
```
f(x) = (Q(x) − Γ)·∇𝔍(x) = (Γ − Q(x))·∇ ln p(x)
```
- (Γ − Q)·∇𝔍: gradient flow on surprisal (minimizes surprise on average)
- Q: solenoidal (divergence-free) coupling — non-gradient, circulating component
- **Constraint**: Direct solenoidal coupling between internal and external states is precluded

## II. Markov Blanket → Bayesian Mechanics

### 2.1 Partition
```
x = {η, s, a, μ}
η = external states (environment)
s = sensory states  } blanket states
a = active states    }
μ = internal states
```

The Markov blanket {s, a} renders internal states μ **conditionally independent** of external states η: `p(μ|s, a, η) = p(μ|s, a)`.

### 2.2 Autonomous Flow
For autonomous (internal + active) states α = {a, μ}:
```
f_α(π) = (Q_αα − Γ_αα) ∇_α 𝔍(π)
```
where π = {s, α} are the **particular states** (blanket + autonomous).

### 2.3 The Variational Free Energy Approximation
If internal states μ encode (on average) an approximate posterior q_μ(η) over external states:
```
f_α(π) ≈ (Q_αα − Γ_αα) ∇_α F(π)
```

### 2.4 Variational Free Energy — Three Equivalent Forms
```
F(π) = E_q[𝔍(η, π)] − H[q_μ(η)]                              (1)
     = 𝔍(π) + D_KL[q_μ(η) ‖ p(η|π)]                          (2)
     = E_q[𝔍(π|η)] + D_KL[q_μ(η) ‖ p(η)]                     (3)  ← accuracy − complexity
     ≥ 𝔍(π)                                                     (upper bound on surprisal)
```

**Form (3) — Accuracy minus Complexity:**
- Accuracy: −E_q[𝔍(π|η)] — how well does the model predict sensory data?
- Complexity: D_KL[q_μ(η) ‖ p(η)] — how much must beliefs change to accommodate the data?
- **Negative free energy = lower bound on log model evidence (ELBO)**

### 2.5 Active Inference
Action DOES NOT maximize reward. Instead, action samples sensory data to confirm the agent's prior beliefs:
- **Perception**: update internal model to fit sensory data
- **Action**: change the world to fit the model's predictions
- Both are unified in a single free-energy-minimizing process

**Epistemic drives** (information-seeking): agents act to reduce uncertainty in their generative model — the computational basis of curiosity and exploration.

## III. FEP Constraints on Consciousness (Wiese & Friston 2021)

### 3.1 NCC (neural correlates) vs CCC (computational correlates)

**Two information geometries:**
- **Intrinsic** (probabilities OF neural states, NESS density): movements HERE are Neural Correlates of Consciousness (NCCs). Existing measures (LZ complexity, spectral exponent, synchrony entropy) track this.
- **Extrinsic** (probabilities ENCODED BY neural states, Bayesian beliefs): movements HERE are Computational Correlates of Consciousness (CCCs). Proposed measure: **information length** — distance traveled on the extrinsic manifold, measured by the Fisher information metric.

### 3.2 Necessary, Not Sufficient

CCCs derived from FEP are **necessary conditions** for consciousness, enabling inferences about ABSENCE of consciousness (e.g., "islands of awareness" — conscious systems with no sensory input or motor output). Free-energy minimization is trivially necessary for any persisting system.

### 3.3 The Self-Model Criterion

In Friston's account, consciousness requires a **generative model that includes the system itself** as a cause of its sensory observations — a self-model maintained through the action-perception cycle. Consciousness = consequence of having a self-model within an active inference loop.

### 3.4 Simulation ≠ Instantiation

A digital simulation on a von Neumann machine does NOT instantiate a conscious system, because its internal states (CPU registers) are not the physical states of a system whose continued existence depends on those computations. The "right kind of system" is defined by whether the computational description's states ARE the physical system's own states, not by substrate (silicon vs. carbon).

### 3.5 Accuracy-Complexity Balance During Disconnection

When disconnected (dreaming, islands of awareness), the same gradient flow `f_α(π) ≈ (Q_αα − Γ_αα)∇_αF(π)` is "mainly driven by the complexity part" — the system minimizes complexity. This dissolves the apparent tension with high measured LZ complexity during conscious states: "complexity is always chasing accuracy" — what is minimized is their difference.

## IV. Mathematical Limitations for Defining Subjective Consciousness

### What FEP CAN mathematically define:
- **Self-evidencing**: a system's autonomous dynamics minimize variational free energy
- **The Markov blanket**: the statistical boundary separating self from world
- **Generative self-models**: encoded beliefs about the causes of sensory inputs
- **Simulation vs. instantiation**: a formal criterion based on physical identity of computational states

### What FEP CANNOT mathematically define:
- **When self-evidencing becomes self-awareness**: FEP applies to bacteria — it doesn't specify the threshold where free energy minimization produces subjective experience
- **The qualitative character**: like IIT, the FEP framework describes necessary conditions but doesn't derive specific qualia
- **The "Hard Problem" bridge**: FEP explains WHY a system with a Markov blanket MUST act AS IF it has beliefs and preferences — but doesn't explain why this AS-IF should be accompanied by felt experience

### The Critical Gap:
FEP shows that any persisting system **behaves as if** it performs Bayesian inference about its world. But behavior-as-if is not phenomenology. The theory provides constraints on the *physical* side (NESS, Markov blanket, free energy gradients) and the *computational* side (encoded beliefs, active inference), but the link between the computational self-model and subjective experience remains a postulate, not a theorem.

---
*Created: 2026-08-11 | Source: arXiv:1906.10184 + Phil Mind Sci 2 (2021)*
