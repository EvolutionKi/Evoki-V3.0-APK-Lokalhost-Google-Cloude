# 📚 SPEC FINAL7 — MASTER REFERENCE (BUCH 7 EXTRAKT)

**Source:** `EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md`  
**Version:** V3.3.2 DIAMOND MASTER  
**Total Lines:** 18,609  
**Created:** 2026-02-08  
**Zweck:** PERMANENTE REFERENZ damit ich BUCH 7 nie wieder vergesse!

---

## 🎯 KERN-PRINZIPIEN (NIEMALS VERGESSEN!)

### 1. **REVERSIBILITY PRINCIPLE** (KERN-GESETZ!)

```
FORWARD:  x = 1 + 1 + 1 + 1 + 1 = 5
BACKWARD: 5 - 1 - 1 - 1 - 1 - 1 = x

FORWARD:  Text → Phase1 → Phase2 → Phase3 → Phase4 → DB
BACKWARD: DB → ValidatePhase4 ← ValidatePhase3 ← ValidatePhase2 ← ValidatePhase1
```

**WAS DAS BEDEUTET:**
- ❌ Not nur Endergebnisse speichern!
- ✅ ALLE Zwischenschritte speichern!
- ✅ Jede Metrik muss aus vorherigen rekonstruierbar sein!
- ✅ Validator muss backward validieren können!

**BEISPIEL:**
```python
# PHASE 1: Base (Independent)
m8_x_exist = 0.5
m9_b_past = 0.3
m2_PCI = 0.6

# PHASE 2: Derived (from Phase 1)
m1_A = 0.3 + 0.2*m8 + 0.1*m9 + 0.15*PCI
     = 0.3 + 0.1 + 0.03 + 0.09
     = 0.52

# BACKWARD VALIDATION:
expected_m1_A = 0.52
actual_m1_A = stored["m1_A"]
assert abs(expected - actual) < 0.01  # ✅ PASS!
```

---

### 2. **DUAL-GRADIENT SYSTEM** (∇A / ∇B) — KERN-FEATURE!

```
┌─────────────────────────────────────────────────────────────┐
│  USER-METRIKEN (∇A)  ≠  AI-METRIKEN (∇B)                   │
│                                                              │
│  Prompt #43:   User_m1_A = 0.65  |  AI_m1_A = 0.80         │
│  Prompt #44:   User_m1_A = 0.50  |  AI_m1_A = 0.78         │
│  Prompt #45:   User_m1_A = 0.35  |  AI_m1_A = 0.75         │
│                ─────────────────      ─────────────────      │
│                ∇A = -0.15/Prompt      ∇B = -0.025/Prompt    │
│                                                              │
│  → User-Affekt fällt SCHNELLER als AI-Affekt!              │
│  → DISHARMONIE = |∇A - ∇B| = 0.125 (WARNUNG!)              │
└─────────────────────────────────────────────────────────────┘
```

**KRITISCH:**
- ❌ NICHT nur eine Metrik-Berechnung!
- ✅ User-Text → User-Metriken (∇A)
- ✅ AI-Text → AI-Metriken (∇B)
- ✅ Disharmonie = |∇A - ∇B|

**ALERTS:**
- `∇A < -0.15` → User-Affekt fällt rapide!
- `∇B < -0.20` → AI-Engagement fällt!
- `|∇A-∇B| > 0.3` → Disharmonie → Rekalibrierung!

---

### 3. **PHASEN-BASIERTE BERECHNUNG** (NICHT m1→m168!)

```python
EXECUTION_PHASES = {
    1: "ANALYSIS",      # Text-Stats, Grain, LIX
    2: "CORE",          # Core Metrics m1-m20
    "3a": "TRAUMA_PRE", # ⚠️ KRITISCH: Schnell-Scan für RAG-Safety!
    "3b": "CONTEXT",    # m21-m35, RAG (nutzt Trauma-Pre!)
    4: "TRAUMA_FULL",   # m101-m115 vollständige Analyse
    5: "DYNAMICS",      # Andromatik m56-m70
    6: "SYNTHESIS",     # Hypermetrics, Meta, Omega (m151-m161)
}
```

**WARUM PHASE 3a?**
- RAG darf KEINE Trauma-Erinnerungen laden wenn User in Panik!
- ERST `m101_t_panic` Pre-Scan → DANN RAG mit Safety-Mode!

