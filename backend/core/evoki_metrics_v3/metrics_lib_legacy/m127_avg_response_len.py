"""
Evoki Metrics Library - m127_avg_response_len

Cognitive metric: Average response length.
"""
from typing import List

def compute_m127_avg_response_len(lengths: List[int]) -> float:
    """
    m127_avg_response_len: Average Response Length
    
    SPEC: mean(lengths)
    
    Average length of responses in current session.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    if not lengths:
        return 0.0
    
    return round(sum(lengths) / len(lengths), 2)
