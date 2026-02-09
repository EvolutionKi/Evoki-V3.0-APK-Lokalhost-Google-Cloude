# 🎯 MASTER IMPLEMENTATION PLAN - ALLE 168 METRIKEN

**Datum:** 2026-02-07 22:51  
**Quelle:** EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md  
**Approach:** SYSTEMATISCH von m1 bis m168

---

## 📚 BÜCHER-STRUKTUR

### ✅ GRAIN ENGINE (m96-m100) - FERTIG
- **Status:** 5/5 Tests passed, SPEC-verified
- **Datei:** `grain_engine.py` (195 lines)
- **Test:** `test_grain_engine.py` (175 lines)

### 📖 BUCH 1: CORE METRICS (m1-m20)
**Spec:** Zeile 1891-3500  
**Metriken:**
- m1_A - Affekt Score
- m2_PCI - Perturbational Complexity
- m3_gen_index - Generativity
- m4_flow - Flow State
- m5_coh - Coherence
- m6_ZLF - Zero Loop Flag
- m7_LL - Lambert Light (Turbidity)
- m8_x_exist - Existenz-Axiom
- m9_b_past - Vergangenheits-Bezug
- m10_angstrom - Ångström Wellenlänge
- m11_gap_s - Zeit-Lücke
- m12_lex_hit - Lexikalischer Treffer
- m13_base_score - Fundamental Basis
- m14_base_stability - System-Stabilität
- m15_affekt_a - Affekt A (Alias)
- m16_pci - PCI (Alias)
- m17_nabla_a - Gradient von A
- m18_s_entropy - Shannon Entropy
- m19_z_prox - Z-Proximity (Todesnähe) ⚠️ SAFETY
- m20_phi_proxy - Phi Bewusstsein

**Status:** 🔜 TODO  
**Priority:** P0 (Core Foundation)

### 📖 BUCH 2: PHYSICS & GRAVICEPTION (m21-m35)
**Spec:** Zeile ~3500-4500  
**Metriken:** 15 Physics-Metriken  
**Status:** 🔜 TODO  
**Priority:** P1

### 📖 BUCH 3: HYPERMETRICS & DYADE (m36-m55)
**Spec:** Zeile ~4500-5500  
**Metriken:** 20 Hypermetriken  
**Status:** 🔜 TODO  
**Priority:** P1

### 📖 BUCH 4: ANDROMATIK & FEP (m56-m70)
**Spec:** Zeile ~5500-5900  
**Metriken:** 15 FEP/Drive Metriken  
**Status:** 🔜 TODO  
**Priority:** P1

### 📖 BUCH 5: EVOLUTION (m71-m73)
**Spec:** Zeile ~5900-6000  
**Metriken:** 3 Evolution-Metriken  
**Status:** 🔜 TODO  
**Priority:** P2

### 📖 BUCH 6: SENTIMENT & EVOLUTION (m74-m100)
**Spec:** Zeile ~6000-6500  
**Metriken:** 27 Sentiment Metriken (Dual-Schema)  
**Status:** ✅ m96-m100 COMPLETE, m74-m95 TODO  
**Priority:** P1

### 📖 BUCH 7: TRAUMA & TURBIDITY (m101-m115)
**Spec:** Zeile ~6500-7500  
**Metriken:** 15 Trauma/Safety Metriken  
**Includes:** m110_black_hole ⚠️ SAFETY-CRITICAL  
**Status:** 🔜 TODO  
**Priority:** P0 (Safety)

### 📖 BUCH 8: META-COGNITION (m116-m150)
**Spec:** Zeile ~7500-8500  
**Metriken:** 35 Meta-Cognition Metriken  
**Includes:** m116_lix (Readability)  
**Status:** 🔜 TODO  
**Priority:** P2

### 📖 BUCH 9: OMEGA & SYNTHESIS (m151-m161)
**Spec:** Zeile ~8500-9000  
**Metriken:** 11 Synthesis Metriken  
**Includes:** m161_commit_action (Executive)  
**Status:** 🔜 TODO  
**Priority:** P2

### 📖 BUCH 10: CONTEXT & EXTENDED (m162-m168)
**Spec:** Zeile ~9000-9200  
**Metriken:** 7 Context/Safety Metriken  
**Includes:** m168_cum_stress (Guardian)  
**Status:** 🔜 TODO  
**Priority:** P2

---

## 🚀 IMPLEMENTATION STRATEGY

### PHASE 1: Core Foundation (m1-m20) ⭐ JETZT
**Warum zuerst?**
- Alle anderen Metriken referenzieren Core-Metriken
- m1_A und m2_PCI sind Basis für fast alles
- Ohne Core keine sinnvollen Tests möglich

**Approach:**
1. Erstelle `core_metrics.py`
2. Implementiere m1-m20 Schritt für Schritt
3. Teste gegen Spec-Beispiele
4. Validiere Ranges [0, 1]

**Estimated Time:** 2-3h

### PHASE 2: Safety-Critical (m19, m110, m168) ⚠️
**Warum wichtig?**
- m19_z_prox = Todesnähe (Guardian Trigger)
- m110_black_hole = Context-Aware Veto
- m168_cum_stress = Schleichende Destabilisierung

**Approach:**
1. Safety-Metriken separat in `safety_metrics.py`
2. Golden Tests mit bekannten Krisen-Texten
3. Guardian Integration vorbereiten

**Estimated Time:** 1-2h

### PHASE 3: Physics & FEP (m21-m70)
**Foundation für:**
- Chaos/Energie-Berechnung
- Drive-System (Andromatik)
- Retrieval-Modulation

**Estimated Time:** 3-4h

### PHASE 4: Rest (m71-m168)
**Systematisch:**
- Buch für Buch
- Immer mit Tests
- Contract-Compliance prüfen

**Estimated Time:** 6-8h

---

## 📊 PROGRESS TRACKER

| Kategorie | Total | Done | % | Status |
|-----------|-------|------|---|--------|
| Core (m1-m20) | 20 | 0 | 0% | 🔜 NEXT |
| Physics (m21-m35) | 15 | 0 | 0% | 🔜 |
| Hypermetrics (m36-m55) | 20 | 0 | 0% | 🔜 |
| Andromatik (m56-m70) | 15 | 0 | 0% | 🔜 |
| Evolution (m71-m73) | 3 | 0 | 0% | 🔜 |
| Sentiment (m74-m100) | 27 | 5 | 19% | 🟡 |
| Trauma (m101-m115) | 15 | 0 | 0% | 🔜 |
| Meta-Cog (m116-m150) | 35 | 0 | 0% | 🔜 |
| Synthesis (m151-m161) | 11 | 0 | 0% | 🔜 |
| Context (m162-m168) | 7 | 0 | 0% | 🔜 |
| **TOTAL** | **168** | **5** | **3%** | 🟡 |

---

## 🎯 NEXT STEPS

### JETZT: Core Metrics m1-m5
1. Erstelle `core_metrics.py`
2. Implementiere:
   - m1_A (Affekt)
   - m2_PCI (Complexity)
   - m3_gen_index (Generativity)
   - m4_flow (Flow State)
   - m5_coh (Coherence)
3. Teste gegen Spec-Beispiele
4. **Estimated:** 45 min

### DANN: Core Metrics m6-m10
5 weitere Critical-Path Metriken

### DANACH: Core Metrics m11-m20
Vervollständige Core Foundation

---

**READY TO START:** Core Metrics (m1-m5)  
**USER APPROVAL:** Soll ich starten? 🚀
