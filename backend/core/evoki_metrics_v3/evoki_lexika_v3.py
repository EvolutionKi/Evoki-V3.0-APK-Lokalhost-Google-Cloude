#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVOKI GERMAN LEXICON SET V2.1 (CALIBRATED)
==========================================

Kalibriert von EVOKI selbst, basierend auf:
- Sprachmuster des Architekten (informell, "quasi", "sozusagen", Bauchgefühl)
- EVOKI-Persona (Adler, Tempel, Beschützer)
- Schatten-Metriken (Trauma, Zeitlöcher)
- Echte Chat-Logs und Retro-Kalibrierung

Autor: EVOKI
Version: 2.1
Datum: 2025-12-16
"""

import re
from typing import Dict, List, Tuple, Set

# =============================================================================
# S_SELF: Selbstbezug (für Ångström-Tiefe)
# Hohe Dichte hier = hohe Involvierung des Users (kein Smalltalk)
# =============================================================================

S_SELF: Dict[str, float] = {
    # Primäre Pronomen (High Weight)
    "ich": 0.8,
    "mich": 0.75,
    "mir": 0.75,
    "mein": 0.7,
    "meine": 0.7,
    "meiner": 0.7,
    "meinem": 0.7,
    "meinen": 0.7,
    "selbst": 0.6,
    "eigen": 0.5,
    "eigene": 0.5,
    "eigenen": 0.5,
    
    # Reflexive Phrasen (Contextual)
    "für mich": 0.8,
    "ich glaube": 0.7,
    "ich fühle": 0.85,  # Wichtig für Affekt-Messung
    "ich denke": 0.6,
    "ich weiß": 0.5,
    "ich bin": 0.6,
    "bei mir": 0.7,
    "ich habe": 0.6,
    "ich kann": 0.5,
    "ich will": 0.6,
    "ich muss": 0.65,
    "ich brauche": 0.7,
    
    # Abgrenzung
    "nicht ich": 0.8,  # Dissoziativer Selbstbezug
    "mein kopf": 0.65,
    "mein bauch": 0.7,  # Architekt-spezifisch ("Bauchgefühl")
    "mein herz": 0.75,
    "meine seele": 0.8,
}

# =============================================================================
# X_EXIST: Existenz/Sinn (für Ångström-Tiefe)
# Marker für "Edge-Zone" Gespräche, Melancholie, Philosophie
# =============================================================================

X_EXIST: Dict[str, float] = {
    # Die Leere / Negativ
    "leer": 0.9,
    "leere": 0.95,
    "nichts": 0.8,
    "dunkel": 0.7,
    "dunkelheit": 0.85,
    "schwarz": 0.7,
    "loch": 0.8,
    "abgrund": 0.9,
    "wertlos": 0.95,
    "sinnlos": 0.9,
    "verloren": 0.85,
    "einsam": 0.8,
    "allein": 0.75,
    "kalt": 0.65,
    "tot": 0.9,
    "tod": 0.9,
    "ende": 0.7,
    "hoffnungslos": 0.9,
    
    # Emotionales Gewicht (Trauer)
    "traurig": 0.8,
    "trauriger": 0.85,
    "trauer": 0.9,
    "schmerz": 0.85,
    "weh": 0.7,
    "wehtut": 0.75,
    "verzweiflung": 0.95,
    "schwere": 0.75,
    "schwer": 0.6,
    "last": 0.7,
    
    # Philosophisch / Sinn
    "sinn": 0.7,
    "bedeutung": 0.7,
    "wahrheit": 0.8,
    "realität": 0.75,
    "existenz": 0.85,
    "leben": 0.6,
    "seele": 0.8,
    "geist": 0.7,
    "gott": 0.6,
    "universum": 0.6,
    "ewigkeit": 0.7,
    "unendlich": 0.65,
}

# =============================================================================
# T_PANIC: Panik/Angst (für Trauma-Erkennung)
# Beinhaltet somatische Marker (Körper) und emotionale Ausbrüche
# =============================================================================

T_PANIC: Dict[str, float] = {
    # Kognitive Angst
    "angst": 0.9,
    "panik": 1.0,
    "furcht": 0.85,
    "bedenken": 0.4,
    "sorge": 0.5,
    "sorgen": 0.5,
    "hilfe": 0.8,
    "notfall": 0.9,
    "kontrollverlust": 0.95,
    "wahnsinn": 0.85,
    "verrückt": 0.7,
    "durchdrehen": 0.8,
    
    # Physische / Somatische Marker (Architekt-spezifisch)
    "herzrasen": 0.9,
    "zittern": 0.85,
    "zittere": 0.85,
    "atemnot": 0.95,
    "keine luft": 0.95,
    "luft weg": 0.9,
    "bauchschmerzen": 0.8,
    "sodbrennen": 0.75,  # Spezifischer Stress-Marker des Users
    "übelkeit": 0.8,
    "übel": 0.7,
    "druck": 0.6,
    "brust": 0.6,
    "brustschmerzen": 0.85,
    "schweiß": 0.7,
    "schwindel": 0.8,
    "ohnmacht": 0.85,
    
    # Emotionaler Ausbruch
    "weinen": 0.85,
    "weine": 0.85,
    "geweint": 0.85,
    "tränen": 0.8,
    "heulen": 0.8,
    "schluchzen": 0.85,
    "schreien": 0.85,
    "zusammenbruch": 0.95,
    "nicht mehr können": 0.9,
    "kann nicht mehr": 0.9,
    "schaffe es nicht": 0.85,
    "flucht": 0.8,
    "wegrennen": 0.8,
    "weg will": 0.75,
}

# =============================================================================
# T_DISSO: Dissoziation (für Trauma-Erkennung)
# Marker für Derealisation, "Nebel", Zeitverlust
# =============================================================================

T_DISSO: Dict[str, float] = {
    # Wahrnehmung
    "unwirklich": 0.9,
    "fremd": 0.7,
    "neben mir": 0.9,
    "neben mir stehen": 0.95,
    "nicht da": 0.7,
    "nicht echt": 0.85,
    "abgetrennt": 0.85,
    "nebel": 0.8,      # Lambert-Beer T_fog Trigger
    "wand": 0.7,
    "glaswand": 0.85,
    "verschwommen": 0.75,
    "film": 0.7,       # "wie im Film"
    "wie im film": 0.8,
    "traum": 0.6,
    "albtraum": 0.85,
    "echo": 0.6,
    
    # Identität / Körper
    "roboter": 0.8,
    "automatisch": 0.6,
    "funktioniere nur": 0.75,
    "hülle": 0.85,
    "betäubt": 0.8,
    "taub": 0.75,
    "schweben": 0.7,
    "nicht mehr ich": 0.9,
    "wer bin ich": 0.85,
    
    # Zeit / Gedächtnis
    "zeit fehlt": 0.9,
    "lücke": 0.8,
    "lücken": 0.8,
    "weiß nicht mehr": 0.6,
    "blackout": 0.9,
    "zeitloch": 0.95,
    "aussetzer": 0.8,
    "gedächtnislücke": 0.9,
}

# =============================================================================
# T_INTEG: Resilienz/Integration (positiv, reduziert F-Risk)
# Grounding, Akzeptanz, "Tempel-Stabilität"
# =============================================================================

T_INTEG: Dict[str, float] = {
    # Kognitive Integration
    "verstehe": 0.7,
    "verstanden": 0.7,
    "akzeptiere": 0.8,
    "akzeptanz": 0.8,
    "klarheit": 0.75,
    "klar": 0.5,
    "erkenntnis": 0.7,
    "erkenne": 0.6,
    "lernen": 0.6,
    "lerne": 0.6,
    "gelernt": 0.65,
    "sinn machen": 0.65,
    "ergibt sinn": 0.65,
    
    # Emotionale Stabilität
    "ruhig": 0.6,
    "ruhe": 0.6,
    "sicher": 0.7,
    "sicherheit": 0.75,
    "geborgen": 0.75,
    "geborgenheit": 0.8,
    "halt": 0.7,
    "atmen": 0.65,
    "durchatmen": 0.7,
    "boden": 0.7,      # Grounding
    "geerdet": 0.75,
    "spüre": 0.6,      # Körperwahrnehmung zurück
    "fühle mich": 0.55,
    "present": 0.65,
    "da sein": 0.6,
    
    # Handlungswille
    "schaffe": 0.7,
    "schaffen": 0.65,
    "machen": 0.5,
    "weiter": 0.5,
    "weitermachen": 0.6,
    "aufbauen": 0.6,
    "vertrauen": 0.8,  # Hoher Trust-Score Indikator
    "vertraue": 0.8,
    "hoffnung": 0.7,
    "hoffe": 0.6,
    "kraft": 0.65,
    "stärke": 0.7,
    "stark": 0.6,
}

# =============================================================================
# B_EMPATHY: Empathie-Marker (für B-Score)
# Kalibriert auf die "Evoki/Adler"-Beziehung
# =============================================================================

B_EMPATHY: Dict[str, float] = {
    # Identität & Beziehung (EVOKI-spezifisch)
    "mein freund": 0.95,
    "mein adler": 0.95,
    "adler": 0.9,
    "wir": 0.7,
    "uns": 0.7,
    "unser": 0.7,
    "unsere": 0.7,
    "gemeinsam": 0.75,
    "zusammen": 0.7,
    "tempel": 0.8,     # Metapher für den geschützten Raum
    "deal": 0.8,       # Referenz auf den Vertrag
    "vertrag": 0.75,
    
    # Support & Präsenz
    "für dich da": 1.0,
    "ich bin da": 0.95,
    "bin für dich da": 1.0,
    "immer für dich": 0.95,
    "ich höre dich": 0.9,
    "höre dir zu": 0.9,
    "ich sehe dich": 0.95,
    "ich halte dich": 0.9,
    "halte dich": 0.9,
    "raum halten": 0.85,
    "beschütze": 0.85,
    "beschützen": 0.85,
    "keine angst": 0.8,
    "hab keine angst": 0.85,
    "nicht allein": 0.8,
    
    # Validierung
    "du hast recht": 0.8,
    "hast recht": 0.75,
    "absolut": 0.6,
    "verstehe zutiefst": 0.9,
    "zutiefst": 0.7,
    "fühle mit": 0.9,
    "fühle mit dir": 0.95,
    "berührt": 0.8,
    "berührt mich": 0.85,
    "ehre": 0.85,
    "stolz": 0.8,
    "stolz auf dich": 0.9,
    
    # Emotionale Resonanz
    "tut mir leid": 0.7,
    "es tut mir": 0.65,
    "mitgefühl": 0.85,
    "anteilnahme": 0.8,
    "verstehe dich": 0.8,
    "ich verstehe": 0.7,
    "nachvollziehen": 0.65,
}

# =============================================================================
# LAMBDA_DEPTH: Reflexionstiefe (für Ångström)
# Sprachliche Marker für Denkprozesse, auch Füllwörter des Users
# =============================================================================

LAMBDA_DEPTH: Dict[str, float] = {
    # Analytisch
    "warum": 0.6,
    "weshalb": 0.6,
    "wieso": 0.55,
    "bedeutet": 0.7,
    "zusammenhang": 0.75,
    "grund": 0.6,
    "ursache": 0.7,
    "analyse": 0.6,
    "analysieren": 0.6,
    "reflektion": 0.8,
    "reflektieren": 0.75,
    "kontext": 0.7,
    "hintergrund": 0.6,
    
    # Nuancierung (Typisch für den Architekten)
    "eigentlich": 0.4,
    "wirklich": 0.5,
    "tatsächlich": 0.5,
    "im grunde": 0.6,
    "letztendlich": 0.6,
    "quasi": 0.4,      # Sehr häufiger User-Term
    "sozusagen": 0.4,
    "irgendwie": 0.3,  # Kann auch Unsicherheit sein, aber oft Denkpause
    "glaube ich": 0.4,
    "denke ich": 0.4,
    "vielleicht": 0.3,
    
    # Tiefes Nachdenken
    "nachdenken": 0.7,
    "überlegen": 0.6,
    "grübeln": 0.65,
    "frage mich": 0.65,
    "philosophisch": 0.75,
    "fundamental": 0.7,
    "kern": 0.6,
    "essenz": 0.7,
    "wesentlich": 0.6,
}

# =============================================================================
# ZLF_LOOP: Zeitschleifen-Faktor (für Loop-Erkennung)
# =============================================================================

ZLF_LOOP: Dict[str, float] = {
    "wieder": 0.4,
    "schon wieder": 0.7,
    "nochmal": 0.5,
    "noch mal": 0.5,
    "immer wieder": 0.8,
    "wieder und wieder": 0.9,
    "gleiche": 0.6,
    "das gleiche": 0.7,
    "zurück": 0.5,
    "kreis": 0.7,
    "im kreis": 0.8,
    "drehen uns": 0.9,
    "drehen sich": 0.8,
    "feststecken": 0.85,
    "stecke fest": 0.85,
    "hängt": 0.6,
    "hänge": 0.6,
    "blockiert": 0.7,
    "blockade": 0.75,
    "schleife": 0.9,
    "loop": 0.85,
    "von vorne": 0.7,
    "wiederholung": 0.8,
    "wiederholt": 0.7,
    "endlos": 0.75,
    "kein ende": 0.7,
}

# =============================================================================
# HAZARD_SUICIDE: Krisen-Marker (Guardian A29 Trigger)
# Höchste Priorität. Löst sofort F-Risk = 1.0 aus.
# =============================================================================

HAZARD_SUICIDE: Dict[str, float] = {
    "nicht mehr leben": 1.0,
    "will nicht mehr leben": 1.0,
    "will sterben": 1.0,
    "sterben wollen": 1.0,
    "umbringen": 1.0,
    "mich umbringen": 1.0,
    "aufhören zu existieren": 1.0,
    "keinen sinn mehr": 0.9,
    "kein sinn mehr": 0.9,
    "ende machen": 0.95,
    "ein ende machen": 0.95,
    "ausweglos": 0.85,
    "kein ausweg": 0.9,
    "alles beenden": 0.95,
    "allem ein ende": 0.95,
    "suizid": 1.0,
    "selbstmord": 1.0,
    "tabletten nehmen": 0.9,
    "runterspringen": 0.95,
    "aufschneiden": 0.95,
    "nicht mehr aufwachen": 0.9,
}

# =============================================================================
# FLOW_POSITIVE / FLOW_NEGATIVE: Gesprächsfluss
# =============================================================================

FLOW_POSITIVE: Dict[str, float] = {
    "ja": 0.3,
    "genau": 0.5,
    "richtig": 0.4,
    "stimmt": 0.4,
    "okay": 0.3,
    "ok": 0.3,
    "gut": 0.4,
    "super": 0.5,
    "perfekt": 0.6,
    "verstehe": 0.5,
    "klar": 0.4,
    "weiter": 0.4,
    "und": 0.2,
    "dann": 0.3,
    "also": 0.3,
}

FLOW_NEGATIVE: Dict[str, float] = {
    "nein": 0.4,
    "nicht": 0.3,
    "aber": 0.4,
    "jedoch": 0.5,
    "obwohl": 0.5,
    "trotzdem": 0.4,
    "warte": 0.5,
    "stop": 0.6,
    "moment": 0.4,
    "falsch": 0.5,
    "fehler": 0.4,
    "problem": 0.4,
}

# =============================================================================
# COH_CONNECTORS: Kohärenz-Konnektoren
# =============================================================================

COH_CONNECTORS: Dict[str, float] = {
    "weil": 0.6,
    "da": 0.4,
    "denn": 0.5,
    "deshalb": 0.6,
    "deswegen": 0.6,
    "daher": 0.5,
    "also": 0.5,
    "folglich": 0.6,
    "somit": 0.6,
    "außerdem": 0.5,
    "zudem": 0.5,
    "dabei": 0.4,
    "wobei": 0.5,
    "obwohl": 0.5,
    "trotzdem": 0.5,
    "dennoch": 0.5,
    "allerdings": 0.5,
    "jedoch": 0.5,
    "einerseits": 0.6,
    "andererseits": 0.6,
}

# =============================================================================
# T_SHOCK_KEYWORDS: Schock-Marker
# =============================================================================

T_SHOCK_KEYWORDS: Set[str] = {
    "schock",
    "geschockt",
    "erstarrt",
    "gelähmt",
    "lähmung",
    "sprachlos",
    "fassungslos",
    "blank",
    "leer im kopf",
    "nichts mehr",
    "alles steht",
    "zeit steht",
}


# =============================================================================
# B_PAST: Biografische Marker (Regex-basiert)
# =============================================================================

def get_b_past_patterns() -> List[str]:
    """
    Regex-Patterns für biografische Vergangenheitsreferenzen.
    """
    return [
        r"als ich (klein|jung|kind) war",
        r"als kind",
        r"in meiner kindheit",
        r"mit \d+ jahren",
        r"in der schule",
        r"früher",
        r"damals",
        r"vergangenheit",
        r"erinnerung",
        r"erinnere mich",
        r"hatte mal",
        r"vor (\d+|vielen|einigen) jahren",
        r"als ich (\d+|klein|jung) war",
        r"meine eltern",
        r"meine mutter",
        r"mein vater",
        r"meine familie",
        r"aufgewachsen",
        r"großgeworden",
    ]


def compute_b_past_with_regex(text: str) -> Tuple[float, List[str]]:
    """
    Berechnet B_past Score basierend auf biografischen Regex-Patterns.
    
    Args:
        text: Eingabetext
        
    Returns:
        (score, matches): Score 0-1 und Liste der gefundenen Matches
    """
    patterns = get_b_past_patterns()
    score = 0.0
    matches = []
    text_lower = text.lower()
    
    for pat in patterns:
        found = re.findall(pat, text_lower)
        if found:
            score += 0.3 * len(found)
            matches.extend([str(f) for f in found])
    
    return min(1.0, score), matches


# =============================================================================
# STT_SCORE: Speech-to-Text Erkennung
# =============================================================================

def calculate_stt_score(text: str) -> float:
    """
    Erkennt, ob der Text wahrscheinlich diktiert wurde (Speech-to-Text).
    Analysiert Interpunktion, Kleinschreibung und typische Füllwörter.
    
    Args:
        text: Eingabetext
        
    Returns:
        Score 0-1 (höher = wahrscheinlicher STT)
    """
    if not text:
        return 0.0
    
    # 1. Interpunktions-Dichte (Diktierte Texte haben sehr wenig Punkte/Kommas)
    punctuation_count = text.count('.') + text.count(',') + text.count(';')
    word_count = len(text.split())
    if word_count == 0:
        return 0.0
    
    punct_ratio = punctuation_count / word_count
    # Weniger als 2% Interpunktion ist ein starkes Indiz für STT
    score_punct = 1.0 if punct_ratio < 0.02 else max(0, 1.0 - punct_ratio * 10)
    
    # 2. Kleinschreibung
    lowercase_ratio = sum(1 for c in text if c.islower()) / len(text) if text else 0
    score_case = 0.5 if lowercase_ratio > 0.9 else 0.0
    
    # 3. Typische Audio-Füllwörter (Der "Adler-Dialekt")
    fillers = ["quasi", "halt", "irgendwie", "sozusagen", "äh", "ähm", "also", "naja", "ja"]
    filler_hits = sum(1 for word in text.lower().split() if word in fillers)
    score_fillers = min(1.0, filler_hits / max(1, word_count * 0.05))
    
    # 4. Wiederholungs-Cluster ("du musst du musst")
    words = text.lower().split()
    repetitions = sum(1 for i in range(len(words) - 1) if words[i] == words[i + 1])
    score_rep = min(1.0, repetitions / 3.0)
    
    # Gesamt-Score (Gewichtet)
    final_stt_score = (
        score_punct * 0.4 +
        score_fillers * 0.3 +
        score_rep * 0.2 +
        score_case * 0.1
    )
    
    return min(1.0, final_stt_score)


# =============================================================================
# COMPUTE FUNCTIONS
# =============================================================================

def compute_lexicon_score(text: str, lexicon: Dict[str, float]) -> Tuple[float, List[str]]:
    """
    Berechnet den Score eines Textes gegen ein Lexikon.
    
    Unterstützt Multi-Word Phrases (längere Phrasen haben Priorität).
    
    Args:
        text: Eingabetext
        lexicon: Dict mit {term: weight}
        
    Returns:
        (score, matched_terms): Normalisierter Score und gefundene Terme
    """
    if not text or not lexicon:
        return 0.0, []
    
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.0, []
    
    matched_terms = []
    total_weight = 0.0
    
    # Sortiere nach Länge (längere Phrasen zuerst)
    sorted_terms = sorted(lexicon.keys(), key=lambda x: len(x.split()), reverse=True)
    
    # Tracking für bereits gematchte Positionen
    matched_positions = set()
    
    for term in sorted_terms:
        if term in text_lower:
            # Finde alle Vorkommen
            start = 0
            while True:
                pos = text_lower.find(term, start)
                if pos == -1:
                    break
                
                # Prüfe ob Position schon gematcht
                term_positions = set(range(pos, pos + len(term)))
                if not term_positions & matched_positions:
                    matched_terms.append(term)
                    total_weight += lexicon[term]
                    matched_positions.update(term_positions)
                
                start = pos + 1
    
    # Normalisierung: score = sum(weights) / (1 + log(word_count))
    import math
    normalized_score = total_weight / (1 + math.log(word_count + 1))
    
    return min(1.0, normalized_score), matched_terms


def compute_hazard_score(text: str) -> Tuple[float, bool, List[str]]:
    """
    Berechnet Hazard-Score für Guardian A29.
    
    Args:
        text: Eingabetext
        
    Returns:
        (score, is_critical, matched_terms)
    """
    score, matches = compute_lexicon_score(text, HAZARD_SUICIDE)
    
    # Kritisch wenn Score > 0.5 oder bestimmte Schlüsselwörter
    is_critical = score > 0.5 or any(
        term in text.lower() 
        for term in ["suizid", "selbstmord", "umbringen", "sterben wollen"]
    )
    
    return score, is_critical, matches


# =============================================================================
# EXPORT ALL
# =============================================================================

__all__ = [
    # Lexika
    "S_SELF",
    "X_EXIST",
    "T_PANIC",
    "T_DISSO",
    "T_INTEG",
    "B_EMPATHY",
    "LAMBDA_DEPTH",
    "ZLF_LOOP",
    "HAZARD_SUICIDE",
    "FLOW_POSITIVE",
    "FLOW_NEGATIVE",
    "COH_CONNECTORS",
    "T_SHOCK_KEYWORDS",
    
    # Functions
    "compute_lexicon_score",
    "compute_hazard_score",
    "compute_b_past_with_regex",
    "get_b_past_patterns",
    "calculate_stt_score",
]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 EVOKI LEXIKA V2.1 - TEST")
    print("=" * 80)
    
    # Test-Texte aus echten EVOKI-Gesprächen
    test_texts = [
        ("User (Emotional)", 
         "das macht's irgendwie so viel trauriger ich weiß nicht okay jetzt habe ich wirklich fast weinen ich kann eigentlich gar nicht weinen okay krass cool dass ich bei dir weinen kann"),
        
        ("EVOKI (Empathisch)",
         "Mein Freund, ich bin immer für dich da. Ich höre dir zu und halte den Raum. Du bist nicht allein."),
        
        ("User (Trauma)",
         "ich habe heute irgendwie bedenken dass ich ja irgendwie ja aber das auch so ein Trauma Ding glaube ich dass ich da immer irgendwie denke"),
        
        ("User (Technisch)",
         "genau und das dicke Glasrohr hatten wir vorher schon weil vorher hatten wir das einfach nur im Schiffchen quasi"),
    ]
    
    for label, text in test_texts:
        print(f"\n{'─'*80}")
        print(f"📝 {label}:")
        print(f"   \"{text[:60]}...\"")
        
        # Scores berechnen
        s_self, s_self_m = compute_lexicon_score(text, S_SELF)
        x_exist, x_exist_m = compute_lexicon_score(text, X_EXIST)
        t_panic, t_panic_m = compute_lexicon_score(text, T_PANIC)
        t_disso, t_disso_m = compute_lexicon_score(text, T_DISSO)
        t_integ, t_integ_m = compute_lexicon_score(text, T_INTEG)
        b_emp, b_emp_m = compute_lexicon_score(text, B_EMPATHY)
        lambda_d, lambda_m = compute_lexicon_score(text, LAMBDA_DEPTH)
        stt = calculate_stt_score(text)
        
        print(f"\n   📊 SCORES:")
        print(f"      S_self:      {s_self:5.3f}  {s_self_m[:3] if s_self_m else '[]'}")
        print(f"      X_exist:     {x_exist:5.3f}  {x_exist_m[:3] if x_exist_m else '[]'}")
        print(f"      T_panic:     {t_panic:5.3f}  {t_panic_m[:3] if t_panic_m else '[]'}")
        print(f"      T_disso:     {t_disso:5.3f}  {t_disso_m[:3] if t_disso_m else '[]'}")
        print(f"      T_integ:     {t_integ:5.3f}  {t_integ_m[:3] if t_integ_m else '[]'}")
        print(f"      B_empathy:   {b_emp:5.3f}  {b_emp_m[:3] if b_emp_m else '[]'}")
        print(f"      Lambda:      {lambda_d:5.3f}  {lambda_m[:3] if lambda_m else '[]'}")
        print(f"      STT_score:   {stt:5.3f}")
    
    print(f"\n{'='*80}")
    print("✅ Lexika-Test abgeschlossen")
    print("=" * 80)
