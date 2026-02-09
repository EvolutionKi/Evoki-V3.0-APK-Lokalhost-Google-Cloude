"""
m9_b_past: Vergangenheits-Bezug (Past Reference)

SPEC (FINAL7 Line 2667):
    b_past = max(weight_i) for all matching terms in lexicon

Measures temporal orientation toward the past.
Uses MAX weight (not count) from lexicon matches.

Reference: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md:2638-2724

Example lexicon:
    {"erinnere": 0.9, "damals": 0.8, "früher": 0.7, "gewesen": 0.6}
"""

from typing import Dict
from ._helpers import clamp


def compute_m9_b_past(text: str, b_past_lexikon: Dict[str, float]) -> float:
    """
    Calculate m9_b_past (Past Reference)
    
    Args:
        text: Input text
        b_past_lexikon: Dict of past-indicators {"term": weight}
                       REQUIRED - no hardcoded defaults!
                       Should be loaded from external lexikon files
    
    Returns:
        b_past score [0, 1] - MAX weight of all found terms
    """
    b_past = 0.0
    text_lower = text.lower()
    
    for term, weight in b_past_lexikon.items():
        if term in text_lower:
            b_past = max(b_past, weight)  # FINAL7: MAX, not COUNT!
    
    return round(clamp(b_past), 4)


__all__ = ['compute_m9_b_past']
