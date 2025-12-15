"""
Fallback service implementations for graceful degradation.

Provides automatic failover from cloud providers to local models.
"""

import logging
import time
from typing import AsyncIterator, Optional
from dataclasses import dataclass

import ollama
from faster_whisper import WhisperModel

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result from speech-to-text transcription."""
    text: str
    latency_ms: float
    provider: str
    confidence: Optional[float] = None


@dataclass
class GenerationResult:
    """Result from LLM generation."""
    text: str
    latency_ms: float
    provider: str
    tokens_used: Optional[int] = None


class FallbackSTT:
    """
    Speech-to-Text with automatic fallback.

    Primary: Groq Whisper (cloud, fast)
    Fallback: faster-whisper (local)
    """

    def __init__(self):
        self._local_model: Optional[WhisperModel] = None
        self._groq_client = None

    def _get_groq_client(self):
        """Lazy-load Groq client."""
        if self._groq_client is None:
            from groq import Groq
            self._groq_client = Groq(api_key=settings.groq_api_key)
        return self._groq_client

    def _get_local_model(self) -> WhisperModel:
        """Lazy-load local Whisper model."""
        if self._local_model is None:
            logger.info("Loading local Whisper model...")
            self._local_model = WhisperModel(
                "base.en",
                device="cpu",
                compute_type="int8"
            )
            logger.info("Local Whisper model loaded")
        return self._local_model

    async def transcribe(
        self,
        audio_bytes: bytes,
        use_local: bool = False
    ) -> TranscriptionResult:
        """
        Transcribe audio with automatic fallback.

        Args:
            audio_bytes: Audio data to transcribe
            use_local: Force local model (skip cloud)

        Returns:
            TranscriptionResult with text and metadata
        """
        if not use_local and settings.groq_api_key:
            try:
                return await self._transcribe_groq(audio_bytes)
            except Exception as e:
                logger.warning(f"Groq STT failed, falling back to local: {e}")

        return await self._transcribe_local(audio_bytes)

    async def _transcribe_groq(self, audio_bytes: bytes) -> TranscriptionResult:
        """Transcribe using Groq Whisper."""
        start = time.perf_counter()
        client = self._get_groq_client()

        transcription = client.audio.transcriptions.create(
            model=settings.stt_model,
            file=("audio.wav", audio_bytes),
            response_format="text",
        )

        latency = (time.perf_counter() - start) * 1000
        logger.debug(f"Groq STT latency: {latency:.0f}ms")

        return TranscriptionResult(
            text=transcription,
            latency_ms=latency,
            provider="groq",
        )

    async def _transcribe_local(self, audio_bytes: bytes) -> TranscriptionResult:
        """Transcribe using local faster-whisper."""
        import tempfile

        start = time.perf_counter()
        model = self._get_local_model()

        # Write audio to temp file (faster-whisper needs file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        segments, _ = model.transcribe(temp_path, beam_size=5)
        text = " ".join(segment.text for segment in segments)

        latency = (time.perf_counter() - start) * 1000
        logger.debug(f"Local STT latency: {latency:.0f}ms")

        return TranscriptionResult(
            text=text.strip(),
            latency_ms=latency,
            provider="local-whisper",
        )


class FallbackLLM:
    """
    LLM with automatic fallback.

    Primary: Groq (cloud, fast inference)
    Fallback: Ollama (local)
    """

    def __init__(self):
        self._groq_client = None

    def _get_groq_client(self):
        """Lazy-load Groq client."""
        if self._groq_client is None:
            from groq import Groq
            self._groq_client = Groq(api_key=settings.groq_api_key)
        return self._groq_client

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        use_local: bool = False,
        max_tokens: int = 150,
    ) -> GenerationResult:
        """
        Generate response with automatic fallback.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            use_local: Force local model (skip cloud)
            max_tokens: Maximum tokens to generate

        Returns:
            GenerationResult with text and metadata
        """
        if not use_local and settings.groq_api_key:
            try:
                return await self._generate_groq(prompt, system, max_tokens)
            except Exception as e:
                logger.warning(f"Groq LLM failed, falling back to Ollama: {e}")

        return await self._generate_ollama(prompt, system, max_tokens)

    async def _generate_groq(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int
    ) -> GenerationResult:
        """Generate using Groq."""
        start = time.perf_counter()
        client = self._get_groq_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )

        latency = (time.perf_counter() - start) * 1000
        logger.debug(f"Groq LLM latency: {latency:.0f}ms")

        return GenerationResult(
            text=response.choices[0].message.content,
            latency_ms=latency,
            provider="groq",
            tokens_used=response.usage.total_tokens if response.usage else None,
        )

    async def _generate_ollama(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int
    ) -> GenerationResult:
        """Generate using local Ollama."""
        start = time.perf_counter()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = ollama.chat(
            model=settings.ollama_model,
            messages=messages,
            options={"num_predict": max_tokens},
        )

        latency = (time.perf_counter() - start) * 1000
        logger.debug(f"Ollama LLM latency: {latency:.0f}ms")

        return GenerationResult(
            text=response["message"]["content"],
            latency_ms=latency,
            provider="ollama",
        )

    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        use_local: bool = False,
    ) -> AsyncIterator[str]:
        """
        Stream response tokens for lower perceived latency.

        Yields:
            Individual tokens/chunks as they're generated
        """
        if not use_local and settings.groq_api_key:
            try:
                async for chunk in self._stream_groq(prompt, system):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Groq streaming failed, falling back: {e}")

        async for chunk in self._stream_ollama(prompt, system):
            yield chunk

    async def _stream_groq(
        self,
        prompt: str,
        system: Optional[str]
    ) -> AsyncIterator[str]:
        """Stream from Groq."""
        client = self._get_groq_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _stream_ollama(
        self,
        prompt: str,
        system: Optional[str]
    ) -> AsyncIterator[str]:
        """Stream from Ollama."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        for chunk in ollama.chat(
            model=settings.ollama_model,
            messages=messages,
            stream=True,
        ):
            if chunk["message"]["content"]:
                yield chunk["message"]["content"]
