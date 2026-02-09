# Adler Integrationen (Vollständige Ergänzungen)

Vollständige Ergänzungen und kritische Systeminformationen für Evoki V3.0, Stand 2026-02-08.

---

## [ADLER] SSE Pipeline Streaming

**Kritischer Fix gegen Timeout-Hölle und URI-Limit**

### Problem
- GET/EventSource scheitert bei langen Prompts (HTTP 414 URI Too Long)
- Frontend 60s Timeout vs Backend 115s Verarbeitung → Zombie-Requests
- Blind-Wartezeit ohne Feedback → schlechte UX

### Lösung
**POST-basierte Streams** mit `@microsoft/fetch-event-source`:

**Frontend (Evoki TempleChat):**
- `fetchEventSource` POST auf `/api/bridge/stream`
- Headers: `Accept: text/event-stream`
- Streaming-Reader oder Callback `onmessage` → `pipelineSteps` UI
- `AbortController` bei Unmount/Tab-Wechsel

**Backend:**
- SSE-Endpoint sendet **Steps 1-12**:
  1. Metrics Calculation
  2. FAISS Semantic Search
  3. SQL Query Execution
  4. Cross-Enrichment
  5. Comparison (metric vs semantic)
  6. A65 Kastasis Check
  7. Weaving (context assembly)
  8. Model Selection
  9. LLM Generation
  10. Storage
  11. Logging
  12. Response Complete

**Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**Heartbeat:** Alle 30s, `req.on('close')` → abort

**UX Benefits:**
- Live-Progress sichtbar
- Sichtbare Parallelität (Dual-Response)
- Keine Blind-Wartezeit
- Timeouts irrelevant solange Daten fließen

**Nginx/Proxy Config:**
- Buffering deaktivieren
- Ggf. Timeout erhöhen (300s+)

---

## [ADLER] Sentinel Veto-Matrix

**5 Regeln mit Score-Anpassung nach Cross-Enrichment, vor A65**

### Regel 1: Dissoziation
```
IF hazard > 0.75 AND semantic < 0.5
  THEN combined_score *= 0.5
  FLAG: DISSOCIATION_DETECTED
```

**Rationale:** Hohe Hazard + niedrige Semantik = User ist dissoziiert, versteht Matches nicht

### Regel 2: Hidden Trigger
```
IF PCI > 0.8 AND semantic < 0.3
  THEN combined_score *= 0.3
  FLAG: HIDDEN_TRIGGER
  SEVERITY: CRITICAL
```

**Rationale:** Starker Panik-Indikator + sehr niedrige Semantik = versteckter Trigger, User bewusst nicht erkennbar

### Regel 3: Safe Match Boost
```
IF hazard < 0.2 AND semantic > 0.9 AND PCI < 0.5
  THEN combined_score *= 1.5
  FLAG: SAFE_BOOST
```

**Rationale:** Niedrige Gefahr + hohe Semantik + keine Panik = sicherer, hochwertiger Match

### Regel 4: Positive Trauma
```
IF hazard < 0.2 AND semantic > 0.9 AND PCI >= 0.5
  THEN warn POSITIVE_TRAUMA
  NO BOOST (ambiguous case)
```

**Rationale:** Hohe Semantik + moderater PCI trotz niedriger Hazard = Trauma-Verarbeitung, vorsichtig behandeln

### Regel 5: High Divergence
```
IF |metric_score - semantic_score| > 0.6
  THEN warning HIGH_DIVERGENCE
```

**Rationale:** Große Diskrepanz zwischen Metriken und Semantik = unsicherer Match, User-Review empfohlen

### Frontend Integration
**Badges mit Severity:**
- LOW: Grün
- MEDIUM: Gelb
- HIGH: Orange
- CRITICAL: Rot

**Display:**
- `sentinelNote`: Beschreibung der Regel
- `score_before` / `score_after`: Transparenz der Anpassung

**Logging:**
- `comparison_log` erweitert um `sentinel_*` Felder
- Dual-Response: HQ-Modell erhält explizite Sentinel-Hinweise im Prompt

---

## [ADLER] Dual-Response Strategie

**Intelligente Kaskade bei großen Kontexten**

### Single-Model Strategie
- **≤128k Tokens:** GPT-4 Turbo
- **≤200k Tokens:** Claude Sonnet 4.5
- **≤1M Tokens:** Gemini 2.5 Flash
- **>1M Tokens:** ERROR (zu groß)

