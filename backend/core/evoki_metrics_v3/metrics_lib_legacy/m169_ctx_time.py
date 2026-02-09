"""
Evoki Metrics Library - m162_ctx_time

Context metric: Temporal context embedding (normalized session time).
"""

def compute_m162_ctx_time(session_start_minutes: float, current_minutes: float) -> float:
    """
    m162_ctx_time: Temporal Context Embedding
    
    SPEC: Normalized session duration (0-60 min → 0-1)
    
    Formula: min(1.0, (current - start) / 60.0)
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    duration = current_minutes - session_start_minutes
    return round(min(1.0, duration / 60.0), 4)
