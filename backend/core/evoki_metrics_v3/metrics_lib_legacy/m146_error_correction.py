"""
m146: Error Correction
"""




def compute_m146_error_correction(corrections: int, total_outputs: int) -> float:
    """m146: Error Correction"""
    return round(corrections / max(1, total_outputs), 4)
