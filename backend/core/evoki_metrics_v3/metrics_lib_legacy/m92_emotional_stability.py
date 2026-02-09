"""
Evoki Metrics Library - m92_emotional_stability

Complex emotion metric: Emotional stability.
"""

def compute_m92_emotional_stability(valence: float, arousal: float) -> float:
    """
    m92_emotional_stability: Complex Emotion - Emotional Stability
    
    SPEC: Stability is low arousal with neutral valence (balanced state).
    
    Formula:(1 - arousal) × (1 - |valence - 0.5| × 2)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round((1 - arousal) * (1 - abs(valence - 0.5) * 2), 4)
