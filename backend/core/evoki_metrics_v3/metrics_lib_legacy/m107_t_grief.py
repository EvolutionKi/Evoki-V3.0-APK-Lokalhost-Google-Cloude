"""m107_t_grief: Grief Score ⚠️ TRAUMA METRIC
Simple word-count based grief detection from marker words."""
from ._helpers import clamp
def compute_m107_t_grief(text: str) -> float:
    grief_words = ["trauer", "verlust", "vermisse", "tot", "gestorben"]
    text_lower = text.lower()
    hits = sum(1 for w in grief_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)
__all__ = ['compute_m107_t_grief']
