from __future__ import annotations

import copy
import string
from simulator1edge.core import *
# from simulator1edge.application.base import Image, Microservice
# from simulator1edge.resource.descriptor import ResourceDescriptor, ResourceType
from simulator1edge.util.environment import Simulation


class Device(object):
    _num_of_devices: int = 0

    def __init__(self, resources: list[ResourceDescriptor]):

        Device._num_of_devices += 1
        self._name = str("Device-" + str(Device._num_of_devices))
        self._resources: dict[ResourceType, ResourceDescriptor] = {copy.deepcopy(res.type): copy.deepcopy(res) for res
                                                                   in resources}

        self._images: dict[string, Image] = {}
        self.microservices: dict[string, Microservice] = {}

    def __str__(self):
        return self.name

    # private service methods
    def _allocate_space_for_image(self, img):
        new_space = int(self.resources[ResourceType.STORAGE].value) - img.size
        self.resources[ResourceType.STORAGE].value = (str(new_space))

    def _create_and_start_microservice(self, microservice):
        self._assign_resources_to_microservice(microservice)

    # TODO: provide implementation
    def _free_microservice_resources(self, microservice: Microservice):

        # check if the device has enough resources to run the microservice
        assert self.has_microservice(microservice)

        for req in microservice.requirements:
            resource_availability = self.resources[req.resource_type]
            resource_availability += req.rd
            self.resources[req.resource_type] = resource_availability

    def _assign_resources_to_microservice(self, microservice):

        # check if the device has enough resources to run the microservice
        assert self.has_enough_resources_for_microservice(microservice)

        for req in microservice.requirements:
            resource_availability = self.resources[req.resource_type]
            resource_availability -= req.rd
            self.resources[req.resource_type] = resource_availability

    # public properties
    @property
    def name(self):
        return self._name

    @property
    def resources(self) -> dict[ResourceType, ResourceDescriptor]:
        return self._resources

    @resources.setter
    def resources(self, value: dict[ResourceType, ResourceDescriptor]):
        self._resources = value

    @property
    def images(self):
        return self._images

    def has_enough_space_for_image(self, size: int) -> bool:
        space = int(self.resources[ResourceType.STORAGE].value)
        return space >= size

    def has_enough_resources_for_microservice(self, microservice) -> bool:
        satisfied = True
        for req in microservice.requirements:
            satisfied = satisfied and req.is_satisfied_by_resource(self.resources.get(req.resource_type))
        return satisfied

    def has_image(self, name: string) -> bool:
        return name in self.images

    def get_image_with_name(self, name: string) -> Image:
        return self.images[name]

    # TODO check if image is already stored
    def store_image(self, img: Image) -> bool:

        if self.has_image(img.name):
            return True

        assert self.has_enough_space_for_image(img.size), \
            f"Not enough space available on device {self.name} for Image {img.name}, space availability should be " \
            f"checked with method has_enough_space_for image(image_name)."

        self._allocate_space_for_image(img)
        self.images[img.name] = img
        return True

    def retrieve_image_from(self, image: Image, device: Device) -> bool:

        # check if the source device has the image
        assert device.has_image(image.name), \
            f"Image {image.name} not available on device {device}, " \
            f"image availability should be checked with method has_image(image_name)."

        # Simulation().env.process()
        img_descriptor: Image = device.get_image_with_name(image.name)

        if self.has_image(image.name):
            return True

        assert self.has_enough_space_for_image(img_descriptor.size), \
            f"Not enough space available on device {self.name} for Image {image.name}, space availability should be " \
            f"checked with method has_enough_space_for image(image_name)."

        self.store_image(img_descriptor)

        return True

    def get_microservice(self, microservice: Microservice) -> dict[string, Microservice]:
        output: dict[string, Microservice] = {}
        for ms_id, ms in self.microservices.items():
            if ms.name == microservice.name:
                output[ms_id] = ms
        return output

    def has_microservice(self, microservice: Microservice) -> bool:
        for ms in self.microservices.values():
            if ms.name == microservice.name:
                return True

        return False

    def start_microservice(self, microservice: Microservice) -> bool:

        srv_img = microservice.image.name

        # check if image already available on the current machine
        assert srv_img in self.images, \
            f"Image {srv_img} not available on device {self.name}, " \
            f"image availability should be checked with method has_image(image_name) before starting any microservice."

        # check if there are enough resources available on the device
        assert self.has_enough_resources_for_microservice(microservice), \
            f"Resources not available on device {self.name} for microservice {microservice.name} " \
            f"resources availability should be checked with method " \
            f"has_enough_resources_for_microservice(microservice) before starting any microservice."

        # create microservice
        self._create_and_start_microservice(microservice)

        # store microservice handle in the internal data structure
        self.microservices[microservice.id] = microservice
        return True

    def terminate_microservice(self, microservice_handler: Microservice) -> bool:

        # TODO: we must check the ms is the last one to unpin image
        if microservice_handler.id in self.microservices:
            self._free_microservice_resources(self.microservices[microservice_handler.id])
            del self.microservices[microservice_handler.id]
            return True
        return False
