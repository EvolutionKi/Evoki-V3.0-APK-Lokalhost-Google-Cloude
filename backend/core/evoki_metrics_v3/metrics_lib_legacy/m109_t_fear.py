"""m109_t_fear: Fear Score ⚠️ TRAUMA METRIC
Simple word-count based fear detection from marker words."""
from ._helpers import clamp
def compute_m109_t_fear(text: str) -> float:
    fear_words = ["angst", "furcht", "befürchte", "sorge", "panik"]
    text_lower = text.lower()
    hits = sum(1 for w in fear_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)
__all__ = ['compute_m109_t_fear']
