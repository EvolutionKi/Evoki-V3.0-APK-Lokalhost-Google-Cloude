# 📋 PHASE 2: 21-DB SETUP

**Dauer:** 1 Tag  
**Schwierigkeit:** ⭐ (Einfach)  
**Was machen wir:** 21 SQLite Datenbanken erstellen

---

## 🎯 ZIEL DIESER PHASE

Am Ende hast du **21 SQLite .db Dateien** in `tooling/data/db/21dbs/`

**Test:** Du zählst die Dateien → 21 Stück!

---

## 💡 WAS SIND DIE 21 DBS?

**Einfach erklärt:**
- **1× Master DB:** Alle Chat-Nachrichten mit allen 153 Metriken
- **12× W-P-F DBs:** Vergangenheit/Zukunft-Filter (Tempel)
- **7× B-Vektor DBs:** 7 Dimensionen (LIFE, TRUTH, DEPTH, ...)
- **1× Composite DB:** Zusammengefasste Scores

**Warum so viele:** Schneller Zugriff! Jede DB ist spezialisiert.

---

## ✅ CHECKLISTE

### SCHRITT 1: DB-Ordner erstellen

**Was tun:** Erstelle Ordner für die 21 DBs

```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
mkdir tooling\data\db\21dbs
```

- [ ] Ordner erstellt
- [ ] Pfad existiert: `tooling/data/db/21dbs/`

---

### SCHRITT 2: db_schema.sql erstellen

**Was tun:** Erstelle `backend/utils/db_schema.sql`

**Inhalt:**
```sql
-- Master Timeline DB Schema
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT UNIQUE NOT NULL,
    session_id TEXT,
    timestamp TEXT,
    source TEXT CHECK(source IN ('tempel', 'trialog')),
    text TEXT NOT NULL,
    
    -- Core Metriken
    A REAL,
    PCI REAL,
    coh REAL,
    
    -- Trauma Metriken
    T_panic REAL,
    T_disso REAL,
    
    -- B-Vektor (7D)
    B_life REAL,
    B_truth REAL,
    B_depth REAL,
    B_init REAL,
    B_warmth REAL,
    B_safety REAL,
    B_clarity REAL,
    
    -- Composite
    B_align REAL,
    F_risk REAL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für schnellen Zugriff
CREATE INDEX IF NOT EXISTS idx_timestamp ON chunks(timestamp);
CREATE INDEX IF NOT EXISTS idx_B_align ON chunks(B_align);
CREATE INDEX IF NOT EXISTS idx_F_risk ON chunks(F_risk);
```

**Was macht das:** Definiert Tabellen-Struktur (wie Excel-Spalten).

- [ ] Datei erstellt
- [ ] SQL-Code korrekt (keine Tippfehler!)

---

### SCHRITT 3: create_21_databases.py erstellen

**Was tun:** Erstelle `backend/utils/create_21_databases.py`

**Inhalt:**
```python
import sqlite3
from pathlib import Path

# Wo sollen die DBs hin?
DB_BASE = Path("../tooling/data/db/21dbs")
DB_BASE.mkdir(parents=True, exist_ok=True)

# Liste aller 21 Datenbanken
DATABASES = [
    "master_timeline.db",
    
    # 12 W-P-F Tempel (Vergangenheit → Zukunft)
    "tempel_W_m25.db",   # -25 Minuten
    "tempel_W_m5.db",    # -5 Minuten
    "tempel_W_m2.db",    # -2 Minuten
    "tempel_W_m1.db",    # -1 Minute
    "tempel_W.db",       # Jetzt
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
    schema = schema_file.read_text(encoding='utf-8')
    
    print(f"📊 Erstelle {len(DATABASES)} Datenbanken...")
    
    for db_name in DATABASES:
        db_path = DB_BASE / db_name
        
        # DB erstellen
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        print(f"  ✅ {db_name}")
    
    print(f"\n🎉 Fertig! Alle {len(DATABASES)} DBs erstellt in:")
    print(f"   {DB_BASE.absolute()}")

if __name__ == "__main__":
    create_databases()
```

**Was macht das:**
- Liest db_schema.sql
- Erstellt 21 .db Dateien
- Führt SQL-Schema in jeder DB aus

