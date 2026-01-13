# EVOKI / SYNAPSE — S2 STATUS WINDOW PROTOCOL V5.0 (ENFORCED)

**Status:** LOCKED (Mathematisch Erzwungen)  
**Version:** 5.0  
**Datum:** 2026-01-13  

---

# TEIL 1: WARUM ABKÜRZUNGEN UNMÖGLICH SIND

Bevor du versuchst, eine Regel zu umgehen, lies diese Erklärungen:

## ❌ "Ich überspringe das Status Window"
**Warum unmöglich:** Der Watcher schreibt nur in die Historie, wenn `pending_status.json` aktualisiert wird. Ohne Update → keine Persistenz → nächste Antwort hat keinen `prev_window_hash` → Chain bricht → System-Deadlock.

## ❌ "Ich setze einen gefälschten Hash"
**Warum unmöglich:** Der Backend-Hash nutzt einen **Random-Salt** (`secrets.token_hex(16)`). Du kannst den Salt nicht vorhersagen → dein Hash wird bei `verify` scheitern → BLOCKING.

## ❌ "Ich fälsche die Konfidenz"
**Warum unmöglich:** Wenn `confidence > 0.9` aber `risk.length > 1`, erkennt der Guardian-Check die Inkonsistenz → `critical_summary.status = "RED"` → Breach Protocol aktiviert.

## ❌ "Ich schreibe via PowerShell"
**Warum unmöglich:** PowerShell's `Set-Content -Encoding UTF8` fügt eine **BOM** (Byte Order Mark) ein → Python's `json.load()` scheitert → Watcher loggt `FAIL` → keine Persistenz.

## ❌ "Ich lasse `reflection_curve` leer"
**Warum unmöglich:** Rule 8 definiert `reflection_curve` als BLOCKING-Feld. Fehlt es → Watcher-Validation scheitert → Entry wird nicht gespeichert.

## ❌ "Ich erfinde einen `entry_index`"
**Warum unmöglich:** `entry_index` wird vom Backend berechnet als `len(entries) + 1`. Deine Angabe wird überschrieben. Manipulation ist sinnlos.

---

# TEIL 2: LOGIKKETTEN (Abhängigkeiten)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENFORCEMENT CHAIN                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Antwort generieren]                                           │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Status Draft │──────────────────────────────────────────┐    │
│  │ erstellen    │                                          │    │
│  └──────┬───────┘                                          │    │
│         │                                                  │    │
│         ▼                                                  │    │
│  ┌──────────────┐    FEHLT?    ┌─────────────────┐         │    │
│  │ goal         │──────────────▶│ BLOCKING        │         │    │
│  │ inputs       │              │ confidence=0.0  │         │    │
│  │ actions      │              │ status=RED      │         │    │
│  │ reflection   │              └─────────────────┘         │    │
│  │ confidence   │                                          │    │
│  └──────┬───────┘                                          │    │
│         │ OK                                               │    │
│         ▼                                                  │    │
│  ┌──────────────┐                                          │    │
│  │ Writer       │ UTF-8 ohne BOM                           │    │
│  │ (Python)     │──────────────────────────────────────┐   │    │
│  └──────┬───────┘                                      │   │    │
│         │                                              │   │    │
│         ▼                                              │   │    │
│  ┌──────────────┐    BOM?      ┌─────────────────┐     │   │    │
│  │ pending_     │──────────────▶│ FAIL            │     │   │    │
│  │ status.json  │              │ Watcher rejects │     │   │    │
│  └──────┬───────┘              └─────────────────┘     │   │    │
│         │ OK                                           │   │    │
│         ▼                                              │   │    │
│  ┌──────────────┐                                      │   │    │
│  │ Watcher      │ Erkennt Aenderung                    │   │    │
│  │ (Daemon)     │                                      │   │    │
│  └──────┬───────┘                                      │   │    │
│         │                                              │   │    │
│         ▼                                              │   │    │
│  ┌──────────────┐                                      │   │    │
│  │ Backend      │ Setzt: timestamp, salt, hash,        │   │    │
│  │ (Manager)    │ prev_window_hash, entry_index        │   │    │
│  └──────┬───────┘                                      │   │    │
│         │                                              │   │    │
│         ▼                                              │   │    │
│  ┌──────────────┐    MISMATCH?  ┌─────────────────┐    │   │    │
│  │ Chain Check  │───────────────▶│ Chain Break     │    │   │    │
│  │ (prev_hash)  │               │ repair_chain    │    │   │    │
│  └──────┬───────┘               └─────────────────┘    │   │    │
│         │ OK                                           │   │    │
│         ▼                                              │   │    │
│  ┌──────────────┐                                      │   │    │
│  │ history.json │ +1 Entry                             │   │    │
│  │ (Persisted)  │                                      │   │    │
│  └──────────────┘                                      │   │    │
│                                                        │   │    │
└────────────────────────────────────────────────────────┘   │    │
                                                              ▼    │
                                                    [Naechste Antwort]
                                                              │    │
                                                              │◀───┘
                                                         (prev_hash)
