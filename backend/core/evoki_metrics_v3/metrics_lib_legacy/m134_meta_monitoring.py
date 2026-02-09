"""
Evoki Metrics Library - m134_meta_monitoring

Meta-cognition metric: Self-monitoring (error detection).
"""

def compute_m134_meta_monitoring(error_count: int, checks: int) -> float:
    """
    m134_meta_monitoring: Self-Monitoring
    
    SPEC: 1 - errors/checks
    
    Measures self-monitoring effectiveness.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(1.0 - error_count / max(1, checks), 4)
