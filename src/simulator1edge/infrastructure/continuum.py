from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx

from simulator1edge.infrastructure.base import ComputingInfrastructure
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.concrete import ContinuumOrchestrator


class ComputingContinuum(object):

    def __init__(self, datacenters: list[ComputingInfrastructure], orchestrator: ContinuumOrchestrator,
                 network: Network):
        self._datacenters = datacenters
        self._orchestrator = orchestrator
        self._network = network

    @property
    def datacenters(self) -> list[ComputingInfrastructure]:
        return self._datacenters

    @datacenters.setter
    def datacenters(self, value: list[ComputingInfrastructure]):
        self._datacenters = value

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, value):
        self._network = value

    @property
    def orchestrator(self) -> ContinuumOrchestrator:
        return self._orchestrator

    @orchestrator.setter
    def orchestrator(self, value: ContinuumOrchestrator):
        self._orchestrator = value

    def draw_continuum(self, filename: str):
        f = plt.figure()
        nx.draw(self.network.graph,
                pos=nx.nx_pydot.graphviz_layout(self.network.graph, prog="neato"),
                node_size=120, node_color='red', linewidths=0.01, font_size=6, font_weight='bold',
                with_labels=True, ax=f.add_subplot(111))
        f.savefig(filename)
