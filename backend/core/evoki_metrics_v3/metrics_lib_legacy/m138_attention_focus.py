"""
Evoki Metrics Library - m138_attention_focus

Meta-cognition metric: Attention focus on main topic.
"""

def compute_m138_attention_focus(main_topic_coverage: float) -> float:
    """
    m138_attention_focus: Attention Focus
    
    SPEC: clamp(main_topic_coverage)
    
    Measures focus on primary topic.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, main_topic_coverage)), 4)
