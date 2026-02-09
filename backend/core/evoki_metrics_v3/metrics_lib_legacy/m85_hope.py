"""
Evoki Metrics Library - m85_hope

Complex emotion metric: Hope.
"""

def compute_m85_hope(valence: float, anticipation: float) -> float:
    """
    m85_hope: Complex Emotion - Hope
    
    SPEC: Hope combines positive valence with anticipation.
    
    Formula: (valence + anticipation) / 2
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round((valence + anticipation) / 2, 4)
