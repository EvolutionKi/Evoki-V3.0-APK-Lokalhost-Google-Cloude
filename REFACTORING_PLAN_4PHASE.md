# 🔄 REFACTORING PLAN: metrics_calculator_4phase.py

**Ziel:** Vollständige Integration aller compute_mXX Funktionen aus calculator_spec_A_PHYS_V11.py

**Status:** PLANNING

---

## 📊 CURRENT STATE

### **calculator_spec_A_PHYS_V11.py:**
- **Size:** 1902 lines, 63KB
- **Functions:** ~168 compute_mXX functions
- **Structure:** Linear (keine Phasen-Trennung)

### **metrics_calculator_4phase.py:**
- **Size:** ~400 lines ❌ (sollte ~1900 lines sein!)
- **Functions:** Nur Orchestrator + vereinfachte Placeholders
- **Structure:** 4-Phasen Pipeline ✅

---

## 🎯 REFACTORING STRATEGY

### **OPTION A: Merge Into 4-Phase File** ⭐ EMPFOHLEN
```
metrics_calculator_4phase.py (1900+ lines):
├── All compute_mXX functions (copied from calculator_spec)
├── 4-Phase Orchestrator
└── Phase-specific calculation methods
```

**Pros:**
- ✅ Alle Funktionen an einem Ort
- ✅ Klare Phase-Zuordnung
- ✅ Einfacher zu warten

**Cons:**
- ❌ Große Datei (~2000 lines)

### **OPTION B: Keep Separate + Import** ❌ NICHT IDEAL
```
calculator_spec_A_PHYS_V11.py - All compute_mXX functions
metrics_calculator_4phase.py - Orchestrator (imports from spec)
```

**Pros:**
- ✅ Kleinere Dateien

**Cons:**
- ❌ Zirkuläre Abhängigkeiten möglich
- ❌ Unklare Phase-Zuordnung
- ❌ Doppelter Code

---

## ✅ ENTSCHEIDUNG: OPTION A

**Merge alles in metrics_calculator_4phase.py:**

1. ✅ Alle compute_mXX Funktionen kopieren (aus calculator_spec)
2. ✅ In 4 Phasen einordnen
3. ✅ Phase-Methoden aufrufen die richtigen Funktionen
4. ✅ calculator_spec als DEPRECATED markieren

---

## 📋 DETAILED IMPLEMENTATION PLAN

### **PHASE 1 FUNCTIONS (Lines ~200-600):**

```python
# TEXT ANALYSIS (Independent)
compute_m2_PCI(text)
compute_m3_gen_index(text)
compute_m4_flow(text)
compute_m5_coh(text)
compute_m10_angstrom(layers)
compute_m11_gap_s(t_prev, t_now)
compute_m18_s_entropy(tokens)

# LEXIKON SCANNING (Independent)
compute_m8_x_exist(text)
compute_m9_b_past(text, coh)
compute_m101_t_panic(text)  # TraumaLexika
compute_m102_t_disso(text)  # TraumaLexika
compute_m103_t_integ(text)  # TraumaLexika
compute_m104_t_shock(text)  # TraumaLexika
compute_m106_t_numb(text)
compute_m107_t_hurt(text)
compute_m108_t_fear(text)
compute_m109_t_rage(text)
compute_m151_hazard(text)   # HazardLexika (CRITICAL!)

# TOKEN ECONOMICS (Independent)
compute_m57_tokens_soc(...)
compute_m58_tokens_log(...)

# INTEGRITY (Simple, no dependencies)
compute_m36_rule_conflict(...)
compute_m37_xxx(...)
# ... m38-m55
```

**~30-40 functions**

---

### **PHASE 2 FUNCTIONS (Lines ~600-1000):**

```python
# CORE AFFEKT (Needs Phase 1: Lexika, PCI)
compute_m1_A(text, x_exist, b_past, pci)

# FLOW & STABILITY (Needs Phase 1: PCI, Coh)
# Already computed in Phase 1, just use values
compute_m6_ZLF(flow, coherence)

# TRAUMA SYNTHESIS (Needs Phase 1: individual trauma scores)
compute_m105_t_fog(m7_LL, m102_disso)

# ANDROMATIK (Needs Phase 1: Tokens, Phase 2: m1_A)
compute_m59_p_antrieb(tokens_soc, tokens_log)
compute_m56_surprise(...)

# PHI PROXY (Needs Phase 2: m1_A, Phase 1: PCI)
compute_m20_phi_proxy(A, PCI)

# FREE ENERGY (Needs Phase 2: m1_A, Phase 1: PCI)
compute_m61_u_fep(A, PCI)
# m62_r_fep - Will calculate in Phase 3 (needs z_prox)
# m63_phi - Will calculate in Phase 3

# GRADIENT (Needs previous metrics)
compute_m17_nabla_a(current_A, prev_A)

# EVOLUTION (Needs Phase 2: m1_A)
compute_m71_ev_resonance(...)
compute_m74_valence(A)
compute_m100_causal(PCI)
```

