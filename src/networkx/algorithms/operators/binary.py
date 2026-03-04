from __future__ import annotations

from networkx import Graph


def compose(left: Graph, right: Graph) -> Graph:
    out = Graph()
    for n in left.nodes:
        out.add_node(n)
    for n in right.nodes:
        out.add_node(n)

    for src in left.nodes:
        for dst, capacity in left.neighbors(src):
            out.add_edge(src, dst, capacity=capacity)

    for src in right.nodes:
        for dst, capacity in right.neighbors(src):
            out.add_edge(src, dst, capacity=capacity)

    return out
