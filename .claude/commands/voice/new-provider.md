---
description: Add a new STT, LLM, or TTS provider integration
allowed-tools: Read, Write, Edit, Bash(pip:*), WebSearch
argument-hint: <provider-type> <provider-name>
---

# Add New Provider Integration

I'll help add a new provider to the voice agent pipeline.

## Arguments
- Provider type: $1 (stt, llm, or tts)
- Provider name: $2 (e.g., deepgram, anthropic, elevenlabs)

## Provider Integration Template

### For STT Providers:
```python
# src/services/stt/{provider_name}.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    latency_ms: float

class BaseSTT(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes) -> TranscriptionResult:
        pass

class {ProviderName}STT(BaseSTT):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("{PROVIDER}_API_KEY")
        self.client = {Provider}Client(api_key=self.api_key)

    async def transcribe(self, audio: bytes) -> TranscriptionResult:
        start = time.perf_counter()
        result = await self.client.transcribe(audio)
        latency = (time.perf_counter() - start) * 1000

        return TranscriptionResult(
            text=result.text,
            confidence=result.confidence,
            latency_ms=latency
        )
```

### For LLM Providers:
```python
# src/services/llm/{provider_name}.py
class {ProviderName}LLM(BaseLLM):
    async def generate(self, prompt: str, **kwargs) -> str:
        # Implementation
        pass

    async def stream(self, prompt: str, **kwargs):
        # Streaming implementation for lower latency
        async for chunk in self.client.stream(...):
            yield chunk
```

### For TTS Providers:
```python
# src/services/tts/{provider_name}.py
class {ProviderName}TTS(BaseTTS):
    async def synthesize(self, text: str) -> bytes:
        # Return audio bytes
        pass

    async def stream(self, text: str):
        # Stream audio chunks for lower TTFB
        async for chunk in self.client.stream(...):
            yield chunk
```

## Steps
1. Install provider SDK
2. Create provider class implementing base interface
3. Add to provider registry
4. Write unit tests
5. Run benchmarks to compare latency
