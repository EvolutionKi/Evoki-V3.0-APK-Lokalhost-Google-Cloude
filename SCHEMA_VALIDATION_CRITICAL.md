# 🚨 SCHEMA VALIDATION REPORT
## Diskrepanzen zwischen Calculator und Database Schemas

**Date:** 2026-02-08  
**Priority:** 🔴 **CRITICAL**

---

## ⚠️ PROBLEM STATEMENT

Der Status Report behauptet "SCHEMA EXISTIERT", aber es gibt **fundamentale Diskrepanzen** zwischen:
1. **Calculator Implementation** (`metrics_calculator_4phase_COMPLETE.py`)
2. **Database Schemas** (`backend/schemas/*.sql`)
3. **Reversibility Test** (`test_reversibility_live.py`)

---

## 🔍 FOUND DISCREPANCIES

### 1. **Data Model Mismatch: Pairs vs Turns**

#### Database Schema (CURRENT):
```sql
-- evoki_metadata_schema.sql
CREATE TABLE prompt_pairs (
    pair_id TEXT PRIMARY KEY,
    user_text TEXT NOT NULL,      -- USER
    ai_text TEXT NOT NULL,         -- AI
    ...
);
```

**Structure:** One row = One user+AI pair

#### Calculator + Test (CURRENT):
```python
# test_reversibility_live.py
CREATE TABLE evoki_core_turns (
    turn_id INTEGER PRIMARY KEY,
    role TEXT CHECK(role IN ('user', 'ai')),
    text TEXT NOT NULL,
    ...
);
```

**Structure:** One row = One turn (either user OR ai)

### **IMPACT:** 🔴 **CRITICAL**
- Calculator test uses `turn_id` + `role`
- Schema uses `pair_id` + separate user/ai fields
- **Incompatible!**

---

### 2. **Metric Column Name Mismatch**

#### Calculator Implementation:
```python
# metrics_calculator_4phase_COMPLETE.py L1487
m["m71_ev_arousal"] = compute_m71_ev_arousal(text)
```

#### Database Schema:
```sql
-- evoki_resonance_schema.sql L190
m71_ev_resonance    REAL,
```

### **IMPACT:** 🟡 **MEDIUM**
- Calculator returns `m71_ev_arousal`
- Schema expects `m71_ev_resonance`
- **Mismatch!**

---

### 3. **Missing Metrics in Schema**

#### Calculator Coverage:
```
Total: 168 metrics (m1-m168)
Tested: 151 metrics functional
```

#### Schema Coverage (evoki_resonance.db):
```
core_metrics:       m1-m20     ✅ (20 metrics)
physics_metrics:    m21-m35    ✅ (15 metrics)
integrity_metrics:  m36-m55    ✅ (20 metrics)
andromatik_metrics: m56-m70    ✅ (15 metrics)
evolution_metrics:  m71-m100   ✅ (30 metrics)

TOTAL RESONANCE: 100 metrics ✅
```

**But where are m101-m168?**

#### Looking at other schemas:

**evoki_triggers_schema.sql:**
```
trauma_metrics:   m101-m115  ✅ (15 metrics)
hazard_log:       m151       ✅ (1 metric)
```

**evoki_metapatterns_schema.sql:**
```
metacog_metrics:  m116-m150  ✅ (35 metrics)
synthesis:        m151-m168  ✅ (18 metrics)
```

### **RESULT:**
```
Resonance:    100 metrics (m1-m100)
Triggers:      16 metrics (m101-m115, m151)
Metapatterns:  53 metrics (m116-m168)
TOTAL:        169 metrics ⚠️ (m151 counted twice!)
```

### **IMPACT:** 🟡 **MEDIUM**
- m151 appears in BOTH triggers AND metapatterns
- Need to clarify which is authoritative

---

### 4. **Reversibility Test Uses Wrong Schema**

#### Test Implementation:
```python
# test_reversibility_live.py L22
CREATE TABLE evoki_core_turns (
    turn_id INTEGER PRIMARY KEY,
    ...
)
```

#### Actual Schemas:
- ❌ No `evoki_core_turns` table exists
- ✅ Only `prompt_pairs` exists

### **IMPACT:** 🔴 **CRITICAL**
- Test creates its own incompatible schema
- Test passes, but won't work with production schema!

---

## 📊 COMPATIBILITY MATRIX

| Component | Data Model | m71 Name | m151 Location | Turn/Pair |
|-----------|------------|----------|---------------|-----------|
| Calculator | Turn-based | `ev_arousal` | Synthesized | Turn |
| Resonance Schema | Pair-based | `ev_resonance` | N/A | Pair |
| Triggers Schema | Pair-based | N/A | `hazard_log` | Pair |
| Metapatterns Schema | Pair-based | N/A | `synthesis` | Pair |
| Reversibility Test | Turn-based | N/A | `evoki_core_turns` | Turn |

**Compatibility:** ❌ **INCOMPATIBLE**

---

