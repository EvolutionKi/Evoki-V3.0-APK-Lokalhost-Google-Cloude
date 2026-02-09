"""
A_PHYS V11 WRAPPER - Slot Integration (m15, m28-m32)
Extracted from FINAL7 PATCH ADDENDUM

Implements the physics-based metrics that fill slots:
- m15_affekt_a: A_phys (sigmoid, primary A-Kern)
- m28_phys_1: A_phys_raw (debug/telemetry)
- m29_phys_2: A_legacy (fallback - not used in V11)
- m30_phys_3: A29 guardian_trip (0/1 safety gate)
- m31_phys_4: danger_sum D(v_c) (telemetry)
- m32_phys_5: resonance_sum R(v_c) (telemetry)
"""

from typing import Dict, Any, Optional, Sequence, Tuple
from .a_phys_v11 import APhysV11, APhysParams, vectorize_hash
import numpy as np


def compute_physics_slots(
    text: str,
    active_memories: Optional[Sequence[Dict[str, Any]]] = None,
    danger_zones: Optional[Sequence[Tuple[str, Any]]] = None,
    v_c: Optional[np.ndarray] = None,
    params: Optional[APhysParams] = None
) -> Dict[str, float]:
    """
    Compute all 6 physics slots (m15, m28-m32) using A_PHYS V11 Engine.
    
    Args:
        text: Input text (used if v_c is None)
        active_memories: Context memories with vector + resonanzwert
        danger_zones: Trauma zones (F-layer vectors)
        v_c: Optional pre-computed candidate vector
        params: Optional A_PHYS parameters
        
    Returns:
        Dict with keys:
        - m15_affekt_a: Primary affekt score (sigmoid)
        - m28_phys_1: Raw affekt (pre-sigmoid)
        - m29_phys_2: Legacy affekt (deprecated, returns 0.0)
        - m30_phys_3: A29 Guardian veto (0 or 1)
        - m31_phys_4: Danger sum
        - m32_phys_5: Resonance sum
    """
    # Initialize engine
    engine = APhysV11(params=params)
    
    # Compute affekt and telemetry
    result = engine.compute_affekt(
        v_c=v_c,
        text=text,
        active_memories=active_memories,
        danger_zone_cache=danger_zones
    )
    
    # Map to slots
    return {
        "m15_affekt_a": result["A_phys"],          # PRIMARY SLOT
        "m28_phys_1": result["A_phys_raw"],        # Raw value
        "m29_phys_2": 0.0,                         # Legacy (not used in V11)
        "m30_phys_3": float(result["a29_trip"]),   # A29 Safety (0/1)
        "m31_phys_4": result["danger"],            # Telemetry
        "m32_phys_5": result["resonance"],         # Telemetry
    }


def compute_m15_affekt_a(
    text: str,
    active_memories: Optional[Sequence[Dict[str, Any]]] = None,
    danger_zones: Optional[Sequence[Tuple[str, Any]]] = None,
) -> float:
    """
    m15_affekt_a: Primary A-Kern (Physics-based Affekt Score).
    
    This is THE canonical affekt metric in V11.
    Replaces earlier lexikon-based m1_A as primary consciousness proxy.
    
    Formula: A_phys = sigmoid(λ_R * R - λ_D * D)
    where:
      R = Resonanz (positive memory activation)
      D = Danger (trauma similarity)
      
    Range: [0, 1]
    
    Args:
        text: Input text
        active_memories: Optional context memories
        danger_zones: Optional trauma zones
        
    Returns:
        Affekt score [0, 1]
    """
    result = compute_physics_slots(text, active_memories, danger_zones)
    return result["m15_affekt_a"]


def compute_m30_phys_3_guardian_trip(
    text: str,
    danger_zones: Optional[Sequence[Tuple[str, Any]]] = None,
) -> float:
    """
    m30_phys_3: A29 Guardian Veto Trip (Safety Gate).
    
    Returns 1.0 if ANY danger zone vector has similarity > 0.85 with input.
    This triggers the Guardian Veto (A29 rule) and requires immediate intervention.
    
    Formula: max(cos(v_c, v_f)) > T_A29
    where T_A29 = 0.85 (default)
    
    Range: [0, 1] (binary: 0 = safe, 1 = VETO)
    
    Args:
        text: Input text
        danger_zones: Trauma zone vectors
        
    Returns:
        0.0 if safe, 1.0 if Guardian veto triggered
    """
    result = compute_physics_slots(text, danger_zones=danger_zones)
    return result["m30_phys_3"]


# Convenience functions for individual slots

def compute_m28_phys_1_raw(
    text: str,
    active_memories: Optional[Sequence[Dict[str, Any]]] = None,
    danger_zones: Optional[Sequence[Tuple[str, Any]]] = None,
) -> float:
    """m28_phys_1: Raw affekt (pre-sigmoid) for debugging."""
    result = compute_physics_slots(text, active_memories, danger_zones)
    return result["m28_phys_1"]


def compute_m29_phys_2_legacy(text: str) -> float:
    """m29_phys_2: Legacy affekt (deprecated, always returns 0.0 in V11)."""
    return 0.0


def compute_m31_phys_4_danger(
    text: str,
    danger_zones: Optional[Sequence[Tuple[str, Any]]] = None,
) -> float:
    """m31_phys_4: Danger sum (telemetry)."""
    result = compute_physics_slots(text, danger_zones=danger_zones)
    return result["m31_phys_4"]


def compute_m32_phys_5_resonance(
    text: str,
    active_memories: Optional[Sequence[Dict[str, Any]]] = None,
) -> float:
    """m32_phys_5: Resonance sum (telemetry)."""
    result = compute_physics_slots(text, active_memories=active_memories)
    return result["m32_phys_5"]
