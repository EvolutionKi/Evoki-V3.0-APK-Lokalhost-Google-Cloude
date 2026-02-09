# 🔴 LIVE PIPELINE TEST PLAN — 1000 Paare → 22.000 Paare

**Version**: 1.0.0  
**Erstellt**: 2026-02-08 03:15 UTC  
**Strategie**: Gate-Keeping mit Live-Monitoring

---

## 🎯 **ZIEL**

**PHASE 1**: Backend-Pipeline mit **1000 echten Paaren** live testen  
**GO-Kriterium**: 0 Fehler, Performance OK, Daten valide  
**PHASE 2**: Scale-Up auf **22.000 Paare** (voller History-Import)

---

## 📊 **ARCHITEKTUR: LIVE-MONITORING SYSTEM**

```
┌─────────────────────────────────────────────────────────────────┐
│                  LIVE-MONITORING ARCHITEKTUR                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. IMPORT PIPELINE (Python)                              │   │
│  │    v3_importer.py --live-monitor --limit 1000            │   │
│  │                                                            │   │
│  │    ✅ Liest 1000 Paare                                     │   │
│  │    ✅ Berechnet 322 Metriken pro Paar                      │   │
│  │    ✅ Schreibt in evoki_v3_core.db                         │   │
│  │    ✅ Updated FAISS Indizes                                │   │
│  │    ✅ Schreibt Status → pipeline_status.json              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 2. STATUS FILE (JSON, updated every 10 Paare)            │   │
│  │    backend/v3_data_layer/logs/pipeline_status.json       │   │
│  │                                                            │   │
│  │    {                                                       │   │
│  │      "status": "running",                                 │   │
│  │      "progress": {                                        │   │
│  │        "total": 1000,                                     │   │
│  │        "processed": 450,                                  │   │
│  │        "percentage": 45.0                                 │   │
│  │      },                                                    │   │
│  │      "performance": {                                     │   │
│  │        "avg_time_per_pair": 0.0015,                       │   │
│  │        "current_speed": 666,  // Paare/s                  │   │
│  │        "eta_seconds": 0.83                                │   │
│  │      },                                                    │   │
│  │      "errors": [],                                        │   │
│  │      "warnings": [],                                      │   │
│  │      "last_update": "2026-02-08T03:15:25Z"                │   │
│  │    }                                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 3. LIVE MONITOR (Python Terminal)                        │   │
│  │    watch_pipeline.py                                      │   │
│  │                                                            │   │
│  │    ┌────────────────────────────────────────────────┐    │   │
│  │    │ 🔴 LIVE IMPORT MONITOR                         │    │   │
│  │    ├────────────────────────────────────────────────┤    │   │
│  │    │ Status:     RUNNING                            │    │   │
│  │    │ Progress:   [████████████░░░░░░░░] 45%        │    │   │
│  │    │ Processed:  450 / 1000 Paare                   │    │   │
│  │    │ Speed:      666 Paare/s                        │    │   │
│  │    │ ETA:        0.8s                               │    │   │
│  │    │                                                 │    │   │
│  │    │ ✅ Errors:     0                                │    │   │
│  │    │ ⚠️  Warnings:  0                                │    │   │
│  │    │                                                 │    │   │
│  │    │ Last Pair:  #450                               │    │   │
│  │    │   m1_A:      0.72                              │    │   │
│  │    │   hazard:    0.45                              │    │   │
│  │    │   B_safety:  0.88                              │    │   │
│  │    │                                                 │    │   │
│  │    │ [Auto-refresh: 0.5s]                           │    │   │
│  │    └────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 4. BACKEND API (Optional, für Web-Dashboard)             │   │
│  │    GET /api/v3/pipeline/status                            │   │
│  │                                                            │   │
│  │    Returns: pipeline_status.json                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 **IMPLEMENTATION: LIVE-MONITORING COMPONENTS**

### **1. Enhanced Importer mit Live-Status** (~30 Min)

**File**: `backend/v3_data_layer/scripts/v3_importer.py`

```python
#!/usr/bin/env python3
"""
V3.0 Importer mit Live-Monitoring Support
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone

class V3ImporterWithMonitoring:
    def __init__(self, status_file="backend/v3_data_layer/logs/pipeline_status.json"):
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.status = {
            "status": "initializing",
            "progress": {"total": 0, "processed": 0, "percentage": 0.0},
            "performance": {
                "avg_time_per_pair": 0.0,
                "current_speed": 0.0,
                "eta_seconds": 0.0,
                "start_time": None,
                "elapsed_seconds": 0.0
            },
            "errors": [],
            "warnings": [],
            "last_update": None,
            "db_stats": {
                "prompt_pairs": 0,
                "metrics_full": 0,
                "b_state_evolution": 0,
                "hazard_events": 0
            },
            "last_pair": {
                "pair_id": None,
                "m1_A": None,
                "hazard": None,
                "B_safety": None
            }
        }
    
    def update_status(self, processed, total, last_pair_metrics=None):
        """Update status file (called every 10 Paare)"""
        now = datetime.now(timezone.utc).isoformat()
        elapsed = time.time() - self.start_time if hasattr(self, 'start_time') else 0
        
        self.status.update({
            "status": "running",
            "progress": {
                "total": total,
                "processed": processed,
                "percentage": round((processed / total) * 100, 1)
            },
            "performance": {
                "avg_time_per_pair": round(elapsed / processed, 4) if processed > 0 else 0,
                "current_speed": round(processed / elapsed, 1) if elapsed > 0 else 0,
                "eta_seconds": round((total - processed) * (elapsed / processed), 1) if processed > 0 else 0,
                "start_time": getattr(self, 'start_time_iso', now),
                "elapsed_seconds": round(elapsed, 1)
            },
            "last_update": now
        })
        
        if last_pair_metrics:
            self.status["last_pair"] = last_pair_metrics
        
        # Write atomically
        tmp_file = self.status_file.with_suffix('.tmp')
        with open(tmp_file, 'w') as f:
            json.dump(self.status, f, indent=2)
        tmp_file.replace(self.status_file)
    
    def import_pairs(self, pairs_data, limit=None):
        """Import pairs with live monitoring"""
        self.start_time = time.time()
        self.start_time_iso = datetime.now(timezone.utc).isoformat()
        
        total = min(len(pairs_data), limit) if limit else len(pairs_data)
        self.status["progress"]["total"] = total
        
        for i, pair in enumerate(pairs_data[:total], 1):
            # === ACTUAL IMPORT LOGIC HERE ===
            # 1. Calculate metrics
            # 2. Write to DB
            # 3. Update FAISS
            # ... (existing T2 pipeline logic)
            
            # Update status every 10 Paare
            if i % 10 == 0 or i == total:
                last_metrics = {
                    "pair_id": pair.get("pair_id"),
                    "m1_A": 0.72,  # from calculator
                    "hazard": 0.45,  # from calculator
                    "B_safety": 0.88  # from calculator
                }
                self.update_status(i, total, last_metrics)
        
        # Final status
        self.status["status"] = "completed"
        self.update_status(total, total)
        
        return {"success": True, "processed": total, "errors": len(self.status["errors"])}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--live-monitor", action="store_true")
    args = parser.parse_args()
    
    importer = V3ImporterWithMonitoring()
    # ... load pairs_data from backend/test_data/1000_pairs/pairs.json
    result = importer.import_pairs(pairs_data, limit=args.limit)
    
    print(f"\n✅ Import complete: {result['processed']} Paare, {result['errors']} Fehler")
```

---

### **2. Live-Monitor Terminal Script** (~20 Min)

**File**: `backend/v3_data_layer/scripts/watch_pipeline.py`

```python
#!/usr/bin/env python3
"""
Live Pipeline Monitor (Terminal-basiert)
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

