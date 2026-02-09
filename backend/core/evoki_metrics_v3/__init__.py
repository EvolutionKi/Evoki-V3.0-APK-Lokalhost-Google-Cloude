# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — METRICS MODULE REGISTRY

Central registry for all 168 metric compute functions.

This module provides easy access to all metrics across all categories.
"""

# Import all compute functions from new modules
from .hypermetrics import *
from .fep_evolution import *
from .emotions import *
from .text_analytics import *
from .dynamics_turbidity import *
from .system_metrics import *
from .final_metrics import *

# Re-export contract registry
from .contract_registry import ContractRegistry


# Module version
__version__ = "3.0.0"

# Total metrics implemented in new modules
NEW_MODULES_COUNT = {
    "hypermetrics": 12,
    "fep_evolution": 21,
    "emotions": 19,
    "text_analytics": 10,
    "dynamics_turbidity": 22,
    "system_metrics": 31,
    "final_metrics": 14,
}

TOTAL_NEW_METRICS = sum(NEW_MODULES_COUNT.values())  # 129 metrics

print(f"EVOKI Metrics v{__version__}")
print(f"New modules: {TOTAL_NEW_METRICS} metrics")
print(f"Module breakdown: {NEW_MODULES_COUNT}")
