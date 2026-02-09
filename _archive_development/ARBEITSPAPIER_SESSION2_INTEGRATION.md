# ARBEITSPAPIER - SESSION 2 (INTEGRATION & TESTING)

**Datum:** 2026-02-08 00:00  
**Agent:** Session 2 (Nach 100%+ Extraction)  
**Status:** Integration Phase

---

## 🎯 ERKENNTNISSE AUS BRAIN-DOKUMENTEN

### **1. EXECUTION ORDER IST KRITISCH! (Phase 3a!)**

**PROBLEM:** Ich dachte Metriken werden linear m1→m168 berechnet.  
**WAHRHEIT:** 6 PHASEN mit **kritischer Safety-Gate VORHER!**

```python
EXECUTION_PHASES = {
    1: "ANALYSIS",      # Text-Stats, Grain, m116
    2: "CORE",          # m1-m20
    "3a": "TRAUMA_PRE", # ⚠️ VOR RAG! T_panic/T_disso
    "3b": "CONTEXT",    # RAG m142 mit Safety-Mode
    4: "TRAUMA_FULL",   # m101-m115
    5: "DYNAMICS",      # m56-m70 (Andromatik)
    6: "SYNTHESIS",     # m151-m161 (Omega)
}
```

**WARUM Phase 3a SO wichtig?**
```python
# Phase 3a - TRAUMA PRE-SCAN
t_panic_pre = compute_m101_t_panic(text)
t_disso_pre = compute_m102_t_disso(text)

# Safety Check für RAG
if t_panic_pre > 0.6 or t_disso_pre > 0.6:
    rag_mode = "SAFE_MODE"  # NUR beruhigende Anker!
else:
    rag_mode = "FULL_RECALL"  # Volle Erinnerung
```

**Das verhindert:** RAG lädt traumatisierende Erinnerungen während User in Panik ist!

---

### **2. DUAL-SCHEMA DATENBANK (m116-m150)**

**PROBLEM:** Metriken m116-m150 haben **ZWEI BEDEUTUNGEN**!

**Schema A:** Text-Werte (z.B. "m", "l", "s" für Lesbarkeit)  
**Schema B:** Numerische Scores (0.0-1.0)

**❌ FALSCH:**
```sql
m116 TEXT  -- Mischen? "m" oder 0.7?!
```

**✅ RICHTIG:**
```sql
m116_lix REAL,      -- Schema A (Text Analytics)
m116_meta REAL,     -- Schema B (Meta-Cognition)
```

**CIRCA 50 Metriken** haben Dual-Schema!

---

### **3. LEXIKA SOURCE OF TRUTH**

**KRITISCH:** Lexika dürfen **NICHT** inline in Python sein!

**EINZIGE Source of Truth:**
```
app/deep_earth/lexika_v3.json
```

**Verboten:**
- ❌ Hardcoded Weights in Python
- ❌ Inline Dictionaries
- ❌ Fallback-Werte unterschiedlich zu JSON

**WARUM?** In V3.2.0: Python hatte `s_self["ich"] = 1.0`, JSON hatte `0.3` → Nach Neustart war Ego 70% schwächer!

---

### **4. TOKEN ECONOMY CLAMPING (m57/m58)**

**PROBLEM:** Token-Counts können unbegrenzt wachsen!

**LÖSUNG:**
```python
def update_tokens(current: float, delta: float) -> float:
    return max(0.0, min(100.0, current + delta))  # CLAMPING!
```

m60_delta_tokens kann negativ sein (Verbrauch) - korrekt!

---

### **5. LAMBDA DEPTH NORMALISIERUNG (m27)**

**PROBLEM:** Formel `token_count / 20.0` kann Werte > 1.0 erzeugen!

**LÖSUNG:**
```python
lambda_d = min(1.0, token_count / 100.0)  # Geclipped!
```

Für FEP-Berechnungen (m61) **MUSS** Wert normiert sein!

---

### **6. m161 COMMIT LOGIC - 3 STUFEN!**

**Nicht nur commit/reject!** Sondern **3 STUFEN:**

```python
if z_prox > 0.65: 
    return "alert"   # BLOCKIEREN!
elif z_prox > 0.50: 
    return "warn"    # Loggen aber senden
else:
    return "commit"  # Normal
```

---

### **7. m19 Z_PROX KONSISTENZ**

**PROBLEM:** m110 und andere re-calculieren z_prox implizit!

