"""
m101_t_panic: Panic Vector ⚠️ TRAUMA METRIC

SPEC Formula:
    t_panic = clip(Σ(panic_lex_hit × weight) / (text_len + 1) × 10.0)

Detects panic-state indicators from lexicon matches.
Normalized by text length and scaled to [0, 1].

Reference: EVOKI_V3_METRICS_SPECIFICATION.md:6347-6389
"""

from ._helpers import clamp
from ._lexika import PANIC_LEXIKON


def compute_m101_t_panic(text: str) -> float:
    """
    Calculate m101_t_panic (Panic Vector)
    
    Args:
        text: Input text
    
    Returns:
        Panic score [0, 1] - Higher = more panic indicators
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in PANIC_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 10.0
    return round(clamp(raw_score), 4)


__all__ = ['compute_m101_t_panic']
