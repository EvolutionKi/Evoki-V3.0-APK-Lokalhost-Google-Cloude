"""
m46_rapport: Beziehungs-Rapport
"""

from typing import List, Dict, Optional, Any


def compute_m46_rapport(trust_history: List[float] = None) -> float:
    """m46_rapport: Beziehungs-Rapport"""
    if not trust_history:
        return 0.5
    recent = trust_history[-5:]
    return round(sum(recent) / len(recent), 4)
