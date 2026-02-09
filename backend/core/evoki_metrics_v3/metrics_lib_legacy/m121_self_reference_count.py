"""
Evoki Metrics Library - m121_self_reference_count

Cognitive metric: Self-reference count.
"""

def compute_m121_self_reference_count(text: str) -> int:
    """
    m121_self_reference_count: Self-Reference Count
    
    SPEC: Count of self-referential words (ich, mich, mir, mein, etc.)
    
    Measures self-focus in communication.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    self_words = ["ich", "mich", "mir", "mein", "meine", "meiner"]
    text_lower = text.lower()
    
    return sum(text_lower.count(w) for w in self_words)
