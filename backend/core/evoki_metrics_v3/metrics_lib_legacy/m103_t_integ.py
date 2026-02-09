"""
m103_t_integ: Integration Vector ✅ POSITIVE TRAUMA COUNTER

Positive counterforce to trauma - measures integration/grounding.
Uses integration lexicon to detect recovery indicators.

Formula:
    t_integ = clip(Σ(integ_lex_hit × weight) / (text_len + 1) × 8.0)

Higher t_integ = better integration, recovery, grounding.
"""

from ._helpers import clamp
from ._lexika import INTEG_LEXIKON


def compute_m103_t_integ(text: str) -> float:
    """
    Calculate m103_t_integ (Integration/Grounding)
    
    Args:
        text: Input text
    
    Returns:
        Integration score [0, 1] - Higher = better integration
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in INTEG_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return round(clamp(raw_score), 4)


__all__ = ['compute_m103_t_integ']
