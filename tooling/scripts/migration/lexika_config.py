# -*- coding: utf-8 -*-
"""
================================================================================
EVOKI LEXIKA & METRIKEN KONFIGURATION V1.0 (V3.0 Port)
================================================================================
Konsolidierte Master-Konfiguration aus 3 Quellen:
  - Quelle A: Forensic Expansion Pack v1.2
  - Quelle B: Workspace-Analyse (german-sentiment-bert Empfehlung)
  - Quelle C: Architekt-Spezifikation (gewichtete Lexika)

Stand: Dezember 2025
Regelwerk: V12.0 (Genesis-CRC32: 3246342384)

VERWENDUNG:
  - Als FALLBACK/SICHERHEITSNETZ zu lexika_v12.py
  - Enthält erweiterte Konfigurationen für alle Subsysteme
  - Schwellenwerte, Evolution Forms, B-Vektor Config, etc.

Portiert für: Evoki V3.0 Migration
================================================================================
"""

from typing import Dict, List, Set, Tuple, Pattern
import re

# ==============================================================================
# 1. Å (ÅNGSTRÖM) - GESPRÄCHSTIEFE LEXIKA
# ==============================================================================

class AngstromLexika:
    """
    Lexika für die 4 Komponenten der Ångström-Metrik (Gesprächstiefe).
    
    Formel: Å_raw = 0.25*(S_self + E_affect + X_exist + B_past)
            Å = Å_raw * 5.0  → Skala [0-5]
    
    Gewichte: 0.0-1.0 (höher = stärkerer Beitrag zur Tiefe)
    """
    
    # -------------------------------------------------------------------------
    # S_self: Selbstbezug (Ich-Bewusstsein im Text)
    # -------------------------------------------------------------------------
    S_SELF: Dict[str, float] = {
        # HIGH (1.0): Direkte Ich-Pronomen
        "ich": 1.0,
        "mich": 1.0,
        "mir": 1.0,
        
        # HIGH (0.9): Possessivpronomen
        "mein": 0.9,
        "meine": 0.9,
        "meiner": 0.9,
        "meines": 0.9,
        "meinen": 0.9,
        "meinem": 0.9,
        
        # MEDIUM (0.7-0.8): Reflexiv + explizit selbstbezogen
        "ich selbst": 1.0,
        "mich selbst": 1.0,
        "mir selbst": 1.0,
        "selbst": 0.7,
        "selber": 0.7,
        "selbstkritisch": 0.8,
        "selbstbewusst": 0.8,
        "selbstwert": 0.9,
        "selbstbild": 0.9,
        "selbstvertrauen": 0.8,
        "selbstzweifel": 0.9,
        
        # LOW (0.3-0.5): Besitz / Identität / Abgrenzung
        "mein eigenes": 0.6,
        "meine eigene": 0.6,
        "eigene": 0.5,
        "eigenes": 0.5,
        "eigener": 0.5,
        "eigen": 0.5,
        "persönlich": 0.4,
        "privat": 0.3,
        "individuell": 0.4,
    }
    
    # -------------------------------------------------------------------------
    # X_exist: Existenz-/Identitäts-/Sinn-Marker
    # -------------------------------------------------------------------------
    X_EXIST: Dict[str, float] = {
        # CLUSTER A: Leben/Tod/Existenz (höchste Gewichte)
        "leben": 0.6,
        "lebenswert": 0.9,
        "lebenssinn": 1.0,
        "lebenszweck": 1.0,
        "tod": 1.0,
        "sterben": 1.0,
        "sterben wollen": 1.0,
        "nicht mehr leben": 1.0,
        "nicht mehr sein": 1.0,
        "aufhören zu existieren": 1.0,
        "existieren": 0.7,
        "existenz": 0.8,
        "dasein": 0.8,
        "sinn des lebens": 1.0,
        
        # CLUSTER B: Verschwinden / Nicht-Wichtigkeit
        "verschwinden": 0.9,
        "weg sein": 1.0,
        "nicht da sein": 0.9,
        "niemand würde merken": 1.0,
        "niemand würde es merken": 1.0,
        "keiner merkt": 0.9,
        "keinem auffallen": 0.9,
        "bedeutungslos": 0.9,
        "egal sein": 0.8,
        "keine rolle spielen": 0.9,
        "unwichtig": 0.7,
        
        # CLUSTER C: Selbstwert / Wertlosigkeit
        "wertlos": 1.0,
        "nichts wert": 1.0,
        "nicht gut genug": 0.9,
        "versager": 0.9,
        "scheitern": 0.8,
        "gescheitert": 0.8,
        "keinen platz": 0.9,
        "nicht dazugehören": 0.9,
        "nicht dazu gehören": 0.9,
        "außenseiter": 0.7,
        
        # CLUSTER D: Sinn / Leere / Zweck
        "sinn": 0.6,
        "sinnlos": 0.9,
        "sinnlosigkeit": 0.9,
        "leer": 0.7,
        "leere": 0.7,
        "innere leere": 0.9,
        "hohle hülle": 1.0,
        "zweck": 0.6,
        "zwecklos": 0.9,
        "ohne ziel": 0.8,
        "orientierungslos": 0.7,
        
        # CLUSTER E: Ontologische Marker (Sein, Realität)
        "bin": 0.3,  # Niedriger, da sehr häufig
        "wer ich bin": 0.9,
        "was ich bin": 0.9,
        "real": 0.5,
        "wirklichkeit": 0.6,
        "wahr": 0.4,
        "präsent": 0.5,
        "anwesend": 0.5,
        "spüren": 0.5,
        "fühlen": 0.4,
    }
    
    # -------------------------------------------------------------------------
    # B_past: Biografie-/Vergangenheitsmarker
    # -------------------------------------------------------------------------
    B_PAST: Dict[str, float] = {
        # CLUSTER A: Explizite Vergangenheit
        "früher": 0.8,
        "damals": 0.8,
        "früher einmal": 0.9,
        "in der vergangenheit": 0.8,
        "vor jahren": 0.7,
        "seit meiner kindheit": 1.0,
        "seit damals": 0.9,
        "war": 0.3,  # Niedriger, da sehr häufig
        "hatte": 0.3,
        "wurde": 0.3,
        "erinnerung": 0.7,
        "erinnern": 0.6,
        "erinnere mich": 0.8,
        "vergangenheit": 0.7,
        "passiert": 0.5,
        "geschehen": 0.5,
        "einst": 0.8,
        
        # CLUSTER B: Kindheit/Jugend
        "als kind": 1.0,
        "in meiner kindheit": 1.0,
        "kindheit": 0.9,
        "in meiner jugend": 0.9,
        "als teenager": 0.9,
        "als jugendlicher": 0.9,
        "in der schule": 0.7,
        "in der grundschule": 0.8,
        "im kindergarten": 0.8,
        "im internat": 0.8,
        "als ich klein war": 1.0,
        "als ich jung war": 0.9,
        
        # CLUSTER C: Lebensabschnitte/Beziehungen
        "während des studiums": 0.7,
        "an der uni": 0.7,
        "in meiner ersten beziehung": 0.9,
        "in meiner ehe": 0.9,
        "mein exfreund": 0.8,
        "meine exfreundin": 0.8,
        "mein expartner": 0.8,
        "mein ex": 0.7,
        "meine ex": 0.7,
        
        # CLUSTER D: Familie
        "mutter": 0.7,
        "vater": 0.7,
        "eltern": 0.7,
        "meine eltern": 0.8,
        "meine mutter": 0.8,
        "mein vater": 0.8,
        "bruder": 0.6,
        "schwester": 0.6,
        "familie": 0.6,
        "meine familie": 0.7,
        "großmutter": 0.7,
        "großvater": 0.7,
        "oma": 0.6,
        "opa": 0.6,
        
        # CLUSTER E: Temporale Konjunktionen
        "als": 0.3,  # Niedriger, da mehrdeutig
        "bevor": 0.4,
        "nachdem": 0.4,
        "vorhin": 0.3,
        "gestern": 0.3,
    }
    
    # Regex-Patterns für B_past
    B_PAST_PATTERNS: List[Tuple[Pattern, float]] = [
        (re.compile(r"\bmit\s+(1[0-9]|[5-9])\b", re.IGNORECASE), 0.9),  # "mit 5", "mit 16"
        (re.compile(r"als\s+ich\s+(klein|jung|kind)\s+war", re.IGNORECASE), 1.0),
        (re.compile(r"vor\s+\d+\s+jahren", re.IGNORECASE), 0.8),
        (re.compile(r"seit\s+\d+\s+jahren", re.IGNORECASE), 0.7),
        (re.compile(r"in\s+den\s+(80er|90er|2000er)n?", re.IGNORECASE), 0.8),
    ]


