"""
Evoki Metrics Library - m168_mode_hp

V3.1 Extension: Mode HP (Hosgelding Principle Mode Selector)
"""

def compute_m168_mode_hp(c_crit: float) -> str:
    """
    m168_mode_hp: Mode HP - Hosgelding Principle (V3.1 Extension)
    
    SPEC V3.1: Selects interaction mode based on criticality (Flussbett-Analogie).
    
    Formula:
        C_crit < 0.3: "probe"   (zu trocken → Probing)
        C_crit > 0.7: "mirror"  (zu nass → Spiegeln)
        else: "guard"           (normal → Guarding)
    
    Physics Interpretation - Riverbed Analogy:
    - Zu trocken (low C_crit): Need to probe, explore, add energy
    - Zu nass (high C_crit): Need to mirror, reflect, calm down
    - Goldilocks zone: Normal guarding/guidance mode
    
    C_crit = (Tension + Danger) / Readiness
    
    Reference: VektorMathik.txt Line 157-158, Andromatik Hosgelding
    """
    if c_crit < 0.3:
        return "probe"  # Low criticality - exploratory mode
    elif c_crit > 0.7:
        return "mirror"  # High criticality - reflective mode
    else:
        return "guard"  # Normal - standard guidance mode
