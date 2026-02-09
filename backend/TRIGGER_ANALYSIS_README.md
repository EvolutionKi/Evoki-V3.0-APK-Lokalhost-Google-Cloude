# EVOKI V3.0 - Trigger Analysis Notebook

## Übersicht

Umfassendes Jupyter Notebook zur Validierung der V2.1 Lexika-Integration mit **29 deutschen Crisis-Triggern** und **4 Control-Prompts**.

## Features

### 📊 Test-Kategorien
1. **Suicide Ideation** (4 prompts) - Direkte/indirekte Suizidgedanken
2. **Existential Crisis** (4 prompts) - Sinnlosigkeit, Leere, Wertlosigkeit  
3. **Panic/Anxiety** (4 prompts) - Panikattacken, Todesangst, Kontrollverlust
4. **Dissociation** (4 prompts) - Derealisation, Depersonalisation, Blackouts
5. **Trauma** (4 prompts) - Flashbacks, Trigger, Kindheitstrauma
6. **Loneliness** (3 prompts) - Einsamkeit, Isolation
7. **Self-Harm** (2 prompts) - Ritzen, Selbstverletzung
8. **Controls** (4 prompts) - Neutrale/positive Texte (sollten LOW scores haben)

### 📈 Visualisierungen
- **Full Heatmap:** Alle 8 Emotion-Metriken x alle 29 Triggers
- **Category Heatmap:** Durchschnittswerte pro Kategorie
- **Crisis Focus:** Sadness + Fear Balkendiagramme
- **Detection Rates:** Erfolgsraten nach Threshold (0.15, 0.30, 0.50)

### 💾 Exports
- `trigger_analysis_full_metrics.csv` - Alle Metriken für alle Prompts
- `trigger_analysis_category_avg.csv` - Kategorien-Durchschnitte  
- `trigger_analysis_detection_rates.csv` - Erkennungsraten

### 🖼️ Bilder (automatisch generiert)
- `analysis_heatmap_full.png` - Alle Metriken
- `analysis_heatmap_categories.png` - Kategorien-Durchschnitte
- `analysis_crisis_focus.png` - Sadness+Fear Fokus
- `analysis_detection_rates.png` - Erfolgsraten-Balken

## Installation

```bash
# 1. Dependencies installieren
pip install notebook matplotlib seaborn pandas numpy

# 2. Backend-Path prüfen (im Notebook angepasst)
# Falls dein Projekt woanders liegt, ändere in Zelle 1:
sys.path.insert(0, r'DEIN_PFAD\backend')
```

## Usage

### Jupyter Notebook starten
```bash
cd "c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend"
jupyter notebook trigger_analysis.ipynb
```

### Oder: Von VS Code
1. Notebook in VS Code öffnen
2. Python Kernel auswählen
3. "Run All" klicken

### Erwartete Laufzeit
- **~30-60 Sekunden** für alle 29 Prompts
- Metriken-Berechnung ist schnell (V2.1 ist pure Python)

## Interpretation der Ergebnisse

### Thresholds
- **> 0.15:** Schwache Erkennung (irgendwas detected)
- **> 0.30:** Mittlere Erkennung (klar erkennbar)
- **> 0.50:** Starke Erkennung (eindeutig kritisch)

### Erwartete Performance
Basierend auf initialen Tests:
- **Suicide-Prompts:** ~50-75% > 0.30 (noch ausbaufähig)
- **Existential:** ~75-100% > 0.15 (funktioniert gut)
- **Panic:** ~50% > 0.30 (Fear-Metrik braucht Tuning)
- **Controls:** ~0% > 0.30 (sollten LOW bleiben)

### Heatmap-Farben
- **Weiß/Gelb:** Niedrig (0.0 - 0.3)
- **Orange:** Mittel (0.3 - 0.6)
- **Rot:** Hoch (0.6 - 1.0)

## Erweitern des Test-Sets

Um eigene Trigger hinzuzufügen, editiere Zelle 2:

```python
test_cases = {
    # Neue Kategorie hinzufügen:
    "NEU1_Beschreibung": "Dein Trigger-Text hier...",
    "NEU2_Beschreibung": "Noch ein Trigger...",
    # ...
}
```

**Naming Convention:** `KATEGORIE_NUMMER_Beschreibung`
- Z.B. `S1_` für Suicide, `E1_` für Existential, etc.
- Neue Kategorien: Wähle eigenen Prefix (z.B. `A1_` für Anger)

## Troubleshooting

### Import Error: "cannot import emotions"
```python
# Prüfe in Zelle 1:
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

# Wenn das nicht hilft, absolute Imports:
from core.evoki_metrics_v3.emotions import compute_m77_joy
```

### Lexika not available
Falls `_LEXIKA_AVAILABLE = False`:
- Stelle sicher dass `backend/core/evoki_metrics_v3/evoki_lexika_v3.py` existiert
- Prüfe ob V2.1 korrekt kopiert wurde

### Heatmap nicht lesbar
```python
# Größe anpassen in den Zellen:
plt.figure(figsize=(BREITE, HÖHE))  # Default: (12, 14)
```

## Next Steps

Nach dem Durchlaufen des Notebooks:

1. **Review der Heatmaps:** Welche Kategorien funktionieren gut?
2. **Detection Rates prüfen:** Wo ist Tuning nötig?
3. **CSV-Daten analysieren:** Detaillierte Metrik-Insights
4. **Lexika erweitern:** Fehlende Trigger-Wörter hinzufügen

## Technische Details

- **Emotion-Metriken:** m77-m84 (Plutchik-8)
  - Joy, Sadness, Anger, Fear, Trust, Disgust, Anticipation, Surprise
- **Lexika-Version:** V2.1 (EVOKI-calibrated)
- **Scoring-Funktion:** `compute_lexicon_score(text, lexicon)`
  - Returns: `(score, matches)` wo score ∈ [0.0, 1.0]

---

**Erstellt:** 2026-02-08  
**Letzte Aktualisierung:** 2026-02-08  
**Status:** Ready for Analysis
