import abc
import string

from edgepysim import ResourceType


class ResourceDescriptor(abc.ABC):

    def __init__(self, res_type: ResourceType, res_value):
        self.res_type = res_type
        self.res_value = res_value

    def __isub__(self, other):
        self.res_value = self.__sub__(other)

    def __iadd__(self, other):
        self.res_value = self.__add__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __lt__(self, other):
        return not self.__ge__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def __gt__(self, other):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass

    @abc.abstractmethod
    def __add__(self, other):
        pass

    @abc.abstractmethod
    def __sub__(self, other):
        pass

    def get_type(self) -> ResourceType:
        return self.res_value

    def set_value(self, value):
        self.res_value = value

    def get_value(self) -> string:
        return self.res_value


class IntegerResourceDescriptor(ResourceDescriptor):

    def __init__(self, res_type: ResourceType, res_value: string):
        super().__init__(res_type, res_value)

    def __gt__(self, other):
        return int(self.res_value) > int(other.res_value)

    def __eq__(self, other):
        return int(other.res_value) == int(self.res_value)

    def __add__(self, other):
        return int(self.res_value) + int(other.res_value)

    def __sub__(self, other):
        return int(self.res_value) - int(other.res_value)


class MemoryAmountResourceDescriptor(IntegerResourceDescriptor):

    def __init__(self, res_value: string):
        super().__init__(ResourceType.MEMORY_AMOUNT, res_value)


class NetworkBandwidthResourceDescriptor(IntegerResourceDescriptor):

    def __init__(self, res_value: string):
        super().__init__(ResourceType.NETWORK_BANDWIDTH, res_value)


class ProcessingCapacityResourceDescriptor(IntegerResourceDescriptor):

    def __init__(self, res_value: string):
        super().__init__(ResourceType.COMPUTING_CAPACITY, res_value)


class StorageSpaceResourceDescriptor(IntegerResourceDescriptor):

    def __init__(self, res_value: string):
        super().__init__(ResourceType.STORAGE, res_value)