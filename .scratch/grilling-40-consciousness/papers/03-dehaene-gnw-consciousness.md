# Global Neuronal Workspace: Consciousness as Global Information Broadcasting

> Dehaene, Kerszberg & Changeux, "A neuronal model of a global workspace in effortful cognitive tasks" — PNAS 95(24), 1998
> Dehaene & Changeux, "Experimental and Theoretical Approaches to Conscious Processing" — Neuron 70(2), 2011
> Mashour, Roelfsema, Changeux & Dehaene, "Conscious Processing and the Global Neuronal Workspace Hypothesis" — Neuron 105(5), 2020

## Core Claim

Conscious access IS global information availability. What we subjectively experience is the **selection, amplification, and global broadcasting** of a single piece of information to many distant brain systems. The GNW concerns **access consciousness** — information made accessible to processors mediating working memory, verbal report, and behavior.

**Crucial distinction**: GNW is a theory of **conscious access**, not phenomenal consciousness/qualia. It explains which information becomes conscious, not why consciousness feels like anything.

## I. Architectural Model

### 1.1 Two Computational Spaces

1. **Parallel specialized processors**: Distributed modular systems operating non-consciously and in parallel — sensory analysis, motor routines, semantic memory, etc.
2. **Global workspace neurons**: Widely distributed excitatory neurons with long-range axons forming reciprocally connected tracts. Anatomical hubs: dorsolateral prefrontal cortex, inferior parietal cortex, mid-temporal cortex, precuneus, anterior cingulate. Key role: large pyramidal cells in cortical layers II/III and V.

### 1.2 Global Workspace as Router

The workspace is not a brain region — it's a distributed "router" through which a SINGLE piece of information at a time is amplified, sustained, and globally broadcast. It functions like a "high-level RAM" for access, coordination, and manipulation.

### 1.3 Capacity Limit

Only one representation occupies the workspace at a time. This accounts for:
- Psychological refractory period (PRP)
- Attentional blink
- Serial nature of conscious processing

## II. Ignition Dynamics (The Core Mechanism)

### 2.1 The Ignition Threshold

**Two regimes for an incoming stimulus:**
- **Subliminal** (below threshold): purely feedforward activation that quickly dies out. Processed by specialized modules but never globally broadcast.
- **Conscious** (above threshold): a non-linear, sudden, coherent activation ("ignition") of a subset of workspace neurons, producing a sustained, large-scale, self-amplifying wave of activity.

### 2.2 Neural Implementation (from primary papers)

The formal models use **spiking neurons with realistic membrane, ion-channel, and receptor properties**:

- **Fast AMPA**: feedforward connections between areas — rapid signal transmission
- **Slow NMDA**: recurrent feedback connections — accumulation dynamics and multi-stable "all-or-none" behavior
- **Thalamo-cortical loops**: recurrent thalamo-cortical networks implementing elementary categorization

**The dynamical picture:**
```
Incoming evidence → AMPA feedforward activation
                  → NMDA recurrent accumulation (slow time constant)
                  → If evidence > threshold: global ignition
                  → If evidence < threshold: activity dies (subliminal)
```

### 2.3 Wong-Wang Reduced Model (Reference 67)

The underlying biophysics can be reduced to a **two-variable attractor model**:
- Attractor states: low-firing (rest) and high-firing (ignited)
- Transition: driven by accumulated NMDA-mediated recurrent excitation
- Noise: spontaneous fluctuations cause stochastic transitions

### 2.4 Empirical Signatures of Ignition

| Component | Timing | Signature |
|-----------|--------|-----------|
| Early sensory | ~100 ms | Linear with stimulus strength (subliminal + conscious) |
| Global ignition | ~300 ms | Non-linear amplification into PFC, parietal, cingulate |
| P3 wave | 300-600 ms | Late slow event-related potential |
| Gamma power | 300+ ms | High-frequency (>30 Hz) oscillations |
| Long-range synchrony | 300+ ms | Beta/gamma phase synchrony across distant areas |

**Key**: Early gamma is non-conscious; LATE gamma (post-200ms) with long-distance synchrony is the consciousness signature.

## III. Distinctions from Other Theories

### 3.1 Conscious Access ≠ Attention
Attention can operate non-consciously (e.g., attentional cueing of invisible stimuli). The GNW is about which information is REPORTABLE and AVAILABLE to the global workspace.

### 3.2 Unconscious Processing is Extensive
The brain's non-conscious processors handle massive parallel computation continuously. Consciousness is a bottleneck — a capacity-limited serial operation on top of unconscious parallel processing.

### 3.3 Comparison with IIT
The review explicitly notes that IIT's Φ "is impossible to compute in practice (only approximations exist)" and that IIT offers no mechanism for the non-linear ignition profile or the empirical signatures of conscious access (P3, late gamma synchrony, sustained prefrontal activation).

## IV. Mathematical Status (for our question)

### What the GNW mathematically defines:
- **Dynamical threshold**: the ignition point in the full spiking-neuron or reduced Wong-Wang model
- **Global broadcasting**: sustained activation of workspace neurons with long-range synchrony
- **Capacity limit**: stochastic winner-take-all in the workspace
- **Empirical predictions**: quantitative signatures (P3 latency, gamma power increase, synchrony measures)

### What the GNW CANNOT mathematically define:
- **Subjectivity itself**: the theory describes the INFORMATION that becomes conscious and the MECHANISM by which it's accessed — but not why access is accompanied by experience
- **Quality of experience**: GNW says NOTHING about what makes pain feel painful or red feel red — it only explains which representations get globally broadcast
- **The access/phenomenal gap**: Block's distinction between access consciousness (GNW's target) and phenomenal consciousness (not addressed) highlights the theory's intended scope limit
- **Necessary and sufficient conditions**: GNW describes a reliable neural SIGNATURE of conscious access, but does not claim this signature IS consciousness

### The GNW's honest scope:
The GNW authors are explicit that their theory targets **conscious access** (information available for report and global control), not the hard problem of phenomenal experience. Any claim that GNW "solves" consciousness mathematically is a misunderstanding of what the theory claims.

---
*Created: 2026-08-11 | Source: PNAS 1998 + Neuron 2011 + Neuron 2020*
