# 🔄 EVOKI V3.0 - REVERSIBILITY PRINCIPLE (KERN-GESETZ)

**Version:** V3.0 FINAL  
**Status:** ✅ MANDATORY LAW  
**Created:** 2026-02-08

---

## 🎯 KERN-PRINZIP

```
FORWARD:  x = 1 + 1 + 1 + 1 + 1 = 5
BACKWARD: 5 - 1 - 1 - 1 - 1 - 1 = x

Was in eine Richtung einen Effekt erzeugt,
muss in umgekehrter Reihenfolge ihn auch rückwärts wieder erzeugen!
```

**Das bedeutet:**

Jede Metrik-Berechnung muss **VOLLSTÄNDIG REKONSTRUIERBAR** sein!

---

## ✅ WARUM IST DAS KRITISCH?

### **1. TRAJEKTORIEN-ANALYSE (W-P-F)**

```
W (Vergangenheit): Prompts #90-99
↓
P (Present):       Prompt #100 → m1_A = 0.3, m19_z_prox = 0.7
↓
F (Future):        Prediction basierend auf Trend

OHNE Reversibilität:
- Wir sehen: m19_z_prox = 0.7 (hoch!)
- Wir wissen NICHT: Warum? Welche Inputs führten dazu?

MIT Reversibilität:
- m19_z_prox = 0.7
  ← WEIL m1_A = 0.3 (niedrig)
  ← WEIL m151_hazard = 0.8 (Krise!)
  ← WEIL Text enthielt "umbringen"
  ← WEIL Trend seit Prompt #95 abwärts
```

### **2. REKONSTRUKTION AM SESSION-START**

```
User startet neue Session nach 3 Tagen Pause.

SYSTEM MUSS REKONSTRUIEREN:
"Wo stand der User MENTAL in letzter Session?"

GESPEICHERT:
- m1_A = 0.4
- m19_z_prox = 0.6
- m151_hazard = 0.7

REKONSTRUKTION (BACKWARD):
m19_z_prox = 0.6 (erhöht!)
  ← m1_A = 0.4 (niedrig)
  ← m151_hazard = 0.7 (hoch!)
     ← Lexikon: ["keinen ausweg", "hoffnungslos"]
  ← m101_T_panic = 0.5 (mittel)

KONTEXT:
"User war in Krise (hazard=0.7), 
 niedrige Energie (A=0.4),
 Panik-Marker vorhanden (T_panic=0.5)"
 
→ GUARDIAN: Vorsichtig agieren!
```

### **3. DATA INTEGRITY (AUDIT TRAIL)**

```
Wie bei Buchhaltung:
- Nicht nur Endergebnis speichern!
- ALLE Zwischenschritte speichern!
- Jederzeit rekonstruierbar!

BEISPIEL:
Saldo: 100€
← Einnahme: +50€
← Ausgabe: -20€
← Einnahme: +70€

Wenn wir nur "100€" speichern → keine Transparenz!
Wenn wir alle Schritte speichern → vollständiger Audit Trail!
```

---

## 📊 IMPLEMENTIERUNG

### **REGEL 1: Database MUSS alle Phasen speichern**

**❌ FALSCH:**
```sql
CREATE TABLE metrics_full (
    pair_id TEXT,
    m161_commit TEXT  -- Nur Endergebnis!
);
```

**✅ RICHTIG:**
```sql
CREATE TABLE metrics_full (
    pair_id TEXT,
    
    -- PHASE 1: Base (Independent)
    m2_PCI REAL,
    m8_x_exist REAL,
    m9_b_past REAL,
    m101_T_panic REAL,
    m151_hazard REAL,
    
    -- PHASE 2: Derived (from Phase 1)
    m1_A REAL,
    m4_flow REAL,
    
    -- PHASE 3: Physics (from Phase 1+2)
    m15_affekt_a REAL,
    m19_z_prox REAL,
    m110_black_hole REAL,
    
    -- PHASE 4: Synthesis (from all)
    m151_omega REAL,
    m160_F_risk REAL,
    m161_commit TEXT
);
```

**BEGRÜNDUNG:**
- Jede Phase kann aus vorherigen rekonstruiert werden
- Validation möglich
- Audit Trail vollständig

---

