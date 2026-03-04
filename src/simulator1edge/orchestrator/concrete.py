from __future__ import annotations
from typing import Union

from simulator1edge.application.base import Application, Image, Microservice
from simulator1edge.device.base import Device
from simulator1edge.infrastructure.base import ComputingInfrastructure
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.base import Orchestrator
from simulator1edge.policies.domain import (
    DomainSelectionPolicy,
    SequentialDomainSelectionPolicy,
)
from simulator1edge.policies.placement import (
    FirstCandidatePlacementPolicy,
    TargetSelectionPolicy,
)
from simulator1edge.util.logs import logs


class ContinuumOrchestrator(Orchestrator):
    def __init__(self, computing_infrastructures: list[ComputingInfrastructure], network: Network,
                 domain_selection_strategy: DomainSelectionPolicy | None = None):
        super().__init__(computing_infrastructures, network)
        self._computing_infrastructures = computing_infrastructures
        self._domain_selection_strategy = domain_selection_strategy or SequentialDomainSelectionPolicy()

    def deploy(self, application: Application) -> bool:
        result = True
        for service in application.components:
            target_infrastructure = self._domain_selection_strategy.select_domain(
                service, self._computing_infrastructures
            )
            if target_infrastructure is None:
                return False
            result = result and target_infrastructure.orchestrator.deploy([service])
        return result

class DomainOrchestrator(Orchestrator):
    def __init__(self, devices: list[Device], network: Network,
                 target_selection_strategy: TargetSelectionPolicy | None = None):
        super().__init__(devices, network)
        self._target_selection_strategy = target_selection_strategy or FirstCandidatePlacementPolicy()

    def deploy(self, services: list[Microservice]) -> bool:
        result: bool = True
        for service in services:
            if not self.can_deploy(service):
                return False
            candidate_resources = self.list_of_candidates(service)
            logs.info("Candidate resources for %s found %s", service.name,
                      ", ".join(i.name for i in candidate_resources))
            image_locations = self._find_image(service.image.name)
            result = result and self._place_service(service, candidate_resources, image_locations)
        return result

    def can_deploy(self, service: Microservice) -> bool:
        has_candidate = len(self.list_of_candidates(service)) > 0
        has_image_location = len(self._find_image(service.image.name)[0]) > 0
        return has_candidate and has_image_location

    def list_of_candidates(self, ms: Microservice) -> list[Device]:
        suitable_devices = \
            [d for d in self.resources
             if Orchestrator.is_device_satisfying_all_requirements(d, ms.requirements)
             and (Orchestrator.is_device_having_the_image_locally(d, ms.image) or
                  Orchestrator.is_device_having_room_for_storing_the_image(d, ms.image))]
        return suitable_devices

    # TODO add the second part: image located outside the cloud
    def _find_image(self, image_name) -> tuple[list[Device], list[Union[Device, ComputingInfrastructure]] | None]:
        image_locations: list = [i for i in self.resources if image_name in i.images]
        return image_locations, None

    # TODO consider to create the interface ImageSource to unify devices and computing infrastructures
    # TODO import images from computing infrastructures
    def _find_best_image_location(self, target: Device, image: Image,
                                  locations: tuple[list[Device], list[Union[Device, ComputingInfrastructure]] | None]) \
            -> Union[Device, ComputingInfrastructure]:

        # if the image is available locally, pick one from that set; otherwise the first of the rest
        if locations[0]:
            return locations[0].pop()
        else:
            # take the first in the list of source outside the local ComputingInfrastructure
            source = locations[1].pop()

            # determine if it is a device or a ComputingInfrastructure
            if isinstance(source, Device):
                return source
            elif isinstance(source, ComputingInfrastructure):
                raise NotImplementedError("Retrieving images from ComputingInfrastructure still has to be implemented")
            else:
                raise TypeError("Image source location should be either a device or a computing infrastructure.")

    def _place_service(self, service: Microservice, candidate_resources: list[Device],
                       image_locations: tuple[list[Device], list[Union[Device, ComputingInfrastructure]] | None]) -> bool:
        """ This method actually places services to the target device.

        If the image is not already present into the target device it is transferred into it retrieving it from a
        proper source.
        """

        # extract the target device
        assert candidate_resources, "No candidate resources available for deployment."
        target = self._target_selection_strategy.select_target(service, candidate_resources)
        candidate_resources = [candidate for candidate in candidate_resources if candidate != target]

        assert target.has_enough_space_for_image(service.image.storage_space_requirements().rd.value) \
               or target.has_image(service.image.name), "Target device must either have the image locally stored or" \
                                                   "enough room for storing it."

        assert image_locations[0] or image_locations[1], "There must be at least one instance the image available."

        # find the best image instance given the target device
        best_location = self._find_best_image_location(target, service.image, image_locations)

        # let the target device retrieve the image
        successfully_retrieved = True
        if target != best_location and not target.has_image(service.image.name):
            successfully_retrieved = target.retrieve_image_from(service.image, best_location)

        if target != best_location:
            print(target.name + " " + best_location.name + " - " + str(self.network.bandwidth(target, best_location)))

        assert successfully_retrieved, f"Device {target} was not able to retrieve " \
                                       f"image {service.image.name} from {best_location}."

        # start the service
        successfully_started = target.start_microservice(service)

        assert successfully_started, f"Device {target} was not able to start microservice " \
                                       f"image {service.name}."

        return True


class CloudOrchestrator(DomainOrchestrator):
    def __init__(self, cloud_resources: list[Device], network: Network,
                 target_selection_strategy: TargetSelectionPolicy | None = None):
        super().__init__(cloud_resources, network, target_selection_strategy=target_selection_strategy)

    def deploy(self, services: list[Microservice]) -> bool:
        return super().deploy(services)


class EdgeOrchestrator(DomainOrchestrator):
    def __init__(self, edge_resources: list[Device], network: Network,
                 target_selection_strategy: TargetSelectionPolicy | None = None):
        super().__init__(edge_resources, network, target_selection_strategy=target_selection_strategy)

    def deploy(self, services: list[Microservice]) -> bool:
        return super().deploy(services)
