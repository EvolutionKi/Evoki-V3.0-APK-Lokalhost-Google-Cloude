"""
Evoki Metrics Library - m139_working_memory

Meta-cognition metric: Working memory utilization.
"""

def compute_m139_working_memory(context_items: int, max_items: int = 7) -> float:
    """
    m139_working_memory: Working Memory Utilization
    
    SPEC: min(1.0, context_items / max_items)
    
    Default max_items = 7 (Miller's magic number).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(min(1.0, context_items / max_items), 4)
