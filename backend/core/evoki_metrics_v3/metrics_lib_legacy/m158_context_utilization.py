"""
Evoki Metrics Library - m158_context_utilization

System metric: Context window utilization.
"""

def compute_m158_context_utilization(used_tokens: int, max_tokens: int) -> float:
    """
    m158_context_utilization: Context Utilization
    
    SPEC: used_tokens / max_tokens
    
    Measures how much of available context window is used.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(used_tokens / max(1, max_tokens), 4)
