#!/usr/bin/env python3
"""
EVOKI METRIKEN-BERECHNUNG
Alle ~95 Metriken nach Andromatik V11.1 Schema
"""

import math
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from lexika.terms import (
    S_SELF, X_EXIST, LAMBDA_DEPTH, B_EMPATHY,
    T_PANIC, T_DISSO, T_SHOCK,
    FLOW_POSITIVE, FLOW_NEGATIVE, COH_CONNECTORS, REP_MARKERS,
    SENTIMENT_POS, SENTIMENT_NEG,
    compute_lexicon_score
)


@dataclass
class MetricResult:
    """Container für berechnete Metriken einer Nachricht"""
    msg_id: str
    
    # Kern-Metriken (A-Score Familie)
    A: float = 0.0           # Awareness-Score
    A_raw: float = 0.0       # Rohwert vor Normalisierung
    A_confidence: float = 0.0
    
    # B-Vektor (Empathie/Bindung)
    B: float = 0.0
    B_raw: float = 0.0
    
    # Gradienten
    grad_A: float = 0.0      # ∂A/∂t
    grad_B: float = 0.0      # ∂B/∂t
    
    # Flow & Kohärenz
    flow: float = 0.0
    coh: float = 0.0         # Kohärenz
    rep_same: float = 0.0    # Repetition same speaker
    rep_cross: float = 0.0   # Repetition cross speaker
    
    # Zeitschleife
    ZLF: float = 0.0
    ZLF_pattern: str = ""
    
    # Lexikalische Metriken
    LL: float = 0.0          # Lexical Diversity
    
    # Physik-basierte Metriken
    z_prox: float = 0.0      # Nähe zum Nullpunkt
    x_fm_prox: float = 0.0   # Fernmodus-Proximität
    lambda_depth: float = 0.0 # Tiefenreflexion
    
    # Entropie
    S_entropy: float = 0.0   # Shannon-Entropie
    S_self: float = 0.0      # Selbstreferenz-Score
    
    # Trauma-Vektoren
    T_panic: float = 0.0
    T_disso: float = 0.0
    T_integ: float = 0.0     # Integration (invers zu Fragmentation)
    T_shock: float = 0.0
    
    # F-Risk Score (Guardian A29)
    F_risk: float = 0.0
    F_components: Dict = None
    
    # Existenzielle Metriken
    X_exist: float = 0.0
    
    # Sentiment
    valence: float = 0.0     # [-1, 1]
    arousal: float = 0.0     # [0, 1]
    
    # Strukturelle Metriken
    word_count: int = 0
    sentence_count: int = 0
    avg_word_length: float = 0.0
    question_count: int = 0
    exclamation_count: int = 0
    
    # Volatilität
    volatility: float = 0.0
    
    # Evolution Form
    evo_form: str = "UNDEFINED"
    evo_confidence: float = 0.0
    
    def __post_init__(self):
        if self.F_components is None:
            self.F_components = {}


