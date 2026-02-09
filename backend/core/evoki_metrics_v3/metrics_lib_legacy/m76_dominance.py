"""
Evoki Metrics Library - m76_dominance

VAD (Valence-Arousal-Dominance) metric: Control/dominance level.
"""

def compute_m76_dominance(text: str) -> float:
    """
    m76_dominance: VAD Dominance
    
    SPEC: Dominance/control dimension in the VAD model.
    Measures sense of control vs helplessness.
    
    Formula: base(0.5) + (high_count - low_count) × 0.05, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    high_words = ["kann", "werde", "bestimme", "kontrolliere", "stark", "sicher"]
    low_words = ["hilflos", "ohnmächtig", "schwach", "verloren", "überfordert"]
    
    text_lower = text.lower()
    high = sum(1 for w in high_words if w in text_lower)
    low = sum(1 for w in low_words if w in text_lower)
    
    val = 0.5 + (high - low) * 0.05
    return round(max(0.0, min(1.0, val)), 4)
