"""
Evoki Metrics Library - m163_x_fm_prox

V3.1 Extension: Fixation Proximity (Matter Stabil Detection)
"""

def compute_m163_x_fm_prox(A_variance: float, nabla_A: float) -> float:
    """
    m163_x_fm_prox: Fixation Proximity (V3.1 Extension)
    
    SPEC V3.1: Detects "Matter Stabil" - forced metastable equilibrium.
    The system is frozen/dead when variance is too low and gradient flatlines.
    
    Formula: x_fm_prox = 1 if (var(A) < 0.005 AND |∇A| < 0.02) else 0
    
    Physics Interpretation:
    - Binary detector for "frozen state"
    - Low variance = no movement in phase space
    - Flat gradient = no evolution pressure
    - Result: System stuck at local minimum (death)
    
    Reference: VektorMathik.txt Line 66-67
    """
    # Thresholds from VektorMathik
    VARIANCE_THRESHOLD = 0.005
    GRADIENT_THRESHOLD = 0.02
    
    if A_variance < VARIANCE_THRESHOLD and abs(nabla_A) < GRADIENT_THRESHOLD:
        return 1.0  # Fixation detected
    return 0.0  # System alive
