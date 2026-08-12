# Zurek: Decoherence, Einselection, and Quantum Darwinism

> arXiv:quant-ph/0105127 (2001), arXiv:0707.2832 (2007), arXiv:1807.02092 (2018)

## Core Mathematical Framework

### 1. The Measurement Problem Structure

Pre-measurement via unitary evolution:
```
|Ψ_t⟩ = Σ_i a_i |s_i⟩|A_i⟩
```
This state suffers "basis ambiguity" — the same state can be rewritten in any basis.

### 2. Einselection (Environment-Induced Superselection)

The S-A-E (System-Apparatus-Environment) triangle resolves the basis ambiguity.

System-Apparatus-Environment interaction Hamiltonian:
```
H_AE = (|⇑⟩⟨⇑| − |⇓⟩⟨⇓|) ⊗ Σ_k g_k (|↑⟩⟨↑| − |↓⟩⟨↓|)_k
```

The **pointer basis** is selected by the commutator condition:
```
[H_AE, Â] = 0
```
i.e., the pointer observable is a constant of motion under the system-environment interaction.

Once the environment records apparatus pointer states with ⟨ε₀|ε₁⟩ = 0, the reduced density matrix ρ_AS becomes diagonal — containing "only classical correlations."

Off-diagonal coherence decays exponentially:
```
|r(t)|² ≈ 2⁻ᴺ ∏_k[1 + (|αₖ|² − |βₖ|²)²]
```
Suppressed exponentially in environment size N.

### 3. Predictability Sieve

Einselected states are those that maximize predictability under environmental monitoring. Not simply the eigenbasis of instantaneous reduced density matrix — it's a dynamical stability criterion.

### 4. Envariance (Environment-Assisted Invariance)

When a transformation U_S on the system can be undone by U_E on the environment alone:
```
U_E ⊗ U_S |ψ_SE⟩ = |ψ_SE⟩
```
The joint state is unchanged, proving the observer's ignorance of the system's state — even with perfect knowledge of the joint state. This derives Born's rule without assuming it.

### 5. Quantum Darwinism

The environment acts as a witness, redundantly recording pointer states. Fragments of the environment F contain information about the system S:
```
I(S:F) = H(S) + H(F) − H(S,F)
```
Redundancy R = number of independent fragments that supply information about S above threshold.

High redundancy ⇒ objectivity ⇒ classical reality emerges without observers.

"Observers intercept small fragments of the environment to learn about the system without perturbing it."

### Key Insight for Our Question

In Zurek's framework, observation decomposes into:
1. **Einselection**: environment selects the pointer basis (what CAN be observed)
2. **Redundant recording**: environment proliferates copies of pointer state information
3. **Information access**: any physical system that intercepts a fragment of the environment "observes"

**The observer is demoted to any physical system that accesses redundantly stored environmental information.** No consciousness required.
