"""
m117: Type-Token-Ratio
"""

from typing import List, Dict, Optional, Any


def compute_m117_vocabulary_richness(tokens: List[str]) -> float:
    """m117: Type-Token-Ratio"""
    if not tokens:
        return 0.0
    unique = len(set(tokens))
    total = len(tokens)
    return round(unique / total, 4)
