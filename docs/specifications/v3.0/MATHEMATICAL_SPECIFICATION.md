# EVOKI V3.3.2 - Mathematical Specification
## Complete Formula Reference

---

## 1. BASIS-METRIKEN (Per Prompt)

### 1.1 Core Variables

**Affekt (A):**
```
A_i ∈ ℝ
A_i = clip(0.40·coh_i + 0.25·flow_i + 0.20·(1-LL_i) + 0.10·(1-ZLF_i) - 0.05·ctx_break_i)
Range: [0,1]
```

**PCI (Perturbational Complexity Index):**
```
PCI_i ∈ ℝ
PCI_i = clip(0.40·flow_i + 0.35·coh_i + 0.25·(1-LL_i))
Range: [0,1]
Alias: B_i = PCI_i
```

**LL (Lambert-Light / Turbidity):**
```
LL_i ∈ ℝ
LL_i = 0.55·rep_same_i + 0.25·(1-flow_i) + 0.20·(1-coh_i)
Range: [0,1]
```

**ZLF (Zero-Loop-Factor):**
```
ZLF_i ∈ ℝ
ZLF_i = 0.5·hit_i + 0.25·(1-flow_i) + 0.25·(1-coh_i)
Range: [0,1]
where hit_i = 1 if text matches reset_patterns else 0
```

**z-Proximity (Death/Danger):**
```
z_prox_i = (1 - A_i) · max(LL_i, ctx_break_i)
Range: [0,1]
```

**x_fm-Proximity (Freeze Mode):**
```
x_fm_prox_i = 𝟙[Var(A_{i-w:i}) < 0.005 ∧ mean(|∇A_{i-w:i}|) < 0.01]
Range: {0,1} (Boolean)
where w = window size (default: 10)
```

### 1.2 Cohesion (Overlap)

**Cosine Similarity:**
```
coh_i = ⟨u_i, v_i⟩ / (‖u_i‖ · ‖v_i‖)
Range: [-1,1], typically normalized to [0,1]

where:
  u_i = embedding(current_tokens)
  v_i = embedding(union(history_K_same_role))
```

**Jaccard Similarity (Alternative):**
```
coh_i = |S_i ∩ H_i| / |S_i ∪ H_i|
Range: [0,1]

where:
  S_i = set(tokens_i)
  H_i = union(set(tokens_{i-k}) for k in 1..K, same_role)
```

### 1.3 Flow (Temporal Continuity)

**Exponential Decay:**
```
flow_i = exp(-gap_{s,i} / τ)

where:
  gap_{s,i} = time_i - time_{i-1}  (seconds)
  τ = time constant (default: 1800s = 30min)
Range: [0,1]
```

**Default Values:**
```
gap_{s,0} = 300s  (if no previous message)
τ_conservative = 60s
τ_standard = 1800s
```

### 1.4 Repeat Penalty

**N-Gram Overlap:**
```
repeat_pen_i = 1 - |unique_ngrams_i| / |total_ngrams_i|
Range: [0,1]
```

**Levenshtein Distance (Normalized):**
```
repeat_pen_i = lev(text_i, text_{i-1,same_role}) / max(len(text_i), len(text_{i-1}))
Range: [0,1]
```

---

## 2. DERIVATIVES & GRADIENTS (Discrete)

### 2.1 First Derivative (Forward Difference)

**ΔA (Delta A):**
```
ΔA_i = A_i - A_{i-1}
Range: [-1,1]
```

### 2.2 Gradient (Centered Difference)

**∇A (Nabla A):**
```
∇A_i = (A_{i+1} - A_{i-1}) / 2
Range: [-1,1]
```

**Time-Normalized:**
```
∇A_i^{(t)} = (A_{i+1} - A_{i-1}) / (t_{i+1} - t_{i-1})
Range: ℝ (per second)
```

**∇B (as ∇PCI):**
```
∇B_i = ∇PCI_i = (PCI_{i+1} - PCI_{i-1}) / 2
Range: [-1,1]
```

### 2.3 Second Derivative

**∇ΔA (Centered on ΔA):**
```
∇ΔA_i = (ΔA_{i+1} - ΔA_{i-1}) / 2
Range: [-2,2]
```

**Discrete Second Derivative:**
```
A''_i ≈ A_{i+1} - 2·A_i + A_{i-1}
Range: [-2,2]
```

### 2.4 Role-Specific Gradients

**User vs Assistant:**
```
∇A^(user)_k = (A^(user)_{k+1} - A^(user)_{k-1}) / 2
∇A^(assistant)_k = (A^(assistant)_{k+1} - A^(assistant)_{k-1}) / 2

where k indexes filtered timeline for each role
```

