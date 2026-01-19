---
description: Projekt Workflow Neue Spezifikation zu docs/specifications/v3.0/ hinzufügen
---

# Neue Spezifikation erstellen

1. Erstelle Dokument in `docs/specifications/v3.0/SPEC_NAME.md`
2. Füge Quellenverzeichnis am Ende hinzu mit Tabelle:
   ```markdown
   ## QUELLENVERZEICHNIS
   | Quelle | Lokale Kopie | Beschreibung |
   ```
3. Aktualisiere `docs/specifications/v3.0/INDEX.md`
4. Falls neue V2.0 Quellen: kopiere nach `docs/specifications/v3.0/sources/v2_*.ext`
5. Aktualisiere `docs/specifications/v3.0/SOURCES_MASTER_INDEX.md`

---
description: Frontend-Komponente hinzufügen
---

# Frontend-Komponente hinzufügen

1. Erstelle Komponente in `app/interface/src/components/CATEGORY/ComponentName.tsx`
2. Nutze relative Imports `import X from './core/X'`
3. Stelle sicher VITE_API_URL für Backend-Calls verwendet wird
4. Teste in Browser (localhost:5173)
5. Aktualisiere `app/interface/src/components/README.md` falls neue Kategorie

---
description: Backend-Endpoint hinzufügen
---

# Backend-Endpoint hinzufügen

1. Erstelle Router in `backend/api/endpoint_name.py`
2. Registriere in `backend/main.py`: `app.include_router(router, prefix="/api/name")`
3. Teste mit curl oder Postman
4. Dokumentiere in TODO/PHASE_3_TEMPLE_ENDPOINT.md falls relevant

---
description: Neue Datenbank hinzufügen
---

# Neue Datenbank hinzufügen

1. Aktualisiere Schema in `backend/utils/db_schema.sql`
2. Füge DB-Name zu DATABASES-Liste in `backend/utils/create_21_databases.py`
3. Führe aus: `python backend/utils/create_21_databases.py`
4. Teste mit `python backend/utils/test_dbs.py`
5. Dokumentiere in `TODO/PHASE_2_21DB_SETUP.md`

---
description: V2.0 Datei archivieren
---

# V2.0 Datei archivieren

