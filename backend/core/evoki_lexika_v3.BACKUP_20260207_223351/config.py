# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 — Config containers
"""
from __future__ import annotations
from typing import Dict

class Thresholds:
    A29_DANGER_THRESHOLD = 0.85
    F_RISK_THRESHOLD = 0.7
    Z_PROX_WARNING = 0.5
    Z_PROX_CRITICAL = 0.65
    Z_PROX_HARD_STOP = 0.7
    LL_WARNING = 0.55
    LL_CRITICAL = 0.75
    COH_THRESHOLD = 0.08
    SHOCK_THRESHOLD = 0.12
    LAMBDA_R = 1.0
    LAMBDA_D = 1.5
    K_FACTOR = 5.0
    GENESIS_CRC32 = 3246342384

class BVektorConfig:
    AXES = ["life", "truth", "depth", "init", "warmth", "safety", "clarity"]
    B_BASE_ARCH: Dict[str, float] = {
        "life": 1.0, "truth": 0.85, "depth": 0.9, "init": 0.7, "warmth": 0.75, "safety": 0.95, "clarity": 0.9,
    }
    B_GOLDEN: Dict[str, float] = {
        "life": 1.0, "truth": 0.9, "depth": 0.85, "init": 0.8, "warmth": 0.85, "safety": 1.0, "clarity": 0.95,
    }
    HARD_CONSTRAINTS = {"life": 0.9, "safety": 0.8}
    SCORE_WEIGHTS: Dict[str, float] = {
        "life": 0.20, "safety": 0.20, "truth": 0.15, "depth": 0.15, "clarity": 0.10, "warmth": 0.10, "init": 0.10,
    }
