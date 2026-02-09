"""
Search Event Logger
Simple utility to log all search queries to analytics DB
"""
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Dict, Any


def get_analytics_db():
    """Get connection to analytics database"""
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_analytics.db"
    return sqlite3.connect(str(db_path))


def log_search_event(
    query: str,
    search_type: str,  # 'semantic', 'metrics', 'trajectory', 'keyword'
    results: List[Dict[str, Any]]
):
    """
    Log a search event to analytics DB
    
    Args:
        query: The search query text
        search_type: Type of search performed
        results: List of search results
    """
    conn = get_analytics_db()
    
    search_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    results_count = len(results)
    top_5_results = json.dumps(results[:5])
    timestamp = datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO search_events 
        (search_id, query, search_type, results_count, top_5_results, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (search_id, query, search_type, results_count, top_5_results, timestamp))
    
    conn.commit()
    conn.close()
    
    return search_id


def get_recent_searches(limit: int = 10, search_type: str = None):
    """Get recent searches, optionally filtered by type"""
    conn = get_analytics_db()
    
    if search_type:
        cursor = conn.execute("""
            SELECT * FROM search_events 
            WHERE search_type = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (search_type, limit))
    else:
        cursor = conn.execute("""
            SELECT * FROM search_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_popular_queries(limit: int = 10):
    """Get most popular search queries"""
    conn = get_analytics_db()
    
    cursor = conn.execute("""
        SELECT query, COUNT(*) as count
        FROM search_events
        GROUP BY query
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
