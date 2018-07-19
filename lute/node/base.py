from abc import abstractmethod, ABCMeta
from typing import Any


class NodeMeta(ABCMeta):
    def __new__(meta_cls, *args, **kwargs):
        cls = super().__new__(meta_cls, *args, **kwargs)

        if cls.__name__ != "Node":
            original_init = cls.__init__
            def __init__(self, *args, **kwargs):
                super(cls, self).__init__()
                self._name = cls.__gen_name__()
                original_init(self, *args, **kwargs)
            cls.__init__ = __init__

        return cls


class Node(metaclass=NodeMeta):
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
    def value(self):
        if not self.evaluated:
            self._output_val = self.eval()
            self.evaluated = True

        return self._output_val

    @abstractmethod
    def eval(self):
        """
        Perform actual evaluation steps for the node
        and return the output
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
        if self.evaluated:
            return '<%s with value "%s">' % (self.name, self.value)
        else:
            return '<%s and unevaluated>' % self.name


class Constant(Node):
    """
    Node with constant value. Will always cache the value, even after
    clear() is called
    """

    def __init__(self, value: Any):
        self._value = value

    def eval(self):
        return self._value

    def __call__(self, other: Node):
        raise Exception("uncallable node")


class Variable(Node):

    def __init__(self):
        pass

    def eval(self):
        return self._output_val

    def __call__(self, other: Node):
        raise Exception("uncallable node")

    @Node.value.setter
    def value(self, val):
        self._output_val = val


class Identity(Node):
    """
    Passes on the value of input
    """

    def __init__(self):
        pass

    def eval(self):
        return self._source_node.value

    def __call__(self, other: Node):
        super().__call__(other)
        self._source_node = other

        return self
