"""
Evoki Metrics Library - m136_meta_evaluation

Meta-cognition metric: Task evaluation/success.
"""

def compute_m136_meta_evaluation(task_success: float) -> float:
    """
    m136_meta_evaluation: Task Evaluation
    
    SPEC: clamp(task_success)
    
    Normalized task success rating.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, task_success)), 4)
