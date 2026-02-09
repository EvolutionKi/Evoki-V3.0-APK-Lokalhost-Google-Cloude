"""
m47_focus_stability: Fokus-Stabilität
"""




def compute_m47_focus_stability(topic_variance: float = 0.5) -> float:
    """m47_focus_stability: Fokus-Stabilität"""
    return round(1.0 - topic_variance, 4)
