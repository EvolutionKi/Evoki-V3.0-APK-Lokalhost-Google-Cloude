#!/usr/bin/env python3
"""
EVOKI LEXIKA - Gewichtete Terme für Metrik-Berechnung
~350 Terme in 12 Kategorien
"""

# S_self: Selbstreferenz (24 Terme)
S_SELF = {
    "ich bin": 1.0, "ich selbst": 1.0, "mein selbst": 1.0, "wer ich bin": 1.0,
    "ich fühle": 0.8, "ich denke": 0.8, "ich glaube": 0.8, "ich weiß": 0.8,
    "ich verstehe": 0.8, "mir ist": 0.8, "ich habe": 0.6, "ich kann": 0.6,
    "ich will": 0.6, "ich muss": 0.6, "mein": 0.5, "mir": 0.5,
    "ich": 0.4, "mich": 0.4, "meiner": 0.4, "meinem": 0.4,
    "meinen": 0.4, "meine": 0.4, "bei mir": 0.5, "für mich": 0.5,
}

# X_exist: Existenzielle Terme (52 Terme)
X_EXIST = {
    "existenz": 1.0, "existieren": 1.0, "sein": 0.9, "dasein": 1.0,
    "wirklichkeit": 0.9, "realität": 0.9, "wahrheit": 0.8, "bedeutung": 0.8,
    "sinn": 0.9, "sinnlos": 0.9, "zweck": 0.7, "ziel": 0.6,
    "leben": 0.8, "tod": 0.9, "sterben": 0.9, "vergänglich": 0.8,
    "ewig": 0.8, "unendlich": 0.7, "endlich": 0.7, "begrenzt": 0.6,
    "nichts": 0.8, "alles": 0.6, "leer": 0.7, "leere": 0.8,
    "voll": 0.5, "ganz": 0.5, "teil": 0.5, "fragment": 0.6,
    "ursprung": 0.7, "anfang": 0.6, "ende": 0.7, "schicksal": 0.8,
    "bestimmung": 0.7, "zufall": 0.6, "notwendig": 0.6, "möglich": 0.5,
    "unmöglich": 0.6, "wahr": 0.7, "falsch": 0.6, "gut": 0.5,
    "böse": 0.6, "richtig": 0.5, "freiheit": 0.8, "gefangen": 0.7,
    "befreit": 0.7, "bewusstsein": 1.0, "unbewusst": 0.8, "gewahr": 0.9,
    "erkenntnis": 0.8, "verstehen": 0.7, "begreifen": 0.7, "wissen": 0.6,
}

# Lambda_tiefe: Tiefenreflexion (35 Terme)
LAMBDA_DEPTH = {
    "warum": 0.8, "weshalb": 0.8, "wieso": 0.7, "wozu": 0.7,
    "wofür": 0.6, "grundlegend": 0.7, "fundamental": 0.8, "tiefgreifend": 0.8,
    "ursprünglich": 0.7, "wesentlich": 0.7, "essentiell": 0.8, "kern": 0.7,
    "wurzel": 0.7, "basis": 0.6, "fundament": 0.7, "hintergrund": 0.6,
    "ursache": 0.8, "grund": 0.7, "motiv": 0.6, "antrieb": 0.6,
    "bedeutet": 0.7, "heißt das": 0.7, "impliziert": 0.8, "folgt": 0.6,
    "zusammenhang": 0.7, "verbindung": 0.6, "beziehung": 0.6, "kontext": 0.6,
    "perspektive": 0.7, "sichtweise": 0.6, "betrachtung": 0.6, "analyse": 0.7,
    "reflexion": 0.9, "nachdenken": 0.7, "überlegung": 0.6,
}

