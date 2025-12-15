# Voice Agent Project

## Overview
Building a real-time voice agent for handling inquiries using open-source tools with free-tier inference providers.

## Tech Stack

### Primary Stack (LiveKit Agents)
- **Framework**: LiveKit Agents (production-grade, powers ChatGPT voice)
- **STT**: Groq Whisper Large v3 Turbo ($0.04/hr, 216x realtime)
- **LLM**: Groq Llama 3.3 70B (free tier) → Ollama fallback
- **TTS**: Kokoro (82M, local) or Cartesia (cloud)
- **VAD**: Silero VAD (voice activity detection)

### Fallback Stack (100% Local)
- **STT**: faster-whisper / Moonshine
- **LLM**: Ollama (Llama 3.2 3B / Gemma 3 4B)
- **TTS**: Kokoro / Piper / Orpheus

## Project Structure
```
voice_agent/
├── .claude/
│   ├── agents/           # Custom Claude Code agents
│   ├── commands/         # Slash commands for workflows
│   ├── skills/           # Reusable skills
│   └── hooks/            # Pre/post automation
├── src/
│   ├── agents/           # Voice agent implementations
│   ├── pipelines/        # STT→LLM→TTS pipelines
│   ├── services/         # Provider integrations (Groq, Ollama)
│   └── utils/            # Helpers, config loaders
├── config/               # Environment configs
└── tests/                # Test suite
```

## Key Commands
- `/voice/setup` - Initialize voice agent environment
- `/voice/test` - Test voice pipeline components
- `/voice/deploy` - Deploy voice agent
- `/voice/benchmark` - Run latency benchmarks

## Custom Agents
- `voice-architect` - Design voice pipelines and architecture
- `voice-debugger` - Debug voice agent issues (latency, quality)
- `voice-tester` - Test voice interactions and edge cases

## Environment Variables
```bash
GROQ_API_KEY=           # Groq API for STT/LLM
LIVEKIT_URL=            # LiveKit server URL
LIVEKIT_API_KEY=        # LiveKit API key
LIVEKIT_API_SECRET=     # LiveKit API secret
CARTESIA_API_KEY=       # Optional: Cartesia TTS
DEEPGRAM_API_KEY=       # Optional: Deepgram STT
```

## Latency Targets
- Voice-to-voice: <500ms (good), <300ms (great)
- STT: <200ms
- LLM TTFT: <150ms
- TTS first chunk: <100ms

## Development Guidelines
1. Always test with real audio, not just text
2. Measure latency at each pipeline stage
3. Handle interruptions gracefully (barge-in)
4. Test with background noise and accents
5. Implement graceful fallback to Ollama when Groq is unavailable
