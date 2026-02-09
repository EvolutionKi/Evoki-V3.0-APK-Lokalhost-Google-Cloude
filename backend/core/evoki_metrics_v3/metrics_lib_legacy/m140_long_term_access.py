"""
Evoki Metrics Library - m140_long_term_access

Meta-cognition metric: Long-term memory retrieval success.
"""

def compute_m140_long_term_access(retrieval_success: float) -> float:
    """
    m140_long_term_access: Long-Term Memory Access
    
    SPEC: clamp(retrieval_success)
    
    Measures RAG/long-term memory retrieval effectiveness.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, retrieval_success)), 4)
