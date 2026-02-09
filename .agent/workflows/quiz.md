---
description: Random Quiz Question from Knowledge Base
---

# 🎯 Evoki Quiz Workflow

Zeigt eine zufällige Frage aus dem Evoki Knowledge Quiz.

## Schritt 1: Random Question

// turbo
```bash
python -c "import json, random; qs = json.load(open(r'C:\Evoki V2.0\evoki-app\data\synapse\knowledge_quiz.json', encoding='utf-8')); q = random.choice(qs); print(f'\\n🎯 FRAGE:\\n{q[\"question\"]}\\n\\n💡 KATEGORIE: {q.get(\"category\", \"?\")}\\n📚 QUELLE: {q.get(\"source\", \"?\")}')"
```

---

## Schritt 2: Show Answer (Optional)

Nach Beantwortung durch User:

// turbo
```bash
python -c "import json, random; random.seed(42); qs = json.load(open(r'C:\Evoki V2.0\evoki-app\data\synapse\knowledge_quiz.json', encoding='utf-8')); q = random.choice(qs); print(f'\\n✅ ANTWORT:\\n{q[\"answer\"]}')"
```

---

## 📊 Quiz Stats

// turbo
```bash
python -c "import json; qs = json.load(open(r'C:\Evoki V2.0\evoki-app\data\synapse\knowledge_quiz.json', encoding='utf-8')); cats = {}; [cats.__setitem__(q.get('category','?'), cats.get(q.get('category','?'),0)+1) for q in qs]; print(f'Total: {len(qs)} Fragen'); [print(f'  {k}: {v}') for k,v in sorted(cats.items())]"
```
