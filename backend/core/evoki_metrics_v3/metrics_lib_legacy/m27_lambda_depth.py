# -*- coding: utf-8 -*-
"""m27_lambda_depth: Semantische Tiefe (Lambda)

SPEC PATCH V3.0.2b: Normalisiert!
lambda_depth = min(1.0, token_count / 100.0)

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m27_lambda_depth(token_count: int) -> float:
    """
    Calculates semantic depth from token count.
    
    Args:
        token_count: Number of tokens in text
        
    Returns:
        Semantic depth value (0.0-1.0, normalized)
    """
    return round(min(1.0, token_count / 100.0), 4)
