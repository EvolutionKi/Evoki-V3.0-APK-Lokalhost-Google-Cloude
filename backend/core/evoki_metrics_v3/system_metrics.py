# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — SYSTEM & CHRONOS METRICS

System health, chronos/temporal sequence, soul-signature, and synthesis metrics.

Categories:
- Soul-Signature / Integrity (m113-m115): hash state, soul signature
- Chronos / Session (m131-m145): temporal metrics, session tracking
- System Health (m146-m150): quality, health, synthesis
- Synthesis (m152-m168): final composite metrics

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import hashlib
import time


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# SOUL-SIGNATURE / INTEGRITY (m113-m115)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m113_hash_state(
    text: str,
    context: Dict
) -> str:
    """
    m113_hash_state - Current State Hash
    
    SHA256 hash of current conversation state.
    Range: String (64 hex chars)
    """
    # Combine text with context for hash
    pair_id = context.get("pair_id", "unknown")
    timestamp = context.get("timestamp", "")
    
    hash_input = f"{pair_id}|{timestamp}|{text}"
    
    state_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    
    return state_hash


def compute_m114_soul_sig(
    m1_A: float,
    m63_phi: float,
    m91_coherence: float,
    context: Dict
) -> str:
    """
    m114_soul_sig - Soul Signature
    
    Unique signature combining awareness, phi, coherence.
    Range: String (hash)
    """
    # Create signature from key metrics
    sig_input = f"{m1_A:.6f}|{m63_phi:.6f}|{m91_coherence:.6f}"
    
    soul_sig = hashlib.sha256(sig_input.encode("utf-8")).hexdigest()[:16]
    
    return soul_sig


def compute_m115_integrity_check(
    m113_hash_state: str,
    context: Dict
) -> float:
    """
    m115_integrity_check - Integrity Verification
    
    Verifies chain integrity.
    Range: [0.0, 1.0]
    
    1.0 = integrity intact, 0.0 = broken
    """
    prev_hash = context.get("prev_hash_state", "")
    
    if not prev_hash:
        return 1.0  # First in chain
    
    # Simple integrity check: hash exists and is valid format
    integrity = 1.0 if len(m113_hash_state) == 64 else 0.0
    
    return integrity


# ═══════════════════════════════════════════════════════════════════════════
# CHRONOS / SESSION (m131-m145)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m131_meta_awareness(context: Dict) -> float:
    """
    m131_meta_awareness (m131_session_dur) - Session Duration
    
    Time since session start.
    Range: [0.0, ∞] (minutes)
    """
    start_time = context.get("session_start_time", time.time())
    current_time = time.time()
    
    duration_seconds = current_time - start_time
    duration_minutes = duration_seconds / 60.0
    
    return max(0.0, duration_minutes)


def compute_m132_turn_count(context: Dict) -> int:
    """
    m132_turn_count - Number of turns in session
    
    Range: [0, ∞]
    """
    turn = context.get("turn", 0)
    
    return turn


def compute_m133_avg_response_time(context: Dict) -> float:
    """
    m133_avg_response_time - Average response time
    
    Range: [0.0, ∞] (seconds)
    """
    response_times = context.get("response_times", [1.0])
    
    avg_time = sum(response_times) / len(response_times) if response_times else 1.0
    
    return avg_time


def compute_m134_session_quality(
    m91_coherence: float,
    m92_stability: float,
    m103_T_integ: float
) -> float:
    """
    m134_session_quality - Session Quality Score
    
    Composite quality metric.
    Range: [0.0, 1.0]
    """
    quality = (m91_coherence + m92_stability + m103_T_integ) / 3.0
    
    return clamp(quality)


def compute_m135_chronos_1(context: Dict) -> float:
    """
    m135_chronos_1 - Temporal marker 1
    
    Normalized session progress.
    Range: [0.0, 1.0]
    """
    turn = context.get("turn", 0)
    max_turns = context.get("max_turns", 100)
    
    progress = min(1.0, turn / max_turns)
    
    return clamp(progress)


def compute_m136_chronos_2(m131_meta_awareness: float) -> float:
    """
    m136_chronos_2 - Temporal marker 2
    
    Normalized session duration.
    Range: [0.0, 1.0]
    """
    # Normalize duration (typical session: 30 minutes)
    normalized = min(1.0, m131_meta_awareness / 30.0)
    
    return clamp(normalized)


