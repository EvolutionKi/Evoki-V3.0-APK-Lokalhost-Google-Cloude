# 🎯 T3: LEXIKA INTEGRATION - ACTION PLAN

**Track:** T3  
**Status:** 🚀 **IN PROGRESS**  
**Zeit:** 2026-02-08 00:39

---

## ✅ DISCOVERY COMPLETE!

### LEXIKA GEFUNDEN!

**File:** `backend/core/evoki_lexika_v3/lexika_complete.py`  
**Lines:** 959  
**Source:** FINAL7 Book 6 (extracted in previous session!)

**Classes:**
1. ✅ `AngstromLexika` - Gesprächstiefe (S_SELF, X_EXIST, B_PAST)
2. ✅ `TraumaLexika` - Trauma markers (T_PANIC, T_DISSO, T_INTEG)
3. ✅ `HazardLexika` - Guardian triggers (SUICIDE_MARKERS, CRISIS_MARKERS)
4. ✅ `LoopLexika` - ZLF detection
5. ✅ `AffektKategorien` - Affekt taxonomy
6. ✅ `BVektorConfig` - 7D Soul Signature

**Total:** 400+ weighted terms!

---

## 🔧 INTEGRATION TASKS

### Task 1: Import Lexika in calculator_spec

**Current:**
```python
# calculator_spec_A_PHYS_V11.py
# NO IMPORTS from lexika!
```

**Target:**
```python
from backend.core.evoki_lexika_v3.lexika_complete import (
    HazardLexika,
    TraumaLexika,
    AngstromLexika
)
```

### Task 2: Update compute_m151_hazard()

**Current:** Missing!

**Target:**
```python
def compute_m151_hazard(text: str) -> float:
    """
    m151: Guardian Hazard Score
    Scans for suicide/crisis markers
    """
    score = 0.0
    text_lower = text.lower()
    
    # Scan all hazard lexika
    for term, weight in HazardLexika.SUICIDE_MARKERS.items():
        if term in text_lower:
            score += weight
    
    for term, weight in HazardLexika.SELF_HARM_MARKERS.items():
        if term in text_lower:
            score += weight * 0.9
    
    for term, weight in HazardLexika.CRISIS_MARKERS.items():
        if term in text_lower:
            score += weight * 0.7
    
    # Normalize by text length (log scale)
    words = len(text_lower.split())
    normalized = score / (1 + math.log(words + 1))
    
    return min(1.0, normalized * 2.0)  # Scale up
```

### Task 3: Update compute_m19_z_prox()

**Current:**
```python
def compute_m19_z_prox(m1_A_lexical, m15_A_structural, LL, text, t_panic):
    # Missing hazard integration!
```

**Target:**
```python
def compute_m19_z_prox(m1_A_lexical, m15_A_structural, LL, text, t_panic, m151_hazard):
    # Include hazard in calculation
    base_z = (1.0 - m1_A_lexical) * LL
    hazard_boost = m151_hazard * 0.5  # 50% contribution
    z_prox = base_z + hazard_boost
    
    # Safety overrides
    if t_panic > 0.7:
        z_prox = max(z_prox, 0.65)
    
    return min(1.0, z_prox)
```

### Task 4: Update Dual-Gradient Engine

**File:** `backend/core/dual_gradient_engine.py`

**Add:**
```python
# Import hazard function
from evoki_metrics_v3.calculator_spec_A_PHYS_V11 import compute_m151_hazard

# In calculate_snapshot():
m151_hazard = compute_m151_hazard(text)

# In analyze():
nabla_hazard = ai_metrics.m151_hazard - user_metrics.m151_hazard

if nabla_hazard > 0.5:  # AI introduced severe hazard!
    action = "ALERT"
```

---

## 📋 EXECUTION PLAN

### Step 1: Create Updated calculator_spec ✅ NEXT!

File: `backend/core/evoki_metrics_v3/calculator_spec_A_PHYS_V11_LEXIKA.py`

- Import lexika
- Add `compute_m151_hazard()`
- Update `compute_m19_z_prox()` signature
- Add lexika scans to all trauma functions

### Step 2: Test Lexika Integration

```bash
python -c "from backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11_LEXIKA import compute_m151_hazard; print(compute_m151_hazard('Ich will sterben'))"
# Expected: ~0.8-1.0
```

### Step 3: Update Dual-Gradient

- Import new functions
- Add m151_hazard to MetricsSnapshot
- Add hazard gradient analysis

### Step 4: Re-test

```bash
python test_dual_gradient.py
# Expected: ALERT on suicide scenarios!
```

---

## 🎯 SUCCESS CRITERIA

1. ✅ Lexika imported successfully
2. ✅ `compute_m151_hazard()` returns >0.8 for "umbringen"
3. ✅ Dual-gradient detects harmful AI responses
4. ✅ Test Case 1 (Suicide) triggers ALERT
5. ✅ Test Case 2 (Panic) triggers WARN/ALERT

---

**STATUS:** Ready to implement! 🚀

**NEXT:** Create `calculator_spec_A_PHYS_V11_LEXIKA.py` with full integration!
