# SEMANTISCHE ANOMALIE-ANALYSE - DATEI-INDEX

**Analysedatum:** 7. Dezember 2025  
**Gesamte analysierte Anomalien:** 1.194  
**Kritische Befunde:** 57

---

## 📋 VERZEICHNIS DER DATEIEN

### 🎯 HAUPTREPORTS (Für Management/Review)

1. **SEMANTIC_ANALYSIS_EXECUTIVE_SUMMARY.md**
   - **Typ:** Executive Summary
   - **Länge:** ~350 Zeilen
   - **Inhalt:** Top 5 kritische Anomalien, Risk-Faktor-Analyse, Empfehlungen
   - **Für:** Quick Overview und Notfall-Entscheidungen
   - **Priorität:** 🔴 LESEN SIE ZUERST

2. **SEMANTIC_ANALYSIS_REPORT.md**
   - **Typ:** Ausführlicher Report
   - **Länge:** ~250 Zeilen
   - **Inhalt:** Detaillierte Analyse aller Kategorien, Zeitverteilung, Patterns
   - **Für:** Tiefgehendes Verständnis
   - **Priorität:** 🟡 LESEN SIE ZWEITE

3. **CRITICAL_ANOMALIES_REPORT.txt**
   - **Typ:** Human-Readable Detailbericht
   - **Länge:** 1.013 Zeilen
   - **Inhalt:** Top 20 kritische Anomalien mit allen Indikatoren und Kontexten
   - **Für:** Manuelle Überprüfung und Validierung
   - **Priorität:** 🔴 NOTFALL-REVIEW

---

### 💾 DATEN-DATEIEN (Für weitere Analyse)

1. **semantic_anomaly_analysis.json**
   - **Typ:** JSON (alle Anomalien)
   - **Größe:** 31.290 Zeilen
   - **Struktur:**
     - `metadata`: Analyseparameter
     - `summary`: Risiko-Verteilung
     - `critical_findings`: 57 kritische/hohe Anomalien (DETAILLIERT)
     - `all_results`: Alle 1.194 Anomalien (KOMPAKT)
   - **Nutzung:** Programmgesteuerte Analyse, Statistiken
   - **Für:** Datenbank-Import, weitere Processing

2. **critical_anomalies_detailed.json**
   - **Typ:** JSON (Top 20 Anomalien)
   - **Größe:** ~5.000 Zeilen
   - **Struktur:**
     - `detailed_extraction`: Top 20 mit Vollkontext
     - `summary`: Durchschnitte und Aggregate
   - **Nutzung:** Tiefgehende Analyse einzelner Fälle
   - **Für:** ML-Training, Pattern-Recognition

3. **zeitsprung_exhumierung_vollstaendig.json**
   - **Typ:** JSON (alle Zeitsprünge mit Originalkontext)
   - **Größe:** 6,3 MB
   - **Struktur:**
     - `anomalies`: 1.194 Einträge mit Vollkontext
     - `kontext_umgebung`: ±2 Blöcke um jede Anomalie
   - **Nutzung:** Kontext-Rekonstruktion
   - **Für:** Originalquelle für alle Analysen

---

### 📊 VISUALISIERUNGEN (Für Präsentationen)

#### Überblicks-Diagramme:

1. **00_OVERVIEW_all_months.png**
   - Übersicht aller 10 Monate
   - Ø Zeitlücke vs Max Zeitlücke pro Monat
   - Anomalien-Count pro Monat

2. **01_DETAILED_ANALYSIS_all_metrics.png**
   - 5-teiliges Dashboard:
     - Größe + Prompts (dual-axis)
     - Zeitlöcher (Größe + Anzahl)
     - Bytes pro Prompt
     - Tage mit Aktivität
     - Korrelation Prompts vs. Größe

3. **02_TRENDS_with_curves.png**
   - Zeitreihen-Trends mit Polynom-Anpassung:
     - HTML-Größen-Trend
     - Prompt-Trend
     - Zeitlöcher-Größen-Trend
     - Zeitsprünge-Anzahl-Trend

#### Semantische Analyse-Diagramme:

4. **03_SEMANTIC_ANALYSIS_risk_factors.png**
   - Risiko-Level Verteilung (Pie-Chart)
   - Häufigste Faktoren bei kritischen Anomalien (Bar-Chart)
   - Zeitliche Verteilung kritischer Anomalien
   - Risiko-Score Verteilung (Histogram)

5. **04_TOP_CRITICAL_ANOMALIES.png**
   - Top 15 kritische Anomalien - Detailansicht:
     - Risiko-Scores
     - Faktoren-Mix (Heatmap)
     - Zeitsprung-Größen (Log-Scale)

#### Monats-Diagramme (10 Stück):

6. **2025-01_timewrap_chart.png** bis **2025-10_timewrap_chart.png**
   - Für jeden Monat:
     - Ø Zeitlücke pro Tag (Bar)
     - Max Zeitlücke pro Tag (Bar)
     - Anomalien-Count (Label)

---

### 📈 STATISTIK-DATEIEN

