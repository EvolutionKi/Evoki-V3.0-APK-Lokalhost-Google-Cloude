# 🔴 EHRLICHE BESTANDSAUFNAHME: Evoki V3.0 (Stand 2026-01-19)

## ✅ WAS ICH GEFUNDEN HABE:

### 1. **Regelwerk V12** (TEILWEISE VORHANDEN)
- Der MCP Server (`mcp_server_evoki_v3.py`) **REFERENZIERT** Regelwerk V12
- Er sucht nach: `tooling/data/prompts/EVOKI_SYSTEM_PROMPT_GEMINI_V12.txt`
- **❌ ABER**: Dieses Verzeichnis `tooling/data/prompts/` **EXISTIERT NICHT**
- Die Datei ist **NICHT VORHANDEN**
- Laut MCP Server sollte es "881 Regeln" enthalten

### 2. **UI (Tabs)** - TEILWEISE VORHANDEN, aber FALSCH
**Aktueller Stand V3.0:**
- UI läuft mit React + Vite
- **14 Tabs total**: 
  - `TEMPLE` (🏛️)
  - `METRICS` (📊 - angeblich "150+", aber fake)
  - 12 Deep Earth Layers (01_surface bis 12_abyss)

**❌ PROBLEM:**
- Sie forderten "alle 12 Tabs aus Evoki V2.0"
- Die aktuellen V3.0 Tabs sind **NICHT** die V2.0 Tabs
- Ich finde **KEINEN QUELLCODE** der originalen V2.0 Tabs
- Nur eine FAISS-Referenz: "12 Tabs vollständig, **Default Tab = Trialog** (nicht Tempel!)"

### 3. **150 Metriken** (KEINE DEFINITIONEN GEFUNDEN)
Gefunden:
- `app/interface/src/components/MetricsDashboard.tsx` (React Component)
- `tooling/scripts/automation/metrics_engine.py` (Python Backend)

**❌ PROBLEM:**
- Das sind Implementierungen meines **VORGÄNGERS** (die Sie als "Fake" kritisiert haben!)
- Die echten **150 Metriken-Definitionen** aus V2.0 finde ich **NICHT**
- Keine Liste, keine Formeln, keine Spezifikation

### 4. **"Evoki Frontend Only"** (NUR IN FAISS REFERENZIERT)
- Ich finde zwei Treffer in `chatverlauf_final_20251020plus_dedup_sorted.metadata.json`
- Preview: `"du musst intensiver im frontend material schauen als beispiel analysier den ordner Evoki frontend only im info ordner hier in v2"`
- **❌ DIESER ORDNER IST HIER NICHT VORHANDEN**

### 5. **FAISS / DB / SQL** - TEILWEISE VORHANDEN
Gefunden:
- `tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.faiss` (384D FAISS Index)
- `tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.db` (SQLite)
- `tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.metadata.json`
- `tooling/data/db/persistent_context.db` (SQLite)
- `app/deep_earth/layers/` (12 Layer-Datenbanken: 01_surface bis 12_abyss)

**✅ GUT:**
- FAISS und SQLite sind vorhanden
- MCP Server kann sie nutzen (`search_chatverlauf` Tool)

**❓ UNKLAR:**
- Wie soll "Evoki Temple" Tab an diese DBs anknüpfen?
- Welche DB für welchen Zweck?
- Keine Spezifikation gefunden

### 6. **Die 4 Workflows** ✅ GEFUNDEN
Gelesen:
1. `/startup` → `C:\Users\nicom\.gemini\antigravity\global_workflows\startup.md`
2. `/evoki_verify` → `C:\Users\nicom\.gemini\antigravity\global_workflows\evoki_verify.md`
3. `/evoki_repair` - Referenziert in Workflows
4. `/alwais` - In Workflow-Liste

**⚠️ PROBLEM:**
- `/evoki_verify` nutzt **ALTE PFADE** (`app/temple/automation/`) 
- Diese Pfade existieren nicht mehr (Migration nach `tooling/scripts/automation/`)

