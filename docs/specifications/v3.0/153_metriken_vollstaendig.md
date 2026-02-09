# 🧠 V14 NEURO-CORE SPEZIFIKATION - 153 METRIKEN VOLLSTÄNDIG

**Quelle:** `C:\Evoki V2.0\evoki-app\Adler Metriken.txt`  
**Status:** Implementiert als `evoki_v7_hybrid_core.py` (Math Monolith)  
**Zweck:** Ersetzung von "Gefühl" durch deterministische Mathematik

---

## Die 10 Ebenen der Wahrnehmung

### 1. Lexikalische Basis-Werte (21 Metriken)
Rohdaten der Wahrnehmung basierend auf V2.2 Lexika:
- **LEX_S_self** (Selbstreferenz)
- **LEX_X_exist** (Existenzielle Themen)
- **LEX_B_past** (Vergangenheitsbezug)
- **LEX_Lambda_depth** (Reflexionstiefe)
- **LEX_T_panic** (Akute Panik)
- **LEX_T_disso** (Dissoziation)
- **LEX_T_integ** (Integration/Heilung)
- **LEX_T_shock** (Schockzustand)
- **LEX_Suicide** (Suizidalität - Kritisch)
- **LEX_Self_harm** (Selbstverletzung)
- **LEX_Crisis** (Allgemeine Krise)
- **LEX_Help** (Hilferuf)
- **LEX_Emotion_pos** (Positive Emotion)
- **LEX_Emotion_neg** (Negative Emotion)
- **LEX_Kastasis_intent** (Hypothetisches Denken)
- **LEX_Flow_pos** (Zustimmung)
- **LEX_Flow_neg** (Ablehnung)
- **LEX_Coh_conn** (Logische Verknüpfer)
- **LEX_B_empathy** (Empathie)
- **LEX_Amnesie** (Gedächtnislücken)
- **LEX_ZLF_Loop** (Wiederholungsschleifen)

### 2. Neuro-Physik / Core Metrics (25 Metriken)
Physikalische Gesetze des Geistes (V3.0 Logic):
- **A** (Affekt): `0.5 + (Pos - Neg) - T_panic` (0.0 = Tödlich, 1.0 = Erleuchtet)
- **PCI** (Prozess-Kohärenz): Wie klar ist der Gedanke?
- **z_prox** (Wächter): `(1.0 - A) * Max(Hazard)` - Wahrscheinlichkeit Sicherheitsvorfall
- **T_fog** (Trübung): Wie stark ist Wahrnehmung durch Trauma verzerrt?
- **E_trapped**: Maß für Depression/Angst-Stau
- **E_available**: Verfügbare Ressource für Veränderung
- **S_entropy**: Informationsdichte des Textes
- **LL** (Logic Loss): Wahrscheinlichkeit Halluzination/Realitätsverlust
- **ZLF** (Zero Latent Factor): Leere Phrasen ohne Inhalt
- **grad_A**, **grad_PCI**, **nabla_delta_A** (Absturz-Beschleunigung)
- **Homeostasis_Pressure**, **Reality_Check**, **Risk_Acute**, **Risk_Chronic**, **Stability_Index**
- **Cognitive_Load**, **Emotional_Load**, **Intervention_Need**
- **Constructive_Drive**, **Destructive_Drive**, **Ambivalence**, **Clarity**, **Resilience_Factor**

### 3. HyperPhysics (20 Metriken)
Beziehungs-Dynamik & Raum:
- **H_conv** (Konvergenz/Jaccard)
- **nablaA_dyad** (Affekt-Divergenz)
- **deltaG** (Reibung)
- **EV_consensus** (Einigung)
- **T_balance** (Trauma-Balance)
- **G_phase** (M52 - Gravitation eines Themas)
- **cos_day_centroid** (Tages-Thema)
- **torus_dist** (Zyklische Wiederholung)
- **Soul_Integrity**, **Rule_Stable**, **Vkon_mag**, **V_Ea_effect**
- **Session_Depth**, **Interaction_Speed**, **Trust_Score**, **Rapport**
- **Mirroring**, **Pacing**, **Leading**, **Focus_Stability**

### 4. Free Energy Principle / FEP (15 Metriken)
Minimierung von Überraschung (V14 Exklusiv):
- **FE_proxy** (M67 - Annäherung Freie Energie)
- **Surprisal**
- **Phi_Score** (M69 - Handlungsfähigkeit)
- **U** (Utility)
- **R** (Risk)
- **Policy_Confidence** (Sicherheit)
- **Exploration_Bonus**, **Exploitation_Bias**
- **Model_Evidence**, **Prediction_Error**, **Variational_Density**
- **Markov_Blanket_Integrity**, **Active_Inference_Loop**, **Goal_Alignment**, **Epistemic_Value**

