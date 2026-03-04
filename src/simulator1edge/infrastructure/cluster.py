from __future__ import annotations

from simulator1edge.device.base import Device
from simulator1edge.infrastructure.base import ComputingInfrastructure
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.base import Orchestrator


class Cloud(ComputingInfrastructure):
    def __init__(self, devices: list[Device], orchestrator: Orchestrator, network: Network):
        super().__init__(devices, orchestrator, network)


class EdgeCluster(ComputingInfrastructure):
    def __init__(self, devices: list[Device], orchestrator: Orchestrator, network: Network):
        super().__init__(devices, orchestrator, network)
