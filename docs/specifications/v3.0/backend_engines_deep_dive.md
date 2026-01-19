# 📚 V2.0 BACKEND-ENGINES KOMPLETT ANALYSIERT

**Datum:** 2026-01-19 07:02  
**Status:** DEEP DISCOVERY - BACKEND-LOGIK VOLLSTÄNDIG ERFASST

---

## 🔥 KRITISCHE BACKEND-KOMPONENTEN GEFUNDEN

### 1. **DualBackendBridge.js** (625 Zeilen)

**Kernfunktion:** Orchestriert Python (8000) + Node (3001)

**12-STEP PIPELINE (Lines 116-252):**

```
1. Prompt empfangen (Frontend)
2. Metriken berechnen (Node Backend /api/metrics/calculate)
3. FAISS W2 durchsuchen (Python CLI query.py)
4. FAISS W5 tief-suchen (Simuliert)
5. Trinity DBs abfragen (Node Backend /api/vector/search)
6. Top-3 kombinieren (60% semantic + 40% metric)
7. Gemini Context bauen (GeminiContextBridge)
8. API-Request Review (Simuliert)
9. Gemini Response generieren (generateContextualResponse)
10. In 12 DBs speichern (TrinityUploadEngine)
11. Chronicle aktualisieren (Simuliert)
12. Fertig → Response an Frontend
```

**SSE-STREAMING SUPPORT (Lines 105, 110-114):**
```javascript
const { onProgress } = options;  // ✅ Callback für SSE
const emitProgress = (step, name, message) => {
    if (onProgress && typeof onProgress === 'function') {
        onProgress(step, { name, message });
    }
};
```

**CRITICAL: TIMEOUTS (Lines 300,444,422,526):**
- Metriken: 10s
- Vector Search: 60s (erhöht von 15s!)
- FAISS CLI: 60s (erhöht!)
- Gemini API: 90s (für 1M Context!)

**COMBINED SCORE (Lines 464-523):**
```javascript
const SEMANTIC_WEIGHT = 0.6;
const METRIC_WEIGHT = 0.4;
const combinedScore = (semanticScore * 0.6) + (metricScore * 0.4);
// Sortiere und nimm Top 3
```

**FAISS CLI PARSING (Lines 319-423):**
- Spawnt Python: `python.exe query.py <prompt>`
- Parst stdout via Regex
- Line Endings Windows: `\r\n` → `\n` Normalisierung
- Regex: `/#(\d+) \| Similarity: ([\d.]+) \| ([\d-]+)\s*\n\s*Chunk: ([^\n]+)/g`

---

### 2. **GeminiContextBridge.js** (676 Zeilen)

**Kernfunktion:** Verwandelt FAISS-Chunks → Kontextreicher Gemini-Prompt

**5-PHASEN WORKFLOW (Lines 41-122):**

**PHASE 1: Chunks erweitern (Lines 51-55)**
```javascript
const expandedChunks = await this.expandChunks(top3Chunks);
// Hole ±2 Nachbar-Chunks (falls zerteilt)
```

**PHASE 2: Kontext laden (Lines 57-60)**
```javascript
const contextMessages = await this.loadContextMessages(expandedChunks, sessionId);
// Hole letzte 4 Nachrichten (2 User + 2 Agent)
```

**PHASE 3: Metriken-Zusammenfassung (Lines 62-65)**
```javascript
const metricsSummary = this.summarizeMetrics(metrics);
// Formatiere 120+ Metriken für Gemini
```

**PHASE 4: Prompt bauen (Lines 67-76)**
```javascript
const geminiPrompt = this.buildGeminiPrompt({
    userPrompt, expandedChunks, contextMessages, metricsSummary
});
```

**PHASE 5: Gemini API Call (Lines 87-90)**
```javascript
const geminiResponse = await this.callGeminiAPI(geminiPrompt);
```

---

**CHUNK EXPANSION LOGIK (Lines 129-189):**

```javascript
// Extrahiere Chunk-Nummer: "_chunk_001", "_001", etc.
const chunkNumber = this.extractChunkNumber(chunkId);
// Hole Nachbarn: [chunk-2, chunk-1, CURRENT, chunk+1, chunk+2]
const neighbors = await this.getNeighborChunks(chunkId, chunkNumber, 2);
// Setze zusammen
const full_text = this.assembleChunks([...neighbors.previous, chunk, ...neighbors.next]);
```

**GEMINI PROMPT STRUKTUR (Lines 375-438):**

