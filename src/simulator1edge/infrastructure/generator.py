from __future__ import annotations

import abc

from abc import ABC, abstractmethod
from typing import Any, cast

from simulator1edge.device.base import Device
from simulator1edge.device.concrete import CloudDevice
from simulator1edge.infrastructure.base import ComputingInfrastructure
from simulator1edge.infrastructure.cluster import Cloud
from simulator1edge.infrastructure.continuum import ComputingContinuum
from simulator1edge.network.areanetwork import CloudAreaNetwork
from simulator1edge.network.core import ComputingContinuumNetwork
from simulator1edge.orchestrator.base import Orchestrator
from simulator1edge.orchestrator.concrete import CloudOrchestrator, ContinuumOrchestrator


class ComputingInfrastructureFactory(ABC):
    """Factory class for creating instances of ComputingInfrastructure and the associated orchestrator and network

    Methods
    -------
    __create_instance__()
        Creates instances of ComputingInfrastructure and the associated orchestrator and network.
    get_computing_infrastructure()
        Returns the ComputingInfrastructure created.
    get_orchestrator()
        Returns the Orchestrator associated to the ComputingInfrastructure.
    """

    NTWRK_FEAT = 'network'
    DEVS_FEAT = 'devices'
    ORCHS_FEAT = 'orchestrator'

    def __init__(self, features: dict[str, Any] = None) -> None:
        """
        Parameters
        ----------
        features : dict[str, Any], optional
            The name of the animal
        """

        self.features = features or {}

        if ComputingInfrastructureFactory.DEVS_FEAT in self.features:
            self._devices = self.features[ComputingInfrastructureFactory.DEVS_FEAT]
        else:
            self._devices = None

        # If network is provided, does not create it
        if ComputingInfrastructureFactory.NTWRK_FEAT in self.features:
            self._network = self.features[ComputingInfrastructureFactory.NTWRK_FEAT]
        else:
            self._network = None

        # If orchestrator is provided, does not create it
        if ComputingInfrastructureFactory.ORCHS_FEAT in self.features:
            self._orchestrator = self.features[ComputingInfrastructureFactory.ORCHS_FEAT]
        else:
            self._orchestrator = None

    @property
    def devices(self) -> list[Device]:
        return self._devices

    @devices.setter
    def devices(self, value: list[Device]):
        self._devices = value

    @property
    def orchestrator(self) -> Orchestrator:
        return self._orchestrator

    @orchestrator.setter
    def orchestrator(self, value: Orchestrator):
        self._orchestrator = value

    @property
    def network(self) -> CloudAreaNetwork:
        return self._network

    @network.setter
    def network(self, value: CloudAreaNetwork):
        self._network = value

    @abstractmethod
    def create_computing_instance(self) -> ComputingInfrastructure:
        raise NotImplementedError("You should implement this!")


