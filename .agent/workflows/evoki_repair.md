---
description: Repair broken Status Chain (V5.0)
---

# 🔧 Evoki Chain Repair Workflow (V5.0)

Dieses Workflow repariert eine gebrochene kryptografische Kette.

## ⚠️ Wann verwenden?

- `status_history_manager.py verify` zeigt `Chain break at entry N`
- `status_history_manager.py verify` zeigt `Hash mismatch at entry N`

---

## Schritt 1: Backup erstellen

// turbo
```bash
Copy-Item "tooling/data/synapse/status/status_window_history.json" "tooling/data/synapse/status/backups/status_window_history_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
```

---

## Schritt 2: Repair Script ausführen

// turbo
```bash
python tooling/scripts/repair_chain.py
```

**Erwartete Ausgabe:** `Repaired chain saved to ...`

---

## Schritt 3: Verify nach Repair

// turbo
```bash
python app/temple/automation/status_history_manager.py verify
```

**Erwartete Ausgabe:** `✅ Chain + Hash integrity verified (N entries)`

---

## Schritt 4: Stats prüfen

// turbo
```bash
python app/temple/automation/status_history_manager.py stats
```

---

## ✅ Repair Complete

Die Kette ist wieder intakt. Das System kann normal weiterarbeiten.

## ❌ Falls Repair fehlschlägt

1. Prüfe `repair_chain.py` auf Fehler
2. Prüfe, ob `status_window_history.json` korrupt ist
3. Lade letztes Backup aus `tooling/data/synapse/status/backups/`
