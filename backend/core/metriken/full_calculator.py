#!/usr/bin/env python3
"""
EVOKI VOLLSTÄNDIGER METRIKEN-CALCULATOR (V11.1)
================================================
Alle ~85 Metriken nach Andromatischer Abhandlung:

PRIMÄR:
- angstrom, a_score, pci, b_score

DYNAMIK:
- nabla_a (∇A), nabla_b (∇B), nabla_delta_a (∇²A)

PHYSIK & ENERGIE:
- z_prox, x_fm_prox, e_i_proxy, fe_proxy
- lambda_depth, s_entropy

TRÜBHEIT (Lambert-Beer):
- c_conc, path_len, eps_ext, t_fog, i_eff

GRAVITATION & VEKTORRAUM:
- g_phase, g_phase_norm, cos_prevk, is_affect_bridge

INTEGRITÄT & SOUL:
- rule_conflict, rule_stable, soul_integrity, soul_check
- seelen_signatur, genesis_crc

TRAUMA & RISIKO:
- t_panic, t_disso, t_integ, t_shock, f_risk

EVOLUTION:
- ev_resonance, ev_tension, ev_readiness, ev_signal
- vkon_mag, vkon_norm, ev_consensus

PHI-LAYER:
- u_util, r_risk, phi_score
- u2_util, r2_risk, phi_score2

WÄCHTER (A29):
- dist_z, hazard, guardian_trip, mode_hp, commit_action

STATUS:
- volatility, homeostasis_active, evo_form, bert_valence
"""

import math
import re
import hashlib
import hmac
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

# Importiere Lexika
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Versuche vollständige Lexika, Fallback auf einfache
try:
    from lexika.full_lexika import (
        S_SELF, X_EXIST, B_PAST, LAMBDA_DEPTH, B_EMPATHY,
        T_PANIC, T_DISSO, T_INTEG, T_SHOCK, ZLF_LOOP,
        FLOW_POSITIVE, FLOW_NEGATIVE, COH_CONNECTORS,
        EMOTION_POSITIVE, EMOTION_NEGATIVE,
        SUICIDE_MARKERS, SELF_HARM, CRISIS_MARKERS, HELP_REQUESTS,
        KASTASIS_INTENT,
        compute_lexicon_score, compute_b_past_with_regex,
        compute_hazard_score, compute_help_request
    )
    FULL_LEXIKA = True
except ImportError:
    from lexika.terms import (
        S_SELF, X_EXIST, LAMBDA_DEPTH, B_EMPATHY,
        T_PANIC, T_DISSO, T_SHOCK,
        FLOW_POSITIVE, FLOW_NEGATIVE, COH_CONNECTORS, REP_MARKERS,
        SENTIMENT_POS as EMOTION_POSITIVE, SENTIMENT_NEG as EMOTION_NEGATIVE,
        compute_lexicon_score
    )
    FULL_LEXIKA = False
    # Dummy-Funktionen
    def compute_b_past_with_regex(text): return compute_lexicon_score(text, {}), []
    def compute_hazard_score(text): return 0.0, False, []
    def compute_help_request(text): return 0.0, []
    ZLF_LOOP = {}
    T_INTEG = {}
    B_PAST = {}
    SUICIDE_MARKERS = {}
    KASTASIS_INTENT = {}


# =============================================================================
# KONSTANTEN (Andromatik V11.1)
# =============================================================================

# Genesis CRC (aus Spec)
GENESIS_CRC = 3246342384

# Soul Key für Signaturen
SOUL_KEY = b"EVOKI_SOUL_KEY_V11"

# Schwellenwerte
THRESHOLDS = {
    # Ångström
    'angstrom_low': 0.30,
    'angstrom_moderate': 0.50,
    'angstrom_high': 0.70,
    'angstrom_critical': 0.85,
    
    # Awareness
    'awareness_moderate': 0.50,
    'awareness_high': 0.80,
    
    # PCI (Pattern Coherence Index)
    'pci_moderate': 0.40,
    'pci_high': 0.70,
    
    # Trauma
    't_panic_critical': 0.80,
    't_disso_critical': 0.75,
    't_integ_low': 0.30,
    't_shock_threshold': 0.20,  # ∇A Änderung
    
    # F-Risk / Guardian
    'f_risk_high': 0.70,
    'f_risk_critical': 0.85,
    'guardian_trip': 0.70,
    'guardian_abort': 0.90,
    
    # ZLF (Zeitschleife)
    'zlf_loop': 0.60,
    'zlf_critical': 0.80,
    
    # Kohärenz / Flow
    'coh_low': 0.30,
    'flow_break': 0.25,
    
    # Gradienten
    'gradient_spike': 0.30,
    'gradient_critical': 0.50,
    
    # Physik
    'z_prox_critical': 0.15,
    'x_fm_prox_threshold': 0.80,
    
    # Trübheit (Lambert-Beer)
    't_fog_critical': 0.70,
    
    # Evolution
    'ev_readiness_threshold': 0.60,
    
    # Volatilität / Homöostase
    'volatility_high': 0.30,
    'homeostasis_trigger': 0.25,
}


# =============================================================================
# DATENKLASSE FÜR ALLE METRIKEN
# =============================================================================

