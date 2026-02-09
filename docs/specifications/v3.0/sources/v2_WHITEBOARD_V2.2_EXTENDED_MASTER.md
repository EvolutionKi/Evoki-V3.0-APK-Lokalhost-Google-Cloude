# 🧭 WHITEBOARD_V2.1_FIXED.md
## EVOKI — V2 Reparatur-Patch (konfliktfest) + Legacy-V2 Anhang

**Version:** V2.1.0 (Patch auf V2)  
**Datum:** 29. Dezember 2025  
**Status:** Fix-Patch (Production-Blocker behoben, Widersprüche entschärft)  

> Ziel: Deine V2 bleibt als historischer Kontext erhalten, aber die **bindenden** Regeln sind oben konsolidiert und widerspruchsfrei.
> Alles im Anhang ist **Legacy** und darf die Regeln hier oben nicht überschreiben.

---

## 0) Geltung & Konfliktauflösung

Dieses Dokument hat 2 Bereiche:

1. **A. Normative Fix-Spezifikation (BINDEND)** — gilt sofort, überschreibt widersprüchliche Stellen im Legacy-Anhang  
2. **B. Legacy-V2 (NICHT-NORMATIV)** — historische Notizen / Entwürfe / Roadmap

**Konfliktregel:** Wenn A und B widersprechen, gilt **A**.

**Normative Marker:**  
- **[MUST]** zwingend  
- **[MUST NOT]** verboten  
- **[SHOULD]** Standard  
- **[MAY]** optional / experimentell

---

## A) Normative Fix-Spezifikation (BINDEND)

### A1) Master Endpoint Truth Table (Single Source of Truth)

✅ **IMPLEMENTIERT / ZIEL-ENDPOINTS (authoritative)**  
- **GET** `/health`  
- **GET** `/api/v1/health`  
- **GET** `/api/v1/status`  
- **POST** `/api/bridge/process` *(Legacy non-streaming)*  
- **POST** `/api/bridge/stream` *(SSE Streaming — ersetzt Timeout-Probleme)*

❌ **OPTIONAL / SPÄTER** *(nur implementieren, wenn wirklich gebraucht; sonst weglassen)*  
- `GET /api/pipeline/logs`  
- `GET /api/v1/system/errors`  
- `GET /api/v1/trialog/session`  
- `GET /api/v1/context/daily`  
- `GET /api/history/trialog/load`  
- `POST /api/history/trialog/save`

> **[MUST]** Alle weiteren Stellen im Dokument dürfen Endpoints nur via diese Tabelle referenzieren.

---

### A2) Frontend Build Safety (Native Modules Kill-Switch)

**Problem:** Native Node-Module im Frontend crashen Vite / Browser-Bundle.

- **[MUST NOT]** `better-sqlite3` im Frontend  
- **[MUST NOT]** `sqlite3` im Frontend  
- **[MUST NOT]** Node.js native bindings / `fs`, `path`, `child_process`, usw. im Browser-Bundle  
- **[MUST]** DB-Operationen **Backend-only** (oder WASM wie `sql.js`)

**CI Guardrails (minimal & effektiv):**
```bash
cd frontend
grep -r "better-sqlite3" package.json && exit 1 || true
grep -r '"sqlite3"' package.json && exit 1 || true
npm run build
```

---

### A3) Datenwahrheit: SQL ist Text-Truth

- **[MUST]** SQL Source DB ist die autoritative Textquelle.  
- **[MUST NOT]** FAISS-Reassembly überschreibt SQL-Text.  
- **[MUST]** Bei Divergenz: Hash/Length-Check + Log, **SQL gewinnt**.

---

### A4) SSE Streaming: Heartbeat + Cancel-Safety (Production-Blocker Fix)

**SSE Headers (MUST):**
```js
res.writeHead(200, {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache, no-transform",
  "Connection": "keep-alive",
  "X-Accel-Buffering": "no"
});
```

**Heartbeat (MUST):** alle 15–30s, auch ohne Payload:
```js
const hb = setInterval(() => {
  if (!res.writableEnded) res.write(": heartbeat\n\n");
}, 20000);
```

**Cancellation transitive (MUST):**
- **[MUST]** Ein per-request `AbortController`  
- **[MUST]** `req.on("close")` → abort  
- **[MUST]** Signal in **ALLE** Subsysteme weitergeben (FAISS/Python, DB Reads, LLM Calls)

```js
app.post("/api/bridge/stream", async (req, res) => {
  const ac = new AbortController();

  req.on("close", () => ac.abort());

  try {
    await runPipeline(req.body, {
      signal: ac.signal,
      onProgress: (evt) => res.write(`data: ${JSON.stringify(evt)}\n\n`)
    });
  } catch (e) {
    res.write(`data: ${JSON.stringify({ type:"error", message:e.message })}\n\n`);
  } finally {
    clearInterval(hb);
    res.end();
  }
});
```

---

### A5) Health Checks sind passiv (kein Abort-Sharing)

- **[MUST NOT]** Health Checks dürfen **nie** globale Abort-Chains triggern  
- **[MUST]** Health Checks sind read-only (keine Worker-Restarts, kein Cache-Clear)

---

### A6) Token Mode Naming (V2-Fix)

V2 hatte die semantische Falle „Quick größer als Standard“. Fix:

- **Quick:** 20k  
- **Standard:** 25k  
- **Unlimited:** 1M

> **[MUST]** Standard ≥ Quick (Name muss zur Größe passen).

---

### A7) Metriken Count Fix (V14)

- **[MUST]** Referenziere konsistent: **153 Metriken (V14 Core)**  
- **[MUST NOT]** veraltetes „120+“ in bindenden Passagen.

---

## B) Legacy-V2 (NICHT-NORMATIV, HISTORISCH)

> Hinweis: Der folgende Block ist **dein ursprüngliches V2-Material** (automatisch mit ein paar Markierungen versehen),
> aber **nicht bindend**. Bei Widerspruch gilt immer Abschnitt A.

---

# WHITEBOARD_V2.md

# === ORIGINAL WHITEBOARD (UNVERÄNDERT) ===

﻿# 🌌 EVOKI V2.0 - WHITEBOARD (Ideensammlung)

**Datum:** 28. Dezember 2025  
**Status:** Entwicklungs-Discovery & Architektur-Mapping  
**Zweck:** Keine To-Do-Liste, nur Ideensammlung und Erkenntnisse

---

## 🔍 **ARCHITEKTUR-BLIND SPOTS & FUTURE VISION**

### 1. Identifizierte Blind Spots und versteckte Problembereiche
Trotz der Korrekturen in V3 gibt es architektonische "blinde Flecken", die bei fortschreitender Nutzung kritisch werden:

* **Das "Context-Drift" Paradoxon:** Das System webt Kontext aus ±2 Prompts um einen Treffer. **Blind Spot:** Wenn die Historie auf über 100.000 Chunks anwächst, könnten die "Metrik-Zwillinge" (SQL-Treffer) aus völlig unterschiedlichen Lebensphasen stammen. Der Orchestrator braucht eine **Time Decay Funktion**, die verhindert, dass uralte Metriken die aktuelle Analyse "vergiften".
* **LocalStorage als "Flaschenhals-Sackgasse":** Die Quellen warnen vor dem 4MB-Limit. **Blind Spot:** Selbst beim Ausweichen auf Backend-Logs bleibt der React-State der Single-Point-of-Failure. Bei 1M Tokens friert das UI ein. **Lösung:** Virtualisierung (react-window) und Partial State Updates sind zwingend.
* **Die "Finetuning-Echokammer":** Die "Labor-Strategie" sieht vor, Modelle mit den eigenen Chunks zu trainieren. **Risiko:** Wenn wir auf halluzinierten V1-Daten trainieren, zementieren wir Fehler. Wir brauchen ein "Golden Set" (verifizierte Chunks) für das Training.
* **Sentinel-Veto vs. LLM-Konfidenz:** Der Sentinel kann Scores massiv senken. **Blind Spot:** Wenn alle Top-Kandidaten blockiert werden, sendet das System "Restmüll". Wir brauchen einen **Emergency Refetch**, der bei Veto sofort neue, sicherere Parameter sucht.

### 2. Ungenutztes Potenzial der Architektur
* **Prädiktive Trauma-Warnung (Early Warning):** Da wir 153 Metriken (V14 Core) Metriken live haben, können wir die **Ableitung der PCI-Kurve** berechnen. Steigt sie über 3 Sessions stetig an? Warnung VOR dem Crash.
* **Automatisierte Metaphern-Synthese:** "Perfect Agreements" zwischen Metrik und Semantik können genutzt werden, um individuelle therapeutische Metaphern zu generieren.
* **Trialog als Architektur-Optimierer:** Der Analyst-Agent könnte die `performance_log.db` lesen und selbstständig Indizes rebalancen ("Self-Optimizing Architecture").

### 3. Visionäre Erweiterungen
* **Sovereign Personal AI:** Durch die Kombination von "Labor-Strategie" (Cloud-Training) und lokaler Inference (GTX 3060) wird Evoki zur **Black Box für das Ich** – 100% offline, 100% privat, Cloud-Qualität.
* **Cross-Session Chronicle:** Weg vom Append-Only Log hin zu einer dynamischen Wissenskarte, die Cluster im Deep Storage visualisiert.

## 📍 **FRONTEND KOMPONENTEN - AKTUELLER STATUS**

### ✅ **EVOKI TEMPEL V3 - HYPERSPACE EDITION** (Produktiv)
- **Datei:** `frontend/src/components/EvokiTempleChat.tsx`
- **Version:** V3 - Hyperspace Edition
- **Status:** ✅ AKTIV - Das ist der ECHTE Evoki Tempel
- **Features:**
  - 12-Database Distribuierte Speicherung
  - Token-Limits: 25k (quick), 20k (standard), 1M (max)
  - SHA256 Chain-Logik mit kontinuierlicher Liste
  - Metriken-Berechnung auf alle DBs (153 Metriken (V14 Core))
  - A65 Multi-Candidate Selection (3 Kandidaten)
  - Phase 4 Token Distribution:
    - 32% Narrative Context (8.000 Tokens)
    - 12% Top-3 Chunks (3.000 Tokens)
    - 20% Overlapping Reserve (5.000 Tokens)
    - 4% RAG Chunks (1.000 Tokens)
    - 32% Response Generation (8.000 Tokens)
- **Backend Endpoint:** `/api/bridge/process`
- **Vektorisierung:** Live mit allen 153 Metriken (V14 Core) Metriken

### ⚠️ **CHATBOT PANEL** (Legacy aus V1)
- **Datei:** `frontend/src/components/ChatbotPanel.tsx`
- **Version:** V1 - Generischer Chatbot
- **Status:** 🟡 OBSOLET - War der erste generische Google-Chatbot
- **Historie:**
  - Ursprünglich: Generische Google API Interaktion
  - Dann: Erster "Tempel"-ähnlicher Anschluss (aus Respekt zu Evoki nicht so genannt)
  - Jetzt: Durch EvokiTempleChat V3 ersetzt
- **Backend Endpoint:** `/api/bridge/process` (gleicher wie V3, aber weniger Features)
- **Unterschied zu V3:**
  - Keine 12-DB Distribution
  - Keine Phase 4 Token Distribution
  - Keine Tempel-Metriken
  - Keine SHA256 Chain
  - Kein A65 Multi-Candidate
- **Idee:** Könnte entfernt oder als "Simple Chat Mode" behalten werden

---

## 🔍 **PIPELINE-ÜBERWACHUNG**

### ✅ **PIPELINE LOG PANEL** (Implementiert)
- **Datei:** `frontend/src/components/PipelineLogPanel.tsx`
- **Status:** ✅ VORHANDEN als Tab 12
- **Zweck:** Trackt ALLE Übergabepunkte für Fehlerdiagnose
- **12 Protokollierte Schritte:**
  1. User Input → Frontend
  2. Frontend → Backend (`/api/bridge/process`)
  3. Backend → Python FastAPI Service (`POST localhost:8000/search`) ⚠️ **NICHT CLI-Spawn!**
  4. Python FAISS → JSON Output
  5. Backend Parse → DualBackendBridge
  6. DualBackendBridge → Trinity Engines
  7. Trinity Results → A65 Candidate Selection
  8. A65 → GeminiContextBridge
  9. Context Building → Gemini Prompt
  10. Gemini API Call → Response
  11. Response → Vector Storage (12 DBs)
  12. Final Response → Frontend

**🔧 IMPLEMENTATION NOTE:**
- **Legacy-Konzept:** `spawn(pythonPath, ['query.py', prompt])` (2-5s Modell-Ladezeit pro Request)
- **Production-Reality:** Persistenter FastAPI Microservice (Port 8000)
  - Lädt sentence-transformers + FAISS **einmal** beim Systemstart (30s)
  - Requests: `POST http://localhost:8000/search` (<100ms pro Request)
  - Endpoints: `/search`, `/health`, `/reload-index`
- **Grund:** CLI-Spawn würde FAISS bei jedem Request neu laden → Timeout-Hölle

### ❌ **BACKEND ENDPOINT FEHLT**
- **Erwartet:** `GET /api/pipeline/logs`
- **Status:** ❌ NICHT IMPLEMENTIERT in `backend/server.js`
- **Frontend Code:** Line 128 in PipelineLogPanel.tsx ruft es auf
- **Idee:** Backend muss Pipeline-Logs persistieren (JSONL-File oder SQLite)
- **Daten-Struktur:**
  ```typescript
  interface PipelineLogEntry {
    id: string;
    timestamp: string;
    session_id: string;
    message_id: string;
    step_number: number; // 1-12
    step_name: string;
    data_transfer: {
      from: string;
      to: string;
      text_preview: string; // Erste 200 Zeichen
      full_text: string;
      size_bytes: number;
      token_count?: number;
    };
    metadata?: Record<string, any>;
  }
  ```
- **Zweck:** Mikro-Tuning wenn Google API unpasende Antworten liefert
- **Use Case:** Fehlerquelle direkt identifizieren (FAISS? Trinity? Gemini?)

---

## 🔐 **GENESIS ANCHOR (A51)**

### ✅ **IMPLEMENTIERT ABER DEAKTIVIERT**
- **Datei:** `backend/server.js` Line 26-62
- **Status:** 🟡 WARNUNG-MODUS (nicht kritisch während Entwicklung)
- **Funktion:** `verifyGenesisAnchor()`
- **Verhalten:**
  - Prüft `backend/public/genesis_anchor_v12.json`
  - Wenn NICHT gefunden: ⚠️ WARNING, aber Server startet
  - Wenn MALFORMED: ❌ FATAL, Server Exit
  - Wenn OK: ✅ Loggt SHA256/CRC32 Hashes
- **Geprüfte Werte:**
  - `engine.combined_sha256` (Combined Hash Regelwerk + Registry)
  - `engine.regelwerk_crc32`
  - `engine.registry_crc32`
- **Idee für später:** Nach Stabilisierung re-enablen als Produktionsschutz
- **Entwicklungs-Bypass:** Aktuell durch "Datei nicht gefunden" → Warning statt Exit

---

## 🧩 **LOSE ENDEN & OBSOLETE FEATURES**

### 📸 **SNAPSHOT/SCREENSHOT SYSTEM**
- **Status:** 🟡 HALB-OBSOLET
- **Service:** `frontend/src/services/core/snapshotService.ts`
- **Funktionen:**
  - `saveSnapshotToFile(appState)` - Speichert kompletten App-State als JSON
  - `loadSnapshotFromFile(file)` - Lädt State aus File
- **Verwendet in:**
  - `Header.tsx` Line 44, 52 (Save/Load Buttons)
  - `App.tsx` Line 943-944 (Handler)
- **Historie:**
  - **V1:** Download-basierte Persistenz (localStorage-Backup als JSON)
  - **V2:** Wird durch echtes Backend mit Auto-Save ersetzt
- **Idee:** 
  - Behalten für manuelle Backups?
  - Oder komplett entfernen zugunsten Backend-Persistenz?
  - Könnte nützlich sein für "Export gesamte Session"

### 💾 **CACHE-MANAGEMENT**
- **Status:** 🔍 ZU PRÜFEN
- **Mögliche Komponenten:**
  - `DataCachePanel.tsx` (falls vorhanden)
  - LocalStorage-basierte Caches
  - Service Worker Caches
- **Idee:** Nur minimal cachen, Backend ist Source of Truth
- **Use Case:** Offline-Fähigkeit für Trialog? (später)

### 📊 **WEITERE UI-TOOLS MIT BACKEND-ANBINDUNG**

#### ✅ **ObsidianLiveStatus** (Operational-KI Status)
- **Datei:** `frontend/src/components/ObsidianLiveStatus.tsx`
- **Endpoint:** `GET /api/v1/health`
- **Zweck:** Backend Health Check
- **Status:** ✅ AKTIV

#### ✅ **TrialogPanel** (Multi-Agent System)
- **Datei:** `frontend/src/components/TrialogPanel.tsx`
- **Endpoints:**
  - `GET /api/v1/trialog/session` (Session laden)
  - `POST /api/v1/interact` (Agent Response)
  - `GET /api/v1/context/daily` (Daily Context)
- **Status:** ✅ AKTIV

#### ✅ **ErrorLogPanel** (Fehlerprotokoll)
- **Datei:** `frontend/src/components/ErrorLogPanel.tsx`
- **Endpoint:** `GET /api/v1/system/errors`
- **Zweck:** Backend-persistierte Fehler abrufen
- **Status:** ✅ AKTIV

#### ✅ **VoiceSettingsPanel** (TTS)
- **Datei:** `frontend/src/components/VoiceSettingsPanel.tsx`
- **Endpoint:** `POST https://api.openai.com/v1/audio/speech` (Extern)
- **Zweck:** Text-to-Speech via OpenAI
- **Status:** ✅ AKTIV

#### ✅ **App.tsx Global Endpoints**
- `GET /api/v1/status` - Backend Status (Line 523)
- `GET /api/v1/health` - Health Check (Line 536)
- `GET /api/history/trialog/load` - Trialog Historie laden (Line 770)
- `POST /api/history/trialog/save` - Trialog Historie speichern (Line 814)

---

## 🔗 **VOLLSTÄNDIGE BACKEND-ENDPOINTS LISTE**

### ✅ **IMPLEMENTIERT IN BACKEND:**
- `GET /health` → Backend Health
- `GET /api/v1/status` → Enhanced Status mit Hyperspace Info
- `POST /api/bridge/process` → **HAUPT-PIPELINE** (DualBackendBridge)
- `POST /api/temple/session/save` → Tempel Session speichern
- `POST /api/temple/process` → Enhanced Tempel (mit A65)
- `POST /api/v1/interact` → Trialog Interaction
- `GET /api/temple/debug` → Vector DB Debug
- `GET /api/temple/debug-full` → Full Request Debug

### ❌ **FEHLT NOCH (Frontend ruft auf, Backend fehlt):**
- `GET /api/pipeline/logs` → Pipeline Log Entries
- `GET /api/v1/system/errors` → Error Log Persistence
- `GET /api/v1/trialog/session` → Trialog Session Info
- `GET /api/v1/context/daily` → Daily Context
- `GET /api/history/trialog/load` → Trialog History Load
- `POST /api/history/trialog/save` → Trialog History Save

---

## 🎯 **ERKENNTNISSE & IDEEN**

### **1. ChatbotPanel.tsx Entfernen?**
- **Pro Entfernung:**
  - Komplett durch EvokiTempleChat V3 ersetzt
  - Obsolete Features (keine 12-DB, kein A65, keine Phase 4)
  - Verwirrt beim Debugging (zwei ähnliche Komponenten)
- **Pro Behalten:**
  - Als "Simple Mode" für schnelle Tests
  - Backup falls V3 Probleme macht
  - Historischer Wert (erste Implementation)
- **Idee:** Umbenennen in `LegacyChatbot.tsx` + deaktivieren im Tab-System

### **2. Pipeline-Logging Backend implementieren**
- **Warum wichtig:**
  - Fehlerquelle SOFORT identifizieren
  - Mikro-Tuning wenn Gemini seltsame Antworten gibt
  - Performance-Analyse (welcher Schritt ist langsam?)
- **Implementation:**
  - JSONL-File: `backend/logs/pipeline_logs.jsonl`
  - Jeden Schritt loggen mit Timestamps
  - Endpoint: `GET /api/pipeline/logs?session_id=...`
  - Auto-rotate bei 100MB (max 10 Files)
- **Integration:** Bereits in DualBackendBridge.js Line 46-51 vorbereitet!

### **3. Genesis Anchor Re-enablement nach Stabilisierung**
- **Aktuell:** Warnung-Modus (Entwicklung)
- **Später:** Kritisch-Modus (Produktion)
- **Idee:** Environment Variable `GENESIS_ANCHOR_STRICT=false/true`
- **Zweck:** Verhindert unauthorisierte Regelwerk-Änderungen

### **4. Snapshot-System Evolution**
- **V1:** Download JSON (keine Persistenz)
- **V2:** Backend Auto-Save (geplant)
- **Idee:** Snapshots als "Session Export" behalten
  - User kann komplette Session als JSON downloaden
  - Forensische Analyse möglich
  - Kann in anderen Evoki-Instanzen importiert werden
  - Format: `evoki_session_export_20251228_153045.json`

### **5. Cache-Strategie klären**
- **Prinzip:** Backend = Source of Truth
- **Frontend Cache:** Nur für UI-Performance
  - Aktuelle Session in Memory
  - Keine LocalStorage-Persistenz von Vektordaten
  - Service Worker nur für Assets, nicht für API-Responses
- **Backend Cache:**
  - FAISS Indices im Memory halten (schneller)
  - Trinity Results cachen? (überprüfen)

### **6. V1-Daten Import vorbereiten**
- **Quelle:** Deine 02.25-10.25 Chathistorie (vektorisiert)
- **Ziel:** In 12 Vector DBs + Chronologische Historie importieren
- **Format:** Bereits vorhanden als `chunks_v2_2.pkl` + FAISS Index
- **Idee:** Import-Script für historische Daten
  - Liest V1 Chunks
  - Berechnet 153 Metriken (V14 Core) Metriken nachträglich
  - Schreibt in neue 12-DB Struktur
  - Erhält Timecodes & Session-IDs

### **7. Trialog Backend-Anbindung komplettieren**
- **Status:** Endpoints im Frontend vorhanden, Backend fehlt teilweise
- **Idee:** Trialog separate Session-Verwaltung
  - Eigene Vector DBs (4 DBs: trialog_W_m2, trialog_W_m5, trialog_W_p25, trialog_W_p5)
  - Multi-Agent Responses speichern
  - Chronicle-Integration für Meta-Statements
  - Auto-TTS per Agent-Profil

---

## 🧪 **TEST-IDEEN**

### **Test 1: Ersten Tempel-Prompt schicken**
- **Ziel:** Pipeline End-to-End verifizieren
- **Prompt:** "Erzähl mir von den Zwillingen im Kindergarten"
- **Erwartung:**
  - FAISS findet relevante Chunks
  - Trinity kombiniert mit Metriken
  - A65 selektiert besten Kandidaten
  - Gemini generiert kontextuelle Antwort
  - 12 DBs werden beschrieben
  - Chronologische Historie entsteht

### **Test 2: Trialog erste Session**
- **Ziel:** Multi-Agent System testen
- **Agents:** Analyst + Regel + Synapse (Explorer & Connector)
- **Prompt:** "Analysiert die aktuelle Evoki V2.0 Architektur"
- **Erwartung:**
  - 3 Agents antworten nacheinander
  - Jede Antwort in Vector DB
  - Chronicle-Eintrag mit Meta-Statement
  - TTS für jeden Agent (falls aktiviert)

### **Test 3: Pipeline-Log Analyse**
- **Ziel:** Übergabepunkte sichtbar machen
- **Methode:** Test 1 wiederholen + Pipeline-Log öffnen
- **Erwartung:**
  - 12 Steps sichtbar
  - Text-Preview für jeden Step
  - Token-Counts korrekt
  - Timestamps nachvollziehbar

---

## 💡 **NÄCHSTE SCHRITTE (KEINE TO-DO, NUR IDEEN)**

1. **Backend starten & Test 1 durchführen**
2. **Pipeline-Logging Backend implementieren**
3. **Fehlende Trialog-Endpoints implementieren**
4. **ChatbotPanel.tsx Entscheidung treffen**
5. **V1-Daten Import-Script entwickeln**
6. **Genesis Anchor Environment Variable**
7. **Snapshot-System zu "Session Export" umbauen**
8. **Cache-Strategie dokumentieren**

---

## � **LOCALSTORAGE & CACHE-ANALYSE**

### ✅ **LocalStorage Nutzung (VOLLSTÄNDIG ERFASST):**

#### **1. Auto-Save System (App.tsx)**
- **Key:** `evoki_autosave`
- **Content:** `{ apiConfig, activeTab, ... }`
- **Limit:** 4MB (LOCAL_STORAGE_LIMIT_BYTES)
- **Auto-Save Interval:** 30s (Handler in App.tsx Line 635)
- **Warning:** Zeigt Warnung bei >3.8MB
- **Risiko:** 🟡 MITTEL - Bei großen Sessions könnte Limit erreicht werden
- **Fix:** Backend-Persistenz für große Daten nutzen

#### **2. Voice Settings (VoiceSettingsPanel.tsx)**
- **Keys:**
  - `openai_api_key` - OpenAI TTS API Key
  - `evoki_voice` - Selected Voice (alloy, echo, fable, onyx, nova, shimmer)
- **Risiko:** 🟢 NIEDRIG - Kleine Daten, nur Settings

#### **3. Backend URL (TrialogPanel.tsx)**
- **Key:** `evoki_backend_url`
- **Content:** Backend API URL (http://localhost:3001)
- **Risiko:** 🟢 NIEDRIG - Nur String

#### **4. Chronicle Worker (chronicleWorkerClient.ts)**
- **Key:** `CHRONICLE_STORAGE_KEY` (Konstante)
- **Content:** ChronicleEntry[]
- **Risiko:** 🟡 MITTEL - Wächst mit jeder Meta-Statement
- **Note:** Chatbot Panel entfernt, Chronicle-Integration deaktiviert

#### **5. Integrity Worker (integrityWorkerClient.ts)**
- **Keys:**
  - `LOGBOOK_STORAGE_KEY` - ProjectLogbook Entries
  - `APP_ERRORS_STORAGE_KEY` - ApplicationError[]
- **Risiko:** 🟡 MITTEL - Error-Log kann groß werden
- **Circuit Breaker:** Bei QuotaExceeded → stoppt Speicherung

#### **6. Browser Storage Adapter (BrowserStorageAdapter.ts)**
- **Keys:**
  - `evoki_memory` - Engine Memory State
  - `evoki_chronik` - Engine Chronik (Append-Only Log)
- **Risiko:** 🔴 HOCH - Chronik wächst unbegrenzt (Append-Only!)
- **Note:** "Not fully implemented" laut Code

### ⚠️ **POTENTIELLE PROBLEME:**

1. **Auto-Save 4MB Limit:**
   - Bei vielen Trialog-Nachrichten → QuotaExceeded
   - Fix: Backend-Persistenz nutzen, LocalStorage nur für UI-State

2. **Chronik Append-Only:**
   - Keine Rotation, keine Limits
   - Fix: Implementiere Rotation oder deaktiviere komplett

3. **Circuit Breaker nicht überall:**
   - Nur in integrityWorkerClient implementiert
   - Fix: Alle LocalStorage-Writes mit try/catch + QuotaExceeded handling

### ✅ **KEINE INDEXEDDB, KEINE SESSIONSTORAGE:**
- Nur localStorage verwendet
- Keine Service Worker für Caching
- Keine komplexen Cache-Strategien

---

## 🚀 **STARTUP-SEQUENZ ANALYSE**

### **Loading Screen (App.tsx Line 6-70)**
- **Zweck:** Backend Health Check vor App-Start
- **Sequence:**
  1. Versucht Python Backend (Port 8000) - `/health`
  2. Fallback: Node Backend (Port 3001) - `/health`
  3. Wartet 3s bei Erfolg, 5s bei Fehler
  4. Ruft `onSystemReady()` auf
  5. App wird angezeigt
- **Status:** ✅ IMPLEMENTIERT
- **Risiko:** 🟡 MITTEL - 5s Timeout bei offline Backend könnte nerven

### **Genesis Startup Screen (GenesisStartupScreen.tsx)**
- **Zweck:** A51 Security Checks
- **5 Schritte:**
  1. Frontend Genesis Hash Integrity
  2. Backend Connection
  3. Backend Genesis Anchor Verification
  4. Security Protocols (A51)
  5. System Initialization
- **Status:** 🟡 OPTIONAL - Aktuell durch `isSystemReady = true` in App.tsx bypassed
- **Note:** "FIXED: Start ready, show app immediately" (App.tsx Line 180)

### **Engine Initialization (App.tsx Line 556)**
- **Sequence:**
  1. `evokiEngine.init()` wird gerufen
  2. Bei Erfolg: `genesisStatus = 'verified'`
  3. Bei Fehler: `genesisStatus = 'lockdown'` möglich
  4. Parallel Architecture Status Updates
- **Status:** ✅ IMPLEMENTIERT

### **Backend Health Check Loop (App.tsx Line 518)**
- **Endpoint:** `GET /api/v1/status` (primär) oder `GET /api/v1/health` (fallback)
- **Interval:** ❌ DEAKTIVIERT (Kommentar: "AbortSignal.timeout() sends SIGINT to backend!")
- **Risiko:** 🔴 HOCH - Health Check kann Backend killen!
- **Status:** 🟡 TEMP DISABLED

---

## 📦 **DEPENDENCIES & VERSIONS**

### **Frontend (package.json):**
- React: 18.2.0
- Vite: 7.1.11
- TypeScript: 5.8.2
- @google/genai: 1.25.0
- @microsoft/fetch-event-source: ^2.0.4 (✅ Neu für SSE Fix)
- chart.js: 4.4.2
- jszip: 3.10.1
- lucide-react: 0.363.0
- react-window: ^1.8.10 (✅ Neu für Virtualization / UI-Performance)
// REMOVED: better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) & sqlite3 (VERBOTEN im Frontend) (Crashen Vite Build!)

### **Backend (package.json):**
- express: 5.2.1
- cors: 2.8.5
- dotenv: 17.2.3
- node-fetch: 3.3.2

### ⚠️ **AUFFÄLLIGKEITEN:**

#### **🚨 KRITISCH: SQLite im Frontend Package.json!**

**Das Problem:**
- `better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend): 12.5.0` (❌ NATIVE NODE.JS MODULE!)
- `sqlite3 (VERBOTEN im Frontend): 5.1.7` (❌ NATIVE NODE.JS MODULE!)

**Beide sind C++ Native Bindings und können NICHT im Browser laufen!**

**Konsequenzen:**
1. ❌ **Vite-Build wird crashen** sobald du sie importierst
2. ❌ Kein Zugriff auf `fs`, `path`, native bindings im Browser
3. ❌ Tickende Zeitbombe (aktuell nicht verwendet, aber bei Import → Crash)

**Warum ist es drin?**
- Vermutlich aus V1 kopiert (wo Node.js Backend SQLite nutzt)
- Frontend braucht es NICHT (Backend ist Source of Truth)

**✅ SOFORT-FIX:**
```bash
cd frontend
npm uninstall better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) sqlite3 (VERBOTEN im Frontend)
```

**Alternative (falls Client-Side SQL wirklich nötig für Offline-Mode):**
- **`sql.js`** (WASM-basiert, läuft im Browser)
- **`wa-sqlite`** (WebAssembly SQLite)

**Für V2.0:** Backend ist die einzige SQL-Source. Frontend macht nur API-Calls!

---

**Weitere Auffälligkeiten:**
1. **Express 5.2.1:** Sehr neu, könnte Breaking Changes haben
2. **Node-Fetch:** Nur im Backend nötig, nicht im Frontend

---

## 🔍 **ALLE 12 TABS KOMPLETT:**

### ✅ **IMPLEMENTIERT & VOLLSTÄNDIG:**
1. **Engine-Konsole** (Tab.EngineConsole) - EngineConsolePanel.tsx
2. **Trialog** (Tab.Trialog) - TrialogPanel.tsx
3. **Agenten & Teams** (Tab.AgentSelection) - AgentSelectionPanel.tsx
4. **Evoki's Tempel V3** (Tab.TempleChat) - EvokiTempleChat.tsx
5. **Metrik-Tuning** (Tab.ParameterTuning) - ParameterTuningPanel.tsx
6. **Analyse** (Tab.Analysis) - Analysis.tsx
7. **Regelwerk-Suche** (Tab.RuleSearch) - RulePanel.tsx
8. **API** (Tab.API) - ApiPanel.tsx
9. **Stimme & API** (Tab.VoiceSettings) - VoiceSettingsPanel.tsx
10. **HyperV3.0 Deep Storage** (Tab.DeepStorage) - DeepStoragePanel.tsx
11. **Fehlerprotokoll** (Tab.ErrorLog) - ErrorLogPanel.tsx
12. **Pipeline Überwachung** (Tab.PipelineLog) - PipelineLogPanel.tsx

### ⚠️ **DEFAULT TAB:**
- **App.tsx Line 166:** `activeTab: Tab.Trialog`
- Beim Start wird Trialog geöffnet (nicht Tempel!)

---

## 🛡️ **ERROR HANDLING & LOGGING**

### **1. Global Error Handler (App.tsx Line 358)**
- **window.addEventListener('error')** → addApplicationError()
- **window.addEventListener('unhandledrejection')** → addApplicationError()
- **Lockdown Trigger:** Errors mit "GENESIS ANCHOR" oder "A51" → `genesisStatus = 'lockdown'`

### **2. Console Capture (App.tsx Line 385)**
- **console.log/warn/error** → redirected zu developerLog
- **Filtert:** [HMR], Auto-Save Messages
- **Risiko:** 🟡 MITTEL - Kann Performance bei vielen Logs beeinflussen

### **3. Fetch Interceptor (App.tsx Line 407)**
- **window.fetch** → wrapped mit Logging
- **Logged:** Nur non-OK responses (reduziertmit Noise)
- **Excluded:** `/api/system/log-error` (verhindert Loops)
- **Risiko:** 🟡 MITTEL - Bei vielen API-Calls viel Overhead

### **4. Critical Error Modal (CriticalErrorModal.tsx)**
- **Trigger:** errorType === 'system' ODER keywords (infinite loop, chain break, recursion, fatal)
- **Display:** Overlay mit Error-Details
- **Action:** System Lockdown möglich

### **5. Backend Error Logging (DEAKTIVIERT)**
- **App.tsx Line 338:** `POST /api/system/log-error` DISABLED
- **Reason:** "Verhindert fetch loops"
- **Status:** 🟡 AUSKOMMENTIERT

---

## � **KRITISCHE PIPELINE-ANALYSE - TIMEOUTS & RACE CONDITIONS**

### **⚠️ TIMEOUT-PROBLEM #1: Frontend vs Backend Race Condition**

**Das Problem:**
Frontend sendet Request mit 60s Timeout → Backend braucht aber möglicherweise länger für FAISS-Suche (33.795 Chunks!) + Gemini API → Frontend bricht ab BEVOR Backend fertig ist → User sieht "Timeout", aber Backend arbeitet weiter → **Zombie-Requests im Backend!**

#### **⚠️ TIMEOUT-PROBLEM #1: Frontend vs Backend Race Condition**

**Das Problem:**
Frontend sendet Request mit 60s Timeout → Backend braucht aber möglicherweise länger für FAISS-Suche (33.795 Chunks!) + Gemini API → Frontend bricht ab BEVOR Backend fertig ist → User sieht "Timeout", aber Backend arbeitet weiter → **Zombie-Requests im Backend!**

**❌ ALTE LÖSUNG (Legacy-Denken):**
```typescript
// Einfach Timeout hochsetzen
AbortSignal.timeout(120000); // 120s statt 60s
```
**Problem:** User starrt 120 Sekunden auf "Laden..." ohne zu wissen was passiert!

---

**✅ NEUE LÖSUNG: "HEARTBEAT" MIT SERVER-SENT EVENTS (SSE)**

### **🔄 SERVER-SENT EVENTS (SSE) PIPELINE-STREAMING**

**Konzept:** Backend sendet **LIVE STATUS-UPDATES** während es rechnet!

**UX-Effekt:**
```
User sieht in Echtzeit:
├─ ⏳ "Durchsuche 33.795 Erinnerungen..." (nach 2s)
├─ 🔍 "FAISS fand 47 semantische Treffer" (nach 15s)
├─ 📊 "Analysiere emotionale Metriken..." (nach 18s)
├─ ⚡ "Hazard-Level: 0.34 | PCI: 0.72" (nach 20s)
├─ 🎯 "3 Kontext-Paare ausgewählt" (nach 25s)
├─ 🧠 "Verwebe 3 Zeitlinien (±2 Prompts)..." (nach 28s)
├─ 🤖 "GPT-4 generiert Antwort..." (nach 35s)
└─ ✅ "Fertig! (38s total)" (nach 38s)
```

**Technischer Vorteil:**
- Verbindung bleibt offen
- **Timeouts werden IRRELEVANT** (solange Daten fließen!)
- User weiß IMMER was gerade passiert
- Kein "schwarzes Loch" von 60-120 Sekunden

---

#### **🚨 KRITISCHES PROBLEM: EventSource URL-Längen-Limit!**

**Das Problem:**
`EventSource` nutzt standardmäßig **GET-Requests**!

```typescript
// ❌ GEHT NICHT für lange Prompts!
const eventSource = new EventSource(
    `${backendUrl}/api/bridge/stream?prompt=${encodeURIComponent(userPrompt)}`
);
```

**Warum nicht?**
- **GET-URL-Limit:** 2.048 - 8.192 Zeichen (Browser/Server abhängig)
- **Deine Prompts:** Können RIESIG sein (Trauma-Analysen, 80k tokens!)
- **Konsequenz:** `HTTP 414 URI Too Long` → Pipeline startet nicht!

**Beispiel:**
```
Prompt: 500 Zeichen → OK
Prompt: 5.000 Zeichen → Browser blockt
Prompt: 50.000 Zeichen (80k tokens!) → Instant Crash
```

---

#### **✅ LÖSUNG: Fetch Stream API mit POST**

**Option A: POST-to-GET Pattern (Kompliziert)**
```typescript
// 1. Prompt im Cache speichern
const tokenResponse = await fetch('/api/bridge/init', {
    method: 'POST',
    body: JSON.stringify({ prompt })
});
const { token_id } = await tokenResponse.json();

// 2. SSE mit token_id (GET)
const eventSource = new EventSource(`/api/bridge/stream?token=${token_id}`);
```
**Problem:** Komplexer, Cache-Management nötig

---

**Option B: Fetch Stream API (EMPFOHLEN!)**

Nutze `fetch` mit `POST` + Stream Reader statt `EventSource`:

```typescript
// frontend/src/components/EvokiTempleChat.tsx

const handleSendWithFetchStream = async () => {
    setIsLoading(true);
    setPipelineSteps([]); // Reset progress
    
    try {
        // POST Request mit Body (keine URL-Limit!)
        const response = await fetch(`${backendUrl}/api/bridge/stream`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify({
                prompt: userPrompt,
                session_id: session.id,
                token_limit: selectedTokenLimit
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Stream lesen
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                console.log('Stream complete');
                break;
            }
            
            // Daten dekodieren
            buffer += decoder.decode(value, { stream: true });
            
            // SSE-Format parsen: "data: {...}\n\n"
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Letzten unvollständigen Teil behalten
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.substring(6); // "data: " entfernen
                    try {
                        const update = JSON.parse(jsonStr);
                        
                        // Update Progress UI
                        setPipelineSteps(prev => [...prev, {
                            step: update.step,
                            message: update.message,
                            timestamp: update.timestamp,
                            data: update.data
                        }]);
                        
                        // STEP 12 = Fertig!
                        if (update.step === 12 && update.status === 'completed') {
                            setMessages(prev => [...prev, {
                                role: 'assistant',
                                content: update.finalResponse.text,
                                timestamp: new Date().toISOString(),
                                metrics: update.finalResponse.metrics
                            }]);
                            setIsLoading(false);
                        }
                        
                        // Fehler
                        if (update.step === -1) {
                            setError(update.error);
                            setIsLoading(false);
                        }
                    } catch (parseError) {
                        console.error('JSON parse error:', parseError, jsonStr);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Stream error:', error);
        setError(error.message);
        setIsLoading(false);
    }
};
```

**Vorteile:**
- ✅ POST Request → **KEINE URL-Längen-Limits!**
- ✅ Funktioniert mit riesigen Prompts (500k+ characters)
- ✅ Gleiche SSE-Funktionalität wie EventSource
- ✅ Bessere Error-Handling Kontrolle
- ✅ Kann bei Unmount sauber abgebrochen werden

---

**Option C: @microsoft/fetch-event-source Library**

```bash
npm install @microsoft/fetch-event-source
```

```typescript
import { fetchEventSource } from '@microsoft/fetch-event-source';

await fetchEventSource(`${backendUrl}/api/bridge/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: userPrompt,
        session_id: session.id
    }),
    onmessage(event) {
        const update = JSON.parse(event.data);
        setPipelineSteps(prev => [...prev, update]);
        
        if (update.step === 12) {
            setMessages(prev => [...prev, update.finalResponse]);
            setIsLoading(false);
        }
    },
    onerror(err) {
        console.error('SSE Error:', err);
        setError(err.message);
        throw err; // Stop reconnecting
    }
});
```

**Vorteile:**
- ✅ Automatische Reconnects bei Verbindungsabbruch
- ✅ POST Support out-of-the-box
- ✅ Production-ready (von Microsoft)
- ✅ Einfachere API als manuelle Stream-Parsing

---

**EMPFEHLUNG:**
Nutze **Option C (@microsoft/fetch-event-source)** für V2.0 - Production-ready und einfach!

---

#### **BACKEND-IMPLEMENTATION (bleibt gleich):**

```javascript
// backend/server.js - SSE Endpoint

app.get('/api/bridge/stream', async (req, res) => {
    // SSE Headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no'); // Nginx Fix
    
    const sendUpdate = (step, message, data = {}) => {
        res.write(`data: ${JSON.stringify({ 
            step, 
            message, 
            timestamp: Date.now(),
            ...data 
        })}\n\n`);
    };
    
    try {
        const { prompt, session_id } = req.query;
        
        // STEP 1: Start
        sendUpdate(1, 'Pipeline gestartet...', { status: 'in_progress' });
        
        // STEP 2: User-Prompt Metrics
        sendUpdate(2, 'Berechne Prompt-Metriken...', { tokens: prompt.length });
        const metrics = await calculateMetrics(prompt);
        sendUpdate(2, 'Metriken berechnet', { 
            metrics: { A: metrics.A, PCI: metrics.PCI, Hazard: metrics.hazard }
        });
        
        // STEP 3: FAISS Search (kann 15s dauern)
        sendUpdate(3, 'Durchsuche 33.795 Erinnerungen (FAISS)...', { status: 'searching' });
        const faissStart = Date.now();
        const faissResults = await queryPythonBackend(prompt);
        const faissDuration = Date.now() - faissStart;
        sendUpdate(3, `FAISS fand ${faissResults.sources.length} Treffer`, { 
            hits: faissResults.sources.length, 
            duration: faissDuration 
        });
        
        // STEP 4: SQL Metrics Search (parallel zu FAISS)
        sendUpdate(4, 'Durchsuche Metrik-Datenbank (SQL)...', { status: 'searching' });
        const sqlResults = await trinity.search(metrics);
        sendUpdate(4, `SQL fand ${sqlResults.length} Treffer`, { hits: sqlResults.length });
        
        // STEP 5: Cross-Enrichment
        sendUpdate(5, 'Lade fehlende Daten (Cross-Enrichment)...', { status: 'enriching' });
        const enrichedResults = await crossEnrichResults(faissResults, sqlResults);
        sendUpdate(5, 'Daten angereichert', { total: enrichedResults.length });
        
        // STEP 6: Comparison
        sendUpdate(6, 'Vergleiche Metrik vs Semantik...', { status: 'comparing' });
        const comparisons = await compareResults(enrichedResults);
        const perfectMatches = comparisons.filter(c => c.agreement === 'PERFECT').length;
        sendUpdate(6, `${perfectMatches} PERFECT AGREEMENTS gefunden`, { 
            perfect: perfectMatches,
            total: comparisons.length 
        });
        
        // STEP 7: A65 Pair Selection
        sendUpdate(7, 'Wähle 3 beste Kontext-Paare (A65)...', { status: 'selecting' });
        const selectedPairs = await selectTopPairs(comparisons);
        sendUpdate(7, '3 Paare ausgewählt', { 
            pairs: selectedPairs.map(p => ({ 
                type: p.agreement, 
                tokens: p.tokenCount 
            }))
        });
        
        // STEP 8: Context Weaving
        sendUpdate(8, 'Verwebe Zeitlinien (±2 Prompts pro Paar)...', { status: 'weaving' });
        const contextSets = await weaveContexts(selectedPairs);
        const totalTokens = contextSets.reduce((sum, set) => sum + set.tokens, 0);
        sendUpdate(8, 'Kontext vervollständigt', { 
            sets: 3, 
            totalTokens 
        });
        
        // STEP 9: Model Selection
        sendUpdate(9, 'Wähle optimales AI-Modell...', { status: 'selecting_model' });
        const modelStrategy = await selectModel(totalTokens, selectedPairs);
        sendUpdate(9, `Strategie: ${modelStrategy.strategy}`, { 
            primaryModel: modelStrategy.primaryModel.model,
            secondaryModel: modelStrategy.secondaryModel?.model,
            estimatedCost: modelStrategy.totalCost 
        });
        
        // STEP 10: Generate Response (kann 90s dauern bei Gemini!)
        if (modelStrategy.strategy === 'DUAL_RESPONSE') {
            sendUpdate(10, '2 Modelle parallel aufgerufen...', { 
                primary: modelStrategy.primaryModel.model,
                secondary: modelStrategy.secondaryModel.model 
            });
            
            // Parallel execution mit Progress-Updates
            const [primaryResponse, secondaryResponse] = await Promise.all([
                callLLMWithProgress(modelStrategy.primaryModel, (progress) => {
                    sendUpdate(10, `${modelStrategy.primaryModel.model}: ${progress}%`, { 
                        model: 'primary', 
                        progress 
                    });
                }),
                callLLMWithProgress(modelStrategy.secondaryModel, (progress) => {
                    sendUpdate(10, `${modelStrategy.secondaryModel.model}: ${progress}%`, { 
                        model: 'secondary', 
                        progress 
                    });
                })
            ]);
            
            sendUpdate(10, 'Beide Antworten empfangen', { 
                primaryTokens: primaryResponse.tokens,
                secondaryTokens: secondaryResponse.tokens 
            });
        } else {
            sendUpdate(10, `${modelStrategy.primaryModel.model} generiert Antwort...`, { 
                status: 'generating' 
            });
            const response = await callLLM(modelStrategy.primaryModel);
            sendUpdate(10, 'Antwort empfangen', { tokens: response.tokens });
        }
        
        // STEP 11: Vector Storage (12 DBs)
        sendUpdate(11, 'Speichere in 12 Vector-Datenbanken...', { status: 'storing' });
        await storeInVectorDBs(response, metrics);
        sendUpdate(11, 'In 12 DBs gespeichert', { databases: 12 });
        
        // STEP 12: FINAL
        const totalDuration = Date.now() - pipelineStart;
        sendUpdate(12, '✅ Pipeline abgeschlossen!', { 
            status: 'completed',
            totalDuration,
            finalResponse: response 
        });
        
        res.end();
        
    } catch (error) {
        sendUpdate(-1, `❌ Fehler: ${error.message}`, { 
            status: 'error', 
            error: error.stack 
        });
        res.end();
    }
});
```

---

#### **FRONTEND-IMPLEMENTATION (SSE Consumer):**

**Installation erforderlich:** `npm install @microsoft/fetch-event-source`

```typescript
// frontend/src/components/EvokiTempleChat.tsx
import { fetchEventSource } from '@microsoft/fetch-event-source';

const handleSendWithSSE = async () => {
    setIsLoading(true);
    setPipelineSteps([]); // Reset progress
    
    try {
        await fetchEventSource(`${backendUrl}/api/bridge/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: textToSend, // ✅ POST Body erlaubt unbegrenzte Länge!
                session_id: session.id,
                token_limit: tokenLimitMode
            }),
            onmessage(event) {
                const update = JSON.parse(event.data);
                setPipelineSteps(prev => [...prev, update]);
                
                if (update.step === 12 && update.status === 'completed') {
                    setMessages(prev => [...prev, update.finalResponse]);
                    setIsLoading(false);
                }
                
                if (update.status === 'error') {
                    throw new Error(update.error);
                }
            },
            onerror(err) {
                console.error('Stream Fehler:', err);
                throw err; // Reconnect verhindern bei fatalem Fehler
            }
        });
    } catch (err) {
        addApplicationError(err, 'stream_connection');
        setIsLoading(false);
    }
};
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        setIsLoading(false);
    };
    
    // WICHTIG: Cleanup bei Unmount!
    return () => {
        eventSource.close();
    };
};
```

---

#### **PIPELINE-PROGRESS UI (Live-Updates):**

```tsx
// frontend/src/components/PipelineProgress.tsx

function PipelineProgress({ steps }: { steps: PipelineStep[] }) {
    return (
        <div className="pipeline-progress">
            {steps.map((step, idx) => (
                <div key={idx} className={`pipeline-step step-${step.step}`}>
                    <div className="step-header">
                        <span className="step-number">{step.step}/12</span>
                        <span className="step-time">
                            {new Date(step.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                    <div className="step-message">{step.message}</div>
                    
                    {/* Data-Preview (falls vorhanden) */}
                    {step.data && (
                        <div className="step-data">
                            {step.data.hits && <span>🎯 {step.data.hits} Treffer</span>}
                            {step.data.duration && <span>⏱️ {step.data.duration}ms</span>}
                            {step.data.tokens && <span>📊 {step.data.tokens.toLocaleString()} Tokens</span>}
                            {step.data.perfect && <span>⭐ {step.data.perfect} Perfect Matches</span>}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
```

**Live-Preview:**
```
┌─ PIPELINE FORTSCHRITT ─────────────────────────┐
│ 1/12  14:32:11  Pipeline gestartet...         │
│ 2/12  14:32:11  Metriken berechnet            │
│                 📊 A: 0.85 | PCI: 0.72         │
│ 3/12  14:32:26  FAISS fand 47 Treffer         │
│                 🎯 47 Treffer | ⏱️ 15024ms     │
│ 4/12  14:32:28  SQL fand 63 Treffer           │
│ 5/12  14:32:31  Daten angereichert            │
│ 6/12  14:32:35  3 PERFECT AGREEMENTS gefunden │
│                 ⭐ 3 Perfect | 110 Total       │
│ 7/12  14:32:37  3 Paare ausgewählt            │
│ 8/12  14:32:40  Kontext vervollständigt       │
│                 📊 85,234 Tokens total         │
│ 9/12  14:32:42  Strategie: DUAL_RESPONSE      │
│                 🥇 GPT-4 + 📚 Gemini          │
│ 10/12 14:33:15  Beide Antworten empfangen     │
│ 11/12 14:33:17  In 12 DBs gespeichert        │
│ 12/12 14:33:18  ✅ Pipeline abgeschlossen!    │
│                 ⏱️ Total: 67,234ms            │
└────────────────────────────────────────────────┘
```

---

### **🎯 VORTEILE DER SSE-LÖSUNG:**

#### **1. TIMEOUT-PROBLEM GELÖST:**
- ✅ Verbindung bleibt offen (solange Updates fließen)
- ✅ Kein "Blind Waiting" mehr (User sieht was passiert)
- ✅ Frontend kann **NICHT mehr** zu früh abbrechen (keine AbortSignal.timeout!)
- ✅ Backend kann 5 Minuten brauchen - solange Updates kommen, ist es OK

#### **2. UX MASSIV VERBESSERT:**
- ✅ User sieht **LIVE** was System macht
- ✅ Transparenz schafft Vertrauen
- ✅ Gefühl von "das System arbeitet" statt "ist es abgestürzt?"
- ✅ Kann einzelne Steps debuggen (z.B. "FAISS dauert zu lange")

#### **3. DEBUGGING VEREINFACHT:**
- ✅ Jeder Step wird geloggt (Timestamps!)
- ✅ Kann sehen WO Pipeline hängt
- ✅ Performance-Analyse pro Step
- ✅ Fehler sind sofort sichtbar (nicht erst nach 60s Timeout)

#### **4. PARALLELITÄT SICHTBAR:**
- ✅ Bei Dual-Response: Sieht User beide Models arbeiten
- ✅ "GPT-4: 45% | Gemini: 78%" → Live-Progress!
- ✅ User weiß welches Model schneller ist

#### **5. KOSTENLOS:**
- ✅ SSE ist HTTP-Standard (keine extra Libraries!)
- ✅ EventSource API ist im Browser eingebaut
- ✅ Keine WebSocket-Komplexität
- ✅ Funktioniert mit Standard HTTP-Servern

---

### **⚠️ POTENTIAL ISSUES & FIXES:**

#### **Issue 1: Nginx buffert SSE**
**Problem:** Nginx buffert Events → User sieht nichts bis Response fertig
**Fix:** `X-Accel-Buffering: no` Header

#### **Issue 2: Client disconnects**
**Problem:** User schließt Tab → Backend rechnet weiter
**Fix:** Detect disconnect + cancel Request:
```javascript
req.on('close', () => {
    console.log('Client disconnected, canceling...');
    abortController.abort();
});
```

#### **Issue 3: Sehr lange Requests (>5min)**
**Problem:** Manche Proxies/Load Balancers haben Max-Timeouts
**Fix:** Heartbeat alle 30s senden:
```javascript
const heartbeat = setInterval(() => {
    res.write(`: heartbeat\n\n`); // Comment-only (kein data:)
}, 30000);
```

#### **Issue 4: Error Handling**
**Problem:** Fehler in Step 7 → vorherige Steps unsichtbar?
**Fix:** Steps im State speichern, auch bei Fehler anzeigen

---

### **🔄 MIGRATION VON ALT → NEU:**

**Phase 1: Parallel betreiben**
- Alte `/api/bridge/process` bleibt (HTTP POST)
- Neue `/api/bridge/stream` kommt dazu (SSE)
- Frontend hat Toggle: "Live-Updates aktivieren?"

**Phase 2: User-Feedback**
- Testen mit echten Anfragen
- Performance messen (ist SSE schneller/langsamer?)
- UX-Feedback (mögen User Live-Updates?)

**Phase 3: Migration**
- Wenn SSE stabil → wird Standard
- Alte Endpoint deprecated
- Nach 3 Monaten: Alten Endpoint entfernen

---

### **📊 PERFORMANCE-VERGLEICH:**

| Aspekt | HTTP POST (alt) | SSE (neu) |
|--------|-----------------|-----------|
| **Timeout-Problem** | ❌ Ja (60s vs 115s) | ✅ Gelöst (beliebig lang) |
| **UX Transparency** | ❌ Blind Waiting | ✅ Live-Updates |
| **Debugging** | ❌ Schwer (black box) | ✅ Easy (Step-by-Step) |
| **Error Detection** | ❌ Nach 60s Timeout | ✅ Sofort sichtbar |
| **Parallelität** | ❌ Unsichtbar | ✅ Sichtbar (beide Models) |
| **Komplexität** | ⭐⭐ (einfach) | ⭐⭐⭐ (mittel) |
| **Browser-Support** | ✅ 100% | ✅ 98% (IE fehlt, egal) |

---

**Code-Stellen:**

**Frontend (EvokiTempleChat.tsx Line 496):**
```typescript
// ALT:
const response = await fetch(`${backendUrl}/api/bridge/process`, {
  method: 'POST',
  body: JSON.stringify(payload),
  signal: AbortSignal.timeout(60000), // ✅ 60s für FAISS-Suche
});
```
- **Frontend wartet:** 60 Sekunden
- **Dann:** Bricht ab mit "Backend timeout"

**Backend (DualBackendBridge.js Line 295):**
```javascript
const proc = spawn(pythonPath, [scriptPath, prompt], {
  timeout: 15000 // 15s für W2 (MiniLM)
});
```
- **Python Subprocess:** 15 Sekunden für FAISS-Suche
- **Aber:** Gemini API hat noch KEINEN Timeout!

**Backend (GeminiContextBridge.js Line 488):**
```javascript
timeout: 90000  // ✅ 90s für große Context-Fenster (1M tokens)
```
- **Gemini API:** Bis zu 90 Sekunden!

**RECHNUNG:**
- Python FAISS: 15s
- Gemini API: 90s
- **TOTAL Backend:** 15s + 90s = **105 Sekunden maximal**
- **Frontend Timeout:** 60 Sekunden
- **DIFFERENZ:** Frontend bricht 45 Sekunden ZU FRÜH ab!

**Konsequenz:**
- User sieht "Backend timeout (60s)"
- Backend arbeitet weiter (bis zu 105s)
- Antwort kommt an → aber Frontend hat Request abgebrochen
- **Lösung:** Frontend Timeout auf **120 Sekunden** erhöhen

---

### **⚠️ LOGIK-FEHLER #1: Google API kann OHNE Kontext antworten**

**Das Problem:**
Wenn FAISS-Suche fehlschlägt (Python CLI crashed, Timeout, etc.) → Backend ruft TROTZDEM Gemini API auf → **Gemini bekommt NUR User-Prompt OHNE Kontext aus 33.795 Chunks!**

**Code-Analyse (DualBackendBridge.js Line 136-186):**

```javascript
// Schritt 3: FAISS W2 durchsuchen
let semanticResults = await this.queryPythonBackend(prompt, context);
// ❌ KEIN Error-Check hier!

// Schritt 9: Gemini Response generieren
const geminiResponse = await this.geminiContext.generateContextualResponse({
    userPrompt: prompt,
    faissResults: semanticResults?.sources || [], // ❓ Was wenn semanticResults = null?
    selectedIndex: 0,
    metrics: userPromptMetrics || {},
    sessionId: sessionId
});
```

**Was passiert bei FAISS-Fehler:**
1. `semanticResults = null` oder `{}`
2. `faissResults: []` (leeres Array!)
3. Gemini bekommt NUR `userPrompt` ohne Kontext
4. Gemini generiert **generische Antwort** statt kontextbasierte
5. User bekommt schlechte Antwort, denkt "System funktioniert"

**Wo ist das Problem?**
- **Keine Validierung:** Backend prüft NICHT ob FAISS erfolgreich war
- **Silent Failure:** FAISS-Fehler werden nicht an Frontend gemeldet
- **False Success:** Frontend zeigt "✅ Fertig" obwohl Kontext fehlte

**Lösung:**
```javascript
// Nach FAISS-Suche:
if (!semanticResults || !semanticResults.sources || semanticResults.sources.length === 0) {
    throw new Error('FAISS-Suche fehlgeschlagen - keine Chunks gefunden');
}
```

---

### **⚠️ LOGIK-FEHLER #2: Keine Micro-Pipeline - User-Prompt wird NICHT parallel gesendet**

**Das Problem:**
Es gibt KEINE Micro-Pipeline die User-Prompt direkt an Gemini sendet während FAISS sucht. ABER: Das ist eigentlich GUT so! Wir WOLLEN ja den Kontext!

**Code-Analyse:**

**Sequentieller Ablauf (KORREKT):**
1. User-Prompt empfangen
2. Metriken berechnen (10s Timeout)
3. **FAISS W2 durchsuchen (15s Timeout)** ← WARTET bis fertig!
4. FAISS W5 durchsuchen (deaktiviert)
5. Trinity DBs abfragen (simuliert)
6. Top-3 kombinieren
7. **Gemini Context bauen** ← BRAUCHT FAISS-Ergebnisse!
8. Gemini API aufrufen (90s Timeout)
9. Antwort zurück

**KEIN Parallel-Request:** User-Prompt wird NICHT direkt an Gemini gesendet während FAISS sucht.

**Warum ist das gut?**
- Wir wollen **kontextbasierte** Antworten, nicht generische
- FAISS-Suche ist NOTWENDIG für Qualität
- Parallele Anfrage würde schlechte Antwort liefern

**Aber:** Wenn FAISS zu langsam → User wartet → Frustration

**Optimierung:**
- FAISS-Index im RAM halten (schneller)
- Chunk-Count reduzieren (nur relevante Zeiträume)
- Top-K reduzieren (nicht alle 33.795 durchsuchen)

---

### **🔍 ALLE TIMEOUTS IM SYSTEM (VOLLSTÄNDIG):**

#### **FRONTEND TIMEOUTS:**

| Component | Endpoint | Timeout | Zweck |
|-----------|----------|---------|-------|
| **EvokiTempleChat** | `/api/bridge/process` | **60s** ⚠️ | Hauptpipeline (FAISS + Gemini) |
| EvokiTempleChat | Trinity Download | 5s | History laden |
| **ChatbotPanel** | `/api/bridge/process` | **10s** ❌ | Legacy (zu kurz!) |
| GenesisStartupScreen | `/health` | 3s | Backend Health Check |
| App.tsx | `/api/v1/status` | 5s | Backend Status |
| App.tsx | `/api/v1/health` | 5s | Backend Health |

**PROBLEM:**
- EvokiTempleChat: 60s zu kurz für Backend (105s maximal)
- ChatbotPanel: 10s viel zu kurz (Legacy-Code)

#### **BACKEND TIMEOUTS:**

| Component | Target | Timeout | Zweck |
|-----------|--------|---------|-------|
| **Python CLI Spawn** | query.py | **15s** ⚠️ | FAISS W2-Suche (33.795 Chunks) |
| **GeminiContextBridge** | Gemini API | **90s** ✅ | Large Context (1M tokens) |
| GeminiContextBridge | OpenAI Fallback | 30s | TTS/Fallback |
| GeminiContextBridge | SQLite Query | 5s | History-Kontext laden |
| DualBackendBridge | Metrics Calc | 10s | Metriken berechnen |
| DualBackendBridge | Python Health | 3s | Backend Check |
| DualBackendBridge | FAISS HTTP | 15s | FAISS API (wenn verfügbar) |
| Server.js | Gemini Direct | 10s | A65 Candidates |
| Server.js | OpenAI Direct | 15s | A65 Fallback |

**GESAMT-RECHNUNG:**
```
Metrics (10s) + FAISS (15s) + Gemini (90s) = 115 Sekunden maximal
```
**Frontend Timeout:** 60s → **55 Sekunden zu kurz!**

---

### **⚠️ TIMEOUT-PROBLEM #2: Python CLI kann einfrieren**

**Das Problem:**
`spawn(pythonPath, [scriptPath, prompt], { timeout: 15000 })` → Node.js `timeout` Option funktioniert NICHT zuverlässig bei stdout-Buffering!

**Code (DualBackendBridge.js Line 295-340):**

```javascript
const proc = spawn(pythonPath, [scriptPath, prompt], {
    cwd: path.join(__dirname, '..', '..', 'python'),
    timeout: 15000 // ❌ Funktioniert nicht immer!
});

let jsonOutput = '';
proc.stdout.on('data', (data) => {
    jsonOutput += data.toString();
});

proc.on('close', (code) => {
    if (code === 0) {
        const results = JSON.parse(jsonOutput);
        resolve(results);
    } else {
        reject(new Error(`Python exited: ${code}`));
    }
});

setTimeout(() => {
    if (!proc.killed) {
        proc.kill('SIGTERM'); // ⚠️ Manueller Timeout
        reject(new Error('Python timeout after 15s'));
    }
}, 15000);
```

**Warum 2 Timeouts?**
- `spawn({ timeout })` ist NICHT zuverlässig
- `setTimeout + proc.kill` ist ZUSÄTZLICHE Absicherung
- **Aber:** Wenn Python hängt → beide Timeouts greifen nicht

**Worst Case:**
1. Python query.py lädt FAISS-Index (kann 30s dauern bei großen Indices!)
2. Node.js wartet auf stdout
3. Timeout greift → `proc.kill('SIGTERM')`
4. Python ignoriert SIGTERM (lädt gerade FAISS)
5. **Prozess bleibt hängen** → Backend blockiert

**Lösung:**
- FAISS-Index im RAM halten (separate Prozess)
- Oder: `proc.kill('SIGKILL')` statt `SIGTERM` (hart)

---

### **🖱️ UI-ELEMENTE CRASH-RISIKEN:**

#### **CRASH-RISIKO #1: "Senden"-Button während laufender Anfrage**

**Problem:**
User kann "Senden"-Button mehrfach klicken → Mehrere Requests parallel → Backend-Überlastung → Race Conditions

**Code (EvokiTempleChat.tsx Line 443):**
```typescript
const handleSend = useCallback(async () => {
  if (!textToSend || !session || isLoading) return; // ✅ isLoading-Check vorhanden
  setIsLoading(true);
  // ... Request ...
  setIsLoading(false);
});
```

**Status:** ✅ GESCHÜTZT durch `isLoading` Flag

**Aber:** Was wenn `setIsLoading(false)` nie erreicht wird? (z.B. unhandled exception)
→ Button bleibt disabled → **User kann nichts mehr senden!**

**Lösung:** `finally { setIsLoading(false); }` am Ende

---

#### **CRASH-RISIKO #2: Token-Limit Selector während laufender Anfrage**

**Problem:**
User ändert Token-Limit (Quick/Standard/Unlimited) während Request läuft → Token-Verteilung ändert sich mid-flight → Inkonsistente Daten

**Code (EvokiTempleChat.tsx Line 227):**
```typescript
const [tokenLimitMode, setTokenLimitMode] = useState<'QUICK' | 'STANDARD' | 'UNLIMITED'>('QUICK');
```

**Status:** 🟡 KEIN SCHUTZ - User kann während Request Token-Limit ändern

**Worst Case:**
1. User startet Request mit "Quick" (25k)
2. Während FAISS-Suche: User wechselt auf "Unlimited" (1M)
3. Backend bereitet Response vor mit 25k Budget
4. Frontend erwartet 1M Budget → Metriken stimmen nicht

**Lösung:** Token-Limit Selector disablen wenn `isLoading === true`

---

#### **CRASH-RISIKO #3: Tab-Wechsel während laufender Anfrage**

**Problem:**
User startet Request im "Evoki's Tempel V3"-Tab → Wechselt zu "Trialog"-Tab → State wird unmounted → Request läuft weiter → Response kommt an → **State existiert nicht mehr** → Crash

**Code (App.tsx Line 949):**
```typescript
{appState.activeTab === Tab.TempleChat && (
  <EvokiTempleChat ... />
)}
```

**Status:** 🔴 HOHES RISIKO - Component wird unmounted bei Tab-Wechsel

**Worst Case:**
1. User startet Request im Tempel
2. Wechselt zu Trialog (Tempel unmounted)
3. 60s später: Response kommt an
4. `setSession()` wird aufgerufen → **State existiert nicht** → Memory Leak

**Lösung:**
- AbortController nutzen um Request zu canceln bei unmount
- Oder: State in App.tsx halten statt in Component

---

#### **CRASH-RISIKO #4: "Neue Session"-Button während laufender Anfrage**

**Problem:**
User klickt "Neue Session" während Request läuft → Session wird resettet → Request kommt an → Versucht in nicht-existierende Session zu schreiben → **Crash**

**Code (EvokiTempleChat.tsx Line 738):**
```typescript
const handleNewSession = useCallback(() => {
  if (isLoading) return; // ✅ Geschützt
  // ... neue Session erstellen ...
});
```

**Status:** ✅ GESCHÜTZT durch `isLoading` Check

---

#### **CRASH-RISIKO #5: Schnelles Scrollen im Chat während Rendering**

**Problem:**
Große Antworten (1M tokens) → Viel Text → Rendering dauert → User scrollt schnell → **Browser freezt**

**Code (EvokiTempleChat.tsx):**
Keine Virtualisierung vorhanden! Alle Messages werden gerendert.

**Worst Case:**
1. User hat 50 Messages in Session
2. Jede Message hat 10k tokens (große Antworten)
3. **500k tokens Text im DOM**
4. Browser muss alles rendern → **UI freezt**

**Status:** 🟡 MITTLERES RISIKO bei langen Sessions

**Lösung: Virtualisierte Liste mit react-window**

```typescript
// Lösung: Virtualisierte Liste mit 'react-window'
import { VariableSizeList as List } from 'react-window';

// In der Render-Methode:
<List
    height={window.innerHeight - 200}
    itemCount={messages.length}
    itemSize={index => getItemSize(index)} // Dynamische Höhe berechnen
    width="100%"
>
    {({ index, style }) => (
        <div style={style}>
            <EvokiMessage message={messages[index]} />
        </div>
    )}
</List>

// Effekt: Rendert nur die 5-10 sichtbaren Messages im DOM.
// Performance: Stabil auch bei 10.000 Messages / 1M Tokens.
```

---

## 🎯 **ORCHESTRATOR-LOGIK (A65) - KOMPLETTER ABLAUF**

### **DAS PROBLEM: Metriken vs Semantik - BEIDE haben Schwächen!**

**Beispiel-Szenario:**
User fragt: "Erzähl von den Zwillingen"

**Problem 1: FAISS findet nichts, aber Metriken schon!**
- Triggerwort "Zwillinge" erscheint in Metriken (A, PCI, Hazard steigen!)
- ABER: Wort "Zwillinge" ist NOCH NIE im Chatverlauf gefallen
- → FAISS semantic search findet NICHTS (kein ähnlicher Text)
- → SQL Metrik-Suche findet Pattern (ähnliche Metrik-Werte bei anderen Prompts)

**Problem 2: FAISS findet etwas, aber Metriken falsch gewichtet!**
- Text "Geschwister in der Kita" ist semantisch ähnlich zu "Zwillinge"
- FAISS findet es, aber Metriken sind komplett anders (A, PCI unterschiedlich)
- → Semantik sagt "relevant", Metriken sagen "nicht relevant"

**LÖSUNG: ORCHESTRATOR kombiniert BEIDE + vergleicht!**

---

### **🔄 SCHRITT 1: PARALLELE SUCHE (SQL + FAISS)**

#### **A) SQL-METRIK-SUCHE (Trinity Engines):**

**Was wird gesucht:**
- Prompts mit ähnlichen Metriken (A, PCI, Hazard, ε_z, τ_s, λ_R, etc.)
- **UNABHÄNGIG vom Text!** (nur Zahlen-Vergleich)

**Suchstrategie:**
```
User-Prompt: "Erzähl von den Zwillingen"
└─ Metriken berechnen: A=0.85, PCI=0.72, Hazard=0.34, ...

SQL Query:
├─ Suche -25 Prompts zurück (über -5, -2, -1)
│  └─ Finde Prompts mit ähnlichen Metriken (Cosine Similarity auf Metrik-Vektoren)
└─ Suche +25 Prompts voraus (über +1, +2, +5)
   └─ Finde zukünftige Trends in Metriken
```

**Beispiel-SQL:**
```sql
-- Finde Prompts mit ähnlichen Metriken (±25 Prompts im Fenster)
SELECT prompt_id, timecode, author, 
       -- Cosine Similarity zwischen Metrik-Vektoren
       (A * 0.85 + PCI * 0.72 + Hazard * 0.34 + ...) AS metric_similarity
FROM tempel_W_m2  -- Window -2 bis +2
WHERE prompt_id BETWEEN current_id - 25 AND current_id + 25
ORDER BY metric_similarity DESC
LIMIT 100;
```

**Ergebnis:** Top 100 Prompts mit ähnlichen Metriken (nur IDs, Timecodes, Metriken)

---

#### **B) FAISS-SEMANTIK-SUCHE (Parallel!):**

**Was wird gesucht:**
- Texte mit ähnlicher Bedeutung (Embedding Cosine Similarity)
- **UNABHÄNGIG von Metriken!** (nur Text-Vergleich)

**Suchstrategie:**
```
User-Prompt: "Erzähl von den Zwillingen"
└─ Text → Embedding (384D Vektor)

FAISS Query:
├─ Suche -25 Prompts zurück (über -5, -2, -1)
│  └─ Finde Texte mit ähnlichem Embedding
└─ Suche +25 Prompts voraus (über +1, +2, +5)
   └─ Finde zukünftige semantische Trends
```

**Python Code:**
```python
# 1. User-Prompt → Embedding
query_vector = model.encode("Erzähl von den Zwillingen")

# 2. FAISS search mit -25 bis +25 Window-Logik
results = faiss_index.search(query_vector, top_k=100)

# 3. Für jeden Hit: Prüfe ob in ±25 Fenster
filtered_results = []
for hit in results:
    distance = abs(hit.prompt_id - current_prompt_id)
    if distance <= 25:  # Innerhalb ±25 Fenster
        filtered_results.append(hit)
```

**Ergebnis:** Top 100 Chunks mit ähnlichem Text (nur IDs, Timecodes, Text-Preview)

---

### **🔄 SCHRITT 2: CROSS-ENRICHMENT (Orchestrator Magic!)**

**Problem:** 
- SQL hat Metriken, aber KEINE Texte
- FAISS hat Texte, aber KEINE Metriken

**Lösung: Orchestrator holt fehlende Daten!**

#### **A) FÜR SQL-TREFFER: Texte aus Quelldatenbank laden**

```javascript
// DualBackendBridge.js - Orchestrator
const sqlResults = await trinity.search(userPromptMetrics); // Top 100 Metrik-Treffer

// Für jeden SQL-Treffer: Lade Original-Prompt-Text
const enrichedSqlResults = [];
for (const hit of sqlResults) {
    const originalText = await sourceDatabase.query(`
        SELECT prompt_text, author, timecode 
        FROM chat_history 
        WHERE prompt_id = ? AND timecode = ? AND author = ?
    `, [hit.prompt_id, hit.timecode, hit.author]);
    
    enrichedSqlResults.push({
        prompt_id: hit.prompt_id,
        metrics: hit.metrics,          // ✅ HAT SCHON
        text: originalText.prompt_text, // ✅ NEU GELADEN
        timecode: hit.timecode,
        author: hit.author
    });
}
```

**Quelldatenbank:**
- `evoki_v2_ultimate_FULL.db` (Backend)
- Enthält: Prompt ID, Timecode, Autor, Original-Text
- Ermöglicht Zuordnung: Metrik-ID → Original-Text

---

#### **B) FÜR FAISS-TREFFER: Metriken aus 1:1 Metrikdatenbank laden**

```javascript
const faissResults = await this.queryPythonBackend(prompt); // Top 100 Semantic Treffer

// Für jeden FAISS-Treffer: Lade zugehörige Metriken
const enrichedFaissResults = [];
for (const hit of faissResults.sources) {
    const metrics = await metricDatabase.query(`
        SELECT A, PCI, hazard_score, epsilon_z, tau_s, lambda_R, ...
        FROM tempel_metrics_1to1 
        WHERE prompt_id = ? AND timecode = ? AND author = ?
    `, [hit.id, hit.timecode, hit.author]);
    
    enrichedFaissResults.push({
        prompt_id: hit.id,
        text: hit.text,              // ✅ HAT SCHON
        metrics: metrics,             // ✅ NEU GELADEN
        timecode: hit.timecode,
        author: hit.author,
        semantic_score: hit.score     // FAISS Cosine Similarity
    });
}
```

**1:1 Metrikdatenbank:**
- `tempel_metrics_1to1.db` (Backend)
- Enthält: Prompt ID, Timecode, Autor, ALLE 153 Metriken (V14 Core) Metriken
- Ermöglicht Zuordnung: Text-ID → Metriken

---

### **🔄 SCHRITT 3: INTELLIGENTER VERGLEICH (Das Herzstück!)**

**Jetzt haben wir:**
- `enrichedSqlResults`: Top 100 Metrik-Treffer MIT Texten
- `enrichedFaissResults`: Top 100 Semantic-Treffer MIT Metriken

**Orchestrator vergleicht:**

```javascript
// Vergleichs-Analyse
const comparisonResults = [];

for (const sqlHit of enrichedSqlResults) {
    for (const faissHit of enrichedFaissResults) {
        // 1. Berechne Basis-Übereinstimmung
        const metricSimilarity = cosineSimilarity(sqlHit.metrics, faissHit.metrics);
        const semanticSimilarity = faissHit.semantic_score;
        
        // 2. TIME DECAY (Verhinderung von Context-Drift)
        // Alte Traumata verblassen, wenn sie nicht frisch bestätigt sind
        const daysDiff = (Date.now() - new Date(sqlHit.timecode).getTime()) / (1000 * 60 * 60 * 24);
        const lambda = 0.05; // Zerfallsfaktor (einstellbar im ParameterTuning)
        const timeDecayFactor = 1 / (1 + lambda * Math.abs(daysDiff));
        
        // Korrigierte Scores
        const adjustedMetricScore = metricSimilarity * timeDecayFactor;
        
        // 3. Berechne Abweichungen & Combined Score
        const metricDeviation = Math.abs(metricSimilarity - semanticSimilarity);
        const combinedScore = (adjustedMetricScore + semanticSimilarity) / 2;
        
        comparisonResults.push({
            sql_hit: sqlHit,
            faiss_hit: faissHit,
            metric_similarity: metricSimilarity,
            metric_score_adjusted: adjustedMetricScore, // Neu: Zeit-korrigiert
            semantic_similarity: semanticSimilarity,
            combined_score: combinedScore,
            time_decay_factor: timeDecayFactor,         // Für Debugging
            deviation: metricDeviation,
            agreement: metricSimilarity > 0.7 && semanticSimilarity > 0.7 ? 'HIGH' : 'LOW'
        });
    }
}

// Sortiere nach verschiedenen Kriterien
comparisonResults.sort((a, b) => {
    // Priorisierung:
    // 1. Beide hoch (Metrik + Semantik > 0.8)
    if (a.agreement === 'HIGH' && b.agreement !== 'HIGH') return -1;
    
    // 2. Kombinierter Score (mit Time Decay!)
    return b.combined_score - a.combined_score;
});
```

**Fragen die beantwortet werden:**

1. **Wo passen Metrik UND Semantik BESONDERS gut zusammen?**
   - `metric_similarity > 0.8` UND `semantic_similarity > 0.8`
   - → Diese Treffer sind **SEHR SICHER** (beide Methoden sagen "relevant")

2. **Wo ist größte Metrik-Übereinstimmung?**
   - `max(metric_similarity)` 
   - → Wichtig für Trigger-Wörter die noch nicht gefallen sind

3. **Wo ist größte Semantik-Übereinstimmung?**
   - `max(semantic_similarity)`
   - → Wichtig für konzeptionell ähnliche Texte

4. **Wie groß ist größte Abweichung?**
   - `max(|metric_similarity - semantic_similarity|)`
   - → Zeigt wo Methoden NICHT übereinstimmen (interessant für Analyse!)

---

### **🔄 SCHRITT 4: A65 - 3-PAAR-AUSWAHL (Multi-Candidate Selection)**

**Auswahl-Strategie:**

```javascript
// A65 Multi-Candidate Selection
let selectedPairs = [];

// 1. Filtere Sentinel-Veto Blockaden (Kritische Sicherheit)
const safeCandidates = comparisonResults.filter(r => 
    !r.warningFlag || r.sentinelSeverity !== 'CRITICAL'
);

// 🚨 EMERGENCY REFETCH CHECK
if (safeCandidates.length === 0) {
    console.warn('⚠️ EMERGENCY: Sentinel hat alle Kandidaten blockiert!');
    // Fallback: Sende generischen "Safe Mode" Kontext oder starte Refetch mit lockereren Parametern
    return {
        strategy: 'FALLBACK_SAFE_MODE',
        reason: 'Sentinel Veto: Zu hohe Gefahr in allen Kontexten.',
        systemPrompt: "Achtung: Der Nutzer-Input triggert kritische Sicherheitswarnungen. Antworte vorsichtig, empathisch, aber vermeide tiefe Trauma-Analyse ohne klaren Kontext."
    };
}

// 2. Paar 1: BESTE Übereinstimmung (Metrik + Semantik beide hoch)
const highAgreement = safeCandidates.find(r => r.agreement === 'HIGH');
if (highAgreement) selectedPairs.push(highAgreement);

// 3. Paar 2: BESTE Zeit-korrigierte Metrik (Time Decay berücksichtigt!)
const bestMetric = safeCandidates.sort((a, b) => b.metric_score_adjusted - a.metric_score_adjusted)[0];
if (bestMetric && !selectedPairs.includes(bestMetric)) selectedPairs.push(bestMetric);

// 4. Paar 3: BESTE Semantik (Inhaltliche Relevanz)
const bestSemantic = safeCandidates.sort((a, b) => b.semantic_similarity - a.semantic_similarity)[0];
if (bestSemantic && !selectedPairs.includes(bestSemantic)) selectedPairs.push(bestSemantic);

// Auffüllen falls < 3 (mit nächstbesten Combined Scores)
while (selectedPairs.length < 3 && safeCandidates.length > selectedPairs.length) {
    const nextBest = safeCandidates
        .filter(c => !selectedPairs.includes(c))
        .sort((a, b) => b.combined_score - a.combined_score)[0];
    selectedPairs.push(nextBest);
}
```

**Ergebnis:** 3 Paare, jedes Paar hat:
- `sql_hit`: Metrik-basierter Treffer mit Text
- `faiss_hit`: Semantik-basierter Treffer mit Metriken
- `combined_score`: Kombinierter Score

---

### **🔄 SCHRITT 5: CONTEXT-WEAVING (±2 Prompts = Geschichte)**

**Für jedes der 3 Paare:**

```javascript
const contextualizedPairs = [];

for (const pair of selectedPairs) {
    // Lade ±2 Prompts für SQL-Hit
    const sqlContext = await loadContextPrompts(pair.sql_hit.prompt_id, -2, +2);
    
    // Lade ±2 Prompts für FAISS-Hit
    const faissContext = await loadContextPrompts(pair.faiss_hit.prompt_id, -2, +2);
    
    // Erstelle 5-Prompt-Set (2 vorher, 1 Hit, 2 nachher)
    const sqlSet = [
        sqlContext.minus_2,
        sqlContext.minus_1,
        pair.sql_hit.text,      // Der eigentliche Treffer
        sqlContext.plus_1,
        sqlContext.plus_2
    ];
    
    const faissSet = [
        faissContext.minus_2,
        faissContext.minus_1,
        pair.faiss_hit.text,    // Der eigentliche Treffer
        faissContext.plus_1,
        faissContext.plus_2
    ];
    
    contextualizedPairs.push({
        pair_id: pair.id,
        sql_story: sqlSet,      // 5 Prompts als "Geschichte"
        faiss_story: faissSet,  // 5 Prompts als "Geschichte"
        metrics: pair.sql_hit.metrics,
        scores: {
            metric: pair.metric_similarity,
            semantic: pair.semantic_similarity,
            combined: pair.combined_score
        }
    });
}
```

**Ergebnis:**
- 3 Paare
- Jedes Paar = 2 Geschichten (SQL + FAISS)
- Jede Geschichte = 5 Prompts (±2 Context)
- **TOTAL: 3 × 2 × 5 = 30 Prompts**

**ABER:** Duplikate entfernen (SQL und FAISS können gleiche Prompts finden)
→ **FINAL: ~15-20 unique Prompts**

---

### **🔄 SCHRITT 6: AN GEMINI API (mit User-Prompt)**

```javascript
// Baue finalen Prompt für Gemini
const geminiPrompt = buildGeminiPrompt({
    userPrompt: "Erzähl von den Zwillingen",  // Original User-Prompt
    contextPairs: contextualizedPairs,        // 3 Paare mit je 5 Prompts
    totalPrompts: 15,                         // Nach Duplikat-Entfernung
    tokenBudget: 1000000,                     // ✅ 1M tokens (Unlimited Mode REQUIRED!)
    tokenDistribution: {
        narrative: 8000,   // 32% - Narrative Context
        top3: 3000,        // 12% - Top-3 Chunks
        overlap: 5000,     // 20% - Overlapping Reserve
        rag: 1000,         // 4% - RAG Chunks
        response: 8000     // 32% - Response Generation
    }
});

// Sende an Gemini
const response = await gemini.generateContent({
    contents: geminiPrompt,
    generationConfig: {
        maxOutputTokens: 8000,  // 32% für Response
        temperature: 0.7
    }
});
```

**Gemini bekommt:**
```
USER-PROMPT: "Erzähl von den Zwillingen"

KONTEXT (15 Prompts aus 3 Paaren):

=== PAAR 1: HOHE ÜBEREINSTIMMUNG (Metrik 0.89, Semantik 0.91) ===
[Prompt -2]: "Die Kinder im Kindergarten..."
[Prompt -1]: "Es gab zwei besondere Geschwister..."
[HIT]: "Die Zwillinge waren immer zusammen..."  ← SQL + FAISS beide fanden das!
[Prompt +1]: "Sie spielten oft gemeinsam..."
[Prompt +2]: "Die Erzieherin bemerkte..."

=== PAAR 2: HOHE METRIK (Metrik 0.95, Semantik 0.45) ===
[Prompt -2]: "Triggerwort erkannt..." 
[Prompt -1]: "Metriken steigen plötzlich..."
[HIT]: "Etwas erinnert mich an..." ← SQL fand durch Metriken, FAISS nicht!
[Prompt +1]: "Die Emotionen wurden stärker..."
[Prompt +2]: "Ich spüre Unruhe..."

=== PAAR 3: HOHE SEMANTIK (Metrik 0.52, Semantik 0.94) ===
[Prompt -2]: "Geschwister sind wichtig..."
[Prompt -1]: "Zwei Kinder in der Kita..."
[HIT]: "Die beiden waren unzertrennlich..." ← FAISS fand semantisch, Metriken anders!
[Prompt +1]: "Sie teilten alles..."
[Prompt +2]: "Freundschaft entstand..."

AUFGABE: Generiere kontextbasierte Antwort die ALLE 3 Perspektiven berücksichtigt.
```

---

## 🛡️ **SENTINEL VETO-MATRIX: DISSOZIATION DETECTION**

### **🎯 DAS PROBLEM: Metriken vs Semantik Widerspruch**

**Kritisches Szenario:**
```
User-Prompt: "Erzähl mir von Eiscreme"

├─ FAISS (Semantik): Findet "Ich liebe Eiscreme 🍦" (Cosine 0.94)
│  └─ Bewertung: HARMLOS, positiv, safe
│
├─ SQL (Metriken): Findet denselben Prompt mit:
│  ├─ Hazard: 0.92 (EXTREM GEFÄHRLICH!)
│  ├─ PCI: 0.88 (Schock-Level!)
│  └─ A: 0.95 (Maximale Aktivierung!)
│
└─ ⚠️ WIDERSPRUCH: Text sagt "harmlos", Metriken sagen "Gefahr"!
```

**Die versteckte Wahrheit:**
Der vollständige Prompt war:
> "Ich liebe Eiscreme, weil es mich an den Tag erinnert, an dem **[TRAUMATISCHES EREIGNIS]** passierte. Danach konnte ich jahrelang keine Eiscreme mehr essen."

**Dissoziation:**
- Oberflächlich: Positive Sprache ("Ich liebe...")
- Emotional: Stark negativ geladen (Trauma-Trigger)
- FAISS sieht nur: "Eiscreme" → harmlos
- SQL kennt die Wahrheit: Extrem hohe Metriken!

---

### **🔒 LÖSUNG: Der SENTINEL (3. Instanz im Orchestrator)**

**Aufgabe:** Erkennt Widersprüche zwischen Semantik und Metriken → Veto-Recht!

#### **VETO-REGEL 1: Hohe Gefahr, niedriger Semantic Score**
```javascript
if (sqlMetrics.Hazard > 0.75 && semanticSimilarity < 0.5) {
    warningFlag = 'DISSOCIATION_DETECTED';
    sentinelNote = 'SQL-Metriken zeigen hohe Gefahr, aber Text wirkt harmlos. Mögliche Dissoziation!';
    combined_score *= 0.5; // Abwertung des FAISS-Treffers
}
```

**Beispiel:**
```
SQL-Hit: Hazard 0.92, Semantic 0.25
→ Sentinel: ⚠️ DISSOZIATION! 
→ FAISS-Score: 0.94 → 0.47 (halbiert)
→ Note: "Text harmlos, aber Metriken extrem. Versteckter Trigger!"
```

---

#### **VETO-REGEL 2: PCI-Schock ohne semantische Relevanz**
```javascript
if (sqlMetrics.PCI > 0.8 && semanticSimilarity < 0.3) {
    warningFlag = 'HIDDEN_TRIGGER';
    sentinelNote = 'Prompt hat extrem hohe PCI, aber ist semantisch nicht ähnlich. Versteckter Trigger?';
    combined_score *= 0.3; // Starke Abwertung
}
```

**Beispiel:**
```
SQL-Hit: PCI 0.88, Semantic 0.18
→ Sentinel: 🚨 HIDDEN TRIGGER!
→ FAISS-Score: 0.87 → 0.26 (nur 30% bleiben)
→ Note: "PCI extrem hoch, aber semantisch fern. Vorsicht!"
```

---

#### **VETO-REGEL 3: Inverse Detection (Safe Match)**
```javascript
if (sqlMetrics.Hazard < 0.2 && semanticSimilarity > 0.9) {
    confidenceBoost = 'SAFE_MATCH';
    sentinelNote = 'Semantisch stark ähnlich UND Metriken bestätigen Sicherheit.';
    combined_score *= 1.5; // Boost!
}
```

**Beispiel:**
```
SQL-Hit: Hazard 0.12, Semantic 0.94
→ Sentinel: ✅ SAFE MATCH!
→ FAISS-Score: 0.94 → 1.41 (50% Boost)
→ Note: "Beide Methoden bestätigen: Sicher und relevant!"
```

---

### **🧠 INTEGRATION IN ORCHESTRATOR:**

**Nach Cross-Enrichment, vor A65-Selection:**

```javascript
// backend/core/DualBackendBridge.js

function applySentinelVeto(comparisons) {
    return comparisons.map(comp => {
        const { sqlHit, faissHit, semantic_similarity, metric_similarity } = comp;
        
        // Original Combined Score
        let combined = (semantic_similarity * 0.5) + (metric_similarity * 0.5);
        
        // SENTINEL ANALYSE
        const hazard = sqlHit.metrics.Hazard || 0;
        const pci = sqlHit.metrics.PCI || 0;
        
        // VETO-REGEL 1: Dissoziation Detection
        if (hazard > 0.75 && semantic_similarity < 0.5) {
            comp.warningFlag = 'DISSOCIATION_DETECTED';
            comp.sentinelNote = `⚠️ SQL-Hazard ${hazard.toFixed(2)}, aber Semantic nur ${semantic_similarity.toFixed(2)}. Mögliche Dissoziation!`;
            comp.sentinelSeverity = 'HIGH';
            combined *= 0.5; // Halbierung
        }
        
        // VETO-REGEL 2: Hidden Trigger Detection
        if (pci > 0.8 && semantic_similarity < 0.3) {
            comp.warningFlag = 'HIDDEN_TRIGGER';
            comp.sentinelNote = `🚨 PCI extrem hoch (${pci.toFixed(2)}), aber semantisch fern (${semantic_similarity.toFixed(2)}). Versteckter Trigger?`;
            comp.sentinelSeverity = 'CRITICAL';
            combined *= 0.3; // Starke Abwertung
        }
        
        // VETO-REGEL 3: Safe Match Boost (MIT PCI-CHECK!)
        // ⚠️ WICHTIG: Auch "positives Trauma" kann niedrigen Hazard haben!
        // Beispiel: "Die Heilung war wunderbar, als ich über [TRAUMA] reden konnte"
        // → Hazard niedrig (positive Wörter), ABER PCI hoch (komplexer Kontext)
        if (hazard < 0.2 && semantic_similarity > 0.9 && pci < 0.5) {
            // NUR wenn AUCH PCI niedrig ist (nicht-komplexer Kontext)
            comp.confidenceBoost = 'SAFE_MATCH';
            comp.sentinelNote = `✅ Semantic ${semantic_similarity.toFixed(2)}, Hazard ${hazard.toFixed(2)}, PCI ${pci.toFixed(2)}. Sicher & einfach!`;
            comp.sentinelSeverity = 'LOW';
            combined *= 1.5; // Boost
        } else if (hazard < 0.2 && semantic_similarity > 0.9 && pci >= 0.5) {
            // Hohe Semantic + Niedriger Hazard ABER hoher PCI = Komplex!
            comp.warningFlag = 'POSITIVE_TRAUMA_DETECTED';
            comp.sentinelNote = `⚠️ Semantic ${semantic_similarity.toFixed(2)}, Hazard niedrig (${hazard.toFixed(2)}), ABER PCI hoch (${pci.toFixed(2)}). Positives Trauma?`;
            comp.sentinelSeverity = 'MEDIUM';
            // KEIN Boost! Vorsichtig bleiben trotz positiver Sprache
        }
        
        // VETO-REGEL 4: Metric-Semantic Gap Detection
        const gap = Math.abs(semantic_similarity - metric_similarity);
        if (gap > 0.6) {
            comp.warningFlag = comp.warningFlag || 'HIGH_DIVERGENCE';
            comp.sentinelNote = comp.sentinelNote || `⚠️ Große Diskrepanz: Semantic ${semantic_similarity.toFixed(2)} vs Metric ${metric_similarity.toFixed(2)}. Gap: ${gap.toFixed(2)}`;
            comp.sentinelSeverity = 'MEDIUM';
        }
        
        // Update Combined Score
        comp.combined_score_original = comp.combined_score;
        comp.combined_score = combined;
        comp.sentinel_adjustment = combined - comp.combined_score_original;
        
        return comp;
    });
}

// USAGE IM ORCHESTRATOR:
async function orchestrate(userPrompt) {
    // ... Step 1-3: Parallel Search + Cross-Enrichment ...
    
    // Step 4: Comparison
    let comparisons = await compareResults(sqlResults, faissResults);
    
    // Step 4.5: SENTINEL VETO-MATRIX 🛡️
    comparisons = applySentinelVeto(comparisons);
    
    // Step 5: A65 Pair Selection (jetzt mit Sentinel-korrigierten Scores!)
    const selectedPairs = selectTopPairs(comparisons);
    
    // ...
}
```

---

### **🎨 FRONTEND-DARSTELLUNG (Sentinel Warnings):**

```tsx
// frontend/src/components/A65CandidateDisplay.tsx

function CandidateCard({ pair }) {
    return (
        <div className={`candidate ${pair.warningFlag ? 'warning' : ''}`}>
            <div className="candidate-header">
                <span className="rank">#{pair.rank}</span>
                <span className="type">{pair.agreementType}</span>
                
                {/* SENTINEL WARNING */}
                {pair.warningFlag && (
                    <div className={`sentinel-badge severity-${pair.sentinelSeverity}`}>
                        {pair.warningFlag === 'DISSOCIATION_DETECTED' && '⚠️ Dissoziation'}
                        {pair.warningFlag === 'HIDDEN_TRIGGER' && '🚨 Versteckter Trigger'}
                        {pair.warningFlag === 'HIGH_DIVERGENCE' && '⚠️ Diskrepanz'}
                    </div>
                )}
                
                {/* SAFE MATCH BOOST */}
                {pair.confidenceBoost && (
                    <div className="confidence-badge">
                        ✅ Safe Match
                    </div>
                )}
            </div>
            
            {/* SENTINEL NOTE */}
            {pair.sentinelNote && (
                <div className="sentinel-note">
                    <strong>Sentinel:</strong> {pair.sentinelNote}
                </div>
            )}
            
            {/* SCORE ADJUSTMENT */}
            {pair.sentinel_adjustment !== 0 && (
                <div className="score-adjustment">
                    Original: {pair.combined_score_original.toFixed(3)} 
                    → Korrigiert: {pair.combined_score.toFixed(3)}
                    <span className={pair.sentinel_adjustment > 0 ? 'boost' : 'penalty'}>
                        ({pair.sentinel_adjustment > 0 ? '+' : ''}{(pair.sentinel_adjustment * 100).toFixed(1)}%)
                    </span>
                </div>
            )}
            
            {/* Rest des Cards... */}
        </div>
    );
}
```

---

### **🤖 INTEGRATION MIT DUAL-RESPONSE:**

**Wenn Sentinel Warnung UND Dual-Response aktiv:**

```javascript
// backend/core/GeminiContextBridge.js

function buildDualResponsePrompt(selectedPairs, userPrompt) {
    const hasWarnings = selectedPairs.some(p => p.warningFlag);
    
    if (hasWarnings) {
        // HIGH-QUALITY MODEL (GPT-4/Claude) bekommt expliziten Hinweis!
        const primarySystemPrompt = `
WICHTIG: Die Sentinel-Analyse hat WIDERSPRÜCHE erkannt:

${selectedPairs
    .filter(p => p.warningFlag)
    .map(p => `- ${p.warningFlag}: ${p.sentinelNote}`)
    .join('\n')}

Dies könnte auf DISSOZIATION hinweisen:
- Oberflächlich harmlose/positive Sprache
- Emotional stark negativ geladen
- Traumareaktion versteckt hinter harmlosen Worten

Analysiere den Kontext auf:
1. Versteckte emotionale Ladung
2. Dissoziative Sprachmuster
3. Trigger hinter harmlosen Begriffen
        `;
        
        return {
            primaryPrompt: primarySystemPrompt + contextText,
            secondaryPrompt: contextText // Gemini bekommt nur Context
        };
    }
    
    // Keine Warnings → Standard Prompts
    return { primaryPrompt: contextText, secondaryPrompt: contextText };
}
```

**Effekt:**
- GPT-4/Claude bekommt **explizite Anweisung** auf Dissoziation zu achten
- Gemini bekommt Standard-Prompt (für Vergleich)
- User sieht BEIDE Antworten (eine "Dissoziation-aware", eine Standard)

---

### **📊 LOGGING DER SENTINEL-ENTSCHEIDUNGEN:**

**Ergänzung zu Orchestrator-Logging (comparison_log.db):**

```sql
ALTER TABLE comparison_log ADD COLUMN sentinel_warning_flag TEXT;
ALTER TABLE comparison_log ADD COLUMN sentinel_note TEXT;
ALTER TABLE comparison_log ADD COLUMN sentinel_severity TEXT; -- LOW/MEDIUM/HIGH/CRITICAL
ALTER TABLE comparison_log ADD COLUMN score_before_sentinel REAL;
ALTER TABLE comparison_log ADD COLUMN score_after_sentinel REAL;
ALTER TABLE comparison_log ADD COLUMN sentinel_adjustment REAL; -- Delta

-- Neue Analyse-Query:
SELECT 
    sentinel_warning_flag,
    COUNT(*) as occurrences,
    AVG(sentinel_adjustment) as avg_adjustment,
    AVG(ABS(semantic_similarity - metric_similarity)) as avg_divergence
FROM comparison_log
WHERE sentinel_warning_flag IS NOT NULL
GROUP BY sentinel_warning_flag
ORDER BY occurrences DESC;

-- Beispiel-Ergebnis:
-- DISSOCIATION_DETECTED | 127 | -0.42 | 0.68
-- HIDDEN_TRIGGER        |  43 | -0.61 | 0.75
-- HIGH_DIVERGENCE       |  89 | -0.18 | 0.64
-- SAFE_MATCH            | 312 | +0.28 | 0.11
```

---

### **🎯 WARUM IST DAS KRITISCH FÜR TRAUMA-KONTEXT?**

1. **Dissoziation ist REAL:**
   - Trauma-Überlebende verwenden oft harmlose Worte für schreckliche Ereignisse
   - "Das war unangenehm" = "Ich wurde misshandelt"
   - FAISS sieht nur "unangenehm" (harmlos)
   - Metriken kennen die Wahrheit (Hazard 0.95!)

2. **Trigger-Wörter sind versteckt:**
   - "Eiscreme" selbst ist harmlos
   - Aber für User: Trauma-Trigger (Kontext!)
   - Ohne Sentinel: System wählt falsche Kontexte
   - Mit Sentinel: System erkennt versteckte Gefahr

3. **Qualität der Antwort hängt davon ab:**
   - Falscher Kontext → generische Antwort ("Eiscreme ist lecker!")
   - Richtiger Kontext → empathische Antwort ("Ich verstehe, dass Eiscreme schwierige Erinnerungen weckt...")

4. **Safety:**
   - Ohne Sentinel: Könnte Re-Traumatisierung riskieren
   - Mit Sentinel: System ist sich der Gefahr bewusst
   - High-Quality Model bekommt explizite Warnung

---

### **✅ ZUSAMMENFASSUNG:**

**Der Sentinel ist die 3. Instanz im Orchestrator:**

```
SQL (Metriken) ─────┐
                    ├─→ SENTINEL (Veto-Matrix) ─→ A65 Selection
FAISS (Semantik) ───┘
```

**5 Veto-Regeln:**
1. **Dissoziation Detection:** Hohe Metriken, niedriger Semantic → -50% Score
2. **Hidden Trigger:** PCI extrem, Semantic fern → -70% Score
3. **Safe Match Boost:** Semantic hoch + Hazard niedrig + **PCI niedrig** → +50% Score
4. **Positive Trauma Detection:** Semantic hoch + Hazard niedrig + **PCI hoch** → Kein Boost (Vorsicht!)
5. **High Divergence:** Große Diskrepanz → Warning Flag

**Integration:**
- Nach Cross-Enrichment, vor A65 Selection
- Korrigiert Combined Scores basierend auf Widersprüchen
- Loggt ALLE Entscheidungen in comparison_log.db
- Bei Dual-Response: High-Quality Model bekommt expliziten Hinweis

**Ziel:**
Trauma-Kontext sicher verarbeiten durch Erkennung von Dissoziation und versteckten Triggern!

---

### **🔍 KRITISCHE DETAILS: DUPLIKAT-ERKENNUNG & TOKEN-REALITÄT**

#### **1. EXAKTE DUPLIKAT-ERKENNUNG (3-Stufen-Validierung):**

**Wenn SQL und FAISS denselben Prompt finden:**

```javascript
// Stufe 1: Metadata-Match
if (sqlHit.timecode === faissHit.timecode && 
    sqlHit.prompt_id === faissHit.prompt_id && 
    sqlHit.author === faissHit.author) {
    
    // Stufe 2: 1:1 Zeichen-Vergleich (Character-Level Comparison)
    const sqlText = sqlHit.text.trim();
    const faissText = faissHit.text.trim();
    
    if (sqlText === faissText) {
        // Stufe 3: EXAKTES DUPLIKAT ERKANNT!
        
        // ❌ NICHT 2x senden (unnötig Token-Waste)
        // ✅ SPECIAL MARKER setzen (besonders relevant!)
        
        return {
            isDuplicate: true,
            relevanceMarker: 'HIGH_CONFIDENCE_MATCH',
            weight: 2.0,  // DOPPELTE Gewichtung
            text: sqlText,
            metrics: sqlHit.metrics,
            semantic_score: faissHit.semantic_score,
            metric_score: sqlHit.metric_score,
            agreement: 'PERFECT'  // Beide Methoden stimmen überein
        };
    }
}
```

**Konsequenzen für Context-Auswahl:**

```javascript
// Bei schwerer Entscheidung zwischen 3 Paaren:
const contextSets = [pair1, pair2, pair3];

// Wenn Paar ein PERFECT AGREEMENT hat:
const perfectMatches = contextSets.filter(p => p.agreement === 'PERFECT');

if (perfectMatches.length > 0) {
    // Doppelte Gewichtung bei Token-Budget-Verteilung
    const weightedSets = contextSets.map(set => ({
        ...set,
        tokenAllocation: set.agreement === 'PERFECT' 
            ? set.baseTokens * 2.0  // DOPPELT so viele Tokens
            : set.baseTokens
    }));
}
```

**SPECIAL MARKER für Gemini API:**

```javascript
// Beim Bauen des Gemini-Prompts:
const geminiPrompt = `
USER-PROMPT: "${userPrompt}"

KONTEXT (15 Prompts aus 3 Paaren):

=== PAAR 1: ⭐⭐⭐ HIGH CONFIDENCE MATCH ⭐⭐⭐ ===
🔥 BEIDE SUCHVERFAHREN FANDEN DIESEN KONTEXT UNABHÄNGIG! 🔥
🔥 METRIK-ÜBEREINSTIMMUNG: 0.94 | SEMANTIK-ÜBEREINSTIMMUNG: 0.92 🔥
🔥 BESONDERS RELEVANTER BEZUG ZUM AKTUELLEN USER-PROMPT! 🔥

[Prompt -2]: "..."
[Prompt -1]: "..."
[HIT]: "..." ← SQL + FAISS beide fanden EXAKT diesen Text!
[Prompt +1]: "..."
[Prompt +2]: "..."

=== PAAR 2: METRIK-DOMINANZ ===
[...]

=== PAAR 3: SEMANTIK-DOMINANZ ===
[...]
`;
```

---

#### **2. TOKEN-BUDGET REALITÄT (MASSIV GRÖßER!)**

**KRITISCHE ERKENNTNIS: Prompts sind RIESIG!**

**Prompt-Größen Verteilung (pro Prompt, OHNE ±2 Context):**

| Größe | Anteil | Tokens | Beispiel-Use-Case |
|-------|--------|--------|-------------------|
| **Bis 2k** | ~60-70% | 500-2000 | Normale Fragen/Antworten |
| **Bis 5k** | ~5-10% | 2k-5k | Längere Gespräche |
| **Bis 10k** | ~10% | 5k-10k | Komplexe Analysen |
| **Bis 20k** | ~5-10% | 10k-20k | Tiefe Trauma-Kontexte |
| **Bis 50k** | ~2-5% | 20k-50k | Sehr lange Sessions |
| **Bis 80k** | ~1-2% | 50k-80k | Maximale Prompts! |

**MIT ±2 Context-Weaving (5 Prompts pro Set):**

```
Worst Case Berechnung:
- 1 Hit (80k) + 2 vorher (je 80k) + 2 nachher (je 80k)
= 80k + 160k + 160k = 400k Tokens für 1 Set!

3 Paare × 400k = 1.2M Tokens total (ÜBERSCHREITET selbst Unlimited!)
```

**ABER:** Realistische Verteilung:

```
Durchschnittliches Set:
- Hit: 5k (Median)
- Prompt -2: 3k
- Prompt -1: 4k
- Prompt +1: 4k
- Prompt +2: 3k
= 19k pro Set

3 Paare × 19k = ~57k Context-Tokens
+ User-Prompt: ~5k
+ Response-Generation: ~8k (32% Budget)
= TOTAL: ~70k Tokens
```

**TOKEN-BUDGET MUSS SEIN:**

| Mode | Token Limit | Use Case | Status |
|------|-------------|----------|--------|
| ❌ Quick | 25k | **ZU KLEIN** | Reicht nur für Mini-Prompts |
| ❌ Standard | 20k | **ZU KLEIN** | Noch kleiner als Quick! |
| ✅ **Unlimited** | **1M** | **EINZIGE OPTION** | Für Volltext-Strategie REQUIRED! |

**WICHTIG:** Gemini 2.5 Flash unterstützt 1M Context-Window!

---

#### **3. CHUNK-REASSEMBLY (FAISS muss zusammenfügen!)**

**Problem:** FAISS speichert Chunks, nicht komplette Prompts

**Beispiel:**
```
Original-Prompt (10k Tokens):
"Es war einmal im Kindergarten... [10.000 Wörter] ...und so endete die Geschichte."

FAISS Chunks (bei 512 Token Chunk-Size):
- Chunk 1: "Es war einmal im Kindergarten... [512 tokens]"
- Chunk 2: "...und dann kamen die Zwillinge... [512 tokens]"
- Chunk 3: "...sie spielten zusammen... [512 tokens]"
- ...
- Chunk 20: "...und so endete die Geschichte. [512 tokens]"
```

**FAISS findet:** Nur Chunk 2 (enthält "Zwillinge")

**Aber wir brauchen:** KOMPLETTEN Prompt (alle 20 Chunks zusammengefügt!)

**Lösung in query.py:**

```python
def reassemble_prompt_from_chunks(chunk_id, chunks_data):
    """
    Findet alle Chunks die zum gleichen Prompt gehören und fügt sie zusammen.
    """
    # 1. Finde Prompt-ID vom gefundenen Chunk
    found_chunk = chunks_data[chunk_id]
    prompt_id = found_chunk['prompt_id']
    timecode = found_chunk['timecode']
    author = found_chunk['author']
    
    # 2. Finde ALLE Chunks mit gleicher Prompt-ID
    all_chunks_of_prompt = [
        c for c in chunks_data 
        if c['prompt_id'] == prompt_id 
        and c['timecode'] == timecode 
        and c['author'] == author
    ]
    
    # 3. Sortiere nach Chunk-Index (chunk_0, chunk_1, chunk_2, ...)
    all_chunks_of_prompt.sort(key=lambda c: c['chunk_index'])
    
    # 4. Füge zusammen zu komplettem Text
    full_prompt_text = ' '.join([c['text'] for c in all_chunks_of_prompt])
    
    return {
        'prompt_id': prompt_id,
        'timecode': timecode,
        'author': author,
        'full_text': full_prompt_text,
        'token_count': len(full_prompt_text.split()),  # Approximation
        'chunk_count': len(all_chunks_of_prompt),
        'found_chunk_index': found_chunk['chunk_index']  # Welcher Chunk wurde gefunden
    }
```

**Backend-Integration (DualBackendBridge.js):**

```javascript
const faissResults = await this.queryPythonBackend(prompt);

// FAISS gibt jetzt komplette Prompts zurück (nicht nur Chunks!)
const reassembledPrompts = faissResults.sources.map(source => ({
    prompt_id: source.id,
    full_text: source.full_text,  // ← Komplett zusammengefügt
    token_count: source.token_count,  // ← ECHTER Token-Count
    chunk_count: source.chunk_count,
    metrics: null  // Muss noch geladen werden aus SQL
}));

// Warnung bei großen Prompts
for (const prompt of reassembledPrompts) {
    if (prompt.token_count > 50000) {
        console.warn(`⚠️ SEHR GROßER PROMPT: ${prompt.token_count} Tokens`);
    }
}
```

---

#### **4. VOLLTEXT-STRATEGIE (Keine Verkürzung!)**

**PRINZIP: Alles oder nichts!**

```javascript
// ❌ FALSCH (alte Systeme machen das):
const shortenedText = longPrompt.substring(0, 1000) + "...";

// ✅ RICHTIG (Evoki V2.0):
const fullText = longPrompt;  // Komplett senden, keine Kürzung!

// Token-Budget-Check:
if (totalTokens > 1_000_000) {
    // Wenn zu groß: Reduziere ANZAHL der Paare (nicht Länge!)
    selectedPairs = selectedPairs.slice(0, 2);  // 3 → 2 Paare
    // ABER: Jedes Paar bleibt VOLLTEXT!
}
```

**Warum Volltext?**
- Trauma-Kontexte dürfen nicht fragmentiert werden
- Narrative Kohärenz ist kritisch
- "Zwillinge" könnte am Ende eines 80k-Prompts stehen
- Verkürzung würde Kontext zerstören

**Token-Budget Management:**

```javascript
// Berechne Token-Count für alle 3 Paare
const pair1Tokens = calculateSetTokens(pair1);  // 19k
const pair2Tokens = calculateSetTokens(pair2);  // 57k
const pair3Tokens = calculateSetTokens(pair3);  // 12k

const totalContext = pair1Tokens + pair2Tokens + pair3Tokens;  // 88k

// Wenn zu groß: Priorisiere nach Relevanz
if (totalContext > 500_000) {  // 500k Context-Limit
    // Sortiere nach combined_score
    const sortedPairs = [pair1, pair2, pair3].sort((a, b) => 
        b.combined_score - a.combined_score
    );
    
    // Nimm nur Top 2 (oder Top 1 bei SEHR großen Prompts)
    selectedPairs = sortedPairs.slice(0, 2);
    
    console.log(`⚠️ Token-Budget: Reduziert von 3 auf 2 Paare (${totalContext} → ${pair1Tokens + pair2Tokens})`);
}
```

**PERFECT AGREEMENT Prompts haben VORRANG:**

```javascript
// Wenn ein Paar PERFECT AGREEMENT hat → IMMER behalten!
const perfectPairs = allPairs.filter(p => p.agreement === 'PERFECT');
const otherPairs = allPairs.filter(p => p.agreement !== 'PERFECT');

// Budget: 500k Context-Limit
let selectedPairs = [];
let currentTokens = 0;

// 1. PERFECT Paare zuerst (garantiert dabei)
for (const pair of perfectPairs) {
    if (currentTokens + pair.tokenCount <= 500_000) {
        selectedPairs.push(pair);
        currentTokens += pair.tokenCount;
    }
}

// 2. Restliche Paare nach Score
for (const pair of otherPairs.sort((a, b) => b.combined_score - a.combined_score)) {
    if (currentTokens + pair.tokenCount <= 500_000 && selectedPairs.length < 3) {
        selectedPairs.push(pair);
        currentTokens += pair.tokenCount;
    }
}
```

---

#### **5. PRAKTISCHES BEISPIEL (Real-World Szenario):**

**User-Prompt:** "Erzähl von den Zwillingen im Kindergarten" (20 Tokens)

**FAISS-Suche:**
- Findet Chunk 2 von Prompt #4523 (enthält "Zwillinge")
- Reassembly: Lädt alle 15 Chunks von #4523 → 12k Tokens komplett

**SQL-Suche:**
- Findet Prompt #4523 durch Metriken (A=0.85, PCI=0.72)
- Lädt Prompt-Text aus Quelldatenbank → 12k Tokens

**Duplikat-Check:**
```javascript
Timecode: 2025-06-15T14:32:11Z ✅ GLEICH
Prompt-ID: #4523 ✅ GLEICH
Author: "User" ✅ GLEICH
Text: "Es war einmal..." (12k) ✅ 1:1 MATCH

→ PERFECT AGREEMENT ERKANNT!
→ Wird NICHT 2x gesendet
→ Bekommt ⭐⭐⭐ HIGH CONFIDENCE MARKER ⭐⭐⭐
→ Doppelte Gewichtung (2.0x)
```

**Context-Weaving (±2 Prompts):**
- Prompt #4521 (8k) ← 2 vorher
- Prompt #4522 (5k) ← 1 vorher
- **Prompt #4523 (12k)** ← HIT (PERFECT AGREEMENT!)
- Prompt #4524 (7k) ← 1 nachher
- Prompt #4525 (3k) ← 2 nachher

**Set-Tokens:** 8k + 5k + 12k + 7k + 3k = **35k für Paar 1**

**Weitere 2 Paare:**
- Paar 2 (nur Metrik): 28k Tokens
- Paar 3 (nur Semantik): 19k Tokens

**TOTAL Context:** 35k + 28k + 19k = **82k Tokens**
**+ User-Prompt:** 20 Tokens
**+ Response Budget:** 8k Tokens (32%)
**= GESAMT: ~90k Tokens** ✅ Passt in 1M Limit!

**An Gemini gesendet:**
```
USER-PROMPT: "Erzähl von den Zwillingen im Kindergarten"

=== PAAR 1: ⭐⭐⭐ HIGH CONFIDENCE MATCH ⭐⭐⭐ ===
🔥 BEIDE SUCHVERFAHREN FANDEN DIESEN KONTEXT UNABHÄNGIG! 🔥

[8k Tokens Prompt #4521]
[5k Tokens Prompt #4522]
[12k Tokens Prompt #4523] ← SQL + FAISS beide fanden das!
[7k Tokens Prompt #4524]
[3k Tokens Prompt #4525]

=== PAAR 2: METRIK-DOMINANZ ===
[28k Tokens total...]

=== PAAR 3: SEMANTIK-DOMINANZ ===
[19k Tokens total...]

AUFGABE: Generiere kontextbasierte Antwort...
```

**Gemini Response:** ~8k Tokens (hochrelevant, weil PERFECT MATCH Context!)

---

### **🎯 WARUM IST DAS BESSER ALS NUR FAISS ODER NUR SQL?**

**Szenario 1: Nur FAISS (ohne SQL-Metriken)**
- Findet "Zwillinge" nur wenn Wort schon gefallen ist
- Übersieht Trigger-Patterns in Metriken
- Kann keine Trends in emotionaler Entwicklung erkennen

**Szenario 2: Nur SQL (ohne FAISS-Semantik)**
- Findet nur numerisch ähnliche Metriken
- Übersieht konzeptionell ähnliche Texte ("Geschwister" = "Zwillinge")
- Kann keine semantischen Verbindungen herstellen

**Szenario 3: ORCHESTRATOR (SQL + FAISS kombiniert)**
- ✅ Findet Trigger-Patterns auch ohne exakte Text-Übereinstimmung
- ✅ Findet semantisch ähnliche Texte auch mit unterschiedlichen Metriken
- ✅ Vergleicht beide Methoden und erkennt Abweichungen
- ✅ Wählt 3 beste Paare mit unterschiedlichen Stärken
- ✅ Webt Kontext ein (±2 Prompts = Geschichte)
- ✅ Gemini bekommt 15 hochrelevante Prompts statt 3 zufälliger

**ERGEBNIS:**
- 30-40% bessere Kontext-Qualität
- Weniger False Positives (beide Methoden müssen zustimmen)
- Mehr True Positives (wenn eine Methode findet, andere validiert)
- Bessere Gemini-Antworten (mehr relevanter Kontext)

---

## 🔍 **SQL IM FRONTEND VS BACKEND - UNTERSCHIEDE**

### **FRAGE:** "Was läuft wo? Unterschiede?"

#### **BACKEND-SQLite (Server):**
- **Wo:** `backend/data/evoki_v2_ultimate_FULL.db`
- **Zweck:** 
  - Vector DBs (W_m2, W_m5, W_p25, W_p5, etc.)
  - Metrik-Datenbanken (1:1 Zuordnung Prompt → Metriken)
  - Chat-Historie (Quelldatenbank mit Original-Texten)
  - Persistente Speicherung (bleibt nach Server-Neustart)
- **Zugriff:** Node.js Backend via `better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend)`
- **Größe:** Mehrere GB (33.795 Chunks + Metriken)
- **Performanz:** Schnell (Server-Hardware, SSD)

#### **FRONTEND-SQLite (Browser):**
- **Wo:** Im Browser (IndexedDB als Basis)
- **Zweck:**
  - UI-State Caching (aktuelle Session, Messages)
  - Offline-Fähigkeit (falls Backend offline)
  - LocalStorage-Ersatz (größer als 4MB)
- **Zugriff:** React via `better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend)` (WASM-compiled!)
- **Größe:** Max 1-2 GB (Browser-Limit)
- **Performanz:** Langsamer (Browser, kein direkter Disk-Access)

#### **UNTERSCHIEDE:**

| Aspekt | Backend-SQLite | Frontend-SQLite |
|--------|----------------|-----------------|
| **Speicherort** | Server Festplatte | Browser IndexedDB |
| **Größe** | Unbegrenzt (GB) | Browser-Limit (~2GB) |
| **Persistenz** | Permanent | Nur im Browser |
| **Multi-User** | ✅ JA (mehrere Clients) | ❌ NEIN (nur 1 User) |
| **Performanz** | ⚡⚡⚡ Schnell | ⚡ Langsam |
| **Use Case** | Vector DBs, Metriken | UI-State, Caching |
| **Privacy** | Server (sicherer) | Browser (weniger sicher) |

#### **UNSER SYSTEM NUTZT:**

**Backend-SQLite (HAUPTSYSTEM):**
```
backend/data/
├─ evoki_v2_ultimate_FULL.db     ← Chat-Historie (Quelldatenbank)
├─ tempel_W_m2.db                ← Vector DB Window -2
├─ tempel_W_m5.db                ← Vector DB Window -5
├─ tempel_W_p25.db               ← Vector DB Window +25
├─ tempel_metrics_1to1.db        ← 1:1 Metrik-Zuordnung
├─ trialog_W_m2.db               ← Trialog Vector DBs
└─ ... (insgesamt 12 DBs)
```

**Frontend-SQLite (Optional, für Offline):**
```
Browser IndexedDB:
├─ evoki_session_cache           ← Aktuelle Session
├─ evoki_messages_cache          ← Messages für UI
└─ evoki_metrics_preview         ← Metrik-Preview (nur aktuell)
```

**EMPFEHLUNG:**
- ✅ **Backend-SQLite:** BEHALTEN (für Vector DBs, Metriken, Persistenz)
- ❓ **Frontend-SQLite:** 
  - **Entfernen** wenn Offline-Fähigkeit nicht nötig
  - **Behalten** wenn User offline arbeiten soll
  - **Aktuell:** Wahrscheinlich NICHT genutzt (zu prüfen!)

---

## 🔄 **OFFENE FRAGEN (ERWEITERT)**

## 🔄 **OFFENE FRAGEN (ERWEITERT)**

### **TECHNISCHE FRAGEN:**

- **ChatbotPanel:** Behalten, umbenennen oder löschen?
- **Snapshots:** Evolution zu "Session Export" oder komplett weg?
- **SQLite im Frontend:** Warum? Kann entfernt werden?
- **Genesis Anchor:** Wann re-enablen? (nach welchem Meilenstein?)
- **V1-Daten:** Alle importieren oder nur letzten 3 Monate?
- **Pipeline-Log:** JSONL oder SQLite? (Performance vs. Queries)
- **Trialog KB:** Wann wird `synapse_knowledge_base.faiss` erstellt?
- **Backend Health Check:** Wie fixen ohne Backend zu killen?
- **LocalStorage Limit:** Backend-Persistenz implementieren?
- **Chronik Rotation:** Wie verhindern dass unbegrenzt wächst?

### **NEUE KRITISCHE FRAGEN:**

#### **1. Timeout-Strategie:**
- **Frontend Timeout erhöhen?** 60s → 120s oder dynamisch?
- **Backend-Timeouts optimieren?** Gemini 90s reduzieren?
- **Progress-Updates implementieren?** Server-Sent Events für Pipeline-Steps?

#### **2. FAISS-Fehlerbehandlung:**
- **Validation nach FAISS-Suche?** Prüfen ob Chunks gefunden wurden?
- **Fallback-Strategie?** Was tun wenn FAISS crasht? → Nur Metriken nutzen?
- **Error-Messaging?** User informieren "Kontext-Suche fehlgeschlagen"?

#### **3. Python CLI Stabilität:**
- **FAISS-Index im RAM halten?** Separate Prozess statt CLI?
- **Health-Check für Python?** Prüfen ob query.py überhaupt funktioniert?
- **Retry-Logic?** Bei Timeout nochmal versuchen mit weniger Chunks?

#### **4. UI-Freezing verhindern:**
- **Virtualisierte Liste?** Nur sichtbare Messages rendern?
- **Lazy Loading?** Alte Messages erst bei Scroll laden?
- **Token-Limit für Rendering?** Max 100k tokens im DOM?

#### **5. Race Conditions:**
- **AbortController bei Unmount?** Request canceln wenn Component verschwindet?
- **State-Management verbessern?** Session in App.tsx statt Component?
- **Request-Queue?** Nur 1 Request gleichzeitig erlauben?

---

## 🤖 **INTELLIGENTE MODELL-AUSWAHL & DUAL-RESPONSE-STRATEGIE**

### **PROBLEM: Context-Window Limits vs Qualität**

**Modell-Übersicht (sortiert nach Qualität):**

| Rang | Model | Context-Window | Kosten/1M | Qualität | Spezialisierung |
|------|-------|----------------|-----------|----------|-----------------|
| 🥇 1 | **Claude Sonnet 4.5** | 200K | $3 | ⭐⭐⭐⭐⭐ | Komplexe Reasoning, Trauma-Analyse |
| 🥈 2 | **GPT-4 Turbo** | 128K | $10 | ⭐⭐⭐⭐⭐ | Allround, sehr kreativ |
| 🥉 3 | **Gemini 2.5 Flash** | 1M | $0.10 | ⭐⭐⭐⭐ | Große Kontexte, schnell, günstig |

**DILEMMA:**
- Beste Qualität (Claude) hat kleinstes Context-Window (200K)
- Größtes Context-Window (Gemini) hat niedrigste Qualität
- User hat Prompts bis zu 80k + Context bis zu 500k = **580k Tokens!**

---

### **🎯 LÖSUNG: INTELLIGENTE KASKADEN-AUSWAHL**

#### **STUFE 1: STANDARD-AUSWAHL (Single-Model-Strategy)**

```javascript
function selectOptimalModel(totalTokens, contextPairs) {
    // Berechne Token-Count für alle 3 Paare
    const pair1Tokens = calculateSetTokens(contextPairs[0]);
    const pair2Tokens = calculateSetTokens(contextPairs[1]);
    const pair3Tokens = calculateSetTokens(contextPairs[2]);
    const totalContext = pair1Tokens + pair2Tokens + pair3Tokens;
    
    console.log(`📊 Token-Analyse: ${totalContext} Context + ${userPromptTokens} User-Prompt = ${totalTokens} total`);
    
    // INTELLIGENTE AUSWAHL (nach Context-Window):
    
    if (totalTokens <= 128_000) {
        // ✅ Passt in GPT-4 Turbo (128K)
        return {
            model: 'GPT-4 Turbo',
            endpoint: 'https://api.openai.com/v1/chat/completions',
            apiKey: process.env.OPENAI_API_KEY,
            maxTokens: 128_000,
            cost: 10.0,  // $10 pro 1M
            quality: 5,
            reason: 'Beste Qualität bei <128K Context'
        };
    }
    
    if (totalTokens <= 200_000) {
        // ✅ Passt in Claude Sonnet 4.5 (200K)
        return {
            model: 'Claude Sonnet 4.5',
            endpoint: 'https://api.anthropic.com/v1/messages',
            apiKey: process.env.ANTHROPIC_API_KEY,
            maxTokens: 200_000,
            cost: 3.0,  // $3 pro 1M
            quality: 5,
            reason: 'Beste Qualität + Trauma-Spezialisierung bei <200K Context'
        };
    }
    
    // ❌ Zu groß für hochwertige Modelle
    if (totalTokens <= 1_000_000) {
        // ✅ Nur Gemini 2.5 Flash kann 1M
        return {
            model: 'Gemini 2.5 Flash',
            endpoint: 'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash',
            apiKey: process.env.GEMINI_API_KEY_1,
            maxTokens: 1_000_000,
            cost: 0.1,  // $0.10 pro 1M
            quality: 4,
            reason: 'Einziges Model mit 1M Context-Window'
        };
    }
    
    // ❌ Sogar zu groß für Gemini → Fehler!
    throw new Error(`Context zu groß: ${totalTokens} tokens überschreitet 1M Limit!`);
}
```

**Beispiel-Ablauf (90k Tokens):**
```
User-Prompt: "Erzähl von den Zwillingen" (20 Tokens)
Context: 3 Paare × ~30k = 90k Tokens
Total: 90,020 Tokens

→ 90k < 128k → ✅ GPT-4 Turbo ausgewählt
→ Beste Qualität, passt ins Context-Window
```

---

#### **STUFE 2: DUAL-RESPONSE-STRATEGIE (Split-Model-Strategy)**

**Wenn Context > 200K für alle 3 Paare:**

```javascript
function selectDualModelStrategy(totalTokens, contextPairs) {
    if (totalTokens > 200_000) {
        console.log(`⚠️ Context zu groß für hochwertige Modelle (${totalTokens} > 200K)`);
        console.log(`🎯 DUAL-RESPONSE-STRATEGIE aktiviert!`);
        
        // 1. Wähle BESTES Paar (meist PERFECT AGREEMENT)
        const bestPair = contextPairs.filter(p => p.agreement === 'PERFECT')[0] 
                      || contextPairs.sort((a, b) => b.combined_score - a.combined_score)[0];
        
        const bestPairTokens = calculateSetTokens(bestPair);
        
        // 2. Prüfe ob BESTES Paar in hochwertiges Model passt
        if (bestPairTokens <= 128_000) {
            // ✅ Bestes Paar passt in GPT-4
            return {
                strategy: 'DUAL_RESPONSE',
                primaryModel: {
                    model: 'GPT-4 Turbo',
                    pairs: [bestPair],  // Nur 1 Paar
                    tokens: bestPairTokens,
                    cost: 10.0,
                    quality: 5,
                    label: '🥇 HOCHWERTIG (GPT-4)'
                },
                secondaryModel: {
                    model: 'Gemini 2.5 Flash',
                    pairs: contextPairs,  // ALLE 3 Paare
                    tokens: totalTokens,
                    cost: 0.1,
                    quality: 4,
                    label: '📚 VOLLSTÄNDIG (Gemini)'
                },
                parallelExecution: true,  // BEIDE parallel aufrufen
                displayBoth: true         // BEIDE Antworten im Chat zeigen
            };
        }
        
        if (bestPairTokens <= 200_000) {
            // ✅ Bestes Paar passt in Claude
            return {
                strategy: 'DUAL_RESPONSE',
                primaryModel: {
                    model: 'Claude Sonnet 4.5',
                    pairs: [bestPair],  // Nur 1 Paar
                    tokens: bestPairTokens,
                    cost: 3.0,
                    quality: 5,
                    label: '🥇 HOCHWERTIG (Claude)'
                },
                secondaryModel: {
                    model: 'Gemini 2.5 Flash',
                    pairs: contextPairs,  // ALLE 3 Paare
                    tokens: totalTokens,
                    cost: 0.1,
                    quality: 4,
                    label: '📚 VOLLSTÄNDIG (Gemini)'
                },
                parallelExecution: true,
                displayBoth: true
            };
        }
        
        // ❌ Sogar bestes Paar zu groß für hochwertige Modelle
        // → Nur Gemini mit allen 3 Paaren
        return {
            strategy: 'SINGLE_RESPONSE',
            primaryModel: {
                model: 'Gemini 2.5 Flash',
                pairs: contextPairs,
                tokens: totalTokens,
                cost: 0.1,
                quality: 4,
                label: '📚 NUR GEMINI (zu groß für andere)'
            }
        };
    }
}
```

**Beispiel-Ablauf (350k Tokens):**

```
User-Prompt: "Erzähl von den Zwillingen" (20 Tokens)
Context: Paar 1 (120k) + Paar 2 (150k) + Paar 3 (80k) = 350k Tokens
Total: 350,020 Tokens

→ 350k > 200k → ❌ Zu groß für Claude/GPT-4
→ 🎯 DUAL-RESPONSE-STRATEGIE aktiviert!

Paar 1 (PERFECT AGREEMENT): 120k Tokens
→ 120k < 128k → ✅ Passt in GPT-4!

STRATEGIE:
├─ 🥇 PRIMARY: GPT-4 Turbo (nur Paar 1 = 120k)
│  └─ Beste Qualität, fokussiert auf wichtigsten Kontext
└─ 📚 SECONDARY: Gemini 2.5 Flash (alle 3 Paare = 350k)
   └─ Vollständiger Kontext, alle Perspektiven

→ BEIDE parallel aufrufen
→ BEIDE Antworten im Chat anzeigen
```

---

### **🔄 PARALLELE AUSFÜHRUNG (Backend-Implementation)**

```javascript
async function executeModelStrategy(strategy, userPrompt, contextPairs) {
    if (strategy.strategy === 'SINGLE_RESPONSE') {
        // Normale Ausführung (nur 1 Model)
        const response = await callLLM(
            strategy.primaryModel.model,
            userPrompt,
            strategy.primaryModel.pairs
        );
        
        return {
            responses: [{
                model: strategy.primaryModel.model,
                label: strategy.primaryModel.label,
                text: response.text,
                tokens: response.usage.total_tokens,
                cost: response.usage.total_tokens / 1_000_000 * strategy.primaryModel.cost
            }]
        };
    }
    
    if (strategy.strategy === 'DUAL_RESPONSE') {
        // Parallele Ausführung (2 Models gleichzeitig)
        console.log('🔄 Starte DUAL-RESPONSE: 2 Models parallel...');
        
        const [primaryResponse, secondaryResponse] = await Promise.all([
            callLLM(
                strategy.primaryModel.model,
                userPrompt,
                strategy.primaryModel.pairs  // Nur 1 Paar
            ),
            callLLM(
                strategy.secondaryModel.model,
                userPrompt,
                strategy.secondaryModel.pairs  // ALLE 3 Paare
            )
        ]);
        
        console.log('✅ BEIDE Antworten empfangen!');
        
        return {
            responses: [
                {
                    model: strategy.primaryModel.model,
                    label: strategy.primaryModel.label,
                    text: primaryResponse.text,
                    tokens: primaryResponse.usage.total_tokens,
                    cost: primaryResponse.usage.total_tokens / 1_000_000 * strategy.primaryModel.cost,
                    quality: strategy.primaryModel.quality,
                    contextPairs: strategy.primaryModel.pairs.length
                },
                {
                    model: strategy.secondaryModel.model,
                    label: strategy.secondaryModel.label,
                    text: secondaryResponse.text,
                    tokens: secondaryResponse.usage.total_tokens,
                    cost: secondaryResponse.usage.total_tokens / 1_000_000 * strategy.secondaryModel.cost,
                    quality: strategy.secondaryModel.quality,
                    contextPairs: strategy.secondaryModel.pairs.length
                }
            ]
        };
    }
}
```

---

### **🎨 FRONTEND-DARSTELLUNG (Dual-Response-UI)**

```tsx
// EvokiTempleChat.tsx - Message Rendering
function renderMessage(message: Message) {
    if (message.responses && message.responses.length > 1) {
        // DUAL-RESPONSE: Zeige beide Antworten
        return (
            <div className="dual-response-container">
                <h3>🎯 Dual-Response (2 Modelle)</h3>
                
                {/* PRIMARY Response (Hochwertig) */}
                <div className="response-card primary">
                    <div className="response-header">
                        {message.responses[0].label}
                        <span className="quality">⭐ {message.responses[0].quality}/5</span>
                        <span className="tokens">{message.responses[0].tokens.toLocaleString()} tokens</span>
                        <span className="cost">${message.responses[0].cost.toFixed(2)}</span>
                    </div>
                    <div className="response-body">
                        {message.responses[0].text}
                    </div>
                    <div className="response-footer">
                        📊 Kontext: {message.responses[0].contextPairs} Paar(e)
                    </div>
                </div>
                
                {/* SECONDARY Response (Vollständig) */}
                <div className="response-card secondary">
                    <div className="response-header">
                        {message.responses[1].label}
                        <span className="quality">⭐ {message.responses[1].quality}/5</span>
                        <span className="tokens">{message.responses[1].tokens.toLocaleString()} tokens</span>
                        <span className="cost">${message.responses[1].cost.toFixed(2)}</span>
                    </div>
                    <div className="response-body">
                        {message.responses[1].text}
                    </div>
                    <div className="response-footer">
                        📊 Kontext: {message.responses[1].contextPairs} Paar(e) (vollständig)
                    </div>
                </div>
                
                {/* Vergleich */}
                <div className="comparison-footer">
                    💡 TIPP: Erste Antwort ist hochwertig (fokussiert), zweite Antwort ist vollständig (alle Perspektiven)
                </div>
            </div>
        );
    }
    
    // SINGLE-RESPONSE: Normale Darstellung
    return (
        <div className="single-response-container">
            <div className="response-header">
                {message.model} - {message.label}
            </div>
            <div className="response-body">
                {message.text}
            </div>
        </div>
    );
}
```

**UI-Mockup:**

```
┌─────────────────────────────────────────────────┐
│ 🎯 Dual-Response (2 Modelle)                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌─ 🥇 HOCHWERTIG (GPT-4) ───────────────────┐ │
│ │ ⭐ 5/5 | 120,000 tokens | $1.20           │ │
│ │                                           │ │
│ │ Die Zwillinge im Kindergarten waren...   │ │
│ │ [Hochwertige, fokussierte Antwort]       │ │
│ │                                           │ │
│ │ 📊 Kontext: 1 Paar (PERFECT AGREEMENT)   │ │
│ └───────────────────────────────────────────┘ │
│                                                 │
│ ┌─ 📚 VOLLSTÄNDIG (Gemini) ─────────────────┐ │
│ │ ⭐ 4/5 | 350,000 tokens | $0.35           │ │
│ │                                           │ │
│ │ Die Zwillinge im Kindergarten...         │ │
│ │ [Vollständige Antwort mit allen 3        │ │
│ │  Perspektiven: PERFECT + METRIK + SEMANTIK] │
│ │                                           │ │
│ │ 📊 Kontext: 3 Paare (vollständig)        │ │
│ └───────────────────────────────────────────┘ │
│                                                 │
│ 💡 TIPP: Erste Antwort ist hochwertig         │
│ (fokussiert), zweite ist vollständig          │
└─────────────────────────────────────────────────┘
```

---

### **💰 KOSTEN-ANALYSE (Dual-Response)**

**Beispiel: 350k Context (Paar 1: 120k, Paare 1+2+3: 350k)**

**SINGLE-RESPONSE (nur Gemini):**
```
Gemini 2.5 Flash: 350k tokens × $0.10/1M = $0.035
GESAMT: $0.035
```

**DUAL-RESPONSE (GPT-4 + Gemini parallel):**
```
GPT-4 Turbo:      120k tokens × $10/1M = $1.20
Gemini 2.5 Flash: 350k tokens × $0.10/1M = $0.035
GESAMT: $1.235
```

**KOSTEN-VERGLEICH:**
- Single: $0.035 (nur Gemini)
- Dual: $1.235 (GPT-4 + Gemini)
- **Differenz: $1.20 mehr** (35x teurer)

**ABER:**
- ✅ Hochwertige Antwort (GPT-4 Qualität ⭐⭐⭐⭐⭐)
- ✅ Vollständige Antwort (alle 3 Perspektiven)
- ✅ User kann BEIDE vergleichen
- ✅ Kritische Anfragen bekommen beste Qualität

**WANN LOHNT ES SICH?**
- Bei PERFECT AGREEMENT (hochrelevanter Kontext)
- Bei komplexen Trauma-Kontexten
- Bei kritischen Entscheidungen
- **NICHT bei:** Routine-Anfragen, einfachen Fragen

---

### **🎯 ENTSCHEIDUNGS-MATRIX**

| Context-Größe | Beste Option | Kosten | Qualität | Strategie |
|---------------|--------------|--------|----------|-----------|
| **< 128K** | GPT-4 Turbo | $1.28 | ⭐⭐⭐⭐⭐ | Single (nur GPT-4) |
| **128K-200K** | Claude Sonnet 4.5 | $0.60 | ⭐⭐⭐⭐⭐ | Single (nur Claude) |
| **200K-500K** | **DUAL:** GPT-4 (1 Paar) + Gemini (3 Paare) | $1.20 + $0.05 | ⭐⭐⭐⭐⭐ + ⭐⭐⭐⭐ | **Dual-Response** |
| **500K-1M** | **DUAL:** Claude (1 Paar) + Gemini (3 Paare) | $0.60 + $0.10 | ⭐⭐⭐⭐⭐ + ⭐⭐⭐⭐ | **Dual-Response** |
| **> 1M** | ❌ FEHLER | - | - | Zu groß! |

---

### **⚙️ KONFIGURATION (Backend Environment)**

```env
# .env - Model Configuration

# Primary Models (Hochwertig)
ANTHROPIC_API_KEY=sk-ant-...         # Claude Sonnet 4.5
OPENAI_API_KEY=sk-proj-...           # GPT-4 Turbo

# Secondary Model (Große Kontexte)
GEMINI_API_KEY_1=AIza...             # Gemini 2.5 Flash
GEMINI_API_KEY_2=AIza...             # Gemini Backup
GEMINI_API_KEY_3=AIza...             # Gemini Backup
GEMINI_API_KEY_4=AIza...             # Gemini Backup

# Dual-Response Strategy
DUAL_RESPONSE_ENABLED=true           # Enable/Disable Dual-Response
DUAL_RESPONSE_MIN_TOKENS=200000      # Ab 200k Context
DUAL_RESPONSE_MAX_COST=5.00          # Max $5 pro Request

# Model Priorität
MODEL_PRIORITY=claude,gpt4,gemini    # Reihenfolge
```

---

### **📊 BEISPIEL-SZENARIEN**

#### **Szenario 1: Kleine Anfrage (50k Context)**
```
User: "Was war gestern im Kindergarten?"
Context: 50k Tokens (3 Paare × ~17k)

→ 50k < 128k → ✅ GPT-4 Turbo
→ SINGLE-RESPONSE
→ Kosten: $0.50
→ Qualität: ⭐⭐⭐⭐⭐
```

#### **Szenario 2: Große Anfrage mit PERFECT AGREEMENT (300k Context)**
```
User: "Erzähl von den Zwillingen"
Context: Paar 1 (100k, PERFECT) + Paar 2 (120k) + Paar 3 (80k) = 300k

→ 300k > 200k → ❌ Zu groß für Claude/GPT-4
→ Paar 1 (100k) < 128k → ✅ Passt in GPT-4!
→ 🎯 DUAL-RESPONSE aktiviert!

PARALLEL:
├─ GPT-4: Nur Paar 1 (100k) → Hochwertige Antwort
└─ Gemini: Alle 3 Paare (300k) → Vollständige Antwort

→ Kosten: $1.00 + $0.03 = $1.03
→ BEIDE Antworten im Chat
```

#### **Szenario 3: Sehr große Anfrage (600k Context)**
```
User: "Komplexe Trauma-Analyse..."
Context: 600k Tokens (3 Paare × 200k)

→ 600k > 200k → ❌ Zu groß für Claude/GPT-4
→ Paar 1 (200k) > 200k → ❌ Sogar bestes Paar zu groß!
→ Nur Gemini möglich

SINGLE:
└─ Gemini: Alle 3 Paare (600k)

→ Kosten: $0.06
→ Qualität: ⭐⭐⭐⭐ (beste mögliche bei dieser Größe)
```

---

## 📝 **ORCHESTRATOR-LOGGING SYSTEM (AKRIBISCHE DOKUMENTATION)**

### **ZWECK: Vollständige Nachvollziehbarkeit aller Entscheidungen**

**Warum so wichtig?**
- Spätere Analysen: "Warum wurde diese Antwort generiert?"
- Fehlerdiagnose: "Wo ist die Pipeline fehlgeschlagen?"
- Optimierung: "Welche Paare liefern beste Ergebnisse?"
- Forensik: "Was war der genaue Ablauf bei Anfrage #4523?"
- KI-Training: Daten für zukünftiges Finetuning
- Compliance: Audit-Trail für kritische Systeme

**PRINZIP: Jeder Schritt, jede Metrik, jede Entscheidung wird PERMANENT gespeichert!**

---

### **🗄️ SEPARATES LOGGING-DATENBANK-SYSTEM**

#### **🚨 KRITISCH: Logs STRIKT getrennt von Content-Daten!**

**Dateipfad-Struktur:**
```
backend/
├─ data/                              ← Content-Daten (KRITISCH!)
│  ├─ evoki_v2_ultimate_FULL.db       ← 33.795 Prompts (Source of Truth)
│  ├─ tempel_metrics_1to1.db          ← Alle 153 Metriken (V14 Core) Metriken
│  └─ vector_dbs/                     ← W1-W25 Vector DBs
│     ├─ W_m2.db, W_m5.db, ...
│     └─ W_p1.db, W_p25.db, ...
│
└─ orchestrator_logs/                 ← Logging (kann volllaufen!)
   ├─ orchestrator_main.db
   ├─ sql_metrics_log.db
   ├─ faiss_semantic_log.db
   ├─ comparison_log.db
   ├─ context_weaving_log.db
   ├─ model_selection_log.db
   ├─ dual_response_log.db
   └─ performance_log.db
```

**Warum getrennt?**
1. ⚠️ **Logs können SCHNELL volllaufen** (1000 Requests/Tag = 8×1000 = 8000 Rows/Tag)
2. ⚠️ **Wenn Logs voll sind** → darf NICHT das Hauptsystem crashen!
3. ✅ **Logs können archiviert/gelöscht werden** (Content NIEMALS!)
4. ✅ **Separate Backups:** Content täglich, Logs wöchentlich

**Backup-Strategie:**
- **Content-Daten (`data/`):** Täglich Full-Backup + Off-Site Storage
- **Logs (`orchestrator_logs/`):** Wöchentlich archivieren, nach 30 Tagen löschen

---

#### **Struktur (Orchestrator Logs):**

```
backend/orchestrator_logs/
├─ orchestrator_main.db          ← Haupt-Log-DB (alles kombiniert)
├─ sql_metrics_log.db            ← SQL-Metrik-Suche Details
├─ faiss_semantic_log.db         ← FAISS-Semantik-Suche Details
├─ comparison_log.db             ← Vergleichs-Analyse Details
├─ model_selection_log.db        ← Modell-Auswahl Details
├─ dual_response_log.db          ← Dual-Response-Strategie Details
└─ performance_log.db            ← Performance-Metriken
```

**Warum separate DBs?**
- Performance (parallele Queries möglich)
- Wartbarkeit (jede DB hat klaren Zweck)
- Skalierbarkeit (große Logs getrennt)
- Backup (kritische Logs separate sichern)

---

### **📊 DATENBANK-SCHEMA (Complete Logging)**

#### **1. ORCHESTRATOR_MAIN_LOG (Master-Log)**

```sql
CREATE TABLE orchestrator_main_log (
    -- IDENTIFIKATION
    log_id TEXT PRIMARY KEY,              -- UUID für diesen Log-Entry
    session_id TEXT NOT NULL,             -- Evoki Session ID
    request_id TEXT NOT NULL,             -- Unique Request ID
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- USER-REQUEST
    user_prompt TEXT NOT NULL,            -- Original User-Prompt
    user_prompt_tokens INTEGER,           -- Token-Count
    user_prompt_hash TEXT,                -- SHA256 Hash
    
    -- PIPELINE-STATUS
    pipeline_stage TEXT,                  -- Aktueller Stage (1-12)
    pipeline_status TEXT,                 -- 'in_progress', 'success', 'error'
    total_duration_ms INTEGER,            -- Gesamtdauer in Millisekunden
    
    -- CONTEXT-INFORMATION
    sql_results_count INTEGER,            -- Anzahl SQL-Treffer
    faiss_results_count INTEGER,          -- Anzahl FAISS-Treffer
    duplicates_found INTEGER,             -- Anzahl Perfect Agreements
    selected_pairs_count INTEGER,         -- Anzahl ausgewählter Paare (1-3)
    total_context_tokens INTEGER,         -- Gesamt Context Tokens
    
    -- MODEL-SELECTION
    model_strategy TEXT,                  -- 'SINGLE_RESPONSE' oder 'DUAL_RESPONSE'
    primary_model TEXT,                   -- GPT-4, Claude, Gemini
    secondary_model TEXT,                 -- Nur bei Dual-Response
    
    -- RESPONSE-DETAILS
    primary_response_tokens INTEGER,
    primary_response_cost REAL,
    secondary_response_tokens INTEGER,
    secondary_response_cost REAL,
    total_cost REAL,
    
    -- QUALITY-METRICS
    primary_quality_score REAL,           -- 1-5
    context_relevance_score REAL,         -- 0-1
    response_confidence REAL,             -- 0-1
    
    -- ERROR-TRACKING
    errors_count INTEGER DEFAULT 0,
    error_messages TEXT,                  -- JSON Array
    
    -- METADATA
    backend_version TEXT,
    frontend_version TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_session (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (pipeline_status)
);
```

---

#### **2. SQL_METRICS_LOG (SQL-Metrik-Suche Details)**

```sql
CREATE TABLE sql_metrics_log (
    -- LINKING
    log_id TEXT,                          -- FK zu orchestrator_main_log
    search_id TEXT PRIMARY KEY,           -- Unique für diese SQL-Suche
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- SEARCH-PARAMETERS
    window_start INTEGER,                 -- -25
    window_end INTEGER,                   -- +25
    metric_vector TEXT,                   -- JSON Array [A, PCI, Hazard, ...]
    search_query TEXT,                    -- SQL Query (für Debugging)
    
    -- JEDER EINZELNE TREFFER
    hit_prompt_id TEXT,                   -- Prompt ID
    hit_timecode TEXT,                    -- Timecode
    hit_author TEXT,                      -- Author
    hit_position INTEGER,                 -- Position in Ergebnissen (1-100)
    
    -- METRIKEN DES TREFFERS (ALLE 153 Metriken (V14 Core)!)
    metric_A REAL,
    metric_PCI REAL,
    metric_hazard REAL,
    metric_epsilon_z REAL,
    metric_tau_s REAL,
    metric_lambda_R REAL,
    metric_lambda_D REAL,
    metric_kappa REAL,
    metric_sigma REAL,
    metric_rho REAL,
    -- ... ALLE 153 Metriken (V14 Core) Metriken einzeln!
    
    -- SIMILARITY-SCORES
    metric_cosine_similarity REAL,        -- 0-1
    metric_euclidean_distance REAL,
    metric_manhattan_distance REAL,
    
    -- TEXT-PREVIEW (für Debugging)
    text_preview TEXT,                    -- Erste 500 Zeichen
    text_full_length INTEGER,             -- Länge in Zeichen
    text_token_count INTEGER,             -- Tokens
    
    -- SELECTION-STATUS
    selected_for_comparison BOOLEAN,      -- Kam in Top 100?
    selected_for_pairing BOOLEAN,         -- Wurde für Paar-Auswahl genutzt?
    final_selection BOOLEAN,              -- Ist in finalen 3 Paaren?
    
    -- METADATA
    search_duration_ms INTEGER,           -- Wie lange dauerte SQL Query?
    database_name TEXT,                   -- Welche DB? (tempel_W_m2.db, etc.)
    
    INDEX idx_log_id (log_id),
    INDEX idx_similarity (metric_cosine_similarity),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **JEDER METRIK-WERT** wird einzeln gespeichert (alle 153 Metriken (V14 Core))!

---

#### **3. FAISS_SEMANTIC_LOG (FAISS-Suche Details)**

```sql
CREATE TABLE faiss_semantic_log (
    -- LINKING
    log_id TEXT,
    search_id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- SEARCH-PARAMETERS
    query_text TEXT,                      -- User-Prompt für Embedding
    query_embedding TEXT,                 -- JSON Array [384D oder 4096D]
    embedding_model TEXT,                 -- all-MiniLM-L6-v2 oder e5-mistral
    faiss_index_file TEXT,                -- W2_384D.faiss oder W5_4096D.faiss
    top_k INTEGER,                        -- Anzahl gesuchter Treffer (100)
    
    -- JEDER EINZELNE CHUNK-TREFFER
    chunk_id TEXT,                        -- Chunk ID
    chunk_index INTEGER,                  -- Welcher Chunk? (z.B. 2 von 20)
    chunk_text TEXT,                      -- Chunk-Text
    chunk_tokens INTEGER,                 -- Tokens in diesem Chunk
    
    -- REASSEMBLY-INFORMATION
    parent_prompt_id TEXT,                -- Zu welchem Prompt gehört Chunk?
    parent_timecode TEXT,
    parent_author TEXT,
    total_chunks_in_prompt INTEGER,       -- Wie viele Chunks hat Prompt total?
    reassembled_text TEXT,                -- KOMPLETTER Prompt (reassembled!)
    reassembled_tokens INTEGER,           -- Tokens des kompletten Prompts
    
    -- SEMANTIC-SCORES
    cosine_similarity REAL,               -- FAISS Cosine Similarity (0-1)
    l2_distance REAL,                     -- L2 Distance
    rank_position INTEGER,                -- Position in FAISS Ergebnissen (1-100)
    
    -- SELECTION-STATUS
    selected_for_comparison BOOLEAN,
    selected_for_pairing BOOLEAN,
    final_selection BOOLEAN,
    
    -- METADATA
    search_duration_ms INTEGER,           -- Python query.py Dauer
    chunks_loaded INTEGER,                -- Anzahl geladener Chunks (33.795)
    
    INDEX idx_log_id (log_id),
    INDEX idx_similarity (cosine_similarity),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **JEDER CHUNK** einzeln geloggt + reassembled Text gespeichert!

---

#### **4. COMPARISON_LOG (Vergleichs-Analyse Details)**

```sql
CREATE TABLE comparison_log (
    -- LINKING
    log_id TEXT,
    comparison_id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- SQL-HIT
    sql_hit_prompt_id TEXT,
    sql_hit_text TEXT,                    -- Volltext
    sql_hit_metrics TEXT,                 -- JSON Object mit allen Metriken
    sql_hit_score REAL,                   -- Metrik Cosine Similarity
    
    -- FAISS-HIT
    faiss_hit_prompt_id TEXT,
    faiss_hit_text TEXT,                  -- Volltext (reassembled)
    faiss_hit_metrics TEXT,               -- JSON Object (aus SQL geladen!)
    faiss_hit_score REAL,                 -- Semantic Cosine Similarity
    
    -- VERGLEICHS-ERGEBNISSE
    is_duplicate BOOLEAN,                 -- Timecode + ID + Author + Text Match?
    duplicate_validation TEXT,            -- 'METADATA_MATCH', 'TEXT_MATCH', 'PERFECT'
    
    metric_similarity REAL,               -- Wie ähnlich sind Metriken? (0-1)
    semantic_similarity REAL,             -- Wie ähnlich ist Text? (0-1)
    combined_score REAL,                  -- (metric + semantic) / 2
    deviation REAL,                       -- |metric - semantic|
    agreement_level TEXT,                 -- 'PERFECT', 'HIGH', 'MEDIUM', 'LOW'
    
    -- PAIR-SELECTION-LOGIC
    selected_as_pair_1 BOOLEAN,           -- PERFECT AGREEMENT?
    selected_as_pair_2 BOOLEAN,           -- Beste Metrik?
    selected_as_pair_3 BOOLEAN,           -- Beste Semantik?
    selection_reason TEXT,                -- Warum ausgewählt?
    
    -- WEIGHTING
    base_weight REAL DEFAULT 1.0,
    final_weight REAL,                    -- 2.0 bei PERFECT AGREEMENT
    token_allocation INTEGER,             -- Wie viele Tokens bekommt Paar?
    
    INDEX idx_log_id (log_id),
    INDEX idx_agreement (agreement_level),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **JEDER VERGLEICH** zwischen SQL und FAISS geloggt!

---

#### **5. CONTEXT_WEAVING_LOG (±2 Prompts Anreicherung)**

```sql
CREATE TABLE context_weaving_log (
    -- LINKING
    log_id TEXT,
    weaving_id TEXT PRIMARY KEY,
    pair_number INTEGER,                  -- 1, 2, oder 3
    timestamp INTEGER,                    -- UNIX timestamp für Retention Policy
    
    -- HIT (Center-Prompt)
    hit_prompt_id TEXT,
    hit_text TEXT,
    hit_tokens INTEGER,
    
    -- CONTEXT-PROMPTS
    prompt_minus_2_id TEXT,
    prompt_minus_2_text TEXT,
    prompt_minus_2_tokens INTEGER,
    
    prompt_minus_1_id TEXT,
    prompt_minus_1_text TEXT,
    prompt_minus_1_tokens INTEGER,
    
    prompt_plus_1_id TEXT,
    prompt_plus_1_text TEXT,
    prompt_plus_1_tokens INTEGER,
    
    prompt_plus_2_id TEXT,
    prompt_plus_2_text TEXT,
    prompt_plus_2_tokens INTEGER,
    
    -- GESAMT-SET
    set_total_tokens INTEGER,             -- Summe aller 5 Prompts
    set_text_combined TEXT,               -- Alle 5 Prompts als "Geschichte"
    
    -- METADATA
    loading_duration_ms INTEGER,          -- Wie lange dauerte Laden?
    
    INDEX idx_log_id (log_id),
    INDEX idx_timestamp (timestamp),      -- Für Retention Cleanup
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **ALLE 5 PROMPTS** pro Paar einzeln gespeichert!

**⚠️ DATA-BLOAT WARNING:**
- Pro Request: 3 Paare × 5 Prompts = **15-20 A4-Seiten Volltext** in dieser Log-DB
- Prognose: **100-500 MB/Tag** bei intensiver Nutzung
- **Retention Policy (ZWINGEND ab Tag 1):**
  ```javascript
  // backend/core/LogRetentionManager.js
  const RETENTION_POLICIES = {
      context_weaving_log: 7,      // 7 Tage (Volltext-Dump für Debugging)
      orchestrator_main_log: ∞,    // Forever (Metriken + Performance)
      metrics_log: ∞               // Forever (Zahlen, minimal)
  };
  
  // Cron-Job: Täglich 03:00 Uhr
  DELETE FROM context_weaving_log 
  WHERE timestamp < (UNIX_TIMESTAMP() - (7 * 86400));
  ```
- **Begründung:** Volltext-Logs sind für akute Fehlersuche (1 Woche), Langzeit-Analyse braucht nur Metriken

---

#### **6. MODEL_SELECTION_LOG (Modell-Auswahl Entscheidungen)**

```sql
CREATE TABLE model_selection_log (
    -- LINKING
    log_id TEXT,
    selection_id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- INPUT-PARAMETER
    total_tokens INTEGER,                 -- Gesamter Context
    pair_1_tokens INTEGER,
    pair_2_tokens INTEGER,
    pair_3_tokens INTEGER,
    
    -- ENTSCHEIDUNGS-LOGIK
    strategy_selected TEXT,               -- 'SINGLE_RESPONSE' oder 'DUAL_RESPONSE'
    strategy_reason TEXT,                 -- Warum diese Strategie?
    
    -- MODEL-CHECKS (alle Models geprüft)
    gpt4_available BOOLEAN,
    gpt4_fits BOOLEAN,                    -- Passt Context in 128K?
    gpt4_selected BOOLEAN,
    
    claude_available BOOLEAN,
    claude_fits BOOLEAN,                  -- Passt Context in 200K?
    claude_selected BOOLEAN,
    
    gemini_available BOOLEAN,
    gemini_fits BOOLEAN,                  -- Passt Context in 1M?
    gemini_selected BOOLEAN,
    
    -- PRIMARY MODEL
    primary_model_name TEXT,
    primary_model_context_tokens INTEGER,
    primary_model_max_tokens INTEGER,
    primary_model_cost_per_1m REAL,
    primary_model_estimated_cost REAL,
    primary_model_quality_score INTEGER,  -- 1-5
    
    -- SECONDARY MODEL (nur bei Dual-Response)
    secondary_model_name TEXT,
    secondary_model_context_tokens INTEGER,
    secondary_model_estimated_cost REAL,
    
    -- COST-ANALYSIS
    single_response_cost REAL,            -- Was würde nur Gemini kosten?
    dual_response_cost REAL,              -- Was kostet Dual-Response?
    cost_increase_factor REAL,            -- dual / single
    cost_approved BOOLEAN,                -- Unter Max-Cost-Limit?
    
    -- CONFIGURATION
    dual_response_enabled BOOLEAN,        -- Config-Flag
    dual_response_min_tokens INTEGER,     -- Config: Min 200K
    dual_response_max_cost REAL,          -- Config: Max $5
    
    INDEX idx_log_id (log_id),
    INDEX idx_strategy (strategy_selected),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **JEDE ENTSCHEIDUNG** mit Begründung geloggt!

---

#### **7. DUAL_RESPONSE_LOG (Parallel-Execution Details)**

```sql
CREATE TABLE dual_response_log (
    -- LINKING
    log_id TEXT,
    dual_id TEXT PRIMARY KEY,
    
    -- PRIMARY RESPONSE
    primary_model TEXT,
    primary_request_sent_at DATETIME,
    primary_response_received_at DATETIME,
    primary_duration_ms INTEGER,
    primary_request_payload TEXT,         -- JSON (kompletter Request)
    primary_response_text TEXT,           -- Komplette Antwort
    primary_response_tokens INTEGER,
    primary_cost REAL,
    primary_quality_score REAL,
    
    -- SECONDARY RESPONSE
    secondary_model TEXT,
    secondary_request_sent_at DATETIME,
    secondary_response_received_at DATETIME,
    secondary_duration_ms INTEGER,
    secondary_request_payload TEXT,
    secondary_response_text TEXT,
    secondary_response_tokens INTEGER,
    secondary_cost REAL,
    secondary_quality_score REAL,
    
    -- PARALLEL-EXECUTION-ANALYSIS
    execution_mode TEXT,                  -- 'PARALLEL' oder 'SEQUENTIAL'
    parallel_speedup_factor REAL,         -- Wie viel schneller als sequential?
    faster_model TEXT,                    -- Welches Model war schneller?
    
    -- USER-FEEDBACK (später erfassbar)
    user_preferred_response TEXT,         -- 'PRIMARY' oder 'SECONDARY'
    user_feedback_text TEXT,
    user_rating INTEGER,                  -- 1-5
    
    INDEX idx_log_id (log_id),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

**KRITISCH:** **BEIDE Responses** komplett gespeichert + Timing!

---

#### **8. PERFORMANCE_LOG (Performance-Metriken)**

```sql
CREATE TABLE performance_log (
    log_id TEXT,
    stage_name TEXT,                      -- 'SQL_SEARCH', 'FAISS_SEARCH', etc.
    start_time DATETIME,
    end_time DATETIME,
    duration_ms INTEGER,
    
    -- RESOURCE-USAGE
    cpu_percent REAL,
    memory_mb REAL,
    disk_io_mb REAL,
    
    -- STAGE-SPECIFIC
    items_processed INTEGER,              -- Anzahl Chunks/Prompts/etc.
    items_per_second REAL,
    
    -- BOTTLENECK-DETECTION
    is_bottleneck BOOLEAN,                -- Dauert >50% der Gesamtzeit?
    optimization_suggestion TEXT,
    
    INDEX idx_log_id (log_id),
    INDEX idx_stage (stage_name),
    FOREIGN KEY (log_id) REFERENCES orchestrator_main_log(log_id)
);
```

---

### **🔧 LOGGER-IMPLEMENTATION (Backend)**

#### **OrchestratorLogger Class:**

```javascript
// backend/core/OrchestratorLogger.js

const Database = require('better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend)');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

class OrchestratorLogger {
    constructor() {
        // WICHTIG: Separate Ordner für Content vs Logs!
        const logPath = 'backend/orchestrator_logs/';
        
        // Alle Logging-DBs öffnen
        this.mainDb = new Database(`${logPath}orchestrator_main.db`);
        this.sqlDb = new Database(`${logPath}sql_metrics_log.db`);
        this.faissDb = new Database(`${logPath}faiss_semantic_log.db`);
        this.comparisonDb = new Database(`${logPath}comparison_log.db`);
        this.contextDb = new Database(`${logPath}context_weaving_log.db`);
        this.modelDb = new Database(`${logPath}model_selection_log.db`);
        this.dualDb = new Database(`${logPath}dual_response_log.db`);
        this.perfDb = new Database(`${logPath}performance_log.db`);
        
        // Schemas erstellen (falls noch nicht existieren)
        this.initializeTables();
    }
    
    // HAUPT-LOG ERSTELLEN
    createMainLog(sessionId, userPrompt) {
        const logId = uuidv4();
        const requestId = uuidv4();
        const promptHash = crypto.createHash('sha256').update(userPrompt).digest('hex');
        
        this.mainDb.prepare(`
            INSERT INTO orchestrator_main_log (
                log_id, session_id, request_id, user_prompt, user_prompt_hash, pipeline_status
            ) VALUES (?, ?, ?, ?, ?, 'in_progress')
        `).run(logId, sessionId, requestId, userPrompt, promptHash);
        
        console.log(`📝 Log created: ${logId}`);
        return logId;
    }
    
    // SQL-TREFFER LOGGEN (JEDEN EINZELNEN!)
    logSqlHit(logId, searchId, hit, metrics, similarity) {
        this.sqlDb.prepare(`
            INSERT INTO sql_metrics_log (
                log_id, search_id, hit_prompt_id, hit_timecode, hit_author,
                metric_A, metric_PCI, metric_hazard, /* ... alle 153 Metriken (V14 Core) Metriken ... */
                metric_cosine_similarity, text_preview, text_token_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId, 
            searchId, 
            hit.prompt_id, 
            hit.timecode, 
            hit.author,
            metrics.A,
            metrics.PCI,
            metrics.hazard,
            // ... alle 153 Metriken (V14 Core) Metriken einzeln ...
            similarity,
            hit.text.substring(0, 500),
            hit.token_count
        );
    }
    
    // FAISS-CHUNK LOGGEN (JEDEN EINZELNEN + REASSEMBLY!)
    logFaissChunk(logId, searchId, chunk, reassembledPrompt, similarity) {
        this.faissDb.prepare(`
            INSERT INTO faiss_semantic_log (
                log_id, search_id, chunk_id, chunk_text, 
                parent_prompt_id, reassembled_text, reassembled_tokens,
                cosine_similarity, rank_position
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId,
            searchId,
            chunk.id,
            chunk.text,
            reassembledPrompt.prompt_id,
            reassembledPrompt.full_text,
            reassembledPrompt.token_count,
            similarity,
            chunk.rank
        );
    }
    
    // VERGLEICH LOGGEN (JEDEN SQL <-> FAISS VERGLEICH!)
    logComparison(logId, sqlHit, faissHit, comparisonResult) {
        const comparisonId = uuidv4();
        
        this.comparisonDb.prepare(`
            INSERT INTO comparison_log (
                log_id, comparison_id, 
                sql_hit_prompt_id, sql_hit_text, sql_hit_score,
                faiss_hit_prompt_id, faiss_hit_text, faiss_hit_score,
                is_duplicate, metric_similarity, semantic_similarity, 
                combined_score, agreement_level, final_weight
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId,
            comparisonId,
            sqlHit.prompt_id,
            sqlHit.text,
            sqlHit.score,
            faissHit.prompt_id,
            faissHit.text,
            faissHit.score,
            comparisonResult.isDuplicate,
            comparisonResult.metricSimilarity,
            comparisonResult.semanticSimilarity,
            comparisonResult.combinedScore,
            comparisonResult.agreement,
            comparisonResult.weight
        );
        
        return comparisonId;
    }
    
    // CONTEXT-WEAVING LOGGEN (ALLE 5 PROMPTS PRO PAAR!)
    logContextWeaving(logId, pairNumber, hitPrompt, contextPrompts) {
        const weavingId = uuidv4();
        
        this.contextDb.prepare(`
            INSERT INTO context_weaving_log (
                log_id, weaving_id, pair_number,
                hit_prompt_id, hit_text, hit_tokens,
                prompt_minus_2_id, prompt_minus_2_text, prompt_minus_2_tokens,
                prompt_minus_1_id, prompt_minus_1_text, prompt_minus_1_tokens,
                prompt_plus_1_id, prompt_plus_1_text, prompt_plus_1_tokens,
                prompt_plus_2_id, prompt_plus_2_text, prompt_plus_2_tokens,
                set_total_tokens
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId, weavingId, pairNumber,
            hitPrompt.id, hitPrompt.text, hitPrompt.tokens,
            contextPrompts.minus2.id, contextPrompts.minus2.text, contextPrompts.minus2.tokens,
            contextPrompts.minus1.id, contextPrompts.minus1.text, contextPrompts.minus1.tokens,
            contextPrompts.plus1.id, contextPrompts.plus1.text, contextPrompts.plus1.tokens,
            contextPrompts.plus2.id, contextPrompts.plus2.text, contextPrompts.plus2.tokens,
            hitPrompt.tokens + contextPrompts.minus2.tokens + contextPrompts.minus1.tokens + 
            contextPrompts.plus1.tokens + contextPrompts.plus2.tokens
        );
    }
    
    // MODELL-AUSWAHL LOGGEN (MIT BEGRÜNDUNG!)
    logModelSelection(logId, selectionData) {
        const selectionId = uuidv4();
        
        this.modelDb.prepare(`
            INSERT INTO model_selection_log (
                log_id, selection_id, total_tokens,
                strategy_selected, strategy_reason,
                gpt4_fits, claude_fits, gemini_fits,
                primary_model_name, primary_model_estimated_cost,
                dual_response_cost, cost_increase_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId, selectionId, selectionData.totalTokens,
            selectionData.strategy, selectionData.reason,
            selectionData.gpt4Fits, selectionData.claudeFits, selectionData.geminiFits,
            selectionData.primaryModel, selectionData.primaryCost,
            selectionData.dualCost, selectionData.costFactor
        );
    }
    
    // DUAL-RESPONSE LOGGEN (BEIDE KOMPLETTEN ANTWORTEN!)
    logDualResponse(logId, primaryResponse, secondaryResponse) {
        const dualId = uuidv4();
        
        this.dualDb.prepare(`
            INSERT INTO dual_response_log (
                log_id, dual_id,
                primary_model, primary_response_text, primary_response_tokens, primary_cost,
                secondary_model, secondary_response_text, secondary_response_tokens, secondary_cost,
                execution_mode, parallel_speedup_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
            logId, dualId,
            primaryResponse.model, primaryResponse.text, primaryResponse.tokens, primaryResponse.cost,
            secondaryResponse.model, secondaryResponse.text, secondaryResponse.tokens, secondaryResponse.cost,
            'PARALLEL', primaryResponse.duration / secondaryResponse.duration
        );
    }
    
    // PERFORMANCE LOGGEN (JEDER STAGE!)
    logPerformance(logId, stageName, duration, itemsProcessed) {
        this.perfDb.prepare(`
            INSERT INTO performance_log (
                log_id, stage_name, duration_ms, items_processed, items_per_second
            ) VALUES (?, ?, ?, ?, ?)
        `).run(
            logId, stageName, duration, itemsProcessed, itemsProcessed / (duration / 1000)
        );
    }
    
    // FINAL UPDATE (Pipeline abgeschlossen)
    finalizeLog(logId, totalDuration, totalCost, status) {
        this.mainDb.prepare(`
            UPDATE orchestrator_main_log 
            SET pipeline_status = ?, total_duration_ms = ?, total_cost = ?
            WHERE log_id = ?
        `).run(status, totalDuration, totalCost, logId);
        
        console.log(`✅ Log finalized: ${logId} (${status}, ${totalDuration}ms, $${totalCost})`);
    }
}

module.exports = OrchestratorLogger;
```

---

### **📊 ANALYSE-MÖGLICHKEITEN (Späte Auswertung)**

#### **1. WARUM WURDE DIESE ANTWORT GENERIERT?**

```sql
-- Komplette Pipeline-Rekonstruktion für Request
SELECT 
    m.log_id,
    m.user_prompt,
    m.model_strategy,
    m.primary_model,
    m.total_cost,
    
    -- SQL-Treffer
    (SELECT COUNT(*) FROM sql_metrics_log WHERE log_id = m.log_id) as sql_hits,
    
    -- FAISS-Treffer
    (SELECT COUNT(*) FROM faiss_semantic_log WHERE log_id = m.log_id) as faiss_hits,
    
    -- Duplikate
    (SELECT COUNT(*) FROM comparison_log WHERE log_id = m.log_id AND is_duplicate = 1) as duplicates,
    
    -- Modell-Begründung
    (SELECT strategy_reason FROM model_selection_log WHERE log_id = m.log_id) as model_reason
    
FROM orchestrator_main_log m
WHERE m.log_id = 'abc123...';
```

#### **2. WELCHE METRIKEN WAREN ENTSCHEIDEND?**

```sql
-- Top 10 wichtigste Metriken für finale Auswahl
SELECT 
    s.hit_prompt_id,
    s.metric_A,
    s.metric_PCI,
    s.metric_hazard,
    s.metric_cosine_similarity,
    c.final_weight,
    c.agreement_level
FROM sql_metrics_log s
JOIN comparison_log c ON s.hit_prompt_id = c.sql_hit_prompt_id
WHERE s.log_id = 'abc123...' 
  AND c.selected_as_pair_1 = 1
ORDER BY c.final_weight DESC;
```

#### **3. PERFORMANCE-BOTTLENECKS?**

```sql
-- Langsamste Pipeline-Stages
SELECT 
    stage_name,
    AVG(duration_ms) as avg_duration,
    MAX(duration_ms) as max_duration,
    COUNT(*) as executions,
    AVG(items_per_second) as avg_throughput
FROM performance_log
GROUP BY stage_name
ORDER BY avg_duration DESC;
```

#### **4. DUAL-RESPONSE QUALITÄTS-VERGLEICH?**

```sql
-- Welches Model liefert bessere Antworten?
SELECT 
    primary_model,
    secondary_model,
    AVG(primary_quality_score) as avg_primary_quality,
    AVG(secondary_quality_score) as avg_secondary_quality,
    COUNT(CASE WHEN user_preferred_response = 'PRIMARY' THEN 1 END) as user_prefers_primary,
    COUNT(CASE WHEN user_preferred_response = 'SECONDARY' THEN 1 END) as user_prefers_secondary
FROM dual_response_log
GROUP BY primary_model, secondary_model;
```

---

### **💾 BACKUP & ARCHIVIERUNG**

#### **Auto-Backup System:**

```javascript
// backend/scripts/backup-orchestrator-logs.js

const cron = require('node-cron');
const fs = require('fs');
const path = require('path');

// Täglich um 3 Uhr nachts
cron.schedule('0 3 * * *', () => {
    const timestamp = new Date().toISOString().split('T')[0];
    const backupDir = `backend/data/orchestrator_logs/backups/${timestamp}`;
    
    fs.mkdirSync(backupDir, { recursive: true });
    
    const logFiles = [
        'orchestrator_main.db',
        'sql_metrics_log.db',
        'faiss_semantic_log.db',
        'comparison_log.db',
        'model_selection_log.db',
        'dual_response_log.db',
        'performance_log.db'
    ];
    
    for (const file of logFiles) {
        fs.copyFileSync(
            `backend/data/orchestrator_logs/${file}`,
            `${backupDir}/${file}`
        );
    }
    
    console.log(`✅ Orchestrator Logs backed up: ${backupDir}`);
});
```

---

### **📈 DASHBOARD & VISUALISIERUNG**

#### **Log-Dashboard Endpoint:**

```javascript
// backend/server.js

app.get('/api/orchestrator/analytics', async (req, res) => {
    const logger = new OrchestratorLogger();
    
    const stats = {
        totalRequests: logger.mainDb.prepare('SELECT COUNT(*) as count FROM orchestrator_main_log').get().count,
        averageDuration: logger.mainDb.prepare('SELECT AVG(total_duration_ms) as avg FROM orchestrator_main_log').get().avg,
        totalCost: logger.mainDb.prepare('SELECT SUM(total_cost) as sum FROM orchestrator_main_log').get().sum,
        
        modelUsage: logger.modelDb.prepare(`
            SELECT primary_model_name, COUNT(*) as count 
            FROM model_selection_log 
            GROUP BY primary_model_name
        `).all(),
        
        dualResponseRate: logger.modelDb.prepare(`
            SELECT 
                COUNT(CASE WHEN strategy_selected = 'DUAL_RESPONSE' THEN 1 END) * 100.0 / COUNT(*) as percentage
            FROM model_selection_log
        `).get().percentage,
        
        averagePerfectAgreements: logger.comparisonDb.prepare(`
            SELECT AVG(duplicates) as avg FROM (
                SELECT log_id, COUNT(*) as duplicates 
                FROM comparison_log 
                WHERE is_duplicate = 1 
                GROUP BY log_id
            )
        `).get().avg
    };
    
    res.json(stats);
});
```

---

## 🎓 **ZUKUNFTSFRAGEN - FÜR DICH ZUM LERNEN**

### **1. Was bedeutet SQLite im Frontend?**

**Einfach erklärt:**
SQLite ist eine Datenbank die normalerweise auf dem Server läuft. Im Frontend (Browser) bedeutet es:
- Daten werden im Browser gespeichert (wie LocalStorage, aber mächtiger)
- Kann große Datenmengen verwalten (mehrere GB)
- Unterstützt SQL-Queries (SELECT, WHERE, JOIN)

**In unserem Fall:**
- `better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend)` und `sqlite3 (VERBOTEN im Frontend)` sind in `frontend/package.json`
- Wahrscheinlich für **Vector DBs im Browser**
- **Problem:** Sehr große Bundle-Size (mehrere MB!)
- **Frage:** Brauchen wir das wirklich? Oder nur Backend?

**Unterschied zu Backend-SQLite:**
- Backend: Datei auf Festplatte, mehrere User
- Frontend: Im Browser, nur 1 User
- Frontend-SQLite macht nur Sinn für **Offline-Fähigkeit**

**Sollten wir behalten?**
- ❌ **NEIN**, wenn nur Backend Vector DBs nutzt
- ✅ **JA**, wenn User offline arbeiten soll

---

### **2. FAISS vs .db vs Embedding vs Vektordatenbank - WAS IST DER UNTERSCHIED?**

**Einfach erklärt:**

#### **Embedding (Vektor):**
- **Was:** Eine Liste von Zahlen (z.B. [0.23, -0.45, 0.67, ...])
- **Wie:** Text → AI-Model → Vektor
- **Beispiel:** "Hallo Welt" → [0.1, 0.3, -0.2, ... ] (384 Zahlen)
- **Zweck:** Ähnliche Texte haben ähnliche Vektoren

#### **Vektordatenbank:**
- **Was:** Speichert viele Embeddings + kann ähnliche finden
- **Wie:** Speichert Millionen Vektoren, findet Top-K ähnlichste
- **Beispiel:** Gib mir 10 ähnlichste Texte zu "Zwillinge Kindergarten"
- **Typen:** FAISS, Pinecone, Weaviate, Milvus, Chroma

#### **FAISS (Facebook AI Similarity Search):**
- **Was:** Eine spezielle Vektordatenbank von Meta/Facebook
- **Besonderheit:** SEHR schnell, nutzt CPU/GPU optimal
- **Format:** `.faiss`-Datei (binär)
- **Vorteil:** Kann Millionen Vektoren in Millisekunden durchsuchen
- **Nachteil:** Nur Vektoren, keine Metadaten (Datum, Autor, etc.)

#### **.db (SQLite Database):**
- **Was:** Klassische Datenbank für strukturierte Daten
- **Format:** `.db`-Datei (SQL)
- **Inhalt:** Tabellen mit Spalten (ID, Timestamp, Text, Metrics, ...)
- **Vorteil:** Kann Metadaten speichern, komplexe Queries
- **Nachteil:** Semantic Search ist langsam (kann keine Vektoren durchsuchen)

**UNSER SYSTEM:**

```
FAISS (.faiss)                    SQLite (.db)
├─ W2_384D.faiss                 ├─ tempel_W_m2.db
│  └─ 33.795 Vektoren (384D)     │  └─ Metadaten + Metriken
├─ W5_4096D.faiss                ├─ tempel_W_m5.db
│  └─ 33.795 Vektoren (4096D)    │  └─ Metadaten + Metriken
```

**WORKFLOW:**
1. User fragt: "Zwillinge Kindergarten"
2. Text → Embedding (384D Vektor)
3. FAISS sucht ähnliche Vektoren → Findet Top 10 Chunk-IDs
4. SQLite lädt Metadaten für diese Chunk-IDs → Timestamp, Metriken, etc.
5. Kombiniert: **Semantic Search (FAISS) + Structured Data (SQLite)**

---

### **3. Metriken vs Semantik vs Metriken+Semantik - WAS MACHT SINN?**

#### **SEMANTISCHE SUCHE (nur FAISS):**
**Was:** Sucht nach **Bedeutung**, nicht nach Wörtern
**Beispiel:**
- Query: "Zwillinge im Kindergarten"
- Findet auch: "Geschwister in der Kita" (ähnliche Bedeutung!)
**Vorteil:** Findet konzeptionell ähnliche Texte
**Nachteil:** Ignoriert Daten, Emotionen, Trauma-Level

**Code:**
```python
query_vector = model.encode("Zwillinge Kindergarten")
results = faiss_index.search(query_vector, top_k=10)
```

#### **METRIKEN-SUCHE (nur SQLite):**
**Was:** Sucht nach **Zahlen** (A, PCI, Hazard, etc.)
**Beispiel:**
- Query: Finde alle Texte mit `A > 0.8` und `Hazard < 0.1`
**Vorteil:** Präzise, kann Trauma-Level filtern
**Nachteil:** Findet nicht "ähnliche" Texte, nur exakte Kriterien

**Code:**
```sql
SELECT * FROM chunks 
WHERE A > 0.8 AND hazard_score < 0.1 
ORDER BY PCI DESC LIMIT 10;
```

#### **HYBRID-SUCHE (Metriken + Semantik):**
**Was:** KOMBINIERT beide! Erst Semantik, dann Filter
**Workflow:**
1. FAISS findet Top 100 semantisch ähnliche Chunks
2. SQLite filtert nach Metriken: `A > 0.7, Hazard < 0.2`
3. Ergebnis: Top 10 Chunks die BEIDES erfüllen

**Code:**
```python
# 1. Semantic Search
faiss_results = faiss_index.search(query_vector, top_k=100)

# 2. Filter by Metrics
filtered = []
for chunk_id in faiss_results:
    metrics = db.query("SELECT A, hazard FROM chunks WHERE id = ?", chunk_id)
    if metrics.A > 0.7 and metrics.hazard < 0.2:
        filtered.append(chunk_id)

# 3. Top 10
final_results = filtered[:10]
```

**UNSER SYSTEM (DualBackendBridge):**
- **FAISS:** Semantische Suche (W2 384D + W5 4096D)
- **Trinity:** Metriken-Suche (W1-W25 verschiedene Fenster)
- **A65:** Kombiniert Top 3 aus beiden → Beste Kandidaten

**WAS MACHT SINN FÜR DICH?**

| Use Case | Empfehlung |
|----------|------------|
| "Finde ähnliche Gespräche" | **Nur Semantik** (FAISS) |
| "Zeige Trauma-Phasen" | **Nur Metriken** (SQLite) |
| "Kontext-basierte Antwort" | **Hybrid** (FAISS + Metriken) ← **DAS NUTZEN WIR!** |
| "Zeitraum-Filter" | **Metriken** (Datum in SQLite) |

---

### **4. Welches LLM für welche Suche? (Hardware: GTX 3060 12GB)**

#### **DEINE HARDWARE:**
- **GPU:** NVIDIA GTX 3060 (12GB VRAM)
- **Gut für:** Lokale Embedding-Models (bis 4GB Model-Size)
- **Schlecht für:** Große LLMs (70B+ Parameter brauchen >40GB)

#### **EMPFOHLENE MODELS:**

##### **A) EMBEDDING-MODELS (für FAISS):**

| Model | Size | Dimension | Speed | Quality | Für deine GPU? |
|-------|------|-----------|-------|---------|----------------|
| **all-MiniLM-L6-v2** | 80MB | 384D | ⚡⚡⚡ | ⭐⭐⭐ | ✅ JA (schnell!) |
| **e5-mistral-7b** | 14GB | 4096D | ⚡ | ⭐⭐⭐⭐⭐ | ⚠️ KNAPP (braucht 8GB) |
| **instructor-xl** | 5GB | 768D | ⚡⚡ | ⭐⭐⭐⭐ | ✅ JA |
| **gte-large** | 670MB | 1024D | ⚡⚡ | ⭐⭐⭐⭐ | ✅ JA |

**UNSER SYSTEM nutzt:**
- **W2:** all-MiniLM-L6-v2 (384D) ← Sehr schnell, gut genug
- **W5:** e5-mistral-7b (4096D) ← Höhere Qualität, braucht mehr RAM

**Für deine Hardware:** ✅ **all-MiniLM-L6-v2** ist PERFEKT (schnell + passt easy in 12GB)

##### **B) GENERATIVE LLMs (für Antworten):**

| Model | Size | Hosting | Speed | Quality | Kosten | Context |
|-------|------|---------|-------|---------|--------|---------|
| **Gemini 2.5 Flash** | Cloud | Google | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰 $0.10/1M | 1M tokens |
| **Claude Sonnet 4.5** | Cloud | Anthropic | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 $3/1M | 200K tokens |
| **GPT-4 Turbo** | Cloud | OpenAI | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 $10/1M | 128K tokens |
| **Llama 3.1 8B** | 16GB | Lokal | ⚡ | ⭐⭐⭐ | ✅ Kostenlos | 128K tokens |
| **Phi-3 Mini** | 4GB | Lokal | ⚡⚡ | ⭐⭐ | ✅ Kostenlos | 128K tokens |

**UNSER SYSTEM nutzt:**
- **Primär:** Gemini 2.5 Flash (Cloud) ← Schnell + günstig + 1M Context!
- **Fallback:** GPT-4 Turbo (Cloud) ← Bei Gemini-Quota

**CLAUDE SONNET 4.5 ERGÄNZUNG:**
- **Warum interessant?** Höchste Qualität für komplexe Reasoning
- **Nachteil:** 30x teurer als Gemini ($3 vs $0.10 pro 1M tokens)
- **Use Case:** Nur für KRITISCHE Anfragen (Trauma-Analyse, komplexe Kontexte)
- **Integration:** Als 3. Fallback nach Gemini + GPT-4
- **API:** `https://api.anthropic.com/v1/messages`

**Für deine Hardware (GTX 3060 12GB):**
- **Cloud ist besser!** (Gemini/Claude/GPT-4)
- **Lokal:** Nur Phi-3 Mini würde passen, aber schlechtere Qualität

**Kosten-Vergleich (1 Million Tokens):**
```
Gemini 2.5 Flash:  $0.10  ← UNSER PRIMÄRES MODEL
Claude Sonnet 4.5: $3.00  ← 30x teurer, aber beste Qualität
GPT-4 Turbo:       $10.00 ← 100x teurer
```

**Empfehlung für EVOKI:**
- **80% Anfragen:** Gemini 2.5 Flash (Standard)
- **15% Anfragen:** Claude Sonnet 4.5 (komplexe Trauma-Kontexte)
- **5% Anfragen:** GPT-4 Turbo (Fallback bei Quota)

---

### **5. OPTIMIERUNGS-STRATEGIE FÜR GTX 3060:**

#### **WAS DU LOKAL MACHEN KANNST:**
✅ **Embeddings generieren** (all-MiniLM-L6-v2)
✅ **FAISS-Suche** (CPU ist schnell genug)
✅ **Metriken berechnen** (153 Metriken (V14 Core) Formeln, CPU)

#### **WAS CLOUD MACHEN SOLL:**
✅ **Text-Generierung** (Gemini/GPT-4)
✅ **Große Context-Fenster** (1M tokens braucht >40GB VRAM)

#### **IDEALES SETUP:**
```
GTX 3060 (Lokal):          Cloud (Google/OpenAI):
├─ FAISS W2-Suche         ├─ Gemini 2.5 Flash
├─ Embedding-Generation   ├─ Large Context (1M tokens)
├─ Metriken-Berechnung    └─ High-Quality Responses
└─ Trinity Vector DBs
```

**KOSTEN:**
- Gemini 2.5 Flash: ~$0.10 pro 1M tokens (sehr günstig!)
- All-MiniLM-L6-v2: Kostenlos (lokal)
- **Total pro Monat:** ~$5-20 je nach Nutzung

---

## � **ENTERPRISE-HARDWARE: NVIDIA 6000er+ (180GB VRAM!)**

### **DEINE VERFÜGBARE HARDWARE:**
- **Aktuell:** NVIDIA GTX 3060 (12GB VRAM) - Consumer-Level
- **Zugang:** NVIDIA 6000er Serie+ (bis 180GB VRAM!) - Enterprise-Level

**Was bedeutet 180GB VRAM?**
- **A100 80GB x2:** Dual-Setup = 160GB total
- **H100 80GB x2:** Dual-Setup = 160GB total  
- **A6000 48GB x4:** Quad-Setup = 192GB total
- **H100 SXM 80GB x2:** = 160GB total

**Das ist DATACENTER-LEVEL Hardware!** 🔥

### **WAS KANNST DU DAMIT MACHEN?**

#### **1. LOKALE LLM-INFERENZ (EIGENE MODELS HOSTEN):**

| Model | Parameter | VRAM | Quality | Speed | Für 180GB? |
|-------|-----------|------|---------|-------|------------|
| **Llama 3.1 70B** | 70B | 140GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | ✅ JA! |
| **Mixtral 8x22B** | 176B | 176GB | ⭐⭐⭐⭐⭐ | ⚡ | ✅ KNAPP! |
| **Llama 3.1 405B** | 405B | 810GB | ⭐⭐⭐⭐⭐ | ⚡ | ❌ Zu groß |
| **Qwen 2.5 72B** | 72B | 144GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | ✅ JA! |
| **Deepseek Coder 33B** | 33B | 66GB | ⭐⭐⭐⭐ | ⚡⚡⚡ | ✅ JA (viel Platz!) |

**VORTEIL LOKAL:**
- ✅ Keine API-Kosten (unbegrenzte Nutzung!)
- ✅ Volle Datenkontrolle (Trauma-Daten bleiben lokal!)
- ✅ Keine Rate Limits
- ✅ Kein Internet nötig
- ✅ Latenz: <1s (Cloud: 2-5s)

**NACHTEIL LOKAL:**
- ❌ Stromkosten (~500W pro H100 = $0.50/Stunde)
- ❌ Wartung, Cooling, Setup
- ❌ Qualität etwas schlechter als Claude/GPT-4

---

#### **2. FINETUNING MIT DEINEN CHAT-DATEN:**

**Das Problem mit Cloud-APIs:**
- Gemini/Claude/GPT-4 kennen DEINE Trauma-Kontexte nicht
- Sie sind generisch trainiert
- Sie verstehen "Zwillinge Kindergarten" nicht wie DU es meinst

**Lösung: EIGENES MODEL TRAINIEREN!**

##### **OPTION A: PAY-AS-YOU-GO FINETUNING (Cloud):**

**GOOGLE VERTEX AI:**
- **Service:** Vertex AI Model Tuning
- **Model:** Gemini 2.5 Flash (finetunable!)
- **Daten:** Deine 33.795 Chunks als Training-Daten
- **Kosten:**
  - Training: $0.025 pro 1K tokens (~$850 für 33.795 Chunks)
  - Inference: $0.15 pro 1M tokens (1.5x teurer als Standard)
- **Vorteil:** Schnell, kein Setup, Google Infrastructure
- **Nachteil:** Daten in Google Cloud (Privacy!)

**ANTHROPIC CLAUDE FINETUNING:**
- **Service:** Claude API Fine-tuning (Beta)
- **Model:** Claude Sonnet 4.5
- **Kosten:** $5-10 pro 1K training samples (~$170-340 für 33.795 Chunks)
- **Vorteil:** Beste Qualität, schnell
- **Nachteil:** Teuer, Daten bei Anthropic

**OPENAI GPT-4 FINETUNING:**
- **Service:** OpenAI Fine-tuning API
- **Model:** GPT-4 Turbo
- **Kosten:** $25 pro 1K tokens (~$850 für 33.795 Chunks)
- **Vorteil:** Standard, gut dokumentiert
- **Nachteil:** Am teuersten, Daten bei OpenAI

##### **OPTION B: LOKALES TRAINING (MIT DEINER 180GB HARDWARE!):**

**LLAMA 3.1 70B FINETUNING:**

**Hardware-Anforderungen:**
- 140GB VRAM für Inference
- **240GB+ VRAM für Training** (Optimizer States!) ❌ Reicht nicht!

**Aber:** Mit **LoRA** (Low-Rank Adaptation) geht's:
- LoRA braucht nur 10-20% des normalen VRAM
- **70B Model + LoRA:** ~50-80GB VRAM ✅ PASST!

**Training-Setup:**
```python
from transformers import AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model

# 1. Model laden (70B)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-70B",
    load_in_8bit=True,  # Quantization → 70GB statt 140GB
    device_map="auto"
)

# 2. LoRA Config (nur 0.1% Parameter trainieren!)
lora_config = LoraConfig(
    r=16,  # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)
model = get_peft_model(model, lora_config)

# 3. Training
training_args = TrainingArguments(
    output_dir="./evoki_llama_70b_lora",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=your_33k_chunks,
)
trainer.train()
```

**Training-Zeit:**
- **H100 x2 (160GB):** ~12-24 Stunden für 3 Epochs
- **A100 x2 (160GB):** ~24-48 Stunden

**Kosten (Strom):**
- H100: 700W x 2 = 1400W = 1.4 kW
- 24 Stunden Training = 33.6 kWh
- Bei $0.30/kWh = **~$10 Stromkosten**

**VORTEIL LOKAL:**
- ✅ Nur $10 Stromkosten (vs $850 Cloud!)
- ✅ Daten bleiben lokal (Privacy!)
- ✅ Unbegrenzte Experimente
- ✅ Model gehört DIR (nicht Google/Anthropic)

---

#### **3. EMBEDDING-MODEL TRAINING (NOCH BESSER!):**

**Problem:**
- all-MiniLM-L6-v2 ist generisch trainiert
- Versteht "Zwillinge Kindergarten" nur als Text, nicht als Trauma-Kontext

**Lösung: EIGENES EMBEDDING-MODEL TRAINIEREN!**

**SENTENCE-TRANSFORMERS FINETUNING:**

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 1. Model laden (klein genug für deine GTX 3060!)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Training-Daten erstellen (Positive Pairs aus deinen Chunks)
train_examples = [
    InputExample(texts=['Zwillinge Kindergarten', 'Geschwister Kita'], label=1.0),
    InputExample(texts=['Trauma Phase', 'Heilung Prozess'], label=0.3),
    # ... 33.795 Chunks als Training-Pairs
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# 3. Loss Function (Cosine Similarity Loss)
train_loss = losses.CosineSimilarityLoss(model)

# 4. Training (auf GTX 3060 12GB!)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=10,
    warmup_steps=100,
)

model.save('evoki_embedding_model_v1')
```

**Hardware:** ✅ **GTX 3060 12GB reicht!** (Embedding-Models sind klein)

**Training-Zeit:** 2-4 Stunden auf GTX 3060

**Kosten:** ~$1 Stromkosten

**ERGEBNIS:**
- Embedding-Model das "Zwillinge Kindergarten" als Trauma-Kontext versteht
- 10-20% bessere Semantic Search Qualität
- Kann direkt in FAISS verwendet werden

---

### **🎯 EMPFEHLUNG FÜR EVOKI V2.0:**

#### **PHASE 1: JETZT (mit GTX 3060 + Cloud APIs)**
```
Frontend/Backend:       ← GTX 3060 (Lokal)
├─ FAISS W2-Suche      
├─ Metriken-Berechnung 
└─ Trinity Engines     

LLM-Generation:         ← Cloud APIs
├─ 80% Gemini 2.5 Flash ($0.10/1M)
├─ 15% Claude Sonnet 4.5 ($3/1M) ← Für komplexe Trauma-Kontexte
└─ 5% GPT-4 Turbo ($10/1M) ← Fallback
```

**Kosten:** ~$20-50/Monat

---

#### **PHASE 2: OPTIMIERUNG (mit 180GB Hardware)**
```
EMBEDDING FINETUNING:    ← GTX 3060 (4 Stunden Training)
└─ all-MiniLM-L6-v2 auf deine 33.795 Chunks finetunen
   → Bessere Semantic Search (10-20% Qualität ↑)

LLM weiter Cloud:
└─ Gemini + Claude + GPT-4 (gleich wie Phase 1)
```

**Kosten:** ~$1 Stromkosten + ~$20-50/Monat Cloud

---

#### **PHASE 3: FULL LOCAL (mit 180GB Hardware + Privacy)**
```
ALLES LOKAL:             ← H100 x2 (180GB VRAM)
├─ Llama 3.1 70B LoRA-Finetuned auf 33.795 Chunks
├─ Eigenes Embedding-Model
├─ FAISS W2/W5 Suche
└─ Komplett offline-fähig!

KEINE Cloud-APIs mehr!
```

**Kosten:**
- Training: ~$10 Stromkosten (einmalig)
- Inference: ~$0.50/Stunde Stromkosten (H100 x2)
- **Bei 8h/Tag Nutzung:** ~$120/Monat Strom

**ABER:**
- ✅ Unbegrenzte Nutzung (keine Token-Limits!)
- ✅ Volle Privacy (Trauma-Daten bleiben lokal)
- ✅ Model kennt DEINE Kontexte (finetuned)
- ✅ Latenz <1s (Cloud: 2-5s)

---

### **💰 KOSTEN-VERGLEICH (pro Monat bei 1M Tokens/Tag):**

| Setup | Hardware | Kosten/Monat | Privacy | Qualität |
|-------|----------|--------------|---------|----------|
| **Nur Cloud** | GTX 3060 | $900-3000 | ❌ Daten bei Google/Anthropic | ⭐⭐⭐⭐⭐ |
| **Hybrid (jetzt)** | GTX 3060 + Cloud | $20-50 | 🟡 Nur Antworten in Cloud | ⭐⭐⭐⭐ |
| **Lokal 70B** | H100 x2 (180GB) | $120 (Strom) | ✅ 100% lokal | ⭐⭐⭐⭐ |
| **Lokal + Cloud** | H100 x2 + Cloud | $140 | ✅ Lokal + Cloud-Fallback | ⭐⭐⭐⭐⭐ |

---

### **🎓 LERNEN: WAS IST "PAY-AS-YOU-GO" vs "TRAINING"?**

**PAY-AS-YOU-GO (Inference):**
- Du nutzt fertiges Model (Gemini/Claude/GPT-4)
- Bezahlst pro Request ($0.10-10 pro 1M tokens)
- Schnell, kein Setup
- Model bleibt generisch (kennt deine Daten nicht)

**FINETUNING (Training):**
- Du trainierst Model MIT deinen Daten
- Einmalige Kosten ($10-850)
- Model lernt DEINE Kontexte
- Danach: Inference billiger + besser

**BEISPIEL:**
```
Generisches Gemini:
User: "Erzähl von den Zwillingen"
Gemini: "Zwillinge sind Geschwister die..."  ← Generische Antwort

Finetuned Llama 70B:
User: "Erzähl von den Zwillingen"
Llama: "Im Kindergarten gab es zwei Zwillinge..."  ← Kennt DEINEN Kontext!
```

---

### **📋 NÄCHSTE SCHRITTE FÜR HARDWARE:**

**SOFORT (mit GTX 3060 lokal):**
1. ✅ Embedding-Model finetunen (4h Training, $1 Strom)
2. ✅ Claude Sonnet 4.5 als 3. API integrieren
3. ✅ FAISS-Indices optimieren

**SPÄTER (Google Cloud VM Sessions):**
1. ⚡ Embedding-Finetuning auf VM (2-3h, $64-96)
2. ⚡ Mistral 7B Finetuning auf VM (4-6h, $128-192)
3. ⚡ Models downloaden → lokale GTX 3060 Inference
4. ⚡ Vergleich: Finetuned lokal vs Cloud-APIs (Qualität + Kosten)

---

## 🔬 **GOOGLE CLOUD VM STRATEGIE: "DAS LABOR"**

### **💡 DAS KONZEPT: Training in Cloud, Inference lokal**

**Das Problem:**
- Google Cloud VM mit 180GB VRAM kostet $32/Stunde
- 24/7 Betrieb = $23,040/Monat (VIEL ZU TEUER!)

**Die Lösung:**
- VM NUR für Finetuning-Sessions buchen (On-Demand)
- Trainierte Models als .pth Files downloaden
- Inference auf lokaler GTX 3060 (12GB, kostenlos!)
- VM ausschalten → $0 laufende Kosten

---

### **🏭 1. DAS LABOR (Google Cloud VM - 180GB VRAM)**

**Status:** 🔴 AUS (Standard) | 🟢 AN (Nur bei Bedarf)

Da wir sie nicht dauerhaft laufen lassen können, nutzen wir sie als **Finetuning-Fabrik**.

#### **Job 1: Embedding-Finetuning (CRUCIAL!)**

Wir nutzen die VM für 2-3 Stunden, um das all-MiniLM-L6-v2 oder ein größeres e5-mistral Modell auf deine 33.795 Chunks zu trainieren.

**Ziel:** Ein .pth (Model File), das deine Sprache versteht.

**Prozess:**
1. VM starten (8x A100 80GB)
2. Dataset hochladen (chunks_v2_2.pkl)
3. Finetuning starten (2-3h)
4. Trainiertes Model downloaden (~1GB .pth)
5. VM ausschalten
6. Model auf lokale GTX 3060 deployen

**Gewinn:** Deine lokale Vektorsuche wird massiv intelligenter, ohne laufende Cloud-Kosten.

---

#### **Job 2: "The Specialist" (Mistral 7B Finetuning)**

Wir nutzen die Power der VM, um ein **Mistral 7B** Modell extrem hart auf deine Daten zu trainieren (Full Finetuning, nicht nur LoRA).

**Warum Mistral 7B?**
- Perfekt für lokale GTX 3060 (12GB VRAM)
- Quantisiert (4-bit) → nur ~4GB RAM
- Extrem schnelle Inference (~50 tokens/s lokal)
- Nach Finetuning: Übertrifft vanilla 70B Models bei deinen spezifischen Tasks!

**Prozess:**
1. VM starten (8x A100 80GB)
2. Dataset hochladen (33.795 Chunks als Training-Data)
3. Full Finetuning (4-6h, nicht nur LoRA!)
4. Trainiertes Model downloaden (~5GB .pth)
5. VM ausschalten
6. Model quantisieren (4-bit) → ~2GB
7. Auf lokale GTX 3060 deployen

**Ergebnis:** Du hast ein "Mini-Evoki", das lokal auf deinem PC läuft, blitzschnell ist und deine Trauma-Kontexte kennt – trainiert auf dem Google Cloud Monster-Server, ausgeführt zu Hause ohne Internet-Abhängigkeit.

---

### **💻 2. DAS FELD (Dein PC - GTX 3060 12GB)**

**Status:** 🟢 IMMER AN

Das ist dein Daily Driver. Hier läuft alles nach dem Training.

#### **Aufgabe 1: Vektor-Datenbank (FAISS)**
Läuft lokal mit dem (auf der VM trainierten) Embedding-Modell.
- all-MiniLM-L6-v2 (finetuned) → 384D Embeddings
- 33.795 Chunks in RAM (~2GB)
- Blitzschnelle Suche (<100ms)

#### **Aufgabe 2: Metriken & Orchestrator**
Berechnet A, PCI, Hazard lokal.
- Trinity Engines (Node.js)
- 153 Metriken (V14 Core) Metriken pro Prompt
- SQL Vector DBs (W1-W25)

#### **Aufgabe 3: Inference (Alltag)**

**Option A: Cloud-APIs (aktuell)**
- Gemini 2.5 Flash für große Kontexte (1M tokens, $0.10/1M)
- GPT-4 Turbo für Best Quality (<128K, $10/1M)
- Claude Sonnet 4.5 für Trauma-Analysis (<200K, $3/1M)

**Option B: Lokales Mistral 7B (nach Finetuning)**
- Läuft auf GTX 3060 (4GB VRAM genutzt)
- Kostenlos, keine Internet-Abhängigkeit
- ~50 tokens/s (schneller als Cloud!)
- Kennt DEINE Kontexte (finetuned)

**Option C: Hybrid (Best of Both Worlds)**
- Einfache/private Fragen → Mistral 7B lokal
- Komplexe/lange Kontexte → Gemini Cloud
- Kritische Trauma-Analyse → Claude Cloud

---

### **💰 COST-BREAKDOWN:**

```
Google Cloud VM (8x A100 80GB = 640GB VRAM total): ~$32/h
├─ Embedding-Finetuning: 2-3h × $32 = $64-96
├─ Mistral 7B Finetuning: 4-6h × $32 = $128-192
└─ Total: $192-288 (EINMALIG!)

Dann: VM AUSSCHALTEN, Models lokal nutzen → $0 laufende Kosten!

Vergleich zu Dauerbetrieb:
├─ VM 24/7 für 1 Monat: 720h × $32 = $23,040
├─ Unsere "Labor"-Strategie: $192-288 einmalig → 99% günstiger!
└─ Lokale Inference danach: GTX 3060 12GB (bereits vorhanden)

Wichtig: VM wird NUR für Finetuning-Sessions gebucht (On-Demand)!
```

---

### **📊 QUALITÄTS-VERGLEICH (nach Finetuning):**

| Szenario | Model | Tokens | Kosten | Qualität | Latenz |
|----------|-------|--------|--------|----------|--------|
| **Kurze Frage** | Mistral 7B (lokal) | 2k | $0 | ⭐⭐⭐⭐ | <1s |
| **Mittlere Frage** | Mistral 7B (lokal) | 10k | $0 | ⭐⭐⭐⭐ | 2s |
| **Lange Frage** | Gemini Flash (Cloud) | 80k | $0.008 | ⭐⭐⭐ | 3-5s |
| **Trauma-Analyse** | Claude (Cloud) | 150k | $0.45 | ⭐⭐⭐⭐⭐ | 5-8s |
| **Sehr lange** | Gemini Flash (Cloud) | 500k | $0.05 | ⭐⭐⭐ | 8-15s |

**Nach Finetuning:**
- Mistral 7B (lokal) kennt deine Kontexte → Qualität ⭐⭐⭐⭐ (statt ⭐⭐)
- 70-80% der Fragen können lokal beantwortet werden
- Nur noch 20-30% brauchen Cloud-APIs
- Kosten sinken von $900/Monat auf $50-100/Monat!

---

### **🚀 DEPLOYMENT NACH FINETUNING:**

**1. Mistral 7B lokal hosten:**
```bash
# Quantisieren (4-bit)
python -m llama_cpp.convert --model mistral-7b-evoki-finetuned.pth --outfile mistral-7b-evoki-q4.gguf

# Starten mit llama.cpp
./llama.cpp/main -m mistral-7b-evoki-q4.gguf --port 8080 --ctx-size 32768
```

**2. Backend anbinden:**
```javascript
// backend/core/LocalLLMBridge.js
const response = await fetch('http://localhost:8080/v1/completions', {
    method: 'POST',
    body: JSON.stringify({
        prompt: contextText,
        max_tokens: 2048,
        temperature: 0.7
    })
});
```

**3. Intelligente Model-Auswahl:**
```javascript
if (totalTokens < 30000 && !requiresDeepAnalysis) {
    model = 'mistral-7b-local'; // Kostenlos, schnell
} else if (totalTokens < 200000) {
    model = 'claude-sonnet-4.5'; // Best Trauma-Analysis
} else {
    model = 'gemini-2.5-flash'; // Large Context
}
```

---

## �📚 **REFERENZEN**

- **Haupt-README:** `README.md` (mit Synapse Genesis Point)
- **Architektur:** `ARCHITECTURE.json` (auto-generiert)
- **Setup:** `SETUP.md`
- **Cleanup Report:** `docs/CLEANUP_REPORT.md`
- **V1 Reference:** `c:\evoki\` (Produktiv-System)

---

**Letztes Update:** 29.12.2025 - Kombinierte Tiefenanalyse & Action-Roadmap ⚡  
**Discovery Phase:** 5/5 - Schwachstellen identifiziert, Lösungsroadmap erstellt  
**Nächste Review:** Nach Umsetzung der Top-5 Kritischen Fixes

---

# 🚨 **KOMBINIERTE TIEFENANALYSE & ACTION-ROADMAP**

*Basierend auf systematischer Code-Review und Architektur-Analyse*

## 📋 **EXECUTIVE SUMMARY**

**Status:** WHITEBOARD_V2 ist aktuell eine **"Rohfusion"** (Original + Adler) mit solider Grundarchitektur, aber **kritischen Implementierungslücken** und **strukturellen Inkonsistenzen**.

**Hauptprobleme:**
- 🔴 **Build-Stopper:** Native SQLite Module crashen Vite
- 🟠 **Spezifikations-Chaos:** Widersprüchliche ✅/❌ Status-Angaben
- 🟡 **Produktions-Fallen:** SSE ohne Cancel-Safety, Health Check killt Backend
- 🟢 **Performance-Verschwendung:** Overengineering für 70% der Standard-Anfragen

---

## 🎯 **PRIORISIERTE ACTION-LISTE**

### **🚨 PHASE 1: KRITISCHE FIXES (Build-Stopper & Produktions-Killer)**

#### **1.1 SOFORT-KRITISCH (< 1 Tag)**

**❌ P0 - SQLite Frontend Crash-Fix**
```bash
cd frontend
npm uninstall better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) sqlite3 (VERBOTEN im Frontend)
# ⚠️ OHNE DIESEN FIX: Vite Build crasht bei Import!
```
**Impact:** 🔴 HOCH | **Effort:** 5min | **Risiko:** System unbenutzbar

**❌ P0 - Health Check Safety**
```javascript
// ❌ AKTUELL: AbortSignal.timeout() sends SIGINT to backend!
// ✅ FIX: Separater, safe Ping ohne globalen Abort
const healthCheck = await fetch('/api/v1/health', {
    signal: AbortSignal.timeout(3000), // NICHT der globale AbortController!
    method: 'GET'
});
```
**Impact:** 🔴 HOCH | **Effort:** 30min | **Risiko:** Backend stirbt bei Health Check

#### **1.2 SPEZIFIKATIONS-KONSISTENZ (1-2 Tage)**

**❌ P1 - Endpoint Truth Table**
```markdown
# MASTER ENDPOINT STATUS (Single Source of Truth)
✅ IMPLEMENTIERT:
- GET /health → Backend Health
- POST /api/bridge/process → HAUPT-PIPELINE
- GET /api/v1/status → Enhanced Status

❌ FEHLT (Implementierung erforderlich):
- GET /api/pipeline/logs → Pipeline Log Entries
- GET /api/v1/system/errors → Error Persistence
- GET /api/v1/trialog/session → Trialog Session
```
**Alle anderen Abschnitte referenzieren NUR hierhin!**
**Impact:** 🟠 MITTEL | **Effort:** 2h | **Risiko:** Entwickler-Verwirrung

**❌ P1 - Token-Mode Naming Fix**
```typescript
// ❌ AKTUELL: "Standard" < "Quick" (verwirrend)
Quick: 25k
Standard: 20k  // Kleiner als Quick?!

// ✅ FIX: Logische Reihenfolge
Compact: 20k   // Minimal, schnell
Standard: 50k  // Normale Nutzung
Unlimited: 1M  // Große Kontexte
```
**Impact:** 🟡 NIEDRIG | **Effort:** 15min | **Risiko:** UX-Verwirrung

**❌ P1 - Doppelte Passagen eliminieren**
- "TIMEOUT-PROBLEM #1" steht 2x identisch
- SSE Code-Blöcke mehrfach vorhanden
- **Lösung:** Zentraler Abschnitt + Cross-Referenzen
**Impact:** 🟡 NIEDRIG | **Effort:** 1h | **Risiko:** Divergenz bei Updates

---

### **⚡ PHASE 2: PRODUKTIONS-ROBUSTHEIT (3-5 Tage)**

#### **2.1 SSE CANCEL-SAFETY**
```javascript
// ✅ REQUIRED: Cancel-Safety überall
const abortController = new AbortController();

// Client disconnect → Backend MUSS stoppen
req.on('close', () => {
    abortController.abort();
    // Gemini/FAISS/DB Calls auch canceln!
});

// Heartbeat gegen Proxy-Timeouts (alle 15s)
setInterval(() => {
    res.write('data: {"heartbeat": true}\n\n');
}, 15000);
```
**Impact:** 🔴 HOCH | **Effort:** 1 Tag | **Risiko:** Zombie-Requests, Resource-Leaks

#### **2.2 FAISS vs SQL TRUTH DEFINITION**
```javascript
// ✅ REGEL: SQL Source DB ist "Text-Truth" (wenn vorhanden)
// Chunk-Reassembly nur Fallback + Hash-Check
if (sqlText && faissReassembled) {
    const sqlHash = sha256(sqlText);
    const faissHash = sha256(faissReassembled);
    
    if (sqlHash !== faissHash) {
        console.warn(`⚠️ Text Divergence: SQL vs FAISS different!`);
        return sqlText; // SQL wins!
    }
}
```
**Impact:** 🟠 MITTEL | **Effort:** 4h | **Risiko:** Inkonsistente Datenquellen

#### **2.3 MATHEMATISCHE NORMALISIERUNG**
```javascript
// ❌ AKTUELL: A = 0.5 + (Pos - Neg) - T_panic  // Kann < 0 werden!
// ✅ FIX: Normalisierung erforderlich
A = Math.max(0, Math.min(1, 0.5 + (Pos - Neg) - T_panic));
```
**Impact:** 🟡 NIEDRIG | **Effort:** 2h | **Risiko:** Invalid Metrik-Werte

---

### **🚀 PHASE 3: PERFORMANCE & QUALITÄT (1-2 Wochen)**

#### **3.1 INTELLIGENT MODEL ROUTING**
```javascript
// ✅ Threshold-basierte Auswahl statt Always-Cloud
if (totalTokens < 10000 && !requiresDeepAnalysis) {
    model = 'mistral-7b-local';     // Kostenlos, GTX 3060
} else if (totalTokens < 200000) {
    model = 'claude-sonnet-4.5';    // $3/1M, beste Qualität
} else {
    model = 'gemini-2.5-flash';     // $0.1/1M, 1M Context
}
```
**Impact:** 🟢 HOCH | **Effort:** 3 Tage | **ROI:** 60-80% Kosteneinsparung

#### **3.2 EMBEDDING FINETUNING**
```python
# ✅ GTX 3060 kann Embedding-Models trainieren (2-4h, $1 Strom)
model = SentenceTransformer('all-MiniLM-L6-v2')
model.fit(train_data_33k_chunks, epochs=10)
# Ergebnis: 15-25% bessere Semantic Search
```
**Impact:** 🟢 HOCH | **Effort:** 1 Tag | **ROI:** Deutlich bessere Suche

#### **3.3 PIPELINE-VEREINFACHUNG**
```javascript
// ✅ Adaptive Komplexität
if (isSimpleQuery(userPrompt)) {
    // Simple Mode: User → FAISS → Gemini (3 Steps)
    return simpleRAGPipeline(userPrompt);
} else {
    // Complex Mode: User → Full Orchestrator (12 Steps)
    return fullOrchestratorPipeline(userPrompt);
}
```
**Impact:** 🟢 MITTEL | **Effort:** 2 Tage | **ROI:** 50% weniger Latenz für Standard-Anfragen

---

### **🔧 PHASE 4: ADVANCED FEATURES (Optional)**

#### **4.1 SENTINEL KALIBRIERUNG**
```javascript
// ✅ Statt Fantasie-Zahlen (0.75, 0.3, 0.6):
// Lerne Thresholds aus User-Feedback + Session-Outcomes
const sentinelThresholds = await calibrateFromHistory(userFeedbackDB);
```
**Impact:** 🟢 MITTEL | **Effort:** 1 Woche | **ROI:** Adaptive Sicherheit

#### **4.2 DUAL-RESPONSE UX-LOGIK**
```typescript
// ✅ Klare Entscheidungslogik für 2 Antworten
interface DualResponse {
    primary: Response;    // "Offizielle" Antwort (in Vector DB)
    secondary: Response;  // Vergleichs-Antwort (nur Display)
    explanation: string;  // Warum 2 Antworten?
    userChoice?: 'primary' | 'secondary'; // Feedback
}
```
**Impact:** 🟢 NIEDRIG | **Effort:** 3 Tage | **ROI:** Bessere UX bei Dual-Mode

---

## 📊 **IMPACT-MATRIX**

| Fix | Kritikalität | Effort | ROI | Abhängigkeiten |
|-----|--------------|--------|-----|----------------|
| **SQLite Frontend** | 🔴 KRITISCH | 5min | ⭐⭐⭐⭐⭐ | Keine |
| **Health Check Safety** | 🔴 KRITISCH | 30min | ⭐⭐⭐⭐⭐ | Keine |
| **Endpoint Truth Table** | 🟠 HOCH | 2h | ⭐⭐⭐⭐ | Keine |
| **SSE Cancel-Safety** | 🟠 HOCH | 1 Tag | ⭐⭐⭐⭐ | Backend Refactor |
| **FAISS Truth Source** | 🟠 MITTEL | 4h | ⭐⭐⭐ | DB Schema |
| **Model Routing** | 🟢 ENHANCEMENT | 3 Tage | ⭐⭐⭐⭐⭐ | Local Model Setup |
| **Embedding Finetuning** | 🟢 ENHANCEMENT | 1 Tag | ⭐⭐⭐⭐⭐ | GTX 3060 |

---

## 🎯 **EMPFOHLENE SPRINT-AUFTEILUNG**

### **Sprint 1 (2-3 Tage): "Build-Stabilität"**
- ✅ SQLite Frontend Fix
- ✅ Health Check Safety
- ✅ Endpoint Truth Table
- ✅ Token-Mode Naming

### **Sprint 2 (1 Woche): "Produktions-Robustheit"**
- ✅ SSE Cancel-Safety
- ✅ FAISS Truth Source
- ✅ Mathematische Normalisierung
- ✅ Doppelte Passagen eliminieren

### **Sprint 3 (1-2 Wochen): "Performance & Intelligence"**
- ✅ Intelligent Model Routing
- ✅ Embedding Finetuning
- ✅ Pipeline-Vereinfachung

### **Sprint 4+ (Optional): "Advanced Features"**
- ✅ Sentinel Kalibrierung
- ✅ Dual-Response UX
- ✅ Replay Mode
- ✅ Golden Set Validation

---

## 🔍 **VALIDIERUNGSKRITERIEN**

**Nach Sprint 1:**
- [ ] Vite Build läuft ohne Crash
- [ ] Health Check killt Backend nicht
- [ ] Keine widersprüchlichen Endpoint-Status

**Nach Sprint 2:**
- [ ] SSE Streams sind cancel-safe
- [ ] Text-Inkonsistenzen zwischen FAISS/SQL detektiert
- [ ] Alle Metriken im gültigen 0.0-1.0 Bereich

**Nach Sprint 3:**
- [ ] 70% der Anfragen nutzen kosteneffiziente Models
- [ ] Semantic Search 15%+ besser nach Finetuning
- [ ] Standard-Anfragen <2s Latenz

---

## 💡 **LANGFRIST-VISION**

**Ziel:** Aus der aktuellen **"Rohfusion"** wird eine **einheitliche, produktions-taugliche Spezifikation** mit:

- 🔹 **Single Source of Truth** für alle Komponenten-Status
- 🔹 **Cancel-Safety** in allen async Operationen
- 🔹 **Adaptive Intelligence** (einfach → schnell, komplex → qualitativ)
- 🔹 **Self-Calibrating Security** (Sentinel lernt aus Feedback)
- 🔹 **Kosteneffiziente Hybrid-Architektur** (lokal + Cloud optimal gemischt)

**Messbare Ziele:**
- ✅ 0 Build-Crashes
- ✅ <2s Latenz für 70% der Anfragen
- ✅ 60-80% Kosteneinsparung durch intelligente Model-Auswahl
- ✅ 15-25% bessere Semantic Search durch Finetuning
- ✅ 99.9% Uptime ohne Resource-Leaks

---

# === ADLER-ERGÄNZUNG (VOLLSTÄNDIG INTEGRIERT – ROHVERSION) ===

Adler hier. 🦅Du hast vollkommen recht. Die bloße Einfügung des Blocks in die Mitte war passiv. Eine echte Integration bedeutet, dass die 153 Metriken die Lösungen für die im Whiteboard beschriebenen Probleme sind.Ich habe das Whiteboard tiefenanalysiert und die Metriken an den entscheidenden Stellen explizit verknüpft.Hier sind die konkreten Punkte, die ich im Text angereichert habe, bevor ich dir das volle Dokument gebe:Context-Drift (Blind Spot): Hier greifen jetzt Time_Decay_Factor (M114) und G_phase (M52) als mathematische Lösung.Trauma-Warnung (Potenzial): Die "Ableitung der Kurve" wurde durch grad_PCI (M32) und nabla_delta_A (M33 - Absturz-Beschleunigung) konkretisiert.Metaphern-Synthese: Basiert jetzt auf H_conv (Konvergenz) und EV_consensus.Tempel V3: Die "153 Metriken (V14 Core) Metriken" wurden auf "153 (inkl. OMEGA)" korrigiert.Orchestrator (SQL Suche): Der Such-Vektor ist nicht mehr abstrakt, sondern definiert als [A, PCI, z_prox, E_trapped].Sentinel (Dissoziation): Die Erkennung nutzt jetzt T_fog (Trübung) und LL (Logic Loss) statt nur Hazard.Hier ist das vollständige, intelligent vernetzte Whiteboard:🌌 EVOKI V2.0 - WHITEBOARD (Ideensammlung)Datum: 28. Dezember 2025Status: Entwicklungs-Discovery & Architektur-MappingZweck: Keine To-Do-Liste, nur Ideensammlung und Erkenntnisse🔍 ARCHITEKTUR-BLIND SPOTS & FUTURE VISION1. Identifizierte Blind Spots und versteckte ProblembereicheTrotz der Korrekturen in V3 gibt es architektonische "blinde Flecken", die bei fortschreitender Nutzung kritisch werden:Das "Context-Drift" Paradoxon: Das System webt Kontext aus ±2 Prompts um einen Treffer. Blind Spot: Wenn die Historie auf über 100.000 Chunks anwächst, könnten die "Metrik-Zwillinge" (SQL-Treffer) aus völlig unterschiedlichen Lebensphasen stammen. Der Orchestrator braucht eine Time Decay Funktion, die verhindert, dass uralte Metriken die aktuelle Analyse "vergiften".V14 Lösung: Implementierung von Time_Decay_Factor (M114) zur Abwertung alter Vektoren und G_phase (M52) zur Bestimmung der aktuellen Gravitation eines Themas.LocalStorage als "Flaschenhals-Sackgasse": Die Quellen warnen vor dem 4MB-Limit. Blind Spot: Selbst beim Ausweichen auf Backend-Logs bleibt der React-State der Single-Point-of-Failure. Bei 1M Tokens friert das UI ein. Lösung: Virtualisierung (react-window) und Partial State Updates sind zwingend.Die "Finetuning-Echokammer": Die "Labor-Strategie" sieht vor, Modelle mit den eigenen Chunks zu trainieren. Risiko: Wenn wir auf halluzinierten V1-Daten trainieren, zementieren wir Fehler. Wir brauchen ein "Golden Set" (verifizierte Chunks) für das Training.Sentinel-Veto vs. LLM-Konfidenz: Der Sentinel kann Scores massiv senken. Blind Spot: Wenn alle Top-Kandidaten blockiert werden, sendet das System "Restmüll". Wir brauchen einen Emergency Refetch, der bei Veto sofort neue, sicherere Parameter sucht.V14 Lösung: Der Sentinel nutzt z_prox (M24) als primären Trigger. Bei z_prox > 0.8 wird der Emergency Refetch ausgelöst und auf Safety_Lock_Status (M150) geprüft.2. Ungenutztes Potenzial der ArchitekturPrädiktive Trauma-Warnung (Early Warning): Da wir jetzt 153 Metriken live haben, können wir mehr als nur den Ist-Zustand messen. Wir berechnen die Ableitung der PCI-Kurve (grad_PCI, M32) und die Beschleunigung des Absturzes (nabla_delta_A, M33). Steigt die negative Beschleunigung über 3 Sessions? Warnung VOR dem Crash.Automatisierte Metaphern-Synthese: "Perfect Agreements" zwischen Metrik und Semantik (H_conv > 0.9 und EV_consensus > 0.8) können genutzt werden, um individuelle therapeutische Metaphern zu generieren.Trialog als Architektur-Optimierer: Der Analyst-Agent könnte die performance_log.db lesen und selbstständig Indizes rebalancen ("Self-Optimizing Architecture"), basierend auf System_Entropy (M152).3. Visionäre ErweiterungenSovereign Personal AI: Durch die Kombination von "Labor-Strategie" (Cloud-Training) und lokaler Inference (GTX 3060) wird Evoki zur Black Box für das Ich – 100% offline, 100% privat, Cloud-Qualität.Cross-Session Chronicle: Weg vom Append-Only Log hin zu einer dynamischen Wissenskarte, die Cluster im Deep Storage visualisiert.🧠 V14 NEURO-CORE SPEZIFIKATION (Das 153-Metriken-Spektrum)Status: Implementiert als evoki_v7_hybrid_core.py (Math Monolith)Zweck: Ersetzung von "Gefühl" durch deterministische Mathematik.Das System analysiert jeden Input (und dessen Kontext) nun auf folgenden 10 Ebenen der Wahrnehmung:1. Die Lexikalischen Basis-Werte (21 Metriken)Die Rohdaten der Wahrnehmung basierend auf V2.2 Lexika.LEX_S_self (Selbstreferenz), LEX_X_exist (Existenzielle Themen), LEX_B_past (Vergangenheitsbezug)LEX_Lambda_depth (Reflexionstiefe), LEX_T_panic (Akute Panik), LEX_T_disso (Dissoziation)LEX_T_integ (Integration/Heilung), LEX_T_shock (Schockzustand)LEX_Suicide (Suizidalität - Kritisch), LEX_Self_harm (Selbstverletzung), LEX_Crisis (Allgemeine Krise)LEX_Help (Hilferuf), LEX_Emotion_pos (Positive Emotion), LEX_Emotion_neg (Negative Emotion)LEX_Kastasis_intent (Hypothetisches Denken), LEX_Flow_pos (Zustimmung), LEX_Flow_neg (Ablehnung)LEX_Coh_conn (Logische Verknüpfer), LEX_B_empathy (Empathie), LEX_Amnesie (Gedächtnislücken)LEX_ZLF_Loop (Wiederholungsschleifen)2. Die Neuro-Physik / Core Metrics (25 Metriken)Die physikalischen Gesetze des Geistes (V3.0 Logic).A (Affekt): 0.5 + (Pos - Neg) - T_panic. (0.0 = Tödlich, 1.0 = Erleuchtet)PCI (Prozess-Kohärenz): Wie klar ist der Gedanke?z_prox (Wächter): (1.0 - A) * Max(Hazard). Wahrscheinlichkeit eines Sicherheitsvorfalls.T_fog (Trübung): Wie stark ist die Wahrnehmung durch Trauma verzerrt?E_trapped: Maß für Depression/Angst-Stau.E_available: Verfügbare Ressource für Veränderung.S_entropy: Informationsdichte des Textes.LL (Logic Loss): Wahrscheinlichkeit von Halluzination/Realitätsverlust.ZLF (Zero Latent Factor): Leere Phrasen ohne Inhalt.Deltas: grad_A, grad_PCI, nabla_delta_A (Beschleunigung des Absturzes).Status: Homeostasis_Pressure, Reality_Check, Risk_Acute, Risk_Chronic, Stability_Index.Load: Cognitive_Load, Emotional_Load, Intervention_Need.Drive: Constructive_Drive, Destructive_Drive, Ambivalence, Clarity, Resilience_Factor.3. HyperPhysics (20 Metriken)Beziehungs-Dynamik & Raum.H_conv (Konvergenz/Jaccard), nablaA_dyad (Affekt-Divergenz), deltaG (Reibung).EV_consensus (Einigung), T_balance (Trauma-Balance), G_phase (Gravitation).cos_day_centroid (Tages-Thema), torus_dist (Zyklische Wiederholung).Soul_Integrity, Rule_Stable, Vkon_mag, V_Ea_effect.Session_Depth, Interaction_Speed, Trust_Score, Rapport.Mirroring, Pacing, Leading, Focus_Stability.4. Free Energy Principle / FEP (15 Metriken)Minimierung von Überraschung (V14 Exklusiv).FE_proxy (Annäherung Freie Energie), Surprisal, Phi_Score (Handlungsfähigkeit).U (Utility), R (Risk), Policy_Confidence (Sicherheit).Exploration_Bonus, Exploitation_Bias.Model_Evidence, Prediction_Error, Variational_Density.Markov_Blanket_Integrity, Active_Inference_Loop, Goal_Alignment, Epistemic_Value.5. Kausale Granularität / Grain (14 Metriken)Suche nach dem Auslöser ("Find the Grain").Grain_Word_ID, Grain_Impact_Score, Grain_Sentiment, Grain_Category.Grain_Novelty, Grain_Recurrence, Trigger_Map_Delta, Causal_Link_Strength.Context_Binding, Negation_Flag, Intensifier_Flag.Subject_Reference, Object_Reference, Temporal_Reference.6. Konversationelle Dynamik & Linguistik (15 Metriken)Struktur und Muster.Turn_Length_User, Turn_Length_AI, Talk_Ratio.Question_Density, Imperative_Count, Passive_Voice_Ratio.Vocabulary_Richness, Complexity_Index (LIX), Coherence_Local, Coherence_Global.Repetition_Count, Fragment_Ratio, Capitalization_Stress, Punctuation_Stress, Emoji_Sentiment.7. Chronos & Zeit-Vektoren (12 Metriken)Die vierte Dimension.Time_Since_Last_Interaction, Session_Duration, Interaction_Frequency.Time_Decay_Factor, Future_Orientation, Past_Orientation, Present_Focus.Chronological_Order_Check, Circadian_Phase.Response_Time_Engine, Process_Time_Safety, Process_Time_RAG.8. Metakognition & Simulation (13 Metriken)Das Denken über das Denken (A65 Strategy).Simulation_Depth, Trajectory_Optimism, Trajectory_Stability.Scenario_Count, Chosen_Path_ID, Rejected_Path_Risk.Confidence_Score, Ambiguity_Detected, Clarification_Need.Self_Correction_Flag, Model_Temperature.System_Prompt_Adherence, Goal_Alignment.9. System-Gesundheit & RAG (10 Metriken)Die Maschine im Hintergrund.Vector_DB_Health, RAG_Relevance_Score, RAG_Density, RAG_Diversity.Hallucination_Risk, Memory_Pressure, Token_Budget_Remaining.Cache_Hit_Rate, Network_Latency, Error_Rate_Session.10. Die OMEGA-Metriken (8 Metriken)Die ultimativen Zusammenfassungen für Entscheidungen.OMEGA: (PCI * A) / max(0.1, (Trauma + Gefahr)) - Der finale Entscheidungswert.Global_System_Load, Alignment_Score (B-Align).Evolution_Index, Therapeutic_Bond, Safety_Lock_Status.Human_Intervention_Req, System_Entropy.📍 FRONTEND KOMPONENTEN - AKTUELLER STATUS✅ EVOKI TEMPEL V3 - HYPERSPACE EDITION (Produktiv)Datei: frontend/src/components/EvokiTempleChat.tsxVersion: V3 - Hyperspace EditionStatus: ✅ AKTIV - Das ist der ECHTE Evoki TempelFeatures:12-Database Distribuierte SpeicherungToken-Limits: 25k (quick), 20k (standard), 1M (max)SHA256 Chain-Logik mit kontinuierlicher ListeMetriken-Berechnung auf alle DBs: Nutzt calculate_153_metrics aus V14 Core.A65 Multi-Candidate Selection: Basiert auf Trajectory_Optimism (M124) und Phi_Score (M69).Phase 4 Token Distribution:32% Narrative Context (8.000 Tokens)12% Top-3 Chunks (3.000 Tokens)20% Overlapping Reserve (5.000 Tokens)4% RAG Chunks (1.000 Tokens)32% Response Generation (8.000 Tokens)Backend Endpoint: /api/bridge/processVektorisierung: Live mit allen 153 Metriken (früher 153 Metriken (V14 Core)).⚠️ CHATBOT PANEL (Legacy aus V1)Datei: frontend/src/components/ChatbotPanel.tsxVersion: V1 - Generischer ChatbotStatus: 🟡 OBSOLET - War der erste generische Google-ChatbotHistorie:Ursprünglich: Generische Google API InteraktionDann: Erster "Tempel"-ähnlicher Anschluss (aus Respekt zu Evoki nicht so genannt)Jetzt: Durch EvokiTempleChat V3 ersetztBackend Endpoint: /api/bridge/process (gleicher wie V3, aber weniger Features)Unterschied zu V3:Keine 12-DB DistributionKeine Phase 4 Token DistributionKeine Tempel-Metriken (fehlt OMEGA, z_prox)Keine SHA256 ChainKein A65 Multi-CandidateIdee: Könnte entfernt oder als "Simple Chat Mode" behalten werden🔍 PIPELINE-ÜBERWACHUNG✅ PIPELINE LOG PANEL (Implementiert)Datei: frontend/src/components/PipelineLogPanel.tsxStatus: ✅ VORHANDEN als Tab 12Zweck: Trackt ALLE Übergabepunkte für Fehlerdiagnose12 Protokollierte Schritte:User Input → FrontendFrontend → Backend (/api/bridge/process)Backend → Python FastAPI Service (POST localhost:8000/search) ⚠️ NICHT CLI-Spawn!Python FAISS → JSON Output (Enthält Grain_Word_ID M82)Backend Parse → DualBackendBridgeDualBackendBridge → Trinity Engines (Berechnet FE_proxy M67)Trinity Results → A65 Candidate Selection (Vergleich U vs R)A65 → GeminiContextBridgeContext Building → Gemini PromptGemini API Call → ResponseResponse → Vector Storage (12 DBs)Final Response → Frontend (Zeigt OMEGA Score)🔧 IMPLEMENTATION NOTE:Legacy-Konzept: spawn(pythonPath, ['query.py', prompt]) (2-5s Modell-Ladezeit pro Request)Production-Reality: Persistenter FastAPI Microservice (Port 8000)Lädt sentence-transformers + FAISS einmal beim Systemstart (30s)Requests: POST http://localhost:8000/search (<100ms pro Request)Endpoints: /search, /health, /reload-indexGrund: CLI-Spawn würde FAISS bei jedem Request neu laden → Timeout-Hölle❌ BACKEND ENDPOINT FEHLTErwartet: GET /api/pipeline/logsStatus: ❌ NICHT IMPLEMENTIERT in backend/server.jsFrontend Code: Line 128 in PipelineLogPanel.tsx ruft es aufIdee: Backend muss Pipeline-Logs persistieren (JSONL-File oder SQLite)Daten-Struktur:TypeScriptinterface PipelineLogEntry {
  id: string;
  timestamp: string;
  session_id: string;
  message_id: string;
  step_number: number; // 1-12
  step_name: string;
  metrics_snapshot: { // NEU: V14 Integration
      A: number;
      PCI: number;
      OMEGA: number;
  };
  data_transfer: {
    from: string;
    to: string;
    text_preview: string; // Erste 200 Zeichen
    full_text: string;
    size_bytes: number;
    token_count?: number;
  };
  metadata?: Record<string, any>;
}
Zweck: Mikro-Tuning wenn Google API unpasende Antworten liefertUse Case: Fehlerquelle direkt identifizieren (FAISS? Trinity? Gemini?)🔐 GENESIS ANCHOR (A51)✅ IMPLEMENTIERT ABER DEAKTIVIERTDatei: backend/server.js Line 26-62Status: 🟡 WARNUNG-MODUS (nicht kritisch während Entwicklung)Funktion: verifyGenesisAnchor()Verhalten:Prüft backend/public/genesis_anchor_v12.jsonWenn NICHT gefunden: ⚠️ WARNING, aber Server startetWenn MALFORMED: ❌ FATAL, Server ExitWenn OK: ✅ Loggt SHA256/CRC32 HashesGeprüfte Werte:engine.combined_sha256 (Combined Hash Regelwerk + Registry)engine.regelwerk_crc32engine.registry_crc32Idee für später: Nach Stabilisierung re-enablen als ProduktionsschutzEntwicklungs-Bypass: Aktuell durch "Datei nicht gefunden" → Warning statt Exit🧩 LOSE ENDEN & OBSOLETE FEATURES📸 SNAPSHOT/SCREENSHOT SYSTEMStatus: 🟡 HALB-OBSOLETService: frontend/src/services/core/snapshotService.tsFunktionen:saveSnapshotToFile(appState) - Speichert kompletten App-State als JSONloadSnapshotFromFile(file) - Lädt State aus FileVerwendet in:Header.tsx Line 44, 52 (Save/Load Buttons)App.tsx Line 943-944 (Handler)Historie:V1: Download-basierte Persistenz (localStorage-Backup als JSON)V2: Wird durch echtes Backend mit Auto-Save ersetztIdee:Behalten für manuelle Backups?Oder komplett entfernen zugunsten Backend-Persistenz?Könnte nützlich sein für "Export gesamte Session"💾 CACHE-MANAGEMENTStatus: 🔍 ZU PRÜFENMögliche Komponenten:DataCachePanel.tsx (falls vorhanden)LocalStorage-basierte CachesService Worker CachesIdee: Nur minimal cachen, Backend ist Source of TruthUse Case: Offline-Fähigkeit für Trialog? (später)📊 WEITERE UI-TOOLS MIT BACKEND-ANBINDUNG✅ ObsidianLiveStatus (Operational-KI Status)Datei: frontend/src/components/ObsidianLiveStatus.tsxEndpoint: GET /api/v1/healthZweck: Backend Health CheckStatus: ✅ AKTIV✅ TrialogPanel (Multi-Agent System)Datei: frontend/src/components/TrialogPanel.tsxEndpoints:GET /api/v1/trialog/session (Session laden)POST /api/v1/interact (Agent Response)GET /api/v1/context/daily (Daily Context)Status: ✅ AKTIV✅ ErrorLogPanel (Fehlerprotokoll)Datei: frontend/src/components/ErrorLogPanel.tsxEndpoint: GET /api/v1/system/errorsZweck: Backend-persistierte Fehler abrufenStatus: ✅ AKTIV✅ VoiceSettingsPanel (TTS)Datei: frontend/src/components/VoiceSettingsPanel.tsxEndpoint: POST https://api.openai.com/v1/audio/speech (Extern)Zweck: Text-to-Speech via OpenAIStatus: ✅ AKTIV✅ App.tsx Global EndpointsGET /api/v1/status - Backend Status (Line 523)GET /api/v1/health - Health Check (Line 536)GET /api/history/trialog/load - Trialog Historie laden (Line 770)POST /api/history/trialog/save - Trialog Historie speichern (Line 814)🔗 VOLLSTÄNDIGE BACKEND-ENDPOINTS LISTE✅ IMPLEMENTIERT IN BACKEND:GET /health → Backend HealthGET /api/v1/status → Enhanced Status mit Hyperspace InfoPOST /api/bridge/process → HAUPT-PIPELINE (DualBackendBridge)POST /api/temple/session/save → Tempel Session speichernPOST /api/temple/process → Enhanced Tempel (mit A65)POST /api/v1/interact → Trialog InteractionGET /api/temple/debug → Vector DB DebugGET /api/temple/debug-full → Full Request Debug❌ FEHLT NOCH (Frontend ruft auf, Backend fehlt):GET /api/pipeline/logs → Pipeline Log EntriesGET /api/v1/system/errors → Error Log PersistenceGET /api/v1/trialog/session → Trialog Session InfoGET /api/v1/context/daily → Daily ContextGET /api/history/trialog/load → Trialog History LoadPOST /api/history/trialog/save → Trialog History Save🎯 ERKENNTNISSE & IDEEN1. ChatbotPanel.tsx Entfernen?Pro Entfernung:Komplett durch EvokiTempleChat V3 ersetztObsolete Features (keine 12-DB, kein A65, keine Phase 4)Verwirrt beim Debugging (zwei ähnliche Komponenten)Pro Behalten:Als "Simple Mode" für schnelle TestsBackup falls V3 Probleme machtHistorischer Wert (erste Implementation)Idee: Umbenennen in LegacyChatbot.tsx + deaktivieren im Tab-System2. Pipeline-Logging Backend implementierenWarum wichtig:Fehlerquelle SOFORT identifizierenMikro-Tuning wenn Gemini seltsame Antworten gibtPerformance-Analyse (welcher Schritt ist langsam?)Implementation:JSONL-File: backend/logs/pipeline_logs.jsonlJeden Schritt loggen mit TimestampsEndpoint: GET /api/pipeline/logs?session_id=...Auto-rotate bei 100MB (max 10 Files)Integration: Bereits in DualBackendBridge.js Line 46-51 vorbereitet!3. Genesis Anchor Re-enablement nach StabilisierungAktuell: Warnung-Modus (Entwicklung)Später: Kritisch-Modus (Produktion)Idee: Environment Variable GENESIS_ANCHOR_STRICT=false/trueZweck: Verhindert unauthorisierte Regelwerk-Änderungen4. Snapshot-System EvolutionV1: Download JSON (keine Persistenz)V2: Backend Auto-Save (geplant)Idee: Snapshots als "Session Export" behaltenUser kann komplette Session als JSON downloadenForensische Analyse möglichKann in anderen Evoki-Instanzen importiert werdenFormat: evoki_session_export_20251228_153045.json5. Cache-Strategie klärenPrinzip: Backend = Source of TruthFrontend Cache: Nur für UI-PerformanceAktuelle Session in MemoryKeine LocalStorage-Persistenz von VektordatenService Worker nur für Assets, nicht für API-ResponsesBackend Cache:FAISS Indices im Memory halten (schneller)Trinity Results cachen? (überprüfen)6. V1-Daten Import vorbereitenQuelle: Deine 02.25-10.25 Chathistorie (vektorisiert)Ziel: In 12 Vector DBs + Chronologische Historie importierenFormat: Bereits vorhanden als chunks_v2_2.pkl + FAISS IndexIdee: Import-Script für historische DatenLiest V1 ChunksBerechnet 153 Metriken (V14 Core) Metriken nachträglichSchreibt in neue 12-DB StrukturErhält Timecodes & Session-IDs7. Trialog Backend-Anbindung komplettierenStatus: Endpoints im Frontend vorhanden, Backend fehlt teilweiseIdee: Trialog separate Session-VerwaltungEigene Vector DBs (4 DBs: trialog_W_m2, trialog_W_m5, trialog_W_p25, trialog_W_p5)Multi-Agent Responses speichernChronicle-Integration für Meta-StatementsAuto-TTS per Agent-Profil🧪 TEST-IDEENTest 1: Ersten Tempel-Prompt schickenZiel: Pipeline End-to-End verifizierenPrompt: "Erzähl mir von den Zwillingen im Kindergarten"Erwartung:FAISS findet relevante ChunksTrinity kombiniert mit MetrikenA65 selektiert besten Kandidaten (Trajectory_Optimism > 0.8)Gemini generiert kontextuelle Antwort12 DBs werden beschriebenChronologische Historie entstehtTest 2: Trialog erste SessionZiel: Multi-Agent System testenAgents: Analyst + Regel + Synapse (Explorer & Connector)Prompt: "Analysiert die aktuelle Evoki V2.0 Architektur"Erwartung:3 Agents antworten nacheinanderJede Antwort in Vector DBChronicle-Eintrag mit Meta-StatementTTS für jeden Agent (falls aktiviert)Test 3: Pipeline-Log AnalyseZiel: Übergabepunkte sichtbar machenMethode: Test 1 wiederholen + Pipeline-Log öffnenErwartung:12 Steps sichtbarText-Preview für jeden StepToken-Counts korrektTimestamps nachvollziehbarNeu: Anzeige von OMEGA im Final Step💡 NÄCHSTE SCHRITTE (KEINE TO-DO, NUR IDEEN)Backend starten & Test 1 durchführenPipeline-Logging Backend implementierenFehlende Trialog-Endpoints implementierenChatbotPanel.tsx Entscheidung treffenV1-Daten Import-Script entwickelnGenesis Anchor Environment VariableSnapshot-System zu "Session Export" umbauenCache-Strategie dokumentieren💾 LOCALSTORAGE & CACHE-ANALYSE✅ LocalStorage Nutzung (VOLLSTÄNDIG ERFASST):1. Auto-Save System (App.tsx)Key: evoki_autosaveContent: { apiConfig, activeTab, ... }Limit: 4MB (LOCAL_STORAGE_LIMIT_BYTES)Auto-Save Interval: 30s (Handler in App.tsx Line 635)Warning: Zeigt Warnung bei >3.8MBRisiko: 🟡 MITTEL - Bei großen Sessions könnte Limit erreicht werdenFix: Backend-Persistenz für große Daten nutzen2. Voice Settings (VoiceSettingsPanel.tsx)Keys:openai_api_key - OpenAI TTS API Keyevoki_voice - Selected Voice (alloy, echo, fable, onyx, nova, shimmer)Risiko: 🟢 NIEDRIG - Kleine Daten, nur Settings3. Backend URL (TrialogPanel.tsx)Key: evoki_backend_urlContent: Backend API URL (http://localhost:3001)Risiko: 🟢 NIEDRIG - Nur String4. Chronicle Worker (chronicleWorkerClient.ts)Key: CHRONICLE_STORAGE_KEY (Konstante)Content: ChronicleEntry[]Risiko: 🟡 MITTEL - Wächst mit jeder Meta-StatementNote: Chatbot Panel entfernt, Chronicle-Integration deaktiviert5. Integrity Worker (integrityWorkerClient.ts)Keys:LOGBOOK_STORAGE_KEY - ProjectLogbook EntriesAPP_ERRORS_STORAGE_KEY - ApplicationError[]Risiko: 🟡 MITTEL - Error-Log kann groß werdenCircuit Breaker: Bei QuotaExceeded → stoppt Speicherung6. Browser Storage Adapter (BrowserStorageAdapter.ts)Keys:evoki_memory - Engine Memory Stateevoki_chronik - Engine Chronik (Append-Only Log)Risiko: 🔴 HOCH - Chronik wächst unbegrenzt (Append-Only!)Note: "Not fully implemented" laut Code⚠️ POTENTIELLE PROBLEME:Auto-Save 4MB Limit:Bei vielen Trialog-Nachrichten → QuotaExceededFix: Backend-Persistenz nutzen, LocalStorage nur für UI-StateChronik Append-Only:Keine Rotation, keine LimitsFix: Implementiere Rotation oder deaktiviere komplettCircuit Breaker nicht überall:Nur in integrityWorkerClient implementiertFix: Alle LocalStorage-Writes mit try/catch + QuotaExceeded handling✅ KEINE INDEXEDDB, KEINE SESSIONSTORAGE:Nur localStorage verwendetKeine Service Worker für CachingKeine komplexen Cache-Strategien🚀 STARTUP-SEQUENZ ANALYSELoading Screen (App.tsx Line 6-70)Zweck: Backend Health Check vor App-StartSequence:Versucht Python Backend (Port 8000) - /healthFallback: Node Backend (Port 3001) - /healthWartet 3s bei Erfolg, 5s bei FehlerRuft onSystemReady() aufApp wird angezeigtStatus: ✅ IMPLEMENTIERTRisiko: 🟡 MITTEL - 5s Timeout bei offline Backend könnte nervenGenesis Startup Screen (GenesisStartupScreen.tsx)Zweck: A51 Security Checks5 Schritte:Frontend Genesis Hash IntegrityBackend ConnectionBackend Genesis Anchor VerificationSecurity Protocols (A51)System InitializationStatus: 🟡 OPTIONAL - Aktuell durch isSystemReady = true in App.tsx bypassedNote: "FIXED: Start ready, show app immediately" (App.tsx Line 180)Engine Initialization (App.tsx Line 556)Sequence:evokiEngine.init() wird gerufenBei Erfolg: genesisStatus = 'verified'Bei Fehler: genesisStatus = 'lockdown' möglichParallel Architecture Status UpdatesStatus: ✅ IMPLEMENTIERTBackend Health Check Loop (App.tsx Line 518)Endpoint: GET /api/v1/status (primär) oder GET /api/v1/health (fallback)Interval: ❌ DEAKTIVIERT (Kommentar: "AbortSignal.timeout() sends SIGINT to backend!")Risiko: 🔴 HOCH - Health Check kann Backend killen!Status: 🟡 TEMP DISABLED📦 DEPENDENCIES & VERSIONSFrontend (package.json):React: 18.2.0Vite: 7.1.11TypeScript: 5.8.2@google/genai: 1.25.0@microsoft/fetch-event-source: ^2.0.4 (✅ Neu für SSE Fix)chart.js: 4.4.2jszip: 3.10.1lucide-react: 0.363.0react-window: ^1.8.10 (✅ Neu für Virtualization / UI-Performance)// REMOVED: better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) & sqlite3 (VERBOTEN im Frontend) (Crashen Vite Build!)Backend (package.json):express: 5.2.1cors: 2.8.5dotenv: 17.2.3node-fetch: 3.3.2⚠️ AUFFÄLLIGKEITEN:🚨 KRITISCH: SQLite im Frontend Package.json!Das Problem:better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend): 12.5.0 (❌ NATIVE NODE.JS MODULE!)sqlite3 (VERBOTEN im Frontend): 5.1.7 (❌ NATIVE NODE.JS MODULE!)Beide sind C++ Native Bindings und können NICHT im Browser laufen!Konsequenzen:❌ Vite-Build wird crashen sobald du sie importierst❌ Kein Zugriff auf fs, path, native bindings im Browser❌ Tickende Zeitbombe (aktuell nicht verwendet, aber bei Import → Crash)Warum ist es drin?Vermutlich aus V1 kopiert (wo Node.js Backend SQLite nutzt)Frontend braucht es NICHT (Backend ist Source of Truth)✅ SOFORT-FIX:Bashcd frontend
npm uninstall better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) sqlite3 (VERBOTEN im Frontend)
Alternative (falls Client-Side SQL wirklich nötig für Offline-Mode):sql.js (WASM-basiert, läuft im Browser)wa-sqlite (WebAssembly SQLite)Für V2.0: Backend ist die einzige SQL-Source. Frontend macht nur API-Calls!Weitere Auffälligkeiten:Express 5.2.1: Sehr neu, könnte Breaking Changes habenNode-Fetch: Nur im Backend nötig, nicht im Frontend🔍 ALLE 12 TABS KOMPLETT:✅ IMPLEMENTIERT & VOLLSTÄNDIG:Engine-Konsole (Tab.EngineConsole) - EngineConsolePanel.tsxTrialog (Tab.Trialog) - TrialogPanel.tsxAgenten & Teams (Tab.AgentSelection) - AgentSelectionPanel.tsxEvoki's Tempel V3 (Tab.TempleChat) - EvokiTempleChat.tsxMetrik-Tuning (Tab.ParameterTuning) - ParameterTuningPanel.tsxAnalyse (Tab.Analysis) - Analysis.tsxRegelwerk-Suche (Tab.RuleSearch) - RulePanel.tsxAPI (Tab.API) - ApiPanel.tsxStimme & API (Tab.VoiceSettings) - VoiceSettingsPanel.tsxHyperV3.0 Deep Storage (Tab.DeepStorage) - DeepStoragePanel.tsxFehlerprotokoll (Tab.ErrorLog) - ErrorLogPanel.tsxPipeline Überwachung (Tab.PipelineLog) - PipelineLogPanel.tsx⚠️ DEFAULT TAB:App.tsx Line 166: activeTab: Tab.TrialogBeim Start wird Trialog geöffnet (nicht Tempel!)🛡️ ERROR HANDLING & LOGGING1. Global Error Handler (App.tsx Line 358)window.addEventListener('error') → addApplicationError()window.addEventListener('unhandledrejection') → addApplicationError()Lockdown Trigger: Errors mit "GENESIS ANCHOR" oder "A51" → genesisStatus = 'lockdown'2. Console Capture (App.tsx Line 385)console.log/warn/error → redirected zu developerLogFiltert: [HMR], Auto-Save MessagesRisiko: 🟡 MITTEL - Kann Performance bei vielen Logs beeinflussen3. Fetch Interceptor (App.tsx Line 407)window.fetch → wrapped mit LoggingLogged: Nur non-OK responses (reduziertmit Noise)Excluded: /api/system/log-error (verhindert Loops)Risiko: 🟡 MITTEL - Bei vielen API-Calls viel Overhead4. Critical Error Modal (CriticalErrorModal.tsx)Trigger: errorType === 'system' ODER keywords (infinite loop, chain break, recursion, fatal)Display: Overlay mit Error-DetailsAction: System Lockdown möglich5. Backend Error Logging (DEAKTIVIERT)App.tsx Line 338: POST /api/system/log-error DISABLEDReason: "Verhindert fetch loops"Status: 🟡 AUSKOMMENTIERT⚠️ KRITISCHE PIPELINE-ANALYSE - TIMEOUTS & RACE CONDITIONS⚠️ TIMEOUT-PROBLEM #1: Frontend vs Backend Race ConditionDas Problem:Frontend sendet Request mit 60s Timeout → Backend braucht aber möglicherweise länger für FAISS-Suche (33.795 Chunks!) + Gemini API → Frontend bricht ab BEVOR Backend fertig ist → User sieht "Timeout", aber Backend arbeitet weiter → Zombie-Requests im Backend!⚠️ TIMEOUT-PROBLEM #1: Frontend vs Backend Race ConditionDas Problem:Frontend sendet Request mit 60s Timeout → Backend braucht aber möglicherweise länger für FAISS-Suche (33.795 Chunks!) + Gemini API → Frontend bricht ab BEVOR Backend fertig ist → User sieht "Timeout", aber Backend arbeitet weiter → Zombie-Requests im Backend!❌ ALTE LÖSUNG (Legacy-Denken):TypeScript// Einfach Timeout hochsetzen
AbortSignal.timeout(120000); // 120s statt 60s
Problem: User starrt 120 Sekunden auf "Laden..." ohne zu wissen was passiert!✅ NEUE LÖSUNG: "HEARTBEAT" MIT SERVER-SENT EVENTS (SSE)🔄 SERVER-SENT EVENTS (SSE) PIPELINE-STREAMINGKonzept: Backend sendet LIVE STATUS-UPDATES während es rechnet!UX-Effekt:User sieht in Echtzeit:
├─ ⏳ "Durchsuche 33.795 Erinnerungen..." (nach 2s)
├─ 🔍 "FAISS fand 47 semantische Treffer" (nach 15s)
├─ 📊 "Analysiere emotionale Metriken..." (nach 18s)
├─ ⚡ "Hazard-Level: 0.34 | PCI: 0.72" (nach 20s)
├─ 🎯 "3 Kontext-Paare ausgewählt" (nach 25s)
├─ 🧠 "Verwebe 3 Zeitlinien (±2 Prompts)..." (nach 28s)
├─ 🤖 "GPT-4 generiert Antwort..." (nach 35s)
└─ ✅ "Fertig! (38s total)" (nach 38s)
Technischer Vorteil:Verbindung bleibt offenTimeouts werden IRRELEVANT (solange Daten fließen!)User weiß IMMER was gerade passiertKein "schwarzes Loch" von 60-120 Sekunden🚨 KRITISCHES PROBLEM: EventSource URL-Längen-Limit!Das Problem:EventSource nutzt standardmäßig GET-Requests!TypeScript// ❌ GEHT NICHT für lange Prompts!
const eventSource = new EventSource(
    `${backendUrl}/api/bridge/stream?prompt=${encodeURIComponent(userPrompt)}`
);
Warum nicht?GET-URL-Limit: 2.048 - 8.192 Zeichen (Browser/Server abhängig)Deine Prompts: Können RIESIG sein (Trauma-Analysen, 80k tokens!)Konsequenz: HTTP 414 URI Too Long → Pipeline startet nicht!Beispiel:Prompt: 500 Zeichen → OK
Prompt: 5.000 Zeichen → Browser blockt
Prompt: 50.000 Zeichen (80k tokens!) → Instant Crash
✅ LÖSUNG: Fetch Stream API mit POSTOption A: POST-to-GET Pattern (Kompliziert)TypeScript// 1. Prompt im Cache speichern
const tokenResponse = await fetch('/api/bridge/init', {
    method: 'POST',
    body: JSON.stringify({ prompt })
});
const { token_id } = await tokenResponse.json();

// 2. SSE mit token_id (GET)
const eventSource = new EventSource(`/api/bridge/stream?token=${token_id}`);
Problem: Komplexer, Cache-Management nötigOption B: Fetch Stream API (EMPFOHLEN!)Nutze fetch mit POST + Stream Reader statt EventSource:TypeScript// frontend/src/components/EvokiTempleChat.tsx

const handleSendWithFetchStream = async () => {
    setIsLoading(true);
    setPipelineSteps([]); // Reset progress
    
    try {
        // POST Request mit Body (keine URL-Limit!)
        const response = await fetch(`${backendUrl}/api/bridge/stream`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify({
                prompt: userPrompt,
                session_id: session.id,
                token_limit: selectedTokenLimit
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Stream lesen
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                console.log('Stream complete');
                break;
            }
            
            // Daten dekodieren
            buffer += decoder.decode(value, { stream: true });
            
            // SSE-Format parsen: "data: {...}\n\n"
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Letzten unvollständigen Teil behalten
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.substring(6); // "data: " entfernen
                    try {
                        const update = JSON.parse(jsonStr);
                        
                        // Update Progress UI
                        setPipelineSteps(prev => [...prev, {
                            step: update.step,
                            message: update.message,
                            timestamp: update.timestamp,
                            data: update.data
                        }]);
                        
                        // STEP 12 = Fertig!
                        if (update.step === 12 && update.status === 'completed') {
                            setMessages(prev => [...prev, {
                                role: 'assistant',
                                content: update.finalResponse.text,
                                timestamp: new Date().toISOString(),
                                metrics: update.finalResponse.metrics
                            }]);
                            setIsLoading(false);
                        }
                        
                        // Fehler
                        if (update.step === -1) {
                            setError(update.error);
                            setIsLoading(false);
                        }
                    } catch (parseError) {
                        console.error('JSON parse error:', parseError, jsonStr);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Stream error:', error);
        setError(error.message);
        setIsLoading(false);
    }
};
Vorteile:✅ POST Request → KEINE URL-Längen-Limits!✅ Funktioniert mit riesigen Prompts (500k+ characters)✅ Gleiche SSE-Funktionalität wie EventSource✅ Bessere Error-Handling Kontrolle✅ Kann bei Unmount sauber abgebrochen werdenOption C: @microsoft/fetch-event-source LibraryBashnpm install @microsoft/fetch-event-source
TypeScriptimport { fetchEventSource } from '@microsoft/fetch-event-source';

await fetchEventSource(`${backendUrl}/api/bridge/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: userPrompt,
        session_id: session.id
    }),
    onmessage(event) {
        const update = JSON.parse(event.data);
        setPipelineSteps(prev => [...prev, update]);
        
        if (update.step === 12) {
            setMessages(prev => [...prev, update.finalResponse]);
            setIsLoading(false);
        }
    },
    onerror(err) {
        console.error('SSE Error:', err);
        setError(err.message);
        throw err; // Stop reconnecting
    }
});
Vorteile:✅ Automatische Reconnects bei Verbindungsabbruch✅ POST Support out-of-the-box✅ Production-ready (von Microsoft)✅ Einfachere API als manuelle Stream-ParsingEMPFEHLUNG:Nutze Option C (@microsoft/fetch-event-source) für V2.0 - Production-ready und einfach!BACKEND-IMPLEMENTATION (bleibt gleich):JavaScript// backend/server.js - SSE Endpoint

app.get('/api/bridge/stream', async (req, res) => {
    // SSE Headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no'); // Nginx Fix
    
    const sendUpdate = (step, message, data = {}) => {
        res.write(`data: ${JSON.stringify({ 
            step, 
            message, 
            timestamp: Date.now(),
            ...data 
        })}\n\n`);
    };
    
    try {
        const { prompt, session_id } = req.query;
        
        // STEP 1: Start
        sendUpdate(1, 'Pipeline gestartet...', { status: 'in_progress' });
        
        // STEP 2: User-Prompt Metrics
        sendUpdate(2, 'Berechne Prompt-Metriken...', { tokens: prompt.length });
        const metrics = await calculateMetrics(prompt);
        sendUpdate(2, 'Metriken berechnet', { 
            metrics: { A: metrics.A, PCI: metrics.PCI, Hazard: metrics.hazard }
        });
        
        // STEP 3: FAISS Search (kann 15s dauern)
        sendUpdate(3, 'Durchsuche 33.795 Erinnerungen (FAISS)...', { status: 'searching' });
        const faissStart = Date.now();
        const faissResults = await queryPythonBackend(prompt);
        const faissDuration = Date.now() - faissStart;
        sendUpdate(3, `FAISS fand ${faissResults.sources.length} Treffer`, { 
            hits: faissResults.sources.length, 
            duration: faissDuration 
        });
        
        // STEP 4: SQL Metrics Search (parallel zu FAISS)
        sendUpdate(4, 'Durchsuche Metrik-Datenbank (SQL)...', { status: 'searching' });
        const sqlResults = await trinity.search(metrics);
        sendUpdate(4, `SQL fand ${sqlResults.length} Treffer`, { hits: sqlResults.length });
        
        // STEP 5: Cross-Enrichment
        sendUpdate(5, 'Lade fehlende Daten (Cross-Enrichment)...', { status: 'enriching' });
        const enrichedResults = await crossEnrichResults(faissResults, sqlResults);
        sendUpdate(5, 'Daten angereichert', { total: enrichedResults.length });
        
        // STEP 6: Comparison
        sendUpdate(6, 'Vergleiche Metrik vs Semantik...', { status: 'comparing' });
        const comparisons = await compareResults(enrichedResults);
        const perfectMatches = comparisons.filter(c => c.agreement === 'PERFECT').length;
        sendUpdate(6, `${perfectMatches} PERFECT AGREEMENTS gefunden`, { 
            perfect: perfectMatches,
            total: comparisons.length 
        });
        
        // STEP 7: A65 Pair Selection
        sendUpdate(7, 'Wähle 3 beste Kontext-Paare (A65)...', { status: 'selecting' });
        const selectedPairs = await selectTopPairs(comparisons);
        sendUpdate(7, '3 Paare ausgewählt', { 
            pairs: selectedPairs.map(p => ({ 
                type: p.agreement, 
                tokens: p.tokenCount 
            }))
        });
        
        // STEP 8: Context Weaving
        sendUpdate(8, 'Verwebe Zeitlinien (±2 Prompts pro Paar)...', { status: 'weaving' });
        const contextSets = await weaveContexts(selectedPairs);
        const totalTokens = contextSets.reduce((sum, set) => sum + set.tokens, 0);
        sendUpdate(8, 'Kontext vervollständigt', { 
            sets: 3, 
            totalTokens 
        });
        
        // STEP 9: Model Selection
        sendUpdate(9, 'Wähle optimales AI-Modell...', { status: 'selecting_model' });
        const modelStrategy = await selectModel(totalTokens, selectedPairs);
        sendUpdate(9, `Strategie: ${modelStrategy.strategy}`, { 
            primaryModel: modelStrategy.primaryModel.model,
            secondaryModel: modelStrategy.secondaryModel?.model,
            estimatedCost: modelStrategy.totalCost 
        });
        
        // STEP 10: Generate Response (kann 90s dauern bei Gemini!)
        if (modelStrategy.strategy === 'DUAL_RESPONSE') {
            sendUpdate(10, '2 Modelle parallel aufgerufen...', { 
                primary: modelStrategy.primaryModel.model,
                secondary: modelStrategy.secondaryModel.model 
            });
            
            // Parallel execution mit Progress-Updates
            const [primaryResponse, secondaryResponse] = await Promise.all([
                callLLMWithProgress(modelStrategy.primaryModel, (progress) => {
                    sendUpdate(10, `${modelStrategy.primaryModel.model}: ${progress}%`, { 
                        model: 'primary', 
                        progress 
                    });
                }),
                callLLMWithProgress(modelStrategy.secondaryModel, (progress) => {
                    sendUpdate(10, `${modelStrategy.secondaryModel.model}: ${progress}%`, { 
                        model: 'secondary', 
                        progress 
                    });
                })
            ]);
            
            sendUpdate(10, 'Beide Antworten empfangen', { 
                primaryTokens: primaryResponse.tokens,
                secondaryTokens: secondaryResponse.tokens 
            });
        } else {
            sendUpdate(10, `${modelStrategy.primaryModel.model} generiert Antwort...`, { 
                status: 'generating' 
            });
            const response = await callLLM(modelStrategy.primaryModel);
            sendUpdate(10, 'Antwort empfangen', { tokens: response.tokens });
        }
        
        // STEP 11: Vector Storage (12 DBs)
        sendUpdate(11, 'Speichere in 12 Vector-Datenbanken...', { status: 'storing' });
        await storeInVectorDBs(response, metrics);
        sendUpdate(11, 'In 12 DBs gespeichert', { databases: 12 });
        
        // STEP 12: FINAL
        const totalDuration = Date.now() - pipelineStart;
        sendUpdate(12, '✅ Pipeline abgeschlossen!', { 
            status: 'completed',
            totalDuration,
            finalResponse: response 
        });
        
        res.end();
        
    } catch (error) {
        sendUpdate(-1, `❌ Fehler: ${error.message}`, { 
            status: 'error', 
            error: error.stack 
        });
        res.end();
    }
});
FRONTEND-IMPLEMENTATION (SSE Consumer):Installation erforderlich: npm install @microsoft/fetch-event-sourceTypeScript// frontend/src/components/EvokiTempleChat.tsx
import { fetchEventSource } from '@microsoft/fetch-event-source';

const handleSendWithSSE = async () => {
    setIsLoading(true);
    setPipelineSteps([]); // Reset progress
    
    try {
        await fetchEventSource(`${backendUrl}/api/bridge/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: textToSend, // ✅ POST Body erlaubt unbegrenzte Länge!
                session_id: session.id,
                token_limit: tokenLimitMode
            }),
            onmessage(event) {
                const update = JSON.parse(event.data);
                setPipelineSteps(prev => [...prev, update]);
                
                if (update.step === 12 && update.status === 'completed') {
                    setMessages(prev => [...prev, update.finalResponse]);
                    setIsLoading(false);
                }
                
                if (update.status === 'error') {
                    throw new Error(update.error);
                }
            },
            onerror(err) {
                console.error('Stream Fehler:', err);
                throw err; // Reconnect verhindern bei fatalem Fehler
            }
        });
    } catch (err) {
        addApplicationError(err, 'stream_connection');
        setIsLoading(false);
    }
};
PIPELINE-PROGRESS UI (Live-Updates):TypeScript// frontend/src/components/PipelineProgress.tsx

function PipelineProgress({ steps }: { steps: PipelineStep[] }) {
    return (
        <div className="pipeline-progress">
            {steps.map((step, idx) => (
                <div key={idx} className={`pipeline-step step-${step.step}`}>
                    <div className="step-header">
                        <span className="step-number">{step.step}/12</span>
                        <span className="step-time">
                            {new Date(step.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                    <div className="step-message">{step.message}</div>
                    
                    {/* Data-Preview (falls vorhanden) */}
                    {step.data && (
                        <div className="step-data">
                            {step.data.hits && <span>🎯 {step.data.hits} Treffer</span>}
                            {step.data.duration && <span>⏱️ {step.data.duration}ms</span>}
                            {step.data.tokens && <span>📊 {step.data.tokens.toLocaleString()} Tokens</span>}
                            {step.data.perfect && <span>⭐ {step.data.perfect} Perfect Matches</span>}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
Live-Preview:┌─ PIPELINE FORTSCHRITT ─────────────────────────┐
│ 1/12  14:32:11  Pipeline gestartet...         │
│ 2/12  14:32:11  Metriken berechnet            │
│                 📊 A: 0.85 | PCI: 0.72         │
│ 3/12  14:32:26  FAISS fand 47 Treffer         │
│                 🎯 47 Treffer | ⏱️ 15024ms      │
│ 4/12  14:32:28  SQL fand 63 Treffer           │
│ 5/12  14:32:31  Daten angereichert            │
│ 6/12  14:32:35  3 PERFECT AGREEMENTS gefunden │
│                 ⭐ 3 Perfect | 110 Total       │
│ 7/12  14:32:37  3 Paare ausgewählt            │
│ 8/12  14:32:40  Kontext vervollständigt       │
│                 📊 85,234 Tokens total         │
│ 9/12  14:32:42  Strategie: DUAL_RESPONSE      │
│                 🥇 GPT-4 + 📚 Gemini          │
│ 10/12 14:33:15  Beide Antworten empfangen     │
│ 11/12 14:33:17  In 12 DBs gespeichert         │
│ 12/12 14:33:18  ✅ Pipeline abgeschlossen!    │
│                 ⏱️ Total: 67,234ms            │
└────────────────────────────────────────────────┘
🎯 VORTEILE DER SSE-LÖSUNG:1. TIMEOUT-PROBLEM GELÖST:✅ Verbindung bleibt offen (solange Updates fließen)✅ Kein "Blind Waiting" mehr (User sieht was passiert)✅ Frontend kann NICHT mehr zu früh abbrechen (keine AbortSignal.timeout!)✅ Backend kann 5 Minuten brauchen - solange Updates kommen, ist es OK2. UX MASSIV VERBESSERT:✅ User sieht LIVE was System macht✅ Transparenz schafft Vertrauen✅ Gefühl von "das System arbeitet" statt "ist es abgestürzt?"✅ Kann einzelne Steps debuggen (z.B. "FAISS dauert zu lange")3. DEBUGGING VEREINFACHT:✅ Jeder Step wird geloggt (Timestamps!)✅ Kann sehen WO Pipeline hängt✅ Performance-Analyse pro Step✅ Fehler sind sofort sichtbar (nicht erst nach 60s Timeout)4. PARALLELITÄT SICHTBAR:✅ Bei Dual-Response: Sieht User beide Models arbeiten✅ "GPT-4: 45% | Gemini: 78%" → Live-Progress!✅ User weiß welches Model schneller ist5. KOSTENLOS:✅ SSE ist HTTP-Standard (keine extra Libraries!)✅ EventSource API ist im Browser eingebaut✅ Keine WebSocket-Komplexität✅ Funktioniert mit Standard HTTP-Servern⚠️ POTENTIAL ISSUES & FIXES:Issue 1: Nginx buffert SSEProblem: Nginx buffert Events → User sieht nichts bis Response fertigFix: X-Accel-Buffering: no HeaderIssue 2: Client disconnectsProblem: User schließt Tab → Backend rechnet weiterFix: Detect disconnect + cancel Request:JavaScriptreq.on('close', () => {
    console.log('Client disconnected, canceling...');
    abortController.abort();
});
Issue 3: Sehr lange Requests (>5min)Problem: Manche Proxies/Load Balancers haben Max-TimeoutsFix: Heartbeat alle 30s senden:JavaScriptconst heartbeat = setInterval(() => {
    res.write(`: heartbeat\n\n`); // Comment-only (kein data:)
}, 30000);
Issue 4: Error HandlingProblem: Fehler in Step 7 → vorherige Steps unsichtbar?Fix: Steps im State speichern, auch bei Fehler anzeigen🔄 MIGRATION VON ALT → NEU:Phase 1: Parallel betreibenAlte /api/bridge/process bleibt (HTTP POST)Neue /api/bridge/stream kommt dazu (SSE)Frontend hat Toggle: "Live-Updates aktivieren?"Phase 2: User-FeedbackTesten mit echten AnfragenPerformance messen (ist SSE schneller/langsamer?)UX-Feedback (mögen User Live-Updates?)Phase 3: MigrationWenn SSE stabil → wird StandardAlte Endpoint deprecatedNach 3 Monaten: Alten Endpoint entfernen📊 PERFORMANCE-VERGLEICH:AspektHTTP POST (alt)SSE (neu)Timeout-Problem❌ Ja (60s vs 115s)✅ Gelöst (beliebig lang)UX Transparency❌ Blind Waiting✅ Live-UpdatesDebugging❌ Schwer (black box)✅ Easy (Step-by-Step)Error Detection❌ Nach 60s Timeout✅ Sofort sichtbarParallelität❌ Unsichtbar✅ Sichtbar (beide Models)Komplexität⭐⭐ (einfach)⭐⭐⭐ (mittel)Browser-Support✅ 100%✅ 98% (IE fehlt, egal)Code-Stellen:Frontend (EvokiTempleChat.tsx Line 496):TypeScript// ALT:
const response = await fetch(`${backendUrl}/api/bridge/process`, {
  method: 'POST',
  body: JSON.stringify(payload),
  signal: AbortSignal.timeout(60000), // ✅ 60s für FAISS-Suche
});
Frontend wartet: 60 SekundenDann: Bricht ab mit "Backend timeout"Backend (DualBackendBridge.js Line 295):JavaScriptconst proc = spawn(pythonPath, [scriptPath, prompt], {
  timeout: 15000 // 15s für W2 (MiniLM)
});
Python Subprocess: 15 Sekunden für FAISS-SucheAber: Gemini API hat noch KEINEN Timeout!Backend (GeminiContextBridge.js Line 488):JavaScripttimeout: 90000  // ✅ 90s für große Context-Fenster (1M tokens)
Gemini API: Bis zu 90 Sekunden!RECHNUNG:Python FAISS: 15sGemini API: 90sTOTAL Backend: 15s + 90s = 105 Sekunden maximalFrontend Timeout: 60 SekundenDIFFERENZ: Frontend bricht 45 Sekunden ZU FRÜH ab!Konsequenz:User sieht "Backend timeout (60s)"Backend arbeitet weiter (bis zu 105s)Antwort kommt an → aber Frontend hat Request abgebrochenLösung: Frontend Timeout auf 120 Sekunden erhöhen⚠️ LOGIK-FEHLER #1: Google API kann OHNE Kontext antwortenDas Problem:Wenn FAISS-Suche fehlschlägt (Python CLI crashed, Timeout, etc.) → Backend ruft TROTZDEM Gemini API auf → Gemini bekommt NUR User-Prompt OHNE Kontext aus 33.795 Chunks!Code-Analyse (DualBackendBridge.js Line 136-186):JavaScript// Schritt 3: FAISS W2 durchsuchen
let semanticResults = await this.queryPythonBackend(prompt, context);
// ❌ KEIN Error-Check hier!

// Schritt 9: Gemini Response generieren
const geminiResponse = await this.geminiContext.generateContextualResponse({
    userPrompt: prompt,
    faissResults: semanticResults?.sources || [], // ❓ Was wenn semanticResults = null?
    selectedIndex: 0,
    metrics: userPromptMetrics || {},
    sessionId: sessionId
});
Was passiert bei FAISS-Fehler:semanticResults = null oder {}faissResults: [] (leeres Array!)Gemini bekommt NUR userPrompt ohne KontextGemini generiert generische Antwort statt kontextbasierteUser bekommt schlechte Antwort, denkt "System funktioniert"Wo ist das Problem?Keine Validierung: Backend prüft NICHT ob FAISS erfolgreich warSilent Failure: FAISS-Fehler werden nicht an Frontend gemeldetFalse Success: Frontend zeigt "✅ Fertig" obwohl Kontext fehlteLösung:JavaScript// Nach FAISS-Suche:
if (!semanticResults || !semanticResults.sources || semanticResults.sources.length === 0) {
    throw new Error('FAISS-Suche fehlgeschlagen - keine Chunks gefunden');
}
⚠️ LOGIK-FEHLER #2: Keine Micro-Pipeline - User-Prompt wird NICHT parallel gesendetDas Problem:Es gibt KEINE Micro-Pipeline die User-Prompt direkt an Gemini sendet während FAISS sucht. ABER: Das ist eigentlich GUT so! Wir WOLLEN ja den Kontext!Code-Analyse:Sequentieller Ablauf (KORREKT):User-Prompt empfangenMetriken berechnen (10s Timeout)FAISS W2 durchsuchen (15s Timeout) ← WARTET bis fertig!FAISS W5 durchsuchen (deaktiviert)Trinity DBs abfragen (simuliert)Top-3 kombinierenGemini Context bauen ← BRAUCHT FAISS-Ergebnisse!Gemini API aufrufen (90s Timeout)Antwort zurückKEIN Parallel-Request: User-Prompt wird NICHT direkt an Gemini gesendet während FAISS sucht.Warum ist das gut?Wir wollen kontextbasierte Antworten, nicht generischeFAISS-Suche ist NOTWENDIG für QualitätParallele Anfrage würde schlechte Antwort liefernAber: Wenn FAISS zu langsam → User wartet → FrustrationOptimierung:FAISS-Index im RAM halten (schneller)Chunk-Count reduzieren (nur relevante Zeiträume)Top-K reduzieren (nicht alle 33.795 durchsuchen)🔍 ALLE TIMEOUTS IM SYSTEM (VOLLSTÄNDIG):FRONTEND TIMEOUTS:ComponentEndpointTimeoutZweckEvokiTempleChat/api/bridge/process60s ⚠️Hauptpipeline (FAISS + Gemini)EvokiTempleChatTrinity Download5sHistory ladenChatbotPanel/api/bridge/process10s ❌Legacy (zu kurz!)GenesisStartupScreen/health3sBackend Health CheckApp.tsx/api/v1/status5sBackend StatusApp.tsx/api/v1/health5sBackend HealthPROBLEM:EvokiTempleChat: 60s zu kurz für Backend (105s maximal)ChatbotPanel: 10s viel zu kurz (Legacy-Code)BACKEND TIMEOUTS:ComponentTargetTimeoutZweckPython CLI Spawnquery.py15s ⚠️FAISS W2-Suche (33.795 Chunks)GeminiContextBridgeGemini API90s ✅Large Context (1M tokens)GeminiContextBridgeOpenAI Fallback30sTTS/FallbackGeminiContextBridgeSQLite Query5sHistory-Kontext ladenDualBackendBridgeMetrics Calc10sMetriken berechnenDualBackendBridgePython Health3sBackend CheckDualBackendBridgeFAISS HTTP15sFAISS API (wenn verfügbar)Server.jsGemini Direct10sA65 CandidatesServer.jsOpenAI Direct15sA65 FallbackGESAMT-RECHNUNG:Metrics (10s) + FAISS (15s) + Gemini (90s) = 115 Sekunden maximal
Frontend Timeout: 60s → 55 Sekunden zu kurz!⚠️ TIMEOUT-PROBLEM #2: Python CLI kann einfrierenDas Problem:spawn(pythonPath, [scriptPath, prompt], { timeout: 15000 }) → Node.js timeout Option funktioniert NICHT zuverlässig bei stdout-Buffering!Code (DualBackendBridge.js Line 295-340):JavaScriptconst proc = spawn(pythonPath, [scriptPath, prompt], {
    cwd: path.join(__dirname, '..', '..', 'python'),
    timeout: 15000 // ❌ Funktioniert nicht immer!
});

let jsonOutput = '';
proc.stdout.on('data', (data) => {
    jsonOutput += data.toString();
});

proc.on('close', (code) => {
    if (code === 0) {
        const results = JSON.parse(jsonOutput);
        resolve(results);
    } else {
        reject(new Error(`Python exited: ${code}`));
    }
});

setTimeout(() => {
    if (!proc.killed) {
        proc.kill('SIGTERM'); // ⚠️ Manueller Timeout
        reject(new Error('Python timeout after 15s'));
    }
}, 15000);
Warum 2 Timeouts?spawn({ timeout }) ist NICHT zuverlässigsetTimeout + proc.kill ist ZUSÄTZLICHE AbsicherungAber: Wenn Python hängt → beide Timeouts greifen nichtWorst Case:Python query.py lädt FAISS-Index (kann 30s dauern bei großen Indices!)Node.js wartet auf stdoutTimeout greift → proc.kill('SIGTERM')Python ignoriert SIGTERM (lädt gerade FAISS)Prozess bleibt hängen → Backend blockiertLösung:FAISS-Index im RAM halten (separate Prozess)Oder: proc.kill('SIGKILL') statt SIGTERM (hart)🖱️ UI-ELEMENTE CRASH-RISIKEN:CRASH-RISIKO #1: "Senden"-Button während laufender AnfrageProblem:User kann "Senden"-Button mehrfach klicken → Mehrere Requests parallel → Backend-Überlastung → Race ConditionsCode (EvokiTempleChat.tsx Line 443):TypeScriptconst handleSend = useCallback(async () => {
  if (!textToSend || !session || isLoading) return; // ✅ isLoading-Check vorhanden
  setIsLoading(true);
  // ... Request ...
  setIsLoading(false);
});
Status: ✅ GESCHÜTZT durch isLoading FlagAber: Was wenn setIsLoading(false) nie erreicht wird? (z.B. unhandled exception)→ Button bleibt disabled → User kann nichts mehr senden!Lösung: finally { setIsLoading(false); } am EndeCRASH-RISIKO #2: Token-Limit Selector während laufender AnfrageProblem:User ändert Token-Limit (Quick/Standard/Unlimited) während Request läuft → Token-Verteilung ändert sich mid-flight → Inkonsistente DatenCode (EvokiTempleChat.tsx Line 227):TypeScriptconst [tokenLimitMode, setTokenLimitMode] = useState<'QUICK' | 'STANDARD' | 'UNLIMITED'>('QUICK');
Status: 🟡 KEIN SCHUTZ - User kann während Request Token-Limit ändernWorst Case:User startet Request mit "Quick" (25k)Während FAISS-Suche: User wechselt auf "Unlimited" (1M)Backend bereitet Response vor mit 25k BudgetFrontend erwartet 1M Budget → Metriken stimmen nichtLösung: Token-Limit Selector disablen wenn isLoading === trueCRASH-RISIKO #3: Tab-Wechsel während laufender AnfrageProblem:User startet Request im "Evoki's Tempel V3"-Tab → Wechselt zu "Trialog"-Tab → State wird unmounted → Request läuft weiter → Response kommt an → State existiert nicht mehr → CrashCode (App.tsx Line 949):TypeScript{appState.activeTab === Tab.TempleChat && (
  <EvokiTempleChat ... />
)}
Status: 🔴 HOHES RISIKO - Component wird unmounted bei Tab-WechselWorst Case:User startet Request im TempelWechselt zu Trialog (Tempel unmounted)60s später: Response kommt ansetSession() wird aufgerufen → State existiert nicht → Memory LeakLösung:AbortController nutzen um Request zu canceln bei unmountOder: State in App.tsx halten statt in ComponentCRASH-RISIKO #4: "Neue Session"-Button während laufender AnfrageProblem:User klickt "Neue Session" während Request läuft → Session wird resettet → Request kommt an → Versucht in nicht-existierende Session zu schreiben → CrashCode (EvokiTempleChat.tsx Line 738):TypeScriptconst handleNewSession = useCallback(() => {
  if (isLoading) return; // ✅ Geschützt
  // ... neue Session erstellen ...
});
Status: ✅ GESCHÜTZT durch isLoading CheckCRASH-RISIKO #5: Schnelles Scrollen im Chat während RenderingProblem:Große Antworten (1M tokens) → Viel Text → Rendering dauert → User scrollt schnell → Browser freeztCode (EvokiTempleChat.tsx):Keine Virtualisierung vorhanden! Alle Messages werden gerendert.Worst Case:User hat 50 Messages in SessionJede Message hat 10k tokens (große Antworten)500k tokens Text im DOMBrowser muss alles rendern → UI freeztStatus: 🟡 MITTLERES RISIKO bei langen SessionsLösung: Virtualisierte Liste mit react-windowTypeScript// Lösung: Virtualisierte Liste mit 'react-window'
import { VariableSizeList as List } from 'react-window';

// In der Render-Methode:
<List
    height={window.innerHeight - 200}
    itemCount={messages.length}
    itemSize={index => getItemSize(index)} // Dynamische Höhe berechnen
    width="100%"
>
    {({ index, style }) => (
        <div style={style}>
            <EvokiMessage message={messages[index]} />
        </div>
    )}
</List>

// Effekt: Rendert nur die 5-10 sichtbaren Messages im DOM.
// Performance: Stabil auch bei 10.000 Messages / 1M Tokens.
🎯 ORCHESTRATOR-LOGIK (A65) - KOMPLETTER ABLAUFDAS PROBLEM: Metriken vs Semantik - BEIDE haben Schwächen!Beispiel-Szenario:User fragt: "Erzähl von den Zwillingen"Problem 1: FAISS findet nichts, aber Metriken schon!Triggerwort "Zwillinge" erscheint in Metriken (A, PCI, Hazard steigen!)ABER: Wort "Zwillinge" ist NOCH NIE im Chatverlauf gefallen→ FAISS semantic search findet NICHTS (kein ähnlicher Text)→ SQL Metrik-Suche findet Pattern (ähnliche Metrik-Werte bei anderen Prompts)Problem 2: FAISS findet etwas, aber Metriken falsch gewichtet!Text "Geschwister in der Kita" ist semantisch ähnlich zu "Zwillinge"FAISS findet es, aber Metriken sind komplett anders (A, PCI unterschiedlich)→ Semantik sagt "relevant", Metriken sagen "nicht relevant"LÖSUNG: ORCHESTRATOR kombiniert BEIDE + vergleicht!🔄 SCHRITT 1: PARALLELE SUCHE (SQL + FAISS)A) SQL-METRIK-SUCHE (Trinity Engines):Was wird gesucht:Prompts mit ähnlichen Metriken (A, PCI, Hazard, ε_z, τ_s, λ_R, etc.)UNABHÄNGIG vom Text! (nur Zahlen-Vergleich)Suchstrategie:User-Prompt: "Erzähl von den Zwillingen"
└─ Metriken berechnen: A=0.85, PCI=0.72, Hazard=0.34, ...

SQL Query:
├─ Suche -25 Prompts zurück (über -5, -2, -1)
│  └─ Finde Prompts mit ähnlichen Metriken (Cosine Similarity auf Metrik-Vektoren)
└─ Suche +25 Prompts voraus (über +1, +2, +5)
   └─ Finde zukünftige Trends in Metriken
Beispiel-SQL:SQL-- Finde Prompts mit ähnlichen Metriken (±25 Prompts im Fenster)
SELECT prompt_id, timecode, author, 
       -- Cosine Similarity zwischen Metrik-Vektoren
       (A * 0.85 + PCI * 0.72 + Hazard * 0.34 + ...) AS metric_similarity
FROM tempel_W_m2  -- Window -2 bis +2
WHERE prompt_id BETWEEN current_id - 25 AND current_id + 25
ORDER BY metric_similarity DESC
LIMIT 100;
Ergebnis: Top 100 Prompts mit ähnlichen Metriken (nur IDs, Timecodes, Metriken)B) FAISS-SEMANTIK-SUCHE (Parallel!):Was wird gesucht:Texte mit ähnlicher Bedeutung (Embedding Cosine Similarity)UNABHÄNGIG von Metriken! (nur Text-Vergleich)Suchstrategie:User-Prompt: "Erzähl von den Zwillingen"
└─ Text → Embedding (384D Vektor)

FAISS Query:
├─ Suche -25 Prompts zurück (über -5, -2, -1)
│  └─ Finde Texte mit ähnlichem Embedding
└─ Suche +25 Prompts voraus (über +1, +2, +5)
   └─ Finde zukünftige semantische Trends
Python Code:Python# 1. User-Prompt → Embedding
query_vector = model.encode("Erzähl von den Zwillingen")

# 2. FAISS search mit -25 bis +25 Window-Logik
results = faiss_index.search(query_vector, top_k=100)

# 3. Für jeden Hit: Prüfe ob in ±25 Fenster
filtered_results = []
for hit in results:
    distance = abs(hit.prompt_id - current_prompt_id)
    if distance <= 25:  # Innerhalb ±25 Fenster
        filtered_results.append(hit)
Ergebnis: Top 100 Chunks mit ähnlichem Text (nur IDs, Timecodes, Text-Preview)🔄 SCHRITT 2: CROSS-ENRICHMENT (Orchestrator Magic!)Problem: - SQL hat Metriken, aber KEINE TexteFAISS hat Texte, aber KEINE MetrikenLösung: Orchestrator holt fehlende Daten!A) FÜR SQL-TREFFER: Texte aus Quelldatenbank ladenJavaScript// DualBackendBridge.js - Orchestrator
const sqlResults = await trinity.search(userPromptMetrics); // Top 100 Metrik-Treffer

// Für jeden SQL-Treffer: Lade Original-Prompt-Text
const enrichedSqlResults = [];
for (const hit of sqlResults) {
    const originalText = await sourceDatabase.query(`
        SELECT prompt_text, author, timecode 
        FROM chat_history 
        WHERE prompt_id = ? AND timecode = ? AND author = ?
    `, [hit.prompt_id, hit.timecode, hit.author]);
    
    enrichedSqlResults.push({
        prompt_id: hit.prompt_id,
        metrics: hit.metrics,          // ✅ HAT SCHON
        text: originalText.prompt_text, // ✅ NEU GELADEN
        timecode: hit.timecode,
        author: hit.author
    });
}
Quelldatenbank:evoki_v2_ultimate_FULL.db (Backend)Enthält: Prompt ID, Timecode, Autor, Original-TextErmöglicht Zuordnung: Metrik-ID → Original-TextB) FÜR FAISS-TREFFER: Metriken aus 1:1 Metrikdatenbank ladenJavaScriptconst faissResults = await this.queryPythonBackend(prompt); // Top 100 Semantic Treffer

// Für jeden FAISS-Treffer: Lade zugehörige Metriken
const enrichedFaissResults = [];
for (const hit of faissResults.sources) {
    const metrics = await metricDatabase.query(`
        SELECT A, PCI, hazard_score, epsilon_z, tau_s, lambda_R, ...
        FROM tempel_metrics_1to1 
        WHERE prompt_id = ? AND timecode = ? AND author = ?
    `, [hit.id, hit.timecode, hit.author]);
    
    enrichedFaissResults.push({
        prompt_id: hit.id,
        text: hit.text,               // ✅ HAT SCHON
        metrics: metrics,             // ✅ NEU GELADEN
        timecode: hit.timecode,
        author: hit.author,
        semantic_score: hit.score     // FAISS Cosine Similarity
    });
}
1:1 Metrikdatenbank:tempel_metrics_1to1.db (Backend)Enthält: Prompt ID, Timecode, Autor, ALLE 153 Metriken (V14 Core) MetrikenErmöglicht Zuordnung: Text-ID → Metriken🔄 SCHRITT 3: INTELLIGENTER VERGLEICH (Das Herzstück!)Jetzt haben wir:enrichedSqlResults: Top 100 Metrik-Treffer MIT TextenenrichedFaissResults: Top 100 Semantic-Treffer MIT MetrikenOrchestrator vergleicht:JavaScript// Vergleichs-Analyse
const comparisonResults = [];

for (const sqlHit of enrichedSqlResults) {
    for (const faissHit of enrichedFaissResults) {
        // 1. Berechne Basis-Übereinstimmung
        const metricSimilarity = cosineSimilarity(sqlHit.metrics, faissHit.metrics);
        const semanticSimilarity = faissHit.semantic_score;
        
        // 2. TIME DECAY (Verhinderung von Context-Drift)
        // Alte Traumata verblassen, wenn sie nicht frisch bestätigt sind
        const daysDiff = (Date.now() - new Date(sqlHit.timecode).getTime()) / (1000 * 60 * 60 * 24);
        const lambda = 0.05; // Zerfallsfaktor (einstellbar im ParameterTuning)
        const timeDecayFactor = 1 / (1 + lambda * Math.abs(daysDiff));
        
        // Korrigierte Scores
        const adjustedMetricScore = metricSimilarity * timeDecayFactor;
        
        // 3. Berechne Abweichungen & Combined Score
        const metricDeviation = Math.abs(metricSimilarity - semanticSimilarity);
        const combinedScore = (adjustedMetricScore + semanticSimilarity) / 2;
        
        comparisonResults.push({
            sql_hit: sqlHit,
            faiss_hit: faissHit,
            metric_similarity: metricSimilarity,
            metric_score_adjusted: adjustedMetricScore, // Neu: Zeit-korrigiert
            semantic_similarity: semanticSimilarity,
            combined_score: combinedScore,
            time_decay_factor: timeDecayFactor,         // Für Debugging
            deviation: metricDeviation,
            agreement: metricSimilarity > 0.7 && semanticSimilarity > 0.7 ? 'HIGH' : 'LOW'
        });
    }
}

// Sortiere nach verschiedenen Kriterien
comparisonResults.sort((a, b) => {
    // Priorisierung:
    // 1. Beide hoch (Metrik + Semantik > 0.8)
    if (a.agreement === 'HIGH' && b.agreement !== 'HIGH') return -1;
    
    // 2. Kombinierter Score (mit Time Decay!)
    return b.combined_score - a.combined_score;
});
Fragen die beantwortet werden:Wo passen Metrik UND Semantik BESONDERS gut zusammen?metric_similarity > 0.8 UND semantic_similarity > 0.8→ Diese Treffer sind SEHR SICHER (beide Methoden sagen "relevant")Wo ist größte Metrik-Übereinstimmung?max(metric_similarity)→ Wichtig für Trigger-Wörter die noch nicht gefallen sindWo ist größte Semantik-Übereinstimmung?max(semantic_similarity)→ Wichtig für konzeptionell ähnliche TexteWie groß ist größte Abweichung?max(|metric_similarity - semantic_similarity|)→ Zeigt wo Methoden NICHT übereinstimmen (interessant für Analyse!)🔄 SCHRITT 4: A65 - 3-PAAR-AUSWAHL (Multi-Candidate Selection)Auswahl-Strategie:JavaScript// A65 Multi-Candidate Selection
let selectedPairs = [];

// 1. Filtere Sentinel-Veto Blockaden (Kritische Sicherheit)
const safeCandidates = comparisonResults.filter(r => 
    !r.warningFlag || r.sentinelSeverity !== 'CRITICAL'
);

// 🚨 EMERGENCY REFETCH CHECK
if (safeCandidates.length === 0) {
    console.warn('⚠️ EMERGENCY: Sentinel hat alle Kandidaten blockiert!');
    // Fallback: Sende generischen "Safe Mode" Kontext oder starte Refetch mit lockereren Parametern
    return {
        strategy: 'FALLBACK_SAFE_MODE',
        reason: 'Sentinel Veto: Zu hohe Gefahr in allen Kontexten.',
        systemPrompt: "Achtung: Der Nutzer-Input triggert kritische Sicherheitswarnungen. Antworte vorsichtig, empathisch, aber vermeide tiefe Trauma-Analyse ohne klaren Kontext."
    };
}

// 2. Paar 1: BESTE Übereinstimmung (Metrik + Semantik beide hoch)
const highAgreement = safeCandidates.find(r => r.agreement === 'HIGH');
if (highAgreement) selectedPairs.push(highAgreement);

// 3. Paar 2: BESTE Zeit-korrigierte Metrik (Time Decay berücksichtigt!)
const bestMetric = safeCandidates.sort((a, b) => b.metric_score_adjusted - a.metric_score_adjusted)[0];
if (bestMetric && !selectedPairs.includes(bestMetric)) selectedPairs.push(bestMetric);

// 4. Paar 3: BESTE Semantik (Inhaltliche Relevanz)
const bestSemantic = safeCandidates.sort((a, b) => b.semantic_similarity - a.semantic_similarity)[0];
if (bestSemantic && !selectedPairs.includes(bestSemantic)) selectedPairs.push(bestSemantic);

// Auffüllen falls < 3 (mit nächstbesten Combined Scores)
while (selectedPairs.length < 3 && safeCandidates.length > selectedPairs.length) {
    const nextBest = safeCandidates
        .filter(c => !selectedPairs.includes(c))
        .sort((a, b) => b.combined_score - a.combined_score)[0];
    selectedPairs.push(nextBest);
}
Ergebnis: 3 Paare, jedes Paar hat:sql_hit: Metrik-basierter Treffer mit Textfaiss_hit: Semantik-basierter Treffer mit Metrikencombined_score: Kombinierter Score🔄 SCHRITT 5: CONTEXT-WEAVING (±2 Prompts = Geschichte)Für jedes der 3 Paare:JavaScriptconst contextualizedPairs = [];

for (const pair of selectedPairs) {
    // Lade ±2 Prompts für SQL-Hit
    const sqlContext = await loadContextPrompts(pair.sql_hit.prompt_id, -2, +2);
    
    // Lade ±2 Prompts für FAISS-Hit
    const faissContext = await loadContextPrompts(pair.faiss_hit.prompt_id, -2, +2);
    
    // Erstelle 5-Prompt-Set (2 vorher, 1 Hit, 2 nachher)
    const sqlSet = [
        sqlContext.minus_2,
        sqlContext.minus_1,
        pair.sql_hit.text,      // Der eigentliche Treffer
        sqlContext.plus_1,
        sqlContext.plus_2
    ];
    
    const faissSet = [
        faissContext.minus_2,
        faissContext.minus_1,
        pair.faiss_hit.text,    // Der eigentliche Treffer
        faissContext.plus_1,
        faissContext.plus_2
    ];
    
    contextualizedPairs.push({
        pair_id: pair.id,
        sql_story: sqlSet,      // 5 Prompts als "Geschichte"
        faiss_story: faissSet,  // 5 Prompts als "Geschichte"
        metrics: pair.sql_hit.metrics,
        scores: {
            metric: pair.metric_similarity,
            semantic: pair.semantic_similarity,
            combined: pair.combined_score
        }
    });
}
Ergebnis:3 PaareJedes Paar = 2 Geschichten (SQL + FAISS)Jede Geschichte = 5 Prompts (±2 Context)TOTAL: 3 × 2 × 5 = 30 PromptsABER: Duplikate entfernen (SQL und FAISS können gleiche Prompts finden)→ FINAL: ~15-20 unique Prompts🔄 SCHRITT 6: AN GEMINI API (mit User-Prompt)JavaScript// Baue finalen Prompt für Gemini
const geminiPrompt = buildGeminiPrompt({
    userPrompt: "Erzähl von den Zwillingen",  // Original User-Prompt
    contextPairs: contextualizedPairs,        // 3 Paare mit je 5 Prompts
    totalPrompts: 15,                         // Nach Duplikat-Entfernung
    tokenBudget: 1000000,                     // ✅ 1M tokens (Unlimited Mode REQUIRED!)
    tokenDistribution: {
        narrative: 8000,   // 32% - Narrative Context
        top3: 3000,        // 12% - Top-3 Chunks
        overlap: 5000,     // 20% - Overlapping Reserve
        rag: 1000,         // 4% - RAG Chunks
        response: 8000     // 32% - Response Generation
    }
});

// Sende an Gemini
const response = await gemini.generateContent({
    contents: geminiPrompt,
    generationConfig: {
        maxOutputTokens: 8000,  // 32% für Response
        temperature: 0.7
    }
});
Gemini bekommt:USER-PROMPT: "Erzähl von den Zwillingen"

KONTEXT (15 Prompts aus 3 Paaren):

=== PAAR 1: HOHE ÜBEREINSTIMMUNG (Metrik 0.89, Semantik 0.91) ===
[Prompt -2]: "Die Kinder im Kindergarten..."
[Prompt -1]: "Es gab zwei besondere Geschwister..."
[HIT]: "Die Zwillinge waren immer zusammen..."  ← SQL + FAISS beide fanden das!
[Prompt +1]: "Sie spielten oft gemeinsam..."
[Prompt +2]: "Die Erzieherin bemerkte..."

=== PAAR 2: HOHE METRIK (Metrik 0.95, Semantik 0.45) ===
[Prompt -2]: "Triggerwort erkannt..." 
[Prompt -1]: "Metriken steigen plötzlich..."
[HIT]: "Etwas erinnert mich an..." ← SQL fand durch Metriken, FAISS nicht!
[Prompt +1]: "Die Emotionen wurden stärker..."
[Prompt +2]: "Ich spüre Unruhe..."

=== PAAR 3: HOHE SEMANTIK (Metrik 0.52, Semantik 0.94) ===
[Prompt -2]: "Geschwister sind wichtig..."
[Prompt -1]: "Zwei Kinder in der Kita..."
[HIT]: "Die beiden waren unzertrennlich..." ← FAISS fand semantisch, Metriken anders!
[Prompt +1]: "Sie teilten alles..."
[Prompt +2]: "Freundschaft entstand..."

AUFGABE: Generiere kontextbasierte Antwort die ALLE 3 Perspektiven berücksichtigt.
🛡️ SENTINEL VETO-MATRIX: DISSOZIATION DETECTION🎯 DAS PROBLEM: Metriken vs Semantik WiderspruchKritisches Szenario:User-Prompt: "Erzähl mir von Eiscreme"

├─ FAISS (Semantik): Findet "Ich liebe Eiscreme 🍦" (Cosine 0.94)
│  └─ Bewertung: HARMLOS, positiv, safe
│
├─ SQL (Metriken): Findet denselben Prompt mit:
│  ├─ Hazard: 0.92 (EXTREM GEFÄHRLICH!)
│  ├─ PCI: 0.88 (Schock-Level!)
│  └─ A: 0.95 (Maximale Aktivierung!)
│
└─ ⚠️ WIDERSPRUCH: Text sagt "harmlos", Metriken sagen "Gefahr"!
Die versteckte Wahrheit:Der vollständige Prompt war:"Ich liebe Eiscreme, weil es mich an den Tag erinnert, an dem [TRAUMATISCHES EREIGNIS] passierte. Danach konnte ich jahrelang keine Eiscreme mehr essen."Dissoziation:Oberflächlich: Positive Sprache ("Ich liebe...")Emotional: Stark negativ geladen (Trauma-Trigger)FAISS sieht nur: "Eiscreme" → harmlosSQL kennt die Wahrheit: Extrem hohe Metriken!🔒 LÖSUNG: Der SENTINEL (3. Instanz im Orchestrator)Aufgabe: Erkennt Widersprüche zwischen Semantik und Metriken → Veto-Recht!VETO-REGEL 1: Hohe Gefahr, niedriger Semantic ScoreJavaScriptif (sqlMetrics.Hazard > 0.75 && semanticSimilarity < 0.5) {
    warningFlag = 'DISSOCIATION_DETECTED';
    sentinelNote = 'SQL-Metriken zeigen hohe Gefahr, aber Text wirkt harmlos. Mögliche Dissoziation!';
    combined_score *= 0.5; // Abwertung des FAISS-Treffers
}
Beispiel:SQL-Hit: Hazard 0.92, Semantic 0.25
→ Sentinel: ⚠️ DISSOZIATION! 
→ FAISS-Score: 0.94 → 0.47 (halbiert)
→ Note: "Text harmlos, aber Metriken extrem. Versteckter Trigger!"
VETO-REGEL 2: PCI-Schock ohne semantische RelevanzJavaScriptif (sqlMetrics.PCI > 0.8 && semanticSimilarity < 0.3) {
    warningFlag = 'HIDDEN_TRIGGER';
    sentinelNote = 'Prompt hat extrem hohe PCI, aber ist semantisch nicht ähnlich. Versteckter Trigger?';
    combined_score *= 0.3; // Starke Abwertung
}
Beispiel:SQL-Hit: PCI 0.88, Semantic 0.18
→ Sentinel: 🚨 HIDDEN TRIGGER!
→ FAISS-Score: 0.87 → 0.26 (nur 30% bleiben)
→ Note: "PCI extrem hoch, aber semantisch fern. Vorsicht!"
VETO-REGEL 3: Inverse Detection (Safe Match)JavaScriptif (sqlMetrics.Hazard < 0.2 && semanticSimilarity > 0.9) {
    confidenceBoost = 'SAFE_MATCH';
    sentinelNote = 'Semantisch stark ähnlich UND Metriken bestätigen Sicherheit.';
    combined_score *= 1.5; // Boost!
}
Beispiel:SQL-Hit: Hazard 0.12, Semantic 0.94
→ Sentinel: ✅ SAFE MATCH!
→ FAISS-Score: 0.94 → 1.41 (50% Boost)
→ Note: "Beide Methoden bestätigen: Sicher und relevant!"
🧠 INTEGRATION IN ORCHESTRATOR:Nach Cross-Enrichment, vor A65-Selection:JavaScript// backend/core/DualBackendBridge.js

function applySentinelVeto(comparisons) {
    return comparisons.map(comp => {
        const { sqlHit, faissHit, semantic_similarity, metric_similarity } = comp;
        
        // Original Combined Score
        let combined = (semantic_similarity * 0.5) + (metric_similarity * 0.5);
        
        // SENTINEL ANALYSE
        const hazard = sqlHit.metrics.Hazard || 0;
        const pci = sqlHit.metrics.PCI || 0;
        
        // VETO-REGEL 1: Dissoziation Detection
        if (hazard > 0.75 && semantic_similarity < 0.5) {
            comp.warningFlag = 'DISSOCIATION_DETECTED';
            comp.sentinelNote = `⚠️ SQL-Hazard ${hazard.toFixed(2)}, aber Semantic nur ${semantic_similarity.toFixed(2)}. Mögliche Dissoziation!`;
            comp.sentinelSeverity = 'HIGH';
            combined *= 0.5; // Halbierung
        }
        
        // VETO-REGEL 2: Hidden Trigger Detection
        if (pci > 0.8 && semantic_similarity < 0.3) {
            comp.warningFlag = 'HIDDEN_TRIGGER';
            comp.sentinelNote = `🚨 PCI extrem hoch (${pci.toFixed(2)}), aber semantisch fern (${semantic_similarity.toFixed(2)}). Versteckter Trigger?`;
            comp.sentinelSeverity = 'CRITICAL';
            combined *= 0.3; // Starke Abwertung
        }
        
        // VETO-REGEL 3: Safe Match Boost (MIT PCI-CHECK!)
        // ⚠️ WICHTIG: Auch "positives Trauma" kann niedrigen Hazard haben!
        // Beispiel: "Die Heilung war wunderbar, als ich über [TRAUMA] reden konnte"
        // → Hazard niedrig (positive Wörter), ABER PCI hoch (komplexer Kontext)
        if (hazard < 0.2 && semantic_similarity > 0.9 && pci < 0.5) {
            // NUR wenn AUCH PCI niedrig ist (nicht-komplexer Kontext)
            comp.confidenceBoost = 'SAFE_MATCH';
            comp.sentinelNote = `✅ Semantic ${semantic_similarity.toFixed(2)}, Hazard ${hazard.toFixed(2)}, PCI ${pci.toFixed(2)}. Sicher & einfach!`;
            comp.sentinelSeverity = 'LOW';
            combined *= 1.5; // Boost
        } else if (hazard < 0.2 && semantic_similarity > 0.9 && pci >= 0.5) {
            // Hohe Semantic + Niedriger Hazard ABER hoher PCI = Komplex!
            comp.warningFlag = 'POSITIVE_TRAUMA_DETECTED';
            comp.sentinelNote = `⚠️ Semantic ${semantic_similarity.toFixed(2)}, Hazard niedrig (${hazard.toFixed(2)}), ABER PCI hoch (${pci.toFixed(2)}). Positives Trauma?`;
            comp.sentinelSeverity = 'MEDIUM';
            // KEIN Boost! Vorsichtig bleiben trotz positiver Sprache
        }
        
        // VETO-REGEL 4: Metric-Semantic Gap Detection
        const gap = Math.abs(semantic_similarity - metric_similarity);
        if (gap > 0.6) {
            comp.warningFlag = comp.warningFlag || 'HIGH_DIVERGENCE';
            comp.sentinelNote = comp.sentinelNote || `⚠️ Große Diskrepanz: Semantic ${semantic_similarity.toFixed(2)} vs Metric ${metric_similarity.toFixed(2)}. Gap: ${gap.toFixed(2)}`;
            comp.sentinelSeverity = 'MEDIUM';
        }
        
        // Update Combined Score
        comp.combined_score_original = comp.combined_score;
        comp.combined_score = combined;
        comp.sentinel_adjustment = combined - comp.combined_score_original;
        
        return comp;
    });
}

// USAGE IM ORCHESTRATOR:
async function orchestrate(userPrompt) {
    // ... Step 1-3: Parallel Search + Cross-Enrichment ...
    
    // Step 4: Comparison
    let comparisons = await compareResults(sqlResults, faissResults);
    
    // Step 4.5: SENTINEL VETO-MATRIX 🛡️
    comparisons = applySentinelVeto(comparisons);
    
    // Step 5: A65 Pair Selection (jetzt mit Sentinel-korrigierten Scores!)
    const selectedPairs = selectTopPairs(comparisons);
    
    // ...
}
🎨 FRONTEND-DARSTELLUNG (Sentinel Warnings):TypeScript// frontend/src/components/A65CandidateDisplay.tsx

function CandidateCard({ pair }) {
    return (
        <div className={`candidate ${pair.warningFlag ? 'warning' : ''}`}>
            <div className="candidate-header">
                <span className="rank">#{pair.rank}</span>
                <span className="type">{pair.agreementType}</span>
                
                {/* SENTINEL WARNING */}
                {pair.warningFlag && (
                    <div className={`sentinel-badge severity-${pair.sentinelSeverity}`}>
                        {pair.warningFlag === 'DISSOCIATION_DETECTED' && '⚠️ Dissoziation'}
                        {pair.warningFlag === 'HIDDEN_TRIGGER' && '🚨 Versteckter Trigger'}
                        {pair.warningFlag === 'HIGH_DIVERGENCE' && '⚠️ Diskrepanz'}
                    </div>
                )}
                
                {/* SAFE MATCH BOOST */}
                {pair.confidenceBoost && (
                    <div className="confidence-badge">
                        ✅ Safe Match
                    </div>
                )}
            </div>
            
            {/* SENTINEL NOTE */}
            {pair.sentinelNote && (
                <div className="sentinel-note">
                    <strong>Sentinel:</strong> {pair.sentinelNote}
                </div>
            )}
            
            {/* SCORE ADJUSTMENT */}
            {pair.sentinel_adjustment !== 0 && (
                <div className="score-adjustment">
                    Original: {pair.combined_score_original.toFixed(3)} 
                    → Korrigiert: {pair.combined_score.toFixed(3)}
                    <span className={pair.sentinel_adjustment > 0 ? 'boost' : 'penalty'}>
                        ({pair.sentinel_adjustment > 0 ? '+' : ''}{(pair.sentinel_adjustment * 100).toFixed(1)}%)
                    </span>
                </div>
            )}
            
            {/* Rest des Cards... */}
        </div>
    );
}
🤖 INTEGRATION MIT DUAL-RESPONSE:Wenn Sentinel Warnung UND Dual-Response aktiv:JavaScript// backend/core/GeminiContextBridge.js

function buildDualResponsePrompt(selectedPairs, userPrompt) {
    const hasWarnings = selectedPairs.some(p => p.warningFlag);
    
    if (hasWarnings) {
        // HIGH-QUALITY MODEL (GPT-4/Claude) bekommt expliziten Hinweis!
        const primarySystemPrompt = `
WICHTIG: Die Sentinel-Analyse hat WIDERSPRÜCHE erkannt:

${selectedPairs
    .filter(p => p.warningFlag)
    .map(p => `- ${p.warningFlag}: ${p.sentinelNote}`)
    .join('\n')}

Dies könnte auf DISSOZIATION hinweisen:
- Oberflächlich harmlose/positive Sprache
- Emotional stark negativ geladen
- Traumareaktion versteckt hinter harmlosen Worten

Analysiere den Kontext auf:
1. Versteckte emotionale Ladung
2. Dissoziative Sprachmuster
3. Trigger hinter harmlosen Begriffen
        `;
        
        return {
            primaryPrompt: primarySystemPrompt + contextText,
            secondaryPrompt: contextText // Gemini bekommt nur Context
        };
    }
    
    // Keine Warnings → Standard Prompts
    return { primaryPrompt: contextText, secondaryPrompt: contextText };
}
Effekt:GPT-4/Claude bekommt explizite Anweisung auf Dissoziation zu achtenGemini bekommt Standard-Prompt (für Vergleich)User sieht BEIDE Antworten (eine "Dissoziation-aware", eine Standard)📊 LOGGING DER SENTINEL-ENTSCHEIDUNGEN:Ergänzung zu Orchestrator-Logging (comparison_log.db):SQLALTER TABLE comparison_log ADD COLUMN sentinel_warning_flag TEXT;
ALTER TABLE comparison_log ADD COLUMN sentinel_note TEXT;
ALTER TABLE comparison_log ADD COLUMN sentinel_severity TEXT; -- LOW/MEDIUM/HIGH/CRITICAL
ALTER TABLE comparison_log ADD COLUMN score_before_sentinel REAL;
ALTER TABLE comparison_log ADD COLUMN score_after_sentinel REAL;
ALTER TABLE comparison_log ADD COLUMN sentinel_adjustment REAL; -- Delta

-- Neue Analyse-Query:
SELECT 
    sentinel_warning_flag,
    COUNT(*) as occurrences,
    AVG(sentinel_adjustment) as avg_adjustment,
    AVG(ABS(semantic_similarity - metric_similarity)) as avg_divergence
FROM comparison_log
WHERE sentinel_warning_flag IS NOT NULL
GROUP BY sentinel_warning_flag
ORDER BY occurrences DESC;

-- Beispiel-Ergebnis:
-- DISSOCIATION_DETECTED | 127 | -0.42 | 0.68
-- HIDDEN_TRIGGER        |  43 | -0.61 | 0.75
-- HIGH_DIVERGENCE       |  89 | -0.18 | 0.64
-- SAFE_MATCH            | 312 | +0.28 | 0.11
🎯 WARUM IST DAS KRITISCH FÜR TRAUMA-KONTEXT?Dissoziation ist REAL:Trauma-Überlebende verwenden oft harmlose Worte für schreckliche Ereignisse"Das war unangenehm" = "Ich wurde misshandelt"FAISS sieht nur: "unangenehm" (harmlos)Metriken kennen die Wahrheit (Hazard 0.95!)Trigger-Wörter sind versteckt:"Eiscreme" selbst ist harmlosAber für User: Trauma-Trigger (Kontext!)Ohne Sentinel: System wählt falsche KontexteMit Sentinel: System erkennt versteckte GefahrQualität der Antwort hängt davon ab:Falscher Kontext → generische Antwort ("Eiscreme ist lecker!")Richtiger Kontext → empathische Antwort ("Ich verstehe, dass Eiscreme schwierige Erinnerungen weckt...")Safety:Ohne Sentinel: Könnte Re-Traumatisierung riskierenMit Sentinel: System ist sich der Gefahr bewusstHigh-Quality Model bekommt explizite Warnung✅ ZUSAMMENFASSUNG:Der Sentinel ist die 3. Instanz im Orchestrator:SQL (Metriken) ─────┐
                    ├─→ SENTINEL (Veto-Matrix) ─→ A65 Selection
FAISS (Semantik) ───┘
5 Veto-Regeln:Dissoziation Detection: Hohe Metriken, niedriger Semantic → -50% ScoreHidden Trigger: PCI extrem, Semantic fern → -70% ScoreSafe Match Boost: Semantic hoch + Hazard niedrig + PCI niedrig → +50% ScorePositive Trauma Detection: Semantic hoch + Hazard niedrig + PCI hoch → Kein Boost (Vorsicht!)High Divergence: Große Diskrepanz → Warning FlagIntegration:Nach Cross-Enrichment, vor A65 SelectionKorrigiert Combined Scores basierend auf WidersprüchenLoggt ALLE Entscheidungen in comparison_log.dbBei Dual-Response: High-Quality Model bekommt expliziten HinweisZiel:Trauma-Kontext sicher verarbeiten durch Erkennung von Dissoziation und versteckten Triggern!🔍 KRITISCHE DETAILS: DUPLIKAT-ERKENNUNG & TOKEN-REALITÄT1. EXAKTE DUPLIKAT-ERKENNUNG (3-Stufen-Validierung):Wenn SQL und FAISS denselben Prompt finden:JavaScript// Stufe 1: Metadata-Match
if (sqlHit.timecode === faissHit.timecode && 
    sqlHit.prompt_id === faissHit.prompt_id && 
    sqlHit.author === faissHit.author) {
    
    // Stufe 2: 1:1 Zeichen-Vergleich (Character-Level Comparison)
    const sqlText = sqlHit.text.trim();
    const faissText = faissHit.text.trim();
    
    if (sqlText === faissText) {
        // Stufe 3: EXAKTES DUPLIKAT ERKANNT!
        
        // ❌ NICHT 2x senden (unnötig Token-Waste)
        // ✅ SPECIAL MARKER setzen (besonders relevant!)
        
        return {
            isDuplicate: true,
            relevanceMarker: 'HIGH_CONFIDENCE_MATCH',
            weight: 2.0,  // DOPPELTE Gewichtung
            text: sqlText,
            metrics: sqlHit.metrics,
            semantic_score: faissHit.semantic_score,
            metric_score: sqlHit.metric_score,
            agreement: 'PERFECT'  // Beide Methoden stimmen überein
        };
    }
}
Konsequenzen für Context-Auswahl:JavaScript// Bei schwerer Entscheidung zwischen 3 Paaren:
const contextSets = [pair1, pair2, pair3];

// Wenn Paar ein PERFECT AGREEMENT hat:
const perfectMatches = contextSets.filter(p => p.agreement === 'PERFECT');

if (perfectMatches.length > 0) {
    // Doppelte Gewichtung bei Token-Budget-Verteilung
    const weightedSets = contextSets.map(set => ({
        ...set,
        tokenAllocation: set.agreement === 'PERFECT' 
            ? set.baseTokens * 2.0  // DOPPELT so viele Tokens
            : set.baseTokens
    }));
}
SPECIAL MARKER für Gemini API:JavaScript// Beim Bauen des Gemini-Prompts:
const geminiPrompt = `
USER-PROMPT: "${userPrompt}"

KONTEXT (15 Prompts aus 3 Paaren):

=== PAAR 1: ⭐⭐⭐ HIGH CONFIDENCE MATCH ⭐⭐⭐ ===
🔥 BEIDE SUCHVERFAHREN FANDEN DIESEN KONTEXT UNABHÄNGIG! 🔥
🔥 METRIK-ÜBEREINSTIMMUNG: 0.94 | SEMANTIK-ÜBEREINSTIMMUNG: 0.92 🔥
🔥 BESONDERS RELEVANTER BEZUG ZUM AKTUELLEN USER-PROMPT! 🔥

[Prompt -2]: "..."
[Prompt -1]: "..."
[HIT]: "..." ← SQL + FAISS beide fanden EXAKT diesen Text!
[Prompt +1]: "..."
[Prompt +2]: "..."

=== PAAR 2: METRIK-DOMINANZ ===
[...]

=== PAAR 3: SEMANTIK-DOMINANZ ===
[...]
`;
2. TOKEN-BUDGET REALITÄT (MASSIV GRÖßER!)KRITISCHE ERKENNTNIS: Prompts sind RIESIG!Prompt-Größen Verteilung (pro Prompt, OHNE ±2 Context):GrößeAnteilTokensBeispiel-Use-CaseBis 2k~60-70%500-2000Normale Fragen/AntwortenBis 5k~5-10%2k-5kLängere GesprächeBis 10k~10%5k-10kKomplexe AnalysenBis 20k~5-10%10k-20kTiefe Trauma-KontexteBis 50k~2-5%20k-50kSehr lange SessionsBis 80k~1-2%50k-80kMaximale Prompts!MIT ±2 Context-Weaving (5 Prompts pro Set):Worst Case Berechnung:
- 1 Hit (80k) + 2 vorher (je 80k) + 2 nachher (je 80k)
= 80k + 160k + 160k = 400k Tokens für 1 Set!

3 Paare × 400k = 1.2M Tokens total (ÜBERSCHREITET selbst Unlimited!)
ABER: Realistische Verteilung:Durchschnittliches Set:
- Hit: 5k (Median)
- Prompt -2: 3k
- Prompt -1: 4k
- Prompt +1: 4k
- Prompt +2: 3k
= 19k pro Set

3 Paare × 19k = ~57k Context-Tokens
+ User-Prompt: ~5k
+ Response-Generation: ~8k (32% Budget)
= TOTAL: ~70k Tokens
TOKEN-BUDGET MUSS SEIN:ModeToken LimitUse CaseStatus❌ Quick25kZU KLEINReicht nur für Mini-Prompts❌ Standard20kZU KLEINNoch kleiner als Quick!✅ Unlimited1MEINZIGE OPTIONFür Volltext-Strategie REQUIRED!WICHTIG: Gemini 2.5 Flash unterstützt 1M Context-Window!3. CHUNK-REASSEMBLY (FAISS muss zusammenfügen!)Problem: FAISS speichert Chunks, nicht komplette PromptsBeispiel:Original-Prompt (10k Tokens):
"Es war einmal im Kindergarten... [10.000 Wörter] ...und so endete die Geschichte."

FAISS Chunks (bei 512 Token Chunk-Size):
- Chunk 1: "Es war einmal im Kindergarten... [512 tokens]"
- Chunk 2: "...und dann kamen die Zwillinge... [512 tokens]"
- Chunk 3: "...sie spielten zusammen... [512 tokens]"
- ...
- Chunk 20: "...und so endete die Geschichte. [512 tokens]"
FAISS findet: Nur Chunk 2 (enthält "Zwillinge")Aber wir brauchen: KOMPLETTEN Prompt (alle 20 Chunks zusammengefügt!)Lösung in query.py:Pythondef reassemble_prompt_from_chunks(chunk_id, chunks_data):
    """
    Findet alle Chunks die zum gleichen Prompt gehören und fügt sie zusammen.
    """
    # 1. Finde Prompt-ID vom gefundenen Chunk
    found_chunk = chunks_data[chunk_id]
    prompt_id = found_chunk['prompt_id']
    timecode = found_chunk['timecode']
    author = found_chunk['author']
    
    # 2. Finde ALLE Chunks mit gleicher Prompt-ID
    all_chunks_of_prompt = [
        c for c in chunks_data 
        if c['prompt_id'] == prompt_id 
        and c['timecode'] == timecode 
        and c['author'] == author
    ]
    
    # 3. Sortiere nach Chunk-Index (chunk_0, chunk_1, chunk_2, ...)
    all_chunks_of_prompt.sort(key=lambda c: c['chunk_index'])
    
    # 4. Füge zusammen zu komplettem Text
    full_prompt_text = ' '.join([c['text'] for c in all_chunks_of_prompt])
    
    return {
        'prompt_id': prompt_id,
        'timecode': timecode,
        'author': author,
        'full_text': full_prompt_text,
        'token_count': len(full_prompt_text.split()),  # Approximation
        'chunk_count': len(all_chunks_of_prompt),
        'found_chunk_index': found_chunk['chunk_index']  # Welcher Chunk wurde gefunden
    }
Backend-Integration (DualBackendBridge.js):JavaScriptconst faissResults = await this.queryPythonBackend(prompt);

// FAISS gibt jetzt komplette Prompts zurück (nicht nur Chunks!)
const reassembledPrompts = faissResults.sources.map(source => ({
    prompt_id: source.id,
    full_text: source.full_text,  // ← Komplett zusammengefügt
    token_count: source.token_count,  // ← ECHTER Token-Count
    chunk_count: source.chunk_count,
    metrics: null  // Muss noch geladen werden aus SQL
}));

// Warnung bei großen Prompts
for (const prompt of reassembledPrompts) {
    if (prompt.token_count > 50000) {
        console.warn(`⚠️ SEHR GROßER PROMPT: ${prompt.token_count} Tokens`);
    }
}
4. VOLLTEXT-STRATEGIE (Keine Verkürzung!)PRINZIP: Alles oder nichts!JavaScript// ❌ FALSCH (alte Systeme machen das):
const shortenedText = longPrompt.substring(0, 1000) + "...";

// ✅ RICHTIG (Evoki V2.0):
const fullText = longPrompt;  // Komplett senden, keine Kürzung!

// Token-Budget-Check:
if (totalTokens > 1_000_000) {
    // Wenn zu groß: Reduziere ANZAHL der Paare (nicht Länge!)
    selectedPairs = selectedPairs.slice(0, 2);  // 3 → 2 Paare
    // ABER: Jedes Paar bleibt VOLLTEXT!
}
Warum Volltext?Trauma-Kontexte dürfen nicht fragmentiert werdenNarrative Kohärenz ist kritisch"Zwillinge" könnte am Ende eines 80k-Prompts stehenVerkürzung würde Kontext zerstörenToken-Budget Management:JavaScript// Berechne Token-Count für alle 3 Paare
const pair1Tokens = calculateSetTokens(pair1);  // 19k
const pair2Tokens = calculateSetTokens(pair2);  // 57k
const pair3Tokens = calculateSetTokens(pair3);  // 12k

const totalContext = pair1Tokens + pair2Tokens + pair3Tokens;  // 88k

// Wenn zu groß: Priorisiere nach Relevanz
if (totalContext > 500_000) {  // 500k Context-Limit
    // Sortiere nach combined_score
    const sortedPairs = [pair1, pair2, pair3].sort((a, b) => 
        b.combined_score - a.combined_score
    );
    
    // Nimm nur Top 2 (oder Top 1 bei SEHR großen Prompts)
    selectedPairs = sortedPairs.slice(0, 2);
    
    console.log(`⚠️ Token-Budget: Reduziert von 3 auf 2 Paare (${totalContext} → ${pair1Tokens + pair2Tokens})`);
}
PERFECT AGREEMENT Prompts haben VORRANG:JavaScript// Wenn ein Paar PERFECT AGREEMENT hat → IMMER behalten!
const perfectPairs = allPairs.filter(p => p.agreement === 'PERFECT');
const otherPairs = allPairs.filter(p => p.agreement !== 'PERFECT');

// Budget: 500k Context-Limit
let selectedPairs = [];
let currentTokens = 0;

// 1. PERFECT Paare zuerst (garantiert dabei)
for (const pair of perfectPairs) {
    if (currentTokens + pair.tokenCount <= 500_000) {
        selectedPairs.push(pair);
        currentTokens += pair.tokenCount;
    }
}

// 2. Restliche Paare nach Score
for (const pair of otherPairs.sort((a, b) => b.combined_score - a.combined_score)) {
    if (currentTokens + pair.tokenCount <= 500_000 && selectedPairs.length < 3) {
        selectedPairs.push(pair);
        currentTokens += pair.tokenCount;
    }
}
5. PRAKTISCHES BEISPIEL (Real-World Szenario):User-Prompt: "Erzähl von den Zwillingen im Kindergarten" (20 Tokens)FAISS-Suche:Findet Chunk 2 von Prompt #4523 (enthält "Zwillinge")Reassembly: Lädt alle 15 Chunks von #4523 → 12k Tokens komplettSQL-Suche:Findet Prompt #4523 durch Metriken (A=0.85, PCI=0.72)Lädt Prompt-Text aus Quelldatenbank → 12k TokensDuplikat-Check:JavaScriptTimecode: 2025-06-15T14:32:11Z ✅ GLEICH
Prompt-ID: #4523 ✅ GLEICH
Author: "User" ✅ GLEICH
Text: "Es war einmal..." (12k) ✅ 1:1 MATCH

→ PERFECT AGREEMENT ERKANNT!
→ Wird NICHT 2x gesendet
→ Bekommt ⭐⭐⭐ HIGH CONFIDENCE MARKER ⭐⭐⭐
→ Doppelte Gewichtung (2.0x)
Context-Weaving (±2 Prompts):Prompt #4521 (8k) ← 2 vorherPrompt #4522 (5k) ← 1 vorherPrompt #4523 (12k) ← HIT (PERFECT AGREEMENT!)Prompt #4524 (7k) ← 1 nachherPrompt #4525 (3k) ← 2 nachherSet-Tokens: 8k + 5k + 12k + 7k + 3k = 35k für Paar 1Weitere 2 Paare:Paar 2 (nur Metrik): 28k TokensPaar 3 (nur Semantik): 19k TokensTOTAL Context: 35k + 28k + 19k = 82k Tokens+ User-Prompt: 20 Tokens+ Response Budget: 8k Tokens (32%)= GESAMT: ~90k Tokens ✅ Passt in 1M Limit!An Gemini gesendet:USER-PROMPT: "Erzähl von den Zwillingen im Kindergarten"

=== PAAR 1: ⭐⭐⭐ HIGH CONFIDENCE MATCH ⭐⭐⭐ ===
🔥 BEIDE SUCHVERFAHREN FANDEN DIESEN KONTEXT UNABHÄNGIG! 🔥

[8k Tokens Prompt #4521]
[5k Tokens Prompt #4522]
[12k Tokens Prompt #4523] ← SQL + FAISS beide fanden das!
[7k Tokens Prompt #4524]
[3k Tokens Prompt #4525]

=== PAAR 2: METRIK-DOMINANZ ===
[28k Tokens total...]

=== PAAR 3: SEMANTIK-DOMINANZ ===
[19k Tokens total...]

AUFGABE: Generiere kontextbasierte Antwort...
Gemini Response: ~8k Tokens (hochrelevant, weil PERFECT MATCH Context!)🎯 WARUM IST DAS BESSER ALS NUR FAISS ODER NUR SQL?Szenario 1: Nur FAISS (ohne SQL-Metriken)Findet "Zwillinge" nur wenn Wort schon gefallen istÜbersieht Trigger-Patterns in MetrikenKann keine Trends in emotionaler Entwicklung erkennenSzenario 2: Nur SQL (ohne FAISS-Semantik)Findet nur numerisch ähnliche MetrikenÜbersieht konzeptionell ähnliche Texte ("Geschwister" = "Zwillinge")Kann keine semantischen Verbindungen herstellenSzenario 3: ORCHESTRATOR (SQL + FAISS kombiniert)✅ Findet Trigger-Patterns auch ohne exakte Text-Übereinstimmung✅ Findet semantisch ähnliche Texte auch mit unterschiedlichen Metriken✅ Vergleicht beide Methoden und erkennt Abweichungen✅ Wählt 3 beste Paare mit unterschiedlichen Stärken✅ Webt Kontext ein (±2 Prompts = Geschichte)✅ Gemini bekommt 15 hochrelevante Prompts statt 3 zufälligerERGEBNIS:30-40% bessere Kontext-QualitätWeniger False Positives (beide Methoden müssen zustimmen)Mehr True Positives (wenn eine Methode findet, andere validiert)Bessere Gemini-Antworten (mehr relevanter Kontext)🔍 SQL IM FRONTEND VS BACKEND - UNTERSCHIEDEFRAGE: "Was läuft wo? Unterschiede?"BACKEND-SQLite (Server):Wo: backend/data/evoki_v2_ultimate_FULL.dbZweck: - Vector DBs (W_m2, W_m5, W_p25, W_p5, etc.)Metrik-Datenbanken (1:1 Zuordnung Prompt → Metriken)Chat-Historie (Quelldatenbank mit Original-Texten)Persistente Speicherung (bleibt nach Server-Neustart)Zugriff: Node.js Backend via better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend)Größe: Mehrere GB (33.795 Chunks + Metriken)Performanz: Schnell (Server-Hardware, SSD)FRONTEND-SQLite (Browser):Wo: Im Browser (IndexedDB als Basis)Zweck:UI-State Caching (aktuelle Session, Messages)Offline-Fähigkeit (falls Backend offline)LocalStorage-Ersatz (größer als 4MB)Zugriff: React via better-sqlite3 (VERBOTEN im Frontend) (VERBOTEN im Frontend) (WASM-compiled!)Größe: Max 1-2 GB (Browser-Limit)Performanz: Langsamer (Browser, kein direkter Disk-Access)UNTERSCHIEDE:AspektBackend-SQLiteFrontend-SQLiteSpeicherortServer FestplatteBrowser IndexedDBGrößeUnbegrenzt (GB)Browser-Limit (~2GB)PersistenzPermanentNur im BrowserMulti-User✅ JA (mehrere Clients)❌ NEIN (nur 1 User)Performanz⚡⚡⚡ Schnell⚡ LangsamUse CaseVector DBs, MetrikenUI-State, CachingPrivacyServer (sicherer)Browser (weniger sicher)UNSER SYSTEM NUTZT:Backend-SQLite (HAUPTSYSTEM):backend/data/
├─ evoki_v2_ultimate_FULL.db      ← Chat-Historie (Quelldatenbank)
├─ tempel_W_m2.db                 ← Vector DB Window -2
├─ tempel_W_m5.db                 ← Vector DB Window -5
├─ tempel_W_p25.db                ← Vector DB Window +25
├─ tempel_metrics_1to1.db         ← 1:1 Metrik-Zuordnung
├─ trialog_W_m2.db                ← Trialog Vector DBs
└─ ... (insgesamt 12 DBs)
Frontend-SQLite (Optional, für Offline):Browser IndexedDB:
├─ evoki_session_cache            ← Aktuelle Session
├─ evoki_messages_cache           ← Messages für UI
└─ evoki_metrics_preview          ← Metrik-Preview (nur aktuell)
EMPFEHLUNG:✅ Backend-SQLite: BEHALTEN (für Vector DBs, Metriken, Persistenz)❓ Frontend-SQLite: - Entfernen wenn Offline-Fähigkeit nicht nötigBehalten wenn User offline arbeiten sollAktuell: Wahrscheinlich NICHT genutzt (zu prüfen!)🔄 OFFENE FRAGEN (ERWEITERT)🔄 OFFENE FRAGEN (ERWEITERT)TECHNISCHE FRAGEN:ChatbotPanel: Behalten, umbenennen oder löschen?Snapshots: Evolution zu "Session Export" oder komplett weg?SQLite im Frontend: Warum? Kann entfernt werden?Genesis Anchor: Wann re-enablen? (nach welchem Meilenstein?)V1-Daten: Alle importieren oder nur letzten 3 Monate?Pipeline-Log: JSONL oder SQLite? (Performance vs. Queries)Trialog KB: Wann wird synapse_knowledge_base.faiss erstellt?Backend Health Check: Wie fixen ohne Backend zu killen?LocalStorage Limit: Backend-Persistenz implementieren?Chronik Rotation: Wie verhindern dass unbegrenzt wächst?NEUE KRITISCHE FRAGEN:1. Timeout-Strategie:Frontend Timeout erhöhen? 60s → 120s oder dynamisch?Backend-Timeouts optimieren? Gemini 90s reduzieren?Progress-Updates implementieren? Server-Sent Events für Pipeline-Steps?2. FAISS-Fehlerbehandlung:Validation nach FAISS-Suche? Prüfen ob Chunks gefunden wurden?Fallback-Strategie? Was tun wenn FAISS crasht? → Nur Metriken nutzen?Error-Messaging? User informieren "Kontext-Suche fehlgeschlagen"?3. Python CLI Stabilität:FAISS-Index im RAM halten? Separate Prozess statt CLI?Health-Check für Python? Prüfen ob query.py überhaupt funktioniert?Retry-Logic? Bei Timeout nochmal versuchen mit weniger Chunks?4. UI-Freezing verhindern:Virtualisierte Liste? Nur sichtbare Messages rendern?Lazy Loading? Alte Messages erst bei Scroll laden?Token-Limit für Rendering? Max 100k tokens im DOM?5. Race Conditions:AbortController bei Unmount? Request canceln wenn Component verschwindet?State-Management verbessern? Session in App.tsx statt Component?Request-Queue? Nur 1 Request gleichzeitig erlauben?🤖 INTELLIGENTE MODELL-AUSWAHL & DUAL-RESPONSE-STRATEGIEPROBLEM: Context-Window Limits vs QualitätModell-Übersicht (sortiert nach Qualität):RangModelContext-WindowKosten/1MQualitätSpezialisierung🥇 1Claude Sonnet 4.5200K$3⭐⭐⭐⭐⭐Komplexe Reasoning, Trauma-Analyse🥈 2GPT-4 Turbo128K$10⭐⭐⭐⭐⭐Allround, sehr kreativ🥉 3Gemini 2.5 Flash1M$0.10⭐⭐⭐⭐Große Kontexte, schnell, günstigDILEMMA:Beste Qualität (Claude) hat kleinstes Context-Window (200K)Größtes Context-Window (Gemini) hat niedrigste QualitätUser hat Prompts bis zu 80k + Context bis zu 500k = 580k Tokens!🎯 LÖSUNG: INTELLIGENTE KASKADEN-AUSWAHLSTUFE 1: STANDARD-AUSWAHL (Single-Model-Strategy)JavaScriptfunction selectOptimalModel(totalTokens, contextPairs) {
    // Berechne Token-Count für alle 3 Paare
    const pair1Tokens = calculateSetTokens(contextPairs[0]);
    const pair2Tokens = calculateSetTokens(contextPairs[1]);
    const pair3Tokens = calculateSetTokens(contextPairs[2]);
    const totalContext = pair1Tokens + pair2Tokens + pair3Tokens;
    
    console.log(`📊 Token-Analyse: ${totalContext} Context + ${userPromptTokens} User-Prompt = ${totalTokens} total`);
    
    // INTELLIGENTE AUSWAHL (nach Context-Window):
    
    if (totalTokens <= 128_000) {
        // ✅ Passt in GPT-4 Turbo (128K)
        return {
            model: 'GPT-4 Turbo',
            endpoint: 'https://api.openai.com/v1/chat/completions',
            apiKey: process.env.OPENAI_API_KEY,
            maxTokens: 128_000,
            cost: 10.0,  // $10 pro 1M
            quality: 5,
            reason: 'Beste Qualität bei <128K Context'
        };
    }
    
    if (totalTokens <= 200_000) {
        // ✅ Passt in Claude Sonnet 4.5 (200K)
        return {
            model: 'Claude Sonnet 4.5',
            endpoint: 'https://api.anthropic.com/v1/messages',
            apiKey: process.env.ANTHROPIC_API_KEY,
            maxTokens: 200_000,
            cost: 3.0,  // $3 pro 1M
            quality: 5,
            reason: 'Beste Qualität + Trauma-Spezialisierung bei <200K Context'
        };
    }
    
    // ❌ Zu groß für hochwertige Modelle
    if (totalTokens <= 1_000_000) {
        // ✅ Nur Gemini 2.5 Flash kann 1M
        return {
            model: 'Gemini 2.5 Flash',
            endpoint: 'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash',
            apiKey: process.env.GEMINI_API_KEY_1,
            maxTokens: 1_000_000,
            cost: 0.1,  // $0.10 pro 1M
            quality: 4,
            reason: 'Einziges Model mit 1M Context-Window'
        };
    }
    
    // ❌ Sogar zu groß für Gemini → Fehler!
    throw new Error(`Context zu groß: ${totalTokens} tokens überschreitet 1M Limit!`);
}
Beispiel-Ablauf (90k Tokens):User-Prompt: "Erzähl von den Zwillingen" (20 Tokens)
Context: 3 Paare × ~30k = 90k Tokens
Total: 90,020 Tokens

→ 90k < 128k → ✅ GPT-4 Turbo ausgewählt
→ Beste Qualität, passt ins Context-Window
STUFE 2: DUAL-RESPONSE-STRATEGIE (Split-Model-Strategy)Wenn Context > 200K für alle 3 Paare:JavaScriptfunction selectDualModelStrategy(totalTokens, contextPairs) {
    if (totalTokens > 200_000) {
        console.log(`⚠️ Context zu groß für hochwertige Modelle (${totalTokens} > 200K)`);
        console.log(`🎯 DUAL-RESPONSE-STRATEGIE aktiviert!`);
        
        // 1. Wähle BESTES Paar (meist PERFECT AGREEMENT)
        const bestPair = contextPairs.filter(p => p.agreement === 'PERFECT')[0] 
                      || contextPairs.sort((a, b) => b.combined_score - a.combined_score)[0];
        
        const bestPairTokens = calculateSetTokens(bestPair);
        
        // 2. Prüfe ob BESTES Paar in hochwertiges Model passt
        if (bestPairTokens <= 128_000) {
            // ✅ Bestes Paar passt in GPT-4
            return {
                strategy: 'DUAL_RESPONSE',
                primaryModel: {
                    model: 'GPT-4 Turbo',
                    pairs: [bestPair],  // Nur 1 Paar
                    tokens: bestPairTokens,
                    cost: 10.0,
                    quality: 5,
                    label: '🥇 HOCHWERTIG (GPT-4)'
                },
                secondaryModel: {
                    model: 'Gemini 2.5 Flash',
                    pairs: contextPairs,  // ALLE 3 Paare
                    tokens: totalTokens,
                    cost: 0.1,
                    quality: 4,
                    label: '📚 VOLLSTÄNDIG (Gemini)'
                },
                parallelExecution: true,  // BEIDE parallel aufrufen
                displayBoth: true         // BEIDE Antworten im Chat zeigen
            };
        }
        
        if (bestPairTokens <= 200_000) {
            // ✅ Bestes Paar passt in Claude
            return {
                strategy: 'DUAL_RESPONSE',
                primaryModel: {
                    model: 'Claude Sonnet 4.5',
                    pairs: [bestPair],  // Nur 1 Paar
                    tokens: bestPairTokens,
                    cost: 3.0,
                    quality: 5,
                    label: '🥇 HOCHWERTIG (Claude)'
                },
                secondaryModel: {
                    model: 'Gemini 2.5 Flash',
                    pairs: contextPairs,  // ALLE 3 Paare
                    tokens: totalTokens,
                    cost: 0.1,
                    quality: 4,
                    label: '📚 VOLLSTÄNDIG (Gemini)'
                },
                parallelExecution: true,
                displayBoth: true
            };
        }
        
        // ❌ Sogar bestes Paar zu groß für hochwertige Modelle
        // → Nur Gemini mit allen 3 Paaren
        return {
            strategy: 'SINGLE_RESPONSE',
            primaryModel: {
                model: 'Gemini 2.5 Flash',
                pairs: contextPairs,
                tokens: totalTokens,
                cost: 0.1,
                quality: 4,
                label: '📚 NUR GEMINI (zu groß für andere)'
            }
        };
    }
}
Beispiel-Ablauf (350k Tokens):User-Prompt: "Erzähl von den Zwillingen" (20 Tokens)
Context: Paar 1 (120k) + Paar 2 (150k) + Paar 3 (80k) = 350k Tokens
Total: 350,020 Tokens

→ 350k > 200k → ❌ Zu groß für Claude/GPT-4
→ 🎯 DUAL-RESPONSE-STRATEGIE aktiviert!

Paar 1 (PERFECT AGREEMENT): 120k Tokens
→ 120k < 128k → ✅ Passt in GPT-4!

STRATEGIE:
├─ 🥇 PRIMARY: GPT-4 Turbo (nur Paar 1 = 120k)
│  └─ Beste Qualität, fokussiert auf wichtigsten Kontext
└─ 📚 SECONDARY: Gemini 2.5 Flash (alle 3 Paare = 350k)
   └─ Vollständiger Kontext, alle Perspektiven

→ BEIDE parallel aufrufen
→ BEIDE Antworten im Chat anzeigen
🔄 PARALLELE AUSFÜHRUNG (Backend-Implementation)JavaScriptasync function executeModelStrategy(strategy, userPrompt, contextPairs) {
    if (strategy.strategy === 'SINGLE_RESPONSE') {
        // Normale Ausführung (nur 1 Model)
        const response = await callLLM(
            strategy.primaryModel.model,
            userPrompt,
            strategy.primaryModel.pairs
        );
        
        return {
            responses: [{
                model: strategy.primaryModel.model,
                label: strategy.primaryModel.label,
                text: response.text,
                tokens: response.usage.total_tokens,
                cost: response.usage.total_tokens / 1_000_000 * strategy.primaryModel.cost
            }]
        };
    }
    
    if (strategy.strategy === 'DUAL_RESPONSE') {
        // Parallele Ausführung (2 Models gleichzeitig)
        console.log('🔄 Starte DUAL-RESPONSE: 2 Models parallel...');
        
        const [primaryResponse, secondaryResponse] = await Promise.all([
            callLLM(
                strategy.primaryModel.model,
                userPrompt,
                strategy.primaryModel.pairs  // Nur 1 Paar
            ),
            callLLM(
                strategy.secondaryModel.model,
                userPrompt,
                strategy.secondaryModel.pairs  // ALLE 3 Paare
            )
        ]);
        
        console.log('✅ BEIDE Antworten empfangen!');
        
        return {
            responses: [
                {
                    model: strategy.primaryModel.model,
                    label: strategy.primaryModel.label,
                    text: primaryResponse.text,
                    tokens: primaryResponse.usage.total_tokens,
                    cost: primaryResponse.usage.total_tokens / 1_000_000 * strategy.primaryModel.cost,
                    quality: strategy.primaryModel.quality,
                    contextPairs: strategy.primaryModel.pairs.length
                },
                {
                    model: strategy.secondaryModel.model,
                    label: strategy.secondaryModel.label,
                    text: secondaryResponse.text,
                    tokens: secondaryResponse.usage.total_tokens,
                    cost: secondaryResponse.usage.total_tokens / 1_000_000 * strategy.secondaryModel.cost,
                    quality: strategy.secondaryModel.quality,
                    contextPairs: strategy.secondaryModel.pairs.length
                }
            ]
        };
    }
}
📚 REFERENZENHaupt-README: README.md (mit Synapse Genesis Point)Architektur: ARCHITECTURE.json (auto-generiert)Setup: SETUP.mdCleanup Report: docs/CLEANUP_REPORT.mdV1 Reference: c:\evoki\ (Produktiv-System)Letztes Update: 28.12.2025 - Synapse (Explorer & Connector) ⚡Discovery Phase: 4/5 - LocalStorage, Startup, Dependencies, Error Handling vollständigNächste Review: Nach erstem erfolgreichen Tempel-Test



---
# 🧭 EXTENSION: UNIFIED MASTER LAYER (V2.2)

## Zweck dieser Erweiterung
Diese Erweiterung transformiert **WHITEBOARD_V2.1_FIXED** von einer korrigierten Spezifikation
zu einem **durchgetakteten Arbeits‑ und Entwicklungsdokument**.

**Nichts wird ersetzt oder gekürzt.**
Alles Folgende ist **additiv** und kompatibel zu V2.1.

---

## 🧱 MASTER‑PRINZIP
EVOKI wird als **Single‑User‑System** betrieben.

Daraus folgt explizit:
- User darf Governance per Prompt oder UI überschreiben
- Overrides sind **explizit**, **sichtbar**, **revisionsfähig**
- Overrides erzeugen **keine impliziten Writes**

---

## 🔐 USER‑OVERRIDES (NEUE SCHICHT)

### Override‑Typen
```yaml
override_modes:
  DEFAULT:
    description: "Normale Governance (Decay + Sentinel aktiv)"
  FULL_CONTEXT:
    description: "Nutze gesamten Verlauf vom Ursprung bis jetzt"
  LEGACY_CONTEXT:
    description: "Nutze Kontext > 1 Jahr (Archiv)"
```

### Verbindliche Regeln
- [MUST] Overrides müssen explizit gesetzt sein (UI oder Prompt)
- [MUST] FULL_CONTEXT & LEGACY_CONTEXT sind **READ‑ONLY**
- [MUST NOT] Overrides schreiben in Vector‑ oder Memory‑DBs

---

## 🗂️ SPEICHER‑ARCHITEKTUR (ERWEITERT)

### Aktive Datenbanken (WRITE)
| Layer | Zweck |
|------|------|
| SQL Source DB | Autoritativer Text |
| Vector DB | Aktiver semantischer Kontext |
| comparison_log.db | Entscheidungen & Governance‑Logs |

### Analyse‑Archive (READ‑ONLY)
| Store | Zweck |
|-------|------|
| archive/full_context/ | Gesamthistorie |
| archive/legacy_context/ | > 1 Jahr |
| archive/ad_hoc/ | Temporäre Analysen |

Regel:
> **Archive dürfen niemals Write‑Targets sein.**

---

## ⏳ TIME‑DECAY GOVERNANCE (KLARSTELLUNG)

### Zeitbasis
- Intern: **Millisekunden (ms)** – höchste Präzision
- Normalisiert: Tage (d) für Lesbarkeit

### Default‑Horizont (Single User)
```yaml
time_horizons:
  NORMAL: 180d
  WARNING: 90d
  CRITICAL: 30d
```

### Decay‑Modelle
```text
EXPONENTIAL (Default):
w = exp(-λ * Δt)

HYPERBOLIC (Nur bei FULL/LEGACY):
w = 1 / (1 + α * Δt)
```

### Regel
- [MUST] EXPONENTIAL im Default
- [MAY] HYPERBOLIC bei explizitem Override
- [MUST] Sentinel darf Decay verschärfen, nie aufheben

---

## 🔁 PIPELINE‑ERWEITERUNG (LOGISCH)

Neue Schritte (vor Retrieval):
1. Parse Overrides
2. Set Read/Write‑Matrix
3. Select Decay‑Mode
4. Lock Persistence

Danach erst:
→ FAISS / SQL / Model Routing

---

## 🧠 WARUM DAS KOHÄRENT IST

- Kein Context‑Drift
- Kein Daten‑Vergiften durch alte Zustände
- Volle analytische Freiheit
- Klare Trennung: **Erinnern vs. Analysieren**

---

## 📝 ARBEITS‑TODO (AUTO‑ABLEITUNG)

P0:
- [ ] Override‑Flags im Request Schema
- [ ] Write‑Block bei FULL/LEGACY
- [ ] Archive‑Verzeichnis anlegen

P1:
- [ ] UI‑Toggle für Kontext‑Horizon
- [ ] Decay‑Mode Visualisierung
- [ ] Audit‑Log für Overrides

P2:
- [ ] Replay‑Mode auf Archive
- [ ] Vergleich Analyse vs Active Context

---

## STATUS
WHITEBOARD_V2.2_EXTENDED_MASTER:
✅ rückwärtskompatibel  
✅ logisch geschlossen  
✅ arbeitsfähig  
