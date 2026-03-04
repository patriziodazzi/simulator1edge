from __future__ import annotations

# from simulator1edge.application.base import Microservice, Image
# from simulator1edge.device.base import Device
# from simulator1edge.network.base import Network
# from simulator1edge.resource.requirement import Requirement

from simulator1edge.core import *


class Orchestrator(object):
    def __init__(self, resources: list, network: Network):
        self._network = network
        self._resources = resources

    @property
    def resources(self):
        return self._resources

    @property
    def network(self):
        return self._network

    def list_of_candidates(self, ms: Microservice) -> list:
        raise NotImplementedError("Subclasses must implement list_of_candidates().")

    @staticmethod
    def is_device_satisfying_requirement(dev: Device, req: Requirement) -> bool:
        available_resources = dev.resources

        actual_resource = None
        for i_rt, i_rd in available_resources.items():
            if i_rt == req.rd.type:
                actual_resource = i_rd

        if not actual_resource:
            return False

        return req.is_satisfied_by_resource(actual_resource)

    @staticmethod
    def is_device_satisfying_all_requirements(dev: Device, rs: list[Requirement]) -> bool:
        return all(map(lambda r: Orchestrator.is_device_satisfying_requirement(dev, r), rs))

    @classmethod
    def is_device_having_the_image_locally(cls, dev: Device, image: Image):
        return dev.has_image(image.name)

    @classmethod
    def is_device_having_room_for_storing_the_image(cls, dev: Device, image: Image):
        return dev.has_enough_space_for_image(image.storage_space_requirements().rd.value)
