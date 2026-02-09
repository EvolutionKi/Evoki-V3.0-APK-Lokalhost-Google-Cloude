"""
Evoki Metrics Library - m128_token_ratio

Cognitive metric: Token ratio user/AI.
"""

def compute_m128_token_ratio(user_tokens: int, ai_tokens: int) -> float:
    """
    m128_token_ratio: Token Ratio User/AI
    
    SPEC: user_tokens / ai_tokens
    
    Ratio of user input to AI response tokens.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(user_tokens / max(1, ai_tokens), 4)
