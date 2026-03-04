from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionSpec:
    """Serverless function metadata used by workflow DAG and schedulers."""

    name: str
    image: str
    base_duration_ms: int
    memory_mb: int = 128
    payload_bytes: int = 0
    retries: int = 0
