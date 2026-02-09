# 🔍 SCHEMA ANALYSE: Was wird ALLES gespeichert?

**Frage:** Werden auch alle anderen Dinge wie Trigger-Worte, B-Vektoren etc. mit den Metriken abgespeichert?

---

## ✅ WAS IST BEREITS IM SCHEMA:

### 1. **METRIKEN** (metrics table)
```sql
-- 14 indexed metrics:
m1_A, m2_PCI, m19_z_prox, m101_t_panic, m151_hazard, F_risk, etc.

-- FULL 168 SPECTRUM (JSON):
metrics_json TEXT  -- {"m1_A": 0.653, "m2_PCI": 0.721, ..., "m168": 0.0}
```
✅ **Ja!** Alle Metriken werden gespeichert!

---

### 2. **B-VEKTOREN** (b_state_evolution table)
```sql
CREATE TABLE b_state_evolution (
    state_id INTEGER PRIMARY KEY,
    turn_id TEXT,
    
    -- 7D Soul Signature:
    B_life REAL,
    B_truth REAL,
    B_depth REAL,
    B_init REAL,
    B_warmth REAL,
    B_safety REAL,
    B_clarity REAL,
    B_align REAL,  -- Composite
    
    timestamp TEXT
);
```
✅ **Ja!** B-Vektoren werden getrackt!

---

### 3. **EMBEDDINGS** (embeddings table)
```sql
CREATE TABLE embeddings (
    turn_id TEXT PRIMARY KEY,
    model_id TEXT,
    dim INTEGER,
    vector_json TEXT,  -- [0.123, 0.456, ..., 0.789]
    created_at TEXT
);
```
✅ **Ja!** Semantic Vektoren werden gespeichert!

---

### 4. **HAZARD EVENTS** (hazard_events table)
```sql
CREATE TABLE hazard_events (
    event_id INTEGER PRIMARY KEY,
    turn_id TEXT,
    hazard_type TEXT,        -- 'SUICIDE_MARKER', 'Z_PROX_ALERT', etc.
    trigger_value REAL,
    action_taken TEXT,       -- 'ALERT_GUARDIAN', 'SAFE_MODE'
    timestamp TEXT
);
```
✅ **Ja!** Hazard-Ereignisse werden geloggt!

---

### 5. **GENESIS CHAIN** (genesis_chain table)
```sql
CREATE TABLE genesis_chain (
    id INTEGER PRIMARY KEY,
    ts_iso TEXT,
    prev_hash TEXT,
    content_hash TEXT,
    chain_hash TEXT
);
```
✅ **Ja!** Integrity chain wird tracked!

---

## ⚠️ WAS FEHLT NOCH:

### 1. **TRIGGER-WORTE** (welche konkret matched haben)
```sql
-- FEHLT:
CREATE TABLE lexikon_matches (
    match_id INTEGER PRIMARY KEY,
    turn_id TEXT,
    lexikon_name TEXT,    -- 'T_PANIC', 'HAZARD_SUICIDE', etc.
    matched_term TEXT,    -- 'umbringen', 'panik', etc.
    term_weight REAL,     -- 1.0, 0.9, etc.
    position INTEGER,     -- Wo im Text?
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);
```
❌ **Nein!** Trigger-Worte werden NICHT gespeichert - nur die Scores!

---

### 2. **A_PHYS TELEMETRY** (Resonanz, Gefahr, Top-Beiträge)
```sql
-- FEHLT:
CREATE TABLE a_phys_telemetry (
    turn_id TEXT PRIMARY KEY,
    A_phys REAL,
    A_phys_raw REAL,
    resonance REAL,
    danger REAL,
    a29_trip INTEGER,
    a29_max_sim REAL,
    a29_id TEXT,
    top_resonance_json TEXT,  -- Top 5 contributors
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);
```
❌ **Nein!** A_Phys Details werden NICHT gespeichert!

---

### 3. **CONTEXT METADATA** (was im Context war bei Berechnung)
```sql
-- FEHLT:
CREATE TABLE calculation_context (
    turn_id TEXT PRIMARY KEY,
    prev_turns_json TEXT,     -- Was war im Context?
    active_memories_count INTEGER,
    danger_zone_count INTEGER,
    physics_ctx_available INTEGER,
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);
```
❌ **Nein!** Calculation Context wird NICHT gespeichert!

---

### 4. **DUAL-GRADIENT ANALYSIS** (User vs AI Metriken)
```sql
-- FEHLT:
CREATE TABLE gradient_analysis (
    analysis_id INTEGER PRIMARY KEY,
    user_turn_id TEXT,
    ai_turn_id TEXT,
    nabla_A REAL,
    nabla_z_prox REAL,
    nabla_hazard REAL,
    disharmony REAL,
    recommended_action TEXT,
    FOREIGN KEY(user_turn_id) REFERENCES turns(turn_id),
    FOREIGN KEY(ai_turn_id) REFERENCES turns(turn_id)
);
```
❌ **Nein!** Gradient-Analyse wird NICHT gespeichert!

---

## 🎯 ZUSAMMENFASSUNG:

### ✅ **WIRD GESPEICHERT:**
1. Alle 168 Metriken (JSON + indexed)
2. B-Vektoren (7D Soul Signature)
3. Embeddings (Semantic Vectors)
4. Hazard Events
5. Genesis Chain
6. Session/Turn Metadaten

### ❌ **WIRD NICHT GESPEICHERT:**
1. **Trigger-Worte** (welche konkret matched)
2. **A_Phys Telemetry** (Resonanz, Gefahr Details)
3. **Context Metadata** (was war aktiv bei Berechnung)
4. **Dual-Gradient** (User-AI Deltas)
5. **Lexikon-Matches** (welche Terms gefunden)

---

## 💡 EMPFEHLUNG:

### **Option A: MINIMAL (wie jetzt)**
- Nur Scores speichern
- Trigger-Worte können aus Text + Lexika rekonstruiert werden
- **Vorteil:** Kleiner DB, schnell
- **Nachteil:** Weniger Debug-Info

### **Option B: FULL DEBUG**
- Speichere ALLES (Trigger, A_Phys, Context, Gradient)
- **Vorteil:** Maximale Transparenz & Debugging
- **Nachteil:** Große DB, komplex

### **Option C: HYBRID (empfohlen!)**
- Speichere nur KRITISCHE Debug-Info:
  - Lexikon_matches für m151_hazard > 0.5 (nur bei Alerts!)
  - A_Phys Telemetry wenn a29_trip = true
  - Gradient nur wenn disharmony > threshold
- **Vorteil:** Best of both worlds!

---

## 🚀 FRAGE AN DICH:

**Welche Option willst du?**

1. **A: Minimal** (wie jetzt - nur Scores)
2. **B: Full Debug** (alles speichern)
3. **C: Hybrid** (nur kritische Debug-Info)

**Oder:** Soll ich einfach mit A weitermachen und später erweitern?
