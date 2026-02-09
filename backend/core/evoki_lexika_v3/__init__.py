# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 package entrypoint.
"""
from .lexika_data import ALL_LEXIKA
from .registry import (
    lexika_hash, get_lexikon_stats, flatten_lexika_terms,
    export_lexika_json, validate_lexika, require_lexika_or_raise,
)
from .engine import (
    compute_lexicon_score, compute_b_past_with_regex, compute_hazard_score, LexMatch,
)
from .config import Thresholds, BVektorConfig

__all__ = [
    "ALL_LEXIKA",
    "lexika_hash", "get_lexikon_stats", "flatten_lexika_terms", "export_lexika_json",
    "validate_lexika", "require_lexika_or_raise",
    "compute_lexicon_score", "compute_b_past_with_regex", "compute_hazard_score", "LexMatch",
    "Thresholds", "BVektorConfig",
]
