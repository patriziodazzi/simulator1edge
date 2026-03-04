from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.application.base import Image, Microservice
from simulator1edge.device.concrete import CloudDevice, NetworkSwitchRouter
from simulator1edge.network.base import Network
from simulator1edge.orchestrator.concrete import CloudOrchestrator
from simulator1edge.resource.descriptor import StorageSpaceResourceDescriptor as STORAGE
from simulator1edge.resource.descriptor import NetworkBandwidthResourceDescriptor as NET
from simulator1edge.resource.descriptor import MemoryAmountResourceDescriptor as MEMORY
from simulator1edge.resource.descriptor import ResourceType
from simulator1edge.resource.requirement import StorageSpaceRequirement as STORAGEreq
from simulator1edge.resource.requirement import NetworkBandwidthRequirement as NETreq
from simulator1edge.resource.requirement import MemoryAmountRequirement as MEMreq


class DeviceBehaviorTests(unittest.TestCase):
    def _device(self):
        return CloudDevice("az1", [STORAGE("100"), NET("100"), MEMORY("100")])

    def _microservice(self, image_size=10, memory_req="20"):
        img = Image("ubuntu", image_size)
        reqs = [STORAGEreq("1"), NETreq("1"), MEMreq(memory_req)]
        return Microservice("ms", reqs, img)

    def test_store_image_is_idempotent(self):
        d = self._device()
        img = Image("ubuntu", 10)
        self.assertTrue(d.store_image(img))
        remaining = int(d.resources[ResourceType.STORAGE].value)
        self.assertTrue(d.store_image(img))
        self.assertEqual(remaining, int(d.resources[ResourceType.STORAGE].value))

    def test_terminate_microservice_frees_resources(self):
        d = self._device()
        ms = self._microservice()
        d.store_image(ms.image)
        before = int(d.resources[ResourceType.MEMORY_AMOUNT].value)
        d.start_microservice(ms)
        during = int(d.resources[ResourceType.MEMORY_AMOUNT].value)
        self.assertLess(during, before)
        self.assertTrue(d.terminate_microservice(ms))
        after = int(d.resources[ResourceType.MEMORY_AMOUNT].value)
        self.assertEqual(after, before)


class OrchestratorBehaviorTests(unittest.TestCase):
    def test_deploy_returns_true(self):
        d1 = CloudDevice("az1", [STORAGE("100"), NET("100"), MEMORY("100")])
        d2 = CloudDevice("az1", [STORAGE("100"), NET("100"), MEMORY("100")])
        image = Image("ubuntu", 10)
        d1.store_image(image)

        ms = Microservice("ms", [STORAGEreq("1"), NETreq("1"), MEMreq("10")], image)
        network = Network(gateway=NetworkSwitchRouter(100))
        network.graph.add_edge(d1, d2, capacity=100)

        orch = CloudOrchestrator([d1, d2], network)
        self.assertTrue(orch.deploy([ms]))


if __name__ == "__main__":
    unittest.main()
