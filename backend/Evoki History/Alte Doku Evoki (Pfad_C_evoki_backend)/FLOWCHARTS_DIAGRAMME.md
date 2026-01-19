```mermaid
flowchart TD
    Start([Google Takeout HTML<br/>73.03 MB]) --> Extract[REGEX EXTRACTION<br/>html_forensic_extractor_v2.py]
    
    Extract --> Parse{Parse HTML}
    Parse --> Pattern[REGEX Pattern Match<br/>Eingegebener Prompt: ...]
    Pattern --> Decode[HTML Decode<br/>html.unescape]
    Decode --> Normalize[Unicode Normalize<br/>xa0 → space]
    Normalize --> Clean[Whitespace Cleanup]
    Clean --> Sort[Chronological Sort<br/>datetime.strptime]
    Sort --> Generate[Generate TXT Files<br/>YYYY/MM/DD/Prompt_N_speaker.txt]
    
    Generate --> Files[(21,987 TXT Files<br/>VectorRegs_FORENSIC/)]
    
    Files --> QuickPath[Quick Analysis Path]
    Files --> DeepPath[Deep Analysis Path]
    
    QuickPath --> Quick[blitz_analyse.py<br/>Sample n=106]
    Quick --> QuickReport[DATENQUALITÄT_BERICHT.txt<br/>Readiness: 65/100]
    
    DeepPath --> Deep[analyse_daten_v2.py<br/>Full Scan]
    Deep --> Segment[Segment Quartiles<br/>S1/S2/S3/S4]
    Segment --> Stats[Per-Segment Stats<br/>Mean, Median, StdDev]
    Stats --> Compare[Quick vs Forensic Δ]
    Compare --> DeepReport[ANALYSE_BERICHT.txt + JSON<br/>Readiness: 90/100]
    
    QuickReport --> Notebook[DEEP_ANALYSE_v1.ipynb<br/>Interactive Analysis]
    DeepReport --> Notebook
    
    Notebook --> Cell1[Load Data<br/>JSON Parsing]
    Cell1 --> Cell2[Quick vs Forensic<br/>Comparison Table]
    Cell2 --> Cell3[Segment Analysis<br/>Detail Tables]
    Cell3 --> Cell4[Interaction Density<br/>21,987 files scan]
    Cell4 --> Cell5[Monthly Density<br/>Bar Chart]
    Cell5 --> Cell6[Daily Heatmap<br/>Weekday × Hour]
    Cell6 --> Cell7[Embedding Compare<br/>386D vs 1536D]
    Cell7 --> Cell8[Semantic Validation<br/>n=1000 sample]
    Cell8 --> Cell9[Word Distribution<br/>User vs AI]
    Cell9 --> Cell10[Final Verdict]
    
    Cell10 --> Archive[TIEFENANALYSE_ARCHIV_v1.md<br/>Complete Documentation]
    
    Archive --> Ready([READY FOR VECTORIZATION ✅])
    
    Ready --> Next1[Embedding Generation<br/>Sentence-BERT / OpenAI]
    Ready --> Next2[Vector Database<br/>ChromaDB / Pinecone]
    Ready --> Next3[Semantic Search<br/>Brain Integration]
    
    style Start fill:#e1f5ff
    style Extract fill:#fff4e1
    style Files fill:#e8f5e9
    style QuickReport fill:#fff9c4
    style DeepReport fill:#fff9c4
    style Notebook fill:#f3e5f5
    style Archive fill:#fce4ec
    style Ready fill:#c8e6c9
```

# FLOWCHART: Datenverarbeitungs-Pipeline

**Legende:**
- 🔵 **Blau:** Eingabedaten
- 🟡 **Gelb:** Extraktionsprozess
- 🟢 **Grün:** Datenspeicherung
- 🟡 **Gelb (hell):** Analyseberichte
- 🟣 **Lila:** Interaktive Analyse
- 🔴 **Rosa:** Archivierung
- 🟢 **Grün (hell):** Finaler Status

---

```mermaid
graph LR
    A[HTML] -->|REGEX| B[21,987 TXT]
    B -->|Quick n=106| C[65/100]
    B -->|Deep Full| D[90/100]
    C --> E[Notebook]
    D --> E
    E -->|21 Cells| F[Archive]
    F --> G[READY ✅]
    
    style A fill:#e1f5ff
    style B fill:#e8f5e9
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#f3e5f5
    style F fill:#fce4ec
    style G fill:#c8e6c9
```

# MINI-FLOWCHART: Simplified Pipeline

---

