# Consistent Histories: Observation without Observers

> Griffiths (1984), Omnès (1988-), Gell-Mann & Hartle (1990-)
> Stanford Encyclopedia of Philosophy: "Consistent Histories Approach to Quantum Mechanics"

## Core Thesis

Eliminate the fundamental role of measurements and observers in quantum mechanics. Instead: study **quantum histories** — sequences of events at different times — and assign probabilities to them directly, without invoking an external observer. Originally motivated by quantum cosmology (the universe as a whole has no external observer).

## Mathematical Framework

### 1. Events and Histories

An **event** at time t_k is a projection operator P_k^{α_k}. A **history** is a chain:
```
Y^α = P_0^{α_0} ⊙ P_1^{α_1} ⊙ ... ⊙ P_f^{α_f}
```

Each history represents a proposition: "the system was in subspace P_0 at t_0, then in P_1 at t_1, ..., then in P_f at t_f."

### 2. Chain Operator

For a closed system with unitary evolution U(t_j, t_k):
```
K(Y^α) = P_f^{α_f} U(t_f, t_{f-1}) P_{f-1}^{α_{f-1}} U(t_{f-1}, t_{f-2}) ... P_1^{α_1} U(t_1, t_0) P_0^{α_0}
```

### 3. Consistency Condition

A family of histories is **consistent** iff:
```
Tr[K(Y^α) K(Y^β)^†] = 0   for α ≠ β
```

This replaces the measurement postulate. When satisfied, probabilities are given by the **generalized Born rule**:
```
Pr(Y^α) = Tr[K(Y^α) K(Y^α)^†]
```

For a pure initial state |ψ₀⟩, chain kets are |Ψ^α⟩ = K(Y^α)|ψ₀⟩, and consistency is ⟨Ψ^α|Ψ^β⟩ = 0.

### 4. Frameworks (Single Framework Rule)

A **framework** = a projective decomposition of the identity (PDI) on the history space.

**Single Framework Rule**: Quantum reasoning must be confined to a single framework. Incompatible frameworks cannot be combined.

Four principles:
- **R1 (Liberty)**: Any number of frameworks may be used
- **R2 (Equality)**: No framework is more fundamental
- **R3 (Incompatibility)**: Incompatible frameworks are never combined
- **R4 (Utility)**: Some frameworks are more useful for particular questions

Classical **unicity** (one true state of affairs) is replaced by quantum **pluricity**.

### 5. How Measurement Is Replaced

A "measurement" = a unitary interaction between system and apparatus, analyzed within a chosen consistent family. The experimenter's knowledge = conditional probabilities within that family:
```
Pr(R^k_2 | [s^j_1]) = Pr([s^j_1] | R^k_2) = δ_jk
```

No wavefunction collapse — it becomes "a legitimate calculational procedure" in certain limits.

### 6. Observer Demotion (IGUSes)

Gell-Mann & Hartle: **IGUSes** (Information Gathering and Utilizing Systems) — physical systems within the universe, described quasiclassically, that "evolve to exploit" a particular quasiclassical domain. Observers occupy no special role in the laws of physics.

### Key Insight for Our Question

In Consistent Histories:
- **Observation is framework-relative, not world-relative** — a measurement outcome has meaning only within a chosen framework
- **No observer is required** — the mathematical structure alone determines which observations are definable and their probabilities
- **Mathematically**: an observation = the selection of a consistent family of histories + computation of conditional probabilities within it
- **Consciousness is irrelevant**: the universe computes its own histories
- **The observer does not collapse the wavefunction** — consistency conditions do the work of ensuring classical probability calculus