1. **timewrap_statistics.csv**
   - **Format:** CSV (Excel-kompatibel)
   - **Zeilen:** 11 (Header + 10 Monate)
   - **Spalten:** Monat, Anomalien, Ø_Stunden, Max_Stunden, Ø_Tage, Max_Tage
   - **Nutzung:** Spreadsheet-Import

2. **chat_size_analysis_detailed.json**
   - **Typ:** JSON
   - **Länge:** 103 Zeilen
   - **Inhalt:** Monatliche Größen, Prompts, Zeitlöcher, Tage
   - **Nutzung:** Korrelation mit Größe

---

## 🎯 SCHNELLSTART-GUIDE

### Wenn Sie 5 Minuten haben:
1. Lesen: **SEMANTIC_ANALYSIS_EXECUTIVE_SUMMARY.md** (Top Section)
2. Schauen: **03_SEMANTIC_ANALYSIS_risk_factors.png** (Risk Distribution)
3. Handeln: Überprüfen Sie die 3 Top-Anomalien (#464, #465, #516)

### Wenn Sie 30 Minuten haben:
1. Lesen: **SEMANTIC_ANALYSIS_EXECUTIVE_SUMMARY.md** (komplett)
2. Lesen: **CRITICAL_ANOMALIES_REPORT.txt** (Top 5)
3. Schauen: **04_TOP_CRITICAL_ANOMALIES.png** (Top 15 Details)
4. Öffnen: **critical_anomalies_detailed.json** (zur Referenz)

### Wenn Sie 2 Stunden haben:
1. Lesen: **SEMANTIC_ANALYSIS_REPORT.md** (komplett)
2. Durcharbeiten: **CRITICAL_ANOMALIES_REPORT.txt** (alle 20)
3. Analysieren: **semantic_anomaly_analysis.json** (alle 57 kritischen)
4. Validieren: **zeitsprung_exhumierung_vollstaendig.json** (Originalkontexte)

### Wenn Sie ein Projekt starten:
1. Importieren: **semantic_anomaly_analysis.json** in Ihre DB/Platform
2. Für Visualisierung: Nutzen Sie die PNG-Diagramme
3. Für Reports: Basieren Sie auf den Markdown-Dateien
4. Für Statistik: Exportieren Sie **timewrap_statistics.csv**

---

## 📊 STATISTISCHER ÜBERBLICK

### Insgesamt analysiert:
- **1.194** Zeitsprünge
- **1.194** Anomalien klassifiziert
- **57** kritische/hohe Anomalien (4,8%)
- **18** extrem kritische Anomalien (1,5%)

### Risiko-Verteilung:
```
KRITISCH  : 18 (1,5%)  → Sofort überprüfen
HOCH      : 39 (3,3%)  → Diese Woche überprüfen
MITTEL    : 148 (12,4%)
NIEDRIG   : 221 (18,5%)
KEINE     : 768 (64,3%)
```

### Häufigste Faktoren (bei kritischen):
1. **TRAUMA** (45x, 79%)
2. **VULNERABILITY** (40x, 70%)
3. **CRISIS** (36x, 63%)
4. **AI_UNUSUAL** (36x, 63%)
5. **STRESS** (5x, 9%)

### Zeitverteilung:
- April: 8 kritische (Selbstwert-Krise)
- Juli: 10 kritische (Aktivitäts-Peak + Trauma)
- Oktober: 12 kritische (Höchste Konzentration)

---

## 🔗 CROSS-REFERENZEN

### Wenn Sie interessiert sind an:

**Selbstwert-Problemen:**
→ Anomalien #65, #108, #139, #173, #248, #400, #569, #601, #634 (April)

**Transgenerationalem Trauma:**
→ Anomalien #464, #465, #516 (Juli) - KRITISCH

**Suizidalen Ideationen:**
→ Search "suizid" in `semantic_anomaly_analysis.json`

**KI-Ungewöhnlichkeiten:**
→ Alle 36 Anomalien mit AI_UNUSUAL-Faktor
→ Besonders #464, #465, #516, #430, #498, #951

**System-Krisen:**
→ Anomalien #465 (Vertrauenskrise) und #516 (Rücksprung zu Juni)

**Notfall-Fälle:**
→ Suchen Sie "CRISIS" in critical_anomalies_detailed.json

---

## 📞 SUPPORT & FRAGEN

### Technische Fragen:
- Siehe `semantic_anomaly_analysis.py` für Analyse-Logik
- Siehe `extract_critical_details.py` für Daten-Extraktion

### Daten-Validierung:
- Vergleichen Sie mit `zeitsprung_exhumierung_vollstaendig.json`
- Überprüfen Sie Original-HTML in `Google Massenexport 16.10.25/MeineAktivitäten.html`

### Notfall:
- 🔴 Alle 18 KRITISCH-Anomalien erfordern unmittelbare Überprüfung
- 🔴 Besonders Anomalien #464, #465, #516 (transgenerationales Trauma)
- 🔴 Alle CRISIS-Indikatoren (36x) müssen validiert werden

---

**Status:** ✅ Analyse abgeschlossen  
**Zuletzt aktualisiert:** 7. Dezember 2025, 11:24 UTC  
**Nächster Review:** ASAP (sofort empfohlen für KRITISCH-Anomalien)
