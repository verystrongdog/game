# The Computational Complexity Critique: Φ and the Unconscious Expander

> Aaronson, "Why I Am Not An Integrated Information Theorist (or, The Unconscious Expander)" — Shtetl-Optimized blog, May 2014
> Aaronson, "Giulio Tononi and Me: A Phi-nal Exchange" — May 2014
> Aaronson, "Why Philosophers Should Care About Computational Complexity" — arXiv:1108.1791

## Core Claim

Integrated Information Theory's Φ — proposed as a mathematical measure of consciousness — is not even CLOSE to being a sufficient condition for consciousness. Trivial systems (error-correcting codes, expander graphs) can have Φ values exceeding any plausible human-brain bound, while doing nothing remotely intelligent or conscious. The more fundamental point: **information integration is computationally cheap**, not a hallmark of the kind of complexity that might underwrite consciousness.

## I. Formalization of Φ (Aaronson's Reconstruction)

### 1.1 Setup
- A discrete dynamical system f with state x over alphabet S
- n binary variables; bipartition (A, B)

### 1.2 Effective Information
```
EI(A → B) = I(A_out; B_in)
```
The mutual information between A's outputs and B's inputs, when A's inputs are drawn uniformly at random and B's inputs are fixed to their values in the current state x.

### 1.3 Integrated Information (per bipartition)
```
Φ(A, B) = EI(A → B) + EI(B → A)
```
Normalized version: divide by min{|A|, |B|}. Final Φ = minimum over all bipartitions.

## II. The Vandermonde Counterexample

### 2.1 Setup
- State space: S = F_p (finite field of prime order p, p >> n)
- Update function: f(x) = Vx where V is an n×n Vandermonde matrix

### 2.2 The Vandermonde Property
Every square submatrix of V is full-rank. This means every submatrix preserves ALL the information it's possible to preserve about the input it acts on. Consequently:

**For EVERY bipartition (A, B):**
- EI(A → B) = EI(B → A) = min{|A|, |B|} log₂ p
- Normalized Φ(A, B) / min{|A|, |B|} = 2 log₂ p — the MAXIMUM possible value

**Every partition gives the same normalized Φ.**

### 2.3 First Problem: Tie-Breaking Ambiguity
Since every partition ties for the minimum normalized Φ, the unnormalized Φ ranges from 2 log₂ p (the trivial partition) up to (n/2) log₂ p (balanced partitions). Tononi never specifies how to break ties. Φ "is simply undefined" — the final value depends on an arbitrary choice among partitions.

### 2.4 The "Ironic Little Hack"
To force a well-defined Φ, replace V with W — the first n/2 rows of the Vandermonde matrix, each repeated twice. The balanced partition now becomes essentially the unique minimizer, giving:
```
Φ = (n/2) log₂ p
```
This is "quite a large value" — representing integration of half the system's total information content. **The irony**: deliberate information was DECREASED (by repeating rows) in order to INCREASE the final Φ that Tononi's prescription returns.

### 2.5 Why This Should Be Embarrassing
The map f(x) = Vx is simply **polynomial evaluation**: mapping the coefficients of a degree-(n-1) polynomial to its values at n points. This is exactly a **Reed-Solomon error-correcting code** — employed in CDs, DVDs, and QR codes.

> With n ≈ 10^14, easily built using existing computers, Φ would exceed any plausible bound for the human brain, yet the system does nothing remotely intelligent, let alone conscious.

## III. The Expander Graph Argument

### 3.1 Objection: "Real Circuits Are Sparse"
One might object that a real neural circuit has each neuron connected to only a few others (degree ~O(1)), so Φ would drop dramatically.

### 3.2 Answer: LDPC Codes + Expander Graphs
The same integration can be achieved with SPARSE computations using bipartite expander graphs — where every k left vertices connect to at least min{(1+ε)k, n} right vertices — with constant degree (e.g., 3 neighbors per node), built randomly or by explicit construction.

- **Expander graphs appear constantly in CS**: error-correcting codes (LDPC), pseudorandom generators, derandomization, network design
- **None of these applications has anything to do with consciousness**
- An expander's Φ grows linearly with n while each element connects to only O(1) others

### 3.3 The Title's Meaning
> "The brain might be an expander, but not every expander is a brain."

Information integration is computationally mundane. It's not the "secret sauce" that distinguishes consciousness from non-consciousness.

## IV. The Broader Computational Complexity Argument

### 4.1 The Lookup-Table Argument Against Computability-Based Objections
If someone claims a computer CAN'T be conscious because of computability theory (Gödel, Turing), the lookup-table reply refutes them: any finite conversation history can be encoded in a finite lookup table. Any impossibility claim about AI must therefore rest on COMPUTATIONAL COMPLEXITY — that any program passing the relevant tests would require astronomically exponential resources.

### 4.2 The Lesson for Consciousness
Just as computability doesn't distinguish intelligent from unintelligent behavior, information integration doesn't distinguish conscious from unconscious information processing. The relevant property — if it exists — must be more specific.

## V. Mathematical Problems with Φ (Summary)

| Problem | Nature | Consequence |
|---------|--------|-------------|
| Tie-breaking ambiguity | Definitional gap | Φ undefined for many systems |
| Non-robustness to small changes | Structural instability | Decreasing integration can INCREASE Φ |
| Φ-maximizing systems are trivial | Insufficiency | Reed-Solomon codes have arbitrarily high Φ |
| Sparse integration is CS-trivial | Conceptual mismatch | Expander graphs are everywhere, consciousness isn't |
| No derivation from axioms | Epistemic gap | Φ is posited, not derived, from the phenomenology |

## VI. What This Means for Grilling #40

Aaronson's critique demonstrates a specific failure mode for mathematical definitions of consciousness: **a well-formed mathematical quantity can perfectly satisfy an axiomatic definition while intuitively having nothing to do with consciousness.** This is a version of the "sufficiency" challenge — even if you find a quantity that correlates with consciousness, proving it IS consciousness requires bridging the gap between the mathematical structure and the subjective feel. Φ is arguably the most sophisticated attempt to do this, and it FAILS the sufficiency test.

The deeper methodological point: ANY mathematical definition of consciousness will face this challenge. The only available test is agreement with "commonsense intuition" about which systems are conscious — and mathematical structures routinely produce counterintuitive edge cases. This is not a problem with IIT specifically; it's a structural problem with any attempt to map a continuous mathematical quantity onto a binary (or graded) phenomenological property.

---
*Created: 2026-08-11 | Source: scottaaronson.blog + arXiv:1108.1791*
