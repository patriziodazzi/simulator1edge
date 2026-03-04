from __future__ import annotations

from simulator1edge.resource.requirement import Requirement, StorageSpaceRequirement


class Volume(object):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


class Image(object):

    # TODO: consider to decouple images from Image descriptors
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.stored_in_device = None
        self.in_use_on_this_device = False
        self._storage_space_requirements = StorageSpaceRequirement(size)

    def storage_space_requirements(self) -> Requirement:
        return self._storage_space_requirements


class Microservice(object):

    def __init__(self, name: str, requirements: list[Requirement], image: Image, has_volumes: bool = False,
                 volumes: list[Volume] | None = None, batch: bool = False, length: int = -1):
        # Mandatory arguments (name, requirement, image)
        self._requirements = requirements
        self._name = name
        self._image = image

        # References to volumes (if any)
        if volumes is None:
            volumes = []
        if has_volumes != (len(volumes) > 0):
            raise ValueError("Error in the setting of Microservice volumes")
        self._has_volumes = has_volumes
        self._volumes = list(volumes)

        # Information about length (if batch)
        if batch != (length > 0):
            raise ValueError("Error in the setting of Microservice length")
        self._batch = batch
        self._length = length

        self._id = id(self)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def requirements(self) -> list[Requirement]:
        return self._requirements

    @property
    def image(self) -> Image:
        return self._image

    @property
    def volumes(self) -> list[Volume]:
        return self._volumes

    def length(self) -> int:
        return self._length

    def has_volumes(self) -> bool:
        return self._has_volumes

    def is_batch(self) -> bool:
        return self._batch


class Application(object):
    def __init__(self, name: str, components: list[Microservice]):
        self._components = components
        self._name = name

    @property
    def components(self) -> list[Microservice]:
        return self._components

    @property
    def name(self) -> str:
        return self._name

    def get_components(self) -> list[Microservice]:
        return self._components

    def get_name(self) -> str:
        return self._name
