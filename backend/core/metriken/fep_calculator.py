#!/usr/bin/env python3
"""
EVOKI FREE ENERGY PRINCIPLE (FEP) METRIKEN
==========================================
Operationalisierung des FEP nach Andromatik V11.1

FEP-Konzept → Evoki-Metrik:
- Überraschung/Entropie → FE_proxy, S_entropy  
- Homöostase → A (Aggregat-Kohärenz), Soul-Integrität
- EFE-Bewertung → Phi-Score (U - λR)
- Policy-Auswahl → commit_action

Pathologie-Mapping:
- Trauma → T_panic, T_disso, T_fog
- Depression → x_fm_prox (Nickel-63-Falle)
- Grübelzwang → LL (Low-Level-Loop)
"""

import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

FEP_THRESHOLDS = {
    'A_collapse': 0.30,
    'LL_collapse': 0.65,
    'nabla_A_stagnation': 0.02,
    'shock_threshold': 0.12,
    'ev_readiness_threshold': 0.6,
    'lambda_R': 1.0,
    'fog_critical': 0.7,
    'volatility_trigger': 0.3,
}

@dataclass
class FEPMetrics:
    FE_proxy: float = 0.0
    surprisal: float = 0.0
    phi_score: float = 0.0
    phi_score2: float = 0.0
    U: float = 0.0
    U2: float = 0.0
    R: float = 0.0
    R2: float = 0.0
    commit_action: str = "commit"
    policy_confidence: float = 0.0
    homeostasis_active: bool = False
    homeostasis_pressure: float = 0.0
    EV_tension: float = 0.0
    EV_resonance: float = 0.0
    EV_readiness: float = 0.0
    depression_risk: float = 0.0
    anxiety_loop: float = 0.0
    dissociation: float = 0.0
    trauma_load: float = 0.0
    E_trapped: float = 0.0
    E_available: float = 0.0
    G_phase: float = 0.0
    exploration_drive: float = 0.0


