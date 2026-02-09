"""
Core Metrics with Genesis Anchor SHA256 Integration

**Purpose:** Convenience wrapper for calculating core metrics (m1-m5)
           with automatic Genesis Anchor chain validation.

**Usage:**
    ```python
    from core_with_genesis import calculate_core_metrics_validated
    
    result = calculate_core_metrics_validated(
        text="Hello world",
        prev_context="Previous message",
        history=["msg1", "msg2"]
    )
    
    print(result['metrics'])      # {m1_A: 0.75, m2_PCI: 0.62, ...}
    print(result['validation'])   # Genesis chain validation result
    ```

**Version:** V3.0 Book 1
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

# Import core metric calculators
from .calculator_spec_A_PHYS_V11 import (
    compute_m1_A,
    compute_m2_PCI,
    compute_m3_gen_index,
    compute_m4_flow,
    compute_m5_coh
)

# Import Genesis Anchor validator
from .genesis_anchor import GenesisValidator, create_session_validator


def calculate_core_metrics_validated(
    text: str,
    prev_context: str = "",
    history: Optional[List[str]] = None,
    word_frequencies: Optional[Dict[str, int]] = None,
    prev_a: float = 0.5,
    nabla_a_prev: float = 0.0,
    validate_chain: bool = True
) -> Dict[str, Any]:
    """
    Calculate core metrics (m1-m5) with Genesis Anchor validation.
    
    Args:
        text: Current text to analyze
        prev_context: Previous text for integration metrics
        history: List of previous texts for generation index
        word_frequencies: Optional word freq dict for m3 rarity bonus
        prev_a: Previous A score for m1 stability
        nabla_a_prev: Previous A gradient for m1 stability
        validate_chain: Whether to compute Genesis chain (default: True)
        
    Returns:
        {
            'metrics': {
                'm1_A': float,
                'm2_PCI': float,
                'm3_gen_index': float,
                'm4_flow': float,
                'm5_coh': float
            },
            'validation': {
                'valid': bool,
                'chain_hash': str,
                'genesis_anchor': str,
                'verdict': str
            },
            'timestamp': str,
            'text_length': int
        }
        
    Example:
        >>> result = calculate_core_metrics_validated("Hello world")
        >>> result['metrics']['m1_A']
        0.7523
        >>> result['validation']['valid']
        True
    """
    if history is None:
        history = []
    
    # Calculate all core metrics
    metrics = {
        'm1_A': compute_m1_A(text, prev_a, nabla_a_prev),
        'm2_PCI': compute_m2_PCI(text, prev_context),
        'm3_gen_index': compute_m3_gen_index(text, history, word_frequencies),
        'm4_flow': compute_m4_flow(text),
        'm5_coh': compute_m5_coh(text)
    }
    
    # Validate with Genesis Anchor (if enabled)
    if validate_chain:
        validator = create_session_validator()
        validation = validator.validate_metrics(metrics)
    else:
        validation = {
            'valid': None,
            'chain_hash': None,
            'genesis_anchor': None,
            'verdict': 'Validation skipped'
        }
    
    return {
        'metrics': metrics,
        'validation': validation,
        'timestamp': datetime.now().isoformat(),
        'text_length': len(text)
    }


def calculate_core_metrics_simple(text: str) -> Dict[str, float]:
    """
    Simple wrapper: calculate core metrics without validation.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict of metric_id -> value
        
    Example:
        >>> metrics = calculate_core_metrics_simple("Hello")
        >>> metrics['m1_A']
        0.7523
    """
    return {
        'm1_A': compute_m1_A(text),
        'm2_PCI': compute_m2_PCI(text),
        'm3_gen_index': compute_m3_gen_index(text),
        'm4_flow': compute_m4_flow(text),
        'm5_coh': compute_m5_coh(text)
    }


__all__ = [
    'calculate_core_metrics_validated',
    'calculate_core_metrics_simple'
]
