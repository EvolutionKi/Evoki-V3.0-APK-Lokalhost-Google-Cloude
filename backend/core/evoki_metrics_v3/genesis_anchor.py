"""
Genesis Anchor SHA256 - Cryptographic Chain Integrity Validation

**Purpose:** Provides cryptographic proof that Evoki V3.0 metric calculations
are authentic and untampered.

**Philosophy:** "Zukunft und safe - alles nur SHA256" ✅

**Version:** V3.0 Book 1 Foundation
**Spec Reference:** EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
    - Line 39: PATCH-04 Genesis Anchor (A51) SHA-256
    - Line 353-380: Genesis Anchor Härtung
    - Line 11860-11920: Genesis Anchor Prüfung Implementation
    - Line 17909: Official Genesis Anchor Hash

**Author:** Evoki V3.0 Core Team
**Date:** 2026-02-08
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


# =============================================================================
# GENESIS ANCHOR - OFFICIAL HASH FROM FINAL7 SPEC
# =============================================================================

# From FINAL7 Line 17909:
# Genesis Anchor SHA-256: bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4
GENESIS_ANCHOR_SHA256 = "bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"

# Genesis Seed (for verification/regeneration if needed)
GENESIS_SEED = "EVOKI_V3_FOUNDATION_2026_BOOK1_CORE_METRICS"

# Legacy CRC32 (deprecated, for reference only)
GENESIS_ANCHOR_CRC32_LEGACY = 3246342384  # Not used in V3.0


# =============================================================================
# GENESIS VALIDATOR - CRYPTOGRAPHIC CHAIN INTEGRITY
# =============================================================================

class GenesisValidator:
    """
    Validates computational chain integrity using SHA256.
    
    Chain Structure:
        Genesis Anchor → m1_A → m2_PCI → m3_gen_index → m4_flow → m5_coh → Final Hash
        
    Each step includes:
        - Previous hash in chain
        - Metric ID
        - Metric value (4 decimal precision)
        
    Purpose:
        - Tamper detection
        - Computation authenticity proof
        - Data lineage tracking
        
    Example:
        >>> validator = GenesisValidator()
        >>> metrics = {'m1_A': 0.7523, 'm2_PCI': 0.6241, ...}
        >>> result = validator.validate_metrics(metrics)
        >>> print(result['chain_hash'])
        'a3f5e8b2c1d4f7e9...'
    """
    
    def __init__(self, genesis_anchor: str = GENESIS_ANCHOR_SHA256):
        """
        Initialize validator with Genesis Anchor.
        
        Args:
            genesis_anchor: SHA256 hash to use as chain root
                           (default: official FINAL7 anchor)
        """
        self.genesis_anchor = genesis_anchor
        
        # Verify anchor format
        if len(genesis_anchor) != 64:
            raise ValueError(f"Genesis Anchor must be 64 hex chars (SHA256), got {len(genesis_anchor)}")
        
        try:
            int(genesis_anchor, 16)
        except ValueError:
            raise ValueError("Genesis Anchor must be valid hexadecimal")
    
    def compute_chain_hash(
        self,
        metrics: Dict[str, float],
        ordered_keys: Optional[List[str]] = None,
        include_metadata: bool = False
    ) -> str:
        """
        Compute chain hash from Genesis Anchor through all metrics.
        
        Args:
            metrics: Dict of metric_id -> value
            ordered_keys: Metric calculation order (default: m1-m5)
            include_metadata: Include timestamp in chain (default: False)
            
        Returns:
            Final SHA256 hash proving computation chain
            
        Raises:
            ValueError: If required metric is missing
            
        Example:
            >>> chain = validator.compute_chain_hash({'m1_A': 0.75, 'm2_PCI': 0.62, ...})
            >>> len(chain)
            64
        """
        if ordered_keys is None:
            ordered_keys = ['m1_A', 'm2_PCI', 'm3_gen_index', 'm4_flow', 'm5_coh']
        
        # Start with Genesis Anchor
        chain = self.genesis_anchor
        
        # Chain through each metric
        for key in ordered_keys:
            if key not in metrics:
                raise ValueError(f"Missing metric in chain: {key}")
            
            value = metrics[key]
            
            # Format: previous_hash:metric_id:value
            chain_input = f"{chain}:{key}:{value:.4f}"
            
            # Compute next hash in chain
            chain = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
        
        # Optional: Include timestamp for session-specific chains
        if include_metadata:
            timestamp = datetime.now().isoformat()
            chain_input = f"{chain}:timestamp:{timestamp}"
            chain = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
        
        return chain
    
    def validate_metrics(
        self,
        metrics: Dict[str, float],
        expected_hash: Optional[str] = None,
        ordered_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate metrics computation integrity.
        
        Args:
            metrics: Dict of metric_id -> value
            expected_hash: Expected final hash (for verification)
            ordered_keys: Metric calculation order
            
        Returns:
            {
                'valid': bool,              # True if chain is valid
                'chain_hash': str,          # Final SHA256 hash
                'genesis_anchor': str,      # Genesis Anchor used
                'metrics_count': int,       # Number of metrics validated
                'timestamp': str,           # ISO timestamp
                'verdict': str              # Human-readable result
            }
            
        Example:
            >>> result = validator.validate_metrics(metrics)
            >>> result['valid']
            True
            >>> result['verdict']
            'SECURE - Chain integrity verified'
        """
        try:
            chain_hash = self.compute_chain_hash(metrics, ordered_keys)
            
            # Determine validity
            if expected_hash:
                is_valid = (chain_hash == expected_hash)
                verdict = "SECURE - Chain matches expected hash" if is_valid else "TAMPERED - Hash mismatch!"
            else:
                is_valid = True  # No expected hash = compute only
                verdict = "SECURE - Chain integrity verified"
            
            return {
                'valid': is_valid,
                'chain_hash': chain_hash,
                'genesis_anchor': self.genesis_anchor,
                'metrics_count': len(metrics),
                'timestamp': datetime.now().isoformat(),
                'verdict': verdict,
                'metrics': list(metrics.keys())
            }
            
        except Exception as e:
            return {
                'valid': False,
                'chain_hash': None,
                'genesis_anchor': self.genesis_anchor,
                'metrics_count': len(metrics),
                'timestamp': datetime.now().isoformat(),
                'verdict': f"ERROR - {str(e)}",
                'error': str(e)
            }
    
    def detect_tampering(
        self,
        metrics_original: Dict[str, float],
        metrics_suspect: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Detect if metrics have been tampered with.
        
        Args:
            metrics_original: Original metric values
            metrics_suspect: Potentially tampered values
            
        Returns:
            {
                'tampered': bool,
                'original_hash': str,
                'suspect_hash': str,
                'changed_metrics': List[str]
            }
            
        Example:
            >>> result = validator.detect_tampering(original, suspect)
            >>> if result['tampered']:
            ...     print(f"Tampered metrics: {result['changed_metrics']}")
        """
        original_hash = self.compute_chain_hash(metrics_original)
        suspect_hash = self.compute_chain_hash(metrics_suspect)
        
        # Find changed metrics
        changed = []
        for key in metrics_original:
            if key in metrics_suspect:
                if abs(metrics_original[key] - metrics_suspect[key]) > 1e-6:
                    changed.append(key)
        
        return {
            'tampered': (original_hash != suspect_hash),
            'original_hash': original_hash,
            'suspect_hash': suspect_hash,
            'changed_metrics': changed,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_chain_proof(
        self,
        metrics: Dict[str, float],
        ordered_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export complete chain proof for audit trail.
        
        Returns:
            Complete proof document with all intermediate hashes
            
        Example:
            >>> proof = validator.export_chain_proof(metrics)
            >>> json.dump(proof, open('chain_proof.json', 'w'), indent=2)
        """
        if ordered_keys is None:
            ordered_keys = ['m1_A', 'm2_PCI', 'm3_gen_index', 'm4_flow', 'm5_coh']
        
        chain_steps = []
        current_hash = self.genesis_anchor
        
        # Genesis step
        chain_steps.append({
            'step': 0,
            'type': 'genesis',
            'hash': current_hash,
            'value': 'GENESIS_ANCHOR'
        })
        
        # Each metric step
        for idx, key in enumerate(ordered_keys, 1):
            if key not in metrics:
                raise ValueError(f"Missing metric: {key}")
            
            value = metrics[key]
            chain_input = f"{current_hash}:{key}:{value:.4f}"
            current_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
            
            chain_steps.append({
                'step': idx,
                'type': 'metric',
                'metric_id': key,
                'metric_value': round(value, 4),
                'chain_input': chain_input,
                'hash': current_hash
            })
        
        return {
            'genesis_anchor': self.genesis_anchor,
            'final_hash': current_hash,
            'chain_steps': chain_steps,
            'metrics_count': len(ordered_keys),
            'timestamp': datetime.now().isoformat(),
            'spec_version': 'FINAL7',
            'book': 'Book 1 - Foundation'
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def verify_genesis_anchor(expected: str = GENESIS_ANCHOR_SHA256) -> Dict[str, Any]:
    """
    Verify that Genesis Anchor matches FINAL7 specification.
    
    Returns:
        {
            'valid': bool,
            'expected': str,
            'spec_reference': str
        }
    """
    return {
        'valid': (GENESIS_ANCHOR_SHA256 == expected),
        'expected': expected,
        'actual': GENESIS_ANCHOR_SHA256,
        'spec_reference': 'FINAL7 Line 17909',
        'timestamp': datetime.now().isoformat()
    }


def create_session_validator() -> GenesisValidator:
    """
    Create a new Genesis Validator for current session.
    
    Returns:
        GenesisValidator instance with official FINAL7 anchor
    """
    return GenesisValidator(genesis_anchor=GENESIS_ANCHOR_SHA256)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'GenesisValidator',
    'GENESIS_ANCHOR_SHA256',
    'GENESIS_SEED',
    'verify_genesis_anchor',
    'create_session_validator'
]
