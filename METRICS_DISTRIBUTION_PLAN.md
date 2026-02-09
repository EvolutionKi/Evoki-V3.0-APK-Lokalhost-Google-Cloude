# 🗄️ EVOKI V3.0 - METRIKEN-VERTEILUNG NACH DATENBANK

**Prinzip:** Jede Metrik NUR in der Datenbank wo sie FUNKTIONAL hingehört!

---

## 📊 VERTEILUNGSPLAN

### **1. evoki_metadata.db** (STRUKTURELLE DATEN)
**Zweck:** Session-Verwaltung, Integrität, Basis-Identifikation

**Metriken:** KEINE! (Nur IDs, Hashes, Timestamps)

**Tables:**
- `sessions` - Session-Container
- `prompt_pairs` - User/AI Text-Paare
- `session_chain` - Blockchain Integrity
- `file_sources` - Quell-Dateien

---

### **2. evoki_resonance.db** (KERN-METRIKEN)
**Zweck:** Affekt, Resonanz, Evolution, Physics

**Metriken (m1-m100, B-Vektor):**

#### **CORE (m1-m20):**
```
m1_A          - Affekt-Score (CRITICAL!)
m2_PCI        - Prompt Complexity Index
m3_gen_index  - Generalization Index
m4_flow       - Flow State
m5_coh        - Coherence
m6_ZLF        - Zero-Loop Flag
m7_LL         - Lebens-Leitlinie (Trübung)
m8_x_exist    - Existenz-Marker
m9_b_past     - Vergangenheits-Belastung
m10_angstrom  - Ångström (Reflexionstiefe)
m11_gap_s     - Zeitlicher Gap
m12_lex_hit   - Lexikon Hit Count
m13_base_score - Base Score
m14_base_stability - Stabilität
m15_affekt_a  - A_Phys Affekt (V11)
m16_pci       - PCI Alias
m17_nabla_a   - Gradient Affekt
m18_s_entropy - Semantic Entropy
m19_z_prox    - Todesnähe (CRITICAL!)
m20_phi_proxy - Phi Integration Proxy
```

#### **PHYSICS (m21-m35):**
```
m21-m35 - A_Phys Engine Outputs
```

#### **INTEGRITY (m36-m55):**
```
m36_rule_conflict - Regelkonflikte
m38_soul_integrity - Seelen-Integrität
m45_trust_score - Vertrauens-Score
m36-m55 - Hyperphysics & Integrity
```

#### **ANDROMATIK (m56-m70):**
```
m56_surprise - Überraschung
m57_tokens_soc - Soziale Tokens
m58_tokens_log - Logische Tokens
m59_p_antrieb - Antrieb
m61_u_fep - Unsicherheit (Free Energy)
m62_r_fep - Risiko (Free Energy)
m63_phi - Φ (Ko-Evolution)
m56-m70 - Andromatik Spectrum
```

#### **EVOLUTION (m71-m100):**
```
m71_ev_resonance - Evolution Resonanz
m74_valence - Valenz
m100_causal - Kausal-Metrik
m71-m100 - Evolution & Grain
```

#### **B-VEKTOR (7D Soul):**
```
B_life    - Lebenswille
B_truth   - Wahrheit
B_depth   - Tiefe
B_init    - Initiative
B_warmth  - Wärme
B_safety  - Sicherheit (CRITICAL!)
B_clarity - Klarheit
B_align   - Gesamt-Ausrichtung
```

**Tables:**
- `core_metrics` - m1-m20 (pro User/AI)
- `physics_metrics` - m21-m35
- `integrity_metrics` - m36-m55
- `andromatik_metrics` - m56-m70
- `evolution_metrics` - m71-m100
- `b_state_evolution` - B-Vektor Historie
- `gradient_analysis` - ∇A, ∇B, Disharmony

---

### **3. evoki_triggers.db** (TRAUMA & HAZARD)
**Zweck:** Safety, Guardian Protocol, Crisis Detection

**Metriken (m101-m115, m151, m160):**

#### **TRAUMA (m101-m115):**
```
m101_T_panic  - Panik (CRITICAL!)
m102_T_disso  - Dissoziation
m103_T_integ  - Integration
m104_T_shock  - Schock
m105_T_fog    - Nebel
m110_black_hole - Schwarzes Loch
m101-m115 - Trauma Spectrum
```

