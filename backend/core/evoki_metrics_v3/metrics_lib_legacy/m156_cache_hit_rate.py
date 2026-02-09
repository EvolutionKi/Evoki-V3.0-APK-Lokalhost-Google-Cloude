"""
Evoki Metrics Library - m156_cache_hit_rate

System metric: Cache hit rate.
"""

def compute_m156_cache_hit_rate(hits: int, total: int) -> float:
    """
    m156_cache_hit_rate: Cache Hit Rate
    
    SPEC: hits / total
    
    Proportion of cache requests that were hits.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(hits / max(1, total), 4)
