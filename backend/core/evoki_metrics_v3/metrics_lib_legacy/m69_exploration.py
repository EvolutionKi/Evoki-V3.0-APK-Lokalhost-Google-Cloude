"""
Evoki Metrics Library - m69_exploration - Exploration Drive

Andromatik Drive System - Exploration vs Exploitation
"""

def compute_m69_exploration(U: float, gen_index: float) -> float:
    """
    m69_exploration: Exploration Drive - Andromatik
    
    ANDROMATIK: Der Entdeckungs-Trieb
    
    Exploration misst den Drang, NEUES zu entdecken statt Bekanntes zu nutzen.
    Kombiniert Nutzen (Informationshunger) mit Generativität (Kreativität).
    
    Formula (Andromatik):
        Exploration = 0.6·U + 0.4·gen_index
    
    Komponenten:
    - U (60%): Nutzen (epistemische Unsicherheit, Info-Hunger)
    - gen_index (40%): Generativität (Neuheitsproduktion)
    
    Interpretation:
    - High Exploration: System sucht aktiv nach neuen Informationen
    - Low Exploration: System ruht in bekannten Mustern
    
    Grounded Theory: Exploration-Exploitation Tradeoff
    - Classic RL dilemma
    - UCB (Upper Confidence Bound) algorithms
    
    Balance:
    - Works in opposition with m70_exploitation
    - Optimal: Dynamic balance based on context
    
    Reference:
        calculator_spec_A_PHYS_V11.py:336-340
    """
    exploration = 0.6 * U + 0.4 * gen_index
    return round(max(0.0, min(1.0, exploration)), 4)
