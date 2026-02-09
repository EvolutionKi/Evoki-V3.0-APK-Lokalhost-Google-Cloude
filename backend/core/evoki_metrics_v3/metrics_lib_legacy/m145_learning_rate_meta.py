"""
Evoki Metrics Library - m145_learning_rate_meta

Meta-cognition metric: Meta-learning rate (performance delta).
"""

def compute_m145_learning_rate_meta(performance_delta: float) -> float:
    """
    m145_learning_rate_meta: Meta-Learning Rate
    
    SPEC: clamp(performance_delta, -0.1, 0.1)
    
    Bounded learning rate change (-0.1 to +0.1).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(-0.1, min(0.1, performance_delta)), 4)
