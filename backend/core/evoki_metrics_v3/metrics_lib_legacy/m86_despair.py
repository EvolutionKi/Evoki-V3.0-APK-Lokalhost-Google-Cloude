"""
Evoki Metrics Library - m86_despair

Complex emotion metric: Despair.
"""

def compute_m86_despair(valence: float, sadness: float) -> float:
    """
    m86_despair: Complex Emotion - Despair
    
    SPEC: Despair combines low valence with sadness.
    
    Formula: ((1 - valence) + sadness) / 2
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(((1 - valence) + sadness) / 2, 4)
