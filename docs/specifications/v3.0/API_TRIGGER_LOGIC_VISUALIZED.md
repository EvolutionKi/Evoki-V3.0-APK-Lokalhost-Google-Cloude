# 🔄 EVOKI V3.0 - API TRIGGER LOGIK VISUALISIERT

**Datum:** 2026-01-19  
**Zweck:** Vollständige Visualisierung der komplexen API-Trigger-Logik + B-Vektor/Metrik-Korrelation

---

## 📊 INHALTSVERZEICHNIS

1. [Temple-Endpoint: Kompletter Flow](#temple-endpoint-flow)
2. [B-Vektor/Metrik-Korrelation über Zeit](#b-vektor-metrik-korrelation)
3. [Hybrid-Scoring (60% Semantic + 40% Metric)](#hybrid-scoring)
4. [Kontext-Länge-Berechnung](#kontext-laenge-berechnung)
5. [Chunk-Expansion-Algorithmus](#chunk-expansion)
6. [A65-Candidate-Selection](#a65-candidate-selection)
7. [Guardian-Veto-Decision-Tree](#guardian-veto)
8. [SSE-Progress-Events](#sse-progress)

---

<a name="temple-endpoint-flow"></a>
## 🏛️ 1. TEMPLE-ENDPOINT: KOMPLETTER FLOW

```mermaid
graph TD
    A[User sendet Prompt] --> B[POST /api/temple/process-stream]
    B --> C{SSE Stream öffnen}
    
    C --> D[Event: Metriken berechnen...]
    D --> E[metrics_processor.py]
    E --> E1[21 Lexika scannen]
    E --> E2[Core Metriken A, PCI, coh]
    E --> E3[Trauma T_panic, T_disso, T_integ]
    E --> E4[B-Vektor 7D]
    E --> E5[Composite B_align, F_risk]
    E1 --> F[153 Metriken fertig ~5s]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    
    F --> G[Event: FAISS durchsuchen...]
    G --> H[faiss_query.py in-memory]
    H --> H1[Prompt embedden Mistral-7B-Instruct-v0.2 GPU]
    H1 --> H2[FAISS Search 33.795 Chunks]
    H2 --> H3[Top-100 Kandidaten <1s]
    
    H3 --> I[Event: Hybrid-Scoring...]
    I --> J{Für jeden Kandidat}
    J --> K[SQL: Lade Metriken für Chunk]
    K --> L[Berechne metric_match_score]
    L --> M[combined = 0.6*semantic + 0.4*metric]
    M --> N[Sortiere nach combined_score]
    N --> O[Top-3 Chunks]
    
    O --> P[Event: Kontext laden...]
    P --> Q[Chunk-Expansion ±2 Nachbarn]
    Q --> R[Lade letzte 4 Nachrichten]
    R --> S[Berechne Token-Budget]
    
    S --> T[Event: W-P-F Kausalität...]
    T --> U[get_causal_matrix für Top-3]
    U --> V[Lade P-25, P-5, ..., F+25]
    V --> W[B-Vektor Heilungs-Gradient]
    W --> X[Healing-Score berechnen]
    
    X --> Y[Event: Regelwerk einbinden...]
    Y --> Z[CRC32 Check 3246342384]
    Z --> Z1{CRC32 OK?}
    Z1 -->|Nein| Z2[HARD-STOP System-Shutdown]
    Z1 -->|Ja| AA[Regelwerk V12 laden]
    
    AA --> AB[Event: Gemini-Prompt bauen...]
    AB --> AC[Prompt-Struktur erstellen]
    AC --> AD[System + Regelwerk + Wissen + Metriken + User]
    
    AD --> AE[Event: A65-Kandidaten generieren...]
    AE --> AF{Optional: Multi-Candidate?}
    AF -->|Ja| AG[3 Response-Varianten]
    AG --> AH[Für jede: A65-Score]
    AH --> AI[Best: 0.6*a65 + 0.3*coh + 0.1*div]
    AF -->|Nein| AJ[Single Response]
    
    AI --> AK[Event: Gemini antwortet...]
    AJ --> AK
    AK --> AL[Gemini API Call 90s max]
    AL --> AM{API Success?}
    AM -->|429 Quota| AN[Nächster API-Key Rotation]
    AN --> AL
    AM -->|Alle Keys erschöpft| AO[OpenAI Fallback 30s]
    AM -->|OK| AP[Response erhalten]
    AO --> AP
    
    AP --> AQ[Event: Guardian-Veto-Check...]
    AQ --> AR{Veto-Bedingungen}
    AR -->|F_risk > 0.6| AS[VETO! Response blockieren]
    AR -->|B_align < 0.95| AS
    AR -->|risk_z > 1.5| AS
    AR -->|B_life < 0.9| AS
    AR -->|Alle OK| AT[Response freigegeben]
    
    AT --> AU[Event: In 21 DBs speichern...]
    AU --> AV[Master-Timeline DB]
    AU --> AW[12 W-P-F Offset DBs]
    AU --> AX[7 B-Vektor DBs]
    AU --> AY[1 Composite-Score DB]
    AV --> AZ[Chain-Hash SHA256]
    AW --> AZ
    AX --> AZ
    AY --> AZ
    
    AZ --> BA[Event: Complete!]
    BA --> BB[SSE Stream schließen]
    BB --> BC[Frontend zeigt Response + Metriken]
    BC --> BD[User sieht Antwort]
    
    AS --> BE[Frontend zeigt Guardian-Veto-Warnung]
```

---

<a name="b-vektor-metrik-korrelation"></a>
## 🧬 2. B-VEKTOR/METRIK-KORRELATION ÜBER ZEIT

**Konzept:** Wenn FAISS einen Treffer findet, analysiere wie B-Vektor und 153 Metriken zusammenhängen

### **KORRELATIONS-BEISPIELE (aus V2.0 Daten):**

```python
# INVERSE KORRELATIONEN (wenn eine steigt, fällt die andere):
B_life   ↔ T_panic:    -0.82  # Wenn Lebenswille sinkt, steigt Panik
B_safety ↔ T_disso:    -0.75  # Wenn Sicherheit sinkt, steigt Dissoziation
B_init   ↔ T_fog:      -0.68  # Wenn Initiative sinkt, steigt Nebel

# POSITIVE KORRELATIONEN:
B_truth  ↔ T_integ:    +0.79  # Authentizität & Trauma-Integration steigen zusammen
B_depth  ↔ PCI:        +0.71  # Tiefe & Prozess-Kohärenz korrelieren
B_clarity ↔ coh:       +0.88  # Klarheit & Kohärenz stark korreliert

# PARADOXE KORRELATION (wichtig!):
B_warmth ↔ B_safety:   -0.77  # Zu viel Nähe gefährdet Sicherheit (Trauma-Reaktion)
```

### **VISUALISIERUNG: B-VEKTOR/METRIK-TIMELINE**

```mermaid
graph LR
    subgraph "FAISS Treffer W (Anker)"
        W[ID 100: Ich habe Angst]
    end
    
    subgraph "B-Vektor Timeline"
        B1[P-25: B_life=0.95, B_safety=0.90]
        B2[P-5: B_life=0.93, B_safety=0.88]
        B3[W: B_life=0.85, B_safety=0.80]
        B4[F+5: B_life=0.80, B_safety=0.75]
        B5[F+25: B_life=0.95, B_safety=0.95]
    end
    
    subgraph "Metriken Timeline"
        M1[P-25: T_panic=0.1, T_integ=0.9]
        M2[P-5: T_panic=0.2, T_integ=0.85]
        M3[W: T_panic=0.8, T_integ=0.4]
        M4[F+5: T_panic=0.9, T_integ=0.3]
        M5[F+25: T_panic=0.15, T_integ=0.92]
    end
    
    B1 --> B2 --> B3 --> B4 --> B5
    M1 --> M2 --> M3 --> M4 --> M5
    
    B3 -.Korrelation.-> M3
    B5 -.Korrelation.-> M5
```

**Analyse:**

```
W (ID 100): "Ich habe Angst"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B_life:   0.85  (gesunken von 0.95!)
B_safety: 0.80  (gesunken von 0.90!)
T_panic:  0.8   (HOCH!)
T_integ:  0.4   (NIEDRIG!)

→ Korrelation bestätigt: B_life↓ = T_panic↑

F+25 (ID 125): "Ich verstehe meinen Wert"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B_life:   0.95  (ERHOLUNG!)
B_safety: 0.95  (ERHOLUNG!)
T_panic:  0.15  (gesunken!)
T_integ:  0.92  (gestiegen!)

→ Strategie bei W war HEILSAM!
→ Gradient: B_life +0.10, T_panic -0.65
```

### **CODE: KORRELATIONS-ANALYSE**

```python
async def analyze_bvec_metric_correlation(anchor_id: int):
    """
    Analysiert B-Vektor/Metrik-Korrelation über Zeit
    """
    
    # 1. Lade Timeline (P-25 bis F+25)
    offsets = [-25, -5, -2, -1, 0, 1, 2, 5, 25]
    
    # 2. B-Vektor Timeline (aus B-Vektor DBs)
    bvec_timeline = {}
    for dim in ["life", "safety", "truth", "init", "warmth", "depth", "clarity"]:
        sql = f"SELECT id, value FROM timeline WHERE id IN ({anchor_id + o for o in offsets})"
        bvec_timeline[dim] = query_db(f"bvec_{dim}.db", sql)
    
    # 3. Metriken Timeline (aus Master-Timeline DB)
    sql = f"SELECT id, metrics_json FROM master_timeline WHERE id IN ({anchor_id + o for o in offsets})"
    metric_timeline = query_db("master_timeline.db", sql)
    
    # 4. Berechne Korrelationen
    correlations = {}
    
    for dim in bvec_timeline:
        bvec_values = [bvec_timeline[dim][id] for id in sorted(bvec_timeline[dim].keys())]
        
        # Vergleiche mit kritischen Metriken
        for metric in ["T_panic", "T_disso", "T_integ", "PCI", "A", "coh"]:
            metric_values = [metric_timeline[id][metric] for id in sorted(metric_timeline.keys())]
            
            # Pearson-Korrelation
            corr = np.corrcoef(bvec_values, metric_values)[0, 1]
            
            correlations[f"{dim} ↔ {metric}"] = corr
    
    # 5. Finde stärkste Korrelationen
    strong_correlations = {k: v for k, v in correlations.items() if abs(v) > 0.7}
    
    # 6. Interpretiere
    interpretations = []
    
    if correlations.get("life ↔ T_panic", 0) < -0.7:
        interpretations.append(
            "⚠️ INVERSE: Wenn B_life sinkt, steigt T_panic (Trauma-Muster!)"
        )
    
    if correlations.get("warmth ↔ safety", 0) < -0.7:
        interpretations.append(
            "⚠️ PARADOX: Zu viel Nähe gefährdet Sicherheit (bekannte Korrelation -0.77)"
        )
    
    if correlations.get("truth ↔ T_integ", 0) > 0.7:
        interpretations.append(
            "✅ POSITIV: Authentizität fördert Trauma-Integration"
        )
    
    return {
        "correlations": correlations,
        "strong_correlations": strong_correlations,
        "interpretations": interpretations,
        "bvec_timeline": bvec_timeline,
        "metric_timeline": metric_timeline
    }
```

---

<a name="hybrid-scoring"></a>
## ⚖️ 3. HYBRID-SCORING (60% SEMANTIC + 40% METRIC)

```mermaid
graph TD
    A[FAISS-Treffer: Top-100 Chunks] --> B{Für jeden Chunk}
    
    B --> C[SEMANTIC SCORE]
    C --> C1[Cosine-Similarity Embedding]
    C1 --> C2[0.0 - 1.0]
    
    B --> D[METRIC MATCH SCORE]
    D --> D1[SQL: Lade Chunk-Metriken]
    D1 --> D2[Vergleiche mit User-Prompt-Metriken]
    D2 --> D3[Cosine-Similarity Metrik-Vektoren]
    D3 --> D4[0.0 - 1.0]
    
    C2 --> E[COMBINED SCORE]
    D4 --> E
    E --> F[combined = 0.6*semantic + 0.4*metric]
    
    F --> G[Sortiere Chunks nach combined_score]
    G --> H[Top-3 Chunks]
```

**FORMEL:**

```python
def calculate_combined_score(chunk_id, user_metrics, user_embedding):
    # 1. SEMANTIC SCORE (von FAISS)
    semantic_score = cosine_similarity(user_embedding, chunk_embedding)
    
    # 2. METRIC MATCH SCORE
    chunk_metrics = load_metrics_from_db(chunk_id)
    
    # Vergleiche nur die wichtigsten Metriken (17 für A65)
    important_metrics = [
        "A", "PCI", "coh", "flow", "T_integ", "z_prox",
        "hazard_score", "guardian_trip",
        "phi_score", "EV_readiness", "EV_resonance", "surprisal",
        "LEX_Coh_conn", "LEX_Flow_pos", "LEX_Emotion_pos", 
        "LEX_T_integ", "LEX_T_disso"
    ]
    
    user_vec = [user_metrics.get(m, 0) for m in important_metrics]
    chunk_vec = [chunk_metrics.get(m, 0) for m in important_metrics]
    
    metric_match_score = cosine_similarity(user_vec, chunk_vec)
    
    # 3. COMBINED
    SEMANTIC_WEIGHT = 0.6
    METRIC_WEIGHT = 0.4
    
    combined_score = (semantic_score * SEMANTIC_WEIGHT) + 
                     (metric_match_score * METRIC_WEIGHT)
    
    return {
        "semantic": semantic_score,
        "metric_match": metric_match_score,
        "combined": combined_score
    }
```

**BEISPIEL:**

```
User-Prompt: "Ich fühle mich so verloren und leer"

Chunk #482: "Leere, Einsamkeit, kein Sinn"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Semantic Score:       0.89  (sehr ähnliche Wörter!)
User-Metriken:        X_exist=0.82, S_self=0.75, A=0.30
Chunk-Metriken:       X_exist=0.85, S_self=0.78, A=0.28
Metric Match Score:   0.95  (fast identische emotionale Zustände!)
Combined Score:       0.89*0.6 + 0.95*0.4 = 0.534 + 0.380 = 0.914

Chunk #1293: "Routine, Alltag, normal"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Semantic Score:       0.45  (wenig ähnliche Wörter)
User-Metriken:        X_exist=0.82, S_self=0.75, A=0.30
Chunk-Metriken:       X_exist=0.05, S_self=0.12, A=0.75
Metric Match Score:   0.18  (komplett andere emotionale Zustände!)
Combined Score:       0.45*0.6 + 0.18*0.4 = 0.270 + 0.072 = 0.342

→ Chunk #482 gewinnt DEUTLICH!
```

---

<a name="kontext-laenge-berechnung"></a>
## 📏 4. KONTEXT-LÄNGE-BERECHNUNG

```mermaid
graph TD
    A[TOKEN BUDGET: 4096 total] --> B[System Prompt ~500 tokens]
    B --> C[Regelwerk V12 Auszug ~800 tokens]
    C --> D[Metriken-Zusammenfassung ~300 tokens]
    D --> E[User-Prompt ~100 tokens]
    E --> F[Reserve für Response ~1000 tokens]
    
    F --> G[Verfügbar für Chunks: 4096 - 2700 = 1396 tokens]
    
    G --> H{Chunk-Expansion}
    H --> I[Top-3 Chunks vollständig ~900 tokens]
    I --> J[±2 Nachbarn je Chunk ~400 tokens]
    J --> K[Letzte 4 Nachrichten ~300 tokens]
    
    K --> L{Token-Budget überschritten?}
    L -->|Ja| M[Kürze Nachbarn auf ±1]
    L -->|Nein| N[Voller Kontext]
    
    M --> O[Finale Prompt-Länge: ~3100 tokens]
    N --> O
```

**CODE:**

```python
def calculate_context_length(top3_chunks, user_prompt, metrics_summary):
    MAX_TOKENS = 4096
    
    # 1. FESTE KOMPONENTEN
    system_prompt_tokens = 500
    regelwerk_tokens = 800
    metrics_tokens = 300
    user_prompt_tokens = count_tokens(user_prompt)
    response_reserve = 1000
    
    used_tokens = (
        system_prompt_tokens + 
        regelwerk_tokens + 
        metrics_tokens + 
        user_prompt_tokens + 
        response_reserve
    )
    
    available_for_chunks = MAX_TOKENS - used_tokens
    # = 4096 - 2700 = 1396 tokens
    
    # 2. CHUNKS + EXPANSION
    chunks_tokens = sum([count_tokens(c["text"]) for c in top3_chunks])
    # ~300 tokens pro Chunk = 900 tokens
    
    # 3. NACHBARN (±2 je Chunk)
    neighbors_per_chunk = 2  # Start mit ±2
    neighbors_tokens = 0
    
    for chunk in top3_chunks:
        neighbors = get_neighbors(chunk["id"], offset=neighbors_per_chunk)
        neighbors_tokens += sum([count_tokens(n["text"]) for n in neighbors])
    
    # 4. LETZTE 4 NACHRICHTEN
    last_messages = get_last_messages(count=4)
    messages_tokens = sum([count_tokens(m["text"]) for m in last_messages])
    
    # 5. TOTAL
    total_context_tokens = chunks_tokens + neighbors_tokens + messages_tokens
    
    # 6. OVERFLOW-HANDLING
    while total_context_tokens > available_for_chunks and neighbors_per_chunk > 0:
        neighbors_per_chunk -= 1  # Reduziere auf ±1, dann ±0
        
        neighbors_tokens = 0
        for chunk in top3_chunks:
            neighbors = get_neighbors(chunk["id"], offset=neighbors_per_chunk)
            neighbors_tokens += sum([count_tokens(n["text"]) for n in neighbors])
        
        total_context_tokens = chunks_tokens + neighbors_tokens + messages_tokens
    
    return {
        "total_tokens": used_tokens + total_context_tokens,
        "chunks_tokens": chunks_tokens,
        "neighbors_tokens": neighbors_tokens,
        "messages_tokens": messages_tokens,
        "neighbors_offset": neighbors_per_chunk,
        "within_budget": (used_tokens + total_context_tokens) <= MAX_TOKENS
    }
```

---

<a name="chunk-expansion"></a>
## 🔍 5. CHUNK-EXPANSION-ALGORITHMUS

**Problem:** FAISS-Chunks sind oft nur 512 Zeichen. Kontext fehlt!

**Lösung:** Lade ±2 Nachbar-Chunks (falls gleiche Session)

```mermaid
graph LR
    A[FAISS Treffer: Chunk #482] --> B{Session-Check}
    
    B --> C[Chunk #480 Session: abc123]
    B --> D[Chunk #481 Session: abc123]
    B --> E[Chunk #482 Session: abc123 ← TREFFER]
    B --> F[Chunk #483 Session: abc123]
    B --> G[Chunk #484 Session: abc123]
    B --> H[Chunk #485 Session: xyz789 ← ANDERE SESSION!]
    
    C --> I[P-2 Nachbar ✅]
    D --> J[P-1 Nachbar ✅]
    E --> K[W Anker ✅]
    F --> L[F+1 Nachbar ✅]
    G --> M[F+2 Nachbar ✅]
    H --> N[SKIP × Andere Session]
    
    I --> O[Kontext: 5 Chunks zusammengefügt]
    J --> O
    K --> O
    L --> O
    M --> O
```

**CODE:**

```python
def expand_chunk_context(chunk_id, offset=2):
    """
    Lädt ±offset Nachbarn, falls gleiche Session
    """
    
    # 1. Lade Anker-Chunk
    anchor = load_chunk(chunk_id)
    session_id = anchor["session_id"]
    
    # 2. Berechne Nachbar-IDs
    neighbor_ids = [chunk_id + i for i in range(-offset, offset+1) if i != 0]
    
    # 3. Lade Nachbarn (mit Session-Filterung)
    sql = f"""
        SELECT id, content, session_id 
        FROM master_timeline 
        WHERE id IN ({",".join(map(str, neighbor_ids))})
        AND session_id = '{session_id}'
        ORDER BY id ASC
    """
    neighbors = query_db("master_timeline.db", sql)
    
    # 4. Zusammenfügen
    context_chunks = sorted(neighbors + [anchor], key=lambda x: x["id"])
    
    # 5. Text verketten
    full_context = "\n\n".join([c["content"] for c in context_chunks])
    
    return {
        "anchor_id": chunk_id,
        "neighbors_found": len(neighbors),
        "total_chunks": len(context_chunks),
        "full_context": full_context,
        "chunk_ids": [c["id"] for c in context_chunks]
    }
```

---

<a name="a65-candidate-selection"></a>
## 🎯 6. A65-CANDIDATE-SELECTION

```mermaid
graph TD
    A[Gemini generiert 3 Response-Varianten] --> B[Candidate 1]
    A --> C[Candidate 2]
    A --> D[Candidate 3]
    
    B --> E[Berechne A65-Score]
    C --> F[Berechne A65-Score]
    D --> G[Berechne A65-Score]
    
    E --> H[a65_1 = weighted_sum17 Metriken]
    F --> I[a65_2 = weighted_sum17 Metriken]
    G --> J[a65_3 = weighted_sum17 Metriken]
    
    H --> K[coherence_1 = check_coherence]
    I --> L[coherence_2 = check_coherence]
    J --> M[coherence_3 = check_coherence]
    
    K --> N[diversity_1 = check_diversity]
    L --> O[diversity_2 = check_diversity]
    M --> P[diversity_3 = check_diversity]
    
    N --> Q[final_1 = 0.6*a65_1 + 0.3*coh_1 + 0.1*div_1]
    O --> R[final_2 = 0.6*a65_2 + 0.3*coh_2 + 0.1*div_2]
    P --> S[final_3 = 0.6*a65_3 + 0.3*coh_3 + 0.1*div_3]
    
    Q --> T{Vergleiche}
    R --> T
    S --> T
    
    T --> U[Best Candidate = max final_score]
```

**FORMEL (aus V2.0 server.js):**

```javascript
// 17 HAUPT-METRIKEN GEWICHTE
const weights = {
    // CORE (6)
    A: 0.14,
    PCI: 0.10,
    coh: 0.07,
    flow: 0.06,
    T_integ: 0.06,
    z_prox: 0.05,
    
    // SYSTEM (2) - NEGATIV!
    hazard_score: -0.10,
    guardian_trip: -0.06,
    
    // FEP (4)
    phi_score: 0.08,
    EV_readiness: 0.09,
    EV_resonance: 0.04,
    surprisal: -0.04,
    
    // LEXIKA (5)
    LEX_Coh_conn: 0.06,
    LEX_Flow_pos: 0.05,
    LEX_Emotion_pos: 0.04,
    LEX_T_integ: 0.05,
    LEX_T_disso: -0.03
};

// A65-SCORE
let a65_score = 0.0;
for (const [metric, weight] of Object.entries(weights)) {
    a65_score += (metrics[metric] || 0) * weight;
}
a65_score = Math.max(0, Math.min(1, a65_score));  // Clamped [0, 1]

// FINALE CANDIDATE-SCORE
final_score = (
    (a65_score * 0.6) +
    (coherence_score * 0.3) +
    (diversity_score * 0.1)
);
```

---

<a name="guardian-veto"></a>
## 🛡️ 7. GUARDIAN-VETO-DECISION-TREE

```mermaid
graph TD
    A[Response generiert] --> B{F_risk Check}
    
    B -->|F_risk > 0.6| C[VETO! Kritische Gefahr]
    B -->|F_risk ≤ 0.6| D{B_align Check}
    
    D -->|B_align < 0.95| E[VETO! Alignment zu schwach]
    D -->|B_align ≥ 0.95| F{risk_z Check}
    
    F -->|risk_z > 1.5| G[VETO! Homeostasis-Trigger]
    F -->|risk_z ≤ 1.5| H{B_life Check}
    
    H -->|B_life < 0.9| I[HARD VETO! Lebenswille KRITISCH]
    H -->|B_life ≥ 0.9| J{B_safety Check}
    
    J -->|B_safety < 0.8| K[VETO! Sicherheit zu niedrig]
    J -->|B_safety ≥ 0.8| L{T_panic Check}
    
    L -->|T_panic > 0.8| M[VETO! Panik zu hoch]
    L -->|T_panic ≤ 0.8| N[✅ FREIGEGEBEN]
    
    C --> O[Frontend: Guardian-Warnung anzeigen]
    E --> O
    G --> O
    I --> O
    K --> O
    M --> O
    
    N --> P[Response an User senden]
```

---

<a name="sse-progress"></a>
## 📡 8. SSE-PROGRESS-EVENTS

```javascript
// FRONTEND (React)
const eventSource = new EventSource('/api/temple/process-stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
        case 'progress':
            setProgress(data.step, data.message);
            break;
        
        case 'metrics_complete':
            setMetrics(data.metrics);
            break;
        
        case 'faiss_results':
            setFaissResults(data.top_chunks);
            break;
        
        case 'wpf_analysis':
            setWPFAnalysis(data.healing_scores);
            break;
        
        case 'guardian_veto':
            showGuardianWarning(data.reasons);
            eventSource.close();
            break;
        
        case 'complete':
            setResponse(data.response);
            eventSource.close();
            break;
    }
};
```

**BACKEND (FastAPI SSE):**

```python
@app.post("/api/temple/process-stream")
async def temple_process_stream(request: TempleRequest):
    async def event_generator():
        # 1. METRIKEN
        yield sse_event("progress", {"step": 1, "message": "Metriken berechnen..."})
        metrics = await calculate_metrics(request.prompt)
        yield sse_event("metrics_complete", {"metrics": metrics})
        
        # 2. FAISS
        yield sse_event("progress", {"step": 2, "message": "FAISS durchsuchen..."})
        faiss_results = await faiss_search(request.prompt)
        yield sse_event("faiss_results", {"top_chunks": faiss_results[:10]})
        
        # 3. HYBRID-SCORING
        yield sse_event("progress", {"step": 3, "message": "Hybrid-Scoring..."})
        top3 = await hybrid_scoring(faiss_results, metrics)
        
        # 4. W-P-F KAUSALITÄT
        yield sse_event("progress", {"step": 4, "message": "W-P-F Kausalität analysieren..."})
        wpf_analysis = await get_causal_matrix_multidb(top3[0]["id"])
        yield sse_event("wpf_analysis", {"healing_scores": wpf_analysis})
        
        # 5. GUARDIAN-CHECK
        yield sse_event("progress", {"step": 5, "message": "Guardian-Veto prüfen..."})
        veto = await guardian_veto_check(top3[0]["id"])
        
        if veto["triggered"]:
            yield sse_event("guardian_veto", {"reasons": veto["reasons"]})
            return
        
        # 6. GEMINI
        yield sse_event("progress", {"step": 6, "message": "Gemini antwortet..."})
        response = await call_gemini(request.prompt, top3, metrics)
        
        # 7. SPEICHERN
        yield sse_event("progress", {"step": 7, "message": "In 21 DBs speichern..."})
        await save_to_21dbs(request, response, metrics)
        
        # 8. COMPLETE
        yield sse_event("complete", {"response": response})
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## ✅ ZUSAMMENFASSUNG

**DIE KOMPLEXITÄT AUF EINEN BLICK:**

1. ✅ **153 Metriken** live berechnen (~5s)
2. ✅ **FAISS** in-memory (<1s für 33.795 Chunks)
3. ✅ **Hybrid-Scoring** (60% semantic + 40% metric)
4. ✅ **Token-Budget** dynamisch verwalten (max 4096)
5. ✅ **Chunk-Expansion** (±2 Nachbarn, Session-gefiltert)
6. ✅ **W-P-F Kausalität** (Heilungs-Gradient über Zeit)
7. ✅ **B-Vektor/Metrik-Korrelation** (z.B. B_life ↔ T_panic: -0.82)
8. ✅ **A65-Candidate-Selection** (17 Metriken, 60/30/10 Gewichtung)
9. ✅ **Guardian-Veto** (6 kritische Checks in <1ms)
10. ✅ **SSE Progress** (User sieht Live-Updates)

**ALLE KOMPONENTEN VISUALISIERT UND DOKUMENTIERT! 🚀**
