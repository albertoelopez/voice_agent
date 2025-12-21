# Voice Agent

Real-time voice agent for handling customer inquiries using LiveKit Agents framework.

## Tech Stack

| Component | Provider | Model |
|-----------|----------|-------|
| STT | Groq | Whisper Large v3 Turbo |
| LLM | Groq | Llama 3.3 70B |
| TTS | Groq | - |
| VAD | Silero | - |
| Framework | LiveKit Agents | v1.3.6 |

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required:
- `GROQ_API_KEY` - Get from https://console.groq.com
- `LIVEKIT_URL` - LiveKit server URL (default: ws://localhost:7880)
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret

### 3. Start LiveKit Server

```bash
docker run -d \
  --name livekit-server \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 50000-50100:50000-50100/udp \
  livekit/livekit-server \
  --bind 0.0.0.0 \
  --dev
```

### 4. Run the Agent

```bash
python -m src.agents.inquiry_agent dev
```

### 5. Test in Browser

Open `test_client.html` in a browser or serve it:

```bash
python -m http.server 8080
# Visit http://localhost:8080/test_client.html
```

## Project Structure

```
voice_agent/
├── src/
│   └── agents/
│       └── inquiry_agent.py    # Main voice agent
├── tests/
│   ├── test_unit.py            # Unit tests (env, SDK, modules)
│   └── test_e2e.py             # E2E Playwright tests
├── test_client.html            # Browser test client
├── requirements.txt
└── .env                        # Environment variables
```

## Configuration

### Alternative TTS Providers

Edit `src/agents/inquiry_agent.py` to switch TTS:

```python
# Groq (default)
from livekit.plugins import groq
tts = groq.TTS()

# Cartesia
from livekit.plugins import cartesia
tts = cartesia.TTS()  # Requires CARTESIA_API_KEY

# Deepgram
from livekit.plugins import deepgram
tts = deepgram.TTS()  # Requires DEEPGRAM_API_KEY
```

## Testing

```bash
# Run unit tests
pytest tests/test_unit.py -v

# Run E2E tests (requires HTTP server on port 8080)
python -m http.server 8080 &
pytest tests/test_e2e.py -v

# Run all tests
pytest tests/test_unit.py tests/test_e2e.py -v
```

## Latency Targets

| Stage | Target |
|-------|--------|
| Voice-to-voice | <500ms |
| STT | <200ms |
| LLM TTFT | <150ms |
| TTS first chunk | <100ms |

## License

MIT
