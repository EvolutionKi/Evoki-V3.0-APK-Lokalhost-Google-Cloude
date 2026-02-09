"""
m118: Lokale Kohärenz
"""

from typing import List, Dict, Optional, Any


def compute_m118_coherence_local(sentences: List[str]) -> float:
    """m118: Lokale Kohärenz"""
    if len(sentences) < 2:
        return 1.0
    overlaps = []
    for i in range(len(sentences) - 1):
        words1 = set(sentences[i].lower().split())
        words2 = set(sentences[i+1].lower().split())
        if not words1 or not words2:
            continue
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        if union > 0:
            overlaps.append(intersection / union)
    return round(sum(overlaps) / len(overlaps), 4) if overlaps else 0.0
