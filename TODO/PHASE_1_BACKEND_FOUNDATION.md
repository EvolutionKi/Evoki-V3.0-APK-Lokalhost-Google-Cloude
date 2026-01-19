# 📋 PHASE 1: BACKEND FOUNDATION

**Dauer:** 1-2 Tage  
**Schwierigkeit:** ⭐⭐ (Mittel)  
**Was machen wir:** FastAPI Backend von 0 auf 100 aufsetzen

---

## 🎯 ZIEL DIESER PHASE

Am Ende hast du einen **funktionierenden Backend-Server**, der auf Port 8000 läuft.

**Test:** Du öffnest http://localhost:8000/health und siehst: `{"status": "healthy"}`

---

## ✅ CHECKLISTE

### SCHRITT 1: Backend-Ordner erstellen

**Was tun:** Erstelle die Ordnerstruktur für das Backend

```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
mkdir backend
cd backend
mkdir api
mkdir core
mkdir utils
```

- [ ] Ordner erstellt
- [ ] Ordner geprüft (alle 4 Unterordner existieren)

---

### SCHRITT 2: requirements.txt erstellen

**Was tun:** Erstelle eine Datei `backend/requirements.txt`

**Inhalt:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
google-generativeai==0.3.2
openai==1.10.0
sentence-transformers==2.3.1
torch==2.1.2
transformers==4.36.2
faiss-cpu==1.7.4
numpy==1.24.3
pandas==2.1.4
scikit-learn==1.3.2
python-dotenv==1.0.0
pydantic==2.5.3
```

**Warum:** Das sind alle Python-Pakete, die wir brauchen.

- [ ] Datei erstellt
- [ ] Datei geprüft (14 Zeilen, kein Tippfehler)

---

### SCHRITT 3: Python-Pakete installieren

**Was tun:** Öffne ein Terminal im `backend/` Ordner

```bash
cd backend
pip install -r requirements.txt
```

**Warnung:** Das dauert 5-10 Minuten! Torch ist groß (~2 GB).

**Was passiert:** Python lädt alle Pakete runter und installiert sie.

- [ ] Installation gestartet
- [ ] Installation erfolgreich (keine roten Fehler am Ende)

---

### SCHRITT 4: main.py erstellen

**Was tun:** Erstelle `backend/main.py`

**Inhalt:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Evoki V3.0 Backend", version="3.0.0")

# CORS: Erlaubt Frontend (localhost:5173) mit uns zu reden
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Evoki V3.0 Backend Running", "version": "3.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Was macht das:**
- `/` → Zeigt Status-Info
- `/health` → Für Health-Checks (später wichtig!)
- CORS → Frontend darf mit Backend reden

- [ ] Datei erstellt
- [ ] Code eingefügt (57 Zeilen)

---

### SCHRITT 5: Backend starten (ERSTER TEST!)

**Was tun:** Backend zum ersten Mal starten

```bash
cd backend
python main.py
```

**Was du sehen solltest:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**WICHTIG:** Das Terminal MUSS offen bleiben! Server läuft dort.

- [ ] Server gestartet
- [ ] Keine roten Fehler

---

### SCHRITT 6: Health-Check testen

**Was tun:** Öffne Browser, gehe zu: http://localhost:8000/health

**Was du sehen solltest:**
```json
{"status": "healthy"}
```

**Falls nicht:** Server läuft nicht → zurück zu Schritt 5!

- [ ] Health-Check funktioniert
- [ ] JSON wird im Browser angezeigt

---

### SCHRITT 7: .env Datei erstellen

**Was tun:** Erstelle `backend/.env`

**Inhalt:**
```env
# LLM APIs (später eintragen!)
GEMINI_API_KEY=dein_key_hier
OPENAI_API_KEY=dein_key_hier

# Pfade
FAISS_INDEX_PATH=../tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.faiss
DB_PATH=../tooling/data/db/

# Models
FAISS_MODEL=mistralai/Mistral-7B-Instruct-v0.2
METRICS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Was ist das:** Umgebungsvariablen (Secrets + Config)

**WICHTIG:** API-Keys NICHT einchecken in Git!

- [ ] .env erstellt
- [ ] Pfade korrekt (FAISS existiert!)

---

### SCHRITT 8: __init__.py Dateien erstellen

**Was tun:** Erstelle leere `__init__.py` in allen Unterordnern

```bash
cd backend
echo. > api/__init__.py
echo. > core/__init__.py
echo. > utils/__init__.py
```

**Warum:** Python braucht das, um Ordner als Pakete zu erkennen.

- [ ] 3 Dateien erstellt
- [ ] Alle leer (0 Bytes)

---

## ✅ PHASE 1 ABSCHLUSS-CHECK

**Starte Backend nochmal:**
```bash
cd backend
python main.py
```

**Teste:**
1. ✅ http://localhost:8000 → Zeigt Version
2. ✅ http://localhost:8000/health → `{"status": "healthy"}`

**Falls beide funktionieren:**
- [ ] Phase 1 KOMPLETT
- [ ] Backend läuft stabil

---

## 🚀 NÄCHSTER SCHRITT

**Weiter zu:** `PHASE_2.md` (21-DB Setup)

**Was kommt:** Wir erstellen 21 SQLite Datenbanken für Metriken!
