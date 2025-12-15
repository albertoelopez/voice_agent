"""
Pytest configuration and fixtures for voice agent tests.
"""

import pytest
import asyncio
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_audio_path() -> Path:
    """Path to sample audio file for testing."""
    return Path(__file__).parent / "fixtures" / "hello_world.wav"


@pytest.fixture
def sample_audio_bytes(sample_audio_path) -> bytes:
    """Sample audio bytes for testing."""
    if sample_audio_path.exists():
        return sample_audio_path.read_bytes()
    # Return empty bytes if no fixture exists yet
    return b""


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Hello! How can I help you today?"
                }
            }
        ],
        "usage": {
            "total_tokens": 25
        }
    }


@pytest.fixture
def mock_transcription():
    """Mock transcription result."""
    return "Hello, I have a question about my order."
