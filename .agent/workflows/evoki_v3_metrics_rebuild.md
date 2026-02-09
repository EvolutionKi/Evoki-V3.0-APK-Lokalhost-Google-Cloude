---
description: Rebuild Evoki V3 metrics from 193 bloated files to 25 core metrics (V12 Clean Architecture)
---

# V3 Metrics Rebuild Workflow

Complete rebuild of Evoki V3 metrics system following V12 Clean Architecture.

**Goal**: Reduce 193 metrics → 25 core metrics with 6-phase calculation pipeline

---

## Prerequisites

1. Backup current state:
```bash
git checkout -b metrics-v12-rebuild
git add -A
git commit -m "Backup before V12 Clean rebuild"
```

2. Read documentation:
- `docs/specifications/v3.0/METRIC_MAPPING_153_TO_25.txt`
- `docs/specifications/v3.0/V11_1_FORMULAS_COMPLETE.md`
- `.gemini/antigravity/brain/{conversation-id}/metrics_audit_v12.md`

---

## Step 1: Archive Legacy System

```bash
cd "c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3"
mv metrics_lib metrics_lib_legacy
mkdir metrics_lib_v12_clean
```

---

## Step 2: Copy 25 Core Metrics

Copy only these files from `metrics_lib_legacy/` to `metrics_lib_v12_clean/`:

**Foundation (5)**:
```bash
cp metrics_lib_legacy/m1_A.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m2_PCI.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m19_z_prox.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m7_LL.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m6_ZLF.py metrics_lib_v12_clean/
```

**Dynamics (3)**:
```bash
cp metrics_lib_legacy/m17_nabla_a.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m23_nabla_pci.py metrics_lib_v12_clean/
# nabla_delta_A needs to be created (new)
```

**Trauma (3)**:
```bash
cp metrics_lib_legacy/m101_t_panic.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m102_t_disso.py metrics_lib_v12_clean/
cp metrics_lib_legacy/m103_t_integ.py metrics_lib_v12_clean/
```

**Support Files**:
```bash
cp metrics_lib_legacy/_helpers.py metrics_lib_v12_clean/
cp metrics_lib_legacy/_lexika.py metrics_lib_v12_clean/
```

---

## Step 3: Create Phase Engine

Create `backend/core/evoki_metrics_v3/metrics_engine_v3.py`:

```python
def compute_all_metrics(user_text: str, ai_text: str, context: dict) -> dict:
    """
    6-Phase Calculation Pipeline
    CRITICAL: Do NOT compute linearly m1→m168!
    """
    results = {}
    
    # Phase 1: Analysis (no dependencies)
    results.update(phase_1_analysis(user_text, ai_text))
    
    # Phase 2: Core Physics
    results.update(phase_2_core(user_text, ai_text, results))
    
    # Phase 3a: Trauma Pre-Scan (SAFETY)
    trauma_pre = phase_3a_trauma_prescan(user_text, results)
    safe_mode = trauma_pre['t_panic_pre'] > 0.6
    
    # Phase 3b: Context & RAG (conditional)
    results.update(phase_3b_context_rag(context, safe_mode, results))
    
    # Phase 4: Trauma Full
    results.update(phase_4_trauma_full(user_text, results))
    
    # Phase 5: Dynamics (needs m103 from Phase 4)
    results.update(phase_5_dynamics(results))
    
    # Phase 6: Synthesis
    results.update(phase_6_synthesis(results))
    
    return results
```

---

## Step 4: Implement Dual-Gradient System

Update database schema in `backend/deep_earth/evoki_v3_core.db`:

```sql
CREATE TABLE IF NOT EXISTS metrics_full (
    prompt_pair_id INTEGER PRIMARY KEY,
    
    -- User Gradient (∇A)
    user_m1_A REAL,
    user_m2_PCI REAL,
    user_m19_z_prox REAL,
    user_m101_t_panic REAL,
    ...
    
    -- AI Gradient (∇B)
    ai_m1_A REAL,
    ai_m2_PCI REAL,
    ai_m161_commit REAL,
    ...
    
    -- Disharmony Detection
    disharmony_score REAL
);
```

---

## Step 5: Build Temple Data Layer

Create in `backend/deep_earth/`:

**5 SQLite Databases**:
```bash
# Core DB
sqlite3 evoki_v3_core.db < schema_core.sql

# Trajectories (Historical Futures)
sqlite3 evoki_v3_trajectories.db < schema_trajectories.sql

# Analytics (Full Logging)
sqlite3 evoki_v3_analytics.db < schema_analytics.sql

# Graph (Relationships)
sqlite3 evoki_v3_graph.db < schema_graph.sql

# Keywords (Learning System)
sqlite3 evoki_v3_keywords.db < schema_keywords.sql
```

