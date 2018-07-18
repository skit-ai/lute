from abc import abstractmethod, ABC
from typing import Any, List


class Node(ABC):
    """
    Base class for all nodes
    """
    _count = -1

    @abstractmethod
    def __init__(self):
        self._name = None
        self._output_val = None
        self.evaluated = False
        self.predecessors = []
        self.successors = []

    @classmethod
    def __gen_name__(cls):
        cls._count += 1
        return "%s_%s" % (cls.__name__, cls._count)

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
        if not self.evaluated:
            self.eval()
            self.evaluated = True

        return self._output_val

    @abstractmethod
    def eval(self):
        """
        Perform actual evaluation steps for the node
        """

        ...

    def clear(self):
        """
        clears the cached input of the node
        """

        self.evaluated = False

        # Free some memory too
        self._output_val = None

    def __call__(self, other: 'Node'):
        other.successors.append(self)
        self.predecessors.append(other)
        return self

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<%s with value "%s">' % (self.name, self.value)


class Constant(Node):
    """
    Node with constant value. Will always cache the value, even after
    clear() is called
    """

    def __init__(self, value: Any):
        super().__init__()
        self._value = value
        self._name = Constant.__gen_name__()

    def eval(self):
        self._output_val = self._value

    def __call__(self, other: Node):
        raise Exception("uncallable node")


class Variable(Node):

    def __init__(self):
        super().__init__()
        self._name = Variable.__gen_name__()

    def eval(self):
        ...

    def __call__(self, other: Node):
        raise Exception("uncallable node")

    @Node.value.setter
    def value(self, val):
        self._output_val = val
