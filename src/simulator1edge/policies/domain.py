from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from simulator1edge.application.base import Microservice
    from simulator1edge.infrastructure.base import ComputingInfrastructure


class DomainSelectionPolicy(Protocol):
    """Strategy interface for selecting a target infrastructure/domain."""

    def select_domain(
        self,
        service: Microservice,
        infrastructures: list[ComputingInfrastructure],
    ) -> ComputingInfrastructure | None:
        raise NotImplementedError


class SequentialDomainSelectionPolicy:
    """Minimal default policy: pick the first domain that can deploy the service."""

    def select_domain(
        self,
        service: Microservice,
        infrastructures: list[ComputingInfrastructure],
    ) -> ComputingInfrastructure | None:
        for infrastructure in infrastructures:
            orchestrator = infrastructure.orchestrator
            if hasattr(orchestrator, "can_deploy") and orchestrator.can_deploy(service):
                return infrastructure
        return None
