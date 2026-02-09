# T1 PROGRESS - FullSpectrum168 Contract

**Track:** T1  
**Status:** IN PROGRESS  
**Zeit:** 2026-02-08 00:13

---

## ✅ ERFOLGE

### 1. Contract JSON Generiert!

**Location:** `evoki_fullspectrum168_contract.json`

**Inhalt:**
- **169 metrics** extracted from calculator_spec_A_PHYS_V11
- Alle `compute_m*` functions inspected
- Metadata extracted: id, name, category, range, source, description

**Categories:**
- core: 19 metrics (m1-m20)
- physics: 15 metrics (m21-m35)
- token_economy: 20 metrics (m36-m55)
- andromatik: 18 metrics (m56-m73)
- sentiment: 22 metrics (m74-m95)
- grain: 4 metrics (m96-m99)
- trauma: 14 metrics (m101-m115)
- text_analysis: 25 metrics (m116-m140)
- rag: 10 metrics (m141-m150)
- meta: 11 metrics (m151-m161)
- context: 10 metrics (m162-m167)
- cumulative: 1 metric (m168)

### 2. Generation Script Created

**File:** `generate_contract.py`  
- Inspects calculator_spec module
- Extracts function signatures & docstrings
- Infers categories from metric IDs
- Infers ranges based on metric type
- Outputs JSON contract

---

## ⚠️ ISSUE: 169 statt 168!

**Expected:** 168 metrics (FullSpectrum168)  
**Got:** 169 metrics

**MÖGLICHE GRÜNDE:**
1. Ein Duplikat (z.B. m84_surprise in both sentiment + andromatik?)
2. Ein Ghost-Metric
3. Zählfehler irgendwo

**NEXT:** Contract analysieren & Duplikat finden!

---

## 📋 ROADMAP T1 STATUS

```yaml
- id: T1
  title: "Contract-first: FullSpectrum168 registry sync"
  priority: P0
  depends_on: [T0] ✅
  outputs: 
    - evoki_fullspectrum168_contract.json  ✅ CREATED (aber 169!)
    - metrics_registry.py                  ⏸️ Already exists
  validation: 
    - evoki_invariants.py contract_invariants OK  ⏸️ Need to fix count
```

---

## 🎯 NÄCHSTE SCHRITTE

1. ✅ Find & fix duplicate (169 → 168)
2. ⏸️ Validate contract structure
3. ⏸️ Sync with metrics_registry.py
4. ⏸️ Run contract_invariants test
5. ⏸️ Move to T2 (History ingestion)

---

**STATUS:** ⚠️ **ALMOST COMPLETE** (need to fix count!)
