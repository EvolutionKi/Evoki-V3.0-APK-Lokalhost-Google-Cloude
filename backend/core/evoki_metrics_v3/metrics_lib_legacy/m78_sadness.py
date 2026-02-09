"""
Evoki Metrics Library - m78_sadness

Plutchik emotion metric: Sadness derived from VAD dimensions.
"""

def compute_m78_sadness(valence: float, arousal: float) -> float:
    """
    m78_sadness: Plutchik Sadness
    
    SPEC: Sadness emotion from Plutchik wheel.
    Low valence + low arousal = sadness.
    
    Formula: (2 - valence - arousal) / 2, clamped to [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    val = (2 - valence - arousal) / 2
    return round(max(0.0, min(1.0, val)), 4)