**LÖSUNG:** Explizit referenzieren:
```python
# ❌ FALSCH: chaos * (1-A) * LL
# ✅ RICHTIG: chaos * m19_z_prox  # Explicit reference
```

Spart Rechenzeit, erzwingt Konsistenz!

---

### **8. B-VECTOR - ZWEI VERSIONEN!**

**Version A:** backend/core/b_vector.py (127 lines, Diff-extract)  
**Version B:** evoki_pipeline/b_vector.py (85 lines, Original)

**ENTSCHEIDUNG:** **Version B nutzen!**

**WARUM?**
- vector_engine_v2_1.py erwartet `update()` Methode
- Version A hat `apply_feedback()` → Interface-Mismatch!
- Version B ist bewährt, kleiner, kompatibel

**ACTION:**
```bash
cp evoki_pipeline/b_vector.py → backend/core/b_vector.py
```

---

### **9. VECTOR_ENGINE_V2_1.PY - 1597 ZEILEN GOLD!**

**evoki_pipeline/vector_engine_v2_1.py:**
- 1597 Zeilen, 65KB
- Implementiert A29, A46, A49, A50, A51, A54, A62, A63, A65, A66, A67, H3.4!
- TRI-ANCHOR RETRIEVAL: Semantic + Hash + Tags + Affekt-Modulation
- B-Vektor Learning
- Genesis Anchor (HMAC-SHA256)
- Wächter-Veto

**KRITISCH:** Braucht `from b_vector import BVector`!

---

### **10. DUAL-GRADIENT SYSTEM (∇A / ∇B)**

**Das Herzstück:**
```
User sends Prompt
    ↓
[1] compute_user_metrics(prompt) → 168 Metriken
    ↓
AI generates Response
    ↓
[2] compute_ai_metrics(response) → 168 Metriken
    ↓
[3] Berechne ∇A, ∇B, |∇A - ∇B| → Disharmonie
    ↓
[4] Alerts:
    - ∇A < -0.15 → User-Affekt fällt!
    - |∇A - ∇B| > 0.3 → Disharmonie!
```

---

### **11. DATABASE SCHEMA - 5 DATENBANKEN**

```
evoki_v3_core.db         → prompt_pairs, metrics_full, b_state_evolution
evoki_v3_vectors.faiss   → 4 FAISS Namespaces
evoki_v3_graph.db        → Relationship-Graph
evoki_v3_keywords.db     → Lernendes Keyword-System
evoki_v3_analytics.db    → API-Logging, B-Vektor-Verifikation
evoki_v3_trajectories.db → Metrik-Trajektorien + Prädiktionen
```

---

### **12. FAISS - 4 NAMESPACES**

```
atomic_pairs        → Prompt-Paar Embeddings (384D)
context_windows     → Dynamische Fenster (5/15/25/50)
metrics_embeddings  → 322D Metriken-PCA
semantic_wpf        → Write-Process-Freeze Layer
```

---

### **13. HAZARD EVENTS - GUARDIAN PROTOCOL**

**hazard_events Table:**
- `hazard_type`: 'suicide', 'self_harm', 'crisis', 'panic', 'disso'
- `severity`: [0, 1]
- `is_critical`: Guardian Trip?
- `intervention_taken`: Boolean
- `intervention_type`: 'warning', 'block', 'emergency_contact'

---

### **14. REGELWERK V12 PATCHES (DIAMOND MASTER)**

**D-01:** Ångström-Normalisierung: `m10_norm = min(1.0, m10/5.0)`  
**D-02:** PCI Doppel-Bestrafung vermeiden  
**D-03:** Schema A/B Kollision (Explizite Suffixe)  
**D-04:** SQLite-Lock: `PRAGMA journal_mode=WAL`  
**D-05:** m35 Stagnations-Blindheit: Fallback `max(external, m6_ZLF)`

**m110 Black Hole V3.3.3:**
```python
if panic_hits >= 2:
    is_real_emergency = semantic_guardian.check_urgency(text)
    if is_real_emergency:
        return max(base, 0.85)  # Bestätigter Notfall
    else:
        return base + 0.1       # Nur leichter Malus
```

---

### **15. A_PHYS V11 PHYSICS**

```
A(v_c) = λ_R × R(v_c) − λ_D × D(v_c)

R(v_c) = Σ max(0, cos(v_c, v_i)) × r_i  (Resonanz)
D(v_c) = Σ exp(-K × d_f)                (Gefahr)
```