# B_empathy: Empathie/Bindung (40 Terme)
B_EMPATHY = {
    "verstehe dich": 1.0, "fühle mit": 1.0, "nachvollziehen": 0.9,
    "einfühlen": 1.0, "mitfühlen": 1.0, "empathie": 1.0,
    "verständnis": 0.8, "anteilnahme": 0.9, "mitgefühl": 1.0,
    "sorge": 0.7, "fürsorge": 0.8, "kümmern": 0.7, "helfen": 0.6,
    "unterstützen": 0.7, "beistehen": 0.8, "trösten": 0.8,
    "verbunden": 0.8, "verbindung": 0.7, "nähe": 0.7, "nah": 0.6,
    "zusammen": 0.6, "gemeinsam": 0.6, "teilen": 0.7, "teilhaben": 0.7,
    "beziehung": 0.7, "bindung": 0.8, "vertrauen": 0.8, "vertraut": 0.7,
    "sicher": 0.6, "geborgen": 0.8, "wärme": 0.7, "herzlich": 0.7,
    "liebe": 0.9, "liebevoll": 0.8, "zuneigung": 0.8, "mögen": 0.6,
    "schätzen": 0.7, "respekt": 0.7, "achtung": 0.7, "wertschätzen": 0.8,
}

# T_panic: Panik-Indikatoren (30 Terme)
T_PANIC = {
    "panik": 1.0, "panisch": 1.0, "angst": 0.9, "furcht": 0.8,
    "terror": 1.0, "schrecken": 0.9, "entsetzen": 0.9, "horror": 0.9,
    "verzweiflung": 0.9, "verzweifelt": 0.9, "hoffnungslos": 0.8,
    "ausweglos": 0.9, "hilflos": 0.8, "ohnmächtig": 0.8, "machtlos": 0.7,
    "gefangen": 0.7, "ersticken": 0.9, "ertrinken": 0.9, "fallen": 0.6,
    "sterben": 0.8, "tot": 0.7, "ende": 0.6, "verloren": 0.7,
    "allein": 0.6, "einsam": 0.6, "verlassen": 0.7, "niemand": 0.6,
    "hilfe": 0.7, "retten": 0.7, "fliehen": 0.8,
}

# T_disso: Dissoziation (28 Terme)
T_DISSO = {
    "fremd": 0.8, "unwirklich": 0.9, "entrückt": 0.9, "abgetrennt": 0.9,
    "losgelöst": 0.8, "schwebend": 0.7, "benebelt": 0.8, "betäubt": 0.8,
    "taub": 0.7, "leer": 0.7, "hohl": 0.8, "nichts fühlen": 1.0,
    "nicht da": 0.9, "weg": 0.6, "woanders": 0.7, "neben mir": 0.9,
    "außerhalb": 0.8, "beobachte mich": 1.0, "film": 0.7, "traum": 0.7,
    "verschwommen": 0.7, "nebel": 0.7, "dunkel": 0.6, "tunnel": 0.7,
    "weit weg": 0.8, "nicht real": 0.9, "surreal": 0.8, "absurd": 0.6,
}

# T_shock: Schock-Indikatoren (20 Terme)
T_SHOCK = {
    "schock": 1.0, "geschockt": 1.0, "erstarrt": 0.9, "gelähmt": 0.9,
    "starr": 0.8, "eingefroren": 0.9, "blockiert": 0.7, "stumm": 0.7,
    "sprachlos": 0.8, "fassungslos": 0.9, "ungläubig": 0.7, "kann nicht": 0.6,
    "wie betäubt": 0.9, "funktioniere": 0.7, "automatisch": 0.6,
    "roboter": 0.7, "zombie": 0.8, "tot innen": 0.9, "abgestorben": 0.9,
    "kalt": 0.6,
}

# FLOW: Dialogfluss-Terme (25 Terme)
FLOW_POSITIVE = {
    "genau": 0.8, "richtig": 0.7, "stimmt": 0.8, "ja": 0.6,
    "verstanden": 0.8, "klar": 0.7, "okay": 0.6, "gut": 0.6,
    "weiter": 0.7, "fortfahren": 0.7, "mehr": 0.6, "erzähl": 0.7,
    "interessant": 0.8, "spannend": 0.7, "neugierig": 0.7,
}

FLOW_NEGATIVE = {
    "nein": 0.7, "falsch": 0.8, "stimmt nicht": 0.9, "verstehe nicht": 0.8,
    "unklar": 0.7, "verwirrt": 0.7, "was": 0.5, "häh": 0.6,
    "stop": 0.8, "warte": 0.6, "moment": 0.5,
}

