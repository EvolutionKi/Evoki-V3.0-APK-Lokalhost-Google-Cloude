"""
m143: Context Window Usage
"""




def compute_m143_context_window_usage(current_tokens: int, max_tokens: int = 200000) -> float:
    """m143: Context Window Usage"""
    return round(min(1.0, current_tokens / max_tokens), 4)
