import itertools
from typing import Any

import networkx as nx
import networkx.algorithms.operators.binary as nx_algo

from simulator1edge.device.base import Device
from simulator1edge.infrastructure.base import ComputingInfrastructure
from simulator1edge.network.base import Network


class EndToEndNetwork(Network):

    # TODO change parameters to encapsulate the graph
    def __init__(self, end_point_a: Device, end_point_b: Device, network_graph: nx.Graph, bandwidth: int):
        super().__init__()
        network_graph.add_node(end_point_a)
        network_graph.add_node(end_point_b)
        network_graph.add_edge(end_point_a, end_point_b, capacity=bandwidth)
        print(f"Linking {end_point_a} with {end_point_b} with a bandwidth of: {bandwidth}")


class ComputingContinuumNetwork(Network):
    TPLGY_FEAT = 'topology'
    LNK_BND_FEAT = 'link_bandwidth'
    CSTM_LNKS_FEAT = 'custom_links'

    CLIQ = 'clique'
    TORS = 'torus'
    CSTM = 'custom'

    _STD_TPLGY = CLIQ
    _STD_LNK_BND = 100

    def __init__(self, resources: list[ComputingInfrastructure]):
        super().__init__(None)
        self._resources = resources
        self._topology = ComputingContinuumNetwork._STD_TPLGY
        self._link_bandwidth = ComputingContinuumNetwork._STD_LNK_BND

    @property
    def resources(self) -> list[ComputingInfrastructure]:
        return self._resources

    @property
    def link_bandwidth(self) -> int:
        return self._link_bandwidth

    @link_bandwidth.setter
    def link_bandwidth(self, value: int):
        self._link_bandwidth = value

    # NOTE: with clique and torus, the link values are the same for all the links
    def do_link_computing_infrastructures(self, features: dict[str, Any] = None):

        if ComputingContinuumNetwork.TPLGY_FEAT in features:
            self._topology = features[ComputingContinuumNetwork.TPLGY_FEAT]

        if ComputingContinuumNetwork.LNK_BND_FEAT in features:
            self._link_bandwidth = features[ComputingContinuumNetwork.LNK_BND_FEAT]

        if self._topology == ComputingContinuumNetwork.CLIQ:
            for a in itertools.combinations(self.resources, 2):
                self.graph.add_edge(a[0].network.gateway, a[1].network.gateway, capacity=self.link_bandwidth)

        if self._topology == ComputingContinuumNetwork.TORS:
            idx: int = -1
            for idx in range(len(self.resources) - 1):
                self.graph.add_edge(self.resources[idx].network.gateway, self.resources[idx + 1].network.gateway, capacity=self.link_bandwidth)
            self.graph.add_edge(self.resources[idx + 1].network.gateway, self.resources[0].network.gateway, capacity=self.link_bandwidth)

        if self._topology == ComputingContinuumNetwork.CSTM:
            links = features[ComputingContinuumNetwork.CSTM_LNKS_FEAT]
            for (i, j, k) in links:
                self.graph.add_edge(self.resources[i].network.gateway, self.resources[j].network.gateway, capacity=k)

        graph = self.graph
        for computing_infrastructure in self.resources:
            graph = nx_algo.compose(graph, computing_infrastructure.network.graph)

        self.graph = graph
