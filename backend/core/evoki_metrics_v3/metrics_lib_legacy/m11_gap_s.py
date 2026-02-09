"""
m11_gap_s: Time Gap in Seconds

Simple time difference between consecutive responses.
Measures time elapsed since last interaction.
"""


def compute_m11_gap_s(timestamp_prev: float, timestamp_now: float) -> float:
    """
    Calculate m11_gap_s (Time Gap)
    
    Args:
        timestamp_prev: Previous timestamp (Unix time)
        timestamp_now: Current timestamp (Unix time)
    
    Returns:
        Gap in seconds [0, ∞)
    """
    return round(max(0.0, timestamp_now - timestamp_prev), 2)


__all__ = ['compute_m11_gap_s']
