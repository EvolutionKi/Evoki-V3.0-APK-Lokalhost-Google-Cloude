#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
EVOKI V3.0 - DATABASE INITIALIZER
═══════════════════════════════════════════════════════════════════════════
Creates and initializes ALL 4 databases with proper structure

DATABASES:
1. evoki_metadata.db     - Full text storage (prompt pairs, sessions)
2. evoki_resonance.db    - Core metrics (m1-m100, NO TEXT!)
3. evoki_triggers.db     - Trauma/Hazard (m101-m115, m151, NO TEXT!)
4. evoki_metapatterns.db - System/Meta (m116-m168, NO TEXT!)

CRITICAL PRINCIPLE:
- ONLY metadata.db contains full text!
- ALL other DBs: pair_id + hash + timecode + author only!
═══════════════════════════════════════════════════════════════════════════
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List

# =============================================================================
# CONFIGURATION
# =============================================================================

# Project root detection
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # backend/utils/ -> backend/ -> project/

# Data directory
DATA_DIR = PROJECT_ROOT / "app" / "deep_earth" / "databases"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Schema directory
SCHEMA_DIR = PROJECT_ROOT / "backend" / "schemas"

# Database files
DATABASES = {
    "metadata": DATA_DIR / "evoki_metadata.db",
    "resonance": DATA_DIR / "evoki_resonance.db",
    "triggers": DATA_DIR / "evoki_triggers.db",
    "metapatterns": DATA_DIR / "evoki_metapatterns.db"
}

# Schema files
SCHEMAS = {
    "metadata": SCHEMA_DIR / "evoki_metadata_schema.sql",
    "resonance": SCHEMA_DIR / "evoki_resonance_schema.sql",
    "triggers": SCHEMA_DIR / "evoki_triggers_schema.sql",
    "metapatterns": SCHEMA_DIR / "evoki_metapatterns_schema.sql"
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def init_database(db_path: Path, schema_path: Path, db_name: str) -> bool:
    """
    Initialize a single database with schema
    
    Args:
        db_path: Path to database file
        schema_path: Path to schema SQL file
        db_name: Name for logging
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        # Check schema exists
        if not schema_path.exists():
            print(f"❌ Schema not found: {schema_path}")
            return False
        
        # Read schema
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ {db_name:20s} - {len(tables)} tables created")
        for table in tables:
            print(f"   └─ {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ {db_name} FAILED: {e}")
        return False


def verify_database(db_path: Path, db_name: str) -> Dict[str, any]:
    """
    Verify database structure and metadata
    
    Returns:
        Dict with verification results
    """
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count tables
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        # Count indices
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        index_count = cursor.fetchone()[0]
        
        # Count views
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
        view_count = cursor.fetchone()[0]
        
        # Get size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_bytes = cursor.fetchone()[0]
        
        # Check WAL mode
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        
        # Check foreign keys
        cursor.execute("PRAGMA foreign_keys")
        foreign_keys = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "tables": table_count,
            "indices": index_count,
            "views": view_count,
            "size_kb": size_bytes / 1024,
            "journal_mode": journal_mode,
            "foreign_keys": bool(foreign_keys)
        }
        
    except Exception as e:
        return {"error": str(e)}


def check_text_separation() -> Dict[str, bool]:
    """
    CRITICAL CHECK: Verify that ONLY metadata DB has text columns!
    
    Returns:
        Dict with check results
    """
    
    print("\n" + "="*70)
    print("TEXT SEPARATION VERIFICATION (CRITICAL!)")
    print("="*70)
    
    results = {}
    
    # Expected text columns per database
    expected = {
        "metadata": ["user_text", "ai_text"],  # ONLY HERE!
        "resonance": [],  # NO TEXT!
        "triggers": [],   # NO TEXT!
        "metapatterns": []  # NO TEXT!
    }
    
    for db_name, db_path in DATABASES.items():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            tables = [t[0] for t in cursor.fetchall()]
            
            # Check each table for text-like columns
            text_columns_found = []
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_name = col[1].lower()
                    col_type = col[2].lower()
                    
                    # Detect TEXT columns (but exclude metadata columns)
                    if ("TEXT" in col_type.upper() and 
                        col_name in ["user_text", "ai_text", "prompt_text", "response_text"]):
                        text_columns_found.append(f"{table}.{col_name}")
           
            conn.close()
            
            # Compare with expected
            expected_cols = expected.get(db_name, [])
            unexpected = [c for c in text_columns_found if c.split('.')[1] not in expected_cols]
            
            if db_name == "metadata":
                # Should have text columns
                has_text = len(text_columns_found) > 0
                status = "✅" if has_text else "❌"
                print(f"{status} {db_name:15s} - Text columns: {text_columns_found}")
                results[db_name] = has_text
            else:
                # Should NOT have unexpected text columns
                no_unexpected = len(unexpected) == 0
                status = "✅" if no_unexpected else "⚠️"
                if unexpected:
                    print(f"{status} {db_name:15s} - Unexpected text: {unexpected}")
                else:
                    print(f"{status} {db_name:15s} - No full text (correct!)")
                results[db_name] = no_unexpected
                
        except Exception as e:
            print(f"❌ {db_name:15s} - Error: {e}")
            results[db_name] = False
    
    return results


def main():
    """Main initialization routine"""
    
    print("="*70)
    print("EVOKI V3.0 - DATABASE INITIALIZATION")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Dir:     {DATA_DIR}")
    print(f"Schema Dir:   {SCHEMA_DIR}")
    print("="*70)
    
    # Initialize each database
    success_count = 0
    
    for db_name, db_path in DATABASES.items():
        print(f"\n--- Initializing {db_name.upper()} ---")
        
        schema_path = SCHEMAS[db_name]
        
        # Backup existing (if any)
        if db_path.exists():
            backup_path = db_path.with_suffix('.db.backup')
            print(f"⚠️  Existing DB found, backing up to: {backup_path.name}")
            db_path.rename(backup_path)
        
        # Initialize
        if init_database(db_path, schema_path, db_name):
            success_count += 1
        else:
            print(f"❌ Failed to initialize {db_name}!")
    
    # Verification
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    for db_name, db_path in DATABASES.items():
        info = verify_database(db_path, db_name)
        if "error" in info:
            print(f"❌ {db_name:15s} - {info['error']}")
        else:
            print(f"✅ {db_name:15s} - "
                  f"{info['tables']} tables, "
                  f"{info['indices']} indices, "
                  f"{info['views']} views, "
                  f"{info['size_kb']:.1f} KB, "
                  f"WAL={info['journal_mode']}, "
                  f"FK={info['foreign_keys']}")
    
    # TEXT SEPARATION CHECK (CRITICAL!)
    sep_results = check_text_separation()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Databases initialized: {success_count}/4")
    print(f"Text separation valid: {all(sep_results.values())}")
    
    if success_count == 4 and all(sep_results.values()):
        print("\n🎉 ALL DATABASES READY! ✅")
        return 0
    else:
        print("\n⚠️  INITIALIZATION INCOMPLETE!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
