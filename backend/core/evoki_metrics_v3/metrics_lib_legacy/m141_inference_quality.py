"""
Evoki Metrics Library - m141_inference_quality

Meta-cognition metric: Logical inference quality.
"""

def compute_m141_inference_quality(logical_consistency: float) -> float:
    """
    m141_inference_quality: Inference Quality
    
    SPEC: clamp(logical_consistency)
    
    Measures quality of logical reasoning.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, logical_consistency)), 4)
