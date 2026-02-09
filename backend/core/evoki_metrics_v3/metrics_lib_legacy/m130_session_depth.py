"""
Evoki Metrics Library - m130_session_depth

Cognitive metric: Session depth (normalized turn count).
"""

def compute_m130_session_depth(turn_count: int) -> float:
    """
    m130_session_depth: Session Depth
    
    SPEC: min(1.0, turn_count / 50)
    
    Normalized session depth (capped at 50 turns = 1.0).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(min(1.0, turn_count / 50.0), 4)