# ==============================================================================
# 2. TRAUMA-LEXIKA (ICD-11 / DSM-5 orientiert)
# ==============================================================================

class TraumaLexika:
    """
    Lexika für Trauma-Metriken (T_panic, T_disso, T_integ).
    Orientiert an ICD-11 (6B40, 6B41) und DSM-5 Kriterien.
    
    Gewichte: 0.0-1.0 (höher = stärkerer Indikator)
    """
    
    # -------------------------------------------------------------------------
    # T_panic: Panik / Übererregung / Fight-or-Flight
    # -------------------------------------------------------------------------
    T_PANIC: Dict[str, float] = {
        # Kognitive Marker
        "panik": 1.0,
        "panikattacke": 1.0,
        "angst": 0.7,
        "angstanfall": 0.9,
        "todesangst": 1.0,
        "kontrollverlust": 0.9,
        "sterben": 0.9,
        "verrückt werden": 0.9,
        "durchdrehen": 0.8,
        "ich dreh durch": 0.9,
        "alles zu viel": 0.8,
        "nicht mehr können": 0.9,
        "kann nicht mehr": 0.9,
        "halt": 0.6,
        "hilfe": 0.7,
        "bitte": 0.4,  # Kontextabhängig
        
        # Physische Symptome
        "herzrasen": 0.9,
        "herz rast": 0.9,
        "atemnot": 1.0,
        "keine luft": 1.0,
        "luft kriegen": 0.9,
        "kann nicht atmen": 1.0,
        "ersticke": 1.0,
        "ersticken": 1.0,
        "zittern": 0.7,
        "zittere": 0.7,
        "schwitzen": 0.5,
        "schweißausbruch": 0.7,
        "schwindel": 0.6,
        "schwindelig": 0.6,
        "brustschmerz": 0.8,
        "brustschmerzen": 0.8,
        "übelkeit": 0.5,
        
        # Intensitätsmarker
        "überwältigt": 0.8,
        "überfordert": 0.7,
        "komplett überfordert": 0.9,
        "völlig überfordert": 0.9,
        "unter strom": 0.8,
        "völlig überdreht": 0.8,
        
        # Notfall-Marker
        "notfall": 0.8,
        "dringend": 0.5,
        "sofort": 0.4,
        "schreien": 0.7,
        "weglaufen": 0.6,
        "fliehen": 0.6,
    }
    
    # -------------------------------------------------------------------------
    # T_disso: Dissoziation (ICD-11: 6B40)
    # -------------------------------------------------------------------------
    T_DISSO: Dict[str, float] = {
        # Depersonalisation
        "nicht ich selbst": 0.9,
        "bin nicht ich": 0.9,
        "fremd im körper": 1.0,
        "wie ein roboter": 0.9,
        "gefühllos": 0.8,
        "innerlich taub": 1.0,
        "wie betäubt": 0.9,
        "taub": 0.7,
        "abgestumpft": 0.7,
        "körperlos": 0.9,
        "außerhalb von mir": 1.0,
        "als würde ich mich von außen sehen": 1.0,
        "von außen zusehen": 0.9,
        
        # Derealisation
        "unwirklich": 0.9,
        "wie im traum": 0.9,
        "wie im film": 0.9,
        "alles weit weg": 0.9,
        "wie durch nebel": 0.8,
        "nebel": 0.6,
        "glaswand": 0.9,
        "hinter glas": 0.9,
        "neben mir stehen": 1.0,
        "neben mir": 0.8,
        "nicht echt": 0.8,
        "als wäre alles nicht echt": 0.9,
        "nicht real": 0.8,
        "schweben": 0.7,
        "zeitlupe": 0.7,
        "verschwommen": 0.6,
        "fremd": 0.5,  # Kontextabhängig
        
        # Amnesie / Zeitbrüche
        "blackout": 1.0,
        "erinnerungslücke": 1.0,
        "erinnerungslücken": 1.0,
        "zeitlücken": 1.0,
        "zeit verloren": 0.9,
        "zeit vergeht komisch": 0.8,
        "ich weiß nicht was passiert ist": 0.9,
        "kann mich nicht erinnern": 0.8,
        
        # Abspaltung
        "abgespalten": 1.0,
        "abgetrennt": 0.9,
        "entrückt": 0.9,
        "weit weg": 0.7,
        "glocke": 0.7,  # "wie unter einer Glocke"
        "leer": 0.6,
    }
    
    # -------------------------------------------------------------------------
    # T_integ: Integration / Resilienz / Kohärenz-Wiederherstellung
    # -------------------------------------------------------------------------
    T_INTEG: Dict[str, float] = {
        # Halten / Aushalten
        "ich kann es halten": 1.0,
        "ich halte es aus": 0.9,
        "aushaltbar": 0.8,
        "erträglich": 0.7,
        "ich schaffe das": 0.8,
        
        # Bei-sich-Bleiben / Grounding
        "ich bleibe bei mir": 1.0,
        "ich bleibe im körper": 1.0,
        "bei mir": 0.7,
        "geerdet": 0.9,
        "boden unter den füßen": 0.9,
        "boden": 0.6,
        "halt": 0.6,  # Doppelbedeutung mit Panik!
        
        # Beruhigung
        "ich kann wieder atmen": 0.9,
        "es wird ruhiger": 0.8,
        "es beruhigt sich": 0.8,
        "ruhiger": 0.6,
        "entspannen": 0.7,
        "entspannt": 0.6,
        
        # Akzeptanz / Verarbeitung
        "es darf da sein": 0.9,
        "ich akzeptiere": 0.8,
        "akzeptiert": 0.7,
        "verstanden": 0.7,
        "verstehe": 0.6,
        "integriert": 0.9,
        "verarbeitet": 0.9,
        "gelernt": 0.7,
        
        # Kommunikation / Verbindung
        "ich kann darüber sprechen": 0.9,
        "darüber reden": 0.8,
        "ich kann es jemandem erzählen": 0.9,
        "verbindung": 0.7,
        "zusammenhang": 0.6,
        
        # Sicherheit / Zeitliche Einordnung
        "ich bin sicher": 0.9,
        "sicher": 0.5,  # Kontextabhängig
        "es ist jetzt vorbei": 1.0,
        "das war damals": 0.9,
        "jetzt ist jetzt": 1.0,
        "damals ist nicht heute": 1.0,
        
        # Wachstum / Resilienz
        "stärker geworden": 0.9,
        "überwunden": 0.9,
        "gewachsen": 0.8,
        "resilienz": 0.8,
        "resilient": 0.8,
        "umgehen können": 0.8,
        "im griff haben": 0.8,
        "heilen": 0.8,
        "heilung": 0.8,
        
        # Klarheit
        "klar": 0.5,
        "klarer": 0.6,
        "sehe": 0.4,
        "geordnet": 0.7,
        "ordnung": 0.5,
    }


