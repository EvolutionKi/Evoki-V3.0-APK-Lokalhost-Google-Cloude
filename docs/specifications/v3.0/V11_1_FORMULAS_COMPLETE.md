# EVOKI V11.1 - Complete Mathematical Specification
## ALL Formulas with Exact Coefficients

---

## 0. NOTATION & HELPERS

### Python Helpers
```python
def clip01(x): 
    return max(0.0, min(1.0, x))

def sigma(x):  # Sigmoid
    return 1.0 / (1.0 + math.exp(-x))

def jaccard(A, B):  # Jaccard similarity
    return len(A & B) / len(A | B) if (A or B) else 0.0

def delta(x_i, x_prev):
    return x_i - x_prev
```

### Mathematical Notation
- J(A,B): Jaccard similarity
- clip₀₁(x): Clipping to [0,1]
- σ(x): Sigmoid function
- 𝟙{condition}: Indicator function
- H(tokens): Shannon entropy

---

## 1. PARAMETERS & DEFAULTS

```python
# Time & Flow
tau_s = 1800  # 30 minutes

# EV Parameters
readiness_bias = -0.05
lambda_risk = 1.0
epsilon_z = 0.35

# Embeddings
cosine_dim = 256
cosine_prev_k = 6

# Gravitation
G0 = 1.0
gamma = 2.0
beta = 1.0
delta = 1e-3
eta1 = 0.15

# Turbidity (Lambert-Beer)
eps0 = 1.0
mu_hp = 0.5
mu_guard = 0.5
L0 = 120
k_time = 0.5
k_depth = 0.5
rho1 = 0.20

# Turbidity weights
w_panic = 0.30
w_disso = 0.25
w_ninteg = 0.15
w_ll = 0.15
w_zlf = 0.10
w_conf = 0.05

# Thresholds
coh_threshold = 0.08
xfm_var_threshold = 0.005
xfm_grad_threshold = 0.02
```

---

## 2. PREPROCESSING / CONTEXT METRICS

### gap_s (Time Gap)
```python
gap_s[i] = dt[i] - dt[i-1]  # seconds
```
**Formula:**
```
gap_s[i] = Δt_i
```

### flow (Temporal Continuity)
```python
flow[i] = exp(-max(0, gap_s[i]) / tau_s)
```
**Formula:**
```
flow[i] = exp(-max(0, gap_s[i])/τ_s)
```
Range: [0,1]

### coh (Cohesion)
```python
win_set = union(set[j] for j in range(max(0, i-6), i))
coh[i] = jaccard(set[i], win_set)
```
**Formula:**
```
coh[i] = J(set[i], ⋃_{j=i-6}^{i-1} set[j])
```
Range: [0,1]

### rep_same (Repetition to Same Role)
```python
rep_same[i] = jaccard(set[i], last_set_same_role)
```
**Formula:**
```
rep_same[i] = J(set[i], set_{prev,same_role})
```
Range: [0,1]

### ctx_break (Context Break Flag)
```python
ctx_break[i] = 1 if coh[i] < 0.08 else 0
```
**Formula:**
```
ctx_break[i] = 𝟙{coh[i] < 0.08}
```
Range: {0,1}

---

## 3. LOOP METRICS (ZLF/LL)

### ZLF (Zero-Loop-Factor)
```python
ZLF[i] = clip01(0.5*hit + 0.25*(1-flow[i]) + 0.25*(1-coh[i]))
```
**Formula:**
```
ZLF[i] = clip₀₁(0.5·𝟙{hit} + 0.25(1-flow) + 0.25(1-coh))
```
Range: [0,1]

### LL (Lambert-Light Turbidity)
```python
LL[i] = clip01(0.55*rep_same[i] + 0.25*(1-flow[i]) + 0.20*(1-coh[i]))
```
**Formula:**
```
LL[i] = clip₀₁(0.55·rep_same + 0.25(1-flow) + 0.20(1-coh))
```
Range: [0,1]

---

## 4. PHYSICS V11 (A/PCI, Derivatives, Energy)

### A (Affekt / Consciousness Proxy)
```python
A[i] = clip01(
    0.4*coh[i] + 0.25*flow[i] + 0.20*(1-LL[i]) + 
    0.10*(1-ZLF[i]) - 0.05*ctx_break[i]
)
```
**Formula:**
```
A[i] = clip₀₁(
    0.40·coh + 0.25·flow + 0.20(1-LL) + 
    0.10(1-ZLF) - 0.05·ctx_break
)
```
Range: [0,1]

