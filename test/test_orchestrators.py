from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.application.base import Application, Image, Microservice
from simulator1edge.device.concrete import CloudDevice
from simulator1edge.infrastructure.cluster import Cloud
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.concrete import CloudOrchestrator, ContinuumOrchestrator, EdgeOrchestrator
from simulator1edge.policies.domain import DomainSelectionPolicy
from simulator1edge.policies.placement import (
    LeastLoadedPlacementPolicy,
    MostFreeMemoryPlacementPolicy,
    TargetSelectionPolicy,
)
from simulator1edge.resource.descriptor import MemoryAmountResourceDescriptor as MEMORY
from simulator1edge.resource.descriptor import NetworkBandwidthResourceDescriptor as NET
from simulator1edge.resource.descriptor import StorageSpaceResourceDescriptor as STORAGE
from simulator1edge.resource.requirement import MemoryAmountRequirement as MEMreq
from simulator1edge.resource.requirement import NetworkBandwidthRequirement as NETreq
from simulator1edge.resource.requirement import StorageSpaceRequirement as STORAGEreq


def _device() -> CloudDevice:
    return CloudDevice("az1", [STORAGE("200"), NET("100"), MEMORY("100")])


def _link_devices(devices: list[CloudDevice]) -> Network:
    network = Network(gateway=devices[0])
    for i in range(len(devices)):
        for j in range(i + 1, len(devices)):
            network.graph.add_edge(devices[i], devices[j], capacity=100)
    return network


def _microservice(name: str, image_name: str) -> Microservice:
    image = Image(image_name, 10)
    requirements = [STORAGEreq("1"), NETreq("1"), MEMreq("10")]
    return Microservice(name, requirements, image)


def _cloud_with_orchestrator() -> tuple[Cloud, list[CloudDevice], CloudOrchestrator]:
    devices = [_device(), _device()]
    network = _link_devices(devices)
    orchestrator = CloudOrchestrator(devices, network)
    cloud = Cloud(devices, orchestrator, network)
    return cloud, devices, orchestrator


class OrchestratorsTests(unittest.TestCase):
    def test_custom_target_selection_strategy_is_used(self):
        class LastCandidateStrategy(TargetSelectionPolicy):
            def select_target(self, service: Microservice, candidates: list[CloudDevice]) -> CloudDevice:
                return candidates[-1]

        devices = [_device(), _device()]
        network = _link_devices(devices)
        orchestrator = CloudOrchestrator(devices, network, target_selection_strategy=LastCandidateStrategy())

        service = _microservice("custom-ms", "custom-img")
        devices[0].store_image(service.image)

        self.assertTrue(orchestrator.deploy([service]))
        self.assertTrue(devices[1].has_microservice(service))

    def test_most_free_memory_policy_selects_expected_device(self):
        lower_memory = CloudDevice("az1", [STORAGE("200"), NET("100"), MEMORY("40")])
        higher_memory = CloudDevice("az1", [STORAGE("200"), NET("100"), MEMORY("120")])
        devices = [lower_memory, higher_memory]
        network = _link_devices(devices)

        orchestrator = CloudOrchestrator(
            devices, network, target_selection_strategy=MostFreeMemoryPlacementPolicy()
        )
        service = _microservice("mem-ms", "mem-img")
        lower_memory.store_image(service.image)

        self.assertTrue(orchestrator.deploy([service]))
        self.assertTrue(higher_memory.has_microservice(service))

    def test_least_loaded_policy_selects_expected_device(self):
        device_a = _device()
        device_b = _device()
        devices = [device_a, device_b]
        network = _link_devices(devices)

        seeded = _microservice("seeded-ms", "seeded-img")
        device_b.store_image(seeded.image)
        self.assertTrue(device_b.start_microservice(seeded))

        service = _microservice("new-ms", "new-img")
        device_a.store_image(service.image)
        device_b.store_image(service.image)

        orchestrator = CloudOrchestrator(
            devices, network, target_selection_strategy=LeastLoadedPlacementPolicy()
        )
        self.assertTrue(orchestrator.deploy([service]))
        self.assertTrue(device_a.has_microservice(service))

    def test_edge_orchestrator_deploy_success(self):
        devices = [_device(), _device()]
        network = _link_devices(devices)
        orchestrator = EdgeOrchestrator(devices, network)

        service = _microservice("edge-ms", "edge-image")
        devices[0].store_image(service.image)

        self.assertTrue(orchestrator.deploy([service]))

    def test_continuum_orchestrator_deploy_success(self):
        cloud_a, devices_a, _ = _cloud_with_orchestrator()
        cloud_b, devices_b, _ = _cloud_with_orchestrator()

        service_1 = _microservice("svc-1", "img-1")
        service_2 = _microservice("svc-2", "img-2")
        devices_a[0].store_image(service_1.image)
        devices_b[0].store_image(service_2.image)

        continuum_network = Network(gateway=devices_a[0])
        continuum_network.graph.add_edge(cloud_a.network.gateway, cloud_b.network.gateway, capacity=100)
        continuum_orchestrator = ContinuumOrchestrator([cloud_a, cloud_b], continuum_network)
        application = Application("app", [service_1, service_2])

        self.assertTrue(continuum_orchestrator.deploy(application))

    def test_continuum_orchestrator_returns_false_when_no_local_image(self):
        cloud_a, devices_a, _ = _cloud_with_orchestrator()
        cloud_b, _, _ = _cloud_with_orchestrator()

        service = _microservice("svc-1", "img-missing")
        continuum_network = Network(gateway=devices_a[0])
        continuum_network.graph.add_edge(cloud_a.network.gateway, cloud_b.network.gateway, capacity=100)
        continuum_orchestrator = ContinuumOrchestrator([cloud_a, cloud_b], continuum_network)
        application = Application("app", [service])

        self.assertFalse(continuum_orchestrator.deploy(application))

    def test_custom_domain_selection_strategy_is_used(self):
        class LastDomainStrategy(DomainSelectionPolicy):
            def select_domain(self, service: Microservice, infrastructures: list[Cloud]) -> Cloud | None:
                return infrastructures[-1]

        cloud_a, devices_a, _ = _cloud_with_orchestrator()
        cloud_b, devices_b, _ = _cloud_with_orchestrator()
        service = _microservice("svc-domain", "img-domain")

        devices_a[0].store_image(service.image)
        devices_b[0].store_image(service.image)

        continuum_network = Network(gateway=devices_a[0])
        continuum_network.graph.add_edge(cloud_a.network.gateway, cloud_b.network.gateway, capacity=100)
        continuum_orchestrator = ContinuumOrchestrator(
            [cloud_a, cloud_b], continuum_network, domain_selection_strategy=LastDomainStrategy()
        )
        application = Application("app", [service])

        self.assertTrue(continuum_orchestrator.deploy(application))
        self.assertTrue(any(device.has_microservice(service) for device in cloud_b.devices))


if __name__ == "__main__":
    unittest.main()
