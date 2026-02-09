"""
m168: Kumulativer Stress
"""

from typing import List, Dict, Optional, Any


def compute_m168_cum_stress(z_prox_history: List[float]) -> float:
    """m168: Kumulativer Stress"""
    if not z_prox_history:
        return 0.0
    recent = z_prox_history[-10:]
    return round(sum(recent) / len(recent), 4)
