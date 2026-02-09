"""
EVOKI V3.0 - BINÄRER FUNKTIONSTEST
Ergebnis: JA (System funktioniert) oder NEIN (System kaputt)
"""
import sys
import traceback

def test():
    print("="*80)
    print("🔍 EVOKI V3.0 — BINÄRER FUNKTIONSTEST")
    print("="*80)
    print()
    
    errors = []
    
    # Test 1: V7 Module importieren
    print("1️⃣ V7 Module...")
    try:
        sys.path.insert(0, 'backend')
        from core import a_phys_v11, evoki_bootcheck, genesis_anchor
        from core import lexika, metrics_registry, evoki_invariants
        from core import evoki_lock, evoki_history_ingest
        print("   ✅ Alle V7 Module importierbar")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("V7 Module")
    
    # Test 2: evoki_pipeline Module
    print("2️⃣ evoki_pipeline Module...")
    try:
        from core import vector_engine_v2_1, b_vector
        from core import timeline_4d_complete, chunk_vectorize_full
        from core.evoki_metrics_v3 import metrics_complete_v3
        print("   ✅ Alle evoki_pipeline Module importierbar")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("evoki_pipeline")
    
    # Test 3: Lexika Bundle
    print("3️⃣ Lexika V3 Bundle...")
    try:
        from core.evoki_lexika_v3 import engine, registry, lexika_data
        print("   ✅ Lexika Bundle importierbar")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("Lexika Bundle")
    
    # Test 4: Backend läuft
    print("4️⃣ Backend Server...")
    try:
        import requests
        r = requests.get("http://localhost:8000/health", timeout=3)
        assert r.status_code == 200
        print("   ✅ Backend antwortet")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("Backend")
    
    # Test 5: Frontend läuft
    print("5️⃣ Frontend Server...")
    try:
        import requests
        r = requests.get("http://localhost:5173", timeout=3)
        assert r.status_code == 200
        print("   ✅ Frontend antwortet")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("Frontend")
    
    # Test 6: Database
    print("6️⃣ Datenbank...")
    try:
        import sqlite3
        conn = sqlite3.connect("backend/data/databases/evoki_v3_core.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prompt_pairs")
        count = cursor.fetchone()[0]
        assert count == 10971
        conn.close()
        print(f"   ✅ Database ({count} Einträge)")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("Database")
    
    # Test 7: FAISS
    print("7️⃣ FAISS Index...")
    try:
        import faiss
        index = faiss.read_index("backend/data/faiss/evoki_v3_vectors_semantic.faiss")
        assert index.ntotal == 10971
        print(f"   ✅ FAISS ({index.ntotal} Vektoren)")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("FAISS")
    
    # Test 8: Temple API funktioniert
    print("8️⃣ Temple API...")
    try:
        import requests
        r = requests.post(
            "http://localhost:8000/api/temple/stream",
            json={"prompt": "Test"},
            timeout=5,
            stream=True
        )
        assert r.status_code == 200
        # Lese ersten Event
        for line in r.iter_lines(decode_unicode=True):
            if line.startswith("event:"):
                print(f"   ✅ Temple API (SSE funktioniert)")
                break
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        errors.append("Temple API")
    
    print()
    print("="*80)
    
    if len(errors) == 0:
        print("✅ ERGEBNIS: JA - SYSTEM FUNKTIONIERT 100%")
        print("="*80)
        return 0
    else:
        print(f"❌ ERGEBNIS: NEIN - {len(errors)} KRITISCHE FEHLER")
        print(f"   Fehlerhafte Komponenten: {', '.join(errors)}")
        print("="*80)
        return 1

if __name__ == "__main__":
    exit(test())
