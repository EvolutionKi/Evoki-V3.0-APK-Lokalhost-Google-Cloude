"""
Evoki Metrics Library - m116_lix

Cognitive metric: LIX readability index.
"""

def compute_m116_lix(text: str) -> float:
    """
    m116_lix: LIX Readability Index
    
    SPEC: LIX = (Wörter/Sätze) + (LangeWörter×100/Wörter)
    
    LIX is a Swedish readability metric.
    Long words = words with more than 6 characters.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    if not words or sentences == 0:
        return 50.0  # Default medium complexity
    
    long_words = sum(1 for w in words if len(w) > 6)
    lix = (len(words) / sentences) + (long_words * 100 / len(words))
    
    return round(lix, 2)
