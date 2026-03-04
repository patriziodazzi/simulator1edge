"""Minimal local fallback for a tiny subset of networkx used by simulator1edge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


class Graph:
    def __init__(self):
        self._nodes = set()
        self._adj: Dict[object, Dict[object, int]] = {}

    @property
    def nodes(self):
        return self._nodes

    def add_node(self, node):
        self._nodes.add(node)
        self._adj.setdefault(node, {})

    def add_edge(self, a, b, capacity=0):
        self.add_node(a)
        self.add_node(b)
        self._adj[a][b] = capacity
        self._adj[b][a] = capacity

    def remove_node(self, node):
        if node not in self._nodes:
            return
        self._nodes.remove(node)
        for n in list(self._adj.get(node, {}).keys()):
            self._adj[n].pop(node, None)
        self._adj.pop(node, None)

    def neighbors(self, node):
        return self._adj.get(node, {}).items()


class _NxPydot:
    @staticmethod
    def graphviz_layout(graph: Graph, prog: str = "neato"):
        # deterministic simple layout on a line
        return {node: (idx, 0) for idx, node in enumerate(graph.nodes)}


nx_pydot = _NxPydot()


def draw(graph: Graph, **kwargs):
    # no-op fallback renderer
    return None
