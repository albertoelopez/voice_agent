"""
Direct API tests - Tests each provider's API directly.

This bypasses LiveKit's job context to test the underlying APIs.
Run with: python tests/test_api_direct.py
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"  [{status}] {name}")
    if details:
        print(f"        {details}")


async def test_groq_llm():
    """Test Groq LLM API directly."""
    print(f"\n{BOLD}Testing Groq LLM (Llama 3.3){RESET}")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print_test("API Key", False, "GROQ_API_KEY not set")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": "Say 'Hello' and nothing else."}],
                    "max_tokens": 10
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data["choices"][0]["message"]["content"]
                    print_test("LLM Chat", True, f"Response: {response}")
                    return True
                else:
                    error = await resp.text()
                    print_test("LLM Chat", False, f"Status {resp.status}: {error[:100]}")
                    return False
    except Exception as e:
        print_test("LLM Chat", False, str(e))
        return False


async def test_groq_stt():
    """Test Groq STT API (Whisper) - just verify endpoint is reachable."""
    print(f"\n{BOLD}Testing Groq STT (Whisper){RESET}")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print_test("API Key", False, "GROQ_API_KEY not set")
        return False

    # We can't easily test STT without audio, but we can verify the API key works
    # by checking if we can reach the transcriptions endpoint
    try:
        async with aiohttp.ClientSession() as session:
            # Test with empty request to verify API key
            async with session.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data=aiohttp.FormData()
            ) as resp:
                # 400 means API key is valid but request is invalid (expected)
                # 401 means API key is invalid
                if resp.status in [400, 422]:
                    print_test("STT Endpoint", True, "API key valid, endpoint reachable")
                    return True
                elif resp.status == 401:
                    print_test("STT Endpoint", False, "Invalid API key")
                    return False
                else:
                    print_test("STT Endpoint", True, f"Status {resp.status} (unexpected but reachable)")
                    return True
    except Exception as e:
        print_test("STT Endpoint", False, str(e))
        return False


async def test_cartesia_tts():
    """Test Cartesia TTS API directly."""
    print(f"\n{BOLD}Testing Cartesia TTS{RESET}")

    api_key = os.getenv("CARTESIA_API_KEY")
    if not api_key:
        print_test("API Key", False, "CARTESIA_API_KEY not set")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            # Test voice list endpoint first
            async with session.get(
                "https://api.cartesia.ai/voices",
                headers={
                    "X-API-Key": api_key,
                    "Cartesia-Version": "2024-06-10"
                }
            ) as resp:
                if resp.status == 200:
                    voices = await resp.json()
                    print_test("Get Voices", True, f"Found {len(voices)} voices")
                else:
                    error = await resp.text()
                    print_test("Get Voices", False, f"Status {resp.status}: {error[:100]}")
                    return False

            # Test TTS synthesis
            async with session.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={
                    "X-API-Key": api_key,
                    "Cartesia-Version": "2024-06-10",
                    "Content-Type": "application/json"
                },
                json={
                    "model_id": "sonic-english",
                    "transcript": "Hello, this is a test.",
                    "voice": {
                        "mode": "id",
                        "id": "a0e99841-438c-4a64-b679-ae501e7d6091"  # Default voice
                    },
                    "output_format": {
                        "container": "raw",
                        "encoding": "pcm_s16le",
                        "sample_rate": 24000
                    }
                }
            ) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    print_test("TTS Synthesis", True, f"Generated {len(audio_data)} bytes of audio")
                    return True
                else:
                    error = await resp.text()
                    print_test("TTS Synthesis", False, f"Status {resp.status}: {error[:200]}")
                    return False

    except Exception as e:
        print_test("TTS Synthesis", False, str(e))
        return False


async def test_deepgram_stt():
    """Test Deepgram STT API (alternative)."""
    print(f"\n{BOLD}Testing Deepgram STT (Alternative){RESET}")

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print_test("API Key", False, "DEEPGRAM_API_KEY not set (optional)")
        return None  # Optional test

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.deepgram.com/v1/projects",
                headers={"Authorization": f"Token {api_key}"}
            ) as resp:
                if resp.status == 200:
                    print_test("API Key Valid", True, "Deepgram API key works")
                    return True
                else:
                    print_test("API Key Valid", False, f"Status {resp.status}")
                    return False
    except Exception as e:
        print_test("API Key Valid", False, str(e))
        return False


async def test_livekit_server():
    """Test LiveKit server is running."""
    print(f"\n{BOLD}Testing LiveKit Server{RESET}")

    url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    http_url = url.replace("ws://", "http://").replace("wss://", "https://")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(http_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    print_test("Server Running", True, f"Response: {text}")
                    return True
                else:
                    print_test("Server Running", False, f"Status {resp.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print_test("Server Running", False, f"Cannot connect to {http_url}")
        return False
    except Exception as e:
        print_test("Server Running", False, str(e))
        return False


async def main():
    """Run all tests."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Voice Agent - Direct API Tests{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    results = {}

    # Run all tests
    results["LiveKit Server"] = await test_livekit_server()
    results["Groq LLM"] = await test_groq_llm()
    results["Groq STT"] = await test_groq_stt()
    results["Cartesia TTS"] = await test_cartesia_tts()
    results["Deepgram STT"] = await test_deepgram_stt()

    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Summary{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for name, result in results.items():
        if result is True:
            print(f"  {GREEN}PASS{RESET} - {name}")
        elif result is False:
            print(f"  {RED}FAIL{RESET} - {name}")
        else:
            print(f"  {YELLOW}SKIP{RESET} - {name}")

    print(f"\n  Total: {passed} passed, {failed} failed, {skipped} skipped")

    # Return exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