### Dual-Response (bei >200k Tokens)
**Bestes Paar (PERFECT AGREEMENT bevorzugt):**
- In HQ-Modell (GPT-4/Claude) wenn <128k/200k
- Alle 3 Paare parallel in Gemini (1M Window)
- **Beide Antworten gleichzeitig anzeigen**

### Parallel Execution
- `Promise.all` für beide Modelle
- Progress-Updates pro Modell
- **Kostenabschätzung:**
  - GPT-4: $10/M Tokens
  - Claude: $3/M Tokens
  - Gemini: $0.1/M Tokens

### Context-Pruning
**Wenn Budget >500k:**
- Paare nach `combined_score` priorisieren
- PERFECT AGREEMENTS bevorzugen
- Falls nötig: Top-K Paare statt alle

---

## [ADLER] Timeout-Analyse & Heartbeat

### Probleme Identifiziert
1. **Frontend 60s vs Backend 115s:**
   - Metrics: 10s
   - FAISS: 15s
   - Gemini: 90s
   - → Zombie-Requests

2. **Python CLI spawn:**
   - Timeout unsicher
   - stdout buffering
   - FAISS-Ladezeit >15s

3. **Nginx SSE buffering:**
   - Response wird zurückgehalten

4. **UI-Freeze:**
   - Große Messages ohne Virtual Scroll

### Lösungen
1. **SSE Heartbeat:**
   - Alle 30s
   - Progress Steps 1-12
   - Keine `AbortSignal.timeout`

2. **AbortController:**
   - Bei Unmount/Tab-Wechsel
   - `isLoading` Guard
   - `finally { setIsLoading(false) }`

3. **FastAPI persistent:**
   - Port 8000 statt CLI spawn
   - `X-Accel-Buffering: no`

4. **React Virtualisierung:**
   - `react-window` für Chat-List
   - Token-Limit Selector während Loading sperren

---

## [ADLER] SQLite Warnung (Frontend)

**KRITISCHER BUILD-BLOCKER!**

### Problem
`better-sqlite3` und `sqlite3` in `frontend/package.json` sind **native Node-Module:**
- Benötigen `fs`, `path`, native bindings
- **Vite/Web-Browser crashen!**

### Sofort-Maßnahme
```bash
cd frontend
npm uninstall better-sqlite3 sqlite3
```

### Browser-Alternativen (NUR falls offline-SQL nötig)
- `sql.js` (WASM, read-only empfohlen)
- `wa-sqlite` (WASM, read-write)

### Für V3.0
**Backend ist alleinige SQL-Source!**
- Alle DB-Queries über API
- Frontier kein direkter DB-Zugriff

---

## [ADLER] 153 Metriken V14

**Neu gegenüber 120+ Metriken**

### 10 Ebenen
1. **Lexika** (S_SELF, X_EXIST, T_PANIC, etc.)
2. **Core** (Ångström, A, F, B-Vektor)
3. **HyperPhysics** (Δ-Operatoren, Gradienten)
4. **FEP** (Free Energy, Surprise, Prediction Error)
5. **Grain** (Granularität, Detailtiefe)
6. **Linguistik** (Kohärenz, COH-Connectors, LL)
7. **Chronos** (Time Decay, Phase Detection)
8. **Metakognition** (Meta-Awareness, Reflexionstiefe)
9. **System-Gesundheit** (Memory Usage, Query Performance)
10. **OMEGA** (Final Synthesis, Phi-Score, EV-Consensus)

### Wichtige Bindeglieder

#### Time Decay
```python
Time_Decay_Factor (M114) = 1 / (1 + lambda * |daysDiff|)
lambda = 0.05  # 5% decay per day
```
Plus: `G_phase` (M52) gegen Context-Drift

#### Sentinel Integration
- Nutzt: `z_prox` (M24), `T_fog`, `LL`
- Emergency Refetch bei `z_prox > 0.8`
- `Safety_Lock_Status` (M150)

#### Early Warning System
- `grad_PCI` (M32): Beschleunigung des Panicanstiegs
- `nabla_delta_A` (M33): Affekt-Absturz-Geschwindigkeit

#### Metaphern-Synthese
- `H_conv`: Entropy of Conversation
- `EV_consensus`: Emergent Value Agreement
- A65 nutzt: `Trajectory_Optimism` (M124), `Phi_Score` (M69)

### Token-Budget Realität
- **Set-Med ian:** ~19k Tokens
- **Worst Case:  400k pro Set**
- **Strategie:** Ggf. Paare reduzieren, aber **Volltext beibehalten** (Chunk-Reassembly im FAISS)

---

**Dokumentiert:** 2026-02-08  
**Quelle:** User-Input (Adler Integrationen Specification)  
**Status:** Integration Pending
