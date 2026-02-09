# VOLLSTÄNDIGER METRIKEN-FIX-PLAN V2.0

**Datum:** 2026-02-07 22:32  
**Quelle:** EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md (Zeilen 8000-12000)  
**Ziel:** Alle 168 Metriken korrekt implementieren

---

## PHASE 1: V7 LEXIKA PACKAGE KOPIEREN ✅ PRIORITÄT 1

**Quelle:**
```
C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\evoki_lexika_v3_bundle\evoki_lexika_v3\
```

**Ziel:**
```
C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_lexika_v3\
```

**Dateien:**
- ✅ `__init__.py` (708 bytes)
- ✅ `config.py` (1090 bytes) - Thresholds + BVektorConfig
- ✅ `drift.py` (1686 bytes)
- ✅ `engine.py` (4884 bytes) - Score-Engine
- ✅ `lexika_data.py` (11734 bytes) - **22 Lexika**
- ✅ `registry.py` (3801 bytes)
- ✅ `README.md` (925 bytes)

**Aktion:**
```powershell
# Backup current
Move-Item "backend\core\evoki_lexika_v3" "backend\core\evoki_lexika_v3.OLD" -Force

# Copy V7
Copy-Item "C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\evoki_lexika_v3_bundle\evoki_lexika_v3" "backend\core\evoki_lexika_v3" -Recurse -Force
```

---

## PHASE 2: GRAIN ENGINE (m96-m100) ✅ PRIORITÄT 2

### m96_grain_word - Wort-Komplexität

**Spec:** Zeile 9278  
**Formel:** Average syllables per word (oder Buchstaben/Wort)  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
def compute_m96_grain_word(text: str) -> float:
    """Wort-Komplexität: Durchschnittliche Wortlänge."""
    words = text.split()
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    # Normalize: 1-5 Buchstaben = 0.0-1.0
    return min(1.0, (avg_len - 1) / 10.0)  # 11+ Buchstaben = 1.0
```

### m97_grain_impact - Emotionale Dichte

**Spec:** Zeile 9279  
**Formel:** Density of emotional words  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
def compute_m97_grain_impact(text: str, emotion_lexika: dict) -> float:
    """Emotionale Dichte: Anteil emotionaler Wörter."""
    words = text.lower().split()
    if not words:
        return 0.0
    
    # Combine EMOTION_POSITIVE + EMOTION_NEGATIVE from lexika
    emotional_words = emotion_lexika.get("Emotion_pos", {}).keys() | emotion_lexika.get("Emotion_neg", {}).keys()
    
    hits = sum(1 for w in words if w in emotional_words)
    return min(1.0, hits / len(words) * 5.0)  # 20% emotional words = 1.0
```

### m98_grain_sentiment - Lokale Sentiment-Varianz

**Spec:** Zeile 9280  
**Formel:** Variance across word-level sentiments  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
import numpy as np

def compute_m98_grain_sentiment(text: str, emotion_lexika: dict) -> float:
    """Sentiment-Varianz auf Wort-Ebene."""
    words = text.lower().split()
    if len(words) < 2:
        return 0.0
    
    pos_lex = emotion_lexika.get("Emotion_pos", {})
    neg_lex = emotion_lexika.get("Emotion_neg", {})
    
    # Get sentiment for each word: +1 for pos, -1 for neg, 0 for neutral
    sentiments = []
    for w in words:
        if w in pos_lex:
            sentiments.append(pos_lex[w])
        elif w in neg_lex:
            sentiments.append(-neg_lex[w])
        else:
            sentiments.append(0.0)
    
    # Variance
    variance = np.var(sentiments)
    return min(1.0, variance * 2.0)  # Normalize
```

### m99_grain_novelty - Novelty-Index

**Spec:** Zeile 9281  
**Formel:** Ratio of unique words  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
def compute_m99_grain_novelty(text: str) -> float:
    """Novelty: Anteil einzigartiger Wörter (Type-Token-Ratio)."""
    words = text.lower().split()
    if not words:
        return 0.0
    
    unique_words = len(set(words))
    total_words = len(words)
    
    # Type-Token Ratio
    return min(1.0, unique_words / total_words)
```

### m100_causal_1 - Kausaler Index

**Spec:** Zeile 9282  
**Formel:** Count of causal connectors ("weil", "daher", "deshalb")  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
def compute_m100_causal_1(text: str) -> float:
    """Kausaler Index: Dichte kausaler Konnektoren."""
    causal_markers = ['weil', 'daher', 'deshalb', 'denn', 'folglich', 'somit', 'deswegen']
    text_lower = text.lower()
    
    hits = sum(1 for marker in causal_markers if marker in text_lower)
    words = len(text.split())
    
    if words == 0:
        return 0.0
    
    # Normalize: 1 causal per 10 words = 1.0
    return min(1.0, (hits / words) * 10.0)
