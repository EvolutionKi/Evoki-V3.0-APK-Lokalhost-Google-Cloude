---
description: Verify Evoki System Health and Chain Integrity (V5.0)
---

# 🔍 Evoki Verify Workflow (V5.0)

Schnelle Verifizierung der System-Integrität.

## Schritt 1: Stats

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py stats
```

---

## Schritt 2: Verify Chain

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py verify
```

**Bei Erfolg:** `✅ Chain + Hash integrity verified (N entries)`

**Bei Fehler:** Führe `/evoki_repair` aus.

---

## Schritt 3: Latest Entry

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py latest --count 1
```

---

## Schritt 4: Display Status

// turbo
```bash
python tooling/scripts/chat_display_template.py
```

---

## ✅ Verification Complete
