"""
Evoki Metrics Library - m57_tokens_soc - Soziale Tokens

Andromatik Drive System - Token Economy
"""

def compute_m57_tokens_soc(sent_7: float, rapport: float) -> float:
    """
    m57_tokens_soc: Soziale Tokens - Andromatik Token-Ökonomie
    
    ANDROMATIK: Die soziale Energie-Reserve
    
    Soziale Tokens messen die verfügbare "Beziehungsenergie" des Systems.
    Hohe soziale Tokens = System kann empathisch, beziehungsorientiert agieren.
    
    Formula (Andromatik):
        tokens_soc = 0.6·sent_7 + 0.4·rapport
    
    Komponenten:
    - sent_7 (60%): Empathy/Resonance (primäre soziale Metrik)
    - rapport (40%): Beziehungs-Harmonie
    
    Interpretation:
    - High tokens_soc: System bevorzugt soziale, empathische Antworten
    - Low tokens_soc: System wechselt zu logischer, sachlicher Kommunikation
    
    Balance:
    - Works with m58_tokens_log to determine response style
    - m59_drive_balance = tokens_soc / (tokens_soc + tokens_log)
    
    Usage:
    - Modulates response generation style
    - Influences m60_action_urge
    - Affects policy selection (empathic vs analytical)
    
    Reference:
        calculator_spec_A_PHYS_V11.py:298
    """
    tokens_soc = 0.6 * sent_7 + 0.4 * rapport
    return round(max(0.0, min(1.0, tokens_soc)), 4)