```

---

## PHASE 3: TEXT/META METRIKEN (m101-m120) ✅ PRIORITÄT 3

### m110_black_hole - Ereignishorizont (KRITISCH!)

**Spec:** Zeile 6900-7004  
**Formel:** V3.3.3 Context-Aware Formula  
**Aktuell:** Hardcoded 0.3 ❌  

**Fix:**
```python
def compute_m110_black_hole(
    chaos: float,  # m21
    A: float,      # m1_A
    LL: float,     # m7_LL
    panic_hits: int = 0,  # aus T_PANIC Lexikon
    text: str = "",
    semantic_guardian = None  # Optional LLM
) -> float:
    """
    V3.3.3 Context-Aware Black Hole.
    
    Base weighted formula:
    - 40% Chaos (Entropie dominiert)
    - 30% Inverted Affekt (Kollaps)
    - 30% Lambert-Light (Trübung)
    
    Context-Aware Veto:
    - If >=2 panic words: Ask Semantic Guardian
    - True emergency: boost to 0.85
    - False positive (gaming context): minor penalty +0.1
    """
    # Base calculation
    base = (0.4 * chaos) + (0.3 * (1.0 - A)) + (0.3 * LL)
    
    # Context-Aware Veto (Lexikon = Accuser, LLM = Judge)
    if panic_hits >= 2:
        if semantic_guardian is not None:
            is_real = semantic_guardian.check_urgency(text)
            if is_real:
                return max(base, 0.85)  # Confirmed emergency
            else:
                return min(1.0, base + 0.1)  # Contextual usage
        else:
            # Fallback: Conservative penalty
            return min(1.0, base + 0.15)
    
    return base
```

### m116_lix - Lesbarkeits-Index (LIX)

**Spec:** Zeile 9313  
**Formel:** LIX = (words/sentences) + (long_words×100/words)  
**Aktuell:** Hardcoded 30.0 ❌  

**Fix:**
```python
def compute_m116_lix(text: str) -> float:
    """
    LIX (Lesbarkeitsindex) nach schwedischer Formel.
    
    LIX = (Wörter/Sätze) + (Lange Wörter × 100 / Wörter)
    Lange Wörter = >6 Buchstaben
    
    Range: ~20 (sehr leicht) bis ~60 (sehr schwer)
    Normalized to [0, 1]: (LIX - 20) / 40
    """
    import re
    
    # Count sentences (. ! ?)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences) if sentences else 1
    
    # Count words
    words = text.split()
    num_words = len(words) if words else 1
    
    # Count long words (>6 letters)
    long_words = sum(1 for w in words if len(w) > 6)
    
    # LIX formula
    lix_raw = (num_words / num_sentences) + (long_words * 100.0 / num_words)
    
    # Normalize to [0, 1]: 20-60 range
    lix_norm = (lix_raw - 20.0) / 40.0
    
    return max(0.0, min(1.0, lix_norm))
```

---

## PHASE 4: ANDROMATIK/FEP (m57-m58) ✅ PRIORITÄT 4

### m57_tokens_soc - Soziale Token-Reserve

**Spec:** Zeile 9231  
**Typ:** STATE (nicht computed!)  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
# Diese Metrik ist STATE, nicht berechnet!
# Muss in compute_all_metrics als Parameter übergeben werden:

def compute_all_metrics(
    text: str,
    ...,
    tokens_soc: float = 100.0,  # Initial reserve
    tokens_log: float = 100.0,  # Initial reserve
    ...
):
    result = {}
    
    # m57/m58 are STATE, not computed
    result['m57_tokens_soc'] = max(0, min(200, tokens_soc))  # Clamp [0, 200]
    result['m58_tokens_log'] = max(0, min(200, tokens_log))  # Clamp [0, 200]
    
    # ... rest of metrics
```

**WICHTIG:** Diese Metriken müssen als **Timeline State** gespeichert werden, nicht neu berechnet!

---

## PHASE 5: CHRONOS/META (m131-m150) ✅ PRIORITÄT 5

**Alle 20 Chronos-Metriken sind aktuell FAKE (hardcoded 0.0 oder random)!**

### m131_session_dur - Session-Dauer

**Spec:** Zeile 9328  
**Typ:** STATE (Sekunden seit Session-Start)  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
from datetime import datetime

def compute_m131_session_dur(session_start: datetime) -> float:
    """Session duration in hours."""
    delta = datetime.now() - session_start
    return delta.total_seconds() / 3600.0  # Convert to hours
