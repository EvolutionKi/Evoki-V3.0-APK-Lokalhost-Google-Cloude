"""
m4_flow: Flow State

SPEC: Measures "smoothness" of text production
flow = smoothness × (1 - break_penalty)

Smoothness is calculated from sentence length variance.
Break penalty counts interruption markers (..., --, etc.)
"""

from ._helpers import clamp


def compute_m4_flow(text: str) -> float:
    """
    Calculate m4_flow (Text Production Flow)
    
    Args:
        text: Input text
    
    Returns:
        Flow score [0, 1] - Higher = smoother production
    """
    break_markers = ['...', '--', '—', '()', '  ']
    break_count = sum(text.count(marker) for marker in break_markers)
    
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 0.8  # Single sentence gets good flow
    
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len)**2 for l in lengths) / len(lengths)
    
    if mean_len > 0:
        smoothness = 1.0 / (1.0 + variance / mean_len)
    else:
        smoothness = 0.5
    
    break_penalty = min(0.5, break_count / len(sentences))
    flow = smoothness * (1.0 - break_penalty)
    
    return round(clamp(flow), 4)


__all__ = ['compute_m4_flow']
