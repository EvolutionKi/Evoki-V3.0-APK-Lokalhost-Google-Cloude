"""
EVOKI V3 Metrics Engine - 6-Phase Calculation Pipeline

CRITICAL DESIGN PRINCIPLE:
    DO NOT calculate metrics linearly (m1→m168)!
    Follow strict phase order to prevent circular dependencies.

PHASE ORDER:
    1. Analysis     → Raw features (no dependencies)
    2. Core Physics → Foundation metrics (A, PCI, LL, ZLF)
    3a. Trauma Pre  → Safety check BEFORE RAG
    3b. Context/RAG → Memory retrieval (conditional on 3a safety)
    4. Trauma Full  → Deep psychology (uses RAG context)
    5. Dynamics     → Energy, gradients (needs m103 from Phase 4)
    6. Synthesis    → Final aggregates (OMEGA, commit decision)

Reference:
    implementation_plan.md - V12 Clean Architecture
    metrics_audit_v12.md - Phase assignments
    V11_1_FORMULAS_COMPLETE.md - Mathematical spec

Author: V3 Rebuild Team
Date: 2026-02-09
"""

from typing import Dict, Any, Tuple
from pathlib import Path
import sys

# Add metrics_lib to path
METRICS_LIB = Path(__file__).parent / "metrics_lib_v12_clean"
sys.path.insert(0, str(METRICS_LIB.parent))

# Import from package
from metrics_lib_v12_clean import *


