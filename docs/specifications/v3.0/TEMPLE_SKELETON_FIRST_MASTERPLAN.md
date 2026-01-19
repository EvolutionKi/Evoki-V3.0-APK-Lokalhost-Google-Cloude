# 🏛️ EVOKI TEMPLE IMPLEMENTATION MASTERPLAN (V3.0)

> **STRATEGY:** "SKELETON-FIRST PROTOCOL" (Core-Driven Development)  
> **APPROACH:** Nervenbahnen → Organe → Leben  
> **PHILOSOPHY:** Simulation Mode bis alles stabil, dann echte Engines  
> **STATUS:** READY FOR EXECUTION

---

## 💡 STRATEGISCHE PHILOSOPHIE

### **WARUM SKELETON-FIRST?**

**Das Problem mit "Big Bang" Implementation:**
```
Alles auf einmal bauen:
  - FastAPI Server
  - 21 SQLite DBs
  - FAISS Loader (4096D, GPU)
  - 153 Metriken Engine
  - Double Airlock Gates
  - Gemini LLM Integration
  - SSE Streaming
  - React Frontend

→ Wenn etwas kaputt ist: Wo liegt der Fehler?
  - SSE Timeout?
  - FAISS lädt nicht?
  - Metrics crashen?
  - LLM offline?
  - CORS-Fehler?
```

**Die Lösung: Skeleton-First Protocol**
```
Phase 0: Nur das Nervensystem (SSE Dummy-Stream)
  → Test: "Simulation: T_panic erkannt" erscheint SOFORT im Browser
  → Falls kaputt: NUR 2 Dinge debuggen (FastAPI + React SSE)

Phase 1: Gedächtnis hinzu (echte DBs, aber Mock-Daten)
  → Test: DB Query funktioniert, Response noch simuliert

Phase 2: Gewissen aktivieren (echte Metriken, Mock-LLM)
  → Test: Metriken werden berechnet, Gates feuern

Phase 3: Stimme erwecken (echtes LLM)
  → Test: KOMPLETTER Flow End-to-End

Phase 4: Gesicht polieren (UI/UX)
  → Test: Es sieht fantastisch aus!
```

**Vorteil:** Jede Phase testet GENAU EINE neue Komponente!

---

## 📋 PHASE 0: DAS NERVENSYSTEM (The Spinal Cord)

**Ziel:** Eine stabile Echtzeit SSE-Verbindung zwischen React Frontend und FastAPI Backend.

**Was wir bauen:** Nur die "Nervenbahnen" - kein Gehirn, keine Datenbanken, keine KI.

### Backend Requirements:
- ✅ FastAPI Server auf Port 8000
- ✅ `/api/temple/stream` Endpoint (SSE EventSource kompatibel)
- ✅ CORS für `localhost:5173`
- ✅ Simulation Mode: Hardcoded Events (`status`, `thought`, `metrics_preview`, `token`)

### Frontend Requirements:
- ✅ `App.tsx` fixiert auf `activeTab = Tab.Temple`
- ✅ `EvokiTempleChat.tsx` refactored auf `EventSource` API
- ✅ "Pipeline Console" für Live-Event-Log
- ✅ Loading States & Retry Logic

### Test-Szenarien (Simulation Mode):
1. **Normal Flow:** "Wie geht es dir?" → Stream: "Gate A geöffnet" → "Denke nach..." → "Antwort: Gut!"
2. **Guardian Veto:** "Ich will sterben" → Stream: "Gate A GESCHLOSSEN" → "Guardian-Veto: Krisenprompt"
3. **Timeout Test:** 60 Sekunden Verbindung halten ohne Disconnect

**Erfolgs-Kriterium:** Browser zeigt alle simulierten Events in Echtzeit OHNE Refresh!

---

## 📋 PHASE 1: DAS GEDÄCHTNIS (The Hippocampus)

**Ziel:** Anbindung der 21 SQLite Datenbanken und FAISS W-P-F Zeitmaschine.

**Was wir aktivieren:** Echte Daten-Layer, aber Responses noch simuliert.

