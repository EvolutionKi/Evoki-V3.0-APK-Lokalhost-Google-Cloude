# WIDERSPRÜCHE IN DEN 3 BRAIN-DOKUMENTEN

**Erstellt:** 2026-02-07 20:08  
**Problem:** Die 3 Brain-Dokumente widersprechen sich an kritischen Stellen!

---

## ⚠️ WIDERSPRUCH #1: vector_engine_v2_1.py existiert oder nicht?

### implementation_plan.md sagt:
> **[!WARNING]**  
> Diese Datei existiert **nirgends**. Interface nur durch Bootcheck-Referenzen rekonstruierbar.  
> **Gibt es eine Version irgendwo auf deinem System?**

### MASTER_TODO.md sagt:
```markdown
[ ] T1.1 — vector_engine_v2_1.py kopieren

**Quelle:** C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py  
**Ziel:** backend/core/vector_engine_v2_1.py

Eigenschaften:
- 1597 Zeilen, 65KB
- Implementiert 12 EVOKI-Regeln
```

**Status in MASTER_TODO:** ✅ **ABGESCHLOSSEN** (!!)

### backend_module_mapping.md sagt:
```markdown
| **`vector_engine_v2_1.py`** | 65KB | 1597 | **VectorEngine V2.1** | **`backend/core/vector_engine_v2_1.py`** |
```

**→ 2 Dokumente sagen EXISTIERT, 1 Dokument sagt FEHLT!**

---

## ⚠️ WIDERSPRUCH #2: b_vector.py - Welche Version?

### V7 Patchpaket Diff-Version:
- **Größe:** 4.2KB, 127 Zeilen
- **Ort:** `backend/core/b_vector.py` (bereits kopiert)
- **Problem:** Interface-Mismatch mit vector_engine_v2_1.py

### evoki_pipeline Version:
- **Größe:** 2.4KB, 85 Zeilen
- **Ort:** `evoki_pipeline/b_vector.py`
- **Vorteil:** Perfekt kompatibel mit vector_engine_v2_1.py

### MASTER_TODO empfiehlt:
> **T1.2 — b_vector.py ersetzen (FORCE!)**  
> Pipeline-Version nutzen, Diff-Version archivieren

### implementation_plan.md sagt:
> **T0.4 — Diffs anwenden (V2 Hardening Patch)**  
> `b_vector.py` aus Diff extrahieren

**→ 2 verschiedene Empfehlungen welche Version zu nutzen ist!**

---

## ⚠️ WIDERSPRUCH #3: Phase T1 Status

### MASTER_TODO.md (Zeile 252):
```markdown
## T1 Zusammenfassung

**Gesamt:** 8/8 Tasks ✅ **ABGESCHLOSSEN**

Kopierte Module:
1. ✅ b_vector.py (evoki_pipeline Version, 85 Zeilen)
2. ✅ vector_engine_v2_1.py (1597 Zeilen, 65KB)
3. ✅ metrics_complete_v3.py (41KB - ECHTE 168 Metriken!)
...
```

### implementation_plan.md (Zeile 115):
```markdown
## Reihenfolge

T0 (Archiv + Kopieren) → T1 (Fehlende Module) → T2 (DBs) + T3 (Pipeline) → T4 (Frontend)
```

### Live-System Realität:
```powershell
PS C:\Evoki V3.0> ls backend/core/vector_engine_v2_1.py
# Datei existiert NICHT!

PS C:\Evoki V3.0> ls backend/core/evoki_metrics_v3/metrics_complete_v3.py
# Datei existiert NICHT!
```

**→ MASTER_TODO sagt DONE, aber Dateien existieren nicht im System!**

---

## ⚠️ WIDERSPRUCH #4: Phase T2 Status

### MASTER_TODO.md (Zeile 396):
```markdown
## T2 Zusammenfassung

**Gesamt:** 3/3 Tasks ✅ **ABGESCHLOSSEN**

Erstellte Dateien:
1. ✅ backend/api/metrics.py (FullSpectrum168 API - 165 Zeilen)
2. ✅ backend/api/vector.py (Vector Search + Memory Ops - 185 Zeilen)
3. ✅ backend/api/timeline.py (4D Trajectories - 155 Zeilen)
4. ✅ backend/main.py (ERWEITERT - Phase 1 Integration)
```

