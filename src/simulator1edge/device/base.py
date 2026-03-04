from __future__ import annotations

import copy

from simulator1edge.application.base import Image, Microservice
from simulator1edge.resource.descriptor import ResourceDescriptor, ResourceType


class Device(object):
    _num_of_devices: int = 0

    def __init__(self, resources: list[ResourceDescriptor]):

        Device._num_of_devices += 1
        self._name = str("Device-" + str(Device._num_of_devices))
        self._resources: dict[ResourceType, ResourceDescriptor] = {copy.deepcopy(res.type): copy.deepcopy(res) for res
                                                                   in resources}

        self._images: dict[str, Image] = {}
        self.microservices: dict[str, Microservice] = {}

    def __str__(self):
        return self.name

    # private service methods
    def _allocate_space_for_image(self, img):
        new_space = int(self.resources[ResourceType.STORAGE].value) - img.size
        self.resources[ResourceType.STORAGE].value = new_space

    def _create_and_start_microservice(self, microservice):
        self._assign_resources_to_microservice(microservice)

    def _free_microservice_resources(self, microservice: Microservice):
        """Free resources allocated by a microservice."""
        # check if the device has enough resources to run the microservice
        if not self.has_microservice(microservice):
            raise ValueError(f"Microservice {microservice.name} not found on device {self.name}")

        for req in microservice.requirements:
            resource_availability = self.resources[req.resource_type]
            resource_availability += req.rd
            self.resources[req.resource_type] = resource_availability

    def _assign_resources_to_microservice(self, microservice):
        """Allocate resources for a microservice."""
        # check if the device has enough resources to run the microservice
        if not self.has_enough_resources_for_microservice(microservice):
            raise ValueError(f"Not enough resources on device {self.name} for microservice {microservice.name}")

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

    def has_image(self, name: str) -> bool:
        return name in self.images

    def get_image_with_name(self, name: str) -> Image:
        return self.images[name]

    def store_image(self, img: Image) -> bool:
        """Store an image on the device."""
        if self.has_image(img.name):
            return True

        if not self.has_enough_space_for_image(img.size):
            raise ValueError(
                f"Not enough space available on device {self.name} for Image {img.name}. "
                f"Check with has_enough_space_for_image() before storing.")

        self._allocate_space_for_image(img)
        self.images[img.name] = img
        return True

    def retrieve_image_from(self, image: Image, device: Device) -> bool:
        """Retrieve an image from another device."""
        # check if the source device has the image
        if not device.has_image(image.name):
            raise ValueError(
                f"Image {image.name} not available on device {device}. "
                f"Check with has_image() before retrieving.")

        img_descriptor: Image = device.get_image_with_name(image.name)

        if self.has_image(image.name):
            return True

        if not self.has_enough_space_for_image(img_descriptor.size):
            raise ValueError(
                f"Not enough space available on device {self.name} for Image {image.name}. "
                f"Check with has_enough_space_for_image() before retrieving.")

        self.store_image(img_descriptor)

        return True

    def get_microservice(self, microservice: Microservice) -> dict[str, Microservice]:
        output: dict[str, Microservice] = {}
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
        """Start a microservice on the device."""
        srv_img = microservice.image.name

        # check if image already available on the current machine
        if srv_img not in self.images:
            raise ValueError(
                f"Image {srv_img} not available on device {self.name}. "
                f"Check with has_image() before starting microservice.")

        # check if there are enough resources available on the device
        if not self.has_enough_resources_for_microservice(microservice):
            raise ValueError(
                f"Insufficient resources on device {self.name} for microservice {microservice.name}. "
                f"Check with has_enough_resources_for_microservice() before starting.")

        self._create_and_start_microservice(microservice)
        instance_key = f"{microservice.name}-{len(self.microservices) + 1}"
        self.microservices[instance_key] = microservice
        return True

    def terminate_microservice(self, microservice: Microservice) -> bool:
        """Terminate one running instance of a microservice and release its resources."""
        target_key = None
        for ms_id, ms in self.microservices.items():
            if ms.name == microservice.name:
                target_key = ms_id
                break

        if target_key is None:
            raise ValueError(f"Microservice {microservice.name} not found on device {self.name}")

        self._free_microservice_resources(self.microservices[target_key])
        del self.microservices[target_key]
        return True