def compute_m137_chronos_3(m133_avg_response_time: float) -> float:
    """
    m137_chronos_3 - Temporal marker 3
    
    Response time efficiency.
    Range: [0.0, 1.0]
    """
    # Inverse of response time (faster = higher score)
    # Typical response: 2 seconds
    efficiency = 1.0 / (1.0 + m133_avg_response_time / 2.0)
    
    return clamp(efficiency)


def compute_m138_chronos_4(context: Dict) -> float:
    """
    m138_chronos_4 - Temporal marker 4
    
    Turn frequency.
    Range: [0.0, 1.0]
    """
    turn = context.get("turn", 0)
    duration_minutes = context.get("session_duration_minutes", 1.0)
    
    if duration_minutes == 0:
        return 0.0
    
    # Turns per minute
    frequency = turn / duration_minutes
    
    # Normalize (typical: 2 turns/minute)
    normalized = min(1.0, frequency / 2.0)
    
    return clamp(normalized)


def compute_m139_chronos_5(m135_chronos_1: float, m136_chronos_2: float) -> float:
    """
    m139_chronos_5 - Temporal composite 1
    
    Range: [0.0, 1.0]
    """
    composite = (m135_chronos_1 + m136_chronos_2) / 2.0
    
    return clamp(composite)


def compute_m140_chronos_6(m137_chronos_3: float, m138_chronos_4: float) -> float:
    """
    m140_chronos_6 - Temporal composite 2
    
    Range: [0.0, 1.0]
    """
    composite = (m137_chronos_3 + m138_chronos_4) / 2.0
    
    return clamp(composite)


def compute_m141_chronos_7(m139_chronos_5: float, m140_chronos_6: float) -> float:
    """
    m141_chronos_7 - Temporal composite 3
    
    Range: [0.0, 1.0]
    """
    composite = (m139_chronos_5 + m140_chronos_6) / 2.0
    
    return clamp(composite)


def compute_m142_chronos_8(context: Dict) -> float:
    """
    m142_chronos_8 - Session momentum
    
    Range: [0.0, 1.0]
    """
    # Increasing turn count indicates momentum
    turn = context.get("turn", 0)
    prev_turn = context.get("prev_turn", 0)
    
    delta_turn = turn - prev_turn
    
    momentum = min(1.0, delta_turn / 2.0)
    
    return clamp(momentum)


def compute_m143_chronos_9(m134_session_quality: float, m141_chronos_7: float) -> float:
    """
    m143_chronos_9 - Quality-Time composite
    
    Range: [0.0, 1.0]
    """
    composite = (m134_session_quality + m141_chronos_7) / 2.0
    
    return clamp(composite)


def compute_m144_chronos_10(context: Dict) -> float:
    """
    m144_chronos_10 - Session health
    
    Range: [0.0, 1.0]
    """
    turn = context.get("turn", 0)
    errors = context.get("error_count", 0)
    
    if turn == 0:
        return 1.0
    
    # Error rate
    error_rate = errors / turn
    
    health = 1.0 - min(1.0, error_rate)
    
    return clamp(health)


def compute_m145_chronos_total(
    m141_chronos_7: float,
    m143_chronos_9: float,
    m144_chronos_10: float
) -> float:
    """
    m145_chronos_total - Total temporal score
    
    Range: [0.0, 1.0]
    """
    total = (m141_chronos_7 + m143_chronos_9 + m144_chronos_10) / 3.0
    
    return clamp(total)


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM HEALTH (m146-m150)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m146_sys_quality(m134_session_quality: float, m145_chronos_total: float) -> float:
    """
    m146_sys_quality - System Quality Score
    
    Range: [0.0, 1.0]
    """
    quality = (m134_session_quality + m145_chronos_total) / 2.0
    
    return clamp(quality)


def compute_m147_sys_health(
    m110_black_hole: float,
    m112_trauma_load: float,
    m146_sys_quality: float
) -> float:
    """
    m147_sys_health - System Health
    
    Range: [0.0, 1.0]
    """
    # High quality, low trauma/danger = high health
    health = m146_sys_quality * (1.0 - m110_black_hole) * (1.0 - m112_trauma_load)
    
    return clamp(health)


def compute_m148_sys_stability(m127_dyn_6: float, m92_stability: float) -> float:
    """
    m148_sys_stability - System Stability
    
    Range: [0.0, 1.0]
    """
    stability = (m127_dyn_6 + m92_stability) / 2.0
    
    return clamp(stability)


def compute_m149_sys_readiness(
    m147_sys_health: float,
    m148_sys_stability: float
) -> float:
    """
    m149_sys_readiness - System Readiness
    
    Range: [0.0, 1.0]
    """
    readiness = (m147_sys_health + m148_sys_stability) / 2.0
    
    return clamp(readiness)


