"""
Evoki Metrics Library - m65_policy_entropy - Policy Entropy

Andromatik Drive System - Decision Uncertainty
"""

def compute_m65_policy_entropy(U: float, surprise: float) -> float:
    """
    m65_policy_entropy: Policy Entropy - Andromatik Entscheidungs-Unsicherheit
    
    ANDROMATIK: Die Offenheit der Strategie-Auswahl
    
    Policy Entropy misst, wie "offen" das System bei der Strategie-Wahl ist.
    Hohe Entropie = viele gleichwertige Optionen (Unsicherheit).
    Niedrige Entropie = klare beste Option (Klarheit).
    
    Formula (Andromatik):
        Policy_Entropy = 0.5·U + 0.5·surprise
    
    Komponenten:
    - U (50%): Nutzen (epistemische Unsicherheit)
    - surprise (50%): Überraschungsfaktor
    
    Interpretation:
    - High Policy Entropy: Viele Handlungsoptionen erscheinen sinnvoll
      → System exploriert, wählt stochastisch
    - Low Policy Entropy: Eine klare beste Aktion
      → System exploitiert, wählt deterministisch
    
    Grounded Theory: Policy Gradient Methods
    - Entropy regularization in RL
    - Soft Actor-Critic (SAC) algorithms
    - Encourages exploration through stochastic policies
    
    Usage:
    - High entropy → more exploration (m69)
    - Low entropy → more exploitation (m70)
    - Modulates action selection temperature
    
    Reference:
        calculator_spec_A_PHYS_V11.py:316-320
    """
    policy_entropy = 0.5 * U + 0.5 * surprise
    return round(max(0.0, min(1.0, policy_entropy)), 4)
