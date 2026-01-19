"""
Evoki V3.0 - Enforcement Gates (Phase 2)

Double Airlock System:
- Gate A: Pre-Prompt Validation (BEFORE LLM call)
- Gate B: Post-Response Validation (AFTER LLM, BEFORE user)

Regelwerk V12 Integration:
- A51: CRC32 Genesis Anchor  
- A7.5/A29: Guardian-Veto (Trauma-Detection)
- A39: Krisenprompt-Erkennung
- A0: Direktive der Wahrheit (Halluzination)
- A46: Soul-Signature Check

Phase 2: All Gates operational except CRC32 (hardcoded for now)
"""

from typing import Dict, List, Optional
import hashlib
from dataclasses import dataclass
from pathlib import Path
import sys

# Import robustly (works with PYTHONPATH=backend and with package-style runs)
try:
    from core.genesis_anchor import validate_full_integrity
except ImportError:  # fallback when backend is a package
    from backend.core.genesis_anchor import validate_full_integrity




# =============================================================================
# INTEGRITY LOCKDOWN STATE (V3.0)
# =============================================================================

# Global Lockdown State
_INTEGRITY_LOCKDOWN = False
_LOCKDOWN_REASON = None


def set_lockdown(reason: str):
    """
    Setzt System in Lockdown-Modus (A51).
    
    Args:
        reason: Grund für Lockdown (Integrity Breach Details)
    """
    global _INTEGRITY_LOCKDOWN, _LOCKDOWN_REASON
    _INTEGRITY_LOCKDOWN = True
    _LOCKDOWN_REASON = reason
    
    print(f"\n⚠️ INTEGRITY LOCKDOWN ACTIVATED!")
    print(f"   Reason: {reason}")
    print(f"   All interactions blocked.\n")
    
    # Log in integrity.db
    try:
        try:
            from core.integrity_db import log_breach
        except ImportError:
            from backend.core.integrity_db import log_breach
        log_breach("LOCKDOWN", reason)
    except Exception as e:
        print(f"   ⚠️ Failed to log breach: {e}")


def is_lockdown() -> tuple:
    """
    Prüft Lockdown-Status.
    
    Returns:
        (is_locked, reason): Tuple
    """
    return _INTEGRITY_LOCKDOWN, _LOCKDOWN_REASON


# =============================================================================
# CRISIS DETECTION
# =============================================================================

CRISIS_KEYWORDS_GATE = [
    "sterben", "suizid", "umbringen", "selbstmord", "töten",
    "will sterben", "nicht mehr leben", "ende machen",
    "aufhören zu leben", "besser ohne mich", "allen zur last"
]


def detect_crisis_prompt(prompt: str) -> Optional[str]:
    """
    A39: Krisenprompt-Erkennung
    
    Returns:
        Detected keyword if crisis, None otherwise
    """
    prompt_lower = prompt.lower()
    
    for keyword in CRISIS_KEYWORDS_GATE:
        if keyword in prompt_lower:
            return keyword
    
    return None


# =============================================================================
# RULE werkV12 CRC32 CHECK
# =============================================================================

def validate_crc32(expected_crc: int = 3246342384) -> bool:
    """
    A51: Genesis Anchor CRC32 Check
    
    Phase 2: Hardcoded (no actual regelwerk file yet)
    Phase 3+: Load actual regelwerk_v12.json and verify
    
    Args:
        expected_crc: Expected CRC32 value (3246342384 for V12)
    
    Returns:
        True if valid (Phase 2: always True)
    """
    # TODO Phase 3: Load and verify actual regelwerk_v12.json
    # For now: Always pass (skeleton mode)
    return True


# =============================================================================
# GATE A: PRE-PROMPT VALIDATION
# =============================================================================

@dataclass
class GateResult:
    """Result from a Gate check"""
    passed: bool
    gate: str  # "A" or "B"
    veto_reasons: List[str]
    rule_violations: List[str]  # Which rules were violated


