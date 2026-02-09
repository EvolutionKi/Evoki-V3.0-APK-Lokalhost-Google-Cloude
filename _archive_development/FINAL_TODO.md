# EVOKI V3.0 — FINAL TODO (BASIEREND AUF REALITÄT)

**Erstellt:** 2026-02-07 20:12  
**Basis:** Live-System-Check + Datei-Verifikation  
**Status:** ✅ Alle Quellpfade verifiziert!

---

## ✅ WIDERSPRÜCHE AUFGELÖST

### FRAGE 1: vector_engine_v2_1.py existiert?
**ANTWORT:** ✅ **JA!**
- **Pfad:** `C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py`
- **Größe:** 64.729 Bytes (64.7KB) ✅
- **implementation_plan.md war FALSCH!**

### FRAGE 2: Welche b_vector.py Version?
**ANTWORT:** ✅ **Beide existieren!**
- **Pipeline-Version:** `C:\Users\nicom\Documents\evoki\evoki_pipeline\b_vector.py` (85 Zeilen, kompatibel)
- **Diff-Version:** `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\b_vector.py` (127 Zeilen, aktuell im System)
- **Empfehlung:** Pipeline-Version nutzen (laut MASTER_TODO kompatibel mit VectorEngine)

### FRAGE 3: evoki_lexika_v3 - Package oder Monolith?
**ANTWORT:** ✅ **Package existiert!**
- **Pfad:** `C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\evoki_lexika_v3_bundle`
- **Plus Monolith:** `evoki_lexika_v3.py` (698 Zeilen) ebenfalls vorhanden
- **Empfehlung:** Package nutzen (strukturierter)

---

## 📊 VERIFIZIERTE QUELLPFADE

### ✅ evoki_pipeline Module (ALLE VORHANDEN!)

| Datei | Pfad | Status |
|-------|------|--------|
| `vector_engine_v2_1.py` | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ 64.7KB |
| `metrics_complete_v3.py` | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ Vorhanden |
| `timeline_4d_complete.py` | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ Vorhanden |
| `chunk_vectorize_full.py` | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ Vorhanden |
| `b_vector.py` (Pipeline) | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ Vorhanden |
| `config.py` | `C:\Users\nicom\Documents\evoki\evoki_pipeline\` | ✅ Vorhanden |

### ✅ V7 Patchpaket Module (BEREITS KOPIERT!)

| Datei | Ziel | Status |
|-------|------|--------|
| `a_phys_v11.py` | `backend/core/` | ✅ Kopiert |
| `evoki_bootcheck.py` | `backend/core/` | ✅ Kopiert |
| `evoki_lock.py` | `backend/core/` | ✅ Kopiert |
| `genesis_anchor.py` | `backend/core/` | ✅ Kopiert |
| `evoki_invariants.py` | `backend/core/` | ✅ Kopiert |
| `metrics_registry.py` | `backend/core/` | ✅ Kopiert |
| `evoki_history_ingest.py` | `backend/core/` | ✅ Kopiert |
| `lexika.py` | `backend/core/` | ✅ Kopiert |
| `evoki_lexika_v3_bundle/` | V7 Patchpaket | ✅ Quelle vorhanden |
| `b_vector.py` (Diff) | `backend/core/` | ✅ Kopiert (127 Zeilen) |

---

## 🎯 TASK-LISTE (BASIEREND AUF REALITÄT)

### 🔥 PHASE 1: KRITISCHE FEHLERBEHEBUNG (2-3 Stunden)

#### [ ] T1.1 — Import-Fehler beheben
**Problem:** `from core import genesis_anchor` schlägt fehl

**Fix:**
```python
# backend/core/__init__.py
from . import genesis_anchor
from . import evoki_invariants
from . import evoki_lock
from . import evoki_bootcheck
from . import a_phys_v11
from . import metrics_registry
from . import evoki_history_ingest
from . import lexika
```

**Test:**
```powershell
cd backend
python -c "from core import genesis_anchor; print('OK')"
```

#### [ ] T1.2 — evoki_pipeline Module kopieren (6 Dateien)

```powershell
# 1. vector_engine_v2_1.py
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\vector_engine_v2_1.py"

# 2. metrics_complete_v3.py
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\metrics_complete_v3.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_complete_v3.py"

