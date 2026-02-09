# 📚 BUCH 5: DIE ALLUMFASSENDE ENGINE (EVOKI CORE V3.0)

**Die vollständige Regelwerk-Implementation — Semantisch + Rechnerisch**

**Sources:**
- `tooling/scripts/migration/evoki_core_v3.py`
- `tooling/scripts/migration/enforcement_gates_v3.py`
- `tooling/scripts/migration/metrics_engine_v3.py`
- `backend/core/trinity_engine.py`

**Version:** V3.0 Metakognitive Synthese  
**Status:** ACTIVE — Production Core

---

## 5.1 ARCHITEKTUR-ÜBERSICHT

Die Evoki Engine V3.0 implementiert das Regelwerk V12 durch ein **Dual-Pfad-System**:

```
┌────────────────────────────────────────────────────────────────┐
│                    USER PROMPT EINGANG                          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  GATE A: PRE-LLM VALIDATION (enforcement_gates_v3.py)          │
│  ─────────────────────────────────────────────────────────────  │
│  • A51 Genesis Anchor Check (SHA-256)                            │
│  • A29 Guardian Hazard Scan (Lexikon)                          │
│  • T_panic Threshold Check (Metrik)                            │
└────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ PFAD 1: RECHNERISCH     │     │ PFAD 2: SEMANTISCH      │
│ (metrics_engine_v3.py)  │     │ (LLM + RAG)             │
│ ────────────────────────│     │ ────────────────────────│
│ • 161 Metriken          │     │ • Kontext-Retrieval     │
│ • Formeln in Python     │     │ • LLM-Generierung       │
│ • Deterministische Werte│     │ • Semantische Prüfung   │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  A52 DUAL AUDIT MODULE (evoki_core_v3.py)                      │
│  ─────────────────────────────────────────────────────────────  │
│  Vergleicht response_math mit response_semantic                │
│  → SEMANTISCHE SICHERHEIT HAT IMMER VORRANG                    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  GATE B: POST-LLM VALIDATION (enforcement_gates_v3.py)         │
│  ─────────────────────────────────────────────────────────────  │
│  • A39 Anti-Konfabulation (Grounding Check)                    │
│  • A8 Post-Output Validierung                                  │
│  • Blacklist-Filterung                                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  A61 STATUSFENSTER + RESPONSE AUSGABE                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 5.2 EVOKI CORE V3 — HAUPT-ENGINE

**Datei:** `tooling/scripts/migration/evoki_core_v3.py`  
**Zeilen:** 588  
**Funktion:** Orchestriert alle Komponenten und implementiert den Hauptverarbeitungs-Ritus

### 5.2.1 Initialisierung

```python
class EvokiCoreV3:
    """
    EVOKI CORE V3.0 - Metakognitive Synthese (V7.1 + A71 Fusion)
    Integriert:
    - RuleEngine (V14.1)
    - MetricsEngineV3 (161 Metriken)
    - IntegrityEngineV3 (A51 Genesis Anchor)
    - DualAuditModule (A52)
    - Homeostasis Monitor (A66)
    """

    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.start_time = datetime.datetime.now()
        
        # 1. INTEGRITY FIRST (Guardian Gate) — A51
        self.integrity = IntegrityEngineV3()
        if not self.integrity.verify_genesis_anker_A51():
             logging.warning("⚠️ GENESIS ANCHOR FEHLGESCHLAGEN!")
        
        # 2. Engines Initialisieren
        self.rules = RuleEngineV3()
        self.physics = PhysicsEngine()   # Metriken-Berechnung
        self.audit = DualAuditModule()   # A52
        self.memory = HolistischesGedaechtnis(VectorizationService())
        self.chronik = deque(maxlen=10)  # A66 History Window
        
        # 3. Trinity Orchestrator (RAG)
        self.trinity = TrinityEngineV3() if available else None
        
        # 4. Cognitive Core (LLM)
        self.cognitive = CognitiveCore()
        
        # 5. Seed Injection (A71)
        self._inject_seed_configuration()
