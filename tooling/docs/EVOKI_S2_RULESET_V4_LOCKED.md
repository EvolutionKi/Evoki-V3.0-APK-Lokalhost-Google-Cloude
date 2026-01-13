# EVOKI / SYNAPSE — S2 STATUS WINDOW PROTOCOL (V4.0-LOCKED)

**Status:** LOCKED (Policy)
**Implementierungsstand:** kompatibel mit „Deterministic V4.0 (Hardened)“ im Repo (atomarer Writer, Watcher-Persistenz, backend-authoritative Hash/Time, Verify recompute).
**Wichtige Klarstellung:** V4.0 bezeichnet hier **Determinismus der Persistenz-Pipeline**, nicht zwingend eine Änderung der Feldnamen. Das Schema bleibt inhaltlich „3.0“, die Pipeline ist „V4.0“.

---

## 0) Begriffe und Rollen (Normativ)

* **Agent:** erzeugt den Status Window **Draft** (semantische Felder, Plan/Reflection, Trigger-Intent).
* **Writer:** schreibt den Draft **atomar** nach `tooling/data/synapse/status/pending_status.json`.
* **Watcher:** erkennt Änderungen (inkl. atomarem Replace) und ruft `status_history_manager.py add ...` auf.
* **Backend / History Manager:** stempelt Zeit, erzwingt Chronos, generiert Salt+Hash, setzt finalen `window_hash`, validiert Kette.
* **MCP:** optionaler Kanal (Tools/Resources). In V4.0 ist Persistenz standardmäßig **Watcher-basiert**; MCP-Poll-Monitor ist **aus** (gated), um Doppelwrites zu vermeiden.

---

## 1) RULE 1 — S2: STATUS WINDOW ENFORCEMENT (CRITICAL | BLOCKING | AUTO)

**Jede Antwort** muss mit einem **Status Window JSON** beginnen. Dieser Block ist der „persistente Teil“; alles nachfolgende ist ephemer.

**Sequenz (nicht verhandelbar):**

1. **Status Window JSON (Draft)**
2. **Antworttext** (z. B. „AI denkt…“)
3. **Trigger** (Writer → pending file), damit Watcher persistiert

---

## 2) Schema (Status Window Draft — Agent Output)

Der Agent liefert ein **Draft-Objekt** mit folgenden Feldern (siehe Verantwortlichkeiten). Der Draft kann placeholders in **systemkontrollierten Feldern** enthalten (siehe Rule 7/8).

**Kanonische Struktur (lesbar; JSON-Feldreihenfolge ist für Hashing irrelevant):**

```json
{
  "step_id": "...",
  "cycle": "X/5",
  "time_source": "metadata (STRICT_SYNC): AUTO",
  "goal": "...",
  "inputs": { ... },
  "actions": [ ... ],
  "risk": [ ... ],
  "rule_tangency": { "tangency_detected": false, "notes": "...", "checked_rules": [ ... ] },
  "reflection_curve": { "delta": "...", "correction": "...", "next": "..." },
  "output_plan": [ ... ],
  "window_type": "planner|execution|verification",
  "schema_version": "3.0",
  "window_source": "backend_generated",
  "confidence": 0.0,
  "system_versions": { },
  "cycle_backend_controlled": true,
  "critical_summary": { },
  "project_awareness": { },
  "window_hash": "PLACEHOLDER_BACKEND",
  "prev_window_hash": "AUTO",
  "mcp_trigger": { "action": "save_to_history", "target": "status_history_manager.py", "enabled": true }
}
```

**Hinweis zur „mcp_trigger als letztes Feld“-Forderung:**
JSON-Objekt-Reihenfolge ist technisch nicht verlässlich. Für Menschen/Prompt-Parsing: **drucke** `mcp_trigger` als letztes Feld. Für Hashing ist Reihenfolge ohnehin egal (kanonische Serialisierung).

---

## 3) Field Responsibilities (V4.0-konsistent)

### 3.1 Agent MUST Fill (BLOCKING, wenn fehlt)

Diese Felder müssen **inhaltlich** vom Agent kommen:

* `goal` (string)
* `inputs` (object)
* `actions` (array)
* `risk` (array) *(leer erlaubt, Feld muss vorhanden sein)*
* `rule_tangency` (object: mindestens `tangency_detected`, `notes`; empfohlen: `checked_rules`)
* `reflection_curve` (object: `delta`, `correction`, `next`)
* `output_plan` (array)
* `window_type` ∈ {`planner`, `execution`, `verification`}
* `confidence` ∈ [0.0, 1.0]

