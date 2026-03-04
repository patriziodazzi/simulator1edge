import abc
import copy
from enum import Enum


class ResourceType(str, Enum):
    STORAGE = 'storage'
    MEMORY_AMOUNT = 'memory_amount'
    COMPUTING_CAPACITY = 'computing_capacity'
    NETWORK_BANDWIDTH = 'network_bandwidth'
    FPGA = 'FPGA'
    GPU = 'GPU'
    WIFI = 'WIFI'
    GPS = 'GPS'
    AVAILABILITY_ZONE = 'availability_zone'


class ResourceDescriptor(abc.ABC):

    def __init__(self, res_type: ResourceType, res_value):
        self.type = res_type
        self.value = res_value

    def __str__(self):
        return str(self.type) + " : " + str(self.value)

    def __isub__(self, other):
        _sub: ResourceDescriptor = self - other
        # self.res_value = self.__sub__(other)
        self.value = _sub.value
        return self

    def __iadd__(self, other):
        _sum: ResourceDescriptor = self + other
        # self.res_value = self.__add__(other)
        self.value = _sum.value
        return self

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

    @property
    def type(self) -> ResourceType:
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class IntegerResourceDescriptor(ResourceDescriptor):
    """Resource descriptor for integer-valued resources."""

    def __init__(self, res_type: ResourceType, res_value: int | str):
        # Store as int internally for consistency
        super().__init__(res_type, int(res_value) if isinstance(res_value, str) else res_value)

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return other.value == self.value

    def __add__(self, other):
        ret: IntegerResourceDescriptor = copy.deepcopy(self)
        ret.value = self.value + other.value
        return ret

    def __sub__(self, other):
        ret: IntegerResourceDescriptor = copy.deepcopy(self)
        ret.value = self.value - other.value
        return ret


class MemoryAmountResourceDescriptor(IntegerResourceDescriptor):
    """Memory amount resource descriptor."""

    def __init__(self, res_value: int | str):
        super().__init__(ResourceType.MEMORY_AMOUNT, res_value)


class NetworkBandwidthResourceDescriptor(IntegerResourceDescriptor):
    """Network bandwidth resource descriptor."""

    def __init__(self, res_value: int | str):
        super().__init__(ResourceType.NETWORK_BANDWIDTH, res_value)


class ProcessingCapacityResourceDescriptor(IntegerResourceDescriptor):
    """Processing capacity resource descriptor."""

    def __init__(self, res_value: int | str):
        super().__init__(ResourceType.COMPUTING_CAPACITY, res_value)


class StorageSpaceResourceDescriptor(IntegerResourceDescriptor):
    """Storage space resource descriptor."""

    def __init__(self, res_value: int | str):
        super().__init__(ResourceType.STORAGE, res_value)