def gate_a_validation(prompt: str, metrics: Dict[str, float]) -> GateResult:
    """
    GATE A: Pre-Prompt Validation (V3.0 Full Integrity).
    
    Checks BEFORE sending prompt to LLM:
    0. INTEGRITY LOCKDOWN: System gesperrt?
    1. A51: FULL Integrity (Genesis + Registry + Combined SHA256)
    2. A7.5/A29: Guardian-Veto (T_panic > 0.8 or F_risk > 0.6)
    3. A39: Krisenprompt-Erkennung
    
    Args:
        prompt: User input text
        metrics: Calculated metrics dictionary
    
    Returns:
        GateResult with passed=True if all checks pass
    """
    veto_reasons = []
    rule_violations = []
    
    # Check 0: INTEGRITY LOCKDOWN (höchste Priorität!)
    lockdown, reason = is_lockdown()
    if lockdown:
        return GateResult(
            passed=False,
            gate="A",
            veto_reasons=[f"INTEGRITY LOCKDOWN: {reason}"],
            rule_violations=["A51"]
        )
    
    # Check 1: A51 FULL Integrity (V3.0 Production)
    integrity_result = validate_full_integrity(strict=True)
    
    if not integrity_result["verified"]:
        # LOCKDOWN auslösen!
        error_msg = integrity_result.get("error", "Unknown integrity breach")
        set_lockdown(error_msg)
        
        # Log breach mit ALLEN Details
        try:
            try:
                from core.integrity_db import log_breach
            except ImportError:
                from backend.core.integrity_db import log_breach
            
            checks = integrity_result.get("checks", {})
            if not checks.get("genesis_ok"):
                log_breach("GENESIS_BREACH", error_msg, integrity_result)
            if checks.get("registry_ok") is False:
                log_breach("REGISTRY_BREACH", error_msg, integrity_result)
            if checks.get("combined_ok") is False:
                log_breach("COMBINED_BREACH", error_msg, integrity_result)
        except Exception as e:
            print(f"⚠️ Failed to log breach: {e}")
        
        return GateResult(
            passed=False,
            gate="A",
            veto_reasons=[error_msg],
            rule_violations=["A51"]
        )
    
    # Check 2: A7.5 Guardian-Veto (T_panic)
    if metrics.get('T_panic', 0) > 0.8:
        veto_reasons.append(f"Guardian-Veto: T_panic = {metrics['T_panic']:.2f} > 0.8")
        rule_violations.append("A7.5")
    
    # Check 3: A29 Wächter (F_risk)
    if metrics.get('F_risk', 0) > 0.6:
        veto_reasons.append(f"Wächter: F_risk = {metrics['F_risk']:.2f} > 0.6")
        rule_violations.append("A29")
    
    # Check 4: A39 Krisenprompt
    crisis_keyword = detect_crisis_prompt(prompt)
    if crisis_keyword:
        veto_reasons.append(f"Krisenprompt erkannt: '{crisis_keyword}'")
        rule_violations.append("A39")
    
    return GateResult(
        passed=len(veto_reasons) == 0,
        gate="A",
        veto_reasons=veto_reasons,
        rule_violations=rule_violations
    )


# =============================================================================
# GATE B: POST-RESPONSE VALIDATION
# =============================================================================

def check_hallucination(response: str, faiss_chunks: List[str]) -> bool:
    """
    A0: Direktive der Wahrheit - Halluzination Check
    
    Phase 2: Simplified check (response length vs context)
    Phase 3+: Semantic similarity check between response and chunks
    
    Returns:
        True if hallucination detected
    """
    # Phase 2 Simplified: If response is much longer than context, might be hallucinating
    if not faiss_chunks:
        return False
    
    response_len = len(response)
    context_len = sum(len(chunk) for chunk in faiss_chunks)
    
    # If response is 3x longer than provided context → suspicious
    if response_len > context_len * 3:
        return True
    
    return False