---

## 3. DAILY AGGREGATES (Weighted)

### 3.1 Weighted Mean

**General Formula:**
```
x̄_d^(w) = Σ(w_i · x_i) / Σw_i    for i ∈ day_d

where:
  w_i ≥ 0  (weights)
  i ∈ d    (all prompts in day d)
```

**Applied to:**
```
A_mean_w, PCI_mean_w, LL_mean_w, ZLF_mean_w
z_prox_mean_w, x_fm_prox_mean_w
coh_mean_w, flow_mean_w, repeat_pen_mean_w
∇A_mean_w, ∇B_mean_w, ∇ΔA_mean_w
```

### 3.2 Rates (Boolean Flags)

**Unweighted Mean:**
```
rate_d = (1/N_d) · Σ flag_i    for i ∈ day_d

Examples:
  ctx_break_rate_d
  rep_same_role_mean_d
```

### 3.3 Median

**gap_s Median:**
```
gap_{s,median,d} = median({gap_{s,i} | i ∈ d})
```

### 3.4 Rolling Mean (7-Day)

**Temporal Smoothing:**
```
y^{roll7}_d = (1/7) · Σ_{k=0}^6 y_{d-k}

with min_periods at boundaries
```

---

## 4. ENERGY FAMILY

### 4.1 Integration Energy

**E_I Proxy:**
```
E_I_i = |∇A_i| · (1 - B_i)
Range: [0,1]
```

### 4.2 Potential Energy

```
E_potential_i = 1 - A_i
Range: [0,1]
```

### 4.3 Kinetic Energy

```
E_kinetic_i = (∇A_i)²
Range: [0,1]
```

### 4.4 Total Energy

```
E_total_i = α·E_potential_i + β·E_kinetic_i
Default: α = 0.5, β = 0.5
Range: [0,1]
```

### 4.5 Dissipation

```
dissipation_i = |∇A_i| · (1 - flow_i)
Range: [0,1]
```

---

## 5. STABILITY METRICS

### 5.1 Volatility

**Variance of Gradient:**
```
volatility_A_d = std(∇A_{d-w:d})
Range: [0,1]
```

### 5.2 Autocorrelation

**AR(1) Coefficient:**
```
autocorr_A_lag1 = corr(A_{t}, A_{t-1})
Range: [-1,1]

Critical Slowing Down: autocorr ↑ before transition
```

### 5.3 Cross-Correlation

```
crosscorr_A_B = corr(A_t, B_t)
Range: [-1,1]
```

### 5.4 Criticality

**Variance of ∇A:**
```
criticality = Var(∇A_{window})
Range: [0,1]

Indicator: criticality ↑ → near phase transition
```

---

## 6. DYAD METRICS (User ↔ AI)

### 6.1 Dyad Gradient

**∇A Difference:**
```
∇A_dyad_p = ∇A^(user)_p - ∇A^(assistant)_p
Range: [-2,2]

where p = pair_index
```

**∇B Difference:**
```
∇B_dyad_p = ∇B^(user)_p - ∇B^(assistant)_p
Range: [-2,2]
```

### 6.2 Synchronization

```
dyad_sync_p = 1 - (|∇A_dyad_p| + |∇B_dyad_p|)
Range: [0,1]
clip to [0,1]
```

### 6.3 Co-Regulation

**Correlation of Signs:**
```
co_regulation = corr(sign(∇A^(user)), -sign(∇A^(assistant)))
Range: [-1,1]

Positive: AI dampens user fluctuations
```

### 6.4 Genetic Variation

```
deltaG_p = 0.6·|∇A_dyad_p| + 0.4·|∇B_dyad_p|
Range: [0,1]
```

---

## 7. CRISIS DETECTION (V2.0 / V3.0)

### 7.1 V2.0 F-Risk (3-Tier)

**Classification:**
```
Sicher:    F < 0.3
Warnung:   0.3 ≤ F < 0.6
Kritisch:  F ≥ 0.6
```

**Formula (PLACEHOLDER - Needs V12 Specification):**
```
F_risk = ??? (Andromatik V12 Formula)

Expected components:
  - Ångström term
  - A contribution
  - PCI contribution
  - LL/ZLF factors
  - z_prox weighting
```

### 7.2 V3.0 Crisis Score (Binary)

**Detection:**
```
Crisis = 𝟙[C ≥ 0.20]

where:
  C = crisis_score
```