### **REGEL 2: Calculator = FORWARD, Validator = BACKWARD**

```python
class MetricsCalculator:
    """FORWARD: Text → Metrics"""
    
    def calculate_all(self, text, role, context):
        # Phase 1: Base
        phase1 = self._calc_phase1(text)
        
        # Phase 2: Derived (uses Phase 1)
        phase2 = self._calc_phase2(text, phase1)
        
        # Phase 3: Physics (uses Phase 1+2)
        phase3 = self._calc_phase3(text, phase1, phase2)
        
        # Phase 4: Synthesis (uses all)
        phase4 = self._calc_phase4(phase1, phase2, phase3)
        
        return {**phase1, **phase2, **phase3, **phase4}


class MetricsValidator:
    """BACKWARD: Metrics → Validate"""
    
    def validate_all(self, stored_metrics: dict) -> bool:
        # Validate Phase 2 from Phase 1
        if not self._validate_phase2(stored_metrics):
            return False
        
        # Validate Phase 3 from Phase 1+2
        if not self._validate_phase3(stored_metrics):
            return False
        
        # Validate Phase 4 from all
        if not self._validate_phase4(stored_metrics):
            return False
        
        return True
    
    def _validate_phase2(self, m: dict) -> bool:
        """
        BACKWARD: Can Phase 2 be reconstructed from Phase 1?
        """
        # Reconstruct m1_A
        expected_m1_A = compute_m1_A(
            m["m8_x_exist"],
            m["m9_b_past"],
            m["m2_PCI"]
        )
        
        # Compare with stored
        actual_m1_A = m["m1_A"]
        
        if abs(expected_m1_A - actual_m1_A) > 0.01:
            print(f"❌ Phase 2 inconsistent!")
            print(f"   Expected m1_A: {expected_m1_A:.3f}")
            print(f"   Stored m1_A:   {actual_m1_A:.3f}")
            print(f"   Inputs: m8={m['m8_x_exist']:.2f}, "
                  f"m9={m['m9_b_past']:.2f}, PCI={m['m2_PCI']:.2f}")
            return False
        
        return True
```

---

### **REGEL 3: Trajectory Analyzer = BIDIRECTIONAL**

```python
class TrajectoryAnalyzer:
    """Analyzes how metrics evolved (FORWARD + BACKWARD)"""
    
    def analyze(self, pair_ids: List[str]) -> dict:
        """
        FORWARD: How did state evolve?
        BACKWARD: WHY did it evolve this way?
        """
        
        trajectory = []
        
        for i, pair_id in enumerate(pair_ids):
            m = db.get_metrics(pair_id)
            
            # FORWARD: Current state
            state = {
                "pair_id": pair_id,
                "index": i,
                "m1_A": m["m1_A"],
                "m19_z_prox": m["m19_z_prox"],
                "m161_commit": m["m161_commit"]
            }
            
            # BACKWARD: Why this state?
            explanation = {
                "m1_A": self._explain_m1_A(m),
                "m19_z_prox": self._explain_z_prox(m),
                "m161_commit": self._explain_commit(m)
            }
            
            state["explanation"] = explanation
            trajectory.append(state)
        
        return {
            "trajectory": trajectory,
            "trend": self._analyze_trend(trajectory),
            "warnings": self._detect_warnings(trajectory)
        }
    
    def _explain_m1_A(self, m: dict) -> dict:
        """BACKWARD: Why this m1_A value?"""
        return {
            "value": m["m1_A"],
            "formula": "0.3 + 0.2*m8 + 0.1*m9 + 0.15*PCI",
            "inputs": {
                "m8_x_exist": m["m8_x_exist"],
                "m9_b_past": m["m9_b_past"],
                "m2_PCI": m["m2_PCI"]
            },
            "interpretation": self._interpret_m1_A(m["m1_A"])
        }
    
    def _explain_z_prox(self, m: dict) -> dict:
        """BACKWARD: Why this z_prox value?"""
        return {
            "value": m["m19_z_prox"],
            "formula": "f(m1_A, m15, m151_hazard, m101_T_panic)",
            "inputs": {
                "m1_A": m["m1_A"],
                "m15_affekt_a": m["m15_affekt_a"],
                "m151_hazard": m["m151_hazard"],
                "m101_T_panic": m["m101_T_panic"]
            },
            "interpretation": self._interpret_z_prox(m["m19_z_prox"])
        }
```

