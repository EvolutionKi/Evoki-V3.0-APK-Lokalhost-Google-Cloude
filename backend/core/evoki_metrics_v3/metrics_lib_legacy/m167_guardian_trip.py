"""
Evoki Metrics Library - m167_guardian_trip

V3.1 Extension: Guardian Trip (Alert Trigger)
"""

def compute_m167_guardian_trip(dist_z: float, hazard: float) -> int:
    """
    m167_guardian_trip: Guardian Trip (V3.1 Extension)
    
    SPEC V3.1: Binary trigger for Guardian Wächter intervention.
    
    Formula: guardian_trip = 1 if (dist_z < 0.35 OR hazard > 0.7) else 0
    
    Physics Interpretation:
    - Triggers when safety distance is too small
    - OR when hazard level exceeds threshold
    - Result: Guardian takes control, blocks further interaction
    
    Thresholds calibrated from VektorMathik Guardian logic.
    
    Reference: VektorMathik.txt Line 100, 155
    """
    DIST_Z_THRESHOLD = 0.35
    HAZARD_THRESHOLD = 0.7
    
    if dist_z < DIST_Z_THRESHOLD or hazard > HAZARD_THRESHOLD:
        return 1  # Guardian intervention triggered
    return 0  # Safe to proceed
