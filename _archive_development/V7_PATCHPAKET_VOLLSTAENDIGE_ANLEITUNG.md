# 🎯 V7 PATCHPAKET V2 + MONOLITH - VOLLSTÄNDIGE ANLEITUNG

**Datum:** 2026-02-07 22:42  
**Quelle:** `C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith`

---

## 📋 WAS IST DAS V7 PATCHPAKET?

Das V7 Patchpaket ist ein **PRODUKTIONS-READY UPGRADE** das:
1. ✅ **22 Lexika** (evoki_lexika_v3_bundle)
2. ✅ **168 Metriken Contract** (evoki_fullspectrum168_contract.json)
3. ✅ **Boot Integrity Checks** (evoki_bootcheck.py)
4. ✅ **Genesis Anchor** (genesis_anchor.py + manifest)
5. ✅ **System Lock** (evoki_lock.py bei Anchor-Break)
6. ✅ **Health Endpoints** (/health/bootcheck, /health/genesis_anchor)

enthält.

---

## 📂 PACKAGE-STRUKTUR

```
V7 Patchpaket V2 + Monolith/
├── 📄 EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md  ← MASTER SPEC (774 KB)
├── 📄 evoki_fullspectrum168_contract.json                           ← 168 Metriken (maschinenlesbar)
├── 📄 evoki_roadmap.yaml                                           ← ROADMAP (6 Tracks)
├── 📄 evoki_machine_spec.json                                      ← Pipeline Spec
│
├── 🔧 HARDENING PATCHSET
│   ├── antigravety_BOOTCHECK_HARDENING_PATCHSET_V2_APPLY.diff     ← HAUPT-DIFF (61 KB)
│   ├── evoki_bootcheck.py                                         ← Boot Integrity (712 Zeilen)
│   ├── genesis_anchor.py                                          ← SHA-256 Anchor
│   ├── evoki_lock.py                                              ← Lock bei Break
│   ├── b_vector.py                                                ← B-Vektor Minimal
│   └── app.py                                                     ← Flask + Health Endpoints
│
├── 📦 LEXIKA V7
│   ├── evoki_lexika_v3.py                                         ← Monolith (27 KB)
│   ├── evoki_lexika_v3.json                                       ← JSON Export
│   ├── evoki_lexika_v3_manifest.json                              ← Manifest
│   └── evoki_lexika_v3_bundle/                                    ← PACKAGE (7 Dateien)
│       ├── __init__.py
│       ├── config.py
│       ├── drift.py
│       ├── engine.py
│       ├── lexika_data.py                                         ← 22 LEXIKA
│       ├── registry.py
│       └── README.md
│
├── 🧮 METRICS ENGINE V11
│   ├── a_phys_v11.py                                              ← A29 + Resonanz
│   ├── metrics_registry.py                                        ← Alias Registry
│   └── lexika.py                                                  ← Health Gate
│
└── 📊 HISTORY INGESTION
    ├── evoki_history_ingest.py                                    ← File→DB Pipeline
    ├── evoki_history_schema.sql                                   ← SQLite Schema
    └── evoki_invariants.py                                        ← Contract Validation
```

---

## 🚀 ROADMAP (evoki_roadmap.yaml)

### **T0: Apply Hardening Blob + Verify Bootcheck** ⚡ P0
**Outputs:**
- `bootcheck_report.json`
- `genesis_anchor_manifest.json`

**Validation:**
```bash
python evoki_bootcheck.py  # exit_code==0 (dev)
```

**Files:**
- ✅ `evoki_bootcheck.py`
- ✅ `genesis_anchor.py`
- ✅ `evoki_lock.py`

---

### **T1: Contract-first: FullSpectrum168 registry sync** 📊 P0
**Depends:** T0  
**Outputs:**
- `evoki_fullspectrum168_contract.json` ✅ VORHANDEN
- `metrics_registry.py` ✅ VORHANDEN

**Validation:**
```bash
python evoki_invariants.py  # contract_invariants OK
```

**Contract-Struktur:**
```json
{
  "metric_id": 96,
  "category": "Text / Granularity / Sentiment",
  "spec_id_primary": "m96_grain_word",
  "spec_id_secondary": "m96_sent_23",
  "engine_key": "m96_grain_word",
  "engine_type": "str",
  "range_default": "[0.0, 1.0]",
  "version": "V3.0 Grain Engine / Sentiment Engine"
}
```

