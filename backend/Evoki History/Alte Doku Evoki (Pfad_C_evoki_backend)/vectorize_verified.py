"""
EVOKI VEKTORISIERUNG - Basiert auf ALLE_NACHRICHTEN_SORTIERT.json
=================================================================
Verwendet die VERIFIZIERTE Datenquelle (3.247.498 Wörter, 0 Verlust)
Nutzt das bestehende upgrade_brain_with_metrics.py als Referenz für Metriken
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import gc
import torch
from sentence_transformers import SentenceTransformer

# ==================== CONFIGURATION ====================
# Verifizierte Quelldatei
SOURCE_JSON = Path(r"C:\evoki\backend\Master Massenexport Extraktor\ALLE_NACHRICHTEN_SORTIERT.json")
OUTPUT_DIR = Path(r"C:\evoki\backend\VectorRegs_VERIFIED")
LOG_FILE = OUTPUT_DIR / "vectorization.log"

MODEL_NAME = 'all-MiniLM-L6-v2'
BLOCK_SIZE = 2000  # Process in blocks
BATCH_SIZE = 64    # GPU batch size

# ==================== SETUP ====================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== DEVICE SETUP ====================
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Device: {device}")
if device == 'cuda':
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

model = SentenceTransformer(MODEL_NAME, device=device)
logger.info(f"Model: {MODEL_NAME}")

# ==================== WORD COUNT VERIFICATION ====================
def count_words(text: str) -> int:
    """Zählt Wörter wie im Original-Script."""
    import re
    return len(re.findall(r'\w+', text))

# ==================== VECTORIZATION ====================
def batch_encode(texts: List[str]) -> List[List[float]]:
    """Encode texts in batches using GPU."""
    if not texts:
        return []
    
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        device=device
    )
    return embeddings.tolist()

def create_vector_entry(msg: Dict, msg_id: int, vector: List[float]) -> Dict:
    """Erstellt einen Vektoreintrag aus einer Nachricht."""
    message_text = msg.get('message', '')
    
    # SHA256 Hash für Integrität
    content_hash = hashlib.sha256(message_text.encode('utf-8')).hexdigest()
    
    return {
        "id": msg_id,
        "timestamp": msg.get('timestamp', ''),
        "parsed_timestamp": msg.get('__parsed_timestamp', ''),
        "speaker": msg.get('speaker', ''),
        "message": message_text,
        "word_count": count_words(message_text),
        "vector": vector,
        "content_hash": content_hash
    }

# ==================== MAIN ====================
def run_vectorization():
    logger.info("=" * 80)
    logger.info("EVOKI VEKTORISIERUNG - VERIFIZIERTE DATEN")
    logger.info("=" * 80)
    
    # Lade Quelldatei
    logger.info(f"Lade: {SOURCE_JSON}")
    with open(SOURCE_JSON, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    total_messages = len(messages)
    logger.info(f"Messages: {total_messages}")
    
    # Verifiziere Wortzahl
    total_words = sum(count_words(msg.get('message', '')) for msg in messages)
    logger.info(f"Wörter gesamt: {total_words:,}")
    logger.info(f"Erwartet (ca.): 3,247,498")
    
    # Zähle User vs AI
    user_count = sum(1 for m in messages if 'user' in m.get('speaker', '').lower())
    ai_count = total_messages - user_count
    logger.info(f"User-Messages: {user_count}")
    logger.info(f"AI-Messages: {ai_count}")
    
    # Vektorisiere in Blöcken
    all_vectors = []
    
    for block_start in range(0, total_messages, BLOCK_SIZE):
        block_end = min(block_start + BLOCK_SIZE, total_messages)
        block = messages[block_start:block_end]
        
        logger.info(f"\nBlock {block_start//BLOCK_SIZE + 1}: Messages {block_start+1} bis {block_end}")
        
        # Extrahiere Texte
        texts = [msg.get('message', '') for msg in block]
        
        # Vektorisiere
        logger.info(f"  Vektorisiere {len(texts)} Texte auf {device}...")
        vectors = batch_encode(texts)
        
        # Erstelle Einträge
        for i, (msg, vec) in enumerate(zip(block, vectors)):
            msg_id = block_start + i + 1
            entry = create_vector_entry(msg, msg_id, vec)
            all_vectors.append(entry)
        
        logger.info(f"  ✓ Block fertig ({len(all_vectors)}/{total_messages})")
        
        # Memory cleanup
        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()
    
    # Verifiziere finale Wortzahl
    final_words = sum(v['word_count'] for v in all_vectors)
    logger.info(f"\n{'='*80}")
    logger.info(f"VERIFIZIERUNG")
    logger.info(f"{'='*80}")
    logger.info(f"Wörter Input:  {total_words:,}")
    logger.info(f"Wörter Output: {final_words:,}")
    logger.info(f"Differenz:     {total_words - final_words}")
    
    if total_words == final_words:
        logger.info("✓✓✓ [OK] LÜCKENLOSE VEKTORISIERUNG! ✓✓✓")
    else:
        logger.warning("⚠⚠⚠ [WARNUNG] Wortzahl-Differenz! ⚠⚠⚠")
    
    # Speichere Output
    output_file = OUTPUT_DIR / "evoki_vectors_verified.json"
    
    output_data = {
        "metadata": {
            "source": str(SOURCE_JSON),
            "model": MODEL_NAME,
            "vector_dimensions": 384,
            "total_messages": len(all_vectors),
            "total_words": final_words,
            "user_messages": user_count,
            "ai_messages": ai_count,
            "created_at": datetime.now().isoformat(),
            "device": device,
            "verification": "PASSED" if total_words == final_words else "FAILED"
        },
        "vectors": all_vectors
    }
    
    logger.info(f"\nSpeichere: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Speichere auch Verifizierungsdatei
    verif_file = OUTPUT_DIR / "Verifizierung_Vektorisierung.txt"
    with open(verif_file, 'w', encoding='utf-8') as f:
        f.write(f"Quelle: {SOURCE_JSON}\n")
        f.write(f"Messages: {total_messages}\n")
        f.write(f"Wörter Input: {total_words}\n")
        f.write(f"Wörter Output: {final_words}\n")
        f.write(f"Differenz: {total_words - final_words}\n")
        f.write(f"User-Messages: {user_count}\n")
        f.write(f"AI-Messages: {ai_count}\n")
        f.write(f"Verhältnis: {final_words/total_words:.5f}\n")
        if total_words == final_words:
            f.write("[OK] Lückenlose Vektorisierung!\n")
        else:
            f.write("[WARNUNG] Wortzahl-Differenz!\n")
    
    logger.info(f"\n{'='*80}")
    logger.info("FERTIG!")
    logger.info(f"{'='*80}")
    logger.info(f"Output: {output_file}")
    logger.info(f"Verifizierung: {verif_file}")
    
    return output_data

if __name__ == "__main__":
    run_vectorization()