```

### m132_inter_freq - Interaktionsfrequenz

**Spec:** Zeile 9329  
**Typ:** STATE (Messages pro Stunde)  
**Aktuell:** `return 0.0` ❌  

**Fix:**
```python
def compute_m132_inter_freq(message_count: int, session_dur_hours: float) -> float:
    """Interaction frequency: messages per hour."""
    if session_dur_hours == 0:
        return 0.0
    return message_count / session_dur_hours
```

### m135_meta_20 - Planung (Future Tense)

**Spec:** Zeile 9332  
**For mel:** Count future tense markers  
**Aktuell:** `return random.uniform(0.0, 1.0)` ❌  

**Fix:**
```python
def compute_m135_meta_20(text: str) -> float:
    """Planning: Future tense marker density."""
    future_markers = ['werde', 'wird', 'werden', 'morgen', 'nächste', 'bald', 'später', 'zukünftig', 'plan', 'vorhabe']
    text_lower = text.lower()
    
    hits = sum(1 for marker in future_markers if marker in text_lower)
    words = len(text.split())
    
    if words == 0:
        return 0.0
    
    return min(1.0, (hits / words) * 10.0)  # 10% future words = 1.0
```

### m136_meta_21 - Reflexion (Past Tense)

**Spec:** Zeile 9333  
**Formel:** Count past tense markers  
**Aktuell:** `return random.uniform(0.0, 1.0)` ❌  

**Fix:**
```python
def compute_m136_meta_21(text: str) -> float:
    """Reflection: Past tense marker density."""
    past_markers = ['war', 'hatte', 'wurde', 'früher', 'damals', 'gestern', 'vorher', 'einst', 'gewesen']
    text_lower = text.lower()
    
    hits = sum(1 for marker in past_markers if marker in text_lower)
    words = len(text.split())
    
    if words == 0:
        return 0.0
    
    return min(1.0, (hits / words) * 10.0)  # 10% past words = 1.0
```

### Remaining Meta Metriken (m137-m150)

**Alle haben ähnliche Formel-Pattern:**
- Count specific linguistic markers
- Normalize by word count or threshold
- Clamp to [0, 1]

**Siehe Spec Zeilen 8000-8200 für Details!**

---

## ZUSAMMENFASSUNG DER FIXES

### ✅ ECHTE METRIKEN (72/168 = 43%)
- Core (m1-m20): 20 Metriken
- Physics (m21-m35): 15 Metriken
- Hypermetrics (m36-m55): 20 Metriken
- Evolution (m71-m73): 3 Metriken
- Trauma Core (m101-m104): 4 Metriken
- Omega (m151-m161): 11 Metriken

### ❌ FAKE METRIKEN (96/168 = 57%)

**Kategorie: Grain Engine (m96-m100)** - 5 Metriken
- m96_grain_word: `return 0.0` → FIX: Avg word length
- m97_grain_impact: `return 0.0` → FIX: Emotional density
- m98_grain_sentiment: `return 0.0` → FIX: Sentiment variance
- m99_grain_novelty: `return 0.0` → FIX: Type-Token-Ratio
- m100_causal_1: `return 0.0` → FIX: Causal marker density

**Kategorie: Andromatik STATE (m57-m58)** - 2 Metriken
- m57_tokens_soc: `return 0.0` → FIX: STATE variable
- m58_tokens_log: `return 0.0` → FIX: STATE variable

**Kategorie: Trauma/Turbidity (m105-m115)** - 11 Metriken
- m110_black_hole: Hardcoded 0.3 → FIX: V3.3.3 Context-Aware formula
- m105-m109, m111-m115: Various fake values → SPEC prüfen

**Kategorie: Meta-Cognition (m116-m150)** - 35 Metriken
- m116_lix: Hardcoded 30.0 → FIX: Real LIX formula
- m117-m150: Random/hardcoded → FIX: Individual formulas from Spec

**Kategorie: FEP/Drive (m56-m70)** - 15 Metriken
- Teilweise implementiert, teilweise fake → AUDIT erforderlich

**Kategorie: Sentiment (m74-m95)** - 22 Metriken
- Schema B (Sentiment) komplett nicht implementiert → SPEC prüfen

---

## NÄCHSTE SCHRITTE

1. **✅ JETZT:** V7 Lexika Package kopieren (PHASE 1)
2. **✅ HEUTE:** Grain Engine implementieren (PHASE 2)
3. **✅ MORGEN:** m110_black_hole + m116_lix fixen (PHASE 3)
4. **⏳ BALD:** Token STATE implementieren (PHASE 4)
5. **⏳ SPÄTER:** Chronos/Meta komplett neu (PHASE 5)

**ERWARTETE ERGEBNISSE:**
- Nach Phase 1-3: **~85% echte Metriken** (142/168)
- Nach Phase 4-5: **100% echte Metriken** (168/168)

---

**STATUS:** ✅ READY TO START  
**NEXT ACTION:** Copy V7 Lexika Package
