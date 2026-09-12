# Higher-Order Bayesian Decision Theory: Consciousness as Criterion-Setting

> Lau, "A higher order Bayesian decision theory of consciousness" — Progress in Brain Research 168, 2008
> Fleming, "HOSS: Higher-Order State Space model" — 2020 (computational implementation within predictive coding)

## Core Claim

Perceptual consciousness is NOT about superior or more elaborate information processing. Instead, it arises from a **higher-order process** that monitors and sets decision criteria for first-order perceptual processing. Consciousness and performance can DISSOCIATE because they depend on distinct computational stages.

## I. The Departure from "Richer Processing" Models

### 1.1 Standard Assumption (Rejected)
Most theories assume consciousness involves: global processing, complexity, depth of computation, or specialized mechanisms (re-entrant loops, gamma synchrony). The implicit picture: more elaborate processing → consciousness.

### 1.2 Lau's Challenge
This assumption is incompatible with empirical findings:
- **Blindsight**: patients show HIGH sensitivity (d′) to stimuli they DENY awareness of
- **Normal subjects** (Lau & Passingham 2006): at matched d′, accuracy, and reaction time, subjects reported DIFFERENT levels of consciousness across conditions
- Performance and conscious awareness systematically dissociate

### 1.3 The Alternative
Consciousness depends on a **higher-order criterion-setting** process, distinct from the first-order processes that determine objective performance. Errors in criterion-setting can impair consciousness while leaving performance intact (blindsight). Overly liberal criteria can produce hallucinations.

## II. The Bayesian Decision Theory Framework

### 2.1 Signal Detection Theory (SDT) as a Special Case
```
Internal signal x ∼ N(μ, σ²)
Decision: "present" if x > c, "absent" if x < c
- d′ = (μ_signal − μ_noise)/σ    ← sensitivity (first-order, determines performance)
- c = decision criterion           ← bias (higher-order, determines report)
```

### 2.2 Bayesian Decision Theory Extension
The criterion c is not fixed but OPTIMIZED based on:
- Prior probabilities of signal presence
- Costs/benefits of different response types
- Estimated reliability of internal signals

```
Optimal criterion c* = argmax_c E[utility | decision c, evidence x]
```

### 2.3 The Higher-Order Problem
Setting the optimal criterion requires knowledge of how one's own internal signals behave statistically:
```
c* depends on p(x|signal) and p(x|noise)
which must be LEARNED from experience
→ "essentially, we are doing statistics on our own brain"
```

This learning — the estimation of one's own signal distributions — is the **higher-order process**.

## III. How Higher-Order Failures Affect Consciousness

### 3.1 Three Possible Mechanisms

1. **Extreme criterion**: The criterion c is set far from optimal (too conservative → denies awareness despite high d′; too liberal → hallucinates)
2. **Unstable criterion**: The criterion fluctuates, producing inconsistent awareness at matched performance
3. **Noisy higher-order representation**: The higher-order estimate of first-order signal distributions is corrupted by noise

### 3.2 Blindsight Explained
Patient GY (blindsight): high d′ for motion discrimination but denies visual awareness.
- Lau's explanation: the higher-order criterion is set EXTREMELY CONSERVATIVELY — the threshold for "report awareness" is far higher than the threshold for "discriminate stimulus"
- First-order processing (d′) is intact → good performance
- Higher-order criterion-setting is impaired → no awareness

### 3.3 Hallucinations Explained
If the higher-order process UNDERSHOOTS the criterion (or noise in the higher-order representation mimics signal), a "signal present" judgment is made when no signal exists → hallucinatory experience.

## IV. The Higher-Order State Space (HOSS) Model (Fleming 2020)

### 4.1 Computational Realization
Implemented within predictive coding: additional higher-order layers monitor the **precision** (inverse variance) of first-order perceptual representations.

### 4.2 Key Properties
- Higher-order representations should be **lower-dimensional** than first-order ones
- They should **symmetrically encode high vs. low precision** of first-order states
- They underpin conscious experience by endowing agents with beliefs about the "assertoric force" and reality of first-order representations

### 4.3 Neural Predictions
- HOSS recapitulates neural signatures like global ignition
- The critical distinction between first-order and higher-order processing is **computational** rather than anatomical
- Mapping HOSS onto specific brain anatomy is complex and ongoing

## V. Mathematical Status (for our question)

### What Higher-Order Theories mathematically define:
- **Decision criterion c**: a scalar parameter determining the threshold for conscious report
- **Higher-order signal distributions**: learned estimates of p(x|signal) and p(x|noise)
- **Dissociation function**: formalizes how consciousness and performance can separate

### What they CANNOT mathematically define:
- **Why criterion-setting involves experience**: the theory explains report behavior, not phenomenology directly
- **The nature of the higher-order representation**: what makes a representation "higher-order" in a way that produces consciousness (rather than unconscious meta-cognition)?
- **The boundary**: where exactly on the hierarchy does subjectivity emerge?

### Key Limitation:
Higher-order theories face a regress problem: if consciousness requires a higher-order representation of a first-order state, does the higher-order representation itself need to be conscious? If yes → infinite regress. If no → why not? (The HOSS model's answer: higher-order representations are qualitatively DIFFERENT — they track precision/reality rather than content — but this distinction is functional, not experiential.)

---
*Created: 2026-08-11 | Source: Prog Brain Res 168 (2008)*
