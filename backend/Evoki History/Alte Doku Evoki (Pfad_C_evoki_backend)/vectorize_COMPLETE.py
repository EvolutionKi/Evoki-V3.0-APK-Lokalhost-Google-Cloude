"""
EVOKI COMPLETE VECTORIZATION - Final Production Version
========================================================
- Processes ALL 13,325 exchanges (not just pairs with AI files)
- HTML entity decoding for source files
- Parallel processing with GPU acceleration
- Block-based with checkpoints every 2000 exchanges
- Individual JSON files per exchange for safety
- Extensive logging to debug empty AI texts
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import torch
from sentence_transformers import SentenceTransformer
import gc

# ==================== CONFIGURATION ====================
BASE_DIR = Path(r"C:\evoki\backend\VectorRegs_TXT_Export")
OUTPUT_DIR = Path(r"C:\evoki\backend\VectorRegs_COMPLETE")
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.json"
LOG_FILE = OUTPUT_DIR / "vectorization.log"

MODEL_NAME = 'all-MiniLM-L6-v2'
BLOCK_SIZE = 2000  # Process in blocks of 2000
BATCH_SIZE = 64    # GPU batch size
MAX_WORKERS = 8    # Parallel file readers
MAX_PAIRS = None   # Process ALL exchanges

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
logger.info(f"Using device: {device}")
if device == 'cuda':
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"CUDA Version: {torch.version.cuda}")

model = SentenceTransformer(MODEL_NAME, device=device)
logger.info(f"Model loaded: {MODEL_NAME}")

# ==================== PARSING FUNCTIONS ====================
def decode_html_entities(text: str) -> str:
    """Decode HTML entities like &quot; to actual characters."""
    return html.unescape(text)

def parse_prompt_file(file_path: Path) -> str:
    """Parse a single prompt file and extract content after header."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Decode HTML entities
        content = decode_html_entities(content)
        
        # Find the separator line
        if '===' in content:
            parts = content.split('===', 1)
            if len(parts) == 2:
                text = parts[1].strip()
                logger.debug(f"Parsed {file_path.name}: {len(text)} chars (separator method)")
                return text
        
        # Fallback: skip first 2 lines (Timestamp + Speaker)
        lines = content.split('\n')
        if len(lines) > 2:
            text = '\n'.join(lines[2:]).strip()
            logger.debug(f"Parsed {file_path.name}: {len(text)} chars (fallback method)")
            return text
        
        logger.warning(f"Could not parse {file_path}: no separator, <3 lines")
        return ""
        
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""

def parse_file_pair(user_file: Path) -> Tuple[str, str, Path]:
    """
    Parse both user and AI files.
    Returns (user_text, ai_text, user_file_path).
    If AI file doesn't exist, ai_text will be empty string.
    """
    ai_file = user_file.parent / user_file.name.replace('_user.txt', '_ai.txt')
    
    user_text = parse_prompt_file(user_file)
    ai_text = ""
    
    if ai_file.exists():
        ai_text = parse_prompt_file(ai_file)
        if not ai_text:
            logger.warning(f"AI file exists but empty after parsing: {ai_file}")
    else:
        logger.debug(f"No AI file for {user_file.name}")
    
    return user_text, ai_text, user_file

# ==================== VECTORIZATION ====================
def batch_encode(texts: List[str], label: str) -> List[List[float]]:
    """Encode texts in batches using GPU."""
    if not texts:
        return []
    
    try:
        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            device=device
        )
        logger.debug(f"Encoded {len(texts)} {label} texts on {device}")
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Encoding failed for {label}: {e}")
        # CPU fallback
        if device == 'cuda':
            logger.info("Retrying on CPU...")
            embeddings = model.encode(
                texts,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
                convert_to_numpy=True,
                device='cpu'
            )
            return embeddings.tolist()
        raise

def create_exchange(exchange_id: int, user_text: str, ai_text: str, 
                   user_vec: List[float], ai_vec: List[float],
                   source_file: Path) -> Dict:
    """Create a single exchange dictionary."""
    timestamp = datetime.now().isoformat()
    
    # Create hash from concatenated texts
    combined = f"{user_text}{ai_text}"
    content_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    return {
        "exchange_id": exchange_id,
        "timestamp": timestamp,
        "source_file": str(source_file),
        "user_text": user_text,
        "ai_text": ai_text,
        "user_vector": user_vec,
        "ai_vector": ai_vec,
        "content_hash": content_hash,
        "has_ai_response": bool(ai_text and ai_text.strip())
    }

