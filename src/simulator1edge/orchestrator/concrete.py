from __future__ import annotations
from typing import Union, cast

from simulator1edge.util.logs import logs
# from simulator1edge.application.base import Application, Microservice, Image
# from simulator1edge.infrastructure.cluster import ComputingInfrastructure
# from simulator1edge.device.base import Device
# from simulator1edge.network.base import Network
# from simulator1edge.orchestrator.base import Orchestrator

from simulator1edge.core import *


class ContinuumOrchestrator(Orchestrator):
    def __init__(self, computing_infrastructures: list[ComputingInfrastructure], network: Network):
        super().__init__(computing_infrastructures, network)
        self._computing_infrastructures = computing_infrastructures

    def deploy(self, application: Application) -> bool:
        for service in application.components:
            deployed = False
            for infrastructure in self.resources:
                orchestrator = cast(Orchestrator, infrastructure.orchestrator)
                candidates = orchestrator.list_of_candidates(service)
                if not candidates:
                    continue
                if orchestrator.deploy([service]):
                    deployed = True
                    break

            if not deployed:
                logs.warning("Unable to deploy service %s on any infrastructure", service.name)
                return False

        return True


class DomainOrchestrator(Orchestrator):
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"

    def __init__(self, devices: list[Device], network: Network, placement_strategy: str = FIRST_FIT):
        super().__init__(devices, network)
        self._placement_strategy = placement_strategy

    @property
    def placement_strategy(self) -> str:
        return self._placement_strategy

    def deploy(self, services: list[Microservice]) -> bool:
        result: bool = True
        for service in services:
            candidate_resources = self.list_of_candidates(service)
            logs.info("Candidate resources for %s found %s", service.name,
                      ", ".join(i.name for i in candidate_resources))
            image_locations = self._find_image(service.image.name)
            if not candidate_resources:
                logs.warning("No candidate resources available for service %s", service.name)
                return False
            if not image_locations[0] and not image_locations[1]:
                logs.warning("No image location found for service %s", service.name)
                return False
            result = result and self._place_service(service, candidate_resources, image_locations)
        return result

    def _select_target_device(self, service: Microservice, candidate_resources: list[Device]) -> Device:
        if self.placement_strategy == DomainOrchestrator.BEST_FIT:
            # choose the candidate with the least remaining MEMORY after deployment (best fit)
            mem_req = 0
            for req in service.requirements:
                if req.resource_type == ResourceType.MEMORY_AMOUNT:
                    mem_req = int(req.rd.value)
                    break

            def score(device: Device):
                available = int(device.resources[ResourceType.MEMORY_AMOUNT].value)
                return available - mem_req

            return min(candidate_resources, key=score)

        # default: first fit preserves previous behavior
        return candidate_resources[-1]

    def list_of_candidates(self, ms: Microservice) -> list[Device]:
        suitable_devices = \
            [d for d in self.resources
             if Orchestrator.is_device_satisfying_all_requirements(d, ms.requirements)
             and (Orchestrator.is_device_having_the_image_locally(d, ms.image) or
                  Orchestrator.is_device_having_room_for_storing_the_image(d, ms.image))]
        return suitable_devices

    # TODO add the second part: image located outside the cloud
    def _find_image(self, image_name) -> tuple[list[Device], list[Union[Device, ComputingInfrastructure]]]:
        image_locations: list[Device] = [i for i in self.resources if (image_name in cast(Device, i).images)]
        return image_locations, []

    # TODO consider to create the interface ImageSource to unify devices and computing infrastructures
    # TODO import images from computing infrastructures
    def _find_best_image_location(self, target: Device, image: Image,
                                  locations: (list[Device], list[Union[Device, ComputingInfrastructure]])) \
            -> Union[Device, ComputingInfrastructure]:

        # if the image is available locally, pick one from that set; otherwise the first of the rest
        if locations[0]:
            return locations[0].pop()
        else:
            # take the first in the list of source outside the local ComputingInfrastructure
            if not locations[1]:
                raise ValueError(f"No image source available for target {target} and image {image.name}.")
            source = locations[1].pop()

            # determine if it is a device or a ComputingInfrastructure
            if isinstance(source, Device):
                return source
            elif isinstance(source, ComputingInfrastructure):
                raise NotImplementedError("Retrieving images from ComputingInfrastructure still has to be implemented")
            else:
                raise TypeError("Image source location should be either a device or a computing infrastructure.")

    def _place_service(self, service: Microservice, candidate_resources: list[Device],
                       image_locations: (list[Device], list[Union[Device, ComputingInfrastructure]])) -> bool:
        """ This method actually places services to the target device.

        If the image is not already present into the target device it is transferred into it retrieving it from a
        proper source.
        """

        # extract the target device
        assert candidate_resources, "No candidate resources available for deployment."
        target = candidate_resources.pop()

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
    def __init__(self, cloud_resources: list[Device], network: Network, placement_strategy: str = DomainOrchestrator.FIRST_FIT):
        super().__init__(cloud_resources, network, placement_strategy)

    def deploy(self, services: list[Microservice]) -> bool:
        return super().deploy(services)


class EdgeOrchestrator(DomainOrchestrator):
    def __init__(self, edge_resources: list[Device], network: Network, placement_strategy: str = DomainOrchestrator.FIRST_FIT):
        super().__init__(edge_resources, network, placement_strategy)

    def deploy(self, services: list[Microservice]) -> bool:
        return super().deploy(services)
