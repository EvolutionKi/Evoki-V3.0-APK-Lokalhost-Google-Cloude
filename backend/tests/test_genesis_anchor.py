"""
Test Suite for Genesis Anchor SHA256 - Cryptographic Chain Validation

**Purpose:** Comprehensive tests for genesis_anchor.py module

**Test Categories:**
1. Genesis Anchor Verification
2. Chain Hash Computation
3. Tamper Detection
4. Chain Proof Export
5. Error Handling

**Philosophy:** "Test everything that can break" ✅
"""

import pytest
import hashlib
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.evoki_metrics_v3.genesis_anchor import (
    GenesisValidator,
    GENESIS_ANCHOR_SHA256,
    GENESIS_SEED,
    verify_genesis_anchor,
    create_session_validator
)


# =============================================================================
# TEST DATA
# =============================================================================

SAMPLE_METRICS = {
    'm1_A': 0.7523,
    'm2_PCI': 0.6241,
    'm3_gen_index': 0.8132,
    'm4_flow': 0.7891,
    'm5_coh': 0.6543
}

TAMPERED_METRICS = {
    'm1_A': 0.7524,  # Changed!
    'm2_PCI': 0.6241,
    'm3_gen_index': 0.8132,
    'm4_flow': 0.7891,
    'm5_coh': 0.6543
}


# =============================================================================
# TEST: GENESIS ANCHOR VERIFICATION
# =============================================================================

def test_genesis_anchor_format():
    """Genesis Anchor must be 64 hex characters (SHA256)."""
    assert len(GENESIS_ANCHOR_SHA256) == 64, "SHA256 must be 64 hex chars"
    
    # Verify it's valid hexadecimal
    try:
        int(GENESIS_ANCHOR_SHA256, 16)
    except ValueError:
        pytest.fail("Genesis Anchor is not valid hexadecimal")


def test_genesis_anchor_matches_spec():
    """Genesis Anchor must match FINAL7 specification."""
    # From FINAL7 Line 17909
    expected = "bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"
    assert GENESIS_ANCHOR_SHA256 == expected, "Genesis Anchor mismatch with FINAL7"


def test_verify_genesis_anchor_function():
    """verify_genesis_anchor() should confirm validity."""
    result = verify_genesis_anchor()
    
    assert result['valid'] is True
    assert result['actual'] == GENESIS_ANCHOR_SHA256
    assert 'timestamp' in result


# =============================================================================
# TEST: GENESIS VALIDATOR INITIALIZATION
# =============================================================================

def test_validator_creation():
    """GenesisValidator should initialize correctly."""
    validator = GenesisValidator()
    
    assert validator.genesis_anchor == GENESIS_ANCHOR_SHA256
    assert len(validator.genesis_anchor) == 64


def test_validator_custom_anchor():
    """GenesisValidator should accept custom anchor."""
    custom = "a" * 64  # Valid hex
    validator = GenesisValidator(genesis_anchor=custom)
    
    assert validator.genesis_anchor == custom


def test_validator_invalid_anchor_length():
    """GenesisValidator should reject invalid anchor length."""
    with pytest.raises(ValueError, match="64 hex chars"):
        GenesisValidator(genesis_anchor="abc123")


def test_validator_invalid_anchor_format():
    """GenesisValidator should reject non-hex anchor."""
    invalid = "z" * 64  # Not hex
    with pytest.raises(ValueError, match="valid hexadecimal"):
        GenesisValidator(genesis_anchor=invalid)


# =============================================================================
# TEST: CHAIN HASH COMPUTATION
# =============================================================================

def test_compute_chain_hash_deterministic():
    """Chain hash must be deterministic (same input = same output)."""
    validator = GenesisValidator()
    
    hash1 = validator.compute_chain_hash(SAMPLE_METRICS)
    hash2 = validator.compute_chain_hash(SAMPLE_METRICS)
    
    assert hash1 == hash2, "Chain hash is not deterministic!"
    assert len(hash1) == 64, "Chain hash must be SHA256 (64 hex)"


def test_compute_chain_hash_format():
    """Chain hash must be valid SHA256."""
    validator = GenesisValidator()
    chain_hash = validator.compute_chain_hash(SAMPLE_METRICS)
    
    assert len(chain_hash) == 64
    
    # Verify it's valid hex
    try:
        int(chain_hash, 16)
    except ValueError:
        pytest.fail("Chain hash is not valid hexadecimal")


def test_compute_chain_hash_missing_metric():
    """Should raise ValueError if metric is missing."""
    validator = GenesisValidator()
    
    incomplete_metrics = {'m1_A': 0.75}  # Missing m2-m5
    
    with pytest.raises(ValueError, match="Missing metric"):
        validator.compute_chain_hash(incomplete_metrics)


def test_compute_chain_hash_custom_order():
    """Should support custom metric order."""
    validator = GenesisValidator()
    
    # Reverse order
    custom_order = ['m5_coh', 'm4_flow', 'm3_gen_index', 'm2_PCI', 'm1_A']
    
    hash1 = validator.compute_chain_hash(SAMPLE_METRICS, ordered_keys=custom_order)
    hash2 = validator.compute_chain_hash(SAMPLE_METRICS, ordered_keys=custom_order)
    
    assert hash1 == hash2, "Custom order should be deterministic"
    
    # Different order = different hash
    default_hash = validator.compute_chain_hash(SAMPLE_METRICS)
    assert hash1 != default_hash, "Different order should give different hash"


