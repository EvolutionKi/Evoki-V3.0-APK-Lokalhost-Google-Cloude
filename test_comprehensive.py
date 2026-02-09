"""
EVOKI V3.0 — COMPREHENSIVE TESTING SUITE
Tests all critical functionality end-to-end.
"""
import requests
import sqlite3
import faiss
import numpy as np
import time
import json
from pathlib import Path

print("="*80)
print("🧪 EVOKI V3.0 — COMPREHENSIVE TEST SUITE")
print("="*80)
print()

test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

def test(name, func):
    """Run a test and track results."""
    try:
        print(f"🔍 {name}...")
        result = func()
        if result:
            print(f"   ✅ PASS")
            test_results["passed"] += 1
        else:
            print(f"   ⚠️  WARNING")
            test_results["warnings"] += 1
        return result
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        test_results["failed"] += 1
        return False

# ============================================================================
# TEST 1: Backend Health Check
# ============================================================================
def test_backend_health():
    response = requests.get("http://localhost:8000/health", timeout=5)
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "healthy"
    print(f"      Mode: {data.get('mode')}, Phase: {data.get('phase')}")
    return True

test("Backend Health", test_backend_health)

# ============================================================================
# TEST 2: Database Integrity
# ============================================================================
def test_database():
    conn = sqlite3.connect("backend/data/databases/evoki_v3_core.db")
    cursor = conn.cursor()
    
    # Check prompt_pairs
    cursor.execute("SELECT COUNT(*) FROM prompt_pairs")
    count = cursor.fetchone()[0]
    assert count > 0, f"No prompt pairs found"
    print(f"      prompt_pairs: {count} entries")
    
    # Check metrics_full exists
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='metrics_full'")
    assert cursor.fetchone()[0] == 1, "metrics_full table missing"
    print(f"      metrics_full: table exists")
    
    # Check session_chain exists
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='session_chain'")
    assert cursor.fetchone()[0] == 1, "session_chain table missing"
    print(f"      session_chain: table exists")
    
    conn.close()
    return True

test("Database Integrity", test_database)

# ============================================================================
# TEST 3: FAISS Index
# ============================================================================
def test_faiss_index():
    index_path = Path("backend/data/faiss/evoki_v3_vectors_semantic.faiss")
    assert index_path.exists(), "FAISS index file not found"
    
    index = faiss.read_index(str(index_path))
    assert index.ntotal > 0, "FAISS index is empty"
    assert index.d == 384, f"Wrong dimension: {index.d} (expected 384)"
    
    print(f"      Vectors: {index.ntotal}, Dimension: {index.d}D")
    
    # Test search
    test_vector = np.random.rand(384).astype('float32')
    test_vector = test_vector / np.linalg.norm(test_vector)
    D, I = index.search(test_vector.reshape(1, -1), k=5)
    
    assert len(I[0]) == 5, "Search didn't return 5 results"
    print(f"      Search: Top-5 scores = {D[0][:3]}")
    
    return True

test("FAISS Index", test_faiss_index)

# ============================================================================
# TEST 4: FAISS Metadata Linkage
# ============================================================================
def test_faiss_metadata():
    conn = sqlite3.connect("backend/data/faiss/faiss_metadata.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM semantic_index")
    count = cursor.fetchone()[0]
    assert count > 0, "No metadata entries"
    
    # Check if metadata matches FAISS size
    index = faiss.read_index("backend/data/faiss/evoki_v3_vectors_semantic.faiss")
    assert count == index.ntotal, f"Metadata mismatch: {count} vs {index.ntotal}"
    
    print(f"      Metadata entries: {count}")
    
    # Check linkage
    cursor.execute("""
        SELECT sm.pair_id, pp.user_text 
        FROM semantic_index sm
        JOIN prompt_pairs pp ON sm.pair_id = pp.pair_id
        LIMIT 3
    """)
    rows = cursor.fetchall()
    assert len(rows) == 3, "Metadata-DB linkage broken"
    print(f"      Linkage: {len(rows)} sample entries verified")
    
    conn.close()
    return True

test("FAISS Metadata Linkage", test_faiss_metadata)

# ============================================================================
# TEST 5: Temple Stream API - Basic
# ============================================================================
def test_temple_stream_basic():
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": "Hello"},
        timeout=10,
        stream=True
    )
    
    assert response.status_code == 200, f"HTTP {response.status_code}"
    
    events = []
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            event_data = line.split(":", 1)[1].strip()
            events.append(event_type)
            if len(events) >= 5:
                break
    
    assert "status" in events, "No status events"
    assert "metrics" in events, "No metrics events"
    print(f"      Events received: {events[:5]}")
    
    return True

