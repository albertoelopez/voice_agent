# Voice Agent Provider Reference

## STT (Speech-to-Text)

### Groq Whisper
```python
from groq import Groq
import base64

client = Groq()

def transcribe_audio(audio_bytes: bytes) -> str:
    # Groq expects base64 or file
    transcription = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",  # or whisper-large-v3
        file=("audio.wav", audio_bytes),
        response_format="text",
    )
    return transcription
```

### faster-whisper (Local)
```python
from faster_whisper import WhisperModel

model = WhisperModel("base.en", device="cpu", compute_type="int8")

def transcribe_local(audio_path: str) -> str:
    segments, info = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text for segment in segments)
```

---

## LLM (Large Language Model)

### Groq
```python
from groq import Groq

client = Groq()

async def generate(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streaming
async def stream(prompt: str):
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Ollama (Local)
```python
import ollama

def generate_local(prompt: str, model: str = "llama3.2:3b") -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# Streaming
def stream_local(prompt: str, model: str = "llama3.2:3b"):
    for chunk in ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        yield chunk["message"]["content"]
```

---

## TTS (Text-to-Speech)

### Kokoro (Local)
```python
from kokoro_onnx import Kokoro
import soundfile as sf

kokoro = Kokoro("kokoro-v1.0.onnx", "voices.bin")

def synthesize(text: str, voice: str = "af_sarah") -> bytes:
    samples, sample_rate = kokoro.create(
        text,
        voice=voice,
        speed=1.0
    )
    # Convert to bytes
    import io
    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format='WAV')
    return buffer.getvalue()
```

### Piper (Local)
```python
import subprocess

def synthesize_piper(text: str, model: str = "en_US-lessac-medium") -> bytes:
    process = subprocess.run(
        ["piper", "--model", model, "--output-raw"],
        input=text.encode(),
        capture_output=True
    )
    return process.stdout
```

### Cartesia (Cloud)
```python
from cartesia import Cartesia

client = Cartesia(api_key=os.environ["CARTESIA_API_KEY"])

async def synthesize_cartesia(text: str) -> bytes:
    audio = await client.tts.bytes(
        model_id="sonic-english",
        transcript=text,
        voice={"mode": "id", "id": "professional-female"},
        output_format={"container": "wav", "sample_rate": 24000}
    )
    return audio
```

---

## VAD (Voice Activity Detection)

### Silero VAD
```python
from livekit.plugins import silero

vad = silero.VAD.load(
    min_speech_duration=0.1,
    min_silence_duration=0.3,
    padding_duration=0.1,
    sample_rate=16000,
)
```

### WebRTC VAD
```python
import webrtcvad

vad = webrtcvad.Vad(3)  # Aggressiveness 0-3

def is_speech(audio_chunk: bytes, sample_rate: int = 16000) -> bool:
    return vad.is_speech(audio_chunk, sample_rate)
```
