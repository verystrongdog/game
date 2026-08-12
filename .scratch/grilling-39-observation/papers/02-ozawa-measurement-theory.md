# Ozawa: Quantum Measurement Theory — POVM, Instruments, Complete Positivity

> arXiv:2110.03219 — "Quantum Measurement Theory for Systems with Finite Dimensional State Spaces"

## Formal Axiomatization of Measurement

### 1. From von Neumann to POVM

Von Neumann's original axioms assumed **repeatability**: measuring twice gives same result. This fails for continuous observables (Arveson's theorem).

Davies & Lewis (1970) abandoned repeatability → **instruments**.

### 2. Theorem 1 — Derivation of POVM

From the mixing law (M2′: output probability is affine in the input state):

**Theorem**: There exists a **unique POVM** Π such that:
```
Pr{x = x ∥ ρ} = Tr[Π(x)ρ]
```
POVM = map x ↦ Π(x) with Π(x) ≥ 0, Σ_x Π(x) = I.

### 3. Theorem 2 — Derivation of Instruments

An **instrument** ℐ(x) is defined by:
```
ℐ(x)ρ = Pr{x=x ∥ ρ} · ρ_{x=x}
```

**Theorem**: From the mixing law for joint output probabilities (M2), every apparatus has a unique Davies-Lewis instrument satisfying:
- Pr{x=x ∥ ρ} = Tr[ℐ(x)ρ]
- ρ_{x=x} = ℐ(x)ρ / Tr[ℐ(x)ρ]
- Joint distribution: Pr{x=x, y=y ∥ ρ} = Tr[ℐ_y(y)ℐ_x(x)ρ]

The POVM is recovered as Π(x) = ℐ(x)*I.

### 4. Complete Positivity & Realization Theorem

**Axiom M3 (Extendability)**: An apparatus measuring S makes no measurement on a remote system S′.
→ Forces **complete positivity (CP)** of the instrument.

**Realization Theorem**: Every CP instrument has an **indirect measurement model**:
- (𝒦, σ, U, M): probe Hilbert space 𝒦, probe state σ, unitary U on ℋ⊗𝒦, meter observable M on 𝒦
- ℐ(x)ρ = Tr_𝒦{[I⊗P^M(x)] U(ρ⊗σ) U†}

**Conclusion**: **physically realizable measurements ⇔ CP instruments**

### 5. Axiom Q5 — General Measurement Axiom

Every apparatus corresponds uniquely to a CP instrument ℐ. This completes von Neumann's axiomatization.

### 6. Kraus Form (Measurement Operators)

Every CP instrument has measurement operators {M_xj}:
```
ℐ(x)ρ = Σ_j M_xj ρ M_xj†
Π(x) = Σ_j M_xj† M_xj
Σ_xj M_xj† M_xj = I
```

### 7. Generalized Wigner Formula

For arbitrary sequential measurements at t₁<...<t_n:
```
Pr{x₁=x₁,...,x_n=x_n ∥ ρ} = Tr[ℐ_n(x_n)α(t_n−t_{n-1})⋯ℐ₂(x₂)α(t₂−t₁)ℐ₁(x₁)α(t₁)ρ]
```

### Key Insight for Our Question

This is the **most mathematically rigorous** definition of measurement. In this framework:
- **Measurement** = any CP instrument ℐ(x) acting on a Hilbert space
- **Observation** = a specific outcome x of this instrument
- The formalism is **observer-agnostic**: any physical system implementing a CP instrument performs a measurement
- **Consciousness plays no role** — measurement is a mathematical property of the CP map
- The formalism covers **all** physically realizable measurements, not just projective ones