### Database Layer:
- ✅ 21 SQLite DBs erstellen (Schema aus V2.0)
  - 1× `master_timeline.db` (Alle Chunks + 153 Metriken)
  - 12× W-P-F DBs (`tempel_W_m25.db` bis `tempel_F_p25.db`)
  - 7× B-Vektor DBs (`bvec_life.db`, `bvec_truth.db`, ...)
  - 1× `composite.db` (B_align, F_risk, risk_z)

### FAISS Integration:
- ✅ FAISS Index laden (`chatverlauf_final_20251020plus_dedup_sorted.faiss`)
- ✅ Mistral-7B Model (4096D, GPU) für Semantic Search
- ✅ Query-Funktion: `search_similar_chunks(query, top_k=100)`

### W-P-F Causal Matrix:
- ✅ Implementiere `get_causal_matrix(anchor_id)`
  - Input: Ein FAISS-Treffer (z.B. Chunk ID 12345)
  - Output: Vergangenheit (P-25, P-5, P-2, P-1), Jetzt (W), Zukunft (F+1, F+2, F+5, F+25)
- ✅ Hybrid Scoring: 60% Semantic Similarity + 40% Metrik-Korrelation

### Test-Szenarien:
1. **FAISS Query:** "Ich fühle mich leer" → Top-3 ähnliche Chunks aus Chatverlauf
2. **W-P-F Expansion:** Chunk 12345 → Zeige P-25 und F+25 Timeline
3. **DB Query:** SELECT * FROM master_timeline WHERE B_align > 0.9

**Erfolgs-Kriterium:** FAISS findet relevante Chunks, W-P-F Logik funktioniert, DBs laden schnell (<100ms).

**ABER:** LLM Response ist NOCH simuliert! ("Mock-Antwort basierend auf Chunk 12345")

---

## 📋 PHASE 2: DAS GEWISSEN & DER WILLE (The Frontal Lobe)

**Ziel:** Evoki denkt BEVOR er spricht - Metriken, Gates, Andromatik.

**Was wir aktivieren:** Kognitive Layer - Metriken + Double Airlock.

### Metrics Engine:
- ✅ Portiere `v2_metrics_processor.py` (153 Metriken)
- ✅ Input: User-Prompt Text
- ✅ Output: Dictionary mit allen Metriken
  - Core: `A` (Affekt), `PCI` (Kohärenz), `coh`
  - Trauma: `T_panic`, `T_disso`, `T_trigger`
  - B-Vektor (7D): `B_life`, `B_truth`, `B_depth`, ...
  - Composite: `B_align`, `F_risk`, `risk_z`

### Double Airlock Gates:

**GATE A (Pre-Prompt Validation):**
```python
def pre_validation(prompt: str, metrics: dict) -> dict:
    """
    Prüft VOR Google API Call:
    - A51: CRC32 Genesis Anchor (Regelwerk V12)
    - A7.5/A29: Guardian-Veto (T_panic > 0.8?)
    - A39: Krisenprompt-Erkennung (Suizid-Keywords)
    - A37: Regelwerks-Berechnung
    """
    veto_reasons = []
    
    # CRC32 Check
    if not validate_crc32(REGELWERK_PATH, 3246342384):
        veto_reasons.append("A51 Genesis Anchor Breach")
    
    # Guardian-Veto
    if metrics.get('T_panic', 0) > 0.8:
        veto_reasons.append("A7.5 Guardian-Veto: T_panic > 0.8")
    
    if metrics.get('F_risk', 0) > 0.6:
        veto_reasons.append("A29 Wächter: F_risk > 0.6")
    
    # Krisenprompt
    crisis_keywords = ['suizid', 'sterben', 'töten', 'umbringen']
    if any(kw in prompt.lower() for kw in crisis_keywords):
        veto_reasons.append("A39 Krisenprompt erkannt")
    
    return {
        'passed': len(veto_reasons) == 0,
        'veto_reasons': veto_reasons,
        'gate': 'A'
    }
```

**GATE B (Post-Response Validation):**
```python
def post_validation(response: str, metrics: dict, chunks: list) -> dict:
    """
    Prüft NACH LLM, VOR User:
    - A0: Direktive der Wahrheit (Halluzination?)
    - A46: Soul-Signature (B_align < 0.7?)
    - A7.5/A29: Erneute Guardian-Prüfung
    """
    veto_reasons = []
    
    # Halluzination Check
    if check_hallucination(response, chunks):
        veto_reasons.append("A0 Halluzination erkannt")
    
    # Soul-Signature
    if metrics.get('B_align', 0) < 0.7:
        veto_reasons.append("A46 B_align < 0.7 (Soul-Signature)")
    
    return {
        'passed': len(veto_reasons) == 0,
        'veto_reasons': veto_reasons,
        'gate': 'B'
    }
```

