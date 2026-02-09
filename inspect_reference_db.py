#!/usr/bin/env python3
"""
Inspect reference DB from evoki_pipeline
"""

import sqlite3
import json

db_path = r'C:\Users\nicom\Documents\evoki\evoki_pipeline\metric_chunks_test\text_index.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("📊 REFERENCE DB INSPECTION - evoki_pipeline/metric_chunks_test/text_index.db")
print("=" * 100)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"\n📋 Tables: {tables}")

for table in tables:
    print(f"\n{'='*100}")
    print(f"TABLE: {table}")
    print(f"{'='*100}")
    
    # Get schema
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    print("\n🔍 SCHEMA:")
    for col in columns:
        print(f"  {col[1]:30s} {col[2]:15s} {'PK' if col[5] else ''}")
    
    # Get count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"\n📊 Row count: {count}")
    
    # Get sample rows
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"\n🔬 Sample rows (first 3):")
        for i, row in enumerate(rows, 1):
            print(f"\n  Row {i}:")
            for col_info, value in zip(columns, row):
                col_name = col_info[1]
                if isinstance(value, str) and len(str(value)) > 100:
                    display_val = str(value)[:97] + "..."
                else:
                    display_val = value
                print(f"    {col_name:30s} = {display_val}")

conn.close()

print("\n" + "=" * 100)
print("✅ INSPECTION COMPLETE")
print("=" * 100)