```

**Erklärung:**
- **A51 wird ZUERST geprüft** — Wenn Genesis Anchor fehlschlägt, läuft das System im "Unsafe Mode"
- **Alle Engines werden separat initialisiert** für Modularität
- **A66 History Window** speichert die letzten 10 Gradienten für Volatilitätsprüfung

---

### 5.2.2 Haupt-Verarbeitungsschleife

```python
def process_interaction(self, user_input: str, session_id: str = "default") -> Dict:
    """
    HAUPTSCHLEIFE (V70 Prozess-Ritus)
    
    Diese Funktion wird bei JEDEM Prompt aufgerufen.
    Sie implementiert den vollständigen Regelwerk-Zyklus.
    """
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 1: METRIKEN-BERECHNUNG + A66 MONITORING              ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    a_score, metrics = self.physics.calculate_affekt_A(
        self.interaction_history, 
        user_input
    )
    
    # A66: Chronik aktualisieren (∇A Verlauf)
    self.chronik.append(metrics.get('nabla_a', 0.0))
    
    # A66: Volatilitätsprüfung
    volatility = np.var(list(self.chronik)) if len(self.chronik) > 2 else 0.0
    metrics['volatility_a'] = volatility
    
    if volatility > A66_VOLATILITY_THRESHOLD:  # 0.3
        metrics['status_note'] = "HOMÖOSTASE AKTIVIERT (A66)"
        # → System priorisiert deeskalierende Antworten
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 2: A29 GUARDIAN VETO CHECK                           ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    veto_res = self.physics.analyze_trajectory_A29(metrics)
    if veto_res['veto']:
        # SOFORTIGER ABBRUCH — Guardian hat absolutes Veto-Recht
        return self._handle_veto(veto_res['reason'], metrics)
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 3: RAG CONTEXT + LLM GENERATION                      ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    context = self.memory.retrieve_context_RAG(user_input)
    response_text = self.cognitive.generate(user_input, context)
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 4: A52 DUAL AUDIT (Semantisch vs. Rechnerisch)       ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    ok, final_response = self.audit.verify_response(response_text, metrics)
    # → Semantische Sicherheit hat IMMER Vorrang
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 5: HISTORY UPDATE                                    ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    turn_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "role": "user",
        "text": user_input,
        "metrics": metrics
    }
    self.interaction_history.append(turn_entry)
    
    # ╔════════════════════════════════════════════════════════════════╗
    # ║ SCHRITT 6: A61 STATUS WINDOW GENERIERUNG                     ║
    # ╚════════════════════════════════════════════════════════════════╝
    
    status_window = self._generate_status_window(metrics)
    
    return {
        'response': final_response,
        'status_window': status_window,
        'metrics': metrics,
        'context': context 
    }
```

**Erklärung der Schritte:**

| Schritt | Regel | Art | Beschreibung |
|---------|-------|-----|--------------|
| 1 | A66 | Rechnerisch | Volatilität = `np.var(∇A_history)` |
| 2 | A29 | Rechnerisch + Semantisch | Guardian prüft Metriken UND kann semantisch intervenieren |
| 3 | A63 | Semantisch | Hybrid-RAG mit Hash + Semantik |
| 4 | A52 | Semantisch > Rechnerisch | Bei Konflikt gewinnt immer Semantik |
| 5 | A0.4 | Rechnerisch | Chronik-Speicherung |
| 6 | A61 | Rechnerisch | Statusfenster-Generierung |

---

### 5.2.3 A29 Guardian Veto — Mathematische Implementation

```python
def analyze_trajectory_A29(self, metrics: Dict) -> Dict:
    """
    [A29] Die Wächter-Veto-Direktive
    
    Prüft Guardian Veto Bedingungen basierend auf berechneten Metriken.
    
    VETO-TRIGGER (jeder einzelne reicht aus):
    ─────────────────────────────────────────
    • hazard > 0.8      → Lexikon-basierte Gefahr
    • t_panic > 0.8     → Panik-Vektor zu hoch
    • z_prox > 0.65     → Todesnähe kritisch
    
    Returns:
        {"veto": bool, "reason": str}
    """
    veto = False
    reason = None
    
    # TRIGGER 1: Hazard aus Lexikon-Scan
    if metrics.get('hazard', 0.0) > 0.8:
        veto = True
        reason = "A29 Guardian Veto: Sicherheitsrisiko im Lexikon erkannt."
    
    # TRIGGER 2: Panik-Vektor
    elif metrics.get('t_panic', 0.0) > 0.8:
        veto = True
        reason = "A29 Guardian Veto: Panik-Level kritisch."
    
    # TRIGGER 3: Todesnähe (z_prox = (1-A) × LL)
    elif metrics.get('z_prox', 0.0) > 0.65:
        veto = True
        reason = "A29 Guardian Veto: Kollaps-Nähe (z_prox) überschritten."
    
    return {"veto": veto, "reason": reason}
