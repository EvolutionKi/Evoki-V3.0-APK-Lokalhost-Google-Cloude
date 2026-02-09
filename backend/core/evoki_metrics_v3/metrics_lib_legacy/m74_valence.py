"""
Evoki Metrics Library - m74_valence

VAD (Valence-Arousal-Dominance) metric: Emotional valence.
"""

def compute_m74_valence(text: str) -> float:
    """
    m74_valence: VAD Valence
    
    SPEC: Emotional valence (positive/negative tone) in the VAD model.
    
    Formula: base(0.5) + (pos_count - neg_count) × 0.05, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    pos_words = ["gut", "toll", "super", "freude", "glücklich", "liebe", "schön", "wunderbar", "fantastisch"]
    neg_words = ["schlecht", "schrecklich", "traurig", "hasse", "elend", "furchtbar", "mies", "übel"]
    
    text_lower = text.lower()
    pos = sum(1 for w in pos_words if w in text_lower)
    neg = sum(1 for w in neg_words if w in text_lower)
    
    val = 0.5 + (pos - neg) * 0.05
    return round(max(0.0, min(1.0, val)), 4)
