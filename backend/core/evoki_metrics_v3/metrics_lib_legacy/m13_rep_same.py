"""
m13_rep_same: Repetition (Same as Previous)

Measures word overlap with immediately previous text.
Uses Jaccard-style ratio: |intersection| / |current_words|

High rep_same indicates stuck/looping on same concepts.
"""


def compute_m13_rep_same(text: str, prev_text: str) -> float:
    """
    Calculate m13_rep_same (Immediate Repetition)
    
    Args:
        text: Current text
        prev_text: Previous text
    
    Returns:
        Repetition score [0, 1] - Higher = more repetitive
    """
    if not prev_text:
        return 0.0
    
    curr_words = set(text.lower().split())
    prev_words = set(prev_text.lower().split())
    
    if not curr_words or not prev_words:
        return 0.0
    
    intersection = len(curr_words & prev_words)
    return round(intersection / len(curr_words), 4)


__all__ = ['compute_m13_rep_same']
