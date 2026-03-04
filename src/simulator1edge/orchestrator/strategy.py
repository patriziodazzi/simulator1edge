from __future__ import annotations

"""
Backward-compatible strategy aliases.

Use `simulator1edge.policies.*` for new integrations.
"""

from simulator1edge.policies.domain import (
    DomainSelectionPolicy as DomainSelectionStrategy,
    SequentialDomainSelectionPolicy as SequentialDomainSelection,
)
from simulator1edge.policies.placement import (
    FirstCandidatePlacementPolicy as FirstCandidateTargetSelection,
    TargetSelectionPolicy as TargetSelectionStrategy,
)

__all__ = [
    "DomainSelectionStrategy",
    "SequentialDomainSelection",
    "FirstCandidateTargetSelection",
    "TargetSelectionStrategy",
]
