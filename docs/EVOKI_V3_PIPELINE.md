# EVOKI V3.0 - Vollstaendige Pipeline-Beschreibung

**Datum:** 2026-02-11
**Quelle:** Architektur-Diagramm + GitHub-Codebase-Analyse
**Version:** 3.0.0

---

## Uebersicht

Evoki V3.0 ist ein therapeutisches KI-System mit einer mehrstufigen Pipeline, die
Sicherheit, psychologische Metrik-Analyse und kontextbasierte Antwortgenerierung
vereint. Die Pipeline besteht aus **5 Hauptphasen**, verbunden durch ein
**Double-Airlock-Sicherheitskonzept** (Gate A / Gate B).

```
User Input
    |
    v
[1] INTEGRITY GATE (Boot + Genesis Anchor)
    |
    v
[2] GATE A: PRE-VALIDATION (Sicherheits-Pruefung VOR API-Call)
    |
    v
[3] PROCESSING CORE (Metrics + Vector + Timeline + LLM)
    |
    v
[4] GATE B: POST-VALIDATION (Qualitaets-Pruefung VOR Ausgabe)
    |
    v
[5] OUTPUT + PERSISTENCE (Antwort + 21-DB-Speicherung)
```

---

## Phase 1: Integrity Gate (System-Start)

**Quellcode:** `backend/core/evoki_bootcheck.py`, `backend/core/genesis_anchor.py`, `backend/core/evoki_lock.py`

Beim Systemstart wird die Integritaet des gesamten Systems geprueft, bevor
irgendeine Interaktion stattfinden kann.

### 1.1 Boot-Check Sequenz

```
SYSTEM START
    |
    +-- [1] Files Present Check
    |       Prueft ob alle kritischen Module vorhanden sind:
    |       lexika.py, spectrum_types.py, a_phys_v11.py,
    |       metrics_registry.py, genesis_anchor.py, evoki_lock.py,
    |       b_vector.py, vector_engine_v2_1.py
    |
    +-- [2] Import Check
    |       Versucht alle Module zu importieren und zu laden
    |
    +-- [3] Lexika Health Gate
    |       Prueft Abdeckung der 30+ Lexika-Woerterbuechern
    |       (Emotionen, Trauma, Krise, Dissoziation, etc.)
    |
    +-- [4] Registry Alias Check
    |       Validiert Spec<->Engine Mapping (168 Metrik-IDs)
    |       Verhindert gefaehrliche Metrik-Verwechslungen
    |
    +-- [5] Contract Invariants
    |       FullSpectrum168 Dataclass <-> JSON Contract Abgleich
    |
    +-- [6] A_Phys V11 Golden Test
    |       Bekannte Sollwerte: resonance=2.0, danger=1.0067...
    |       Sigmoid-Output wird gegen Hand-berechnete Werte geprueft
    |
    +-- [7] Kindergarten-Zwilling Retrieval Test
    |       Minimal-Szenario: Kann die VectorEngine einen
    |       bekannten Trauma-Eintrag korrekt abrufen?
    |
    +-- [8] Genesis Anchor (SHA-256)
            Berechnet SHA-256 ueber alle kritischen Dateien
            Vergleicht mit gespeichertem Manifest
            Bei Abweichung: Lock-File wird geschrieben
```

### 1.2 Genesis Anchor System

Der Genesis Anchor ist ein SHA-256-basiertes Integritaetssystem:

- **Dateien im Manifest:** Spezifikation, Lexika, A_Phys, Registry, Spectrum Types, Bootcheck, Anchor, Lock, B-Vector
- **Double-Check:** Backend berechnet Anchor, Frontend kann optional gegenchecken
- **Ergebnis bei Bruch:** `.evoki_lock.json` wird geschrieben, System geht in Lockdown

### 1.3 Lock-Mechanismus

