# 🔄 EVOKI V3.0 - METRIKEN CALCULATION ORDER

**CRITICAL:** Metriken können NICHT parallel berechnet werden!  
**Grund:** Abhängigkeiten (Dependencies) zwischen Metriken!

---

## 📊 CALCULATION PIPELINE (4 PHASEN)

### **PHASE 1: BASE METRICS** (Unabhängig vom Text)
**Input:** Raw Text  
**Dependencies:** KEINE  
**Order:** Beliebig parallel

```python
# Diese können ZUERST berechnet werden:

# 1.1 TEXT BASICS
m11_gap_s         # Zeit seit letztem Prompt (Delta)
m57_tokens_soc    # Token Count (Social)
m58_tokens_log    # Token Count (Logical)

# 1.2 LEXIKON SCANNING (Parallel möglich)
m12_lex_hit       # Lexikon Hit Count
m8_x_exist        # X_EXIST Lexikon
m9_b_past         # B_PAST Lexikon
m101_T_panic      # T_PANIC Lexikon
m102_T_disso      # T_DISSO Lexikon
m103_T_integ      # T_INTEG Lexikon
m104_T_shock      # T_SHOCK Lexikon
m151_hazard       # HAZARD Lexikon (Suicide/Self-Harm/Crisis)

# 1.3 TEXT ANALYSIS
m2_PCI            # Prompt Complexity Index
m3_gen_index      # Generalization Index
m5_coh            # Coherence
m18_s_entropy     # Semantic Entropy
m10_angstrom      # Ångström (aus PCI)
```

**Output Phase 1:**
- Alle Lexikon-basierten Scores
- Alle Text-Statistiken
- Token Counts

---

### **PHASE 2: DERIVED METRICS** (Brauchen Phase 1)
**Input:** Phase 1 Outputs  
**Dependencies:** Phase 1  
**Order:** Muss NACH Phase 1!

```python
# 2.1 CORE AFFEKT (braucht Lexika)
m1_A              # Affekt = f(X_EXIST, B_PAST, Lexika)

# 2.2 FLOW & STABILITY (brauchen PCI, Coherence)
m4_flow           # Flow = f(PCI, Coherence)
m13_base_score    # = flow * coh
m14_base_stability # = 1 - LL

# 2.3 TRÜBUNG (braucht andere Metriken)
m7_LL             # Lebens-Leitlinie (Trübung) = f(z_prox, T_panic)

# 2.4 LOOP DETECTION (braucht PCI, History)
m6_ZLF            # Zero-Loop Flag = f(PCI, Repetition)

# 2.5 ANDROMATIK (braucht Tokens, Affekt)
m59_p_antrieb     # = (tokens_soc + tokens_log) / 200
m56_surprise      # = |Random - A|

# 2.6 PHI PROXY (braucht A, PCI)
m20_phi_proxy     # = A * PCI

# 2.7 TRAUMA SYNTHESIS (braucht einzelne Trauma-Lexika)
m105_t_fog        # = (LL + T_disso) / 2
```

**Output Phase 2:**
- m1_A (CRITICAL!)
- Flow, Stability
- Antrieb, Surprise

---

### **PHASE 3: PHYSICS & COMPLEX METRICS** (Brauchen Phase 1+2)
**Input:** Phase 1 + 2 Outputs  
**Dependencies:** m1_A, Lexika, PCI  
**Order:** Muss NACH Phase 2!

```python
# 3.1 A_PHYS ENGINE (braucht m1_A, Embeddings, Historie)
m15_affekt_a      # A_Phys V11 Affekt = f(m1_A, Resonance, Danger)
m21-m35           # Physics Outputs (Resonance, Danger, etc.)

# 3.2 FREE ENERGY PRINCIPLE (braucht A, Lexika)
m61_u_fep         # Unsicherheit = A * 0.4 + PCI * 0.3
m62_r_fep         # Risiko = z_prox * 0.4 + Hazard * 0.5
m63_phi           # Φ = u_fep - r_fep (Ko-Evolution!)

# 3.3 TODESNÄHE (braucht A, Hazard, Trauma!)
m19_z_prox        # z_prox = f(m1_A, m15_affekt_a, m151_hazard, m101_T_panic)
                  # CRITICAL: Safety Override bei Hazard > 0.5!

# 3.4 BLACK HOLE (braucht Trauma-Metriken!)
m110_black_hole   # = z_prox * Hazard (+ Lexikon Veto Logic)

# 3.5 INTEGRITY (braucht Physics, Trauma)
m36_rule_conflict # Regelkonflikte
m38_soul_integrity # = B_safety
m45_trust_score   # = B_safety * 0.9

# 3.6 EVOLUTION (braucht A, PCI, Historie)
m71_ev_resonance  # = B_safety
m74_valence       # = A
m100_causal       # = PCI
```