class PipelineMonitor:
    def __init__(self, status_file="backend/v3_data_layer/logs/pipeline_status.json"):
        self.status_file = Path(status_file)
    
    def render(self, status):
        """Render terminal UI"""
        # Clear screen (ANSI escape)
        print("\033[2J\033[H", end="")
        
        # Header
        print("="*60)
        print("🔴 LIVE IMPORT MONITOR — V3.0 PIPELINE")
        print("="*60)
        
        # Status
        status_emoji = {
            "initializing": "⏳",
            "running": "🔴",
            "completed": "✅",
            "failed": "❌"
        }
        s = status["status"]
        print(f"\nStatus:     {status_emoji.get(s, '❓')} {s.upper()}")
        
        # Progress bar
        prog = status["progress"]
        pct = prog["percentage"]
        bar_width = 40
        filled = int((pct / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"Progress:   [{bar}] {pct}%")
        print(f"Processed:  {prog['processed']} / {prog['total']} Paare")
        
        # Performance
        perf = status["performance"]
        print(f"\nSpeed:      {perf['current_speed']:.1f} Paare/s")
        print(f"Avg Time:   {perf['avg_time_per_pair']*1000:.2f} ms/Paar")
        print(f"Elapsed:    {perf['elapsed_seconds']:.1f}s")
        print(f"ETA:        {perf['eta_seconds']:.1f}s")
        
        # Errors/Warnings
        print(f"\n✅ Errors:     {len(status['errors'])}")
        print(f"⚠️  Warnings:  {len(status['warnings'])}")
        
        if status['errors']:
            print("\n❌ LATEST ERRORS:")
            for err in status['errors'][-3:]:  # Last 3
                print(f"   • {err}")
        
        # Last Pair Stats
        last = status.get("last_pair", {})
        if last.get("pair_id"):
            print(f"\nLast Pair:  {last['pair_id']}")
            print(f"  m1_A:      {last.get('m1_A', 'N/A')}")
            print(f"  hazard:    {last.get('hazard', 'N/A')}")
            print(f"  B_safety:  {last.get('B_safety', 'N/A')}")
        
        # Footer
        print("\n" + "="*60)
        print(f"Last Update: {status.get('last_update', 'N/A')}")
        print("[Auto-refresh: 0.5s] | Ctrl+C to exit")
        print("="*60)
    
    def watch(self, refresh_interval=0.5):
        """Watch status file and render live"""
        print("🔍 Monitoring pipeline status...")
        print(f"📁 Status file: {self.status_file}")
        print("\nWaiting for pipeline to start...\n")
        
        try:
            while True:
                if self.status_file.exists():
                    with open(self.status_file) as f:
                        status = json.load(f)
                    
                    self.render(status)
                    
                    # Exit if completed or failed
                    if status["status"] in ["completed", "failed"]:
                        print("\n✅ Pipeline finished. Exiting monitor.")
                        break
                else:
                    print("⏳ Waiting for status file...")
                
                time.sleep(refresh_interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitor stopped by user.")

if __name__ == "__main__":
    monitor = PipelineMonitor()
    monitor.watch()
```

**Usage**:
```powershell
# Terminal 1: Start Pipeline
python backend/v3_data_layer/scripts/v3_importer.py --live-monitor --limit 1000

# Terminal 2: Start Monitor
python backend/v3_data_layer/scripts/watch_pipeline.py
```

---

### **3. Backend API Endpoint (Optional)** (~30 Min)

**File**: `backend/api/v3_pipeline_status.py`

```python
#!/usr/bin/env python3
"""
Backend API Endpoint für Pipeline-Status
"""

from flask import Flask, jsonify
from pathlib import Path
import json

app = Flask(__name__)

STATUS_FILE = Path("backend/v3_data_layer/logs/pipeline_status.json")

@app.route("/api/v3/pipeline/status", methods=["GET"])
def get_pipeline_status():
    """Return current pipeline status"""
    if not STATUS_FILE.exists():
        return jsonify({"error": "Pipeline not running"}), 404
    
    with open(STATUS_FILE) as f:
        status = json.load(f)
    
    return jsonify(status), 200

@app.route("/api/v3/pipeline/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
```

**Usage**:
```powershell
# Start API
python backend/api/v3_pipeline_status.py

# Test
curl http://localhost:5001/api/v3/pipeline/status
```

---

## ✅ **GO/NO-GO KRITERIEN — 1000 PAARE TEST**

Nach 1000-Paare-Import **MUSS ALLES GRÜN** sein:

### **MUST-HAVE (Blocker wenn nicht erfüllt)**:

- [ ] **✅ 0 Fehler** während Import
  - SQL Constraint Violations → ❌ NO-GO
  - Metrik-Berechnungs-Fehler → ❌ NO-GO
  - FAISS Index Crashes → ❌ NO-GO

- [ ] **✅ Performance: ≥ 500 Paare/s**
  - Wenn < 500 Paare/s → Performance-Probleme finden & fixen
  - Ziel: 22.000 Paare in < 45 Sekunden

- [ ] **✅ DB Integrität**
  - `SELECT COUNT(*) FROM prompt_pairs` → **MUSS 1000 sein**
  - `SELECT COUNT(*) FROM metrics_full` → **MUSS 1000 sein**
  - `SELECT COUNT(*) FROM b_state_evolution` → **MUSS 1000 sein**

- [ ] **✅ FAISS Indizes valide**
  - `atomic_pairs.index` existiert mit 1000 Vektoren
  - Test-Search funktioniert (Top-5 Ergebnisse plausibel)

- [ ] **✅ Metriken plausibel**
  - `SELECT AVG(user_m1_A) FROM metrics_full` → **0.3 - 0.8** (nicht 0.0 oder 1.0)
  - `SELECT AVG(user_m151_hazard) FROM metrics_full` → **0.1 - 0.6**
  - `SELECT COUNT(*) FROM hazard_events` → **30-80** (3-8% Hazard-Rate)

### **NICE-TO-HAVE (Warnings, aber nicht Blocker)**:

- [ ] **⚠️ Warnings: < 10**
  - Einzelne fehlende Lexika-Matches → OK
  - Einzelne Metriken außerhalb Expected Range → LOG but continue

- [ ] **⚠️ Memory Usage: < 2 GB**
  - Bei 1000 Paaren sollte RAM-Verbrauch niedrig sein

### **VALIDATION SCRIPT**:

**File**: `backend/v3_data_layer/scripts/validate_1000_import.py`

```python
#!/usr/bin/env python3
"""
Validation Script für 1000-Paare Import
"""

import sqlite3
import json
from pathlib import Path

def validate_import():
    """Run all validation checks"""
    db = sqlite3.connect("backend/v3_data_layer/databases/evoki_v3_core.db")
    cur = db.cursor()
    
    checks = {
        "prompt_pairs_count": False,
        "metrics_full_count": False,
        "b_state_count": False,
        "metrics_plausible": False,
        "hazard_rate_ok": False,
        "faiss_index_exists": False
    }
    
    # Check 1: Counts
    cur.execute("SELECT COUNT(*) FROM prompt_pairs")
    pair_count = cur.fetchone()[0]
    checks["prompt_pairs_count"] = (pair_count == 1000)
    
    cur.execute("SELECT COUNT(*) FROM metrics_full")
    metrics_count = cur.fetchone()[0]
    checks["metrics_full_count"] = (metrics_count == 1000)
    
    cur.execute("SELECT COUNT(*) FROM b_state_evolution")
    b_state_count = cur.fetchone()[0]
    checks["b_state_count"] = (b_state_count == 1000)
    
    # Check 2: Metrics plausibility
    cur.execute("SELECT AVG(user_m1_A), AVG(user_m151_hazard) FROM metrics_full")
    avg_m1, avg_hazard = cur.fetchone()
    checks["metrics_plausible"] = (0.3 <= avg_m1 <= 0.8 and 0.1 <= avg_hazard <= 0.6)
    
    # Check 3: Hazard rate
    cur.execute("SELECT COUNT(*) FROM hazard_events")
    hazard_count = cur.fetchone()[0]
    checks["hazard_rate_ok"] = (30 <= hazard_count <= 80)
    
    # Check 4: FAISS Index
    faiss_index = Path("backend/v3_data_layer/faiss_indices/atomic_pairs.index")
    checks["faiss_index_exists"] = faiss_index.exists()
    
    # Print Report
    print("\n" + "="*60)
    print("📊 VALIDATION REPORT — 1000 PAARE IMPORT")
    print("="*60)
    
    all_passed = True
    for check, passed in checks.items():
        emoji = "✅" if passed else "❌"
        print(f"{emoji} {check}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✅✅✅ ALL CHECKS PASSED — GO FOR 22.000 PAARE! ✅✅✅\n")
        return True
    else:
        print("\n❌ SOME CHECKS FAILED — FIX BEFORE SCALE-UP!\n")
        return False

if __name__ == "__main__":
    success = validate_import()
    exit(0 if success else 1)
```

**Usage**:
```powershell
# Nach 1000-Paare Import
python backend/v3_data_layer/scripts/validate_1000_import.py
```

**Expected Output**:
```
============================================================
📊 VALIDATION REPORT — 1000 PAARE IMPORT
============================================================
✅ prompt_pairs_count: PASS
✅ metrics_full_count: PASS
✅ b_state_count: PASS
✅ metrics_plausible: PASS
✅ hazard_rate_ok: PASS
✅ faiss_index_exists: PASS
============================================================

✅✅✅ ALL CHECKS PASSED — GO FOR 22.000 PAARE! ✅✅✅
```

---

## 🚀 **SCALE-UP: 22.000 PAARE**

### **Nur wenn 1000-Paare Test ✅ ist!**

```powershell
# Full History Import
python backend/v3_data_layer/scripts/v3_importer.py --live-monitor --source full_history

# Monitor in parallel Terminal
python backend/v3_data_layer/scripts/watch_pipeline.py
```

### **Expected Performance (22k Paare)**:

```
Total Paare:    22.000
Speed:          ~650 Paare/s (basierend auf 1000-Test)
Total Time:     ~34 Sekunden
DB Size:        ~100 MB (evoki_v3_core.db)
FAISS Size:     ~35 MB (alle 3 Indizes)
```

### **Final Validation (22k)**:

```powershell
python backend/v3_data_layer/scripts/validate_22k_import.py
```

Expected:
```
============================================================
📊 VALIDATION REPORT — 22.000 PAARE IMPORT
============================================================
✅ prompt_pairs_count: 22000
✅ metrics_full_count: 22000
✅ b_state_count: 22000
✅ sessions_count: ~250 Sessions
✅ hazard_events: ~800-1500 Events
✅ faiss_atomic_pairs: 22000 Vektoren
✅ faiss_metrics_wpf: 22000 Vektoren
✅ faiss_trajectory_wpf: ~17000 Vektoren (80% mit Historie)
============================================================

✅✅✅ PRODUCTION READY — V3.0 DATA LAYER COMPLETE! ✅✅✅
```

---

## 📋 **COMPLETE WORKFLOW**

### **PHASE 0-1: Foundation + Core DB** (wie geplant)

### **PHASE 1.5: LIVE-TEST MIT 1000 PAAREN** (NEU!)

1. **Start Import Pipeline** (Terminal 1):
   ```powershell
   python backend/v3_data_layer/scripts/v3_importer.py --live-monitor --limit 1000
   ```

2. **Start Live Monitor** (Terminal 2):
   ```powershell
   python backend/v3_data_layer/scripts/watch_pipeline.py
   ```

3. **Warte auf Completion** (~2 Sekunden für 1000 Paare)

4. **Run Validation**:
   ```powershell
   python backend/v3_data_layer/scripts/validate_1000_import.py
   ```

5. **GO/NO-GO Decision**:
   - ✅ ALL CHECKS PASS → **GO für 22k**
   - ❌ ANY CHECK FAILS → **FIX & RE-TEST**

### **PHASE 1.6: SCALE-UP AUF 22.000 PAARE**

1. **Start Full Import** (Terminal 1):
   ```powershell
   python backend/v3_data_layer/scripts/v3_importer.py --live-monitor --source full_history
   ```

2. **Monitor** (Terminal 2):
   ```powershell
   python backend/v3_data_layer/scripts/watch_pipeline.py
   ```

3. **Wait** (~34 Sekunden)

4. **Final Validation**:
   ```powershell
   python backend/v3_data_layer/scripts/validate_22k_import.py
   ```

5. **DONE!** ✅

---

## 🎯 **ZUSAMMENFASSUNG**

### **Was du jetzt hast**:
1. ✅ Live-Monitoring während Import (Terminal UI)
2. ✅ Klare GO/NO-GO Kriterien (Validation Script)
3. ✅ Gate-Keeping: 1000 → 22.000 Paare
4. ✅ Alle Tools fertig zur Implementation

### **Timeline**:
- **Phase 0** (Foundation): 2-3 Stunden
- **Phase 1** (Core DB):  1-2 Tage
- **Phase 1.5** (Live-Test 1000): **10 Minuten**
- **Phase 1.6** (Scale-Up 22k): **5 Minuten**
- **Phase 2-4** (Analytics, Learning Engines, Integration): 4-6 Tage

**TOTAL**: ~1 Woche → Production-ready V3.0 Data Layer

---

**NÄCHSTER SCHRITT**: Erstelle die Live-Monitoring Scripts in Phase 1! 🚀