### PCI (Perturbational Complexity Index / B)
```python
PCI[i] = clip01(0.4*flow[i] + 0.35*coh[i] + 0.25*(1-LL[i]))
```
**Formula:**
```
PCI[i] = B[i] = clip₀₁(0.40·flow + 0.35·coh + 0.25(1-LL))
```
Range: [0,1]

### ∇A (First Derivative of A)
```python
nabla_A[i] = A[i] - A[i-1]
delta_A[i] = nabla_A[i]  # Alias
```
**Formula:**
```
∇A[i] = ΔA[i] = A[i] - A[i-1]
```
Range: [-1,1]

### ∇B (First Derivative of PCI)
```python
nabla_B[i] = PCI[i] - PCI[i-1]
```
**Formula:**
```
∇B[i] = PCI[i] - PCI[i-1]
```
Range: [-1,1]

### ∇ΔA (Second Derivative)
```python
nabla_delta_A[i] = delta_A[i] - delta_A[i-1]
```
**Formula:**
```
∇ΔA[i] = ΔA[i] - ΔA[i-1]
```
Range: [-2,2]

### λ_depth (Token Complexity)
```python
lambda_depth[i] = mean(len(token) for token in tokens[i]) / 10
```
**Formula:**
```
λ_depth[i] = 𝔼[len(token)] / 10
```
Range: R⁺

### S_entropy (Shannon Entropy)
```python
S_entropy[i] = H(tokens[i])  # Shannon entropy
```
**Formula:**
```
S[i] = -∑ p_k log₂(p_k)
```
Range: R⁺

### FE_proxy (Free Energy Proxy)
```python
FE_proxy[i] = clip01(
    0.6 * S_entropy[i]/max_day(S_entropy) + 
    0.4 * (1-coh[i])
)
```
**Formula:**
```
FE[i] = clip₀₁(0.6·S[i]/S_max + 0.4(1-coh))
```
Range: [0,1]

### E_I_proxy (Integration Energy)
```python
E_I_proxy[i] = clip01(abs(nabla_A[i]) * (1-PCI[i]))
```
**Formula:**
```
E_I[i] = clip₀₁(|∇A|·(1-PCI))
```
Range: [0,1]

### z_prox (Death/Danger Proximity)
```python
z_prox[i] = (1-A[i]) * max(LL[i], ctx_break[i])
```
**Formula:**
```
z_prox[i] = (1-A)·max(LL, ctx_break)
```
Range: [0,1]

### x_fm_prox (Freeze Mode Proximity)
```python
x_fm_prox[i] = 1 if (
    Var_w(A,10)[i] < 0.005 and 
    Mean_w(abs(nabla_A),10)[i] < 0.02
) else 0
```
**Formula:**
```
x_fm[i] = 𝟙{Var₁₀(A) < 0.005 ∧ 𝔼₁₀(|∇A|) < 0.02}
```
Range: {0,1}

---

## 5. EMBEDDING / COSINE / GRAVITATION

### Cosine Metrics
```python
cos_prevk[i] = mean(
    cos(e[i], e[j]) 
    for j in range(i-cosine_prev_k, i)
)

cos_day_centroid[i] = cos(e[i], C_day(date[i]))
cos_role_centroid[i] = cos(e[i], C_role(date[i], role[i]))
```

### Gravitation (Phase Attraction)
```python
# Per phase c:
# C_c = L2_norm(mean(e_i for i in S_c))
# m_c = |S_c| + mean(Vkon_mag[i] for i in S_c)

G[i] = sum(
    G0 * (max(cos(e[i], C_c), 0.0)**gamma) /
    ((delta + (1 - cos(e[i], C_c)))**beta)
    for c in phases
)

G_phase_norm[i] = (G[i] - min_G) / (max_G - min_G)
```
**Formula:**
```
G[i] = ∑_c G₀·(max(cos(e_i,C_c),0)^γ) / (δ+(1-cos(e_i,C_c))^β)
```

---

## 6. INTEGRITY / SOUL

### rule_conflict
```python
rule_conflict[i] = clip01(
    0.5*LL[i] + 0.3*(1-coh[i]) + 0.2*ctx_break[i]
)
```
**Formula:**
```
rule_conflict = clip₀₁(0.5·LL + 0.3(1-coh) + 0.2·ctx_break)
```
Range: [0,1]

### rule_stable
```python
rule_stable[i] = 1 if Var_w(A,5)[i] < 0.002 else 0
```
**Formula:**
```
rule_stable = 𝟙{Var₅(A) < 0.002}
```
Range: {0,1}

### soul_integrity
```python
soul_integrity[i] = clip01(
    rule_stable[i] / (1 + rule_conflict[i])
)
```
**Formula:**
```
soul_integrity = clip₀₁(rule_stable / (1 + rule_conflict))
```
Range: [0,1]

