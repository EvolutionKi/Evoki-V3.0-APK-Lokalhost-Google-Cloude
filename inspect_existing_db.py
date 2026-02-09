#!/usr/bin/env python3
"""
Inspect EXISTING evoki_v3_core.db
"""

import sqlite3

db_path = r'C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\data\databases\evoki_v3_core.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("📊 EXISTING DB - evoki_v3_core.db")
print("=" * 100)

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"\n📋 Tables: {tables}")

for table in tables:
    print(f"\n{'='*100}")
    print(f"TABLE: {table}")
    print(f"{'='*100}")
    
    # Schema
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    print("\n🔍 SCHEMA:")
    for col in columns:
        print(f"  {col[1]:30s} {col[2]:15s} {'PK' if col[5] else ''}")
    
    # Count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"\n📊 Row count: {count}")
    
    # Sample if data exists
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        rows = cursor.fetchall()
        print(f"\n🔬 Sample (first 2 rows):")
        for i, row in enumerate(rows, 1):
            print(f"\n  Row {i}:")
            for col_info, value in zip(columns, row):
                col_name = col_info[1]
                if isinstance(value, str) and len(str(value)) > 80:
                    display_val = str(value)[:77] + "..."
                else:
                    display_val = value
                print(f"    {col_name:30s} = {display_val}")

conn.close()

print("\n" + "=" * 100)
print("✅ INSPECTION COMPLETE")
print("=" * 100)