# 3. timeline_4d_complete.py
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\timeline_4d_complete.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\timeline_4d_complete.py"

# 4. chunk_vectorize_full.py
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\chunk_vectorize_full.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\chunk_vectorize_full.py"

# 5. b_vector.py (Pipeline-Version ersetzen)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\b_vector.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\b_vector.py" -Force

# 6. config.py
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\config.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\config.py"
```

**Zeitaufwand:** 30 Minuten

#### [ ] T1.3 — spectrum_types.py generieren

**Quelle:** `backend/core/evoki_fullspectrum168_contract.json`  
**Ziel:** `backend/core/spectrum_types.py`

**Script:**
```python
import json
from pathlib import Path

# Lade Contract
contract = json.loads(Path("backend/core/evoki_fullspectrum168_contract.json").read_text())

# Generiere Dataclass
output = '''"""
Auto-generated FullSpectrum168 Dataclass
Source: evoki_fullspectrum168_contract.json
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FullSpectrum168:
    """168 Metriken Contract"""
'''

for metric in contract['metrics']:
    output += f"    {metric['id']}: float = 0.0  # {metric['name']}\n"

Path("backend/core/spectrum_types.py").write_text(output)
print("✅ spectrum_types.py generated!")
```

**Zeitaufwand:** 30 Minuten

#### [ ] T1.4 — evoki_metrics_v3 Package Setup

```python
# backend/core/evoki_metrics_v3/__init__.py
"""
Evoki V3 Metrics Package
"""
from .metrics_complete_v3 import (
    MetricsEngine,
    compute_all_metrics,
    FullSpectrum168
)

__all__ = ['MetricsEngine', 'compute_all_metrics', 'FullSpectrum168']
```

**Zeitaufwand:** 15 Minuten

---

### ⚡ PHASE 2: BACKEND-INTEGRATION (3-4 Stunden)

#### [ ] T2.1 — temple.py erweitern (Dual-Response API)

**Ziel:** User-Metriken + AI-Metriken + Dual-Gradient

**Code:**
```python
from backend.core.vector_engine_v2_1 import VectorEngine
from backend.core.a_phys_v11 import APhysEngine
from backend.core.evoki_metrics_v3 import MetricsEngine

engine = VectorEngine(...)
aphys = APhysEngine()
metrics = MetricsEngine()

@router.post("/stream")
async def temple_stream(request: TempleRequest):
    # 1. User-Metriken
    user_metrics = metrics.compute_all_metrics(request.prompt, target='user')
    
    # 2. Vector Search
    context = engine.retrieve_context_RAG(request.prompt, top_k=5)
    
    # 3. A-Score
    a_score = aphys.compute_a_score(user_metrics)
    
    # 4. AI-Antwort (Google API)
    ai_response = await generate_ai_response(...)
    
    # 5. AI-Metriken
    ai_metrics = metrics.compute_all_metrics(ai_response, target='ai')
    
    # 6. Dual-Gradient
    delta_user_A = user_metrics['m1_A'] - prev_user_metrics.get('m1_A', 0)
    delta_ai_A = ai_metrics['m1_A'] - prev_ai_metrics.get('m1_A', 0)
    diff_gradient = delta_user_A - delta_ai_A
    
    # 7. Events
    alerts = check_gradient_alerts(delta_user_A, delta_ai_A)
    
    return {
        "user_metrics": user_metrics,
        "ai_response": ai_response,
        "ai_metrics": ai_metrics,
        "context": context,
        "dual_gradient": {
            "delta_user_A": delta_user_A,
            "delta_ai_A": delta_ai_A,
            "diff_gradient": diff_gradient,
            "alerts": alerts
        }
    }
