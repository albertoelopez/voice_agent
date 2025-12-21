import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class TestEnvironmentVariables:
    def test_groq_api_key_exists(self):
        assert os.getenv("GROQ_API_KEY") is not None
        assert len(os.getenv("GROQ_API_KEY")) > 0

    def test_livekit_url_exists(self):
        url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        assert url.startswith("ws://") or url.startswith("wss://")

    def test_livekit_credentials_exist(self):
        assert os.getenv("LIVEKIT_API_KEY") is not None
        assert os.getenv("LIVEKIT_API_SECRET") is not None


class TestLiveKitSDK:
    def test_can_import_livekit_agents(self):
        from livekit.agents import Agent, AgentSession, WorkerOptions, cli
        assert Agent is not None
        assert AgentSession is not None

    def test_can_import_livekit_plugins(self):
        from livekit.plugins import groq, silero
        assert groq is not None
        assert silero is not None

    def test_can_create_groq_stt(self):
        from livekit.plugins import groq
        stt = groq.STT(model="whisper-large-v3-turbo")
        assert stt is not None

    def test_can_create_groq_llm(self):
        from livekit.plugins import groq
        llm = groq.LLM(model="llama-3.3-70b-versatile")
        assert llm is not None

    def test_can_create_groq_tts(self):
        from livekit.plugins import groq
        tts = groq.TTS()
        assert tts is not None

    def test_can_load_silero_vad(self):
        from livekit.plugins import silero
        vad = silero.VAD.load()
        assert vad is not None


class TestTokenGeneration:
    def test_can_generate_token(self):
        from livekit import api

        token = api.AccessToken(
            os.getenv("LIVEKIT_API_KEY", "devkey"),
            os.getenv("LIVEKIT_API_SECRET", "secret")
        ).with_identity("test-user").with_grants(
            api.VideoGrants(room_join=True, room="test-room")
        ).to_jwt()

        assert token is not None
        assert len(token) > 0
        assert token.count(".") == 2


class TestAgentModule:
    def test_can_import_inquiry_agent(self):
        from src.agents import inquiry_agent
        assert inquiry_agent is not None

    def test_system_prompt_exists(self):
        from src.agents.inquiry_agent import SYSTEM_PROMPT
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 100

    def test_entrypoint_function_exists(self):
        from src.agents.inquiry_agent import entrypoint
        assert callable(entrypoint)

    def test_prewarm_function_exists(self):
        from src.agents.inquiry_agent import prewarm
        assert callable(prewarm)
