"""
Evoki Metrics Library - m90_resistance

Complex emotion metric: Resistance/opposition.
"""

def compute_m90_resistance(arousal: float, acceptance: float) -> float:
    """
    m90_resistance: Complex Emotion - Resistance
    
    SPEC: Resistance is high arousal with low acceptance.
    
    Formula: arousal × (1 - acceptance)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(arousal * (1 - acceptance), 4)