## 🎯 ROOT CAUSE ANALYSIS

### Historical Context:

1. **Original Schemas (V2.0?):** Pair-based design
   - User + AI together in one row
   - `prompt_pairs` table

2. **Calculator Design (V3.0):** Turn-based design
   - Separate calculations for user vs AI
   - `role` field distinguishes

3. **Test Implementation:** Created own schema
   - Matched calculator expectations
   - Ignored existing schemas

### **Result:** Two parallel systems that don't talk to each other!

---

## 🔧 REQUIRED FIXES

### Option A: **Migrate Schemas to Turn-Based** (RECOMMENDED)

**Pros:**
- Matches calculator design
- Cleaner separation of user/AI
- More flexible for gradients
- Reversibility test already works

**Cons:**
- Need to migrate existing schemas
- Double the rows (user+AI separate)

**Changes needed:**
```sql
-- NEW: evoki_metadata_schema.sql
CREATE TABLE evoki_core_turns (
    turn_id INTEGER PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('user', 'ai')),
    text TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    gap_seconds INTEGER,
    ...
);

-- DROP: prompt_pairs
-- MIGRATE: Existing data split into 2 rows per pair
```

### Option B: **Adapt Calculator to Pair-Based**

**Pros:**
- No schema migration needed
- Existing data preserved

**Cons:**
- More complex calculator logic
- Harder to track gradients
- Reversibility validator needs rewrite

**Changes needed:**
```python
# Calculator must handle pairs instead of turns
def calculate_all_for_pair(user_text, ai_text, ...):
    user_metrics = calculate_turn(user_text, role='user', ...)
    ai_metrics = calculate_turn(ai_text, role='ai', ...)
    return (user_metrics, ai_metrics)
```

---

## 🚀 RECOMMENDED ACTION PLAN

### **PHASE 1: Schema Alignment (2-3 hours)**

1. **Create unified schema:**
   - Base on turn-based model
   - Update all 4 units

2. **Update schema files:**
   ```
   - evoki_metadata_schema.sql → turn-based
   - evoki_resonance_schema.sql → turn-based
   - evoki_triggers_schema.sql → turn-based  
   - evoki_metapatterns_schema.sql → turn-based
   ```

3. **Fix metric name:**
   ```sql
   -- Change:
   m71_ev_resonance REAL
   -- To:
   m71_ev_arousal REAL
   ```

4. **Clarify m151:**
   ```
   Decision: m151_hazard in triggers.db (primary)
            m151_omega in metapatterns.db (synthesis)
   ```

### **PHASE 2: Migration Script (1-2 hours)**

```python
# migrate_pairs_to_turns.py
def migrate_pair_to_turns(pair):
    """Split one pair into two turns"""
    user_turn = {
        'turn_id': pair.id * 2,
        'role': 'user',
        'text': pair.user_text,
        'timestamp': pair.user_ts
    }
    ai_turn = {
        'turn_id': pair.id * 2 + 1,
        'role': 'ai',
        'text': pair.ai_text,
        'timestamp': pair.ai_ts
    }
    return (user_turn, ai_turn)
```

### **PHASE 3: Validation (1 hour)**

1. Run reversibility test against new schema
2. Verify metric counts match (168 total)
3. Confirm no duplicate m151

---

## 📋 CHECKLIST

### Before T2 (History Import) can proceed:

- [ ] **Schema alignment completed**
  - [ ] Turn-based model finalized
  - [ ] All 4 units updated
  - [ ] m71 name fixed
  - [ ] m151 clarified

- [ ] **Migration strategy**
  - [ ] Migration script written
  - [ ] Test migration on sample data
  - [ ] Rollback plan documented

- [ ] **Validation**
  - [ ] Reversibility test uses production schema
  - [ ] Calculator output matches schema columns
  - [ ] No duplicate metrics

### Estimated Time: **4-6 hours total**

---

## 🎓 LESSONS LEARNED

1. **Schema-first approach essential**
   - Calculator should be built to match schema
   - Not the other way around

2. **Test with production schemas**
   - Don't create custom test schemas
   - Use actual DB files

3. **Version control for schemas**
   - Track schema versions
   - Document breaking changes

4. **Naming conventions matter**
   - `m71_ev_arousal` vs `m71_ev_resonance`
   - Causes silent failures

---

## ✅ CONCLUSION

**Current Status:** ⚠️ **SCHEMAS NOT PRODUCTION-READY**

Despite successful calculator tests, the underlying database schemas are:
- ❌ Incompatible with calculator (pair vs turn)
- ❌ Inconsistent naming (m71)
- ❌ Unclear metric ownership (m151)

**Recommendation:** **STOP T2 IMPORT UNTIL SCHEMAS ARE ALIGNED**

**Priority:** Fix schemas BEFORE importing history

**Estimated Impact:** 4-6 hours delay, but prevents data corruption

---

**Status:** 🔴 **BLOCKERS IDENTIFIED - ACTION REQUIRED**