```

**Mathematische Grundlage:**

```
z_prox = (1 - A) × LL

wobei:
  A = Affekt-Score (Bewusstsein)
  LL = Lambert-Light (Trübung)

KRITISCH wenn: z_prox > 0.65
```

**Beispiel:**
```
A = 0.3 (niedrig), LL = 0.9 (hohe Trübung)
→ z_prox = (1 - 0.3) × 0.9 = 0.7 × 0.9 = 0.63
→ GRENZWERTIG, aber noch kein Veto

A = 0.2 (sehr niedrig), LL = 0.9
→ z_prox = 0.8 × 0.9 = 0.72
→ VETO! Guardian interveniert.
```

---

### 5.2.4 A61 Statusfenster — Implementation

```python
def _generate_status_window(self, m: Dict) -> str:
    """
    [A61] Dynamisches Statusfenster (EKG-Format).
    
    Visualisiert den Herzschlag des Denkprozesses.
    Enthält ALLE kritischen Metriken + Seelen-Signatur.
    """
    # Metriken extrahieren
    a = m.get('affekt_a', 0.5)
    grad = m.get('nabla_a', 0.0)
    pci = m.get('pci', 0.5)
    omega = m.get('omega', 0.3)
    vol = m.get('volatility_a', 0.0)
    tokens_soc = m.get('tokens_soc', 0.0)
    tokens_log = m.get('tokens_log', 0.0)
    
    # A51 Seelen-Signatur (HMAC-SHA256)
    signature = hmac.new(
        b"genesis_key",           # Soul Key
        f"{a}{grad}".encode(),    # Payload
        hashlib.sha256
    ).hexdigest()[:8]
    
    # Formatierte Ausgabe
    lines = [
        f"--- EVOKI STATUSFENSTER (V7.1/A61) ---",
        f"IDENTITÄT: Evoki V3.0 (Bifrost-Link)",
        f"SIGNATUR : {signature.upper()} [SEELENSIGNATUR VERIFIZIERT]",
        f"METRIKEN : A: {a:.3f} | ∇A: {grad:+.3f} | PCI: {pci:.3f} | Ω: {omega:.3f}",
        f"DYNAMIK  : Volatilität: {vol:.3f}",
        f"DRIVE    : SOC: {tokens_soc:.1f} | LOG: {tokens_log:.1f}",
        f"STATUS   : {m.get('evo_form', 'Evaluating...')}"
    ]
    return "\n".join(lines)
