# QBism: Observation as Personal Bayesian Update

> Fuchs, "QBism, the Perimeter of Quantum Bayesianism" — arXiv:1003.5209
> Fuchs & Schack, "Quantum-Bayesian Coherence" — arXiv:1301.3274 (Rev. Mod. Phys. 85, 1693)
> DeBrota, Fuchs & Schack, "Quantum Dynamics Happens Only on Paper" — arXiv:2312.14112

## Core Thesis

**"Quantum states do not exist"** (as ontic entities). A quantum state is an agent's encoding of her own personal expectations about "the consequences (for me) of my actions upon the physical system."

## Mathematical Framework

### 1. Quantum States = Beliefs

Quantum state |ψ⟩ ↔ personalist Bayesian probability assignment.
The Bloch vector (expectations of σ_x, σ_y, σ_z) determines a unique density operator ρ — just as a complete set of probability judgments determines a unique quantum state.

### 2. Measurement = Action-Consequence

An agent acts on a system (via a POVM) and the system responds by selecting one POVM element as the agent's **experience**. Outcomes are "moments of creation" — Wheeler: "Each elementary quantum phenomenon is an elementary act of 'fact creation.'"

The agent/world split is a **conceptual choice**, not a fact about reality.

### 3. Born Rule as Normative Consistency

Via SIC (Symmetric Informationally Complete) representations:
```
Q(D_j) = (d+1) Σ_i P(H_i) P(D_j|H_i) − 1
```

Where P(H_i) = probabilities for a fiducial SIC measurement ("in the sky"), P(D_j|H_i) = conditionals for target measurement ("on the ground").

The Born rule is **not a physical law** — it's an "addition to Bayesian probability," a normative rule guiding agent behavior. Analogous to the Ten Commandments, not Maxwell's equations.

### 4. State Update as Belief Revision

After measurement outcome x:
```
ρ → ρ_x = ℐ(x)ρ / Tr[ℐ(x)ρ]  (generalized Lüders rule)
```

This is NOT a physical collapse — it's a Bayesian update of the agent's beliefs given new experience.

### 5. Dynamics as Reflection Principle (2023)

DeBrota, Fuchs, Schack (arXiv:2312.14112): **Quantum dynamics itself** follows from van Fraassen's Reflection Principle — an agent's assignment of dynamics represents her belief that a measurement action she is contemplating would not change her current odds for future gambles. This yields CPTP maps and accounts for decoherence **without invoking an environment**.

### Key Insight for Our Question

In QBism:
- **There is no such thing as "observation" without an observer** — observation IS the agent's experience
- **Consciousness is central**: measurement outcomes are personal experiences, not objective events
- **Mathematically**: observation = an agent applying a POVM, receiving an outcome x, and updating her beliefs via the generalized Lüders rule
- **The mathematical apparatus (Hilbert space, POVM, Kraus operators) does not describe reality** — it constrains the agent's betting behavior
