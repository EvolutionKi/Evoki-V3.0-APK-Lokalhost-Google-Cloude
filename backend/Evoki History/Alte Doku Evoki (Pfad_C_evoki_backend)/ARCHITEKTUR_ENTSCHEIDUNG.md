# 🏗️ ARCHITEKTUR-ENTSCHEIDUNG: V11 füttern vs. Neu aufbauen

## Ausgangslage

### Backend V11 (evoki_engine_v11.py - 1514 Zeilen)
```
Klassen:
├── VectorizationService      → Text → 384D Vektor
├── ErrorRegistry             → Fehler-Tracking
├── PhysicsEngine             → KERN: Affekt, Trajektorie, Gefahrenzonen
├── StorageAdapter (abstract) → Speicher-Interface
├── IntegrityEngine           → Regelwerk-Check, Prüfkennzahl
└── Flask API                 → REST Endpoints
```

**Was V11 KANN:**
- ✅ Vektorisierung (jetzt VectorRegs-kompatibel dank Model-Fix)
- ✅ Affekt-Berechnung (A, ∇A)
- ✅ Gefahrenzonen-Erkennung (Trauma F)
- ✅ Trajektorien-Analyse (Wächter-Veto A7.5)
- ✅ Affektbrücken (Wurmloch-Navigation)
- ✅ Prüfkennzahl-Berechnung (A37)
- ✅ Master-Blaupause V7.0 vollständig eingebettet

**Was V11 NICHT KANN:**
- ❌ 60+ Metriken aus MetricsService.ts
- ❌ Φ-Layer (phi_score, U, R)
- ❌ EV-Familie (resonance, tension, readiness)
- ❌ Dyade-Metriken (nablaA_dyad, T_balance)
- ❌ Trübungs-Modell (T_fog, I_eff)
- ❌ Gravitations-Phase (G_phase)
- ❌ Klassifikation (evo_form: Near-z, Stagnation, etc.)

---

### Frontend MetricsService.ts (318 Zeilen)
```
Metriken in 10 Kategorien:
├── C) Core/Kontext   → gap_s, flow, coh, rep_same, ZLF, LL
├── D) Physics V11    → A, PCI, nabla_A, z_prox, x_fm_prox
├── E) Vektorraum     → cos_prevk, G_phase, is_affect_bridge
├── F) Soul/Integrity → soul_integrity, soul_check, guardian
├── G) Dyade          → H_conv, nablaA_dyad, T_balance
├── H) Trauma         → T_panic, T_disso, T_shock, T_fog
├── I) EV-Familie     → EV_resonance, EV_tension, danger
├── J) Φ-Layer        → U, R, phi_score, phi_score2
├── K) Klassifikation → evo_form (Near-z, Kernfusion, etc.)
└── Guardian          → commit_action, mode_hp
```

**Frontend-Vorteile:**
- ✅ Vollständiges Metrik-Registry
- ✅ TypeScript-typisiert (IMetricsState)
- ✅ LIVE-Berechnung (kein Speicher-Overhead)
- ✅ Modular (VectorizationService, RuleEngine)

---

### Master-Blaupause V7.0 (in V7.py - 1840 Zeilen)
```
MASTER_BLAUPAUSE_CORE_TEXT enthält:
├── A0-A67: Alle Meta-Regeln vollständig
├── A66: Homöostase (Volatilitäts-Threshold)
├── A67: Selbstreflexion
├── A65: Strategische Voraussicht
└── Kompletter historischer Kontext
```

**V7 hat:**
- ✅ Vollständigstes Regelwerk (A0-A67 vs V11: A0-A52)
- ✅ CognitiveCore mit Gemini-Integration
- ✅ Chronik-Protokoll
- ✅ Metakognitive Synthese
- ❌ Kein VectorRegs-Support
- ❌ Komplexere Flask-API

---

## 🎯 EMPFEHLUNG: HYBRID-ANSATZ

### NICHT V11 füttern, NICHT komplett neu aufbauen!

