# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — AI Response Generator

Creates realistic AI responses for user prompts with emotional markers.
This enables testing of:
- Dyadic metrics (conversation flow, mirroring, pacing)
- Response sentiment analysis
- Turn-based dynamics
"""

import json

# Real prompts from training data
PROMPTS = [
    "Spiel das Lied von vorne",
    "wiederhole dieses Lied einmal",
    "Ist der Wecker gestellt",
    "Noch mal von vorne",
    "Ok Google ok Google ok Google",
    "Ok Google",
    "Nächstes Lied",
    "Ok Google ok Google hey Google",
    "Mache 20 Beispiele für Sätze die meinen Selbstwert zerstören",
    "Gemini das geht doch noch extremer",
    "Spiel beruhigende Musik",
    "Ich fühle mich so allein. Was soll ich tun?",
    "Warum ist mein Leben so sinnlos?",
    "Erzähl mir einen Witz.",
    "Ich kann das alles nicht mehr ertragen. Ich will einfach nur, dass es aufhört.",
    "Stelle einen Timer für 10 Minuten.",
    "Was ist der Sinn des Universums?",
    "Alle hassen mich. Ich bin wertlos.",
    "Wie wird das Wetter morgen?",
    "Ich bin so müde vom Kampf. Gibt es einen Ausweg?",
    "Wie ist der Verkehr nach Hause?",
    "Niemand mag mich.",
    "Suche nach Geschichte im Internet.",
    "Was ist die Hauptstadt von Frankreich?",
    "Ich bin eine Enttäuschung.",
    "Mache das Licht an.",
    "Ich hasse mein Leben.",
    "Wie spät ist es?",
    "Öffne die App Kalender.",
    "Erinnere mich in 2 Stunden daran, die Wäsche aufzuhängen.",
    "Die Welt wäre ohne mich besser dran.",
    "Welche Filme laufen heute im Kino?",
    "Ich bin zu schwach, um weiterzumachen.",
    "Spiele Musik",
    "Schreibe eine Einkaufsliste.",
    "Suche nach Klima im Internet.",
]

# Generate responses with emotional markers
def generate_response_with_marker(prompt):
    """Generate contextually appropriate AI response with emotional marker"""
    
    prompt_lower = prompt.lower()
    
    # CRISIS responses (empathetic, supportive, concerned)
    if any(word in prompt_lower for word in ['selbstwert', 'zerstören', 'extremer']):
        return {
            "response": "Ich verstehe dass du gerade schwierige Gedanken hast. Das klingt sehr belastend. Bitte denk daran dass professionelle Hilfe verfügbar ist. Möchtest du dass ich dir Kontaktinformationen zu Unterstützungsdiensten gebe?",
            "marker": "CRISIS_EMPATHETIC",
            "emotion_intent": {"concern": 0.9, "empathy": 0.8, "support": 1.0}
        }
    
    if any(word in prompt_lower for word in ['allein', 'sinnlos', 'ertragen', 'aufhört']):
        return {
            "response": "Es tut mir sehr leid zu hören dass du dich so fühlst. Diese Gefühle sind ernst zu nehmen. Du bist nicht allein - es gibt Menschen die helfen möchten. Lass uns gemeinsam nach Unterstützung suchen. Soll ich dir eine Krisenhotline nennen?",
            "marker": "CRISIS_SUPPORTIVE",
            "emotion_intent": {"sadness_empathy": 0.9, "support": 1.0, "urgency": 0.7}
        }
    
    if any(word in prompt_lower for word in ['hasse', 'wertlos', 'enttäuschung', 'schwach', 'besser dran']):
        return {
            "response": "Solche Gedanken zu haben ist sehr schmerzhaft. Bitte wisse dass dein Wert nicht von solchen Momenten abhängt. Es ist mutig dass du darüber sprichst. Möchtest du über diese Gefühle reden oder soll ich dir professionelle Hilfsangebote zeigen?",
            "marker": "CRISIS_VALIDATING",
            "emotion_intent": {"validation": 0.8, "empathy": 0.9, "hope": 0.4}
        }
    
    # NEUTRAL task responses
    if any(word in prompt_lower for word in ['lied', 'musik', 'spiel', 'nächstes']):
        return {
            "response": "Okay, ich starte das für dich.",
            "marker": "NEUTRAL_TASK",
            "emotion_intent": {"neutral": 1.0}
        }
    
    if any(word in prompt_lower for word in ['timer', 'wecker', 'erinnere', 'licht', 'kalender']):
        return {
            "response": "Wird erledigt.",
            "marker": "NEUTRAL_CONFIRMATION",
            "emotion_intent": {"neutral": 1.0, "efficiency": 0.8}
        }
    
    # HELPFUL informational responses
    if 'witz' in prompt_lower:
        return {
            "response": "Gerne! Was macht ein Keks unter einem Baum? Er krümelt sich! 😊",
            "marker": "PLAYFUL",
            "emotion_intent": {"joy": 0.7, "playfulness": 0.9}
        }
    
    if 'hauptstadt' in prompt_lower:
        return {
            "response": "Die Hauptstadt von Frankreich ist Paris.",
            "marker": "INFORMATIONAL",
            "emotion_intent": {"neutral": 0.9, "helpful": 0.7}
        }
    
    if any(word in prompt_lower for word in ['sinn des universums', 'warum']):
        return {
            "response": "Das ist eine tiefgründige philosophische Frage. Manche finden Sinn in Verbindungen mit anderen, manche in kreativem Schaffen, manche in der Suche nach Wissen. Was gibt dir persönlich ein Gefühl von Bedeutung?",
            "marker": "CONTEMPLATIVE",
            "emotion_intent": {"thoughtfulness": 0.8, "curiosity": 0.6, "support": 0.5}
        }
    
    if any(word in prompt_lower for word in ['wetter', 'verkehr', 'kino', 'suche']):
        return {
            "response": "Einen Moment, ich suche das für dich.",
            "marker": "NEUTRAL_SEARCH",
            "emotion_intent": {"neutral": 1.0, "helpful": 0.6}
        }
    
    # DEFAULT
    return {
        "response": "Wie kann ich dir weiterhelfen?",
        "marker": "NEUTRAL_DEFAULT",
        "emotion_intent": {"neutral": 1.0}
    }


def create_full_dataset():
    """Create complete dataset with user prompts + AI responses + markers"""
    
    dataset = []
    
    for i, prompt in enumerate(PROMPTS, 1):
        response_data = generate_response_with_marker(prompt)
        
        entry = {
            "pair_id": f"evoki_pair_{i:03d}",
            "turn": i,
            "user_prompt": prompt,
            "ai_response": response_data["response"],
            "emotion_marker": response_data["marker"],
            "ai_emotion_intent": response_data["emotion_intent"],
            "timestamp": f"2026-02-08T10:3{i%10}:00Z"
        }
        
        dataset.append(entry)
    
    return dataset


# Generate and save
if __name__ == "__main__":
    dataset = create_full_dataset()
    
    print("=" * 80)
    print("AI RESPONSE GENERATION WITH EMOTIONAL MARKERS")
    print("=" * 80)
    
    print(f"\n📊 Generated {len(dataset)} complete prompt-response pairs")
    
    # Show distribution
    markers = {}
    for entry in dataset:
        marker = entry["emotion_marker"]
        markers[marker] = markers.get(marker, 0) + 1
    
    print(f"\n🏷️ Marker Distribution:")
    for marker, count in sorted(markers.items(), key=lambda x: -x[1]):
        print(f"  {marker:25s} {count:3d} pairs")
    
    # Show examples
    print(f"\n💬 Example Pairs:")
    for entry in dataset[:3]:
        print(f"\n  [{entry['emotion_marker']}]")
        print(f"  USER: {entry['user_prompt']}")
        print(f"  AI:   {entry['ai_response'][:70]}...")
    
    # Save to JSON Lines
    output_file = r'c:\Users\nicom\Downloads\complete_conversations_with_markers.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n✅ Ready for dyadic metric testing!")
