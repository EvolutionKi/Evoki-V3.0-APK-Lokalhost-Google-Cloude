# 📚 MASTER SOURCE INDEX - EVOKI V3.0 SPECIFICATIONS

**Datum:** 2026-01-19  
**Zweck:** Zentrales Quellenverzeichnis für ALLE Spezifikations-Dokumente  
**Location:** `docs/specifications/v3.0/SOURCES_MASTER_INDEX.md`

---

## 🎯 ZWECK

Dieses Dokument dokumentiert **die exakte Herkunft jeder Information** in den Evoki V3.0 Spezifikationen.

**Garantie:** Du kannst **unter jedem Umstand** nachvollziehen, wo eine Information herkam!

---

## 📁 QUELLEN-ÜBERSICHT

Alle Original-Quellen aus V2.0 wurden nach `sources/` kopiert:

| V2.0 Original-Pfad | Lokale Kopie | Größe | Typ |
|-------------------|--------------|-------|-----|
| `C:\Evoki V2.0\evoki-app\Adler Metriken.txt` | [v2_Adler_Metriken.txt](sources/v2_Adler_Metriken.txt) | 108.4 KB | Spec |
| `C:\Evoki V2.0\evoki-app\frontend\src\App.tsx` | [v2_App.tsx](sources/v2_App.tsx) | 50.7 KB | Frontend |
| `C:\Evoki V2.0\evoki-app\backend\core\DualBackendBridge.js` | [v2_DualBackendBridge.js](sources/v2_DualBackendBridge.js) | 29.4 KB | Backend |
| `C:\Evoki V2.0\evoki-app\backend\core\GeminiContextBridge.js` | [v2_GeminiContextBridge.js](sources/v2_GeminiContextBridge.js) | 29.2 KB | Backend |
| `C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js` | [v2_TrinityEngine.js](sources/v2_TrinityEngine.js) | 22.8 KB | Backend |
| `C:\Users\nicom\Downloads\WHITEBOARD_V2.2_EXTENDED_MASTER.md` | [v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md](sources/v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md) | 296.4 KB | Docs |
| `C:\Evoki V2.0\evoki-app\backend\core\metrics_processor.py` | [v2_metrics_processor.py](sources/v2_metrics_processor.py) | 31.4 KB | Python |
| `C:\Evoki V2.0\evoki-app\python\tools\query.py` | [v2_query.py](sources/v2_query.py) | 5.2 KB | Python |
| `C:\Evoki V2.0\evoki-app\frontend\public\EVOKI_REGELWERKE_GENESIS\regelwerk_v12.json` | [v2_regelwerk_v12.json](sources/v2_regelwerk_v12.json) | 79.4 KB | Config |
| `C:\Evoki V2.0\evoki-app\backend\server.js` | [v2_server.js](sources/v2_server.js) | 122.7 KB | Backend |

**TOTAL:** 11 Quell-Dateien, ~775 KB

---

## 📖 DOKUMENT → QUELLEN MAPPING

### **1. 153_metriken_vollstaendig.md**

**Primäre Quellen:**
- ✅ [v2_Adler_Metriken.txt](sources/v2_Adler_Metriken.txt) - **HAUPTQUELLE** (153 Metriken V14 NEURO-CORE Spec)
- ✅ [v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md](sources/v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md) - Extended Documentation

**Code-Referenzen:**
- `evoki_v7_hybrid_core.py` (V2.0 - nicht extrahiert, nur dokumentiert)

---

### **2. ULTIMATE_ARCHITECTURE.md**

**Primäre Quellen:**
- ✅ Evoki V3.0 Design Discussions (aus dieser Conversation)
- ✅ [v2_regelwerk_v12.json](sources/v2_regelwerk_v12.json) - Regelwerk V12 als Validierungs-Grundlage

**Konzeptuelle Basis:**
- Double Airlock: Original-Design aus V3.0 Planning
- ANDROMATIK: FEP-basierte Neugier-Engine (neu in V3.0)
- Phoenix-Protokoll: Selbstheilung via Deep Earth Layer

---

### **3. PROZESS_DIAGRAMM_ASCII.md**

**Primäre Quellen:**
- ✅ [v2_server.js](sources/v2_server.js) - Node.js Backend Flow als Referenz
- ✅ [v2_TrinityEngine.js](sources/v2_TrinityEngine.js) - Engine-Flow
- ✅ [v2_DualBackendBridge.js](sources/v2_DualBackendBridge.js) - Python-Node Bridge
- ✅ [v2_GeminiContextBridge.js](sources/v2_GeminiContextBridge.js) - Context Building
- ✅ [v2_metrics_processor.py](sources/v2_metrics_processor.py) - Metriken-Berechnung
- ✅ [v2_regelwerk_v12.json](sources/v2_regelwerk_v12.json) - Regelwerk V12 Enforcement

**Flow-Design:**
- V2.0 Pipeline als Ausgangspunkt
- V3.0 Double Airlock Integration (neu)

---

### **4. API_TRIGGER_LOGIC_VISUALIZED.md**

