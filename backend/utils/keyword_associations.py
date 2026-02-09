"""
Keyword Association Learning
Learns co-occurrence patterns and computes PMI scores
"""
import math
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Tuple


def get_keywords_db():
    """Get connection to keywords database"""
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_keywords.db"
    return sqlite3.connect(str(db_path))


def learn_keyword_associations(keywords: List[str]):
    """
    Learn associations between co-occurring keywords
    
    Args:
        keywords: List of keywords from a single prompt
    """
    conn = get_keywords_db()
    timestamp = datetime.now().isoformat()
    
    # For each pair of keywords
    for i, kw_a in enumerate(keywords):
        for kw_b in keywords[i+1:]:
            # Ensure alphabetical order for consistency
            if kw_a > kw_b:
                kw_a, kw_b = kw_b, kw_a
            
            # Check if association exists
            cursor = conn.execute("""
                SELECT assoc_id, co_occurrence_count 
                FROM keyword_associations 
                WHERE keyword_a = ? AND keyword_b = ?
            """, (kw_a, kw_b))
            
            row = cursor.fetchone()
            
            if row:
                # Increment co-occurrence
                assoc_id, count = row
                conn.execute("""
                    UPDATE keyword_associations 
                    SET co_occurrence_count = co_occurrence_count + 1
                    WHERE assoc_id = ?
                """, (assoc_id,))
            else:
                # New association
                assoc_id = f"assoc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                conn.execute("""
                    INSERT INTO keyword_associations 
                    (assoc_id, keyword_a, keyword_b, co_occurrence_count, created_at)
                    VALUES (?, ?, ?, 1, ?)
                """, (assoc_id, kw_a, kw_b, timestamp))
    
    conn.commit()
    conn.close()


def compute_pmi_score(keyword_a: str, keyword_b: str) -> float:
    """
    Compute Pointwise Mutual Information (PMI) score
    
    PMI(A,B) = log(P(A,B) / (P(A) * P(B)))
    
    Args:
        keyword_a: First keyword
        keyword_b: Second keyword
    
    Returns:
        PMI score (higher = stronger association)
    """
    conn = get_keywords_db()
    
    # Total number of prompts
    cursor = conn.execute("SELECT COUNT(DISTINCT pair_id) FROM keyword_pair_links")
    total_prompts = cursor.fetchone()[0]
    
    if total_prompts == 0:
        conn.close()
        return 0.0
    
    # P(A) - Probability of keyword A
    cursor = conn.execute("""
        SELECT COUNT(DISTINCT pair_id) 
        FROM keyword_pair_links kpl
        JOIN keyword_registry kr ON kpl.keyword_id = kr.keyword_id
        WHERE kr.keyword = ?
    """, (keyword_a,))
    count_a = cursor.fetchone()[0]
    p_a = count_a / total_prompts
    
    # P(B) - Probability of keyword B
    cursor = conn.execute("""
        SELECT COUNT(DISTINCT pair_id) 
        FROM keyword_pair_links kpl
        JOIN keyword_registry kr ON kpl.keyword_id = kr.keyword_id
        WHERE kr.keyword = ?
    """, (keyword_b,))
    count_b = cursor.fetchone()[0]
    p_b = count_b / total_prompts
    
    # P(A,B) - Probability of both
    cursor = conn.execute("""
        SELECT co_occurrence_count 
        FROM keyword_associations 
        WHERE (keyword_a = ? AND keyword_b = ?) 
           OR (keyword_a = ? AND keyword_b = ?)
    """, (keyword_a, keyword_b, keyword_b, keyword_a))
    
    row = cursor.fetchone()
    count_ab = row[0] if row else 0
    p_ab = count_ab / total_prompts
    
    conn.close()
    
    # Compute PMI
    if p_a == 0 or p_b == 0 or p_ab == 0:
        return 0.0
    
    pmi = math.log(p_ab / (p_a * p_b))
    
    return pmi


def update_all_pmi_scores():
    """Recompute PMI scores for all associations"""
    conn = get_keywords_db()
    
    cursor = conn.execute("SELECT keyword_a, keyword_b FROM keyword_associations")
    associations = cursor.fetchall()
    
    for keyword_a, keyword_b in associations:
        pmi = compute_pmi_score(keyword_a, keyword_b)
        
        conn.execute("""
            UPDATE keyword_associations
            SET pmi_score = ?
            WHERE keyword_a = ? AND keyword_b = ?
        """, (pmi, keyword_a, keyword_b))
    
    conn.commit()
    conn.close()


def get_related_keywords(keyword: str, limit: int = 10) -> List[Tuple[str, float, int]]:
    """
    Find keywords most strongly associated with given keyword
    
    Args:
        keyword: Query keyword
        limit: Max results
    
    Returns:
        List of (related_keyword, pmi_score, co_occurrence_count)
    """
    conn = get_keywords_db()
    
    cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN keyword_a = ? THEN keyword_b 
                ELSE keyword_a 
            END as related_keyword,
            pmi_score,
            co_occurrence_count
        FROM keyword_associations
        WHERE keyword_a = ? OR keyword_b = ?
        ORDER BY pmi_score DESC
        LIMIT ?
    """, (keyword, keyword, keyword, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def cluster_keywords_by_similarity(min_pmi: float = 1.0) -> List[List[str]]:
    """
    Cluster keywords based on PMI scores
    
    Args:
        min_pmi: Minimum PMI threshold for clustering
    
    Returns:
        List of keyword clusters
    """
    conn = get_keywords_db()
    
    # Get all strong associations
    cursor = conn.execute("""
        SELECT keyword_a, keyword_b, pmi_score
        FROM keyword_associations
        WHERE pmi_score >= ?
        ORDER BY pmi_score DESC
    """, (min_pmi,))
    
    associations = cursor.fetchall()
    conn.close()
    
    # Simple clustering: union-find
    clusters = {}
    
    for keyword_a, keyword_b, pmi in associations:
        # Find cluster for A
        cluster_a = clusters.get(keyword_a, {keyword_a})
        # Find cluster for B
        cluster_b = clusters.get(keyword_b, {keyword_b})
        
        # Merge clusters
        merged = cluster_a | cluster_b
        
        # Update all keywords in merged cluster
        for kw in merged:
            clusters[kw] = merged
    
    # De-duplicate clusters
    unique_clusters = list({frozenset(cluster): cluster for cluster in clusters.values()}.values())
    
    return [sorted(list(cluster)) for cluster in unique_clusters]