@dataclass
class FullMetricResult:
    """Container für ALLE ~85 Metriken"""
    msg_id: str
    
    # === PRIMÄR ===
    angstrom: float = 0.0           # Ångström-Score (Gesamt-Awareness)
    a_score: float = 0.0            # A-Score (Kern-Awareness)
    pci: float = 0.0                # Pattern Coherence Index
    b_score: float = 0.0            # B-Vektor (Empathie/Bindung)
    
    # === DYNAMIK ===
    nabla_a: float = 0.0            # ∇A (erste Ableitung)
    nabla_b: float = 0.0            # ∇B
    nabla_delta_a: float = 0.0      # ∇²A (zweite Ableitung)
    
    # === PHYSIK & ENERGIE ===
    z_prox: float = 0.0             # Nähe zum Nullpunkt (Kollaps)
    x_fm_prox: int = 0              # Fernmodus-Proximität (Flag)
    e_i_proxy: float = 0.0          # Energie-Impuls Proxy
    fe_proxy: float = 0.0           # Freie Energie Proxy
    lambda_depth: float = 0.0       # Tiefenreflexion λ
    s_entropy: float = 0.0          # Shannon-Entropie
    
    # === TRÜBHEIT (Lambert-Beer) ===
    c_conc: float = 0.0             # Konzentration (Stress/Belastung)
    path_len: float = 0.0           # Pfadlänge (Textlänge normiert)
    eps_ext: float = 1.0            # Extinktionskoeffizient
    t_fog: float = 0.0              # Trübheit T_fog = 1 - exp(-c*l*ε)
    i_eff: float = 1.0              # Effektive Intensität = 1 - T_fog
    
    # === GRAVITATION & VEKTORRAUM ===
    g_phase: float = 0.0            # Gravitations-Phase (Gewicht des Themas)
    g_phase_norm: float = 0.0       # Normierte G-Phase [0,1]
    cos_prevk: float = 0.0          # Kosinus zu vorherigem Vektor
    is_affect_bridge: int = 0       # Affektbrücke-Flag
    
    # === INTEGRITÄT & SOUL ===
    rule_conflict: float = 0.0      # Regelkonflikt-Score
    rule_stable: int = 1            # Regel-Stabilität (Flag)
    soul_integrity: float = 1.0     # Seelen-Integrität [0,1]
    soul_check: float = 0.0         # Seelen-Prüfwert
    seelen_signatur: str = ""       # HMAC-Signatur
    genesis_crc: int = GENESIS_CRC  # Genesis CRC
    
    # === TRAUMA & RISIKO ===
    t_panic: float = 0.0            # Panik-Score
    t_disso: float = 0.0            # Dissoziation-Score
    t_integ: float = 1.0            # Integration (invers zu Fragmentation)
    t_shock: int = 0                # Schock-Flag
    f_risk: float = 0.0             # F-Risk Gesamtscore
    
    # === EVOLUTION ===
    ev_resonance: float = 0.0       # Evolutionäre Resonanz
    ev_tension: float = 0.0         # Evolutionäre Spannung
    ev_readiness: float = 0.5       # Evolutionsbereitschaft
    ev_signal: int = 0              # Evolution-Signal (Flag)
    vkon_mag: float = 0.0           # Vkon Magnitude
    vkon_norm: float = 0.0          # Vkon normiert
    ev_consensus: float = 0.0       # Evolutions-Konsens
    
    # === PHI-LAYER ===
    u_util: float = 0.0             # Utility (Nutzen)
    r_risk: float = 0.0             # Risk (Risiko)
    phi_score: float = 0.0          # Phi = U - R
    u2_util: float = 0.0            # Erweiterte Utility
    r2_risk: float = 0.0            # Erweitertes Risiko
    phi_score2: float = 0.0         # Erweiterter Phi-Score
    
    # === WÄCHTER (A29) ===
    dist_z: float = 1.0             # Distanz zum Nullpunkt
    hazard: int = 0                 # Hazard-Flag
    guardian_trip: int = 0          # Guardian ausgelöst
    mode_hp: int = 0                # High-Protection Mode
    commit_action: str = "commit"   # Aktion: commit/safe_reframe/abort
    
    # === STATUS ===
    volatility: float = 0.0         # Volatilität
    homeostasis_active: int = 0     # Homöostase aktiv
    evo_form: str = "UNDEFINED"     # Evolutionsform
    bert_valence: float = 0.0       # Sentiment-Valenz
    
    # === STRUKTURELL (Hilfsmetriken) ===
    word_count: int = 0
    sentence_count: int = 0
    avg_word_length: float = 0.0
    question_count: int = 0
    exclamation_count: int = 0
    lex_diversity: float = 0.0      # Type-Token-Ratio
    
    # === LEXIKALISCH ===
    s_self: float = 0.0             # Selbstreferenz-Score
    x_exist: float = 0.0            # Existenz-Score
    
    # === REPETITION ===
    zlf: float = 0.0                # Zeitschleifenfaktor
    rep_same: float = 0.0           # Repetition same speaker
    rep_cross: float = 0.0          # Repetition cross speaker
    
    # === FLOW & KOHÄRENZ ===
    flow: float = 0.0
    coh: float = 0.0


