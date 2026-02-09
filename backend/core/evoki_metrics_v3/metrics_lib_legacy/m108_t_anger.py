"""m108_t_anger: Anger Score ⚠️ TRAUMA METRIC
Simple word-count based anger detection from marker words."""
from ._helpers import clamp
def compute_m108_t_anger(text: str) -> float:
    anger_words = ["wut", "wütend", "ärger", "hass", "sauer"]
    text_lower = text.lower()
    hits = sum(1 for w in anger_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)
__all__ = ['compute_m108_t_anger']