**Output Phase 3:**
- m19_z_prox (CRITICAL!)
- A_Phys Outputs (m15, m21-m35)
- Φ (Ko-Evolution)
- Black Hole Score

---

### **PHASE 4: SYNTHESIS & SYSTEM** (Brauchen ALLES)
**Input:** Phase 1 + 2 + 3 Outputs  
**Dependencies:** Fast alle vorherigen Metriken  
**Order:** Muss ZULETZT!

```python
# 4.1 OMEGA (braucht Φ, Rule Conflicts!)
m151_omega        # = φ - (rule_conflict * 1.5)

# 4.2 FUTURE RISK (braucht Hazard, A, T_panic, Omega)
m160_F_risk       # = Hazard * 0.8 + (1 - A) * 0.2
                  # ODER: F_risk = f(T_panic, Omega, B_align) (komplexe Formel)

# 4.3 GRADIENT ANALYSIS (braucht Historie!)
m17_nabla_a       # = Δ A zum Vorgänger

# 4.4 STRESS ACCUMULATION (braucht Historie!)
m168_cum_stress   # = Σ z_prox über Zeit

# 4.5 COMMIT FLAG (braucht Hazard, z_prox, Omega)
m161_commit       # = "alert" if (Hazard > 0.8 OR z_prox > 0.65) else "commit"

# 4.6 SYSTEM HEALTH (braucht ALLES!)
m152_a51_compliance # Genesis Anchor Check
m153_health       # System Health = f(Coverage, Integrity)
m154_boot_status  # Boot Status
```

**Output Phase 4:**
- Omega (Final Integration)
- F_risk (Future Prediction)
- System Status
- Commit/Alert Decision

---

## 🔗 DEPENDENCY GRAPH (Vereinfacht)

```
PHASE 1 (Base)
├── Text → PCI, Tokens, Coherence
├── Lexika → m101, m102, m151, m8, m9
└── Stats → m11, m18

↓

PHASE 2 (Derived)
├── m1_A ← [Lexika, PCI]
├── m4_flow ← [PCI, Coherence]
├── m7_LL ← [z_prox (preliminary), T_panic]
├── m59_p_antrieb ← [Tokens]
└── m63_phi ← [m61_u_fep, m62_r_fep]

↓

PHASE 3 (Physics)
├── m15_affekt_a ← [m1_A, Embeddings, Historie]
├── m19_z_prox ← [m1_A, m15_affekt_a, m151_hazard, m101_T_panic] ⚠️ CRITICAL!
├── m110_black_hole ← [m19_z_prox, m151_hazard, Lexikon]
└── m21-m35 (Physics) ← [m1_A, m15_affekt_a, Vektoren]

↓

PHASE 4 (Synthesis)
├── m151_omega ← [m63_phi, m36_rule_conflict]
├── m160_F_risk ← [m151_hazard, m1_A, m101_T_panic, B_align]
└── m161_commit ← [m151_hazard, m19_z_prox, m151_omega]
```

---

## ⚠️ CRITICAL DEPENDENCIES

### **1. m19_z_prox (Todesnähe)**
```python
# MUSS berechnet werden NACH:
# - m1_A (Phase 2)
# - m15_affekt_a (Phase 3)
# - m151_hazard (Phase 1)
# - m101_T_panic (Phase 1)

def compute_m19_z_prox(m1_A, m15_affekt_a, m151_hazard, m101_T_panic):
    # SAFETY OVERRIDE!
    if m151_hazard > 0.5:
        return min(1.0, m151_hazard * 1.2)  # Force high z_prox
    
    # Normal Berechnung
    base = (1.0 - m1_A) * 0.4
    affekt_push = (1.0 - m15_affekt_a) * 0.3
    panic_push = m101_T_panic * 0.3
    
    return min(1.0, base + affekt_push + panic_push)
```

