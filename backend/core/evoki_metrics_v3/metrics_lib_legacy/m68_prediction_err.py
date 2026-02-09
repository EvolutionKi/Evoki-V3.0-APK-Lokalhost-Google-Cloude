"""
m68_prediction_err: Prediction Error
"""




def compute_m68_prediction_err(expected: float, actual: float) -> float:
    """m68_prediction_err: Prediction Error"""
    return round(abs(expected - actual), 4)
