from abc import abstractmethod, ABC
from typing import Any


class Node(ABC):
    """
    Base class for all nodes
    """
    _count = -1

    @abstractmethod
    def __init__(self):
        self._output_val = None
        self._name = None

    @property
    def name(self) -> str:
        """
        :return: unique name for the node
        """
        return self._name

    @property
    def value(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: evaluated output value of the node
        """
        return self._output_val

    def clear(self):
        """
        clears the cached input of the node
        """
        self._output_val = None

    @abstractmethod
    def serialize(self):
        pass

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return other.name == self.name

    def __repr__(self):
        return '<%s with value "%s">' % (self.name, self.value)


class Constant(Node):
    """
    Node with constant value. Will always cache the value, even after
    clear() is called
    """

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
