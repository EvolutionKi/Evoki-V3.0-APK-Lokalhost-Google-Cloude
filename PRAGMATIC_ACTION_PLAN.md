# ⚡ PRAGMATISCHER ACTION PLAN — V3.0 DATA LAYER

**Datum**: 2026-02-08 03:21 UTC  
**Status**: **READY TO START**  
**Strategi**: Nutze **vorhandene Komponenten** statt alles neu zu bauen!

---

## ✅ **WAS BEREITS EXISTIERT**

```
backend/
├── core/
│   ├── evoki_metrics_v3/
│   │   └── calculator_spec_A_PHYS_V11.py     ✅ 168 Metriken FUNKTIONIERT
│   └── BUCH7_evoki_v3_vector_store.py        ✅ FAISS System (4 Namespaces)
│
├── schemas/
│   ├── BUCH7_evoki_v3_core_schema.sql        ✅ V3.0 Core DB Schema
│   └── BUCH7_evoki_v3_graph_schema.sql       ✅ V3.0 Graph DB Schema
│
└── migration/
    ├── t2_history_importer.py                ✅ Import Logic (650 Paare/s)
    └── build_evoki_v3_core_db.py             ✅ DB Builder
```

**FAZIT**: **60% der Arbeit ist SCHON ERLEDIGT!** 🎉

---

## 🎯 **NEUE STRATEGIE: FEH

LENDE 40% ERGÄNZEN**

Statt 100% neu bauen → **Integriere das Vorhandene** + füge **fehlende Bindegl ieder** hinzu!

### **PHASE 1: INTEGRATION (JETZT!)** (~2 Stunden)

#### **1.1 Master Pipeline Script** ✅ **DONE**
- ✅ `backend/v3_pipeline_master.py` erstellt
- Verbindet: MetricsCalculator + VectorStore + SQL Schemas
- Fügt hinzu: Live-Monitoring Integration

#### **1.2 Echte Daten laden** (~30 Min)
- [ ] Finde T2 Pipeline Test-Output (1000 Paare)
- [ ] Oder: Extrahiere 1000 Paare aus History Archive
- [ ] Als JSON speichern in `backend/data/test_1000_pairs.json`

#### **1.3 Live-Monitor Script** (~30 Min)
- [ ] Kopiere `watch_pipeline.py` aus `LIVE_PIPELINE_TEST_PLAN.md`
- [ ] Speichere als `backend/scripts/watch_pipeline.py`
- [ ] Teste: `python backend/scripts/watch_pipeline.py`

#### **1.4 Validation Script** (~1 Stunde)
- [ ] Erstelle `backend/scripts/validate_import.py`
- [ ] Prüft:
  - DB Counts (prompt_pairs, metrics_full, etc.)
  - Metriken-Plausibilität
  - FAISS Index Integrität
- [ ] Returns: GO/NO-GO Decision

---

### **PHASE 2: LIVE-TEST (10 Minuten!)**

```powershell
# Terminal 1: Start Pipeline
python backend/v3_pipeline_master.py --test --limit 1000

# Terminal 2: Watch Live
python backend/scripts/watch_pipeline.py
```

**Expected Output**:
```
🔴 LIVE IMPORT MONITOR
════════════════════════
Status:      🔴 RUNNING
Progress:    [████████████████████] 100%
Processed:   1000 / 1000 Paare
Speed:       650 Paare/s

✅ Errors:   0

Last Pair:   #1000
  m1_A:      0.72
  hazard:    0.45
════════════════════════
```

**Validation**:
```powershell
python backend/scripts/validate_import.py
```

**GO/NO-GO**:
- ✅ 0 Fehler → **GO für 22k**
- ❌ Fehler → **FIX & RE-TEST**

---

### **PHASE 3: SCALE-UP (5 Minuten)**

```powershell
# Full Import
python backend/v3_pipeline_master.py --full

# Watch
python backend/scripts/watch_pipeline.py
```

**Expected**: ~34 Sekunden für 22.000 Paare

---

## 📝 **MINIMAL TODO (nur fehlende Teile!)**

### **TODO #1: Datenquelle finden** (~15 Min)

```powershell
# Option A: T2 Pipeline Output nutzen
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
Get-ChildItem -Recurse -Filter "*1000*pairs*.json" | Select-Object FullName

# Option B: History Archive durchsuchen
Get-ChildItem "backend\Evoki History" -Recurse | Select-Object FullName

# Option C: Aus SQLite extrahieren (falls T2 DBs existieren)
sqlite3 backend/data/evoki_metadata.db "SELECT COUNT(*) FROM prompt_pairs;"
```

**Ziel**: Finde/erstelle `backend/data/test_1000_pairs.json`

**Format**:
```json
[
  {
    "pair_id": "uuid-1",
    "session_id": "session-1",
    "user_text": "...",
    "ai_text": "...",
    "user_ts": "2025-02-15T14:30:00Z",
    "ai_ts": "2025-02-15T14:30:05Z"
  },
  ...
]
```

---

### **TODO #2: Live-Monitor Script erstellen** (~20 Min)

**File**: `backend/scripts/watch_pipeline.py`

