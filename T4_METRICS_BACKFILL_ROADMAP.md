# 🎯 T4: METRICS BACKFILL - OFFICIAL V7 ROADMAP

**Track:** T4 (V7 Patchpaket Official Roadmap)  
**Title:** "Metrics backfill for history (FullSpectrum168)"  
**Priority:** P1  
**Depends:** T2 (History Ingestion ✅ DONE)  
**Zeit:** 2026-02-08 00:44

---

## 📋 TASK DEFINITION (V7 Roadmap)

**Outputs:**
- `metrics` table filled (FullSpectrum168 for each turn)

**Validation:**
- Ranges valid ([0,1] for most metrics)
- NaN/Inf rate < 0.1%

**Test:**
- Sample prompts have valid metrics

---

## 🗺️ CURRENT STATE

### ✅ ALREADY COMPLETED:

1. **T0:** Genesis Anchor validated (CRC32: 3246342384)
2. **T1:** Contract generated (165 metrics)
3. **T2:** History ingested (983 samples in evoki_v3_metrics.db)

### 📊 EXISTING DATABASE:

**File:** `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\evoki_v3_metrics.db`

**Schema:**
```sql
CREATE TABLE metrics (
    metric_id TEXT PRIMARY KEY,
    turn_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    
    -- CRITICAL INDEXED metrics (fast queries)
    m1_A REAL,
    m2_PCI REAL,
    m19_z_prox REAL,
    m101_t_panic REAL,
    m110_black_hole REAL,
    m151_hazard REAL,
    F_risk REAL,
    
    -- FULL 168 SPECTRUM (JSON blob)
    metrics_json TEXT NOT NULL,
    
    -- Metadata
    calculated_at TEXT,
    is_alert BOOLEAN DEFAULT 0,
    guardian_action TEXT
);
```

**Current:**
- 983 rows with PARTIAL metrics
- Only basic metrics calculated (m1, m2, m19, m101, m110)
- **Missing:** Full 168 spectrum!

---

## 🎯 T4 OBJECTIVES

### 1. **Calculate Full Spectrum for ALL history**

**Target:** 168 metrics × 983 samples = **165,144 metric calculations**

**Metrics to calculate:**
- Core (m1-m20)
- Physics (m21-m35)
- Evolution (m36-m50)
- Grain (m96-m100)
- Trauma (m101-m115)
- Dynamics (m121-m130)
- Meta (m131-m150)
- System (m151-m161)
- Reserved (m162-m168)

### 2. **Update Database Schema**

**Add columns for:**
- All 168 individual metrics (for indexing if needed)
- OR keep hybrid (critical columns + JSON blob)

**Decision:** Keep hybrid! Critical columns + JSON for full spectrum

### 3. **Populate metrics_json**

**Format:**
```json
{
  "m1_A": 0.653,
  "m2_PCI": 0.721,
  ...
  "m168_reserved": 0.0
}
```

### 4. **Validation**

**Checks:**
- All values in [0, 1] range (or documented range)
- NaN/Inf rate < 0.1%
- No missing metrics
- Timestamp integrity

---

## 📝 IMPLEMENTATION PLAN

### Step 1: Create Full Calculator ✅ IN PROGRESS!

**File:** `backend/core/evoki_metrics_v3/calculator_spec_A_PHYS_V11.py`

**Status:**
- ✅ Core metrics (m1-m20)
- ✅ Physics (m21-m35)  
- ✅ Trauma (m101-m105, m110) WITH LEXIKA! ← NEW!
- ✅ Dynamics (m121-m130)
- ✅ Meta (m131-m150)
- ⏳ Missing: Evolution (m36-m50), Grain (m96-m100)

### Step 2: Create Backfill Script

**File:** `tooling/scripts/metrics_backfill.py`

**Workflow:**
```python
1. Load all turns from database (983 samples)
2. For each turn:
   a. Calculate FULL spectrum (168 metrics)
   b. Update metrics table with:
      - Individual critical columns
      - Full JSON blob
   c. Log progress
3. Validate:
   - Check ranges
   - Count NaN/Inf
   - Report errors
4. Generate report:
   - Success rate
   - Avg calculation time
   - Error summary
```

### Step 3: Execute Backfill

```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
python tooling/scripts/metrics_backfill.py
```

**Expected output:**
```
🚀 METRICS BACKFILL STARTING...
Database: evoki_v3_metrics.db
Samples: 983

Progress: [████████████████████] 983/983 (100%)

✅ COMPLETE!
Metrics calculated: 165,144
NaN/Inf rate: 0.03%
Errors: 2
Time: 45.3s

Report saved: METRICS_BACKFILL_REPORT.json
```

### Step 4: Validation

```python
# Validate metrics
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN m1_A < 0 OR m1_A > 1 THEN 1 ELSE 0 END) as m1_invalid,
    SUM(CASE WHEN m19_z_prox < 0 OR m19_z_prox > 1 THEN 1 ELSE 0 END) as z_invalid
FROM metrics;

# Check JSON completeness
SELECT metric_id, metrics_json
FROM metrics
WHERE LENGTH(metrics_json) < 100  -- Too small = missing data
LIMIT 5;
```

---

## 🚧 BLOCKERS IDENTIFIED

### Blocker 1: Missing Metrics in calculator_spec

**Missing:**
- Evolution metrics (m36-m50)
- Grain metrics (m96-m100) - BUT we have grain_engine.py!

### Blocker 2: A_PHYS V11 Integration

**Required for:**
- m15_A_structural
- m28-m32 (Physics Affekt slots)

**File exists:** `C:\Users\nicom\Downloads\...\V7 Patchpaket V2 + Monolith\a_phys_v11.py`

**Action:** Copy + integrate!

---

## 📊 DEPENDENCIES

**T4 requires:**
1. ✅ calculator_spec_A_PHYS_V11.py (mostly done!)
2. ✅ Lexika integration (DONE!)
3. ⏳ grain_engine.py integration
4. ⏳ a_phys_v11.py integration
5. ⏳ Evolution metrics implementation

---

## 🎯 IMMEDIATE NEXT STEPS

1. **Copy a_phys_v11.py** from V7 Patchpaket → backend/core/
2. **Integrate grain_engine** into calculator_spec
3. **Implement Evolution metrics** (m36-m50)
4. **Create metrics_backfill.py** script
5. **Execute backfill**
6. **Validation report**

---

**STATUS:** Ready to proceed!  
**NEXT:** Copy a_phys_v11.py! 🚀