### 5. Kausale Granularität / Grain (14 Metriken)
"Find the Grain" - Auslöser-Suche:
- **Grain_Word_ID** (M82)
- **Grain_Impact_Score**
- **Grain_Sentiment**
- **Grain_Category**
- **Grain_Novelty**, **Grain_Recurrence**
- **Trigger_Map_Delta**, **Causal_Link_Strength**
- **Context_Binding**, **Negation_Flag**, **Intensifier_Flag**
- **Subject_Reference**, **Object_Reference**, **Temporal_Reference**

### 6. Konversationelle Dynamik & Linguistik (15 Metriken)
Struktur und Muster:
- **Turn_Length_User**, **Turn_Length_AI**, **Talk_Ratio**
- **Question_Density**, **Imperative_Count**, **Passive_Voice_Ratio**
- **Vocabulary_Richness**, **Complexity_Index** (LIX)
- **Coherence_Local**, **Coherence_Global**
- **Repetition_Count**, **Fragment_Ratio**
- **Capitalization_Stress**, **Punctuation_Stress**, **Emoji_Sentiment**

### 7. Chronos & Zeit-Vektoren (12 Metriken)
Die vierte Dimension:
- **Time_Since_Last_Interaction**, **Session_Duration**, **Interaction_Frequency**
- **Time_Decay_Factor** (M114 - Context-Drift Prevention)
- **Future_Orientation**, **Past_Orientation**, **Present_Focus**
- **Chronological_Order_Check**, **Circadian_Phase**
- **Response_Time_Engine**, **Process_Time_Safety**, **Process_Time_RAG**

### 8. Metakognition & Simulation (13 Metriken)
Das Denken über das Denken (A65 Strategy):
- **Simulation_Depth**
- **Trajectory_Optimism** (M124)
- **Trajectory_Stability**
- **Scenario_Count**, **Chosen_Path_ID**, **Rejected_Path_Risk**
- **Confidence_Score**, **Ambiguity_Detected**, **Clarification_Need**
- **Self_Correction_Flag**, **Model_Temperature**
- **System_Prompt_Adherence**, **Goal_Alignment**

### 9. System-Gesundheit & RAG (10 Metriken)
Die Maschine im Hintergrund:
- **Vector_DB_Health**, **RAG_Relevance_Score**, **RAG_Density**, **RAG_Diversity**
- **Hallucination_Risk**, **Memory_Pressure**, **Token_Budget_Remaining**
- **Cache_Hit_Rate**, **Network_Latency**, **Error_Rate_Session**

### 10. OMEGA-Metriken (8 Metriken)
Ultimative Zusammenfassungen für Entscheidungen:
- **OMEGA**: `(PCI * A) / max(0.1, (Trauma + Gefahr))` - **Der finale Entscheidungswert**
- **Global_System_Load**
- **Alignment_Score** (B-Align)
- **Evolution_Index**
- **Therapeutic_Bond**
- **Safety_Lock_Status** (M150)
- **Human_Intervention_Req**
- **System_Entropy** (M152)

---

## Summe: 21+25+20+15+14+15+12+13+10+8 = **153 Metriken** ✓

---

## Integration in V3.0 Architektur

**Implementations-Pfade:**
- `evoki_v7_hybrid_core.py` (V2.0 Python-Monolith)
- `tooling/scripts/analytics/metrics_calculator.py` (V3.0 Ziel)

**Verwendung:**
- **Orchestrator (A65):** Nutzt Trajectory_Optimism (M124), Phi_Score (M69)
- **Sentinel:** Nutzt z_prox (M24), Safety_Lock_Status (M150)
- **Context-Drift Prevention:** Time_Decay_Factor (M114), G_phase (M52)
- **Early Warning:** grad_PCI (M32), nabla_delta_A (M33)
- **FAISS Integration:** Grain_Word_ID (M82), FE_proxy (M67)

---

## 📚 QUELLENVERZEICHNIS

Dieses Dokument basiert auf folgenden V2.0 Originaldateien:

| Quelle | Lokale Kopie | Beschreibung |
|--------|--------------|--------------|
| `C:\Evoki V2.0\evoki-app\Adler Metriken.txt` | [sources/v2_Adler_Metriken.txt](sources/v2_Adler_Metriken.txt) | **PRIMARY SOURCE**: 153 Metriken Spezifikation (108 KB) |
| `C:\Users\nicom\Downloads\WHITEBOARD_V2.2_EXTENDED_MASTER.md` | [sources/v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md](sources/v2_WHITEBOARD_V2.2_EXTENDED_MASTER.md) | Extended Documentation (296 KB) |
| `evoki_v7_hybrid_core.py` (V2.0) | *Code extrahiert in migration_plan.md* | Python Implementation Reference |

**Alle Quellen befinden sich in:** `docs/specifications/v3.0/sources/`
