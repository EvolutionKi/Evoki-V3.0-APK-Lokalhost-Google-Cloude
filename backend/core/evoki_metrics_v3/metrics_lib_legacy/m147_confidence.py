"""
Evoki Metrics Library - m147_confidence

Meta-cognition metric: Confidence (1 - variance).
"""

def compute_m147_confidence(variance: float) -> float:
    """
    m147_confidence: Confidence
    
    SPEC: 1 - clamp(variance)
    
    High variance = low confidence.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    clamped_var = max(0.0, min(1.0, variance))
    return round(1.0 - clamped_var, 4)
