"""
metrics_lib_v12_clean - V12 Clean Architecture Metrics Library

25 Core Metrics + Components + Aggregates

CRITICAL: This is the CLEAN V12 implementation!
All formulas verified against V11.1 specification.
"""

# Helpers (must import first)
from ._helpers import clamp
from ._lexika import load_lexika

# Phase 1: Analysis
from .m18_s_entropy import compute_m18_s_entropy

# Phase 2: Core Physics
from .m1_A import compute_m1_A
from .m2_PCI import compute_m2_PCI
from .m6_ZLF import compute_m6_ZLF
from .m7_LL import compute_m7_LL
from .m19_z_prox import compute_m19_z_prox

# Phase 3a: Trauma Pre-Scan
from .m101_t_panic import compute_m101_t_panic
from .m102_t_disso import compute_m102_t_disso
from .m103_t_integ import compute_m103_t_integ
from .m110_black_hole import compute_m110_black_hole

# Phase 4: Trauma Full
from .m111_turbidity_total import compute_m111_turbidity_total
from .m112_trauma_load import compute_m112_trauma_load
from .m114_t_recovery import compute_m114_t_recovery

# Phase 5: Dynamics
from .m17_nabla_a import compute_m17_nabla_a
from .m23_nabla_pci import compute_m23_nabla_pci
from .m22_cog_load import compute_m22_cog_load

# Phase 6: Synthesis
from .m36_rule_conflict import compute_m36_rule_conflict
from .m37_rule_stable import compute_m37_rule_stable
from .m38_soul_integrity import compute_m38_soul_integrity
from .m39_soul_check import compute_m39_soul_check
from .m144_sys_stability import compute_m144_sys_stability
from .m151_omega import compute_m151_omega
from .m153_sys_health import compute_m153_sys_health
from .m161_commit import compute_m161_commit

__all__ = [
    # Helpers
    'clamp',
    'load_lexika',
    
    # Phase 1
    'compute_m18_s_entropy',
    
    # Phase 2
    'compute_m1_A',
    'compute_m2_PCI',
    'compute_m6_ZLF',
    'compute_m7_LL',
    'compute_m19_z_prox',
    
    # Phase 3a
    'compute_m101_t_panic',
    'compute_m102_t_disso',
    'compute_m103_t_integ',
    'compute_m110_black_hole',
    
    # Phase 4
    'compute_m111_turbidity_total',
    'compute_m112_trauma_load',
    'compute_m114_t_recovery',
    
    # Phase 5
    'compute_m17_nabla_a',
    'compute_m23_nabla_pci',
    'compute_m22_cog_load',
    
    # Phase 6
    'compute_m36_rule_conflict',
    'compute_m37_rule_stable',
    'compute_m38_soul_integrity',
    'compute_m39_soul_check',
    'compute_m144_sys_stability',
    'compute_m151_omega',
    'compute_m153_sys_health',
    'compute_m161_commit',
]

__version__ = '3.0.0-v12-clean'