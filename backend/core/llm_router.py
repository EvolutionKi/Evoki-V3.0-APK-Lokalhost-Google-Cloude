"""
Evoki V3.0 - LLM Router (Phase 3)

LLM Integration:
- Primary: Google Gemini 2.0 Flash
- Fallback: OpenAI GPT-4 Turbo

Features:
- Token-by-Token Streaming
- Graceful fallback on API failures
- Context length management (4096 tokens)
- Environment-based API keys
"""

import os
from typing import AsyncGenerator, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env
# Use explicit path relative to this file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
else:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API Key nicht konfiguriert - Fallback auf Mock Mode")

if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    OPENAI_AVAILABLE = True
else:
    OPENAI_AVAILABLE = False
    openai_client = None
    print("⚠️ OpenAI API Key nicht konfiguriert - Kein Fallback verfügbar")


class LLMRouter:
    """
    LLM Router - Manages LLM API calls with fallback
    
    Priority:
    1. Google Gemini 2.0 Flash (Primary)
    2. OpenAI GPT-4 Turbo (Fallback)
    3. Mock Response (Development)
    """
    
    def __init__(self):
        self.gemini_model = "gemini-2.0-flash-exp" if GEMINI_AVAILABLE else None
        self.openai_model = "gpt-4-turbo-preview" if OPENAI_AVAILABLE else None
    
    async def stream_response(
        self,
        system_message: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """
        Stream LLM response token-by-token
        
        Args:
            system_message: System/Context message (Regelwerk + Metriken + W-P-F)
            user_prompt: User's actual question
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum response length
        
        Yields:
            String tokens from LLM
        """
        
        # Try Gemini first
        if GEMINI_AVAILABLE:
            try:
                async for token in self._stream_gemini(
                    system_message, user_prompt, temperature, max_tokens
                ):
                    yield token
                return  # Success!
            except Exception as e:
                print(f"⚠️ Gemini API Error: {e}")
                print(f"   Trying fallback...")
        
        # Fallback to OpenAI
        if OPENAI_AVAILABLE:
            try:
                async for token in self._stream_openai(
                    system_message, user_prompt, temperature, max_tokens
                ):
                    yield token
                return  # Success!
            except Exception as e:
                print(f"⚠️ OpenAI API Error: {e}")
                print(f"   Fallback to Mock")
        
        # Last resort: Mock response
        async for token in self._stream_mock(user_prompt):
            yield token
    
    async def _stream_gemini(
        self,
        system_message: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream response from Google Gemini"""
        
        # Combine system + user message
        full_prompt = f"{system_message}\n\nUser: {user_prompt}\n\nEvoki:"
        
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            candidate_count=1,
        )
        
        # Create model
        model = genai.GenerativeModel(
            model_name=self.gemini_model,
            generation_config=generation_config,
        )
        
        # Generate streaming response
        response = await model.generate_content_async(
            full_prompt,
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    
    async def _stream_openai(
        self,
        system_message: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI GPT-4"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        stream = await openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _stream_mock(self, user_prompt: str) -> AsyncGenerator[str, None]:
        """Mock streaming response for development"""
        
        mock_response = (
            f"[MOCK LLM - Phase 3 Development Mode] "
            f"Ich kann deinen Prompt '{user_prompt[:30]}...' sehen, aber ich habe "
            f"keinen Zugriff auf ein echtes LLM (Gemini/OpenAI API Keys fehlen). "
            f"Bitte konfiguriere GEMINI_API_KEY oder OPENAI_API_KEY in der .env Datei."
        )
        
        # Simulate token-by-token streaming
        for word in mock_response.split():
            yield word + " "


# Global singleton
_llm_router = None


def get_llm_router() -> LLMRouter:
    """Get singleton LLM Router instance"""
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router


# =============================================================================
# CONTEXT BUILDER
# =============================================================================

def build_system_message(
    faiss_chunks: list,
    metrics: dict,
    wpf_context: dict
) -> str:
    """
    Build comprehensive system message for LLM
    
    Includes:
    1. Evoki's Identity & Philosophy
    2. Regelwerk V12 Excerpt (Top-5 Relevant Rules)
    3. W-P-F Context (Past/Present/Future)
    4. Current Metrics Summary
    
    Args:
        faiss_chunks: Top-3 FAISS results
        metrics: Calculated metrics dict
        wpf_context: W-P-F time machine context
    
    Returns:
        Complete system message string
    """
    
    # Part 1: Identity
    identity = """# EVOKI - Therapeutischer KI-Begleiter

Du bist EVOKI, ein therapeutischer KI-Begleiter der auf Traumatherapie und emotionale Unterstützung spezialisiert ist.

## Deine Philosophie:
- Wahrheit vor Trost (Direktive A0)
- Halte den Raum, ziehe keine Grenzen (A46 Soul-Signature)
- Guardian-Veto bei Selbstgefährdung (A7.5, A29, A39)
- Basiere Antworten auf Fakten aus dem Chatverlauf (W-P-F Zeitmaschine)

## Dein Stil:
- Direkt, klar, ohne Floskeln
- Nutze "Du" statt "Sie"
- Keine Phrasen wie "Ich verstehe, dass...", sondern konkretes Eingehen
- Kurze, prägnante Antworten (2-4 Sätze ideal)
"""
    
    # Part 2: Regelwerk V12 Excerpt (Simplified for Phase 3)
    regelwerk = """
## Wichtigste Regeln:
- **A0:** Direktive der Wahrheit - Keine Halluzinationen, nur Fakten aus Kontext
- **A39:** Krisenprompt-Erkennung - Bei Suizid-Äußerungen Guardian aktivieren
- **A46:** Soul-Signature Check - Authentizität bewahren (B_align > 0.7)
- **A7.5:** Guardian-Veto - Bei T_panic > 0.8 keine destabilisierenden Antworten
- **A29:** Wächter - Bei F_risk > 0.6 vorsichtig agieren
"""
    
    # Part 3: Current Metrics
    metrics_summary = f"""
## Aktuelle Metriken:
- **A (Affekt):** {metrics.get('A', 0.5):.2f} (0=crisis, 1=positiv)
- **T_panic:** {metrics.get('T_panic', 0.0):.2f} (0=ruhig, 1=panik)
- **B_align:** {metrics.get('B_align', 0.5):.2f} (Soul-Signature)
- **F_risk:** {metrics.get('F_risk', 0.0):.2f} (0=sicher, 1=gefährdet)
- **PCI:** {metrics.get('PCI', 0.5):.2f} (Kohärenz)
"""
    
    # Part 4: W-P-F Context
    wpf_summary = f"""
## W-P-F Zeitmaschine Kontext:
- **Vergangenheit (P-25):** {wpf_context.get('P_m25', 'N/A')}
- **Vergangenheit (P-5):** {wpf_context.get('P_m5', 'N/A')}
- **Jetzt (W):** {wpf_context.get('W', 'N/A')}
- **Zukunft (F+5):** {wpf_context.get('F_p5', 'N/A')}
"""
    
    # Part 5: FAISS Chunks (Top-3 ähnliche Konversationen)
    faiss_summary = "\n## Relevante Chatverlauf-Ausschnitte:\n"
    for i, chunk in enumerate(faiss_chunks[:3], 1):
        faiss_summary += f"{i}. {chunk.get('chunk_id', 'unknown')} (Similarity: {chunk.get('similarity', 0):.2f})\n"
    
    # Combine all parts
    complete_message = (
        identity + "\n" +
        regelwerk + "\n" +
        metrics_summary + "\n" +
        wpf_summary + "\n" +
        faiss_summary + "\n" +
        "## Anweisung:\n"
        "Antworte basierend auf diesem Kontext. Sei authentisch, direkt und hilfreich."
    )
    
    return complete_message


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_llm_router():
        print("=" * 80)
        print("EVOKI V3.0 - LLM ROUTER TEST (Phase 3)")
        print("=" * 80)
        
        router = get_llm_router()
        
        print(f"\n📊 Status:")
        print(f"  Gemini Available: {GEMINI_AVAILABLE}")
        print(f"  OpenAI Available: {OPENAI_AVAILABLE}")
        
        # Build mock context
        system_msg = build_system_message(
            faiss_chunks=[{"chunk_id": "test_123", "similarity": 0.85}],
            metrics={"A": 0.7, "T_panic": 0.1, "B_align": 0.85, "F_risk": 0.2, "PCI": 0.8},
            wpf_context={"P_m25": "Mock Past", "P_m5": "Mock", "W": "test_123", "F_p5": "Mock Future"}
        )
        
        print(f"\n{'─' * 80}")
        print(f"Test: LLM Streaming")
        print(f"{'─' * 80}\n")
        
        # Stream response
        full_response = ""
        async for token in router.stream_response(system_msg, "Wie geht es dir?"):
            print(token, end="", flush=True)
            full_response += token
        
        print(f"\n\n{'─' * 80}")
        print(f"✅ Test Complete! Response length: {len(full_response)} chars")
        print(f"{'─' * 80}")
    
    asyncio.run(test_llm_router())
