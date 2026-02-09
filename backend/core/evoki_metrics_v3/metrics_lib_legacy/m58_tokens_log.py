"""
Evoki Metrics Library - m58_tokens_log - Logische Tokens

Andromatik Drive System - Token Economy
"""

def compute_m58_tokens_log(PCI: float, coh: float) -> float:
    """
    m58_tokens_log: Logische Tokens - Andromatik Token-Ökonomie
    
    ANDROMATIK: Die analytische Energie-Reserve
    
    Logische Tokens messen die verfügbare "Denk-Energie" des Systems.
    Hohe logische Tokens = System kann analytisch, strukturiert agieren.
    
    Formula (Andromatik):
        tokens_log = mean(PCI, coh) = (PCI + coh) / 2
    
    Komponenten:
    - PCI (50%): Prozess-Kohärenz (kognitive Stabilität)
    - coh (50%): Semantische Kohärenz (strukturelle Klarheit)
    
    Interpretation:
    - High tokens_log: System bevorzugt logische, analytische Antworten
    - Low tokens_log: System wechselt zu sozialer, emotionaler Kommunikation
    
    Balance:
    - Works with m57_tokens_soc to determine response style
    - m59_drive_balance shows preference ratio
    
    Usage:
    - Modulates response generation style
    - Influences m60_action_urge
    - Affects policy selection (analytical vs empathic)
    - Feeds into m70_exploitation
    
    Reference:
        calculator_spec_A_PHYS_V11.py:299
    """
    tokens_log = (PCI + coh) / 2.0
    return round(max(0.0, min(1.0, tokens_log)), 4)