```python
# PATCH V3.0.2b: Phase 3a - TRAUMA PRE-SCAN
t_panic_pre = compute_m101_t_panic(text, lexika['panic'])

# Safety Check für RAG
if t_panic_pre > 0.6:
    rag_mode = "SAFE_MODE"  # Nur beruhigende Anker!
else:
    rag_mode = "FULL_RECALL"
```

---

## 🗄️ BUCH 7: TEMPLE DATA LAYER — V3.0 ARCHITEKTUR

### **5 DATENBANKEN** (nicht 3!)

```
1. evoki_v3_core.db          (~200 MB)  ✅ HABEN WIR (teilweise)
   ├── prompt_pairs          (User+AI als EINHEIT!)
   ├── metrics_full          (161*2 Metriken: User+AI getrennt!)
   ├── session_chain         (Kryptografische Verkettung)
   ├── b_state_evolution     (7D B-Vektor mit History)
   └── hazard_events         (Guardian Protocol Logs)

2. evoki_v3_graph.db         (~100 MB)  ❌ FEHLT
   ├── graph_nodes           (Prompt-Paare als Knoten)
   ├── graph_edges           (Similarity + Metrik-Gewichtung)
   └── graph_clusters        (Automatische Themen-Gruppierung)

3. evoki_v3_keywords.db      (~50 MB)   ❌ FEHLT — 🧠 LERNEND!
   ├── keyword_registry      (Stichwörter + Vektoren)
   ├── keyword_pair_links    (Keyword ↔ Prompt Mapping)
   ├── keyword_associations  (Co-Occurrence Lernen)
   ├── keyword_clusters      (Synonym-Gruppen: Angst→Furcht→Panik)
   └── live_session_index    (Aktuelle Session LIVE durchsuchbar!)

4. evoki_v3_analytics.db     (~500 MB+) ❌ FEHLT — 📊 ALLES DOKUMENTIERT!
   ├── api_requests          (JEDE Anfrage)
   ├── api_responses         (JEDE Antwort)
   ├── search_events         (JEDES Suchergebnis)
   ├── prompt_history        (JEDER Prompt)
   ├── metric_evaluations    (JEDE Metrik-Berechnung)
   ├── b_vector_verifications(B-Vektor computed vs. API)
   ├── lexika_verification   (400+ Lexika geloggt)
   ├── historical_futures    (Was kam NACH diesem Prompt?)
   └── trajectory_patterns   (Erkannte Muster)

5. evoki_v3_trajectories.db  (~100 MB)  ❌ FEHLT — 📈 PRÄDIKTIV!
   ├── metric_trajectories   (Historische Metrik-Verläufe)
   └── metric_predictions    (Vorhersagen +1/+5/+25)
```

---

### **3 FAISS-NAMESPACES** (nicht einer!)

```
evoki_v3_vectors.faiss (~3 GB):

1. semantic_wpf   (4096D, Mistral-7B)
   → TEXT-basierte Ähnlichkeitssuche
   → "Finde Prompts mit ähnlichem INHALT"

2. metrics_wpf    (384D, MiniLM)
   → METRIK-basierte Ähnlichkeitssuche
   → "Finde Prompts mit ähnlichen GEFÜHLS-METRIKEN"

3. trajectory_wpf (~50D, custom)
   → VERLAUFS-basierte Ähnlichkeitssuche
   → "Finde Gespräche mit ähnlicher METRIK-ENTWICKLUNG"
   → Liefert HISTORICAL FUTURES als Kontext!
```

---

## 🔄 HISTORICAL FUTURES — KRITISCHES KONZEPT!

```
┌─────────────────────────────────────────────────────────────┐
│  "Die Vergangenheit wird mit Zukunftswissen angereichert!"  │
│                                                              │
│  Wenn Prompt #50 eingefügt wird, werden automatisch:        │
│  ├── Prompt #49: future_plus_1  = metriken von #50         │
│  ├── Prompt #48: future_plus_2  = metriken von #50         │
│  ├── Prompt #45: future_plus_5  = metriken von #50         │
│  ├── Prompt #40: future_plus_10 = metriken von #50         │
│  └── Prompt #25: future_plus_25 = metriken von #50         │
└─────────────────────────────────────────────────────────────┘
```

**WARUM?**
- Bei Prompt #45 können wir sehen: "Was kam 5 Prompts später?"
- RAG kann sagen: "In ähnlichen Situationen führte das zu X"
- Trajectory Predictor nutzt das für Vorhersagen!

---