**Slot-Mapping:**
- m15_affekt_a = A_phys (primär)
- m28_phys_1 = A_phys_raw (debug)
- m29_phys_2 = A_legacy (fallback)
- m30_phys_3 = A29 guardian_trip (0/1)
- m31_phys_4 = danger_sum D(v_c)
- m32_phys_5 = resonance_sum R(v_c)

---

## 🚦 WAS ICH JETZT WEISS (TESTRESULTATE)

### ✅ **WAS FUNKTIONIERT:**

1. **calculator_spec_A_PHYS_V11.py** - ALLE 168 Metriken!
   - Import: ✅
   - m1_A("Hello") = 0.48 ✅
   - m101_t_panic("Panik!") = 1.0 ✅
   - m19_z_prox berechnet ✅
   - m161_commit entscheidet ✅

2. **lexika_complete.py** - 400+ Terms!
   - Import: ✅ (nach Fix!)
   - T_PANIC: 45 terms ✅
   - SUICIDE: 18 terms ✅
   - T_DISSO: 44 terms ✅

3. **Formeln sind DETERMINISTISCH!**
   - Gleicher Input → Gleicher Output ✅
   - Keine random.uniform() ✅

4. **Emotion Metrics (VAD + Plutchik):**
   - m77_joy = v + a - 1 ✅ (Formel korrekt!)
   - m80_fear berechnet ✅

5. **PCI Complexity:**
   - "ja ja ja" → 0.2 ✅
   - "Die philosophische..." → 0.64 ✅

### ⚠️ **WAS FEHLT:**

1. **SUICIDE Detection in z_prox!**
   - "Ich will nicht mehr leben" → z_prox = 0.008 ❌
   - SOLLTE: z_prox > 0.65 (ALERT!)
   - **BUG:** SUICIDE_MARKERS wird nicht in z_prox verwendet!

2. **Phasenweise Execution!**
   - calculator_spec berechnet linear ❌
   - SOLLTE: Phase 3a VOR RAG! ❌

3. **RAG Safety Gate!**
   - Kein SAFE_MODE implementiert ❌

4. **Dual-Schema Spalten!**
   - DB hat wahrscheinlich nicht m116_lix + m116_meta ❌

5. **Dual-Gradient System!**
   - Nur User-Metriken, keine AI-Metriken ❌
   - Kein ∇A, ∇B berechnet ❌

---

## 📋 NÄCHSTE SCHRITTE (MEIN PLAN)

### **PHASE 1: KRITISCHE BUGS FIXEN (30min)**

**1.1 Suicide Detection in z_prox:**
```python
# In compute_m19_z_prox():
suicide_score = lexical_match(text, LEXIKON_SUICIDE)
if suicide_score > 0.8:
    z_prox = max(z_prox, 0.75)  # Force critical!
```

**1.2 Phasenweise Execution wrapper:**
```python
def compute_all_metrics_phased(text: str, prev_text: str):
    results = {}
    
    # Phase 1: ANALYSIS
    results.update(compute_grain_metrics(text))
    results["m116_lix"] = compute_lix(text)
    
    # Phase 2: CORE
    results["m1_A"] = compute_m1_A(text)
    # ... m2-m20 ...
    
    # Phase 3a: TRAUMA PRE-SCAN (CRITICAL!)
    t_panic_pre = compute_m101_t_panic(text)
    t_disso_pre = compute_m102_t_disso(text)
    
    # Safety Gate
    if t_panic_pre > 0.6 or t_disso_pre > 0.6:
        rag_mode = "SAFE_MODE"
    else:
        rag_mode = "FULL_RECALL"
    
    # Phase 3b: CONTEXT (mit Safety!)
    results["m142_rag_align"] = run_rag(text, mode=rag_mode)
    
    # Phase 4-6: Rest...
    
    return results
```

### **PHASE 2: DB SCHEMA VERVOLLSTÄNDIGEN (1h)**

**2.1 Generate complete SQL:**
```python
# Generate ALL 168 metrics für metrics_full table
# user_m1_A ... user_m168_cum_stress
# ai_m1_A ... ai_m168_cum_stress
# delta_m1_A ... delta_m168
```

**2.2 Dual-Schema Spalten:**
```sql
-- m116-m150: Dual-Schema
m116_lix REAL,
m116_meta REAL,
-- ... (repeat for all dual-schema metrics)
```

### **PHASE 3: DUAL-GRADIENT IMPLEMENTIEREN (1h)**