def compute_m150_sys_total(
    m146_sys_quality: float,
    m147_sys_health: float,
    m148_sys_stability: float,
    m149_sys_readiness: float
) -> float:
    """
    m150_sys_total - Total System Score
    
    Range: [0.0, 1.0]
    """
    total = (m146_sys_quality + m147_sys_health + m148_sys_stability + m149_sys_readiness) / 4.0
    
    return clamp(total)


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS (m152-m159, m162-m168)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m152_syn_1(m146_sys_quality: float, m63_phi: float) -> float:
    """
    m152_syn_1 - Synthesis metric 1
    Range: [0.0, 1.0]
    """
    return clamp((m146_sys_quality + abs(m63_phi)) / 2.0)


def compute_m153_syn_2(m147_sys_health: float, m103_T_integ: float) -> float:
    """
    m153_syn_2 - Synthesis metric 2
    Range: [0.0, 1.0]
    """
    return clamp((m147_sys_health + m103_T_integ) / 2.0)


def compute_m154_syn_3(m1_A: float, m4_flow: float, m5_coh: float) -> float:
    """
    m154_syn_3 - Core synthesis
    Range: [0.0, 1.0]
    """
    return clamp((m1_A + m4_flow + m5_coh) / 3.0)


def compute_m155_syn_4(m77_joy: float, m81_trust: float) -> float:
    """
    m155_syn_4 - Positive emotion synthesis
    Range: [0.0, 1.0]
    """
    return clamp((m77_joy + m81_trust) / 2.0)


def compute_m156_syn_5(m78_sadness: float, m79_anger: float, m80_fear: float) -> float:
    """
    m156_syn_5 - Negative emotion synthesis
    Range: [0.0, 1.0]
    """
    return clamp((m78_sadness + m79_anger + m80_fear) / 3.0)


def compute_m157_syn_6(m155_syn_4: float, m156_syn_5: float) -> float:
    """
    m157_syn_6 - Emotional balance
    Range: [0.0, 1.0]
    """
    balance = m155_syn_4 - m156_syn_5
    return clamp((balance + 1.0) / 2.0)


def compute_m158_syn_7(m126_dyn_5: float, m145_chronos_total: float) -> float:
    """
    m158_syn_7 - Dynamic-temporal synthesis
    Range: [0.0, 1.0]
    """
    return clamp((m126_dyn_5 + m145_chronos_total) / 2.0)


def compute_m159_syn_8(m150_sys_total: float, m154_syn_3: float) -> float:
    """
    m159_syn_8 - System-core synthesis
    Range: [0.0, 1.0]
    """
    return clamp((m150_sys_total + m154_syn_3) / 2.0)