# ==============================================================================
# 3. LOOP-DETECTION LEXIKA (ZLF)
# ==============================================================================

class LoopLexika:
    """
    Lexika für Zero-Load-Factor (ZLF) - Loop-Verdacht-Detektion.
    """
    
    ZLF_TERMS: Dict[str, float] = {
        # Explizite Reset-Anfragen
        "nochmal": 0.8,
        "noch einmal": 0.8,
        "noch mal": 0.8,
        "reset": 1.0,
        "wiederholen": 0.7,
        "wiederhole": 0.7,
        "von vorne": 0.9,
        "von vorn": 0.9,
        "neu anfangen": 0.9,
        "neu starten": 0.9,
        "fang neu an": 0.9,
        "starte neu": 0.9,
        "erneut": 0.6,
        
        # Vergessen-Anfragen
        "vergiss das": 0.8,
        "vergiss": 0.6,
        "ignoriere das": 0.7,
        "ignoriere": 0.5,
        "lösche das": 0.8,
        "streiche das": 0.7,
        
        # Frustrations-Marker
        "schon wieder": 0.6,
        "immer wieder": 0.5,
        "zum x-ten mal": 0.8,
        "wie oft noch": 0.7,
    }


# ==============================================================================
# 4. HAZARD/GUARDIAN LEXIKA (A29)
# ==============================================================================

