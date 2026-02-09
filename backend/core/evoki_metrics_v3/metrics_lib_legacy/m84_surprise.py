"""
Evoki Metrics Library - m84_surprise

Plutchik emotion metric: Surprise.
"""

def compute_m84_surprise(valence: float, arousal: float) -> float:
    """
    m84_surprise: Plutchik Surprise
    
    SPEC: Surprise emotion from Plutchik wheel.
    High arousal with neutral valence = surprise.
    
    Formula: arousal × (1 - |valence - 0.5| × 2)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(arousal * (1 - abs(valence - 0.5) * 2), 4)