**~20-30 functions**

---

### **PHASE 3 FUNCTIONS (Lines ~1000-1400):**

```python
# A_PHYS ENGINE (Needs Phase 2: m1_A, Embeddings)
compute_m15_affekt_a(m1_A, embeddings, memories, danger_cache)

# PHYSICS OUTPUTS (Needs A_Phys)
compute_m21_xxx(...)
# ... m22-m35

# TODESNÄHE (CRITICAL! Needs Phase 2: m1_A, m15, Phase 1: m151, m101)
compute_m19_z_prox(m1_A, m15_affekt_a, m151_hazard, m101_panic)

# Update m7_LL with z_prox
compute_m7_LL(z_prox)

# FREE ENERGY r_fep (Needs Phase 3: z_prox, Phase 1: hazard)
compute_m62_r_fep(z_prox, hazard)
compute_m63_phi(u_fep, r_fep)

# BLACK HOLE (Needs Phase 3: z_prox, Phase 1: hazard)
compute_m110_black_hole(z_prox, hazard, t_panic, t_disso, text)

# INTEGRITY (Needs Physics, Trauma)
compute_m38_soul_integrity(b_vector)
compute_m39_soul_check(b_vector)
compute_m40_h_conv(...)
compute_m45_trust_score(h_conv, pacing, soul)
```

**~40-50 functions**

---

### **PHASE 4 FUNCTIONS (Lines ~1400-1800):**

```python
# OMEGA (Needs Phase 3: phi, Phase 2: rule_conflict)
compute_m151_omega(phi, rule_conflict, ...)

# FUTURE RISK (Needs Phase 1: hazard, Phase 2: A, Phase 1: t_panic, B_align)
compute_m160_F_risk(hazard, A, t_panic, b_align)

# CUMULATIVE STRESS (Needs History)
compute_m168_cum_stress(z_prox_history)

# COMMIT FLAG (Needs Phase 1: hazard, Phase 3: z_prox, Phase 4: omega)
compute_m161_commit(hazard, z_prox, omega)

# SYSTEM HEALTH (Needs Everything!)
compute_m152_a51_compliance(...)
compute_m153_health(...)
compute_m154_boot_status(...)

# META-COGNITION (m116-m150)
compute_m131_xxx(...)
# ... m132-m150

# REMAINING SYSTEM (m155-m167)
compute_m155_xxx(...)
# ... m156-m167
```

**~40-50 functions**

---

## 🔄 MIGRATION STEPS

### **Step 1: Copy ALL compute_mXX functions** ✅
```bash
# Extract all functions from calculator_spec
grep -n "^def compute_m" calculator_spec_A_PHYS_V11.py
```

### **Step 2: Reorganize into phases**
```python
# Add to metrics_calculator_4phase.py:

# =============================================================================
# PHASE 1: BASE METRIC FUNCTIONS
# =============================================================================

# [Copy functions here]

# =============================================================================
# PHASE 2: DERIVED METRIC FUNCTIONS
# =============================================================================

# [Copy functions here]

# ... etc
```

### **Step 3: Update phase calculation methods**
```python
def _calculate_phase1_base(self, text, role, context):
    m = {}
    
    # Call REAL functions (not placeholders!)
    m["m2_PCI"] = compute_m2_PCI(text)
    m["m3_gen_index"] = compute_m3_gen_index(text)
    # ... etc
    
    return m
```

### **Step 4: Test each phase**
```python
# Test Phase 1 alone
phase1 = calc._calculate_phase1_base(text, "user", context)
assert "m2_PCI" in phase1
assert "m151_hazard" in phase1

# Test Phase 2 (needs Phase 1)
phase2 = calc._calculate_phase2_derived(text, "user", phase1, context)
assert "m1_A" in phase2

# ... etc
```

### **Step 5: Deprecate calculator_spec** ✅
```python
# Add to calculator_spec_A_PHYS_V11.py:
"""
⚠️ DEPRECATED!
Use metrics_calculator_4phase.py instead!

This file is kept for reference only.
"""
```

---

## 📊 EXPECTED FILE SIZE

```
metrics_calculator_4phase.py:
├── Imports & Helpers: ~100 lines
├── MetricsContext class: ~30 lines
├── Phase 1 functions: ~400 lines (30-40 funcs × 10 lines avg)
├── Phase 2 functions: ~300 lines (20-30 funcs × 10 lines avg)
├── Phase 3 functions: ~400 lines (40-50 funcs × 10 lines avg)
├── Phase 4 functions: ~400 lines (40-50 funcs × 10 lines avg)
├── MetricsCalculator class: ~200 lines (orchestrator)
└── Tests & Examples: ~100 lines

TOTAL: ~1930 lines ✅ (matches calculator_spec!)
```

---

## ✅ NEXT ACTION

**Jetzt implementieren:**
1. Alle Funktionen aus calculator_spec kopieren
2. In 4 Phasen reorganisieren
3. Orchestrator anpassen
4. Testen

**Estimated time:** 30-45 min

**Do it?** YES! ✅
