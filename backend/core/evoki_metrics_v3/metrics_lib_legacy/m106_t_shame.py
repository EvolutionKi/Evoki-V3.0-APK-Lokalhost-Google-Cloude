"""m106_t_shame: Shame Score ⚠️ TRAUMA METRIC
Simple word-count based shame detection from marker words."""
from ._helpers import clamp
def compute_m106_t_shame(text: str) -> float:
    shame_words = ["peinlich", "schäme", "blamiert", "dumm"]
    text_lower = text.lower()
    hits = sum(1 for w in shame_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)
__all__ = ['compute_m106_t_shame']
