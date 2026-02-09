"""
Evoki Metrics Library - m63_phi_score - Phi-Score

Andromatik Drive System - Phi-Layer (Finale Entscheidung)
"""

def compute_m63_phi_score(U: float, R: float, lambda_weight: float = 1.0) -> float:
    """
    m63_phi_score: Phi-Score - Andromatik Phi-Layer
    
    ANDROMATIK (Original): Die finale Abwägung
    
    Der "Phi-Score" entscheidet: Go or No-Go?
    Formula: U - λ·R (Nutzen minus gewichtetes Risiko)
    
    Formula (Andromatik):
        Phi = U - λ·R
        
        wobei λ (Lambda) = Risiko-Gewichtung (default 1.0)
    
    Interpretation:
    - Phi > 0: Go! (Nutzen überwiegt Risiko)
    - Phi < 0: Stop! (Risiko überwiegt Nutzen)
    - Phi ≈ 0: Grenzfall (weitere Analyse nötig)
    
    Grounded Theory: Free Energy Principle
    - Phi = "Expected Free Energy"
    - System minimiert Free Energy durch Action Selection
    
    Reference:
        VekTorMathik.txt Line 152-153
        calculator_spec_A_PHYS_V11.py:287
    """
    phi = U - lambda_weight * R
    # Note: Phi CAN be negative! (Risk dominates)
    return round(phi, 4)
