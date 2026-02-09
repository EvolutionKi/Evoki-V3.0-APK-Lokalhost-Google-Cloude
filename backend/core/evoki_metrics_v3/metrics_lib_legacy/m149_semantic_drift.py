"""
m149: Semantic Drift
"""

import math


def compute_m149_semantic_drift(current_vec: list, initial_vec: list) -> float:
    """m149: Semantic Drift"""
    if not current_vec or not initial_vec:
        return 0.0
    dist = math.sqrt(sum((a - b)**2 for a, b in zip(current_vec[:10], initial_vec[:10])))
    return round(min(1.0, dist / 10.0), 4)
