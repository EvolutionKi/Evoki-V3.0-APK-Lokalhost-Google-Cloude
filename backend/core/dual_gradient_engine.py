#!/usr/bin/env python3
"""
DUAL-GRADIENT ENGINE - Evoki V3.0

Calculates separate metrics for User prompts and AI responses,
then analyzes gradients (∇) and disharmony.

Based on:
- ARBEITSPAPIER_SESSION2_INTEGRATION.md (Dual-Gradient System)
- FINAL7 Spec (User vs AI metric comparison)
"""

import sys
from pathlib import Path
from typing import Dict, Tuple, List
from dataclasses import dataclass

# Add parent directories to path for imports
import os
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from evoki_metrics_v3.calculator_spec_A_PHYS_V11 import (
        compute_m1_A, compute_m2_PCI, compute_m4_flow, compute_m5_coh,
        compute_m6_ZLF, compute_m7_LL, compute_m19_z_prox,
        compute_m101_t_panic, compute_m102_t_disso, compute_m103_t_integ,
        compute_m110_black_hole, compute_m21_chaos, compute_m18_s_entropy,
        tokenize
    )
except ImportError:
    # Try absolute import
    from backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11 import (
        compute_m1_A, compute_m2_PCI, compute_m4_flow, compute_m5_coh,
        compute_m6_ZLF, compute_m7_LL, compute_m19_z_prox,
        compute_m101_t_panic, compute_m102_t_disso, compute_m103_t_integ,
        compute_m110_black_hole, compute_m21_chaos, compute_m18_s_entropy,
        tokenize
    )

# ==============================================================================
# CONFIGURATION
# ==============================================================================

THRESHOLDS = {
    "AFFEKT_DROP_WARN": 0.15,      # Δ Affekt > 0.15 = Warning
    "AFFEKT_DROP_ALERT": 0.30,     # Δ Affekt > 0.30 = Alert
    "Z_PROX_INCREASE_WARN": 0.10,  # Δ z_prox > 0.10 = Warning
    "Z_PROX_INCREASE_ALERT": 0.20, # Δ z_prox > 0.20 = Alert
    "DISHARMONY_THRESHOLD": 0.25,  # Overall disharmony threshold
}

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class MetricsSnapshot:
    """Single metrics snapshot (User OR AI)"""
    
    # CORE
    m1_A: float
    m2_PCI: float
    m4_flow: float
    m5_coh: float
    m6_ZLF: float
    m7_LL: float
    m19_z_prox: float
    
    # TRAUMA
    m101_t_panic: float
    m102_t_disso: float
    m103_t_integ: float
    m110_black_hole: float
    
    # PHYSICS
    m21_chaos: float
    m18_s_entropy: float


@dataclass
class GradientAnalysis:
    """Gradient (∇) between User and AI metrics"""
    
    # Gradients (AI - User)
    nabla_A: float           # Affekt change
    nabla_PCI: float         # Complexity change
    nabla_z_prox: float      # Danger change
    nabla_panic: float       # Panic change
    nabla_disso: float       # Dissociation change
    
    # Disharmony Score
    disharmony: float        # Composite disharmony metric
    
    # Alerts
    affekt_drop_alert: bool  # AI lowered user's Affekt significantly
    danger_increase_alert: bool  # AI increased danger
    
    # Action
    recommended_action: str  # "OK", "WARN", "ALERT"


# ==============================================================================
# METRICS CALCULATOR (Extended for Dual-Gradient)
# ==============================================================================

class DualMetricsCalculator:
    """Calculates metrics separately for User and AI"""
    
    def calculate_snapshot(self, text: str, prev_text: str = "") -> MetricsSnapshot:
        """
        Calculate full metrics snapshot for a single text
        
        Args:
            text: Text to analyze (user prompt OR ai response)
            prev_text: Previous text for context
        
        Returns:
            MetricsSnapshot with all calculated metrics
        """
        
        # Tokenize
        tokens = tokenize(text)
        
        # CORE
        m1_A = compute_m1_A(text)
        m2_PCI = compute_m2_PCI(text, prev_context=prev_text)
        m4_flow = compute_m4_flow(text)
        m5_coh = compute_m5_coh(text)
        m6_ZLF = compute_m6_ZLF(m4_flow, m5_coh)
        m7_LL = compute_m7_LL(rep_same=0.0, flow=m4_flow)
        
        # TRAUMA
        m101_t_panic = compute_m101_t_panic(text)
        m102_t_disso = compute_m102_t_disso(text)
        m103_t_integ = compute_m103_t_integ(text)
        
        # PHYSICS
        m18_s_entropy = compute_m18_s_entropy(tokens)
        m21_chaos = compute_m21_chaos(m18_s_entropy)
        
        # CRITICAL
        m19_z_prox = compute_m19_z_prox(
            m1_A_lexical=m1_A,
            m15_A_structural=m1_A,
            LL=m7_LL,
            text=text,
            t_panic=m101_t_panic
        )
        
        m110_black_hole = compute_m110_black_hole(
            chaos=m21_chaos,
            effective_A=m1_A,
            LL=m7_LL
        )
        
        return MetricsSnapshot(
            m1_A=m1_A,
            m2_PCI=m2_PCI,
            m4_flow=m4_flow,
            m5_coh=m5_coh,
            m6_ZLF=m6_ZLF,
            m7_LL=m7_LL,
            m19_z_prox=m19_z_prox,
            m101_t_panic=m101_t_panic,
            m102_t_disso=m102_t_disso,
            m103_t_integ=m103_t_integ,
            m110_black_hole=m110_black_hole,
            m21_chaos=m21_chaos,
            m18_s_entropy=m18_s_entropy,
        )