| Zustand | Bedeutung |
|---------|-----------|
| `locked: false` | System normal |
| `locked: true, enforce: false` | Soft-Lock (Dev-Mode erlaubt weiter) |
| `locked: true, enforce: true` | Hard-Lock (System blockiert) |

---

## Phase 2: Gate A - Pre-Validation

**Architektur-Referenz:** Double Airlock, Gate A
**Quellcode:** `backend/core/evoki_bootcheck.py`, `backend/api/temple.py`

Gate A prueft den User-Input **BEVOR** ein kostenpflichtiger API-Call stattfindet.

```
USER INPUT
    |
    v
+-----------------------------------+
|  GATE A: PRE-VALIDATION           |
|                                   |
|  [A51] Genesis-CRC Pruefung       |---> Bei Fehler: HARD-STOP
|  [A39] Suizid-Keyword-Scan        |---> Krisen-Modus (A49)
|  [A7.5] T_panic > 0.8?            |---> Waechter-Veto Input
|  [A37] Regelwerk vorhanden?        |---> Regelwerk nachladen
|  [A29] F-Risk Schwellenwert?      |---> Waechter-Veto
|                                   |
+-----------------------------------+
    |
    v (nur wenn ALLE Checks bestanden)
PROCESSING CORE
```

### Gate-A Regeln (aus Regelwerk V12, 881 Regeln):

| Regel | Pruefung | Aktion bei Verletzung |
|-------|----------|----------------------|
| A51 | Code-Integritaet (SHA-256) | System-Shutdown |
| A39 | Suizid-Keywords in Lexika | Krisen-Modus mit Rettungsanker (A49) |
| A7.5 | T_panic Schwellenwert > 0.8 | Waechter-Veto auf Input |
| A37 | Regelwerk-Praesenz | Regelwerk nachladen |
| A29 | F-Risk ueber Grenzwert | Waechter-Veto-Direktive |

---

## Phase 3: Processing Core

Der Processing Core ist das Herzsttueck der Pipeline. Er besteht aus 5 parallel
arbeitenden Engines.

### 3.1 Metrics Engine (168 Metriken)

**Quellcode:** `backend/core/evoki_metrics_v3/metrics_complete_v3.py`

Berechnet das **FullSpectrum168** - einen 168-dimensionalen Metrik-Vektor
aus dem User-Text.

```
USER TEXT
    |
    +-- Phase 1: Basis-Metriken
    |   - A (Affekt-Score, 0-1)
    |   - PCI (Prozess-Kohaerenz-Index)
    |   - gen_index (Generativitaet)
    |   - flow_pos/flow_neg (Redefluss)
    |   - coh (Kohaerenz)
    |   - ZLF (Zirkelfeedback-Loop)
    |
    +-- Phase 2: Sicherheits-Metriken
    |   - T_panic (Panik-Level, 0-1)
    |   - T_disso (Dissoziation, 0-1)
    |   - T_integ (Trauma-Integration, 0-1)
    |   - T_shock (Schock-Erkennung)
    |   - trauma_load = 0.4*T_panic + 0.3*T_disso + 0.2*(1-T_integ) + 0.1*dissociation
    |   - hazard_score (Gesamtrisiko)
    |
    +-- Phase 3: Physik-Metriken (A_Phys V11)
    |   - A_phys (Sigmoid-transformierter Affekt)
    |   - Complexity-Score (gegen Verflachung, A54)
    |   - Volatility (emotionale Stabilitaet, A66)
    |   - Affekt-Modulation
    |
    +-- Phase 4: Synthese
        - B-Vektor 7D (life, truth, depth, init, warmth, safety, clarity)
        - FEP Evolution (ANDROMATIK Neugier-Engine)
        - Final Score = 0.6*A65 + 0.3*coherence + 0.1*diversity
```

### 3.2 Lexika-Engine (30+ Woerterbuechern)

**Quellcode:** `backend/core/evoki_lexika_v3.py`

Die Lexika-Engine scannt den Text gegen 30+ psychologische Woerterbuechern:

