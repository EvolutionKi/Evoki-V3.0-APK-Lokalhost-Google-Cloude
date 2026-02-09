"""
Evoki Metrics Library - m154_sys_latency

System metric: Normalized system latency.
"""

def compute_m154_sys_latency(response_time_ms: float, target_ms: float = 500.0) -> float:
    """
    m154_sys_latency: System Latency (Normalized)
    
    SPEC: min(1.0, response_time_ms / target_ms)
    
    Normalized latency (1.0 = at target, >1.0 = slower than target).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(min(1.0, response_time_ms / target_ms), 4)
