"""
Evoki Metrics Library - m75_arousal

VAD (Valence-Arousal-Dominance) metric: Arousal/activation level.
"""

def compute_m75_arousal(text: str) -> float:
    """
    m75_arousal: VAD Arousal
    
    SPEC: Arousal/activation level in the VAD model.
    Measures intensity of emotional state (high energy vs low energy).
    
    Formula: base(0.5) + (high_count - low_count) × 0.05, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    high_words = ["aufgeregt", "begeistert", "wütend", "ängstlich", "energisch", "intensiv"]
    low_words = ["ruhig", "entspannt", "müde", "gelassen", "friedlich", "langsam"]
    
    text_lower = text.lower()
    high = sum(1 for w in high_words if w in text_lower)
    low = sum(1 for w in low_words if w in text_lower)
    
    val = 0.5 + (high - low) * 0.05
    return round(max(0.0, min(1.0, val)), 4)
