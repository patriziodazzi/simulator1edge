from edgepysim import *


class GlobalOrchestrator(Orchestrator):
    def __init__(self):
        super().__init__()

    def deploy(self, application: Application) -> bool:
        pass


class CloudOrchestrator(Orchestrator):
    def __init__(self, cloud: Cloud):
        super().__init__()

    def deploy(self, services: set[Microservice]) -> bool:
        pass


class EdgeOrchestrator(Orchestrator):
    def __init__(self, edge_cluster: EdgeCluster):
        super().__init__()

    def deploy(self, services: set[Microservice]) -> bool:
        pass