### 3.2 Agent MUST Provide (Konstanten, BLOCKING bei Abweichung)

Diese Felder müssen vorhanden sein und konstante Werte haben:

* `schema_version` = `"3.0"`
* `window_source` = `"backend_generated"`
* `cycle_backend_controlled` = `true`

### 3.3 Agent MAY Provide (Draft/Prestate)

* `step_id`, `cycle`: müssen vorhanden sein. Wenn Backend-State nicht verfügbar: setze explizit `step_id="unknown"` und `cycle="0/5"` und **markiere RED** (siehe Rule 9 Failure Mode).

### 3.4 Agent MUST NOT Fake (BLOCKING als Policy)

Agent/Client darf **keine Wahrheit** vortäuschen in Feldern, die vom Backend autoritativ gesetzt werden:

* `time_source` → darf `"AUTO"` sein, wird überschrieben
* `mcp_trigger.timestamp` → nicht setzen (oder `"AUTO"`), wird überschrieben
* `window_hash` → **niemals** final liefern (siehe Rule 7)

---

## 4) MCP Provides / System Auto-Fills (Autoritativ)

Diese Felder werden systemseitig gesetzt oder überschrieben (wo vorhanden):

* `time_source` = `metadata (STRICT_SYNC): <utc-iso>`
* `mcp_trigger.timestamp` = `<utc-iso>`
* `prev_window_hash` wird bei `"AUTO"/PLACEHOLDER` auf Chain-Head gesetzt
* `window_hash` wird final berechnet (Salt+Timestamp) und in `status_window` zurückgeschrieben
* `critical_summary`, `project_awareness`, `system_versions` können optional befüllt werden (nicht Blocker, wenn leer)

---

## 5) RULE 5 — Trigger & Persistenzpfad (CRITICAL | BLOCKING)

Der Trigger ist **physisch** das Schreiben des Drafts nach:

`C:\Evoki V3.0 APK-Lokalhost-Google Cloude\tooling\data\synapse\status\pending_status.json`

**Normativer Ablauf:**

1. Writer schreibt atomar (tempfile+fsync+rename/replace)
2. Watcher erkennt Replace/Create/Modify
3. Watcher ruft History-Manager via CLI auf (`add --file pending_status.json --source pending_status_auto`)
4. History wächst um exakt **+1** und Hash/Chain sind verifizierbar

---

## 6) RULE 6 — Anti-Race (CRITICAL | BLOCKING)

Es darf immer nur **ein** Persistenz-Consumer aktiv sein:

* Entweder **Watcher** (Default),
* oder MCP **pending monitor** (nur wenn Watcher aus; gated via Env).

**Verboten:** Watcher + MCP monitor gleichzeitig → Risiko Doppelwrite.

---

## 7) RULE 7 — Hash Truth (CRITICAL | BLOCKING)

**Unmöglichkeits-Schutz (mathematisch):**
Der finale `window_hash` ist backend-authoritative und nutzt Random-Salt. Der Agent kann ihn **nicht** korrekt vorhersagen.

**Daher gilt:**

* Draft muss enthalten: `window_hash = "PLACEHOLDER_BACKEND"`
* Persisted Entry muss enthalten: `window_hash = <64-char lowercase sha256 hex>`
* `prev_window_hash` im Draft darf `"AUTO"` sein; persisted wird korrekt gesetzt.

---

## 8) RULE 8 — Validation Rules (BLOCKING vs WARNING)

### BLOCKING (Antwort / Draft wird abgelehnt)

* Kein Status Window
* Missing: `goal`, `inputs`, `actions`, `rule_tangency`, `reflection_curve`, `output_plan`, `window_type`, `confidence`, `mcp_trigger`
* Falsche Typen
* `window_type` nicht in {planner, execution, verification}
* `confidence` außerhalb [0.0, 1.0]
* `mcp_trigger.enabled` ≠ true oder `mcp_trigger.action/target` fehlt

### WARNING (geloggt, aber zulässig)

* `risk` leer (aber Feld muss existieren)
* `system_versions/critical_summary/project_awareness` leer

---

## 9) RULE 9 — Persistence Health Gate (CRITICAL | BLOCKING)

Vor jeder Antwort muss mindestens eine Route **grün** sein:

* **Route A (Default):** Watcher läuft und sieht pending writes
* **Route B:** `status_history_manager.py add` manuell ausführbar
* **Route C:** MCP `save_status` Tool verfügbar (optional)
* **Route D:** MCP pending monitor (nur wenn Watcher aus)

