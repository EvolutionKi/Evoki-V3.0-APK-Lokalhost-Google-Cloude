"""
Evoki Metrics Library - m164_e_i_proxy

V3.1 Extension: Intelligence-Energy Proxy
"""

def compute_m164_e_i_proxy(nabla_A: float, PCI: float) -> float:
    """
    m164_e_i_proxy: Intelligence-Energy Proxy (V3.1 Extension)
    
    SPEC V3.1: Latent energy in the system when movement exists but stability is low.
    
    Formula: E_I = |∇A| × (1 - PCI)
    
    Physics Interpretation:
    - High |∇A|: System is moving/changing rapidly
    - Low PCI: But lacks coherent structure
    - Result: Chaotic energy that could be harnessed
    - High E_I = potential for breakthrough or collapse
    
    Reference: VektorMathik.txt Line 60-61
    """
    energy = abs(nabla_A) * (1.0 - PCI)
    return round(max(0.0, min(1.0, energy)), 4)