class FEPCalculator:
    def __init__(self):
        self.max_S_entropy = 8.0
    
    def calculate(self, base_metrics: Dict) -> FEPMetrics:
        fep = FEPMetrics()
        
        a_score = base_metrics.get('a_score', 0.5)
        coh = base_metrics.get('coh', 0.5)
        flow = base_metrics.get('flow', 0.5)
        s_entropy = base_metrics.get('s_entropy', 0.0)
        z_prox = base_metrics.get('z_prox', 0.0)
        x_fm_prox = base_metrics.get('x_fm_prox', 0)
        t_fog = base_metrics.get('t_fog', 0.0)
        t_panic = base_metrics.get('t_panic', 0.0)
        t_disso = base_metrics.get('t_disso', 0.0)
        t_integ = base_metrics.get('t_integ', 1.0)
        zlf = base_metrics.get('zlf', 0.0)
        nabla_a = base_metrics.get('nabla_a', 0.0)
        volatility = base_metrics.get('volatility', 0.0)
        g_phase_norm = base_metrics.get('g_phase_norm', 0.0)
        lambda_depth = base_metrics.get('lambda_depth', 0.0)
        f_risk = base_metrics.get('f_risk', 0.0)
        rep_same = base_metrics.get('rep_same', 0.0)
        
        trauma_factor = (t_panic + t_disso) / 2
        
        # FE_proxy
        fep.FE_proxy = min(1.0, 0.6 * (s_entropy / self.max_S_entropy) + 0.4 * (1 - coh))
        fep.surprisal = min(1.0, (1 - coh) * 0.5 + (s_entropy / self.max_S_entropy) * 0.5)
        
        # Tension & Resonance
        fep.EV_tension = min(1.0, 0.5 * z_prox + 0.3 * float(x_fm_prox) + 0.2 * (1 - flow))
        fep.EV_resonance = min(1.0, t_integ * coh * (1 - trauma_factor))
        
        # Utility & Risk
        fep.U = 0.4 * a_score + 0.3 * coh + 0.3 * t_integ
        fep.R = 0.4 * trauma_factor + 0.3 * z_prox + 0.3 * (1 - coh)
        fep.phi_score = fep.U - fep.R
        fep.U2 = min(1.0, fep.U + 0.15 * g_phase_norm + 0.1 * lambda_depth)
        fep.R2 = min(1.0, fep.R + 0.2 * t_fog + 0.1 * zlf)
        fep.phi_score2 = fep.U2 - fep.R2
        
        # Readiness
        fep.EV_readiness = min(1.0, max(0.0, 0.4 * fep.EV_resonance + 0.3 * (1 - fep.EV_tension) + 0.3 * t_integ))
        
        # Homeostasis
        fep.homeostasis_active = volatility > FEP_THRESHOLDS['volatility_trigger']
        fep.homeostasis_pressure = min(1.0, volatility * 2 + fep.EV_tension)
        
        # Pathology
        stagnation = 1.0 if abs(nabla_a) < FEP_THRESHOLDS['nabla_A_stagnation'] else 0.0
        fep.depression_risk = min(1.0, 0.5 * float(x_fm_prox) + 0.3 * stagnation + 0.2 * (1 - fep.EV_resonance))
        fep.anxiety_loop = min(1.0, 0.5 * rep_same + 0.3 * (1 - coh) + 0.2 * zlf)
        fep.dissociation = min(1.0, 0.6 * t_fog + 0.3 * t_disso + 0.1 * (1 - a_score))
        fep.trauma_load = min(1.0, 0.4 * t_panic + 0.3 * t_disso + 0.2 * (1 - t_integ) + 0.1 * fep.dissociation)
        
        # Energy
        fep.E_trapped = min(1.0, 0.6 * float(x_fm_prox) + 0.4 * fep.depression_risk)
        fep.E_available = max(0.0, 1.0 - fep.E_trapped - fep.trauma_load * 0.5)
        fep.G_phase = g_phase_norm
        fep.exploration_drive = min(1.0, 0.4 * (s_entropy / self.max_S_entropy) + 0.3 * fep.E_available + 0.3 * (1 - float(x_fm_prox)))
        
        # Policy
        fep.commit_action, fep.policy_confidence = self._select_policy(fep, f_risk, base_metrics.get('guardian_trip', 0))
        
        return fep
    
    def _select_policy(self, fep, f_risk, guardian_trip) -> Tuple[str, float]:
        if guardian_trip or f_risk > 0.85:
            return ("safe_noop", 0.95)
        if f_risk > 0.7 or fep.trauma_load > 0.7:
            return ("safe_reframe", 0.85)
        if fep.homeostasis_active:
            return ("stabilize", 0.8)
        if fep.EV_readiness > 0.6 and f_risk < 0.4:
            return ("explore", 0.75)
        if fep.depression_risk > 0.6:
            return ("gentle_intervention", 0.7)
        return ("commit", max(0.5, 1.0 - f_risk))

def fep_metrics_to_dict(fep: FEPMetrics) -> Dict:
    return {
        'FE_proxy': fep.FE_proxy, 'surprisal': fep.surprisal,
        'phi_score': fep.phi_score, 'phi_score2': fep.phi_score2,
        'U': fep.U, 'U2': fep.U2, 'R': fep.R, 'R2': fep.R2,
        'commit_action': fep.commit_action, 'policy_confidence': fep.policy_confidence,
        'homeostasis_active': int(fep.homeostasis_active), 'homeostasis_pressure': fep.homeostasis_pressure,
        'EV_tension': fep.EV_tension, 'EV_resonance': fep.EV_resonance, 'EV_readiness': fep.EV_readiness,
        'depression_risk': fep.depression_risk, 'anxiety_loop': fep.anxiety_loop,
        'dissociation': fep.dissociation, 'trauma_load': fep.trauma_load,
        'E_trapped': fep.E_trapped, 'E_available': fep.E_available,
        'G_phase': fep.G_phase, 'exploration_drive': fep.exploration_drive,
    }
