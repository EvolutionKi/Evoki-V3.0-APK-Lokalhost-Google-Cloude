"""
Evoki Metrics Library - m60_action_urge - Handlungsdrang

Andromatik Drive System - Action Trigger
"""

def compute_m60_action_urge(surprise: float, phi: float) -> float:
    """
    m60_action_urge: Handlungsdrang - Andromatik Action Trigger
    
    ANDROMATIK: Der Impuls zu handeln
    
    Action Urge misst den "Drang" des Systems, eine Aktion auszuführen.
    Kombiniert Überraschung (neuer Input) mit Phi-Score (Go-Signal).
    
    Formula (Andromatik):
        action_urge = 0.5·surprise + 0.5·max(0, phi)
    
    Komponenten:
    - surprise (50%): Überraschungsfaktor (neuer Stimulus)
    - max(0, phi) (50%): Positiver Phi nur (nur wenn Nutzen > Risiko)
    
    Interpretation:
    - High action_urge: System "will" aktiv handeln
      → Generiert Antwort, schlägt Actions vor
    - Low action_urge: System "wartet" passiv
      → Beobachtet, sammelt mehr Info
    
    Critical Note:
    - Uses max(0, phi) - negative Phi (Risk > Utility) wird NICHT gezählt!
    - Surprise allein kann Action triggern (explorativ)
    - Phi positiv = verfärkt Action (exploitativ)
    
    Usage:
    - Triggers response generation threshold
    - Modulates response length/depth
    - Influences whether to ask questions vs make statements
    - Core of Active Inference loop
    
    Reference:
        calculator_spec_A_PHYS_V11.py:306-310
        Active Inference: Actions are selected to minimize expected free energy
    """
    positive_phi = max(0.0, phi)
    action_urge = 0.5 * surprise + 0.5 * positive_phi
    return round(max(0.0, min(1.0, action_urge)), 4)
