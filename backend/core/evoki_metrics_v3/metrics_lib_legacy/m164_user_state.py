"""
m164: User-Zustand
"""

from typing import List, Dict, Optional, Any


def compute_m164_user_state(recent_affects: List[float]) -> float:
    """m164: User-Zustand"""
    if not recent_affects:
        return 0.5
    weights = [0.1, 0.15, 0.2, 0.25, 0.3]
    weights = weights[-len(recent_affects):]
    weighted_sum = sum(a * w for a, w in zip(recent_affects, weights))
    return round(weighted_sum / sum(weights), 4)
