---
description: Initialize voice agent development environment with all dependencies
allowed-tools: Bash(pip:*), Bash(python:*), Write, Read, Edit
---

# Voice Agent Setup

I'll set up the complete voice agent development environment.

## Step 1: Create Python virtual environment
```bash
cd /home/darthvader/AI_Projects/voice_agent
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Install core dependencies

**LiveKit Agents** (primary framework):
```bash
pip install livekit-agents livekit-plugins-groq livekit-plugins-silero livekit-plugins-cartesia
```

**Pipecat** (alternative/comparison):
```bash
pip install pipecat-ai[groq,silero,cartesia]
```

**Local fallbacks**:
```bash
pip install faster-whisper ollama kokoro-onnx piper-tts
```

**Development tools**:
```bash
pip install pytest pytest-asyncio pytest-cov python-dotenv rich
```

## Step 3: Create environment file

Create `.env` with required API keys:
```
GROQ_API_KEY=your_groq_api_key
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

## Step 4: Verify installation

Test that all components load correctly:
```python
python -c "
from livekit.agents import VoicePipelineAgent
from livekit.plugins import groq, silero
print('LiveKit Agents: OK')

import faster_whisper
print('faster-whisper: OK')

import ollama
print('Ollama: OK')

print('\\nAll dependencies installed successfully!')
"
```

## Step 5: Download local models (optional)

For 100% offline capability:
```bash
# Whisper model for local STT
python -c "from faster_whisper import WhisperModel; WhisperModel('base.en')"

# Ollama models for local LLM
ollama pull llama3.2:3b
ollama pull gemma3:4b
```

## Next Steps
- Run `/voice/test` to verify the pipeline works
- Use the `voice-architect` agent to design your pipeline
- Check `.claude/CLAUDE.md` for project documentation
