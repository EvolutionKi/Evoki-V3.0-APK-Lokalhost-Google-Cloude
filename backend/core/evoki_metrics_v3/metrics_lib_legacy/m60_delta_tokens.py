"""
m60_delta_tokens: Token-Delta
"""




def compute_m60_delta_tokens(tok_new: float, tok_old: float) -> float:
    """m60_delta_tokens: Token-Delta"""
    return round(tok_new - tok_old, 2)
