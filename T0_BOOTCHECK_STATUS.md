# T0: Bootcheck & Genesis Anchor - STATUS

**Track:** T0  
**Title:** Apply Hardening Blob + Verify Bootcheck  
**Priority:** P0  
**Depends:** None  
**Started:** 2026-02-08 00:03

---

## ZIEL (T0)

**Outputs:**
- `bootcheck_report.json`
- `genesis_anchor_manifest.json`

**Validation:**
```bash
python evoki_bootcheck.py
# exit_code == 0 (dev)
```

---

## AKTUELLE SCHRITTE

### Step 1: SPEC-Datei kopieren ✅

**Ergebnis:** SUCCESS! 774KB file copied.

### Step 2: Bootcheck Pfade fixen ✅

**Problem:** Bootcheck suchte Files im root, aber sie sind in `backend/core/`

**Fix:** `evoki_bootcheck.py` Zeile 538-548 korrigiert:
```python
anchor_files = [
    spec_file,
    "backend/core/evoki_lexika_v3/lexika_complete.py",
    "backend/core/a_phys_v11.py",
    ...
]
```

### Step 3: Genesis Anchor generiert! ✅

**Ergebnis:**
```json
{
  "anchor_ok": true,
  "anchor_current": "3617077bcec4b1b1317e40a4fbac48de47c3a095612449cc94012fac2ecb2ce5",
  "anchor_expected": "3617077bcec4b1b1317e40a4fbac48de47c3a095612449cc94012fac2ecb2ce5"
}
```

**Manifest:** `genesis_anchor_manifest.json` ✅  
**Report:** `logs/bootcheck_report.json` ✅

### Step 4: Fix _check_files_present Pfade ⏳

**Problem:** Import checks fail weil sie im ROOT suchen statt `backend/core/`

**NEXT:** Fix `_check_files_present()` + `_check_imports()` to use backend/core/ paths

---

## ROADMAP KONTEXT

```yaml
- id: T0
  title: "Apply Hardening Blob + Verify Bootcheck"
  priority: P0
  depends_on: []
  outputs: ["bootcheck_report.json", "genesis_anchor_manifest.json"]
  validation: ["python evoki_bootcheck.py exit_code==0 (dev)"]
```

**NÄCHSTER TRACK:** T1 (Contract-first: FullSpectrum168)

---

## ARBEITSPRINZIP

**USER sagte:** "100% fleich wie in Spec, wie ich hinkomme egal"

**BEDEUTET:**
- ✅ Strikt nach Roadmap
- ✅ Genauigkeit > Speed
- ✅ Validation Tests MÜSSEN passen
- ✅ Output-Files wie spec
- ❌ Keine Shortcuts
- ❌ Keine "good enough"

---

**STATUS:** ⏳ In Progress - Waiting for Copy...
