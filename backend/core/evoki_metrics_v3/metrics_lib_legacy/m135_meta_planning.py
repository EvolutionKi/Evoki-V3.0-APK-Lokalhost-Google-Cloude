"""
Evoki Metrics Library - m135_meta_planning

Meta-cognition metric: Planning progress.
"""

def compute_m135_meta_planning(goal_progress: float) -> float:
    """
    m135_meta_planning: Planning Progress
    
    SPEC: clamp(goal_progress)
    
    Normalized goal progress indicator.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, goal_progress)), 4)
