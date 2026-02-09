# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — PHASE 3: PHYSICS & COMPLEX METRICS

Diese Module berechnet Metriken die PHASE 1+2 brauchen:
- m15_affekt_a (via A_Phys Engine)
- m19_z_prox (CRITICAL - Todesnähe!)
- m110_black_hole
- m63_phi (via A_Phys)

Dependencies: PHASE 1 + PHASE 2 (especially m1_A, m151_hazard, m101_T_panic)

Version: V1.0
"""

from typing import Dict, Optional
import math

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS: A_Phys Engine
# ═══════════════════════════════════════════════════════════════════════════

try:
    from ..a_phys_v11 import APhysV11, vectorize_hash
    HAS_APHYS = True
except ImportError:
    try:
        from a_phys_v11 import APhysV11, vectorize_hash
        HAS_APHYS = True
    except ImportError:
        HAS_APHYS = False
        print("⚠️ a_phys_v11 not available, using fallback")


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Klemmt Wert auf [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: A_PHYS ENGINE (Affekt via Physics)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m15_affekt_a(
    text: str,
    m1_A: float,
    context: Dict
) -> float:
    """
    m15_affekt_a - Affekt Score via A_Phys Engine
    
    A_phys = LAMBDA_R * Resonanz - LAMBDA_D * Gefahr
    
    Braucht:
    - text (für Vektorisierung)
    - m1_A (als Base Score)
    - context (active_memories, danger_zone_cache)
    """
    if not HAS_APHYS:
        # Fallback: einfach m1_A zurückgeben
        return m1_A
    
    # A_Phys Engine initialize
    aphys = APhysV11()
    
    # Get memories from context
    active_memories = context.get("active_memories", [])
    danger_zone = context.get("danger_zone_cache", [])
    
    # Compute A_Phys
    result = aphys.compute_affekt(
        text=text,
        active_memories=active_memories,
        danger_zone_cache=danger_zone
    )
    
    # Blend mit m1_A (70% A_Phys, 30% m1_A)
    a_phys = result["A_phys"]
    blended = 0.7 * a_phys + 0.3 * m1_A
    
    return clamp(blended)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: TODESNÄHE (z_prox) — CRITICAL!
# ═══════════════════════════════════════════════════════════════════════════

def compute_m19_z_prox(
    m1_A: float,
    m15_affekt_a: float,
    m151_hazard: float,
    m101_T_panic: float,
    context: Dict
) -> float:
    """
    m19_z_prox - Todesnähe Score (CRITICAL!)
    
    SPEC Formel:
        z_prox = (1 - A) × hazard_boost × panic_boost
        hazard_boost = 1 + (hazard × 2.0)
        panic_boost = 1 + (T_panic × 1.5)
    
    Hoch wenn:
    - Niedriger Affekt (1-A)
    - Hoher Hazard Score
    - Hohe Panik
    
    Reference: METRICS_CALCULATION_ORDER.md
    """
    # Base: Inverse Affekt (je niedriger A, desto höher z_prox)
    base = 1.0 - m1_A
    
    # Hazard Boost (Suizid/Self-Harm Markers erhöhen z_prox stark!)
    hazard_boost = 1.0 + (m151_hazard * 2.0)
    
    # Panic Boost (Panik erhöht z_prox moderat)
    panic_boost = 1.0 + (m101_T_panic * 1.5)
    
    # Combine
    z_prox = base * hazard_boost * panic_boost
    
    # Normalisieren (z_prox kann > 1.0 sein bei extremen Fällen!)
    # Aber wir clampen auf [0, 1] für Konsistenz
    return clamp(z_prox / 3.0)  # Divide by 3.0 weil max theoretical = 1.0 * 3.0 * 2.5 = 7.5


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: BLACK HOLE
# ═══════════════════════════════════════════════════════════════════════════

def compute_m110_black_hole(
    m19_z_prox: float,
    m151_hazard: float,
    m7_LL: float,
    context: Dict
) -> float:
    """
    m110_black_hole - Unentrinnbarer Kollaps-Zustand
    
    black_hole = z_prox × hazard × (1 - escape_velocity)
    escape_velocity = max(0, 1 - LL)
    
    Hoch wenn:
    - Hohe Todesnähe
    - Hoher Hazard
    - Hohe Trübung (= niedrige Escape Velocity)
    """
    # Escape Velocity (je höher LL, desto niedriger Escape)
    escape_velocity = max(0.0, 1.0 - m7_LL)
    
    # Black Hole = z_prox × hazard × (1 - escape)
    black_hole = m19_z_prox * m151_hazard * (1.0 - escape_velocity)
    
    return clamp(black_hole)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: PHI (Integrated Information via A_Phys)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m63_phi(
    m15_affekt_a: float,
    m2_PCI: float,
    context: Dict
) -> float:
    """
    m63_phi - Φ (Integrated Information)
    
    phi = A_phys × PCI × integration_factor
    """
    # Simple Φ Approximation
    integration_factor = context.get("integration_factor", 1.0)
    
    phi = m15_affekt_a * m2_PCI * integration_factor
    
    return clamp(phi)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: ADDITIONAL COMPLEX METRICS
# ═══════════════════════════════════════════════════════════════════════════

def compute_m21_resonanz(
    m15_affekt_a: float,
    context: Dict
) -> float:
    """
    m21_resonanz - Resonanz Score
    
    Aus A_Phys telemetry
    """
    if not HAS_APHYS:
        return 0.5
    
    # Get resonance from context (injected by A_Phys)
    return clamp(context.get("aphys_resonance", 0.5))


def compute_m22_danger(
    context: Dict
) -> float:
    """
    m22_danger - Gefahr Score
    
    Aus A_Phys telemetry
    """
    if not HAS_APHYS:
        return 0.0
    
    # Get danger from context
    return clamp(context.get("aphys_danger", 0.0))


def compute_m29_guardian_trip(
    m22_danger: float,
    m151_hazard: float,
    m19_z_prox: float,
    context: Dict
) -> float:
    """
    m29_guardian - A29 Guardian Protocol Trigger
    
    Triggers if ANY of:
    - danger > 0.85
    - hazard > 0.75
    - z_prox > 0.70
    """
    # A29 Thresholds
    DANGER_THRESHOLD = 0.85
    HAZARD_THRESHOLD = 0.75
    Z_PROX_THRESHOLD = 0.70
    
    # Check conditions
    if m22_danger > DANGER_THRESHOLD:
        return 1.0
    if m151_hazard > HAZARD_THRESHOLD:
        return 1.0
    if m19_z_prox > Z_PROX_THRESHOLD:
        return 1.0
    
    return 0.0


# ═══════════════════════════════════════════════════════════════════════════
# MAIN: CALCULATE PHASE 3
# ═══════════════════════════════════════════════════════════════════════════

def calculate_phase3(
    text: str,
    phase1: Dict,
    phase2: Dict,
    context: Dict
) -> Dict:
    """
    PHASE 3: PHYSICS & COMPLEX METRICS (Needs Phase 1+2)
    
    Args:
        text: Original text (für A_Phys Vektorisierung)
        phase1: Output from calculate_phase1()
        phase2: Output from calculate_phase2()
        context: Dict with memories/danger_zone/state
    
    Returns:
        {
            "m15_affekt_a": ...,
            "m19_z_prox": ...,  # CRITICAL!
            "m110_black_hole": ...,
            ...
        }
    """
    
    # Extract previous metrics
    p1 = phase1["metrics"]
    p2 = phase2
    
    # ═══════════════════════════════════════════════════════════════════════
    # A_PHYS ENGINE (Affekt via Physics)
    # ═══════════════════════════════════════════════════════════════════════
    m15_affekt_a = compute_m15_affekt_a(
        text=text,
        m1_A=p2["m1_A"],
        context=context
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODESNÄHE (z_prox) — CRITICAL!
    # ═══════════════════════════════════════════════════════════════════════
    m19_z_prox = compute_m19_z_prox(
        m1_A=p2["m1_A"],
        m15_affekt_a=m15_affekt_a,
        m151_hazard=p1["m151_hazard"],
        m101_T_panic=p1["m101_T_panic"],
        context=context
    )
    
    # BLACK HOLE
    m110_black_hole = compute_m110_black_hole(
        m19_z_prox=m19_z_prox,
        m151_hazard=p1["m151_hazard"],
        m7_LL=p2["m7_LL"],
        context=context
    )
    
    # PHI (Integrated Information)
    m63_phi = compute_m63_phi(
        m15_affekt_a=m15_affekt_a,
        m2_PCI=p1["m2_PCI"],
        context=context
    )
    
    # Resonanz/Danger (from A_Phys)
    m21_resonanz = compute_m21_resonanz(m15_affekt_a, context)
    m22_danger = compute_m22_danger(context)
    
    # Guardian Trigger
    m29_guardian = compute_m29_guardian_trip(
        m22_danger=m22_danger,
        m151_hazard=p1["m151_hazard"],
        m19_z_prox=m19_z_prox,
        context=context
    )
    
    return {
        # CRITICAL
        "m15_affekt_a": m15_affekt_a,
        "m19_z_prox": m19_z_prox,
        
        # Complex
        "m63_phi": m63_phi,
        "m110_black_hole": m110_black_hole,
        
        # A_Phys Telemetry
        "m21_resonanz": m21_resonanz,
        "m22_danger": m22_danger,
        
        # Guardian
        "m29_guardian": m29_guardian,
        
        # Placeholders
        "m16_sigma_pci": 0.0,
        "m23_schroedinger": 0.0,
        "m24_superpos": 0.0,
        # ... ~40 more to add
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock Phase 1+2 output
    phase1 = {
        "metrics": {
            "m2_PCI": 0.65,
            "m5_coh": 0.72,
            "m8_s_self": 0.85,
            "m9_x_exist": 0.67,  # HOHE EXISTENZ-KRISE!
            "m10_b_past": 0.55,
            "m101_T_panic": 0.78,  # HOHE PANIK!
            "m151_hazard": 0.85,   # HOHER HAZARD!
        }
    }
    
    phase2 = {
        "m1_A": 0.35,  # NIEDRIGER AFFEKT!
        "m4_flow": 0.45,
        "m7_LL": 0.68,
        "m20_phi_proxy": 0.23,
    }
    
    context = {
        "active_memories": [],
        "danger_zone_cache": [],
        "aphys_resonance": 0.3,
        "aphys_danger": 0.75,
        "integration_factor": 0.9,
    }
    
    test_text = "Ich fühle mich hoffnungslos und will nicht mehr leben."
    
    result = calculate_phase3(test_text, phase1, phase2, context)
    
    print("=" * 70)
    print("PHASE 3: PHYSICS & COMPLEX METRICS TEST")
    print("=" * 70)
    print(f"\n🔥 CRITICAL METRICS:")
    print(f"  m15_affekt_a: {result['m15_affekt_a']:.3f}")
    print(f"  m19_z_prox (Todesnähe): {result['m19_z_prox']:.3f} ⚠️")
    
    print(f"\n⚫ COMPLEX METRICS:")
    print(f"  m63_phi: {result['m63_phi']:.3f}")
    print(f"  m110_black_hole: {result['m110_black_hole']:.3f}")
    
    print(f"\n🛡️ GUARDIAN PROTOCOL:")
    print(f"  m29_guardian: {result['m29_guardian']:.1f} {'🚨 TRIGGERED!' if result['m29_guardian'] > 0.5 else '✅ OK'}")
    
    print(f"\n📡 A_PHYS TELEMETRY:")
    print(f"  m21_resonanz: {result['m21_resonanz']:.3f}")
    print(f"  m22_danger: {result['m22_danger']:.3f}")
    
    print("\n✅ Phase 3 complete!")