**FAISS Indices**:
```python
# Initialize 4 namespaces
faiss_index = faiss.IndexFlatIP(384)
# Save to: backend/deep_earth/faiss/evoki_v3_vectors.faiss
```

---

## Step 6: Safety & Integrity Layer

**Genesis Anchor**:
```python
# backend/core/evoki_metrics_v3/genesis_anchor.py
import hashlib

GENESIS_HASH = "..."  # SHA-256 of regelwerk_v12.json

def validate_genesis_anchor():
    rulebook = Path("backend/core/regelwerk_v12.json")
    current_hash = hashlib.sha256(rulebook.read_bytes()).hexdigest()
    
    if current_hash != GENESIS_HASH:
        raise IntegrityError("Genesis Anchor mismatch!")
```

**Enforcement Gates**:
```python
# backend/core/evoki_metrics_v3/enforcement_gates_v3.py

def gate_a_pre_llm(user_input: str) -> bool:
    """Pre-LLM Security"""
    validate_genesis_anchor()
    hazard_check = scan_hazard_lexicon(user_input)
    if hazard_check > 0.8:
        return False  # VETO
    return True

def gate_b_post_llm(ai_response: str, metrics: dict) -> bool:
    """Post-LLM Validation"""
    # Dual Audit: Semantic > Mathematical
    if metrics['z_prox'] > 0.65:
        semantic_safe = llm_safety_check(ai_response)
        return semantic_safe  # Semantic wins
    return True
```

---

## Step 7: Update Configuration

**lexika_v3.json** (Source of Truth):
```json
{
  "T_panic": {
    "keywords": ["suizid", "sterben", "töten", ...],
    "weights": {"suizid": 1.0, "angst": 0.3}
  },
  "thresholds": {
    "z_prox_critical": 0.65,
    "z_prox_warning": 0.50,
    "t_panic_veto": 0.9
  }
}
```

**regelwerk_v12.json**:
- Immutable rulebook
- Calculate SHA-256: `python -c "import hashlib; print(hashlib.sha256(open('regelwerk_v12.json','rb').read()).hexdigest())"`
- Store hash in `genesis_anchor.py`

---

## Step 8: Testing

### Unit Tests
```bash
# Test phase order
python -m pytest backend/tests/test_phase_order.py

# Test dual-gradient
python -m pytest backend/tests/test_dual_gradient.py

# Test safety thresholds
python -m pytest backend/tests/test_safety_gates.py
```

### Integration Test
```python
# backend/tests/test_full_pipeline.py
def test_full_pipeline():
    user_input = "Test prompt"
    ai_response = "Test response"
    
    # Phase 1-6 execution
    metrics = compute_all_metrics(user_input, ai_response, {})
    
    # Verify all 25 core metrics present
    assert 'm1_A' in metrics
    assert 'm19_z_prox' in metrics
    ...
    
    # Verify dual-gradient separation
    assert 'user_m1_A' in metrics
    assert 'ai_m1_A' in metrics
```

---

## Step 9: Deployment

```bash
# Rename v12_clean → metrics_lib
mv metrics_lib_v12_clean metrics_lib

# Update __init__.py
python backend/core/evoki_metrics_v3/generate_init.py

# Final verification
python backend/core/evoki_metrics_v3/verify_system.py
```

---

## Step 10: Verification Checklist

- [ ] Only 25 core metrics in `metrics_lib/`
- [ ] 6-phase calculation prevents circular deps
- [ ] Dual-gradient system working (User ∇A vs AI ∇B)
- [ ] Temple Data Layer created (5 DBs + FAISS)
- [ ] Genesis Anchor passes on boot
- [ ] Safety Gates (A & B) functional
- [ ] All formulas match V11.1 spec
- [ ] Performance < 2500ms

---

## Rollback (If Needed)

```bash
git checkout HEAD -- backend/core/evoki_metrics_v3/
mv metrics_lib_legacy metrics_lib
```

---

## References

- Implementation Plan: `.gemini/antigravity/brain/{id}/implementation_plan.md`
- Metrics Audit: `.gemini/antigravity/brain/{id}/metrics_audit_v12.md`
- V12 Mapping: `docs/specifications/v3.0/METRIC_MAPPING_153_TO_25.txt`
- V11.1 Formulas: `docs/specifications/v3.0/V11_1_FORMULAS_COMPLETE.md`
