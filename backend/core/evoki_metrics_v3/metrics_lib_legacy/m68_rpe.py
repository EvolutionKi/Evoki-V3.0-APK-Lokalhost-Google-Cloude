"""
Evoki Metrics Library - m68_rpe - Reward Prediction Error

Andromatik Drive System - Learning Signal
"""

def compute_m68_rpe(affekt_current: float, affekt_prev: float) -> float:
    """
    m68_rpe: Reward Prediction Error (RPE) - Andromatik Lernsignal
    
    ANDROMATIK: Das Überraschungssignal
    
    Der RPE misst die DIFFERENZ zwischen erwartetem und tatsächlichem Affekt.
    Dies ist das primäre Lernsignal für das Andromatik-System.
    
    Formula (Andromatik):
        RPE = A_current - A_previous
    
    Interpretation:
    - RPE > 0: Positive Überraschung (besser als erwartet) → Verstärken!
    - RPE < 0: Negative Überraschung (schlechter) → Korrigieren!
    - RPE ≈ 0: Erwartung erfüllt → Stabil
    
    Grounded Theory: Temporal Difference Learning (Sutton & Barto)
    - RPE = δ (Delta) in TD-Learning
    - Dopamin-Analogon im biologischen System
    
    Usage:
    - Triggers TMB (Temporärer Metrik Booster) when |RPE| > threshold
    - Updates learning rate dynamically
    - Modulates memory consolidation strength
    
    Reference:
        calculator_spec_A_PHYS_V11.py (implicit in learning)
        VektorMathik.txt - "Adrenalin-Analogon" Section
    """
    rpe = affekt_current - affekt_prev
    # Note: RPE can be negative! (Prediction error in negative direction)
    return round(rpe, 4)