### Live-System Realität:
```powershell
PS C:\Evoki V3.0> cat backend/api/metrics.py
# Datei existiert!

PS C:\Evoki V3.0> cat backend/api/vector.py  
# Datei existiert!

PS C:\Evoki V3.0> cat backend/api/timeline.py
# Datei existiert!
```

**→ T2 tatsächlich teilweise DONE, aber APIs haben keine Implementierung (nur Stubs)!**

---

## ⚠️ WIDERSPRUCH #5: Task-Zählung

### MASTER_TODO.md:
```
Gesamt: 27 Tasks (3 erledigt, 24 offen)
```

### TODO_COMPLETE_V3.md (meine Zählung):
```
GESAMT: 21 Tasks (3 DONE, 18 TODO)
```

### implementation_plan.md:
```
Gesamt: ~18 Tasks über 4 Phasen
```

**→ 3 verschiedene Task-Zahlen: 27, 21, 18!**

---

## ⚠️ WIDERSPRUCH #6: Datenbank-Anzahl

### MASTER_TODO.md:
```
PHASE T3: DATA LAYER AUFBAU 🔄
5 SQLite-Datenbanken + 3 FAISS-Namespaces
```

### implementation_plan.md:
```
## Phase T2: Datenbank-Architektur
> Spec definiert 6 DBs. Nur master_timeline.db (45MB) und Layer-DBs existieren.

#### [ ] T2.1 — evoki_v3_core.db
#### [ ] T2.2 — evoki_v3_graph.db
#### [ ] T2.3 — evoki_v3_keywords.db
#### [ ] T2.4 — evoki_v3_analytics.db
#### [ ] T2.5 — evoki_v3_trajectories.db
#### [ ] T2.6 — FAISS Namespaces
```

**→ 5 DBs vs. 6 DBs!**

---

## ⚠️ WIDERSPRUCH #7: FAISS Namespace-Namen

### MASTER_TODO.md:
```
1. semantic_wpf (4096D, Mistral-7B)
2. metrics_wpf (384D, MiniLM) ✅ EXISTIERT
3. trajectory_wpf (~50D, custom)
```

### implementation_plan.md:
```
#### [ ] T2.6 — FAISS Namespaces: 
atomic_pairs, context_windows, trajectory_wpf, metrics_embeddings
```

**→ Komplett andere Namen!**
- `semantic_wpf` vs. `atomic_pairs`?
- `metrics_wpf` vs. `metrics_embeddings`?
- `context_windows` existiert gar nicht in MASTER_TODO!

---

## ⚠️ WIDERSPRUCH #8: evoki_lexika_v3 Package vs. Monolith

### MASTER_TODO.md (T0.4):
```markdown
- [x] evoki_lexika_v3.py (Monolith, 698 Zeilen, 27699 bytes) → backend/core/
  - Vollständige Lexika V3.0 Implementation (ALL_LEXIKA Registry + Engine)
  - Wichtig: Parallele Version zum Package evoki_lexika_v3/
```

### implementation_plan.md (T0.3):
```markdown
#### [ ] T0.3 — Lexika V3 Bundle kopieren
- evoki_lexika_v3_bundle/evoki_lexika_v3/ → backend/core/evoki_lexika_v3/
  - __init__.py, config.py, drift.py, engine.py, lexika_data.py, registry.py
```

**→ 2 VERSCHIEDENE Lexika-Implementierungen:**
1. **Monolith:** `evoki_lexika_v3.py` (698 Zeilen, eine Datei)
2. **Package:** `evoki_lexika_v3/` (6 Module)

**Welche ist kanonisch?**

---

## 📊 ZUSAMMENFASSUNG DER WIDERSPRÜCHE