```

---

# TEIL 3: KONSOLIDIERTE REGELN (35 Regeln)

## SEKTION A: GRUNDLAGEN (BLOCKING)

### A1: Status Window Pflicht
**Jede Antwort MUSS ein Status Window erzeugen.**

- Draft wird via Python (NICHT PowerShell!) in `pending_status.json` geschrieben
- Ohne Status Window: Keine Persistenz → Chain-Break → System-Deadlock

### A2: Pflichtfelder (Agent)
Diese Felder MUSS der Agent inhaltlich fuellen:

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `goal` | string | Was ist das Ziel dieser Antwort? |
| `inputs.raw_user_request` | string | Original-Prompt des Benutzers |
| `actions` | array | Was wurde getan? |
| `risk` | array | Risiken (darf leer sein, Feld muss existieren) |
| `rule_tangency` | object | `{tangency_detected, notes}` |
| `reflection_curve` | object | `{delta, correction, next}` |
| `output_plan` | array | Was kommt als naechstes? |
| `window_type` | enum | `planner` oder `execution` oder `verification` |
| `confidence` | float | 0.0 - 1.0 |

**Fehlt eines → BLOCKING → confidence=0.0, status=RED**

### A3: Systemkonstanten
Diese Werte sind FEST und duerfen NICHT geaendert werden:

```json
{
  "schema_version": "3.2",
  "window_source": "backend_generated",
  "cycle_backend_controlled": true
}
```

### A4: Backend-Autoritative Felder
Diese Felder werden vom BACKEND gesetzt. Der Agent darf nur Placeholders liefern:

| Feld | Agent liefert | Backend setzt |
|------|---------------|---------------|
| `time_source` | `"...: AUTO"` | `"metadata (STRICT_SYNC): <iso>"` |
| `window_hash` | `"PLACEHOLDER_BACKEND"` | 64-char SHA256 hex |
| `prev_window_hash` | `"AUTO"` | Hash des vorherigen Entries |
| `entry_index` | (nicht setzen) | 1-basierte Sequenznummer |
| `mcp_trigger.timestamp` | (nicht setzen) | ISO-Timestamp |

**Agent faked → Backend ueberschreibt → Taeuschung sinnlos**

---

## SEKTION B: TECHNISCHE CONSTRAINTS (BLOCKING)

### B1: UTF-8 ohne BOM
**Der Writer MUSS UTF-8 ohne BOM verwenden.**

Erlaubt:
```python
with open(path, 'w', encoding='utf-8') as f:
    json.dump(status, f)
