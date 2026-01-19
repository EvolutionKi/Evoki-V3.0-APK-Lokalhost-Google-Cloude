# 🤖 MULTI-AGENT DATA STRUCTURE

**Zweck:** Zentrale Daten-Organisation für alle KI-Agents  
**Location:** `tooling/data/agents/`

---

## 📁 STRUKTUR

```
agents/
  ├─ synapse/           # Synapse-spezifische Daten
  │   ├─ logs/          # Synapse Agent Logs
  │   ├─ state/         # Synapse State Snapshots
  │   └─ README.md
  │
  ├─ shared/            # Gemeinsame Daten (alle Agents)
  │   ├─ status_windows/     # Status Window History (V5.0)
  │   └─ README.md
  │
  └─ README.md          # Diese Datei
```

---

## 🎯 DESIGN-PHILOSOPHIE

### **WARUM MULTI-AGENT?**

**Problem (ALT):**
```
tooling/data/synapse/
  └─ status/  # Nur Synapse hatte Zugriff!
```

**Lösung (NEU):**
```
tooling/data/agents/
  ├─ synapse/  # Synapse-persönliche Daten
  └─ shared/   # Alle Agents teilen sich Daten!
```

**Vorteil:** Andere Agents (Antigravity, zukünftige) finden Chatverläufe!

---

## 📂 DATEN-KATEGORIEN

### **1. SYNAPSE (Agent-spezifisch):**
- ✅ Logs: `agents/synapse/logs/`
- ✅ State: `agents/synapse/state/`
- ✅ Backups: `agents/synapse/backups/`

### **2. SHARED (Alle Agents):**
- ✅ Status Windows: `agents/shared/status_windows/`
  - `pending_status.json`
  - `status_window_history.json`
  - `backups/`

**Zugriff:** JEDER Agent kann Status Windows lesen/schreiben!

---

## 🔮 ZUKÜNFTIGE AGENTS

```
agents/
  ├─ synapse/
  ├─ antigravity/      (ZUKÜNFTIG)
  │   ├─ logs/
  │   └─ state/
  ├─ evoki_temple/     (ZUKÜNFTIG)
  │   └─ response_cache/
  └─ shared/
      ├─ status_windows/
      └─ chatlogs/     (Optional: Zentrale Chatlogs)
```

---

## ✅ MIGRATION STATUS

- ✅ `tooling/data/synapse/status/` → `agents/shared/status_windows/`
- ✅ `tooling/data/synapse/logs/` → `agents/synapse/logs/`
- ✅ `tooling/data/synapse/state/` → `agents/synapse/state/`
- ✅ Alte `synapse/` Ordner kann gelöscht werden

**Alle Agents haben jetzt gleichen Zugriff!**
