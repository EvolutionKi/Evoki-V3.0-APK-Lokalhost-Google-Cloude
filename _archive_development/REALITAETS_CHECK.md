# EVOKI V3.0 — REALITÄTS-CHECK & NÄCHSTE SCHRITTE

**Zeit:** 2026-02-07 20:13  
**Status:** Alle Dateien verifiziert, **NICHTS kopiert/implementiert!**

---

## ✅ WAS DONE IST (Phase T0)

1. ✅ V7 Module kopiert nach `backend/core/`:
   - a_phys_v11.py, evoki_bootcheck.py, evoki_lock.py
   - genesis_anchor.py, evoki_invariants.py, metrics_registry.py
   - evoki_history_ingest.py, lexika.py
   - evoki_lexika_v3/ Package
   - b_vector.py (Diff-Version, 127 Zeilen)
   - evoki_fullspectrum168_contract.json

2. ✅ Alte Module archiviert nach `backend/_archive_v2/`

3. ✅ 10.971 Prompt-Paare in evoki_v3_core.db

4. ✅ 10.971 FAISS Vektoren (metrics_wpf, 384D)

5. ✅ Backend läuft (FastAPI, Port 8000)

6. ✅ Frontend läuft (React/Vite, Port 5173)

---

## ❌ WAS NOCH ZU TUN IST

### 🔥 KRITISCH (Blockiert alles):

#### 1. Import-Fehler beheben
**Problem:**
```python
from core import genesis_anchor  # ModuleNotFoundError!
```

**Fix:**
```python
# backend/core/__init__.py MUSS erweitert werden:
from . import genesis_anchor
from . import evoki_invariants
from . import evoki_lock
from . import evoki_bootcheck
from . import a_phys_v11
from . import metrics_registry
```

**Zeitaufwand:** 5 Minuten

---

#### 2. evoki_pipeline Module kopieren (6 Dateien!)

**Von:** `C:\Users\nicom\Documents\evoki\evoki_pipeline\`  
**Nach:** `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\`

| Datei | Ziel | Status |
|-------|------|--------|
| `vector_engine_v2_1.py` (64.7KB) | `backend/core/` | ❌ NICHT KOPIERT |
| `metrics_complete_v3.py` | `backend/core/evoki_metrics_v3/` | ❌ NICHT KOPIERT |
| `timeline_4d_complete.py` | `backend/core/` | ❌ NICHT KOPIERT |
| `chunk_vectorize_full.py` | `backend/core/` | ❌ NICHT KOPIERT |
| `b_vector.py` (85 Zeilen) | `backend/core/` (ERSETZEN!) | ❌ NICHT ERSETZT |
| `config.py` | `backend/core/` | ❌ NICHT KOPIERT |

**Zeitaufwand:** 10 Minuten (Copy-Commands)

---

#### 3. spectrum_types.py generieren

**Quelle:** `backend/core/evoki_fullspectrum168_contract.json` ✅ vorhanden  
**Ziel:** `backend/core/spectrum_types.py` ❌ **FEHLT!**

**Was:** Python Dataclass mit 168 Feldern (m1_A, m2_PCI, ..., m168_*)

**Benötigt von:**
- evoki_bootcheck.py
- metrics_registry.py
- evoki_invariants.py

**Zeitaufwand:** 15 Minuten (Script schreiben + ausführen)

---

#### 4. Backend-Integration umschreiben

**Dateien die UMGESCHRIEBEN werden müssen:**

##### 4.1 `backend/api/temple.py` erweitern
**Aktuell:** Nur SSE-Stream mit Dummy-Metriken  
**Soll:** 
- VectorEngine-Integration
- Metrics Complete V3 Integration
- Dual-Response API (User + AI Metriken)
- Dual-Gradient Berechnung

**Zeitaufwand:** 2-3 Stunden

##### 4.2 `backend/api/metrics.py` implementieren
**Aktuell:** Stub (leer)  
**Soll:** FullSpectrum168 API Endpoints

**Zeitaufwand:** 1 Stunde

##### 4.3 `backend/api/vector.py` implementieren
**Aktuell:** Stub (leer)  
**Soll:** Vector Search Endpoints

**Zeitaufwand:** 1 Stunde

##### 4.4 `backend/api/timeline.py` implementieren
**Aktuell:** Stub (leer)  
**Soll:** Timeline 4D API Endpoints

**Zeitaufwand:** 1 Stunde

---

### ⚡ HIGH PRIORITY:

#### 5. Datenbanken erstellen (4 DBs fehlen!)

**Erstellen:**
- evoki_v3_graph.db
- evoki_v3_keywords.db
- evoki_v3_analytics.db
- evoki_v3_trajectories.db

**Plus:** evoki_v3_core.db Schema erweitern (Dual-Gradient Spalten)

**Zeitaufwand:** 4-5 Stunden

---

#### 6. FAISS Indices erstellen (2 fehlen!)

**Erstellen:**
- semantic_wpf (4096D, Mistral-7B)
- trajectory_wpf (~50D, custom)

**Zeitaufwand:** 1-2 Stunden

---

### 📊 MEDIUM PRIORITY:

#### 7. Frontend anpassen

**Dateien die UMGESCHRIEBEN werden müssen:**
- `app/interface/src/api/temple.ts` — Dual-Response API
- `app/interface/src/components/core/TempleTab.tsx` — Dual-Metrics UI
- `app/interface/src/components/core/MetricsDashboard.tsx` — Gradient-Charts

**Zeitaufwand:** 2-3 Stunden

---

## 📋 GESAMT-ZEITSCHÄTZUNG

| Phase | Tasks | Zeitaufwand | Status |
|-------|-------|-------------|--------|
| **Import-Fix + Kopieren** | 4 | 30 Minuten | ❌ TODO |
| **Backend-Integration** | 4 | 5-6 Stunden | ❌ TODO |
| **Datenbanken** | 5 | 4-5 Stunden | ❌ TODO |
| **FAISS** | 2 | 1-2 Stunden | ❌ TODO |
| **Frontend** | 3 | 2-3 Stunden | ❌ TODO |
| **Testing** | 3 | 2-3 Stunden | ❌ TODO |
| **GESAMT** | **21** | **15-20 Stunden** | - |

---

## 🎯 NÄCHSTE SCHRITTE - WAS SOLL ICH TUN?

### Option A: Sofort starten (automatisch)
Ich kann **JETZT** folgendes tun:
1. ✅ `backend/core/__init__.py` fixen (Import-Fehler)
2. ✅ Alle 6 evoki_pipeline Dateien kopieren
3. ✅ `spectrum_types.py` generieren
4. ✅ Testen ob Imports funktionieren

**Zeitaufwand:** 30 Minuten  
**Danach:** Import-Fehler behoben, alle Module vorhanden

### Option B: Nur dokumentieren
Ich erstelle detaillierte Schritt-für-Schritt-Anleitung was du manuell machen musst.

### Option C: Gezielt einzelne Schritte
Du sagst mir welchen Schritt ich als nächstes machen soll.

---

## 🚨 KRITISCHE ENTSCHEIDUNG

**Was möchtest du dass ich JETZT mache?**

**A)** ✅ Sofort starten mit Import-Fix + Kopieren (30 Min automatisch)  
**B)** 📋 Nur dokumentieren  
**C)** 🎯 Du sagst mir den nächsten Schritt  

---

**Ende REALITAETS_CHECK.md**
