"""
m70_active_inf: Active Inference
"""




def compute_m70_active_inf(action_space: int, precision: float) -> float:
    """m70_active_inf: Active Inference"""
    return round(1.0 / (1.0 + action_space / max(0.01, precision)), 4)
