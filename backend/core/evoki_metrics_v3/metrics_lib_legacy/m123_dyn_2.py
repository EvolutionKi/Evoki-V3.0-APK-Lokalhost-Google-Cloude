"""
Evoki Metrics Library - m123_dyn_2

Cognitive metric: Affect momentum.
"""

def compute_m123_dyn_2(A: float, A_prev: float) -> float:
    """
    m123_dyn_2: Affect Momentum
    
    SPEC: A - A_prev
    
    Change in affect value (emotional momentum).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(A - A_prev, 4)
