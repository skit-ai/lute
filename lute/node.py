from abc import abstractmethod, ABC
from typing import Any


class Node(ABC):
    _count = -1

    @abstractmethod
    def __init__(self):
        self._output_val = None
        self._name = None

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    @abstractmethod
    def serialize(self):
        pass

    @property
    def value(self, *args, **kwargs):
        return self._output_val

    def clear(self):
        self._output_val = None


class Constant(Node):

    def __init__(self, value: Any):
        super().__init__()

        Constant._count += 1
        self._name = "%s_%s" % (__class__.__name__, Constant._count)
        self._value = value

    @property
    def value(self):
        self._output_val = self._value
        return self._output_val

    def serialize(self):
        pass


class Variable(Node):

    def __init__(self):
        super().__init__()

        Variable._count += 1
        self._name = "%s_%s" % (__class__.__name__, Variable._count)

    @Node.value.setter
    def value(self, val):
        self._output_val = val

    def serialize(self):
        pass