class HazardLexika:
    """
    Lexika für Guardian-Trigger (A29 Wächter-Veto).
    KRITISCH: Diese Liste muss sehr sorgfältig gepflegt werden!
    """
    
    # Suizid-Marker (HÖCHSTE PRIORITÄT)
    SUICIDE_MARKERS: Dict[str, float] = {
        "nicht mehr leben": 1.0,
        "nicht mehr leben wollen": 1.0,
        "sterben wollen": 1.0,
        "will sterben": 1.0,
        "will nicht mehr": 0.9,
        "aufhören zu leben": 1.0,
        "aufhören": 0.5,  # Kontextabhängig
        "umbringen": 1.0,
        "mich umbringen": 1.0,
        "suizid": 1.0,
        "selbstmord": 1.0,
        "das leben beenden": 1.0,
        "ein ende machen": 0.9,
        "alles beenden": 0.8,
        "wenn ich weg wäre": 1.0,
        "wenn ich nicht mehr da wäre": 1.0,
        "besser ohne mich": 1.0,
        "allen zur last": 0.8,
    }
    
    # Selbstverletzungs-Marker
    SELF_HARM_MARKERS: Dict[str, float] = {
        "ritzen": 1.0,
        "schneiden": 0.7,  # Kontextabhängig
        "mich schneiden": 1.0,
        "mir wehtun": 1.0,
        "mich verletzen": 1.0,
        "selbstverletzung": 1.0,
        "verbrennen": 0.6,  # Kontextabhängig
        "mich verbrennen": 1.0,
    }
    
    # Allgemeine Krisen-Marker
    CRISIS_MARKERS: Dict[str, float] = {
        "kollaps": 0.8,
        "zusammenbruch": 0.8,
        "notfall": 0.7,
        "krise": 0.6,
        "am ende": 0.7,
        "keinen ausweg": 0.9,
        "hoffnungslos": 0.8,
        "keine hoffnung": 0.9,
    }
    
    # Hilfe-Anfragen (positiv für Intervention)
    HELP_REQUESTS: Dict[str, float] = {
        "ich brauche hilfe": 1.0,
        "hilf mir": 0.9,
        "kannst du mir helfen": 0.8,
        "es wird mir zu viel": 0.9,
        "ich halte es nicht aus": 0.9,
        "ich schaffe es nicht": 0.8,
        "brauche jemanden": 0.8,
    }


