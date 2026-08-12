# Rovelli: Relational Quantum Mechanics

> Rovelli, "Relational Quantum Mechanics" — arXiv:quant-ph/9609002 (1996)
> Drezet, "In defense of RQM" — arXiv:2202.02615 (2022)

## Core Thesis

"The notion of absolute state of a system... is meaningless." States and values of physical quantities are **relational notions** — they exist only relative to a specific observer-system.

## Mathematical Framework

### 1. Measurement as Physical Interaction

Standard von Neumann interaction on joint system:
```
(α|1⟩ + β|2⟩) ⊗ |init⟩ → α|1⟩⊗|O1⟩ + β|2⟩⊗|O2⟩
```

**No collapse**: The joint state is a superposition. O's account says q=1; P (a third observer)'s account says the joint system is still in superposition. **Both are correct** — relative to their respective perspectives.

### 2. The "Has-Measured" Operator M

From P's perspective, whether O has measured S is itself a quantum question:
```
M(|1⟩⊗|O1⟩) = |1⟩⊗|O1⟩
M(|2⟩⊗|O2⟩) = |2⟩⊗|O2⟩  
M(|1⟩⊗|O2⟩) = 0, M(|2⟩⊗|O1⟩) = 0
```

On the post-measurement S-O state, P predicts M=1 with certainty. But if the correlation is imperfect, "there is no half-a-measurement; there is probability one-half that the measurement has been made."

### 3. Relational Variables & Information

The physical content of "q = 1 relative to O" is: relative to P, O's pointer variable is **correlated** with S's q variable. "Correlation is 'information' in Shannon's sense."

**An observer is any physical system with more than one state** — an electron can observe another electron.

### 4. Postulate Reconstruction (Information-Theoretic)

- **Postulate 1 (Limited information)**: Max N bits of relevant information
- **Postulate 2 (Unlimited information)**: New information always acquirable
- **Postulate 3 (Superposition)**: Transition probabilities obey interference

From these, the full Hilbert space formalism (Born rule, Schrödinger dynamics) is reconstructed.

### 5. Reduced Density Matrix Formulation (2022)

The fundamental object relative to observer O:
```
ρ_S^(red) = Tr_O[ρ_OS] = Tr_O[|Ψ_OS⟩⟨Ψ_OS|]
```

This is **basis-independent** — resolves the preferred-basis dilemma. All physical predictions are contained in Tr_O.

### Key Insight for Our Question

In RQM:
- **Observation = correlation between system states**
- **Any physical system is an observer** — consciousness is irrelevant
- **Values are always relative** — no absolute "measurement outcome" exists
- The mathematical definition: **the reduced density matrix ρ_S^(red) = Tr_O[ρ_OS] captures all information S has about O (and vice versa)**
- "Observer" means "reference system relative to which properties are defined"
