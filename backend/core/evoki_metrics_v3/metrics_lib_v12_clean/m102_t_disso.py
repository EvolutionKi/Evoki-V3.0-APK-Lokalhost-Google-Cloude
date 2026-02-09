"""
m102_t_disso: Dissociation Vector ⚠️ TRAUMA METRIC

SPEC Formula:
    t_disso = clip(Σ(disso_lex_hit × weight) / (text_len + 1) × 8.0)

Detects dissociative state indicators from lexicon.
Normalized by text length, scaled to [0, 1].

Reference: EVOKI_V3_METRICS_SPECIFICATION.md:6435-6473
"""

from ._helpers import clamp
from ._lexika import DISSO_LEXIKON


def compute_m102_t_disso(text: str) -> float:
    """
    Calculate m102_t_disso (Dissociation Vector)
    
    Args:
        text: Input text
    
    Returns:
        Dissociation score [0, 1] - Higher = more dissociative
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in DISSO_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return round(clamp(raw_score), 4)


__all__ = ['compute_m102_t_disso']
