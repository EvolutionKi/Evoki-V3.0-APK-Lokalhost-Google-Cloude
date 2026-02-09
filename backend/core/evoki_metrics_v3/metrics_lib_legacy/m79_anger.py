"""
Evoki Metrics Library - m79_anger

Plutchik emotion metric: Anger derived from VAD dimensions.
"""

def compute_m79_anger(valence: float, arousal: float) -> float:
    """
    m79_anger: Plutchik Anger
    
    SPEC: Anger emotion from Plutchik wheel.
    Low valence + high arousal = anger.
    
    Formula: (1 - valence + arousal) / 2, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    val = (1 - valence + arousal) / 2
    return round(max(0.0, min(1.0, val)), 4)
