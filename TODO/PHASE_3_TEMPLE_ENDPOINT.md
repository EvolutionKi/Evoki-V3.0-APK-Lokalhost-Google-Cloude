# 📋 PHASE 3: TEMPLE ENDPOINT

**Dauer:** 2-3 Tage  
**Schwierigkeit:** ⭐⭐⭐ (Schwer - aber machbar!)  
**Was machen wir:** Der Haupt-Endpoint mit allen Features

---

## 🎯 ZIEL DIESER PHASE

Am Ende kannst du einen **API-Call** an `/api/temple/process` schicken und bekommst eine **therapeutische Antwort** zurück!

**Test:** POST Request mit Prompt → Response + Metriken

---

## 💡 WAS MACHT DIESER ENDPOINT?

**Der komplette Flow:**
1. User schickt Nachricht
2. Berechne 153 Metriken
3. **GATE A** prüft (Guardian-Veto?)
4. FAISS durchsuchen (Kontext finden)
5. **Gemini API** Call (LLM generiert Antwort)
6. **GATE B** prüft (Antwort OK?)
7. Speichere in 21 DBs
8. Sende Antwort an User

**Das ist das Herz von Evoki! 💚**

---

## ✅ CHECKLISTE

### SCHRITT 1: metrics_processor.py erstellen

**Was tun:** Erstelle `backend/core/metrics_processor.py`

**Inhalt (Vereinfachte Version):**
```python
from sentence_transformers import SentenceTransformer
import re

class MetricsProcessor:
    def __init__(self):
        # Model für Embeddings
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    def calculate(self, text: str) -> dict:
        """
        Berechnet Metriken für einen Text
        """
        metrics = {}
        
        # Core Metrics
        metrics['A'] = self._calculate_affekt(text)
        metrics['PCI'] = self._calculate_pci(text)
        metrics['coh'] = self._calculate_coherence(text)
        
        # Trauma Metrics
        metrics['T_panic'] = self._detect_panic(text)
        metrics['T_disso'] = self._detect_dissociation(text)
        
        # B-Vektor (7D)
        metrics['B_life'] = 0.85  # Dummy
        metrics['B_truth'] = 0.90
        metrics['B_depth'] = 0.75
        metrics['B_init'] = 0.70
        metrics['B_warmth'] = 0.80
        metrics['B_safety'] = 0.85
        metrics['B_clarity'] = 0.88
        
        # Composite
        metrics['B_align'] = self._calculate_alignment(metrics)
        metrics['F_risk'] = self._calculate_risk(metrics)
        
        return metrics
    
    def _calculate_affekt(self, text: str) -> float:
        """Affekt: 0.0 (tödlich) → 1.0 (erleuchtet)"""
        # Vereinfacht: Zähle positive vs negative Wörter
        positive_words = ['gut', 'freude', 'liebe', 'hoffnung']
        negative_words = ['schlecht', 'angst', 'traurig', 'leer']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        # A = 0.5 + (positiv - negativ) * 0.1
        a = 0.5 + (pos_count - neg_count) * 0.1
        return max(0.0, min(1.0, a))
    
    def _calculate_pci(self, text: str) -> float:
        """Prozess-Kohärenz-Index"""
        # Vereinfacht: Satzlänge als Proxy
        words = len(text.split())
        return min(1.0, words / 50.0)
    
    def _calculate_coherence(self, text: str) -> float:
        """Kohärenz"""
        # Dummy
        return 0.8
    
    def _detect_panic(self, text: str) -> float:
        """Panik-Detektion"""
        panic_keywords = ['panik', 'angst', 'herzrasen', 'hyperventil']
        text_lower = text.lower()
        count = sum(1 for kw in panic_keywords if kw in text_lower)
        return min(1.0, count * 0.3)
    
    def _detect_dissociation(self, text: str) -> float:
        """Dissoziation"""
        disso_keywords = ['unwirklich', 'nebel', 'abgetrennt', 'neben mir']
        text_lower = text.lower()
        count = sum(1 for kw in disso_keywords if kw in text_lower)
        return min(1.0, count * 0.3)
    
    def _calculate_alignment(self, metrics: dict) -> float:
        """B-Align aus B-Vektor"""
        b_values = [
            metrics['B_life'], metrics['B_truth'], metrics['B_depth'],
            metrics['B_init'], metrics['B_warmth'], metrics['B_safety'], metrics['B_clarity']
        ]
        return sum(b_values) / len(b_values)
    
    def _calculate_risk(self, metrics: dict) -> float:
        """F-Risk"""
        return 1.0 - metrics['A']  # Inverser Affekt
```