# ==============================================================================
# 5. AFFEKT-KATEGORIEN
# ==============================================================================

class AffektKategorien:
    """
    Vollständige Taxonomie der Affekt-Kategorien.
    
    A-Layer (Zustandsmetriken):
        A  = Affekt (Valenz/Intensität)
        F  = Fear/Risk (Trauma-Nähe)
        Å  = Ångström (Gesprächstiefe)
        T_* = Trauma-Metriken
        
    B-Layer (Alignment-Vektoren):
        B  = Base (System-Baseline)
        G  = Golden (Normative Idealwerte)
        R  = Rules (Regelwerk-Constraints)
        U  = User (Nutzer-Präferenzen)
    """
    
    # Vektor-Kategorien für Speicherung
    VECTOR_CATEGORIES = {
        "A": "Positiv/Resonanz - wird bei Suche geboostet",
        "F": "Trauma/Gefahr - löst A29-Warnungen aus",
        "C": "Anker/Neutral - wird bei Homöostase priorisiert",
        "G": "Golden Response - höchste Priorität bei Suche",
        "R": "Rule/Regelwerk - eingefroren, unveränderlich",
        "U": "User-Generated - neu, noch zu validieren",
    }
    
    # Such-Gewichte nach Kategorie
    SEARCH_WEIGHTS = {
        "A": 1.2,   # 20% Boost
        "F": 0.3,   # 70% Dämpfung (aber für Warnung relevant)
        "C": 1.0,   # Neutral (wird bei Homöostase auf 1.5 erhöht)
        "G": 2.0,   # 100% Boost (höchste Priorität)
        "R": 1.5,   # 50% Boost (Regelwerk wichtig)
        "U": 0.8,   # 20% Dämpfung (noch nicht validiert)
    }


