#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_history_logs.py — Import Chat History from Text Files

Imports prompt pairs from backend/Evoki History/2025/ into evoki_v3_core.db
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
import uuid
import logging
import numpy as np

# FAISS and embeddings
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS/SentenceTransformers not available - skipping vector indexing")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Projekt Root finden
REPO_ROOT = Path(__file__).resolve().parents[2]
HISTORY_DIR = REPO_ROOT / "backend" / "Evoki History" / "2025"
DB_PATH = REPO_ROOT / "backend" / "data" / "databases" / "evoki_v3_core.db"
FAISS_DIR = REPO_ROOT / "backend" / "data" / "faiss"
SEMANTIC_FAISS = FAISS_DIR / "evoki_v3_vectors_semantic.faiss"
METRICS_FAISS = FAISS_DIR / "evoki_v3_vectors_metrics.faiss"
FAISS_META_DB = FAISS_DIR / "faiss_metadata.db"

# Embedding models (lazy load)
_semantic_model = None
_metrics_model = None


def get_semantic_model():
    """Get or load semantic embedding model (384D MiniLM for now, TODO: Mistral 4096D)."""
    global _semantic_model
    if _semantic_model is None and FAISS_AVAILABLE:
        # Auto-detect GPU
        try:
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Loading semantic embedding model (all-MiniLM-L6-v2) on {device.upper()}...")
            _semantic_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            if device == 'cuda':
                logger.info(f"  🚀 Using GPU: {torch.cuda.get_device_name(0)}")
        except:
            logger.info("Loading semantic embedding model (all-MiniLM-L6-v2) on CPU...")
            _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _semantic_model


def get_metrics_model():
    """Get or load metrics embedding model (384D MiniLM)."""
    global _metrics_model
    if _metrics_model is None and FAISS_AVAILABLE:
        # Auto-detect GPU
        try:
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Loading metrics embedding model (all-MiniLM-L6-v2) on {device.upper()}...")
            _metrics_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            if device == 'cuda':
                logger.info(f"  🚀 Using GPU: {torch.cuda.get_device_name(0)}")
        except:
            logger.info("Loading metrics embedding model (all-MiniLM-L6-v2) on CPU...")
            _metrics_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _metrics_model


def parse_history_file(file_path: Path) -> tuple:
    """
    Parse history file with header format:
    Timestamp: DD.MM.YYYY, HH:MM:SS MESZ
    Speaker: user|ai
    <blank line>
    <text>
    
    Returns:
        (timestamp_str, speaker, text)
    """
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    timestamp_str = None
    speaker = None
    text_start_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith('Timestamp:'):
            timestamp_str = line.replace('Timestamp:', '').strip()
        elif line.startswith('Speaker:'):
            speaker = line.replace('Speaker:', '').strip()
        elif line.strip() == '' and i > 0:
            text_start_idx = i + 1
            break
    
    text = '\n'.join(lines[text_start_idx:]).strip()
    return timestamp_str, speaker, text


