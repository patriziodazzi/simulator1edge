import networkx as nx
import networkx.algorithms.flow.maxflow as mf

from simulator1edge.device.base import Device


class Network(object):

    def __init__(self, gateway: Device = None):
        self._graph = nx.Graph()
        self._gateway = gateway

    @property
    def graph(self) -> nx.Graph:
        return self._graph

    @graph.setter
    def graph(self, value: nx.Graph):
        self._graph = value

    @property
    def gateway(self) -> Device:
        return self._gateway

    @gateway.setter
    def gateway(self, value: Device):
        self._gateway = value

    def bandwidth(self, src: Device, dest: Device):
        return mf.maximum_flow_value(self.graph, src, dest)
