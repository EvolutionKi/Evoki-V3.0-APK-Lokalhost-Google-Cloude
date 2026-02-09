"""m22_cog_load: Cognitive Load
SPEC Formula: cog_load = clip(token_count / 500.0)
Reference: EVOKI_V3_METRICS_SPECIFICATION.md:3257-3267"""
from ._helpers import clamp
def compute_m22_cog_load(token_count: int) -> float:
    return round(clamp(token_count / 500.0), 4)
__all__ = ['compute_m22_cog_load']
