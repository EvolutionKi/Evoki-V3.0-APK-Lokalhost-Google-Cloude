"""m105_t_guilt: Guilt Score ⚠️ TRAUMA METRIC
Simple word-count based guilt detection from marker words."""
from ._helpers import clamp
def compute_m105_t_guilt(text: str) -> float:
    guilt_words = ["schuld", "fehler", "hätte", "bereue", "sorry"]
    text_lower = text.lower()
    hits = sum(1 for w in guilt_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)
__all__ = ['compute_m105_t_guilt']