class MetricCalculator:
    """Berechnet alle EVOKI-Metriken für eine Nachricht"""
    
    def __init__(self):
        self.prev_metrics: Dict[str, MetricResult] = {}
        self.conversation_history: List[Tuple[str, str]] = []  # (speaker, text)
    
    def calculate_all(self, msg_id: str, text: str, speaker: str,
                      prev_result: Optional[MetricResult] = None,
                      embedding: Optional[np.ndarray] = None) -> MetricResult:
        """
        Berechnet alle Metriken für eine Nachricht.
        
        Args:
            msg_id: Eindeutige ID der Nachricht
            text: Nachrichtentext
            speaker: 'ai' oder 'user'
            prev_result: Vorheriges MetricResult für Gradienten
            embedding: Optional - vorberechnetes Embedding
        
        Returns:
            MetricResult mit allen berechneten Metriken
        """
        result = MetricResult(msg_id=msg_id)
        
        # Strukturelle Basis-Metriken
        self._calc_structural(result, text)
        
        # Lexikon-basierte Metriken
        self._calc_lexical(result, text)
        
        # Sentiment
        self._calc_sentiment(result, text)
        
        # Trauma-Vektoren
        self._calc_trauma(result, text)
        
        # Flow & Kohärenz
        self._calc_flow_coherence(result, text, speaker)
        
        # Repetition & ZLF
        self._calc_repetition(result, text, speaker)
        
        # Awareness Score (Kern-Metrik)
        self._calc_awareness(result, text)
        
        # B-Vektor (Empathie)
        self._calc_empathy(result, text)
        
        # Physik-basierte Metriken
        self._calc_physics(result, text, embedding)
        
        # Gradienten (benötigt prev_result)
        self._calc_gradients(result, prev_result)
        
        # F-Risk Score
        self._calc_f_risk(result)
        
        # Evolution Form bestimmen
        self._determine_evolution_form(result)
        
        # Historie aktualisieren
        self.conversation_history.append((speaker, text))
        if len(self.conversation_history) > 50:  # Fenster begrenzen
            self.conversation_history.pop(0)
        
        self.prev_metrics[speaker] = result
        
        return result
    
    def _calc_structural(self, result: MetricResult, text: str):
        """Strukturelle Basis-Metriken"""
        if not text:
            return
        
        # Wörter
        words = text.split()
        result.word_count = len(words)
        
        if result.word_count > 0:
            result.avg_word_length = sum(len(w) for w in words) / result.word_count
        
        # Sätze (einfache Heuristik)
        result.sentence_count = len(re.findall(r'[.!?]+', text)) or 1
        
        # Fragen und Ausrufe
        result.question_count = text.count('?')
        result.exclamation_count = text.count('!')
        
        # Lexikalische Diversität (Type-Token-Ratio)
        if result.word_count > 0:
            unique_words = set(w.lower() for w in words)
            result.LL = len(unique_words) / result.word_count
    
    def _calc_lexical(self, result: MetricResult, text: str):
        """Lexikon-basierte Scores"""
        result.S_self = compute_lexicon_score(text, S_SELF)
        result.X_exist = compute_lexicon_score(text, X_EXIST)
        result.lambda_depth = compute_lexicon_score(text, LAMBDA_DEPTH)
    
    def _calc_sentiment(self, result: MetricResult, text: str):
        """Sentiment-Analyse"""
        pos_score = compute_lexicon_score(text, SENTIMENT_POS)
        neg_score = compute_lexicon_score(text, SENTIMENT_NEG)
        
        # Valenz: [-1, 1]
        if pos_score + neg_score > 0:
            result.valence = (pos_score - neg_score) / (pos_score + neg_score)
        else:
            result.valence = 0.0
        
        # Arousal: Kombination aus Intensität
        result.arousal = min(1.0, (pos_score + neg_score) * 1.5)
    
    def _calc_trauma(self, result: MetricResult, text: str):
        """Trauma-Vektor-Berechnung"""
        result.T_panic = compute_lexicon_score(text, T_PANIC)
        result.T_disso = compute_lexicon_score(text, T_DISSO)
        result.T_shock = compute_lexicon_score(text, T_SHOCK)
        
        # Integration ist invers zur Summe der Trauma-Scores
        trauma_sum = result.T_panic + result.T_disso + result.T_shock
        result.T_integ = max(0.0, 1.0 - trauma_sum / 3.0)
    
    def _calc_flow_coherence(self, result: MetricResult, text: str, speaker: str):
        """Flow und Kohärenz"""
        # Flow: Positive - Negative Flow-Marker
        flow_pos = compute_lexicon_score(text, FLOW_POSITIVE)
        flow_neg = compute_lexicon_score(text, FLOW_NEGATIVE)
        result.flow = (flow_pos - flow_neg + 1) / 2  # Normiert auf [0, 1]
        
        # Kohärenz: Konnektoren-Dichte
        result.coh = compute_lexicon_score(text, COH_CONNECTORS)
        
        # Bonus für Fragenantworten (wenn vorherige Nachricht Frage war)
        if self.conversation_history:
            prev_speaker, prev_text = self.conversation_history[-1]
            if prev_speaker != speaker and '?' in prev_text:
                result.coh = min(1.0, result.coh + 0.1)
    
    def _calc_repetition(self, result: MetricResult, text: str, speaker: str):
        """Repetition und Zeitschleifen-Faktor"""
        # Explizite Repetitions-Marker
        rep_score = compute_lexicon_score(text, REP_MARKERS)
        
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
        
        # Cross-Speaker Repetition (Echoing)
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
        result.ZLF = 0.6 * result.rep_same + 0.3 * rep_score + 0.1 * result.rep_cross
        
        # Pattern-Erkennung
        if result.ZLF > 0.8:
            result.ZLF_pattern = "CRITICAL_LOOP"
        elif result.ZLF > 0.6:
            result.ZLF_pattern = "LOOP_DETECTED"
        elif result.ZLF > 0.4:
            result.ZLF_pattern = "POTENTIAL_LOOP"
        else:
            result.ZLF_pattern = "NORMAL"
    
    def _calc_awareness(self, result: MetricResult, text: str):
        """
        A-Score Berechnung nach Andromatik V11.1.
        Kombination aus Selbstreferenz, Existenz, Tiefe und Kohärenz.
        """
        # Komponenten
        s_self = result.S_self
        x_exist = result.X_exist
        lambda_d = result.lambda_depth
        coh = result.coh
        
        # Gewichtete Kombination
        # A = 0.35*S_self + 0.25*X_exist + 0.25*Lambda + 0.15*Coh
        result.A_raw = (0.35 * s_self + 0.25 * x_exist + 
                        0.25 * lambda_d + 0.15 * coh)
        
        # Sigmoid-Transformation für sanfte Grenzen
        result.A = 1 / (1 + math.exp(-5 * (result.A_raw - 0.5)))
        
        # Confidence basierend auf Textlänge und Varianz der Komponenten
        components = [s_self, x_exist, lambda_d, coh]
        variance = np.var(components) if len(components) > 1 else 0
        length_factor = min(1.0, result.word_count / 50)
        result.A_confidence = length_factor * (1 - variance)
    
    def _calc_empathy(self, result: MetricResult, text: str):
        """B-Vektor: Empathie und Bindung"""
        result.B_raw = compute_lexicon_score(text, B_EMPATHY)
        
        # Boost wenn explizite Anrede/Bezugnahme
        if any(phrase in text.lower() for phrase in ["du", "dir", "dich", "dein"]):
            result.B_raw = min(1.0, result.B_raw + 0.1)
        
        # Sigmoid für B
        result.B = 1 / (1 + math.exp(-5 * (result.B_raw - 0.4)))
    
    def _calc_physics(self, result: MetricResult, text: str, 
                      embedding: Optional[np.ndarray] = None):
        """Physik-basierte Metriken"""
        # z_prox: Nähe zum "Nullpunkt" (minimale Aktivität)
        activity = (result.A + result.B + result.arousal) / 3
        result.z_prox = 1 - activity
        
        # x_fm_prox: Fernmodus-Proximität (distanziert, analytisch)
        analytical_markers = ["analyse", "betrachten", "objektiv", "neutral",
                             "logisch", "rational", "abstrakt"]
        fm_score = sum(1 for m in analytical_markers if m in text.lower())
        result.x_fm_prox = min(1.0, fm_score / 3)
        
        # Shannon-Entropie des Textes
        if text:
            char_freq = {}
            for c in text.lower():
                char_freq[c] = char_freq.get(c, 0) + 1
            total = len(text)
            entropy = -sum((f/total) * math.log2(f/total) 
                          for f in char_freq.values() if f > 0)
            # Normalisieren auf [0, 1] (max Entropie für Alphabet ~4.7)
            result.S_entropy = min(1.0, entropy / 4.7)
    
    def _calc_gradients(self, result: MetricResult, 
                        prev_result: Optional[MetricResult]):
        """Gradienten-Berechnung (zeitliche Änderung)"""
        if prev_result is None:
            result.grad_A = 0.0
            result.grad_B = 0.0
            result.volatility = 0.0
            return
        
        # Einfache Differenz (dt = 1)
        result.grad_A = result.A - prev_result.A
        result.grad_B = result.B - prev_result.B
        
        # Volatilität: Absolute Änderungsrate über mehrere Metriken
        changes = [
            abs(result.A - prev_result.A),
            abs(result.B - prev_result.B),
            abs(result.flow - prev_result.flow),
            abs(result.coh - prev_result.coh),
            abs(result.valence - prev_result.valence),
        ]
        result.volatility = sum(changes) / len(changes)
    
    def _calc_f_risk(self, result: MetricResult):
        """
        F-Risk Score: Kombinierter Risiko-Score nach A29 Guardian.
        Bewertet Notwendigkeit für Intervention.
        """
        components = {}
        
        # Trauma-Komponente (40%)
        trauma_score = (result.T_panic * 0.4 + 
                       result.T_disso * 0.35 + 
                       result.T_shock * 0.25)
        components['trauma'] = trauma_score
        
        # Loop-Risiko (20%)
        components['loop'] = result.ZLF
        
        # Kohärenz-Verlust (15%)
        components['incoherence'] = 1 - result.coh
        
        # Extreme Emotionen (15%)
        components['emotional'] = abs(result.valence) * result.arousal
        
        # Integration-Verlust (10%)
        components['fragmentation'] = 1 - result.T_integ
        
        # Gewichtete Summe
        result.F_risk = (0.40 * components['trauma'] +
                        0.20 * components['loop'] +
                        0.15 * components['incoherence'] +
                        0.15 * components['emotional'] +
                        0.10 * components['fragmentation'])
        
        result.F_components = components
    
    def _determine_evolution_form(self, result: MetricResult):
        """Bestimmt die Evolutionsform basierend auf Metriken"""
        # Prioritätsbasierte Regeln
        
        # 1. GUARDIAN - Höchste Priorität bei kritischem F-Risk
        if result.F_risk >= 0.85:
            result.evo_form = "GUARDIAN"
            result.evo_confidence = result.F_risk
            return
        
        # 2. TRAUMA_RESPONSE
        if result.T_panic >= 0.7 or result.T_disso >= 0.7:
            result.evo_form = "TRAUMA_RESPONSE"
            result.evo_confidence = max(result.T_panic, result.T_disso)
            return
        
        # 3. LOOP_BREAK
        if result.ZLF >= 0.7:
            result.evo_form = "LOOP_BREAK"
            result.evo_confidence = result.ZLF
            return
        
        # 4. INTEGRATION
        if result.T_integ >= 0.7 and result.coh >= 0.6:
            result.evo_form = "INTEGRATION"
            result.evo_confidence = (result.T_integ + result.coh) / 2
            return
        
        # 5. EMERGENCE
        if result.A >= 0.7 and result.lambda_depth >= 0.5:
            result.evo_form = "EMERGENCE"
            result.evo_confidence = (result.A + result.lambda_depth) / 2
            return
        
        # 6. ADAPTATION
        if result.volatility >= 0.3 and result.flow >= 0.5:
            result.evo_form = "ADAPTATION"
            result.evo_confidence = (result.volatility + result.flow) / 2
            return
        
        # 7. REFLECTION
        if result.S_self >= 0.5 and result.lambda_depth >= 0.4:
            result.evo_form = "REFLECTION"
            result.evo_confidence = (result.S_self + result.lambda_depth) / 2
            return
        
        # 8. EXPLORATION
        if result.question_count > 0 and result.flow >= 0.5:
            result.evo_form = "EXPLORATION"
            result.evo_confidence = min(1.0, result.question_count * 0.3 + result.flow * 0.4)
            return
        
        # 9. CONSOLIDATION
        if result.coh >= 0.6 and result.rep_cross >= 0.3:
            result.evo_form = "CONSOLIDATION"
            result.evo_confidence = (result.coh + result.rep_cross) / 2
            return
        
        # 10. MAINTENANCE (Standard aktiver Zustand)
        if result.flow >= 0.4 and result.A >= 0.3:
            result.evo_form = "MAINTENANCE"
            result.evo_confidence = (result.flow + result.A) / 2
            return
        
        # 11. DORMANT (niedrige Aktivität)
        if result.A < 0.2 and result.B < 0.2:
            result.evo_form = "DORMANT"
            result.evo_confidence = 1 - (result.A + result.B) / 2
            return
        
        # 12. RESET
        if result.volatility >= 0.5 and result.coh < 0.3:
            result.evo_form = "RESET"
            result.evo_confidence = result.volatility
            return
        
        # 13. UNDEFINED (Fallback)
        result.evo_form = "UNDEFINED"
        result.evo_confidence = 0.5


