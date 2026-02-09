"""
Evoki Metrics Library - m160_uptime

System metric: System uptime (availability).
"""

def compute_m160_uptime(uptime_seconds: float, total_seconds: float) -> float:
    """
    m160_uptime: System Uptime
    
    SPEC: uptime_seconds / total_seconds
    
    Measures system availability ratio.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(uptime_seconds / max(1.0, total_seconds), 4)
