"""
Evoki Metrics Library - m77_joy

Plutchik emotion metric: Joy derived from VAD dimensions.
"""

def compute_m77_joy(valence: float, arousal: float) -> float:
    """
    m77_joy: Plutchik Joy
    
    SPEC: Joy emotion from Plutchik wheel, derived from VAD.
    High valence + high arousal = joy.
    
    Formula: valence + arousal - 1, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    val = valence + arousal - 1.0
    return round(max(0.0, min(1.0, val)), 4)
