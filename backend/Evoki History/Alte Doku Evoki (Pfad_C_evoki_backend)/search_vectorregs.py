"""Suche in VectorRegs nach dem Tsunami/Sintflut/Diamant Ereignis"""
import sys
sys.path.insert(0, 'src/services')
from vectorRegsService import VectorRegsService
from sentence_transformers import SentenceTransformer

print("Lade Embedding-Modell...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Lade VectorRegs (mit explizitem Laden)...")
vrs = VectorRegsService('VectorRegs_in_Use')

# Explizit laden
print("Lade Atomic Vectors...")
vrs._load_brain_atomic()
print(f"Stats: {vrs.get_stats()}")

query_text = "sintflut tsunami zusammenbruch firewall wächter diamant meeresboden 38mb token millionen trauma regelwerk kollaps hybris phönix asche"

print(f"\nSuche nach: {query_text[:80]}...")
query_vector = model.encode(query_text)
results = vrs.search(query_vector, top_k=10)

for i, r in enumerate(results):
    print(f"\n{'='*60}")
    print(f"Treffer {i+1} | Score: {r['score']:.3f} | ID: {r.get('id', 'N/A')}")
    print(f"{'='*60}")
    print(r['text'][:800])