# =============================================================================
# TEST: METRIC VALIDATION
# =============================================================================

def test_validate_metrics_success():
    """Validation should succeed with correct metrics."""
    validator = GenesisValidator()
    result = validator.validate_metrics(SAMPLE_METRICS)
    
    assert result['valid'] is True
    assert 'chain_hash' in result
    assert result['metrics_count'] == 5
    assert result['verdict'].startswith('SECURE')
    assert 'timestamp' in result


def test_validate_metrics_with_expected_hash():
    """Validation should verify against expected hash."""
    validator = GenesisValidator()
    
    # Compute expected hash
    expected_hash = validator.compute_chain_hash(SAMPLE_METRICS)
    
    # Validate with same hash
    result = validator.validate_metrics(SAMPLE_METRICS, expected_hash=expected_hash)
    
    assert result['valid'] is True
    assert result['chain_hash'] == expected_hash
    assert 'matches expected hash' in result['verdict']


def test_validate_metrics_tampered_detection():
    """Validation should fail with tampered metrics."""
    validator = GenesisValidator()
    
    # Compute original hash
    original_hash = validator.compute_chain_hash(SAMPLE_METRICS)
    
    # Validate tampered metrics against original hash
    result = validator.validate_metrics(TAMPERED_METRICS, expected_hash=original_hash)
    
    assert result['valid'] is False
    assert result['chain_hash'] != original_hash
    assert 'TAMPERED' in result['verdict']


# =============================================================================
# TEST: TAMPER DETECTION
# =============================================================================

def test_detect_tampering_no_change():
    """Should not detect tampering if metrics are identical."""
    validator = GenesisValidator()
    
    result = validator.detect_tampering(SAMPLE_METRICS, SAMPLE_METRICS.copy())
    
    assert result['tampered'] is False
    assert result['original_hash'] == result['suspect_hash']
    assert len(result['changed_metrics']) == 0


def test_detect_tampering_actual_tampering():
    """Should detect tampering when metrics change."""
    validator = GenesisValidator()
    
    result = validator.detect_tampering(SAMPLE_METRICS, TAMPERED_METRICS)
    
    assert result['tampered'] is True
    assert result['original_hash'] != result['suspect_hash']
    assert 'm1_A' in result['changed_metrics']
    assert len(result['changed_metrics']) == 1


def test_detect_tampering_multiple_changes():
    """Should detect all changed metrics."""
    validator = GenesisValidator()
    
    multi_tampered = SAMPLE_METRICS.copy()
    multi_tampered['m1_A'] = 0.9999
    multi_tampered['m3_gen_index'] = 0.0001
    
    result = validator.detect_tampering(SAMPLE_METRICS, multi_tampered)
    
    assert result['tampered'] is True
    assert 'm1_A' in result['changed_metrics']
    assert 'm3_gen_index' in result['changed_metrics']
    assert len(result['changed_metrics']) == 2


# =============================================================================
# TEST: CHAIN PROOF EXPORT
# =============================================================================

def test_export_chain_proof_structure():
    """Chain proof should have correct structure."""
    validator = GenesisValidator()
    proof = validator.export_chain_proof(SAMPLE_METRICS)
    
    assert 'genesis_anchor' in proof
    assert 'final_hash' in proof
    assert 'chain_steps' in proof
    assert 'metrics_count' in proof
    assert 'timestamp' in proof
    
    assert proof['metrics_count'] == 5
    assert proof['spec_version'] == 'FINAL7'
    assert proof['book'] == 'Book 1 - Foundation'


def test_export_chain_proof_steps():
    """Chain proof should have correct step count."""
    validator = GenesisValidator()
    proof = validator.export_chain_proof(SAMPLE_METRICS)
    
    # Should have genesis + 5 metrics = 6 steps
    assert len(proof['chain_steps']) == 6
    
    # First step is genesis
    assert proof['chain_steps'][0]['type'] == 'genesis'
    assert proof['chain_steps'][0]['step'] == 0
    
    # Other steps are metrics
    for i in range(1, 6):
        assert proof['chain_steps'][i]['type'] == 'metric'
        assert proof['chain_steps'][i]['step'] == i


def test_export_chain_proof_reproducibility():
    """Chain proof should be reproducible."""
    validator = GenesisValidator()
    
    proof1 = validator.export_chain_proof(SAMPLE_METRICS)
    proof2 = validator.export_chain_proof(SAMPLE_METRICS)
    
    assert proof1['final_hash'] == proof2['final_hash']
    assert len(proof1['chain_steps']) == len(proof2['chain_steps'])


# =============================================================================
# TEST: UTILITY FUNCTIONS
# =============================================================================

def test_create_session_validator():
    """create_session_validator() should return valid instance."""
    validator = create_session_validator()
    
    assert isinstance(validator, GenesisValidator)
    assert validator.genesis_anchor == GENESIS_ANCHOR_SHA256


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================

def test_validate_metrics_with_error():
    """Validation should handle errors gracefully."""
    validator = GenesisValidator()
    
    # Missing metrics
    result = validator.validate_metrics({})
    
    assert result['valid'] is False
    assert 'ERROR' in result['verdict']
    assert 'error' in result


def test_chain_hash_empty_metrics():
    """Should raise error for empty metrics dict."""
    validator = GenesisValidator()
    
    with pytest.raises(ValueError):
        validator.compute_chain_hash({})


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
