"""
Evoki Metrics Library - m71_ev_arousal

Evolution metric: Emotional arousal level (evolutionary perspective).
"""

def compute_m71_ev_arousal(text: str) -> float:
    """
    m71_ev_arousal: Evolutionary Arousal
    
    SPEC: Measures activation/energy level from evolutionary psychology perspective.
    Detects high-energy words (excitement, enthusiasm) vs low-energy words (tired, bored).
    
    Formula: base(0.5) + 0.2 * pos_count - 0.2 * neg_count, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    arousal_pos = ["aufgeregt", "begeistert", "energisch", "enthusiastisch"]
    arousal_neg = ["müde", "erschöpft", "gelangweilt", "lethargisch"]
    
    text_lower = text.lower()
    pos = sum(1 for w in arousal_pos if w in text_lower)
    neg = sum(1 for w in arousal_neg if w in text_lower)
    
    val = 0.5 + 0.2 * pos - 0.2 * neg
    return round(max(0.0, min(1.0, val)), 4)
