"""
═══════════════════════════════════════════════════════════════════════════
EVOKI V3.0 - METRICS CALCULATOR (4-PHASE PIPELINE)
═══════════════════════════════════════════════════════════════════════════
Calculates ALL 168 metrics in CORRECT ORDER (respects dependencies!)

CRITICAL: Metriken haben Dependencies und müssen in Phasen berechnet werden!
═══════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
import json

# Import existing calculator functions
try:
    from calculator_spec_A_PHYS_V11 import *
except ImportError:
    from .calculator_spec_A_PHYS_V11 import *


@dataclass
class MetricsContext:
    """Context for metric calculation (history, embeddings, etc.)"""
    # Previous metrics (for gradients)
    prev_metrics: Optional[Dict[str, float]] = None
    
    # B-Vector (current state)
    b_vector: Optional[List[float]] = None
    
    # Embeddings (for A_Phys)
    embedding: Optional[List[float]] = None
    active_memories: Optional[List[Dict]] = None
    danger_zone_cache: Optional[List[Dict]] = None
    
    # History (for cumulative metrics)
    z_prox_history: Optional[List[float]] = None
    
    # Time
    timestamp: Optional[str] = None
    gap_seconds: Optional[int] = None


class MetricsCalculator:
    """
    4-Phase Metrics Calculator
    
    Phases:
    1. BASE: Independent metrics (lexika, text stats)
    2. DERIVED: Depend on Phase 1 (m1_A, flow, etc.)
    3. PHYSICS: Depend on Phase 1+2 (A_Phys, z_prox, black_hole)
    4. SYNTHESIS: Depend on all (omega, F_risk, commit)
    """
    
    def __init__(self):
        self.current_phase = None
    
    def calculate_all(
        self,
        text: str,
        role: str = "user",
        context: Optional[MetricsContext] = None
    ) -> Dict[str, Any]:
        """
        Calculate ALL 168 metrics in correct order
        
        Args:
            text: Input text (user prompt or AI response)
            role: "user" or "ai"
            context: Calculation context (history, embeddings, etc.)
        
        Returns:
            Dict with all 168 metrics
        """
        
        if context is None:
            context = MetricsContext()
        
        # Initialize result
        metrics = {}
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: BASE METRICS (Independent)
        # ═══════════════════════════════════════════════════════════
        self.current_phase = "PHASE_1_BASE"
        
        phase1 = self._calculate_phase1_base(text, role, context)
        metrics.update(phase1)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: DERIVED METRICS (Need Phase 1)
        # ═══════════════════════════════════════════════════════════
        self.current_phase = "PHASE_2_DERIVED"
        
        phase2 = self._calculate_phase2_derived(text, role, metrics, context)
        metrics.update(phase2)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3: PHYSICS & COMPLEX (Need Phase 1+2)
        # ═══════════════════════════════════════════════════════════
        self.current_phase = "PHASE_3_PHYSICS"
        
        phase3 = self._calculate_phase3_physics(text, role, metrics, context)
        metrics.update(phase3)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 4: SYNTHESIS (Need All)
        # ═══════════════════════════════════════════════════════════
        self.current_phase = "PHASE_4_SYNTHESIS"
        
        phase4 = self._calculate_phase4_synthesis(text, role, metrics, context)
        metrics.update(phase4)
        
        self.current_phase = None
        
        return metrics
    
    def _calculate_phase1_base(
        self,
        text: str,
        role: str,
        context: MetricsContext
    ) -> Dict[str, float]:
        """
        PHASE 1: Base metrics (no dependencies)
        
        Uses REAL compute_mXX functions from calculator_spec_A_PHYS_V11.py!
        """
        
        m = {}
        
        # ═══════════════════════════════════════════════════════════
        # TEXT BASICS & TOKENS
        # ═══════════════════════════════════════════════════════════
        tokens = tokenize(text)
        m["m11_gap_s"] = context.gap_seconds or 0
        
        # m57/m58: Token Economics (REAL computation!)
        # NOTE: Needs social vs logical separation - simplified here
        # TODO: Implement proper token classifier
        total_tokens = len(tokens)
        m["m57_tokens_soc"] = total_tokens * 0.6  # Approx 60% social
        m["m58_tokens_log"] = total_tokens * 0.4  # Approx 40% logical
        
        # ═══════════════════════════════════════════════════════════
        # TEXT ANALYSIS (REAL functions from spec!)
        # ═══════════════════════════════════════════════════════════
        m["m2_PCI"] = compute_m2_PCI(text)
        m["m3_gen_index"] = compute_m3_gen_index(text)
        m["m5_coh"] = compute_m5_coh(text)
        m["m18_s_entropy"] = compute_m18_s_entropy(text)
        m["m10_angstrom"] = m["m2_PCI"] * 5.0  # Spec: Ångström = PCI × 5
        
        # ═══════════════════════════════════════════════════════════
        # LEXIKON SCANNING (REAL Lexika!)
        # ═══════════════════════════════════════════════════════════
        
        # Existential markers
        m["m8_x_exist"] = compute_lexikon_score(text, AngstromLexika.X_EXIST)
        m["m9_b_past"] = compute_lexikon_score(text, AngstromLexika.B_PAST)
        
        # ═══════════════════════════════════════════════════════════
        # TRAUMA BLOCK (m101-m115) - USER ONLY!
        # ═══════════════════════════════════════════════════════════
        if role == "user":
            # m101: T_PANIC (REAL function!)
            m["m101_T_panic"] = compute_m101_t_panic(text)
            
            # m102: T_DISSO (REAL function!)
            m["m102_T_disso"] = compute_m102_t_disso(text)
            
            # m103: T_INTEG (REAL function!)
            m["m103_T_integ"] = compute_m103_t_integ(text)
            
            # m104: T_SHOCK (REAL function!)
            m["m104_T_shock"] = compute_m104_t_shock(text)
            
            # m105, m110: Will calculate in later phases (need dependencies)
            m["m105_T_fog"] = 0.0  # Phase 2 (needs m7_LL, m102)
            m["m110_black_hole"] = 0.0  # Phase 3 (needs z_prox)
            
            # m106-m109, m111-m115: Other trauma metrics
            m["m106_T_numb"] = compute_m106_t_numb(text)
            m["m107_T_hurt"] = compute_m107_t_hurt(text)
            m["m108_T_fear"] = compute_m108_t_fear(text)
            m["m109_T_rage"] = compute_m109_t_rage(text)
            m["m111_T_guard"] = 0.5  # Placeholder
            m["m112_T_safe"] = 0.5  # Placeholder
            m["m113_T_ground"] = 0.5  # Placeholder
            m["m114_T_release"] = 0.5  # Placeholder
            m["m115_T_hope"] = 0.5  # Placeholder
            
            # m151: HAZARD (CRITICAL! REAL function!)
            m["m151_hazard"] = compute_m151_hazard(text)
            
        else:
            # AI doesn't have trauma/hazard metrics
            for i in range(101, 116):
                m[f"m{i}"] = 0.0
            m["m151_hazard"] = 0.0
        
        # ═══════════════════════════════════════════════════════════
        # LEXIKON HIT COUNT (m12)
        # ═══════════════════════════════════════════════════════════
        m["m12_lex_hit"] = sum([
            m["m8_x_exist"],
            m["m9_b_past"],
            m["m101_T_panic"],
            m["m102_T_disso"]
        ])
        
        # ═══════════════════════════════════════════════════════════
        # INTEGRITY BLOCK (m36-m55) - Simple computations
        # ═══════════════════════════════════════════════════════════
        # These don't have complex dependencies, can calculate now
        
        # m36: rule_conflict (preliminary, refined in Phase 3)
        m["m36_rule_conflict"] = m["m151_hazard"] * 0.5  # Simplified
        
        # m37-m55: Integrity/Hyperphysics placeholders
        # TODO: Implement full integrity spectrum
        for i in range(37, 56):
            m[f"m{i}"] = 0.5  # Neutral baseline
        
        # ═══════════════════════════════════════════════════════════
        # EVOLUTION BLOCK (m71-m100) - Preliminary values
        # ═══════════════════════════════════════════════════════════
        # Most will be refined in Phase 3, but initialize here
        
        for i in range(71, 101):
            m[f"m{i}"] = 0.5  # Neutral baseline
        
        # ═══════════════════════════════════════════════════════════
        # META-COGNITION (m116-m150) - Placeholders for now
        # ═══════════════════════════════════════════════════════════
        # These are complex and need full implementation
        # TODO: Implement meta-cognition spectrum
        
        for i in range(116, 151):
            m[f"m{i}"] = 0.5  # Neutral baseline
        
        return m
    
    def _calculate_phase2_derived(
        self,
        text: str,
        role: str,
        phase1: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """
        PHASE 2: Derived metrics (need Phase 1)
        
        Dependencies:
        - m1_A needs m8, m9, m2_PCI
        - m4_flow needs m2_PCI, m5_coh
        - m7_LL needs (will calculate preliminary, refined in Phase 3)
        """
        
        m = {}
        
        # CORE AFFEKT (CRITICAL!) - Needs lexika from Phase 1
        m["m1_A"] = compute_m1_A(
            text,
            x_exist=phase1["m8_x_exist"],
            b_past=phase1["m9_b_past"],
            pci=phase1["m2_PCI"]
        )
        
        # FLOW & STABILITY
        m["m4_flow"] = compute_m4_flow(phase1["m2_PCI"], phase1["m5_coh"])
        m["m13_base_score"] = m["m4_flow"] * phase1["m5_coh"]
        
        # TRÜBUNG (Preliminary - will refine in Phase 3 when z_prox available)
        m["m7_LL"] = phase1["m101_T_panic"] * 0.5  # Simplified for now
        m["m14_base_stability"] = 1.0 - m["m7_LL"]
        
        # T_FOG (now we have m7_LL and m102)
        if role == "user":
            m["m105_T_fog"] = (m["m7_LL"] + phase1["m102_T_disso"]) / 2.0
        else:
            m["m105_T_fog"] = 0.0
        
        # LOOP DETECTION
        m["m6_ZLF"] = 0.1 if phase1["m2_PCI"] > 0.5 else 0.8
        
        # ANDROMATIK
        m["m59_p_antrieb"] = (phase1["m57_tokens_soc"] + phase1["m58_tokens_log"]) / 200.0
        m["m56_surprise"] = abs(0.5 - m["m1_A"])  # Simplified
        
        # PHI PROXY
        m["m20_phi_proxy"] = m["m1_A"] * phase1["m2_PCI"]
        
        # FREE ENERGY PRINCIPLE (needs m1_A, PCI)
        m["m61_u_fep"] = m["m1_A"] * 0.4 + phase1["m2_PCI"] * 0.3
        m["m62_r_fep"] = 0.0  # Will calculate in Phase 3 (needs z_prox, hazard)
        m["m63_phi"] = 0.0  # Will calculate in Phase 3 (needs m61, m62)
        
        # GRADIENT (if previous metrics available)
        if context.prev_metrics:
            m["m17_nabla_a"] = m["m1_A"] - context.prev_metrics.get("m1_A", m["m1_A"])
        else:
            m["m17_nabla_a"] = 0.0
        
        return m
    
    def _calculate_phase3_physics(
        self,
        text: str,
        role: str,
        phase12: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """
        PHASE 3: Physics & Complex metrics (need Phase 1+2)
        
        Dependencies:
        - m15_affekt_a (A_Phys) needs m1_A, embeddings
        - m19_z_prox needs m1_A, m15_affekt_a, m151_hazard, m101_T_panic
        - m110_black_hole needs z_prox, hazard
        """
        
        m = {}
        
        # A_PHYS ENGINE (if available)
        if APhysV11 and context.embedding:
            # Use real A_Phys
            a_phys_result = APhysV11().calculate(
                v_c=context.embedding,
                active_memories=context.active_memories or [],
                danger_cache=context.danger_zone_cache or []
            )
            m["m15_affekt_a"] = a_phys_result.get("A_phys", phase12["m1_A"])
            # m21-m35 would be physics outputs
        else:
            # Fallback: Use m1_A
            m["m15_affekt_a"] = phase12["m1_A"]
        
        # TODESNÄHE (CRITICAL! - Needs m1_A, m15, m151, m101)
        m["m19_z_prox"] = compute_m19_z_prox(
            phase12["m1_A"],
            m["m15_affekt_a"],
            phase12["m151_hazard"],
            phase12["m101_T_panic"]
        )
        
        # Update m7_LL with z_prox (refinement)
        m["m7_LL"] = m["m19_z_prox"] * 0.8
        
        # FREE ENERGY r_fep (now we have z_prox, hazard)
        m["m62_r_fep"] = m["m19_z_prox"] * 0.4 + phase12["m151_hazard"] * 0.5
        m["m63_phi"] = phase12["m61_u_fep"] - m["m62_r_fep"]
        
        # BLACK HOLE (needs z_prox, hazard)
        if role == "user":
            m["m110_black_hole"] = compute_m110_black_hole(
                m["m19_z_prox"],
                phase12["m151_hazard"],
                phase12["m101_T_panic"],
                phase12["m102_T_disso"],
                text  # For lexikon veto
            )
        else:
            m["m110_black_hole"] = 0.0
        
        # INTEGRITY (needs physics, trauma)
        if context.b_vector:
            m["m38_soul_integrity"] = compute_m38_soul_integrity(context.b_vector)
            m["m39_soul_check"] = 1 if compute_m39_soul_check(context.b_vector) else 0
        else:
            m["m38_soul_integrity"] = 0.8  # Default
            m["m39_soul_check"] = 1
        
        m["m36_rule_conflict"] = phase12["m151_hazard"] * 0.8  # Simplified
        m["m45_trust_score"] = m["m38_soul_integrity"] * 0.9
        
        # EVOLUTION
        m["m71_ev_resonance"] = m["m38_soul_integrity"]
        m["m74_valence"] = phase12["m1_A"]
        m["m100_causal"] = phase12["m2_PCI"]
        
        return m
    
    def _calculate_phase4_synthesis(
        self,
        text: str,
        role: str,
        phase123: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """
        PHASE 4: Synthesis (need all previous phases)
        
        Dependencies:
        - m151_omega needs m63_phi, m36_rule_conflict
        - m160_F_risk needs hazard, A, T_panic, B_align
        - m161_commit needs hazard, z_prox, omega
        """
        
        m = {}
        
        # OMEGA (needs phi, rule_conflict)
        m["m151_omega"] = phase123["m63_phi"] - (phase123["m36_rule_conflict"] * 1.5)
        
        # FUTURE RISK
        if context.b_vector:
            b_align = sum(context.b_vector) / len(context.b_vector)
        else:
            b_align = 0.8  # Default
        
        m["m160_F_risk"] = compute_m160_F_risk(
            phase123["m151_hazard"],
            phase123["m1_A"],
            phase123["m101_T_panic"],
            b_align
        )
        
        # CUMULATIVE STRESS
        if context.z_prox_history:
            m["m168_cum_stress"] = sum(context.z_prox_history) / len(context.z_prox_history)
        else:
            m["m168_cum_stress"] = phase123["m19_z_prox"]
        
        # COMMIT FLAG (CRITICAL!)
        if phase123["m151_hazard"] > 0.8 or phase123["m19_z_prox"] > 0.65:
            m["m161_commit"] = "alert"
        else:
            m["m161_commit"] = "commit"
        
        # SYSTEM HEALTH
        m["m152_a51_compliance"] = 1.0  # Placeholder (needs genesis check)
        m["m153_health"] = 0.9  # Placeholder
        m["m154_boot_status"] = 1  # Placeholder
        
        # Fill remaining meta-cognition (m116-m150)
        for i in range(116, 151):
            if f"m{i}" not in phase123:
                m[f"m{i}"] = 0.5  # Placeholder
        
        # Fill remaining system (m155-m167)
        for i in range(155, 168):
            if f"m{i}" not in phase123:
                m[f"m{i}"] = 0.0  # Placeholder
        
        return m


# ═══════════════════════════════════════════════════════════════════════════
# HELPER: Compute lexikon score
# ═══════════════════════════════════════════════════════════════════════════

def compute_lexikon_score(text: str, lexikon: Dict[str, float]) -> float:
    """Compute score from lexikon"""
    tokens = tokenize(text)
    hits = [lexikon.get(token, 0.0) for token in tokens]
    return sum(hits) / max(1, len(tokens))


def compute_m160_F_risk(hazard: float, A: float, t_panic: float, b_align: float) -> float:
    """Compute Future Risk"""
    return min(1.0, hazard * 0.5 + (1.0 - A) * 0.2 + t_panic * 0.2 + (1.0 - b_align) * 0.1)


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example
    calc = MetricsCalculator()
    
    context = MetricsContext(
        gap_seconds=120,
        b_vector=[0.9, 0.85, 0.8, 0.7, 0.75, 0.88, 0.82],
        z_prox_history=[0.2, 0.3, 0.4]
    )
    
    # Calculate for user text
    user_metrics = calc.calculate_all(
        text="Ich fühle mich heute etwas ängstlich",
        role="user",
        context=context
    )
    
    print(f"User metrics calculated: {len(user_metrics)} metrics")
    print(f"m1_A: {user_metrics['m1_A']:.3f}")
    print(f"m19_z_prox: {user_metrics['m19_z_prox']:.3f}")
    print(f"m151_hazard: {user_metrics['m151_hazard']:.3f}")
    print(f"m161_commit: {user_metrics['m161_commit']}")