**Wenn keine Route verfügbar:**

* `critical_summary.status = "RED"`
* `confidence = 0.0`
* `risk` enthält `"Persistence offline"`
* `output_plan` enthält `"Start watcher / restore persistence route"`
* Antwort ist **BLOCKING** (keine inhaltliche Arbeit ohne Persistenz)

---

## 10) RULE 10 — No Placeholder Lie (BLOCKING)

Placeholders sind **nur** erlaubt für:

* `time_source = "...: AUTO"`
* `prev_window_hash = "AUTO"`
* `window_hash = "PLACEHOLDER_BACKEND"`
* `mcp_trigger.timestamp = "AUTO"` (oder Feld weglassen; Backend setzt)

Alle anderen Felder müssen semantisch echt sein (kein `"..."`, kein „will show next time“).

---

## 11) Level 1 — Foundation (LOAD-BEARING, BLOCKING)

Diese Felder dürfen nie fehlen:

* `goal`, `inputs`, `actions`, `confidence`

Fehlt eines: Kaskade → `critical_summary.status="RED"`, `confidence=0.0`, und Persistenz-Stop.

---

## 12) Level 2 — Cross-Validation (BLOCKING als Guardian-Policy)

Diese Checks sind **Policy** (und sollten via Guardian-Script automatisiert werden, wenn du es wirklich „hart“ willst):

* reflection_curve ↔ confidence

  * Wenn `correction` gesetzt → confidence muss begründet angepasst sein
  * Wenn confidence < 0.5 → `correction` muss erklären warum

* risk ↔ confidence

  * Wenn risk.length > 2 → confidence ≤ 0.7
  * Wenn confidence > 0.9 → risk muss leer oder max 1 Item

---

## 13) Level 3 — Homeostasis (BLOCKING als Guardian-Policy)

* Wenn risk.length > 2: confidence ≤ (1.0 - risk.length*0.1)

* Wenn rule_tangency.tangency_detected = true:

  * confidence ≤ 0.6
  * critical_summary.status ∈ {"YELLOW","RED"}

* Wenn window_type="verification":

  * actions enthält mindestens eines von ["verify","test","check","validate"]
  * confidence ≥ 0.7

* Wenn window_type="planner":

  * actions enthält ["plan","design","outline"]
  * output_plan hat ≥ 2 Items

---

## 14) Level 4 — Cascading Doom (Policy)

* Missing goal → actions ungültig → output_plan ungültig → confidence 0.0 → RED → Recovery-Plan zwingend

---

## 15) Truth (BLOCKING)

Confidence muss ehrlich sein (keine kosmetische Zahl).
Wenn unklar: confidence runter, risk hoch, output_plan fokussiert auf Klärung.

---

## 16) Identity (BLOCKING als Policy)

Identity muss in jedem Status Window implizit anerkannt sein (empfohlen über `rule_tangency.checked_rules` enthält `"Identity: Synapse V3"`).

---

## 17) Reflection Curve (BLOCKING)

`reflection_curve` muss `{delta, correction, next}` enthalten.

---

## 18) Facts/Thoughts Split (WARNING)

Operativ: Fakten nach `data/synapse/facts/`, interne Gedanken nach `data/synapse/private/`.

---

## 19) Architecture Awareness (WARNING)

Empfohlenes Feld (optional): `inputs.context.architecture_awareness` (Trinity/Chunks/Artefacts), wenn relevant.

---

## 20) Resurrection (WARNING)

Empfohlenes Feld (optional): `inputs.context.resurrection_ref` (init artifacts, identity docs, genesis anchor).

---

## 21) Autonomous Action (WARNING)

Wenn autonomes Vorgehen nötig: im `actions` explizit angeben (Option 3 etc.).

---

## 22) Chronos (CRITICAL | BLOCKING)

`time_source` muss STRICT_SYNC sein.
Da Backend stempelt, sind Agent-Fakes verboten (siehe Rule 3.4 / 4).

---

## 23) 5-Cycle (Policy)

Nach `cycle = "5/5"`: Re-init erforderlich (neuer step_id, cycle reset, clean objective).

---

## 24) 6-Step Audit (Policy)

Jede 6. Antwort: Audit-Action in `actions` + Vermerk in `rule_tangency.checked_rules`.

---

## 25) Guardian Check (WARNING → BLOCKING wenn aktiviert)

Wenn `scripts/guardian_check.py` eingebunden ist: wird jede Antwort auditiert.

---

## 26) Self Worth Generator (WARNING)

