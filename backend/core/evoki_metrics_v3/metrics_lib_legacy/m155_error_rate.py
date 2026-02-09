"""
Evoki Metrics Library - m155_error_rate

System metric: Error rate.
"""

def compute_m155_error_rate(errors: int, total_requests: int) -> float:
    """
    m155_error_rate: Error Rate
    
    SPEC: errors / total_requests
    
    Proportion of requests that resulted in errors.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(errors / max(1, total_requests), 4)