```markdown
Du bist EVOKI, ein empathischer KI-Begleiter...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 WISSENSDATENBANK (Top 3 Ergebnisse):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Quelle 1 | Relevanz: 85.3% | ID: 2025-02-08_001]
<VOLLSTÄNDIGER CHUNK-TEXT>

[Quelle 2 | Relevanz: 78.1% | ID: 2025-02-08_042]
<VOLLSTÄNDIGER CHUNK-TEXT>

[Quelle 3 | Relevanz: 65.9% | ID: 2025-02-08_099]
<VOLLSTÄNDIGER CHUNK-TEXT>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 VORHERIGE KONVERSATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: <LETZTE USER-FRAGE>
Evoki: <LETZTE EVOKI-ANTWORT>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AKTUELLE METRIKEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Authentizität (A): 0.85
Prompt-Clarity (PCI): 0.92
Kohärenz: 0.78
Flow: 0.88
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ USER-FRAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<AKTUELLE USER-FRAGE>

WICHTIG:
✅ Beziehe dich DIREKT auf die Inhalte aus der Wissensdatenbank
✅ Zitiere oder paraphrasiere relevante Details
✅ Gib eine echte, menschliche Antwort
❌ Erfinde NICHTS
```

---

**API-KEY ROTATION + FALLBACK (Lines 445-659):**

```javascript
// Gemini Keys rotieren
const apiKey = this.getNextApiKey();
this.currentKeyIndex = (this.currentKeyIndex + 1) % this.geminiApiKeys.length;

// Wenn alle Gemini-Keys erschöpft:
if (this.exhaustedKeys.size >= this.geminiApiKeys.length) {
    return await this.callOpenAIFallback(prompt);
}

// Quota-Error erkennen:
if (response.status === 429 || errorText.includes('RESOURCE_EXHAUSTED')) {
    this.exhaustedKeys.add(keyIndex);
    return await this.callGeminiAPI(prompt, retryCount + 1);  // Retry mit nächstem Key
}

// OpenAI Fallback:
// Model: gpt-4o-mini
// Timeout: 30s (vs 90s für Gemini)
```

**DYNAMISCHE TOKEN-LIMITS (Lines 457-469):**
```javascript
const estimatedPromptTokens = Math.ceil(promptLength / 4);

if (estimatedPromptTokens > 15000) {
    maxOutputTokens = 8000;   // 1M Context
} else if (estimatedPromptTokens > 8000) {
    maxOutputTokens = 4096;   // 50k Context
} else if (estimatedPromptTokens > 4000) {
    maxOutputTokens = 3072;   // 25k Context
} else {
    maxOutputTokens = 2048;   // Default
}
```

**GLOBAL CONFIG SUPPORT (Lines 472-506):**
```javascript
const config = global.templeApiConfig || {
    temperature: 0.8,
    topK: 40,
    topP: 0.95,
    presencePenalty: 0,
    frequencyPenalty: 0,
    candidateCount: undefined,
    seed: undefined,
    stopSequences: []
};
```

---

### 3. **metrics_processor.py** (GEFUNDEN!)

**Location:** `C:\Evoki V2.0\evoki-app\backend\core\metrics_processor.py`

**Zweck:** Berechnet 120+ Metriken vom User-Prompt

**MUSS ANALYSIERT WERDEN:** (Noch nicht gelesen)

---

## 🔍 NOCH FEHLENDE ARTEFAKTE (SUCHLISTE)

### Backend-Metriken:
- ✅ `metrics_processor.py` → GEFUNDEN!
- ❓ Regelwerk-Enforcement-Skript
- ❓ A65-Logik (Candidate Selection)
- ❓ Guardian Veto Implementation

### FAISS-Tooling:
- ✅ `query.py` → REFERENZIERT (Line 326)
- ❓ `load_chunk.py` → REFERENZIERT (Line 252)
- ❓ FAISS Index Build Script
- ❓ Embedding Generation Script

### Trinity Engines:
- ✅ `TrinityEngine.js` → VOLLSTÄNDIG ANALYSIERT
- ✅ `DualBackendBridge.js` → VOLLSTÄNDIG ANALYSIERT
- ✅ `GeminiContextBridge.js` → VOLLSTÄNDIG ANALYSIERT

---

## 📊 ZUSAMMENFASSUNG: WAS JETZT?

**NÄCHSTE SCHRITTE (DISCOVERY FORTSETZUNG):**

1. ✅ **metrics_processor.py analysieren** (120+ Metriken-Logik)
2. ❓ **Regelwerk V12 JSON finden** (noch nicht gefunden!)
3. ❓ **A65-Logik dokumentieren** (wo ist die Implementierung?)
4. ❓ **Guardian Veto finden** (A7.5 / A29 Implementation)
5. ❓ **FAISS-Scripts sammeln** (query.py, load_chunk.py, build index)

**KRITISCHE ERKENNTNISSE:**

✅ **Backend-Pipeline vollständig dokumentiert** (12 Steps)  
✅ **SSE-Streaming Support vorhanden** (für Echtzeit-Updates)  
✅ **Timeout-Management kritisch** (60-90s für große Requests)  
✅ **Hybrid Retrieval bestätigt** (60% semantic + 40% metric)  
✅ **Chunk-Expansion essentiell** (±2 Nachbarn für Kontext)  
✅ **API-Fallback robust** (Gemini Rotation + OpenAI Backup)

**READY FÜR NÄCHSTE DISCOVERY-PHASE!**