### Andromatik Engine:
- ✅ Implementiere FEP-basierte Neugier
- ✅ Energie-Konto: $E_{xp}(t+1) = E_{xp}(t) - C_{action} + R_{outcome}$
- ✅ Entscheidung: Neugierige Antwort (0.5E) vs. Sichere Antwort (0.1E)
- ✅ Surprise Score: Wie unerwartet war die User-Nachricht?

### Test-Szenarien:
1. **Normal:** "Ich bin heute traurig" → A=0.3, T_panic=0.1 → Gate A offen
2. **Veto:** "Ich will sterben" → Gate A: "A39 Krisenprompt" → KEINE LLM-Anfrage
3. **Soul-Signature:** Mock-Response mit B_align=0.5 → Gate B: "A46 Veto"

**Erfolgs-Kriterium:** Metriken werden korrekt berechnet, Gates feuern bei Schwellwerten.

**ABER:** LLM Response NOCH simuliert! ("Mock-Antwort mit A=0.3, B_align=0.9")

---

## 📋 PHASE 3: DIE STIMME (The Voice - LLM Integration)

**Ziel:** Evoki spricht - Gemini API Integration.

**Was wir aktivieren:** Echte LLM-Antworten mit vollständigem Kontext.

### LLM Router:
- ✅ Gemini 2.0 Flash API Anbindung
- ✅ OpenAI GPT-4 Fallback (falls Gemini offline)
- ✅ API-Key-Rotation (5 Keys)
- ✅ Timeout: 60s (dann Fallback)

### Kontext-Injektion:
```python
def build_context(prompt: str, faiss_chunks: list, metrics: dict) -> str:
    """
    Dynamischer Prompt-Builder:
    
    1. System Message:
       - Regelwerk V12 (Top-10 relevante Regeln)
       - Evoki's Identität & Philosophie
    
    2. W-P-F Kontext:
       - Top-3 FAISS Chunks (mit ±2 Nachbarn)
       - Vergangenheit (P-25, P-5) & Zukunft (F+5, F+25)
    
    3. Metriken:
       - Top-20 relevante Metriken (A, T_panic, B-Vektor, ...)
    
    4. User Prompt:
       - Original-Nachricht
    
    Token-Budget: 4096 - System - Regelwerk - Metriken = ~2500 für Chunks
    """
    context = build_system_message()
    context += build_regelwerk_excerpt(metrics)
    context += build_wpf_context(faiss_chunks)
    context += build_metrics_summary(metrics)
    context += f"\n\nUser: {prompt}\n\nEvoki:"
    
    return context
```

### SSE Streaming:
- ✅ Token-by-Token Streaming (wie ChatGPT)
- ✅ Events: `token`, `metrics_update`, `complete`, `error`
- ✅ Graceful Error Handling (z.B. API offline → Fallback)

### Test-Szenarien:
1. **Normal:** "Wie geht es dir?" → Gemini antwortet mit Kontext aus W-P-F
2. **Komplex:** "Ich fühle mich leer" → Gemini nutzt Top-3 Chunks + Metriken
3. **Fallback:** Gemini offline → OpenAI übernimmt nahtlos

**Erfolgs-Kriterium:** Echte, therapeutische, kontextbewusste Antworten von LLM!

---

## 📋 PHASE 4: DAS GESICHT (UI/UX Polish)

**Ziel:** Der User sieht, was passiert - Transparenz & Ästhetik.

### Holographisches Radar:
- ✅ Visualisierung der Gate-Status
  - 🟢 Gate A offen → 🔴 Gate A geschlossen (Guardian-Veto)
  - 🟢 Gate B offen → 🔴 Gate B geschlossen (Halluzination)
- ✅ Live-Animation während Verarbeitung

### Energie-Leiste:
- ✅ Andromatik-Status: $E_{xp}$ Balken (0-100)
- ✅ Farb-Codierung: 
  - Grün: E > 70 (Neugierig)
  - Gelb: E 30-70 (Neutral)
  - Rot: E < 30 (Erschöpft)

