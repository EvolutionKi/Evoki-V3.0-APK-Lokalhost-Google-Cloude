"""
m56_surprise: Überraschungsfaktor
"""




def compute_m56_surprise(A_current: float, A_predicted: float) -> float:
    """m56_surprise: Überraschungsfaktor"""
    return round(abs(A_current - A_predicted), 4)
