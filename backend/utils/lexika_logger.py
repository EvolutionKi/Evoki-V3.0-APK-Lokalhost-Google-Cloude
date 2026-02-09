"""
Lexika Verification Logger
Logs all lexika hits for analytics and debugging
"""
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Dict


def get_analytics_db():
    """Get connection to analytics database"""
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_analytics.db"
    return sqlite3.connect(str(db_path))


def log_lexika_verification(
    pair_id: str,
    text: str,
    lexikon_name: str,
    hits: List[str],
    score: float
):
    """
    Log lexika verification results
    
    Args:
        pair_id: ID of the prompt pair
        text: The analyzed text
        lexikon_name: Name of the lexikon (e.g., "T_panic", "Suicide")
        hits: List of matched terms
        score: Calculated score from hits
    """
    conn = get_analytics_db()
    
    verify_id = f"lexverif_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    hits_count = len(hits)
    matched_terms = json.dumps(hits, ensure_ascii=False)
    timestamp = datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO lexika_verification_log 
        (verify_id, pair_id, lexikon_name, hits_count, matched_terms, score, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (verify_id, pair_id, lexikon_name, hits_count, matched_terms, score, timestamp))
    
    conn.commit()
    conn.close()
    
    return verify_id


def verify_text_against_all_lexika(pair_id: str, text: str, lexika_dict: Dict[str, Dict[str, float]]):
    """
    Verify text against all lexika and log results
    
    Args:
        pair_id: ID of the prompt pair
        text: Text to analyze
        lexika_dict: Dictionary of all lexika {lexikon_name: {term: weight}}
    
    Returns:
        Dict with all lexika hits and scores
    """
    results = {}
    words = text.lower().split()
    
    for lexikon_name, lexikon_terms in lexika_dict.items():
        hits = [word for word in words if word in lexikon_terms]
        
        if hits:
            # Calculate weighted score
            score = sum(lexikon_terms.get(word, 0) for word in hits)
            
            # Log to analytics
            log_lexika_verification(pair_id, text, lexikon_name, hits, score)
            
            results[lexikon_name] = {
                "hits_count": len(hits),
                "matched_terms": hits,
                "score": score
            }
    
    return results


def get_lexika_stats_for_pair(pair_id: str):
    """Get all lexika verification stats for a specific pair"""
    conn = get_analytics_db()
    
    cursor = conn.execute("""
        SELECT lexikon_name, hits_count, matched_terms, score
        FROM lexika_verification_log
        WHERE pair_id = ?
        ORDER BY score DESC
    """, (pair_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_most_triggered_lexika(limit: int = 10):
    """Get lexika that trigger most frequently"""
    conn = get_analytics_db()
    
    cursor = conn.execute("""
        SELECT lexikon_name, COUNT(*) as trigger_count, AVG(score) as avg_score
        FROM lexika_verification_log
        WHERE hits_count > 0
        GROUP BY lexikon_name
        ORDER BY trigger_count DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