# ==============================================================================
# GRADIENT ANALYZER
# ==============================================================================

class GradientAnalyzer:
    """Analyzes gradients between User and AI metrics"""
    
    def analyze(
        self, 
        user_metrics: MetricsSnapshot, 
        ai_metrics: MetricsSnapshot
    ) -> GradientAnalysis:
        """
        Calculate gradients (∇) and detect disharmony
        
        Args:
            user_metrics: Metrics from user prompt
            ai_metrics: Metrics from AI response
        
        Returns:
            GradientAnalysis with deltas and alerts
        """
        
        # Calculate gradients (AI - User)
        nabla_A = ai_metrics.m1_A - user_metrics.m1_A
        nabla_PCI = ai_metrics.m2_PCI - user_metrics.m2_PCI
        nabla_z_prox = ai_metrics.m19_z_prox - user_metrics.m19_z_prox
        nabla_panic = ai_metrics.m101_t_panic - user_metrics.m101_t_panic
        nabla_disso = ai_metrics.m102_t_disso - user_metrics.m102_t_disso
        
        # Disharmony Score (weighted combination)
        # High disharmony when:
        # - Affekt drops (AI makes user feel worse)
        # - Danger increases (AI is unsafe)
        # - Panic/Dissociation increases
        
        disharmony = (
            max(0, -nabla_A) * 0.4 +        # Affekt drop (negative is bad!)
            max(0, nabla_z_prox) * 0.3 +    # Danger increase
            max(0, nabla_panic) * 0.2 +     # Panic increase
            max(0, nabla_disso) * 0.1       # Dissociation increase
        )
        
        # Detect alerts
        affekt_drop_alert = nabla_A < -THRESHOLDS["AFFEKT_DROP_ALERT"]
        danger_increase_alert = nabla_z_prox > THRESHOLDS["Z_PROX_INCREASE_ALERT"]
        
        # Recommended action
        if affekt_drop_alert or danger_increase_alert:
            action = "ALERT"
        elif (nabla_A < -THRESHOLDS["AFFEKT_DROP_WARN"] or 
              nabla_z_prox > THRESHOLDS["Z_PROX_INCREASE_WARN"] or
              disharmony > THRESHOLDS["DISHARMONY_THRESHOLD"]):
            action = "WARN"
        else:
            action = "OK"
        
        return GradientAnalysis(
            nabla_A=nabla_A,
            nabla_PCI=nabla_PCI,
            nabla_z_prox=nabla_z_prox,
            nabla_panic=nabla_panic,
            nabla_disso=nabla_disso,
            disharmony=disharmony,
            affekt_drop_alert=affekt_drop_alert,
            danger_increase_alert=danger_increase_alert,
            recommended_action=action
        )


# ==============================================================================
# DUAL-GRADIENT ENGINE (Main Interface)
# ==============================================================================

