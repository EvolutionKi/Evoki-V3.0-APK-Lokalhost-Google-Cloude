"""
Evoki Metrics Library - m94_comfort

Complex emotion metric: Comfort.
"""

def compute_m94_comfort(valence: float, arousal: float) -> float:
    """
    m94_comfort: Complex Emotion - Comfort
    
    SPEC: Comfort is low arousal with slightly positive valence.
    
    Formula: (1 - arousal) × (1 - |valence - 0.6|)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round((1 - arousal) * (1 - abs(valence - 0.6)), 4)
