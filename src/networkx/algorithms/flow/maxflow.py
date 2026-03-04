from __future__ import annotations

from collections import deque


# Fallback: compute widest-path capacity (maximin) for undirected graph.
def maximum_flow_value(graph, src, dst):
    if src == dst:
        return 0

    best = {src: float("inf")}
    q = deque([src])

    while q:
        node = q.popleft()
        current = best[node]
        for neigh, capacity in graph.neighbors(node):
            candidate = min(current, capacity)
            if candidate > best.get(neigh, -1):
                best[neigh] = candidate
                q.append(neigh)

    return 0 if dst not in best else best[dst]