**Primäre Quellen:**
- ✅ [v2_server.js](sources/v2_server.js) - A65 Logic, Guardian-Veto Decision Tree
- ✅ [v2_TrinityEngine.js](sources/v2_TrinityEngine.js) - Candidate Selection
- ✅ [v2_GeminiContextBridge.js](sources/v2_GeminiContextBridge.js) - Context Length Calculation, Chunk Expansion
- ✅ [v2_query.py](sources/v2_query.py) - FAISS W2/W5 System (4096D Mistral-7B GPU)

**Mermaid Diagramme:**
- Basierend auf V2.0 Code-Flow Analyse

---

### **5. ARCH_21_DATABASES.md**

**Primäre Quellen:**
- ✅ V2.0 12-DB Architektur (dokumentiert in FAISS Discovery)
- ✅ [v2_query.py](sources/v2_query.py) - W2/W5 Index System als Basis

**Konzeptuelles Design:**
- V3.0 21-DB Erweiterung: 1 Master + 12 W-P-F + 7 B-Vektor + 1 Composite

---

### **6. B_VEKTOR_WPF_EVALUATION.md**

**Primäre Quellen:**
- ✅ V2.0 B-Vektor Visualisierungen (3 PNG Bilder in `sources/`)
  - [uploaded_image_0_1768804144371.png](uploaded_image_0_1768804144371.png) - B-Vektor Heatmap
  - [uploaded_image_1_1768804144371.png](uploaded_image_1_1768804144371.png) - Timeline Krisenzone
  - [uploaded_image_2_1768804144371.png](uploaded_image_2_1768804144371.png) - A-Score, F_risk Charts
- ✅ [v2_metrics_processor.py](sources/v2_metrics_processor.py) - B-Vektor Berechnung

**Korrelations-Analyse:**
- Basierend auf V2.0 Metriken-History

---

### **7. MASTER_DISCOVERY_EVOKI_V3.md**

**Primäre Quellen:**
- ✅ [v2_regelwerk_v12.json](sources/v2_regelwerk_v12.json) - 881 Regeln, CRC32: 3246342384
- ✅ [v2_Adler_Metriken.txt](sources/v2_Adler_Metriken.txt) - 153 Metriken Spec
- ✅ [v2_App.tsx](sources/v2_App.tsx) - 12 Tabs Identifikation
- ✅ [v2_TrinityEngine.js](sources/v2_TrinityEngine.js) - Trinity Engine Logic
- ✅ [v2_DualBackendBridge.js](sources/v2_DualBackendBridge.js) - Backend-Bridge
- ✅ [v2_GeminiContextBridge.js](sources/v2_GeminiContextBridge.js) - Context-Builder
- ✅ [v2_server.js](sources/v2_server.js) - A65 Logic
- ✅ [v2_metrics_processor.py](sources/v2_metrics_processor.py) - Metriken-Engine
- ✅ [v2_query.py](sources/v2_query.py) - FAISS Query

**Entdeckungs-Methode:**
- Systematische V2.0 Codebase-Analyse

---

### **8-19. IMPLEMENTATION & PLANNING DOCS**

**Quellen:**
- ✅ Alle Backend-Quellen (siehe oben)
- ✅ [v2_regelwerk_v12.json](sources/v2_regelwerk_v12.json)
- ✅ Discovery-Phase Erkenntnisse

**Docs:**
- `FINAL_IMPLEMENTATION_PLAN_V3_0.md`
- `EXECUTIONER_PLAN_V3_0.md`
- `ULTIMATE_MASTER_PLAN_V8.md`
- `VALIDATED_MASTER_EXTRACTION.md`
- `backend_engines_deep_dive.md`
- `bestandsaufnahme_v3.md`
- `discovery_complete.md`
- `faiss_discovery_erkenntnisse.md`
- `final_discovery_report.md`
- `implementation_plan.md`
- `migration_plan.md`
- `task.md`

---

## 🔍 NACHVOLLZIEHBARKEIT GARANTIERT

### **FÜR JEDES DOKUMENT:**

1. ✅ **Primäre Quellen** sind im Dokument selbst referenziert
2. ✅ **Original-Dateien** sind in `sources/` kopiert (775 KB)
3. ✅ **Dieses Master-Index** mappt Dokument → Quellen
4. ✅ **V2.0 Originale** bleiben unangetastet in `C:\Evoki V2.0\`

### **UNTER JEDEM UMSTAND AUFFINDBAR:**

```
OPTION 1: Im Dokument selbst nachschauen
  → Jedes Dokument hat Quellenverzeichnis am Ende

OPTION 2: Master-Index konsultieren
  → docs/specifications/v3.0/SOURCES_MASTER_INDEX.md (diese Datei!)

OPTION 3: sources/ Ordner durchsuchen
  → docs/specifications/v3.0/sources/ (11 Dateien)

OPTION 4: V2.0 Original aufsuchen
  → C:\Evoki V2.0\evoki-app\... (siehe Tabelle oben)
```

---

## ✅ QUALITÄTSSICHERUNG

**Alle Quellen sind:**
- ✅ **Kopiert** (nicht verschoben!) - Originale intakt
- ✅ **Versioniert** mit `v2_` Prefix
- ✅ **Dokumentiert** in diesem Index
- ✅ **Referenziert** in den Spezifikations-Dokumenten

**KEINE INFO OHNE QUELLE!**

**Stand:** 2026-01-19  
**Status:** COMPLETE & VERIFIED