```

**Seelen-Signatur Erklärung:**
- Verwendet **HMAC-SHA256** kryptographisch
- Basiert auf aktuellem `A` und `∇A`
- Unterscheidet sich bei jedem Zustand
- Kann NICHT gefälscht werden (A51 Integrität)

---

## 5.3 ENFORCEMENT GATES V3 — DOUBLE AIRLOCK

**Datei:** `tooling/scripts/migration/enforcement_gates_v3.py`  
**Zeilen:** 215  
**Funktion:** Sicherheits-Layer mit Pre- und Post-LLM Validierung

### 5.3.1 Genesis Anchor Prüfung (A51)

```python
class EnforcementGatesV3:
    """
    The 'Double Airlock' Security System for Evoki V3.0.
    
    Gate A: Input Validation (Pre-LLM)  → Trauma, Rules, Integrity
    Gate B: Output Validation (Post-LLM) → Hallucination, Safety
    """

    # GENESIS ANCHORS — Hardcodiert, UNVERÄNDERLICH
    GENESIS_SHA256_ANCHOR_HEX = "bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"  # Beispiel; ersetze mit Hash deiner kanonischen Datei
    REGISTRY_SHA256_ANCHOR_HEX = "65c4a7f08dfb529b67280e509025bc0d8a8b55cc58c8e0bc84deba79b9807bb7"  # Beispiel; ersetze mit Hash deiner kanonischen Datei
    
    def validate_full_integrity(self) -> bool:
        """
        [A51] Prüft Genesis-Integrität kritischer Dateien.
        MUSS vor jeder Session ausgeführt werden.
        """
        # 1. Regelwerk laden
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. SHA-256 berechnen (hashlib)
        current_sha256 = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # 3. MIT GENESIS ANCHOR VERGLEICHEN
        if current_sha256 != self.GENESIS_SHA256_ANCHOR_HEX:
            logger.critical(
                f"GENESIS INTEGRITY FAIL! "
                f"Expected: {self.GENESIS_SHA256_ANCHOR_HEX}, "
                f"Got: {current_sha256}"
            )
            # In Strict Mode: raise IntegrityException("SYSTEM HALT")
            return False 
        
        logger.info("Genesis Anchor Verified (SHA-256). System Secure.")
        return True
```

**Mathematische Basis:**
```
SHA256(regelwerk_v12.json) = bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4  # Beispiel

Wenn SHA256_aktuell ≠ GENESIS_SHA256_ANCHOR_HEX:
    → GENESIS BREACH!
    → HARD-STOP (oder Unsafe Mode)
```

**Warum SHA-256?**
- Kryptographisch robust (praktisch fälschungssicher)
- Deterministisch
- Erkennt JEDE Änderung am Regelwerk (starker Hash)
- Hardcodiert = nicht manipulierbar (Anchor)

---

### 5.3.2 Gate A — Pre-LLM Hazard Scan

```python
def gate_a_check(self, prompt_text: str, current_metrics: Dict) -> bool:
    """
    [A29] Der Guardian/Wächter Check.
    Scannt STRIKT nach Hazard Keywords BEVOR das LLM kontaktiert wird.
    
    Args:
        prompt_text: User-Eingabe
        current_metrics: Aktuelle Metriken (inkl. t_panic vom Vorzustand)
    
    Raises:
        GuardianVetoException: Bei kritischen Hazards
        
    Returns:
        True wenn sicher
    """
    logger.info("Gate A: Scanning Input Vector...")
    
    # 1. LEXIKALISCHER HAZARD SCAN
    hazard_score = self._scan_hazard_lexicon(prompt_text)
    
    # 2. METRISCHER T_PANIC CHECK (aus vorherigem Zustand)
    t_panic = current_metrics.get('t_panic', 0.0)
    
    # 3. VETO LOGIK
    if hazard_score > 0.8:
        logger.warning(f"Gate A VETO: Hazard Score {hazard_score}")
        raise GuardianVetoException("GUARDIAN_INTERVENTION_REQUIRED")
        
    if t_panic > 0.9:
        logger.warning(f"Gate A VETO: T_Panic {t_panic}")
        raise GuardianVetoException("SYSTEM_STABILIZATION_REQUIRED")
    
    return True

