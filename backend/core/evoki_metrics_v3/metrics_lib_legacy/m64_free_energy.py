"""
Evoki Metrics Library - m64_free_energy - Freie Energie

Andromatik Drive System - Energy Metric
"""

def compute_m64_free_energy(U: float, R: float) -> float:
    """
    m64_free_energy: Freie Energie - Andromatik
    
    ANDROMATIK: Die verfügbare System-Energie
    
    Freie Energie misst die Diskrepanz zwischen Nutzen und Sicherheit.
    Hohe freie Energie = System ist im Ungleichgewicht, muss handeln.
    
    Formula (Andromatik):
        Free_Energy = |U - (1 - R)|
    
    Komponenten:
    - U: Nutzen (Informationshunger)
    - (1-R): Sicherheit (inverse Risiko)
    
    Interpretation:
    - High Free Energy: System im Ungleichgewicht
      → Muss Aktionen wählen, um Balance zu finden
    - Low Free Energy: System im Gleichgewicht
      → Kann ruhen, keine dringende Action nötig
    
    Grounded Theory: Free Energy Principle (Karl Friston)
    - Biological systems minimize free energy
    - FE = Surprise + Divergence
    - Core principle of Active Inference
    
    Usage in Andromatik:
    - Triggers action selection when FE > threshold
    - Modulates learning rate
    - Influences policy entropy (exploration)
    
    Reference:
        calculator_spec_A_PHYS_V11.py:312-315
        Friston, K. (2010). "The free-energy principle"
    """
    # Absolute difference between utility and safety
    free_energy = abs(U - (1.0 - R))
    return round(max(0.0, min(1.0, free_energy)), 4)
