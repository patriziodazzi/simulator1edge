from __future__ import annotations

from collections import deque

from simulator1edge.workflow.model import FunctionSpec


class WorkflowDAG:
    """Directed acyclic graph of serverless functions."""

    def __init__(self, name: str):
        self._name = name
        self._nodes: dict[str, FunctionSpec] = {}
        self._successors: dict[str, set[str]] = {}
        self._predecessors: dict[str, set[str]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def nodes(self) -> dict[str, FunctionSpec]:
        return self._nodes

    def add_node(self, node: FunctionSpec) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Node '{node.name}' already exists in workflow '{self.name}'.")
        self._nodes[node.name] = node
        self._successors[node.name] = set()
        self._predecessors[node.name] = set()

    def add_dependency(self, source: str, target: str) -> None:
        if source not in self._nodes or target not in self._nodes:
            raise ValueError("Both source and target nodes must exist before adding dependencies.")
        self._successors[source].add(target)
        self._predecessors[target].add(source)
        self.validate_acyclic()

    def predecessors_of(self, node_name: str) -> set[str]:
        self._ensure_node(node_name)
        return set(self._predecessors[node_name])

    def successors_of(self, node_name: str) -> set[str]:
        self._ensure_node(node_name)
        return set(self._successors[node_name])

    def topological_layers(self) -> list[list[str]]:
        indegree: dict[str, int] = {name: len(preds) for name, preds in self._predecessors.items()}
        ready = deque(sorted([name for name, degree in indegree.items() if degree == 0]))
        layers: list[list[str]] = []
        visited = 0

        while ready:
            layer_size = len(ready)
            layer: list[str] = []
            for _ in range(layer_size):
                node_name = ready.popleft()
                layer.append(node_name)
                visited += 1
                for successor in sorted(self._successors[node_name]):
                    indegree[successor] -= 1
                    if indegree[successor] == 0:
                        ready.append(successor)
            layers.append(layer)

        if visited != len(self._nodes):
            raise ValueError(f"Workflow '{self.name}' contains a cycle.")
        return layers

    def validate_acyclic(self) -> None:
        self.topological_layers()

    def _ensure_node(self, node_name: str) -> None:
        if node_name not in self._nodes:
            raise ValueError(f"Node '{node_name}' not found in workflow '{self.name}'.")