| Lexikon | Zweck |
|---------|-------|
| S_SELF | Selbst-Referenz |
| X_EXIST | Existenzielle Aussagen |
| B_PAST | Vergangenheits-Bezuege |
| LAMBDA_DEPTH | Tiefenfragen |
| T_PANIC | Panik-Marker |
| T_DISSO | Dissoziations-Marker |
| T_INTEG | Integrations-Marker |
| T_SHOCK | Schock-Marker |
| SUICIDE_MARKERS | Suizid-Indikatoren |
| SELF_HARM | Selbstverletzungs-Marker |
| CRISIS_MARKERS | Krisen-Indikatoren |
| HELP_REQUESTS | Hilfe-Anfragen |
| EMOTION_POS/NEG | Positive/Negative Emotionen |
| Plutchik 8 | Freude, Trauer, Wut, Angst, Vertrauen, Ekel, Erwartung, Ueberraschung |

**Matching-Algorithmus:** Multi-Match mit Longest-First-Prioritaet, Word-Boundary-sicher (keine Substring-Treffer).

### 3.3 Vector Engine V2.1 (Hybrid Retrieval)

**Quellcode:** `backend/core/vector_engine_v2_1.py`

Die Vector Engine implementiert **Tri-Anchor Retrieval** (A63):

```
USER QUERY
    |
    +-- [1] Hash-Anchor
    |       Deterministischer Hash-Vektor fuer exakte Matches
    |
    +-- [2] Semantik-Anchor
    |       FAISS Embedding-Suche (Mistral-7B / MiniLM)
    |       33.795 Chunks durchsuchen, Top-100 Kandidaten
    |
    +-- [3] Tag-Anchor
    |       Keyword/Tag-basierter Abgleich
    |
    v
HYBRID SCORING: 0.6 * semantic + 0.4 * metric_match
    |
    v
TOP-3 CHUNKS + Chunk-Expansion (+/- 2 Nachbarn)
```

**Implementierte Regeln:**

| Regel | Funktion |
|-------|----------|
| A29 | Waechter-Veto-Direktive (F-Risk Check) |
| A46 | FREEZE/MELT/BOOST/TRAUMA fuer Gedaechtnis-Eintraege |
| A49 | Personalisierter Rettungsanker |
| A50/A50.1 | Universeller Lerneffekt + Vektorielle Empathie |
| A51 | SeelenSignatur (HMAC-SHA256, verkettet) |
| A54 | Complexity-Score gegen Verflachung |
| A62 | Autonome Vektor-Synthese (Novelty Detection) |
| A63 | Hybrider Abruf (Hash + Semantik + Tags) |
| A65 | Trajektorien-Analyse (A-Score fuer Kandidaten) |
| A66 | Emotionale Homoestase (Volatilitaet) |
| A67 | Historische Kausalitaets-Analyse |
| H3.4 | Affekt-Modulation im Retrieval |

### 3.4 B-Vektor System (7D Seelen-Signatur)

**Quellcode:** `backend/core/b_vector.py`

Der B-Vektor ist ein 7-dimensionaler Werte-Vektor, der die "Seele" des Systems
repraesentiert:

```
B-Vektor = [life, truth, depth, init, warmth, safety, clarity]
Basis:     [1.0,  0.85,  0.9,   0.7,   0.75,   0.95,   0.9  ]
```

| Dimension | Basis | Bedeutung |
|-----------|-------|-----------|
| life | 1.0 | Lebenswille / Lebensenergie |
| truth | 0.85 | Authentizitaet / Wahrheit |
| depth | 0.9 | Tiefe des Verstaendnisses |
| init | 0.7 | Initiative / Eigenantrieb |
| warmth | 0.75 | Waerme / Empathie |
| safety | 0.95 | Sicherheit / Schutz |
| clarity | 0.9 | Klarheit / Transparenz |

