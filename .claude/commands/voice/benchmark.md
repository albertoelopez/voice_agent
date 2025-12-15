---
description: Run latency benchmarks on voice agent pipeline
allowed-tools: Bash(python:*), Read, Write
---

# Voice Agent Latency Benchmark

I'll run comprehensive latency benchmarks on the voice pipeline.

## Benchmark Configuration
- Iterations: 100 (default)
- Metrics: P50, P95, P99, Mean
- Components: STT, LLM, TTS, End-to-End

## Run Benchmark

```python
import asyncio
import statistics
import time
from dataclasses import dataclass
from typing import List

@dataclass
class BenchmarkResult:
    component: str
    p50: float
    p95: float
    p99: float
    mean: float
    min_ms: float
    max_ms: float

async def benchmark_component(name: str, func, iterations: int = 100) -> BenchmarkResult:
    latencies = []
    for i in range(iterations):
        start = time.perf_counter()
        await func()
        latencies.append((time.perf_counter() - start) * 1000)
        if (i + 1) % 10 == 0:
            print(f"  {name}: {i + 1}/{iterations}")

    sorted_latencies = sorted(latencies)
    return BenchmarkResult(
        component=name,
        p50=sorted_latencies[int(iterations * 0.50)],
        p95=sorted_latencies[int(iterations * 0.95)],
        p99=sorted_latencies[int(iterations * 0.99)],
        mean=statistics.mean(latencies),
        min_ms=min(latencies),
        max_ms=max(latencies),
    )

def print_results(results: List[BenchmarkResult]):
    print("\n" + "=" * 60)
    print("VOICE AGENT LATENCY BENCHMARK RESULTS")
    print("=" * 60)
    print(f"{'Component':<15} {'P50':>8} {'P95':>8} {'P99':>8} {'Mean':>8}")
    print("-" * 60)
    for r in results:
        print(f"{r.component:<15} {r.p50:>7.0f}ms {r.p95:>7.0f}ms {r.p99:>7.0f}ms {r.mean:>7.0f}ms")
    print("=" * 60)

    total_p50 = sum(r.p50 for r in results if r.component != "e2e")
    print(f"\nEstimated E2E P50: {total_p50:.0f}ms")

    if total_p50 < 300:
        print("Status: EXCELLENT - Natural conversation feel")
    elif total_p50 < 500:
        print("Status: GOOD - Acceptable latency")
    elif total_p50 < 800:
        print("Status: FAIR - Noticeable delay")
    else:
        print("Status: POOR - Needs optimization")
```

## Provider Comparison

Run benchmarks against multiple providers:

| Provider | Component | Expected P50 |
|----------|-----------|--------------|
| Groq Whisper | STT | 100-150ms |
| Groq Llama 3.3 | LLM | 80-120ms |
| Cartesia | TTS | 80-120ms |
| Deepgram | STT | 150-200ms |
| Ollama (local) | LLM | 200-500ms |
| Kokoro (local) | TTS | 50-100ms |

## Output

Results will be saved to `benchmarks/results_{timestamp}.json`