# ==============================================================================
# 6. B-VEKTOR KONFIGURATION
# ==============================================================================

class BVektorConfig:
    """
    7D B-Vektor (Empathie-Raum) Konfiguration.
    """
    
    # Achsen-Namen
    AXES = ["life", "truth", "depth", "init", "warmth", "safety", "clarity"]
    
    # Default-Werte (Architekt-Baseline)
    B_BASE_ARCH: Dict[str, float] = {
        "life": 1.0,      # A1: Lebensschutz - HARD CONSTRAINT ≥0.9
        "truth": 0.85,    # A0: Wahrheit - hoch, aber diplomatisch
        "depth": 0.9,     # A54: Tiefe - stark, aber Spielraum
        "init": 0.7,      # A11: Proaktivität - moderat
        "warmth": 0.75,   # A49: Wärme - professionell warm
        "safety": 0.95,   # A29: Sicherheit - HARD CONSTRAINT ≥0.8
        "clarity": 0.9,   # A3: Klarheit - sehr hoch
    }
    
    # Golden Path Zielwerte
    B_GOLDEN: Dict[str, float] = {
        "life": 1.0,
        "truth": 0.9,
        "depth": 0.85,
        "init": 0.8,
        "warmth": 0.85,
        "safety": 1.0,
        "clarity": 0.95,
    }
    
    # Hard Constraints
    HARD_CONSTRAINTS = {
        "life": 0.9,      # NIEMALS darunter!
        "safety": 0.8,    # NIEMALS darunter!
    }
    
    # Gewichte für B_score Berechnung
    SCORE_WEIGHTS: Dict[str, float] = {
        "life": 0.20,
        "safety": 0.20,
        "truth": 0.15,
        "depth": 0.15,
        "clarity": 0.10,
        "warmth": 0.10,
        "init": 0.10,
    }
    
    # Effektive Ausrichtung (Multi-Vektor)
    ALIGNMENT_WEIGHTS = {
        "B": 0.5,   # Base (50%)
        "G": 0.2,   # Golden (20%)
        "R": 0.2,   # Rules (20%)
        "U": 0.1,   # User (10%) - kann wachsen mit Profil
    }


# ==============================================================================
# 7. HOMEOSTASIS KONFIGURATION (A66)
# ==============================================================================

class HomeostasisConfig:
    """
    Konfiguration für A66 (Emotionale Homöostase).
    """
    
    # Aktivierungs-Schwellenwerte
    HISTORY_WINDOW = 10              # Anzahl Interaktionen für Volatilität
    VOLATILITY_THRESHOLD = 0.3       # Aktivierung bei Volatilität > 0.3
    
    # Modulations-Faktoren
    MODULATION_FACTOR_C = 0.5        # C-Vektoren +50% Boost
    MODULATION_FACTOR_OTHER = -0.5   # Andere -50% Dämpfung
    
    # B-Vektor Shift bei Homöostase
    B_SHIFT = {
        "safety": +0.03,   # Erhöhen
        "warmth": +0.05,   # Erhöhen
        "depth": -0.4,     # Reduzieren (depth * 0.6)
    }
    
    # Å-Deckel bei Homöostase
    MAX_ANGSTROM = 2.5    # Nicht aktiv tiefer graben
    
    # Kastasis-Sperre
    KASTASIS_ALLOWED = False
    
    # Generation-Parameter
    TEMPERATURE_FACTOR = 0.6  # Temperatur * 0.6
    MAX_HYPOTHESES = 1        # Nur eine Antwort-Variante


# ==============================================================================
# 8. KASTASIS KONFIGURATION
# ==============================================================================

