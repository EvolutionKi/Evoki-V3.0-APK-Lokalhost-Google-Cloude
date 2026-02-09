"""
m5_coh: Coherence (Kohärenz)

SPEC: Jaccard similarity between consecutive sentences
Measures semantic continuity across sentence boundaries.

coh = avg(Jaccard(sent_i, sent_i+1)) for all consecutive pairs
"""

from ._helpers import clamp


def compute_m5_coh(text: str) -> float:
    """
    Calculate m5_coh (Text Coherence)
    
    Args:
        text: Input text
    
    Returns:
        Coherence score [0, 1] - Higher = more coherent
    """
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 1.0  # Single sentence = perfect coherence
    
    coherences = []
    for i in range(len(sentences) - 1):
        words_a = set(sentences[i].lower().split())
        words_b = set(sentences[i+1].lower().split())
        
        if len(words_a) == 0 or len(words_b) == 0:
            continue
        
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        if union > 0:
            coherences.append(intersection / union)
    
    if len(coherences) == 0:
        return 0.5
    
    return round(sum(coherences) / len(coherences), 4)


__all__ = ['compute_m5_coh']
