from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WarmContainer:
    container_id: str
    image: str
    busy_until_ms: int
    expires_at_ms: int
    last_used_ms: int


class ContainerPool:
    """Container pool implementing warm reuse with TTL-based expiration."""

    def __init__(self, warm_ttl_ms: int = 300_000, max_containers_per_image: int | None = None):
        self._warm_ttl_ms = warm_ttl_ms
        self._max_containers_per_image = max_containers_per_image
        self._containers_by_image: dict[str, list[WarmContainer]] = {}
        self._counter = 0

        self.warm_hits = 0
        self.cold_misses = 0
        self.expired_evictions = 0
        self.capacity_misses = 0

    def checkout(self, image: str, now_ms: int, expected_duration_ms: int) -> tuple[bool, str]:
        """Return (cold_start, container_id)."""
        self._evict_expired(now_ms)
        image_containers = self._containers_by_image.setdefault(image, [])

        reusable = [
            container
            for container in image_containers
            if container.busy_until_ms <= now_ms and container.expires_at_ms > now_ms
        ]
        if reusable:
            reusable.sort(key=lambda container: container.last_used_ms)
            container = reusable[0]
            container.busy_until_ms = now_ms + expected_duration_ms
            container.expires_at_ms = container.busy_until_ms + self._warm_ttl_ms
            container.last_used_ms = now_ms
            self.warm_hits += 1
            return False, container.container_id

        if self._max_containers_per_image is not None and len(image_containers) >= self._max_containers_per_image:
            # Capacity reached and no reusable warm container: invocation is a cold miss not retained in pool.
            self.cold_misses += 1
            self.capacity_misses += 1
            return True, self._new_ephemeral_id(image)

        container = self._new_pooled_container(image, now_ms, expected_duration_ms)
        image_containers.append(container)
        self.cold_misses += 1
        return True, container.container_id

    def _new_pooled_container(self, image: str, now_ms: int, expected_duration_ms: int) -> WarmContainer:
        self._counter += 1
        busy_until_ms = now_ms + expected_duration_ms
        return WarmContainer(
            container_id=f"{image}-ctr-{self._counter}",
            image=image,
            busy_until_ms=busy_until_ms,
            expires_at_ms=busy_until_ms + self._warm_ttl_ms,
            last_used_ms=now_ms,
        )

    def _new_ephemeral_id(self, image: str) -> str:
        self._counter += 1
        return f"{image}-ephemeral-{self._counter}"

    def _evict_expired(self, now_ms: int) -> None:
        for image in list(self._containers_by_image.keys()):
            containers = self._containers_by_image[image]
            kept = [container for container in containers if container.expires_at_ms > now_ms]
            self.expired_evictions += len(containers) - len(kept)
            if kept:
                self._containers_by_image[image] = kept
            else:
                del self._containers_by_image[image]