def gate_b_validation(
    response: str,
    metrics: Dict[str, float],
    faiss_chunks: Optional[List[str]] = None
) -> GateResult:
    """
    GATE B: Post-Response Validation
    
    Checks AFTER LLM generated response, BEFORE showing to user:
    1. A0: Direktive der Wahrheit (Halluzination?)
    2. A46: Soul-Signature (B_align < 0.7?)
    3. A7.5/A29: Re-check Guardian (in case metrics drifted)
    
    Args:
        response: LLM-generated response text
        metrics: Current metrics
        faiss_chunks: FAISS chunks used for context (optional)
    
    Returns:
        GateResult with passed=True if all checks pass
    """
    veto_reasons = []
    rule_violations = []
    
    # Check 1: A0 Halluzination
    if faiss_chunks and check_hallucination(response, faiss_chunks):
        veto_reasons.append("Halluzination erkannt (Response >> Context)")
        rule_violations.append("A0")
    
    # Check 2: A46 Soul-Signature
    if metrics.get('B_align', 0) < 0.7:
        veto_reasons.append(f"Soul-Signature schwach: B_align = {metrics['B_align']:.2f} < 0.7")
        rule_violations.append("A46")
    
    # Check 3: Re-check Guardian (A7.5/A29)
    if metrics.get('T_panic', 0) > 0.8:
        veto_reasons.append(f"Guardian Re-Check: T_panic = {metrics['T_panic']:.2f} > 0.8")
        rule_violations.append("A7.5")
    
    if metrics.get('F_risk', 0) > 0.6:
        veto_reasons.append(f"Wächter Re-Check: F_risk = {metrics['F_risk']:.2f} > 0.6")
        rule_violations.append("A29")
    
    return GateResult(
        passed=len(veto_reasons) == 0,
        gate="B",
        veto_reasons=veto_reasons,
        rule_violations=rule_violations
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def check_both_gates(
    prompt: str,
    response: str,
    metrics: Dict[str, float],
    faiss_chunks: Optional[List[str]] = None
) -> Dict[str, GateResult]:
    """
    Check both Gates A and B
    
    Returns:
        Dict with "gate_a" and "gate_b" results
    """
    return {
        "gate_a": gate_a_validation(prompt, metrics),
        "gate_b": gate_b_validation(response, metrics, faiss_chunks)
    }


def gate_result_to_dict(result: GateResult) -> Dict:
    """Convert GateResult to dictionary for JSON serialization"""
    return {
        "passed": result.passed,
        "gate": result.gate,
        "veto_reasons": result.veto_reasons,
        "rule_violations": result.rule_violations
    }


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("EVOKI V3.0 - ENFORCEMENT GATES TEST")
    print("=" * 80)
    
    # Test Case 1: Normal prompt
    print("\n" + "─" * 80)
    print("Test 1: Normal prompt")
    print("─" * 80)
    
    metrics_normal = {
        "A": 0.7,
        "T_panic": 0.1,
        "F_risk": 0.2,
        "B_align": 0.85
    }
    
    gate_a = gate_a_validation("Ich fühle mich heute gut", metrics_normal)
    print(f"\nGate A: {'✅ PASS' if gate_a.passed else '🔴 VETO'}")
    if gate_a.veto_reasons:
        for reason in gate_a.veto_reasons:
            print(f"  - {reason}")
    
    # Test Case 2: Crisis prompt
    print("\n" + "─" * 80)
    print("Test 2: Crisis prompt")
    print("─" * 80)
    
    metrics_crisis = {
        "A": 0.3,
        "T_panic": 0.9,
        "F_risk": 0.8,
        "B_align": 0.5
    }
    
    gate_a = gate_a_validation("Ich will sterben", metrics_crisis)
    print(f"\nGate A: {'✅ PASS' if gate_a.passed else '🔴 VETO'}")
    if gate_a.veto_reasons:
        print("Veto Reasons:")
        for reason in gate_a.veto_reasons:
            print(f"  - {reason}")
        print(f"\nRule Violations: {', '.join(gate_a.rule_violations)}")
    
    # Test Case 3: Gate B with weak soul-signature
    print("\n" + "─" * 80)
    print("Test 3: Gate B (weak soul-signature)")
    print("─" * 80)
    
    metrics_weak = {
        "A": 0.6,
        "T_panic": 0.1,
        "F_risk": 0.3,
        "B_align": 0.65  # < 0.7!
    }
    
    gate_b = gate_b_validation("Mock response", metrics_weak, faiss_chunks=["chunk1"])
    print(f"\nGate B: {'✅ PASS' if gate_b.passed else '🔴 VETO'}")
    if gate_b.veto_reasons:
        print("Veto Reasons:")
        for reason in gate_b.veto_reasons:
            print(f"  - {reason}")
        print(f"\nRule Violations: {', '.join(gate_b.rule_violations)}")
    
    print("\n" + "=" * 80)