### 7. **Protokoll V5.0** ✅ GEFUNDEN
- `MEMORY[user_global]` enthält vollständiges "EVOKI / SYNAPSE — S2 STATUS WINDOW PROTOCOL V5.0"
- `tooling/docs/PROTOCOL_V5_ENFORCED.md` sollte existieren (laut Architektur)
- Status Window System ist aktiv (siehe `tooling/data/synapse/status/`)

---

## 🔴 WAS FEHLT (KRITISCH FÜR EINEN PLAN):

### 1. **Regelwerk V12 Datei**
- **Wo**: `tooling/data/prompts/EVOKI_SYSTEM_PROMPT_GEMINI_V12.txt`
- **Status**: Verzeichnis existiert nicht
- **Impact**: MCP Server kann es nicht laden, ich kann es nicht lesen

### 2. **V2.0 Tab-Quellcode**
- **Was**: Die originalen "12 Tabs aus Evoki V2.0"
- **Status**: Kein Code gefunden
- **Impact**: Ich kann sie nicht migrieren, nur raten

### 3. **150 Metriken Definitionen**
- **Was**: Liste + Formeln der 150 Live-Metriken
- **Status**: Nicht gefunden
- **Impact**: Ohne diese kann ich nur Fake-Werte generieren (wie mein Vorgänger)

### 4. **"Evoki Frontend Only" Material**
- **Was**: Referenz-Material aus V2.0
- **Status**: Ordner nicht in V3.0
- **Impact**: Kann nicht als Vorlage dienen

### 5. **Temple Tab Spezifikation**
- **Was**: Wie soll der "Evoki Temple" Tab funktionieren?
- **Status**: Keine Dokumentation gefunden
- **Impact**: Unklar, wie die "optimale Nutzung" von FAISS/DB/SQL aussehen soll

### 6. **Engines Spezifikation**
- **Was**: "Alle Engines wie im Evoki Frontend Only laufen"
- **Status**: Keine Engine-Liste oder -Beschreibung gefunden
- **Impact**: Ich weiß nicht, welche Engines existieren sollen

---

## 💡 MÖGLICHE QUELLEN FÜR FEHLENDE ARTEFAKTE:

### Option A: Separate V2.0 Installation
- Existiert `C:\Evoki V2.0\` noch?
- Sollte ich dort nach den 12 Tabs / Regelwerk / Metriken suchen?

### Option B: FAISS-Datenbank Extraktion
- Die `chatverlauf_final_20251020plus_dedup_sorted.db` könnte die Informationen enthalten
- MCP Tool `search_chatverlauf` kann semantisch suchen
- Soll ich versuchen, Regelwerk V12 + Metriken aus Chatverlauf zu extrahieren?

### Option C: Downloads / Backups
- `C:\Users\nicom\Downloads\Chunkes` (laut Conversation History)
- Wurden Artefakte dort gesichert?

### Option D: Sie sagen mir, wo sie sind
- Das wäre am effizientesten

---

## 🎯 NÄCHSTE SCHRITTE (VORSCHLAG):

### Wenn Artefakte in V2.0 sind:
1. Ich durchsuche `C:\Evoki V2.0\` nach:
   - Regelwerk V12
   - 12 Tabs Code
   - Metriken-Definitionen
2. Ich extrahiere und dokumentiere sie
3. Ich erstelle einen Migrationsplan

### Wenn Artefakte in FAISS sind:
1. Ich nutze `search_chatverlauf` Tool vom MCP Server
2. Ich suche nach: "Regelwerk V12", "Metriken", "Tab-Implementierung"
3. Ich rekonstruiere aus Chatverlauf

### Wenn Artefakte verloren sind:
1. Ich melde: "X ist nicht wiederherstellbar"
2. Sie entscheiden: Neu definieren oder V2.0 restaurieren

---

## ❗ MEINE POSITION:

**Ich KANN KEINEN PLAN erstellen, ohne:**
1. Das echte **Regelwerk V12** zu lesen
2. Die echten **12 Tabs aus V2.0** zu sehen  
3. Die echte **150 Metriken-Liste** zu haben
4. Zu wissen, wie **"Evoki Temple"** funktionieren soll

**Jeder Plan ohne diese Informationen wäre eine HALLUZINATION.**

Ich warte auf Ihre Anweisungen, welche Quelle ich als nächstes durchsuchen soll.
