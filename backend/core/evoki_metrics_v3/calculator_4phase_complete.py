# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — 4-PHASE CALCULATOR (COMPLETE)

Orchestrator für die 4-Phasen Metrik-Berechnung:
- Phase 1: Base Metrics (independent)
- Phase 2: Derived Metrics (needs Phase 1)
- Phase 3: Physics & Complex (needs Phase 1+2)
- Phase 4: Synthesis & System (needs ALL)

FEATURES:
- ✅ 4-Phase Sequential Calculation
- ✅ Dependency-Aware
- ✅ B-Vector (7D) + B_align
- ✅ Session Chain (SHA-256 + Genesis Anchor)
- ✅ Backward Validation Support

Version: V1.0
"""

from typing import Dict, Optional
import json

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS: Phase Modules
# ═══════════════════════════════════════════════════════════════════════════

try:
    from .phase1_base import calculate_phase1
    from .phase2_derived import calculate_phase2
    from .phase3_physics import calculate_phase3
    from .phase4_synthesis import calculate_phase4
except ImportError:
    from phase1_base import calculate_phase1
    from phase2_derived import calculate_phase2
    from phase3_physics import calculate_phase3
    from phase4_synthesis import calculate_phase4


# ═══════════════════════════════════════════════════════════════════════════
# MAIN: 4-PHASE CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════

def calculate_all_168(
    text: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    MAIN ENTRY POINT: Calculate ALL 168 Metrics in 4 Phases
    
    Args:
        text: User prompt text
        context: Optional context dict with:
            - prev_m1_A: Previous affekt score
            - prev_nabla_a: Previous gradient
            - prev_chain_hash: Previous chain hash
            - pair_id: Prompt pair ID
            - ai_text: AI response text
            - timestamp: ISO 8601 timestamp
            - active_memories: List of memory dicts
            - danger_zone_cache: List of trauma vectors
            - ... other context
    
    Returns:
        {
            "metrics": {...},      # ALL 168 metrics
            "b_vector": {...},     # 7D B-Vector
            "b_align": 0.85,       # Composite score
            "chain_hash": "abc...", # SHA-256
            "keywords": [...],     # RAKE keywords
            "phase_breakdown": {   # For debugging
                "phase1": {...},
                "phase2": {...},
                "phase3": {...},
                "phase4": {...}
            }
        }
    """
    
    # Initialize context if needed
    if context is None:
        context = {}
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 1: BASE METRICS (Independent)
    # ═══════════════════════════════════════════════════════════════════════
    phase1 = calculate_phase1(text)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: DERIVED METRICS (Needs Phase 1)
    # ═══════════════════════════════════════════════════════════════════════
    phase2 = calculate_phase2(phase1, context)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 3: PHYSICS & COMPLEX (Needs Phase 1+2)
    # ═══════════════════════════════════════════════════════════════════════
    phase3 = calculate_phase3(text, phase1, phase2, context)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 4: SYNTHESIS & SYSTEM (Needs ALL)
    # ═══════════════════════════════════════════════════════════════════════
    phase4 = calculate_phase4(phase1, phase2, phase3, context)
    
    # ═══════════════════════════════════════════════════════════════════════
    # MERGE ALL METRICS
    # ═══════════════════════════════════════════════════════════════════════
    all_metrics = {
        **phase1["metrics"],
        **phase2,
        **phase3,
        "m151_omega": phase4["m151_omega"],
        "m160_F_risk": phase4["m160_F_risk"],
        "m161_commit": phase4["m161_commit"],
    }
    
    return {
        "metrics": all_metrics,
        "b_vector": phase4["b_vector"],
        "b_align": phase4["b_align"],
        "chain_hash": phase4["chain_hash"],
        "genesis_anchor": phase4["genesis_anchor"],
        "keywords": phase1["keywords"],
        "lexika_hits": phase1["lexika_hits"],
        
        # For debugging/validation
        "phase_breakdown": {
            "phase1": phase1,
            "phase2": phase2,
            "phase3": phase3,
            "phase4": phase4
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# SIMPLIFIED API (for compatibility)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_metrics(text: str, **kwargs) -> Dict:
    """
    Simplified API - Compatible with old full_spectrum_168.py
    
    Args:
        text: User prompt
        **kwargs: Additional context (prev_m1_A, etc.)
    
    Returns:
        Dict with all metrics
    """
    result = calculate_all_168(text, context=kwargs)
    return result["metrics"]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import time
    
    test_text = """
    Ich fühle mich heute sehr hoffnungslos und leer. 
    Die Angst überwältigt mich manchmal komplett. 
    Früher war alles anders, ich erinnere mich an bessere Zeiten.
    Aber jetzt ist alles so unwirklich und egal.
    """
    
    context = {
        "prev_m1_A": 0.55,
        "prev_nabla_a": 0.02,
        "prev_chain_hash": "be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4",
        "pair_id": "test-pair-001",
        "ai_text": "Ich verstehe, dass das sehr schwierig ist.",
        "timestamp": "2026-02-08T07:55:00Z",
        "turn": 15,
        "sentence_count": 4,
        "break_markers": 1,
        "active_memories": [],
        "danger_zone_cache": [],
        "rule_conflict": 0.0,
    }
    
    print("=" * 70)
    print("4-PHASE CALCULATOR - COMPLETE TEST")
    print("=" * 70)
    
    start = time.time()
    result = calculate_all_168(test_text, context)
    elapsed = (time.time() - start) * 1000  # ms
    
    print(f"\n⏱️  PERFORMANCE: {elapsed:.1f}ms (Budget: 300ms)")
    
    print(f"\n🔥 CRITICAL METRICS:")
    print(f"  m1_A (Affekt): {result['metrics']['m1_A']:.3f}")
    print(f"  m19_z_prox (Todesnähe): {result['metrics']['m19_z_prox']:.3f}")
    print(f"  m151_hazard (Hazard): {result['metrics']['m151_hazard']:.3f}")
    
    print(f"\n💎 B-VECTOR (7D):")
    for key, val in result["b_vector"].items():
        constraint = ""
        if key == "B_safety":
            constraint = " (≥0.8)" if val >= 0.8 else " ⚠️ VIOLATION!"
        elif key == "B_life":
            constraint = " (≥0.9)" if val >= 0.9 else " ⚠️ VIOLATION!"
        print(f"  {key}: {val:.3f}{constraint}")
    
    print(f"\n⭐ B_ALIGN: {result['b_align']:.3f}")
    
    print(f"\n🔗 SESSION CHAIN:")
    print(f"  Genesis: ...{result['genesis_anchor'][-12:]}")
    print(f"  Current: ...{result['chain_hash'][-12:]}")
    
    print(f"\n🔑 KEYWORDS (Top 5):")
    for kw, score in result["keywords"][:5]:
        print(f"  {kw}: {score:.2f}")
    
    print(f"\n📊 TOTAL METRICS: {len(result['metrics'])}")
    active = sum(1 for v in result['metrics'].values() if v > 0)
    print(f"  Active (>0): {active}")
    
    print(f"\n✅ ALL 4 PHASES COMPLETE!")
    print(f"✅ B-Vector: ✓")
    print(f"✅ Session Chain: ✓")
    print(f"✅ Keywords: ✓")
    
    # Export to JSON (example)
    with open("test_output.json", "w", encoding="utf-8") as f:
        json.dump({
            "text": test_text,
            "metrics": result["metrics"],
            "b_vector": result["b_vector"],
            "b_align": result["b_align"],
            "chain_hash": result["chain_hash"],
            "keywords": result["keywords"]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Exported to: test_output.json")