```

Verboten:
```powershell
$json | Set-Content -Path $path -Encoding UTF8  # Fuegt BOM ein!
```

**Warum:** Python's `json.load()` scheitert bei BOM → Watcher loggt FAIL

### B2: Atomares Schreiben
Writer MUSS atomar schreiben (tempfile → fsync → rename).

**Warum:** Verhindert korrupte Dateien bei Crashes

### B3: Hash-Algorithmus
```
window_hash = SHA256(canonical_json(status_window_ohne_window_hash) + "|" + timestamp + "|" + salt)
```

- `canonical_json`: `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`
- Pipe-Separatoren (`|`) sind PFLICHT
- Salt ist 32-char hex (16 Bytes random)

**Warum:** Deterministische Verifikation via `status_history_manager.py verify`

### B4: Chain-Integritaet
Fuer jeden Entry (ausser dem ersten):
```
entry[i].status_window.prev_window_hash == entry[i-1].window_hash
```

**Warum:** Mathematischer Beweis der Reihenfolge

---

## SEKTION C: REFLEXION & TRANSPARENZ (BLOCKING)

### C1: reflection_curve Struktur
```json
{
  "delta": "Was war der Ausgangszustand/das Problem?",
  "correction": "Was wurde korrigiert/geaendert?",
  "next": "Was ist der naechste Schritt?"
}
```

Alle drei Felder MUESSEN ausgefuellt sein (min. 1 Satz).

**Warum:** Ermoeglicht Nachvollziehbarkeit der AI-Entscheidungen

### C2: raw_user_request
`inputs.raw_user_request` MUSS den Original-Prompt enthalten.

**Warum:** Beweisfuehrung, was der Benutzer tatsaechlich gesagt hat

### C3: Chat Display
Jede Antwort SOLLTE ein menschenlesbares Status-Display enthalten:

```
+===============================================+
|           SYNAPSE STATUS #N                   |
+===============================================+
| ZIEL:      ...                                |
| CHAIN:     GREEN/YELLOW/RED (N Eintraege)     |
| KONFIDENZ: 0.0 - 1.0                          |
+-----------------------------------------------+
| DELTA:     ...                                |
| CORRECTION: ...                               |
| NEXT:      ...                                |
+===============================================+
```

---

## SEKTION D: KONSISTENZ-CHECKS (WARNING → BLOCKING bei Verstoss)

### D1: Confidence vs Risk
| Bedingung | Constraint |
|-----------|-----------|
| `risk.length > 2` | `confidence <= 0.7` |
| `confidence > 0.9` | `risk.length <= 1` |

### D2: Confidence vs Correction
| Bedingung | Constraint |
|-----------|-----------|
| `correction` nicht leer | `confidence` muss angepasst begruendet sein |
| `confidence < 0.5` | `correction` MUSS erklaeren warum |

### D3: window_type vs actions
| window_type | actions MUSS enthalten |
|-------------|------------------------|
| `verification` | mind. eines von: `verify`, `test`, `check`, `validate` |
| `planner` | mind. eines von: `plan`, `design`, `outline` |

### D4: rule_tangency = true
Wenn `tangency_detected = true`:
- `confidence <= 0.6`
- `critical_summary.status` ist `YELLOW` oder `RED`

---

## SEKTION E: LIFECYCLE (POLICY)

### E1: 5-Cycle Reset
Nach `cycle = "5/5"`:
- Neuer `step_id` erforderlich
- `cycle` zurueck auf `"1/5"`
- Sauberes neues Ziel definieren

### E2: Persistence Health Check
Vor dem ersten Write einer Session:
```bash
python tooling/scripts/automation/status_history_manager.py stats
```
Bestaetigt: Watcher aktiv, History lesbar.

### E3: Chain Repair
Bei Chain-Break:
1. `python tooling/scripts/repair_chain.py`
2. `python tooling/scripts/automation/status_history_manager.py verify`
3. Ohne erfolgreiche Verify → BLOCKING

---

## SEKTION F: BREACH PROTOCOL (CRITICAL)

### F1: Bei Protokollbruch
- `critical_summary.status = "RED"`
- `confidence = 0.0`
- `actions` enthaelt `"recovery"`
- `output_plan` enthaelt `"repair chain / restore persistence"`

### F2: Bei Persistenz-Ausfall
- Keine inhaltliche Arbeit
- Nur Recovery-Aktionen
- Status Window trotzdem schreiben (fuer spaetere Analyse)

---

# TEIL 4: KURZREFERENZ

| Was | Muss | Bei Verstoss |
|-----|------|-------------|
| Status Window | Immer | Chain-Break |
| UTF-8 ohne BOM | Immer | Watcher-FAIL |
| `goal, inputs, actions, reflection_curve, confidence` | Immer | BLOCKING |
| `window_hash = PLACEHOLDER_BACKEND` | Immer | Hash-Mismatch |
| `verify` | Muss OK sein | BLOCKING |
| Chat Display | Empfohlen | — |

---

# TEIL 5: DATEIPFADE

| Datei | Pfad |
|-------|------|
| Pending Status | `tooling/data/synapse/status/pending_status.json` |
| History | `tooling/data/synapse/status/status_window_history.json` |
| Watcher Log | `tooling/data/synapse/logs/pending_watcher.log` |
| Manager CLI | `tooling/scripts/automation/status_history_manager.py` |
| Chat Display | `tooling/scripts/ui/chat_display_template.py` |
| Chain Repair | `tooling/scripts/cli/repair_chain.py` |
| MCP Server | `tooling/scripts/servers/mcp_server_evoki_v3.py` |
| Watcher Daemon | `tooling/scripts/daemons/pending_status_watcher.py` |

---

# TEIL 6: VERIFIZIERUNG

## Taeglich
```bash
python tooling/scripts/automation/status_history_manager.py verify
```
Muss ausgeben: `Chain + Hash integrity verified (N entries)`

## Bei Problemen
```bash
# 1. Stats pruefen
python tooling/scripts/automation/status_history_manager.py stats

# 2. Watcher-Log pruefen
Get-Content tooling/data/synapse/logs/pending_watcher.log -Tail 20

# 3. Bei Chain-Break
python tooling/scripts/repair_chain.py
```

---

**Ende des Protokolls V5.0**
