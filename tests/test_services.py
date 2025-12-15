"""
Tests for voice agent services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.services.fallback import FallbackLLM, FallbackSTT, TranscriptionResult, GenerationResult


class TestFallbackLLM:
    """Tests for FallbackLLM service."""

    @pytest.fixture
    def llm(self):
        return FallbackLLM()

    @pytest.mark.asyncio
    async def test_generate_returns_result(self, llm, mock_groq_response):
        """Test that generate returns a GenerationResult."""
        with patch.object(llm, '_generate_groq', new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = GenerationResult(
                text="Hello! How can I help?",
                latency_ms=100,
                provider="groq",
            )

            result = await llm.generate("Hello")

            assert isinstance(result, GenerationResult)
            assert result.text == "Hello! How can I help?"
            assert result.provider == "groq"

    @pytest.mark.asyncio
    async def test_generate_falls_back_to_ollama(self, llm):
        """Test fallback to Ollama when Groq fails."""
        with patch.object(llm, '_generate_groq', new_callable=AsyncMock) as mock_groq:
            mock_groq.side_effect = Exception("Groq API error")

            with patch.object(llm, '_generate_ollama', new_callable=AsyncMock) as mock_ollama:
                mock_ollama.return_value = GenerationResult(
                    text="Hello from Ollama!",
                    latency_ms=300,
                    provider="ollama",
                )

                result = await llm.generate("Hello")

                assert result.provider == "ollama"
                assert result.text == "Hello from Ollama!"

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, llm):
        """Test generation with system prompt."""
        with patch.object(llm, '_generate_groq', new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = GenerationResult(
                text="Response",
                latency_ms=100,
                provider="groq",
            )

            await llm.generate(
                prompt="Hello",
                system="You are a helpful assistant."
            )

            mock_groq.assert_called_once()

    @pytest.mark.asyncio
    async def test_force_local_skips_groq(self, llm):
        """Test that use_local=True skips Groq entirely."""
        with patch.object(llm, '_generate_groq', new_callable=AsyncMock) as mock_groq:
            with patch.object(llm, '_generate_ollama', new_callable=AsyncMock) as mock_ollama:
                mock_ollama.return_value = GenerationResult(
                    text="Local response",
                    latency_ms=200,
                    provider="ollama",
                )

                result = await llm.generate("Hello", use_local=True)

                mock_groq.assert_not_called()
                assert result.provider == "ollama"


class TestFallbackSTT:
    """Tests for FallbackSTT service."""

    @pytest.fixture
    def stt(self):
        return FallbackSTT()

    @pytest.mark.asyncio
    async def test_transcribe_returns_result(self, stt, sample_audio_bytes):
        """Test that transcribe returns a TranscriptionResult."""
        with patch.object(stt, '_transcribe_groq', new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = TranscriptionResult(
                text="Hello world",
                latency_ms=100,
                provider="groq",
            )

            result = await stt.transcribe(sample_audio_bytes)

            assert isinstance(result, TranscriptionResult)
            assert result.text == "Hello world"

    @pytest.mark.asyncio
    async def test_transcribe_falls_back_to_local(self, stt, sample_audio_bytes):
        """Test fallback to local Whisper when Groq fails."""
        with patch.object(stt, '_transcribe_groq', new_callable=AsyncMock) as mock_groq:
            mock_groq.side_effect = Exception("Groq API error")

            with patch.object(stt, '_transcribe_local', new_callable=AsyncMock) as mock_local:
                mock_local.return_value = TranscriptionResult(
                    text="Hello from local",
                    latency_ms=250,
                    provider="local-whisper",
                )

                result = await stt.transcribe(sample_audio_bytes)

                assert result.provider == "local-whisper"


class TestLatencyMetrics:
    """Tests for latency tracking utilities."""

    def test_tracker_records_measurements(self):
        """Test that LatencyTracker records measurements correctly."""
        from src.utils.metrics import LatencyTracker

        tracker = LatencyTracker()

        with tracker.measure("test_stage"):
            pass  # Instant operation

        assert "test_stage" in tracker.stages
        assert tracker.stages["test_stage"].count == 1

    def test_tracker_calculates_percentiles(self):
        """Test percentile calculations."""
        from src.utils.metrics import StageMetrics

        metrics = StageMetrics(name="test")
        for i in range(100):
            metrics.add(float(i))

        assert metrics.p50 == 50.0
        assert metrics.p95 == 95.0
        assert metrics.mean == 49.5
