"""Voice Agent Configuration Settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from enum import Enum


class STTProvider(str, Enum):
    GROQ = "groq"
    DEEPGRAM = "deepgram"
    LOCAL = "local"  # faster-whisper


class LLMProvider(str, Enum):
    GROQ = "groq"
    OLLAMA = "ollama"
    OPENAI = "openai"


class TTSProvider(str, Enum):
    CARTESIA = "cartesia"
    KOKORO = "kokoro"
    PIPER = "piper"
    OPENAI = "openai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LiveKit Configuration
    livekit_url: str = Field(default="ws://localhost:7880", alias="LIVEKIT_URL")
    livekit_api_key: str = Field(default="devkey", alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(default="secret", alias="LIVEKIT_API_SECRET")

    # Provider API Keys
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    deepgram_api_key: Optional[str] = Field(default=None, alias="DEEPGRAM_API_KEY")
    cartesia_api_key: Optional[str] = Field(default=None, alias="CARTESIA_API_KEY")

    # Provider Selection
    stt_provider: STTProvider = Field(default=STTProvider.GROQ)
    llm_provider: LLMProvider = Field(default=LLMProvider.GROQ)
    tts_provider: TTSProvider = Field(default=TTSProvider.CARTESIA)

    # Model Configuration
    stt_model: str = Field(default="whisper-large-v3-turbo")
    llm_model: str = Field(default="llama-3.3-70b-versatile")
    tts_voice: str = Field(default="professional-female")

    # Ollama (Local Fallback)
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3.2:3b")

    # Pipeline Settings
    allow_interruptions: bool = Field(default=True)
    interrupt_speech_duration: float = Field(default=0.5)
    min_silence_duration: float = Field(default=0.3)

    # Latency Targets (ms)
    target_stt_latency: int = Field(default=200)
    target_llm_latency: int = Field(default=150)
    target_tts_latency: int = Field(default=100)
    target_total_latency: int = Field(default=500)

    # Logging
    log_level: str = Field(default="INFO")
    log_latency_metrics: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