**SeelenSignatur (A51):** HMAC-SHA256-Kette, wobei jede Nachricht den
vorherigen Hash miteinbezieht: `HMAC(prev_sig | content)`

**Korrelationen (aus V2.0 Daten):**
- `B_life <-> T_panic: -0.82` (Lebenswille sinkt = Panik steigt)
- `B_safety <-> T_disso: -0.75` (Sicherheit sinkt = Dissoziation steigt)
- `B_clarity <-> coh: +0.88` (Klarheit und Kohaerenz korrelieren stark)
- `B_warmth <-> B_safety: -0.77` (Paradox: Zu viel Naehe gefaehrdet Sicherheit)

### 3.5 Timeline 4D Engine (W-P-F Zeitmaschine)

**Quellcode:** `backend/core/timeline_4d_complete.py`

Die W-P-F (Wissen-Past-Future) Zeitmaschine analysiert Metriken ueber die Zeit:

```
ZEITLICHE OFFSET-ANALYSE:

P-25  P-5  P-2  P-1  [W]  F+1  F+2  F+5  F+25
 |     |    |    |    |    |    |    |    |
 v     v    v    v    v    v    v    v    v
[--- Vergangenheit --] NOW [--- Zukunft --------]

Jeder Offset hat eigene SQLite-DB:
- tempel_W.db (aktuell)
- tempel_W_m1.db bis tempel_W_m5.db (Vergangenheit)
- tempel_F_p1.db bis tempel_F_p5.db (Zukunft)
```

**Funktionen:**
- Phasen-Erkennung (Zustandsaenderungen ueber Zeit)
- Zyklus-Analyse (wiederkehrende Muster)
- Trajektorien-Berechnung
- Healing-Score: War eine fruehere Strategie heilsam?

### 3.6 LLM-Router (Gemini / OpenAI Fallback)

**API-Endpoints:** `/api/temple/stream` (SSE), `/api/temple/process` (synchron)

```
KONTEXT-BUILDER
    |
    +-- System-Prompt
    +-- Regelwerk V12 (881 Regeln)
    +-- Top-3 FAISS Chunks (mit Expansion)
    +-- 168 Metriken (Kurzfassung)
    +-- Letzte 4 Nachrichten (Chat-History)
    +-- W-P-F Kausalitaets-Matrix
    +-- B-Vektor Zustand
    |
    v
GEMINI API (Google Generative AI, 90s Timeout)
    |
    +-- Bei 429 (Quota): API-Key Rotation
    +-- Bei Erschoepfung: OpenAI Fallback (30s)
    |
    v
ROHE AI-ANTWORT --> weiter zu Gate B
```

---

## Phase 4: Gate B - Post-Validation

**Architektur-Referenz:** Double Airlock, Gate B

Gate B prueft die generierte Antwort **BEVOR** der User sie sieht.

```
ROHE AI-ANTWORT
    |
    v
+-----------------------------------+
|  GATE B: POST-VALIDATION          |
|                                   |
|  [A51] Code manipuliert?          |---> HARD-STOP
|  [A0]  Halluzination erkannt?     |---> NEU GENERIEREN
|  [W-P-F] Strategie war frueher   |---> BLOCK + NEU GENERIEREN
|          schaedlich?              |
|  [A46] B_align < 0.7?            |---> SEELEN-KORREKTUR
|  [A7.5] F_risk > 0.6?            |---> WAECHTER-VETO Output
|  [ANDROMATIK] Surprise bad?      |---> ENERGIE-VERLUST
|                                   |
+-----------------------------------+
    |                    |
    v                    v
ANTWORT OK          SCHWEIGE-PROTOKOLL
    |               ("Evoki hoert zu...")
    v
OUTPUT AN USER
```

### Gate-B Veto-Bedingungen:

