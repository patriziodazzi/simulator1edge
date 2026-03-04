import abc

from simulator1edge.resource.descriptor import ResourceDescriptor, NetworkBandwidthResourceDescriptor, \
    StorageSpaceResourceDescriptor, MemoryAmountResourceDescriptor, ProcessingCapacityResourceDescriptor


class Requirement(abc.ABC):

    def __init__(self, rd: ResourceDescriptor, matching_rule):
        self.rd = rd
        self.matching_rule = matching_rule

    @property
    def resource_type(self):
        return self.rd.type

    @abc.abstractmethod
    def _matching_rule(self):
        return self.matching_rule

    def is_satisfied_by_resource(self, actual_resource: ResourceDescriptor) -> bool:

        if self._matching_rule() == "eq":
            return actual_resource == self.rd
        elif self._matching_rule() == "gt":
            return actual_resource > self.rd
        elif self._matching_rule() == "lt":
            return actual_resource < self.rd
        elif self._matching_rule() == "ge":
            return actual_resource >= self.rd
        elif self._matching_rule() == "le":
            return actual_resource <= self.rd

        return False


class RequirementSet(object):

    def __init__(self, reqs: list[Requirement]):
        self.requirement_set = reqs


class IntegerRequirement(Requirement):

    def __init__(self, rd: ResourceDescriptor, matching: str):
        super().__init__(rd, matching)
        self.matching = matching

    def _matching_rule(self):
        return self.matching


class NetworkBandwidthRequirement(IntegerRequirement):
    def __init__(self, res_value: int | str):
        super().__init__(NetworkBandwidthResourceDescriptor(res_value), matching="ge")


class StorageSpaceRequirement(IntegerRequirement):
    def __init__(self, res_value: int | str):
        super().__init__(StorageSpaceResourceDescriptor(res_value), matching="ge")


class MemoryAmountRequirement(IntegerRequirement):
    def __init__(self, res_value: int | str):
        super().__init__(MemoryAmountResourceDescriptor(res_value), matching="ge")


class ProcessingCapacityResourceRequirement(IntegerRequirement):
    def __init__(self, res_value: int | str):
        super().__init__(ProcessingCapacityResourceDescriptor(res_value), matching="ge")