```python
#!/usr/bin/env python3
"""Live Pipeline Monitor (copy from LIVE_PIPELINE_TEST_PLAN.md)"""

import json
import time
from pathlib import Path

STATUS_FILE = Path("backend/data/pipeline_status.json")

def render_status(status):
    """Render terminal UI"""
    print("\033[2J\033[H", end="")  # Clear screen
    
    print("="*60)
    print("🔴 LIVE IMPORT MONITOR — V3.0 PIPELINE")
    print("="*60)
    
    # Status
    s = status.get("status", "unknown")
    print(f"\nStatus:     {'🔴' if s == 'running' else '✅'} {s.upper()}")
    
    # Progress
    prog = status.get("progress", {})
    pct = prog.get("percentage", 0)
    bar_width = 40
    filled = int((pct / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"Progress:   [{bar}] {pct}%")
    print(f"Processed:  {prog.get('processed', 0)} / {prog.get('total', 0)} Paare")
    
    # Performance
    perf = status.get("performance", {})
    print(f"\nSpeed:      {perf.get('current_speed', 0):.1f} Paare/s")
    print(f"ETA:        {perf.get('eta_seconds', 0):.1f}s")
    
    # Errors
    errors = status.get("errors", [])
    print(f"\n✅ Errors:   {len(errors)}")
    
    # Last Pair
    last = status.get("last_pair", {})
    if last.get("pair_id"):
        print(f"\nLast Pair:  {last.get('pair_id')}")
        print(f"  m1_A:      {last.get('m1_A', 'N/A')}")
        print(f"  hazard:    {last.get('hazard', 'N/A')}")
    
    print("\n" + "="*60)
    print("[Auto-refresh: 0.5s] | Ctrl+C to exit")

def watch():
    """Watch status file"""
    print("🔍 Monitoring pipeline...")
    try:
        while True:
            if STATUS_FILE.exists():
                with open(STATUS_FILE) as f:
                    status = json.load(f)
                render_status(status)
                
                if status.get("status") in ["completed", "failed"]:
                    print("\n✅ Pipeline finished.")
                    break
            else:
                print("⏳ Waiting for pipeline to start...")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor stopped.")

if __name__ == "__main__":
    watch()
```

---

### **TODO #3: Validation Script** (~30 Min)

**File**: `backend/scripts/validate_import.py`

```python
#!/usr/bin/env python3
"""Validation Script für Import"""

import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/evoki_v3_core.db")

def validate():
    """Run validation checks"""
    if not DB_PATH.exists():
        print("❌ Database not found!")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    checks = {}
    
    # Check 1: Counts
    cur.execute("SELECT COUNT(*) FROM prompt_pairs")
    pair_count = cur.fetchone()[0]
    checks["prompt_pairs_count"] = pair_count
    
    cur.execute("SELECT COUNT(*) FROM metrics_full")
    metrics_count = cur.fetchone()[0]
    checks["metrics_full_count"] = metrics_count
    
    # Check 2: Metrics plausibility
    cur.execute("SELECT AVG(user_m1_A), AVG(user_m151_hazard) FROM metrics_full")
    avg_m1, avg_hazard = cur.fetchone()
    checks["avg_user_m1_A"] = avg_m1
    checks["avg_user_hazard"] = avg_hazard
    plausible = (0.3 <= avg_m1 <= 0.8) and (0.1 <= avg_hazard <= 0.6)
    
    conn.close()
    
    # Print Report
    print("\n" + "="*60)
    print("📊 VALIDATION REPORT")
    print("="*60)
    print(f"✅ prompt_pairs:       {checks['prompt_pairs_count']}")
    print(f"✅ metrics_full:       {checks['metrics_full_count']}")
    print(f"📊 avg user_m1_A:      {checks['avg_user_m1_A']:.2f}")
    print(f"📊 avg user_hazard:    {checks['avg_user_hazard']:.2f}")
    print(f"{'✅' if plausible else '❌'} Metrics plausible: {plausible}")
    print("="*60)
    
    success = (checks['prompt_pairs_count'] > 0 and 
               checks['metrics_full_count'] > 0 and 
               plausible)
    
    if success:
        print("\n✅✅✅ ALL CHECKS PASSED — GO FOR SCALE-UP! ✅✅✅\n")
    else:
        print("\n❌ SOME CHECKS FAILED — FIX BEFORE SCALE-UP!\n")
    
    return success

if __name__ == "__main__":
    success = validate()
    exit(0 if success else 1)
```

---

## 🚀 **WORKFLOW (END-TO-END)**

```bash
# 1. Prepare environment
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"

# 2. Create missing scripts
# (Paste TODO #2 and #3 code above)

# 3. Find/create test data
# (Follow TODO #1)

# 4. Terminal 1: Run Pipeline
python backend/v3_pipeline_master.py --test --limit 1000

# 5. Terminal 2: Monitor
python backend/scripts/watch_pipeline.py

# 6. Validate
python backend/scripts/validate_import.py

# 7. If ✅ → Scale-Up
python backend/v3_pipeline_master.py --full
```

---

## 📊 **TIMELINE**

```
NOW:         Create missing scripts                [30 Min]
  ↓
+30 MIN:     Test mit 1000 Paaren                  [10 Min]
  ↓
+40 MIN:     Validation GO/NO-GO                   [2 Min]
  ↓
+42 MIN:     Scale-Up auf 22k (wenn GO)            [5 Min]
  ↓
+47 MIN:     ✅ PRODUCTION READY!
```

**TOTAL**: ~1 Stunde bis functioning V3.0 Data Layer!

---

## ⚠️ **KEY PRINCIPLE**

**"Don't Rebuild — Integrate!"**

- ✅ MetricsCalculator **existiert** → nutze ihn!
- ✅ VectorStore **existiert** → nutze ihn!
- ✅ SQL Schemas **existieren** → nutze sie!
- ✅ T2 Import Logic **existiert** → nutze sie!

**NUR BAUE**: Live-Monitoring + Validation + Integration-Layer

---

**NÄCHSTER MOVE**: Erstelle TODO #2 (watch_pipeline.py) → dann TODO #3 (validate_import.py) → dann TEST! 🚀