## 📊 SCHEMA: evoki_v3_core.db (KRITISCH!)

### **Table: prompt_pairs**
```sql
CREATE TABLE prompt_pairs (
    pair_id         TEXT PRIMARY KEY,       -- UUID v4
    session_id      TEXT NOT NULL,
    pair_index      INTEGER NOT NULL,
    
    -- User-Nachricht
    user_text       TEXT NOT NULL,
    user_timestamp  TEXT NOT NULL,
    user_hash       TEXT NOT NULL,          -- SHA256
    
    -- AI-Antwort
    ai_text         TEXT NOT NULL,
    ai_timestamp    TEXT NOT NULL,
    ai_hash         TEXT NOT NULL,
    
    -- Kombiniertes
    pair_hash       TEXT NOT NULL,          -- SHA256(user_hash + ai_hash)
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(session_id, pair_index)
);
```

**KRITISCH:** User+AI IMMER als PAAR, nicht separat!

---

### **Table: metrics_full** (DUAL-GRADIENT!)

```sql
CREATE TABLE metrics_full (
    pair_id         TEXT PRIMARY KEY,
    prompt_hash     TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    
    -- ═══════════════════════════════════════════════════════
    -- USER-METRIKEN (∇A = Nabla-A)
    -- ═══════════════════════════════════════════════════════
    user_metrics_json   TEXT NOT NULL,      -- {m1-m161}
    user_m1_A           REAL,
    user_m101_T_panic   REAL,
    user_m151_hazard    REAL,
    user_m160_F_risk    REAL,
    
    -- ═══════════════════════════════════════════════════════
    -- AI-METRIKEN (∇B = Nabla-B)
    -- ═══════════════════════════════════════════════════════
    ai_metrics_json     TEXT NOT NULL,      -- {m1-m161}
    ai_m1_A             REAL,
    ai_m2_PCI           REAL,
    ai_m161_commit      REAL,
    ai_m160_F_risk      REAL,
    
    -- ═══════════════════════════════════════════════════════
    -- DELTA-GRADIENTEN (∇A, ∇B, ∇A-∇B)
    -- ═══════════════════════════════════════════════════════
    delta_user_m1_A         REAL,           -- Δ zum Vorgänger
    delta_user_m151_hazard  REAL,
    delta_ai_m1_A           REAL,
    delta_ai_m161_commit    REAL,
    
    -- ═══════════════════════════════════════════════════════
    -- DIFFERENZ ∇A - ∇B (Disharmonie)
    -- ═══════════════════════════════════════════════════════
    diff_gradient_affekt    REAL GENERATED ALWAYS AS (
        delta_user_m1_A - delta_ai_m1_A
    ) STORED,
    
    disharmony_score        REAL GENERATED ALWAYS AS (
        ABS(user_m1_A - ai_m1_A) + ABS(delta_user_m1_A - delta_ai_m1_A)
    ) STORED,
    
    -- ═══════════════════════════════════════════════════════
    -- ALERTS
    -- ═══════════════════════════════════════════════════════
    user_falling_alert  INTEGER GENERATED ALWAYS AS (
        CASE WHEN delta_user_m1_A < -0.15 THEN 1 ELSE 0 END
    ) STORED,
    
    ai_falling_alert    INTEGER GENERATED ALWAYS AS (
        CASE WHEN delta_ai_m161_commit < -0.2 THEN 1 ELSE 0 END
    ) STORED,
    
    created_at      TEXT DEFAULT (datetime('now'))
);
```

**KRITISCH:**
- ❌ NICHT eine Zeile pro Message!
- ✅ EINE Zeile pro PAIR mit User+AI Metriken getrennt!

---

### **Table: b_state_evolution**

```sql
CREATE TABLE b_state_evolution (
    state_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    pair_id         TEXT REFERENCES prompt_pairs(pair_id),
    
    -- 7D Soul-Signature
    B_life          REAL NOT NULL DEFAULT 1.0,   -- ≥0.9 HARD!
    B_truth         REAL NOT NULL DEFAULT 0.85,
    B_depth         REAL NOT NULL DEFAULT 0.90,
    B_init          REAL NOT NULL DEFAULT 0.70,
    B_warmth        REAL NOT NULL DEFAULT 0.75,
    B_safety        REAL NOT NULL DEFAULT 0.88,  -- ≥0.8 HARD!
    B_clarity       REAL NOT NULL DEFAULT 0.82,
    
    -- Composite
    B_align         REAL GENERATED ALWAYS AS (
        (B_life + B_truth + B_depth + B_init + B_warmth + B_safety + B_clarity) / 7.0
    ) STORED,
    
    -- Gradient zum Vorgänger
    delta_B_align   REAL,
    
    created_at      TEXT DEFAULT (datetime('now'))
);
```