# ==================== CHECKPOINT MANAGEMENT ====================
def load_checkpoint() -> int:
    """Load checkpoint and return last processed exchange ID."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                data = json.load(f)
            last_id = data.get('last_exchange_id', 0)
            logger.info(f"Resuming from checkpoint: {last_id}")
            return last_id
        except Exception as e:
            logger.error(f"Could not load checkpoint: {e}")
    return 0

def save_checkpoint(exchange_id: int, total_processed: int):
    """Save checkpoint."""
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'last_exchange_id': exchange_id,
                'total_processed': total_processed,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        logger.info(f"Checkpoint saved at exchange {exchange_id}")
    except Exception as e:
        logger.error(f"Could not save checkpoint: {e}")

# ==================== MAIN PROCESSING ====================
def run_complete_vectorization():
    """
    Main vectorization loop with block processing.
    """
    logger.info("=" * 80)
    logger.info("EVOKI COMPLETE VECTORIZATION START")
    logger.info("=" * 80)
    
    # Get all user files
    all_user_files = sorted(BASE_DIR.rglob("*_user.txt"))
    total_files = len(all_user_files)
    logger.info(f"Found {total_files} user files")
    
    # Load checkpoint
    start_id = load_checkpoint()
    if start_id > 0:
        all_user_files = all_user_files[start_id:]
        logger.info(f"Skipping first {start_id} files (checkpoint)")
    
    # Apply MAX_PAIRS limit if set
    if MAX_PAIRS:
        all_user_files = all_user_files[:MAX_PAIRS]
        logger.info(f"Limited to {MAX_PAIRS} exchanges")
    
    # Initialize summary
    summary_file = OUTPUT_DIR / "vectorization_summary.json"
    if summary_file.exists() and start_id == 0:
        logger.warning("Deleting existing summary file")
        summary_file.unlink()
    
    # Process in blocks
    total_processed = start_id
    empty_ai_count = 0
    
    for block_start in range(0, len(all_user_files), BLOCK_SIZE):
        block_end = min(block_start + BLOCK_SIZE, len(all_user_files))
        block_files = all_user_files[block_start:block_end]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"BLOCK {block_start//BLOCK_SIZE + 1}: Processing files {block_start} to {block_end-1}")
        logger.info(f"{'='*60}")
        
        # Parallel file reading
        logger.info(f"Reading {len(block_files)} file pairs in parallel...")
        file_data = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(parse_file_pair, f): f for f in block_files}
            
            for i, future in enumerate(as_completed(futures)):
                user_text, ai_text, source_file = future.result()
                file_data.append((user_text, ai_text, source_file))
                
                if (i + 1) % 500 == 0:
                    logger.info(f"  Read {i+1}/{len(block_files)} files...")
        
        # Separate texts for vectorization
        user_texts = [d[0] for d in file_data]
        ai_texts = [d[1] for d in file_data]
        
        # Count empty AI texts
        block_empty_ai = sum(1 for ai in ai_texts if not ai or not ai.strip())
        empty_ai_count += block_empty_ai
        logger.info(f"Block stats: {block_empty_ai}/{len(ai_texts)} exchanges without AI response ({100*block_empty_ai/len(ai_texts):.1f}%)")
        
        # Vectorize
        logger.info(f"Vectorizing {len(user_texts)} user texts on {device}...")
        user_vectors = batch_encode(user_texts, "user")
        
        logger.info(f"Vectorizing {len(ai_texts)} AI texts on {device}...")
        ai_vectors = batch_encode(ai_texts, "AI")
        
        # Create exchanges and write individual files
        logger.info(f"Writing individual exchange files...")
        exchanges = []
        
        for i, (user_text, ai_text, source_file) in enumerate(file_data):
            exchange_id = total_processed + i + 1
            
            exchange = create_exchange(
                exchange_id=exchange_id,
                user_text=user_text,
                ai_text=ai_text,
                user_vec=user_vectors[i],
                ai_vec=ai_vectors[i],
                source_file=source_file
            )
            
            exchanges.append(exchange)
            
            # Write individual file
            exchange_file = OUTPUT_DIR / f"exchange_{exchange_id:06d}.json"
            with open(exchange_file, 'w', encoding='utf-8') as f:
                json.dump(exchange, f, ensure_ascii=False, indent=2)
        
        # Update summary file (append mode)
        logger.info(f"Updating summary file...")
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
        else:
            summary = {
                "metadata": {
                    "model": MODEL_NAME,
                    "vector_dimensions": 384,
                    "created_at": datetime.now().isoformat(),
                    "device": device
                },
                "exchanges": []
            }
        
        summary["exchanges"].extend(exchanges)
        summary["metadata"]["last_updated"] = datetime.now().isoformat()
        summary["metadata"]["total_exchanges"] = len(summary["exchanges"])
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # Update counters
        total_processed += len(file_data)
        
        # Save checkpoint
        save_checkpoint(total_processed, total_processed)
        
        # Log progress
        logger.info(f"Block complete: {len(file_data)} exchanges written")
        logger.info(f"Total progress: {total_processed}/{total_files} ({100*total_processed/total_files:.1f}%)")
        logger.info(f"Cumulative empty AI: {empty_ai_count}/{total_processed} ({100*empty_ai_count/total_processed:.1f}%)")
        
        # Memory cleanup
        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("VECTORIZATION COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Total exchanges processed: {total_processed}")
    logger.info(f"Exchanges without AI response: {empty_ai_count} ({100*empty_ai_count/total_processed:.1f}%)")
    logger.info(f"Valid pairs with AI response: {total_processed - empty_ai_count}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Summary file: {summary_file}")
    logger.info("=" * 80)

if __name__ == "__main__":
    run_complete_vectorization()