---

## 🔄 VALIDATION EXAMPLES

### **Example 1: Consistent Metrics** ✅

```python
stored = {
    # Phase 1
    "m8_x_exist": 0.5,
    "m9_b_past": 0.3,
    "m2_PCI": 0.6,
    
    # Phase 2
    "m1_A": 0.52,
}

# BACKWARD Validate
expected_m1_A = 0.3 + 0.2*0.5 + 0.1*0.3 + 0.15*0.6
              = 0.3 + 0.1 + 0.03 + 0.09
              = 0.52

assert abs(expected_m1_A - stored["m1_A"]) < 0.01  # ✅ PASS!
```

### **Example 2: Inconsistent Metrics** ❌

```python
stored = {
    # Phase 1
    "m8_x_exist": 0.5,
    "m9_b_past": 0.3,
    "m2_PCI": 0.6,
    
    # Phase 2
    "m1_A": 0.75,  # ❌ WRONG!
}

# BACKWARD Validate
expected_m1_A = 0.52  # (from calculation above)
actual_m1_A = 0.75

assert abs(expected_m1_A - actual_m1_A) > 0.01  # ❌ FAIL!

# REPAIR:
stored["m1_A"] = expected_m1_A
db.update(stored)
```

---

## 📋 CONSEQUENCES FOR SYSTEM

### **1. T4 Metrics Backfill:**

```python
def backfill_metrics():
    for pair in old_data:
        # Calculate
        metrics = calculator.calculate_all(pair.text, context)
        
        # Store
        db.insert(metrics)
        
        # Validate (CRITICAL!)
        if not validator.validate_all(db.get(pair.id)):
            raise ValueError(f"Inconsistent metrics for {pair.id}!")
```

### **2. Graph Building:**

```python
def build_graph():
    for pair in all_pairs:
        metrics = db.get_metrics(pair.id)
        
        # Validate before using!
        if not validator.validate_all(metrics):
            # Recalculate!
            metrics = calculator.calculate_all(pair.text, context)
            db.update(pair.id, metrics)
        
        graph.add_node(pair.id, metrics)
```

### **3. Guardian Protocol:**

```python
def guardian_check(pair_id):
    m = db.get_metrics(pair_id)
    
    # FORWARD: Is there danger?
    if m["m19_z_prox"] > 0.65:
        # BACKWARD: Why?
        explanation = trajectory.explain_z_prox(m)
        
        alert = {
            "level": "CRITICAL",
            "value": m["m19_z_prox"],
            "causes": explanation["inputs"],
            "lexikon_matches": lexikon.matches(pair.text)
        }
        
        return alert
```

---

## ✅ CHECKL IST FÜR IMPLEMENTATION

Jede neue Feature MUSS:

- [ ] **Database:** Alle Phasen speichern (nicht nur Endergebnis)
- [ ] **Calculator:** Forward-Berechnung in korrekter Phase-Reihenfolge
- [ ] **Validator:** Backward-Validierung implementieren
- [ ] **Tests:** Forward + Backward Tests schreiben
- [ ] **Documentation:** Dependency Chain dokumentieren

---

## 🎯 ZUSAMMENFASSUNG

**REVERSIBILITY PRINCIPLE:**

```
x = 1 + 1 + 1 + 1 + 1 = 5
5 - 1 - 1 - 1 - 1 - 1 = x

FORWARD:  Text → Phase1 → Phase2 → Phase3 → Phase4 → DB
BACKWARD: DB → ValidatePhase4 ← ValidatePhase3 ← ValidatePhase2 ← ValidatePhase1

GLEICHE Formeln, GLEICHE Dependencies, BEIDE Richtungen!
```

**Das ermöglicht:**
- ✅ Trajektorien-Analyse (W-P-F)
- ✅ Rekonstruktion am Session-Start
- ✅ Data Integrity (Audit Trail)
- ✅ Guardian Explanations
- ✅ Debugging & Validation

**Ohne Reversibilität → KEINE EVOKI V3.0!** ⚠️

---

**Status:** ✅ MANDATORY LAW  
**Gilt für:** ALLE Metriken, ALLE Datenbanken, ALLE Berechnungen!
