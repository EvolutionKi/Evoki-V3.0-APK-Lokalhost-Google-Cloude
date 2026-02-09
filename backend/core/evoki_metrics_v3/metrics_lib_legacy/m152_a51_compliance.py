"""
Evoki Metrics Library - m152_a51_compliance

System metric: A51 rule compliance.
"""

def compute_m152_a51_compliance(rules_checked: int, rules_passed: int) -> float:
    """
    m152_a51_compliance: A51 Rule Compliance
    
    SPEC: rules_passed / rules_checked
    
    Measures adherence to A51 Genesis Anchor rules.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(rules_passed / max(1, rules_checked), 4)