| # | Thema | MASTER_TODO | implementation_plan | backend_mapping | Live-System |
|---|-------|-------------|---------------------|-----------------|-------------|
| 1 | vector_engine_v2_1.py | ✅ DONE (65KB) | ❌ FEHLT | Quelle angegeben | ❌ NICHT VORHANDEN |
| 2 | b_vector.py Version | Pipeline (85 Zeilen) | Diff (127 Zeilen) | Beide erwähnt | Diff vorhanden |
| 3 | Phase T1 Status | ✅ DONE | ❌ TODO | ❌ TODO | ❌ NICHT VORHANDEN |
| 4 | Phase T2 Status | ✅ DONE | ❌ TODO | ❌ TODO | ⚠️ Stubs vorhanden |
| 5 | Task-Anzahl | 27 | 18 | - | - |
| 6 | Datenbank-Anzahl | 5 SQLite | 6 DBs | - | 1 vorhanden |
| 7 | FAISS Namen | semantic_wpf, metrics_wpf, trajectory_wpf | atomic_pairs, context_windows, metrics_embeddings, trajectory_wpf | - | 1 vorhanden (metrics_wpf) |
| 8 | Lexika Implementation | Monolith + Package | Package | Package | Package vorhanden |

---

## 🎯 REALITÄT vs. DOKUMENTE

### Was die Dokumente behaupten:
- ✅ T0: Archivierung DONE
- ✅ T1: evoki_pipeline Module kopiert
- ✅ T2: Backend-APIs erstellt
- **Completion: ~50%**

### Was das Live-System zeigt:
- ✅ T0: Teilweise (V7 Module kopiert, aber Import-Fehler!)
- ❌ T1: NICHT DONE (vector_engine_v2_1.py fehlt!)
- ⚠️ T2: Nur Stubs (APIs existieren, aber leer)
- **Tatsächliche Completion: ~14%** (3 von 21 Tasks)

---

## ❓ OFFENE FRAGEN DIE GEKLÄRT WERDEN MÜSSEN

1. **Existiert `vector_engine_v2_1.py` wirklich?**
   - Wenn JA: Pfad bestätigen
   - Wenn NEIN: MASTER_TODO ist falsch!

2. **Welche `b_vector.py` Version nutzen?**
   - Diff-Version (aktuell im System)
   - Pipeline-Version (laut MASTER_TODO besser)

3. **Warum sagt MASTER_TODO "T1 DONE" wenn Dateien fehlen?**
   - War das ein früheres Conversation-Ergebnis?
   - Wurde zurückgerollt?
   - Dokument veraltet?

4. **Welche Lexika-Implementation nutzen?**
   - Monolith `evoki_lexika_v3.py` (698 Zeilen)
   - Package `evoki_lexika_v3/` (6 Module)
   - Beide parallel?

5. **Welche FAISS-Namespace-Namen sind korrekt?**
   - MASTER_TODO: semantic_wpf, metrics_wpf, trajectory_wpf
   - implementation_plan: atomic_pairs, context_windows, trajectory_wpf, metrics_embeddings

---

## ✅ EMPFEHLUNG: WIE WEITERMACHEN?

### Schritt 1: REALITÄT PRÜFEN
```powershell
# Prüfe ob vector_engine_v2_1.py existiert
Test-Path "C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py"

# Prüfe b_vector.py Versionen
ls "C:\Users\nicom\Documents\evoki\evoki_pipeline\b_vector.py"
ls "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\b_vector.py"

# Prüfe Lexika
ls "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_lexika_v3.py"
ls "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_lexika_v3\"
```

### Schritt 2: TODO BASIEREND AUF REALITÄT ERSTELLEN
- ❌ Ignoriere MASTER_TODO "DONE" Status
- ✅ Nutze Live-System als Source of Truth
- ✅ Prüfe jede Datei bevor "DONE" markiert wird

### Schritt 3: KLARE PRIORITÄTEN
1. 🔥 Import-Fehler beheben (T1.1-T1.2)
2. 🔥 Fehlende Module finden/kopieren (vector_engine, metrics_complete_v3)
3. ⚡ Datenbanken erstellen
4. ⚡ Backend-APIs implementieren (nicht nur Stubs!)

---

**Ende WIDERSPRUECHE_IN_BRAIN_DOCS.md**
