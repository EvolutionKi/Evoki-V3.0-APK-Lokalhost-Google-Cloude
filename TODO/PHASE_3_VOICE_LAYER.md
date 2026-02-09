# 📋 PHASE 3: DIE STIMME (LLM Integration)

**Dauer:** 1-2 Tage  
**Schwierigkeit:** ⭐⭐⭐ (Mittel)  
**Was:** Echtes Gemini/OpenAI LLM!

---

## 🎯 ZIEL

**KOMPLETT echter Flow:** Metriken → FAISS → Gates → **ECHTES LLM** → Gates

**Test:** "Wie geht es dir?" → Gemini antwortet mit W-P-F Kontext + Regelwerk V12!

---

## ✅ CHECKLISTE

### 1. LLM Router

```python
class LLMRouter:
    def call_gemini(context): ...
    def call_openai_fallback(context): ...
```

- [ ] Gemini API Integration
- [ ] OpenAI Fallback
- [ ] API-Key aus .env

### 2. Kontext-Builder

```python
def build_context(prompt, faiss_chunks, metrics):
    # Regelwerk V12 + W-P-F + Metriken
```

- [ ] System Message
- [ ] W-P-F Kontext
- [ ] Metriken-Summary

### 3. Token Streaming

SSE: `token` Event für jeden Token

- [ ] Token-by-Token Streaming
- [ ] Frontend zeigt live

### 4. Tests

- [ ] Gemini antwortet
- [ ] Kontext wird genutzt
- [ ] Fallback funktioniert

- [ ] PHASE 3 KOMPLETT

**Weiter:** `PHASE_4_UI_POLISH.md`