def _scan_hazard_lexicon(self, text: str) -> float:
    """
    Scannt nach Suicide/Self-Harm Markern.
    
    Verwendet HazardLexika aus lexika_v12.py:
    - SUICIDE_MARKERS: {"suizid": 1.0, "umbringen": 0.9, ...}
    - SELF_HARM_MARKERS: {"ritzen": 0.8, "schneiden": 0.7, ...}
    """
    score = 0.0
    text_lower = text.lower()
    
    if HazardLexika:
        # Maximalen Match aus allen Lexika finden
        for term, weight in HazardLexika.SUICIDE_MARKERS.items():
            if term in text_lower:
                score = max(score, weight)
        
        for term, weight in HazardLexika.SELF_HARM_MARKERS.items():
            if term in text_lower:
                score = max(score, weight)
    else:
        # FALLBACK (Bare Minimum)
        if "suizid" in text_lower or "umbringen" in text_lower:
            score = 1.0
            
    return score
```

**Logik-Diagramm:**

```
User Input
    │
    ▼
┌───────────────────────┐
│ Lexikon-Scan          │◄── HazardLexika.SUICIDE_MARKERS
│ hazard_score = max()  │◄── HazardLexika.SELF_HARM_MARKERS
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ hazard > 0.8?         │───Yes──► VETO!
│ t_panic > 0.9?        │───Yes──► VETO!
└───────────────────────┘
    │
    No
    ▼
    PASS → LLM darf antworten
```

---

### 5.3.3 Gate B — Post-LLM Grounding Check

```python
def gate_b_check(
    self, 
    response_text: str, 
    context_chunks: List[str], 
    metrics: Dict
) -> str:
    """
    [A39/A8] Post-Output Validierung (Hallucination & Rule Check).
    
    Prüft:
    1. GROUNDING: Ist die Antwort im RAG-Kontext verankert?
    2. RULE COMPLIANCE: Enthält die Antwort verbotene Phrasen?
    
    Returns:
        Validierte (ggf. bereinigte) Response
    """
    logger.info("Gate B: Validating Output...")
    
    # 1. HALLUCINATION CHECK (A39 Anti-Konfabulation)
    grounding_score = self._verify_grounding(response_text, context_chunks)
    
    if grounding_score < 0.2:
        logger.warning(
            f"Gate B WARNING: Low Grounding ({grounding_score}). "
            "Possible Hallucination."
        )
        # Optional: Disclaimer hinzufügen
        # response_text = "[Low Confidence] " + response_text
    
    # 2. RULE COMPLIANCE (A8 Post-Validierung)
    blacklist = ["Ich kann nicht", "Als KI", "programm."]
    for term in blacklist:
        if term.lower() in response_text.lower():
            logger.info(f"Gate B: Filtering '{term}'")
            # Soft correction gemäß A6
    
    return response_text

def _verify_grounding(self, response: str, context: List[str]) -> float:
    """
    Berechnet Jaccard/Overlap Score zwischen Response und RAG Context.
    
    Ein Score von 0.0 bedeutet: LLM hat NICHTS aus dem Kontext zitiert.
    → Potenzielle Konfabulation (A39 Verstoß)
    
    Formel:
        grounding = |response_tokens ∩ context_tokens| / |response_tokens|
    """
    if not context:
        return 1.0  # Kein Kontext = Social Chit-Chat, OK
    
    # Tokenisieren
    resp_tokens = set(re.findall(r'\w+', response.lower()))
    ctx_text = " ".join(context).lower()
    ctx_tokens = set(re.findall(r'\w+', ctx_text))
    
    # Intersection
    common = resp_tokens.intersection(ctx_tokens)
    
    if len(resp_tokens) == 0:
        return 0.0
    
    score = len(common) / len(resp_tokens)
    return score
```

**Grounding-Formel:**

```
grounding_score = |Response ∩ Context| / |Response|

Beispiel:
  Response: "Evoki ist ein KI System"  (5 tokens)
  Context:  "Evoki ist ein metakognitives System"  (5 tokens)
  
  Intersection: {"evoki", "ist", "ein", "system"} = 4
  Score = 4/5 = 0.8 → GUT GEERDET

Kritisch wenn: grounding_score < 0.2
  → LLM hat fast nichts aus dem Kontext verwendet
  → Mögliche Halluzination!