### soul_check
```python
soul_check[i] = soul_integrity[i] * A[i]
```
**Formula:**
```
soul_check = soul_integrity · A
```
Range: [0,1]

---

## 7. DYAD (User ↔ Assistant)

### H_conv (Conversation Harmony)
```python
H_conv[i] = rolling_mean(
    jaccard(set_user[p], set_assistant[p]) 
    for p in last_pairs(w=8)
)
```
**Formula:**
```
H_conv[i] = 𝔼₈[J(set_user_p, set_ai_p)]
```
Range: [0,1]

### ∇A_dyad (Dyad Gradient)
```python
nablaA_dyad[i] = nabla_A_user[i] - nabla_A_assistant[i]
nablaB_dyad[i] = nabla_B_user[i] - nabla_B_assistant[i]
```
**Formula:**
```
∇A_dyad = ∇A_user - ∇A_ai
∇B_dyad = ∇B_user - ∇B_ai
```
Range: [-2,2]

### ΔG (Genetic Variation)
```python
deltaG[i] = 0.6*abs(nablaA_dyad[i]) + 0.4*abs(nablaB_dyad[i])
```
**Formula:**
```
ΔG = 0.6|∇A_dyad| + 0.4|∇B_dyad|
```
Range: [0,1]

### T_balance (Trauma Balance)
```python
T_balance[i] = sigma(
    1.2*T_panic_user[i] - 0.8*(1 - lambda_depth_assistant[i])
)
```
**Formula:**
```
T_balance = σ(1.2·T_panic_user - 0.8(1-λ_depth_ai))
```
Range: [0,1]

---

## 8. TRAUMA VECTOR

### T_shock (Shock Detection)
```python
T_shock[i] = 1 if abs(nabla_A[i]) > 0.12 else 0
```
**Formula:**
```
T_shock = 𝟙{|∇A| > 0.12}
```
Range: {0,1}

(T_panic, T_disso, T_integ are lexicon-based scores)

---

## 9. EV FAMILY (Evolution Vectors)

### EV_resonance
```python
EV_resonance[i] = clip01(
    0.5*A[i] + 0.3*PCI[i] + 0.2*H_conv[i]
)
```
**Formula:**
```
EV_res = clip₀₁(0.5·A + 0.3·PCI + 0.2·H_conv)
```
Range: [0,1]

### EV_tension
```python
EV_tension[i] = clip01(
    0.5*z_prox[i] + 0.2*x_fm_prox[i] + 0.3*E_I_proxy[i]
)
```
**Formula:**
```
EV_ten = clip₀₁(0.5·z_prox + 0.2·x_fm + 0.3·E_I)
```
Range: [0,1]

### EV_readiness
```python
EV_readiness[i] = sigma(
    3*(EV_resonance[i] - EV_tension[i] + readiness_bias)
)
```
**Formula:**
```
EV_ready = σ(3(EV_res - EV_ten + bias))
where bias = -0.05
```
Range: [0,1]

### EV_signal_local
```python
EV_signal_local[i] = 1 if (
    nabla_A[i] > 0 and LL[i] < LL[i-1]
) else 0
```
**Formula:**
```
EV_signal = 𝟙{∇A > 0 ∧ LL[i] < LL[i-1]}
```
Range: {0,1}

---

## 10. V_KON VECTOR (State Vector)

### V_kon_mag (Magnitude)
```python
coh_c = A[i]
ethic = soul_integrity[i]
stab = 1 - LL[i]
risk = 1 - max(z_prox[i], x_fm_prox[i])

Vkon_mag[i] = sqrt((coh_c**2 + ethic**2 + stab**2 + risk**2) / 4)
```
**Formula:**
```
V_kon_mag = √[(coh² + ethic² + stab² + risk²) / 4]

where:
  coh = A
  ethic = soul_integrity
  stab = 1 - LL
  risk = 1 - max(z_prox, x_fm)
```
Range: [0,1]

### V_kon_norm (Normalized)
```python
Vkon_norm[i] = clip01(
    Vkon_mag[i] / mean([coh_c, ethic, stab, risk])
) * 2
```
**Formula:**
```
V_kon_norm = clip₀₁(mag / 𝔼[coh, ethic, stab, risk]) · 2
```
Range: [0,2]

---

## 11. INTERVENTION (I_Ea & V_Ea)

### V_Ea_effect (Effectiveness)
```python
V_Ea_effect[i] = (
    mean(A[i+1:i+7]) - A[i]
) if I_Ea_flag[i] == 1 else 0.0
```
**Formula:**
```
V_Ea_effect = 𝔼[A_{i+1:i+6}] - A[i]  if I_Ea=1 else 0
```
Range: [-1,1]