1. Kopiere Original nach `docs/specifications/v3.0/sources/v2_FILENAME.ext`
2. Original in `C:\Evoki V2.0\` bleibt unangetastet
3. Aktualisiere `docs/specifications/v3.0/sources/README.md`
4. Referenziere in relevantem Spec-Dokument via Quellenverzeichnis
5. Aktualisiere `SOURCES_MASTER_INDEX.md`

---
description: Struktur validieren vor Commit
---

# Struktur validieren

1. Führe aus: `python tooling/scripts/cli/enforce_structure.py check`
2. Prüfe Output auf MIXED_DIRECTORY Violations
3. Falls akzeptabel (README.md, Docs, etc.): ignorieren
4. Falls kritisch: beheben via enforce_structure.py fix
5. Regeneriere ARCHITECTURE.txt: `python tooling/scripts/helpers/generate_architecture_map.py`

---
description: TODO Phase abschließen
---

# TODO Phase abschließen

1. Arbeite alle Schritte in `TODO/PHASE_N.md` ab
2. Setze beide Checkboxen [ ] → [x] für jeden Schritt
3. Führe Abschluss-Check aus (am Ende der Phase dokumentiert)
4. Markiere Phase als komplett in `TODO/README.md`
5. Weiter zu nächster Phase

---
description: Multi-Agent Daten speichern
---

# Multi-Agent Daten speichern

1. Agent-spezifische Daten: `tooling/data/agents/AGENT_NAME/`
2. Geteilte Daten: `tooling/data/agents/shared/`
3. Status Windows: `tooling/data/agents/shared/status_windows/`
4. Niemals in `tooling/data/synapse/` (deprecated)

---
description: Chatlog archivieren
---

# Chatlog archivieren

1. Kopiere nach `tooling/history/Chatlogs/`
2. Benenne sinnvoll (Datum, Quelle, Format)
3. Aktualisiere README in Chatlogs/ falls nötig
4. Original bleibt an Ursprungsort

---
description: Brain-Ordner aufräumen
---

# Brain-Ordner aufräumen

1. Navigiere zu `C:\Users\nicom\.gemini\antigravity\brain\{conversation-id}\`
2. Lösche alle `*.metadata.json` Dateien
3. Lösche alle `*.resolved*` Dateien
4. Behalte nur finale .md Artifacts (falls wichtig)
5. Regel: Brain ist temporärer Workspace, finale Docs leben in Projekt

---
description: ARCHITECTURE.txt regenerieren
---

# ARCHITECTURE.txt regenerieren

// turbo
1. Ausführen: `python tooling/scripts/helpers/generate_architecture_map.py`

---
description: FAISS-Index nutzen
---

# FAISS-Index nutzen

1. Für Semantic Search: Mistral-7B-Instruct-v0.2 Model (4096D, GPU)
2. Index-Pfad: `tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.faiss`
3. Für Metriken-Embeddings: all-MiniLM-L6-v2 (384D, CPU)
4. Niemals beide verwechseln: verschiedene Dimensionen!

---
description: Double Airlock implementieren
---

# Double Airlock implementieren

1. Gate A (Pre-Prompt): vor LLM-Call in enforcement_gate.py::pre_validation()
2. Prüfe: T_panic, F_risk, Krisenprompts (A39)
3. Gate B (Post-Response): nach LLM-Call in enforcement_gate.py::post_validation()
4. Prüfe: Halluzination (A0), B_align (A46)
5. Bei Veto: KEINE Antwort an User, nur Veto-Gründe

---
description: APK-Deployment vorbereiten
---

# APK-Deployment vorbereiten

1. Stelle sicher alle Backend-Calls nutzen `import.meta.env.VITE_API_URL`
2. Erstelle .env.production mit `VITE_API_URL=https://api.evoki.app`
3. Keine localhost-Hardcodes im Code
4. Components-Struktur muss sauber sein (nur Unterordner in components/)
5. Build testen: `npm run build` im Frontend

---
description: README.md aktualisieren
---

# README.md aktualisieren

1. Bei neuen Features: Features-Sektion aktualisieren
2. Bei Struktur-Änderungen: PROJECT STRUCTURE aktualisieren
3. Bei neuen Dokumenten: KEY DOCUMENTS Tabelle aktualisieren
4. Halte Quick Start aktuell
5. Version und Last Updated Datum aktualisieren

---
description: TODO-Liste für neues Feature erstellen
---

# TODO-Liste für neues Feature erstellen

1. Erstelle neues Dokument in `TODO/FEATURE_NAME.md`
2. Struktur wie PHASE_*.md: Ziel, Checkliste mit doppelten Boxen [ ] [ ]
3. Einfache Sprache ("auch Kevin versteht es")
4. Jeden Schritt mit "Was du sehen solltest" ergänzen
5. Troubleshooting-Sektion am Ende
6. Aktualisiere `TODO/README.md` Master-Checkliste

---
description: Neue Spezifikations-Dokument-Kategorie erstellen
---

# Neue Spezifikations-Dokument-Kategorie

1. Erstelle Unterordner in `docs/specifications/v3.0/CATEGORY/`
2. Erstelle `docs/specifications/v3.0/CATEGORY/README.md` mit Übersicht
3. Dokumente in Kategorie mit Quellenverzeichnis
4. Aktualisiere `docs/specifications/v3.0/INDEX.md`
5. Aktualisiere Root `README.md` KEY DOCUMENTS Tabelle

---
description: Ordner-README generieren
---

# Ordner-README generieren

1. Nutze `python tooling/scripts/cli/enforce_structure.py readme`
2. Generiert automatisch README.md in Ordnern ohne
3. Prüfe generierte READMEs auf Sinnhaftigkeit
4. Passe Template in enforce_structure.py an falls nötig
5. Commit generierte READMEs

