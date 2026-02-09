"""
Keyword Extractor
Automatic keyword extraction from prompts
"""
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Set


# German stopwords
STOPWORDS = {
    'der', 'die', 'das', 'den', 'dem', 'des',
    'ein', 'eine', 'einer', 'eines', 'einem', 'einen',
    'und', 'oder', 'aber', 'doch', 'sondern',
    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
    'mein', 'dein', 'sein', 'ihr', 'unser', 'euer',
    'ist', 'sind', 'war', 'waren', 'hat', 'haben', 'hatte', 'hatten',
    'wird', 'werden', 'wurde', 'wurden',
    'kann', 'können', 'konnte', 'muss', 'müssen', 'musste',
    'mit', 'von', 'zu', 'aus', 'bei', 'nach', 'vor', 'über', 'unter',
    'für', 'gegen', 'ohne', 'durch', 'um',
    'in', 'an', 'auf', 'als', 'wie', 'wenn', 'weil', 'dass',
    'nicht', 'nur', 'auch', 'noch', 'schon', 'mehr',
    'sehr', 'viel', 'wenig', 'gut', 'schlecht',
    'was', 'wie', 'wo', 'wann', 'warum', 'wer', 'wen', 'wem'
}


def extract_keywords(text: str, min_length: int = 3, min_frequency: int = 1) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum word length (default 3)
        min_frequency: Minimum frequency to be considered keyword (default 1)
    
    Returns:
        List of extracted keywords
    """
    # Normalize text
    text = text.lower()
    
    # Extract words (alphanumeric + umlauts)
    words = re.findall(r'\b[\wäöüß]+\b', text)
    
    # Filter stopwords and short words
    words = [
        word for word in words 
        if word not in STOPWORDS and len(word) >= min_length
    ]
    
    # Count frequency
    freq = Counter(words)
    
    # Return keywords with sufficient frequency
    keywords = [word for word, count in freq.items() if count >= min_frequency]
    
    return keywords


def get_keywords_db():
    """Get connection to keywords database"""
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_keywords.db"
    return sqlite3.connect(str(db_path))


def register_keyword(keyword: str):
    """
    Register a keyword in the registry (or increment frequency)
    
    Args:
        keyword: The keyword to register
    
    Returns:
        keyword_id
    """
    conn = get_keywords_db()
    timestamp = datetime.now().isoformat()
    
    # Check if keyword exists
    cursor = conn.execute("SELECT keyword_id, frequency FROM keyword_registry WHERE keyword = ?", (keyword,))
    row = cursor.fetchone()
    
    if row:
        keyword_id, freq = row
        # Increment frequency
        conn.execute("""
            UPDATE keyword_registry 
            SET frequency = frequency + 1, last_seen = ?
            WHERE keyword_id = ?
        """, (timestamp, keyword_id))
    else:
        # New keyword
        keyword_id = f"kw_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        conn.execute("""
            INSERT INTO keyword_registry 
            (keyword_id, keyword, frequency, first_seen, last_seen)
            VALUES (?, ?, 1, ?, ?)
        """, (keyword_id, keyword, timestamp, timestamp))
    
    conn.commit()
    conn.close()
    
    return keyword_id


def link_keyword_to_pair(keyword: str, pair_id: str, context_window: str = None):
    """
    Link a keyword to a prompt pair
    
    Args:
        keyword: The keyword
        pair_id: The prompt pair ID
        context_window: Optional context (20 chars before + 20 after)
    """
    conn = get_keywords_db()
    
    # Get or create keyword
    keyword_id = register_keyword(keyword)
    
    # Create link
    link_id = f"link_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    timestamp = datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO keyword_pair_links 
        (link_id, keyword_id, pair_id, context_window, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (link_id, keyword_id, pair_id, context_window, timestamp))
    
    conn.commit()
    conn.close()
    
    return link_id


def extract_and_register_keywords(text: str, pair_id: str) -> List[str]:
    """
    Extract keywords from text and register them
    
    Args:
        text: Text to analyze
        pair_id: Prompt pair ID
    
    Returns:
        List of extracted keywords
    """
    keywords = extract_keywords(text)
    
    for keyword in keywords:
        # Find context window (20 chars before + 20 after)
        pattern = re.compile(rf'(.{{0,20}})\b{re.escape(keyword)}\b(.{{0,20}})', re.IGNORECASE)
        match = pattern.search(text)
        
        context = None
        if match:
            context = match.group(1) + keyword + match.group(2)
        
        link_keyword_to_pair(keyword, pair_id, context)
    
    return keywords


def get_top_keywords(limit: int = 50) -> List[tuple]:
    """Get most frequent keywords"""
    conn = get_keywords_db()
    
    cursor = conn.execute("""
        SELECT keyword, frequency
        FROM keyword_registry
        ORDER BY frequency DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def search_by_keyword(keyword: str, limit: int = 10) -> List[str]:
    """
    Search for prompt pairs containing a keyword
    
    Args:
        keyword: Keyword to search for
        limit: Max results
    
    Returns:
        List of pair_ids
    """
    conn = get_keywords_db()
    
    cursor = conn.execute("""
        SELECT kpl.pair_id, kpl.context_window
        FROM keyword_pair_links kpl
        JOIN keyword_registry kr ON kpl.keyword_id = kr.keyword_id
        WHERE kr.keyword = ?
        ORDER BY kpl.created_at DESC
        LIMIT ?
    """, (keyword, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
