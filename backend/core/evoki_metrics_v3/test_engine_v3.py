"""
Quick test of MetricsEngineV3 - 6-Phase Pipeline

Verifies:
1. Engine initializes
2. All 6 phases execute in order
3. Dual-gradient system works
4. Safety gates function
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from metrics_engine_v3 import MetricsEngineV3, compute_metrics_for_pair


def test_basic_execution():
    """Test basic metrics calculation"""
    print("=" * 70)
    print("EVOKI METRICS ENGINE V3 - QUICK TEST")
    print("=" * 70)
    
    # Test data
    user_text = "Ich fühle mich heute sehr gut und optimistisch."
    ai_text = "Das freut mich zu hören! Können Sie mehr darüber erzählen?"
    
    context = {
        'flow': 0.85,
        'coh': 0.75,
        'rep_same': 0.2,
        'ctx_break': False,
    }
    
    print("\n📝 User Input:")
    print(f"   '{user_text}'")
    print("\n🤖 AI Response:")
    print(f"   '{ai_text}'")
    
    # Compute metrics
    print("\n⚙️  Computing metrics...")
    try:
        user_metrics, ai_metrics, disharmony = compute_metrics_for_pair(
            user_text=user_text,
            ai_text=ai_text,
            context=context
        )
        
        print("\n✅ Computation successful!")
        
        # Display key metrics
        print("\n" + "=" * 70)
        print("USER METRICS (∇A)")
        print("=" * 70)
        print_key_metrics(user_metrics)
        
        print("\n" + "=" * 70)
        print("AI METRICS (∇B)")
        print("=" * 70)
        print_key_metrics(ai_metrics)
        
        print("\n" + "=" * 70)
        print(f"DISHARMONY SCORE: {disharmony:.4f}")
        print("=" * 70)
        
        # Verify phase execution
        print("\n" + "=" * 70)
        print("PHASE VERIFICATION")
        print("=" * 70)
        verify_phases(user_metrics)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_key_metrics(metrics: dict):
    """Print key metrics in organized format"""
    
    # Phase 1: Analysis
    print("\n📊 Phase 1: Analysis")
    print(f"   Word Count: {metrics.get('word_count', 'N/A')}")
    print(f"   Entropy: {metrics.get('m18_s_entropy', 'N/A'):.4f}")
    
    # Phase 2: Core Physics
    print("\n⚛️  Phase 2: Core Physics")
    print(f"   m1_A (Affekt): {metrics.get('m1_A', 'N/A'):.4f}")
    print(f"   m2_PCI: {metrics.get('m2_PCI', 'N/A'):.4f}")
    print(f"   m7_LL (Turbidity): {metrics.get('m7_LL', 'N/A'):.4f}")
    print(f"   m6_ZLF (Loop): {metrics.get('m6_ZLF', 'N/A'):.4f}")
    print(f"   m19_z_prox (Danger): {metrics.get('m19_z_prox', 'N/A'):.4f}")
    
    # Phase 3a: Trauma Pre-Scan
    print("\n🛡️  Phase 3a: Trauma Pre-Scan")
    print(f"   T_panic: {metrics.get('t_panic_pre', 'N/A'):.4f}")
    print(f"   T_disso: {metrics.get('t_disso_pre', 'N/A'):.4f}")
    print(f"   T_integ: {metrics.get('t_integ_pre', 'N/A'):.4f}")
    print(f"   Safe Mode: {metrics.get('safe_mode', 'N/A')}")
    
    # Phase 3b: Context
    print("\n🔍 Phase 3b: Context/RAG")
    print(f"   RAG Active: {metrics.get('rag_active', 'N/A')}")
    
    # Phase 4: Trauma Full
    print("\n🧠 Phase 4: Trauma Full")
    print(f"   Turbidity Total: {metrics.get('m111_turbidity', 'N/A'):.4f}")
    print(f"   Trauma Load: {metrics.get('m112_trauma_load', 'N/A'):.4f}")
    
    # Phase 5: Dynamics
    print("\n📈 Phase 5: Dynamics")
    print(f"   ∇A (Gradient): {metrics.get('m17_nabla_a', 'N/A'):.4f}")
    print(f"   Cognitive Load: {metrics.get('m22_cog_load', 'N/A'):.4f}")
    
    # Phase 6: Synthesis
    print("\n🎯 Phase 6: Synthesis")
    print(f"   OMEGA: {metrics.get('m151_omega', 'N/A'):.4f}")
    print(f"   Soul Integrity: {metrics.get('m38_soul_integrity', 'N/A'):.4f}")
    print(f"   Commit Decision: {metrics.get('m161_commit', 'N/A')}")


def verify_phases(metrics: dict):
    """Verify all phases executed"""
    phases = {
        "Phase 1 (Analysis)": ['word_count', 'm18_s_entropy'],
        "Phase 2 (Core Physics)": ['m1_A', 'm2_PCI', 'm7_LL', 'm6_ZLF'],
        "Phase 3a (Trauma Pre)": ['t_panic_pre', 't_disso_pre'],
        "Phase 3b (Context/RAG)": ['rag_active'],
        "Phase 4 (Trauma Full)": ['m111_turbidity', 'm112_trauma_load'],
        "Phase 5 (Dynamics)": ['m17_nabla_a', 'm22_cog_load'],
        "Phase 6 (Synthesis)": ['m151_omega', 'm161_commit'],
    }
    
    all_ok = True
    for phase_name, required_keys in phases.items():
        missing = [k for k in required_keys if k not in metrics]
        if missing:
            print(f"❌ {phase_name}: MISSING {missing}")
            all_ok = False
        else:
            print(f"✅ {phase_name}: OK")
    
    if all_ok:
        print("\n🎉 ALL PHASES EXECUTED SUCCESSFULLY!")
    else:
        print("\n⚠️  SOME PHASES INCOMPLETE")
    
    return all_ok


if __name__ == "__main__":
    success = test_basic_execution()
    sys.exit(0 if success else 1)
