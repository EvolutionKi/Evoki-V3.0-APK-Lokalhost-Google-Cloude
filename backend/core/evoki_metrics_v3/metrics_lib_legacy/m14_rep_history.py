"""
m14_rep_history: Repetition (Historical)

Measures word overlap with conversation history (last 10 turns).
Uses Jaccard-style ratio: |intersection| / |current_words|

Detects broader repetitive patterns across conversation.
"""

from typing import List


def compute_m14_rep_history(text: str, history: List[str]) -> float:
    """
    Calculate m14_rep_history (Historical Repetition)
    
    Args:
        text: Current text
        history: List of previous texts
    
    Returns:
        Repetition score [0, 1] - Higher = more repetitive with history
    """
    if not history:
        return 0.0
    
    curr_words = set(text.lower().split())
    all_history_words = set()
    for h in history[-10:]:  # Last 10 turns
        all_history_words.update(h.lower().split())
    
    if not curr_words or not all_history_words:
        return 0.0
    
    intersection = len(curr_words & all_history_words)
    return round(intersection / len(curr_words), 4)


__all__ = ['compute_m14_rep_history']
