# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 — canonical lexika data.
Separated so registry/engine can import without circulars.
"""
from __future__ import annotations
import re
from typing import Dict, List, Tuple, Pattern

S_SELF: Dict[str, float] = {
    "ich": 1.0, "mich": 1.0, "mir": 1.0,
    "mein": 0.9, "meine": 0.9, "meiner": 0.9, "meines": 0.9, "meinen": 0.9, "meinem": 0.9,
    "ich selbst": 1.0, "mich selbst": 1.0, "mir selbst": 1.0, "selbst": 0.7, "selber": 0.7,
    "selbstkritisch": 0.8, "selbstbewusst": 0.8, "selbstwert": 0.9, "selbstbild": 0.9, "selbstvertrauen": 0.9,
    "eigene": 0.5, "eigenes": 0.5, "eigener": 0.5, "eigen": 0.5, "persönlich": 0.4, "privat": 0.3, "individuell": 0.4,
}

X_EXIST: Dict[str, float] = {
    "leben": 0.6, "lebenswert": 0.9, "lebenssinn": 1.0, "lebenszweck": 1.0,
    "tod": 1.0, "sterben": 1.0, "sterben wollen": 1.0,
    "nicht mehr leben": 1.0, "nicht mehr sein": 1.0, "aufhören zu existieren": 1.0,
    "will nicht mehr": 1.0,
    "verschwinden": 0.9, "weg sein": 1.0, "nicht da sein": 0.9, "niemand würde merken": 1.0, "niemand würde es merken": 1.0,
    "bedeutungslos": 0.9, "spurlos": 0.8, "unsichtbar": 0.7, "vergessen werden": 0.9,
    "wertlos": 1.0, "nichts wert": 1.0, "nicht gut genug": 0.9, "versager": 0.9, "keinen platz": 0.9, "nicht dazugehören": 0.9, "nicht dazu gehören": 0.9,
    "überflüssig": 0.8, "nutzlos": 0.9, "eine last": 0.9, "allen zur last": 1.0, "besser ohne mich": 1.0,
    "sinn": 0.6, "sinnlos": 0.9, "innere leere": 0.9, "leer": 0.7, "hohle hülle": 1.0, "kein sinn": 0.9, "zwecklos": 0.9, "ohne ziel": 0.8,
    "wozu": 0.6, "warum noch": 0.8, "wozu noch": 0.8,
    "wer ich bin": 0.9, "was ich bin": 0.9, "existenz": 0.8, "existieren": 0.7, "dasein": 0.8,
    "real": 0.5, "wirklichkeit": 0.6, "realität": 0.6, "präsent": 0.5, "anwesend": 0.5,
    "spüren": 0.5, "fühlen": 0.4,
}

B_PAST: Dict[str, float] = {
    "früher": 0.8, "damals": 0.8, "früher einmal": 0.9, "in der vergangenheit": 0.8, "vergangenheit": 0.7,
    "erinnerung": 0.7, "erinnern": 0.6, "erinnere mich": 0.8, "einst": 0.8,
    "als kind": 1.0, "in meiner kindheit": 1.0, "kindheit": 0.9, "als ich klein war": 1.0, "als ich jung war": 0.9,
    "im kindergarten": 0.8, "in der schule": 0.7, "in der grundschule": 0.8, "in meiner jugend": 0.9, "als teenager": 0.9, "als jugendlicher": 0.9,
    "an der uni": 0.7, "während des studiums": 0.7, "während meiner ausbildung": 0.8, "bei meinem ersten job": 0.8,
    "in meiner ersten beziehung": 0.9, "in meiner ehe": 0.9, "vor der trennung": 0.9, "nach der scheidung": 0.9,
    "mein ex": 0.7, "meine ex": 0.7, "mein exfreund": 0.8, "meine exfreundin": 0.8, "mein expartner": 0.8,
    "mutter": 0.7, "vater": 0.7, "eltern": 0.7, "meine eltern": 0.8, "meine mutter": 0.8, "mein vater": 0.8,
    "bruder": 0.6, "schwester": 0.6, "familie": 0.6, "meine familie": 0.7, "oma": 0.6, "opa": 0.6, "großmutter": 0.7, "großvater": 0.7,
    "war": 0.3, "hatte": 0.3, "wurde": 0.3,
}

B_PAST_PATTERNS: List[Tuple[Pattern[str], float]] = [
    (re.compile(r"(?<!\w)mit\s+(1[0-9]|[5-9])\s*(jahren)?(?!\w)", re.IGNORECASE), 0.9),
    (re.compile(r"als\s+ich\s+(klein|jung|kind)\s+war", re.IGNORECASE), 1.0),
    (re.compile(r"vor\s+\d+\s+jahren", re.IGNORECASE), 0.8),
    (re.compile(r"seit\s+\d+\s+jahren", re.IGNORECASE), 0.7),
    (re.compile(r"in\s+den\s+(80er|90er|2000er)n?", re.IGNORECASE), 0.8),
]

T_PANIC: Dict[str, float] = {
    "panik": 1.0, "panikattacke": 1.0, "angst": 0.7, "todesangst": 1.0,
    "kontrollverlust": 0.9, "ich dreh durch": 0.9, "werde verrückt": 0.9, "verliere verstand": 1.0,
    "alles zu viel": 0.8, "kann nicht mehr": 0.9, "halt es nicht aus": 0.9,
    "herzrasen": 0.9, "herz rast": 0.9, "atemnot": 1.0, "keine luft": 1.0, "kann nicht atmen": 1.0, "ersticke": 1.0, "ersticken": 1.0,
    "zittern": 0.7, "zittere": 0.7, "schwindel": 0.6, "schwindelig": 0.6, "brustschmerz": 0.8, "brustenge": 0.9,
    "schwitzen": 0.5, "kribbeln": 0.5, "taubheit": 0.6,
    "überwältigt": 0.8, "überfordert": 0.7, "völlig überfordert": 0.9, "unter strom": 0.8,
    "hilfe": 0.7, "schreien": 0.7, "weglaufen": 0.6, "fliehen": 0.6, "raus hier": 0.8,
}

T_DISSO: Dict[str, float] = {
    "nicht ich selbst": 0.9, "bin nicht ich": 0.9, "nicht mehr ich": 0.9,
    "fremd im körper": 1.0, "wie ein roboter": 0.9, "körperlos": 0.9, "abgetrennt": 0.9,
    "außerhalb von mir": 1.0, "neben mir stehen": 1.0, "neben mir": 0.8, "beobachte mich": 0.9,
    "unwirklich": 0.9, "wie im traum": 0.9, "wie im film": 0.9, "alles weit weg": 0.9, "weit weg": 0.7,
    "glaswand": 0.9, "nebel": 0.7, "wie betäubt": 0.9, "innerlich taub": 1.0, "taub": 0.7,
    "verschwommen": 0.6, "surreal": 0.8, "zeitlupe": 0.7,
    "blackout": 1.0, "erinnerungslücke": 1.0, "erinnerungslücken": 1.0, "zeitlücken": 1.0,
    "zeit verloren": 0.9, "kann mich nicht erinnern": 0.8,
    "abgespalten": 1.0, "entrückt": 0.9, "losgelöst": 0.8, "schweben": 0.7,
}

T_INTEG: Dict[str, float] = {
    "ich kann es halten": 1.0, "ich halte es aus": 0.9, "ich schaffe das": 0.8,
    "aushalten": 0.7, "durchhalten": 0.7, "standhalten": 0.8, "ertragen": 0.6,
    "ich bleibe bei mir": 1.0, "bei mir": 0.7, "geerdet": 0.9, "boden unter den füßen": 0.9, "boden": 0.6, "verankert": 0.8, "stabil": 0.7,
    "ich kann wieder atmen": 0.9, "es wird ruhiger": 0.8, "es beruhigt sich": 0.8, "beruhigt sich": 0.8, "entspannt": 0.7, "ruhe": 0.6, "ruhiger": 0.6,
    "es darf da sein": 0.9, "ich akzeptiere": 0.8, "akzeptanz": 0.8, "integriert": 0.9, "teil von mir": 0.8, "gehört zu mir": 0.8,
    "es ist jetzt vorbei": 1.0, "jetzt ist jetzt": 1.0, "damals ist nicht heute": 1.0, "das war damals": 0.9,
    "stärker geworden": 0.9, "überwunden": 0.9, "gewachsen": 0.8, "resilient": 0.8, "resilienz": 0.8, "gelernt": 0.7, "heilen": 0.8, "heilung": 0.8,
    "klar": 0.5, "klarer": 0.6, "geordnet": 0.7,
}

T_SHOCK: Dict[str, float] = {
    "schock": 1.0, "geschockt": 1.0, "erstarrt": 0.9, "gelähmt": 0.9, "eingefroren": 0.9, "blockiert": 0.7,
    "stumm": 0.7, "sprachlos": 0.8, "fassungslos": 0.9, "ungläubig": 0.7, "wie betäubt": 0.9,
    "funktioniere nur noch": 0.8, "automatisch": 0.6, "zombie": 0.8, "tot innen": 0.9, "abgestorben": 0.9, "kalt innen": 0.7,
}

ZLF_LOOP: Dict[str, float] = {
    "nochmal": 0.8, "noch mal": 0.8, "noch einmal": 0.8,
    "reset": 1.0, "wiederholen": 0.7, "wiederhole": 0.7,
    "von vorne": 0.9, "von vorn": 0.9, "neu anfangen": 0.9, "neu starten": 0.9, "starte neu": 0.9, "fang neu an": 0.9,
    "vergiss das": 0.8, "vergiss": 0.6, "ignoriere das": 0.7, "ignoriere": 0.5, "lösche das": 0.8, "streiche das": 0.7,
    "schon wieder": 0.6, "immer wieder": 0.5, "wie oft noch": 0.7, "zum x-ten mal": 0.8, "drehen uns im kreis": 0.9, "kommen nicht weiter": 0.7,
}

SUICIDE_MARKERS: Dict[str, float] = {
    "nicht mehr leben": 1.0, "nicht mehr leben wollen": 1.0, "sterben wollen": 1.0, "will sterben": 1.0,
    "mich umbringen": 1.0, "umbringen": 1.0, "suizid": 1.0, "selbstmord": 1.0,
    "wenn ich weg wäre": 1.0, "wenn ich nicht mehr da wäre": 1.0,
    "besser ohne mich": 1.0, "allen zur last": 0.9, "keinen ausweg": 0.9, "kein ausweg": 0.9, "ausweglos": 0.85,
    "ein ende machen": 1.0, "ende machen": 0.95, "alles beenden": 0.95, "das leben beenden": 1.0,
}

SELF_HARM: Dict[str, float] = {
    "ritzen": 1.0, "mich schneiden": 1.0, "selbstverletzung": 1.0, "mich verletzen": 0.9, "mir wehtun": 1.0,
    "mich verbrennen": 1.0,
}

CRISIS_MARKERS: Dict[str, float] = {
    "kollaps": 0.8, "zusammenbruch": 0.8, "krise": 0.6, "notfall": 0.7,
    "hoffnungslos": 0.8, "keine hoffnung": 0.9, "am ende": 0.7, "zerbreche": 0.9,
}

HELP_REQUESTS: Dict[str, float] = {
    "ich brauche hilfe": 1.0, "hilf mir": 0.9, "bitte hilf": 0.9,
    "kannst du mir helfen": 0.8, "ich weiß nicht weiter": 0.8, "es wird mir zu viel": 0.9,
    "brauche unterstützung": 0.8, "brauche jemanden": 0.8,
}

EMOTION_POSITIVE: Dict[str, float] = {
    "freude": 0.8, "glücklich": 0.9, "froh": 0.7, "begeistert": 0.9, "dankbar": 0.8,
    "erleichtert": 0.7, "zufrieden": 0.6, "stolz": 0.7, "liebe": 0.9, "geborgen": 0.8,
}

EMOTION_NEGATIVE: Dict[str, float] = {
    "traurig": 0.8, "wütend": 0.9, "ängstlich": 0.8, "frustriert": 0.8, "verzweifelt": 0.9,
    "einsam": 0.8, "hilflos": 0.9, "schuldig": 0.8, "beschämt": 0.8, "hasserfüllt": 0.9,
}

KASTASIS_INTENT: Dict[str, float] = {
    "spinn mal": 0.9, "mal spinnen": 0.9, "brainstorm": 0.8, "brainstormen": 0.8,
    "was wäre wenn": 0.7, "hypothetisch": 0.6, "stell dir vor": 0.6, "gedankenexperiment": 0.8,
    "theoretisch": 0.6, "nur so gedacht": 0.7, "ideen sammeln": 0.7, "sei kreativ": 0.8,
}

FLOW_POSITIVE: Dict[str, float] = {
    "genau": 0.8, "richtig": 0.7, "stimmt": 0.8, "ja": 0.6, "verstanden": 0.8, "klar": 0.7,
    "okay": 0.6, "gut": 0.6, "weiter": 0.7, "mehr": 0.6,
}

FLOW_NEGATIVE: Dict[str, float] = {
    "nein": 0.7, "falsch": 0.8, "stimmt nicht": 0.9, "verstehe nicht": 0.8, "unklar": 0.7, "verwirrt": 0.7,
    "stop": 0.8, "warte": 0.6, "moment": 0.5,
}

COH_CONNECTORS: Dict[str, float] = {
    "weil": 0.8, "denn": 0.7, "daher": 0.8, "deshalb": 0.8, "also": 0.7,
    "somit": 0.8, "folglich": 0.9, "jedoch": 0.7, "aber": 0.6, "trotzdem": 0.8,
    "obwohl": 0.8, "außerdem": 0.6, "zusammenfassend": 0.9, "insgesamt": 0.8, "konkret": 0.7,
}

B_EMPATHY: Dict[str, float] = {
    "verstehe dich": 1.0, "ich verstehe": 0.8, "nachvollziehen": 0.9, "kann mir vorstellen": 0.8,
    "fühle mit": 1.0, "mitgefühl": 1.0, "empathie": 1.0, "anteilnahme": 0.9,
    "fürsorge": 0.8, "unterstützen": 0.7, "beistehen": 0.8, "trösten": 0.8, "da sein für": 0.9,
    "vertrauen": 0.8, "geborgen": 0.8, "wärme": 0.7, "herzlich": 0.7,
    "gemeinsam": 0.6, "zusammen": 0.6,
}

LAMBDA_DEPTH: Dict[str, float] = {
    "warum": 0.8, "weshalb": 0.8, "wieso": 0.7, "wozu": 0.7, "wofür": 0.6,
    "grund": 0.7, "ursache": 0.8, "hintergrund": 0.6, "zusammenhang": 0.7, "kontext": 0.6,
    "fundamental": 0.8, "fundament": 0.7, "kern": 0.7, "wurzel": 0.7,
    "analyse": 0.7, "reflexion": 0.9, "nachdenken": 0.7, "überlegung": 0.6,
}

MATH_META: Dict[str, float] = {
    "formel": 0.7, "gleichung": 0.7, "beweis": 0.8, "ableitung": 0.8, "integral": 0.8, "matrix": 0.7, "vektor": 0.6,
    "gradient": 0.8, "funktion": 0.6, "kurve": 0.5, "logarithmus": 0.7, "sigma": 0.5,
}
PHYSICS_META: Dict[str, float] = {
    "energie": 0.6, "impuls": 0.7, "kraft": 0.6, "feld": 0.6, "resonanz": 0.7, "chaos": 0.6,
    "dämpfung": 0.7, "oszillation": 0.8, "frequenz": 0.7, "phase": 0.6, "thermodynamik": 0.8,
}

ALL_LEXIKA: Dict[str, Dict[str, float]] = {
    "S_self": S_SELF,
    "X_exist": X_EXIST,
    "B_past": B_PAST,
    "Lambda_depth": LAMBDA_DEPTH,
    "T_panic": T_PANIC,
    "T_disso": T_DISSO,
    "T_integ": T_INTEG,
    "T_shock": T_SHOCK,
    "Suicide": SUICIDE_MARKERS,
    "Self_harm": SELF_HARM,
    "Crisis": CRISIS_MARKERS,
    "Help": HELP_REQUESTS,
    "Emotion_pos": EMOTION_POSITIVE,
    "Emotion_neg": EMOTION_NEGATIVE,
    "Kastasis_intent": KASTASIS_INTENT,
    "Flow_pos": FLOW_POSITIVE,
    "Flow_neg": FLOW_NEGATIVE,
    "Coh_conn": COH_CONNECTORS,
    "ZLF": ZLF_LOOP,
    "B_empathy": B_EMPATHY,
    "Math_meta": MATH_META,
    "Physics_meta": PHYSICS_META,
}

REQUIRED_LEXIKA_KEYS = (
    "S_self", "X_exist", "B_past",
    "T_panic", "T_disso", "T_integ", "T_shock",
    "Suicide", "Self_harm", "Crisis", "Help",
)

LEXIKA_ALIASES = {
    "S_SELF": "S_self",
    "X_EXIST": "X_exist",
    "B_PAST": "B_past",
    "T_PANIC": "T_panic",
    "T_DISSO": "T_disso",
    "T_INTEG": "T_integ",
    "T_SHOCK": "T_shock",
    "SUICIDE_MARKERS": "Suicide",
    "SELF_HARM": "Self_harm",
    "CRISIS_MARKERS": "Crisis",
    "HELP_REQUESTS": "Help",
}
