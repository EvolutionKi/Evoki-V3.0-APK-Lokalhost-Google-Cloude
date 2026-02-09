"""
Evoki Metrics Library - m125_dyn_4

Cognitive metric: Coherence momentum.
"""

def compute_m125_dyn_4(coh: float, coh_prev: float) -> float:
    """
    m125_dyn_4: Coherence Momentum
    
    SPEC: coh - coh_prev
    
    Change in coherence value.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(coh - coh_prev, 4)