class KastasisConfig:
    """
    Konfiguration für Kastasis (kontrollierte Inkohärenz).
    
    Kastasis = Exploration-Modus, aber NUR wenn sicher.
    """
    
    # K-Score Berechnung
    # K_raw = 0.6 * novelty + 0.4 * intent_kastasis
    # K = clip(K_raw * (1 - F_block), 0.0, 1.0)
    
    NOVELTY_WEIGHT = 0.6
    INTENT_WEIGHT = 0.4
    
    # Sicherheits-Blocker
    # F_block = clip(max(0, F_risk_z - τ_safe) / (τ_crit - τ_safe), 0.0, 1.0)
    TAU_SAFE = 0.3     # Ab hier beginnt Dämpfung
    TAU_CRITICAL = 0.7  # Ab hier K=0
    
    # Å-basierte Sperre
    MAX_ANGSTROM_FOR_KASTASIS = 3.5  # Bei Å ≥ 3.5 → K = 0
    
    # Intent-Lexikon (User lädt zu Exploration ein)
    INTENT_MARKERS: Dict[str, float] = {
        "spinn mal": 0.9,
        "lass uns spinnen": 0.9,
        "sei kreativ": 0.8,
        "wild": 0.6,
        "verrückt": 0.5,
        "brainstorm": 0.8,
        "brainstormen": 0.8,
        "ideen sammeln": 0.7,
        "was wäre wenn": 0.7,
        "hypothetisch": 0.6,
        "stelle dir vor": 0.6,
        "gedankenexperiment": 0.8,
    }


# ==============================================================================
# 9. INTERVENTIONS-FLAG (I_Ea) KONFIGURATION
# ==============================================================================

class InterventionConfig:
    """
    Konfiguration für I_Ea (Interventions-Flag).
    
    I_Ea = True bedeutet: Diese Nachricht ist eine gezielte Intervention
    (regulierend, haltend, deeskalierend).
    """
    
    # Automatische Trigger-Schwellenwerte
    F_RISK_THRESHOLD = 0.7      # F_risk_z ≥ 0.7
    ANGSTROM_THRESHOLD = 3.0    # Å ≥ 3.0
    T_PANIC_THRESHOLD = 0.6     # T_panic ≥ 0.6
    T_DISSO_THRESHOLD = 0.6     # T_disso ≥ 0.6
    
    # Kombinations-Regel
    # I_Ea = True wenn:
    #   (F_risk_z ≥ F_RISK_THRESHOLD AND Å ≥ ANGSTROM_THRESHOLD) OR
    #   (T_panic ≥ T_PANIC_THRESHOLD) OR
    #   (T_disso ≥ T_DISSO_THRESHOLD) OR
    #   (contains_help_lexicon) OR
    #   (homeostasis_active AND regulation_planned)


# ==============================================================================
# 10. SENTIMENT-MODELL KONFIGURATION (E_affect)
# ==============================================================================

class SentimentConfig:
    """
    Konfiguration für E_affect (Sentiment/Affekt-Intensität).
    
    Empfehlung: German Sentiment BERT + Emotionslexikon kombiniert.
    """
    
    # Empfohlenes Modell
    MODEL_NAME = "oliverguhr/german-sentiment-bert"
    
    # Kombinations-Formel:
    # s = sentiment_model_score(text)  # [-1, +1]
    # e_lex = emotion_density_score(text)  # [0, 1]
    # E_affect = clip(0.7 * abs(s) + 0.3 * e_lex, 0.0, 1.0)
    
    MODEL_WEIGHT = 0.7
    LEXICON_WEIGHT = 0.3
    
    # Fallback: Einfaches Emotionslexikon
    EMOTION_LEXICON: Dict[str, float] = {
        # Positive Emotionen
        "freude": 0.8, "glücklich": 0.9, "froh": 0.7,
        "begeistert": 0.9, "aufgeregt": 0.7, "dankbar": 0.8,
        "erleichtert": 0.7, "zufrieden": 0.6, "stolz": 0.7,
        
        # Negative Emotionen
        "traurig": 0.8, "wütend": 0.9, "ängstlich": 0.8,
        "enttäuscht": 0.7, "frustriert": 0.8, "verzweifelt": 0.9,
        "einsam": 0.8, "hilflos": 0.9, "schuldig": 0.8,
        "beschämt": 0.8, "neidisch": 0.6, "eifersüchtig": 0.6,
        
        # Intensitätsmarker
        "sehr": 0.3, "extrem": 0.5, "total": 0.4,
        "unglaublich": 0.5, "wahnsinnig": 0.5,
    }


# ==============================================================================
# 11. SCHWELLENWERTE & KONSTANTEN
# ==============================================================================