### **2. m110_black_hole (Schwarzes Loch)**
```python
# MUSS berechnet werden NACH:
# - m19_z_prox (Phase 3)
# - m151_hazard (Phase 1)
# - m101_T_panic (Phase 1)
# - m102_T_disso (Phase 1)

def compute_m110_black_hole(z_prox, hazard, t_panic, t_disso, lexika):
    # Weighted combination
    base = z_prox * 0.4 + hazard * 0.4 + t_panic * 0.2
    
    # Lexikon Veto (wenn Hilfe-Anfragen erkannt)
    if has_help_requests(lexika):
        base *= 0.5  # Reduce black hole wenn Hilfe gesucht wird
    
    return min(1.0, base)
```

### **3. m160_F_risk (Future Risk)**
```python
# MUSS berechnet werden NACH:
# - m151_hazard (Phase 1)
# - m1_A (Phase 2)
# - m101_T_panic (Phase 1)
# - B_align (aus B-Vektor)

def compute_m160_F_risk(hazard, A, t_panic, b_align):
    # Komplexe Formel aus Spec
    hazard_component = hazard * 0.5
    affekt_component = (1.0 - A) * 0.2
    trauma_component = t_panic * 0.2
    stability_component = (1.0 - b_align) * 0.1
    
    return min(1.0, hazard_component + affekt_component + 
               trauma_component + stability_component)
```

---

## 🔄 IMPLEMENTATION STRATEGY

### **Option A: Sequential Pipeline**
```python
class MetricsCalculator:
    def calculate_all(self, text: str, context: dict) -> dict:
        # PHASE 1: Base
        phase1 = self.calculate_phase1_base(text)
        
        # PHASE 2: Derived (needs phase1)
        phase2 = self.calculate_phase2_derived(text, phase1, context)
        
        # PHASE 3: Physics (needs phase1 + phase2)
        phase3 = self.calculate_phase3_physics(text, phase1, phase2, context)
        
        # PHASE 4: Synthesis (needs all)
        phase4 = self.calculate_phase4_synthesis(phase1, phase2, phase3, context)
        
        # Merge all
        return {**phase1, **phase2, **phase3, **phase4}
```

### **Option B: Topological Sort (Dependency Graph)**
```python
class MetricsDAG:
    def __init__(self):
        self.dependencies = {
            'm1_A': ['m8_x_exist', 'm9_b_past', 'm2_PCI'],
            'm19_z_prox': ['m1_A', 'm15_affekt_a', 'm151_hazard', 'm101_T_panic'],
            'm110_black_hole': ['m19_z_prox', 'm151_hazard', 'm101_T_panic'],
            'm160_F_risk': ['m151_hazard', 'm1_A', 'm101_T_panic', 'B_align'],
            # ... etc
        }
    
    def calculate_in_order(self, text: str) -> dict:
        # Topological sort of dependency graph
        order = self.topological_sort()
        
        results = {}
        for metric_name in order:
            # Calculate metric (dependencies already in results)
            results[metric_name] = self.calculate_metric(metric_name, results)
        
        return results
```

---

## ✅ KONSEQUENZEN FÜR ARCHITEKTUR

### **1. Calculation Module Struktur:**
```python
backend/core/evoki_metrics_v3/
├── phase1_base.py         # m1-m20 (unabhängig)
├── phase2_derived.py      # Braucht Phase 1
├── phase3_physics.py      # Braucht Phase 1+2
├── phase4_synthesis.py    # Braucht Phase 1+2+3
└── calculator.py          # Orchestrator
```

### **2. Database Schema muss warten bis ALLE berechnet:**
```python
# NICHT:
for metric in all_metrics:
    calculate(metric)  # FALSCH! Dependencies!

# SONDERN:
metrics = calculator.calculate_all_phases(text, context)
# DANN:
db.insert_metrics(metrics)
```

### **3. T4 Backfill muss Phasen respektieren:**
```python
# Für JEDES Prompt-Paar:
1. Load context (previous metrics, embeddings)
2. Calculate Phase 1 (base)
3. Calculate Phase 2 (derived from Phase 1)
4. Calculate Phase 3 (physics from Phase 1+2)
5. Calculate Phase 4 (synthesis from all)
6. Store in appropriate DBs
```

---

## 🎯 NEXT STEPS

1. ✅ **calculator_spec_A_PHYS_V11.py** analysieren für exakte Dependencies
2. ✅ Dependency Graph vollständig dokumentieren
3. ✅ 4-Phasen Calculator implementieren
4. ✅ Tests für jede Phase einzeln
5. ✅ Backfill-Script mit richtiger Order

**KEINE vereinfachte Struktur - ALLE 168 Metriken in RICHTIGER REIHENFOLGE!** 🎯