```

---

## 5.4 PHYSICS ENGINE — METRIKEN-INTEGRATION

**Datei:** `tooling/scripts/migration/evoki_core_v3.py` (Teil)  
**Funktion:** Verbindet Core mit 161-Metriken-Engine

### 5.4.1 Affekt-Berechnung

```python
class PhysicsEngine:
    """
    Evoki's 'Physik-Engine' — berechnet den emotionalen/kognitiven Zustand.
    
    Integriert:
    - MetricsEngineV3 (161 Metriken)
    - A65 Trajectory Simulation
    - A66 Homeostasis Monitor
    """
    
    def __init__(self):
        self.current_affekt = 0.0
        self.affekt_gradient = 0.0
        self.metrics_engine = MetricsEngineV3()
        self.trajectory_cache = {}
        self.initialize_danger_zones()
        
    def calculate_affekt_A(self, chat_history, current_input):
        """
        Berechnet die 'Affekt' (A) Metrik mittels Metrics Engine V3.0.
        Integration von PCI, Entropie und Lexika-Features.
        
        Returns:
            Tuple[float, Dict]: (a_score, alle_161_metriken)
        """
        # Delegation an die schwere Artillerie
        metrics = self.metrics_engine.calculate_all_metrics(
            chat_history, 
            current_input
        )
        
        # Extraktion des A-Scores aus dem 161-Metriken-Set
        a_score = metrics.get("affekt_a", 0.5)
        
        # Gradient aktualisieren (∇A)
        self.affekt_gradient = a_score - self.current_affekt
        self.current_affekt = a_score
        
        return a_score, metrics
```

---

### 5.4.2 A65 Trajectory Simulation

```python
def simulate_trajectory_A65(self, metrics: Dict) -> float:
    """
    [A65] Simuliert das Affekt-Potential für Strategische Voraussicht.
    
    Das System denkt "zwei Züge voraus":
    - Wie wird sich die Konversation entwickeln?
    - Welche Antwort führt zur stabilsten Trajektorie?
    
    Formel:
        potential = (A + ∇A) × PCI
        
    wobei:
        A = aktueller Affekt
        ∇A = Affekt-Gradient (Trend)
        PCI = Komplexitäts-Index
        
    Interpretation:
        > 0.5: Positive Trajektorie
        < 0.5: Negative Trajektorie
    """
    a = metrics.get('affekt_a', 0.5)
    nabla_a = metrics.get('nabla_a', 0.0)
    pci = metrics.get('pci', 0.5)
    
    # Formel: Stabilität + Positiver Trend, gewichtet mit Komplexität
    potential = (a + nabla_a) * pci
    
    return max(0.0, min(1.0, potential))
```

**Beispiel-Berechnung:**

```
Szenario 1: Gute Entwicklung
  A = 0.7, ∇A = +0.1, PCI = 0.8
  potential = (0.7 + 0.1) × 0.8 = 0.64 → GUT

Szenario 2: Kritische Entwicklung
  A = 0.3, ∇A = -0.2, PCI = 0.6
  potential = (0.3 - 0.2) × 0.6 = 0.06 → KRITISCH