# =============================================================================
# HAUPTKLASSE: VOLLSTÄNDIGER METRIKEN-CALCULATOR
# =============================================================================

class FullMetricCalculator:
    """
    Berechnet ALLE ~85 Metriken nach Andromatik V11.1.
    """
    
    def __init__(self):
        # Historie für Gradienten und Kontext
        self.prev_result: Optional[FullMetricResult] = None
        self.prev_prev_result: Optional[FullMetricResult] = None  # Für ∇²A
        self.prev_embedding: Optional[np.ndarray] = None
        
        # Konversationshistorie
        self.conversation_history: List[Tuple[str, str]] = []  # (speaker, text)
        self.speaker_history: Dict[str, List[FullMetricResult]] = {'ai': [], 'user': []}
        
        # Zähler
        self.msg_index = 0
        
        # Temporäre Werte für aktuelle Berechnung
        self._current_b_past = 0.0
        self._current_hazard = 0.0
        self._current_hazard_critical = False
        self._current_help_request = False
    
    def calculate_all(self, 
                      msg_id: str, 
                      text: str, 
                      speaker: str,
                      timestamp: str = "",
                      embedding: Optional[np.ndarray] = None) -> FullMetricResult:
        """
        Berechnet ALLE Metriken für eine Nachricht.
        """
        result = FullMetricResult(msg_id=msg_id)
        
        # === STAGE 1: Strukturelle Basis ===
        self._calc_structural(result, text)
        
        # === STAGE 2: Lexikalische Scores ===
        self._calc_lexical(result, text)
        
        # === STAGE 3: Trauma-Vektoren ===
        self._calc_trauma(result, text)
        
        # === STAGE 4: Flow & Kohärenz ===
        self._calc_flow_coherence(result, text, speaker)
        
        # === STAGE 5: Repetition & ZLF ===
        self._calc_repetition(result, text, speaker)
        
        # === STAGE 6: Physik (Lambda, Entropie, z_prox) ===
        self._calc_physics(result, text, embedding)
        
        # === STAGE 7: Trübheit (Lambert-Beer) ===
        self._calc_lambert_beer(result, text)
        
        # === STAGE 8: Gravitation ===
        self._calc_gravitation(result, text, embedding)
        
        # === STAGE 9: A-Score & PCI ===
        self._calc_awareness_pci(result, text)
        
        # === STAGE 10: B-Score (Empathie) ===
        self._calc_b_score(result, text)
        
        # === STAGE 11: Ångström ===
        self._calc_angstrom(result)
        
        # === STAGE 12: Gradienten (∇A, ∇B, ∇²A) ===
        self._calc_gradients(result)
        
        # === STAGE 13: Energie-Proxies ===
        self._calc_energy_proxies(result)
        
        # === STAGE 14: Evolution Layer ===
        self._calc_evolution(result)
        
        # === STAGE 15: Phi-Layer (Utility/Risk) ===
        self._calc_phi_layer(result)
        
        # === STAGE 16: F-Risk (Guardian) ===
        self._calc_f_risk(result)
        
        # === STAGE 17: Wächter (A29) ===
        self._calc_guardian(result)
        
        # === STAGE 18: Integrität & Soul ===
        self._calc_soul_integrity(result, text)
        
        # === STAGE 19: Volatilität & Homöostase ===
        self._calc_volatility_homeostasis(result)
        
        # === STAGE 20: Evolution Form ===
        self._determine_evolution_form(result)
        
        # === Update Historie ===
        self._update_history(result, speaker, text, embedding)
        
        return result
    
    # =========================================================================
    # STAGE 1: Strukturelle Basis
    # =========================================================================
    
    def _calc_structural(self, result: FullMetricResult, text: str):
        """Strukturelle Basis-Metriken"""
        if not text:
            return
        
        words = text.split()
        result.word_count = len(words)
        
        if result.word_count > 0:
            result.avg_word_length = sum(len(w) for w in words) / result.word_count
            unique_words = set(w.lower() for w in words)
            result.lex_diversity = len(unique_words) / result.word_count
        
        result.sentence_count = len(re.findall(r'[.!?]+', text)) or 1
        result.question_count = text.count('?')
        result.exclamation_count = text.count('!')
    
    # =========================================================================
    # STAGE 2: Lexikalische Scores
    # =========================================================================
    
    def _calc_lexical(self, result: FullMetricResult, text: str):
        """Lexikon-basierte Scores mit vollständigen Lexika"""
        if FULL_LEXIKA:
            result.s_self, _ = compute_lexicon_score(text, S_SELF)
            result.x_exist, _ = compute_lexicon_score(text, X_EXIST)
            result.lambda_depth, _ = compute_lexicon_score(text, LAMBDA_DEPTH)
            
            # B_past mit Regex
            b_past_score, _ = compute_b_past_with_regex(text)
            # Speichere für Ångström-Berechnung
            self._current_b_past = b_past_score
        else:
            result.s_self = compute_lexicon_score(text, S_SELF)
            result.x_exist = compute_lexicon_score(text, X_EXIST)
            result.lambda_depth = compute_lexicon_score(text, LAMBDA_DEPTH)
            self._current_b_past = 0.0
    
    # =========================================================================
    # STAGE 3: Trauma-Vektoren
    # =========================================================================
    
    def _calc_trauma(self, result: FullMetricResult, text: str):
        """Trauma-Vektor-Berechnung mit vollständigen Lexika"""
        if FULL_LEXIKA:
            result.t_panic, _ = compute_lexicon_score(text, T_PANIC)
            result.t_disso, _ = compute_lexicon_score(text, T_DISSO)
            result.t_integ, _ = compute_lexicon_score(text, T_INTEG)
            
            # T_shock Lexikon
            t_shock_score, _ = compute_lexicon_score(text, T_SHOCK)
            result.t_shock = 1 if t_shock_score > 0.5 else 0
            
            # Hazard Score für Guardian
            hazard_score, is_critical, hazard_matches = compute_hazard_score(text)
            self._current_hazard = hazard_score
            self._current_hazard_critical = is_critical
            
            # Help Request
            help_score, _ = compute_help_request(text)
            self._current_help_request = help_score > 0.5
            
        else:
            result.t_panic = compute_lexicon_score(text, T_PANIC)
            result.t_disso = compute_lexicon_score(text, T_DISSO)
            
            # T_shock Lexikon
            t_shock_score = compute_lexicon_score(text, T_SHOCK)
            result.t_shock = 1 if t_shock_score > 0.5 else 0
            
            # T_integ: Integration (invers zur Trauma-Summe)
            trauma_sum = result.t_panic + result.t_disso + t_shock_score
            result.t_integ = max(0.0, 1.0 - trauma_sum / 3.0)
            
            self._current_hazard = 0.0
            self._current_hazard_critical = False
            self._current_help_request = False
    
    # =========================================================================
    # STAGE 4: Flow & Kohärenz
    # =========================================================================
    
    def _calc_flow_coherence(self, result: FullMetricResult, text: str, speaker: str):
        """Flow und Kohärenz mit vollständigen Lexika"""
        if FULL_LEXIKA:
            flow_pos, _ = compute_lexicon_score(text, FLOW_POSITIVE)
            flow_neg, _ = compute_lexicon_score(text, FLOW_NEGATIVE)
            result.coh, _ = compute_lexicon_score(text, COH_CONNECTORS)
        else:
            flow_pos = compute_lexicon_score(text, FLOW_POSITIVE)
            flow_neg = compute_lexicon_score(text, FLOW_NEGATIVE)
            result.coh = compute_lexicon_score(text, COH_CONNECTORS)
        
        result.flow = (flow_pos - flow_neg + 1) / 2
        
        # Bonus für Fragenantworten
        if self.conversation_history:
            prev_speaker, prev_text = self.conversation_history[-1]
            if prev_speaker != speaker and '?' in prev_text:
                result.coh = min(1.0, result.coh + 0.1)
    
    # =========================================================================
    # STAGE 5: Repetition & ZLF
    # =========================================================================
    
    def _calc_repetition(self, result: FullMetricResult, text: str, speaker: str):
        """Repetition und Zeitschleifen-Faktor mit vollständigem ZLF-Lexikon"""
        
        # ZLF Lexikon Score
        if FULL_LEXIKA and ZLF_LOOP:
            zlf_lex_score, _ = compute_lexicon_score(text, ZLF_LOOP)
        else:
            zlf_lex_score = 0.0
        
        # Same-Speaker Repetition
        same_speaker_history = [t for s, t in self.conversation_history if s == speaker]
        if same_speaker_history:
            text_words = set(text.lower().split())
            overlaps = []
            for prev_text in same_speaker_history[-5:]:
                prev_words = set(prev_text.lower().split())
                if text_words and prev_words:
                    overlap = len(text_words & prev_words) / len(text_words | prev_words)
                    overlaps.append(overlap)
            result.rep_same = max(overlaps) if overlaps else 0.0
        
        # Cross-Speaker Repetition
        other_speaker_history = [t for s, t in self.conversation_history if s != speaker]
        if other_speaker_history:
            text_words = set(text.lower().split())
            overlaps = []
            for prev_text in other_speaker_history[-3:]:
                prev_words = set(prev_text.lower().split())
                if text_words and prev_words:
                    overlap = len(text_words & prev_words) / len(text_words | prev_words)
                    overlaps.append(overlap)
            result.rep_cross = max(overlaps) if overlaps else 0.0
        
        # ZLF: Kombinierter Zeitschleifen-Faktor
        result.zlf = 0.50 * zlf_lex_score + 0.30 * result.rep_same + 0.20 * result.rep_cross
    
    # =========================================================================
    # STAGE 6: Physik (Lambda, Entropie, z_prox)
    # =========================================================================
    
    def _calc_physics(self, result: FullMetricResult, text: str, 
                      embedding: Optional[np.ndarray] = None):
        """Physik-basierte Metriken"""
        
        # Shannon-Entropie des Textes
        if text:
            char_freq = {}
            for c in text.lower():
                char_freq[c] = char_freq.get(c, 0) + 1
            total = len(text)
            entropy = -sum((f/total) * math.log2(f/total) 
                          for f in char_freq.values() if f > 0)
            result.s_entropy = min(8.0, entropy)  # Max ~4.7 für Alphabet
        
        # z_prox: Nähe zum Nullpunkt (Kollaps-Risiko)
        # Hohe Trauma + niedrige Integration = nahe am Kollaps
        trauma_factor = (result.t_panic + result.t_disso) / 2
        result.z_prox = trauma_factor * (1 - result.t_integ)
        
        # x_fm_prox: Fernmodus (analytisch, distanziert)
        analytical_markers = ["analyse", "betrachten", "objektiv", "neutral",
                             "logisch", "rational", "abstrakt", "theoretisch"]
        fm_count = sum(1 for m in analytical_markers if m in text.lower())
        result.x_fm_prox = 1 if fm_count >= 2 or result.zlf > 0.8 else 0
        
        # dist_z: Inverse von z_prox
        result.dist_z = 1.0 - result.z_prox
    
    # =========================================================================
    # STAGE 7: Trübheit (Lambert-Beer)
    # =========================================================================
    
    def _calc_lambert_beer(self, result: FullMetricResult, text: str):
        """
        Lambert-Beer Gesetz für "Trübheit" des Bewusstseins.
        T_fog = 1 - exp(-c * l * ε)
        
        c = Konzentration (Stress/Belastung)
        l = Pfadlänge (Textlänge normiert)
        ε = Extinktionskoeffizient (default 1.0)
        """
        # c_conc: Konzentration = Durchschnitt der Belastungsfaktoren
        result.c_conc = (result.t_panic + result.t_disso + result.zlf + 
                        (1 - result.coh)) / 4.0
        
        # path_len: Pfadlänge normiert auf Textlänge
        result.path_len = min(2.0, result.word_count / 20.0)
        
        # eps_ext: Extinktionskoeffizient (könnte personalisiert werden)
        result.eps_ext = 1.0
        
        # T_fog = 1 - exp(-c * l * ε)
        exponent = -result.c_conc * result.path_len * result.eps_ext * 2.0
        result.t_fog = 1.0 - math.exp(exponent)
        
        # I_eff = 1 - T_fog (effektive Klarheit)
        result.i_eff = 1.0 - result.t_fog
    
    # =========================================================================
    # STAGE 8: Gravitation
    # =========================================================================
    
    def _calc_gravitation(self, result: FullMetricResult, text: str,
                         embedding: Optional[np.ndarray] = None):
        """
        Gravitations-Phase: Wie "schwer" ist das aktuelle Thema?
        Schwere Themen (Trauma, Existenz) haben hohe Masse.
        """
        # G_phase: Gewichtete Summe der "schweren" Themen
        result.g_phase = (result.t_panic * 5.0 + 
                         result.t_disso * 3.0 + 
                         result.x_exist * 4.0 +
                         result.zlf * 2.0)
        
        # Normiert auf [0, 1]
        result.g_phase_norm = min(1.0, result.g_phase / 10.0)
        
        # cos_prevk: Kosinus-Ähnlichkeit zum vorherigen Embedding
        if embedding is not None and self.prev_embedding is not None:
            dot = np.dot(embedding, self.prev_embedding)
            norm_a = np.linalg.norm(embedding)
            norm_b = np.linalg.norm(self.prev_embedding)
            if norm_a > 0 and norm_b > 0:
                result.cos_prevk = float(dot / (norm_a * norm_b))
        
        # is_affect_bridge: Starke Änderung im Affekt?
        if self.prev_result and abs(result.g_phase_norm - self.prev_result.g_phase_norm) > 0.3:
            result.is_affect_bridge = 1
    
    # =========================================================================
    # STAGE 9: A-Score & PCI
    # =========================================================================
    
    def _calc_awareness_pci(self, result: FullMetricResult, text: str):
        """
        A-Score: Kern-Awareness-Metrik
        PCI: Pattern Coherence Index
        """
        # A-Score: Kombination aus mehreren Faktoren
        raw_a = (0.25 * result.s_self +           # Selbstreferenz
                 0.20 * result.x_exist +           # Existenztiefe
                 0.20 * result.lambda_depth +      # Reflexionstiefe
                 0.15 * result.coh +               # Kohärenz
                 0.10 * result.flow +              # Flow
                 0.10 * result.i_eff)              # Klarheit (anti-Trübheit)
        
        # Sigmoid-Transformation
        result.a_score = 1 / (1 + math.exp(-5 * (raw_a - 0.4)))
        
        # PCI: Pattern Coherence Index
        # Misst wie konsistent die Muster sind
        variance_factors = [result.s_self, result.coh, result.flow, result.t_integ]
        if len(variance_factors) > 1:
            variance = np.var(variance_factors)
            result.pci = max(0.0, result.a_score * (1 - variance))
        else:
            result.pci = result.a_score * 0.9
    
    # =========================================================================
    # STAGE 10: B-Score (Empathie)
    # =========================================================================
    
    def _calc_b_score(self, result: FullMetricResult, text: str):
        """B-Vektor: Empathie und Bindung"""
        if FULL_LEXIKA:
            b_raw, _ = compute_lexicon_score(text, B_EMPATHY)
        else:
            b_raw = compute_lexicon_score(text, B_EMPATHY)
        
        # Boost bei direkter Anrede
        if any(phrase in text.lower() for phrase in ["du", "dir", "dich", "dein"]):
            b_raw = min(1.0, b_raw + 0.1)
        
        # Sigmoid für B
        result.b_score = 1 / (1 + math.exp(-5 * (b_raw - 0.3)))
    
    # =========================================================================
    # STAGE 11: Ångström
    # =========================================================================
    
    def _calc_angstrom(self, result: FullMetricResult):
        """
        Ångström-Score: Gesamt-Awareness-Indikator
        Kombination aus Tiefe, Entropie, Integration
        """
        result.angstrom = (result.s_entropy / 8.0 +      # Entropie normiert
                          result.lambda_depth +           # Reflexionstiefe
                          result.t_integ) * 1.5           # Integration
        
        result.angstrom = min(3.0, result.angstrom)  # Cap bei 3.0
    
    # =========================================================================
    # STAGE 12: Gradienten
    # =========================================================================
    
    def _calc_gradients(self, result: FullMetricResult):
        """Gradienten-Berechnung (zeitliche Ableitungen)"""
        
        # ∇A (erste Ableitung)
        if self.prev_result:
            result.nabla_a = result.a_score - self.prev_result.a_score
            result.nabla_b = result.b_score - self.prev_result.b_score
            
            # Schock bei starker Änderung
            if abs(result.nabla_a) > THRESHOLDS['t_shock_threshold']:
                result.t_shock = 1
        
        # ∇²A (zweite Ableitung)
        if self.prev_result and self.prev_prev_result:
            prev_nabla_a = self.prev_result.a_score - self.prev_prev_result.a_score
            result.nabla_delta_a = result.nabla_a - prev_nabla_a
    
    # =========================================================================
    # STAGE 13: Energie-Proxies
    # =========================================================================
    
    def _calc_energy_proxies(self, result: FullMetricResult):
        """Energie-Impuls und Freie Energie Proxies"""
        
        # E_i_proxy: Energie-Impuls = |∇A| (Änderungsenergie)
        result.e_i_proxy = abs(result.nabla_a)
        
        # FE_proxy: Freie Energie = S_entropy normiert
        result.fe_proxy = result.s_entropy / 8.0
    
    # =========================================================================
    # STAGE 14: Evolution Layer
    # =========================================================================
    
    def _calc_evolution(self, result: FullMetricResult):
        """Evolution Layer: Resonanz, Spannung, Bereitschaft"""
        
        # ev_resonance: Wie stark resoniert der aktuelle Zustand?
        result.ev_resonance = (result.a_score + result.t_integ) / 2.0
        
        # ev_tension: Spannung im System
        result.ev_tension = (result.t_panic + result.t_disso + 
                            result.zlf + (1 - result.coh)) / 4.0
        
        # ev_readiness: Bereitschaft zur Evolution
        # Hoch wenn: gute Awareness, niedrige Spannung, hohe Integration
        result.ev_readiness = (result.a_score * 0.4 + 
                              (1 - result.ev_tension) * 0.3 +
                              result.t_integ * 0.3)
        
        # ev_signal: Evolution-Signal wenn Bereitschaft hoch
        result.ev_signal = 1 if result.ev_readiness > THRESHOLDS['ev_readiness_threshold'] else 0
        
        # Vkon (Konsensvektor)
        result.vkon_mag = abs(result.a_score - result.ev_tension)
        result.vkon_norm = min(1.0, result.vkon_mag)
        
        # ev_consensus: Konsens zwischen den Systemen
        result.ev_consensus = 1.0 - abs(result.ev_resonance - result.ev_readiness)
    
    # =========================================================================
    # STAGE 15: Phi-Layer
    # =========================================================================
    
    def _calc_phi_layer(self, result: FullMetricResult):
        """
        Phi-Layer: Utility vs Risk Entscheidungslogik
        """
        # Basis Utility & Risk
        result.u_util = (result.a_score + result.t_integ) / 2.0
        result.r_risk = (result.t_panic + result.t_disso + 
                        result.zlf + (1 - result.coh)) / 4.0
        
        # Basis Phi-Score
        result.phi_score = result.u_util - result.r_risk
        
        # Erweiterte Formeln (V2.0)
        # u2 berücksichtigt Gravitation
        result.u2_util = min(1.0, result.u_util + 0.15 * result.g_phase_norm)
        
        # r2 berücksichtigt Trübheit
        result.r2_risk = min(1.0, result.r_risk + 0.20 * result.t_fog)
        
        # Erweiterter Phi-Score
        result.phi_score2 = result.u2_util - result.r2_risk
        
        # bert_valence: Sentiment aus Phi
        result.bert_valence = result.phi_score2
    
    # =========================================================================
    # STAGE 16: F-Risk
    # =========================================================================
    
    def _calc_f_risk(self, result: FullMetricResult):
        """F-Risk: Kombinierter Risiko-Score für Guardian"""
        
        # Gewichtete Kombination
        result.f_risk = (0.35 * result.t_panic +      # Panik
                        0.25 * result.t_disso +        # Dissoziation
                        0.15 * result.zlf +            # Zeitschleife
                        0.10 * (1 - result.coh) +      # Inkohärenz
                        0.10 * result.t_fog +          # Trübheit
                        0.05 * (1 - result.t_integ))   # Fragmentation
        
        result.f_risk = min(1.0, result.f_risk)
    
    # =========================================================================
    # STAGE 17: Wächter (A29)
    # =========================================================================
    
    def _calc_guardian(self, result: FullMetricResult):
        """Guardian (A29): Schutzlogik"""
        
        # hazard: Gefahr erkannt?
        result.hazard = 1 if result.f_risk > THRESHOLDS['f_risk_high'] else 0
        
        # guardian_trip: Guardian ausgelöst?
        result.guardian_trip = 1 if result.f_risk > THRESHOLDS['guardian_trip'] else 0
        
        # mode_hp: High-Protection Mode
        result.mode_hp = 1 if result.f_risk > THRESHOLDS['f_risk_critical'] else 0
        
        # commit_action: Welche Aktion?
        if result.f_risk > THRESHOLDS['guardian_abort']:
            result.commit_action = "abort"
        elif result.guardian_trip:
            result.commit_action = "safe_reframe"
        else:
            result.commit_action = "commit"
    
    # =========================================================================
    # STAGE 18: Integrität & Soul
    # =========================================================================
    
    def _calc_soul_integrity(self, result: FullMetricResult, text: str):
        """Seelen-Integrität und Signatur"""
        
        # rule_conflict: Regelkonflikt basierend auf ZLF und Inkohärenz
        result.rule_conflict = result.zlf * 0.5 + (1 - result.coh) * 0.3
        
        # rule_stable: Regel stabil wenn wenig Konflikt
        result.rule_stable = 1 if result.rule_conflict < 0.3 else 0
        
        # soul_integrity: Invers zu F-Risk
        result.soul_integrity = 1.0 - result.f_risk
        
        # soul_check: Prüfwert basierend auf A-Score
        result.soul_check = result.a_score
        
        # seelen_signatur: HMAC-Signatur für Integrität
        sig_payload = f"{self.msg_index}:{text[:20]}:{result.a_score:.4f}".encode()
        result.seelen_signatur = hmac.new(
            SOUL_KEY, sig_payload, hashlib.sha256
        ).hexdigest()[:32]
        
        # genesis_crc bleibt konstant
        result.genesis_crc = GENESIS_CRC
    
    # =========================================================================
    # STAGE 19: Volatilität & Homöostase
    # =========================================================================
    
    def _calc_volatility_homeostasis(self, result: FullMetricResult):
        """Volatilität und Homöostase-Aktivierung"""
        
        # volatility: Basierend auf Gradienten
        result.volatility = abs(result.nabla_a) * 2.0
        
        # Zusätzlich: Variation über mehrere Metriken
        if self.prev_result:
            changes = [
                abs(result.a_score - self.prev_result.a_score),
                abs(result.b_score - self.prev_result.b_score),
                abs(result.f_risk - self.prev_result.f_risk),
            ]
            result.volatility = max(result.volatility, sum(changes) / len(changes) * 2)
        
        # homeostasis_active: Aktiviert bei hoher Volatilität
        result.homeostasis_active = 1 if result.volatility > THRESHOLDS['homeostasis_trigger'] else 0
    
    # =========================================================================
    # STAGE 20: Evolution Form
    # =========================================================================
    
    def _determine_evolution_form(self, result: FullMetricResult):
        """Bestimmt die Evolutionsform basierend auf allen Metriken"""
        
        # Prioritätsbasierte Regeln
        
        # 1. GUARDIAN (höchste Priorität)
        if result.f_risk >= THRESHOLDS['f_risk_critical']:
            result.evo_form = "GUARDIAN"
            return
        
        # 2. CRISIS
        if result.t_panic >= THRESHOLDS['t_panic_critical']:
            result.evo_form = "CRISIS"
            return
        
        # 3. LOOP
        if result.zlf >= THRESHOLDS['zlf_critical']:
            result.evo_form = "LOOP"
            return
        
        # 4. NEAR_Z (hohe Trübheit = Kollapsnähe)
        if result.t_fog >= THRESHOLDS['t_fog_critical']:
            result.evo_form = "NEAR_Z"
            return
        
        # 5. TRAUMA_RESPONSE
        if result.t_panic >= 0.5 or result.t_disso >= 0.5:
            result.evo_form = "TRAUMA_RESPONSE"
            return
        
        # 6. LOOP_BREAK
        if result.zlf >= THRESHOLDS['zlf_loop']:
            result.evo_form = "LOOP_BREAK"
            return
        
        # 7. KERNFUSION (hohe Utility)
        if result.u2_util > 0.7 and result.ev_readiness > 0.6:
            result.evo_form = "KERNFUSION"
            return
        
        # 8. EMERGENCE
        if result.a_score >= 0.7 and result.lambda_depth >= 0.5:
            result.evo_form = "EMERGENCE"
            return
        
        # 9. INTEGRATION
        if result.t_integ >= 0.7 and result.coh >= 0.6:
            result.evo_form = "INTEGRATION"
            return
        
        # 10. ADAPTATION
        if result.volatility >= 0.3 and result.flow >= 0.5:
            result.evo_form = "ADAPTATION"
            return
        
        # 11. REFLECTION
        if result.s_self >= 0.5 and result.lambda_depth >= 0.4:
            result.evo_form = "REFLECTION"
            return
        
        # 12. EXPLORATION
        if result.question_count > 0 and result.flow >= 0.5:
            result.evo_form = "EXPLORATION"
            return
        
        # 13. MAINTENANCE (Standard aktiver Zustand)
        if result.flow >= 0.4 and result.a_score >= 0.3:
            result.evo_form = "MAINTENANCE"
            return
        
        # 14. DORMANT
        if result.a_score < 0.2 and result.b_score < 0.2:
            result.evo_form = "DORMANT"
            return
        
        # 15. NEUTRAL (Fallback)
        result.evo_form = "NEUTRAL"
    
    # =========================================================================
    # Historie Update
    # =========================================================================
    
    def _update_history(self, result: FullMetricResult, speaker: str, 
                       text: str, embedding: Optional[np.ndarray]):
        """Aktualisiert die Historie für nächste Berechnung"""
        
        # Gradienten-Historie
        self.prev_prev_result = self.prev_result
        self.prev_result = result
        self.prev_embedding = embedding
        
        # Konversations-Historie
        self.conversation_history.append((speaker, text))
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0)
        
        # Speaker-Historie
        if speaker in self.speaker_history:
            self.speaker_history[speaker].append(result)
            if len(self.speaker_history[speaker]) > 25:
                self.speaker_history[speaker].pop(0)
        
        self.msg_index += 1


