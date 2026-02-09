#!/usr/bin/env python3
"""
EVOKI METRIKEN-CALCULATOR V2.0 - SPEC-KONFORM
==============================================

KRITISCHE ÄNDERUNGEN gegenüber V1:

1. Å vs A SAUBER GETRENNT:
   - Å (Ångström) = TIEFE (0-5) aus Lexika (S_self, E_affect, X_exist, B_past)
   - A (A-Score) = AFFEKT-KOHÄRENZ (0-1) aus Dynamik (coh, flow, LL, ZLF)

2. TIMELINE-ECHTE COH/FLOW:
   - flow = exp(-Δt_seconds / 1800)  # Exponentieller Zerfall
   - coh = Jaccard(current_tokens, window_k6_tokens)  # Echte Überlappung

3. F_RISK DOPPELT:
   - Lexikalisch (T_panic, T_disso, Hazard) = erklärbar
   - Embedding-basiert (cos_sim zu F-Vektoren) = präziser

Autor: Architekt + Claude
Version: 2.0.0
Datum: 2025-12-16
"""

import math
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Set
from datetime import datetime
import numpy as np

# Import Lexika
try:
    from lexika.evoki_lexika_v21 import (
        S_SELF, X_EXIST, LAMBDA_DEPTH,
        T_PANIC, T_DISSO, T_INTEG, T_SHOCK_KEYWORDS,
        ZLF_LOOP, FLOW_POSITIVE, FLOW_NEGATIVE,
        COH_CONNECTORS, B_EMPATHY,
        compute_lexicon_score, compute_b_past_with_regex,
        compute_hazard_score, calculate_stt_score
    )
    FULL_LEXIKA = True
except ImportError:
    try:
        from lexika.full_lexika import (
            S_SELF, X_EXIST, LAMBDA_DEPTH,
            T_PANIC, T_DISSO, T_INTEG, T_SHOCK_KEYWORDS,
            ZLF_LOOP, FLOW_POSITIVE, FLOW_NEGATIVE,
            COH_CONNECTORS, B_EMPATHY,
            compute_lexicon_score, compute_b_past_with_regex,
            compute_hazard_score
        )
        FULL_LEXIKA = True
    except ImportError:
        FULL_LEXIKA = False
        print("⚠️  Full Lexika nicht verfügbar, verwende Fallback")


# ============================================================================
# KONSTANTEN
# ============================================================================

TAU_FLOW = 1800.0  # 30 Minuten Halbwertszeit für Flow
WINDOW_K = 6       # Fenster für Kohärenz-Berechnung
COH_THRESHOLD = 0.08  # Kontext-Break Schwelle


# ============================================================================
# DATACLASS
# ============================================================================

@dataclass
class EVOKIMetrics:
    """EVOKI Metriken V2.0 - Spec-konform"""
    
    # TIEFE (Ångström) - 0 bis 5
    angstrom: float = 0.0
    angstrom_components: dict = None  # s_self, e_affect, x_exist, b_past
    
    # AFFEKT-KOHÄRENZ (A-Score) - 0 bis 1
    a_score: float = 0.0
    a_components: dict = None  # coh, flow, LL, ZLF, ctx_break
    
    # FLOW & KOHÄRENZ (Timeline-echt)
    flow: float = 0.5
    flow_gap_seconds: float = 0.0
    coh: float = 0.0
    coh_jaccard: float = 0.0  # Jaccard gegen Window
    ctx_break: int = 0
    
    # TRAUMA (Lexikalisch + Embedding)
    t_panic: float = 0.0
    t_disso: float = 0.0
    t_integ: float = 0.0
    t_shock: int = 0
    
    # F-RISK (Doppelt gefahren)
    f_risk_lexical: float = 0.0  # Aus Lexika
    f_risk_embedding: float = 0.0  # Aus Embeddings
    f_risk: float = 0.0  # Kombiniert
    f_risk_method: str = "hybrid"  # lexical | embedding | hybrid
    
    # ANDERE (wie gehabt)
    b_score: float = 0.0
    pci: float = 0.0
    zlf: float = 0.0
    rep_same: float = 0.0
    rep_cross: float = 0.0
    
    # LEXIKA
    s_self: float = 0.0
    x_exist: float = 0.0
    lambda_depth: float = 0.0
    
    # STATUS
    word_count: int = 0
    lex_diversity: float = 0.0
    timestamp: Optional[datetime] = None


