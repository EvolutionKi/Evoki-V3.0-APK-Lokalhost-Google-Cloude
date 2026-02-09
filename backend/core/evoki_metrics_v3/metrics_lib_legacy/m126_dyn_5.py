"""
Evoki Metrics Library - m126_dyn_5

Cognitive metric: Panic momentum.
"""

def compute_m126_dyn_5(t_panic: float, t_panic_prev: float) -> float:
    """
    m126_dyn_5: Panic Momentum
    
    SPEC: t_panic - t_panic_prev
    
    Change in panic level (trauma dynamics).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(t_panic - t_panic_prev, 4)