```mermaid
gantt
    title Analyse-Timeline (Execution)
    dateFormat  YYYY-MM-DD
    section Extraktion
    HTML → TXT (13s)           :a1, 2025-12-06, 13s
    section Quick Analysis
    Blitzanalyse (6s)          :a2, after a1, 6s
    section Deep Analysis
    Forensic Scan (6s)         :a3, after a1, 6s
    section Interactive
    Notebook Execute (8s)      :a4, after a3, 8s
    section Archiv
    Dokumentation (Manual)     :a5, after a4, 1d
```

# GANTT: Execution Timeline

**Total Runtime:** ~27 Sekunden (automatisiert)

---

```mermaid
pie title Monatliche Verteilung (21,987 Einträge)
    "Juli (8,941)" : 40.7
    "März (3,156)" : 14.4
    "Oktober (2,718)" : 12.4
    "April (2,589)" : 11.8
    "Mai (1,987)" : 9.0
    "Juni (1,254)" : 5.7
    "Februar (1,342)" : 6.1
```

# PIE CHART: Monatliche Aktivität

**Peak:** Juli 2025 (40.7% aller Daten)

---

```mermaid
graph TD
    subgraph Segment 1
    S1[Feb-Jul<br/>5,496 Dateien<br/>Ø 163 Wörter<br/>σ 312]
    end
    
    subgraph Segment 2
    S2[Jul-Jul<br/>5,497 Dateien<br/>Ø 214 Wörter<br/>σ 453]
    end
    
    subgraph Segment 3
    S3[Jul-Okt<br/>5,497 Dateien<br/>Ø 127 Wörter<br/>σ 335]
    end
    
    subgraph Segment 4
    S4[Okt-Okt<br/>5,497 Dateien<br/>Ø 237 Wörter<br/>σ 932]
    end
    
    S1 -->|+31%| S2
    S2 -->|-41%| S3
    S3 -->|+87%| S4
    
    S4 -.->|Current| Peak[PEAK COMPLEXITY<br/>Max: 43,165 Wörter]
    
    style S1 fill:#e1f5ff
    style S2 fill:#fff4e1
    style S3 fill:#e8f5e9
    style S4 fill:#fce4ec
    style Peak fill:#ffcdd2
```

# SEGMENT EVOLUTION: Chronologische Entwicklung

**Trend:** Moderate → Intensive → Konsolidierung → **EXPLOSION**

---

```mermaid
graph LR
    subgraph User
    U[Ø 44 Wörter<br/>Median 25]
    end
    
    subgraph AI
    A[Ø 328 Wörter<br/>Median 205]
    end
    
    U -->|7.5x länger| A
    
    style U fill:#e1f5ff
    style A fill:#f3e5f5
```

# USER vs. AI: Wort-Ratio

**Interpretation:** Klassisches Q&A-Pattern (kurze Frage → ausführliche Antwort)

---

```mermaid
sequenceDiagram
    participant HTML as Google Takeout
    participant Extractor as REGEX Extractor
    participant Files as 21,987 TXT
    participant Quick as Quick Analysis
    participant Deep as Deep Analysis
    participant Notebook as Jupyter Notebook
    participant Archive as Archive MD
    
    HTML->>Extractor: 73.03 MB HTML
    Extractor->>Files: Parse & Generate
    Files->>Quick: Sample n=106
    Files->>Deep: Full Scan
    Quick->>Notebook: 65/100 Readiness
    Deep->>Notebook: 90/100 Readiness + Segments
    Notebook->>Archive: Interactive Analysis
    Archive->>Archive: Complete Documentation
    Archive-->>User: READY ✅
```

# SEQUENCE DIAGRAM: Datenfluss

---

```mermaid
mindmap
  root((TIEFENANALYSE))
    Quick Analysis
      Sample n=106
      Basic Stats
      65/100 Readiness
    Deep Analysis
      Full Scan 21,987
      4 Segments
      90/100 Readiness
    Interaction Density
      Monthly Bar Chart
      Daily Heatmap
      Peak: Juli 2025
    Embedding Compare
      386D Current
      384D Sentence-BERT
      1536D OpenAI
    Semantic Validation
      100% Speaker
      100% Timestamps
      86% Satzzeichen
    Final Verdict
      READY ✅
      Next: Embeddings
      Next: Vector DB
```

# MINDMAP: Analysestruktur

---

**Erstellt:** 2025-12-06  
**Quelle:** DEEP_ANALYSE_v1.ipynb  
**Format:** Mermaid Diagrams  
**Status:** PRODUCTION-READY ✅
