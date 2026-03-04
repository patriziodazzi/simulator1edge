from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

from simulator1edge.runtime.container_pool import ContainerPool
from simulator1edge.workflow.engine import FunctionExecutionResult
from simulator1edge.workflow.model import FunctionSpec


class ImageCache:
    """Simple image cache with optional max-size and LRU eviction."""

    def __init__(self, image_pull_latency_ms: int = 50, max_images: int | None = None):
        self._image_pull_latency_ms = image_pull_latency_ms
        self._max_images = max_images
        self._cache: OrderedDict[str, None] = OrderedDict()
        self.cache_hits = 0
        self.cache_misses = 0
        self.evictions = 0

    def ensure_image(self, image_name: str) -> int:
        """Return additional latency due to image pull."""
        if image_name in self._cache:
            self._cache.move_to_end(image_name)
            self.cache_hits += 1
            return 0

        self.cache_misses += 1
        self._cache[image_name] = None
        if self._max_images is not None and len(self._cache) > self._max_images:
            self._cache.popitem(last=False)
            self.evictions += 1
        return self._image_pull_latency_ms


@dataclass(frozen=True)
class ServerlessRuntimeMetrics:
    cold_starts: int
    warm_starts: int
    image_cache_hits: int
    image_cache_misses: int
    image_cache_evictions: int
    pool_expired_evictions: int
    pool_capacity_misses: int


class ServerlessRuntime:
    """Runtime model for function invocation with cold/warm and image caching effects."""

    def __init__(
        self,
        cold_start_overhead_ms: int = 150,
        warm_ttl_ms: int = 300_000,
        image_pull_latency_ms: int = 50,
        max_cached_images: int | None = None,
        max_containers_per_image: int | None = None,
    ):
        self._cold_start_overhead_ms = cold_start_overhead_ms
        self._pool = ContainerPool(
            warm_ttl_ms=warm_ttl_ms,
            max_containers_per_image=max_containers_per_image,
        )
        self._image_cache = ImageCache(
            image_pull_latency_ms=image_pull_latency_ms,
            max_images=max_cached_images,
        )

    def invoke(self, function: FunctionSpec, start_ms: int) -> FunctionExecutionResult:
        image_pull_ms = self._image_cache.ensure_image(function.image)
        cold_start, _container_id = self._pool.checkout(
            function.image, start_ms, expected_duration_ms=function.base_duration_ms
        )
        startup_ms = self._cold_start_overhead_ms if cold_start else 0
        total_latency = function.base_duration_ms + startup_ms + image_pull_ms
        mode = "cold" if cold_start else "warm"
        details = f"{mode}_start,image_pull_ms={image_pull_ms}"
        return FunctionExecutionResult(
            status="success",
            latency_ms=total_latency,
            cold_start=cold_start,
            details=details,
        )

    def metrics(self) -> ServerlessRuntimeMetrics:
        return ServerlessRuntimeMetrics(
            cold_starts=self._pool.cold_misses,
            warm_starts=self._pool.warm_hits,
            image_cache_hits=self._image_cache.cache_hits,
            image_cache_misses=self._image_cache.cache_misses,
            image_cache_evictions=self._image_cache.evictions,
            pool_expired_evictions=self._pool.expired_evictions,
            pool_capacity_misses=self._pool.capacity_misses,
        )
