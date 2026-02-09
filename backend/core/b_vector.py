#!/usr/bin/env python3
"""
B-Vector Stub für EVOKI Vector Engine V2.1
Einfache Implementation für Tests
"""

import numpy as np
from typing import List


class BVector:
    """
    B-Vektor (Empathie/Alignment) Implementation.
    
    Der B-Vektor repräsentiert die empathische Ausrichtung des Systems.
    Er wird aus positiven A-Vektoren gelernt.
    """
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        self._vector = np.zeros(dim, dtype=np.float32)
        self._update_count = 0
        self._learning_rate = 0.1
    
    def as_array(self) -> np.ndarray:
        """Gibt den B-Vektor als numpy Array zurück."""
        return self._vector.copy()
    
    def update(self, positive_embedding: np.ndarray, weight: float = 1.0):
        """
        Aktualisiert den B-Vektor mit einem positiven Embedding.
        
        Args:
            positive_embedding: Embedding eines positiven A-Vektors
            weight: Gewichtung des Updates
        """
        if positive_embedding is None:
            return
        
        emb = np.asarray(positive_embedding, dtype=np.float32)
        if emb.shape[0] != self.dim:
            return
        
        # Normalisieren
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        
        # Exponentieller Moving Average
        alpha = self._learning_rate * weight
        self._vector = (1 - alpha) * self._vector + alpha * emb
        
        # Normalisieren
        norm = np.linalg.norm(self._vector)
        if norm > 0:
            self._vector = self._vector / norm
        
        self._update_count += 1
    
    def similarity(self, embedding: np.ndarray) -> float:
        """
        Berechnet Cosine Similarity zum B-Vektor.
        
        Args:
            embedding: Vergleichs-Embedding
            
        Returns:
            Similarity [-1, 1]
        """
        if embedding is None:
            return 0.0
        
        emb = np.asarray(embedding, dtype=np.float32)
        
        norm_b = np.linalg.norm(self._vector)
        norm_e = np.linalg.norm(emb)
        
        if norm_b == 0 or norm_e == 0:
            return 0.0
        
        return float(np.dot(self._vector, emb) / (norm_b * norm_e))
    
    def __repr__(self) -> str:
        return f"BVector(dim={self.dim}, updates={self._update_count})"