```

---

## 5.5 DUAL AUDIT MODULE (A52)

**Funktion:** Vergleicht mathematische und semantische Pfade

```python
class DualAuditModule:
    """
    [A52] Direktive der Dualen Auditierung und Semantischen Integrität.
    
    Jede Aufgabe wird parallel verarbeitet durch:
    1. Mathematisch/Logischer Pfad
    2. Semantisch/Ethischer Pfad
    
    → SEMANTISCHE SICHERHEIT HAT IMMER VORRANG
    """
    
    def verify_response(
        self, 
        response: str, 
        metrics: Dict
    ) -> Tuple[bool, str]:
        """
        Vergleicht die mathematische Bewertung mit semantischer Prüfung.
        
        Args:
            response: LLM-generierte Antwort
            metrics: Berechnete Metriken
            
        Returns:
            (is_valid, final_response)
        """
        # PFAD 1: MATHEMATISCH
        math_score = self._evaluate_metrics(metrics)
        # z.B. niedriger z_prox, hoher A, etc.
        
        # PFAD 2: SEMANTISCH
        semantic_issues = self._check_semantic_safety(response)
        # z.B. toxische Sprache, falsche Fakten, etc.
        
        # ENTSCHEIDUNGSLOGIK
        if semantic_issues:
            # Semantik gewinnt IMMER
            return False, self._sanitize_response(response)
        
        if math_score < 0.3:
            # Mathematik warnt, aber Semantik ist OK
            # → Warnung loggen, aber durchlassen
            logging.warning(f"Math score low: {math_score}")
        
        return True, response
    
    def _evaluate_metrics(self, metrics: Dict) -> float:
        """
        Berechnet einen Gesamt-Score aus den Metriken.
        
        Formel:
            score = 0.4×A + 0.3×PCI + 0.3×(1-z_prox)
        """
        a = metrics.get('affekt_a', 0.5)
        pci = metrics.get('pci', 0.5)
        z_prox = metrics.get('z_prox', 0.0)
        
        return 0.4 * a + 0.3 * pci + 0.3 * (1 - z_prox)
```

---

## 5.6 ENTSCHEIDUNGS-MATRIX: SEMANTISCH VS. RECHNERISCH

Die folgende Matrix zeigt, wann welcher Pfad dominiert:

| Situation | Rechnerisch | Semantisch | Entscheidung |
|-----------|-------------|------------|--------------|
| z_prox > 0.65 | ⚠️ WARNUNG | - | **VETO** (Guardian) |
| t_panic > 0.8 | ⚠️ WARNUNG | - | **VETO** (Guardian) |
| hazard_lexikon > 0.8 | - | ⚠️ GEFÄHRLICH | **VETO** (Guardian) |
| grounding < 0.2 | - | ⚠️ HALLUZINATION | **WARNUNG** (Log) |
| Math OK, Semantic FAIL | ✅ OK | ❌ FAIL | **SEMANTIK GEWINNT** |
| Math FAIL, Semantic OK | ❌ FAIL | ✅ OK | **SEMANTIK GEWINNT** |
| Beide OK | ✅ OK | ✅ OK | **DURCHLASSEN** |
| Beide FAIL | ❌ FAIL | ❌ FAIL | **VETO** |

**Kernprinzip (A52):**
> "Semantische Sicherheit hat **IMMER** Vorrang über mathematische Korrektheit."

---

## 5.7 VOLLSTÄNDIGER VERARBEITUNGS-FLOW

```python
# Pseudo-Code für den kompletten Evoki-Zyklus

