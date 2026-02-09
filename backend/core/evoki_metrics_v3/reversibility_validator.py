"""
EVOKI V3.0 - REVERSIBILITY VALIDATOR
====================================

Validiert dass Metriken in BEIDE Richtungen gleich sind:
- FORWARD:  Text → Metriken (Konstruktion)
- BACKWARD: Metriken → Validation (Rekonstruktion)

Prinzip: x = 1+1+1+1+1 = 5, 5-1-1-1-1-1 = x
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .metrics_calculator_4phase_COMPLETE import MetricsCalculator, MetricsContext


@dataclass
class ValidationResult:
    """Result of reversibility validation"""
    is_valid: bool
    turn_id: int
    errors: List[str]
    drift: Dict[str, float]  # metric_name -> difference
    max_drift: float
    

class ReversibilityValidator:
    """
    Validates that metrics can be reconstructed from stored data
    
    This ensures data integrity across the conversation history.
    """
    
    def __init__(self, db_path: str, tolerance: float = 0.001):
        """
        Args:
            db_path: Path to evoki_v3_core.db
            tolerance: Maximum allowed drift for float comparisons
        """
        self.db_path = db_path
        self.tolerance = tolerance
        self.calculator = MetricsCalculator()
    
    def validate_turn(self, turn_id: int) -> ValidationResult:
        """
        Validate a single turn's metrics
        
        FORWARD:  Load text → Calculate metrics
        BACKWARD: Load stored metrics → Compare
        
        Args:
            turn_id: Turn to validate
            
        Returns:
            ValidationResult with is_valid=True if metrics match
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # LOAD TURN DATA
        cur.execute("""
            SELECT turn_id, role, text, timestamp, gap_seconds
            FROM evoki_core_turns
            WHERE turn_id = ?
        """, (turn_id,))
        
        turn_row = cur.fetchone()
        if not turn_row:
            return ValidationResult(
                is_valid=False,
                turn_id=turn_id,
                errors=[f"Turn {turn_id} not found"],
                drift={},
                max_drift=0.0
            )
        
        text = turn_row['text']
        role = turn_row['role']
        gap_seconds = turn_row['gap_seconds']
        
        # LOAD PREVIOUS METRICS (for gradients)
        prev_metrics = self._load_prev_metrics(cur, turn_id)
        
        # LOAD B-VECTOR
        b_vector = self._load_b_vector(cur, turn_id)
        
        # LOAD Z_PROX HISTORY
        z_prox_history = self._load_z_prox_history(cur, turn_id)
        
        # BUILD CONTEXT
        context = MetricsContext(
            prev_metrics=prev_metrics,
            b_vector=b_vector,
            z_prox_history=z_prox_history,
            gap_seconds=gap_seconds,
            timestamp=turn_row['timestamp']
        )
        
        # ============================================================
        # FORWARD CALCULATION (Konstruktion)
        # ============================================================
        calculated_metrics = self.calculator.calculate_all(
            text=text,
            role=role,
            context=context
        )
        
        # ============================================================
        # BACKWARD VALIDATION (Rekonstruktion)
        # ============================================================
        stored_metrics = self._load_stored_metrics(cur, turn_id)
        
        # COMPARE
        errors = []
        drift = {}
        max_drift = 0.0
        
        for metric_name in calculated_metrics.keys():
            calc_val = calculated_metrics.get(metric_name)
            stored_val = stored_metrics.get(metric_name)
            
            if stored_val is None:
                errors.append(f"{metric_name}: Missing in DB")
                continue
            
            # Skip string comparisons (e.g. m161_commit)
            if isinstance(calc_val, str):
                if calc_val != stored_val:
                    errors.append(f"{metric_name}: '{calc_val}' != '{stored_val}'")
                continue
            
            # Float comparison with tolerance
            diff = abs(calc_val - stored_val)
            if diff > self.tolerance:
                drift[metric_name] = diff
                max_drift = max(max_drift, diff)
                errors.append(
                    f"{metric_name}: Drift {diff:.6f} "
                    f"(calc={calc_val:.4f}, stored={stored_val:.4f})"
                )
        
        conn.close()
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            turn_id=turn_id,
            errors=errors,
            drift=drift,
            max_drift=max_drift
        )
    
    def validate_conversation(self, conversation_id: str) -> List[ValidationResult]:
        """
        Validate entire conversation history
        
        Returns:
            List of ValidationResults, one per turn
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Get all turns in conversation
        cur.execute("""
            SELECT turn_id FROM evoki_core_turns
            WHERE conversation_id = ?
            ORDER BY turn_id ASC
        """, (conversation_id,))
        
        turn_ids = [row[0] for row in cur.fetchall()]
        conn.close()
        
        results = []
        for turn_id in turn_ids:
            result = self.validate_turn(turn_id)
            results.append(result)
        
        return results
    
    def _load_prev_metrics(self, cur, turn_id: int) -> Optional[Dict[str, float]]:
        """Load metrics from previous turn"""
        cur.execute("""
            SELECT m1_A, m15_affekt_a, m19_z_prox, m2_PCI, m4_flow, m5_coh
            FROM evoki_core_turns
            WHERE turn_id = ?
        """, (turn_id - 1,))
        
        row = cur.fetchone()
        if not row:
            return None
        
        return dict(row)
    
    def _load_b_vector(self, cur, turn_id: int) -> Optional[List[float]]:
        """Load B-vector for turn"""
        # TODO: Implement when B-vector storage is ready
        return [0.9, 0.85, 0.8, 0.7, 0.75, 0.88, 0.82]  # Placeholder
    
    def _load_z_prox_history(self, cur, turn_id: int, window: int = 5) -> List[float]:
        """Load recent z_prox values"""
        cur.execute("""
            SELECT m19_z_prox FROM evoki_core_turns
            WHERE turn_id < ? AND turn_id >= ?
            ORDER BY turn_id DESC
        """, (turn_id, turn_id - window))
        
        return [row[0] for row in cur.fetchall()]
    
    def _load_stored_metrics(self, cur, turn_id: int) -> Dict[str, float]:
        """Load all stored metrics for turn"""
        # Load from resonance table
        cur.execute("""
            SELECT * FROM evoki_resonance_metrics
            WHERE turn_id = ?
        """, (turn_id,))
        
        row = cur.fetchone()
        if not row:
            return {}
        
        return dict(row)


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example: Validate conversation
    validator = ReversibilityValidator(
        db_path="C:/Evoki V3.0 APK-Lokalhost-Google Cloude/evoki_v3_core.db",
        tolerance=0.001  # 0.1% tolerance
    )
    
    # Validate single turn
    result = validator.validate_turn(turn_id=42)
    
    if result.is_valid:
        print(f"✅ Turn {result.turn_id}: VALID")
    else:
        print(f"❌ Turn {result.turn_id}: INVALID")
        print(f"   Max drift: {result.max_drift:.6f}")
        print(f"   Errors: {len(result.errors)}")
        for error in result.errors[:5]:  # Show first 5
            print(f"      - {error}")
    
    # Validate entire conversation
    conv_results = validator.validate_conversation("conv-2024-02-08-001")
    
    valid_count = sum(1 for r in conv_results if r.is_valid)
    print(f"\n📊 Conversation Validation:")
    print(f"   Valid turns: {valid_count}/{len(conv_results)}")
    print(f"   Invalid turns: {len(conv_results) - valid_count}")
    
    # Report invalid turns
    for result in conv_results:
        if not result.is_valid:
            print(f"   ⚠️  Turn {result.turn_id}: {len(result.errors)} errors")