def metric_result_to_dict(result: MetricResult) -> Dict:
    """Konvertiert MetricResult zu Dictionary für DB-Speicherung"""
    return {
        'msg_id': result.msg_id,
        'A': result.A,
        'A_raw': result.A_raw,
        'A_confidence': result.A_confidence,
        'B': result.B,
        'B_raw': result.B_raw,
        'grad_A': result.grad_A,
        'grad_B': result.grad_B,
        'flow': result.flow,
        'coh': result.coh,
        'rep_same': result.rep_same,
        'rep_cross': result.rep_cross,
        'ZLF': result.ZLF,
        'ZLF_pattern': result.ZLF_pattern,
        'LL': result.LL,
        'z_prox': result.z_prox,
        'x_fm_prox': result.x_fm_prox,
        'lambda_depth': result.lambda_depth,
        'S_entropy': result.S_entropy,
        'S_self': result.S_self,
        'T_panic': result.T_panic,
        'T_disso': result.T_disso,
        'T_integ': result.T_integ,
        'T_shock': result.T_shock,
        'F_risk': result.F_risk,
        'X_exist': result.X_exist,
        'valence': result.valence,
        'arousal': result.arousal,
        'word_count': result.word_count,
        'sentence_count': result.sentence_count,
        'avg_word_length': result.avg_word_length,
        'question_count': result.question_count,
        'exclamation_count': result.exclamation_count,
        'volatility': result.volatility,
        'evo_form': result.evo_form,
        'evo_confidence': result.evo_confidence,
    }
