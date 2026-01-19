#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  EVOKI Engine Launcher V1.1                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Startet evoki_engine.py V7.1 mit VectorRegs_in_Use Integration               ║
║                                                                                ║
║  Features:                                                                     ║
║  - Master-Blaupause V7.1 (A68: Lokale Vektor-Souveränität)                   ║
║  - Physics Engine (Metakognitive Synthese)                                    ║
║  - VectorRegs_in_Use (70.2 Mio. Dimensionen)                                  ║
║  - A68: VectorRegs Cache → Local Model → API Fallback                        ║
║  - Neuroplastizität (Live-Learning)                                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Verwendung:
    python evoki_launcher.py [--port 5000] [--substrates path/to/substrate.json]
"""

import os
import sys
import argparse
import logging

# UTF-8 Encoding für Windows Terminal
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EVOKI_LAUNCHER")

# Pfade setzen
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(BACKEND_DIR, "src", "services"))

def main():
    parser = argparse.ArgumentParser(description="EVOKI Engine Launcher V7.1")
    parser.add_argument("--port", type=int, default=5000, help="Server Port")
    parser.add_argument("--substrates", type=str, nargs="+", default=[],
                        help="Strukturelle Substrate (JSON) für A0.2")
    parser.add_argument("--generic-substrates", type=str, nargs="+", default=[],
                        help="Generische Wissensquellen (JSON/TXT)")
    args = parser.parse_args()

    print("="*70)
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║           EVOKI ENGINE LAUNCHER V1.1                              ║")
    print("║           ChrononEngine V7.1 - Metakognitive Synthese             ║")
    print("║           A68: Lokale Vektor-Souveränität                         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("="*70)

    # Import Engine Module
    print("\n📦 Importiere Engine-Module...")
    
    try:
        from evoki_engine import ChrononEngine, ENGINE_VERSION
        print(f"  ✓ evoki_engine.py V{ENGINE_VERSION} geladen")
    except ImportError as e:
        logger.error(f"Fehler beim Import von evoki_engine: {e}")
        sys.exit(1)

    # A68: VectorRegs sind jetzt in der Engine integriert
    print("  ✓ A68: VectorRegs Integration (nativ in Engine)")

    # Pfade konfigurieren
    DATA_DIR = os.path.join(BACKEND_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    GEDAECHTNIS_PFAD = os.path.join(DATA_DIR, "gedaechtnis.json")
    CHRONIK_PFAD = os.path.join(DATA_DIR, "chronik.log")

    print(f"\n📁 Datenpfade:")
    print(f"  Data Dir: {DATA_DIR}")
    print(f"  Gedächtnis: {GEDAECHTNIS_PFAD}")
    print(f"  Chronik: {CHRONIK_PFAD}")

    # Storage-Pfad vorbereiten
    print(f"\n💾 Storage-Pfade:")
    print(f"  Data Dir: {DATA_DIR}")

    # ChrononEngine V7.1 initialisieren
    print(f"\n🧠 Initialisiere ChrononEngine V7.1...")
    print(f"  A0.3 Manifestations-Anker: 31. Januar 1991")
    
    try:
        engine = ChrononEngine(
            storage_path=DATA_DIR,
            structured_substrate_files=args.substrates,
            generic_substrate_files=args.generic_substrates
        )
        
        print(f"  ✓ Engine initialisiert")
        print(f"    - Memory Einträge: {len(engine.memory.memory.get('eintraege', {})):,}")
        print(f"    - Danger Zones: {len(engine.physics.danger_zone_cache)}")
        print(f"    - Metrik A: {engine.system_state['Metrik_A']:.4f}")
        print(f"    - A68 Lokal: {engine.vector_service.is_local_available}")
        print(f"    - VectorRegs Index: {len(engine.vector_service.vectorregs_index):,}")
        
    except Exception as e:
        logger.error(f"Fehler bei Engine-Initialisierung: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Statistiken
    print(f"\n📊 Gedächtnis-Statistiken:")
    affekt_counts = {'A': 0, 'F': 0, 'C': 0}
    for entry in engine.memory.memory.get('eintraege', {}).values():
        if isinstance(entry, dict):
            affekt = entry.get('affektwert', 'C')
            affekt_counts[affekt] = affekt_counts.get(affekt, 0) + 1
    
    for affekt, count in sorted(affekt_counts.items()):
        label = {'A': 'Positiv', 'F': 'Trauma', 'C': 'Neutral'}.get(affekt, affekt)
        print(f"    - {label} ({affekt}): {count:,}")

    # Interaktive CLI für Tests
    print(f"\n🚀 ChrononEngine V7.1 bereit")
    print("\n" + "="*70)
    print("   EVOKI V7.1 - Metakognitive Synthese")
    print("   A68: Lokale Vektor-Souveränität aktiv")
    print("="*70 + "\n")

    print("📡 Interaktiver Modus (CLI):")
    print("   Gib 'exit' ein zum Beenden")
    print("   Gib 'status' für EKG-Statusfenster ein")
    print("")

    # Simple CLI loop
    while True:
        try:
            user_input = input("\n[EVOKI] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Evoki verabschiedet sich. Auf Wiedersehen!")
                break
            if user_input.lower() == 'status':
                print(f"\n📊 System Status:")
                print(f"   Metrik A: {engine.system_state['Metrik_A']:.4f}")
                print(f"   Gradient ∇A: {engine.system_state['Grad_A']:+.4f}")
                print(f"   Volatilität: {engine.system_state.get('Volatility_A', 0.0):.4f}")
                print(f"   Homöostase: {'AKTIV' if engine.homeostasis_active else 'inaktiv'}")
                continue
            
            result = engine.process_interaction(user_input)
            print(f"\n{result['response']}")
            print(f"\n{'─'*70}")
            print(result['status_window'])
            print('─'*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Evoki verabschiedet sich. Auf Wiedersehen!")
            break
        except Exception as e:
            logger.error(f"Fehler: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