---
description: Änderungen dokumentieren nach Feature-Implementation
---

# Änderungen dokumentieren nach Feature

1. Aktualisiere relevante TODO/PHASE_*.md: Checkboxen setzen
2. Aktualisiere HOW_TO_EVOKI_V3.md falls Architektur betroffen
3. Aktualisiere docs/specifications/v3.0/ falls neue Konzepte
4. Regeneriere ARCHITECTURE.txt
5. Aktualisiere Root README.md (Features, Status)
6. Commit mit aussagekräftiger Message

---
description: Wöchentliche Dokumentations-Pflege
---

# Wöchentliche Dokumentations-Pflege

1. Prüfe TODO/README.md: Sind alle Phasen-Status aktuell?
2. Prüfe Root README.md: Ist Implementation Status aktuell?
3. Regeneriere ARCHITECTURE.txt: `python tooling/scripts/helpers/generate_architecture_map.py`
4. Prüfe docs/specifications/v3.0/INDEX.md: Alle Docs gelistet?
5. Brain-Ordner aufräumen: Lösche .resolved und .metadata.json
6. Checke .agent/rules/project_rules.md: Neue Regeln nötig?

---
description: Migration von V2.0 Features dokumentieren
---

# Migration von V2.0 Features dokumentieren

1. Erstelle `docs/specifications/v3.0/MIGRATION_FEATURE_NAME.md`
2. Dokumentiere: Was war in V2.0, Was ist in V3.0, Änderungen
3. Kopiere relevante V2.0 Source-Dateien nach sources/
4. Füge Quellenverzeichnis hinzu
5. Aktualisiere SOURCES_MASTER_INDEX.md
6. Aktualisiere INDEX.md

---
description: Code-Kommentare für komplexe Logik hinzufügen
---

# Code-Kommentare hinzufügen

1. Komplexe Algorithmen: Docstring mit Erklärung, Input, Output
2. Metriken-Berechnungen: Formel als Kommentar, Quelle referenzieren
3. Double Airlock Gates: Regelwerk-Nummer (z.B. A7.5) als Kommentar
4. FAISS-Queries: Dimensionen und Model als Kommentar
5. Magic Numbers: Erklärung warum dieser Wert (z.B. threshold 0.8)

---
description: Inline-Dokumentation für APIs
---

# Inline-Dokumentation für APIs

1. FastAPI Endpoints: Pydantic Models mit field descriptions
2. Router-Docstrings mit Beschreibung, Parameters, Returns, Raises
3. Beispiel-Request/Response in Docstring
4. Status-Codes dokumentieren (200, 400, 500)
5. Veto-Fälle explizit dokumentieren

---
description: Visualisierung für komplexe Flows erstellen
---

# Visualisierung erstellen

1. Nutze Mermaid für Flow-Diagramme in Markdown
2. ASCII-Art für Terminal-Output (wie PROZESS_DIAGRAMM_ASCII.md)
3. Screenshots/Recordings für UI-Flows
4. Speichere in docs/specifications/v3.0/ oder relevanter TODO/
5. Embed in Dokumentation via ![caption](path)

---
description: Changelog pflegen
---

# Changelog pflegen

1. Erstelle CHANGELOG.md im Root (falls nicht vorhanden)
2. Format: ## [Version] - YYYY-MM-DD, dann Added/Changed/Fixed/Removed
3. Bei jedem Feature-Merge: CHANGELOG aktualisieren
4. Semantic Versioning: MAJOR.MINOR.PATCH
5. Unreleased-Sektion für laufende Entwicklung

---
description: Git-Commit-Messages strukturieren
---

# Git-Commit-Messages

1. Format: `type(scope): subject` z.B. `feat(temple): Add Double Airlock validation`
2. Types: feat, fix, docs, style, refactor, test, chore
3. Subject: Max 50 chars, imperative mood (Add, Fix, Update)
4. Body: Warum die Änderung, nicht was (das sieht man im Diff)
5. Footer: Closes #123, Breaking Change: falls relevant