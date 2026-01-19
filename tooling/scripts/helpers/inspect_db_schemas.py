#!/usr/bin/env python3
"""
Database Schema Inspector
Inspects all skeleton databases and compares schemas.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Dynamic project root
EVOKI_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEEP_EARTH_LAYERS = EVOKI_ROOT / "app" / "deep_earth" / "layers"
TWENTYONE_DBS = EVOKI_ROOT / "tooling" / "data" / "db" / "21dbs"
REFERENCE_SCHEMA = EVOKI_ROOT / "backend" / "utils" / "db_schema.sql"
OUTPUT_FILE = EVOKI_ROOT / "tooling" / "data" / "schema_comparison_report.md"

def get_db_schema(db_path: Path):
    """Extract complete schema from a SQLite database."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Get indices
            cursor.execute(f"PRAGMA index_list({table})")
            indices = cursor.fetchall()
            
            schema[table] = {
                "columns": [
                    {
                        "cid": col[0],
                        "name": col[1],
                        "type": col[2],
                        "notnull": bool(col[3]),
                        "default": col[4],
                        "pk": bool(col[5])
                    }
                    for col in columns
                ],
                "indices": [idx[1] for idx in indices],
                "row_count": cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            }
        
        conn.close()
        return schema
    
    except Exception as e:
        return {"error": str(e)}

def inspect_all_databases():
    """Inspect all databases and collect schema information."""
    print("🔍 Inspecting databases...")
    
    report = {
        "inspection_timestamp": datetime.now().isoformat(),
        "deep_earth_layers": {},
        "twentyone_dbs": {},
        "schema_comparison": {}
    }
    
    # Deep Earth Layers
    print(f"\n📂 Deep Earth Layers: {DEEP_EARTH_LAYERS}")
    for layer_dir in sorted(DEEP_EARTH_LAYERS.glob("??_*")):
        if layer_dir.is_dir():
            db_path = layer_dir / "layer.db"
            if db_path.exists():
                print(f"  • {layer_dir.name}/layer.db")
                schema = get_db_schema(db_path)
                report["deep_earth_layers"][layer_dir.name] = {
                    "path": str(db_path.relative_to(EVOKI_ROOT)),
                    "schema": schema
                }
    
    # 21 Databases
    print(f"\n📂 21 Databases: {TWENTYONE_DBS}")
    for db_path in sorted(TWENTYONE_DBS.glob("*.db")):
        print(f"  • {db_path.name}")
        schema = get_db_schema(db_path)
        report["twentyone_dbs"][db_path.stem] = {
            "path": str(db_path.relative_to(EVOKI_ROOT)),
            "schema": schema
        }
    
    # Schema Comparison
    print("\n🔍 Comparing schemas...")
    
    # Check if all have same structure
    all_schemas = list(report["deep_earth_layers"].values()) + list(report["twentyone_dbs"].values())
    
    unique_schemas = {}
    for db_name, db_data in {**report["deep_earth_layers"], **report["twentyone_dbs"]}.items():
        schema_sig = json.dumps(db_data["schema"], sort_keys=True)
        if schema_sig not in unique_schemas:
            unique_schemas[schema_sig] = []
        unique_schemas[schema_sig].append(db_name)
    
    report["schema_comparison"]["unique_schema_count"] = len(unique_schemas)
    report["schema_comparison"]["schema_groups"] = {
        f"group_{i+1}": dbs for i, dbs in enumerate(unique_schemas.values())
    }
    
    return report

def generate_markdown_report(report: dict):
    """Generate human-readable markdown report."""
    md = []
    md.append("# Database Schema Comparison Report\n")
    md.append(f"**Generated:** {report['inspection_timestamp']}\n")
    md.append("---\n")
    
    # Deep Earth Layers
    md.append("## 📂 Deep Earth Layers (12 Layers)\n")
    for layer_name, data in sorted(report["deep_earth_layers"].items()):
        md.append(f"### {layer_name}\n")
        md.append(f"**Path:** `{data['path']}`\n")
        
        if "error" in data["schema"]:
            md.append(f"**Status:** ❌ Error - {data['schema']['error']}\n")
        elif not data["schema"]:
            md.append("**Status:** ✅ Empty skeleton (no tables)\n")
        else:
            md.append(f"**Status:** ✅ {len(data['schema'])} table(s)\n")
            for table_name, table_info in data["schema"].items():
                md.append(f"  - **Table:** `{table_name}` ({table_info['row_count']} rows)\n")
                md.append(f"    - Columns: {len(table_info['columns'])}\n")
    
    # 21 Databases
    md.append("\n## 📂 21 Databases\n")
    for db_name, data in sorted(report["twentyone_dbs"].items()):
        md.append(f"### {db_name}.db\n")
        md.append(f"**Path:** `{data['path']}`\n")
        
        if "error" in data["schema"]:
            md.append(f"**Status:** ❌ Error - {data['schema']['error']}\n")
        elif not data["schema"]:
            md.append("**Status:** ✅ Empty skeleton (no tables)\n")
        else:
            md.append(f"**Status:** ✅ {len(data['schema'])} table(s)\n")
            for table_name, table_info in data["schema"].items():
                md.append(f"  - **Table:** `{table_name}` ({table_info['row_count']} rows)\n")
                md.append(f"    - Columns: {len(table_info['columns'])}\n")
    
    # Schema Comparison
    md.append("\n## 🔍 Schema Comparison\n")
    md.append(f"**Unique Schemas:** {report['schema_comparison']['unique_schema_count']}\n\n")
    
    for group_name, dbs in report['schema_comparison']['schema_groups'].items():
        md.append(f"### {group_name}\n")
        md.append(f"Databases with identical schema: {len(dbs)}\n")
        for db in dbs:
            md.append(f"  - `{db}`\n")
        md.append("\n")
    
    return "".join(md)

def main():
    print("=" * 60)
    print("DATABASE SCHEMA INSPECTOR")
    print("=" * 60)
    
    report = inspect_all_databases()
    
    # Save JSON report
    json_output = OUTPUT_FILE.with_suffix('.json')
    json_output.parent.mkdir(parents=True, exist_ok=True)
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON report saved: {json_output.relative_to(EVOKI_ROOT)}")
    
    # Save Markdown report
    md_content = generate_markdown_report(report)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Markdown report saved: {OUTPUT_FILE.relative_to(EVOKI_ROOT)}")
    
    # Print summary
    print("\n📊 SUMMARY:")
    print(f"  Deep Earth Layers: {len(report['deep_earth_layers'])}")
    print(f"  21 Databases: {len(report['twentyone_dbs'])}")
    print(f"  Unique Schemas: {report['schema_comparison']['unique_schema_count']}")
    
    return 0

if __name__ == "__main__":
    exit(main())