class CloudFactory(ComputingInfrastructureFactory):
    # Standard Values
    _STD_INTL_NET_BNDWDTH = 100
    _STD_EXTL_NET_BNDWDTH = 100
    _STD_IS_RTD = True
    _STD_GTWY = None

    # Parameters Keys
    INTL_NET_BNDWDTH_FEAT = 'internal_bandwidth'
    EXTL_NET_BNDWDTH_FEAT = 'external_bandwidth'
    IS_RTD_FEAT = 'is_routed'
    GTWY_FEAT = 'gateway'

    def __init__(self, features: dict[str, Any] = None):
        super().__init__(features)

        # If internal_bandwidth is provided, uses it, otherwise uses the standard value
        if CloudFactory.INTL_NET_BNDWDTH_FEAT in self.features:
            self._internal_bandwidth = self.features[CloudFactory.INTL_NET_BNDWDTH_FEAT]
        else:
            self._internal_bandwidth = CloudFactory._STD_INTL_NET_BNDWDTH

        # If external_bandwidth is provided, uses it, otherwise uses the standard value
        if CloudFactory.EXTL_NET_BNDWDTH_FEAT in self.features:
            self._external_bandwidth = self.features[CloudFactory.EXTL_NET_BNDWDTH_FEAT]
        else:
            self._external_bandwidth = CloudFactory._STD_EXTL_NET_BNDWDTH

        # If is_routed is provided, uses it, otherwise uses the standard value
        if CloudFactory.IS_RTD_FEAT in self.features:
            self._is_routed = self.features[CloudFactory.IS_RTD_FEAT]
        else:
            self._is_routed = CloudFactory._STD_IS_RTD

        self._computing_infrastructure = None
        self._gateway = None

    @property
    def internal_bandwidth(self) -> int:
        return self._internal_bandwidth

    @internal_bandwidth.setter
    def internal_bandwidth(self, value: int):
        self._internal_bandwidth = value

    @property
    def external_bandwidth(self) -> int:
        return self._external_bandwidth

    @external_bandwidth.setter
    def external_bandwidth(self, value: int):
        self._external_bandwidth = value

    @property
    def is_routed(self) -> bool:
        return self._is_routed

    @is_routed.setter
    def is_routed(self, value: bool):
        self._is_routed = value

    @property
    def gateway(self) -> Device:
        return self._gateway

    @gateway.setter
    def gateway(self, value: Device):
        self._gateway = value

    @property
    def computing_infrastructure(self):
        return self._computing_infrastructure

    def create_computing_instance(self, instance_features: dict[str, Any] = None) -> ComputingInfrastructure:

        if instance_features:
            if ComputingInfrastructureFactory.DEVS_FEAT in instance_features:
                self._devices = instance_features[ComputingInfrastructureFactory.DEVS_FEAT]
            else:
                self._devices = None

            # If network is provided, does not create it
            if ComputingInfrastructureFactory.NTWRK_FEAT in instance_features:
                self._network = instance_features[ComputingInfrastructureFactory.NTWRK_FEAT]
            else:
                self._network = None

            # If orchestrator is provided, does not create it
            if ComputingInfrastructureFactory.ORCHS_FEAT in instance_features:
                self._orchestrator = instance_features[ComputingInfrastructureFactory.ORCHS_FEAT]
            else:
                self._orchestrator = None

        # If gateway is provided, uses it, otherwise uses the standard value
        if CloudFactory.GTWY_FEAT in self.features:
            self._gateway = self.features[CloudFactory.GTWY_FEAT]
        else:
            self._gateway = CloudFactory._STD_GTWY

        if instance_features:
            # If gateway is provided, uses it, otherwise uses the standard value
            if CloudFactory.GTWY_FEAT in instance_features:
                self._gateway = instance_features[CloudFactory.GTWY_FEAT]
            else:
                self._gateway = CloudFactory._STD_GTWY

        # if network has not been provided, creates it
        if not self.network:

            # If gateway is provided, specifies it, otherwise uses the shorter constructor
            if self.gateway:
                self.network = CloudAreaNetwork(cast(list[CloudDevice], self.devices), self.internal_bandwidth,
                                                self.external_bandwidth, self.is_routed, self.gateway)
            else:
                self.network = CloudAreaNetwork(cast(list[CloudDevice], self.devices), self.internal_bandwidth,
                                                self.external_bandwidth, self.is_routed)

        # if orchestrator has not been provided, creates it
        if not self.orchestrator:
            # If orchestrator is provided, specifies it, otherwise uses the shorter constructor
            self.orchestrator = CloudOrchestrator(cast(list[CloudDevice], self.devices), self.network)

        self._computing_infrastructure = Cloud(cast(list[CloudDevice], self.devices),
                                               cast(CloudOrchestrator, self.orchestrator), self.network)

        return self._computing_infrastructure


class IComputingContinuumBuilder(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError("Subclasses must implement __init__().")

    @abc.abstractmethod
    def create_network(self, features: dict[str, Any]):
        raise NotImplementedError("Subclasses must implement create_network().")

    @abc.abstractmethod
    def create_orchestrator(self, features: dict[str, Any]):
        raise NotImplementedError("Subclasses must implement create_orchestrator().")

    @abc.abstractmethod
    def create_continuum(self, features: dict[str, Any]):
        raise NotImplementedError("Subclasses must implement create_continuum().")

    @abc.abstractmethod
    def result(self):
        raise NotImplementedError("Subclasses must implement result.")


class ComputingContinuumBuildDirector(object):
    CMP_CNT_RES_FEAT = 'computing_continuum_resources'

    def __init__(self, builder: IComputingContinuumBuilder):
        self._builder = builder

    def construct(self, features: dict[str, Any]):
        self._builder.create_network(features)
        self._builder.create_orchestrator(features)
        self._builder.create_continuum(features)

    @property
    def result(self):
        return self._builder.result


class ComputingContinuumBuilder(IComputingContinuumBuilder):

    def __init__(self):
        self._orchestrator = None
        self._network = None
        self._resources = None
        self._computing_infrastructure = None

    def create_network(self, features: dict[str, Any]):
        self._resources: list[ComputingInfrastructure] = features[ComputingContinuumBuildDirector.CMP_CNT_RES_FEAT]
        self._network = ComputingContinuumNetwork(self._resources)
        self._network.do_link_computing_infrastructures(
            {ComputingContinuumNetwork.TPLGY_FEAT: ComputingContinuumNetwork.CLIQ})

    def create_orchestrator(self, features: dict[str, Any]):
        self._orchestrator = ContinuumOrchestrator(self._resources, self._network)

    def create_continuum(self, features: dict[str, Any]):
        self._computing_infrastructure = ComputingContinuum(self._resources, self._orchestrator, self._network)

    @property
    def result(self):
        return self._computing_infrastructure