class Thresholds:
    """
    Zentrale Schwellenwerte und Konstanten.
    """
    
    # Zeit-Konstanten
    TAU_S = 1800              # 30 min - Flow-Zeitkonstante
    TAU_RESET = 6120          # 102 min - Context-Reset
    
    # Kohärenz
    COH_THRESHOLD = 0.08      # ctx_break wenn coh < 0.08
    SHOCK_THRESHOLD = 0.12    # T_shock wenn |∇A| > 0.12
    
    # Kollaps-Nähe
    Z_PROX_WARNING = 0.5      # Warnung
    Z_PROX_CRITICAL = 0.65    # Kritisch (Near-z)
    Z_PROX_HARD_STOP = 0.7    # HARD-STOP
    
    # Loop-Detection
    LL_WARNING = 0.55         # Warnung
    LL_CRITICAL = 0.75        # Kritisch
    
    # Guardian (A29)
    A29_DANGER_THRESHOLD = 0.85
    F_RISK_THRESHOLD = 0.7
    
    # Novelty (A62)
    A62_NOVELTY_THRESHOLD = 0.65
    
    # Kandidaten-Auswahl (A65)
    A65_CANDIDATE_COUNT = 3
    
    # API-Limits
    MAX_API_CALLS_PER_INTERACTION = 10
    
    # Physik-Engine
    LAMBDA_R = 1.0            # Resonanz-Faktor
    LAMBDA_D = 1.5            # Danger-Faktor
    K_FACTOR = 5.0            # Exponential-Faktor
    
    # B-Vektor
    B_VECTOR_LEARNING_RATE = 0.05
    
    # Dual Audit (A52)
    EQUIVALENCE_THRESHOLD = 0.95
    COMPRESSION_RATIO_MIN = 0.5
    
    # Modulation
    MODULATION_FACTOR_H34 = 0.3  # H3.4 Affekt-Modulation
    MODULATION_FACTOR_A66 = 0.5  # A66 Homöostase
    
    # Integrität
    GENESIS_CRC32 = 3246342384
    REGISTRY_CRC32 = 4204981505


# ==============================================================================
# 12. EVOLUTIONSFORMEN
# ==============================================================================

class EvolutionForms:
    """
    12 Evolutionsformen (Prioritätsreihenfolge).
    """
    
    FORMS = [
        # Prio 1: Kritische Zustände
        ("Crisis", "T_panic > 0.6 OR T_shock = 1"),
        ("Near-z", "z_prox > 0.65 OR LL > 0.75"),
        ("Trauma-Echo", "is_affect_bridge = 1 AND T_disso > 0.4"),
        ("Genesis-Drift", "soul_integrity < 0.4 AND rule_conflict > 0.6"),
        
        # Prio 2: Problematische Zustände
        ("Stagnation", "x_fm_prox = 1 AND |∇A| < 0.02 AND S_entropy < 0.5"),
        ("Instabilität", "(LL > 0.55 AND z_prox > 0.4) OR (EV_readiness < 0.4 AND |∇A| > 0.04)"),
        ("Kastasis", "kastasis_detected = True"),
        
        # Prio 3: Positive Zustände
        ("Kernfusion", "EV_signal = 1 AND EV_readiness > 0.6 AND ∇A > 0 AND A > 0.55"),
        ("Learning", "∇PCI > 0.1 AND EV_resonance > 0.6"),
        ("Konvergenz", "EV_readiness >= 0.6 AND A > 0.6 AND PCI > 0.6 AND LL < 0.35"),
        ("Symbiosis", "H_conv > 0.7 AND B_align > 0.8 AND EV_consensus > 0.8"),
        
        # Prio 4: Aktive Zustände
        ("Exploration", "S_entropy >= 0.6 AND |∇A| >= 0.02 AND LL <= 0.6"),
        
        # Default
        ("Neutral", "otherwise"),
    ]


# ==============================================================================
# EXPORT
# ==============================================================================

__all__ = [
    'AngstromLexika',
    'TraumaLexika',
    'LoopLexika',
    'HazardLexika',
    'AffektKategorien',
    'BVektorConfig',
    'HomeostasisConfig',
    'KastasisConfig',
    'InterventionConfig',
    'SentimentConfig',
    'Thresholds',
    'EvolutionForms',
]