#### **HAZARD (m151, m160):**
```
m151_hazard - Hazard Score (CRITICAL!)
m160_F_risk - Future Risk
```

**Tables:**
- `trauma_metrics` - m101-m115 (User only!)
- `hazard_events` - m151, m160 Events
- `lexikon_matches` - Welche Begriffe triggerten
- `personal_trauma_markers` - Gelernte Trigger
- `crisis_patterns` - Muster-Erkennung
- `safety_interventions` - Guardian Actions

---

### **4. evoki_metapatterns.db** (META-COGNITION & SYSTEM)
**Zweck:** System-Metriken, Meta-Kognition, Linguistic Analysis

**Metriken (m116-m168, außer m151/m160):**

#### **META-COGNITION (m116-m150):**
```
m131-m150 - Meta-kognitive Metriken
m116-m130 - Schema A/B Dual-Interpretation
```

#### **SYSTEM (m152-m168):**
```
m152_a51_compliance - A51 Integrität
m153_health - System Health
m154_boot_status - Boot Status
m161_commit - Commit/Alert Flag
m168_cum_stress - Kumulativer Stress
m152-m168 - System & Monitoring
```

**Tables:**
- `meta_cognition_metrics` - m116-m150
- `system_metrics` - m152-m168
- `user_vocabulary` - Wortschatz
- `metaphors` - Metaphern
- `themes` - Themen
- `ngrams` - N-Gramme
- `speech_patterns` - Sprach-Muster
- `semantic_fingerprint` - Linguistisches Profil

---

### **5. evoki_v3_graph.db** (RELATIONSHIPS)
**Zweck:** Semantischer Graph, Cluster, Pfade

**Metriken:** Denormalisiert (Kopien für Graph-Queries)
```
user_m1_A
user_m151_hazard
ai_m1_A
ai_m161_commit
disharmony_score
```

**Tables:**
- `graph_nodes` - Knoten mit denormalisierten Metriken
- `graph_edges` - Kanten mit Similarity
- `graph_clusters` - Themen-Cluster
- `graph_paths` - Vorberechnete Pfade

---

## 🔄 DATENFLUSS

### **INGESTION:**
```
1. Parse → prompt_pairs (metadata DB)
   
2. Calculate ALL 168 metrics
   
3. SPLIT by function:
   ├── m1-m100 + B-Vector → resonance DB
   ├── m101-m115 + m151 + m160 → triggers DB
   └── m116-m168 (rest) → metapatterns DB
   
4. Build graph nodes (copy critical metrics) → graph DB
```

### **QUERIES:**

**"Wie war mein Affekt gestern?"**
```sql
-- Query resonance DB
SELECT user_m1_A FROM core_metrics 
WHERE timecode BETWEEN X AND Y
```

**"Gab es Hazard Events?"**
```sql
-- Query triggers DB
SELECT * FROM hazard_events 
WHERE hazard_level = 'critical'
```

**"Welche Themen hatte ich?"**
```sql
-- Query graph DB
SELECT cluster_label, node_count 
FROM graph_clusters
ORDER BY node_count DESC
```

---

## ✅ VORTEILE

### **1. PERFORMANCE:**
- Kleinere Tabellen = schnellere Queries
- Indices nur wo nötig
- Graph-Queries isoliert von Metrik-Berechnungen

### **2. SICHERHEIT:**
- Trauma-Metriken isoliert in triggers DB
- Kann feiner gesteuert werden (Zugriff, Backup)

### **3. SKALIERUNG:**
- Metapatterns DB kann wachsen ohne Core zu verlangsamen
- Graph DB kann separat optimiert werden

### **4. LOGIK:**
- Jede Metrik in der DB wo sie FUNKTIONAL hingehört!
- Keine Vermischung von Concerns

---

## 📋 NÄCHSTE SCHRITTE

1. ✅ Schemas pro DB mit RICHTIGEN Metriken erstellen
2. ✅ Builder-Script anpassen (split metrics by function)
3. ✅ ALLE 168 Metriken korrekt berechnen
4. ✅ Tests für jede DB einzeln

**Kein vereinfachtes Spektrum - ALLE 168 da, aber RICHTIG verteilt!** 🎯
