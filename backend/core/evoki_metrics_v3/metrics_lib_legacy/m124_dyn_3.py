"""
Evoki Metrics Library - m124_dyn_3

Cognitive metric: Flow momentum.
"""

def compute_m124_dyn_3(flow: float, flow_prev: float) -> float:
    """
    m124_dyn_3: Flow Momentum
    
    SPEC: flow - flow_prev
    
    Change in flow state.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(flow - flow_prev, 4)