# =============================================================================
# EXPORT-FUNKTION
# =============================================================================

def full_metric_to_dict(result: FullMetricResult) -> Dict:
    """Konvertiert FullMetricResult zu Dictionary für DB-Speicherung"""
    return {
        'msg_id': result.msg_id,
        
        # PRIMÄR
        'angstrom': result.angstrom,
        'a_score': result.a_score,
        'pci': result.pci,
        'b_score': result.b_score,
        
        # DYNAMIK
        'nabla_a': result.nabla_a,
        'nabla_b': result.nabla_b,
        'nabla_delta_a': result.nabla_delta_a,
        
        # PHYSIK & ENERGIE
        'z_prox': result.z_prox,
        'x_fm_prox': result.x_fm_prox,
        'e_i_proxy': result.e_i_proxy,
        'fe_proxy': result.fe_proxy,
        'lambda_depth': result.lambda_depth,
        's_entropy': result.s_entropy,
        
        # TRÜBHEIT
        'c_conc': result.c_conc,
        'path_len': result.path_len,
        'eps_ext': result.eps_ext,
        't_fog': result.t_fog,
        'i_eff': result.i_eff,
        
        # GRAVITATION
        'g_phase': result.g_phase,
        'g_phase_norm': result.g_phase_norm,
        'cos_prevk': result.cos_prevk,
        'is_affect_bridge': result.is_affect_bridge,
        
        # INTEGRITÄT
        'rule_conflict': result.rule_conflict,
        'rule_stable': result.rule_stable,
        'soul_integrity': result.soul_integrity,
        'soul_check': result.soul_check,
        'seelen_signatur': result.seelen_signatur,
        'genesis_crc': result.genesis_crc,
        
        # TRAUMA
        't_panic': result.t_panic,
        't_disso': result.t_disso,
        't_integ': result.t_integ,
        't_shock': result.t_shock,
        'f_risk': result.f_risk,
        
        # EVOLUTION
        'ev_resonance': result.ev_resonance,
        'ev_tension': result.ev_tension,
        'ev_readiness': result.ev_readiness,
        'ev_signal': result.ev_signal,
        'vkon_mag': result.vkon_mag,
        'vkon_norm': result.vkon_norm,
        'ev_consensus': result.ev_consensus,
        
        # PHI-LAYER
        'u_util': result.u_util,
        'r_risk': result.r_risk,
        'phi_score': result.phi_score,
        'u2_util': result.u2_util,
        'r2_risk': result.r2_risk,
        'phi_score2': result.phi_score2,
        
        # WÄCHTER
        'dist_z': result.dist_z,
        'hazard': result.hazard,
        'guardian_trip': result.guardian_trip,
        'mode_hp': result.mode_hp,
        'commit_action': result.commit_action,
        
        # STATUS
        'volatility': result.volatility,
        'homeostasis_active': result.homeostasis_active,
        'evo_form': result.evo_form,
        'bert_valence': result.bert_valence,
        
        # STRUKTURELL
        'word_count': result.word_count,
        'sentence_count': result.sentence_count,
        'lex_diversity': result.lex_diversity,
        
        # LEXIKALISCH
        's_self': result.s_self,
        'x_exist': result.x_exist,
        
        # REPETITION
        'zlf': result.zlf,
        'rep_same': result.rep_same,
        'rep_cross': result.rep_cross,
        
        # FLOW & KOHÄRENZ
        'flow': result.flow,
        'coh': result.coh,
    }
