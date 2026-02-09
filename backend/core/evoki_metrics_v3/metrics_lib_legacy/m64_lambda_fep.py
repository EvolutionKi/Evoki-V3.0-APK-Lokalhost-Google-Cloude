"""
m64_lambda: Lambda FEP
"""




def compute_m64_lambda_fep(s_entropy: float, action_space: int = 10) -> float:
    """m64_lambda: Lambda FEP"""
    return round(s_entropy / action_space, 4)
