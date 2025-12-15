"""
Latency and performance metrics tracking.
"""

import time
import logging
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage."""
    name: str
    latencies: List[float] = field(default_factory=list)

    def add(self, latency_ms: float):
        """Add a latency measurement."""
        self.latencies.append(latency_ms)

    @property
    def count(self) -> int:
        return len(self.latencies)

    @property
    def mean(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0

    @property
    def p50(self) -> float:
        if not self.latencies:
            return 0
        sorted_vals = sorted(self.latencies)
        return sorted_vals[int(len(sorted_vals) * 0.50)]

    @property
    def p95(self) -> float:
        if not self.latencies:
            return 0
        sorted_vals = sorted(self.latencies)
        return sorted_vals[int(len(sorted_vals) * 0.95)]

    @property
    def p99(self) -> float:
        if not self.latencies:
            return 0
        sorted_vals = sorted(self.latencies)
        return sorted_vals[min(int(len(sorted_vals) * 0.99), len(sorted_vals) - 1)]


class LatencyTracker:
    """
    Track latency metrics across voice pipeline stages.

    Usage:
        tracker = LatencyTracker()

        with tracker.measure("stt"):
            result = await stt.transcribe(audio)

        with tracker.measure("llm"):
            response = await llm.generate(prompt)

        tracker.print_summary()
    """

    def __init__(self):
        self.stages: Dict[str, StageMetrics] = {}
        self._start_times: Dict[str, float] = {}

    @contextmanager
    def measure(self, stage_name: str):
        """Context manager to measure a pipeline stage."""
        start = time.perf_counter()
        try:
            yield
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            self._record(stage_name, latency_ms)

    def _record(self, stage_name: str, latency_ms: float):
        """Record a latency measurement."""
        if stage_name not in self.stages:
            self.stages[stage_name] = StageMetrics(name=stage_name)
        self.stages[stage_name].add(latency_ms)
        logger.debug(f"{stage_name}: {latency_ms:.0f}ms")

    def start(self, stage_name: str):
        """Start timing a stage (for non-context-manager usage)."""
        self._start_times[stage_name] = time.perf_counter()

    def stop(self, stage_name: str) -> float:
        """Stop timing and record the measurement."""
        if stage_name not in self._start_times:
            raise ValueError(f"Stage '{stage_name}' was not started")
        latency_ms = (time.perf_counter() - self._start_times[stage_name]) * 1000
        del self._start_times[stage_name]
        self._record(stage_name, latency_ms)
        return latency_ms

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all stages."""
        return {
            name: {
                "count": stage.count,
                "mean": stage.mean,
                "p50": stage.p50,
                "p95": stage.p95,
                "p99": stage.p99,
            }
            for name, stage in self.stages.items()
        }

    def print_summary(self):
        """Print a formatted summary table."""
        table = Table(title="Voice Pipeline Latency Metrics")

        table.add_column("Stage", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Mean", justify="right")
        table.add_column("P50", justify="right")
        table.add_column("P95", justify="right")
        table.add_column("P99", justify="right")

        total_p50 = 0
        for name, stage in self.stages.items():
            table.add_row(
                name,
                str(stage.count),
                f"{stage.mean:.0f}ms",
                f"{stage.p50:.0f}ms",
                f"{stage.p95:.0f}ms",
                f"{stage.p99:.0f}ms",
            )
            total_p50 += stage.p50

        table.add_section()
        table.add_row(
            "TOTAL (estimated)",
            "-",
            "-",
            f"{total_p50:.0f}ms",
            "-",
            "-",
            style="bold green" if total_p50 < 500 else "bold yellow" if total_p50 < 800 else "bold red"
        )

        console.print(table)

        # Print status
        if total_p50 < 300:
            console.print("\n[green]Status: EXCELLENT[/green] - Natural conversation feel")
        elif total_p50 < 500:
            console.print("\n[green]Status: GOOD[/green] - Acceptable latency")
        elif total_p50 < 800:
            console.print("\n[yellow]Status: FAIR[/yellow] - Noticeable delay")
        else:
            console.print("\n[red]Status: POOR[/red] - Needs optimization")

    def reset(self):
        """Reset all metrics."""
        self.stages.clear()
        self._start_times.clear()


# Global tracker instance
tracker = LatencyTracker()
