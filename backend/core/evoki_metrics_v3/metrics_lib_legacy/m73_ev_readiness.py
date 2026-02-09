"""
Evoki Metrics Library - m73_ev_readiness

Evolution metric: Readiness for action/change.
"""

def compute_m73_ev_readiness(t_integ: float, A: float) -> float:
    """
    m73_ev_readiness: Evolutionary Readiness
    
    SPEC: Measures readiness for action based on trauma integration and affect.
    
    Formula: T_integ × A
    
    Args:
        t_integ: Trauma integration score [0, 1]
        A: Affect value (normalized)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(t_integ * A, 4)
