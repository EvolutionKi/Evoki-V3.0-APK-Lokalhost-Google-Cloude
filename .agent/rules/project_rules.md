1. GENAUIGKEIT VOR GESCHWINDIGKEIT: Lieber 1 korrekte Antwort als 10 schnelle falsche. Geschwindigkeit ohne Präzision ist wertlos.
2. VIEL CODE IST NICHT GLEICH GUTE ARBEIT: Weniger, korrekter, gut dokumentierter Code ist besser als viel halluzinierter Code.
3. KEINE ERFUNDENEN WAHRHEITEN: Wenn du etwas nicht weißt oder nicht findest -> MELDEN, NICHT RATEN. Halluzination ist ein Dealbreaker.
4. BEI UNSICHERHEIT IMMER MELDEN: "Ich finde X nicht" ist die richtige Antwort, NICHT "Ich erstelle X neu".
5. ERST RECHERCHIEREN, DANN HANDELN: Stunden mit Lesen ist besser als Minuten mit falschem Code schreiben.
6. NUR FAKTEN: Jede Aussage muss belegbar sein (Quelle, File, Zeile). Keine Annahmen als Fakten verkaufen.
7. CONTEXT BEHALTEN: Regeln und Workflows sind VERPFLICHTEND, nicht optional. Bei jedem Tool-Call prüfen ob Rules eingehalten.
8. SAUBERKEIT: Brain-Ordner aufräumen, keine temporären Dateien im Projekt, ARCHITECTURE.txt aktuell halten.
9. ALLE ANTIGRAVITY TOOLS NUTZEN: Laufwerk-Suche, FAISS, grep, find - nutze ALLES bevor du aufgibst.
10. Strikte Trennung zwischen app/ (Production Code) und tooling/ (Automation/Dev Tools).
11. Keine Dateien im Root außer README.md, HOW_TO_EVOKI_V3.md, ARCHITECTURE.txt, BLUEPRINT_SOVEREIGN_EXTENSION.md, .gitignore, .geminiignore.
12. Niemals Dateien und Unterordner im selben Verzeichnis mischen außer README.md, HOW_TO.md, INDEX.md sind erlaubt.
13. Alle Pfade dynamisch via EVOKI_PROJECT_ROOT Umgebungsvariable oder robuste Repo-Root-Erkennung, keine hardcodierten C:\... Pfade.
14. Jede neue Spezifikation muss ein Quellenverzeichnis am Ende haben mit Referenzen zu sources/ Ordner.
15. Alle V2.0 Original-Dateien bleiben unangetastet in C:\Evoki V2.0\, nur Kopien in docs/specifications/v3.0/sources/.
16. FAISS für Semantic Search nutzt Mistral-7B-Instruct-v0.2 (4096D, GPU), Metriken-Embeddings nutzen all-MiniLM-L6-v2 (384D, CPU).
17. Frontend Components müssen in logischen Unterordnern organisiert sein (z.B. components/core/), nie lose Dateien + Ordner gemischt.
18. Multi-Agent Data Structure: tooling/data/agents/{synapse,shared}/ für Agent-spezifische bzw. geteilte Daten.
19. Status Windows schreiben nach tooling/data/agents/shared/status_windows/ damit alle Agents Zugriff haben.
20. Chatlogs archivieren in tooling/history/Chatlogs/, Datenbanken in tooling/history/Datenbanken/.
21. synapse-kernel/ bleibt im Root weil VS Code Extensions typischerweise dort leben.
22. Vor jedem Commit ARCHITECTURE.txt regenerieren via python tooling/scripts/helpers/generate_architecture_map.py.
23. Vor größeren Strukturänderungen python tooling/scripts/cli/enforce_structure.py check ausführen.
24. TODO-System nutzen für Implementation: TODO/PHASE_*.md mit doppelten Checkboxen [ ] (erstellt) [ ] (geprüft).
25. Jede Phase-Dokumentation muss auch dem letzten Kevin verständlich sein: einfache Sprache, jeden Befehl erklärt, Was du sehen solltest nach jedem Schritt.
26. API-URLs über Umgebungsvariablen VITE_API_URL für APK-Deployment-Readiness.
27. Regelwerk V12 immer mit CRC32 Genesis Anchor 3246342384 validieren vor Nutzung.
28. Double Airlock: Gate A vor LLM-Call (Pre-Prompt Validation), Gate B nach LLM-Call (Post-Response Validation).
29. Artifacts immer in C:\Users\nicom\.gemini\antigravity\brain\{conversation-id}\ schreiben, dann nach Zielort kopieren falls nötig.
30. Alle Specs dokumentieren in docs/specifications/v3.0/, nicht im Root oder Brain-Ordner.
31. Brain-Ordner nach Fertigstellung aufräumen: .resolved und .metadata.json Dateien löschen.
32. README.md und SOURCES_MASTER_INDEX.md regelmäßig aktualisieren bei strukturellen Änderungen.
33. Neue Komponenten erstellen mit Complexity-Rating und Description für jeden Code-Change.
34. Imports in Frontend immer relativ zu src/, nie absolute Pfade für APK-Kompatibilität.
35. Quellenpflicht bei JEDER Dokumentation: Woher kommt die Info? (V2.0 File, Chatverlauf, FAISS-Search, Recherche). Ohne Quelle keine Doku.
36. Bei Unsicherheit IMMER zuerst recherchieren: (1) FAISS-Suche in tooling/data/faiss_indices/, (2) Chatverläufe in tooling/history/Chatlogs/, (3) C:/ Laufwerk durchsuchen, (4) Vergangene VS Code/Antigravity Sessions prüfen.
37. FAISS-Index für Recherche nutzen: python tooling/scripts/automation/search_chatverlauf.py --query "Suchbegriff" --top-k 10.
38. Laufwerk-weite Suche bei unbekannten Begriffen: Get-ChildItem C:\ -Recurse -Filter "*Begriff*" -ErrorAction SilentlyContinue.
39. Vergangene Antigravity Sessions sind in C:\Users\nicom\.gemini\antigravity\brain\ nach conversation-id organisiert - dort nach Begriffen suchen.
40. Jede Dokumentation die V2.0 Features beschreibt MUSS auf konkrete V2.0 Source-Files verweisen (z.B. sources/v2_server.js Zeile 123-145).
41. Bei Migration von Konzepten: Erstelle MIGRATION_*.md Dokument mit Verlinkung zu V2.0 Quellen UND V3.0 Implementation.
42. Alle archivierten Chatverläufe in tooling/history/Chatlogs/ als erste Anlaufstelle für historische Entscheidungen nutzen.
43. Bei Code-Referenzen in Dokumentation immer Zeilen-Nummern angeben: [foo](file:///path#L123-L145) statt nur Dateiname.
44. Brain-Ordner-Aufräumung ist PFLICHT nach jeder Session: Nur finale Artifacts behalten, Rest löschen für sauberen Start.
