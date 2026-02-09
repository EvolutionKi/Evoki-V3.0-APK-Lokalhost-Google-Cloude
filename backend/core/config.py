#!/usr/bin/env python3
"""EVOKI Pipeline - Konfiguration und Schwellenwerte (Andromatik V11.1)"""

from dataclasses import dataclass

@dataclass
class Config:
    # Pfade
    INPUT_JSONL: str = "evoki_messages.jsonl"
    OUTPUT_DB: str = "evoki_vectors.db"
    
    # Embedding
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    BATCH_SIZE: int = 64
    USE_GPU: bool = True
    
    # Schwellenwerte
    A_CRITICAL: float = 0.85
    F_RISK_CRITICAL: float = 0.85
    T_PANIC_CRITICAL: float = 0.80
    T_DISSO_CRITICAL: float = 0.75
    ZLF_LOOP: float = 0.60
    COH_LOW: float = 0.30
    
    # Fenster
    WINDOW_SHORT: int = 3
    WINDOW_MEDIUM: int = 7
    TRAJECTORY_WINDOW: int = 5

CFG = Config()
