"""
Component tests for Voice Agent pipeline.

Tests each component independently:
- STT (Speech-to-Text) - Groq Whisper
- LLM (Language Model) - Groq Llama
- TTS (Text-to-Speech) - Cartesia

Run with: python -m pytest tests/test_components.py -v
"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class TestEnvironment:
    """Test that required environment variables are set."""

    def test_groq_api_key_exists(self):
        """GROQ_API_KEY should be set for STT and LLM."""
        api_key = os.getenv("GROQ_API_KEY")
        assert api_key is not None, "GROQ_API_KEY not set in .env"
        assert len(api_key) > 10, "GROQ_API_KEY seems invalid"
        print(f"  GROQ_API_KEY: {api_key[:10]}...{api_key[-4:]}")

    def test_cartesia_api_key_exists(self):
        """CARTESIA_API_KEY should be set for TTS."""
        api_key = os.getenv("CARTESIA_API_KEY")
        assert api_key is not None, "CARTESIA_API_KEY not set in .env"
        assert len(api_key) > 10, "CARTESIA_API_KEY seems invalid"
        print(f"  CARTESIA_API_KEY: {api_key[:10]}...{api_key[-4:]}")

    def test_livekit_config_exists(self):
        """LiveKit configuration should be set."""
        url = os.getenv("LIVEKIT_URL")
        key = os.getenv("LIVEKIT_API_KEY")
        secret = os.getenv("LIVEKIT_API_SECRET")

        assert url is not None, "LIVEKIT_URL not set"
        assert key is not None, "LIVEKIT_API_KEY not set"
        assert secret is not None, "LIVEKIT_API_SECRET not set"
        print(f"  LIVEKIT_URL: {url}")


class TestGroqSTT:
    """Test Groq Speech-to-Text (Whisper)."""

    @pytest.mark.asyncio
    async def test_stt_initialization(self):
        """STT should initialize without errors."""
        from livekit.plugins import groq

        stt = groq.STT(model="whisper-large-v3-turbo")
        assert stt is not None
        print(f"  STT Model: whisper-large-v3-turbo")
        print(f"  STT initialized successfully")


class TestGroqLLM:
    """Test Groq Language Model (Llama)."""

    @pytest.mark.asyncio
    async def test_llm_initialization(self):
        """LLM should initialize without errors."""
        from livekit.plugins import groq

        llm = groq.LLM(model="llama-3.3-70b-versatile")
        assert llm is not None
        print(f"  LLM Model: llama-3.3-70b-versatile")
        print(f"  LLM initialized successfully")

    @pytest.mark.asyncio
    async def test_llm_chat_completion(self):
        """LLM should respond to a simple prompt."""
        from livekit.plugins import groq
        from livekit.agents.llm import ChatContext, ChatMessage

        llm = groq.LLM(model="llama-3.3-70b-versatile")

        # Create a simple chat context
        ctx = ChatContext()
        ctx.messages.append(ChatMessage(role="user", content="Say 'test successful' and nothing else."))

        # Get response
        stream = llm.chat(chat_ctx=ctx)
        response_text = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content

        assert len(response_text) > 0, "LLM returned empty response"
        print(f"  LLM Response: {response_text[:100]}")


class TestCartesiaTTS:
    """Test Cartesia Text-to-Speech."""

    @pytest.mark.asyncio
    async def test_tts_initialization(self):
        """TTS should initialize without errors."""
        from livekit.plugins import cartesia

        tts = cartesia.TTS()
        assert tts is not None
        print(f"  TTS initialized successfully")

    @pytest.mark.asyncio
    async def test_tts_synthesis(self):
        """TTS should synthesize speech from text."""
        from livekit.plugins import cartesia

        tts = cartesia.TTS()

        # Synthesize a short phrase
        audio_stream = tts.synthesize("Hello, this is a test.")

        frames = []
        async for frame in audio_stream:
            frames.append(frame)

        assert len(frames) > 0, "TTS returned no audio frames"
        print(f"  TTS generated {len(frames)} audio frames")


class TestVAD:
    """Test Voice Activity Detection (Silero)."""

    def test_vad_initialization(self):
        """VAD should load without errors."""
        from livekit.plugins import silero

        vad = silero.VAD.load()
        assert vad is not None
        print(f"  VAD (Silero) loaded successfully")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