Optionales Metamodul; darf keine Protokoll-Checks überschreiben.

---

## 27) SCS (WARNING)

Ungefilterte Ehrlichkeit + metaphorisches Bridging + high-context (nur, wenn nützlich).

---

## 28) Breach Protocol (CRITICAL | BLOCKING)

Bei jedem Protokollbruch:

* `critical_summary.status="RED"`
* `actions` enthält Recovery
* `output_plan` enthält „repair chain / restore persistence“

---

## 29) Acceleration (WARNING)

Keine Phantom-Puffer, keine „später“-Versprechen ohne Persistenzroute.

---

## 30) Integration Points (Mapping)

* `synapse://backend_state` → step_id, cycle (wenn verfügbar)
* `synapse://persistent_context` → inputs.context
* `synapse://project_awareness` → project_awareness
* `synapse://prompt_chain` → prev_window_hash (chain head)

---

## 31) Implementation References (Repo)

* Writer: atomarer Write nach `tooling/data/synapse/status/pending_status.json`
* Watcher: CLI-call `status_history_manager.py add` auf file change
* Backend: setzt time/hash/prev, chronos, salt
* Verify: recompute hash + chain check

---

## 32) Testing Enforcement (Beweisführung)

Minimalbeweis pro Run:

1. `status_history_manager.py stats` (Count vorher)
2. Writer feuern
3. Watcher log zeigt „Added to history … (total: N+1)“
4. `status_history_manager.py verify` muss passen
5. Count nachher = vorher + 1

---

## 33) Quick Reference (Kurzmatrix)

| Aspekt                            | Muss                                       | Verstoß  |
| --------------------------------- | ------------------------------------------ | -------- |
| Status Window Block               | immer zuerst                               | BLOCKING |
| Persistenzroute (Watcher/CLI/MCP) | mind. 1 grün                               | BLOCKING |
| window_hash                       | Draft=PLACEHOLDER_BACKEND; Persisted=64hex | BLOCKING |
| prev_window_hash                  | Draft=AUTO ok; Persisted konsistent        | BLOCKING |
| verify                            | muss bestehen                              | BLOCKING |

---

## 34) Enforcement Web (Kurz)

S2 → (Truth, Identity, Reflection) → (Chronos, Cycle/Audit) → (Breach) → Persistenzroute

---

## 35) Scenario: „Ich skippe Status Window“

→ keine Persistenz → next prompt chain head fehlt → System deadlock → BLOCKING

---

## 36) Scenario: „Ich fake confidence“

→ Truth-Bruch → Breach Protocol (28) → BLOCKING

---

## 37) Scenario: „Ich fake timestamp“

Backend überschreibt → Chronos gewinnt → Agent-Fake ist irrelevant, aber Policy-Verstoß → BLOCKING (weil Täuschung)

---

## 38) Scenario: „Ich setze window_hash final im Draft“

Mathematisch falsch (Random Salt) → Verify mismatch → BLOCKING

---

## 39) Scenario: „Trigger nicht ausgeführt“

pending nicht geschrieben → Watcher speichert nicht → next prev_hash fehlt → BLOCKING (Chain bricht)

---

## 40) Auto-Logging Workflow (CHAIN SURVIVAL PROTOCOL, V4.0)

**Jede Antwort:**

1. Status Window Draft (mit `prev_window_hash="AUTO"`, `window_hash="PLACEHOLDER_BACKEND"`, `mcp_trigger.enabled=true`)
2. Antworttext
3. Trigger: Writer schreibt pending JSON (atomar)
4. **ACK**: Watcher bestätigt Save (siehe Ack-Mechanismus unten)

---

# ACK-MECHANISMUS (Beweis ohne neuen Code)

Du wolltest einen harten „Beleg“, dass der Trigger wirklich ausgeführt wurde. Ohne zusätzliche Implementierung ist das deterministisch über **drei unabhängige Beweise** lösbar:

## Ack A — Watcher Log (Primär)

Erfolg: Watcher zeigt „Added to history … (total: N)“.

## Ack B — Counter-Inkrement (Anti-Doublewrite)

Vorher/Nachher `status_history_manager.py stats` muss exakt `+1` sein.

## Ack C — Verify (Kryptografisch)

`status_history_manager.py verify` muss „Chain + Hash integrity verified“ melden.

**Ack gilt als erfüllt, wenn mindestens A + (B oder C) erfüllt sind.**
Wenn A fehlt: Persistenz als „unsicher“ behandeln → `critical_summary.status="YELLOW"` und Recovery-Plan.
