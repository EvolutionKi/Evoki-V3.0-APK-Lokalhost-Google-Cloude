"""
Evoki Metrics Library - m144_sys_stability

System metric: System stability from error rate and latency.
"""

def compute_m144_sys_stability(error_rate: float, latency_norm: float) -> float:
    """
    m144_sys_stability: System Stability
    
    SPEC: 1.0 - (0.5 × error_rate + 0.5 × latency_norm), clamped
    
    Combined measure of system reliability.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    stability = 1.0 - (0.5 * error_rate + 0.5 * latency_norm)
    return round(max(0.0, min(1.0, stability)), 4)
