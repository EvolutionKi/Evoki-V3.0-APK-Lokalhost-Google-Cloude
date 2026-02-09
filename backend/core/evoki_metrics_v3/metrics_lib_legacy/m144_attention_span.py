"""
m144: Attention Span
"""




def compute_m144_attention_span(focus_duration: float, max_duration: float = 60.0) -> float:
    """m144: Attention Span"""
    return round(min(1.0, focus_duration / max_duration), 4)