```
┌─────────────────────────────────────────────────────────────┐
│  NEUE ARCHITEKTUR: evoki_engine_v12.py                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Fundament: V11 PhysicsEngine                        │   │
│  │  - VectorizationService (VectorRegs-kompatibel)      │   │
│  │  - StorageAdapter → VectorRegsIntegration            │   │
│  │  - PhysicsEngine (Gefahrenzonen, Trajektorie)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Erweiterung: MetricsService.ts → Python Port        │   │
│  │  - 11 MINIMALE Metriken (siehe METRIK_ANALYSE.py)    │   │
│  │  - A, nabla_A, z_prox, danger, T_shock, phi_score    │   │
│  │  - LIVE berechnet, NICHT gespeichert                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Regelwerk: Master-Blaupause V7.0 (vollständig)      │   │
│  │  - A0-A67 aus evoki_engine_v7.py                     │   │
│  │  - Integrität 2.0, Seelen-Schlüssel                  │   │
│  │  - Chronik-Protokoll                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Konkrete Schritte

### Phase 1: Minimaler MetricsService für Python (1-2h)
```python
# evoki_metrics_service.py - Port von MetricsService.ts
class MetricsService:
    def calculate_minimal(self, text, history) -> dict:
        return {
            'A': self._calc_A(text, history),
            'nabla_A': ...,
            'z_prox': ...,
            'danger': ...,
            'T_shock': ...,
            'T_panic': ...,
            'T_disso': ...,
            'phi_score': ...,
            'evo_form': ...,
            'LL': ...,
            'affektwert': self._A_to_kategorie(A)  # A-F
        }
```

### Phase 2: V11 + MetricsService fusionieren (1h)
```python
# In evoki_engine_v11.py
from evoki_metrics_service import MetricsService

class PhysicsEngine:
    def __init__(self, ...):
        self.metrics = MetricsService(self.vector_service)
    
    def process_interaction(self, text, history):
        metrics = self.metrics.calculate_minimal(text, history)
        # Gefahrenzonen-Check mit metrics['danger']
        # Trajektorie mit metrics['z_prox']
```

### Phase 3: Master-Blaupause V7.0 integrieren (30min)
```python
# Kopiere MASTER_BLAUPAUSE_CORE_TEXT von V7.py → V11.py
# Ersetze REGELWERK_VOLLTEXT (A0-A52) mit V7.0 (A0-A67)
```

### Phase 4: VectorRegs vollständig anbinden (bereits done!)
```python
# vectorRegsIntegration.py ist ready
# 21,332 Vektoren laden erfolgreich
```

---

## Warum NICHT komplett neu?

1. **V11 PhysicsEngine ist SOLID**
   - Gefahrenzonen-Logik funktioniert
   - Trajektorien-Analyse ist wertvoll
   - Affektbrücken-Navigation einzigartig

2. **Frontend-MetricsService ist KOMPLEX**
   - 318 Zeilen TypeScript
   - Viele Abhängigkeiten (VectorizationService, RuleEngine)
   - Live-Berechnung optimal - nicht alles muss nach Python

3. **VectorRegs-Integration FERTIG**
   - Model-Mismatch behoben
   - StorageAdapter bereit
   - 70.2 Mio. Dimensionen warten

---

## Fazit

| Ansatz | Aufwand | Risiko | Ergebnis |
|--------|---------|--------|----------|
| V11 füttern | 2-3h | Niedrig | 80% Funktionalität |
| Komplett neu | 2-3 Tage | Hoch | 100% aber Bugs |
| **HYBRID** | **4-5h** | **Mittel** | **95% mit V7.0 Regelwerk** |

**Meine Empfehlung: HYBRID**
- V11 als stabiles Fundament behalten
- 11 minimale Metriken aus Frontend portieren
- Master-Blaupause V7.0 (A0-A67) einfügen
- VectorRegs-Integration aktivieren

Soll ich mit Phase 1 beginnen?