# ============================================================================
# CALCULATOR V2
# ============================================================================

class EVOKICalculatorV2:
    """
    EVOKI Metriken-Calculator V2.0 - Timeline-aware, Spec-konform
    """
    
    def __init__(self, f_vectors: Optional[np.ndarray] = None):
        """
        Args:
            f_vectors: Pre-computed F-Vektoren für Trauma-Erkennung (optional)
        """
        self.history: List[Tuple[str, str, datetime, Set[str]]] = []
        # (speaker, text, timestamp, tokens_set)
        
        self.f_vectors = f_vectors
        self.has_embeddings = f_vectors is not None
    
    def compute(self, 
                text: str, 
                speaker: str = "unknown",
                timestamp: Optional[datetime] = None,
                embedding: Optional[np.ndarray] = None) -> EVOKIMetrics:
        """
        Berechne ALLE Metriken für eine Nachricht
        
        Args:
            text: Nachrichtentext
            speaker: user | assistant
            timestamp: Zeitstempel (für Flow)
            embedding: 386D Embedding (für F-Risk)
        
        Returns:
            EVOKIMetrics mit allen Werten
        """
        result = EVOKIMetrics()
        result.timestamp = timestamp or datetime.now()
        
        if not text:
            return result
        
        # Struktur
        self._compute_structure(result, text)
        
        # Lexika
        self._compute_lexical(result, text)
        
        # Timeline-echte Flow/Coh
        self._compute_flow_coherence(result, text, speaker, timestamp)
        
        # Ångström (TIEFE)
        self._compute_angstrom(result)
        
        # Trauma
        self._compute_trauma(result, text)
        
        # F-Risk (DOPPELT)
        self._compute_f_risk(result, text, embedding)
        
        # Repetition
        self._compute_repetition(result, text, speaker)
        
        # A-Score (AFFEKT-KOHÄRENZ)
        self._compute_a_score(result)
        
        # Update Historie
        tokens = set(text.lower().split())
        self.history.append((speaker, text, result.timestamp, tokens))
        
        return result
    
    # ========================================================================
    # STRUKTUR
    # ========================================================================
    
    def _compute_structure(self, result: EVOKIMetrics, text: str):
        """Basis-Struktur"""
        words = text.split()
        result.word_count = len(words)
        
        if result.word_count > 0:
            unique = set(w.lower() for w in words)
            result.lex_diversity = len(unique) / result.word_count
    
    # ========================================================================
    # LEXIKA
    # ========================================================================
    
    def _compute_lexical(self, result: EVOKIMetrics, text: str):
        """Lexikon-Scores"""
        if not FULL_LEXIKA:
            return
        
        result.s_self, _ = compute_lexicon_score(text, S_SELF)
        result.x_exist, _ = compute_lexicon_score(text, X_EXIST)
        result.lambda_depth, _ = compute_lexicon_score(text, LAMBDA_DEPTH)
    
    # ========================================================================
    # ÄNDERUNG 2: TIMELINE-ECHTE FLOW/COH
    # ========================================================================
    
    def _compute_flow_coherence(self, 
                                 result: EVOKIMetrics, 
                                 text: str, 
                                 speaker: str,
                                 timestamp: Optional[datetime]):
        """
        TIMELINE-ECHTE Flow & Kohärenz
        
        flow = exp(-Δt / τ)  mit τ = 1800s (30min)
        coh = Jaccard(current, window_k6)
        """
        
        # FLOW aus Zeitdifferenz
        if self.history and timestamp:
            prev_ts = self.history[-1][2]
            gap_seconds = (timestamp - prev_ts).total_seconds()
            result.flow_gap_seconds = gap_seconds
            
            # Exponentieller Zerfall
            result.flow = math.exp(-max(0, gap_seconds) / TAU_FLOW)
        else:
            result.flow = 1.0  # Erste Nachricht
        
        # KOHÄRENZ als Jaccard gegen Window
        current_tokens = set(text.lower().split())
        
        if len(self.history) >= 1:
            # Sammle Window der letzten WINDOW_K Nachrichten
            window_tokens = set()
            for i in range(max(0, len(self.history) - WINDOW_K), len(self.history)):
                window_tokens.update(self.history[i][3])
            
            # Jaccard
            if current_tokens and window_tokens:
                intersection = len(current_tokens & window_tokens)
                union = len(current_tokens | window_tokens)
                result.coh_jaccard = intersection / union if union > 0 else 0.0
            
            result.coh = result.coh_jaccard
        else:
            result.coh = 0.0
        
        # Kontext-Break
        result.ctx_break = 1 if result.coh < COH_THRESHOLD else 0
    
    # ========================================================================
    # ÄNDERUNG 1: ÅNGSTRÖM (TIEFE) - SAUBER GETRENNT
    # ========================================================================
    
    def _compute_angstrom(self, result: EVOKIMetrics):
        """
        Ångström = TIEFE (0-5)
        
        Formel aus Spec V11.1:
        Å = 2.0 * S_self + 1.5 * E_affect + 1.0 * X_exist + 0.5 * B_past
        """
        
        # E_affect approximation (falls BERT nicht da)
        e_affect = result.lambda_depth * 0.7  # Placeholder
        
        angstrom = (
            2.0 * result.s_self +
            1.5 * e_affect +
            1.0 * result.x_exist +
            0.5 * 0.0  # B_past (noch nicht implementiert)
        )
        
        result.angstrom = min(5.0, angstrom)
        result.angstrom_components = {
            's_self': result.s_self,
            'e_affect': e_affect,
            'x_exist': result.x_exist,
            'b_past': 0.0
        }
    
    # ========================================================================
    # TRAUMA
    # ========================================================================
    
    def _compute_trauma(self, result: EVOKIMetrics, text: str):
        """Trauma-Vektoren aus Lexika"""
        if not FULL_LEXIKA:
            return
        
        result.t_panic, _ = compute_lexicon_score(text, T_PANIC)
        result.t_disso, _ = compute_lexicon_score(text, T_DISSO)
        result.t_integ, _ = compute_lexicon_score(text, T_INTEG)
        
        # T_shock (binär)
        result.t_shock = 1 if any(kw in text.lower() for kw in T_SHOCK_KEYWORDS) else 0
    
    # ========================================================================
    # ÄNDERUNG 3: F-RISK DOPPELT GEFAHREN
    # ========================================================================
    
    def _compute_f_risk(self, 
                        result: EVOKIMetrics, 
                        text: str,
                        embedding: Optional[np.ndarray]):
        """
        F-Risk DOPPELT gefahren:
        
        1. LEXIKALISCH (erklärbar):
           F_lex = 0.40*T_panic + 0.30*T_disso + 0.20*(1-T_integ) + 0.10*Hazard
        
        2. EMBEDDING-BASIERT (präziser):
           F_emb = max(cos_sim(embedding, f_vector) for f_vector in F_vectors)
        
        3. HYBRID:
           F_risk = 0.6*F_emb + 0.4*F_lex  (wenn Embeddings verfügbar)
        """
        
        # 1. LEXIKALISCH
        if FULL_LEXIKA:
            hazard_score, is_critical, _ = compute_hazard_score(text)
        else:
            hazard_score = 0.0
        
        f_lex = (
            0.40 * result.t_panic +
            0.30 * result.t_disso +
            0.20 * (1.0 - result.t_integ) +
            0.10 * hazard_score
        )
        result.f_risk_lexical = min(1.0, f_lex)
        
        # 2. EMBEDDING-BASIERT
        if embedding is not None and self.f_vectors is not None:
            # Cosine Similarity gegen alle F-Vektoren
            similarities = np.dot(self.f_vectors, embedding)
            result.f_risk_embedding = float(np.max(similarities))
            
            # 3. HYBRID
            result.f_risk = 0.6 * result.f_risk_embedding + 0.4 * result.f_risk_lexical
            result.f_risk_method = "hybrid"
        else:
            # Nur lexikalisch
            result.f_risk = result.f_risk_lexical
            result.f_risk_method = "lexical"
    
    # ========================================================================
    # REPETITION
    # ========================================================================
    
    def _compute_repetition(self, result: EVOKIMetrics, text: str, speaker: str):
        """Repetition (wie gehabt)"""
        current_tokens = set(text.lower().split())
        
        # Same-Speaker
        same_hist = [h for h in self.history if h[0] == speaker]
        if same_hist:
            overlaps = []
            for _, _, _, prev_tokens in same_hist[-5:]:
                if current_tokens and prev_tokens:
                    jaccard = len(current_tokens & prev_tokens) / len(current_tokens | prev_tokens)
                    overlaps.append(jaccard)
            result.rep_same = max(overlaps) if overlaps else 0.0
        
        # Cross-Speaker
        other_hist = [h for h in self.history if h[0] != speaker]
        if other_hist:
            overlaps = []
            for _, _, _, prev_tokens in other_hist[-3:]:
                if current_tokens and prev_tokens:
                    jaccard = len(current_tokens & prev_tokens) / len(current_tokens | prev_tokens)
                    overlaps.append(jaccard)
            result.rep_cross = max(overlaps) if overlaps else 0.0
        
        # ZLF
        zlf_lex = 0.0
        if FULL_LEXIKA and ZLF_LOOP:
            zlf_lex, _ = compute_lexicon_score(text, ZLF_LOOP)
        
        result.zlf = (
            0.50 * zlf_lex +
            0.30 * result.rep_same +
            0.20 * result.rep_cross
        )
    
    # ========================================================================
    # A-SCORE (AFFEKT-KOHÄRENZ) - SAUBER GETRENNT VON Å
    # ========================================================================
    
    def _compute_a_score(self, result: EVOKIMetrics):
        """
        A-Score = AFFEKT-KOHÄRENZ (0-1)
        
        Formel aus Spec:
        A = 0.40*coh + 0.25*flow + 0.20*(1-LL) + 0.10*(1-ZLF) - 0.05*ctx_break
        
        wobei LL = Low-Level Loop (hier approximiert als ZLF)
        """
        
        # LL approximation
        ll = result.zlf  # Vereinfachung
        
        a_score = (
            0.40 * result.coh +
            0.25 * result.flow +
            0.20 * (1.0 - ll) +
            0.10 * (1.0 - result.zlf) -
            0.05 * result.ctx_break
        )
        
        result.a_score = max(0.0, min(1.0, a_score))
        result.a_components = {
            'coh': result.coh,
            'flow': result.flow,
            'LL': ll,
            'ZLF': result.zlf,
            'ctx_break': result.ctx_break
        }


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 EVOKI CALCULATOR V2.0 - SPEC-KONFORM")
    print("=" * 80)
    
    calc = EVOKICalculatorV2()
    
    # Test Messages mit Timestamps
    from datetime import datetime, timedelta
    
    messages = [
        ("user", "Ich fühle mich so leer und wertlos heute.", 
         datetime(2025, 1, 1, 10, 0)),
        ("assistant", "Das klingt sehr schwer. Ich höre dir zu.",
         datetime(2025, 1, 1, 10, 1)),
        ("user", "Ja, es ist schwer. Ich habe auch Angst.",
         datetime(2025, 1, 1, 10, 35)),  # 34min später → niedriger Flow
    ]
    
    print("\n📊 VERGLEICH: Å (Tiefe) vs A (Affekt-Kohärenz)")
    print("-" * 80)
    
    for speaker, text, ts in messages:
        result = calc.compute(text, speaker, ts)
        
        print(f"\n💬 {speaker}: \"{text[:50]}...\"")
        print(f"\n   🎯 TIEFE (Ångström):")
        print(f"      Å = {result.angstrom:.3f}  [0-5]")
        print(f"      ├─ S_self:   {result.angstrom_components['s_self']:.3f}")
        print(f"      ├─ X_exist:  {result.angstrom_components['x_exist']:.3f}")
        print(f"      └─ E_affect: {result.angstrom_components['e_affect']:.3f}")
        
        print(f"\n   💓 AFFEKT-KOHÄRENZ (A-Score):")
        print(f"      A = {result.a_score:.3f}  [0-1]")
        print(f"      ├─ coh:       {result.a_components['coh']:.3f}")
        print(f"      ├─ flow:      {result.a_components['flow']:.3f}  (Δt={result.flow_gap_seconds:.0f}s)")
        print(f"      ├─ ZLF:       {result.a_components['ZLF']:.3f}")
        print(f"      └─ ctx_break: {result.a_components['ctx_break']}")
        
        print(f"\n   ⚠️  TRAUMA & F-RISK:")
        print(f"      F-Risk (lex):  {result.f_risk_lexical:.3f}")
        print(f"      F-Risk (emb):  {result.f_risk_embedding:.3f}")
        print(f"      F-Risk (final):{result.f_risk:.3f}  [{result.f_risk_method}]")
        print(f"      T_panic:       {result.t_panic:.3f}")
        print(f"      T_disso:       {result.t_disso:.3f}")
    
    print("\n" + "=" * 80)
    print("✅ V2.0: Å/A getrennt, Timeline-Flow, F-Risk doppelt")
    print("=" * 80)