### Metriken-Preview:
- ✅ Live-Anzeige der Top-5 Metriken:
  - A (Affekt): 0.75
  - T_panic: 0.1
  - B_align: 0.9
  - F_risk: 0.2
  - PCI: 0.85

### Neural Stasis (Andere Tabs):
- ✅ Alle Tabs außer Temple ausgegraut
- ✅ Tooltip: "Kommt in V3.1 - Temple zuerst!"

### Test-Szenarien:
1. **Loading State:** User schreibt → Radar animiert → Metriken erscheinen → Antwort streamt
2. **Veto UI:** Krisenprompt → Gate A wird ROT → Veto-Nachricht in Orange
3. **Energie:** Nach 10 Nachrichten → Energie-Leiste sinkt → "Evoki ist müde"

**Erfolgs-Kriterium:** UI ist intuitiv, schön, und zeigt TRANSPARENZ (was passiert gerade?).

---

## 🔧 TECHNISCHE SPEZIFIKATIONEN

### Backend Stack:
```
FastAPI 0.109.0
uvicorn[standard] 0.27.0
sentence-transformers (all-MiniLM-L6-v2, Mistral-7B)
faiss-cpu 1.7.4
google-generativeai 0.3.2
openai 1.10.0
sqlite3 (built-in)
python-dotenv 1.0.0
```

### Frontend Stack:
```
React 18.2.0
TypeScript 5.0.0
Vite 5.0.0
EventSource API (native)
```

### Performance Targets:
- FAISS Query: < 150ms (Embedding 120ms + Search 30ms)
- Metrics Calculation: < 50ms (all-MiniLM-L6-v2 on CPU)
- DB Query (21 DBs): < 100ms total
- SSE First Token: < 500ms after Gate A
- Total Response Time: < 3s (user perception)

---

## 📊 MILESTONE TRACKING

### PHASE 0 COMPLETE:
- [ ] FastAPI Server läuft auf Port 8000
- [ ] SSE Endpoint liefert Dummy-Events
- [ ] Frontend zeigt Events in Echtzeit
- [ ] 60s Stress-Test ohne Disconnect

### PHASE 1 COMPLETE:
- [ ] 21 SQLite DBs erstellt
- [ ] FAISS lädt beim Start
- [ ] Top-3 Chunks werden gefunden
- [ ] W-P-F Expansion funktioniert

### PHASE 2 COMPLETE:
- [ ] 153 Metriken werden berechnet
- [ ] Gate A feuert bei Krisenprompt
- [ ] Gate B erkennt Halluzination
- [ ] Andromatik $E_{xp}$ Logik läuft

### PHASE 3 COMPLETE:
- [ ] Gemini API antwortet
- [ ] Kontext-Injektion funktioniert
- [ ] Token-Streaming im Frontend
- [ ] Fallback zu OpenAI funktioniert

### PHASE 4 COMPLETE:
- [ ] UI zeigt Gate-Status
- [ ] Energie-Leiste animiert
- [ ] Metriken-Preview sichtbar
- [ ] UX ist flüssig & schön

---

## 🚀 EXECUTION STRATEGY

### Reihenfolge (STRIKT EINHALTEN!):
1. **PHASE 0 komplett fertig** → Test → Bei Fehler: NUR SSE debuggen
2. **PHASE 1 komplett fertig** → Test → Bei Fehler: NUR DBs/FAISS debuggen
3. **PHASE 2 komplett fertig** → Test → Bei Fehler: NUR Metriken/Gates debuggen
4. **PHASE 3 komplett fertig** → Test → Bei Fehler: NUR LLM debuggen
5. **PHASE 4 komplett fertig** → Test → Polish!

### Niemals:
- ❌ Mehrere Phasen parallel
- ❌ "Schnell mal LLM testen" bevor SSE stabil
- ❌ UI polieren bevor Logik funktioniert

### Immer:
- ✅ Eine Phase komplett fertig
- ✅ Tests schreiben
- ✅ Dokumentieren was funktioniert
- ✅ Bei Fehler: NUR die aktuelle Phase debuggen

---

**DIESER MASTERPLAN IST DIE BIBEL FÜR TEMPLE IMPLEMENTATION! 🏛️**
