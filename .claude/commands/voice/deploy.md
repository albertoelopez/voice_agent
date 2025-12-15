---
description: Deploy voice agent to production
allowed-tools: Bash(docker:*), Bash(python:*), Bash(pip:*), Read, Write, Edit
---

# Voice Agent Deployment

I'll help deploy the voice agent to production.

## Deployment Options

### Option 1: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "src.agents.voice_agent"]
```

```bash
docker build -t voice-agent:latest .
docker run -d \
  --name voice-agent \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e LIVEKIT_URL=$LIVEKIT_URL \
  -e LIVEKIT_API_KEY=$LIVEKIT_API_KEY \
  -e LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET \
  voice-agent:latest
```

### Option 2: LiveKit Cloud
```bash
# Deploy to LiveKit Cloud
lk cloud deploy --project voice-agent
```

### Option 3: Self-Hosted LiveKit
```yaml
# docker-compose.yml
version: '3.8'
services:
  livekit:
    image: livekit/livekit-server:latest
    ports:
      - "7880:7880"
      - "7881:7881"
    environment:
      - LIVEKIT_KEYS=devkey:secret

  voice-agent:
    build: .
    depends_on:
      - livekit
    environment:
      - LIVEKIT_URL=ws://livekit:7880
      - GROQ_API_KEY=${GROQ_API_KEY}
```

## Pre-Deployment Checklist
- [ ] All tests passing (`/voice/test`)
- [ ] Latency benchmarks acceptable (`/voice/benchmark`)
- [ ] Environment variables configured
- [ ] Fallback to Ollama tested
- [ ] Error handling verified
- [ ] Monitoring/logging configured

## Post-Deployment Verification
```bash
# Check agent status
docker logs voice-agent

# Test connectivity
curl -X POST http://localhost:7880/twirp/livekit.RoomService/ListRooms \
  -H "Content-Type: application/json" \
  -d '{}'
```
