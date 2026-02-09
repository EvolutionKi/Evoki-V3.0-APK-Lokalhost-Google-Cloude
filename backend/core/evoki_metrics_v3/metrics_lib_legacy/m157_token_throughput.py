"""
Evoki Metrics Library - m157_token_throughput

System metric: Token throughput (tokens per second).
"""

def compute_m157_token_throughput(tokens: int, seconds: float) -> float:
    """
    m157_token_throughput: Token Throughput
    
    SPEC: tokens / seconds
    
    Processing speed in tokens per second.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(tokens / max(0.01, seconds), 2)
