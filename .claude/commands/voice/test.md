---
description: Test voice agent pipeline components (STT, LLM, TTS)
allowed-tools: Bash(python:*), Bash(pytest:*), Read, Write
---

# Voice Pipeline Component Tests

I'll test each component of the voice pipeline to ensure everything works.

## Test Target: $ARGUMENTS

If no target specified, I'll test all components.

## Component Tests

### 1. Test Groq STT (Whisper)
```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Test with a simple audio file or generate test audio
print("Testing Groq Whisper STT...")
# Measure latency and verify transcription
```

### 2. Test Groq LLM
```python
import time
from groq import Groq

client = Groq()
start = time.perf_counter()

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    max_tokens=50,
)

latency = (time.perf_counter() - start) * 1000
print(f"LLM Response: {response.choices[0].message.content}")
print(f"Latency: {latency:.0f}ms")
```

### 3. Test Local Ollama Fallback
```python
import ollama
import time

start = time.perf_counter()
response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Say hello in one sentence."}]
)
latency = (time.perf_counter() - start) * 1000
print(f"Ollama Response: {response['message']['content']}")
print(f"Latency: {latency:.0f}ms")
```

### 4. Test TTS
```python
# Test Kokoro TTS (local)
from kokoro_onnx import Kokoro

kokoro = Kokoro("kokoro-v1.0.onnx", "voices.bin")
samples, sr = kokoro.create("Hello, this is a test of the voice agent.")
print(f"Generated {len(samples)/sr:.2f}s of audio at {sr}Hz")
```

### 5. Test Full Pipeline Latency
```python
import asyncio
import time

async def test_full_pipeline():
    # Simulate: Audio → STT → LLM → TTS
    stages = {}

    # STT
    t0 = time.perf_counter()
    text = await stt.transcribe(audio)
    stages['stt'] = (time.perf_counter() - t0) * 1000

    # LLM
    t0 = time.perf_counter()
    response = await llm.generate(text)
    stages['llm'] = (time.perf_counter() - t0) * 1000

    # TTS
    t0 = time.perf_counter()
    audio_out = await tts.synthesize(response)
    stages['tts'] = (time.perf_counter() - t0) * 1000

    stages['total'] = sum(stages.values())
    return stages
```

## Expected Results
- STT: <200ms
- LLM (TTFT): <150ms
- TTS (first chunk): <100ms
- Total: <500ms (target)
