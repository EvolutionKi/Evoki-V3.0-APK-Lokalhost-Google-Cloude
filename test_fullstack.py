"""
Test script to verify the complete Evoki V3.0 stack.
Tests: Frontend, Backend, Database, FAISS
"""
import requests
import json
import time

print("="*80)
print("EVOKI V3.0 — FULL STACK TEST")
print("="*80)
print()

# Test 1: Backend Health
print("1️⃣ Testing Backend Health...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Backend: {response.json()}")
    else:
        print(f"   ❌ Backend HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend Error: {e}")
print()

# Test 2: Frontend
print("2️⃣ Testing Frontend...")
try:
    response = requests.get("http://localhost:5173", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Frontend loads (HTTP 200)")
    else:
        print(f"   ❌ Frontend HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Frontend Error: {e}")
print()

# Test 3: Temple Stream API (the real test!)
print("3️⃣ Testing Temple Stream API...")
try:
    response = requests.post(
        "http://localhost:8000/api/temple/stream",
        json={"prompt": "Test prompt for integration check"},
        timeout=10,
        stream=True
    )
    
    if response.status_code == 200:
        print(f"   ✅ Temple API: HTTP {response.status_code}")
        print(f"   📡 SSE Events received:")
        
        # Parse SSE events
        events = []
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()
                events.append((event_type, event_data))
                print(f"      - {event_type}: {event_data[:60]}...")
                
                # Stop after 10 events
                if len(events) >= 10:
                    break
        
        print(f"   ✅ Received {len(events)} events")
    else:
        print(f"   ❌ Temple API HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Temple API Error: {e}")
print()

# Test 4: Database
print("4️⃣ Testing Database...")
try:
    import sqlite3
    conn = sqlite3.connect("backend/data/databases/evoki_v3_core.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM prompt_pairs")
    count = cursor.fetchone()[0]
    print(f"   ✅ Database: {count} prompt pairs")
    conn.close()
except Exception as e:
    print(f"   ❌ Database Error: {e}")
print()

# Test 5: FAISS Index
print("5️⃣ Testing FAISS Index...")
try:
    import faiss
    index = faiss.read_index("backend/data/faiss/evoki_v3_vectors_semantic.faiss")
    print(f"   ✅ FAISS: {index.ntotal} vectors ({index.d}D)")
except Exception as e:
    print(f"   ❌ FAISS Error: {e}")
print()

print("="*80)
print("✅ FULL STACK TEST COMPLETE")
print("="*80)