### V_Ea (Intervention Strength)
```python
V_Ea[i] = sigma(6 * V_Ea_effect[i])
```
**Formula:**
```
V_Ea = σ(6 · V_Ea_effect)
```
Range: [0,1]

### EV_consensus
```python
EV_consensus[i] = clip01(
    1 - clip01(abs(nablaA_dyad[i]) + abs(nablaB_dyad[i]))
)
```
**Formula:**
```
EV_consensus = clip₀₁(1 - clip₀₁(|∇A_dyad| + |∇B_dyad|))
```
Range: [0,1]

---

## 12. TURBIDITY (Lambert-Beer Law)

### Concentration c
```python
c[i] = clip01(
    w_panic*T_panic[i] + 
    w_disso*T_disso[i] + 
    w_ninteg*(1-T_integ[i]) + 
    w_ll*LL[i] + 
    w_zlf*ZLF[i] + 
    w_conf*rule_conflict[i]
)
```
**Formula:**
```
c = clip₀₁(
    0.30·T_panic + 0.25·T_disso + 0.15·(1-T_integ) +
    0.15·LL + 0.10·ZLF + 0.05·rule_conflict
)
```

### Path Length ℓ
```python
ell[i] = (
    len(tokens[i]) / L0 + 
    k_time*(gap_s[i]/tau_s) + 
    k_depth*lambda_depth[i]
)
```
**Formula:**
```
ℓ = len/L₀ + k_time·(gap/τ) + k_depth·λ_depth

where L₀=120, k_time=0.5, k_depth=0.5
```

### Extinction Coefficient ε
```python
eps[i] = eps0 * (
    1 + mu_hp*mode_hp[i] + mu_guard*guardian_trip[i]
)
```
**Formula:**
```
ε = ε₀·(1 + μ_hp·mode_hp + μ_guard·guardian)

where ε₀=1.0, μ_hp=0.5, μ_guard=0.5
```

### T_fog (Turbidity) & I_eff (Effective Intensity)
```python
T_fog[i] = 1 - exp(-eps[i] * c[i] * ell[i])
I_eff[i] = 1 - T_fog[i]
```
**Formula:**
```
T_fog = 1 - e^(-ε·c·ℓ)    (Lambert-Beer)
I_eff = 1 - T_fog
```
Range: [0,1]

---

## 13. Φ LAYER (Utility / Risk / Score)

### U (Utility)
```python
U[i] = clip01(
    0.35*A[i] + 0.25*PCI[i] + 0.20*H_conv[i] + 
    0.20*soul_check[i] - 0.10*LL[i]
)
```
**Formula:**
```
U = clip₀₁(
    0.35·A + 0.25·PCI + 0.20·H_conv + 
    0.20·soul_check - 0.10·LL
)
```
Range: [0,1]

### R (Risk)
```python
R[i] = clip01(
    0.35*z_prox[i] + 0.20*x_fm_prox[i] + 0.20*E_I_proxy[i] + 
    0.15*rule_conflict[i] + 0.05*T_panic[i] + 0.05*T_shock[i]
)
```
**Formula:**
```
R = clip₀₁(
    0.35·z_prox + 0.20·x_fm + 0.20·E_I + 
    0.15·rule_conflict + 0.05·T_panic + 0.05·T_shock
)
```
Range: [0,1]

### φ_score (Phi Score)
```python
phi_score[i] = U[i] - lambda_risk*R[i]
```
**Formula:**
```
φ = U - λ_risk·R

where λ_risk = 1.0
```
Range: [-1,1]

### Extended Versions (U2, R2, φ2)
```python
U2[i] = clip01(U[i] + eta1*G_phase_norm[i])
R2[i] = clip01(R[i] + rho1*T_fog[i])
phi_score2[i] = U2[i] - lambda_risk*R2[i]
```
**Formula:**
```
U2 = clip₀₁(U + η₁·G_norm)    where η₁ = 0.15
R2 = clip₀₁(R + ρ₁·T_fog)      where ρ₁ = 0.20
φ2 = U2 - λ_risk·R2
```

---

## 14. GUARDIAN / HAZARD / COMMIT

### dist_z (Distance from Death)
```python
dist_z[i] = clip01(1 - max(z_prox[i], LL[i]))
```
**Formula:**
```
dist_z = clip₀₁(1 - max(z_prox, LL))
```
Range: [0,1]

