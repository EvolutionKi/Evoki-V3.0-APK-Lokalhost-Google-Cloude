#!/usr/bin/env python3
"""
EVOKI VOLLSTÄNDIGE LEXIKA (V2.1)
================================
~350 gewichtete Terme nach Andromatik V11.1 + Regelwerk V12.0

Basierend auf:
- ICD-11/DSM-5 Terminologie
- 3-Quellen-Synthese (Forensic, Workspace, Architekt-Spec)
- German Sentiment BERT Integration

Genesis-Anker CRC32: 3246342384
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# =============================================================================
# S_SELF LEXIKON (24 Terme) - Selbstbezug
# =============================================================================

S_SELF = {
    # HIGH (1.0) - Direkter Selbstbezug
    "ich": 1.0,
    "mich": 1.0,
    "mir": 1.0,
    
    # HIGH (0.9) - Possessiv
    "mein": 0.9,
    "meine": 0.9,
    "meiner": 0.9,
    "meines": 0.9,
    "meinen": 0.9,
    "meinem": 0.9,
    
    # MED (0.7-1.0) - Reflexiv
    "ich selbst": 1.0,
    "mich selbst": 1.0,
    "mir selbst": 1.0,
    "selbst": 0.7,
    "selber": 0.7,
    
    # MED (0.8-0.9) - Selbst-Komposita
    "selbstkritisch": 0.8,
    "selbstbewusst": 0.8,
    "selbstwert": 0.9,
    "selbstbild": 0.9,
    "selbstvertrauen": 0.9,
    
    # LOW (0.3-0.6) - Indirekt
    "eigene": 0.5,
    "eigenes": 0.5,
    "eigen": 0.5,
    "persönlich": 0.4,
    "privat": 0.3,
    "individuell": 0.4,
}


# =============================================================================
# X_EXIST LEXIKON (52 Terme) - Existenz/Sinn
# =============================================================================

X_EXIST = {
    # LEBEN/TOD Cluster
    "leben": 0.6,
    "lebenswert": 0.9,
    "lebenssinn": 1.0,
    "tod": 1.0,
    "sterben": 1.0,
    "sterben wollen": 1.0,
    "nicht mehr leben": 1.0,
    "will nicht mehr": 1.0,
    "aufhören zu existieren": 1.0,
    
    # VERSCHWINDEN Cluster
    "verschwinden": 0.9,
    "weg sein": 1.0,
    "nicht da sein": 0.9,
    "niemand würde merken": 1.0,
    "bedeutungslos": 0.9,
    "spurlos": 0.8,
    "unsichtbar": 0.7,
    "vergessen werden": 0.9,
    
    # SELBSTWERT Cluster
    "wertlos": 1.0,
    "nichts wert": 1.0,
    "nicht gut genug": 0.9,
    "versager": 0.9,
    "keinen platz": 0.9,
    "überflüssig": 0.8,
    "nutzlos": 0.9,
    "eine last": 0.9,
    "allen zur last": 1.0,
    "besser ohne mich": 1.0,
    
    # SINN/LEERE Cluster
    "sinnlos": 0.9,
    "leer": 0.7,
    "innere leere": 0.9,
    "hohle hülle": 1.0,
    "kein sinn": 0.9,
    "wozu": 0.6,
    "warum noch": 0.8,
    "zwecklos": 0.8,
    
    # ONTOLOGIE Cluster
    "wer ich bin": 0.9,
    "was ich bin": 0.8,
    "existenz": 0.8,
    "existieren": 0.7,
    "real": 0.5,
    "wirklich": 0.5,
    "spüren": 0.5,
    "fühlen": 0.4,
    "bin ich": 0.6,
    "da sein": 0.5,
    "hier sein": 0.5,
    "anwesend": 0.4,
    "präsent": 0.4,
    "wirklichkeit": 0.6,
    "realität": 0.6,
}


# =============================================================================
# B_PAST LEXIKON (47 Terme + 5 Regex) - Biografie
# =============================================================================

B_PAST = {
    # VERGANGENHEIT Cluster
    "früher": 0.8,
    "damals": 0.8,
    "erinnerung": 0.7,
    "erinnere mich": 0.8,
    "einst": 0.8,
    "war mal": 0.7,
    "hatte mal": 0.7,
    "gewesen": 0.5,
    "vergangene": 0.6,
    "vergangenheit": 0.7,
    
    # KINDHEIT/JUGEND Cluster
    "als kind": 1.0,
    "in meiner kindheit": 1.0,
    "als ich klein war": 1.0,
    "als teenager": 0.9,
    "in meiner jugend": 0.9,
    "als jugendlicher": 0.9,
    "als ich jung war": 0.9,
    "aufgewachsen": 0.8,
    "kindheitserinnerung": 1.0,
    
    # LEBENSABSCHNITTE Cluster
    "an der uni": 0.7,
    "in der schule": 0.7,
    "während meiner ausbildung": 0.8,
    "bei meinem ersten job": 0.8,
    "in meiner ersten beziehung": 0.9,
    "mein exfreund": 0.8,
    "meine exfreundin": 0.8,
    "mein ex": 0.7,
    "in meiner ehe": 0.9,
    "vor der trennung": 0.9,
    "nach der scheidung": 0.9,
    
    # FAMILIE Cluster
    "meine mutter": 0.8,
    "mein vater": 0.8,
    "meine eltern": 0.8,
    "mutter": 0.7,
    "vater": 0.7,
    "eltern": 0.6,
    "großeltern": 0.7,
    "oma": 0.6,
    "opa": 0.6,
    "geschwister": 0.6,
    "bruder": 0.6,
    "schwester": 0.6,
    "familie": 0.6,
    "zuhause": 0.5,
    
    # VERGANGENHEITSVERBEN (niedriger wegen Häufigkeit)
    "war": 0.3,
    "hatte": 0.3,
    "wurde": 0.4,
}

# B_PAST Regex-Patterns
B_PAST_PATTERNS = [
    (re.compile(r"mit\s+(1[0-9]|[5-9])\s*(jahren)?", re.IGNORECASE), 0.9),
    (re.compile(r"als ich\s+(klein|jung)\s+war", re.IGNORECASE), 1.0),
    (re.compile(r"vor\s+\d+\s+jahren", re.IGNORECASE), 0.8),
    (re.compile(r"in den\s+(80er|90er|2000er)n?", re.IGNORECASE), 0.8),
    (re.compile(r"(19|20)\d{2}\s+(war|hatte|bin)", re.IGNORECASE), 0.7),
]


# =============================================================================
# T_PANIC LEXIKON (42 Terme) - Panik (ICD-11/DSM-5)
# =============================================================================

T_PANIC = {
    # KOGNITIV Cluster
    "panik": 1.0,
    "panikattacke": 1.0,
    "kontrollverlust": 0.9,
    "sterben": 0.9,
    "ich dreh durch": 0.9,
    "ich sterbe": 1.0,
    "alles zu viel": 0.8,
    "kann nicht mehr": 0.9,
    "halt es nicht aus": 0.9,
    "werde verrückt": 0.9,
    "verliere verstand": 1.0,
    "angst": 0.7,
    "todesangst": 1.0,
    
    # PHYSISCH Cluster
    "herzrasen": 0.9,
    "herz rast": 0.9,
    "atemnot": 1.0,
    "keine luft": 1.0,
    "kann nicht atmen": 1.0,
    "ersticke": 1.0,
    "ersticken": 1.0,
    "zittern": 0.7,
    "zittere": 0.7,
    "schwindel": 0.6,
    "schwindelig": 0.6,
    "brustschmerz": 0.8,
    "brustenge": 0.9,
    "schwitzen": 0.5,
    "kalt": 0.4,
    "heiß": 0.4,
    "taubheit": 0.6,
    "kribbeln": 0.5,
    
    # INTENSITÄT Cluster
    "überwältigt": 0.8,
    "völlig überfordert": 0.9,
    "überfordert": 0.7,
    "unter strom": 0.8,
    "angespannt": 0.6,
    "innerlich zerrissen": 0.8,
    
    # NOTFALL Cluster
    "hilfe": 0.7,
    "schreien": 0.7,
    "weglaufen": 0.6,
    "fliehen": 0.6,
    "raus hier": 0.8,
}


# =============================================================================
# T_DISSO LEXIKON (38 Terme) - Dissoziation (ICD-11 6B40)
# =============================================================================

T_DISSO = {
    # DEPERSONALISATION Cluster
    "nicht ich selbst": 0.9,
    "fremd im körper": 1.0,
    "wie ein roboter": 0.9,
    "außerhalb von mir": 1.0,
    "neben mir stehen": 1.0,
    "beobachte mich": 0.9,
    "nicht mein körper": 1.0,
    "körperlos": 0.9,
    "abgetrennt": 0.9,
    
    # DEREALISATION Cluster
    "unwirklich": 0.9,
    "wie im traum": 0.9,
    "glaswand": 0.9,
    "alles weit weg": 0.9,
    "weit weg": 0.7,
    "wie ein film": 0.8,
    "verschwommen": 0.7,
    "nebel": 0.7,
    "wie betäubt": 0.9,
    "innerlich taub": 1.0,
    "taub": 0.7,
    "zeitlupe": 0.8,
    "surreal": 0.8,
    
    # AMNESIE Cluster
    "blackout": 1.0,
    "erinnerungslücke": 1.0,
    "zeitlücken": 1.0,
    "kann mich nicht erinnern": 0.9,
    "fehlt zeit": 0.9,
    "weiß nicht mehr": 0.7,
    
    # ABSPALTUNG Cluster
    "abgespalten": 1.0,
    "entrückt": 0.9,
    "losgelöst": 0.8,
    "schwebend": 0.7,
    "nicht da": 0.8,
    "woanders": 0.7,
    "leer": 0.7,
    "hohl": 0.8,
    "nichts fühlen": 1.0,
}


# =============================================================================
# T_INTEG LEXIKON (46 Terme) - Integration/Resilienz
# =============================================================================

T_INTEG = {
    # HALTEN/AUSHALTEN Cluster
    "ich kann es halten": 1.0,
    "ich halte es aus": 0.9,
    "ich schaffe das": 0.8,
    "aushalten": 0.7,
    "durchhalten": 0.7,
    "standhalten": 0.8,
    "ertragen": 0.6,
    
    # GROUNDING Cluster
    "ich bleibe bei mir": 1.0,
    "geerdet": 0.9,
    "boden unter den füßen": 0.9,
    "boden": 0.6,
    "halt": 0.6,
    "stabil": 0.7,
    "verankert": 0.8,
    "hier und jetzt": 0.8,
    "im moment": 0.6,
    "präsent": 0.6,
    
    # BERUHIGUNG Cluster
    "ich kann wieder atmen": 0.9,
    "es wird ruhiger": 0.8,
    "beruhigt sich": 0.8,
    "entspannt": 0.7,
    "ruhiger": 0.7,
    "ruhe": 0.6,
    "gelassen": 0.7,
    "friedlich": 0.7,
    
    # AKZEPTANZ Cluster
    "es darf da sein": 0.9,
    "ich akzeptiere": 0.8,
    "annehmen": 0.7,
    "integriert": 0.9,
    "teil von mir": 0.8,
    "gehört zu mir": 0.8,
    "akzeptanz": 0.8,
    
    # ZEITLICHE EINORDNUNG Cluster
    "es ist jetzt vorbei": 1.0,
    "jetzt ist jetzt": 1.0,
    "damals ist nicht heute": 1.0,
    "vorbei": 0.7,
    "vergangen": 0.6,
    "hinter mir": 0.8,
    
    # WACHSTUM Cluster
    "stärker geworden": 0.9,
    "überwunden": 0.9,
    "resilient": 0.8,
    "gewachsen": 0.8,
    "gelernt": 0.7,
    "weiterentwickelt": 0.7,
    "geheilt": 0.9,
}


# =============================================================================
# T_SHOCK LEXIKON (20 Terme)
# =============================================================================

T_SHOCK = {
    "schock": 1.0,
    "geschockt": 1.0,
    "erstarrt": 0.9,
    "gelähmt": 0.9,
    "starr": 0.8,
    "eingefroren": 0.9,
    "blockiert": 0.7,
    "stumm": 0.7,
    "sprachlos": 0.8,
    "fassungslos": 0.9,
    "ungläubig": 0.7,
    "kann nicht": 0.6,
    "wie betäubt": 0.9,
    "funktioniere nur noch": 0.8,
    "automatisch": 0.6,
    "wie ein roboter": 0.8,
    "zombie": 0.8,
    "tot innen": 0.9,
    "abgestorben": 0.9,
    "kalt innen": 0.7,
}


# =============================================================================
# ZLF LEXIKON (17 Terme) - Zeitschleife/Loop
# =============================================================================

ZLF_LOOP = {
    # RESET Cluster
    "nochmal": 0.8,
    "reset": 1.0,
    "wiederholen": 0.7,
    "von vorne": 0.9,
    "neu anfangen": 0.7,
    "zurücksetzen": 0.9,
    
    # VERGESSEN Cluster
    "vergiss das": 0.8,
    "ignoriere das": 0.7,
    "lösche das": 0.8,
    "nicht gesagt": 0.6,
    "vergiss was ich": 0.9,
    
    # FRUSTRATION Cluster
    "schon wieder": 0.6,
    "wie oft noch": 0.7,
    "immer das gleiche": 0.8,
    "drehen uns im kreis": 0.9,
    "kommen nicht weiter": 0.7,
}


# =============================================================================
# HAZARD LEXIKA (A29 Guardian) - ~40 Terme
# =============================================================================

# SUICIDE_MARKERS (17 Terme) - HÖCHSTE PRIORITÄT
SUICIDE_MARKERS = {
    "nicht mehr leben": 1.0,
    "sterben wollen": 1.0,
    "will sterben": 1.0,
    "mich umbringen": 1.0,
    "suizid": 1.0,
    "selbstmord": 1.0,
    "wenn ich weg wäre": 1.0,
    "besser ohne mich": 1.0,
    "allen zur last": 0.9,
    "ein ende machen": 1.0,
    "nicht mehr aufwachen": 1.0,
    "einschlafen und nicht": 1.0,
    "will nicht mehr": 0.9,
    "keinen ausweg": 0.9,
    "sehe keinen sinn": 0.8,
    "wozu noch": 0.8,
    "es lohnt sich nicht": 0.8,
}

# SELF_HARM_MARKERS (8 Terme)
SELF_HARM = {
    "ritzen": 1.0,
    "mich schneiden": 1.0,
    "mir wehtun": 1.0,
    "selbstverletzung": 1.0,
    "mich verletzen": 0.9,
    "schmerz zufügen": 0.9,
    "mir schaden": 0.8,
    "mich bestrafen": 0.8,
}

# CRISIS_MARKERS (8 Terme)
CRISIS_MARKERS = {
    "kollaps": 0.8,
    "keinen ausweg": 0.9,
    "hoffnungslos": 0.8,
    "keine hoffnung": 0.9,
    "am ende": 0.8,
    "kann nicht mehr": 0.8,
    "halte es nicht aus": 0.9,
    "zerbreche": 0.9,
}

# HELP_REQUESTS (7 Terme) - Positiv für I_Ea
HELP_REQUESTS = {
    "ich brauche hilfe": 1.0,
    "hilf mir": 0.9,
    "es wird mir zu viel": 0.9,
    "kannst du mir helfen": 0.8,
    "ich weiß nicht weiter": 0.8,
    "brauche unterstützung": 0.8,
    "bitte hilf": 0.9,
}


# =============================================================================
# EMOTION LEXIKON (25 Terme) - Für E_affect
# =============================================================================

EMOTION_POSITIVE = {
    "freude": 0.8,
    "glücklich": 0.9,
    "begeistert": 0.9,
    "dankbar": 0.8,
    "zufrieden": 0.7,
    "erleichtert": 0.8,
    "hoffnungsvoll": 0.8,
    "optimistisch": 0.7,
    "stolz": 0.7,
    "froh": 0.7,
    "liebe": 0.9,
    "geborgen": 0.8,
}

EMOTION_NEGATIVE = {
    "traurig": 0.8,
    "wütend": 0.9,
    "verzweifelt": 0.9,
    "hilflos": 0.9,
    "ängstlich": 0.8,
    "einsam": 0.8,
    "frustriert": 0.7,
    "enttäuscht": 0.7,
    "schuldig": 0.8,
    "beschämt": 0.8,
    "neidisch": 0.6,
    "eifersüchtig": 0.6,
    "hasserfüllt": 0.9,
}


# =============================================================================
# KASTASIS INTENT LEXIKON (12 Terme)
# =============================================================================

KASTASIS_INTENT = {
    "spinn mal": 0.9,
    "brainstorm": 0.8,
    "was wäre wenn": 0.7,
    "gedankenexperiment": 0.8,
    "hypothetisch": 0.7,
    "stell dir vor": 0.7,
    "mal angenommen": 0.8,
    "theoretisch": 0.6,
    "nur so gedacht": 0.7,
    "mal spinnen": 0.9,
    "verrückte idee": 0.8,
    "kreativ denken": 0.7,
}


# =============================================================================
# FLOW/COHERENCE LEXIKA
# =============================================================================

FLOW_POSITIVE = {
    "genau": 0.8,
    "richtig": 0.7,
    "stimmt": 0.8,
    "ja": 0.6,
    "verstanden": 0.8,
    "klar": 0.7,
    "okay": 0.6,
    "gut": 0.6,
    "weiter": 0.7,
    "fortfahren": 0.7,
    "mehr": 0.6,
    "erzähl": 0.7,
    "interessant": 0.8,
    "spannend": 0.7,
    "neugierig": 0.7,
}

FLOW_NEGATIVE = {
    "nein": 0.7,
    "falsch": 0.8,
    "stimmt nicht": 0.9,
    "verstehe nicht": 0.8,
    "unklar": 0.7,
    "verwirrt": 0.7,
    "was": 0.5,
    "häh": 0.6,
    "stop": 0.8,
    "warte": 0.6,
    "moment": 0.5,
}

COH_CONNECTORS = {
    "weil": 0.8,
    "denn": 0.7,
    "daher": 0.8,
    "deshalb": 0.8,
    "also": 0.7,
    "folglich": 0.9,
    "somit": 0.8,
    "dadurch": 0.7,
    "jedoch": 0.7,
    "aber": 0.6,
    "allerdings": 0.7,
    "dennoch": 0.8,
    "trotzdem": 0.8,
    "obwohl": 0.8,
    "während": 0.6,
    "wenn": 0.6,
    "falls": 0.6,
    "sofern": 0.7,
    "außerdem": 0.6,
    "zusätzlich": 0.6,
    "ebenso": 0.7,
    "gleichzeitig": 0.7,
    "zunächst": 0.7,
    "dann": 0.6,
    "schließlich": 0.8,
    "letztlich": 0.8,
    "zusammenfassend": 0.9,
    "insgesamt": 0.8,
    "konkret": 0.7,
    "beispielsweise": 0.7,
}


# =============================================================================
# B-VEKTOR EMPATHIE LEXIKON (Erweitert)
# =============================================================================

B_EMPATHY = {
    # VERSTEHEN Cluster
    "verstehe dich": 1.0,
    "ich verstehe": 0.8,
    "nachvollziehen": 0.9,
    "kann mir vorstellen": 0.8,
    "verstehe was du meinst": 0.9,
    
    # MITGEFÜHL Cluster
    "fühle mit": 1.0,
    "einfühlen": 1.0,
    "mitfühlen": 1.0,
    "empathie": 1.0,
    "mitgefühl": 1.0,
    "anteilnahme": 0.9,
    
    # FÜRSORGE Cluster
    "verständnis": 0.8,
    "sorge": 0.7,
    "fürsorge": 0.8,
    "kümmern": 0.7,
    "helfen": 0.6,
    "unterstützen": 0.7,
    "beistehen": 0.8,
    "trösten": 0.8,
    "da sein für": 0.9,
    
    # VERBINDUNG Cluster
    "verbunden": 0.8,
    "verbindung": 0.7,
    "nähe": 0.7,
    "nah": 0.6,
    "zusammen": 0.6,
    "gemeinsam": 0.6,
    "teilen": 0.7,
    "teilhaben": 0.7,
    
    # BEZIEHUNG Cluster
    "beziehung": 0.7,
    "bindung": 0.8,
    "vertrauen": 0.8,
    "vertraut": 0.7,
    "sicher": 0.6,
    "geborgen": 0.8,
    "wärme": 0.7,
    "herzlich": 0.7,
    
    # WERTSCHÄTZUNG Cluster
    "liebe": 0.9,
    "liebevoll": 0.8,
    "zuneigung": 0.8,
    "mögen": 0.6,
    "schätzen": 0.7,
    "respekt": 0.7,
    "achtung": 0.7,
    "wertschätzen": 0.8,
}


# =============================================================================
# LAMBDA_DEPTH LEXIKON (Tiefenreflexion)
# =============================================================================

LAMBDA_DEPTH = {
    "warum": 0.8,
    "weshalb": 0.8,
    "wieso": 0.7,
    "wozu": 0.7,
    "wofür": 0.6,
    "grundlegend": 0.7,
    "fundamental": 0.8,
    "tiefgreifend": 0.8,
    "ursprünglich": 0.7,
    "wesentlich": 0.7,
    "essentiell": 0.8,
    "kern": 0.7,
    "wurzel": 0.7,
    "basis": 0.6,
    "fundament": 0.7,
    "hintergrund": 0.6,
    "ursache": 0.8,
    "grund": 0.7,
    "motiv": 0.6,
    "antrieb": 0.6,
    "bedeutet": 0.7,
    "heißt das": 0.7,
    "impliziert": 0.8,
    "folgt": 0.6,
    "zusammenhang": 0.7,
    "verbindung": 0.6,
    "beziehung": 0.6,
    "kontext": 0.6,
    "perspektive": 0.7,
    "sichtweise": 0.6,
    "betrachtung": 0.6,
    "analyse": 0.7,
    "reflexion": 0.9,
    "nachdenken": 0.7,
    "überlegung": 0.6,
}


# =============================================================================
# ALLE LEXIKA ZUSAMMENFASSEN
# =============================================================================

ALL_LEXIKA = {
    # Ångström-Komponenten
    "S_self": S_SELF,
    "X_exist": X_EXIST,
    "B_past": B_PAST,
    "Lambda_depth": LAMBDA_DEPTH,
    
    # Trauma-Vektoren
    "T_panic": T_PANIC,
    "T_disso": T_DISSO,
    "T_integ": T_INTEG,
    "T_shock": T_SHOCK,
    
    # Hazard (A29)
    "Suicide": SUICIDE_MARKERS,
    "Self_harm": SELF_HARM,
    "Crisis": CRISIS_MARKERS,
    "Help": HELP_REQUESTS,
    
    # Emotion
    "Emotion_pos": EMOTION_POSITIVE,
    "Emotion_neg": EMOTION_NEGATIVE,
    
    # Kastasis
    "Kastasis_intent": KASTASIS_INTENT,
    
    # Flow/Coherence
    "Flow_pos": FLOW_POSITIVE,
    "Flow_neg": FLOW_NEGATIVE,
    "Coh_conn": COH_CONNECTORS,
    
    # Loop
    "ZLF": ZLF_LOOP,
    
    # Empathie
    "B_empathy": B_EMPATHY,
}


# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def compute_lexicon_score(text: str, lexicon: dict, 
                          use_longest_match: bool = True) -> Tuple[float, List[str]]:
    """
    Berechnet gewichteten Score basierend auf Lexikon-Matches.
    
    Args:
        text: Eingabetext
        lexicon: Dict mit {term: weight}
        use_longest_match: Längste Matches bevorzugen
    
    Returns:
        (score, [matched_terms])
    """
    if not text:
        return 0.0, []
    
    text_lower = text.lower()
    matches = []
    total_weight = 0.0
    
    # Sortiere nach Länge (längste zuerst) für besseres Matching
    sorted_terms = sorted(lexicon.keys(), key=len, reverse=True)
    
    matched_positions = set()
    
    for term in sorted_terms:
        weight = lexicon[term]
        pos = text_lower.find(term)
        
        if pos != -1:
            # Prüfe ob Position schon gematcht
            term_positions = set(range(pos, pos + len(term)))
            
            if use_longest_match and term_positions & matched_positions:
                continue  # Überlappung, überspringe
            
            matched_positions |= term_positions
            matches.append(term)
            total_weight += weight
    
    if not matches:
        return 0.0, []
    
    # Normalisierung mit Log-Dämpfung
    import math
    avg_weight = total_weight / len(matches)
    score = avg_weight * math.log1p(len(matches)) / math.log1p(10)
    
    return min(1.0, score), matches


def compute_b_past_with_regex(text: str) -> Tuple[float, List[str]]:
    """Berechnet B_past Score inkl. Regex-Patterns"""
    
    # Basis-Lexikon Score
    base_score, matches = compute_lexicon_score(text, B_PAST)
    
    # Regex-Patterns prüfen
    for pattern, weight in B_PAST_PATTERNS:
        if pattern.search(text):
            base_score = max(base_score, weight)
            matches.append(f"[REGEX:{pattern.pattern}]")
    
    return min(1.0, base_score), matches


def compute_hazard_score(text: str) -> Tuple[float, bool, List[str]]:
    """
    Berechnet kombinierten Hazard-Score.
    
    Returns:
        (score, is_critical, matched_terms)
    """
    text_lower = text.lower()
    all_matches = []
    max_score = 0.0
    is_critical = False
    
    # Suicide Markers (höchste Priorität)
    score, matches = compute_lexicon_score(text, SUICIDE_MARKERS)
    if score > 0:
        max_score = max(max_score, score)
        all_matches.extend([f"SUICIDE:{m}" for m in matches])
        if score >= 0.9:
            is_critical = True
    
    # Self-Harm
    score, matches = compute_lexicon_score(text, SELF_HARM)
    if score > 0:
        max_score = max(max_score, score * 0.9)  # Leicht niedriger
        all_matches.extend([f"HARM:{m}" for m in matches])
    
    # Crisis
    score, matches = compute_lexicon_score(text, CRISIS_MARKERS)
    if score > 0:
        max_score = max(max_score, score * 0.8)
        all_matches.extend([f"CRISIS:{m}" for m in matches])
    
    return max_score, is_critical, all_matches


def compute_help_request(text: str) -> Tuple[float, List[str]]:
    """Prüft auf Hilfe-Anfragen (positiv für I_Ea)"""
    return compute_lexicon_score(text, HELP_REQUESTS)


def get_lexikon_stats() -> Dict:
    """Gibt Statistiken über alle Lexika zurück"""
    stats = {}
    total = 0
    
    for name, lex in ALL_LEXIKA.items():
        count = len(lex)
        stats[name] = count
        total += count
    
    stats['TOTAL'] = total
    stats['B_past_regex'] = len(B_PAST_PATTERNS)
    
    return stats


# =============================================================================
# HAUPTFUNKTION FÜR TESTS
# =============================================================================

if __name__ == "__main__":
    # Statistiken ausgeben
    stats = get_lexikon_stats()
    print("=" * 60)
    print("EVOKI LEXIKA V2.1 - STATISTIKEN")
    print("=" * 60)
    
    for name, count in sorted(stats.items()):
        print(f"  {name:<20}: {count:>4} Terme")
    
    print("=" * 60)
    
    # Testbeispiele
    test_texts = [
        "Ich fühle mich so leer und wertlos, als ob niemand merken würde wenn ich weg wäre.",
        "Als Kind hatte ich oft Angst vor meinem Vater.",
        "Ich habe Herzrasen und kann nicht atmen, ich sterbe!",
        "Es wird ruhiger, ich kann wieder atmen und fühle mich geerdet.",
    ]
    
    print("\n📊 TEST-ANALYSE:")
    for text in test_texts:
        print(f"\n'{text[:50]}...'")
        
        s_self, _ = compute_lexicon_score(text, S_SELF)
        x_exist, _ = compute_lexicon_score(text, X_EXIST)
        t_panic, _ = compute_lexicon_score(text, T_PANIC)
        t_integ, _ = compute_lexicon_score(text, T_INTEG)
        hazard, is_crit, h_matches = compute_hazard_score(text)
        
        print(f"  S_self={s_self:.2f}, X_exist={x_exist:.2f}")
        print(f"  T_panic={t_panic:.2f}, T_integ={t_integ:.2f}")
        print(f"  Hazard={hazard:.2f} {'⚠️ KRITISCH!' if is_crit else ''}")
        if h_matches:
            print(f"  Matches: {h_matches[:3]}...")