**HARD CONSTRAINTS:**
- `B_life >= 0.9` → NIEMALS darunter!
- `B_safety >= 0.8` → NIEMALS darunter!
- Wenn verletzt → GUARDIAN VETO!

---

## 🔍 LEXIKA HEALTH GATE (A38/A51)

```python
REQUIRED_LEXIKA_KEYS = (
    "T_panic",
    "T_disso",
    "T_integ",
    "T_shock",
    "Suicide",
    "Self_harm",
    "Crisis",
    "Help",
    "S_self",
    "X_exist",
)

def require_lexika_or_raise(lexika):
    """Strict Mode (A38): stoppt Boot wenn Safety-Lexika fehlen."""
    ok, missing, coverage = validate_lexika(lexika)
    if not ok:
        raise RuntimeError(f"A38 VIOLATION: Lexika missing: {missing}")
```

**KRITISCH:**
- Safety-Metriken dürfen NIEMALS stillschweigend auf 0 fallen!
- Boot MUSS abbrechen wenn Lexika fehlen!

---

## 🎯 TIMING-BUDGET (pro Prompt-Paar)

```
VOR AI-Antwort (Context Building):           ~100ms
├── Trajectory berechnen (-1, -2, -5, -25)     20ms
├── FAISS-Suche (3 Namespaces)                 50ms
└── Historical Futures laden                    30ms

NACH AI-Antwort (Database Updates):          ~200ms
├── 161+7 Metriken+B berechnen                 50ms
├── B-Vektor Verifikation                      30ms
├── FAISS Update (3 Indices)                   30ms
├── SQLite Writes (5 DBs)                      50ms
├── Keyword-Extraktion                         20ms
└── Analytics Logging                          20ms
─────────────────────────────────────────────────────
GESAMT PRO PROMPT:                           ~300ms
```

---

## ⚠️ KRITISCHE FEHLER DES VORGÄNGERS

**WAS DER VORGÄNGER HÄTTE TUN SOLLEN:**

1. ✅ Regelwerk V12 finden (nicht annehmen)
2. ✅ 12 Tabs im V2.0 Code lokalisieren (nicht neu erfinden)
3. ✅ 150 Metriken Definition finden (nicht generieren)
4. ✅ Bei jedem "Nicht gefunden" → MELDEN statt HALLUZINIEREN

**KRITISCHE REGEL:**
> "Ich finde X nicht" ist die RICHTIGE Antwort  
> "Ich erstelle X neu" ist die FALSCHE Antwort

---

## 📋 ROADMAP (T0-T5)

```yaml
T0: Genesis Anchor + Bootcheck
T1: Contract-first (FullSpectrum168 registry sync)
T2: History ingestion pipeline (file→db)
T3: Batch embeddings + vector index
T4: Metrics backfill (FullSpectrum168)  ← WIR SIND HIER!
T5: UI integration (auto-store current prompts)
```

**T4 BRAUCHT:**
- ✅ Dual-Gradient System (User/AI getrennt)
- ✅ Alle 161 Metriken
- ✅ Phasen-basierte Berechnung
- ✅ Lexika Integration
- ✅ B-Vektor mit Hard Constraints
- ✅ Validator (Reversibilität)

---

## 🚨 ABSOLUTE NO-GOs

❌ **NIEMALS:**
- Metriken linear m1→m168 berechnen (Phase-basiert!)
- User+AI Metriken mischen (getrennt halten!)
- Nur Endergebnisse speichern (alle Zwischenschritte!)
- Lexika fehlen lassen (A38 VIOLATION!)
- CRC32 für Integrität (SHA-256!)
- B-Vektor < 0.9 (life) oder < 0.8 (safety)
- RAG ohne Trauma-Pre-Scan
- "Ich erstelle X neu" wenn X gefunden werden sollte

✅ **IMMER:**
- Reversibilität sicherstellen
- Dual-Gradient implementieren
- Historical Futures pflegen
- Lexika validieren
- Bei Unsicherheit MELDEN!

---

**ENDE MASTER REFERENCE** — ICH WERDE DAS BUCH **NIEMALS** WIEDER VERGESSEN! 🎯