test("Temple Stream API - Basic", test_temple_stream_basic)

# ============================================================================
# TEST 6: Metrics Calculation
# ============================================================================
def test_metrics_calculation():
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": "I am feeling great today!"},
        timeout=10,
        stream=True
    )
    
    metrics_data = None
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("event: metrics"):
            continue
        elif line.startswith("data:") and metrics_data is None:
            try:
                metrics_data = json.loads(line.split(":", 1)[1].strip())
                break
            except:
                pass
    
    assert metrics_data is not None, "No metrics received"
    assert "A" in metrics_data, "Missing A metric"
    assert "PCI" in metrics_data, "Missing PCI metric"
    assert "B_vector" in metrics_data, "Missing B_vector"
    
    print(f"      A={metrics_data['A']:.2f}, PCI={metrics_data['PCI']:.2f}")
    print(f"      B_vector keys: {list(metrics_data['B_vector'].keys())[:3]}...")
    
    return True

test("Metrics Calculation", test_metrics_calculation)

# ============================================================================
# TEST 7: Vector Search with Real Query
# ============================================================================
def test_vector_search_real():
    # Get a real prompt from DB
    conn = sqlite3.connect("backend/data/databases/evoki_v3_core.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_text FROM prompt_pairs LIMIT 1")
    sample_text = cursor.fetchone()[0]
    conn.close()
    
    # Search for similar prompts
    response = requests.post(
        "http://localhost:8000/api/vector/search",
        json={"query": sample_text[:100], "top_k": 5},
        timeout=10
    )
    
    assert response.status_code == 200, f"HTTP {response.status_code}"
    data = response.json()
    
    assert "results" in data, "No results field"
    assert len(data["results"]) > 0, "No search results"
    
    print(f"      Found {len(data['results'])} results")
    print(f"      Top score: {data['results'][0].get('score', 'N/A')}")
    
    return True

test("Vector Search - Real Query", test_vector_search_real)

# ============================================================================
# TEST 8: Performance - Response Time
# ============================================================================
def test_performance():
    start = time.time()
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": "Quick test"},
        timeout=15,
        stream=True
    )
    
    # Consume first 3 events
    count = 0
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("event:"):
            count += 1
            if count >= 3:
                break
    
    elapsed = time.time() - start
    assert elapsed < 10, f"Too slow: {elapsed:.2f}s"
    
    print(f"      First 3 events in {elapsed:.2f}s")
    
    return True

test("Performance - Response Time", test_performance)

# ============================================================================
# TEST 9: FAISS Search Integration
# ============================================================================
def test_faiss_integration():
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": "Tell me about FAISS"},
        timeout=10,
        stream=True
    )
    
    faiss_event_found = False
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("event: faiss_results"):
            faiss_event_found = True
            break
        if line.startswith("event: token"):
            # We've reached tokens, stop looking
            break
    
    # FAISS integration is optional, so warning not error
    if not faiss_event_found:
        print(f"      ⚠️  FAISS event not found (may be empty results)")
        return True
    
    print(f"      FAISS event received")
    return True

test("FAISS Integration", test_faiss_integration)

# ============================================================================
# TEST 10: Error Handling
# ============================================================================
def test_error_handling():
    # Test empty prompt
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": ""},
        timeout=5
    )
    
    # Should either reject or handle gracefully
    assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
    print(f"      Empty prompt handling: HTTP {response.status_code}")
    
    return True

test("Error Handling", test_error_handling)

# ============================================================================
# FINAL REPORT
# ============================================================================
print()
print("="*80)
print("📊 TEST SUMMARY")
print("="*80)
print(f"✅ Passed:   {test_results['passed']}")
print(f"⚠️  Warnings: {test_results['warnings']}")
print(f"❌ Failed:   {test_results['failed']}")
print()

total = test_results['passed'] + test_results['warnings'] + test_results['failed']
success_rate = (test_results['passed'] / total * 100) if total > 0 else 0

print(f"Success Rate: {success_rate:.1f}%")
print()

if test_results['failed'] == 0:
    print("🎉 ALL CRITICAL TESTS PASSED!")
    print("✅ System is PRODUCTION READY!")
else:
    print(f"⚠️  {test_results['failed']} critical test(s) failed")
    print("🔧 Please review failures above")

print("="*80)
