"""
Evoki Metrics Library - m59_drive_balance - Antriebsbalance

Andromatik Drive System - Token Economy
"""

def compute_m59_drive_balance(tokens_soc: float, tokens_log: float, epsilon: float = 1e-9) -> float:
    """
    m59_drive_balance: Antriebsbalance - Andromatik
    
    ANDROMATIK: Die Präferenz-Balance (Sozial vs Logisch)
    
    Drive Balance misst das Verhältnis zwischen sozialen und logischen Tokens.
    Zeigt die aktuelle "Ausrichtung" des Systems.
    
    Formula (Andromatik):
        drive_balance = tokens_soc / (tokens_soc + tokens_log + ε)
    
    Komponenten:
    - tokens_soc: Soziale Token-Reserve
    - tokens_log: Logische Token-Reserve
    - ε (epsilon): Stabilisierungskonstante (verhindert Division durch 0)
    
    Interpretation:
    - drive_balance > 0.6: Sozial-orientiert (empathic mode)
    - drive_balance ≈ 0.5: Ausgewogen (balanced mode)
    - drive_balance < 0.4: Logik-orientiert (analytical mode)
    
    Usage:
    - Determines response generation strategy
    - Influences tone and style
    - Modulates m60_action_urge
    - Guides policy selection in Andromatik Drive
    
    Example States:
    - 0.8: "Ich bin im Empathie-Modus" (sehr sozial)
    - 0.5: "Ich bin im Balance-Modus" (hybrid)
    - 0.2: "Ich bin im Analyse-Modus" (sehr logisch)
    
    Reference:
        calculator_spec_A_PHYS_V11.py:300-305
    """
    denominator = tokens_soc + tokens_log + epsilon
    drive_balance = tokens_soc / denominator
    return round(max(0.0, min(1.0, drive_balance)), 4)
