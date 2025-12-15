---
name: voice-pipeline
description: |
  Build and configure voice agent pipelines with STT, LLM, and TTS components.
  Use when creating voice agents, configuring audio pipelines, or integrating
  providers like Groq, Ollama, Deepgram, Cartesia, or Kokoro.
  Handles LiveKit Agents and Pipecat frameworks.
---

# Voice Pipeline Configuration Skill

You are an expert at building real-time voice pipelines.

## Supported Frameworks

### LiveKit Agents
```python
from livekit.agents import VoicePipelineAgent, JobContext
from livekit.plugins import groq, silero, cartesia

async def entrypoint(ctx: JobContext):
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=cartesia.TTS(voice="professional-female"),
        allow_interruptions=True,
        interrupt_speech_duration=0.5,
    )

    await agent.start(ctx.room)
```

### Pipecat
```python
from pipecat.pipeline import Pipeline
from pipecat.services.groq import GroqLLMService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.daily import DailyTransport

pipeline = Pipeline([
    transport.input(),
    stt_service,
    llm_service,
    tts_service,
    transport.output(),
])
```

## Provider Configurations

### STT Providers
| Provider | Code | Latency | Cost |
|----------|------|---------|------|
| Groq Whisper | `groq.STT(model="whisper-large-v3-turbo")` | ~100ms | $0.04/hr |
| Deepgram | `deepgram.STT()` | ~150ms | $0.0125/min |
| faster-whisper | `LocalSTT(model="base.en")` | ~200ms | Free |

### LLM Providers
| Provider | Code | TTFT | Cost |
|----------|------|------|------|
| Groq Llama | `groq.LLM(model="llama-3.3-70b-versatile")` | ~100ms | Free tier |
| Ollama | `OllamaLLM(model="llama3.2:3b")` | ~300ms | Free |
| OpenAI | `openai.LLM(model="gpt-4o-mini")` | ~200ms | $0.15/1M tokens |

### TTS Providers
| Provider | Code | TTFB | Cost |
|----------|------|------|------|
| Cartesia | `cartesia.TTS()` | ~80ms | $0.01/1k chars |
| Kokoro | `KokoroTTS()` | ~50ms | Free |
| ElevenLabs | `elevenlabs.TTS()` | ~150ms | $0.30/1k chars |

## Pipeline Patterns

### Cloud-First with Fallback
```python
class FallbackLLM:
    def __init__(self):
        self.primary = GroqLLM()
        self.fallback = OllamaLLM()

    async def generate(self, prompt):
        try:
            return await self.primary.generate(prompt)
        except Exception:
            return await self.fallback.generate(prompt)
```

### Streaming Pipeline
```python
async def streaming_pipeline(audio_stream):
    async for audio_chunk in audio_stream:
        text = await stt.transcribe_streaming(audio_chunk)
        if text:
            async for llm_chunk in llm.stream(text):
                async for audio in tts.stream(llm_chunk):
                    yield audio
```

## Optimization Tips
1. Use streaming APIs everywhere
2. Pre-warm connections on startup
3. Use semantic turn detection (not silence timers)
4. Implement proper barge-in handling
5. Cache TTS for common responses