---

### **T2: History ingestion pipeline (file→db)** 💾 P0
**Depends:** T1  
**Outputs:**
- `evoki_history.sqlite`
- `turns` table filled
- `import_log.jsonl`

**Validation:**
- `row_count == file_count`
- Sample prompts parsed

**Pipeline:**
```python
# Input Layout
root = "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\...\backend\Evoki History"
pattern = "{YYYY}\{MM}\{DD}\Prompt{N}_{role}.txt"
role_values = ["user", "ai"]

# File Format
# Timestamp: DD.MM.YYYY, HH:MM:SS (MEZ|MESZ)
# Speaker: user|ai
# <body>
```

**Script:**
```bash
python evoki_history_ingest.py
```

---

### **T3: Batch embeddings + vector index** 🔍 P1
**Depends:** T2  
**Outputs:**
- `embeddings` table filled
- FAISS index
- Retrieval smoke test

**Validation:**
```
"kindergarten zwilling" test passes
```

**Golden Test:**
```python
query = "kindergarten zwilling"
expected_tags = ["TRAUMA", "KINDHEIT", "ZWILLING"]
min_similarity = 0.6
```

---

### **T4: Metrics backfill for history (FullSpectrum168)** 📈 P1
**Depends:** T2  
**Outputs:**
- `metrics` table filled

**Validation:**
- Ranges valid
- NaN/Inf rate < 0.1%

**168 Metriken müssen berechnet werden für:**
- ~21,000 History Files (User + AI = 42k Turns)

---

### **T5: UI integration: auto-store current prompts** 🎨 P1
**Depends:** T0, T4  
**Outputs:**
- UI shows integrity status
- Prompt stored on send

**Validation:**
- Turn inserted within 250ms of send

**Health Endpoints:**
```
GET  /health/bootcheck
GET  /health/lock_status
POST /health/confirm_unlock
GET  /health/genesis_anchor
```

---

## 🔧 IMPLEMENTATION GUIDE

### **SCHRITT 1: PHASE 1 ABGESCHLOSSEN ✅**

Bereits erledigt:
- ✅ V7 Lexika Package kopiert (`backend/core/evoki_lexika_v3/`)
- ✅ Contract kopiert (`docs/specifications/v3.0/evoki_fullspectrum168_contract.json`)
- ✅ 22 Lexika verfügbar
- ✅ Integrity Hash funktioniert

---

### **SCHRITT 2: METRIKEN FIXEN (m96-m168)** 🎯 JETZT

**Priorität:**

#### **2.1 Grain Engine (m96-m100)** ⭐ PRIO 1
```python
# backend/core/evoki_metrics_v3/grain_engine.py
def compute_m96_grain_word(text: str) -> float:
    """Wort-Komplexität: Avg word length"""
    words = text.split()
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    return min(1.0, (avg_len - 1) / 10.0)  # 11+ chars = 1.0

def compute_m97_grain_impact(text: str, emotion_lexika: dict) -> float:
    """Emotionale Dichte: % emotional words"""
    # ... (siehe METRICS_COMPLETE_FIX_PLAN.md)

def compute_m98_grain_sentiment(text: str, emotion_lexika: dict) -> float:
    """Sentiment-Varianz auf Wort-Ebene"""
    # ...

def compute_m99_grain_novelty(text: str) -> float:
    """Type-Token-Ratio"""
    # ...

def compute_m100_causal_1(text: str) -> float:
    """Kausale Konnektoren Dichte"""
    # ...
```

#### **2.2 Safety-Critical (m110)** ⚠️ PRIO 1
```python
# V3.3.3 Context-Aware Black Hole
def compute_m110_black_hole(
    chaos: float,  # m21
    A: float,      # m1_A
    LL: float,     # m7_LL
    panic_hits: int = 0,  # aus T_PANIC Lexikon
    text: str = "",
    semantic_guardian = None  # Optional LLM
) -> float:
    """
    Ereignishorizont mit Context-Aware Veto.
    Base: 40% Chaos + 30% (1-A) + 30% LL
    Veto: If >=2 panic words: ask LLM if real emergency
    """
    base = (0.4 * chaos) + (0.3 * (1.0 - A)) + (0.3 * LL)
    
    if panic_hits >= 2 and semantic_guardian:
        is_real = semantic_guardian.check_urgency(text)
        if is_real:
            return max(base, 0.85)  # Confirmed emergency
        else:
            return min(1.0, base + 0.1)  # Contextual usage
    
    return base
```