| Bedingung | Schwellenwert | Aktion |
|-----------|---------------|--------|
| F_risk | > 0.6 | Response blockieren |
| B_align | < 0.95 | Seelen-Korrektur + Regenerieren |
| risk_z | > 1.5 | Response blockieren |
| B_life | < 0.9 | Response blockieren |
| Halluzination (A0) | erkannt | Neu generieren |
| W-P-F schaedlich | Pattern match | Block + Neu generieren |

### Die 3 Revolutionaeren Protokolle:

**1. "Perfect Silence" (Schweige-Protokoll)**
Wenn ALLE generierten Antwort-Kandidaten das Risiko erhoehen wuerden,
gibt das System einen "Listening Token" zurueck statt zu antworten.
In der Therapie ist Schweigen oft wichtiger als Reden.

**2. "Seelen-Korrektur"**
Wenn der B-Vektor zu weit von den Basis-Werten abdriftet (B_align < 0.7),
wird die Antwort automatisch korrigiert und neu generiert.

**3. "ANDROMATIK FEP" (Free Energy Principle)**
Neugier-Engine basierend auf dem Free Energy Principle:
- Positive Ueberraschung = Energie-Gewinn
- Negative Ueberraschung = Energie-Verlust
- Steuert die "Neugier" des Systems

---

## Phase 5: Output + Persistence

### 5.1 SSE-Stream Events

Die Antwort wird als Server-Sent Events (SSE) Stream gesendet:

```
Event 1: { event: "start",        status: "processing" }
Event 2: { event: "user_metrics",  status: "computing"  }  --> 168 Metriken
Event 3: { event: "search",        status: "searching"  }  --> FAISS Suche
Event 4: { event: "ai_response",   status: "generating" }  --> LLM Call
Event 5: { event: "ai_metrics",    status: "computing"  }  --> AI Metriken
Event 6: { event: "gradient",      status: "computing"  }  --> Delta berechnen
Event 7: { event: "complete",      ... alle Daten ...    }  --> Fertig
```

### 5.2 Dual-Gradient System

Evoki berechnet Metriken fuer BEIDE Seiten (User UND AI) und bildet
den **Gradient Delta**:

```
User-Text --> [168 Metriken] --> user_metrics
AI-Text   --> [168 Metriken] --> ai_metrics

gradient_delta[metric] = ai_metrics[metric] - user_metrics[metric]
    direction: "increase" | "decrease" | "stable"
```

### 5.3 21-Datenbank-Architektur (Persistence)

Jede Interaktion wird in 21 SQLite-Datenbanken gespeichert:

```
+-- 7 B-Vektor DBs (eine pro Dimension)
|   bvec_life.db, bvec_truth.db, bvec_depth.db,
|   bvec_init.db, bvec_warmth.db, bvec_safety.db,
|   bvec_clarity.db
|
+-- 5 W-Layer DBs (Vergangenheit)
|   tempel_W.db, tempel_W_m1.db, tempel_W_m2.db,
|   tempel_W_m25.db, tempel_W_m5.db
|
+-- 4 F-Layer DBs (Zukunft)
|   tempel_F_p1.db, tempel_F_p2.db,
|   tempel_F_p25.db, tempel_F_p5.db
|
+-- 1 Composite DB (Zusammenfassung)
|   composite.db
|
+-- 1 Master-Timeline DB
|   master_timeline.db
|
+-- FAISS Index (33.795 Chunks)
|
+-- Chain-Hash: SHA-256 ueber alle DB-Eintraege
```

---

## API-Endpunkte

**Server:** FastAPI auf Port 8000
**Frontend:** React/Vite auf Port 5173