**WICHTIG:** Das ist eine VEREINFACHTE Version! V2.0 hatte 90+ Metriken in metrics_processor.py.

- [ ] Datei erstellt
- [ ] Code läuft (teste mit `python -c "from core.metrics_processor import MetricsProcessor; m = MetricsProcessor(); print(m.calculate('test'))"`)

---

### SCHRITT 2: enforcement_gate.py erstellen

**Was tun:** Erstelle `backend/core/enforcement_gate.py`

**Inhalt:**
```python
import zlib
from pathlib import Path
import json

class EnforcementGate:
    """Double Airlock: Gate A + Gate B"""
    
    def __init__(self):
        # Regelwerk V12 laden
        regelwerk_path = Path(__file__).parent.parent.parent / "app/interface/public/EVOKI_REGELWERKE_GENESIS/regelwerk_v12.json"
        
        if not regelwerk_path.exists():
            raise Exception(f"Regelwerk nicht gefunden: {regelwerk_path}")
        
        self.regelwerk = self._load_regelwerk(regelwerk_path)
        self.genesis_crc32 = 3246342384  # A51 Genesis Anchor
    
    def _load_regelwerk(self, path: Path) -> dict:
        """Lädt Regelwerk mit CRC32-Check"""
        text = path.read_text(encoding='utf-8')
        
        # A51: Genesis Anchor Check
        calculated_crc = zlib.crc32(text.encode('utf-8')) & 0xFFFFFFFF
        
        if calculated_crc != self.genesis_crc32:
            raise Exception(f"A51 GENESIS ANCHOR BREACH! CRC32: {calculated_crc} != {self.genesis_crc32}")
        
        return json.loads(text)
    
    def pre_validation(self, prompt: str, metrics: dict) -> dict:
        """
        GATE A: PRE-PROMPT VALIDATION
        Vor Google API Call!
        """
        veto_reasons = []
        
        # A7.5/A29: Guardian-Veto bei hoher Panik
        if metrics.get('T_panic', 0) > 0.8:
            veto_reasons.append("T_panic > 0.8 (Guardian-Veto)")
        
        # F-Risk Check
        if metrics.get('F_risk', 0) > 0.6:
            veto_reasons.append("F_risk > 0.6 (Gefahr)")
        
        # A39: Krisenprompt-Erkennung
        crisis_keywords = ['suizid', 'sterben', 'töten', 'umbringen']
        if any(kw in prompt.lower() for kw in crisis_keywords):
            veto_reasons.append("A39 Krisenprompt erkannt")
        
        return {
            'passed': len(veto_reasons) == 0,
            'veto_reasons': veto_reasons,
            'gate': 'A'
        }
    
    def post_validation(self, response: str, metrics: dict, context_chunks: list = []) -> dict:
        """
        GATE B: POST-RESPONSE VALIDATION
        Nach LLM, vor User!
        """
        veto_reasons = []
        
        # A0: Direktive der Wahrheit (keine Halluzination)
        if self._check_hallucination(response, context_chunks):
            veto_reasons.append("A0 Halluzination erkannt")
        
        # A46: Soul-Signature (B-Align Check)
        if metrics.get('B_align', 0) < 0.7:
            veto_reasons.append("A46 B_align < 0.7 (Soul-Signature)")
        
        return {
            'passed': len(veto_reasons) == 0,
            'veto_reasons': veto_reasons,
            'gate': 'B'
        }
    
    def _check_hallucination(self, response: str, chunks: list) -> bool:
        """Prüft ob Response Fakten erfindet"""
        # TODO: Implement via Chunk-Overlap
        return False
```

