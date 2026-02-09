"""
Evoki Metrics Library - m72_ev_valence

Evolution metric: Emotional valence (positive/negative) from evolutionary perspective.
"""

def compute_m72_ev_valence(text: str) -> float:
    """
    m72_ev_valence: Evolutionary Valence
    
    SPEC: Measures positive vs negative emotional tone from evolutionary psychology.
    
    Formula: base(0.5) + 0.15 * pos_count - 0.15 * neg_count, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    valence_pos = ["gut", "toll", "super", "freude", "glücklich", "liebe"]
    valence_neg = ["schlecht", "schrecklich", "traurig", "hasse", "elend"]
    
    text_lower = text.lower()
    pos = sum(1 for w in valence_pos if w in text_lower)
    neg = sum(1 for w in valence_neg if w in text_lower)
    
    val = 0.5 + 0.15 * pos - 0.15 * neg
    return round(max(0.0, min(1.0, val)), 4)
