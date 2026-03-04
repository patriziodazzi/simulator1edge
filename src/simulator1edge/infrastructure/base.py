from __future__ import annotations

import abc

from simulator1edge.device.base import Device
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.base import Orchestrator


class ComputingInfrastructure(abc.ABC):
    def __init__(self, devices: list[Device], orchestrator: Orchestrator, network: Network):
        self._devices = devices
        self._orchestrator = orchestrator
        self._network = network

    @property
    def devices(self) -> list[Device]:
        return self._devices

    @devices.setter
    def devices(self, value: list[Device]):
        self._devices = value

    @property
    def orchestrator(self) -> Orchestrator:
        return self._orchestrator

    @orchestrator.setter
    def orchestrator(self, value: Orchestrator):
        self._orchestrator = value

    @property
    def network(self) -> Network:
        return self._network

    @network.setter
    def network(self, value: Network):
        self._network = value
