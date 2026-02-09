"""
Evoki Metrics Library - m165_dist_z

V3.1 Extension: Distance to Z (Safety Distance)
"""

def compute_m165_dist_z(A: float, LL: float, ctx_break: float) -> float:
    """
    m165_dist_z: Distance to Z (V3.1 Extension)
    
    SPEC V3.1: Safety distance to the collapse point ("z").
    Updated formula from VektorMathik spec.
    
    Formula: dist_z = A × (1 - max(LL, ctx_break))
    
    Physics Interpretation:
    - High A: System has base vitality
    - max(LL, ctx_break): Worst loop/break condition
    - Result: Distance shrinks with loops or context breaks
    - Low dist_z triggers Guardian intervention
    
    Reference: VektorMathik.txt Line 63-64 (z_prox inverse)
    """
    worst_condition = max(LL, ctx_break)
    distance = A * (1.0 - worst_condition)
    return round(max(0.0, min(1.0, distance)), 4)