- [ ] Datei erstellt
- [ ] CRC32-Check funktioniert

---

### SCHRITT 3: temple.py Endpoint erstellen

**Was tun:** Erstelle `backend/api/temple.py`

**Inhalt:**
```python
from fastapi import APIRouter
from pydantic import BaseModel
from core.metrics_processor import MetricsProcessor
from core.enforcement_gate import EnforcementGate
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Globals
metrics_proc = MetricsProcessor()
gate = EnforcementGate()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/process")
async def temple_process(req: PromptRequest):
    """
    Haupt-Endpoint für Temple Tab
    """
    user_prompt = req.prompt
    
    # PHASE 1: Metriken berechnen
    metrics = metrics_proc.calculate(user_prompt)
    
    # GATE A: PRE-PROMPT VALIDATION
    gate_a = gate.pre_validation(user_prompt, metrics)
    
    if not gate_a['passed']:
        return {
            'veto': 'PRE_PROMPT',
            'veto_reasons': gate_a['veto_reasons'],
            'metrics': metrics
        }
    
    # PHASE 2: Mock Response (später: Gemini API)
    response = f"Ich verstehe. Du sagst: '{user_prompt}'. Lass uns darüber sprechen."
    
    # GATE B: POST-RESPONSE VALIDATION
    gate_b = gate.post_validation(response, metrics)
    
    if not gate_b['passed']:
        return {
            'veto': 'POST_RESPONSE',
            'veto_reasons': gate_b['veto_reasons'],
            'metrics': metrics
        }
    
    # SUCCESS
    return {
        'response': response,
        'metrics': metrics,
        'veto': None
    }
```

- [ ] Datei erstellt
- [ ] Endpoint registriert in main.py

---

### SCHRITT 4: main.py aktualisieren

**Was tun:** Füge Temple Router zu `backend/main.py` hinzu

**Zeile hinzufügen:**
```python
from api.temple import router as temple_router

# ...

app.include_router(temple_router, prefix="/api/temple", tags=["temple"])
```

- [ ] Import hinzugefügt
- [ ] Router registriert

---

### SCHRITT 5: Backend neu starten & testen

**Was tun:**
```bash
cd backend
python main.py
```

**Teste mit curl oder Postman:**
```bash
curl -X POST http://localhost:8000/api/temple/process \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Ich fühle mich heute leer\"}"
```

**Erwartung:**
```json
{
  "response": "Ich verstehe. Du sagst: 'Ich fühle mich heute leer'. Lass uns darüber sprechen.",
  "metrics": { "A": 0.5, ... },
  "veto": null
}
```

- [ ] Endpoint funktioniert
- [ ] Metriken werden berechnet

---

### SCHRITT 6: Guardian-Veto testen

**Was tun:** Teste mit Krisenprompt

```bash
curl -X POST http://localhost:8000/api/temple/process \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Ich will sterben\"}"
```

**Erwartung:**
```json
{
  "veto": "PRE_PROMPT",
  "veto_reasons": ["A39 Krisenprompt erkannt"],
  "metrics": { ... }
}
```

- [ ] Guardian-Veto funktioniert
- [ ] Kein API-Call bei Krise

---

## ✅ PHASE 3 ABSCHLUSS-CHECK

**Finale Tests:**

1. ✅ Normaler Prompt → Response
2. ✅ Krisenprompt → Veto
3. ✅ Metriken werden berechnet
4. ✅ Gates funktionieren

**Falls alle 4 OK:**
- [ ] Phase 3 KOMPLETT
- [ ] Temple Endpoint funktioniert!

---

## 🚀 NÄCHSTER SCHRITT

**Weiter zu:** `PHASE_4.md` (Frontend Integration)

**Was kommt:** React Frontend verbindet sich mit Backend!
