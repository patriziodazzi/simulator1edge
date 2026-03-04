from __future__ import annotations

from simulator1edge.policies.domain import (
    DomainSelectionPolicy,
    SequentialDomainSelectionPolicy,
)
from simulator1edge.policies.placement import (
    FirstCandidatePlacementPolicy,
    LeastLoadedPlacementPolicy,
    MostFreeMemoryPlacementPolicy,
    TargetSelectionPolicy,
)


PLACEMENT_POLICIES: dict[str, type[TargetSelectionPolicy]] = {
    "first_candidate": FirstCandidatePlacementPolicy,
    "least_loaded": LeastLoadedPlacementPolicy,
    "most_free_memory": MostFreeMemoryPlacementPolicy,
}

DOMAIN_POLICIES: dict[str, type[DomainSelectionPolicy]] = {
    "sequential": SequentialDomainSelectionPolicy,
}


def build_placement_policy(name: str) -> TargetSelectionPolicy:
    policy_cls = PLACEMENT_POLICIES.get(name)
    if policy_cls is None:
        available = ", ".join(sorted(PLACEMENT_POLICIES.keys()))
        raise ValueError(f"Unknown placement policy '{name}'. Available policies: {available}")
    return policy_cls()


def build_domain_policy(name: str) -> DomainSelectionPolicy:
    policy_cls = DOMAIN_POLICIES.get(name)
    if policy_cls is None:
        available = ", ".join(sorted(DOMAIN_POLICIES.keys()))
        raise ValueError(f"Unknown domain policy '{name}'. Available policies: {available}")
    return policy_cls()
