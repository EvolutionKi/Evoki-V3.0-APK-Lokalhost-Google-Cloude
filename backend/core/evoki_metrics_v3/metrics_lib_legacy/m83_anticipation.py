"""
Evoki Metrics Library - m83_anticipation

Plutchik emotion metric: Anticipation.
"""

def compute_m83_anticipation(arousal: float) -> float:
    """
    m83_anticipation: Plutchik Anticipation
    
    SPEC: Anticipation/expectation emotion from Plutchik wheel.
    Directly proportional to arousal (high arousal = high anticipation).
    
    Formula: arousal × 0.8
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(arousal * 0.8, 4)
