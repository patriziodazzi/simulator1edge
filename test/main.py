from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from typing import cast

from simulator1edge.application.base import Image, Microservice, Application
from simulator1edge.device.concrete import NetworkSwitchRouter as Router
from simulator1edge.device.generator import CloudDeviceFactory as CDF
from simulator1edge.infrastructure.generator import CloudFactory as CF, ComputingInfrastructureFactory as CIF, \
    ComputingContinuumBuildDirector, ComputingContinuumBuilder
from simulator1edge.orchestrator.concrete import CloudOrchestrator
from simulator1edge.resource.descriptor import StorageSpaceResourceDescriptor as STORAGE, \
    NetworkBandwidthResourceDescriptor as NET_BANDWIDTH, MemoryAmountResourceDescriptor as MEMORY
from simulator1edge.resource.requirement import StorageSpaceRequirement as STORAGEreq, \
    NetworkBandwidthRequirement as NET_BANDWIDTHreq, MemoryAmountRequirement as MEMORYreq
from simulator1edge.util.environment import Simulation

if __name__ == '__main__':

    # Create Simulation Environment
    sim = Simulation()

    # Create Application
    reqs = [STORAGEreq("1500"), NET_BANDWIDTHreq("10"), MEMORYreq("512")]
    img = Image("ubuntu", 250)
    ms = Microservice("ms1", reqs, img)
    # app = Application("Linux", [ms])

    # Create resources
    hpc_res = [STORAGE("2000"), NET_BANDWIDTH("1000"), MEMORY("1024")]
    avg_res = [STORAGE("1000"), NET_BANDWIDTH("100"), MEMORY("512")]
    low_res = [STORAGE("500"), NET_BANDWIDTH("50"), MEMORY("256")]
    # dev_res: list = [hpc_res, avg_res, low_res]

    # Device and Cloud factory
    device_factory = CDF([(hpc_res, 8), (avg_res, 2), (low_res, 1)])
    cloud_factory = CF({CF.INTL_NET_BNDWDTH_FEAT: 100, CF.EXTL_NET_BNDWDTH_FEAT: 1000})

    # Create cloud#1
    devices = device_factory.create_device_instances({CDF.CLD_NAM_FEAT: "cloud1"})
    cloud1 = cloud_factory.create_computing_instance({CIF.DEVS_FEAT: devices, CF.GTWY_FEAT: Router(10)})

    # Create cloud#2
    devices = device_factory.create_device_instances({CDF.CLD_NAM_FEAT: "cloud2"})
    cloud2 = cloud_factory.create_computing_instance({CIF.DEVS_FEAT: devices, CF.GTWY_FEAT: Router(10)})

    # Create cloud#3
    device_factory = CDF([(hpc_res, 4), (avg_res, 2), (low_res, 1)])
    devices = device_factory.create_device_instances({CDF.CLD_NAM_FEAT: "cloud3"})
    cloud3 = cloud_factory.create_computing_instance({CIF.DEVS_FEAT: devices, CF.GTWY_FEAT: Router(10)})

    # Create Continuum
    continuum_builder = ComputingContinuumBuildDirector(ComputingContinuumBuilder())
    continuum_builder.construct({ComputingContinuumBuildDirector.CMP_CNT_RES_FEAT: [cloud1, cloud2, cloud3]})
    continuum = continuum_builder.result

    # Print network graph
    continuum.draw_continuum("ciccio.png")

    # Ask the orchestrator of cloud #3 the all the resources able to host ms
    cloud_orchestrator = cast(CloudOrchestrator, cloud3.orchestrator)
    resources_viable = cloud_orchestrator.list_of_candidates(ms)

    cloud3.devices[0].store_image(ms.image)

    cloud_orchestrator.deploy([ms])
    cloud_orchestrator.deploy([ms])
    cloud_orchestrator.deploy([ms])
    cloud_orchestrator.deploy([ms])


    # idx = 0
    # for res in resources_viable:
    #     print(res)
    #     if idx % 2:
    #         res.store_image(ms.image)
    #         res.start_microservice(ms)
    #
    #     idx += 1
    #
    # print("cucchiero")
    #
    # resources_viable = cloud_orchestrator.list_of_candidates(ms)
    # for res in resources_viable:
    #     print(res)
    #
    # print(cloud3.devices[0])
    # cloud3.devices[0].terminate_microservice(ms)
    #
    # resources_viable = cloud_orchestrator.list_of_candidates(ms)
    # for res in resources_viable:
    #     print(res)
    sim.run()

    print(sim.env.now)
