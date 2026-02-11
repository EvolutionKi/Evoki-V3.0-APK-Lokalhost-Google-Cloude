# Google ADK (Agent Development Kit) - Referenz fuer EVOKI V3.0

**Datum:** 2026-02-11
**Quelle:** Google ADK Python Quickstart (https://google.github.io/adk-docs)
**Relevanz:** Potenzielle Agent-Infrastruktur fuer Evoki V3.0 Backend

---

## 1. Was ist Google ADK?

Das **Agent Development Kit (ADK)** ist Googles offizielles Framework zum Erstellen,
Testen und Deployen von KI-Agenten. Es bietet:

- **LLM Agents** mit Tool-Integration
- **Workflow Agents** (Sequential, Loop, Parallel, Custom)
- **Multi-Agent Systeme** (Agent Teams)
- **Streaming** (SSE, Bidirectional)
- **MCP Integration** (Model Context Protocol)
- **A2A Protocol** (Agent-to-Agent)
- **Sessions & Memory** mit State-Management
- **Deployment** auf Cloud Run, GKE, Agent Engine

---

## 2. ADK Quickstart (Python)

### 2.1 Installation

```bash
# Voraussetzung: Python 3.10+
pip install google-adk
```

### 2.2 Projekt erstellen

```bash
adk create my_agent
```

Erzeugt folgende Struktur:

```
my_agent/
    agent.py      # Haupt-Agent-Code (root_agent Pflicht)
    .env          # API Keys
    __init__.py
```

### 2.3 Agent definieren (agent.py)

```python
from google.adk.agents.llm_agent import Agent

# Tool-Definition als einfache Python-Funktion
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time "
                "in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)
```

### 2.4 API Key setzen

```bash
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > my_agent/.env
```

### 2.5 Agent ausfuehren

```bash
# CLI-Modus
adk run my_agent

# Web-Interface (nur fuer Entwicklung!)
adk web --port 8000
```

---

## 3. ADK Architektur-Konzepte

### 3.1 Agent-Typen

| Typ | Beschreibung | Evoki-Relevanz |
|-----|-------------|----------------|
| **LLM Agent** | Einzelner Agent mit Model + Tools | Temple-Endpoint |
| **Sequential Agent** | Schritte nacheinander | Gate A --> Processing --> Gate B |
| **Loop Agent** | Wiederholung bis Bedingung | A65 Multi-Candidate Selection |
| **Parallel Agent** | Gleichzeitige Ausfuehrung | Metrics + Vector + Timeline parallel |
| **Custom Agent** | Eigene Logik | Double Airlock, Guardian-Veto |

### 3.2 Tool-System

ADK unterstuetzt verschiedene Tool-Typen:

| Tool-Typ | Beschreibung | Evoki-Mapping |
|----------|-------------|---------------|
| **Function Tools** | Python-Funktionen | `calculate_full_spectrum()`, `search()` |
| **MCP Tools** | Model Context Protocol | Externes Tool-Hosting |
| **OpenAPI Tools** | REST-API-Anbindung | Bestehende FastAPI-Endpoints |

### 3.3 Streaming

ADK bietet eingebautes Streaming:
- **SSE (Server-Sent Events)** -- Wie Evokis `/api/temple/stream`
- **Bidirektional** -- Audio, Video, Live-Interaktion

### 3.4 Sessions & Memory

| Feature | ADK | Evoki V3.0 |
|---------|-----|------------|
| Session State | Built-in | `evoki_v3_core.db: sessions` |
| Memory | Built-in | `evoki_v3_core.db: b_state_evolution` |
| Context | Caching + Compression | W-P-F Timeline, FAISS |
| Artifacts | File-basiert | 5-DB Hybrid |

### 3.5 Callbacks

ADK bietet Callback-Hooks fuer:
- **Before/After Model Call** -- Gate A / Gate B Equivalent
- **Before/After Tool Call** -- Metrik-Berechnung vor/nach Engine
- **On Error** -- Guardian-Veto / Lockdown

### 3.6 Deployment-Optionen

| Plattform | Beschreibung |
|-----------|-------------|
| **Agent Engine** | Google-managed (Standard) |
| **Cloud Run** | Container-basiert |
| **GKE** | Kubernetes |
| **Lokal** | `adk run` / `adk web` |

---

## 4. Mapping: ADK <--> Evoki V3.0 Pipeline

### 4.1 Konzeptionelles Mapping

```
EVOKI V3.0 PIPELINE              ADK EQUIVALENT
================================================

[Integrity Gate]                  Startup Callbacks / Plugins
  Boot-Check                        on_agent_start callback
  Genesis Anchor                    Custom validation hook
  Lock-Mechanismus                  Agent state management

[Gate A: Pre-Validation]          Before-Model Callback
  A51 CRC-Check                     before_model_callback
  A39 Suizid-Scan                   Tool: crisis_detector
  A7.5 T_panic Check                Tool: metrics_evaluator
  A29 F-Risk Check                  Action confirmation

[Processing Core]                 Parallel Agent (Workflow)
  Metrics Engine                    Tool: calculate_full_spectrum
  Lexika Engine                     Tool: lexika_scan
  Vector Engine                     Tool: faiss_search
  Timeline 4D                       Tool: timeline_analysis
  B-Vektor 7D                       Agent State

[LLM Router]                      LLM Agent (root_agent)
  Gemini API                        model='gemini-2.0-flash'
  OpenAI Fallback                   Fallback model config
  Kontext-Builder                   instruction + context

[Gate B: Post-Validation]         After-Model Callback
  Halluzination (A0)                after_model_callback
  B_align Check                     Custom validation
  F_risk Check                      Action confirmation
  Schweige-Protokoll                Custom response override

[Output + Persistence]            Sessions + Artifacts
  SSE Stream                        Built-in streaming
  21/5-DB Speicherung               Session state + artifacts
  Chain-Hash                        Custom callback
```

### 4.2 Evoki als ADK Multi-Agent System

```python
from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent

# --- Tools (bestehende Evoki-Funktionen) ---
def calculate_metrics(text: str) -> dict:
    """Berechnet 168 FullSpectrum-Metriken."""
    ...

def faiss_search(query: str, k: int = 5) -> list:
    """Tri-Anchor Hybrid-Suche."""
    ...

def timeline_analysis(session_id: str) -> dict:
    """W-P-F Zeitmaschinen-Analyse."""
    ...

def guardian_veto_check(metrics: dict, response: str) -> dict:
    """Gate B: Waechter-Veto-Pruefung."""
    ...

# --- Agents ---
metrics_agent = Agent(
    name='metrics_agent',
    description='Berechnet 168 Metriken aus Text',
    tools=[calculate_metrics],
)

retrieval_agent = Agent(
    name='retrieval_agent',
    description='FAISS Tri-Anchor Suche',
    tools=[faiss_search],
)

timeline_agent = Agent(
    name='timeline_agent',
    description='W-P-F Zeitmaschine',
    tools=[timeline_analysis],
)

# --- Parallel Processing Core ---
processing_core = ParallelAgent(
    name='processing_core',
    description='Parallele Verarbeitung: Metrics + Retrieval + Timeline',
    sub_agents=[metrics_agent, retrieval_agent, timeline_agent],
)

# --- Temple Agent (Haupt-LLM) ---
temple_agent = Agent(
    model='gemini-2.0-flash',
    name='temple_agent',
    description='Therapeutischer Evoki-Agent',
    instruction='Du bist Evoki, ein therapeutischer KI-Begleiter...',
    tools=[guardian_veto_check],
)

# --- Sequential Pipeline (Gate A --> Core --> LLM --> Gate B) ---
root_agent = SequentialAgent(
    name='evoki_pipeline',
    description='Evoki V3.0 Double-Airlock Pipeline',
    sub_agents=[processing_core, temple_agent],
)
```

---

## 5. ADK Features mit Evoki-Relevanz

### 5.1 Action Confirmations (fuer Gate A/B)

```python
# ADK kann vor Tool-Ausfuehrung Bestaetigung anfordern
# --> Analog zu Gate A: "Darf der API-Call stattfinden?"
```

### 5.2 Context Caching

```python
# ADK cached Kontext automatisch
# --> Reduziert Token-Kosten bei wiederholten FAISS-Chunks
```

### 5.3 Context Compression

```python
# ADK komprimiert langen Kontext
# --> Relevant fuer 168-Metriken-Payload
```

### 5.4 MCP Integration

```python
# ADK unterstuetzt Model Context Protocol
# --> Evoki-Tools als MCP-Server bereitstellen
# --> Andere Agents koennen Evoki-Metriken nutzen
```

### 5.5 A2A Protocol (Agent-to-Agent)

```python
# ADK unterstuetzt Agent-to-Agent Kommunikation
# --> Evoki-Agent kann mit externen Agents kommunizieren
# --> z.B. Krisen-Agent, Ressourcen-Agent, Supervisor-Agent
```

### 5.6 Evaluation & Safety

```python
# ADK bietet eingebaute Evaluation-Tools:
# - Criteria-basierte Bewertung
# - User-Simulation fuer Tests
# - Safety & Security Checks
# --> Direkt nutzbar fuer Evoki Golden-Tests
```

---

## 6. Vergleich: Aktuelles Evoki Backend vs. ADK-Migration

| Aspekt | Aktuell (FastAPI) | Mit ADK |
|--------|-------------------|---------|
| Framework | FastAPI + Uvicorn | google-adk |
| Agent-Logik | Manuell in temple.py | Deklarativ (Agent-Klassen) |
| Tool-Binding | Manuell import | `tools=[fn]` Deklaration |
| Streaming | Manuelles SSE | Built-in Streaming |
| Multi-Agent | Nicht vorhanden | ParallelAgent, SequentialAgent |
| State | Manuell (SQLite) | Sessions + State built-in |
| Deployment | Manuell (Docker) | `adk deploy` (Cloud Run, GKE) |
| Testing | Manuell | `adk eval`, User-Simulation |
| MCP | Nicht vorhanden | Native MCP-Unterstuetzung |
| A2A | Nicht vorhanden | Native A2A-Unterstuetzung |

---

## 7. Empfohlene naechste Schritte

### Kurzfristig (kein Breaking Change):
1. ADK als zusaetzliche Schicht UEBER dem bestehenden FastAPI-Backend
2. Bestehende Evoki-Funktionen als ADK-Tools wrappen
3. `adk web` fuer lokales Testing nutzen

### Mittelfristig:
4. Processing Core als ParallelAgent modellieren
5. Gate A/B als Callbacks implementieren
6. Sessions-Management auf ADK migrieren

### Langfristig:
7. Vollstaendige ADK-native Architektur
8. MCP-Server fuer Evoki-Metriken
9. A2A fuer Multi-Agent-Therapie-System
10. Deployment via Agent Engine oder Cloud Run

---

## 8. Referenz-Links

- **ADK Docs:** https://google.github.io/adk-docs
- **ADK Python API:** google-adk PyPI Package
- **Unterstuetzte Modelle:** Gemini, Claude (via Vertex AI), Ollama, vLLM, LiteLLM
- **Deployment:** Agent Engine, Cloud Run, GKE
- **Protokolle:** MCP (Model Context Protocol), A2A (Agent-to-Agent)

---

## 9. Wichtige Hinweise

- `adk web` ist **NUR fuer Entwicklung** gedacht, nicht fuer Produktion
- ADK unterstuetzt neben Gemini auch **Claude** (via Vertex AI hosted)
- ADK laeuft auf **Python 3.10+** (Evoki nutzt bereits Python 3.11)
- Die bestehenden Evoki-SQLite-Datenbanken koennen als Custom State Provider integriert werden