# COH: Kohärenz-Marker (30 Terme)
COH_CONNECTORS = {
    "weil": 0.8, "denn": 0.7, "daher": 0.8, "deshalb": 0.8,
    "also": 0.7, "folglich": 0.9, "somit": 0.8, "dadurch": 0.7,
    "jedoch": 0.7, "aber": 0.6, "allerdings": 0.7, "dennoch": 0.8,
    "trotzdem": 0.8, "obwohl": 0.8, "während": 0.6, "wenn": 0.6,
    "falls": 0.6, "sofern": 0.7, "außerdem": 0.6, "zusätzlich": 0.6,
    "ebenso": 0.7, "gleichzeitig": 0.7, "zunächst": 0.7, "dann": 0.6,
    "schließlich": 0.8, "letztlich": 0.8, "zusammenfassend": 0.9,
    "insgesamt": 0.8, "konkret": 0.7, "beispielsweise": 0.7,
}

# REP: Repetition-Marker
REP_MARKERS = {
    "wieder": 0.8, "erneut": 0.8, "nochmal": 0.9, "abermals": 0.9,
    "immer noch": 0.9, "weiterhin": 0.7, "nach wie vor": 0.9,
    "wie gesagt": 1.0, "wie erwähnt": 1.0, "bereits": 0.7,
    "schon wieder": 1.0, "dasselbe": 0.9, "gleiche": 0.7,
}

# SENTIMENT: Valenz-Lexikon
SENTIMENT_POS = {
    "gut": 0.6, "schön": 0.7, "toll": 0.8, "super": 0.8, "wunderbar": 0.9,
    "fantastisch": 0.9, "großartig": 0.9, "perfekt": 0.9, "genial": 0.9,
    "freude": 0.8, "glück": 0.9, "glücklich": 0.9, "zufrieden": 0.7,
    "dankbar": 0.8, "hoffnung": 0.7, "optimistisch": 0.8, "positiv": 0.7,
    "liebe": 0.9, "frieden": 0.8, "harmonie": 0.8, "erfolg": 0.7,
}

SENTIMENT_NEG = {
    "schlecht": 0.6, "schrecklich": 0.9, "furchtbar": 0.9, "grauenhaft": 0.9,
    "traurig": 0.7, "trauer": 0.8, "wut": 0.8, "wütend": 0.8, "zorn": 0.8,
    "hass": 0.9, "ekel": 0.8, "abscheu": 0.9, "verachtung": 0.8,
    "angst": 0.8, "sorge": 0.6, "problem": 0.5, "fehler": 0.6,
    "scheitern": 0.7, "verlust": 0.7, "schmerz": 0.8, "leid": 0.8,
}

# Alle Lexika zusammenfassen für einfachen Zugriff
ALL_LEXIKA = {
    "S_self": S_SELF,
    "X_exist": X_EXIST,
    "Lambda_depth": LAMBDA_DEPTH,
    "B_empathy": B_EMPATHY,
    "T_panic": T_PANIC,
    "T_disso": T_DISSO,
    "T_shock": T_SHOCK,
    "Flow_pos": FLOW_POSITIVE,
    "Flow_neg": FLOW_NEGATIVE,
    "Coh_conn": COH_CONNECTORS,
    "Rep_mark": REP_MARKERS,
    "Sent_pos": SENTIMENT_POS,
    "Sent_neg": SENTIMENT_NEG,
}


def compute_lexicon_score(text: str, lexicon: dict) -> float:
    """
    Berechnet gewichteten Score basierend auf Lexikon-Matches.
    Normalisiert auf [0, 1].
    """
    if not text:
        return 0.0
    
    text_lower = text.lower()
    total_weight = 0.0
    match_count = 0
    
    for term, weight in lexicon.items():
        if term in text_lower:
            total_weight += weight
            match_count += 1
    
    if match_count == 0:
        return 0.0
    
    # Normalisierung: Durchschnittliches Gewicht * log(1 + Anzahl Matches)
    import math
    avg_weight = total_weight / match_count
    score = avg_weight * math.log1p(match_count) / math.log1p(len(lexicon))
    
    return min(1.0, score)