def import_prompt_pair(conn, user_file: Path, ai_file: Path, session_id: str, 
                       faiss_sem_index=None, faiss_meta_conn=None):
    """
    Import a single prompt pair into the database AND FAISS indices.
    
    Args:
        conn: SQLite connection (core DB)
        user_file: Path to user prompt file
        ai_file: Path to AI response file
        session_id: Session ID for grouping
        faiss_sem_index: FAISS semantic index (optional)
        faiss_meta_conn: FAISS metadata DB connection (optional)
    """
    try:
        # Parse files with header
        user_timestamp, user_speaker, user_text = parse_history_file(user_file)
        ai_timestamp, ai_speaker, ai_text = parse_history_file(ai_file)
        
        # Validate speakers
        if user_speaker != 'user' or ai_speaker != 'ai':
            logger.warning(f"Speaker mismatch: {user_file.name} ({user_speaker}/{ai_speaker})")
        
        # Generate pair_id
        pair_hash = hashlib.sha256(f"{user_text}{ai_text}".encode()).hexdigest()[:16]
        pair_id = f"hist_{pair_hash}_{uuid.uuid4().hex[:8]}"
        
        # Use timestamp from file if available, otherwise extract from path
        if user_timestamp:
            # Parse: "DD.MM.YYYY, HH:MM:SS MESZ" -> ISO format
            try:
                from datetime import datetime as dt
                timestamp = dt.strptime(user_timestamp.replace(' MESZ', ''), '%d.%m.%Y, %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = user_timestamp  # Fallback
        else:
            # Extract from path
            parts = user_file.parts
            year_idx = parts.index("2025")
            month = parts[year_idx + 1]
            day = parts[year_idx + 2]
            timestamp = f"2025-{month}-{day} 12:00:00"  # Default to noon
        
        # Insert into prompt_pairs (match actual schema!)
        cursor = conn.cursor()
        
        # Generate turn_number (simple increment per session)
        cursor.execute("SELECT COALESCE(MAX(turn_number), 0) + 1 FROM prompt_pairs WHERE session_id = ?", (session_id,))
        turn_number = cursor.fetchone()[0]
        
        # Convert timestamp to unix
        import time
        ts_unix = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        
        cursor.execute("""
            INSERT OR IGNORE INTO prompt_pairs (
                pair_id, session_id, turn_number, created_at, ts_unix,
                user_text, user_text_hash, ai_text, ai_text_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id, session_id, turn_number, timestamp, ts_unix,
            user_text, hashlib.sha256(user_text.encode()).hexdigest(),
            ai_text, hashlib.sha256(ai_text.encode()).hexdigest()
        ))
        
        if cursor.rowcount == 0:
            logger.debug(f"⏭️ Skipped (duplicate): {user_file.name}")
            return False
        
        # === FAISS INDEXING ===
        if FAISS_AVAILABLE and faiss_sem_index is not None and faiss_meta_conn is not None:
            try:
                # Generate embedding (user prompt for semantic search)
                model = get_semantic_model()
                if model is not None:
                    # Embed user text
                    embedding = model.encode(user_text, convert_to_numpy=True)
                    embedding = embedding.astype('float32')
                    
                    # Normalize for Inner Product (cosine similarity)
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    
                    # Get current FAISS position
                    faiss_position = faiss_sem_index.ntotal
                    
                    # Add to FAISS
                    faiss_sem_index.add(embedding.reshape(1, -1))
                    
                    # Store metadata
                    meta_cursor = faiss_meta_conn.cursor()
                    meta_cursor.execute("""
                        INSERT INTO semantic_index (
                            faiss_position, pair_id, embedding_model, embedding_timestamp
                        ) VALUES (?, ?, ?, ?)
                    """, (faiss_position, pair_id, "all-MiniLM-L6-v2", datetime.now().isoformat()))
                    
                    logger.debug(f"  ↳ Added to FAISS position {faiss_position}")
                    
            except Exception as e:
                logger.warning(f"  ⚠️ FAISS indexing failed: {e}")
        
        logger.info(f"✅ Imported: {user_file.name} → {pair_id}")
        return True
            
    except Exception as e:
        logger.error(f"❌ Failed to import {user_file}: {e}")
        return False


def scan_history_directory():
    """
    Scan the history directory and yield user/AI file pairs.
    
    Yields:
        tuple: (user_file, ai_file, session_id)
    """
    if not HISTORY_DIR.exists():
        logger.warning(f"History directory not found: {HISTORY_DIR}")
        return
    
    # Scan all month/day folders (HISTORY_DIR already points to 2025/)
    year = "2025"  # HISTORY_DIR = .../2025
    
    for month_dir in HISTORY_DIR.iterdir():
        if not month_dir.is_dir():
            continue
        month = month_dir.name  # e.g., "02"
            
        for day_dir in month_dir.iterdir():
            if not day_dir.is_dir():
                continue
            day = day_dir.name  # e.g., "08"
            
            # Session ID from date
            session_id = f"session_{year}_{month}_{day}"
            
            # Find prompt pairs (Prompt1_user.txt, Prompt1_ai.txt, etc.)
            user_files = sorted(day_dir.glob("Prompt*_user.txt"))
            
            for user_file in user_files:
                # Extract prompt number
                prompt_num = user_file.stem.replace("_user", "")
                ai_file = day_dir / f"{prompt_num}_ai.txt"
                
                if ai_file.exists():
                    yield (user_file, ai_file, session_id)
                else:
                    logger.warning(f"Missing AI response for: {user_file}")


def main():
    """Import all history logs into DB + FAISS."""
    logger.info("=" * 80)
    logger.info("EVOKI V3.0 — HISTORY IMPORT (DB + FAISS)")
    logger.info("=" * 80)
    logger.info(f"History Directory: {HISTORY_DIR}")
    logger.info(f"Target Database: {DB_PATH}")
    logger.info(f"FAISS Directory: {FAISS_DIR}")
    logger.info("")
    
    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        logger.error("Run initialize_databases.py first!")
        return 1
    
    # Connect to DBs
    conn = sqlite3.connect(DB_PATH)
    
    # Load or create FAISS index
    faiss_sem_index = None
    faiss_meta_conn = None
    
    if FAISS_AVAILABLE:
        try:
            if SEMANTIC_FAISS.exists():
                logger.info(f"Loading existing FAISS index: {SEMANTIC_FAISS}")
                faiss_sem_index = faiss.read_index(str(SEMANTIC_FAISS))
                logger.info(f"  Current size: {faiss_sem_index.ntotal} vectors")
            else:
                logger.info("Creating new FAISS index (384D, InnerProduct)")
                faiss_sem_index = faiss.IndexFlatIP(384)  # 384D MiniLM
                logger.info("  Created empty index")
            
            # Connect to metadata DB
            faiss_meta_conn = sqlite3.connect(FAISS_META_DB)
            logger.info(f"Connected to FAISS metadata DB: {FAISS_META_DB}")
            
        except Exception as e:
            logger.warning(f"FAISS initialization failed: {e}")
            logger.warning("Continuing WITHOUT vector indexing")
            faiss_sem_index = None
            faiss_meta_conn = None
    else:
        logger.warning("FAISS not available - DB-only import")
    
    try:
        imported = 0
        skipped = 0
        errors = 0
        
        for user_file, ai_file, session_id in scan_history_directory():
            success = import_prompt_pair(
                conn, user_file, ai_file, session_id,
                faiss_sem_index=faiss_sem_index,
                faiss_meta_conn=faiss_meta_conn
            )
            
            if success:
                imported += 1
            elif success is False:
                skipped += 1
            else:
                errors += 1
        
        # Commit all imports
        conn.commit()
        if faiss_meta_conn:
            faiss_meta_conn.commit()
        
        # Save FAISS index
        if faiss_sem_index is not None and imported > 0:
            logger.info("")
            logger.info(f"Saving FAISS index with {faiss_sem_index.ntotal} vectors...")
            FAISS_DIR.mkdir(parents=True, exist_ok=True)
            faiss.write_index(faiss_sem_index, str(SEMANTIC_FAISS))
            logger.info(f"  ✅ Saved to: {SEMANTIC_FAISS}")
        
        # Stats
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prompt_pairs")
        total_imported = cursor.fetchone()[0]
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ IMPORT COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Imported this run: {imported}")
        logger.info(f"Skipped (duplicates): {skipped}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Total in DB: {total_imported}")
        
        if faiss_sem_index:
            logger.info(f"Total in FAISS: {faiss_sem_index.ntotal}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        conn.close()
        if faiss_meta_conn:
            faiss_meta_conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
