"""
21-DB Creation Script - Phase 1

Erstellt alle 21 SQLite Datenbanken für Evoki V3.0:
- 1x master_timeline.db (alle Chunks + Metriken)
- 12x W-P-F Tempel (Zeitmaschine: Past → Present → Future)
- 7x B-Vektor DBs (eine pro Soul-Dimension)
- 1x composite.db (B_align, F_risk, risk_z)

Speicherort: tooling/data/db/21dbs/
"""
import sqlite3
from pathlib import Path

# Wo sollen die DBs hin?
DB_BASE = Path(__file__).parent.parent.parent / "tooling" / "data" / "db" / "21dbs"
DB_BASE.mkdir(parents=True, exist_ok=True)

# Liste aller 21 Datenbanken
DATABASES = [
    "master_timeline.db",
    
    # 12 W-P-F Tempel (Vergangenheit → Zukunft)
    "tempel_W_m25.db",   # -25 Minuten
    "tempel_W_m5.db",    # -5 Minuten  
    "tempel_W_m2.db",    # -2 Minuten
    "tempel_W_m1.db",    # -1 Minute
    "tempel_W.db",       # Jetzt (W = Wirklichkeit)
    "tempel_F_p1.db",    # +1 Minute
    "tempel_F_p2.db",    # +2 Minuten
    "tempel_F_p5.db",    # +5 Minuten
    "tempel_F_p25.db",   # +25 Minuten
    
    # 7 B-Vektor DBs (eine pro Dimension)
    "bvec_life.db",
    "bvec_truth.db",
    "bvec_depth.db",
    "bvec_init.db",
    "bvec_warmth.db",
    "bvec_safety.db",
    "bvec_clarity.db",
    
    # 1 Composite DB
    "composite.db"
]


def create_databases():
    """Erstellt alle 21 Datenbanken"""
    
    # SQL Schema laden
    schema_file = Path(__file__).parent / "db_schema.sql"
    if not schema_file.exists():
        print(f"❌ FEHLER: db_schema.sql nicht gefunden!")
        print(f"   Erwartet in: {schema_file}")
        return
    
    schema = schema_file.read_text(encoding='utf-8')
    
    print(f"📊 Erstelle {len(DATABASES)} Datenbanken in:")
    print(f"   {DB_BASE.absolute()}\n")
    
    for db_name in DATABASES:
        db_path = DB_BASE / db_name
        
        # DB erstellen
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        print(f"  ✅ {db_name}")
    
    print(f"\n🎉 Fertig! Alle {len(DATABASES)} DBs erstellt!")
    print(f"\nGröße prüfen:")
    total_size = sum((DB_BASE / db).stat().st_size for db in DATABASES)
    print(f"  Total: {total_size / 1024:.1f} KB (~{total_size / len(DATABASES) / 1024:.1f} KB pro DB)")
    
    print(f"\n📁 Speicherort:")
    print(f"  {DB_BASE.absolute()}")


if __name__ == "__main__":
    create_databases()