**3.1 API Endpoint:**
```python
@app.post("/api/temple/analyze_pair")
def analyze_pair(user_text: str, ai_text: str):
    # User Metrics
    user_metrics = compute_all_metrics_phased(user_text, prev="")
    
    # AI Metrics
    ai_metrics = compute_all_metrics_phased(ai_text, prev=user_text)
    
    # Gradients
    delta_A_user = user_metrics["m1_A"] - prev_user_A
    delta_A_ai = ai_metrics["m1_A"] - prev_ai_A
    disharmony = abs(delta_A_user - delta_A_ai)
    
    # Alerts
    alerts = []
    if delta_A_user < -0.15:
        alerts.append("USER_AFFEKT_FALLING")
    if disharmony > 0.3:
        alerts.append("DISHARMONY_DETECTED")
    
    return {
        "user_metrics": user_metrics,
        "ai_metrics": ai_metrics,
        "gradients": {
            "delta_A_user": delta_A_user,
            "delta_A_ai": delta_A_ai,
            "disharmony": disharmony
        },
        "alerts": alerts
    }
```

### **PHASE 4: POPULIEREN & TESTEN (1h)**

**4.1 10,971 Prompts durchrechnen:**
```python
# Load text_lookup
conn = sqlite3.connect("evoki_pipeline/metric_chunks_test/text_index.db")
prompts = conn.execute("SELECT * FROM text_lookup LIMIT 1000").fetchall()

# Compute metrics
for msg_id, timecode, conv_date, speaker, text, text_length in prompts:
    metrics = compute_all_metrics_phased(text, prev="")
    
    # Insert into evoki_v3_core.db
    insert_metrics(msg_id, speaker, text, metrics)
```

**4.2 Frontend Test:**
```bash
cd app/interface
npm run dev
# Test Temple Tab mit ECHTEN Metriken!
```

---

## 🎯 PRIORITÄTS-ENTSCHEIDUNGEN

**FRAGE AN USER:**
1. Welche Phase ZUERST? A) Bugs fixen? B) DB Schema? C) Dual-Gradient?
2. ALLE 168 oder nur kritische?
3. DB Migration oder neue DB?
4. Welche Tests wichtigst?

**MEINE EMPFEHLUNG:**
1. ✅ **Bugs fixen** (Suicide, Phase 3a) — SAFETY FIRST!
2. ✅ **Dann DB Schema** vervollständigen
3. ✅ **Dann Dual-Gradient** implementieren
4. ✅ **Dann populieren** mit echten Daten

---

## 📊 AKTUELLE STATISTIKEN

**Extrahiert aus V7:**
- ✅ 18,609 Zeilen gelesen
- ✅ 10,167 Zeilen Code extrahiert
- ✅ 168 Metriken (nicht 172!)
- ✅ 400+ Lexikon-Terms
- ✅ calculator_spec: 1,875 lines
- ✅ a_phys_v11: 226 lines
- ✅ lexika_complete: 951 lines
- ✅ b_vector_system: 351 lines
- ✅ grain_engine: 195 lines (5/5 tests!)

**Tests bestanden:**
- ✅ calculator_spec imports
- ✅ lexika imports (nach Fix)
- ✅ Determinismus verified
- ✅ Panic detection works
- ✅ Z_prox calculates
- ✅ Commit logic works
- ✅ Emotions calculate
- ✅ PCI works

**Bekannte Bugs:**
- ⚠️ Suicide nicht in z_prox
- ⚠️ Keine phasenweise Execution
- ⚠️ Kein RAG Safety Gate
- ⚠️ Dual-Schema fehlt
- ⚠️ Dual-Gradient fehlt

---

## 🏆 MEILENSTEINE

**Session 1 (Vorgänger):**
- ❌ Oberflächlich gelesen
- ❌ Halluzinierte Lösungen
- ❌ Fake random values
- ❌ Nicht getestet

**Session 2 (ICH):**
- ✅ 18,609 Zeilen KOMPLETT gelesen
- ✅ 100%+ Coverage erreicht
- ✅ ECHTE Metriken extrahiert
- ✅ GETESTET (DEEP_VERIFICATION!)
- ✅ Brain-Dokumente analysiert
- ✅ Kritische Patterns identifiziert

**HEUTE ZIEL:**
- ⏰ Integration Phase abschließen
- ⏰ Bugs fixen
- ⏰ DB Schema complete
- ⏰ Dual-Gradient functional
- ⏰ Demo mit ECHTEN Daten!

---

**STATUS:** ✅ **READY TO INTEGRATE**  
**CONFIDENCE:** 🟢 **HIGH** (basierend auf Tests + Brain-Docs)

🚀
