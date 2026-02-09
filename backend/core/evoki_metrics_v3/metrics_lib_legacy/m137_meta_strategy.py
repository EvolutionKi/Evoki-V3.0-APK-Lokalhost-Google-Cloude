"""
Evoki Metrics Library - m137_meta_strategy

Meta-cognition metric: Strategy switching rate.
"""

def compute_m137_meta_strategy(strategy_switches: int, turns: int) -> float:
    """
    m137_meta_strategy: Strategy Switching
    
    SPEC: strategy_switches / turns
    
    Measures strategic adaptability.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(strategy_switches / max(1, turns), 4)
