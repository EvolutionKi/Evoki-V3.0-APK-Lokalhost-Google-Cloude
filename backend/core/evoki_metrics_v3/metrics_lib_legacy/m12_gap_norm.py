"""
m12_gap_norm: Normalized Time Gap

Normalizes time gap to [0, 1] range using 60 seconds as baseline.
gap_norm = min(1.0, gap_s / 60.0)

Values > 60s are clamped to 1.0 (long pause).
"""


def compute_m12_gap_norm(gap_s: float) -> float:
    """
    Calculate m12_gap_norm (Normalized Time Gap)
    
    Args:
        gap_s: Gap in seconds (m11_gap_s)
    
    Returns:
        Normalized gap [0, 1] - capped at 60 seconds
    """
    return round(min(1.0, gap_s / 60.0), 4)


__all__ = ['compute_m12_gap_norm']