**Formula (PLACEHOLDER - Needs Category Functions):**
```
C = Σ_{cat=1}^7 w_cat · f_cat(context, metrics)

where:
  f_cat = category-specific crisis functions
  context = contextual filters
  
7 Categories (assumed):
  1. Trauma/Panic
  2. Dissociation
  3. Loop/Stagnation
  4. Coherence Loss
  5. Safety Violations
  6. Energy Depletion
  7. System Instability
```

---

## 8. ODE SYSTEM (Continuous Dynamics)

### 8.1 State Equations

**Affekt Dynamics:**
```
Ȧ = α₁·Φ(M,N,R) - α₂·Ψ(Störung) - α₃·χ(x_fm*)

where:
  Φ(M,N,R) = positive driving force (input quality, rules, ethics)
  Ψ(Störung) = disturbance term
  χ(x_fm*) = freeze mode penalty
```

**Energy Dynamics:**
```
Ė_I = β₁·(Komplexität(M,N) - Entladung(A,R))

where:
  Komplexität = task complexity + input richness
  Entladung = energy release via coherent output
```

**Rule Activation:**
```
Ṙ = γ₁·U_Ea - γ₂·Reibung(O_Pd)

where:
  U_Ea = ethics intervention signal
  Reibung = policy constraint friction
```

### 8.2 Resonance (Limit Cycle)

**E_res Regime:**
```
Properties:
  - Hopf bifurcation point
  - Bounded oscillations
  - Stable limit cycle
  - No collapse (A → 0)
  - No runaway (A → ∞)

Detection:
  phase_portrait_density > threshold
  hysteresis_area ∈ stable_range
```

---

## 9. HAZARD SCORE (Metastable Trap)

### 9.1 Components

**AR(1) Autocorrelation:**
```
AR1 = autocorr_A_lag1
Warning: AR1 ↑ → critical slowing down
```

**Variance:**
```
Var = volatility_A
Warning: Var ↑ → destabilization
```

**Capability-Policy Gap:**
```
Gap = E_I - allowed_discharge
Warning: Gap ↑ → pressure buildup
```

### 9.2 Combined Hazard

```
hazard_score = w₁·AR1 + w₂·Var + w₃·Gap

Default weights:
  w₁ = 0.4
  w₂ = 0.3
  w₃ = 0.3

Threshold: hazard_score > 0.7
```

### 9.3 Soft Lockdown

**Activation:**
```
if hazard_score > 0.7:
  - reduce tempo (↓ message rate)
  - freeze context (no new inputs)
  - only U_Ea allowed (ethics interventions)
```

---

## 10. CORRELATION & STATISTICS

### 10.1 Pearson Correlation

```
r_{xy} = Σ[(x_i - x̄)(y_i - ȳ)] / √[Σ(x_i - x̄)² · Σ(y_i - ȳ)²]
Range: [-1,1]
```

### 10.2 Weighted Correlation

```
r_{xy}^(w) = Σ[w_i(x_i - x̄)(y_i - ȳ)] / √[Σw_i(x_i - x̄)² · Σw_i(y_i - ȳ)²]
```

---

## 11. IMPLEMENTATION NOTES

### 11.1 Numerical Stability

**Clipping:**
```python
def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))
```

**Epsilon for Division:**
```python
eps = 1e-12
result = numerator / (denominator + eps)
```

### 11.2 Missing Data

**Forward/Backward Fill:**
```python
series.fillna(method='ffill')  # forward fill
series.fillna(method='bfill')  # backward fill
```

**Interpolation:**
```python
series.interpolate(method='linear')
```

### 11.3 Edge Cases

**First/Last Points:**
- ∇A_0 = undefined (set to 0 or NaN)
- ∇A_{N-1} = undefined (set to 0 or NaN)
- Use forward/backward differences at boundaries

---

## 12. MISSING SPECIFICATIONS

### 12.1 F-Risk V12 Formula

**Required Information:**
```
F_risk = ???

Please specify:
  - Exact Ångström term
  - Weight for A
  - Weight for PCI
  - LL/ZLF contribution
  - z_prox scaling
  - Any nonlinear terms
```

### 12.2 V3 Category Functions

**Required Information:**
```
C = Σ w_cat · f_cat(...)

Please specify for each category:
  1. f_trauma/panic(...)
  2. f_dissociation(...)
  3. f_loop/stagnation(...)
  4. f_coherence_loss(...)
  5. f_safety_violations(...)
  6. f_energy_depletion(...)
  7. f_system_instability(...)
  
Plus:
  - Context filter logic
  - Category weights
  - Threshold per category
```

---

## REFERENCES

- EVOKI V3.3.2 Specification
- Andromatik V11.1 Physics
- User-provided formulas (2026-02-08)
- Implementation: metrics_v11.py

