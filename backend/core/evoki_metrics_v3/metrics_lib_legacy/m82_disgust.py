"""
Evoki Metrics Library - m82_disgust

Plutchik emotion metric: Disgust.
"""

def compute_m82_disgust(valence: float) -> float:
    """
    m82_disgust: Plutchik Disgust
    
    SPEC: Disgust emotion from Plutchik wheel.
    Inverse of valence (low valence = high disgust).
    
    Formula: (1 - valence) × 0.7
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round((1 - valence) * 0.7, 4)
