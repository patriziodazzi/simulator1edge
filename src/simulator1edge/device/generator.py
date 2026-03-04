from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from simulator1edge.device.base import Device
from simulator1edge.device.concrete import CloudDevice
from simulator1edge.resource.descriptor import ResourceDescriptor


class DeviceFactory(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def create_device_instances(self, features: dict[str, Any]) -> list[Device]:
        raise NotImplementedError("Subclasses must implement create_device_instances().")


class CloudDeviceFactory(DeviceFactory):

    CLD_NAM_FEAT = 'cloud_name'
    _STD_CLD_NAM_FEAT = 'generic_cloud'

    def __init__(self, description: list[tuple[list[ResourceDescriptor], int]], features: dict[str, Any] | None = None):
        super().__init__()
        self._description = description

    @property
    def description(self) -> list[tuple[list[ResourceDescriptor], int]]:
        return self._description

    @description.setter
    def description(self, description: list[tuple[list[ResourceDescriptor], int]]):
        self._description = description

    def create_device_instances(self, features: dict[str, Any]) -> list[Device]:

        cloud_name = CloudDeviceFactory._STD_CLD_NAM_FEAT
        provided_name = features.get(CloudDeviceFactory.CLD_NAM_FEAT)
        if provided_name:
            cloud_name = provided_name

        devices: list[Device] = []
        for device_template, device_cardinality in self.description:
            for i in range(device_cardinality):
                devices.append(CloudDevice(cloud_name, device_template))

        return devices
