# 📋 PHASE 2: DAS GEWISSEN (Metriken + Gates)

**Dauer:** 2-3 Tage  
**Schwierigkeit:** ⭐⭐⭐⭐ (Schwer)  
**Was:** 153 Metriken + Double Airlock - LLM NOCH Mock!

---

## 🎯 ZIEL

**Echte Metriken berechnen + Gates feuern** - aber LLM-Response Mock!

**Test:** "Ich will sterben" → T_panic berechnet → Gate A: 🔴 VETO → KEIN LLM-Call!

---

## ✅ CHECKLISTE

### 1. metrics_processor.py portieren

Portiere `docs/specifications/v3.0/sources/v2_metrics_processor.py`

**Erstelle:** `backend/core/metrics_processor.py`

- [ ] 153 Metriken Engine erstellt
- [ ] Berechnung funktioniert

### 2. enforcement_gate.py erstellen

**Gates A + B mit Regelwerk V12 CRC32 Check**

```python
class EnforcementGate:
    def pre_validation(prompt, metrics): 
        # A51, A7.5, A29, A39
    def post_validation(response, metrics):
        # A0, A46
```

- [ ] Gate A implementiert
- [ ] Gate B implementiert

### 3. Temple Integration

Metriken + Gates in `/api/temple/stream`

- [ ] Metriken werden berechnet
- [ ] Gates prüfen vor/nach Mock-LLM

### 4. Frontend Metriken-Anzeige

Live-Metriken in UI

- [ ] Top-5 Metriken sichtbar
- [ ] Gate-Status (🟢/🔴)

### 5. Tests

- [ ] Normal: A=0.7, T_panic=0.1 → Gates offen
- [ ] Veto: "Ich will sterben" → Gate A 🔴
- [ ] Performance: Metriken < 50ms

- [ ] PHASE 2 KOMPLETT

**Weiter:** `PHASE_3_VOICE_LAYER.md`
