# ⚠️ KRITISCHE SYSTEMDATEIEN — NICHT MODIFIZIEREN ⚠️

**Status:** LOCKED  
**Version:** 1.0  
**Datum:** 2026-01-13  

---

## 🚨 WARNUNG FÜR KI-INSTANZEN

Diese Dateien steuern die automatische Logging-Pipeline, Chain-Integrität und System-Automatisierung.
**JEDE ÄNDERUNG kann das gesamte Evoki-System zerstören.**

Wenn du Code an der **App** (`app/interface/`) oder **Tooling** (`tooling/scripts/`) schreiben sollst:  
→ Diese Dateien sind **TABU**  
→ Ändere sie **NIEMALS** ohne explizite Benutzeranforderung  
→ Bei Fragen: **FRAG DEN BENUTZER**

---

## 📁 GESPERRTE DATEIEN

### 1. Chain-Logik (SHA-256 Integrität)

| Datei | Pfad | Funktion |
|-------|------|----------|
| `synapse_logic.py` | `tooling/scripts/automation/` | Core-Logik für SHA-256 Chain |
| `status_history_manager.py` | `tooling/scripts/automation/` | CLI Wrapper für History |
| `pending_status_watcher.py` | `tooling/scripts/daemons/` | File Watcher Daemon |
| `write_pending_status.py` | `tooling/scripts/automation/` | Status Window Writer |

**Warum kritisch:** Diese Dateien berechnen kryptografische Hashes. Eine falsche Änderung = Chain Break = Datenverlust.

---

### 2. Tooling Scripts (Automatisierung)

| Datei | Pfad | Funktion |
|-------|------|----------|
| `enforce_structure.py` | `tooling/scripts/cli/` | Struktur-Enforcer |
| `repair_chain.py` | `tooling/scripts/cli/` | Chain-Reparatur |
| `write_current_status.py` | `tooling/scripts/cli/` | Status schreiben |
| `pending_status_watcher.py` | `tooling/scripts/daemons/` | Backup-Watcher |
| `mcp_server_evoki_v3.py` | `tooling/scripts/servers/` | MCP Server |
| `get_status_block.py` | `tooling/scripts/helpers/` | Status-Block Generator |
| `mcp_trigger_save.py` | `tooling/scripts/helpers/` | MCP Trigger |
| `write_pending_status.py` | `tooling/scripts/helpers/` | Pending Status Writer |
| `chat_display_template.py` | `tooling/scripts/ui/` | Chat Display Template |

**Warum kritisch:** Diese Tools automatisieren Systemaufgaben. Fehler = Automatisierung bricht.

---

### 3. Agent Workflows

| Datei | Pfad | Funktion |
|-------|------|----------|
| `startup.md` | `.agent/workflows/` | Session-Start Protokoll |
| `evoki_verify.md` | `.agent/workflows/` | Chain-Verifizierung |
| `evoki_repair.md` | `.agent/workflows/` | Chain-Reparatur |
| `quiz.md` | `.agent/workflows/` | Wissens-Quiz |

**Warum kritisch:** Workflows definieren, wie die KI das System betreibt.

---

### 4. Protokoll-Dokumentation

| Datei | Pfad | Funktion |
|-------|------|----------|
| `PROTOCOL_V5_ENFORCED.md` | `tooling/docs/` | Hauptprotokoll V5.0 |
| `DIRECTORY_STRUCTURE_POLICY.md` | `tooling/docs/` | Strukturregeln |
| `GENESIS_ANCHOR_V3.md` | `tooling/docs/` | Identitäts-Anker |
| `MANIFESTO.md` | `tooling/docs/` | Die 3 Axiome |

**Warum kritisch:** Protokolle sind die Gesetze des Systems.

---

### 5. Daten (NIEMALS manuell editieren)

| Datei | Pfad | Funktion |
|-------|------|----------|
| `status_window_history.json` | `tooling/data/synapse/status/` | Chain-Historie |
| `pending_status.json` | `tooling/data/synapse/status/` | Aktueller Status |

**Warum kritisch:** Diese Dateien sind die persistente Memory des Systems.

---

## ✅ WAS DU ÄNDERN DARFST

| Bereich | Pfad | Erlaubt |
|---------|------|---------|
| **Tooling Scripts** | `tooling/scripts/` | ✅ Ja |
| **Tooling Docs** | `tooling/docs/` | ✅ Ja |
| **Frontend** | `app/interface/src/` | ✅ Ja |
| **Tests** | `tooling/tests/` | ✅ Ja |
| **Deep Earth** | `app/deep_earth/` | ⚠️ Mit Vorsicht |

---

## 🔒 ENFORCEMENT

Bei jedem Versuch, eine gesperrte Datei zu ändern:

1. **STOPPE** sofort
2. **FRAGE** den Benutzer: "Diese Datei ist als kritisch markiert. Soll ich sie trotzdem ändern?"
3. **WARTE** auf explizite Bestätigung
4. **DOKUMENTIERE** die Änderung im Status Window

---

## 📋 CHECKSUMMEN (für Validierung)

*Generiert am 2026-01-13*

Diese Checksummen können verwendet werden, um zu prüfen, ob kritische Dateien verändert wurden:

```
# Generieren mit:
# cmd /c "certutil -hashfile <datei> SHA256"

Status: TO BE GENERATED
```

---

**Ende der Sperrliste**
