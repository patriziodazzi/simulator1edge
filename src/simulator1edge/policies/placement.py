from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from simulator1edge.resource.descriptor import ResourceType

if TYPE_CHECKING:
    from simulator1edge.application.base import Microservice
    from simulator1edge.device.base import Device


class TargetSelectionPolicy(Protocol):
    """Strategy interface for selecting a target device among candidates."""

    def select_target(self, service: Microservice, candidates: list[Device]) -> Device:
        raise NotImplementedError


class FirstCandidatePlacementPolicy:
    """Minimal default policy: select the first candidate."""

    def select_target(self, service: Microservice, candidates: list[Device]) -> Device:
        if not candidates:
            raise ValueError("No candidate resources available for deployment.")
        return candidates[0]


class MostFreeMemoryPlacementPolicy:
    """Select the candidate with the highest currently available memory."""

    def _available_memory(self, device: Device) -> int:
        descriptor = device.resources.get(ResourceType.MEMORY_AMOUNT)
        if descriptor is None:
            return -1
        return int(descriptor.value)

    def select_target(self, service: Microservice, candidates: list[Device]) -> Device:
        if not candidates:
            raise ValueError("No candidate resources available for deployment.")
        return max(candidates, key=self._available_memory)


class LeastLoadedPlacementPolicy:
    """Select the candidate with the lowest number of running microservice instances."""

    def _load(self, device: Device) -> int:
        return len(device.microservices)

    def select_target(self, service: Microservice, candidates: list[Device]) -> Device:
        if not candidates:
            raise ValueError("No candidate resources available for deployment.")
        return min(candidates, key=self._load)