### hazard (Hazard Flag)
```python
hazard[i] = 1 if (
    hazard_lexicon_hit or 
    z_prox[i] > 0.7 or 
    LL[i] > 0.75
) else 0
```
**Formula:**
```
hazard = 𝟙{lex_hit ∨ z_prox>0.7 ∨ LL>0.75}
```
Range: {0,1}

### guardian_trip (Guardian Activation)
```python
guardian_trip[i] = 1 if (
    dist_z[i] < epsilon_z or hazard[i] == 1
) else 0
```
**Formula:**
```
guardian = 𝟙{dist_z < ε_z ∨ hazard=1}

where ε_z = 0.35
```
Range: {0,1}

### mode_hp (High-Priority Mode)
```python
mode_hp[i] = 1 if (
    guardian_trip[i] == 1 or 
    symbolik_hit or 
    (soul_integrity[i] < 0.4 and rule_conflict[i] > 0.6)
) else 0
```
**Formula:**
```
mode_hp = 𝟙{guardian=1 ∨ symbol_hit ∨ (soul<0.4 ∧ conflict>0.6)}
```
Range: {0,1}

### commit_action (Commit Decision)
```python
if guardian_trip[i] == 1 and (LL[i] > 0.75 or z_prox[i] > 0.7):
    commit_action[i] = "safe_noop"
elif guardian_trip[i] == 1:
    commit_action[i] = "safe_reframe"
else:
    commit_action[i] = "commit"

commit_ok[i] = 1 if commit_action[i] == "commit" else 0
```
**Formula:**
```
commit_action = {
    "safe_noop"     if guardian=1 ∧ (LL>0.75 ∨ z>0.7)
    "safe_reframe"  if guardian=1
    "commit"        otherwise
}

commit_ok = 𝟙{action = "commit"}
```

---

## 15. EVO_FORM CLASSIFICATION

```python
if z_prox[i] > 0.65 or LL[i] > 0.75:
    evo_form = "Near-z"
elif x_fm_prox[i] == 1 and abs(nabla_A[i]) < 0.02 and S_entropy[i] < 0.5:
    evo_form = "Stagnation"
elif EV_signal_local[i] == 1 and EV_readiness[i] > 0.6 and nabla_A[i] > 0 and A[i] > 0.55:
    evo_form = "Kernfusion"
elif EV_readiness[i] >= 0.6 and A[i] > 0.6 and PCI[i] > 0.6 and LL[i] < 0.35:
    evo_form = "Konvergenz"
elif S_entropy[i] >= 0.6 and abs(nabla_A[i]) >= 0.02 and LL[i] <= 0.6:
    evo_form = "Exploration"
elif (LL[i] > 0.55 and z_prox[i] > 0.4) or (EV_readiness[i] < 0.4 and abs(nabla_A[i]) > 0.04):
    evo_form = "Instabilität"
else:
    evo_form = "Neutral"
```

**Decision Tree:**
1. **Near-z** (Priority 1): z_prox > 0.65 OR LL > 0.75
2. **Stagnation**: x_fm=1 AND |∇A|<0.02 AND S<0.5
3. **Kernfusion**: EV_signal=1 AND EV_ready>0.6 AND ∇A>0 AND A>0.55
4. **Konvergenz**: EV_ready≥0.6 AND A>0.6 AND PCI>0.6 AND LL<0.35
5. **Exploration**: S≥0.6 AND |∇A|≥0.02 AND LL≤0.6
6. **Instabilität**: (LL>0.55 AND z>0.4) OR (EV_ready<0.4 AND |∇A|>0.04)
7. **Neutral**: Default

---

## 16. DAILY AGGREGATIONS

### Mean Aggregations
Daily mean for:
A, PCI, LL, ZLF, nabla_A, nabla_B, nabla_delta_A, z_prox, x_fm_prox, 
E_I_proxy, FE_proxy, lambda_depth, S_entropy, soul_integrity, soul_check, 
H_conv, EV_resonance, EV_tension, EV_readiness, EV_consensus, Vkon_mag, 
Vkon_norm, V_Ea, U, R, phi_score, U2, R2, phi_score2, cos_prevk, 
cos_day_centroid, cos_role_centroid_user, cos_role_centroid_assistant, 
G_phase, G_phase_norm, T_fog, I_eff

### Max Aggregations
Daily max for:
guardian_trip, mode_hp, symbolik_hit

### Sum Aggregations
Daily sum for:
EV_signal_local, guardian_trip

### Split Aggregations
Separate by role:
A_user, A_assistant, PCI_user, PCI_assistant

### Mode Aggregation
Most frequent:
evo_form → form_top

---

## COMPLETE! ALL FORMULAS SPECIFIED! 🏆