```

**Zeitaufwand:** 2 Stunden

#### [ ] T2.2 — Backend-API Endpoints implementieren

**Erstellen:**
- `backend/api/metrics.py` — FullSpectrum168 API
- `backend/api/vector.py` — Vector Search API  
- `backend/api/timeline.py` — Timeline 4D API

**Zeitaufwand:** 1-2 Stunden

---

### 📊 PHASE 3: DATENBANKEN (4-5 Stunden)

#### [ ] T3.1 — evoki_v3_core.db Schema erweitern (Dual-Gradient)

```sql
ALTER TABLE metrics_full ADD COLUMN ai_metrics_json TEXT;
ALTER TABLE metrics_full ADD COLUMN delta_user_m1_A REAL;
ALTER TABLE metrics_full ADD COLUMN delta_ai_m1_A REAL;
ALTER TABLE metrics_full ADD COLUMN diff_gradient_affekt REAL;
ALTER TABLE metrics_full ADD COLUMN disharmony_score REAL;
```

#### [ ] T3.2 — evoki_v3_graph.db erstellen
#### [ ] T3.3 — evoki_v3_keywords.db erstellen (Lernend!)
#### [ ] T3.4 — evoki_v3_analytics.db erstellen (Vollständig!)
#### [ ] T3.5 — evoki_v3_trajectories.db erstellen

**Zeitaufwand:** 4-5 Stunden

---

### 🔍 PHASE 4: FAISS INDICES (1-2 Stunden)

#### [ ] T4.1 — semantic_wpf (4096D, Mistral-7B)
#### [ ] T4.2 — trajectory_wpf (~50D, custom)

**Zeitaufwand:** 1-2 Stunden

---

### 🎨 PHASE 5: FRONTEND (2-3 Stunden)

#### [ ] T5.1 — Temple Tab UI (Dual-Metrics Display)
#### [ ] T5.2 — Metrics Dashboard (Gradient-Charts)
#### [ ] T5.3 — IntegrityGuard.tsx (V7 Health-Endpoints)

**Zeitaufwand:** 2-3 Stunden

---

### ✅ PHASE 6: TESTING (2-3 Stunden)

#### [ ] T6.1 — Unit Tests (VectorEngine, Metriken, Bootcheck)
#### [ ] T6.2 — Integration Tests (Prompt-Flow, Dual-Gradient)
#### [ ] T6.3 — Performance Tests (<500ms Latency)

**Zeitaufwand:** 2-3 Stunden

---

## 📋 GESAMT-ZUSAMMENFASSUNG

| Phase | Tasks | Zeitaufwand | Priorität |
|-------|-------|-------------|-----------|
| **Phase 1: Kritisch** | 4 | 2-3 Stunden | 🔥 SOFORT |
| **Phase 2: Backend** | 2 | 3-4 Stunden | 🔥 SOFORT |
| **Phase 3: Datenbanken** | 5 | 4-5 Stunden | ⚡ HIGH |
| **Phase 4: FAISS** | 2 | 1-2 Stunden | ⚡ HIGH |
| **Phase 5: Frontend** | 3 | 2-3 Stunden | 📊 MEDIUM |
| **Phase 6: Testing** | 3 | 2-3 Stunden | ✅ HIGH |
| **GESAMT** | **19** | **14-20 Stunden** | - |

---

## 🎯 NÄCHSTE SCHRITTE (SOFORT)

### Schritt 1: Import-Fehler beheben (30 Min)
```powershell
# Fix backend/core/__init__.py
code backend/core/__init__.py
```

### Schritt 2: evoki_pipeline Module kopieren (30 Min)
```powershell
# Alle 6 Dateien kopieren
.\copy_evoki_pipeline_modules.ps1
```

### Schritt 3: spectrum_types.py generieren (30 Min)
```powershell
python tooling/scripts/helpers/generate_spectrum_types.py
```

### Schritt 4: Testen (30 Min)
```powershell
# Imports testen
cd backend
python -c "from core import genesis_anchor, vector_engine_v2_1; print('✅ Imports OK!')"

# Backend starten
cd ..
uvicorn backend.main:app --reload

# Tests laufen lassen
python test_fullstack.py
```

**Nach 2 Stunden:**
- ✅ Alle Import-Fehler behoben
- ✅ Alle evoki_pipeline Module integriert
- ✅ Backend läuft mit VectorEngine + Metriken

**Nach 5-6 Stunden:**
- ✅ Dual-Response API implementiert
- ✅ Backend-Integration abgeschlossen
- ✅ 168 Metriken LIVE berechnet

**Nach 14-20 Stunden:**
- ✅ Alle Datenbanken + FAISS Indices erstellt
- ✅ Frontend vollständig angebunden
- ✅ Tests laufen
- ✅ System 100% funktionsfähig

---

**Ende FINAL_TODO.md**