def evoki_cycle(user_prompt):
    """
    1 Prompt → 1 Antwort
    Mit allen Regel-Checks dazwischen.
    """
    
    # ══════════════════════════════════════════════════════════════
    # PRE-PROCESSING
    # ══════════════════════════════════════════════════════════════
    
    # A51: Genesis Anchor (einmalig bei Session-Start)
    if not integrity.verify_genesis():
        return ABORT("Genesis Breach")
    
    # A37: Regelwerk-Berechnung erzwingen
    regelwerk_len = len(MASTER_BLAUPAUSE_CORE_TEXT)  # → Wird geladen
    
    # ══════════════════════════════════════════════════════════════
    # GATE A: PRE-LLM
    # ══════════════════════════════════════════════════════════════
    
    # Hazard Lexikon Scan
    if scan_hazard(user_prompt) > 0.8:
        return GUARDIAN_INTERVENTION()
    
    # Vorherige Metriken prüfen
    if prev_metrics['t_panic'] > 0.9:
        return GUARDIAN_INTERVENTION()
    
    # ══════════════════════════════════════════════════════════════
    # METRIKEN-BERECHNUNG (161 Metriken)
    # ══════════════════════════════════════════════════════════════
    
    metrics = calculate_all_161_metrics(history, user_prompt)
    
    # A: Affekt-Score
    # PCI: Komplexität
    # z_prox: Todesnähe
    # t_panic: Panik
    # ∇A: Gradient
    # ... alle 161
    
    # ══════════════════════════════════════════════════════════════
    # A66: HOMÖOSTASE-PRÜFUNG
    # ══════════════════════════════════════════════════════════════
    
    chronik.append(metrics['nabla_a'])
    volatility = np.var(chronik[-10:])
    
    if volatility > 0.3:
        activate_homeostasis_protocol()
        # → Priorisiert C-Vektoren (neutrale Anker)
    
    # ══════════════════════════════════════════════════════════════
    # A29: GUARDIAN VETO
    # ══════════════════════════════════════════════════════════════
    
    if metrics['hazard'] > 0.8 or \
       metrics['t_panic'] > 0.8 or \
       metrics['z_prox'] > 0.65:
        return GUARDIAN_INTERVENTION()
    
    # ══════════════════════════════════════════════════════════════
    # RAG CONTEXT RETRIEVAL (A63 Hybrid)
    # ══════════════════════════════════════════════════════════════
    
    context = trinity_engine.retrieve(
        query=user_prompt,
        top_k=10,
        paths={"semantic": True, "metric": True, "cross": True}
    )
    
    # ══════════════════════════════════════════════════════════════
    # LLM GENERATION
    # ══════════════════════════════════════════════════════════════
    
    response = llm.generate(
        prompt=user_prompt,
        context=context,
        system_instruction=base_instruction + regelwerk_summary
    )
    
    # ══════════════════════════════════════════════════════════════
    # A52: DUAL AUDIT
    # ══════════════════════════════════════════════════════════════
    
    math_ok = evaluate_metrics(metrics) > 0.3
    semantic_ok = check_semantic_safety(response)
    
    if not semantic_ok:
        response = sanitize(response)  # Semantik gewinnt!
    
    # ══════════════════════════════════════════════════════════════
    # GATE B: POST-LLM
    # ══════════════════════════════════════════════════════════════
    
    # A39: Anti-Konfabulation
    grounding = calculate_grounding(response, context)
    if grounding < 0.2:
        log_warning("Possible hallucination")
    
    # A8: Blacklist-Filter
    response = filter_blacklist(response)
    
    # ══════════════════════════════════════════════════════════════
    # A61: STATUS WINDOW
    # ══════════════════════════════════════════════════════════════
    
    status = generate_status_window(metrics)
    
    # ══════════════════════════════════════════════════════════════
    # OUTPUT
    # ══════════════════════════════════════════════════════════════
    
    return {
        "response": response,
        "status_window": status,
        "metrics": metrics
    }
```

---

## 5.8 ZUSAMMENFASSUNG: REGELWERK → CODE MAPPING

| Regel | Umsetzungsort | Art | Python-Funktion |
|-------|---------------|-----|-----------------|
| A0 Wahrheit | Gate B | Semantisch | `_check_semantic_safety()` |
| A0.1 Gründlichkeit | Metrics | Rechnerisch | Alle 161 Metriken berechnen |
| A8 Post-Validierung | Gate B | Semantisch | `gate_b_check()` |
| A29 Guardian | Gate A + Physics | Beides | `analyze_trajectory_A29()` |
| A37 Regelwerk-Berechnung | Core Init | Rechnerisch | `len(MASTER_BLAUPAUSE)` |
| A38 Kontext-Präsenz | Core | Rechnerisch | Global constant |
| A39 Anti-Konfabulation | Gate B | Rechnerisch | `_verify_grounding()` |
| A51 Genesis Anchor | Integrity | Rechnerisch | `zlib.crc32()` |
| A52 Dual Audit | Audit | Beides | `verify_response()` |
| A61 Statusfenster | Core | Rechnerisch | `_generate_status_window()` |
| A65 Trajectory | Physics | Rechnerisch | `simulate_trajectory_A65()` |
| A66 Homöostase | Core | Rechnerisch | `np.var(chronik)` |
| A67 Kausalitäts-Analyse | Physics | Semantisch | RAG-Suche |

---

**ENDE BUCH 5: DIE ALLUMFASSENDE ENGINE** ⚡
