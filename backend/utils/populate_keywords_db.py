"""
Populate keywords database from existing prompt pairs
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.keyword_extractor import extract_keywords, register_keyword, link_keyword_to_pair


def populate_keywords_db(limit=None):
    """Extract keywords from all prompt pairs and populate keywords DB"""
    
    # Connect to core DB
    core_db = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_core.db"
    conn_core = sqlite3.connect(str(core_db))
    
    # Get all prompt pairs
    query = "SELECT pair_id, user_prompt, ai_response FROM prompt_pairs"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor = conn_core.execute(query)
    pairs = cursor.fetchall()
    
    print(f"Processing {len(pairs):,} prompt pairs...")
    
    total_keywords = 0
    processed = 0
    
    for pair_id, user_prompt, ai_response in pairs:
        # Extract keywords from user prompt
        user_keywords = extract_keywords(user_prompt or "", min_length=3, min_frequency=1)
        
        # Extract keywords from AI response
        ai_keywords = extract_keywords(ai_response or "", min_length=3, min_frequency=1)
        
        # Combine
        all_keywords = list(set(user_keywords + ai_keywords))
        
        # Register and link
        for keyword in all_keywords:
            # Find context window
            text = (user_prompt or "") + " " + (ai_response or "")
            import re
            pattern = re.compile(rf'(.{{0,20}})\b{re.escape(keyword)}\b(.{{0,20}})', re.IGNORECASE)
            match = pattern.search(text)
            
            context = None
            if match:
                context = match.group(1) + keyword + match.group(2)
            
            try:
                link_keyword_to_pair(keyword, pair_id, context)
                total_keywords += 1
            except Exception as e:
                pass  # Duplicate links are ok
        
        processed += 1
        if processed % 1000 == 0:
            print(f"  Processed: {processed:,} pairs, {total_keywords:,} keyword links")
    
    conn_core.close()
    
    print(f"\n✅ Populated keywords database!")
    print(f"   Processed pairs: {processed:,}")
    print(f"   Total keyword links: {total_keywords:,}")
    
    # Get stats
    keywords_db = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_keywords.db"
    conn_kw = sqlite3.connect(str(keywords_db))
    
    cursor = conn_kw.execute("SELECT COUNT(*) FROM keyword_registry")
    unique_keywords = cursor.fetchone()[0]
    
    cursor = conn_kw.execute("SELECT COUNT(*) FROM keyword_pair_links")
    total_links = cursor.fetchone()[0]
    
    print(f"\n📊 Keywords Database Stats:")
    print(f"   Unique keywords: {unique_keywords:,}")
    print(f"   Total links: {total_links:,}")
    print(f"   Avg keywords/pair: {total_links / processed:.1f}")
    
    conn_kw.close()


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    if limit:
        print(f"⚠️ TESTING MODE: Processing only {limit} pairs")
    else:
        print(f"🔥 FULL MODE: Processing ALL 10,971 pairs")
    
    populate_keywords_db(limit=limit)
