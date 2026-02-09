"""
m104_t_shock: Shock Score ⚠️ TRAUMA METRIC

Detects shock-state indicators from specific markers.
Simple word count of shock-related terms.

Formula:
    t_shock = clip((shock_hits / word_count) × 5.0)

Shock words: "plötzlich", "überraschend", "schock", "unerwartet", "boom"
"""

from ._helpers import clamp


def compute_m104_t_shock(text: str) -> float:
    """
    Calculate m104_t_shock (Shock Score)
    
    Args:
        text: Input text
    
    Returns:
        Shock score [0, 1] - Sudden/unexpected event indicators
    """
    shock_words = ["plötzlich", "überraschend", "schock", "unerwartet", "boom"]
    text_lower = text.lower()
    hits = sum(1 for w in shock_words if w in text_lower)
    words = len(text.split())
    return round(clamp(hits / max(1, words) * 5.0), 4)


__all__ = ['compute_m104_t_shock']