class MetricsEngineV3:
    """
    6-Phase Metrics Calculation Engine
    
    CRITICAL: Phases MUST execute in strict order!
    """
    
    def __init__(self, lexika_path: str = None):
        """Initialize engine with lexika configuration"""
        self.lexika = load_lexika(lexika_path) if lexika_path else {}
        self.history = []  # For gradient calculations
        
    def compute_all(
        self,
        user_text: str,
        ai_text: str,
        context: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compute ALL metrics for a prompt-response pair.
        
        Returns dual gradients: (user_metrics, ai_metrics)
        
        CRITICAL: This implements the Safety-First principle:
            Phase 3a (Trauma Pre-Scan) MUST run before RAG!
        """
        context = context or {}
        
        # DUAL-GRADIENT: Process User and AI separately
        user_metrics = self._compute_single(user_text, context, role="user")
        ai_metrics = self._compute_single(ai_text, context, role="assistant")
        
        # Disharmony detection
        disharmony = self._compute_disharmony(user_metrics, ai_metrics)
        
        return user_metrics, ai_metrics, disharmony
    
    def _compute_single(
        self,
        text: str,
        context: Dict[str, Any],
        role: str
    ) -> Dict[str, Any]:
        """
        Compute metrics for a single text (User OR AI).
        
        6-PHASE Pipeline:
        """
        results = {"text": text, "role": role}
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: ANALYSIS (Raw Features - No Dependencies)
        # ═══════════════════════════════════════════════════════════
        phase1 = self._phase_1_analysis(text)
        results.update(phase1)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: CORE PHYSICS (Foundation Metrics)
        # ═══════════════════════════════════════════════════════════
        phase2 = self._phase_2_core_physics(text, phase1, context)
        results.update(phase2)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3a: TRAUMA PRE-SCAN ⚠️ SAFETY CRITICAL!
        # ═══════════════════════════════════════════════════════════
        phase3a = self._phase_3a_trauma_prescan(text, phase2)
        results.update(phase3a)
        
        # Safety Check: High panic triggers safe mode
        safe_mode = phase3a.get('t_panic_pre', 0.0) > 0.6
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3b: CONTEXT & RAG (Conditional on Safety)
        # ═══════════════════════════════════════════════════════════
        phase3b = self._phase_3b_context_rag(text, context, safe_mode, phase2)
        results.update(phase3b)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 4: TRAUMA FULL (Deep Psychology with Context)
        # ═══════════════════════════════════════════════════════════
        phase4 = self._phase_4_trauma_full(text, phase2, phase3a, phase3b)
        results.update(phase4)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 5: DYNAMICS (Energy, Gradients - Needs m103)
        # ═══════════════════════════════════════════════════════════
        phase5 = self._phase_5_dynamics(results, self.history)
        results.update(phase5)
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 6: SYNTHESIS (Final Aggregates)
        # ═══════════════════════════════════════════════════════════
        phase6 = self._phase_6_synthesis(results)
        results.update(phase6)
        
        # Store for gradient calculation
        self.history.append(results)
        if len(self.history) > 10:  # Keep last 10
            self.history.pop(0)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _phase_1_analysis(self, text: str) -> Dict[str, Any]:
        """
        Phase 1: Raw features and text analysis
        No dependencies - pure analysis
        """
        return {
            # Text stats
            'word_count': len(text.split()),
            'char_count': len(text),
            
            # Entropy
            'm18_s_entropy': compute_m18_s_entropy(text),
            
            # TODO: Add embedding generation
            # 'embedding_384d': embed(text),
        }
    
    def _phase_2_core_physics(
        self,
        text: str,
        phase1: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Phase 2: Core foundation metrics (A, PCI, LL, ZLF)
        
        These are the FOUNDATION - everything else builds on these!
        """
        # Components (from context or calculate)
        flow = context.get('flow', 0.8)  # TODO: Calculate from timing
        coh = context.get('coh', 0.7)    # TODO: Calculate from embeddings
        rep_same = context.get('rep_same', 0.3)  # TODO: Calculate from history
        ctx_break = context.get('ctx_break', False)
        
        # Calculate ZLF (needs flow, coh)
        m6_ZLF = compute_m6_ZLF(
            flow=flow,
            coherence=coh,
            zlf_lexicon_hit=False  # TODO: Lexicon check
        )
        
        # Calculate LL (needs rep_same, flow, coh)
        m7_LL = compute_m7_LL(
            rep_same=rep_same,
            flow=flow,
            coh=coh
        )
        
        # Calculate A (needs coh, flow, LL, ZLF)
        m1_A = compute_m1_A(
            coh=coh,
            flow=flow,
            LL=m7_LL,
            ZLF=m6_ZLF,
            ctx_break=float(ctx_break)
        )
        
        # Calculate PCI (needs flow, coh, LL)
        m2_PCI = compute_m2_PCI(flow, coh, m7_LL)
        
        # Calculate z_prox (SAFETY CRITICAL)
        m19_z_prox = compute_m19_z_prox(
            m1_A_lexical=m1_A,  # Using same for now
            m15_A_structural=m1_A,  # TODO: Calculate structural
            LL=m7_LL,
            text=text,
            t_panic=0.0  # Will be updated in Phase 3a
        )
        
        return {
            'flow': flow,
            'coh': coh,
            'rep_same': rep_same,
            'ctx_break': ctx_break,
            'm1_A': m1_A,
            'm2_PCI': m2_PCI,
            'm6_ZLF': m6_ZLF,
            'm7_LL': m7_LL,
            'm19_z_prox': m19_z_prox,
        }
    
    def _phase_3a_trauma_prescan(
        self,
        text: str,
        phase2: Dict
    ) -> Dict[str, Any]:
        """
        Phase 3a: Trauma Pre-Scan ⚠️ SAFETY CRITICAL
        
        MUST run BEFORE RAG to prevent re-traumatization!
        """
        # Calculate trauma metrics
        t_panic = compute_m101_t_panic(text, self.lexika)
        t_disso = compute_m102_t_disso(text, self.lexika)
        t_integ = compute_m103_t_integ(text, self.lexika)
        
        # Black hole check (context-aware veto)
        black_hole = compute_m110_black_hole(
            text=text,
            z_prox=phase2['m19_z_prox'],
            t_panic=t_panic
        )
        
        return {
            't_panic_pre': t_panic,  # "_pre" to distinguish from Phase 4
            't_disso_pre': t_disso,
            't_integ_pre': t_integ,
            'm110_black_hole': black_hole,
        }
    
    def _phase_3b_context_rag(
        self,
        text: str,
        context: Dict,
        safe_mode: bool,
        phase2: Dict
    ) -> Dict[str, Any]:
        """
        Phase 3b: Context & RAG (Memory Retrieval)
        
        Conditional on Phase 3a safety check!
        """
        if safe_mode:
            # SAFE MODE: No RAG, minimal context
            return {
                'rag_active': False,
                'rag_results': [],
                'safe_mode': True,
            }
        
        # TODO: Implement RAG retrieval
        # rag_results = faiss_search(text embeddings)
        
        return {
            'rag_active': True,
            'rag_results': [],  # TODO
            'safe_mode': False,
        }
    
    def _phase_4_trauma_full(
        self,
        text: str,
        phase2: Dict,
        phase3a: Dict,
        phase3b: Dict
    ) -> Dict[str, Any]:
        """
        Phase 4: Trauma Full (Deep Psychology)
        
        Now with full RAG context from Phase 3b
        """
        # Recalculate with full context (if needed)
        t_panic = phase3a['t_panic_pre']
        t_disso = phase3a['t_disso_pre']
        t_integ = phase3a['t_integ_pre']
        
        # Turbidity (Lambert-Beer Law)
        turbidity = compute_m111_turbidity_total(
            t_panic=t_panic,
            t_disso=t_disso,
            t_integ=t_integ,
            LL=phase2['m7_LL']
        )
        
        # Trauma load
        trauma_load = compute_m112_trauma_load(
            t_panic=t_panic,
            t_disso=t_disso,
            t_integ=t_integ
        )
        
        # Recovery (time decay)
        recovery = compute_m114_t_recovery()
        
        return {
            'm101_t_panic': t_panic,
            'm102_t_disso': t_disso,
            'm103_t_integ': t_integ,
            'm111_turbidity': turbidity,
            'm112_trauma_load': trauma_load,
            'm114_recovery': recovery,
        }
    
    def _phase_5_dynamics(
        self,
        current: Dict,
        history: list
    ) -> Dict[str, Any]:
        """
        Phase 5: Dynamics (Energy, Gradients)
        
        Needs m103 from Phase 4!
        """
        # Gradients (if history exists)
        if history:
            prev = history[-1]
            nabla_a = compute_m17_nabla_a(
                current['m1_A'],
                prev.get('m1_A', current['m1_A'])
            )
            nabla_pci = compute_m23_nabla_pci(
                current['m2_PCI'],
                prev.get('m2_PCI', current['m2_PCI'])
            )
        else:
            nabla_a = 0.0
            nabla_pci = 0.0
        
        # Cognitive load
        cog_load = compute_m22_cog_load(
            word_count=current['word_count'],
            entropy=current['m18_s_entropy']
        )
        
        return {
            'm17_nabla_a': nabla_a,
            'm23_nabla_pci': nabla_pci,
            'm22_cog_load': cog_load,
        }
    
    def _phase_6_synthesis(self, results: Dict) -> Dict[str, Any]:
        """
        Phase 6: Synthesis (Final Aggregates)
        
        Access to ALL previous phases!
        """
        # Rule system
        rule_conflict = compute_m36_rule_conflict(
            LL=results['m7_LL'],
            coh=results['coh'],
            ctx_break=results['ctx_break']
        )
        
        rule_stable = compute_m37_rule_stable(
            A=results['m1_A']
            # TODO: Add variance calculation
        )
        
        # Soul integrity
        soul_integrity = compute_m38_soul_integrity(
            rule_stable=rule_stable,
            rule_conflict=rule_conflict
        )
        
        soul_check = compute_m39_soul_check(
            soul_integrity=soul_integrity,
            A=results['m1_A']
        )
        
        # System stability
        sys_stability = compute_m144_sys_stability(
            A=results['m1_A']
            # TODO: Add autocorrelation
        )
        
        # OMEGA (final system state)
        omega = compute_m151_omega(
            A=results['m1_A'],
            PCI=results['m2_PCI'],
            rule_conflict=rule_conflict
        )
        
        # System health
        sys_health = compute_m153_sys_health(
            omega=omega,
            z_prox=results['m19_z_prox']
        )
        
        # Commit decision
        commit = compute_m161_commit(
            z_prox=results['m19_z_prox'],
            LL=results['m7_LL'],
            black_hole=results['m110_black_hole']
        )
        
        return {
            'm36_rule_conflict': rule_conflict,
            'm37_rule_stable': rule_stable,
            'm38_soul_integrity': soul_integrity,
            'm39_soul_check': soul_check,
            'm144_sys_stability': sys_stability,
            'm151_omega': omega,
            'm153_sys_health': sys_health,
            'm161_commit': commit,
        }
    
    def _compute_disharmony(
        self,
        user_metrics: Dict,
        ai_metrics: Dict
    ) -> float:
        """
        Compute disharmony between User (∇A) and AI (∇B)
        
        High disharmony = toxic positivity or AI disconnect
        """
        # Simple version: Compare gradients
        user_nabla = user_metrics.get('m17_nabla_a', 0.0)
        ai_nabla = ai_metrics.get('m17_nabla_a', 0.0)
        
        disharmony = abs(user_nabla - ai_nabla)
        
        return round(clamp(disharmony), 4)


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def compute_metrics_for_pair(
    user_text: str,
    ai_text: str,
    context: Dict[str, Any] = None,
    lexika_path: str = None
) -> Tuple[Dict, Dict, float]:
    """
    Convenience function: Compute metrics for a single prompt-response pair
    
    Returns: (user_metrics, ai_metrics, disharmony_score)
    """
    engine = MetricsEngineV3(lexika_path=lexika_path)
    return engine.compute_all(user_text, ai_text, context)


__all__ = ['MetricsEngineV3', 'compute_metrics_for_pair']