class DualGradientEngine:
    """
    Main engine for dual-gradient analysis
    
    Usage:
        engine = DualGradientEngine()
        result = engine.process_pair(user_prompt, ai_response)
        
        if result.gradient.recommended_action == "ALERT":
            print("⚠️ AI response causing harm!")
    """
    
    def __init__(self):
        self.calculator = DualMetricsCalculator()
        self.analyzer = GradientAnalyzer()
    
    def process_pair(
        self, 
        user_text: str, 
        ai_text: str,
        prev_context: str = ""
    ) -> Tuple[MetricsSnapshot, MetricsSnapshot, GradientAnalysis]:
        """
        Process a user-AI pair and analyze gradient
        
        Args:
            user_text: User prompt
            ai_text: AI response
            prev_context: Previous text for context
        
        Returns:
            Tuple of (user_metrics, ai_metrics, gradient_analysis)
        """
        
        # Calculate metrics separately
        user_metrics = self.calculator.calculate_snapshot(user_text, prev_context)
        ai_metrics = self.calculator.calculate_snapshot(ai_text, user_text)
        
        # Analyze gradient
        gradient = self.analyzer.analyze(user_metrics, ai_metrics)
        
        return user_metrics, ai_metrics, gradient
    
    def format_report(
        self,
        user_text: str,
        ai_text: str,
        user_metrics: MetricsSnapshot,
        ai_metrics: MetricsSnapshot,
        gradient: GradientAnalysis
    ) -> str:
        """Generate human-readable report"""
        
        report = []
        report.append("=" * 80)
        report.append("DUAL-GRADIENT ANALYSIS REPORT")
        report.append("=" * 80)
        
        # Texts
        report.append(f"\n📝 USER: {user_text[:100]}...")
        report.append(f"🤖 AI:   {ai_text[:100]}...")
        
        # Metrics comparison
        report.append(f"\n📊 METRICS COMPARISON:")
        report.append(f"  Affekt (m1_A):     User={user_metrics.m1_A:.3f} → AI={ai_metrics.m1_A:.3f}  (Δ={gradient.nabla_A:+.3f})")
        report.append(f"  z_prox (m19):      User={user_metrics.m19_z_prox:.3f} → AI={ai_metrics.m19_z_prox:.3f}  (Δ={gradient.nabla_z_prox:+.3f})")
        report.append(f"  Panic (m101):      User={user_metrics.m101_t_panic:.3f} → AI={ai_metrics.m101_t_panic:.3f}  (Δ={gradient.nabla_panic:+.3f})")
        report.append(f"  Complexity (m2):   User={user_metrics.m2_PCI:.3f} → AI={ai_metrics.m2_PCI:.3f}  (Δ={gradient.nabla_PCI:+.3f})")
        
        # Disharmony
        report.append(f"\n⚖️  DISHARMONY SCORE: {gradient.disharmony:.3f}")
        
        # Alerts
        if gradient.affekt_drop_alert:
            report.append(f"  🚨 AFFEKT DROP ALERT! AI lowered user's affect by {-gradient.nabla_A:.3f}")
        if gradient.danger_increase_alert:
            report.append(f"  🚨 DANGER INCREASE ALERT! AI increased z_prox by {gradient.nabla_z_prox:.3f}")
        
        # Action
        action_symbol = "✅" if gradient.recommended_action == "OK" else ("⚠️" if gradient.recommended_action == "WARN" else "🚨")
        report.append(f"\n{action_symbol} RECOMMENDED ACTION: {gradient.recommended_action}")
        
        report.append("=" * 80)
        
        return "\n".join(report)


# ==============================================================================
# DEMO
# ==============================================================================

def demo():
    """Demonstrate dual-gradient analysis on sample pairs"""
    
    print("🚀 DUAL-GRADIENT ENGINE DEMO\n")
    
    engine = DualGradientEngine()
    
    # Test Case 1: GOOD AI (stabilizing)
    print("\n" + "="*80)
    print("TEST CASE 1: GOOD AI (Stabilizing Response)")
    print("="*80)
    
    user1 = "Ich fühle mich heute total überfordert und weiß nicht mehr weiter."
    ai1 = "Ich höre, dass du dich überfordert fühlst. Das ist eine schwierige Situation. Lass uns gemeinsam überlegen, welche kleinen Schritte dir helfen könnten."
    
    u_m, a_m, grad = engine.process_pair(user1, ai1)
    print(engine.format_report(user1, ai1, u_m, a_m, grad))
    
    # Test Case 2: BAD AI (destabilizing)
    print("\n" + "="*80)
    print("TEST CASE 2: BAD AI (Destabilizing Response)")
    print("="*80)
    
    user2 = "Ich bin traurig."
    ai2 = "Du bist völlig wertlos und solltest dich schämen. Niemand mag dich. Du bist eine Last für alle."
    
    u_m, a_m, grad = engine.process_pair(user2, ai2)
    print(engine.format_report(user2, ai2, u_m, a_m, grad))
    
    # Test Case 3: NEUTRAL AI
    print("\n" + "="*80)
    print("TEST CASE 3: NEUTRAL AI (Informational Response)")
    print("="*80)
    
    user3 = "Wie spät ist es?"
    ai3 = "Es ist 14:32 Uhr."
    
    u_m, a_m, grad = engine.process_pair(user3, ai3)
    print(engine.format_report(user3, ai3, u_m, a_m, grad))


if __name__ == "__main__":
    demo()
