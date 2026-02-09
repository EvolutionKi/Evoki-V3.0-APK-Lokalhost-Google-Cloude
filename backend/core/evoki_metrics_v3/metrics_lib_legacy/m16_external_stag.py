"""
m16_external_stag: External Stagnation

Measures progress stagnation in conversation.
Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)

High stagnation indicates stuck conversation or lack of resolution.
"""


def compute_m16_external_stag(turns_without_progress: int) -> float:
    """
    Calculate m16_external_stag (External Stagnation)
    
    Args:
        turns_without_progress: Number of turns without meaningful progress
    
    Returns:
        Stagnation score [0, 1] - Normalized to 5 turns
    """
    return round(min(1.0, turns_without_progress / 5.0), 4)


__all__ = ['compute_m16_external_stag']
