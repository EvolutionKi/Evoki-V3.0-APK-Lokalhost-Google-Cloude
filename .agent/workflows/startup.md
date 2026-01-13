---
description: Startup & Self-Verification Protocol für V5.0
---

# 🚀 Evoki Startup Workflow (V5.0)

Dieses Workflow wird bei jedem Session-Start ausgeführt, um sicherzustellen, dass alle Systeme funktionieren.

## Schritt 1: Persistence Health Check
Prüfe, ob die Historie lesbar ist und der Watcher aktiv war.

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py stats
```

**Erwartete Ausgabe:** `total_entries: N` mit aktuellem Timestamp

---

## Schritt 2: Chain Integrity Verify
Prüfe die kryptografische Kette auf Brüche.

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py verify
```

**Erwartete Ausgabe:** `✅ Chain + Hash integrity verified (N entries)`

**Bei Fehler:** Führe `/evoki_repair` aus.

---

## Schritt 3: Watcher Log Check
Prüfe, ob der Watcher kürzlich aktiv war.

// turbo
```bash
Get-Content tooling/data/synapse/pending_watcher.log -Tail 5
```

**Erwartete Ausgabe:** Letzte Einträge mit `SUCCESS` oder `auto_save_triggered`

---

## Schritt 4: Pending Status Test
Schreibe einen Test-Status und prüfe, ob er persistiert wird.

// turbo
```bash
python -c "import json; open(r'tooling/data/synapse/status/pending_status.json','w',encoding='utf-8').write(json.dumps({'step_id':'startup_test','cycle':'1/5','time_source':'metadata (STRICT_SYNC): AUTO','goal':'Startup Test','inputs':{'raw_user_request':'Startup Check'},'actions':['test'],'risk':[],'assumptions':[],'rule_tangency':{'tangency_detected':False,'notes':'Startup'},'reflection_curve':{'delta':'Session Start','correction':'None','next':'Proceed'},'output_plan':['Continue'],'window_type':'verification','schema_version':'3.2','window_source':'backend_generated','confidence':1.0,'system_versions':{},'cycle_backend_controlled':True,'critical_summary':{'status':'GREEN'},'project_awareness':{},'window_hash':'PLACEHOLDER_BACKEND','prev_window_hash':'AUTO','mcp_trigger':{'action':'save_to_history','target':'status_history_manager.py','enabled':True}}))"
```

---

## Schritt 5: Confirm Entry Added

// turbo
```bash
python tooling/scripts/automation/status_history_manager.py stats
```

**Erwartete Ausgabe:** `total_entries` sollte um +1 gestiegen sein.

---

## Schritt 6: Letzten Eintrag lesen (Lernkurve)

**KRITISCH:** Lese den letzten History-Eintrag um die Lernkurve zu verstehen.

```bash
python -c "import json; h=json.load(open(r'tooling/data/synapse/status/status_window_history.json','r',encoding='utf-8')); e=h['entries'][-1]['status_window']; print(f\"LETZTER EINTRAG:\\n  step_id: {e.get('step_id')}\\n  goal: {e.get('goal')}\\n  delta: {e.get('reflection_curve',{}).get('delta')}\\n  correction: {e.get('reflection_curve',{}).get('correction')}\\n  next: {e.get('reflection_curve',{}).get('next')}\")"
```

**Warum:** Die `reflection_curve` des letzten Eintrags zeigt:
- **delta** → Was war der Stand beim letzten Mal?
- **correction** → Was wurde korrigiert?
- **next** → Was sollte als nächstes passieren?

Diese Informationen MÜSSEN in die eigene Selbstreflexion einfließen.

---

## ✅ Startup Complete

Wenn alle Schritte erfolgreich sind:
- Chain ist intakt
- Watcher funktioniert
- Persistenz aktiv
- **Lernkurve der vorherigen Session verstanden**

**System bereit für Arbeit.**