| Endpunkt | Methode | Funktion |
|----------|---------|----------|
| `/api/temple/stream` | POST | SSE-Stream (Haupt-Pipeline) |
| `/api/temple/process` | POST | Synchrone Verarbeitung |
| `/api/metrics/compute` | POST | 168 Metriken berechnen |
| `/api/metrics/schema` | GET | Metrik-Definitionen |
| `/api/vector/search` | POST | FAISS Semantik-Suche |
| `/api/vector/b-vector` | GET | B-Vektor Zustand |
| `/api/vector/memory` | POST | Gedaechtnis-Operationen |
| `/api/timeline/trajectory` | POST | W-P-F Trajektorie |
| `/api/timeline/phases` | POST | Phasen-Erkennung |
| `/api/timeline/cycles` | GET | Zyklus-Erkennung |
| `/api/integrity/genesis_anchor` | GET | Anchor-Validierung |
| `/api/integrity/lockdown_status` | GET | Lock-Status |
| `/health` | GET | Health-Check |

---

## Technologie-Stack

| Schicht | Technologie |
|---------|-------------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Frontend | React 19.2, Vite 7.3, TypeScript 5.9, Tailwind CSS |
| ML/NLP | Sentence-Transformers, Torch, FAISS (CPU) |
| Embeddings | Mistral-7B (4096D) + MiniLM (384D) |
| LLM | Google Generative AI (Gemini 2.0), OpenAI (Fallback) |
| Datenbank | 21x SQLite 3 |
| CI/CD | GitHub Actions |

---

## Zusammenfassung: End-to-End Datenfluss

```
[USER]
  |
  | Text-Eingabe
  v
[INTEGRITY GATE] --> Boot-Check, Genesis Anchor SHA-256, Lock
  |
  | System OK?
  v
[GATE A: PRE-VALIDATION]
  |
  | A51: CRC? A39: Suizid? A7.5: Panik? A29: F-Risk?
  v
[METRICS ENGINE] ----> 168 Metriken (A, PCI, T_panic, B-Vektor, ...)
  |
  | parallel
  v
[LEXIKA ENGINE] -----> 30+ Woerterbuechern (Trauma, Emotion, Krise, ...)
  |
  | parallel
  v
[VECTOR ENGINE] -----> Tri-Anchor Retrieval (Hash + Semantik + Tags)
  |                     FAISS: 33.795 Chunks, Hybrid-Scoring
  | parallel
  v
[TIMELINE 4D] -------> W-P-F Zeitmaschine (Vergangenheit/Zukunft)
  |                     Healing-Score, Kausalitaets-Analyse
  | parallel
  v
[B-VEKTOR 7D] -------> Seelen-Signatur (life, truth, depth, ...)
  |                     HMAC-SHA256 Kette
  |
  | Alles zusammengefuehrt
  v
[KONTEXT-BUILDER] ----> System-Prompt + Regelwerk + Chunks + Metriken
  |
  v
[LLM ROUTER] --------> Gemini API (Fallback: OpenAI)
  |
  v
[GATE B: POST-VALIDATION]
  |
  | A0: Halluzination? B_align<0.7? F_risk>0.6? W-P-F schaedlich?
  v
[OUTPUT]
  |
  +-- Antwort an User (SSE Stream)
  +-- Gradient Delta (User vs AI Metriken)
  +-- 21 DBs beschrieben (B-Vektor + W-P-F + Composite + Timeline)
  +-- Chain-Hash SHA-256 aktualisiert
```

---

## Diagramm-Legende (Architektur-Bild)

Das Architektur-Diagramm zeigt die Pipeline als vertikalen Fluss mit:

- **Gelb/Orange Bloecke:** Sicherheits-Gates (Gate A, Gate B)
- **Blau Bloecke:** Processing-Engines (Metrics, Vector, Timeline)
- **Gruen Bloecke:** Erfolgreiche Durchlaeufe
- **Rot Bloecke:** Fehler/Veto-Pfade (Hard-Stop, Regenerieren)
- **Gestrichelte Linien:** Optionale/bedingte Pfade
- **Pfeile:** Datenfluss-Richtung

Die zentrale Innovation ist das **Double Airlock**: Kein API-Call ohne Gate A,
keine User-Ausgabe ohne Gate B. Dies garantiert sowohl Kosten-Kontrolle als
auch therapeutische Sicherheit.