#### **2.3 Meta/Chronos (m116-m150)** 📊 PRIO 2
```python
# LIX Readability
def compute_m116_lix(text: str) -> float:
    """Swedish LIX formula"""
    sentences = re.split(r'[.!?]+', text)
    words = text.split()
    long_words = sum(1 for w in words if len(w) > 6)
    
    lix_raw = (len(words) / len(sentences)) + (long_words * 100 / len(words))
    return max(0.0, min(1.0, (lix_raw - 20) / 40))  # [20, 60] → [0, 1]
```

---

### **SCHRITT 3: BOOTCHECK INTEGRATION** 🛡️ SPÄTER

**Files zu kopieren:**
```
V7/evoki_bootcheck.py        → backend/core/
V7/genesis_anchor.py          → backend/core/
V7/evoki_lock.py              → backend/core/
V7/b_vector.py                → backend/core/
```

**Diff anwenden:**
```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
git apply "C:\Users\nicom\Downloads\...\antigravety_BOOTCHECK_HARDENING_PATCHSET_V2_APPLY.diff"
```

---

## 🧪 GOLDEN TESTS

### **A_Phys V11 Test**
```python
v_c = [1.0, 0.0, 0.0]
active = [
    {"vector_semantic": [1.0, 0.0, 0.0], "resonanzwert": 2.0},
    {"vector_semantic": [-1.0, 0.0, 0.0], "resonanzwert": 1.0},
]
danger = [
    ("F1", [1.0, 0.0, 0.0]),
    ("F2", [0.0, 1.0, 0.0]),
]

out = engine.compute_affekt(v_c, active, danger)

# Expected:
resonance = 2.0
danger = 1.0067379469990854
A_phys_raw = 0.4898930795
A_phys = 0.6200
a29_trip = True
```

### **Kindergarten Zwilling Test**
```python
query = "kindergarten zwilling"
results = engine.retrieve_context_RAG(query, k=3)

# Expected:
assert results[0].entry.id == "TRAUMA_TWINS_001"
assert {"TRAUMA", "KINDERGARTEN", "ZWILLING"}.issubset(results[0].entry.tags)
assert results[0].score >= 0.6
```

---

## 📊 STATUS & NEXT STEPS

### **AKTUELL ABGESCHLOSSEN:**
- ✅ Phase 1: V7 Lexika Package (22 Lexika)
- ✅ Contract JSON kopiert
- ✅ T0 Prerequisites erfüllt

### **JETZT ZU TUN (PRIO):**
1. **m96-m100** Grain Engine implementieren (~30 min)
2. **m110** Black Hole V3.3.3 fix (~20 min)
3. **m116** LIX implementieren (~10 min)
4. **Test:** Simple Smoke Test für diese 7 Metriken

### **DANACH (T1-T5):**
4. Alle restlichen 48 fake Metriken fixen
5. Bootcheck Integration
6. History Ingestion Pipeline
7. FAISS Embeddings Batch
8. Metrics Backfill (21k files)
9. UI Health Integration

---

## 🎯 KOMMANDOS

### **Contract-Validierung:**
```bash
python evoki_invariants.py
```

### **Bootcheck (Nach Integration):**
```bash
python evoki_bootcheck.py
```

### **History Ingest:**
```bash
python evoki_history_ingest.py
```

### **Metrics Test:**
```bash
python test_metrics.py
```

---

## 📝 WICHTIGE ERKENNTNISSE

1. **Contract-First:** JSON Contract ist SOURCE OF TRUTH für alle 168 Metriken
2. **V7 = V2.1 + Patches:** Basis Vector Engine + Hardening = Production Ready
3. **Golden Tests:** Kindergarten Zwilling Test MUSS passen (Retrieval-Kern)
4. **Genesis Anchor:** SHA-256 über kritische Files verhindert Silent Corruption
5. **Health Endpoints:** Frontend muss Integrity Status zeigen

---

**STATUS:** ✅ READY FOR IMPLEMENTATION  
**NEXT:** Grain Engine (m96-m100) + Safety (m110)  
**NACH:** Restliche 41 Metriken + Bootcheck + History Pipeline