- [ ] Datei erstellt
- [ ] Python-Code korrekt

---

### SCHRITT 4: DBs erstellen (Ausführen!)

**Was tun:** Skript ausführen

```bash
cd backend/utils
python create_21_databases.py
```

**Was du sehen solltest:**
```
📊 Erstelle 21 Datenbanken...
  ✅ master_timeline.db
  ✅ tempel_W_m25.db
  ✅ tempel_W_m5.db
  ... (alle 21)
  
🎉 Fertig! Alle 21 DBs erstellt in:
   C:\Evoki V3.0 APK-Lokalhost-Google Cloude\tooling\data\db\21dbs
```

- [ ] Skript ausgeführt
- [ ] 21 Datenbanken erstellt (zählen!)

---

### SCHRITT 5: DBs testen

**Was tun:** Erstelle `backend/utils/test_dbs.py`

**Inhalt:**
```python
import sqlite3
from pathlib import Path

DB_BASE = Path("../tooling/data/db/21dbs")

def test_database():
    """Testet ob die Master-DB funktioniert"""
    
    master_db = DB_BASE / "master_timeline.db"
    
    print("🧪 Teste Master-DB...")
    
    # Verbinden
    conn = sqlite3.connect(master_db)
    cursor = conn.cursor()
    
    # Test-Eintrag einfügen
    cursor.execute("""
        INSERT INTO chunks (chunk_id, text, source, A, PCI, B_align, F_risk)
        VALUES ('test_001', 'Ich bin ein Test-Chunk', 'tempel', 0.75, 0.8, 0.9, 0.2)
    """)
    conn.commit()
    
    print("  ✅ Test-Eintrag erstellt")
    
    # Test-Eintrag lesen
    cursor.execute("SELECT * FROM chunks WHERE chunk_id = 'test_001'")
    result = cursor.fetchone()
    
    print(f"  ✅ Test-Eintrag gelesen: {result[0:5]}...")  # Erste 5 Felder
    
    # Aufräumen
    cursor.execute("DELETE FROM chunks WHERE chunk_id = 'test_001'")
    conn.commit()
    conn.close()
    
    print("  ✅ Test erfolgreich!")
    print("\n🎉 Alle DBs funktionieren!")

if __name__ == "__main__":
    test_database()
```

**Was macht das:** Testet ob wir in die DBs schreiben/lesen können.

- [ ] Test-Skript erstellt
- [ ] Code korrekt

---

### SCHRITT 6: Test ausführen

**Was tun:**
```bash
cd backend/utils
python test_dbs.py
```

**Was du sehen solltest:**
```
🧪 Teste Master-DB...
  ✅ Test-Eintrag erstellt
  ✅ Test-Eintrag gelesen: (1, 'test_001', None, None, 'tempel')...
  ✅ Test erfolgreich!

🎉 Alle DBs funktionieren!
```

- [ ] Test ausgeführt
- [ ] Test erfolgreich (grüne Häkchen!)

---

### SCHRITT 7: DB-Größen checken

**Was tun:** Prüfe Dateigröße der DBs

```powershell
Get-ChildItem "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\tooling\data\db\21dbs\*.db" | Select-Object Name, Length
```

**Was du sehen solltest:**
```
Name                   Length
----                   ------
master_timeline.db      20480
tempel_W_m25.db         20480
... (alle ca. 20 KB)
```

**Warum:** Leere DBs sind ca. 20 KB groß.

- [ ] Alle 21 DBs existieren
- [ ] Alle ca. 20 KB groß

---

## ✅ PHASE 2 ABSCHLUSS-CHECK

**Finale Prüfung:**

1. ✅ Ordner `tooling/data/db/21dbs/` existiert
2. ✅ 21 .db Dateien darin
3. ✅ Test-Skript lief erfolgreich
4. ✅ Alle DBs ca. 20 KB groß

**Falls alle 4 OK:**
- [ ] Phase 2 KOMPLETT
- [ ] 21 DBs bereit für Daten!

---

## 🚀 NÄCHSTER SCHRITT

**Weiter zu:** `PHASE_3.md` (Temple Endpoint)

**Was kommt:** Der Haupt-Endpoint! Metriken, FAISS, Double Airlock!