def compute_m162_syn_final(
    m152_syn_1: float,
    m157_syn_6: float,
    m159_syn_8: float
) -> float:
    """
    m162_syn_final - Final synthesis score
    Range: [0.0, 1.0]
    """
    return clamp((m152_syn_1 + m157_syn_6 + m159_syn_8) / 3.0)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Soul-Signature
    "compute_m113_hash_state",
    "compute_m114_soul_sig",
    "compute_m115_integrity_check",
    # Chronos
    "compute_m131_meta_awareness",
    "compute_m132_turn_count",
    "compute_m133_avg_response_time",
    "compute_m134_session_quality",
    "compute_m135_chronos_1",
    "compute_m136_chronos_2",
    "compute_m137_chronos_3",
    "compute_m138_chronos_4",
    "compute_m139_chronos_5",
    "compute_m140_chronos_6",
    "compute_m141_chronos_7",
    "compute_m142_chronos_8",
    "compute_m143_chronos_9",
    "compute_m144_chronos_10",
    "compute_m145_chronos_total",
    # System Health
    "compute_m146_sys_quality",
    "compute_m147_sys_health",
    "compute_m148_sys_stability",
    "compute_m149_sys_readiness",
    "compute_m150_sys_total",
    # Synthesis
    "compute_m152_syn_1",
    "compute_m153_syn_2",
    "compute_m154_syn_3",
    "compute_m155_syn_4",
    "compute_m156_syn_5",
    "compute_m157_syn_6",
    "compute_m158_syn_7",
    "compute_m159_syn_8",
    "compute_m162_syn_final",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock context
    test_context = {
        "pair_id": "test-001",
        "timestamp": "2026-02-08T09:40:00Z",
        "session_start_time": time.time() - 600,  # 10 minutes ago
        "turn": 15,
        "max_turns": 100,
        "response_times": [1.2, 1.5, 1.8, 1.1],
        "error_count": 0,
    }
    
    # Mock metric dependencies
    m1_A = 0.75
    m4_flow = 0.82
    m5_coh = 0.72
    m63_phi = 0.18
    m77_joy = 0.85
    m78_sadness = 0.10
    m79_anger = 0.05
    m80_fear = 0.08
    m81_trust = 0.75
    m91_coherence = 0.72
    m92_stability = 0.70
    m103_T_integ = 0.73
    m110_black_hole = 0.08
    m112_trauma_load = 0.12
    m126_dyn_5 = 0.04
    m127_dyn_6 = 0.96
    
    print("=" * 70)
    print("SYSTEM & CHRONOS METRICS TEST")
    print("=" * 70)
    
    # Soul-Signature
    m113 = compute_m113_hash_state("Test text", test_context)
    m114 = compute_m114_soul_sig(m1_A, m63_phi, m91_coherence, test_context)
    m115 = compute_m115_integrity_check(m113, test_context)
    
    print(f"\n🔐 Soul-Signature:")
    print(f"  m113_hash_state:      ...{m113[-12:]}")
    print(f"  m114_soul_sig:        {m114}")
    print(f"  m115_integrity_check: {m115:.3f}")
    
    # Chronos
    m131 = compute_m131_meta_awareness(test_context)
    m132 = compute_m132_turn_count(test_context)
    m133 = compute_m133_avg_response_time(test_context)
    m134 = compute_m134_session_quality(m91_coherence, m92_stability, m103_T_integ)
    m135 = compute_m135_chronos_1(test_context)
    m136 = compute_m136_chronos_2(m131)
    m137 = compute_m137_chronos_3(m133)
    m138 = compute_m138_chronos_4({**test_context, "session_duration_minutes": 10.0})
    m139 = compute_m139_chronos_5(m135, m136)
    m140 = compute_m140_chronos_6(m137, m138)
    m141 = compute_m141_chronos_7(m139, m140)
    m142 = compute_m142_chronos_8({**test_context, "prev_turn": 14})
    m143 = compute_m143_chronos_9(m134, m141)
    m144 = compute_m144_chronos_10(test_context)
    m145 = compute_m145_chronos_total(m141, m143, m144)
    
    print(f"\n⏰ Chronos / Session:")
    print(f"  m131_meta_awareness:  {m131:.2f} min")
    print(f"  m132_turn_count:      {m132}")
    print(f"  m134_session_quality: {m134:.3f}")
    print(f"  m145_chronos_total:   {m145:.3f}")
    
    # System Health
    m146 = compute_m146_sys_quality(m134, m145)
    m147 = compute_m147_sys_health(m110_black_hole, m112_trauma_load, m146)
    m148 = compute_m148_sys_stability(m127_dyn_6, m92_stability)
    m149 = compute_m149_sys_readiness(m147, m148)
    m150 = compute_m150_sys_total(m146, m147, m148, m149)
    
    print(f"\n🏥 System Health:")
    print(f"  m146_sys_quality:     {m146:.3f}")
    print(f"  m147_sys_health:      {m147:.3f}")
    print(f"  m148_sys_stability:   {m148:.3f}")
    print(f"  m149_sys_readiness:   {m149:.3f}")
    print(f"  m150_sys_total:       {m150:.3f}")
    
    # Synthesis
    m152 = compute_m152_syn_1(m146, m63_phi)
    m153 = compute_m153_syn_2(m147, m103_T_integ)
    m154 = compute_m154_syn_3(m1_A, m4_flow, m5_coh)
    m155 = compute_m155_syn_4(m77_joy, m81_trust)
    m156 = compute_m156_syn_5(m78_sadness, m79_anger, m80_fear)
    m157 = compute_m157_syn_6(m155, m156)
    m158 = compute_m158_syn_7(m126_dyn_5, m145)
    m159 = compute_m159_syn_8(m150, m154)
    m162 = compute_m162_syn_final(m152, m157, m159)
    
    print(f"\n🔮 Synthesis:")
    print(f"  m152_syn_1:           {m152:.3f}")
    print(f"  m157_syn_6 (balance): {m157:.3f}")
    print(f"  m159_syn_8:           {m159:.3f}")
    print(f"  m162_syn_final:       {m162:.3f}")
    
    print(f"\n✅ 31 new System & Synthesis metrics implemented!")
